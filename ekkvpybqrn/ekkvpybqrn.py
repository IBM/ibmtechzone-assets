#!/usr/bin/env python
# coding: utf-8

# @hidden_cell
# The project token is an authorization token that is used to access project resources like data sources, connections, and used by platform APIs.
from project_lib import Project
project = Project(project_id='PRJ-ID', project_access_token='TOKEN')
pc = project.project_context

from ibm_watson_studio_lib import access_project_or_space
wslib = access_project_or_space({'token':'ACCESS-TOKEN'})

import watson_nlp
import pandas as pd
from tqdm import tqdm
from langchain_ibm import WatsonxLLM
import numpy as np
import multiprocessing
import time
import os
import re
from watson_nlp.blocks.classification.transformer import Transformer
from watson_core.data_model.streams.resolver import DataStreamResolver

os.environ["WATSONX_APIKEY"] = 'API-KEY'

def train_model(training_data_file, model_name, target_column):
    batch_size = 64
    epochs = 50
   
    # create datastream from training data
    data_stream_resolver = DataStreamResolver(target_stream_type=list, expected_keys={'TEXT': str, target_column: str})
    train_stream = data_stream_resolver.as_data_stream(training_data_file)
    #dev_stream = data_stream_resolver.as_data_stream(test_data_file)

    # Load pre-trained Slate model
    pretrained_model_resource = watson_nlp.load('pretrained-model_slate.153m.distilled_many_transformer_multilingual_uncased')

    # Train model
    model = Transformer.train(train_stream, pretrained_model_resource, num_train_epochs=epochs, train_batch_size=batch_size, verbose=2, learning_rate=5e-5)
    model.save(model_name)
    return model

def clean_text(text):

    # Remove non-alphanumeric characters
    text = re.sub(r'[^a-zA-Z0-9]', ' ', text)

    # Reduce multiple spaces to a single space
    text = re.sub(r'\s+', ' ', text)
    return text

def generate_response(prompt):
    parameters = {
    "decoding_method": "sample",
    "min_new_tokens": 1,
    "max_new_tokens": 4096,
    "stop_sequences": [],
    "repetition_penalty": 1,
    'temperature': 0
    }
    watsonx_llm = WatsonxLLM(
    model_id="meta-llama/llama-3-1-70b-instruct",
    url="https://us-south.ml.cloud.ibm.com",
    project_id='PROJECT-ID',
    params=parameters
    )

    response = watsonx_llm.invoke(prompt)
    return response

def oversample_data(text):
    prompt = f'''
    <|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are an expert english paraphraser. Generate new sentences by adhering to the INSTRUCTIONS shared below.
    
    ABOUT TEXT:
    1. The text comprises of 8 complaints regarding a car's part/model each represented by ">"
    
    INSTRUCTIONS:
    1. Respond by generating 5 new complaints from the user complaints mentioned in the text at all cost!
    2. Generate 5 new complaints by paraphrasing or by changing the way it is written in the TEXT section
    3. Don't include any irrelevant information. Generate only relevant text.
    4. Don't include any header or footer in your response at any cost!
    5. Each new complaint should be represented by ">" by all means!
    6. Maintain the same format/style of the text that has been written in the TEXT section
    7. The new complaints shouldn't be similar to the original complaints at all - I need new ones!
    8. Only keep the car's part/model same, rest change the entire sentence.
    
    Expected Input:
    >Complaint 1
    >Complaint 2
    >Complaint 3
    >Complaint 4
    >Complaint 5
    >Complaint 6
    >Complaint 7
    >Complaint 8
    
    Expected Output:
    >New Complaint 1
    >New Complaint 2
    >New Complaint 3
    >New Complaint 4
    >New Complaint 5
    >New Complaint 6
    >New Complaint 7
    >New Complaint 8
    
    TEXT:
    {text}
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    '''
    response = generate_response(prompt)
    return response

def generate_new_samples(df, class_name):
    final_list = []
    original_df = df[df.COMPO_CODE==class_name]
    new_df = df[df.COMPO_CODE==class_name].sample(frac = 1).reset_index()
#     print(f'Class samples before - {class_name}',new_df.shape)
    new_complaints = []
    for i in range(0, len(new_df), 8):
        try:
            text = '>'
            text += '\n>'.join(new_df['TEXT'].iloc[i:i+8].to_list())
            response = oversample_data(text)

            idx = response.index('>')
            response = response[idx:]
            response = response.split('>')
#             print(len(response))
            new_complaints.extend([resp for resp in response if resp not in ('\n', ' ', '')])
        except Exception as e:
            print('Printing Error: ', e)
            pass
    for complaint in new_complaints:
        if 'New Complaint' not in complaint:
            final_list.append(complaint)

    new_class_list = [class_name]*len(final_list)
    text_list = new_df.TEXT.to_list()
    class_list = new_df.COMPO_CODE.to_list()
    
    text_list += final_list
    class_list += new_class_list
    
    new_df = pd.DataFrame()
    new_df['TEXT'] = text_list
    new_df['COMPO_CODE'] = class_list
    new_df = pd.concat([original_df, new_df])
