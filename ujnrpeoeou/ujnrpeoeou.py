import gradio as gr
from PIL import Image

output_demo_image_path = 'output.png'
output_demo_image = Image.open(output_demo_image_path)

key_image_path = 'key.png'
key_image = Image.open(key_image_path)

def analyze_image(input_image):
    report_text = "Date range: Jan 2021 - Dec 2021\n" \
                  "Crop wise information: Wheat (40%), Corn (20%), Other (40%)\n" \
                  "Comparison with historic data: Slight increase in crop diversity compared to previous year."
    return output_demo_image, report_text

with gr.Blocks() as iface:
    gr.Markdown("# Anonymous Analysis")
    gr.Markdown("Upload a TIFF image to analyze geo-spatial data and get a detailed report.")
    btn = gr.Button("Analyze Image")
    with gr.Row():
        input_image = gr.Image(type="pil", label="Input Image")
        output_image = gr.Image(type="pil", label="Vegetation Output")
        report_textbox = gr.Textbox(label="Report")

    btn.click(analyze_image, inputs=input_image, outputs=[output_image, report_textbox])
    gr.Markdown("## Key")
    gr.Image(value=key_image, type="pil", label="Symbols Key")

iface.launch()
