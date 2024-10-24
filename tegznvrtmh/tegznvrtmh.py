# Please replace APIKEY and ProjectID
import os
import re
import time
from langchain_ibm import WatsonxLLM
import concurrent.futures
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime
import numpy as np

os.environ['WATSONX_APIKEY'] = "WATSONX_APIKEY"

def generate_response(prompt, model):
    '''
    Generates a response from a given prompt using a specified model.
    '''
    if 'ibm/granite' in model:
        header = ''
        footer = ''
    if 'mistralai/' in model:
        header = '<s>[INST]'
        footer = '[/INST]</s>'
    if 'meta-llama/llama' in model:
        header = '<|begin_of_text|><|start_header_id|>user<|end_header_id|>'
        footer = '<|eot_id|><|start_header_id|>assistant<|end_header_id|>'

    parameters = {
    "decoding_method": "sample",
    "min_new_tokens": 1,
    "max_new_tokens": 4096,
    "stop_sequences": [],
    "repetition_penalty": 1,
    'temperature': 0
    }

    prompt_new = prompt.format(header=header, footer=footer)
    watsonx_llm = WatsonxLLM(model_id=model, url="https://us-south.ml.cloud.ibm.com",
    project_id='ProjectID', params=parameters)
    response = watsonx_llm.invoke(prompt_new)
    return re.sub(r"\*\*([^*]+)\*\*", r"\1", response)

@dataclass
class ResponseMetrics:
    """Class to store response and its metrics"""
    response: str
    processing_time: float
    start_time: datetime
    end_time: datetime
    token_count: int = 0
    cost_per_token: float = 0.0
    conciseness_score: float = 0.0

def count_tokens(text: str) -> int:
    """
    Simple token count estimation.
    """
    return int(len(text.split())*0.75)

def calculate_conciseness_score(response: str) -> float:
    """
    Calculate conciseness score based on response length and content.
    """
    words = response.split()
    ideal_length = 50  # adjust based on your needs
    length_score = 1 - min(abs(len(words) - ideal_length) / ideal_length, 1)
    return length_score

def get_cost_per_1k_token(model: str) -> float:
    """
    Get cost per token for different models.
    """
    cost_mapping = {
        'meta-llama/llama-3-1-70b-instruct': 0.0018,
        'meta-llama/llama-3-70b-instruct': 0.0010,
        'meta-llama/llama-3-8b-instruct': 0.0005,
        'ibm/granite-13b-chat-v2':0.0006,
        'ibm/granite-20b-multilingual':0.0006,
        'mistralai/mistral-large':0.01,
        'mistralai/mixtral-8x7b-instruct-v01':0.0006
    }
    return cost_mapping.get(model)

def generate_responses_parallel(prompt_list: List[str], model_list: List[str]) -> Dict[str, Dict[str, ResponseMetrics]]:
    """
    Generate responses for multiple prompts and models in parallel using ThreadPoolExecutor.
    """
    results = {}
    total_start_time = time.time()
    
    def process_single_combination(prompt: str, model: str) -> tuple:
        """Helper function to process a single prompt-model combination"""
        start_time = datetime.now()
        start_processing = time.time()
        
        try:
            response = generate_response(prompt, model)
            processing_time = time.time() - start_processing
            end_time = datetime.now()
            
            # Calculate additional metrics
            token_count = count_tokens(prompt+response)
            cost_per_1k_token = get_cost_per_1k_token(model)
            conciseness_score = calculate_conciseness_score(response)
            
            metrics = ResponseMetrics(
                response=response,
                processing_time=processing_time,
                start_time=start_time,
                end_time=end_time,
                token_count=token_count,
                cost_per_token=cost_per_1k_token,
                conciseness_score=conciseness_score
            )
            return (prompt, model, metrics)
        except Exception as e:
            processing_time = time.time() - start_processing
            end_time = datetime.now()
            
            metrics = ResponseMetrics(
                response=f"Error: {str(e)}",
                processing_time=processing_time,
                start_time=start_time,
                end_time=end_time
            )
            
            return (prompt, model, metrics)

    # Create a list of all prompt-model combinations
    combinations = [(prompt, model) 
                   for prompt in prompt_list
                   for model in model_list]
    
    # Initialize results dictionary
    results = {prompt: {} for prompt in prompt_list}
    
    # Use ThreadPoolExecutor for parallel processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(combinations), 10)) as executor:
        future_to_combo = {
            executor.submit(process_single_combination, prompt, model): (prompt, model)
            for prompt, model in combinations
        }
        
        for future in concurrent.futures.as_completed(future_to_combo):
            prompt, model = future_to_combo[future]
            try:
                prompt_result, model_result, metrics = future.result()
                results[prompt_result][model_result] = metrics
            except Exception as e:
                end_time = datetime.now()
                results[prompt][model] = ResponseMetrics(
                    response=f"Error in processing: {str(e)}",
                    processing_time=0.0,
                    start_time=end_time,
                    end_time=end_time
                )
    total_time = time.time() - total_start_time
    print(f"Total processing time: {total_time:.2f} seconds")
    return results

