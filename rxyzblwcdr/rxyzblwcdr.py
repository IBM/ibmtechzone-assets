import gradio as gr
import time
import os
import pandas as pd
from datetime import datetime
import json
import threading

global translation
translation = "OFF"

def handle_refresh():
    print("Page is refreshed")

active_time = time.time()
class Relogin:
    def __init__(self):
        global active_time
        active_time = time.time()
  
def check_inactivity():
    global active_time
    print("active_time in def is:",active_time)
    while True:
        time.sleep(1)
        if time.time() - active_time > 180:  # 180 seconds
            active_time=time.time()
            print("session have been inactive for more than 3 minutes")  


# Start the inactivity check in a separate thread
thread = threading.Thread(target=check_inactivity)
thread.daemon = True
thread.start()

def ui():

    summary_status = "ON"
    with gr.Blocks() as demo:
        gr.Markdown("Smart Search AI Assistant")

       
        with gr.Column():

            #Question entry
            gr.Markdown("##### 1.Enter the search question here")
            question = gr.Textbox(label="", value= "User inputs the question here")
            question.change(Relogin)
            
            #Search target (multiple sources) selection (check box)
            gr.Markdown("##### 2.Select ")
            with gr.Column():
                a = gr.Checkbox(label="doc1", info="", value = True, interactive = True)
                a.change(Relogin, inputs=None, outputs=None)
                b = gr.Checkbox(label="doc2", info="", value = True, interactive = True)
                b.change(Relogin, inputs=None, outputs=None)

            
            ##search parameter
            gr.Markdown("##### 3.set the search parameters")
            with gr.Row():
                with gr.Column(): 
                    n_show = gr.Number(label = "Enter the chunk size to be displayed", minimum = "0", maximum = "10", value = "3", interactive = True)
                    n_show.change(Relogin, inputs=None, outputs=None)
                with gr.Column(): 
                    thres = gr.Number(label = "Enter the threshold value for similarity check", minimum = "0", maximum = "100", value = "70", interactive = True)
                    thres.change(Relogin, inputs=None, outputs=None)
                with gr.Column(): 
                    summary_request = gr.Radio(["ON", "OFF"], value="ON", label="Summary of the chunk",interactive = True)  
                    summary_request.change(Relogin)
              
                
            search_button = gr.Button("search")
            search_button.click(Relogin)
    
            suggest_source = gr.Textbox(label="Top source code", value="Top chunks will be displayed here")
            suggest_source.change(Relogin)
            
            
            # answer generation
            gr.Markdown("##### Select the sources to generate the answer")
            with gr.Row():
                with gr.Column(): 
                    id_var = gr.CheckboxGroup(choices = [],label="select the chunks for answer generation",info="",value=[])
                    id_var.change(Relogin, inputs=None, outputs=None)
                
                with gr.Column(): 
                    LLM_choice = gr.Dropdown(
                        [
                        'meta-llama/llama-3-70b-instruct',
                        'ibm-mistralai/mixtral-8x7b-instruct-v01-q',
                        'elyza-japanese-llama-2',
                        'ibm/granite-8b-japanese'
                        ], 
                        value="ibm-mistralai/mixtral-8x7b-instruct-v01-q", multiselect=False, label="model", info="Select the model.")
                
                with gr.Column(): 
                    translation_request = gr.Radio(["ON", "OFF"], value="ON", label="Japanese translation",interactive = True)  
                    translation_request.change(Relogin)
            
            result_button = gr.Button("Generate answer")  
            result_button.click(Relogin)
            final_answer = gr.Textbox(label="final answer", value="")
            final_answer.change(Relogin)

        with gr.Accordion("Developer:"):
            gr.Markdown("IBM Client Engineering, Insurance Team")

    
        search_button.click(answer_generation, inputs=[], outputs=[suggest_source])
        result_button.click(stream_answer, inputs=[], outputs=[final_answer])
        demo.load(handle_refresh, inputs=None, outputs=None)


    # Additional tabs and functionalities can be defined following the similar structure
    demo.queue()
    demo.launch()
    

def answer_generation():

    return "This displays the top chunks"

def num_checkbox_update(n_show):
    
    choices = [str(i) for i in range(1, n_show + 1)]
    return gr.update(choices=choices,value=choices)

def stream_answer():
    answer= "This displays the generated answer"
    for i in range(len(answer)):
        time.sleep(0.01)
        yield answer[:i+1]


ui()





