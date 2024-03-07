from dotenv import load_dotenv
import os
import re

from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI


from genai import Credentials, Client
from genai.schema import TextGenerationParameters, TextGenerationReturnOptions
from genai.extensions.langchain import LangChainInterface
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
#from genai.model import Credentials, Model

from langchain.chains.question_answering import load_qa_chain
load_dotenv()

chunk_size = 1000
chunk_overlap = 100
loader = PyPDFLoader("breast-biopsy-bcv1.pdf")
data = loader.load()

print("Fetched " + str(len(data)) + " documents")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
docs = text_splitter.split_documents(data)

print("Split into " + str(len(docs)) + " chunks")

from InstructorEmbedding import INSTRUCTOR
embeddings = HuggingFaceInstructEmbeddings(
        model_name = "hkunlp/instructor-large",
        model_kwargs = {"device": "cpu"}
    )
    
db = FAISS.from_documents(docs, embeddings)
os.environ["GENAI_KEY"] = "Cxx2bK4cKMSNSIAjChTez6Qd_H7i6SIaSusWsSttCU77"
os.environ["GENAI_API"] = "https://us-south.ml.cloud.ibm.com"

api_key = os.getenv("GENAI_KEY", None) 
api_url = os.getenv("GENAI_API", None)

query = "help me generate a summarised text to a patient for the biopsy report"
resultmed = db.similarity_search(query, k=2)
print(resultmed)

from langchain import PromptTemplate
from langchain.prompts.few_shot import FewShotPromptTemplate


