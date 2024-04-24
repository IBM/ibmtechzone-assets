
### Querying Pandas Dataframe

#### importing libraries


from genai.model import Credentials, Model
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)
if api_key is None or api_endpoint is None:
    print("Ensure you copied the .env file that you created earlier into the same directory as this notebook")
else:
    creds = Credentials(api_key=api_key, api_endpoint=api_endpoint)

model_id = "meta-llama/llama-2-70b-chat"

generation_params = {
                               "decoding_method": "sample",
                                "max_new_tokens": 256,
                                "stop_sequences": ["\n\n\n"],
                                "temperature": 0.1,
                                "top_k": 50,
                                "top_p": 1,
                                "repetition_penalty": 1
                                }

model = Model(model_id, params=generation_params, credentials=creds)

import pandas as pd
data = {'ID': [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35],
        'Experience_Years': [5,1,3,2,1,25,19,2,10,15,4,6,14,11,2,4,10,15,2,10,15,4,5,1,4,3,1,27,19,2,10,15,20,19,16],
        'Age': [28,21,23,22,17,62,54,21,36,54,26,29,39,40,23,27,34,54,21,36,54,26,29,21,23,22,18,62,54,21,34,54,55,53,49],
        'Gender': ['Female','Male','Female','Male','Male','Male','Female','Female','Female','Female','Female','Male','Male','Male','Male','Female','Female','Female','Male','Male','Male','Male','Male','Female','Female','Female','Male','Female','Female','Female','Male','Male','Female','Female','Male'],
        'Salary': [250000,50000,170000,25000,10000,5001000,800000,9000,61500,650000,250000,1400000,6000050,220100,7500,87000,930000,7900000,15000,330000,6570000,25000,6845000,6000,8900,20000,3000,10000000,5000000,6100,80000,900000,1540000,9300000,7600000],
        'Name': ['sakshi','pradumn','ruhi','ronak','abhay','john','kushi','anusha','vennela','ankitha','abhilasha','vivek','vinay','amogh','akash','karunya','parinitha','bhumika','rudresh','pati','varun','karan','shaily','ekta','raksha','shreya','mahi','shivangi','saloni','sanvi','shivank','avinash','neela','rashmi','manav']}
df = pd.DataFrame(data)

columns = df.columns
shape = df.shape

question = "find me a male employee who is getting highest salary?"
prompt = f'''<s>
<<SYS>>\n
[INST]
Generate corresponding pandas code to solve the following question:
[/INST]
Question:
"How many unique values are there in the 'name' column?"
DataFrame columns: ['id', 'name', 'age', 'city']
DataFrame shape: (100, 4)
Code:
df['name'].nunique()

Question:
"What is the average age of people in the 'city' column with value 'New York'?"
DataFrame columns: ['id', 'name', 'age', 'city']
DataFrame shape: (100, 4)
Code:
df[df['city'] == 'New York']['age'].mean()

Question:
"How many rows have 'age' greater than 25?"
DataFrame columns: ['id', 'name', 'age', 'city']
DataFrame shape: (100, 4)
Code:
len(df[df['age'] > 25])
\n<<SYS>>\n\n
Question:
{question}
DataFrame columns: {columns}
DataFrame shape: {shape}
code :
'''

def send_to_watsonxai(prompts):
        for response in model.generate(prompts):
            return response.generated_text

response = send_to_watsonxai(prompts=[prompt])

response