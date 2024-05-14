import os
from dotenv import load_dotenv
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams


class WatsonXCE(Model):
    '''
    WatsonX Client Engineering class derived from the 'Model' base class.
    Supports all parent methods.
    '''
    def __init__(self, param_api_key, \
                    param_ibm_cloud_url, \
                    param_project_id, \
                    wml_credentials,\
                    model_name="meta-llama/llama-2-70b-chat", \
                    decoding_method="greedy", \
                    max_new_tokens=100, \
                    min_new_tokens=30, \
                    temperature=1.0, \
                    repetition_penalty=1.0,
                    top_k=76, \
                    top_p = 0.75, \
                    random_seed=42, \
                    stop_seq = [],\
                    ):
        '''
        WatsonX Client Engineering class constructor.
        Supports additional methods on top of parent class.
        '''
        self.api_key = param_api_key
        self.ibm_cloud_url = param_ibm_cloud_url
        self.project_id = param_project_id
        self.credentials = wml_credentials
        if self.api_key is None or self.ibm_cloud_url is None or self.project_id is None:
            raise Exception("Ensure the credentials are correct !")
        else:
            self.creds = {
                "url": self.ibm_cloud_url,
                "apikey": self.api_key 
            }
            
        
        self.model_params = {
            GenParams.DECODING_METHOD: decoding_method,
            GenParams.MIN_NEW_TOKENS: min_new_tokens,
            GenParams.MAX_NEW_TOKENS: max_new_tokens,
            GenParams.RANDOM_SEED: random_seed,
            GenParams.TEMPERATURE: temperature,
            GenParams.REPETITION_PENALTY: repetition_penalty,
            GenParams.TOP_K: top_k,
            GenParams.TOP_P: top_p,
            GenParams.STOP_SEQUENCES:stop_seq
        }

                
        super().__init__(
                model_id=model_name,
                credentials=self.credentials,
                params=self.model_params,
                project_id=self.project_id,
                space_id=None,
                verify=False
                )



    def wx_get_credentials(self):
        print ("API Key : ", self.api_key)
        print ("Project ID : ", self.project_id)

    def wx_send_to_watsonxai(self, prompts, 
                    decoding_method="greedy", \
                    max_new_tokens=100, \
                    min_new_tokens=30, \
                    temperature=1.0, \
                    repetition_penalty=1.0):
            '''
            helper function for sending prompts and params to Watsonx.ai
            
            Args:  
                prompts:list list of text prompts
                decoding:str Watsonx.ai parameter "sample" or "greedy"
                max_new_tok:int Watsonx.ai parameter for max new tokens/response returned
                temperature:float Watsonx.ai parameter for temperature (range 0>2)
                repetition_penalty:float Watsonx.ai parameter for repetition penalty (range 1.0 to 2.0)

            Returns: None
                prints response
            '''

            assert not any(map(lambda prompt: len(prompt) < 1, prompts)), "make sure none of the prompts in the inputs prompts are empty"

            self.model_params = {
                GenParams.DECODING_METHOD: decoding_method,
                GenParams.MIN_NEW_TOKENS: min_new_tokens,
                GenParams.MAX_NEW_TOKENS: max_new_tokens,
                GenParams.RANDOM_SEED: 42,
                GenParams.TEMPERATURE: temperature,
                GenParams.REPETITION_PENALTY: repetition_penalty,
            }

            #Update decoding parameters
            self.params=self.model_params
            return self.generate_text(prompts[0])
