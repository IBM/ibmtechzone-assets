from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler
from llama_index.core import Settings
from langchain_ibm import WatsonxLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.callbacks import CBEventType, EventPayload

def get_generated_text(query):
    # define the LLM model  here
    llm = WatsonxLLM(
    model_id="google/flan-ul2",
    url="https://us-south.ml.cloud.ibm.com",
    apikey=os.environ["apikey"],
    project_id=os.environ["project_id"],
    )

    Settings.llm = llm

    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )
    data = SimpleDirectoryReader(input_dir='').load_data()
    vector_query_engine = VectorStoreIndex.from_documents(
            data,
            use_async=True,
        ).as_query_engine()

        # setup base query engine as tool
    query_engine_tools = [
        QueryEngineTool(
            query_engine=vector_query_engine,
            metadata=ToolMetadata(
                name="Data Analyser",
                description="Data Analyser - Analyse data from different data sources to compile the results from the financial query",
            ),
        ),
    ]
    query_engine = SubQuestionQueryEngine.from_defaults(
            query_engine_tools=query_engine_tools,
            use_async=True,
        )
    response = query_engine.query(query)
    return response.response

query = os.environ['query']
response = get_generated_text(query)

sub_answers=[]
sub_questions=[]
for i, (start_event, end_event) in enumerate(
    llama_debug.get_event_pairs(CBEventType.SUB_QUESTION)
):
    qa_pair = end_event.payload[EventPayload.SUB_QUESTION]
    print("Sub Question " + str(i) + ": " + qa_pair.sub_q.sub_question.strip())
    print("Answer: " + qa_pair.answer.strip())
    print("====================================")
    sub_answers.append(qa_pair.answer.strip())
    sub_questions.append(qa_pair.question.strip())