import javalang
import javalang.tree
import string
import re
import os

java_code = os.environ["java_code"]


def dfs(alphabet, sofar=None):
    if sofar is None:
        sofar = [""]
    for i in sofar:
        for j in alphabet:
            sofar.append(i + j)
            yield i + j

    dfs(alphabet, sofar)


def main():
    variable_name_generator = iter(dfs(string.ascii_lowercase))
    variable_name_mapping = {}

    original_code = java_code
    parsed_code = javalang.parse.parse(original_code)

    for path, node in parsed_code:
        if type(node) is javalang.tree.VariableDeclarator:
            variable_name_mapping[node.name] = next(variable_name_generator)

    # remove lines with only spaces
    original_code = re.sub(r"\n\s+\n", r"\n", original_code)

    # remove lines with only semicolons
    original_code = re.sub(r";\s*\n", r";", original_code)

    # remove spaces in lines with only curly braces
    # original_code = re.sub(r"\s*\}\s*\n", r"}", original_code)

    # replace multiple newlines with single newline
    original_code = re.sub(r"\n+", r"\n", original_code)

    # multiple spaces
    original_code = re.sub(r"[ ]+", r" ", original_code)

    # single line comments
    original_code = re.sub(
        r"(^.*?)\/\/.*?\n", r"\1\n", original_code, flags=re.MULTILINE
    )

    # multiline comments
    original_code = re.sub(
        r"/\*.*?\*/", "", original_code, flags=re.MULTILINE | re.DOTALL
    )

    for v1, v2 in variable_name_mapping.items():
        original_code = re.sub(
            f"([^\\w])({v1})([^\\w])",
            f"\\1{v2}\\3",
            original_code,
            flags=re.MULTILINE | re.DOTALL,
        )

    with open(f"minifiedCode.java", "w") as f:
        f.write(original_code)

    javalang.parse.parse(original_code)


if __name__ == "__main__":
    main()