#     print(f'Class samples after - {class_name}', new_df.shape)
    return new_df

def worker(class_name):
    return generate_new_samples(train_set, class_name)

files = ['COMPO_CODE_TRAIN_EN_Large.csv', 'COMPO_CODE_TEST_EN.csv']

df = pd.DataFrame()
for file in files:
    wslib.download_file(file)
    
# Reading trainset
df_train = pd.read_csv(files[0])
train_set = df_train[df_train.COMPO_CODE!='     '].reset_index(drop=True)
train_set.TEXT = [text.lower() for text in train_set.TEXT]
print(train_set.shape)

# Removing special characters
list_of_cleaned_text = []
for text in tqdm(train_set.TEXT):
    cleaned_text = clean_text(text)
    list_of_cleaned_text.append(cleaned_text)
train_set.TEXT = list_of_cleaned_text

# Oversampling only those classes whose num of samples<median num of samples
class_distribution = dict(train_set.COMPO_CODE.value_counts())
median_value = np.median(np.array(list(class_distribution.values())))
classes_less_than_median = [class_name for class_name in class_distribution if class_distribution[class_name]<median_value]
print(len(classes_less_than_median))

# Parallel Process - Oversampling
start = time.time()
with multiprocessing.Pool(processes=20) as pool:
    with tqdm(total=len(classes_less_than_median), desc="Processing classes") as pbar:
        results = pool.imap_unordered(worker, classes_less_than_median)
        oversampled_df = pd.concat(results, ignore_index=True)
        pbar.update(1)
end = time.time()
print('Total Time taken in mins: ', round((end-start)/60, 2))
print(oversampled_df.shape)

# Concatenating oversampled data
oversampled_df = oversampled_df.reset_index(drop=True)
oversampled_df = pd.concat([train_set[~train_set.COMPO_CODE.isin(classes_less_than_median)], oversampled_df]).reset_index(drop=True)
oversampled_df = oversampled_df[['TEXT', 'COMPO_CODE']]
print(oversampled_df.shape)

# Saving oversampled files
oversampled_df.to_csv('compo_code_oversampled_data.csv', index=False)
wslib.upload_file('compo_code_oversampled_data.csv', overwrite=True)

file_name = 'compo_code_oversampled_data.csv'
model_name = 'model_compo_code_en'
model = train_model(file_name, model_name, 'COMPO_CODE')
get_ipython().system('zip -r model_compo_code_en.zip model_compo_code_en')
wslib.upload_file(model_name+'.zip', overwrite=True)

# Reading test file
df_test = pd.read_csv(files[1])
print(df_test.shape)

# Excluding specific classes
exclude_classes = set(df_test.COMPO_CODE).difference(set(oversampled_df.COMPO_CODE))
df_test = df_test[~df_test.COMPO_CODE.isin(exclude_classes)].reset_index(drop=True)

# Evaluations - Calculating top 1, 3 and 5 accuracy
results = []
top_5_sum = 0
top_3_sum = 0
top_1_sum = 0

for i in tqdm.tqdm(range(len(df_test.index))):
    result = model.run(df_test.iloc[i]["TEXT"]).to_dict()
    result_dict = {
        "Top1": result["classes"][0]["class_name"],
        "Top2": result["classes"][1]["class_name"],
        "Top3": result["classes"][2]["class_name"],
        "Top4": result["classes"][3]["class_name"],
        "Top5": result["classes"][4]["class_name"]
    }
    results.append(result_dict)
    
    if result["classes"][0]["class_name"] == df_test.iloc[i]["COMPO_CODE"]:
        top_1_sum += 1
        top_3_sum += 1
        top_5_sum += 1
    elif result["classes"][1]["class_name"] == df_test.iloc[i]["COMPO_CODE"]:
        top_3_sum += 1
        top_5_sum += 1
    elif result["classes"][2]["class_name"] == df_test.iloc[i]["COMPO_CODE"]:
        top_3_sum += 1
        top_5_sum += 1
    elif result["classes"][3]["class_name"] == df_test.iloc[i]["COMPO_CODE"]:
        top_5_sum += 1
    elif result["classes"][4]["class_name"] == df_test.iloc[i]["COMPO_CODE"]:
        top_5_sum += 1

print("Top1 Accuracy: {0}".format(top_1_sum/len(df_test.index)))
print("Top3 Accuracy: {0}".format(top_3_sum/len(df_test.index)))
print("Top5 Accuracy: {0}".format(top_5_sum/len(df_test.index)))