from transformers import BertTokenizer, BertModel
import torch
from minio import Minio
from sklearn.metrics.pairwise import cosine_similarity

import pandas as pd
import re
from io import BytesIO

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def create_minio_client():
    """
    Create and return a MinIO client object configured with the provided credentials.

    Returns:
    - Minio: A MinIO client object configured with the provided credentials.

    Notes:
    - The MinIO client is initialized with the endpoint, access key, and secret key.
    - The `secure` parameter is set to False to allow connection without SSL/TLS encryption.
    """
    minio_client = Minio(
        endpoint='**********',
        access_key='*************',
        secret_key='*****************',
        secure=False
    )

    return minio_client

def create_master_df():
    """
    Creates and returns two pandas DataFrames:
    
    - df_target_pr: DataFrame containing property-related data
    - df_target_fr: DataFrame containing floor and room-related data
    
    Returns:
        tuple: A tuple containing two pandas DataFrames: (df_target_pr, df_target_fr)
    """

    target_master_pr = {'Property ID': {0: 244, 1: 242, 2: 240, 3: 239, 4: 235}, 
                        'Client': {0: 'Acme', 1: 'Acme', 2: 'Acme', 3: 'Acme', 4: 'Acme'}, 
                        'Property Name': {0: 'Houston Campus - Life Building', 1: 'Houston Campus - Wortham Tower', 2: '2401 South Osage Street (Osage', 3: '2271 SE 27th Avenue (Osage Cam', 4: 'Houston Campus -America Tower'}, 
                        'Type': {0: 'Office', 1: 'Office', 2: 'Office', 3: 'Office', 4: 'Office'}, 
                        'SubType': {0: 'Office', 1: 'Office', 2: 'Office', 3: 'Office', 4: 'Office'}, 
                        'Status': {0: 'Active', 1: 'Active', 2: 'Active', 3: 'Active', 4: 'Active'}, 
                        'Ownership': {0: 'Owned', 1: 'Owned', 2: 'Owned', 3: 'Owned', 4: 'Owned'}, 
                        'Area Unit of Measure': {0: 'SQ FT', 1: 'SQ FT', 2: 'SQ FT', 3: 'SQ FT', 4: 'SQ FT'}, 
                        'Gross Area': {0: 233770.61, 1: 203422.0, 2: 7200.0, 3: 117605.0, 4: 187116.38}, 
                        'Net Area': {0: 233770.61, 1: 2292.0, 2: 5225.6533, 3: 112165.484, 4: 187116.38}, 
                        'Country': {0: 'United States of America', 1: 'United States of America', 2: 'United States of America', 3: 'United States of America', 4: 'United States of America'}, 
                        'Ignore Address Suggestions': {0: False, 1: False, 2: False, 3: False, 4: False}, 
                        'Street Address': {0: '2727 Allen Pkwy', 1: '2727 Allen Pkwy', 2: '2401 S Osage St', 3: '2271 SE 27th Ave', 4: '2929 Allen Pkwy'}, 
                        'Street Address2': {0: 'Life Building', 1: 'Wortham Tower', 2: 'Osage Annex', 3: 'Osage Campus', 4: 'Americas Tower'}, 
                        'City': {0: 'Houston', 1: 'Houston', 2: 'Amarillo', 3: 'Amarillo', 4: 'Houston'}, 
                        'State/Province': {0: 'TX', 1: 'TX', 2: 'TX', 3: 'TX', 4: 'TX'}, 
                        'Postal Code': {0: 77019, 1: 77019, 2: 79103, 3: 79103, 4: 77019}, 
                        'Latitude': {0: 29.759714126586918, 1: 29.759714126586918, 2: 35.18737793, 3: 35.18638229370117, 4: 29.75993537902832}, 
                        'Longitude': {0: -95.39560699, 1: -95.39560699, 2: -101.812027, 3: -101.810051, 4: -95.39672089}, 
                        'Client Property ID': {0: 1000186, 1: 1001076, 2: 1001414, 3: 1001113, 4: 1000300}, 
                        'Client Property Name': {0: '2727A Allen', 1: '2727B Allen', 2: 'TX10022-A OFA', 3: 'TX1014', 4: '2929 Allen'}, 
                        'Client Property Type': {0: 'Americas\xa0Houston\u200b', 1: 'Americas\xa0Houston\u200b', 2: 'Americas\xa0(other)\u200b', 3: 'Americas\xa0(other)\u200b', 4: 'Americas\xa0Houston\u200b'}, 
                        'Client Property Sub-type': {0: 'Acme', 1: 'Acme', 2: 'Acme', 3: 'Acme', 4: 'Acme'}, 
                        'RegionNumber': {0: 1, 1: 2, 2: 3, 3: 4, 4: 4}, 
                        'DivisionNumber': {0: 86, 1: 88, 2: 39, 3: 3, 4: 4}, 
                        'EmployeeNumber': {0: 6018, 1: 6018, 2: 6018, 3: 6018, 4: 6018}, 
                        'EmployeeNumber2': {0: 1000, 1: 1000, 2: 1000, 3: 1004, 4: 1074},
                        'DateOpened': {0: '16/11/22', 1: '16/11/22', 2: '16/11/22', 3: '16/11/22', 4: '16/11/22'}, 
                        'GroupName': {0: 'Null', 1: 'Null', 2: 'Null', 3: 'Null', 4: 'Null'}, 
                        'TypeName': {0: 'Null', 1: 'Null', 2: 'Null', 3: 'Null', 4: 'Null'}, 
                        'AltKey': {0: 'Null', 1: 'Null', 2: 'Null', 3: 'Null', 4: 'Null'}, 
                        'PhoneNumber': {0: 'Null', 1: 'Null', 2: 'Null', 3: 'Null', 4: 'Null'}, 
                        'TCC_Project_Number': {0: 'UAE001', 1: 'ARG005', 2: 'AUT001', 3: 'TB-COKXAU02', 4: 'TB-COKXAU03'}, 
                        'Product_Type': {0: 'Null', 1: 'Null', 2: 'Null', 3: 'Null', 4: 'Null'}, 
                        'TCC_Business_Unit': {0: 'Null', 1: 'Null', 2: 'Null', 3: 'Null', 4: 'Null'}, 
                        'Owner_Entity': {0: 'Null', 1: 'Null', 2: 'Null', 3: 'Null', 4: 'Null'}, 
                        'Square_Feet': {0: 30619, 1: 171148, 2: 16299, 3: 13746, 4: 13018}, 
                        'UserDef1': {0: 'Null', 1: 'Null', 2: 'Null', 3: 'Null', 4: 'Null'}, 
                        'UserDef2': {0: 'Null', 1: 'Null', 2: 'Null', 3: 'Null', 4: 'Null'}, 
                        'EmployeeNumber3': {0: 1065, 1: 1085, 2: 1068, 3: 1000, 4: 1000}, 
                        'TimeZone': {0: 'UTC+04', 1: 'UTC-03', 2: 'UTC+01', 3: 'UTC+10', 4: 'UTC+10'}, 
                        'Daylight': {0: 0, 1: 0, 2: 1, 3: 1, 4: 1}, 
                        'LandlordVendor': {0: 2, 1: 10, 2: 9, 3: 7, 4: 4}, 
                        'LandlordVendorSite': {0: 1, 1: 1, 2: 1, 3: 1, 4: 1}, 
                        'PropMgmtVendor': {0: 'Null', 1: 'Null', 2: 'Null', 3: 'Null', 4: 'Null'}, 
                        'PropMgmtVendorSite': {0: 'Null', 1: 'Null', 2: 'Null', 3: 'Null', 4: 'Null'}, 
                        'LeaseOwn': {0: 'L', 1: 'O', 2: 'L', 3: 'L', 4: 'L'}, 
                        'LeaseRenewal': {0: 'Null', 1: 'Null', 2: 'Null', 3: 'Null', 4: 'Null'}, 
                        'LeaseExpire': {0: 'Null', 1: 'Null', 2: 'Null', 3: 'Null', 4: 'Null'}, 
                        'FacilityType': {0: 'Office', 1: 'Office', 2: 'Office', 3: 'Office', 4: 'Office'}, 
                        'CountryCode': {0: 'AE', 1: 'AR', 2: 'AT', 3: 'AU', 4: 'AU'}, 
                        'FilterSeq': {0: 3, 1: 4, 2: 3, 3: 2, 4: 2}, 
                        'LocaleID': {0: 1033, 1: 11274, 2: 3079, 3: 1033, 4: 1033}, 
                        'ServiceCenterID': {0: 73, 1: 2, 2: 4, 3: 3, 4: 3}, 
                        'Address3': {0: 'Null', 1: 'Null', 2: 'Null', 3: 'Null', 4: 'Null'}, 
                        'Address4': {0: 'Null', 1: 'Null', 2: 'Null', 3: 'Null', 4: 'Null'}, 
                        'Tech1': {0: 'Null', 1: 'Null', 2: 'Null', 3: 'Null', 4: 'Null'}, 
                        'Tech2': {0: 1065, 1: 1085, 2: 1068, 3: 1000, 4: 1000}, 
                        'LocationEmail': {0: 'Null', 1: 'Null', 2: 'Null', 3: 'Null', 4: 'Null'}, 
                        'TrsAutoDispatch': {0: 1, 1: 1, 2: 1, 3: 1, 4: 1}, 
                        'BusClockStart': {0: '18/11/22 7:00', 1: '18/11/22 8:00', 2: '18/11/22 8:00', 3: '18/11/22 8:00', 4: '18/11/22 8:00'}, 
                        'BusClockEnd': {0: '18/11/22 20:30', 1: '18/11/22 18:00', 2: '18/11/22 19:00', 3: '18/11/22 19:00', 4: '18/11/22 19:00'}, 
                        'DateClosed': {0: '28/12/22', 1: 'Null', 2: 'Null', 3: 'Null', 4: 'Null'}, 
                        'NTEApprovalCode': {0: 'Null', 1: 'Null', 2: 'Null', 3: 'Null', 4: 'Null'}, 
                        'DefaultPREmployee': {0: 1065, 1: 1085, 2: 1068, 3: 1000, 4: 1000}}

    df_target_pr = pd.DataFrame(target_master_pr)
    df_target_fr = pd.DataFrame(columns=['Property Name', 'Floor ID', 'Floor Description', 'Floor User Defined 1', 'Floor User Defined 2', 'Room ID', 'Room Name', 
                                         'Reference1', 'Reference2', 'Reference3', 'Reference4'])

    

    return df_target_pr, df_target_fr

