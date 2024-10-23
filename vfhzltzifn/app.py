from flask import Flask, request, jsonify, abort, send_file
from flask_cors import CORS
import pandas as pd
import os
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from functions import *
import json
import re
import shutil

app = Flask(__name__)
CORS(app)
# CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}})

@app.route('/hello', methods=['GET'])
def hello():
    return jsonify(message="Hello, World!")

# Define a POST endpoint to upload a CSV file, save it, and return its first row
@app.route('/upload', methods=['POST'])
def upload_file():
    # status_df = pd.read_csv('status.csv')
    # status = status_df['processing'].iloc[0]
    # if status:
    #     return jsonify({"error": "Previous process still in progress"}), 400
    # print(request.files)
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request::"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Load the file into a pandas DataFrame
        trials_data = pd.read_csv(file)
        # Save the file as CSV in the current working directory
        saved_file_path = os.path.join(os.getcwd(), "full_trial_data.csv")
        trials_data.to_csv(saved_file_path, index=False)
        # Step 2: Call the get_list_from_criteria function
        # status = get_list_from_criteria(trials_data)
        # main_ref_text_engine
        return jsonify({"message": "Data uploaded successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/details_extraction_engine', methods=['GET'])
def details_extraction_engine():
    """API for extracting details based on trial criteria"""
    try:
        trials_data = pd.read_csv("full_trial_data.csv")
        # Call the function to get the status message
        status = get_list_from_criteria(trials_data)  # Assuming no input is needed
        return jsonify({'status': status}), 200
    except Exception as e:
        return jsonify({'status': f'Error: {str(e)}'}), 400


@app.route('/reference_extraction_engine', methods=['GET'])
def reference_extraction_engine():
    """API for generating reference text """
    try:
        # Call the function and get the status message
        status = main_ref_text_engine()
        return jsonify({'status': status}), 200
    except Exception as e:
        return jsonify({'status': f'Error: {str(e)}'}), 400


# API call to return the status of the function
@app.route('/status', methods=['GET'])
def get_status():
    try:
        # Read the status from the saved CSV
        status_df = pd.read_csv('status.csv')
        status = status_df['processing'].iloc[0]  # Get the first value (True or False)
        return jsonify({'status': 'running' if status else 'completed'})
    except Exception as e:
        return jsonify({'error': str(e), 'message': 'Unable to read status file'}), 500

# API call to return the progress of the function
@app.route('/progress', methods=['GET'])
def get_progress():
    try:
        # Read the progress from the saved CSV
        progress_df = pd.read_csv('progress.csv')
        progress = progress_df['progress'].iloc[0]  # Get the most recent progress value
        return jsonify({'progress': progress})  # Return the raw numerical progress
    except Exception as e:
        return jsonify({'error': str(e), 'message': 'Unable to read progress file'}), 500

@app.route('/get_trial_criteria', methods=['POST'])
def get_trial_criteria():
    """API to return trial criteria based on NCT ID provided in POST request."""
    try:
        # Extract NCT ID from request body
        data = request.get_json()
        if 'nct_id' not in data:
            return jsonify({'status': 'Error', 'message': 'NCT ID is required'}), 400
        
        nct_id = data['nct_id']

        # Load the inclusion and exclusion data
        inclusion_df, exclusion_df = load_criteria_data()

        # Filter the inclusion and exclusion data based on NCT ID
        inclusion_data = inclusion_df[inclusion_df['NCT ID'] == nct_id]
        exclusion_data = exclusion_df[exclusion_df['NCT ID'] == nct_id]

        # Check if there is data for the given NCT ID
        if inclusion_data.empty and exclusion_data.empty:
            return jsonify({'status': 'Error', 'message': f'No data found for NCT ID: {nct_id}'}), 404

        # Prepare the response data
        response = {
            'nct_id': nct_id,
            'inclusion_data': inclusion_data.to_dict(orient='records'),
            'exclusion_data': exclusion_data.to_dict(orient='records')
        }

        # Return the filtered data as a JSON response
        return jsonify(response), 200

    except FileNotFoundError as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 500

# POST API to read results.csv and return specified columns as JSON
@app.route('/get_results', methods=['POST'])
def get_results():
    try:
        # Define the file path and read the CSV file
        file_path = os.path.join(os.getcwd(), 'results.csv')
        results_df = pd.read_csv(file_path)
        results_df = results_df.dropna()

        # Select the required columns
        selected_columns = ['NCT ID', 'Inclusion Criteria', 'Exclusion Criteria', 'Inclusion List', 'Exclusion List']
        results_df = results_df[selected_columns]

        # Reformat the DataFrame into the desired JSON structure
        results_json = {
            row['NCT ID']: {
                'Inclusion Criteria': row['Inclusion Criteria'],
                'Exclusion Criteria': row['Exclusion Criteria'],
                'Inclusion List': row['Inclusion List'],
                'Exclusion List': row['Exclusion List']
            }
            for _, row in results_df.iterrows()
        }

        # Extract just the list of NCT IDs
        nct_ids = list(results_json.keys())

        # Prepare the final response
        response = {
            'results': results_json,
            'nct_ids': nct_ids
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e), 'message': 'Unable to read results file'}), 500

