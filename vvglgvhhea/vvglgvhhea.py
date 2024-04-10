from dotenv import load_dotenv
from ibm_watson_machine_learning.foundation_models import Model
import os


class GenerateTranslation:
    def __init__(self,model_id = "meta-llama/llama-2-70b-chat",en_2_fr_mdl_type = "google/flan-t5-xxl"
                 ,generation_params = {
                "decoding_method": "greedy",
                "max_new_tokens": 512,
                "stop_sequences": ["\n\n\n"],
                # "temperature": 0.1,
                # "top_k": 50,
                # "top_p": 1,
                "repetition_penalty": 1
                },en_2_fr_params = {
                "decoding_method": "greedy",
                "max_new_tokens": 512,
                "stop_sequences": ["English:", "\n\n"],
                "temperature": 0.75,
                # "top_k": 50,
                # "top_p": 1,
                "repetition_penalty": 1,
            }):
        

        # Load credentials
        load_dotenv()
        api_key = os.getenv("API_KEY", None)
        ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
        project_id = os.getenv("PROJECT_ID", None)
        creds = {
                "url": ibm_cloud_url,
                "apikey": api_key 
                }
        # Initialize model 
        self.model = Model(model_id, params=generation_params, credentials=creds,project_id=project_id)
        self.modelen2fr=Model(en_2_fr_mdl_type,params=en_2_fr_params,credentials=creds,project_id=project_id)
    # Create the Prompt
    def translate_eng_fr(self,eng):
        prompt=f'''<<SYS>>
[INST]
- You have to look into project description and convert the description from English to French. 
- Make sure your translations represent project description.
- Make sure the translations are around same length as the transcript text. 
- Do not output any extra text other than the translation.
[/INST]

Use the examples given below as reference to understand the project perspective and carry out the task of translating the English text to French.
- Example translations:
English: "Describe how VTOL aircraft can be used for delivery in remote areas and their autonomous navigation systems."
French: "Décrivez comment les aéronefs à décollage et atterrissage verticaux (ADAV) peuvent être utilisés pour la livraison dans des zones reculées et leurs systèmes de navigation autonomes."

English: "Explain the process and benefits of fermenting legume proteins for improved nutritional value."
French: "Expliquez le processus et les avantages de la fermentation des protéines de légumineuses pour améliorer leur valeur nutritionnelle."

English: "Discuss the development of decision-making dashboards for workforce well-being management."
French: "Discutez du développement de tableaux de bord de prise de décision pour la gestion du bien-être de la main-d'œuvre."

<</SYS>>
English: {eng}
'''
        return prompt
    
    def translate_fr_eng(self,fr):
        prompt=f'''<<SYS>>
[INST]
- You have to look into project description and convert the description from French to English
- Make sure your translations represent project description.
- Make sure the translations are around same length as the transcript text. 
- Do not output any extra text other than the translation.
[/INST]

Use the examples given below as reference to understand project perspective and carry out the task of translating the French text to English.
- Example translations:
French: "Décrivez comment les aéronefs à décollage et atterrissage verticaux (ADAV) peuvent être utilisés pour la livraison dans des zones reculées et leurs systèmes de navigation autonomes."
English: "Describe how VTOL aircraft can be used for delivery in remote areas and their autonomous navigation systems."

French: "Expliquez le processus et les avantages de la fermentation des protéines de légumineuses pour améliorer leur valeur nutritionnelle."
English: "Explain the process and benefits of fermenting legume proteins for improved nutritional value."

French: "Discutez du développement de tableaux de bord de prise de décision pour la gestion du bien-être de la main-d'œuvre."
English: "Discuss the development of decision-making dashboards for workforce well-being management."

<</SYS>>

French: {fr}
'''
        return prompt
    
    def generate_answer(self,lang,text):
        text=text.replace('\n','')
        if lang=='en':
            prompt = self.translate_eng_fr(text).strip()
            result=self.modelen2fr.generate(prompt)
        if lang=='fr':
            prompt = self.translate_fr_eng(text).strip()
            result = self.model.generate(prompt)

        print(prompt)
        result = result["results"][0]["generated_text"]
        return result.strip()
    
if __name__ == "__main__":
  # Initialize the translation generator
  translator = GenerateTranslation()

  # Example text to be translated from English to French
  english_text = "This is an example sentence to be translated from English to French."

  # Translate from English to French
  translation_en_fr = translator.generate_answer("en", english_text)
  print("Translation from English to French:", translation_en_fr)

  # Example text to be translated from French to English
  french_text = "Ceci est une phrase d'exemple à traduire du français vers l'anglais."

  # Translate from French to English
  translation_fr_en = translator.generate_answer("fr", french_text)
  print("Translation from French to English:", translation_fr_en)

    
    
