import os
import json
import pandas as pd
import time
import re
import io
from utils import data_preprocess, response_generation, response_generation_llm, data_preprocess
from BOI_issue_prediction import boi_prediction
from utils import extracted_keywords
from sklearn.preprocessing import MinMaxScaler
import streamlit as st
import requests
import pandas as pd
import webbrowser
session_state = st.session_state

file_name = "dummy_Issue_responses_file.xlsx" #Replace with the file path where the file is located
st.markdown(
	f"""
	<style>
		.logo {{
			position: absolute;
			top: 10px; 
			left: 10px; 
			width: 100px; 
			height: auto; 
		}}
	</style>
	""",
	unsafe_allow_html=True
)


button_style = """
	<style>
	.stButton>button {
		width: 200px; /* Adjust width to change button size */
		height: 50px; /* Adjust height to change button size */
	}
	.wide-button {
		width: 680px !important; /* Adjust width to make it wider */
		height: 50px;
	}
	</style>
"""
st.markdown(button_style, unsafe_allow_html=True)

def upload_file_to_server(file):

	df = pd.read_excel(file)
	return df


# Function to assign sentiment based on star rating
def assign_sentiment(rating):
	sentiment_map = {
		1: "Negative",
		2: "Negative",
		3: "Neutral",
		4: "Positive",
		5: "Positive"
	}
	return sentiment_map.get(rating, "unknown")

# Function to save the sentiment in data
def save_assign_sentiment(test_data):
	i=0
	test_data['Sentiment'] = None
	max_column = len(test_data.columns)-1
	for rating in test_data["Star Rating"]:
		test_data.iloc[i,max_column] = assign_sentiment(rating)
		i+=1
	return test_data

# To identify the negative sentiment count based on star rating
def star_rating_negative_count(test_data):

	# creation of new dataframe with two columns
	df = test_data[['predicted_issue', 'Sentiment']]

	# Split the issues in each row and explode the dataframe
	df['predicted_issue'] = df['predicted_issue'].str.split(', ')
	df = df.explode('predicted_issue')

	# Group by 'predicted_issue' column and count the occurrences of 'negative' sentiment
	negative_counts = df[df['Sentiment'] == 'Negative'].groupby('predicted_issue').size().reset_index(name='negative_count')

	return negative_counts

# Function to count the occurrence of issue
def issues_recurrence(issue_list):
	test_data = pd.DataFrame(issue_list,columns = ['predicted_issue'])
	sentiment_counts = test_data.groupby('predicted_issue').size().reset_index(name='issue_count')
	return sentiment_counts

# To extract the bad keywords based on review text
def extracted_keywords_function(test_data):
	test_data['extracted_keywords_for_severity'] = None
	test_data['count_bad_keywords'] = None
	extracted_keywords_data = extracted_keywords.extracted_issue_prediction(test_data)
	return extracted_keywords_data

# To get the bad keyword count based on bad keywords extracted
def extracted_keywords_overall_count(test_data):
	# To extract bad keywords from review 
	extracted_keywords_analysis = extracted_keywords_function(test_data)
	extracted_keywords_analysis.to_excel('extracted_bad_keywords.xlsx', index = False)

	# creation of new dataframe with two columns
	df = test_data[['predicted_issue', 'count_bad_keywords']]

	# Split the issues in each row and explode the dataframe
	df['predicted_issue'] = df['predicted_issue'].str.split(', ')
	df = df.explode('predicted_issue')

	total_keyword_count = df.groupby('predicted_issue')['count_bad_keywords'].sum().reset_index()
	new_df = total_keyword_count.rename(columns={'keyword_count': 'total_keyword_count'})
	return new_df


# To get the severity data by merging dataframes with star rating sentiment and issue recurrence
def severity_count_data(test_data, issue_list):
	issue_count = issues_recurrence(issue_list)

	# For asssigning sentiment based on star rating 
	star_rating_sentiment = save_assign_sentiment(test_data)

	# For finding count of negative sentiment in each of the issue based on star rating
	star_severity_analysis_logic = star_rating_negative_count(star_rating_sentiment)

	# To get the dataframe with predicted issue and total count of each of the issue
	keyword_count = extracted_keywords_overall_count(test_data)

	severity_input = pd.merge(issue_count, keyword_count, on='predicted_issue', how='outer')
	severity_input = pd.merge(severity_input, star_severity_analysis_logic, on='predicted_issue', how='outer')
	severity_input = severity_input.fillna(0)
	return severity_input

# Function to normalize the valuse of two columns and get the final score
def severity_score(severity_data):
	final_score = []
	scaler = MinMaxScaler()
	severity_data[['issue_count_norm','bad_keyword_norm','negative_count_norm']] = scaler.fit_transform(severity_data[['issue_count','count_bad_keywords','negative_count']])
	final_score = (0.3 * severity_data['issue_count_norm'] + 0.2 * severity_data['bad_keyword_norm'] + 0.5 * severity_data['negative_count_norm'])
	return final_score

# Function to categorize the score based on thresholds
def categorize_score(score):
	if score >= 0.3:
		return 'High'
	elif 0.1 <= score < 0.3:
		return 'Medium'
	else:
		return 'Low' 