def pre_processing(column_names):
    """
    Pre-processes a list of column names by applying various regex patterns for replacement.

    Args:
        column_names (list): A list of column names to be pre-processed.

    Returns:
        list: A list of pre-processed column names with standardized formatting.
    """
    regex_patterns = [
        (r'\n', ' '),         # Replace newline characters with space
        (r'\r', ' '),         # Replace carriage return characters with space
        (r'/', ' or '),       # Replace forward slashes with 'or'
        (r'[-().:]', ''),     # Remove hyphens, parentheses, dots, and colons
        (r'#', ' number ')   # Replace hash symbols with the word 'number'
    ]

    # Apply regex patterns to each column name
    processed_column_names = column_names[:]
    for pattern, replacement in regex_patterns:
        processed_column_names = [re.sub(pattern, replacement, x) for x in processed_column_names]

    # Convert column names to lowercase and replace spaces with underscores
    processed_column_names = [x.lower().strip() for x in processed_column_names]
    processed_column_names = [x.replace(' ', '_') for x in processed_column_names]

    # Replace multiple underscores with a single underscore
    processed_column_names = [re.sub(r'_+', '_', x) for x in processed_column_names]

    return processed_column_names


def read_files_name(bucket_name: str, folder_path: str) -> dict:
    """
    Reads the names of CSV files within a specified folder in a Minio bucket.

    Args:
        bucket_name (str): The name of the Minio bucket.
        folder_path (str): The path to the folder containing the CSV files.

    Returns:
        dict: A dictionary where keys are derived from the first part of the file names (before the first hyphen),
            and values are lists of file paths within the specified folder that have the same key.
    """
    minio_client = create_minio_client()

    # List objects in the specified folder in the Minio bucket
    objects = minio_client.list_objects(
        bucket_name=bucket_name,
        prefix=folder_path,
        recursive=True
    )

    # Filter out only the CSV files
    files = [obj.object_name for obj in objects if obj.object_name.endswith('.csv')]

    # Group files based on the prefix before the first hyphen in their names
    files_dict = {}
    for file in set([file.split('/')[1].split('-')[0] for file in files]):
        files_dict[file] = [x for x in files if file in x]

    return files_dict

