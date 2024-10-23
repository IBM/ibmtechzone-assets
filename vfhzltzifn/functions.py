import pandas as pd
import os
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from chromadbclass import ChromaDBHandler
from dotenv import load_dotenv
import re
import requests
api_key = os.getenv("WATSONX_KEY", None)
project_id = os.getenv("WATSONX_PROJECT", None)
ibm_cloud_url = "https://us-south.ml.cloud.ibm.com"
creds = {"url": ibm_cloud_url,"apikey": api_key}

# Initialize ChromaDBHandler globally
chromadb_handler = ChromaDBHandler()

# Define function to create custom prompt for each integrity check
def make_prompt_inclusion(criteria):
    
    prompt = f""" You are an expert in extracting all measurable health outcomes from the provided criteria without hallucinations.

Review the inclusion criteria below and extract all measurable health outcomes and durations with their required ranges or thresholds, in a tabular format. 
Focus on capturing all relevant details, including numerical values, performance statuses, and treatment conditions, and do not miss even minor details.
Avoid extra text and descriptions; just generate the table.

Instructions:
- Always use symbols like '>' and numerals like '24' where applicable.
- Please ensure not to confuse or hallucinate symbols such as 'greater than,' 'less than,' and their corresponding symbols '>' and '<' in the outputs.
- Importantly, maintain a clear and organized tabular format, ensuring no information is omitted.
- Follow the structure in the example for short, clear outputs, avoiding lengthy pointers while keeping all relevant details.
- Stricly follow the tabular format
- Start and end the table with ***

Example:
| Inclusion Criteria          | Details      |
|-----------------------------|--------------|
| Age                         | > 21 years   |
| BMI                         | 18-30        |
| ECOG Performance Status     | 0-1          |
| Prior Therapy               | ≥ 6 months   |
| Hemoglobin                  | ≥ 9 g/dL     |                 

Now, review the following inclusion criteria and extract the table:
Inclusion criteria: {criteria}

Output table:
"""
    
    return prompt


# Define function to create custom prompt for each integrity check
def make_prompt_exclusion(criteria):
    
    prompt = f""" You are an expert in extracting all measurable health outcomes from the provided criteria without hallucinations.

Review the exclusion criteria below and extract all measurable health outcomes and durations with their required ranges or thresholds, in a tabular format. 
Focus on capturing all relevant details, including numerical values, performance statuses, and treatment conditions, and do not miss even minor details.
Avoid extra text and descriptions; just generate the table.

Instructions:
- Always use symbols like '>' and numerals like '24' where applicable.
- Please ensure not to confuse or hallucinate symbols such as 'greater than,' 'less than,' and their corresponding symbols '>' and '<' in the outputs.
- Importantly, maintain a clear and organized tabular format, ensuring no information is omitted.
- Follow the structure in the example for short, clear outputs, avoiding lengthy pointers while keeping all relevant details.
- If there are no exclusion criteria, just say "No exclusion criteria."
- Stricly follow the tabular format
- Start and end the table with ***

Example:
| Exclusion Criteria                                      | Details                                                  |
|---------------------------------------------------------|----------------------------------------------------------|
| Stage IV breast cancer                                  | Excluded                                                 |
| Prior invasive breast cancer (ipsi- or contralateral)   | Excluded                                                 |
| Recurrent disease post-therapy                          | Excluded                                                 |
| Active liver disease (e.g., HBV, HCV)                   | Excluded                                                 |
| Grade 3 or 4 hypersensitivity to pembrolizumab          | Excluded                                                 |
| Chronic systemic steroids or immunosuppressive meds     | Excluded in the last 2 years                             |
| Patients unable/unwilling to comply                     | Excluded                                                 |
| Multicentric carcinoma                                  | In more than one quadrant                                |
| Multicentric carcinoma                                  | Separated by > 4 centimeters                             |

Now, review the following exclusion criteria and extract the table:
Exclusion criteria: {criteria}

Output table:
"""
    
    return prompt

smaller_model = "meta-llama/llama-3-70b-instruct"
larger_model = "meta-llama/llama-3-405b-instruct"

