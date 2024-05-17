import json
import os
import shutil
import pandas as pd
import ast
import uuid
import datetime
import time
from io import StringIO
from WatsonxAPI import WatsonxAPI
from prompts import object_prompt_start,object_prompt_end, testcase_prompt_start, mapping_testcase_and_object_prompt_start
from config import watsonx_selenium_object_config, watsonx_selenium_object_config_greedy

model = WatsonxAPI(watsonx_selenium_object_config)
model2 = WatsonxAPI(watsonx_selenium_object_config_greedy)

# input_path_to_java = '/Users/pinkal/Documents/projects/selenium_to_qualitia/code/TestCases/TestCase1/input/'
# output_path = "/Users/pinkal/Documents/projects/selenium_to_qualitia/code/TestCases/TestCase1/output_temp/"

# java_files = [file_j for file_j in os.listdir(input_path_to_java) if file_j.endswith('.java') and "TestData" not in file_j]
# print(java_files)

# Read Object JSON Template
with open('json_template/input_object_json_format.txt', 'r') as f:
    sample_object_dict = json.load(f)
print(sample_object_dict)

# Object JSON Template Read
with open('json_template/input_testcase_json_format.txt', 'r') as f:
    sample_tc_dict = json.load(f)
print(sample_tc_dict)

with open('json_template/input_testcase_task_json_format_level1.txt', 'r') as f:
    sample_tc_task_dict = json.load(f)
print(sample_tc_task_dict)

with open('json_template/input_testcase_object_json_format_level2.txt', 'r') as f:
    sample_tc_task_obj_dict = json.load(f)
print(sample_tc_task_obj_dict)

def read_java_files(selenium_java_files):
    java_text = []
    for file_name in selenium_java_files:
        if os.path.isfile(file_name):
            with open(file_name) as java_file:
                java_text.append(java_file.read())
    return java_text

obj_class_rejection_list = ['page','by','using']
def obj_class_correction(obj_class,property_value):
    clean_obj_class = obj_class.lower().strip()
    if clean_obj_class and clean_obj_class in obj_class_rejection_list:
        if clean_obj_class=='page':
            obj_class = 'WebElement'
    elif property_value and 'button' in property_value.lower():
        obj_class = 'WebButton'
    return obj_class

def read_java_files_prev(selenium_java_files):
    java_text = []
    print("selenium_java_files: ",selenium_java_files)
    for file in selenium_java_files:
        stringio=StringIO(file.getvalue().decode('utf-8'))
        read_data=stringio.read()
        java_text.append(read_data)
    return java_text

def processing_obj_response(object_json_dict,final_object_dict = {}):
    # final_object_dict = {}
    object_list = []
    for row in object_json_dict:
        if row.get('objectName','') and final_object_dict.get(row.get('objectName','')):
            object_list.append(row.get('objectName',''))
            continue
        if not row.get('propertyName','') and not row.get('propertyValue',''):
            continue
        temp_dict = sample_object_dict.copy()
        current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        object_id = uuid.uuid4().hex
        temp_dict['objectClass'] = obj_class_correction(row.get('objectClass',''),row.get('propertyValue',''))
        temp_dict['objectName'] = row.get('objectName','')
        temp_dict['propertyList'] = [
                                        {
                                            'propertyName':row.get('propertyName',''),
                                            'propertyValue':row.get('propertyValue','')
                                        },
                                        {'propertyName': 'ObjectData', 'propertyValue': ''}
                                    ]
        temp_dict['objectId'] = object_id
        temp_dict['createdOn'] = current_time
        temp_dict['updatedOn'] = current_time
        object_list.append(row.get('objectName',''))
        final_object_dict[temp_dict['objectName']] = temp_dict
        print(object_id,row.get('objectName',''),row.get('objectClass',''),row.get('propertyName',''),row.get('propertyValue',''))
        del temp_dict
    return final_object_dict, object_list

def processing_obj_response_prev(object_json_dict):
    final_object_dict = {}
    for row in object_json_dict:
        if not row.get('propertyName','') and not row.get('propertyValue',''):
            continue
        temp_dict = sample_object_dict.copy()
        current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        object_id = uuid.uuid4().hex
        temp_dict['objectClass'] = obj_class_correction(row.get('objectClass',''),row.get('propertyValue',''))
        temp_dict['objectName'] = row.get('objectName','')
        temp_dict['propertyList'] = [
                                        {
                                            'propertyName':row.get('propertyName',''),
                                            'propertyValue':row.get('propertyValue','')
                                        },
                                        {'propertyName': 'ObjectData', 'propertyValue': ''}
                                    ]
        temp_dict['objectId'] = object_id
        temp_dict['createdOn'] = current_time
        temp_dict['updatedOn'] = current_time
        final_object_dict[temp_dict['objectName']] = temp_dict
        print(object_id,row.get('objectName',''),row.get('objectClass',''),row.get('propertyName',''),row.get('propertyValue',''))
        del temp_dict
    return final_object_dict