def load_data(bucket_name: str, files: list) -> dict:
    """
    Loads data from CSV files stored in a Minio bucket.

    Args:
        bucket_name (str): The name of the Minio bucket.
        files (list): A list of file paths within the specified bucket.

    Returns:
        dict: A dictionary where keys are the names of the CSV files, and values are pandas DataFrames
              containing the data from the corresponding CSV files.
    """
    minio_client = create_minio_client()

    # Initialize an empty dictionary to store DataFrames
    dfs = {}

    # Iterate over each file path
    for file in files:
        # Retrieve the CSV file from Minio
        data = minio_client.get_object(bucket_name, file)
        csv_data = data.read()
        
        # Load CSV data into a pandas DataFrame
        dfs[file.split('/')[-1]] = pd.read_csv(BytesIO(csv_data), dtype=object)

    return dfs


def create_bert_embeddings_col(texts):
    """
    Creates BERT embeddings for the given text using a pre-trained BERT model.

    Args:
        texts (str): The text for which BERT embeddings need to be generated.

    Returns:
        numpy.ndarray: BERT embeddings for the input text.
    """
    bert_embeddings = []  # List to store BERT embeddings
    inputs = tokenizer(texts, return_tensors="pt", max_length=512, truncation=True)  # Tokenize input text
    with torch.no_grad():
        outputs = model(**inputs)  # Pass tokenized input through BERT model
    embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()  # Compute mean of hidden states as embeddings
    bert_embeddings.append(embeddings)  # Append embeddings to list
    return embeddings  # Return BERT embeddings


