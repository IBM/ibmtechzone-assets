import re

def extract_numerical_entities(texts):
    return [re.findall(r'(\S+\d[\d,\.]*?\b)', text) for text in texts]

def compare_entities(expected_entities, llm_entities):
    return [exp == llm for exp, llm in zip(expected_entities, llm_entities)]
