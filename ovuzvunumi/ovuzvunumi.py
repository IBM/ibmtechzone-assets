import os
import sqlite3
import pandas as pd
import gradio as gr

from app.services.prompt_gen import answer_question
from app.template.css import CUSTOM_CSS


BANNER_PATH = os.path.join(os.getcwd(), "app/images/banner.jpg")

DB_PATH = os.path.join(os.getcwd(), "app/db/Tvshows.db")


def get_frame(query):
    try:
        connection_object = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, connection_object)
        search_results = "No. of records: {}".format(str(df.shape[0]))
        return df, search_results
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return None, None
    finally:
        if connection_object:
            connection_object.close()


def get_metadata(arg1):
    return ""


with gr.Blocks(theme=gr.themes.Soft(), css=CUSTOM_CSS) as demo:
    gr.Image(BANNER_PATH, show_label=False)
    
    
    ############ English UI  ############
    
    ## For English UI, comment from line 62-77 and uncomment until from line 41-56
    
    gr.Markdown(
        "<center><span style='font-size: 26px; font-weight: bold;'>SQL Query Generator</span></center>")  # You can use Markdown to create a title
    input_textbox = gr.Textbox(label="Input", lines=2, placeholder="Enter the natural language query")
    submit_button0 = gr.Button("Generate Metadata & SQL", elem_id="custom-button1-id",
                                       elem_classes=["custom-button1-class"])
    gr.Markdown(
            "<left><span style='font-size: 26px; font-weight: bold;'>AI BOT Output</span></left>")  
    with gr.Row():
        with gr.Column():
            metadata_textbox = gr.Textbox(label="Output Metadata", lines=2)
            output_textbox = gr.Textbox(label="Output SQL", lines=2)
            submit_button1 = gr.Button("Get Result", elem_id="custom-button-id",
                                       elem_classes=["custom-button-class"])
        with gr.Column():
            records_textbox = records_textbox = gr.Markdown(label="No. of records: ")
            frame_box = gr.Dataframe(label="Result of SQL query")
    
    ############ Japanese UI  ############
    
    ## For Japanese UI, comment from line 41-56 and uncomment from line 62-77
    
    # gr.Markdown(
    #     "<center><span style='font-size: 26px; font-weight: bold;'>自然言語でRDBを検索するデモ</span></center>")  # You can use Markdown to create a title
    # input_textbox = gr.Textbox(label="ほしいデータを自然言語で入力してください", lines=2, placeholder="ここに入力")
    # submit_button0 = gr.Button("表・列名を選択し、SQLを生成します", elem_id="custom-button1-id",
    #                                elem_classes=["custom-button1-class"])
    # gr.Markdown(
    #     "<left><span style='font-size: 26px; font-weight: bold;'>AIボット出力</span></left>")  
    # with gr.Row():
    #     with gr.Column():
    #         metadata_textbox = gr.Textbox(label="選択された表名および列名", lines=2)
    #         output_textbox = gr.Textbox(label="生成されたSQL", lines=2)
    #         submit_button1 = gr.Button("生成されたSQLを実行します", elem_id="custom-button-id",
    #                                    elem_classes=["custom-button-class"])
    #     with gr.Column():
    #         records_textbox = records_textbox = gr.Markdown(label="行数: ")
    #         frame_box = gr.Dataframe(label="SQL実行結果")

    # Define what happens when you click the submit button
    submit_button0.click(
        fn=answer_question,
        inputs=input_textbox,
        outputs=[metadata_textbox, output_textbox]
    )
    submit_button1.click(
        fn=get_frame,
        inputs=output_textbox,
        outputs=[frame_box, records_textbox]
    )

# Launch the demo
demo.launch(server_port=7860)