# Function to interact with the watsonx.ai models
def send_to_watsonxai(prompt,
                    model_name,
                    decoding_method="sample",
                    max_new_tokens=3000,
                    min_new_tokens=10,
                    temperature=0.4,
                    stop_sequences=['Please', 'Note', '"""'],
                    repetition_penalty=1.2,
                    truncate_input_tokens=3000):
    
    
    """
    helper function for sending prompts and params to Watsonx.ai

    Args:  
        prompts:list list of text prompts
        decoding:str Watsonx.ai parameter "sample" or "greedy"
        max_new_tok:int Watsonx.ai parameter for max new tokens/response returned
        temperature:float Watsonx.ai parameter for temperature (range 0>2)
        repetition_penalty:float Watsonx.ai parameter for repetition penalty (range 1.0 to 2.0)

    Returns: None
        prints response
    """
    

    assert not (len(prompt) < 1), "make sure none of the prompts in the inputs prompts are empty"

    model_params = {
        GenParams.DECODING_METHOD: decoding_method,
        GenParams.MIN_NEW_TOKENS: min_new_tokens,
        GenParams.MAX_NEW_TOKENS: max_new_tokens,
        GenParams.STOP_SEQUENCES: stop_sequences,
        GenParams.RANDOM_SEED: 42,
        GenParams.TEMPERATURE: temperature,
        GenParams.REPETITION_PENALTY: repetition_penalty,
        GenParams.TRUNCATE_INPUT_TOKENS: truncate_input_tokens}

    model = Model(
        model_id=model_name,
        params=model_params,
        credentials=creds,
        project_id=project_id)

    responses = model.generate_text(prompt)
        
    return responses




def divide_and_conquer(criteria, study_id, criteria_type):
    split_dfs = []
    pattern = r"\|(.*)\|(.*)\|"
    criteria_list = criteria.split("*")
    factor = int(len(criteria_list)/3)
    chunks = [" ".join(x for x in criteria_list[0:factor]), 
              " ".join(x for x in criteria_list[factor:2*factor]), 
              " ".join(x for x in criteria_list[2*factor:])]

    for chunk in chunks:
        if criteria_type == 'inclusion':
            prompt_inclusion = make_prompt_inclusion(chunk)
            inclusion_list = send_to_watsonxai(model_name=smaller_model, prompt=prompt_inclusion)
            inclusion_list_matches = re.findall(pattern, inclusion_list)
        
            if len(inclusion_list_matches) <= 1: 
                'sending to larger model...'
                inclusion_list = send_to_watsonxai(model_name=larger_model, prompt=prompt_inclusion)
                inclusion_list_matches = re.findall(pattern, inclusion_list)
            
            inclusion_list_header = inclusion_list_matches[0]
            inclusion_list_data = inclusion_list_matches[2:]
            
            inclusion_list_df = pd.DataFrame(inclusion_list_data, columns=inclusion_list_header)
            inclusion_list_df['NCT ID'] = study_id
            inclusion_list_df.columns = inclusion_list_df.columns.str.strip()
            inclusion_list_df = inclusion_list_df[['NCT ID', 'Inclusion Criteria', 'Details']]
            split_dfs.append(inclusion_list_df)
            
        elif criteria_type == 'exclusion':
            prompt_exclusion = make_prompt_exclusion(chunk)
            exclusion_list = send_to_watsonxai(model_name=smaller_model, prompt=prompt_exclusion)
            exclusion_list_matches = re.findall(pattern, exclusion_list)
            
            if len(exclusion_list_matches) <= 1: 
                exclusion_list = send_to_watsonxai(model_name=larger_model, prompt=prompt_exclusion)
                exclusion_list_matches = re.findall(pattern, exclusion_list)
            
            exclusion_list_header = exclusion_list_matches[0]
            exclusion_list_data = exclusion_list_matches[2:]
            
            exclusion_list_df = pd.DataFrame(exclusion_list_data, columns=exclusion_list_header)
            exclusion_list_df['NCT ID'] = study_id
            exclusion_list_df.columns = exclusion_list_df.columns.str.strip()
            exclusion_list_df = exclusion_list_df[['NCT ID', 'Exclusion Criteria', 'Details']]
            split_dfs.append(exclusion_list_df)
            
    return split_dfs

import numpy as np

def merge_criteria(df, criteria_column):
    # Replace empty or whitespace criteria with NaN
    df[criteria_column] = df[criteria_column].replace(r'^\s*$', np.nan, regex=True)

    # Forward fill NaN values in the criteria column
    df[criteria_column] = df[criteria_column].ffill()

    # Group by 'NCT ID' and the criteria column and aggregate 'Details'
    result_df = df.groupby(['NCT ID', criteria_column], as_index=False).agg({
        'Details': lambda x: ', '.join(x)  # Concatenate all details into one string
    })

    return result_df