def match_data_column_names_fr(input_df, target_df, threshold=0.8):
    """
    Matches columns of input DataFrame to target DataFrame based on similarity using BERT embeddings.

    Args:
        input_df (pandas.DataFrame): The DataFrame containing input data.
        target_df (pandas.DataFrame): The DataFrame containing target data to match against.
        threshold (float, optional): The threshold similarity score for considering a match. Defaults to 0.8.

    Returns:
        dict: A dictionary where keys are the column names of the input DataFrame and values are the matched column names
              from the target DataFrame. Columns with similarity below the threshold are not matched.
    """
    matched_columns = {}  # Dictionary to store matched columns
    matched_sim = {}      # Dictionary to store similarity scores for matched columns
    target_embeddings = {}  # Dictionary to store BERT embeddings for target columns
    source_columns = input_df.columns.tolist()  # List of column names in the input DataFrame
    target_columns = target_df.columns.tolist()  # List of column names in the target DataFrame

    # Create BERT embeddings for each target column
    for col2 in target_columns:
        target_embeddings[col2] = create_bert_embeddings_col(col2)

    # Iterate over each column in the input DataFrame
    for col1 in source_columns:
        matched_column = None  # Initialize matched column to None
        similarities = []       # List to store similarity scores
        input_embedding = create_bert_embeddings_col(col1)  # Create BERT embedding for input column
        # Iterate over each column in the target DataFrame
        for col2 in target_columns:
            target_embedding = target_embeddings[col2]  # Get BERT embedding for target column
            # Calculate cosine similarity between input and target embeddings
            similarity_col = cosine_similarity(input_embedding.reshape(1, -1).tolist(), target_embedding.reshape(1, -1).tolist())
            similarities.append(similarity_col)  # Append similarity score to list
            
        similarity = max(similarities)  # Get maximum similarity score
        similarity_index = similarities.index(similarity)  # Get index of maximum similarity
        # Check if similarity score meets threshold and assign matched column accordingly
        if similarity >= threshold:
            matched_column = target_columns[similarity_index]
            matched_column = target_columns[similarity_index]  # Assign matched column
            # Update matched_sim dictionary with similarity score for matched column
            if matched_column in matched_sim.keys():
                key = list(matched_sim[matched_column].keys())[0]
                if similarity > matched_sim[matched_column][key]:
                    matched_sim[matched_column] = {col1: similarity}
                    matched_columns[key] = None
                else:
                    matched_column = None
            else:
                matched_sim[matched_column] = {}
                matched_sim[matched_column][col1] = similarity
                
        matched_columns[col1] = matched_column  # Store matched column in result dictionary

    result = matched_columns  # Assign result to matched_columns

    return result


def create_mapping_pr(matched_columns_dict, filename, source_columns_frs, df_input_pr):
    """
    Creates mappings between columns in the input DataFrame and the target DataFrame based on matched column names.

    Args:
        matched_columns_dict (dict): Dictionary containing matched column names between the input and target DataFrames.
        filename (str): Name of the file from which the input DataFrame was loaded.
        source_columns_frs (list): List of column names from the source DataFrame.
        df_input_pr (pandas.DataFrame): Input DataFrame containing property-related data.

    Returns:
        list: List of dictionaries representing mappings between columns.
    """
    mappings_pr = []  # List to store mappings between columns
    for col1, col2 in matched_columns_dict.items():
        mapping_dict = {}  # Dictionary to represent a mapping
        mapping_dict['key_column'] = False  # Flag to indicate if the column is a key column
        mapping_dict['working_table'] = "property"  # Name of the working table
        mapping_dict['is_mapped'] = True if col2 else False  # Flag indicating if the column is mapped
        mapping_dict['key_column'] = df_input_pr[col1].dropna().is_unique and col1 in source_columns_frs and not check_value_in_list_of_dicts(mappings_pr, True)  # Check if the column is a key column
        mapping_dict['file_name'] = filename  # Name of the file from which the input DataFrame was loaded
        mapping_dict['column_name'] = col1  # Name of the input column
        mapping_dict['target_data_column_name'] = col2 if col2 else "Unmapped"  # Name of the corresponding target column
        mappings_pr.append(mapping_dict)  # Add the mapping to the list of mappings
    return mappings_pr  # Return the list of mappings


