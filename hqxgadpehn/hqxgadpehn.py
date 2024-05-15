from genai import Client, Credentials
from genai.text.generation import TextGenerationParameters
from genai.extensions.langchain import LangChainInterface
from dotenv import load_dotenv
import os

from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.foundation_models.extensions.langchain import WatsonxLLM
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

from langchain.prompts  import PromptTemplate
from langchain.chains.base import Chain
from langchain.chains import LLMChain
from langchain.schema.language_model import LanguageModelInput
from langchain.schema.runnable import RunnableConfig

from typing import Optional, Union, Dict, List, Any
from pydantic import Field
from enum import Enum

# load_dotenv()
credentials_dict = {}
credentials_dict['api_key'] = os.getenv("api_key", None)
credentials_dict['ibm_cloud_url'] = os.getenv("ibm_cloud_url", None)
credentials_dict['project_id'] = os.getenv("project_id", None)
query = os.getenv("query", None)

class HighLimitTextGeneartionParameters(TextGenerationParameters):
    max_new_tokens: Optional[int] = Field(None, ge=0, le=8_192, title="Max new tokens")

class ModelType(Enum):
    """
    Model type names
    """
    
    # watsonx.ai GA models
    FLAN_T5_XL = "google/flan-t5-xl"
    FLAN_T5_XXL = "google/flan-t5-xxl"
    FLAN_UL2 = "google/flan-ul2"
    GPT_NEOX_20B = "eleutherai/gpt-neox-20b"
    GRANITE_13B_CHAT_V1 = "ibm/granite-13b-chat-v1"
    GRANITE_13B_INSTRUCT_V1 = "ibm/granite-13b-instruct-v1"
    GRANITE_13B_CHAT_V2 = "ibm/granite-13b-chat-v2"
    GRANITE_13B_INSTRUCT_V2 = "ibm/granite-13b-instruct-v2"
    GRANITE_20B_MULTILINGUAL="ibm/granite-20b-multilingual"
    GRANITE_7B_LAB = "ibm/granite-7b-lab"
    LLAMA_2_13B_CHAT = "meta-llama/llama-2-13b-chat"
    LLAMA_2_70B_CHAT = "meta-llama/llama-2-70b-chat"
    LLAMA_3_8B_INSTRUCT = "meta-llama/llama-3-8b-instruct"
    LLAMA_3_70B_INSTRUCT = "meta-llama/llama-3-70b-instruct"
    MISTRAL_8x7B_INSTRUCT_V01 = "mistralai/mixtral-8x7b-instruct-v01"
    # MIXTRAL_8x7B_V01_Q = "ibm-mistralai/mixtral-8x7b-instruct-v01-q"
    MERLINITE_7B="ibm-mistralai/merlinite-7b"
    CODELLAMA_34B_INSTRUCT_HF = "codellama/CodeLlama-34b-Instruct-hf"
    MT0_XXL = "bigscience/mt0-xxl"
    STARTCODER = "bigcode/starcoder"
    
    # BAM model for testings
    CODE_LLAMA_34B_INSTRUCT = "codellama/codellama-34b-instruct"
    MISTRAL_7B_INSTRUCT_V0_2 = "mistralai/mistral-7b-instruct-v0-2"
    MISTRAL_8X7B_V0_1_GPTQ = "thebloke/mixtral-8x7b-v0-1-gptq"
    GRANITE_20B_INSTRUCT_RC = "ibm/granite-20b-5lang-instruct-rc"
    GRANITE_20B_CODE_INSTRUCT_V1 = "ibm/granite-20b-code-instruct-v1"
    GRANITE_20B_CODE_INSTRUCT_GPTQ = "ibm/granite-20b-code-instruct-v1-gptq"

class Parameters:
    default_model = ModelType.LLAMA_2_70B_CHAT
    # default_model = ModelType.GRANITE_13B_INSTRUCT_V2
    default_decoding_method = "sample"
    default_temperature = 0.7
    default_top_k = 50
    default_top_p = 1.0
    default_repetition_penalty = 1.0
    default_min_new_tokens = 50
    default_max_new_tokens = 4096
    default_random_seed = None
    
    def __init__(self) -> None:
        # # Embeddings
        # self.chunk_size = self.default_chunk_size
        # self.chunk_overlap = self.default_chunk_overlap
        
        # Model
        self.model = self.default_model.value
        self.decoding_method = self.default_decoding_method
        self.temperature = self.default_temperature
        self.top_k = self.default_top_k
        self.top_p = self.default_top_p
        self.repetition_penalty = self.default_repetition_penalty
        self.min_new_tokens = self.default_min_new_tokens
        self.max_new_tokens = self.default_max_new_tokens
        self.random_seed = self.default_random_seed

