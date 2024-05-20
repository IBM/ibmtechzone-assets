# Author: Pinkal Patel
'''
Title: Comparison of Analyst Report With Financial Summary And Metrics
Description:
In this project, we can compare two analyst reports about one company and show a financial summary, pros, cons, and financial metrics. It is stored the document in ChromaDB
Input: Two Analyst reports Ex. BALM.pdf and Philips.pdf
Output: financial summary of two reports, pros, cons, and financial metrics

'''
#import subprocess
import sys
#subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
import streamlit as st
import pandas as pd
import concurrent.futures
from streamlit.web import cli as stcli
from streamlit import runtime

if runtime.exists():
  from save_chroma import *
  from helper import extract_paragraphs,LLMresponce,textToTable
# Dummy helper functions to simulate processing
def data_frame(data_1):
    start_prompt_1="""Please extract the following financial metrics from the provided page if available for FY24E  :
        1. Target Stock Price: [Information else "Data not available "]
        2. VNB :[Information else "Data not available "]
        3. APE : [Information else "Data not available "]
        4. VNB Margin: [Information else "Data not available "]
        5. EV : [Information else "Data not available "]
        6. RoEV: [Information else "Data not available "]
        7. P/EV: [Information else "Data not available "]

        note P/EV is Price/ Earnings Ratio
        "
     """
    start_prompt_2="""Please extract the following financial metrics from the provided page if available for FY25E  :
        1. Target Stock Price: [Information else "Data not available "]
        2. VNB :[Information else "Data not available "]
        3. APE : [Information else "Data not available "]
        4. VNB Margin: [Information else "Data not available "]
        5. EV : [Information else "Data not available "]
        6. RoEV: [Information else "Data not available "]
        7. P/EV : [Information else "Data not available "]

        note P/EV is Price/ Earnings Ratio
        "
     """
    end_prompt="Based"
    params={
    "decoding_method": "greedy",
    # "stop_sequences": [
    #   "\n\n"
    # ],
    "min_new_tokens": 1,
    "max_new_tokens": 800,
    # "repetition_penalty": 1.25,
    "moderations": {
      "hap": {
        "input": "false",
        "threshold": 0.75,
        "output": "false"
      }
    }
  }
    print("promt given ")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []  
        futures.append(executor.submit(LLMresponce,start_prompt_1+data_1[0]+data_1[1]+ end_prompt,params))
        futures.append(executor.submit(LLMresponce,start_prompt_2+data_1[0]+data_1[1]+ end_prompt,params))
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    df1 = textToTable(end_prompt+results[0].strip("Note that some of"))
    df2 = textToTable(end_prompt+results[1].strip("Note that some of"))
    # print(df1)
    # print(df2)
    # merging df1 and df2
    merged_df = pd.merge(df1,df2, on = 'Metric')
    merged_df.set_index('Metric',inplace = True)
    return merged_df
def process_summary(data):
    params={
    "decoding_method": "greedy",
    "stop_sequences": [
      "\n\n"
    ],
    "min_new_tokens": 1,
    "max_new_tokens": 500,
    "repetition_penalty": 1.25,
    "moderations": {
      "hap": {
        "input": "false",
        "threshold": 0.75,
        "output": "false"
      }
    }
  }
    summary=LLMresponce("Write a financial summary in 5 points in ~ ' 300 ' words of the below text  : "+ data[0] + "Do not repeat points in summary. \n Executive Summary: \n *",params).strip()
    return summary