def extract_measurable_outcomes(inclusion_criteria, exclusion_criteria, study_id):
    
    # Inclusion
    split_dfs_inclusion = divide_and_conquer(inclusion_criteria, study_id, criteria_type='inclusion')
    inclusion_df = pd.concat([x for x in split_dfs_inclusion], axis=0).reset_index(drop=True)
    inclusion_df.to_csv('test.csv')
    inclusion_df = merge_criteria(inclusion_df, "Inclusion Criteria")
    # Exclusion
    split_dfs_exclusion = divide_and_conquer(exclusion_criteria, study_id, criteria_type='exclusion')
    exclusion_df = pd.concat([x for x in split_dfs_exclusion], axis=0).reset_index(drop=True)
    exclusion_df = merge_criteria(exclusion_df, "Exclusion Criteria")
    return inclusion_df, exclusion_df



import pandas as pd
import os

def get_list_from_criteria(trials_data):
    # Initialize processing status
    # pd.DataFrame({'processing': [True]}).to_csv("status.csv", index=False)
    pd.DataFrame({'status': [False]}).to_csv('cancel.csv', index=False)
    pd.DataFrame({'progress': [0.1]}).to_csv("progress.csv", index=False)
    # Add two new columns for inclusion and exclusion lists
    trials_data['Inclusion List'] = None
    trials_data['Exclusion List'] = None
    
    # Get the list of study IDs
    study_list = list(trials_data['NCT ID'])
    total_studies = len(study_list)  # Get total number of studies
    inclusion_dfs = []
    exclusion_dfs = []
    for idx, study_id in enumerate(study_list, 1):  # Start index at 1 for easier progress calculation    
        try:
            print(idx,":",study_id)
            # Check for cancellation status
            cancel_status = pd.read_csv('cancel.csv')['status'].iloc[0]
            if cancel_status:  # If status is True, stop processing
                # pd.DataFrame({'processing': [False]}).to_csv("status.csv", index=False)
                return "Processing stopped by user."
            
            my_study = trials_data[trials_data['NCT ID'] == study_id]
            # Extract measurable outcomes
            inclusion_criteria = my_study['Inclusion Criteria'].values[0].replace('\\', '')
            exclusion_criteria = my_study['Exclusion Criteria'].values[0].replace('\\', '')

            # Call your function that extracts measurable outcomes
            inclusion_list_df, exclusion_list_df = extract_measurable_outcomes(inclusion_criteria, exclusion_criteria, study_id)
            inclusion_dfs.append(inclusion_list_df)
            exclusion_dfs.append(exclusion_list_df)
            
        except Exception as e:
            # Handle errors by appending None for failed IDs
            print(f"Error processing study ID {study_id}: {e}")
        

        # Update progress and save to progress.csv
        progress = (idx / total_studies) * 100  # Calculate progress as a percentage
        pd.DataFrame({'progress': [progress]}).to_csv("progress.csv", index=False)
        
        # Update results in results.csv after each iteration
    pd.concat(inclusion_dfs, ignore_index=True).to_csv("all_inclusion_criteria.csv")
    pd.concat(exclusion_dfs, ignore_index=True).to_csv("all_exclusion_criteria.csv")

    # Finalize processing status
    # pd.DataFrame({'processing': [False]}).to_csv("status.csv", index=False)
    return "Processing complete and results saved."

# This below section of function regarding extraction of reference text for the extracted details from the table
import pandas as pd

def get_criteria(trials_data, nct_id, criteria_type='inclusion'):
    # Ensure criteria_type is either 'inclusion' or 'exclusion'
    if criteria_type.lower() not in ['inclusion', 'exclusion']:
        raise ValueError("criteria_type must be either 'inclusion' or 'exclusion'")
    
    # Select the column based on the criteria_type
    criteria_column = 'Inclusion Criteria' if criteria_type.lower() == 'inclusion' else 'Exclusion Criteria'
    
    # Filter the trials_data to find the row with the matching NCT ID
    study_row = trials_data[trials_data['NCT ID'] == nct_id]
    
    if study_row.empty:
        raise ValueError(f"NCT ID {nct_id} not found in trials_data.")
    
    # Get the criteria value from the specified column
    criteria_value = study_row[criteria_column].values[0]
    
    return criteria_value

import pandas as pd

def filter_criteria_by_nct_id(criteria_df, nct_id):
    # Filter the DataFrame based on the given NCT ID
    filtered_df = criteria_df[criteria_df['NCT ID'] == nct_id]
    
    # Check if the NCT ID exists in the DataFrame
    if filtered_df.empty:
        raise ValueError(f"NCT ID {nct_id} not found in the provided criteria DataFrame.")
    
    return filtered_df