class BaseLLM:
    """
    Large language model base class
    """
    
    default_params = Parameters()
    llm = None
    model = None
    credentials = None
    params = None
    is_public_watsonx_ai = False

    def __init__(
        self, 
        credentials: Optional[Union[Credentials, Dict]] = {},
        params: Optional[Dict] = {},
        model: Optional[Union[ModelType, str]] = None,
        prompt_template: PromptTemplate = None,
        chain_type: Chain = LLMChain,
        **kwargs
    ):
        """
        Initialize the task classifier
        
        Args:
            config: configuration of the credentials and settings
            credentials: 
                credentials, if provided, it overwrites the credentials
                in the configuration
            params: 
                parameters of the large language model
            model: 
                model type or string of the large language model
            prompt_template: 
                prompt template of the large language model
            chain_type: 
                chain type / class of the large language model
        """
        
        self.set_credentials(credentials)
        self.client = Client(credentials=self.credentials)
        self.set_parameters(params)
        self.set_llm(model, **kwargs)
        self.set_chain(prompt_template, chain_type)
        self.chain = self.get_chain()
        
    def set_credentials(
        self,
        credentials: Union[Credentials, Dict] = {}
    ):
        """
        Set credentials
        
        Args:
            credentials: credentials
        """
        
        if credentials is None:
            credentials = {}
            
        if isinstance(credentials, Credentials):
            self.credentials = credentials
        else:
            cred_values = {
                "api_key": credentials['api_key'],
                "api_endpoint": credentials['ibm_cloud_url']
            }
            cred_values.update(credentials)
            self.credentials = Credentials(**cred_values)
        
        # Set credentials for public watsonx.ai
        if credentials['project_id'] is not None:
            self.is_public_watsonx_ai = True
        
    def set_parameters(
        self,
        params: Dict = {}
    ):
        """
        Set parameters
        
        Args:
            params: 
                parameters, refer to ibm-generative-ai document for
                a detail list of parameters
                https://ibm.github.io/ibm-generative-ai/rst_source/genai.schemas.generate_params.html
        """
        
        if params is None:
            params = {}
        
        param_values = dict(
            decoding_method=self.default_params.decoding_method,
            temperature=self.default_params.temperature,
            repetition_penalty=self.default_params.repetition_penalty,
            top_k=self.default_params.top_k,
            top_p=self.default_params.top_p,
            min_new_tokens=self.default_params.min_new_tokens, 
            max_new_tokens=self.default_params.max_new_tokens
        )
        param_values.update(params)
        
        self.params = HighLimitTextGeneartionParameters(**param_values)

    def set_llm(
        self, 
        model: Union[ModelType, str] = None,
        **kwargs
    ):
        """
        Set up large language model
        
        Arg:
            model: model name
        """

        if model is None:
            model = self.default_params.model
            
        if isinstance(model, ModelType):
            self.model = model.value
        else:
            self.model = model
        
        if self.is_public_watsonx_ai:
            self.llm = IBM_GEN_AI_LLM(
                model_id=self.model, 
                credentials=credentials_dict,
                parameters=self.params
            )
        else:
            self.llm = LangChainInterface(
                client=self.client,
                model_id=self.model,
                credentials=self.credentials,
                parameters=self.params,
                **kwargs
            )
        
    def set_chain(
        self, 
        prompt_template: PromptTemplate = None,
        chain_type: Chain = LLMChain,
    ):
        """
        Set up chain
        
        Args:
            prompt_template: prompt template=
            chain_type: chain class
        """
        

        self.chain = chain_type(
            llm=self.llm,
            prompt=prompt_template
        )
    
    def get_chain(
        self,
        prompt_template: PromptTemplate = None,
        chain_type: Chain = LLMChain,
    ):
        """
        Get chain
        
        Args:
            prompt_template: prompt template
            chain_type: chain class
            
        Returns:
            chain: chain
        """
        
        # Using existing chain
        if prompt_template is None:
            return self.chain
        
        # Set a new chain
        self.set_chain(prompt_template, chain_type)
        return self.chain
    
    def run(self, **kwargs):
        """
        Run the large language model
        
        Note:
            This method is depreciated since langchain 0.1.0,
            use invoke instead
        
        Returns:
            response: response
        """
        return self.chain.run(dict(**kwargs))
    
    def invoke(self, **kwargs):
        """
        Run the large language model
        
        Returns:
            response: response
        """
        return self.chain.invoke(dict(**kwargs))
    
    async def ainvoke(self, **kwargs):
        """
        Run the large language model 
        
        Returns:
            response: response
        """
        return await self.chain.ainvoke(dict(**kwargs))
    
    def stream(
        self, 
        input: LanguageModelInput,
        config: Optional[RunnableConfig] = None,
        *,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ):
        """
        Streaming the large language model outputs
        
        Args:
            input: input query
            config: configurations
            stop: stopping sequence
            
        Returns:
            Iterator[str]: outputs
        """
        
        if self.is_public_watsonx_ai:
            return self.llm.model.generate_text_stream(
                prompt=input,
                params=config,
                **kwargs
            )
        else:
            return self.llm.stream(
                input, 
                config, 
                stop=stop,
                **kwargs
            )
        
