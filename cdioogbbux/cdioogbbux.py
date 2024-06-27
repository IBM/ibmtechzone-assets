import pandas as pd
import os
from dotenv import load_dotenv
from llama_index.query_pipeline import QueryPipeline as QP, Link, InputComponent
from llama_index.query_engine.pandas import PandasInstructionParser
from llama_index.llms import OpenAI
from llama_index.prompts import PromptTemplate
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import DecodingMethods
from langchain_ibm import WatsonxLLM
from langchain.llms.base import LLM
from pydantic import BaseModel, Extra
from typing import Any, List, Mapping, Optional, Dict

# Load environment variables
load_dotenv()

# Load the dataframe from the environment variable
dataset_path = os.getenv("DATASET_PATH")
df = pd.read_csv(dataset_path)

# Set up API credentials
api_key = os.getenv("API_KEY")
project_id = os.getenv("PROJECT_ID")
cloud_url = os.getenv("CLOUD_URL")
credentials = {"url": cloud_url, "apikey": api_key}

class WatsonxLLM(LLM, BaseModel):
    credentials: Optional[Dict] = None
    model: Optional[str] = None
    params: Optional[Dict] = None
    project_id: Optional[str] = None
    callback_manager: Optional[Any] = None

    class Config:
        extra = Extra.forbid

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        _params = self.params or {}
        return {
            **{"model": self.model},
            **{"params": _params},
        }

    @property
    def _llm_type(self) -> str:
        return "IBM WATSONX"

    def set_callback_manager(self, callback_manager: Any) -> None:
        self.callback_manager = callback_manager

    @property
    def free_req_input_keys(self) -> List[str]:
        return ["prompt"]

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        params = self.params or {}
        model = Model(model_id=self.model, params=params, credentials=self.credentials, project_id=self.project_id)
        text = model.generate_text(prompt)
        if stop is not None:
            text = enforce_stop_tokens(text, stop)
        return text

    def run_component(self, **kwargs) -> Any:
        prompt = kwargs.get("prompt", "")
        result = self._call(prompt)
        print(f"WatsonxLLM run_component output: {result}")
        return {"text": result}

params_summary = {
    GenParams.DECODING_METHOD: "",  # add decoding method
    GenParams.TEMPERATURE: 0.7,
    GenParams.MIN_NEW_TOKENS: 1,
    GenParams.MAX_NEW_TOKENS: 400,
    GenParams.REPETITION_PENALTY: 1,
    GenParams.STOP_SEQUENCES: ["\n\n"]
}

instruction_str = (
    "1. Convert the query to executable Python code using Pandas.\n"
    "2. The final line of code should be a Python expression that can be called with the `eval()` function.\n"
    "3. The code should represent a solution to the query.\n"
    "4. PRINT ONLY THE EXPRESSION.\n"
    "5. Do not include any explanations or extra text.\n"
)

pandas_prompt_str = (
    "You are working with a pandas dataframe in Python.\n"
    "The name of the dataframe is `df`.\n"
    "This is the result of `print(df.head())`:\n"
    "{df_str}\n\n"
    "Follow these instructions:\n"
    "{instruction_str}\n"
    "Query: {query_str}\n\n"
    "Expression:"
)
response_synthesis_prompt_str = (
    "Given an input question, synthesize a response from the query results.\n"
    "Query: {query_str}\n\n"
    "Pandas Instructions (optional):\n{pandas_instructions}\n\n"
    "Pandas Output: {pandas_output}\n\n"
    "Response: "
)

pandas_prompt = PromptTemplate(pandas_prompt_str).partial_format(
    instruction_str=instruction_str, df_str=df.head(5)
)
pandas_output_parser = PandasInstructionParser(df)
response_synthesis_prompt = PromptTemplate(response_synthesis_prompt_str)

llm = WatsonxLLM(
    model="greedy",  # give your model name 
    params=params_summary,
    credentials=credentials,
    project_id=project_id
)

qp = QP(
    modules={
        "input": InputComponent(),
        "pandas_prompt": pandas_prompt,
        "llm1": llm,
        "pandas_output_parser": pandas_output_parser,
        "response_synthesis_prompt": response_synthesis_prompt,
        "llm2": llm,
    },
    verbose=True,
)

qp.add_chain(["input", "pandas_prompt", "llm1", "pandas_output_parser"])
qp.add_links(
    [
        Link("input", "response_synthesis_prompt", dest_key="query_str"),
        Link("llm1", "response_synthesis_prompt", dest_key="pandas_instructions"),
        Link("pandas_output_parser", "response_synthesis_prompt", dest_key="pandas_output"),
    ]
)
qp.add_link("response_synthesis_prompt", "llm2")

response = qp.run(
    query_str="what is the correlation between survival and age?",
)
print(response)