def processing_tc_task_obj_response(tc_task_obj_model_response_dict,obj_dict):
    testcase_final_dict = {}
    for tc in tc_task_obj_model_response_dict.get("TestCases",[]):
        tc_name = tc.get("TestCaseName","")
        if not tc_name:
            continue
        tc_id = uuid.uuid4().hex
        temp_tc_dict = sample_tc_dict.copy()
        temp_tc_dict["testCaseId"] = tc_id
        temp_tc_dict["tcName"] = tc_name
        temp_task_list = []
        for task_dict in tc.get("Functions",[]):
            task_name = task_dict.get("FunctionName","")
            if not task_name:
                continue
            task_id = uuid.uuid4().hex
            temp_task_dict = sample_tc_task_dict.copy()
            temp_task_dict["taskId"] = task_id
            temp_task_dict["taskName"] = task_name
            temp_task_obj_list = []
            for ob_name in task_dict.get("ObjectActions",{}):
                ob_action = task_dict['ObjectActions'].get(ob_name,"")
                ob_id = obj_dict.get(ob_name,{}).get("objectId","")
                #print(ob_name,task_dict['ObjectActions'].get(ob_name,""),obj_dict.get(ob_name,{}).get("objectId",""))
                if not ob_name.strip():# or not ob_id:
                    continue
                temp_task_obj_dict = sample_tc_task_obj_dict.copy()
                temp_task_obj_dict["objectId"] = ob_id
                temp_task_obj_dict["objectName"] = ob_name
                temp_task_obj_dict["objectAction"] = ob_action
                temp_task_obj_list.append(temp_task_obj_dict)
                del temp_task_obj_dict
            temp_task_dict["steps"] = temp_task_obj_list
            temp_task_list.append(temp_task_dict)
            del temp_task_dict
        temp_tc_dict["steps"] = temp_task_list
        testcase_final_dict[tc_name] = temp_tc_dict
        del temp_tc_dict
    return testcase_final_dict

def selenium_to_json_prev(selenium_obj_files,selenium_test_files):
    obj_text = read_java_files_prev(selenium_obj_files)
    test_text = read_java_files_prev(selenium_test_files)
    #print(java_text)

    # Generate Prompt
    object_prompt = object_prompt_start + " ".join(obj_text) + object_prompt_end
    #print("Prompt: ",object_prompt)

    # Call WatsonX.AI Model
    object_json_dict = model._generate_text(prompt=object_prompt)
    #print("Model Output: ",object_json_dict)

    # Post-processing output
    object_json_dict = json.loads(object_json_dict)
    print("After:",object_json_dict)
    final_object_dict = processing_obj_response_prev(object_json_dict)

    objectNames = str(list(final_object_dict.keys()))
    object_prompt_tc_extr = testcase_prompt_start + "\n".join(test_text) + object_prompt_end
    tc_json = model2._generate_text(prompt=object_prompt_tc_extr)
    print("Testcase and Function JSON output:",tc_json)

    json_format = "TestCase JSON:\n" + tc_json
    objList = "ObjectName List:\n" + objectNames
    object_prompt_combination = mapping_testcase_and_object_prompt_start  + json_format + "\n" + objList + "\n".join(obj_text + test_text) + object_prompt_end
    print(object_prompt_combination)
    final_response = model2._generate_text(prompt=object_prompt_combination)
    print("final_response before json load: ",final_response)
    final_response = json.loads(final_response.split('\nNote:')[0])
    print("final_response: ",final_response)

    # post processing 
    testcase_final_dict = processing_tc_task_obj_response(final_response,final_object_dict)
    return final_object_dict, testcase_final_dict

