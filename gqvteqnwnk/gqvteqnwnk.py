import traceback
from langchain_ibm import WatsonxLLM
import re
import os

os.environ['WATSONX_APIKEY'] = "YOUR API KEY"

def generate_response(prompt, temperature):
    parameters = {
    "decoding_method": "sample",
    "min_new_tokens": 1,
    "max_new_tokens": 4096,
    "stop_sequences": [],
    "repetition_penalty": 1,
    'temperature': temperature
    }
    watsonx_llm = WatsonxLLM(
    model_id='meta-llama/llama-3-1-70b-instruct',
    url="https://us-south.ml.cloud.ibm.com",
    project_id='PROJECT ID',
    params=parameters
    )
    response = watsonx_llm.invoke(prompt)
    return re.sub(r"\*\*([^*]+)\*\*", r"\1", response)

def auto_debugger(code, temperature):
    error_message = error_prompt.format(code_description = code_description, traceback = traceback.format_exc(), code = code)
    debugged_code = generate_response(error_message, temperature)
    print(debugged_code)
    return debugged_code[1:]

error_prompt = '''
<|begin_of_text|><|start_header_id|>user<|end_header_id|>
You are an expert coder! Debug the below code for me.
Code Description: {code_description}
Traceback of the code: {traceback}
Code: {code}

Adhere to below instructions at all costs!
Instruction:
1. Identify the cause of the error and rewrite the code - make it error free
2. Don't include any text in your response at any cost
3. Rewrite the code as a function
4. Follow these instructions by all means

Example:
USER INPUT- 
Code Description: Code to check whether the number is odd or even
Traceback Error: SyntaxError: cannot assign to expression here. Maybe you meant '==' instead of '='?
Code: 
def check_odd_even(number):
    if number % 2 = 0:
        result = "Even."
    else:
        result = "Odd."
    return result

num = int(input("Enter a number: "))
result = check_odd_even(num)

OUTPUT (Debugged Code) -
def check_odd_even(number):
    if number % 2 == 0:
        result = "Even."
    else:
        result = "Odd."
    return result

num = int(input("Enter a number: "))
result = check_odd_even(num)
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
'''

temperature, iteration, limit = -0.2, 0, 2
code_description = '''A function that that takes a list of numbers as input and returns the sum of all even numbers. If no even numbers are found, return zero'''

# Introducing an intensional error to demonstrate the working of auto debugger
code = '''
def sum_even_numbers(numbers):
    total = 0  # Initialize the total sum variable
    for num in numbers:
        if num % 2 == 0:  
            total += "num" 
    return total  # Return the sum of even numbers

# Example usage
numbers = [1, 2, 3, 4, 5, 6]
result = sum_even_numbers(numbers)
print(f"The sum of even numbers is: {result}")
'''
result = ''
while iteration < limit:
    try:
       dynamic_dict = {'code': code, 'result': result}
       print('Code  ---->', code)
       exec(code, dynamic_dict)
       result = dynamic_dict['result']
       break
    except Exception as e:
        print('Error ---->', e, end='\n\n')
        temperature += 0.2
        print(f'Iteration: {iteration}')
        code = auto_debugger(code, temperature).replace('`', '').replace('python', '')
        iteration+=1
        print('----------------------------------------------------------------')

if iteration==limit: 
    print('Max tries reached: Code was not debugged - please tune the prompt based on your use case.')
else:
    print('\n\nAfter Code Execution: ', result)