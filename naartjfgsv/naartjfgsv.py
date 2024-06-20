import pandas as pd
from langchain.embeddings import HuggingFaceEmbeddings
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
import os
import re


pd.options.mode.copy_on_write = True
os.environ['KMP_DUPLICATE_LIB_OK']='True'
os.environ['TOKENIZERS_PARALLELISM']='false'
embedding = HuggingFaceEmbeddings(model_name='intfloat/multilingual-e5-large-instruct')
api_key = os.environ["api_key"]
ibm_cloud_url = os.environ["ibm_cloud_url"]
project_id = os.environ["project_id"]
creds = {
        "url": ibm_cloud_url,
        "apikey": api_key 
    }
model_params = {
    GenParams.DECODING_METHOD: "greedy",
    GenParams.MIN_NEW_TOKENS: 1,
    GenParams.MAX_NEW_TOKENS: 4095,
    GenParams.RANDOM_SEED: 42,
    GenParams.TEMPERATURE: 0,
    GenParams.REPETITION_PENALTY: 1.0,
}

model = Model(
    model_id="meta-llama/llama-3-70b-instruct",
    # ibm-mistralai/mixtral-8x7b-instruct-v01-q",
    # model_id="google/flan-ul2",
    project_id=project_id,
    credentials=creds,
    params=model_params,
    )
""" Uncomment this if you want to use some of these regex to clean your dataframe"""
# def clean_question(question):
#     question = re.sub(r'\b(?:ＴＥＬ|TEL)[:：][\d\-（）]+', '', question)
#     question = re.sub(r'\b(?:ＦＡＸ|FAX)[:：][\d\-（）]+', '', question)
#     question = re.sub(r'ＦＡＸ[:：]', '', question)
#     question = re.sub(r'\bnan\b', '', question)
#     match = re.search(r'＜質問内容＞(.*?)$', question)
#     if match:
#         return match.group(1).strip()
#     else:
#         return question.strip()    
def send_to_llm(prompt):
    return model.generate_text(prompt)
cleaned_new_df = pd.read_csv("chunk_1.csv")

len(cleaned_new_df)
cleaned_new_df.head()
prompt_template=""" You are an excellent Japanese Data Analyst and follows all the instruction given properly. You are trained on React prompt engineering  where you response is based on thought, action and observation and finally responding in Japanese. Your will be given an input which will include Question and Answer pair and your task is to provide and output which will include REPHRASED QUESTION AND REPHRASED ANSWER. Follow the below template to generate the output as mentioned below

|input|

Question:

#instructions

Answer:

|output|

Rephrased Question:
#instructions
Rephrased Answer:

|input|

Question:
プリンターの設定について プリンターの設定について ＴＥＬ：03-5533-9191ＦＡＸ：管理番号：PD43115メーカー：＜エラーメッセージ＞＜質問内容＞平素よりお世話になっております。営業教育部の木村と申します。標題の件について、質問があります。プリンターではなく、コピー機から印刷をしたい場合、外部からソフトウェアを導入する必要がありますでしょうか。該当者（91253）が産育休に入られる前は使用できていたそうです。宜しくお願いします。

#instructions
Follow this reAct Prompt Engineering method to give your final one line REPHRASED QUESTION in JAPANESE. Do not miss any important information. YOU DO NOT NEED TO SHOW THE approach just the ANSWER.
        "Thought 1: Identify the main question within the provided text."
        "Action 1: Extract core question"
        "Observation 1: What is the core question?"
        "Thought 2: Simplify and rephrase the question for clarity."
        "Action 2: Rephrase"
        "Observation 2: What is the rephrased question?"

REPHRASED QUESTION:
プリンターではなく、コピー機から印刷するために外部ソフトの導入は必要か

#instructions
Based on the above generated REPHRASED QUESTION generate an appropriate REPHRASED ANSWER:

Answer:
システムＱＳＣ：山名　貴子◆いつもお世話になっております。下記手順書に従って初期設定を実施してください。＜リコー複合機の場合＞【 複合機設定手順（RICOH MP5002）】http://c-sp.nissay-intra.net/contents/in/TEBJADJBBJAABGAHEEB/board/Lists/List/DispForm.aspx?ID=73（QSC管理番号:NL7103）＜ゼロックス複合機の場合＞【ゼロックス複合機 プリンタ・スキャナ機能関連】（本部の場合）2_(本部用)【Xer

REPHRASED ANSWER:

この場合、外部からソフトウェアを導入する必要はありません。リコーMP5002の場合は、http://c-sp.nissay-intra.net/contents/in/TEBJADJBBJAABGAHEEB/board/Lists/List/DispForm.aspx?ID=73（QSC管理番号：NL7103）をご参照ください。ゼロックスの複写機については、「ZeroXs Copier - Printer and Scanner Functionality」というタイトルのドキュメントを参照してください。これらのリソースを使用すれば、外部ソフトウェアを使用せずにコピー機から印刷することができます。

|input|

Question: {question}


Answer: {answer}


|output|

"""
Skipped_Ids = []

def process_row(row):
    question = row["Question"]
    answer = row["Answer"]

    if not isinstance(question, str):
        question = ""
    if not isinstance(answer, str):
        answer = ""

    question = question.replace('\n', ' ').strip()
    answer = answer.replace('\n', ' ').strip()
    
    prompt = prompt_template.format(question=question, answer=answer)
    
    response = send_to_llm(prompt)
    
    rephrased_question_match = re.search(r'Rephrased Question:\n(.*?)\nRephrased Answer:', response, re.DOTALL)
    rephrased_answer_match = re.search(r'Rephrased Answer:\n(.*)', response, re.DOTALL)
    if rephrased_question_match and rephrased_answer_match:
        rephrased_question = rephrased_question_match.group(1).replace('\n', ' ').strip()
        rephrased_answer = rephrased_answer_match.group(1).replace('\n', ' ').strip()
        return rephrased_question, rephrased_answer
    else:
        return None, None

total_rows = len(cleaned_new_df)
print(f"Total number of rows: {total_rows}")
Questions = []
Answers = []
Ids = []

for index in range(total_rows):
    try:
        print(f"Rephrasing {index+1} of {total_rows} rows")

        row = cleaned_new_df.iloc[index]
        print(row)
        rephrased_question, rephrased_answer = process_row(row)
        
        if rephrased_question is not None and rephrased_answer is not None:
            Questions.append(rephrased_question)
            Answers.append(rephrased_answer)
            Ids.append(cleaned_new_df['ID'].iloc[index])
            print(f"Rephrased {index+1} of {total_rows} rows")
        else:
            print(f"Skipping row {index+1} due to missing rephrased question or answer")
            Skipped_Ids.append(cleaned_new_df['ID'].iloc[index])

    except Exception as e:
        print(f"Error processing row {index+1}: {e}")
        print("Stopped Early-----")
        break

result_df = pd.DataFrame({
    "Id": Ids,
    "Question": Questions,
    "Answer": Answers
})
result_df.to_csv("rephrased_QA_final.csv", index=False)

skipped_df = pd.DataFrame({
    "Skipped Ids": Skipped_Ids
})
skipped_df.to_csv("skipped_ids_final.csv", index=False)

print(f"Progress saved {len(Ids)} rows in rephrased_QA_final.csv")
print(f"Skipped {len(Skipped_Ids)} rows saved in skipped_ids_final.csv")
print("All results saved to rephrased_QA_final.csv and skipped_ids_final.csv")