def print_detailed_statistics(results):
    """
    Print both per-prompt and aggregate statistics with detailed latency analysis.
    """
    # Per-prompt statistics
    print("\nPer-Prompt Statistics:")
    print("=" * 80)
    
    for prompt in results:
        prompt_latencies = []
        prompt_costs = []
        prompt_conciseness = []
        model_metrics = {}
        
        # Collect metrics for this prompt
        for model, metrics in results[prompt].items():
            prompt_latencies.append(metrics.processing_time)
            prompt_costs.append((metrics.token_count * metrics.cost_per_token))
            prompt_conciseness.append(metrics.conciseness_score)
            model_metrics[model] = metrics.processing_time
        prompt = prompt.replace('{header}','').replace('{footer}','')

        # Print prompt-specific statistics
        print(f"\nPrompt: {prompt[:100]}...")  # Show first 100 chars of prompt
        print(f"Latency Statistics:")
        print(f"  Average Latency: {np.mean(prompt_latencies):.2f} seconds")
        print(f"  Best Latency: {min(prompt_latencies):.2f} seconds")
        print(f"     Model: {min(model_metrics.items(), key=lambda x: x[1])[0]}")
        print(f"  Worst Latency: {max(prompt_latencies):.2f} seconds")
        print(f"     Model: {max(model_metrics.items(), key=lambda x: x[1])[0]}")
        
        print(f"\nCost and Conciseness:")
        print(f"  Best Cost: {min(prompt_costs):.5f}")
        print(f"     Model: {min(model_metrics.items(), key=lambda x: x[1])[0]}")
        print(f"  Worst Cost: {max(prompt_costs):.5f}")
        print(f"     Model: {max(model_metrics.items(), key=lambda x: x[1])[0]}")
        print(f"  Average Conciseness Score: {np.mean(prompt_conciseness):.2f}")
        print("-" * 80)
    
    all_model_metrics = {}
    for prompt in results:
        for model, metrics in results[prompt].items():
            if model not in all_model_metrics:
                all_model_metrics[model] = {'latency':[], 'cost':[]}
            
            all_model_metrics[model]['latency'].append(metrics.processing_time)
            all_model_metrics[model]['cost'].append(metrics.token_count * metrics.cost_per_token)
    
    print("\nOverall Aggregate Statistics:")
    print("\nPer-Model Performance:")
    for model in all_model_metrics:
        model_metrics = all_model_metrics[model]
        print(f"\n  {model}:")
        print(f"    Average Latency: {np.mean(model_metrics['latency']):.2f} seconds")
        print(f"    Average Cost: {np.mean(model_metrics['cost']):.2f}")
        
model_list = [
    'meta-llama/llama-3-1-70b-instruct',
    'meta-llama/llama-3-70b-instruct',
    'mistralai/mistral-large'
]
prompt1 = "{header}What is the capital of France?{footer}"
prompt2 = '''{header}
You are tasked with reviewing system engineering requirements according to INCOSE guidelines. For the given requirement statement, 
your objective is to list the specific INCOSE rules that are failing, along with brief explanations of why they are failing. 
The output should be formatted as a JSON array where each item follows this pattern:

- Rule number: A reference to the INCOSE rule that is failing (e.g., "R1 - Structured Statements")
The input is as follows:

Input requirement: The system should be fast.
Output:
{footer}
'''
prompt_list = [prompt1, prompt2]

# Generate responses
results = generate_responses_parallel(prompt_list, model_list)

# Print detailed statistics
print_detailed_statistics(results)