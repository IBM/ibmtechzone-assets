import os
from dotenv import load_dotenv
from typing import Any, List, Mapping, Optional, Union, Dict
from pydantic import BaseModel, Extra

from langchain.llms.base import LLM
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SimpleSequentialChain

from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from ibm_watson_machine_learning.foundation_models.utils.enums import DecodingMethods
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams

# Loading Enviromental Variables
WML_API_KEY = os.getenv("WML_API_KEY")
WML_URL = os.getenv("WML_URL")
WML_PROJECT_ID = os.getenv("WML_PROJECT_ID")

creds = {"url": WML_URL,
         "apikey": WML_API_KEY}

# Setting Parameters
parameters = {GenParams.DECODING_METHOD: DecodingMethods.SAMPLE.value,
    GenParams.MAX_NEW_TOKENS: 100,
    GenParams.MIN_NEW_TOKENS: 1,
    GenParams.TEMPERATURE: 0.5,
    GenParams.TOP_K: 50,
    GenParams.TOP_P: 1}
    
# Wrap the WatsonX Model in a langchain.llms.base.LLM subclass to allow LangChain to interact with the model
class LangChainInterface(LLM, BaseModel):
    credentials: Optional[Dict] = None
    model: Optional[str] = None
    params: Optional[Dict] = None
    project_id : Optional[str]=None

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        _params = self.params or {}
        return {
            **{"model": self.model},
            **{"params": _params},
        }
    
    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "IBM WATSONX"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Call the WatsonX model"""
        params = self.params or {}
        model = Model(model_id=self.model, params=params, credentials=self.credentials, project_id=self.project_id)
        text = model.generate_text(prompt)
        if stop is not None:
            text = enforce_stop_tokens(text, stop)
        return text
# Initialize and configure an interface to a specific large language model (LLM) within the LangChain framework    
granite_llm = LangChainInterface(model='ibm/granite-13b-chat-v2', 
                                 credentials=creds, 
                                 params=parameters, 
                                 project_id=WML_PROJECT_ID)

googleflan_llm = LangChainInterface(model='google/flan-ul2', 
                                    credentials=creds, 
                                    params=parameters, 
                                    project_id=WML_PROJECT_ID)
                                    
prompt_1 = PromptTemplate(input_variables=["topic"], 
                          template="Generate a random question about {topic}: Question: ")


prompt_2 = PromptTemplate(input_variables=["question"],
                          template="Answer the following question: {question}",)

# LangChain determines a model's output based on its response. In our examples, the first model creates a response to the end prompt of "Question:" which LangChain maps as an input variable called "question" which it passes to the 2nd model.                          

prompt_to_granite = LLMChain(llm=granite_llm, 
                             prompt=prompt_1, 
                             output_key='question')

prompt_to_googleflan = LLMChain(llm=googleflan_llm, 
                                prompt=prompt_2, 
                                output_key='answer')
                                
q_a = SimpleSequentialChain(chains=[prompt_to_granite, 
                                    prompt_to_googleflan], 
                            verbose=True)
                            
q_a.run("life")