# Example usage in your process function:
def generate_ref_text(trials_data, inclusion_df, criteria_type):
    
    # # Initialize the ChromaDBHandler
    # chromadb_handler = ChromaDBHandler()

    #collect list of nct_ids
    nct_ids = list(trials_data['NCT ID'].values)
    
    # Initialize an empty list to store individual DataFrames
    df_list = []

    # Iterate over each NCT ID
    for nct_id in nct_ids:
        print(nct_id)
        # Step 1: Get the inclusion criteria
        criteria = get_criteria(trials_data, nct_id, criteria_type)
        # Step 2: Filter the inclusion_df for the given NCT ID
        filtered_df = filter_criteria_by_nct_id(inclusion_df, nct_id)

        if criteria_type == 'inclusion':
            criteria_column = 'Inclusion Criteria'
        else:
            criteria_column = 'Exclusion Criteria'
        # Step 3: Concatenate 'Inclusion Criteria' and 'Details' columns
        # filtered_df['Concatenated'] = filtered_df.apply(lambda row: f"{row[criteria_column]} is {row['Details']}", axis=1)
        # Step 4: Clear the ChromaDB collection
        chromadb_handler.delete_all_data()
        # Step 5: Insert the criteria text
        chromadb_handler.insert_data(criteria)
        # Step 6: Query for top matches and update the dataframe
        filtered_df['Reference Text'] = filtered_df[criteria_column].apply(chromadb_handler.query_data)
        # Step 7: Append the processed DataFrame to the list
        df_list.append(filtered_df)
    # Concatenate all DataFrames into one
    final_df = pd.concat(df_list, ignore_index=True)
    # final_df.drop(columns=['Concatenated'], inplace=True)
    return final_df, df_list

import pandas as pd

def main_ref_text_engine():
    try:
        # Load the data files
        trials_data = pd.read_csv("full_trial_data.csv")
    except FileNotFoundError:
        return "Error: 'full_trial_data.csv' not found."

    try:
        inclusion_df = pd.read_csv("all_inclusion_criteria.csv")
    except FileNotFoundError:
        return "Error: 'all_inclusion_criteria.csv' not found."

    try:
        exclusion_df = pd.read_csv("all_exclusion_criteria.csv")
    except FileNotFoundError:
        return "Error: 'all_exclusion_criteria.csv' not found."

    try:
        # Generate reference text for inclusion and exclusion criteria
        reference_txt_inclusion_df, _ = generate_ref_text(trials_data, inclusion_df, 'inclusion')
        reference_txt_exclusion_df, _ = generate_ref_text(trials_data, exclusion_df, 'exclusion')
        # Save the data with reference text
        reference_txt_inclusion_df.to_csv("all_inclusion_criteria_with_ref.csv")
        reference_txt_exclusion_df.to_csv("all_exclusion_criteria_with_ref.csv")
        
    except Exception as e:
        print(e)
        return f"An error occurred while processing the data: {e}"

    return "Reference text generated successfully"

def load_criteria_data():
    """Helper function to load inclusion and exclusion data from CSV files."""
    try:
        inclusion_df = pd.read_csv("all_inclusion_criteria.csv")
        exclusion_df = pd.read_csv("all_exclusion_criteria.csv")
        return inclusion_df, exclusion_df
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {str(e)}")
    except Exception as e:
        raise Exception(f"An error occurred while loading the data: {str(e)}")

# Load datasets
def load_data():
    inclusion_data = pd.read_csv("all_inclusion_criteria.csv")
    exclusion_data = pd.read_csv("all_exclusion_criteria.csv")
    patient_data = pd.read_excel("clinical_trial.xlsx")
    return inclusion_data, exclusion_data, patient_data

