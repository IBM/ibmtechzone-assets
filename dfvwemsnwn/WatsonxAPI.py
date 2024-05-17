from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import DecodingMethods
from ibm_watson_machine_learning.foundation_models import Model

class WatsonxAPI:
    def __init__(self, config: dict):
        self.model_id = config["genAI_config"]["model_id"]
        self.api_key = config["genAI_config"]["api_key"]
        self.url = config["genAI_config"]["url"]
        self.project_id = config["genAI_config"]["project_id"]
        self.max_tokens = config["genAI_config"]["max_tokens"]
        self.stop_sequences = config["genAI_config"]["stop_sequences"]
        self.repetition_penalty = config["genAI_config"]["repetition_penalty"]
        self.temperature = config["genAI_config"]["temperature"]
        self.random_seed = 42
        self.decoding_method = config["genAI_config"]["decoding_method"]
        self.min_tokens = config["genAI_config"]["min_tokens"]

    def _generate_text(self, prompt,model_id = "meta-llama/llama-2-70b-chat") -> str:
        credentials = {
            "url": self.url,
            "apikey": self.api_key
        }
        model_id =model_id
        if self.model_id:
            model_id = self.model_id
        parameters = {
            GenParams.MIN_NEW_TOKENS: self.min_tokens,
            GenParams.MAX_NEW_TOKENS: self.max_tokens,
            GenParams.DECODING_METHOD: self.decoding_method,
            GenParams.REPETITION_PENALTY: self.repetition_penalty,
            GenParams.TEMPERATURE: self.temperature,
            GenParams.STOP_SEQUENCES: self.stop_sequences,
            GenParams.RANDOM_SEED: self.random_seed
        }
        #print("model paramters: ",parameters)
        llm = Model(model_id=model_id, params=parameters, credentials=credentials, project_id=self.project_id)
 
        return llm.generate_text(prompt=prompt)
    # guardrails=False