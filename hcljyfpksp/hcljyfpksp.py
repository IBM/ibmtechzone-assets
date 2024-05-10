import re
import os
import logging
import torch
import gradio as gr
from threading import Thread
from dotenv import load_dotenv
from transformers import TextIteratorStreamer, AutoTokenizer, AutoModelForCausalLM


load_dotenv()

username = os.environ.get("username", "")
password = os.environ.get("password", "")


# import subprocess
# subprocess.run('pip install flash-attn --no-build-isolation', env={'FLASH_ATTENTION_SKIP_CUDA_BUILD': "TRUE"}, shell=True)

model_id = "vikhyatk/moondream2"
revision = "2024-04-02"
tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)
moondream = AutoModelForCausalLM.from_pretrained(
    model_id, trust_remote_code=True, revision=revision,
    torch_dtype=torch.bfloat16,)
moondream.eval()


def answer_question(img, prompt):
    image_embeds = moondream.encode_image(img)
    streamer = TextIteratorStreamer(tokenizer, skip_special_tokens=True)
    thread = Thread(
        target=moondream.answer_question,
        kwargs={
            "image_embeds": image_embeds,
            "question": prompt,
            "tokenizer": tokenizer,
            "streamer": streamer,
        },
    )
    thread.start()

    buffer = ""
    for new_text in streamer:
        buffer += new_text
        yield buffer.strip()


with gr.Blocks(css="footer{display:none !important}",theme='gstaff/sketch',title="CodeEngine IBM") as demo:
    gr.Markdown(
        """
        <link rel="icon" type="image/png" href="/favicon/favico.ico" />
        # Multi Model (Image-Text-to-Text) on Code Engine 
        A Open Source Multi Vision Model for Image based tasks
        """
    )
    with gr.Row():
        prompt = gr.Textbox(label="Input", value="Describe this image.", scale=2)
        submit = gr.Button("Submit")
    with gr.Row():
        img = gr.Image(type="pil", label="Upload an Image")
        output = gr.TextArea(label="Response")
    submit.click(answer_question, [img, prompt], output)
    prompt.submit(answer_question, [img, prompt], output)
    with gr.Row():
        gr.HTML(
            """
            <div></br></br></div>
            <div>
            <p class="text-xs italic max-w-lg">
            <b>Note:</b>When first run, the app will download and cache the model, which could 
            take a few minutes. This is because of CPU used currently in Code engine generation will take a
            few minutes to start😔.
            </p>
            </div>
            <div></br></br></div>
            <div class="container text-gray-100 px-6 py-12 mx-auto">
            <div class="fade-in-section">
            <h1 class="text-2xl font-semibold text-gray-100 lg:text-3xl dark:text-white">Frequently asked questions.</h1>
            </div>
            <div class="grid grid-cols-1 gap-8 mt-8 lg:mt-16 md:grid-cols-2 xl:grid-cols-3">
            <div class="fade-in-section">
            <h1 class="text-xl font-semibold text-gray-250">What is moondream?</h1>
            <p class="mt-2 text-sm text-gray-400">moondream is a computer-vision model can answer real-world questions about images. It's tiny by today's models, with only 1.6B parameters. That enables it to run on a variety of devices, including mobile phones and edge devices.</p>
            </div>
            <div class="fade-in-section">
            <h1 class="text-xl font-semibold text-gray-100">What's the license?</h1>
            <p class="mt-2 text-sm text-gray-400">Apache 2.0. You can use moondream for commercial purposes.</p>
            </div>
            <div class="fade-in-section">
            <h1 class="text-xl font-semibold text-gray-100">How can I contact you?</h1>
            <p class="mt-2 text-sm text-gray-400">You can file issues at our <a href="https://github.ibm.com/Owais-Ahmad/multi-model-image-text-to-text-code-engine">github repository</a>. For other inquiries, you can reach out to us at <a href="mailto:owais.ahmad@ibm.com">owais.ahmad@ibm.com</a>.</p>
            </div>
            <div class="fade-in-section">
            <h1 class="text-xl font-semibold text-gray-100">What's it good at?</h1>
            <p class="mt-2 text-sm text-gray-400">moondream is great at answering questions about images. Since it's tiny, it can run everywhere, even on mobile devices or Raspberry Pi's, for example. It's quick and can process images quickly.</p>
            </div>
            <div class="fade-in-section">
            <h1 class="text-xl font-semibold text-gray-100">Are there limitations?</h1>
            <p class="mt-2 text-sm text-gray-400">It's purposefully built to answer questions about images, and does not do well with theoretical or abstract questions (e.g., "why would a cat do that?"). Because images are sampled down to 378x378, it may not be able to answer questions about very small details in the image. This also limits its ability to perform OCR. It's also not great at counting items beyond 2 or 3.</p>
            </div>
            </div>
            </div>"""
        )

demo.queue().launch(debug=True,auth=(username, password), server_name="0.0.0.0", server_port=8000,favicon_path="favicon/favico.ico",share=False)
Footer