# Define function to create custom prompt for each integrity check
def make_prompt_inclusion_review(criteria, patient):
    
    prompt = f"""You are a medical researcher tasked with evaluating patient profiles against criteria to check if they qualify for a breast cancer trial.

Review every criteria in the trial criteria list and evaluate the patient record, in a tabular format.
Avoid extra text, descriptions and code; just generate the table.
Respond with only Yes, No/Not Applicable, Missing, or More Information Required.
Say Yes if you can match the patient record to the criteria and they meet the requirements.
Say No/Not Applicable if you can match the patient record to the criteria but they do not meet the requirements or only meet partial requirements.
Say Missing if you cannot match the criteria to any field in the patient record.
Say More Information Required if you found only partial information in the patient record.
Provide your reasoning for your responses as well.
Refrain from making statements that you cannot back up with evidence from the patient record.
Provide complete criteria description in your output, do not trail off with '...'.

Remember:
nan means the patient data for that field is missing
+ means Positive, - means Negative

Example:
Patient Data: [('AgeDx': 68.0), ('Organ': 'Breast'), ('ER': 'Positive (50%)'), ('Her2': 'Positive'), ('Stage', 'II')]
Trial Criteria: [('Estrogen Receptor': '≥ 1%'), ('Progesterone Receptor': '≥ 1%'), ('Clinical Stage': 'T1-4, N0-3'), ('Weakly ER-Positive Breast Cancer', '1-10%'), ('Node-Positive Residual Disease', 'Required for HR+, HER2+ cancers')]
Output table:
| Criteria                                                        | Met in Patient Record     | Reason                                                                                                                     |
|-----------------------------------------------------------------|---------------------------|----------------------------------------------------------------------------------------------------------------------------|
| Estrogen Receptor: ≥ 1%                                         | Yes                       | I matched this with the patient ER field; this is met since the patient ER is Positive and the criteria requires ER ≥ 1%.  |
| Progesterone Receptor: ≥ 1%                                     | Missing                   | I cannot confidently evaluate this against any field in the patient record.                                                |
| Clinical Stage: T1-4, N0-3                                      | Yes                       | I matched this with Stage field; it's met since the patient is Stage III.                                                  |
| Weakly ER-Positive Breast Cancer: 1-10%                         | No/Not Applicable         | I matched this criteria with the ER field. However the criteria requires ER between 1% and 10% and the patient's ER is 50%.|
| Node-Positive Residual Disease: Required for HR+, HER2+ cancers | More Information Required | The patient record contains HR and HER2 Positive; however it is unclear whether they have node-positive residual disease.  |

Example:
Patient Data: [('AgeDx': 42.0), ('Organ': 'Breast'), ('ER': 'Positive'), ('Her2': 'Negative'),  ('PR': 'Positive'), ('TNM staging': 'T1b N0 M0')]
Trial Criteria: [('HR': 'Positive'), ('Weakly ER-Positive Breast Cancer', '1-10%'), ('Primary tumor', 'pT1-3 (if N0, must be T1c or higher)'), ('Clinically N0 Disease', 'SLNB Required'), ('Clinically N1 Disease Diagnosis', 'Additional Axillary Evaluation')]
Output table:
| Criteria                                                        | Met in Patient Record     | Reason                                                                                                    |
|-----------------------------------------------------------------|---------------------------|-----------------------------------------------------------------------------------------------------------|
| HR: Positive                                                    | Yes                       | I matched this with the patient's ER and PR fields; this is met since the patient ER and PR are Positive. |
| Weakly ER-Positive Breast Cancer: 1-10%                         | More Information Required | The criteria requires ER between 1% and 10% and the patient's ER is only listed as Positive.              |
| Node-Positive Residual Disease: Required for HR+, HER2+ cancers | No/Not Applicable         | The patient has HR+ cancer but is HER2 negative so this criteria does not apply.                          |
| PR: <= 10%                                                      | More Information Required | The criteria requires PR to be less than or equal to 10% but the patient's PR is only listed as Positive. |
| Primary tumor: pT1-3 (if N0, must be T1c or higher)             | No/Not Applicable         | The patient has N0 so they need to be higher than T1c; however they are T1b.                              |
| Clinically N0 Disease: SLNB Required                            | More Information Required | The patient has N0 but I don't have any information about SLNB.                                           |
| Clinically N1 Disease Diagnosis: Additional Axillary Evaluation | No/Not Applicable         | The patient does not have N1 so this criteria does not apply.                                             |    

Patient Data: {patient}
Trial Criteria: {criteria}
Output table:"""
    
    return prompt