# Function to assign categories for multiple issues
def assign_category(test_data,test_output):
	nan_indices = test_data[test_data['Severity Category'].isna()].index.tolist()
	for item in nan_indices:
		strings = test_data.loc[item,'predicted_issue'].split(', ')
		category = []
		for issue in strings:
			for i in range(len(test_output)):
				if test_output.iloc[i,0].find(issue)!=-1:
					# print("category", test_output.iloc[i,8])
					category.append(test_output.iloc[i,8])
		# print(i, "category", category)
		# print(i, "predicted issue", test_data.loc[item,'predicted_issue'])
		if 'High' in category:
			test_data.loc[item,'Severity Category'] = 'High'
		elif 'Medium' in category:
			test_data.loc[item,'Severity Category'] = 'Medium'
		elif 'Low' in category:
			test_data.loc[item,'Severity Category'] = 'Low'
		elif test_data.loc[item,'predicted_issue'] == 'Good' or test_data.loc[item,'predicted_issue'] == 'Good app' or test_data.loc[item,'predicted_issue'] == 'Good user experience' or test_data.loc[item,'predicted_issue'] == 'Good service'or test_data.loc[item,'predicted_issue'] == 'Useful app' or test_data.loc[item,'predicted_issue'] == 'Good service' or test_data.loc[item,'predicted_issue'] == 'Good App' or test_data.loc[item,'predicted_issue'] == 'nan' :
			if test_data.loc[item,'Sentiment'] == 'Negative':
				test_data.loc[item,'Severity Category'] = 'Low'
			else:
				test_data.loc[item,'Severity Category'] = ''
		else:
			continue
	return test_data

# function to assign the final severity category to each of the predicted issue
def severity(issue_prediction, issue_list):

	# To get the dataframe merging two dataframes, one from issue recurrence and other from negative sentiment count 
	severity_output = severity_count_data(issue_prediction, issue_list)

	# severity_output = severity_output[~(severity_output['predicted_issue'].str.startswith('Useful') | severity_output['predicted_issue'].str.startswith('Good'))]
	severity_output = severity_output[~(severity_output['predicted_issue'].str.startswith('Useful') | severity_output['predicted_issue'].str.startswith('Good') | severity_output['predicted_issue'].str.startswith('nan'))]
	
	# Define the list of strings to exclude
	strings_to_exclude = ['S']

	# Modify the statement
	severity_output = severity_output[~severity_output['predicted_issue'].isin(strings_to_exclude)]

	# Function to get the severity score
	severity_output['Severity_Score'] = severity_score(severity_output)
   
	# Apply the function to the 'Severity_Score' column and create a new column 'Category'
	severity_output['Severity Category'] = severity_output['Severity_Score'].apply(categorize_score)
	severity_output.to_excel("assigned_severity.xlsx", index=False) 

	# Merge the two DataFrames on the 'predicted_issue' column using left merge
	severity_data = pd.merge(issue_prediction, severity_output[['predicted_issue', 'Severity Category']], on='predicted_issue', how='left')

	# To assign the categories to original preprocessed data
	severity_data = assign_category(severity_data,severity_output)
	columns_to_drop = ['extracted_keywords_for_severity', 'count_bad_keywords']
	severity_data.drop(columns = columns_to_drop, inplace=True)
	
	return severity_data


def main():
	st.subheader("App Review Analysis & Automated Response Generation")
	st.write("")
	st.write("")
	st.write("")
	st.write("")
	col1, col2, col3 = st.columns(3)
	uploaded_file = None
	device_df = None
	if 'clicked' not in st.session_state:
		st.session_state.clicked = False
	if 'upload' not in st.session_state:
		st.session_state.upload = True
	if 'device_df' not in st.session_state:
		st.session_state.device_df = None
	def set_clicked():
		st.session_state.clicked = True

	def set_upload():
		st.session_state.upload = True
		if uploaded_file is not None:
			st.write("File Uploaded Successfully")
			processing_message = st.empty() 
			processing_message.write("Processing file...")  
			progress_bar = st.progress(0)  
			df = data_preprocess.preprocessing(uploaded_file)
			progress_bar.progress(20)  
			issue_prediction, issue_list = boi_prediction(df)
			progress_bar.progress(40)  
			severity_data = severity(issue_prediction, issue_list)
			progress_bar.progress(60)  
			df_response = response_generation.response(severity_data, file_name)
			progress_bar.progress(80) 
			st.session_state.device_df = response_generation_llm.response_generation_llm(df_response)
			progress_bar.progress(100)  
			processing_message.empty()
			st.write("Processed File Review")  

	with col1:
		st.button('Upload', on_click=set_clicked)
		if st.session_state.clicked:
			uploaded_file = st.file_uploader("Please upload the file", type="xlsx")
			
			#set_upload()
			if uploaded_file is not None and st.session_state.upload:
				set_upload()
				st.session_state.upload = False
			
	with col2:
		# Download button
		if st.button("Download", key="download"):

			device_df = st.session_state.device_df
			if device_df is not None:
				excel_buffer = io.BytesIO()
				device_df.to_excel(excel_buffer, index=False)
				excel_bytes = excel_buffer.getvalue()
				st.write("Please download the file")
				st.download_button(label='Click to Download',
									data=excel_bytes,
									file_name='output.xlsx',
									mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
	with col3:
		if st.button("Cognos Dashboard", key="third"):
			st.write("")
	st.write("")
	st.write("")
	
	device_df = st.session_state.device_df
	
	if device_df is not None:
		st.write(device_df)

if __name__ == "__main__":
	main()