# few Examples of input and output
examples = [
    {
        "docs": "\n\nDIAGNOSIS:\nBREAST, RIGHT 11:00, ULTRASOUND-GUIDED NEEDLE BIOPSY: INVASIVE\nLOBULAR CARCINOMA.\nNOTE: Dr. Kristen N. Vandewalker has reviewed this case and concurs. The results are\ngiven to Dr. Test on 3/24/16. ER, PR and HER-2/neu studies will be performed on the tissue and the\nresults will be reported separately.\nGROSS DESCRIPTION: PC:sas\nPlaced in formalin at 10:00 in a container labeled with the patient’s name and \"RT\" are four tan to yellow to bright pink\ncores of fibrofatty tissue. The cores measure from 1.9 to 0.95 cm in length with an average diameter of 0.2 cm. The\nspecimen is filtered and entirely submitted between sponges one cassette.\nMICROSCOPIC DESCRIPTION:\nANATOMIC PATHOLOGY\nREPORT\n\n\nPatient: TEST, PATIENT Age: 68 (01/01/47) Pathology #: DPS-16-01234\nAcct#: Sex: FEMALE Epic:\n\nDoctor: Date Obtained: 03/23/2016\nDate Received: 03/23/2016\nTest Doctor\n1234 Test st\n\n\nSections show an invasive lobular carcinoma in a fibroelastotic background with focal LCIS. If the cores are\nrepresentative of the tumor then it is grade I (estimated SBR score 5). The tumor measures at least 0.8 cm in greatest",
        "output": "The report is about a breast biopsy that was done on the right breast. It shows that the patient has an invasive lobular carcinoma. This means that the cancer cells have spread from the milk ducts into the surrounding tissues. The tumor measures at least 0.8 cm in greatest dimension."
    },
    {
        "docs": "Lung Biopsy Pathology Report\n\nDescription: Lung, wedge biopsy right lower lobe and resection right upper lobe. Lymph node, biopsy level 2 and 4 and biopsy level 7 subcarinal. PET scan demonstrated a mass in the right upper lobe and also a mass in the right lower lobe, which were also identified by CT scan.\n\nA 48-year-old smoker found to have a right upper lobe mass on chest x-ray and is being evaluated for chest pain. PET scan demonstrated a mass in the right upper lobe and also a mass in the right lower lobe, which were also identified by CT scan. The lower lobe mass was approximately 1 cm in diameter and the upper lobe mass was 4 cm to 5 cm in diameter. The patient was referred for surgical treatment.\n\nSPECIMEN:\nA. Lung, wedge biopsy right lower lobe\nB. Lung, resection right upper lobe\nC. Lymph node, biopsy level 2 and 4\nD. Lymph node, biopsy level 7 subcarinal\n\nFINAL DIAGNOSIS:\nA. Wedge biopsy of right lower lobe showing: Adenocarcinoma, Grade 2, Measuring 1 cm in diameter with invasion of the overlying pleura and with free resection margin.\n\nB. Right upper lobe lung resection showing: Adenocarcinoma, grade 2, measuring 4 cm in diameter with invasion of the overlying pleura and with free bronchial margin. Two (2) hilar lymph nodes with no metastatic tumor.\nC. Lymph node biopsy at level 2 and 4 showing seven (7) lymph nodes with anthracosis and no metastatic tumor.\nD. Lymph node biopsy, level 7 subcarinal showing (5) lymph nodes with anthracosis and no metastatic tumor.\n\nCOMMENT: The morphology of the tumor seen in both lobes is similar and we feel that the smaller tumor involving the right lower lobe is most likely secondary to transbronchial spread from the main tumor involving the right upper lobe. This suggestion is supported by the fact that no obvious vascular or lymphatic invasion is demonstrated and adjacent to the smaller tumor, there is isolated nests of tumor cells within the air spaces. Furthermore, immunoperoxidase stain for Ck-7, CK-20 and TTF are performed on both the right lower and right upper lobe nodule. The immunohistochemical results confirm the lung origin of both tumors and we feel that the tumor involving the right lower lobe is due to transbronchial spread from the larger tumor nodule involving the right upper lobe.",
        "output": "A 48-year-old smoker found to have a right upper lobe mass on chest x-ray and is being evaluated for chest pain. PET scan demonstrated a mass in the right upper lobe and also a mass in the right lower lobe, which were also identified by CT scan. The lower lobe mass was approximately 1 cm in diameter and the upper lobe mass was 4 cm to 5 cm in diameter. The patient was referred for surgical treatment."
    },
    {
        "docs": "IMPRESSION :\nHISTOPATHOLOGY TEST REPORT\nContainer 1 (appendix): Acute on chronic appendicitis (Fig 1) Container 2 (Fibroid): Leiomyoma with hyalinisation (Fig 2)\nGROSS\nReceived 2 containers\n1. Container : Received specimen of appendix with mesoappendix measuring 6.5cms in length. External surface is congested. Cut section : lumen noted & filled with fecolith. (1P)\n2. Container : Received 2 nodular whitish tissue fragments, largest measuring 3x2.5x2.5cms. Cut surface shows whitish whorled areas. (2P) (2-3)\nGROSSING DONE BY\nDr.Swapnika\nMICROSCOPY :\nContainer 1: Section studied from the appendix shows features of acute on chronic appendicitis with lymphoid follicular hyperplasia. Section is negative for granulomas or malignancy.\nContainer 2: Sections studied from the nodular mass show a tumor with features of leiomyoma with areas of hyalinisation. Sections are negative for granulomas or malignancy.",
        "output": "The biopsy shows an inflammation of the appendix and a leiomyoma with hyalinisation. It is negative for malignancy. There were two containers which have different diagnoses. This means that the appendix shows signs of inflammation and infection, while the nodular mass appears to be a benign leiomyoma with some changes in the tissue. There are no indications of serious concerns like cancer or granulomas in either container."
    }
]

# Define the prompt template
template = """Below are the examples of summary text of a patient’s biopsy report".

Input:
{examples}

Help me generate a summarised text to a patient for the below biopsy report::
{resultmed}


Output:

"""
# Create a PromptTemplate
prompt_template = PromptTemplate(
    input_variables=["examples", "resultmed"],
    template=template
)

# Generate the formatted prompt string
formatted_prompt = prompt_template.format( examples=examples, resultmed=resultmed
)

#print(formatted_prompt)
api_key = os.getenv("GENAI_KEY", None) 
api_url = os.getenv("GENAI_API", None)
creds = {
        "url": api_url,
        "apikey": api_key 
    }

print("\n------------- Example (Model Talk)-------------\n")
print(api_url)

# params = GenerateParams(decoding_method="greedy", max_new_tokens=200, min_new_tokens=1, repetition_penalty=1.0)

params = {
    GenParams.DECODING_METHOD: "greedy",
    GenParams.REPETITION_PENALTY: 1.0,
    GenParams.MIN_NEW_TOKENS: 1,
    GenParams.MAX_NEW_TOKENS: 200
}


langchain_model = Model(model_id="meta-llama/llama-2-13b-chat", params=params, credentials=creds, project_id="b6bc701d-7ea2-416e-a3cc-8486948a9505").to_langchain()
print(langchain_model(formatted_prompt))