import pandas as pd
import numpy as np
import time
from dotenv import dotenv_values
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models import Model 
from bert_score import BERTScorer
from rouge import Rouge
scorer = BERTScorer(lang="en", rescale_with_baseline=True)

"""
LLM Hyperparameter tuning.
"""

# Load environment variables from the file
watsonx_env = dotenv_values('watsonx_credentials.env')

watsonx_project_id = watsonx_env.get('PROJECT_ID')
watsonx_apikey = watsonx_env.get('WATSONX_APIKEY')                    
ibmcloud_apikey = watsonx_env.get('IBMCLOUD_APIKEY')                     
watsonx_url = watsonx_env.get('WATSONX_URL')                                

watsonx_credentials = {
    "url": watsonx_url,
    "apikey": ibmcloud_apikey
}

search_params = {
    "metric_type": "IP", 
    "ignore_growing": False, 
    "params": {"nprobe": 32}
}

def calculate_bert_score(answer,groundtruth):
    """
    Calculate Bert Score for 'answer' and 'ground_truth'.
    """
    P, R, F1 = scorer.score([answer], [groundtruth], verbose=False)
    return F1.item()
   
def calculate_rouge_l_score(answer,groundtruth):
    """
    Calculate ROUGE-L score for 'answer' and 'ground_truth'.

    Args:
    - row: pandas Series representing a row of the DataFrame.

    Returns:
    - Returns the ROUGE-L score representing the similarity between the hypothesis and reference.
    """

    # Initialize Rouge
    rouge = Rouge()

    # Calculate ROUGE scores
    scores = rouge.get_scores(answer, groundtruth, avg=True)
    
    # Extract ROUGE-L score
    rouge_f1 = scores['rouge-l']['f']
    
    return rouge_f1

def evaluate_model(eval_data, model_id):
    """ 
    Function to evaluate the performance of a model with different parameters on a given dataset.

    Args:
        - eval_data (DataFrame): DataFrame containing the evaluation dataset (dataframe with question and groundtruth column).
        - model_id (str): Identifier for the LLAMA model to be used.

    Returns:
        - row_with_highest_score (Series): Series containing the row with the highest average score.
    """
    
    temperatures = [0.1, 0.2, 0.5, 0.8]
    top_ps = [0.3, 0.5, 0.6, 0.7]
    top_ks = [10, 30, 50]
    num_metrics=2

    # Initialize lists to store results
    temp_list = []
    top_p_list = []
    top_k_list = []
    time_taken_list = []  
    average_scores_list=[]


    # Iterate over each combination of temperature, top_p, and top_k parameters to evaluate the model's performance.
    for temperature in temperatures:
        for top_p in top_ps:
            for top_k in top_ks:
                llm_params = {GenParams.MAX_NEW_TOKENS: 500, GenParams.MIN_NEW_TOKENS: 50, 
                              GenParams.TEMPERATURE: temperature, GenParams.TOP_P: top_p, GenParams.TOP_K: top_k}
                print("LLM parameters used", llm_params)
                # Initialize the LLAMA model with the current set of parameters.
                try:
                    model_2 = Model(
                        model_id=model_id,
                        params=llm_params,  
                        credentials=watsonx_credentials,
                        project_id=watsonx_project_id)

                    # Initialize lists to store scores and time taken for each question
                    bert_scores = []
                    rouge_scores = []
                    perplexity_scores = []
                    time_taken = []

                    # Iterate through each question in the evaluation dataset to generate LLAMA-2 answers and calculate scores.
                    for index, row in eval_data.iterrows():
                        start_time = time.time()
                        question = row['question']
                        pdf_context, pdf_titles = get_context_and_pdf_details(question,search_params)
                        prompt_text = make_prompt(question, pdf_context, pdf_titles)
                        llama_answer = model_2.generate_text(prompt=prompt_text)
                        end_time = time.time()
                        ## time computation
                        time_taken.append(end_time - start_time)
                        ## scores computation
                        bert_f1 = calculate_bert_score(llama_answer,row["groundtruth"])
                        bert_scores.append(bert_f1)
                        rouge_f1 = calculate_rouge_l_score(llama_answer,row["groundtruth"])
                        rouge_scores.append(rouge_f1)


                    
                    sum_bert_score = sum(bert_scores)
                    sum_rouge_score = sum(rouge_scores)
                    total_time_taken=sum(time_taken)
                    
                    # Append results to lists
                    temp_list.append(temperature)
                    top_p_list.append(top_p)
                    top_k_list.append(top_k)
                    time_taken_list.append(total_time_taken)
                    average_scores_list.append((sum_bert_score+ sum_rouge_score)/ num_metrics * len(eval_data))

                except Exception as e:
                    # Handle any exceptions that occur during model initialization or LLAMA answer generation
                    print(f"Error occurred: {e}")
                

    # Creating a results DataFrame to store evaluation results.
    results_df = pd.DataFrame({
        'Temperature': temp_list,
        'Top_p': top_p_list,
        'Top_k': top_k_list,
        'Total_Time_Taken': time_taken_list,
        'Average_Score_all_ques': average_scores_list
    })

    # Calculate average time taken
    results_df['Average_Time_per_question'] = results_df["Total_Time_Taken"] / len(eval_data)
    # Find the index of the row with the highest average score
    max_score_index = results_df['Average_Score_all_ques'].idxmax()

    # Retrieve the row with the highest average score
    row_with_highest_score = results_df.loc[max_score_index]

    return row_with_highest_score


if __name__ == "__main__":

    golden_data = pd.read_csv("Golden_questions.csv",index=False)
    row_with_highest_score = evaluate_model(eval_data=golden_data,model_id='meta-llama/llama-2-70b-chat')
    print(row_with_highest_score)