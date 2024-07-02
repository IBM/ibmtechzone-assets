import warnings
warnings.filterwarnings("ignore")

import os
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from tqdm import tqdm
from rouge import Rouge
from dotenv import load_dotenv 
from nltk.metrics import jaccard_distance
from base import LLMEvaluator 
from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.meteor_score import single_meteor_score
from nltk.tokenize import word_tokenize
from itertools import combinations
from collections import Counter
import requests
import zipfile

import nltk
nltk.download('wordnet') 

class EvaluationMetrics:
    def __init__(self, csv_file):
        self.data = pd.read_csv(csv_file)[:]

    def calculate_bleu_score(self):
        bleu_scores = []
        for _, row in self.data.iterrows():
            hypothesis = row['answer'].split()
            reference = row['ground_truths'].split()
            bleu_scores.append(round(sentence_bleu([reference], hypothesis), 5))
        self.data['BLEU Score'] = bleu_scores

    def calculate_meteor_score(self):
        meteor_scores = []
        for _, row in self.data.iterrows():
            hypothesis = row['answer'].split()
            reference = row['ground_truths'].split()
            meteor_scores.append(round(single_meteor_score(reference, hypothesis), 5))
        self.data['METEOR Score'] = meteor_scores

    def calculate_rouge_l(self):
        rouge = Rouge()
        rouge_l_precision = []
        rouge_l_recall = []
        for _, row in self.data.iterrows():
            hypothesis = row['answer']
            reference = row['ground_truths']
            scores = rouge.get_scores(hypothesis, reference)[0]
            rouge_l_precision.append(round(scores['rouge-l']['p'], 5))
            rouge_l_recall.append(round(scores['rouge-l']['r'], 5))
        self.data['ROUGE-L Precision'] = rouge_l_precision
        self.data['ROUGE-L Recall'] = rouge_l_recall

    def calculate_rouge_n(self, n):
        rouge = Rouge()
        rouge_n_precision = []
        rouge_n_recall = []
        for _, row in self.data.iterrows():
            hypothesis = row['answer']
            reference = row['ground_truths']
            scores = rouge.get_scores(hypothesis, reference)[0]
            rouge_n_precision.append(round(scores[f'rouge-{n}']['p'], 5))
            rouge_n_recall.append(round(scores[f'rouge-{n}']['r'], 5))
        self.data[f'ROUGE-{n} Precision'] = rouge_n_precision
        self.data[f'ROUGE-{n} Recall'] = rouge_n_recall

    def calculate_jaccard_score(self):
        jaccard_scores = []
        for _, row in self.data.iterrows():
            hypothesis = set(row['answer'].split())
            reference = set(row['ground_truths'].split())
            jaccard_scores.append(round((1 - jaccard_distance(hypothesis, reference)), 5))
        self.data['Jaccard Score'] = jaccard_scores

    def return_output_csv(self):
        return self.data
    
def rag_metrics(input_csv,MDOEL_ID,URL,API_KEY,PROJECT_ID):
    # self.data = pd.read_csv(input_csv)[:]
    metrics = EvaluationMetrics(input_csv)
    metrics.calculate_bleu_score()
    metrics.calculate_meteor_score()
    metrics.calculate_rouge_l()
    metrics.calculate_rouge_n(n=1)  # Change 'n' to desired ROUGE-N value
    metrics.calculate_jaccard_score()
    data = metrics.return_output_csv()

    cr_score = []
    cr_reason = []
    ar_score = []
    ar_reason = []
    faithful_score = []

    evaluator = LLMEvaluator(
        model_id=MDOEL_ID,
        url=URL,
        api_key=API_KEY,
        project_id=PROJECT_ID
    )

    for i in tqdm(range(0, len(data)), desc="Processing...", position=0):
        question = data.loc[i, 'question'][:].strip()
        answer = data.loc[i, 'answer'][:].strip()
        context = data.loc[i, 'contexts'][:].strip()
        cr = evaluator.context_relevance_with_cot_reasons(question=question, context=context)
        ar = evaluator.answer_relevance_with_cot_reasons(question=question, answer=answer)
        f = evaluator.faithfulness(question=question, answer=answer, context=context)
        cr_score.append(cr[0])
        cr_reason.append(cr[1]["reason"])
        ar_score.append(ar[0])
        ar_reason.append(ar[1]["reason"])
        faithful = faithful_score.append(f)

    data["Context_Relevance_Score"] = cr_score
    data["Context_Relevance_Score_Reason"] = cr_reason
    data["Groundedness"] = faithful_score
    data["Answer_Relevance_Score"] = ar_score
    data["Answer_Relevance_Score_Reason"] = ar_reason
    return data