def save_multi_json(final_object_dict,testcase_final_dict,output_path):
    # Check Output Folder as exists and if it is not exists, create it
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # else:
    #     shutil.rmtree(output_path)
    #     os.makedirs(output_path)
    object_json_output_path = output_path.rstrip("/") + "/object/"
    testcase_json_output_path = output_path.rstrip("/") + "/testcase/"
    if not os.path.exists(object_json_output_path):
        os.makedirs(object_json_output_path)
    if not os.path.exists(testcase_json_output_path):
        os.makedirs(testcase_json_output_path)
    
    # Saving Object JSON
    print("Final objects: ")
    data_list = []
    for obj_key in final_object_dict:
        obj_json = final_object_dict[obj_key]
        with open(object_json_output_path+str(obj_json['objectId'])+'.json', 'w') as fp:
            json.dump(obj_json, fp)
        data_list.append([obj_json['objectId'],obj_json.get('objectName',''),obj_json.get('objectClass',''),obj_json['propertyList'][0].get('propertyName',''),obj_json['propertyList'][0].get('propertyValue','')])
        print(obj_json['objectId'],obj_json.get('objectName',''),obj_json.get('objectClass',''),obj_json['propertyList'][0].get('propertyName',''),obj_json['propertyList'][0].get('propertyValue',''))
    obj_df = pd.DataFrame(data_list,columns=["Object ID","Object Name","Object Class","Property Name","Property Value"])

    # Saving Testcase JSON
    tc_data = []
    for tc_key in testcase_final_dict:
        tc_json = testcase_final_dict[tc_key]
        with open(testcase_json_output_path+str(tc_json['testCaseId'])+'.json', 'w') as fp:
            json.dump(tc_json, fp)
        for task_json in tc_json.get('steps',{}):
            for task_ob_json in task_json.get('steps',{}):
                tc_data.append([tc_json['testCaseId'],tc_json['tcName'],task_json['taskName'],task_ob_json.get('objectName',''),task_ob_json.get('objectId',''),task_ob_json.get('objectAction','')])

    tc_df = pd.DataFrame(tc_data,columns=['TestCase Id','TestCase Name','Task Name','Object Name','Object ID', 'Object Action'])

    return obj_df,tc_df

def selenium_to_json(folder_path):

    test_files_with_dependency = code_discovery_and_refactore(folder_path)

    final_object_dict = {}
    final_response_list = []

    for test_main_file in list(test_files_with_dependency.keys()):
        selenium_test_files = [test_main_file]
        selenium_obj_files = test_files_with_dependency[test_main_file]

        print(selenium_obj_files)
        print(selenium_test_files)
        obj_text = read_java_files(selenium_obj_files)
        test_text = read_java_files(selenium_test_files)
        #print(java_text)

        # Generate Prompt
        object_prompt = object_prompt_start + " ".join(obj_text) + object_prompt_end
        print("Prompt: ",object_prompt)

        # Call WatsonX.AI Model
        object_json_dict = model._generate_text(prompt=object_prompt)
        #print("Model Output: ",object_json_dict)

        # Post-processing output
        object_json_dict = json.loads(object_json_dict)
        print("After:",object_json_dict)
        final_object_dict, object_list = processing_obj_response(object_json_dict,final_object_dict)
        all_text = " ".join(obj_text) + '\n' + " ".join(test_text)
        counter = 0
        not_in = []
        for obj_name in object_list:
            if obj_name not in all_text:
                del final_object_dict[obj_name]
                counter += 1
                not_in.append(obj_name)

        if len(object_list) > 0 and (counter*100)/len(object_list) >= 70.00:
            print("CONTINUE++++++++++++++++++++++++")
            continue

        else:
            object_list = list(set(object_list) - set(not_in))
            objectNames = str(object_list)
            object_prompt_tc_extr = testcase_prompt_start + "\n".join(test_text) + object_prompt_end
            tc_json = model2._generate_text(prompt=object_prompt_tc_extr)
            print("Testcase and Function JSON output:",tc_json)

            json_format = "TestCase JSON:\n" + tc_json
            objList = "ObjectName List:\n" + objectNames
            object_prompt_combination = mapping_testcase_and_object_prompt_start  + json_format + "\n" + objList + "\n".join(obj_text + test_text) + object_prompt_end
            print(object_prompt_combination)
            final_response = model2._generate_text(prompt=object_prompt_combination)
            print("final_response before json load: ",final_response)
            final_response = json.loads(final_response.rsplit('}',1)[0]+'}')
            print("final_response: ",final_response)

            # post processing 
            # testcase_final_dict = processing_tc_task_obj_response(final_response,final_object_dict)
            final_response_list.append(final_response)
            del final_response
            time.sleep(15)

    final_test_list = []
    for final_response in final_response_list:
        testcase_final_dict = processing_tc_task_obj_response(final_response,final_object_dict)
        final_test_list.append(testcase_final_dict)
    
    return final_object_dict, final_test_list


def save_multi_json_final(final_object_dict, final_test_list, custom_output_path):
    final_tc_df = pd.DataFrame()
    for testcase_final_dict in final_test_list:
        obj_df,tc_df = save_multi_json(final_object_dict,testcase_final_dict, custom_output_path)
        final_tc_df = final_tc_df.append(tc_df, ignore_index=True)
    
    return obj_df, final_tc_df