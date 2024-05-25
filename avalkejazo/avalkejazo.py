import gradio as gr
from functools import partial
from src.utils.vector_db import *
from src.utils.query_utils import *
from src.utils.prompt_builder import make_prompt
from config import send_to_watsonxai
from langchain.globals import get_llm_cache
from src.utils.similarity_score import get_top_5_chunks
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_question(vector_dbs, question, slider):
    cache = get_llm_cache()

    cached_response = cache.lookup(question, "")
    if cached_response is not None:
        print("Response found in cache.")
        return cached_response
   
    combined_results = []
    metadatas = []
  
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(partial(query_vector_db, question=question), db) for db in vector_dbs]

        for future in as_completed(futures):
            documents, metadata = future.result()
            combined_results.extend(documents)
            metadatas.extend(metadata)

    flat_metadatas = [metadata for metadata_list in metadatas for metadata in metadata_list if 'file_info' in metadata]

    top_15_results = combined_results[:15]

    all_chunks = [chunk for top_15_results in top_15_results for chunk in top_15_results]

    document_texts = get_top_5_chunks(question, all_chunks,flat_metadatas)

# Uncomment to see the metadata
    # for i, (chunk,metadata, similarity) in enumerate(document_texts, start=1):
    #     # print(f"Chunk {i}:")
    #     # print(chunk)
    #     # print(similarity)
    #     # print("\nFile Info:", metadata['file_info']) 
    #     # print()

    document_texts = [chunk_text for chunk_text, _ , _ in document_texts]

    context = "\n\n\n".join(document_texts)

    prompt = make_prompt(context, question)

    response = send_to_watsonxai(prompt, max_new_tokens=slider)
    

    cache.update(question, "", response)
    
    return response
    
    
  #Example usage
  # def launch_gradio_interface(vector_dbs):
  #   iface = gr.Interface(
  #       fn=partial(process_question, vector_dbs),
  #       inputs=[gr.Textbox(lines=1, label="Question"),gr.Slider(label="Max new tokens", 
  #                                     value=20,  
  #                                     maximum=1024, 
  #                                     minimum=1)],
  #       outputs=[gr.Textbox(lines=5, label="Response")],
  #       title="C.I.R.U.S",
  #       description="<span style = 'size: 24px'>Enter your question and get the answer.</span>",
  #       theme= gr.themes.Monochrome(),
  #   )
  #   iface.launch()
