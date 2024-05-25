import os
import pandas as pd
import typing as t
import warnings
warnings.filterwarnings("ignore")
from langchain.callbacks.base import Callbacks
from langchain.prompts import ChatPromptTemplate
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.schema import LLMResult
from langchain.llms.base import BaseLLM
from datasets import Dataset
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from langchain_community.llms.watsonxllm import WatsonxLLM
from ragas.llms import LangchainLLM
from ragas import evaluate
from ragas.metrics import (faithfulness, answer_relevancy, context_precision, context_relevancy, context_recall, answer_similarity, answer_correctness)
from ragas.llms.langchain import MULTIPLE_COMPLETION_SUPPORTED
MULTIPLE_COMPLETION_SUPPORTED.append(WatsonxLLM)



WATSONX_API_KEY = os.environ["watsonx_api_key"]
IBM_CLOUD_URL = os.environ["ibm_cloud_url"]
PROJECT_ID = os.environ["project_id"]
EMBEDDINGS_GEN = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-base")
MODEL = 'mistralai/mixtral-8x7b-instruct-v01'



def isWatsonx(llm: WatsonxLLM) -> bool:
    return isinstance(llm, WatsonxLLM)



class CustomizedLangchainLLM(LangchainLLM):
    def generate(self, prompts: list[ChatPromptTemplate], n: int = 1, temperature: float = 1e-8, callbacks: t.Optional[Callbacks] = None) -> LLMResult:
        return self._generate_multiple_completions_watsonx(prompts, callbacks)

    def _generate_multiple_completions_watsonx(self, prompts: list[ChatPromptTemplate], callbacks: t.Optional[Callbacks] = None) -> LLMResult:
        self.langchain_llm = t.cast(WatsonxLLM, self.langchain_llm)
        if isinstance(self.llm, BaseLLM):
            ps = [p.format() for p in prompts]
            result = self.llm.generate(ps, callbacks=callbacks)
        else:  
            ps = [p.format_messages() for p in prompts]
            result = self.llm.generate(ps, callbacks=callbacks)
        return result  



generate_params = {
    GenParams.DECODING_METHOD: 'greedy',
    GenParams.MIN_NEW_TOKENS: 1,
    GenParams.MAX_NEW_TOKENS: 600,
    GenParams.TEMPERATURE: 0.1,
    GenParams.RANDOM_SEED: 42,
    GenParams.REPETITION_PENALTY: 1.,
}
watsonx_llm = WatsonxLLM(
    model_id=MODEL,
    apikey=WATSONX_API_KEY,
    url=IBM_CLOUD_URL,
    project_id=PROJECT_ID,
    params=generate_params,
)
ragas_llm = CustomizedLangchainLLM(llm = watsonx_llm)



metrics = [faithfulness, context_relevancy, answer_similarity, answer_relevancy]
for m in metrics:
    m.__setattr__("llm", ragas_llm)
    if hasattr(m, "embeddings"):
        m.__setattr__("embeddings", EMBEDDINGS_GEN)
# answer_correctness.faithfulness = faithfulness
# answer_correctness.answer_similarity = answer_similarity