# Define function to create custom prompt for each integrity check
def make_prompt_exclusion_review(criteria, patient):
    
    prompt = f"""You are a medical researcher tasked with evaluating patient profiles against exclusion criteria to check if they are disqualified from a trial.

Review every exclusion criteria in the trial criteria list and evaluate if the patient record contains any information that disqualifies them.
Respond with only Yes, No/Not Applicable, Missing, or More Information Required.
Say Yes if you can match the patient record to the criteria and they meet the requirements.
Say No/Not Applicable if you can match the patient record to the criteria but they do not meet the requirements or only meet partial requirements.
Say Missing if you cannot match the criteria to any field in the patient record.
Say More Information Required if you found only partial information in the patient record.
Provide your reasoning for your responses as well.
Refrain from making statements that you cannot back up with evidence from the patient record.
Provide complete criteria description in your output, do not trail off with '...'.

Remember:
nan means the patient data for that field is missing
+ means Positive, - means Negative

Example:
Patient Data: [('AgeDx', 68.0), ('CaType', 'Invasive Ductal Carcinoma'), ('ER', 'Positive'), ('Her2', 'Negative'), ('Stage', 'III'), ('NYHA criteria', 'Class >= II'), ('Uncontrolled hypertension', 'BP > 180 mmHg')]
Trial Criteria: [('Prior invasive breast cancer', 'Ipsilateral or Contralateral, Within 3 years of Registration'), ('Anthracycline exposure', 'Doxorubicin > 240 mg/m^2 | Epirubicin > 480 mg/m^2'), ('Adjuvant treatment with investigational drug', 'Within 28 days prior to registration'), ('Uncontrolled hypertension', 'Systolic BP > 180 mmHg and/or Diastolic BP > 100 mmHg'), ('Peripheral neuropathy', 'Any etiology exceeding grade 1'), ('NYHA criteria', 'Class >= II')]
Output table:
| Criteria                                                                                   | Met in Patient Record     | Reason                                                                                                                                       |
|--------------------------------------------------------------------------------------------|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| Prior invasive breast cancer Ipsilateral or Contralateral, Within 3 years of Registration  | No/Not Applicable         | The patient’s record indicates Invasive Ductal Carcinoma, but no evidence of prior ipsilateral or contralateral invasive cancer is provided. |
| Anthracycline exposure Doxorubicin > 240 mg/m^2 | Epirubicin or Myocet > 480 mg/m^2        | Missing                   | Did not anthracycline exposure or dosage in the patient data, so I cannot confidently evaluate it against any patient record field           |
| Uncontrolled hypertension Systolic BP > 180 mmHg and/or Diastolic BP > 100 mmHg            | More Information Required | The patient record only shows BP > 180 mmHg but lacks systolic and diastolic values, so I am unsure if uncontrolled hypertension is present  |
| Peripheral neuropathy exceeding grade 1 Any etiology exceeding grade 1                     | Missing                   | There is no indication of peripheral neuropathy in the patient data, so I cannot confidently evaluate it against any patient record field.   |
| NYHA criteria: Class >= II                                                                 | Yes                       | Given the patient’s age and the advanced stage III cancer, it’s reasonable to assume potential heart strain, meeting NYHA class II or higher |


Example:
Patient Data: [('AgeDx', 65.0), ('CaType', 'Ductal Carcinoma In Situ'), ('ER', 'Negative'), ('Her2', 'Positive'), ('Stage', 'II'), ('Strong CYP3A4/CYP2C8 inhibitors', 'Used within 2 weeks prior to registration')]
Trial Criteria: [('Serious cardiac arrhythmia', 'Not controlled by adequate medication'), ('Trastuzumab/murine protein intolerance', 'History of grade 3 to 4 infusion reaction'), ('Strong CYP3A4/CYP2C8 inhibitors', 'Used within 2 weeks prior to registration'), ('Pregnancy', 'Excluded'), ('Recurrent disease', 'Post-preoperative Therapy & Surgery'), ('Stage IV breast cancer', 'Metastatic')]
Output table:
| Criteria                                                                        | Met in Patient Record     | Reason                                                                                                                                 |
|---------------------------------------------------------------------------------|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| Serious cardiac arrhythmia Not controlled by adequate medication                | Missing                   | Did not  find arrhythmia or cardiac medication in the patient data,so I cannot confidently evaluate it against any patient record field|
| Trastuzumab/murine protein intolerance History of grade 3 to 4 infusion reaction| More Information Required | The patient record lacks information on Trastuzumab treatment or any intolerance to murine proteins, making it unclear if this applies.|
| Strong CYP3A4/CYP2C8 inhibitors Used within 2 weeks prior to registration       | Yes                       | The patient is receiving therapy that typically involves the use of CYP3A4 inhibitors, which matches the exclusion criterion.          |
| Pregnancy  Excluded                                                             | Missing                   | The patients information lacks information about pregnancy, I cannot confidently match the exclusion criteria                          |
| Recurrent disease Post-preoperative Therapy & Surgery                           | More Information Required | There is no clear indication of disease recurrence in the patient data post-preoperative therapy, so I cannot confidently assess this. |
| Stage IV breast cancer Metastatic                                               | No/Not Applicable         | The patient is recorded as having Stage II breast cancer, which does not meet the exclusion for metastatic (Stage IV) breast cancer.   |

Patient Data: {patient}
Trial Criteria: {criteria}
Output table:"""

    return prompt

