import re
import json
import os
java_file=os.getenv('java_file')
java_file = f"""
{java_file}
"""
# Standard Java data types
standard_types = {'byte', 'short', 'int', 'long', 'float', 'double', 'char', 'boolean', 'String'}

def find_non_standard_variables(text):
    non_standard_variables = []
    pattern = re.compile(r'\bprivate\s+(\w+)\s+(\w+);\s*$')
    lines = text.split('\n')
    for line in lines:
        match = pattern.match(line.strip())
        if match:
            data_type = match.group(1)
            variable_name = match.group(2)
            if data_type not in standard_types:
                non_standard_variables.append((data_type, variable_name))
    return non_standard_variables


non_standard_variables = find_non_standard_variables(java_file)

variables_by_type = {}


for data_type, variable_name in non_standard_variables:
    if data_type not in variables_by_type:
        variables_by_type[data_type] = []
    variables_by_type[data_type].append(variable_name)
    
print(json.dumps( variables_by_type, indent= 3 ))
if non_standard_variables:
    print("The following non-standard variables are found:")
    for data_type, variable_name in non_standard_variables:
        print(f"Data Type: {data_type}, Variable Name: {variable_name}")
else:
    print("No non-standard variables found.")