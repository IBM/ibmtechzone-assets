import time
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import CrossEncoder
from watson_ai_api import get_watson_ai_output
from multiprocessing import Pool
import concurrent.futures
import shutil
import time
import os
from langchain.embeddings import HuggingFaceInstructEmbeddings
import pandas as pd
global dbs1
global dbs2

model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)
embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large")
TOKENIZERS_PARALLELISM = True
#7. P/EV is "Price/Earnings Ratio".
#8. Target Stock Price is Price objective or stock data.
RAG_PROMPT = """
    Please answer the given question using input document.
    Intruction:
    1. You will be given a document that must be used to reply to user questions.
    2. You should generate response only using the information available in the input documents.
    3. If you can't find an answer, strictly say only "Data not available".
    4. Do not use any other knowledge.
    5. Please generate the answer in tabular format only.
    6. Please mention unite Mn or Bn for financial metrics in answer.
   
    Input:
    {context_document}

    Question: {query}
    Output:
    """
# query_list = [
#         '''Please extract the following financial metrics if available for financial year 2024(FY24E) and 2025(FY25E) in tablur format:
#         1. VNB : 
#         3. VNB Margin:
#         ''',
#         '''Please extract the following financial key metric if available for financial year 2024(FY24E) and 2025(FY25E) in tablur format:
#         1. APE : 
#         ''',
#         '''Please extract the following financial metrics if available for financial year 2024(FY24E) and 2025(FY25E) in tablur format:
#         RoEV : [Information else ""]
#         ''',
#         '''Please extract the following financial metrics if available for financial year 2024(FY24E) and 2025(FY25E) in tablur format:
#         P/EV : [Information else ""]
#         ''',
#         '''Please extract the following financial metrics if available for financial year 2024(FY24E) and 2025(FY25E) in tablur format:
#         Target Stock Price: [Information else ""]
#         '''
#         ]

query_list = [
        '''Please extract the following financial metrics if available for financial year 2024(FY24E) and 2025(FY25E) in tablur format:
        1. VNB :
        2. APE
        3. VNB Margin:
        '''
        ]

def rerank_results(data, top_k=5):
    # print(data.to_numpy())
    global model
    # data = [(query, doc[0].page_content) for doc in docs]
    scores = model.predict(data[['query','paragraph']].to_numpy())
    data['score'] = scores
    # df = pd.DataFrame([(data[i][0].page_content, scores[i]) for i in range(len(data))], columns=['passage', 'score'])
    data = data.sort_values(by='score', ascending=False)
    return data[:top_k]

def save_data_to_chroma(data,chunk_size,chunk_overlap,croma_save_dir):
    if os.path.isdir(croma_save_dir):
        shutil.rmtree(croma_save_dir)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size, chunk_overlap = chunk_overlap)
    text_chunks = text_splitter.create_documents(data)
    Chroma.from_documents(text_chunks, embeddings, persist_directory = croma_save_dir)

def saveDb(data1, data2):
    chunk_size1 = 800
    chunk_overlap1 = 0
    db_name1 = "db1"
    chunk_size2 = 800
    chunk_overlap2 = 0
    db_name2 = "db2"

    croma_save_dir1 = 'db_{}_{}_db1'.format(chunk_size1, chunk_overlap1)
    croma_save_dir2 = 'db_{}_{}_db2'.format(chunk_size2, chunk_overlap2)
    save_data_to_chroma(data1,chunk_size1,chunk_overlap1,croma_save_dir1)
    save_data_to_chroma(data2,chunk_size2,chunk_overlap2,croma_save_dir2)
    dbs1 = Chroma(persist_directory=croma_save_dir1, embedding_function = embeddings)
    dbs2 = Chroma(persist_directory=croma_save_dir2, embedding_function = embeddings)
    
    
    query1_doc_list = []
    query2_doc_list = []
    for ind,que in enumerate(query_list):
        query1 = que
        query2 = que
        docs1 = dbs1.similarity_search_with_relevance_scores(query1, k=15)
        docs2 = dbs2.similarity_search_with_relevance_scores(query2, k=14)
        _docs1 = pd.DataFrame([(query1, doc[0].page_content) for doc in docs1], columns=['query', 'paragraph'])
        _docs2 = pd.DataFrame([(query2, doc[0].page_content) for doc in docs2], columns=['query', 'paragraph'])
        _docs1 = _docs1.drop_duplicates(["paragraph"])
        _docs1 = rerank_results(_docs1, top_k=10)
        _docs2 = _docs2.drop_duplicates(["paragraph"])
        _docs2 = rerank_results(_docs2, top_k=10)
        query1_doc_list.append(["1:"+query1,"\n\n".join(_docs1['paragraph'])[:3500]])
        query2_doc_list.append(["2:"+query2,"\n\n".join(_docs2['paragraph'])[:3500]])
    query_doc_list = query1_doc_list + query2_doc_list
    
    start = time.perf_counter()
    query_ans_dict=dict()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        output = dict((executor.submit(get_watson_ai_output,query,document),query) for query,document in query_doc_list)
    for output_fun in concurrent.futures.as_completed(output):
        query = output[output_fun]
        query_ans_dict[query] = output_fun.result().split("\n\n")[0]
        print("===> ",query,output_fun.result())
    finish = time.perf_counter()
    # print(f'Finished in {round(finish-start, 2)} second(s)')
    query_ans_dict_sorted = sorted(query_ans_dict, key=lambda x:x[1])
    #print(query_ans_dict)
    doc1_ans=[]
    doc2_ans=[]
    for key in query_ans_dict.keys():
        if "1:" in key[:3]:
            doc1_ans.extend([row.replace(':','|').strip('|').split('|') for row in query_ans_dict[key].split('\n') if row and '|---|---|---|' not in row and '| --- | --- | --- |' not in row and 'Metric' not in row])
        if "2:" in key[:3]:
            doc2_ans.extend([row.replace(':','|').strip('|').split('|') for row in query_ans_dict[key].split('\n') if row and '|---|---|---|' not in row and '| --- | --- | --- |' not in row and 'Metric' not in row])
    print("1: ",doc1_ans)
    print("2: ",doc2_ans)
    doc1_df = pd.DataFrame(doc1_ans)
    doc2_df = pd.DataFrame(doc2_ans)
    doc1_df.columns=["Metrics","FE24E","FE25E"]
    doc2_df.columns=["Metrics","FE24E","FE25E"]
    doc1_df["Metrics"] = doc1_df["Metrics"].str.strip()
    doc2_df["Metrics"] = doc2_df["Metrics"].str.strip()
    doc1_df = doc1_df.drop_duplicates("Metrics",keep='last')
    doc2_df = doc2_df.drop_duplicates("Metrics",keep='last')
    #print(doc1_df)
    #print(doc2_df)
    filter_values = ["Target Stock Price","APE","VNB","VNB Margin","P/E ratio","P/EV","RoEV","Price / Earnings Ratio or P/EV","Target Stock Price or PO"]
    doc1_df = doc1_df[doc1_df['Metrics'].isin(filter_values)]
    doc2_df = doc2_df[doc2_df['Metrics'].isin(filter_values)]
    doc1_df = doc1_df.sort_values('Metrics')
    doc2_df = doc2_df.sort_values('Metrics')
    #print(doc1_df)
    #print(doc2_df)
    #doc1_df = doc1_df.iloc[filter_values]
    #doc2_df = doc2_df.iloc[filter_values]

    return doc1_df, doc2_df
    