def getProCons(data_1,data_2):
    startPrompt_ProCons="""I will provide you with financial data from Company X's latest financial report.
    I need an analysis that outlines the strengths and weaknesses evident in the numbers.
    The data includes various financial metrics such as revenue, expenses, profit margins, debt levels, equity, cash flow, and investment activities.

    Upon presenting the data, please provide:
    2
    A list of pros (positive aspects) that can be inferred from the financial information.
    A list of cons (negative aspects) or potential risks suggested by the data.
    Here is the financial data:
    "
    """
    endPrompt_ProCons="""."

    pros:
    """
    params={
    "decoding_method": "greedy",
    "stop_sequences": [
      "Overall, "
    ],
    "min_new_tokens": 1,
    "max_new_tokens": 1000,
    # "repetition_penalty": 1.25,
    "moderations": {
      "hap": {
        "input": "false",
        "threshold": 0.75,
        "output": "false"
      }
    }
  }
    pro_cons_1=LLMresponce(startPrompt_ProCons+data_1[0]+ endPrompt_ProCons,params).strip()
    pro_cons_2=LLMresponce(startPrompt_ProCons+data_2[0]+ endPrompt_ProCons,params).strip()

    final_pro_cons="""Examine the two provided lists of pros and cons from the financial reports. Create a comprehensive, merged list that includes all unique advantages and disadvantages, making sure to eliminate any duplicates. Tailor this list to be particularly useful for executive members, aiding them in making informed decisions. Ensure that each point on the list is accompanied by a clear and concise explanation, highlighting how it impacts the overall financial health and strategic direction of the company. This explanation should provide deep insights and facilitate smart, strategic decision-making at the executive level"""
    # Highlight any similar points only once and ensure that the final list is a concise summary of all the distinct advantages and disadvantages mentioned
    # """
    params={
    "decoding_method": "greedy",
    # "stop_sequences": [
    #   "Overall, "
    # ],
    "min_new_tokens": 1,
    "max_new_tokens": 1000,
    "repetition_penalty": 1.25,
    "moderations": {
      "hap": {
        "input": "false",
        "threshold": 0.75,
        "output": "false"
      }
    }
  }
    return pro_cons_1,pro_cons_2,LLMresponce(final_pro_cons+"pros: "+pro_cons_1+"pros: "+pro_cons_2+"consolidated pros:",params)


#logo_path = 'src/logo.jpg'
#logo = Image.open(logo_path)
if runtime.exists():
  #st.image(logo, use_column_width=True)
  st.title("Analyst Report Summary")
  # File uploader for Entity 1
  st.title("Analyst Report  1")
  entity1_file = st.file_uploader("Report 1 ", type=['pdf'])
  # File uploader for Entity 2
  st.title("Analyst Report 2")
  entity2_file = st.file_uploader("Report 2 ", type=['pdf'])
  if entity1_file is not None:
    filename1 = entity1_file.name.split()[0].strip(".pdf")
  if entity2_file is not None:
    filename2 = entity2_file.name.split()[0].strip(".pdf")
  # Placeholder for summaries
  summary_placeholder = st.empty()
  pros_placeholder = st.empty()
  cons_placeholder = st.empty()
  if entity1_file is not None and entity2_file is not None:
      data_1 = extract_paragraphs(entity1_file)
      data_2 = extract_paragraphs(entity2_file)

      with st.spinner(f'Processing {filename1}...'):
          with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
              futures = []
              futures.append(executor.submit(process_summary, data_1))
              futures.append(executor.submit(process_summary, data_2))
              results = [future.result() for future in concurrent.futures.as_completed(futures)]

          summary1= "* "+results[0]
          summary2 = "* "+results[1]
      summary_placeholder.subheader("Document Summaries")
      st.write(f"{filename1} Summary: \n\n", summary1)
      st.write(f"{filename2} Summary: \n\n", summary2)
      # Display Pros and Cons
      with st.spinner('Processing ...'):
          PC_1,PC_2,PC_T=getProCons(data_1,data_2)
          # pros_placeholder.subheader("Pros & Cons")
          st.write(f"{filename1} \n\n  Pros: \n\n "+PC_1)
          st.write(f"{filename2} \n\n  Pros: \n\n "+PC_2)
          st.write("consolidated pros: \n\n "+PC_T)
      st.subheader("Data Tables")
      with st.spinner('Processing ...'):
          # with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
          #     futures = []
          #     futures.append(executor.submit(data_frame, data_1))
          #     futures.append(executor.submit(data_frame, data_2))
          #     results = [future.result() for future in concurrent.futures.as_completed(futures)]
          a1,b2=saveDb(data_1,data_2)
      col1, col2 = st.columns(2)
      with col1:
          st.markdown(f"**{filename1} Data Table**")
          st.dataframe(a1,hide_index=True)
      with col2:
          st.markdown(f"**{filename2} Data Table**")
          st.dataframe(b2,hide_index=True)

if __name__ == '__main__':
    if runtime.exists():
        print("Running ......")
    else:
        ibm_cloud_url = sys.argv[1]
        watson_ai_project_id = sys.argv[2]
        watson_ai_api_key = sys.argv[3]

        #make file
        filename = ".env"
        with open(filename, "w") as file:
            file.write(f"IBM_CLOUD_URL={ibm_cloud_url}\n")
            file.write(f"PROJECT_ID={watson_ai_project_id}\n")
            file.write(f"API_KEY={watson_ai_api_key}\n")

        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())