def calculate_coherence(tokens):
    word_counts = Counter(tokens)
    total_words = len(tokens)
    co_occurrences = Counter(zip(tokens, tokens[1:]))
    
    pmi_scores = {}
    for (word1, word2), co_occurrence_count in co_occurrences.items():
        pmi = np.log2((co_occurrence_count / total_words) / ((word_counts[word1] / total_words) * (word_counts[word2] / total_words)))
        pmi_scores[(word1, word2)] = pmi

    coherence_score = np.mean(list(pmi_scores.values()))
    normalized_coherence = (coherence_score - np.min(list(pmi_scores.values()))) / (np.max(list(pmi_scores.values())) - np.min(list(pmi_scores.values())))

    return normalized_coherence

def calculate_u_mass_coherence(texts):
    co_occurrences = Counter()
    for tokens in texts:
        for a, b in combinations(tokens, 2):
            co_occurrences[(a, b)] += 1

    pmi_scores = {}
    for (a, b), co_occurrence_count in co_occurrences.items():
        pmi = np.log2((co_occurrence_count / len(texts)) / ((tokens.count(a) / len(texts)) * (tokens.count(b) / len(texts))))
        pmi_scores[(a, b)] = pmi

    coherence_score = np.mean(list(pmi_scores.values()))
    normalized_coherence = (coherence_score - np.min(list(pmi_scores.values()))) / (np.max(list(pmi_scores.values())) - np.min(list(pmi_scores.values())))

    return normalized_coherence

def compute_coherence_scores(df, text_columns):
    for col in text_columns:
        coherence_scores = []
        for _, row in df.iterrows():
            tokens = word_tokenize(row[col].lower())
            coherence_score = calculate_u_mass_coherence([tokens])
            coherence_scores.append(coherence_score)

        df[f'{col}_Normalized_Coherence_Score'] = coherence_scores

    return df

def summary_metrics(file_fpath):
    result_df= None
    if file_fpath:
        df = pd.read_csv(file_fpath)
        selected_columns = os.environ('selected_columns_summary',None)
        if selected_columns:
            selected_columns = selected_columns.split(',')
            result_df = compute_coherence_scores(df, selected_columns)
        else:
            print("No columns selected")
    else:
        print("No files selected")
    return result_df
    
    
def select_usecase():
    usecase = os.environ("usecase",None)
    print(usecase)
    file_path = os.environ("file_path",'')
    usecase = usecase.lower()
    if 'summarization' in usecase:
        print('Summary usecase')
        file_fpath=download_box(file_path)
        summary_metrics_res=summary_metrics(file_fpath)
        output_file = 'summarization_output.csv'
        summary_metrics_res.to_csv(output_file, index=False)
        print(f'Results saved to {output_file}')
    elif 'rag' in usecase:
        print('RAG usecae')
        output_csv = 'rag_output.csv'  # Replace with desired output CSV file path
        MDOEL_ID = "meta-llama/llama-2-70b-chat"
        URL = os.environ("url",None)
        API_KEY = os.environ("api_key", None)
        PROJECT_ID = os.environ("project_id", None)
        file_fpath = download_box(file_path)
        rag_metrics_res = rag_metrics(file_fpath,MDOEL_ID,URL,API_KEY,PROJECT_ID)
        rag_metrics_res.to_csv(output_csv, index=False)


def download_box(file_path):
    os.makedirs('data', exist_ok=True)
    os.chdir('data')
    CWD = os.getcwd()
    response = requests.get(file_path)
    file_name = file_path.split('/')[-1]
    file_fpath = os.path.join(CWD, file_name)
    with open(file_fpath, 'wb') as file:
        file.write(response.content)
    for file in os.listdir(CWD):
        if file.endswith('.zip'):
            # Unzip the file
            with zipfile.ZipFile(file, 'r') as zip_ref:
                zip_ref.extractall(CWD)
    return file_fpath


if __name__ == "__main__":
    #when you enable load_env make sure you are changing os.environ to os.getenv
    # load_dotenv()
    select_usecase()

    