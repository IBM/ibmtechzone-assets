import os
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import Model


def get_credentials():
	return {
        #Setting the environment credentials : "IBM_CLOUD_URL" & "IBM_CLOUD_API_KEY" from .env file
		"url" : os.environ["ibm_cloud_url"),
		"apikey" : os.environ("ibm_cloud_api_key")
	}

def javaCodeGen():

    load_dotenv()

    #Project ID Configuration  
    project_id = os.environ("project_id")
    
    #LLM model Configuration 
    model_mistral_large='mistralai/mistral-large'
    parameters_mistral= {
         'decoding_method': 'sample',
         'max_new_tokens': 16384,
         "random_seed": 3,
         'temperature': 0.45,
         'top_k': 50,
         'top_p': 1, 
         'repetition_penalty': 1
    }

    #Model Initialization
    print("Initializing LLM model...")
    model = Model(
  	model_id = model_mistral_large,
  	params = parameters_mistral,
  	credentials = get_credentials(),
  	project_id = project_id
    )
    
    Code_Specific_Condition = os.environ["code_specific_condition"]
    
    Embedded_Condition = os.environ["embedded_Condition"]
    
    Variable_Names_Datatypes = os.environ["variable_names_datatypes"]
    
    Older_version_Pseudocode = os.environ["older_version_pseudocode"]
    
    Older_version_Java_Code = os.environ["older_version_javaCode"]
    
    New_version_Pseudocode = os.environ["new_version_pseudocode"]
    
    prompt_input_base = f"""     
    ROLE: You are an excellent agent focused on creating accurate and efficient Java code. 

    JOB: Consider the provided older version of pseudocode, older version of javacode as a example java code. Generate the New version Java code according to New version Pseudocode. New version Java code must contain the updated logic made in the New version Pseudocode. 

    RESTRICTIONS:
    1. Required to generate the code without object oriented programming concepts. Only code snippet is required.
    2. First Understand the older version pseudocode and its corresponding older version of javacode then compare the New version Pseudocode with older version Pseudocode. Strictly consider the updation made in New version Pseudocode.
    3. You must use the same parameter names for the java function call which was mention in the older version Java Code. 
    4. You may use the same variable names of older version Java Code in New version Java code.
    5. The changes made in the new version Java code must be included in the New version Java code.
    6. Use the English translated variable names from the Japanese written New version Pseudocode.
    7. Use the java built-in constant null value to validate the variables with null.
    8. Variable declaration and initialisation are required only when its mentioned in New version Pseudocode.
    9. You need to use the Constant variable names for Constant characters and Constant numbers.
    10. You need to embed Java `||` operator for the Japanese word "または" and embed Java `&&` operator for the japanese word "かつ". 
    11. You need to focus only on the code generation.
    12. You need to use `Objects.nonNull` to validate the Objects is nonNull.

    CASE SPECIFIC RESTRICTION CONDITION:
    {Code_Specific_Condition}

    JAPANESE WORD AND ITS SPECIFIC MEANING DEFINITION:
    Explicitly Define the Word and Its Specific Meaning: Clearly state the specific meaning of the word you want to embed.
    Japanese word Tag Name is "JAPANESE WORD" and Value is "SPECIFIC MEANING DEFINITION".
    {Embedded_Condition}

    VARIABLE NAMES AS A JAPANESE WORD AND ITS JAVA DATA TYPES:
    Explicitly assigned the Java data types that should be use for java variable names.
    Japanese word Tag Name is "JAPANESE WORD" and Value is "JAVA DATA TYPES"
    {Variable_Names_Datatypes}

    Example older version Pseudocode:
    {Older_version_Pseudocode}

    Example older version Java Code:
    {Older_version_Java_Code}

    Input New version Pseudocode: 
    {New_version_Pseudocode_001}

    FORMAT: 
    1. Strictly follow that you should print the new version java code inside this grave accent symbol.
    ```

    ```

    Output New version Java code:

    Output:"""

    #LLM Respose Generation
    print("Submitting generation request...")
    generated_response = model.generate_text(prompt=prompt_input_base)
    return generated_response

if __name__ == '__main__':

    code=javaCodeGen()
    print(code)