def create_mapping_fr(matched_columns_dict, filename, source_columns_pr):
    """
    Creates mappings between columns in the input DataFrame and the target DataFrame based on matched column names.

    Args:
        matched_columns_dict (dict): Dictionary containing matched column names between the input and target DataFrames.
        filename (str): Name of the file from which the input DataFrame was loaded.
        source_columns_pr (list): List of column names from the source DataFrame.

    Returns:
        list: List of dictionaries representing mappings between columns.
    """
    mappings = []  # List to store mappings between columns
    for col1, col2 in matched_columns_dict.items():
        mapping_dict = {}  # Dictionary to represent a mapping
        mapping_dict['key_column'] = False  # Flag to indicate if the column is a key column
        mapping_dict['working_table'] = "floors_and_rooms"  # Name of the working table
        mapping_dict['is_mapped'] = True if col2 else False  # Flag indicating if the column is mapped
        mapping_dict['key_column'] = col1 in source_columns_pr and not check_value_in_list_of_dicts(mappings, True)  # Check if the column is a key column
        mapping_dict['file_name'] = filename  # Name of the file from which the input DataFrame was loaded
        mapping_dict['column_name'] = col1  # Name of the input column
        mapping_dict['target_data_column_name'] = col2 if col2 else "Unmapped"  # Name of the corresponding target column
        mappings.append(mapping_dict)  # Add the mapping to the list of mappings
    return mappings  # Return the list of mappings


def create_mapping(project_name):
    bucket_name = 'cbre-projects'
    df_target_pr, df_target_fr = create_master_df()
    target_columns_pr = pre_processing(df_target_pr.columns.tolist())
    target_columns_fr = pre_processing(df_target_fr.columns.tolist())
    df_target_pr.columns, df_target_fr.columns = target_columns_pr, target_columns_fr

    files_dict = read_files_name(bucket_name, project_name)
    fr_columns = ['floor_number','spacenumber','space_name','room_name', 'room', 'room_counter', 'room_package', 'room_description']
    mappings = []
    for file in files_dict:
        dfs = load_data(bucket_name, files_dict[file])
        flag_sp = True
        flag_pr = True
        fr_dfs = {}
        pr_dfs = {}
        num_files = 0
        for key, val in dfs.items():
            num_files = num_files + 1
            df_columns = pre_processing(val.columns.tolist())
            if not any(col in fr_columns for col in df_columns):
                df_input_pr = val
                filename_pr = key
                pr_dfs[key] = val
                flag_pr = False
            elif flag_pr and num_files == len(dfs):
                df_input_pr = val
                filename_pr = key
                flag_pr = False
            else:
                fr_dfs[key] = val
            
        matched_columns_dict_pr = {}
        source_columns_pr = []
        for key, value in pr_dfs.items():
            value.columns = pre_processing(value.columns.tolist())
            matched_columns_dict_pr[key] = match_data_column_names_fr(value, df_target_pr,threshold=0.8)
            source_columns_pr.extend(value.columns.tolist()) 
            
        matched_columns_dict_fr = {}
        source_columns_frs = []
        for key, value in fr_dfs.items():
            value.columns = pre_processing(value.columns.tolist())
            matched_columns_dict_fr[key] = match_data_column_names_fr(value, df_target_fr,threshold=0.8)
            source_columns_frs.extend(value.columns.tolist())  
        for key, value in matched_columns_dict_pr.items(): 
                mappings.extend(create_mapping_pr(matched_columns_dict_pr[key], key, source_columns_frs, pr_dfs[key]))
        for key, value in matched_columns_dict_fr.items():
                mappings.extend(create_mapping_fr(matched_columns_dict_fr[key], key, source_columns_pr))
    return mappings

if __name__ == '__main__':
    project_name = str(input('Enter project folder name in Minio: '))
    mappings = create_mapping(project_name)