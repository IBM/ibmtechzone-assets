import streamlit as st
from uuid import uuid4
from llm import Backend
from utils import llm_tasks
@st.cache_resource
def get_agent():
    return Backend(model_id="meta-llama/llama-3-70b-instruct")
agent:Backend = get_agent()
st.title("🤖 Meta Prompt Generator ")
st.info("💡 The motivation behind this approach is that the model will generate instructions to perform the task guided by its own intrinsic comprehension.")
task = st.text_input("Describe the task for which you want to create a prompt")

if st.button("Generate Prompt"):
    prompt = agent.build_prompt(task=task)
    generated_prompt = agent.send_to_genai(prompts=prompt)
    st.text(generated_prompt)
st.text("Examples")
st.json(llm_tasks)