# Sample dataset - Modify this with the client data + LLM generated responses
data_samples = {
    'question': [
        'Who is known as the "Little Master" in cricket?',
        'Which player has the highest number of international centuries in ODI cricket?',
        'Which team has won the most ICC Cricket World Cups?',
        'Who is famous for the "helicopter shot" in cricket?',
        'In which year did Sachin Tendulkar retire from international cricket?',
        'Who holds the record for the fastest century in T20 international cricket?',
        'Which team is often referred to as the "Proteas" in international cricket?',
        'Who is considered the best captain in the history of Indian cricket?',
        'In which city is the iconic Melbourne Cricket Ground (MCG) located?',
        'Which country won the ICC Cricket World Cup in 2019?'
    ],
    'ground_truths': [
        ['Sachin Tendulkar is often called the "Little Master" in cricket.'],
        ['Virat Kohli is known for his numerous international centuries in ODI format.'],
        ['Australia dominated the ICC Cricket World Cup with multiple victories.'],
        ['MS Dhoni popularized the "helicopter shot" in cricket.'],
        ['Sachin Tendulkar bid farewell to international cricket in 2013.'],
        ['AB de Villiers set the record for the fastest century in T20 international cricket.'],
        ['The South African cricket team is nicknamed the "Proteas."'],
        ['M.S. Dhoni is highly regarded as the best captain in Indian cricket history.'],
        ['The iconic Melbourne Cricket Ground (MCG) is situated in Melbourne, Australia.'],
        ['England won the ICC Cricket World Cup in 2019']
    ],
    'contexts': [
        ['Sachin Tendulkar, known as the "Little Master," is hailed as one of the greatest batsmen to have played cricket.', 'His elegant and technically sound batting style has left a lasting impact on the game.'],
        ['Virat Kohli holds the record for the highest number of international centuries in ODI cricket surpassing his idol Sachin Tendulkar who has 49 centuries, showcasing his incredible consistency and skill as a batsman.', 'His ability to chase targets and play under pressure has earned him immense admiration.'],
        ['Australia has won the most ICC Cricket World Cups, dominating the tournament with their aggressive and competitive cricket over the years.', 'Their success is attributed to a strong cricketing culture and talented players.'],
        ['MS Dhoni, the former captain of the Indian cricket team, is famous for the "helicopter shot," a unique and powerful stroke that he popularized.', 'The shot involves a high backlift and a powerful flick of the wrists.'],
        ['Sachin Tendulkar retired from international cricket in 2013, marking the end of an illustrious career that spanned over two decades.', 'His farewell speech at the Wankhede Stadium in Mumbai was an emotional moment for cricket fans worldwide.'],
        ['South African cricketer AB de Villiers holds the record for the fastest century in T20 international cricket, achieving the feat in just 31 balls.', 'His ability to score at a rapid pace has made him one of the most exciting players in the format.'],
        ['The South African cricket team is often referred to as the "Proteas" in international cricket, symbolizing resilience and strength.', 'The team has produced some exceptional players and has a competitive spirit on the field.'],
        ['M.S. Dhoni is considered the best captain in the history of Indian cricket, leading the team to numerous victories, including the ICC Cricket World Cup in 2011.', 'His calm and composed captaincy style earned him the nickname "Captain Cool."'],
        ['The iconic Melbourne Cricket Ground (MCG) is located in Melbourne, Australia, and is one of the largest and most historic cricket stadiums in the world.', 'It has hosted numerous memorable cricket matches and is a symbol of Australian sports culture.'],
        ['The ICC Cricket World Cup in 2019 was hosted by England.', 'England won the tournament by defeating New Zealand in a thrilling final.']
    ],
    'answer': [
        'Sachin Tendulkar is known as the "Little Master."',
        'Virat Kohli holds the record for the highest number of international centuries.',
        'Australia has won the most ICC Cricket World Cups.',
        'MS Dhoni is famous for the "helicopter shot" in cricket.',
        'Sachin Tendulkar retired from international cricket in 2013.',
        'AB de Villiers holds the record for the fastest century in T20 international cricket.',
        'The South African cricket team is often referred to as the "Proteas" in international cricket.',
        'M.S. Dhoni is considered the best captain in the history of Indian cricket.',
        'The iconic Melbourne Cricket Ground (MCG) is located in Melbourne, Australia.',
        'England'
    ]
}



def validate_data_format(data_samples):
    """
    Validate the format of data_samples based on the provided specifications.

    Args:
    - data_samples (dict): Dictionary containing 'question', 'answer', 'contexts', and 'ground_truths'.
    """
    expected_keys = ['question', 'answer', 'contexts', 'ground_truths']
    # Check if all expected keys are present
    if set(data_samples.keys()) != set(expected_keys):
        raise ValueError("Invalid keys in data_samples. Expected keys: {}".format(expected_keys))
    # Check types and lengths of values
    if not isinstance(data_samples['question'], list) or not all(isinstance(q, str) for q in data_samples['question']):
        raise ValueError("Invalid format for 'question'. It should be a list of strings.")
    if not isinstance(data_samples['answer'], list) or not all(isinstance(a, str) for a in data_samples['answer']):
        raise ValueError("Invalid format for 'answer'. It should be a list of strings.")
    if not isinstance(data_samples['contexts'], list) or not all(isinstance(c, list) and all(isinstance(sc, str) for sc in c) for c in data_samples['contexts']):
        raise ValueError("Invalid format for 'contexts'. It should be a list of lists of strings.")
    if not isinstance(data_samples['ground_truths'], list) or not all(isinstance(gt, list) and all(isinstance(sgt, str) for sgt in gt) for gt in data_samples['ground_truths']):
        raise ValueError("Invalid format for 'ground_truths'. It should be a list of lists of strings.")
    # Check if lengths of lists are consistent
    num_samples = len(data_samples['question'])
    if not all(len(lst) == num_samples for lst in data_samples.values()):
        raise ValueError("Inconsistent lengths of lists in data_samples.")
    print("Data format validation successful.")
    


validate_data_format(data_samples)
my_dataset = Dataset.from_dict(data_samples)
print("Dataset Format:" , my_dataset ,  "\n")



results_rag = evaluate(
    dataset = my_dataset,
    metrics = metrics,
)
print("RAGAS Evaluation Results:" , results_rag , "\n")
df_results = results_rag.to_pandas()
df_results.to_csv("ragas_eval_results.csv", index=False)
print(df_results)