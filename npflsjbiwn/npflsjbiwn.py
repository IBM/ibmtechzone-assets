import os
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import Model


def get_credentials():
	return {
        #Setting the environment credentials : "IBM_CLOUD_URL" & "IBM_CLOUD_API_KEY" from .env file
		"url" : os.environ["ibm_cloud_url"],
		"apikey" : os.environ["ibm_cloud_api_key"]
	}

#Here you can add your old pseudocode
older_version_Pseudocode = os.environ["sample_pseudocode"]

#Here you can add your old java code
older_version_Java_Code = os.environ["sample_java_code"]

#Here you can add your new pseudocode
New_version_Pseudocode = os.environ["new_pseudocode"]

#Prompt for java code generation based on the provided pseudocode.
prompt_input = f"""Input: You are an excellent agent focused on creating accurate and efficient Java code. Consider the provided older version of pseudocode, older version of javacode as a example. Generate the New version Java code according to New version Pseudocode. New version java code must be compatible with stable JDK(java development version) version. Generated New version Java code must contain the updated logic made in the New version Pseudocode. 
***IMPORTANT CONDITIONS AND STEPS TO FOLLOW IN NEW VERSION JAVA CODE GENERATION PROCESS :
1. Required to generate the code without object oriented programming concepts. Only code snippet is required.
2. First Understand the older version pseudocode and its corresponding older version of javacode then compare the New version Pseudocode with older version Pseudocode. Strictly consider the updation made in New version Pseudocode.
3. You must use the same parameter names for the java function call which was mention in the older version Java Code. 
4. You may use the same variable names of older version Java Code in New version Java code.
5. The changes made in the new version Java code must be included in the New version Java code.
6. Use the IF condition validation like written in older version Java Code.
7. Use the English translated variable names from the Japanese written New version Pseudocode.
8. Use StringUtil.isBlank java in-built method to validate that the variable whether it contains whitespace character or not.

older version Pseudocode:
{older_version_Pseudocode}

older version Java Code:
{older_version_Java_Code}

New version Pseudocode: 
{New_version_Pseudocode:}

New version Java code:

Output:"""


def javaCodeGen():

    load_dotenv()

    #LLM model Configuration  
    model_id = "mistralai/mixtral-8x7b-instruct-v01"
    #Project ID Configuration  
    project_id = os.environ["project_id"]

    #Setting up the LLM parameters
    parameters = {
    "decoding_method": "sample",
    "max_new_tokens": 3000,
    "random_seed": 3,
    "temperature": 0.45,
    "top_k": 50,
    "top_p": 1,
    "repetition_penalty": 1
    }
    
    #Model Initialization
    print("Initializing LLM model...")
    model = Model(
	model_id = model_id,
	params = parameters,
	credentials = get_credentials(),
	project_id = project_id
    )

    #LLM Respose Generation
    print("Submitting generation request...")
    generated_response = model.generate_text(prompt=prompt_input)
    return generated_response

if __name__ == '__main__':

    code=javaCodeGen()
    print(code)