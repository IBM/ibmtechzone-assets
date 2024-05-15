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

    code1 = '''
- name: Start Springboot Applications
  hosts: all
  gather_facts: yes
  vars:
    sbApps: "{{ node['visa_springboot']['apps_dir'] }}"
    log_file: "{{ node['visa_springboot']['log_dir'] }}/day2_start.log"

  tasks:
    - name: Check User and Group
      ansible.builtin.include_role:
        name: visa_springboot
      vars:
        check_user_group: true
      register: check_result
      when: check_user_group is defined

    - name: Raise Error if Declined
      ansible.builtin.fail:
        msg: "DECLINED: {{ check_result.results[0].msg }}"
      when: check_result.results[0].msg is defined

    - name: Create Log Directory
      ansible.builtin.file:
        path: "{{ node['visa_springboot']['log_dir'] }}"
        state: directory
        mode: '0755'
'''
    code2 = '''
- name: Start Springboot Containers
  hosts: all
  gather_facts: yes
  vars:
    log_file: "/var/log/springboot.log"
    sbApps: "/opt/visa/sbApps"

  tasks:
    - name: Start Container
      ansible.builtin.bash:
        user: "{{ node['visa_springboot']['service_user'] }}"
        group: "{{ node['visa_springboot']['service_group'] }}"
        content: |
          exec 1>>{{ log_file }}
          exec 2>&1
          echo ""
          echo "{{ node['visa_springboot']['timestamp'] }}"
          echo "*** Starting {{ container_name }} ***"
          {{ sbApps }}/{{ container_name }}/bin/sbruntime-ctl.sh start
          sleep 8
        notify: Validate Container Action
        when: "container_name in node['visa_springboot']['containers'].keys()"
        register: container_result
        ignore_errors: true

    - name: Validate Container Action
      ansible.builtin.block:
        - name: Check Container Status
          ansible.builtin.command: ps -ef|grep {{ sbApps }}/{{ container_name }}/conf|grep -v grep
          register: check_result
          changed_when: false
          failed_when: check_result.rc != 0
          ignore_errors: true

        - name: Raise Error if Container Not Running
          ansible.builtin.fail:
            msg: "{{ container_name }} could not be started"
          when: check_result.rc != 0

  handlers:
    - name: Validate Container Action
      ansible.builtin.block:
        - name: Log Container Result
          ansible.builtin.debug:
            var: container_result
'''

    import os
    CODE1_FILE_NAME = os.environ["code1_file"]
    CODE2_FILE_NAME = os.environ["code2_file"]

    if os.path.isfile(CODE1_FILE_NAME) and os.path.isfile(CODE2_FILE_NAME):
        # If file exists read data from the data file
        with open(CODE1_FILE_NAME, 'r') as file:
                code1 = file.read()

        with open(CODE2_FILE_NAME, 'r') as file:
                code2 = file.read()

    print('First code string:', code1)
    print('Second code string:', code2)

    ma = Merge_Ansible()

    codes = [code1, code2]

    merged_dict = ma.merge_sections(codes)

    merged_script = ma.dict_to_yaml_string(merged_dict)

    print('Output Code String:', merged_script)
    