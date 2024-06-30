# Building RAG with LlamaIndex + DSPy
# This notebook demonstrates how to Build and Optimize Query Pipelines with DSPy predictors.
# It shows how to write DSPy code to define signatures for LLM inputs/outputs. And then port over these components to overall workflows within LlamaIndex Query pipelines, and then end-to-end optimize the entire system.


# References:
# 1. https://medium.com/@gautam75/revolutionizing-prompt-engineering-with-dspy-c125a4b920f9
# 2. https://dspy-docs.vercel.app/docs/intro
# 3. https://github.com/dmatrix/genai-cookbook/tree/main/dspy


# Import Required Libraries
import os
import subprocess
from llama_index.core import Settings
from llama_index.llms.ibm import WatsonxLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.query_pipeline import QueryPipeline as QP, InputComponent, FnComponent
import dspy
from dspy import Example
from dspy.teleprompt import BootstrapFewShot
from llama_index.core.evaluation import SemanticSimilarityEvaluator
from dspy.predict.llamaindex import DSPyComponent, LlamaIndexModule
import nest_asyncio
nest_asyncio.apply()


# Setup the credentials
WATSONX_API_KEY = os.environ["watsonx_api_key"]
IBM_CLOUD_URL = os.environ["ibm_cloud_url"]
PROJECT_ID = os.environ["project_id"]
CREDENTIALS = {
    "url": IBM_CLOUD_URL,
    "apikey": WATSONX_API_KEY
}


# Wrapper around Watsonx AI's API
# The constructor initializes the base class LM to support prompting requests to Watsonx models.Constructor to initialize the base class LM to support prompting requests to Watsonx models.
wx_model = dspy.Watsonx(model = "meta-llama/llama-3-70b-instruct", credentials = CREDENTIALS, project_id = PROJECT_ID)
dspy.settings.configure(lm=wx_model)


# Sample example of DSPy Class based Signature
print("Sample example of DSPy Class based Signature")
class BasicQA(dspy.Signature):
    """Answer questions with short factoid answers"""
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words",
                            prefix="Question's Answer:")

generate_response = dspy.Predict(BasicQA)
question = "What year did World War II end?"
print(f"Question: {question}")
pred = generate_response(question = question)
print(f"Answer: {pred.answer}\n\n")


# Setup Signature for RAG
# Define the LLM setting for DSPy (note: this is separate from using the LlamaIndex LLMs), and also the answer signature.
class GenerateAnswer(dspy.Signature):
    """Answer questions with short factoid answers."""

    context_str = dspy.InputField(desc="contains relevant facts")
    query_str = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")


# Embedding Model
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.llm = None
Settings.embed_model = embed_model


# Download the sample data
print("Downloading the sample data")
url = "https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt"
output_file = "paul_graham_essay.txt"
try:
    subprocess.run(["wget", url, "-O", output_file], check=True)
    print(f"File downloaded successfully as {output_file}")
except subprocess.CalledProcessError as e:
    print(f"Error downloading file: {e}")


# Load Data and Build Index
print("Loading data and building Index")
reader = SimpleDirectoryReader(input_files=[os.path.abspath("paul_graham_essay.txt")])
docs = reader.load_data()
index = VectorStoreIndex.from_documents(docs)
retriever = index.as_retriever(similarity_top_k=2)


# Build and Optimize a Query Pipeline with DSPy Modules
# We will use DSPy query components to plugin DSPy prompts/LLMs, stitched together with the query pipeline abstraction.
# Any query pipeline can be plugged into the LlamaIndexModule. We can then let DSPy optimize the entire thing end-to-end.
# Replace the synthesis piece with the DSPy component (make sure GenerateAnswer matches signature of inputs/outputs).
print("Building a Query Pipeline with DSPy Modules")
dspy_component = DSPyComponent(
    dspy.ChainOfThought(GenerateAnswer)
)

retriever_post = FnComponent(
    lambda contexts: "\n\n".join([n.get_content() for n in contexts])
)

p = QP(verbose=True)
p.add_modules(
    {
        "input": InputComponent(),
        "retriever": retriever,
        "retriever_post": retriever_post,
        "synthesizer": dspy_component,
    }
)
p.add_link("input", "retriever")
p.add_link("retriever", "retriever_post")
p.add_link("input", "synthesizer", dest_key="query_str")
p.add_link("retriever_post", "synthesizer", dest_key="context_str")

dspy_qp = LlamaIndexModule(p)

question = "What did the author do in Y Combinator"
print(f"Question: {question}")
output = dspy_qp(query_str=question)
print(f"Answer: {output.answer}")