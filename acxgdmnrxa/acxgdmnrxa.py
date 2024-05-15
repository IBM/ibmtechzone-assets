import yaml
import re
import os
import argparse

class Merge_Ansible:

    def __init__(self) -> None:
        pass

    def preprocess_codeBlock(self, code_block):
        return code_block.replace('\n        ','\n').replace('```\n---\n','').replace('\n```', '\n').replace('```\n', '\n')

    # def get_proper(self, code_blocks):
    #     converted_codes = []
    #     for code_block in code_blocks:
    #         try:
    #             # Attempt to parse the YAML content
    #             cd = yaml.safe_load(code_block)
    #             converted_codes.append(cd)
    #             print("YAML content is valid:", cd)
    #         except yaml.YAMLError as e:
    #             print("Error parsing YAML content:", e)

    #     return converted_codes

    

    def merge_hosts(self, hosts1, hosts2):
        if hosts1 == "all" or hosts2 == "all":
            # If one block has 'all', prioritize 'all' and merge to 'all'
            return "all"
        elif hosts1 == "localhost" or hosts2 == "localhost":
            # If one block has 'localhost', prioritize 'localhost' and merge to 'localhost'
            return "localhost"
        else:
            # If both blocks have different specific hosts or groups, merge them with a colon separator
            return f"{hosts1}:{hosts2}"
    

    def merge_sections(self, code_blocks):
        merged_code = {}
        for code_block in code_blocks:

            code_block = self.preprocess_codeBlock(code_block)

            try:
                # Attempt to parse the YAML content
                yaml_data = yaml.safe_load(code_block)
                print("YAML content is valid:", yaml_data)
            except yaml.YAMLError as e:
                print("Error parsing YAML content:", yaml_data)
                raise e

            try:
                for section_name, section_content in yaml_data[0].items():
                    if section_name not in merged_code:
                        merged_code[section_name] = section_content
                    else:
                        if section_name == "name":
                            # Concatenate strings with ' & ' in between
                            merged_code[section_name] += " & " + section_content
                        elif section_name == "hosts":
                            # Merge hosts using logical rules
                            merged_code[section_name] = self.merge_hosts(merged_code[section_name], section_content)
                        elif isinstance(section_content, str):
                            # Append strings from different code blocks
                            merged_code[section_name] += section_content
                        elif isinstance(section_content, dict):
                            # Merge dictionaries ensuring no duplicate keys
                            for key, value in section_content.items():
                                if key not in merged_code[section_name]:
                                    merged_code[section_name][key] = value
                        elif isinstance(section_content, list):
                            # Extend lists from different code blocks
                            merged_code[section_name].extend(section_content)
                        # Add more logic for merging specific sections as needed
            except Exception as e:
                raise e
            
        return merged_code
    

    def check_values(self, val):
        if isinstance(val, bool):
            if val == True:
                return 'true'
            else:
                return 'false'
        elif isinstance(val, int):
            return val
        elif val == None:
            return "null"
        
        elif isinstance(val, str):
            pattern = r'.*{{.*}}.*'
            if re.match(pattern, val):
                return '"' + val + '"'
        else:
            return val
    

    def dict_to_yaml_string(self, data, indent=0):
        yaml_string = "- "
        indent += 1
        for key, value in data.items():
            if isinstance(value, dict):
                indent += 1
                yaml_string += f"{self.check_values(key.lower())}:\n" + "  " * indent 

                for ki, val in value.items():

                    if isinstance(val, str) and "\n" in val:
                        val = "|" + f"\n" + "  " * (indent+1) + re.sub(r'\n\s+', '\n' + "  " * (indent+1), val) #val.replace("\n", f"\n" + "  ")

                    # Assuming Dict where values are strings/int/bool, if list or dict then more logic needed to be applied here
                    yaml_string += f"{self.check_values(ki.lower())}: {self.check_values(val)}\n" + "  " * indent

                yaml_string = yaml_string[:-2]
                indent -= 1

            elif isinstance(value, list):
                indent += 1
                yaml_string += f"{self.check_values(key.lower())}:\n" + "  " * indent

                for item in value:
                    if isinstance(item, dict):
                        yaml_string += self.dict_to_yaml_string(item, indent)
                    else:
                        yaml_string += "- " + self.check_values(str(item)) + "\n" + "  " * (indent+1)

                    yaml_string = yaml_string[:-2]

                yaml_string = yaml_string[:-2]
                indent -= 1
            else:
                yaml_string += f"{self.check_values(key.lower())}: {self.check_values(value)}\n" + "  " * indent
        return re.sub(r'\n\s+\n', '\n\n', yaml_string)
    


if __name__ == '__main__':

    # Create argument parser
    parser = argparse.ArgumentParser(description='Process two code strings.')

    # Add arguments for code strings
    parser.add_argument('code1', type=str, help='First code string.')
    parser.add_argument('code2', type=str, help='Second code string.')

    # Parse the arguments
    args = parser.parse_args()

    # Access the code strings
    code1 = args.code1
    code2 = args.code2

    # Do something with the code strings
    print('First code string:', code1)
    print('Second code string:', code2)

    ma = Merge_Ansible()

    codes = [code1, code2]

    merged_dict = ma.merge_sections(codes)

    merged_script = ma.dict_to_yaml_string(merged_dict)

    print('Output Code String:', merged_script)
    