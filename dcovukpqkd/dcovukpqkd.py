import re
import os
java_file=os.getenv('java_file')

def find_similar_lines_public(text):
    similar_lines = []
    inside_block = False
    pattern = re.compile(r'(private|public)\s+(\w+)\s+(\w+)\(.*?\)\s*{')
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



similar_lines_1 = find_similar_lines_private(java_file)
similar_lines_2 = find_similar_lines_public(java_file)
for line in similar_lines_1:
    print(line)
for line in similar_lines_2:
    print(line)