# # POST API to update results.csv with new values
# @app.route('/update_results', methods=['POST'])
# def update_results():
    try:
        # Read the existing results.csv
        file_path = os.path.join(os.getcwd(), 'results.csv')
        results_df = pd.read_csv(file_path)

        # Get the JSON data from the request
        update_data = request.get_json()

        # Update the DataFrame based on the received data
        for nct_id, updates in update_data.items():
            if nct_id in results_df['NCT ID'].values:
                # Update the corresponding row in the DataFrame
                for key, value in updates.items():
                    if key in results_df.columns:
                        results_df.loc[results_df['NCT ID'] == nct_id, key] = value

        # Save the updated DataFrame back to results.csv
        results_df.to_csv(file_path, index=False)

        return jsonify({'message': 'Results updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e), 'message': 'Unable to update results file'}), 500

@app.route('/cancel', methods=['GET'])
def cancel():
    # Create a DataFrame with the desired data
    data = {'status': [True]}
    df = pd.DataFrame(data)

    # Save the DataFrame to a CSV file
    df.to_csv('cancel.csv', index=False)

    return jsonify({'message': 'Cancel status saved'}), 200

@app.route('/change_status', methods=['POST'])
def status():
    # Create a DataFrame with the desired data
    status = request.json['status']
    data = {'processing': [status]}
    df = pd.DataFrame(data)

    # Save the DataFrame to a CSV file
    df.to_csv('status.csv', index=False)

    return jsonify({'message': 'status changed'}), 200



@app.route('/reset_results', methods=['GET'])
def reset_results():
    # Define the source and destination files
    source_dir = './Original files'  # Directory where original files are stored
    files_to_copy = [
        'clinical_trial.xlsx',
        # 'validation_all_patients_exclusion.csv',
        # 'validation_all_patients_inclusion.csv',
        'all_patients_all_exclusion_dfs.csv',
        'full_trial_data.csv',
        'all_patients_all_inclusion_dfs.csv',
        'all_inclusion_criteria_with_ref.csv',
        'all_exclusion_criteria_with_ref.csv',
        'patient_trial_evaluation_summaries.csv'
    ]
    
    copied_files = []
    errors = []
    pd.DataFrame({'status': [False]}).to_csv('cancel.csv', index=False)
    for file_name in files_to_copy:
        src_path = os.path.join(source_dir, file_name)
        dest_path = os.path.join(os.getcwd(), file_name)  # Destination is current working directory

        try:
            # Copy the file from source to destination, replacing the target if it exists
            shutil.copy(src_path, dest_path)
            copied_files.append(file_name)
        except Exception as e:
            errors.append(f"Error copying {file_name}: {str(e)}")

    return jsonify({
        'copied_files': copied_files,
        'errors': errors
    }), 200

@app.route('/nct_ids', methods=['GET'])
def get_nct_ids():
    # Read the full trial data
    full_trial_df = pd.read_csv('full_trial_data.csv')
    
    # Extract the unique NCT IDs
    nct_ids = full_trial_df['NCT ID'].unique().tolist()
    # nct_ids = full_trial_df['NCT ID'].unique().tolist()
    
    # Return the NCT IDs as a JSON response
    return jsonify({'nct_ids': nct_ids})


@app.route('/review/<nct_id>', methods=['GET'])
def review_by_nct(nct_id):
    # Read the CSV files into DataFrames
    inclusion_df = pd.read_csv('all_inclusion_criteria_with_ref.csv').drop(['Unnamed: 0', 'Unnamed: 0.1'], axis=1, errors='ignore')
    exclusion_df = pd.read_csv('all_exclusion_criteria_with_ref.csv').drop(['Unnamed: 0', 'Unnamed: 0.1'], axis=1, errors='ignore')
    full_trial_df = pd.read_csv('full_trial_data.csv')

    # Filter the data based on the selected NCT ID
    filtered_inclusion = inclusion_df[inclusion_df['NCT ID'] == nct_id]
    filtered_exclusion = exclusion_df[exclusion_df['NCT ID'] == nct_id]
    filtered_full_trial = full_trial_df[full_trial_df['NCT ID'] == nct_id]

    # Get the Study Title for the filtered NCT ID
    study_title = filtered_full_trial['Study Title'].values[0] if not filtered_full_trial.empty else None

    # Add Study Title to the inclusion and exclusion DataFrames
    filtered_inclusion['Study Title'] = study_title
    filtered_exclusion['Study Title'] = study_title

    # Convert filtered DataFrames to JSON format
    inclusion_json = filtered_inclusion.to_dict(orient='records')
    exclusion_json = filtered_exclusion.to_dict(orient='records')
    full_trial_json = filtered_full_trial.to_dict(orient='records')

    # Return the filtered data as a JSON response
    return jsonify({
        'inclusion_criteria_insights': inclusion_json,
        'exclusion_criteria_insights': exclusion_json,
        'full_trial_data': full_trial_json
    })

@app.route('/update_results', methods=['POST'])
def update_results():
    # Load the existing DataFrames from CSV files
    inclusion_df = pd.read_csv('all_inclusion_criteria_with_ref.csv')
    exclusion_df = pd.read_csv('all_exclusion_criteria_with_ref.csv')

    # Get the JSON payload from the request
    data = request.get_json()

    # Get the updated inclusion and exclusion data from the request
    updated_inclusion_data = data.get('inclusion_criteria_insights', [])
    updated_exclusion_data = data.get('exclusion_criteria_insights', [])

    # Create DataFrames from the received updated data
    updated_inclusion_df = pd.DataFrame(updated_inclusion_data).drop(['id', 'Study Title'], axis=1, errors='ignore')
    updated_exclusion_df = pd.DataFrame(updated_exclusion_data).drop(['id', 'Study Title'], axis=1, errors='ignore')

    # Ensure both DataFrames contain data before proceeding
    if not updated_inclusion_df.empty:
        # Extract the NCT ID from the first row (since all rows should have the same NCT ID)
        nct_id = updated_inclusion_df['NCT ID'].iloc[0]

        # Remove all rows for the given NCT ID from the original inclusion DataFrame
        inclusion_df = inclusion_df[inclusion_df['NCT ID'] != nct_id]

        # Append the new rows for the NCT ID
        inclusion_df = pd.concat([inclusion_df, updated_inclusion_df], ignore_index=True)

    if not updated_exclusion_df.empty:
        # Extract the NCT ID from the first row (since all rows should have the same NCT ID)
        nct_id = updated_exclusion_df['NCT ID'].iloc[0]

        # Remove all rows for the given NCT ID from the original exclusion DataFrame
        exclusion_df = exclusion_df[exclusion_df['NCT ID'] != nct_id]

        # Append the new rows for the NCT ID
        exclusion_df = pd.concat([exclusion_df, updated_exclusion_df], ignore_index=True)

    # Save the updated DataFrames back to their CSV files
    inclusion_df.to_csv('all_inclusion_criteria_with_ref.csv', index=False)
    exclusion_df.to_csv('all_exclusion_criteria_with_ref.csv', index=False)

    return jsonify({'message': 'Data updated successfully'}), 200

# Assuming the following functions are defined:
# load_data(), process_patients(), and a smaller_model object

@app.route('/patient_matching_engine', methods=['GET'])
def patient_matching_engine():
    try:
        # Load data
        inclusion_data, exclusion_data, patient_data = load_data()
        # patient_data['Name'] = ['patient1', 'patient2', 'patient3', 'patient4', 'patient5', 'patient6']
        model_name = smaller_model  # Define your WatsonXAI model name here
        # Save the results to CSV files
        inclusion_file = "all_patients_all_inclusion_dfs.csv"
        exclusion_file = "all_patients_all_exclusion_dfs.csv"
        # Process patients using inclusion criteria
        final_inclusion_df = process_patients(inclusion_data, patient_data, model_name, criteria_type='inclusion')
        final_inclusion_df.to_csv(inclusion_file, index=False)  # Save inclusion results
        # Process patients using exclusion criteria
        final_exclusion_df = process_patients(exclusion_data, patient_data, model_name, criteria_type='exclusion')
        final_exclusion_df.to_csv(exclusion_file, index=False)  # Save exclusion results
        pd.DataFrame({'status': [False]}).to_csv('cancel.csv', index=False)
        # If everything is successful, return success message
        return jsonify({"message": "Successfully executed"}), 200

    except Exception as e:
        # If an error occurs, return a 500 status with an error message
        pd.DataFrame({'status': [False]}).to_csv('cancel.csv', index=False)
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

@app.route('/fetch_patient_matching_results', methods=['POST'])
def fetch_patient_matching_results():
    data = request.json
    nct_id = data.get('nct_id')
    patient_name = data.get('patient_name')

    # Load the exclusion, inclusion, and patient data files (assuming CSV format)
    exclusion_df = pd.read_csv('all_patients_all_exclusion_dfs.csv')
    inclusion_df = pd.read_csv('all_patients_all_inclusion_dfs.csv')
    patient_data_df = pd.read_excel('clinical_trial.xlsx')  # Replace with actual patient data file path

    # Filter based on NCT ID and Patient Name
    filtered_exclusion = exclusion_df[(exclusion_df['Trial'] == nct_id) & 
                                      (exclusion_df['Patient'] == patient_name)].drop(['Unnamed: 0', 'Unnamed: 0.1'], axis=1, errors='ignore')
    filtered_inclusion = inclusion_df[(inclusion_df['Trial'] == nct_id) & 
                                      (inclusion_df['Patient'] == patient_name)].drop(['Unnamed: 0', 'Unnamed: 0.1'], axis=1, errors='ignore')

    # Filter patient data based on NCT ID and Patient Name
    filtered_patient_data = patient_data_df[(patient_data_df['Name'] == patient_name)]

    # Combine the filtered data and return as JSON
    result = {
        'filtered_exclusion': filtered_exclusion.fillna('').to_dict(orient='records'),
        'filtered_inclusion': filtered_inclusion.fillna('').to_dict(orient='records'),
        'patient_data': filtered_patient_data.fillna('').to_dict(orient='records')
    }

    return jsonify(result)

@app.route('/update_matching_results', methods=['POST'])
def update_matching_results():
    data = request.json
    nct_id = data.get('nct_id')
    patient_name = data.get('patient_name')
    # print(nct_id)
    updated_exclusion = pd.DataFrame(data.get('filtered_exclusion')).drop(['id'], axis=1, errors='ignore')
    updated_inclusion = pd.DataFrame(data.get('filtered_inclusion')).drop(['id'], axis=1, errors='ignore')
    # updated_patient_data = pd.DataFrame(data.get('patient_data'))
    # print(updated_exclusion)
    # Load the original data files
    exclusion_df = pd.read_csv('all_patients_all_exclusion_dfs.csv')
    inclusion_df = pd.read_csv('all_patients_all_inclusion_dfs.csv')
    # patient_data_df = pd.read_excel('clinical_trial.xlsx')  # Replace with actual patient data file path
    
    # Remove rows matching the NCT ID and Patient Name
    exclusion_df = exclusion_df[~((exclusion_df['Trial'] == nct_id) & 
                                  (exclusion_df['Patient'] == patient_name))]
    inclusion_df = inclusion_df[~((inclusion_df['Trial'] == nct_id) & 
                                  (inclusion_df['Patient'] == patient_name))]
    
    # print(nct_id, patient_name)
    # print(exclusion_df['Trial'][0])
    # print(inclusion_df['Trial'][0])
    # patient_data_df = patient_data_df[patient_data_df['Name'] != patient_name]
    # print(exclusion_df)
    # Append the updated data back to the original DataFrames
    exclusion_df = pd.concat([exclusion_df, updated_exclusion], ignore_index=True)
    inclusion_df = pd.concat([inclusion_df, updated_inclusion], ignore_index=True)
    # patient_data_df = pd.concat([patient_data_df, updated_patient_data], ignore_index=True)

    # Save the updated DataFrames back to their respective files
    exclusion_df.to_csv('all_patients_all_exclusion_dfs.csv', index=False)
    inclusion_df.to_csv('all_patients_all_inclusion_dfs.csv', index=False)
    # patient_data_df.to_excel('clinical_trial.xlsx', index=False)  # Ensure file path is correct

    return jsonify({'message': 'Data updated successfully'})

@app.route('/get_nct_patient_list', methods=['GET'])
def get_nct_patient_list():
    # Load the clinical trials file to get the patient list
    clinical_trials_df = pd.read_excel('clinical_trial.xlsx')
    
    # Load only one file for NCT IDs (inclusion_df)
    inclusion_df = pd.read_csv('all_patients_all_inclusion_dfs.csv')
    
    # Extract the 'Name' column from clinical trials for patient names
    patient_names = clinical_trials_df['Name'].drop_duplicates().tolist()
    
    # Extract unique NCT IDs from the inclusion file
    unique_nct_ids = inclusion_df['Trial'].drop_duplicates().tolist()

    # Prepare the result
    result = {
        'nct_ids': unique_nct_ids,
        'patient_names': patient_names,
    }

    return jsonify(result)

@app.route('/get_trial_summary', methods=['POST'])
def get_trial_summary():
    try:
        # Parse the trial ID from the request body
        data = request.get_json()
        trial_id = data.get('trial_id')

        if not trial_id:
            return jsonify({"error": "Trial ID is required"}), 400
        exclusion_df = pd.read_csv('all_patients_all_exclusion_dfs.csv')
        inclusion_df = pd.read_csv('all_patients_all_inclusion_dfs.csv')
        # Calculate patient percentages for inclusion and exclusion
        inclusion_summary = calculate_patient_percentages_for_trial(inclusion_df, trial_id)
        exclusion_summary = calculate_patient_percentages_for_trial(exclusion_df, trial_id)

        # Return the results as a JSON response
        return jsonify({
            'inclusion_summary': inclusion_summary,
            'exclusion_summary': exclusion_summary
        }), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/save_study_data', methods=['POST'])
def save_study_data():
    data = request.json
    # Set default base URL
    base_url = 'https://clinicaltrials.gov/api/v2/studies/'
    nct_ids_text = data.get('nct_ids')  # Receive NCT IDs as a comma-separated string
    output_file = 'downloaded_trial_data.csv'  # Optional output file name
    
    if not nct_ids_text:
        return jsonify({'error': 'nct_ids are required'}), 400

    # Split the NCT IDs by comma and strip any whitespace
    nct_ids = [nct_id.strip() for nct_id in nct_ids_text.split(',')]

    # Call the function to fetch and save the study data
    try:
        fetch_and_save_study_data(base_url, nct_ids, output_file)
        return jsonify({'message': f'Study data saved to {output_file}'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download-csv', methods=['GET'])
def download_csv():
    # Get the file name from query parameters
    file_name = request.args.get('fileName')
    
    # Validate the file name and check if it exists
    if not file_name:
        abort(400, description="No file name provided")
    
    # Construct the file path from the current working directory (CWD)
    file_path = os.path.join(os.getcwd(), file_name)
    
    if not os.path.exists(file_path) or not file_name.endswith('.csv'):
        abort(404, description="File not found or not a CSV file")
    
    # Send the file to the UI
    return send_file(file_path, as_attachment=True, download_name=file_name)



@app.route('/filter_data', methods=['POST'])
def filter_data():
    data = request.json
    filter_flag = data.get('filter', False)
    file_name = data.get('file_name')
    nct_id = data.get('nct_id')
    patient = data.get('patient')

    # Path to the file
    file_path = os.path.join(os.getcwd(), file_name)  # Assuming the files are in 'uploads' folder

    try:
        # Check if the file exists before attempting to read
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        # Read the CSV file
        df = pd.read_csv(file_path)

        if not filter_flag:
            # If no filtering is required, return the CSV for download
            return send_file(file_path, as_attachment=True)

        # Filter based on the presence of nct_id and patient
        if filter_flag:
            if nct_id and patient:
                filtered_df = df[(df['Trial'] == nct_id) & (df['Patient'] == patient)]
            elif nct_id:
                filtered_df = df[df['NCT ID'] == nct_id]
            else:
                return jsonify({"error": "NCT ID or Patient information is missing for filtering"}), 400

            # Save the filtered data to a new CSV file
            filtered_file_name = f"filtered_{file_name}"
            filtered_file_path = os.path.join('uploads', filtered_file_name)
            os.makedirs(os.path.dirname(filtered_file_path), exist_ok=True)
            filtered_df.to_csv(filtered_file_path, index=False)

            # Return the filtered file for download
            return send_file(filtered_file_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_patient_trial_summary', methods=['POST'])
def get_patient_trial_summary():
    # Extract data from POST request
    data = request.get_json()
    patient_id = data.get('patient_id')
    trial = data.get('trial')
    # Load the CSV file once to avoid reloading on every request
    df = pd.read_csv('patient_trial_evaluation_summaries.csv')
    # Filter the DataFrame for the given patient and trial
    result = df[(df['Patient'] == patient_id) & (df['Trial'] == trial)]
    
    # If the result is found, return inclusion and exclusion summaries
    if not result.empty:
        inclusion_summary = result['Inclusion Evaluation Summary'].values[0]
        exclusion_summary = result['Exclusion Evaluation Summary'].values[0]
        return jsonify({
            'patient_id': patient_id,
            'trial': trial,
            'inclusion_summary': inclusion_summary,
            'exclusion_summary': exclusion_summary
        }), 200
    else:
        # If no matching record is found, return an error
        return jsonify({'error': 'No matching record found'}), 404
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