def get_criteria_list(model_name, prompt):
    # Send prompt to WatsonXAI and get the response
    criteria_list = send_to_watsonxai(model_name=model_name, prompt=prompt, temperature=0.40, repetition_penalty=1.0)
    
    # Use regex to extract data from the result (assuming the pattern remains the same)
    pattern = r"\|(.*)\|(.*)\|(.*)\|"
    criteria_list_matches = re.findall(pattern, criteria_list)
    
    # First match is assumed to be the header, the rest are data rows
    criteria_list_header = criteria_list_matches[0]
    criteria_list_data = criteria_list_matches[2:]  # Skipping first two (header and column descriptions)
    
    # Create a DataFrame and clean up column names
    criteria_list_df = pd.DataFrame(criteria_list_data, columns=criteria_list_header)
    criteria_list_df.columns = [x.strip() for x in criteria_list_df.columns]
    
    return criteria_list_df

def process_patients(criteria_data, patient_data, model_name, criteria_type='inclusion'):
    # Extract unique NCT IDs from the criteria data
    pd.DataFrame({'status': [False]}).to_csv('cancel.csv', index=False)
    nct_ids = criteria_data['NCT ID'].unique()
    results = []
    total_patients = len(patient_data)
    print("----------Totall patients length------------:::", total_patients)
    pd.DataFrame({'progress': [0.1]}).to_csv("progress.csv", index=False)
    for index, patient_row in patient_data.iterrows():
        # Check for cancellation status
        cancel_status = pd.read_csv('cancel.csv')['status'].iloc[0]
        if cancel_status:  # If status is True, stop processing
            # pd.DataFrame({'processing': [False]}).to_csv("status.csv", index=False)
            return "Processing stopped by user."
        # Extract the value of the 'Name' column for each patient row
        patient_name = patient_row['Name']
        # Convert patient row data into a dictionary format for prompt
        patient_data_dict = str(list(zip(patient_data.columns, patient_row.values)))
        print("Patient::",patient_data_dict)
        
        for nct_id in nct_ids:
            # Filter the criteria data based on the current NCT ID
            criteria_data_sample = criteria_data[criteria_data['NCT ID'] == nct_id]
            
            # Depending on the criteria type, use the appropriate column for prompt creation
            if criteria_type == 'inclusion':
                trial_data_dict = list(zip(criteria_data_sample["Inclusion Criteria"], criteria_data_sample["Details"]))
            elif criteria_type == 'exclusion':
                trial_data_dict = list(zip(criteria_data_sample["Exclusion Criteria"], criteria_data_sample["Details"]))
            
            # Convert to a string (or markdown table as needed)
            trial_data_dict_str = str(trial_data_dict)
            # print("Criteria::",trial_data_dict_str)
            
            # Create the prompt using a generic prompt creation function
            if criteria_type == 'inclusion':
                prompt_criteria_review = make_prompt_inclusion_review(trial_data_dict_str, patient_data_dict)  # Could rename this function to be more generic if needed
            elif criteria_type == 'exclusion':
                prompt_criteria_review = make_prompt_exclusion_review(trial_data_dict_str, patient_data_dict)  # Could rename this function to be more generic if needed
            
            # Get the criteria list (inclusion or exclusion) from WatsonXAI
            criteria_list_df = get_criteria_list(model_name, prompt_criteria_review)
            
            # Add NCT ID to the DataFrame
            criteria_list_df['Trial'] = nct_id
            criteria_list_df['Patient'] = patient_name
            results.append(criteria_list_df)
            # display(criteria_list_df)
        progress = (index / total_patients) * 100  # Calculate progress as a percentage
        pd.DataFrame({'progress': [progress]}).to_csv("progress.csv", index=False)

    # Combine results from all patients and studies into one DataFrame
    final_df = pd.concat(results, ignore_index=True)
    pd.DataFrame({'status': [False]}).to_csv('cancel.csv', index=False)
    return final_df

