import re
import pandas as pd 
from pprint import pprint


def find_similar_lines_public(text):
    similar_lines = []
    inside_block = False
    pattern = re.compile(r'(private|public)\s+(\w+)\s+(\w+)\(.*?\)\s*{')
    #pattern = re.compile(r'(private|public|protected)?\s+(\w+)\s+(\w+)(\(.*?\))?\s*{')
    lines = text.split('\n')
    for line in lines:
        if inside_block:
            similar_lines.append(line.strip())
            if '}' in line:
                inside_block = False
        else:
            match = pattern.match(line.strip())
            if match:
                similar_lines.append(line.strip())
                if '{' in line:
                    inside_block = True
    return similar_lines


def find_similar_lines_private(text):
    similar_lines = []
    pattern = re.compile(r'\bprivate\s+\w+\s+\w+;\s*$')
    lines = text.split('\n')
    for line in lines:
        if pattern.match(line.strip()):
            similar_lines.append(line.strip())
    return similar_lines


variables_list = find_similar_lines_private(java_file)
functions_list = find_similar_lines_public(java_file)


private_vars = re.findall(r"private \w+ (\w+);", java_file)


usage_dict = {var: [] for var in private_vars}


method_pattern = re.compile(r"public \w+ (\w+)\(.*?\) \{([\s\S]*?)\}")

methods = method_pattern.findall(java_file)


for method, body in methods:
    for var in private_vars:
        if var in body:
            usage_dict[var].append(method)

data = [(var, ', '.join(funcs)) for var, funcs in usage_dict.items() if funcs]
df = pd.DataFrame(data, columns=['Private Variable', 'Functions Using Variable'])


pprint(variables_list)
pprint(functions_list)
pprint(df)