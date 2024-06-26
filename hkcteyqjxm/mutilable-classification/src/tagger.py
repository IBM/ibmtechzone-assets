import os
from langchain.docstore.document import Document
from utils import process_text_files, get_text_chunks, add_to_vector_store, get_similar_doc, get_similar_text
from test_case_utils import get_test_case_samples, get_test_case_samples_discovery
from langchain.prompts import PromptTemplate
import getpass
import json
import pandas as pd
from ibm_watsonx_ai.foundation_models import Model
from prompt import tagger_prompt, topic_specific_prompt, test_case_prompt, segregate_prompt
from itertools import islice
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models import ModelInference
from dotenv import load_dotenv, find_dotenv

RETRIEVE_THRESHOLD_LIMIT = 30
REPEAT_THRESHOLD = 5
MAX_SUBSYSTEM_TAGS = 12

sub_system = (os.linesep).join(["Below is the sample text that belongs to topic named {} :","{}",os.linesep])
reiterate_exceptions = "Generate the Output by understanding listed exceptions."

def get_credentials():
    return {"url": os.getenv("GA_URL"), "apikey": os.getenv("GA_API_KEY")}

def get_file_dict():
    file_dict = {
       ** Your text file dict goes here **
    }
    return file_dict

def get_subsystems():
    key_arr = [(k) for k in get_file_dict().keys()]
    return (os.linesep+"- ").join(key_arr)

def take(n, iterable):
    """Return the first n items of the iterable as a list."""
    return list(islice(iterable, n))

def get_sample_subsystem_topics(text_for_tagging):
    result_set = get_similar_doc(text_for_tagging, item_count=RETRIEVE_THRESHOLD_LIMIT)
    topic_list = []
    subsystem_dict = {}
    print("RESULT SET LENGTH:",len(result_set))
    for resultant in result_set:
        current_topic = resultant.metadata['topic']
        if topic_list.count(current_topic) <= REPEAT_THRESHOLD:
            topic_list.append({"Topic":current_topic,"Content":resultant.page_content})
    return list(topic_list)

def check_exception_cases(text):
    exception_list_txt = ['install','depot','rolling']
    for excep in exception_list_txt:
        if excep in text.lower():
            return True
    return False

def build_subsystem_samples(subsystem_dict):
    final_subsystem_text = ""
    for index in range(len(subsystem_dict)):
        arr = []
        for key,values in ((subsystem_dict[index]).items()):
            arr.append(values)
        #print(arr)
        if len(arr)==2:
            subsytem_text = sub_system.format(arr[0], arr[1])
            final_subsystem_text = (os.linesep).join([final_subsystem_text,subsytem_text])
    return final_subsystem_text

def get_prompt(example_for_topics, input):
    prompt = PromptTemplate(
        template=tagger_prompt, input_variables=["topic_list", "example_for_topics", "reiterate","input"]
    )
    tag_prompt = prompt.format(
        topic_list = get_subsystems(),
        example_for_topics = example_for_topics,
        reiterate = reiterate_exceptions if check_exception_cases(input) else "",
        input = input
    )
    return tag_prompt

def get_prompt_segregate(text):
    prompt = PromptTemplate(
        template = segregate_prompt, input_variables=["text"]
    )
    segregate_prompt_text = prompt.format(
        text = text
    )
    return segregate_prompt_text

def get_prompt_for_topic(main_context, topic):
    child_contexts = get_similar_text(main_context, MAX_SUBSYSTEM_TAGS, topic)
    prompt = PromptTemplate(
        template=topic_specific_prompt, input_variables=["main_context", "child_contexts", "topic"]
    )
    tag_prompt = prompt.format(
        main_context = main_context,
        child_contexts = child_contexts,
        topic = topic
    )
    return tag_prompt

def get_prompt_test_case(requirement, supporting_text, topic):
    dynamic_test_samples = get_test_case_samples_discovery(supporting_text, 5, topic)
    #For unstructured
    #dynamic_test_samples = get_test_case_samples(supporting_text, 30, topic)
    print("DYNAMIC")
    print(dynamic_test_samples)
    prompt = PromptTemplate(
        template=test_case_prompt, input_variables=["dynamic_test_samples", "requirement", "supporting_text","subsystem"]
    )
    tag_prompt = prompt.format(
        dynamic_test_samples = dynamic_test_samples,
        requirement = requirement,
        supporting_text = supporting_text,
        subsystem = topic
    )
    return tag_prompt

def process_file():
    file_text_collection = process_text_files(get_file_dict())
    docs = Document(page_content="")
    doc_list = []
    i = 0
    for file_meta in file_text_collection:
        docs = get_text_chunks(file_name=file_meta['file_name'], topic=file_meta['topic'], text=file_meta['content'])
        print(i)
        i = i+1
        add_to_vector_store(docs)

def get_prompt_text(text_search):
    subsytem_dict = get_sample_subsystem_topics(text_search)
    example_for_topics = (build_subsystem_samples(subsytem_dict))
    prompt_text = get_prompt(example_for_topics, text_search)
    print(prompt_text)
    return prompt_text

def get_prompt_text_based_topic(text_search, topic):
    prompt_text = get_prompt_for_topic(text_search, topic)
    print(prompt_text)
    return prompt_text

def get_prompt_test_cases(requirement, supporting_text, topic):
    prompt_text = get_prompt_test_case(requirement, supporting_text, topic)
    #print(prompt_text)
    return prompt_text

#process_file()