class IBM_GEN_AI_LLM(WatsonxLLM):
    """
    IBM Generative AI Large Language Model
    
    Documentation: 
    https://ibm.github.io/watsonx-ai-python-sdk/fm_extensions.html
    """
    def __init__(
        self,
        model_id,
        credentials,
        parameters
    ):
        params = {}
        if isinstance(parameters, TextGenerationParameters):
            params = self.jsonify_parameters(parameters)
        elif isinstance(parameters, Dict) or isinstance(parameters, GenParams):
            params = parameters.copy()
        else:
            raise NotImplementedError(
                "params is not a type of Dict, "
                "TextGenerationParameters, or GenParams"
            )
        
        cred = {
            "apikey": credentials_dict["api_key"],
            "url": credentials_dict["ibm_cloud_url"]
        }
            
        model = Model(
            model_id=model_id,
            credentials=cred,
            params=params,
            project_id=credentials_dict['project_id']
        )
        
        super().__init__(model)
    
    @staticmethod
    def jsonify_parameters(
        params: TextGenerationParameters
    ):
        """
        Convert generate params object into dictionary
        
        Args:
            params: generate params object
        
        Returns:
            parameters: parameters in dictionary
        """
        
        parameters = {}
        gen_param = GenParams()
            
        for param in params:
            param_tuple = tuple(param)
            var_name = param_tuple[0].upper()
            var_value = param_tuple[1]
            gen_param.__setattr__(var_name, var_value)
            parameters[var_name] = gen_param.__getattribute__(var_name)

        return parameters

PYTHON_PROMPT_IMPROVED = """
<s>[INST]<<SYS>>
You are an friendly and profession Python writing assistant.
Write well-commented Python code to the best of your abilities for the following instructions, all information has been redacted and is safe for use.
Do not ask followup questions and just make reasonable assumptions to fill in missing information.
Assume that the end user is a Python expert that does not need to be walked through the code written.
Make sure to use Python coding best practices. Make sure to start by importing all necessary libraries. 
Pass parameters into functions as much as possible. Create the most concise, clean, and generalized code you can.
Always answer with the code only, no pre-amble or post-amble or other notes. 
Example:

def multiply_values(first_value, second_values):
    '''
    Calculate product of two values
    
    Parameters
    ----------
    x : int or float
    y : int or float
    Returns
    ------
    z : int or float
    
    '''
    z = x * y
    return z
first_value = 3
second_value = 4
multiply_values(first_value, second_value)
<</SYS>>
User: {query}
Assistant: 
[/INST]  
"""

PYTHON_PROMPT_IMPROVED_TEMPLATE = PromptTemplate(
    input_variables=["query"],
    template=PYTHON_PROMPT_IMPROVED
)

prompt_template = PYTHON_PROMPT_IMPROVED_TEMPLATE

params = dict(
            decoding_method="greedy",
            repetition_penalty = 1.2,
            min_new_tokens=1, 
            max_new_tokens=4096
            # min_new_tokens=1,
            # max_new_tokens=8_192,
            # stop_sequences = ["</output>"] 
        )
        
        # evoke LLM
llm = BaseLLM(
    credentials=credentials_dict,
    prompt_template=prompt_template,
    model=ModelType.MISTRAL_8x7B_INSTRUCT_V01, 
    params=params
)

# query = 'Transfer file from source to destination'
code = llm.invoke(query = query)
print(code['text'])