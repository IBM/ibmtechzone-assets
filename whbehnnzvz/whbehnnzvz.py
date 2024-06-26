import os
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from sentence_transformers import SentenceTransformer
from typing import Optional, Any, Iterable, List
from llama_index.llms.watsonx import WatsonX
from llama_index.core.query_engine.router_query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector
from llama_index.core.response.notebook_utils import display_source_node
from dotenv import load_dotenv
from llama_index.core import (
    VectorStoreIndex,
    SummaryIndex,
    SimpleKeywordTableIndex,
    SimpleDirectoryReader,
    ServiceContext,
    Settings
)
from llama_index.core.tools import QueryEngineTool
from llama_index.core.base.embeddings.base import BaseEmbedding
from typing import List
from pydantic import BaseModel, Field, PrivateAttr
import chromadb
from chromadb.utils import embedding_functions
from ibm_watsonx_ai.foundation_models import Embeddings
from ibm_watsonx_ai.metanames import EmbedTextParamsMetaNames as EmbedParams
from ibm_watsonx_ai.foundation_models.utils.enums import EmbeddingTypes
from llama_index.core import StorageContext
from llama_index.core.node_parser import SentenceSplitter
from IPython.display import Markdown, display
import chromadb


#config Watsonx.ai environment
load_dotenv()
api_key = os.getenv("api_key", None)
ibm_cloud_url = os.getenv("ibm_cloud_url", None)
project_id = os.getenv("project_id", None)
if api_key is None or ibm_cloud_url is None or project_id is None:
    print("Ensure you copied the .env file that you created earlier into the same directory as this notebook")
else:
    creds = {
        "url": ibm_cloud_url,
        "apikey": api_key 
    }

def watsonx_model(model_id = "meta-llama/llama-3-70b-instruct"):
    model = WatsonX(
    model_id = model_id,
    credentials=creds, 
    project_id=project_id)
    return model

# Set up your WatsonX embedding model
embed_params = {
    EmbedParams.TRUNCATE_INPUT_TOKENS: 512,
    EmbedParams.RETURN_OPTIONS: {
        'input_text': True
    }
}

embed_model = input("What is your model's name:")

embedding = Embeddings(
    model_id=embed_model,
    credentials=creds,
    params=embed_params,
    project_id=project_id
)

class WatsonXEmbedding(BaseEmbedding):
    _model: Embeddings = PrivateAttr()

    def __init__(
        self,
        model_id: str = 'baai/bge-large-en-v1',
        credentials: dict = {"api_key": "default_api_key"},
        params: dict = {"your_params_key": "your_params_value"},
        project_id: str = "your_project_id",
        **kwargs: Any,
    ) -> None:
        self._model = Embeddings(
            model_id=model_id,
            credentials=credentials,
            params=params,
            project_id=project_id
        )
        super().__init__(**kwargs)

    def _get_query_embedding(self, query: str) -> List[float]:
        embeddings = self._model.embed_query(query)
        return embeddings  # Assuming the response is always a list of list of floats

    def _get_text_embedding(self, text: str) -> List[float]:
        embeddings = self._model.embed_documents([text])
        return embeddings[0]  # Assuming the response is always a list of list of floats

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = self._model.embed_documents([text for text in texts])
        return embeddings  # Assuming the response is always a list of list of floats

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embedding(text)

# Initialize the WatsonX embedding wrapper
watsonx_embedding = WatsonXEmbedding(
    instructor_model_name='baai/bge-large-en-v1',
    credentials=creds,
    project_id=project_id,
    params=embed_params
)

# load documents
path = input("Enter the path of the document: ")
documents = SimpleDirectoryReader(input_files=[path]).load_data()

splitter = SentenceSplitter(chunk_size=512)
nodes = splitter.get_nodes_from_documents(documents)

vector_index = VectorStoreIndex(nodes=nodes, embed_model=watsonx_embedding)
summary_index =  SummaryIndex(nodes=nodes, embed_model=watsonx_embedding)

#Initializing the model
Settings.llm = model

vector_query_engine = vector_index.as_query_engine()
summary_query_engine = summary_index.as_query_engine(
    response_model="tree_summary",
    use_async=True,
)
vecto_tool = QueryEngineTool.from_defaults(
    query_engine=vector_query_engine,
    description=(
        "Description of Annual Report"
    )
)

summary_tool = QueryEngineTool.from_defaults(
    query_engine=summary_query_engine,
    description=(
        "Useful for summarizing annual report."
    )
)

query_egine = RouterQueryEngine(
    selector=LLMSingleSelector.from_defaults(),
    query_engine_tools=[vecto_tool, summary_tool],
    verbose=True,
)

# response = query_egine.query("What is the annual report all about?")
# print(str(response))