def calculate_patient_percentages_for_trial(df, trial):
    # Filter the DataFrame for the selected trial
    trial_df = df[df['Trial'] == trial]
    
    # Initialize an empty dictionary to store the results
    patient_percentages = {}
    
    # Get the list of unique patients in the selected trial
    patients = trial_df['Patient'].unique()

    # Iterate over each patient
    for patient in patients:
        # Filter the DataFrame for the current patient within the selected trial
        patient_df = trial_df[trial_df['Patient'] == patient]
        
        # Get the count of each status in the "Met in Patient Record" column
        status_counts = patient_df['Met in Patient Record'].str.strip().value_counts(normalize=True) * 100
        
        # Get the percentages for each status
        yes_percentage = status_counts.get('Yes', 0)
        missing_percentage = status_counts.get('Missing', 0)
        no_percentage = status_counts.get('No/Not Applicable', 0)
        more_info_req_percentage = status_counts.get('More Information Required', 0)
        
        # Store the percentages in a dictionary for the current patient
        patient_percentages[patient] = {
            'Yes': yes_percentage,
            'Missing': missing_percentage,
            'No': no_percentage,
            'More Information Required': more_info_req_percentage
        }
    
    return patient_percentages


def fetch_and_save_study_data(base_url, nct_ids, output_file='study_data.csv'):
    # Initialize an empty list to store the data
    data_list = []

    # Loop through each study ID in the provided NCT ID list
    for idx, study in enumerate(nct_ids):
        # Define the complete URL for each study
        study_url = base_url + study
        print(f"Fetching data from: {study_url}")  # For debugging

        # Send a GET request to the API
        response = requests.get(study_url)

        # Check if the request was successful
        if response.status_code == 200:
            study_data = response.json()  # Parse JSON response

            # Safely access nested keys
            nctId = study_data['protocolSection']['identificationModule'].get('nctId', 'Unknown')
            title = study_data['protocolSection']['identificationModule'].get('officialTitle', 'No title available')
            overallStatus = study_data['protocolSection']['statusModule'].get('overallStatus', 'Unknown')
            startDate = study_data['protocolSection']['statusModule'].get('startDateStruct', {}).get('date', 'Unknown Date')
            conditions = ', '.join(study_data['protocolSection']['conditionsModule'].get('conditions', ['No conditions listed']))
            acronym = study_data['protocolSection']['identificationModule'].get('acronym', 'Unknown')

            # Extract interventions safely
            interventions_list = study_data['protocolSection'].get('armsInterventionsModule', {}).get('interventions', [])
            interventions = ', '.join([intervention.get('name', 'No intervention name listed') for intervention in interventions_list]) if interventions_list else "No interventions listed"

            # Extract locations safely
            locations_list = study_data['protocolSection'].get('contactsLocationsModule', {}).get('locations', [])
            locations = ', '.join([f"{location.get('city', 'No City')} - {location.get('country', 'No Country')}" for location in locations_list]) if locations_list else "No locations listed"

            # Extract eligibility
            criteria_split = study_data['protocolSection']['eligibilityModule']['eligibilityCriteria'].split('Exclusion')
            inclusion_criteria = criteria_split[0]
            exclusion_criteria = "Exclusion" + criteria_split[1] if len(criteria_split) > 1 else "There are no exclusion criteria."

            # Extract dates and phases
            primaryCompletionDate = study_data['protocolSection']['statusModule'].get('primaryCompletionDateStruct', {}).get('date', 'Unknown Date')
            studyFirstPostDate = study_data['protocolSection']['statusModule'].get('studyFirstPostDateStruct', {}).get('date', 'Unknown Date')
            lastUpdatePostDate = study_data['protocolSection']['statusModule'].get('lastUpdatePostDateStruct', {}).get('date', 'Unknown Date')
            studyType = study_data['protocolSection']['designModule'].get('studyType', 'Unknown')
            phases = ', '.join(study_data['protocolSection']['designModule'].get('phases', ['Not Available']))

            # Append the data to the list as a dictionary
            data_list.append({
                "NCT ID": nctId,
                "Study Title": title,
                "Acronym": acronym,
                "Overall Status": overallStatus,
                "Start Date": startDate,
                "Conditions": conditions,
                "Interventions": interventions,
                "Locations": locations,
                "Inclusion Criteria": inclusion_criteria,
                "Exclusion Criteria": exclusion_criteria,
                "Primary Completion Date": primaryCompletionDate,
                "Study First Post Date": studyFirstPostDate,
                "Last Update Post Date": lastUpdatePostDate,
                "Study Type": studyType,
                "Phases": phases,
                "Link": study_url
            })
        else:
            print(f"Failed to fetch data for {study}. Status code: {response.status_code}")

    # Create a DataFrame from the list of dictionaries
    study_df = pd.DataFrame(data_list)

    # Save the DataFrame as a CSV file
    study_df.to_csv(output_file, index=False)
    print(f"Study data saved to {output_file}")



