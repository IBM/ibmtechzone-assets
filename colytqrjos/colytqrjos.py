import streamlit as st

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import collections
import time
import json
import re 


from ibm_watsonx_ai.foundation_models import Model
from ibm_watson import DiscoveryV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from dotenv import load_dotenv
from pdf2image import convert_from_path
import warnings
warnings.filterwarnings("ignore")

import logging

logging.basicConfig(filename='my_app.log',
                    filemode='w',
                    format='%(asctime)s %(levelname)s %(message)s',
                    )

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) 
st.set_page_config(
    page_title="Invoice Extraction",
    page_icon="🚀",
)

load_dotenv()

final_output = []
json_filename = "document_ids.json"
invoices = []
extract_keys = ['Model_ID', 'File_Name', 'Invoice_Number', 'Due_Date', 'Purchase_Order_Number', 'Total_amount', 'Classification']
classified_invoices = []
classify_keys = ['File_Name', 'Classification']

ai_project_id = os.getenv('WATSONX_AI_PROJECT_ID')
bam_url = os.getenv('BAM_URL')
bam_api = os.getenv('BAM_API_KEY')


platform_type = os.getenv('PLATFORM_TYPE')




def get_credentials_ga():
    return {
        "url" : os.getenv("WATSONX_AI_URL"),
        "apikey" : os.getenv("WATSONX_CLOUD_API_KEY")
        
    }

parameters = {
    "decoding_method": "greedy",
    "max_new_tokens": 150,
    "repetition_penalty": 1,
    "temperature":0
}


def init_model(model_id):
    model = Model(
        model_id = model_id,
        params = parameters,
        credentials = get_credentials_ga(),
        project_id = ai_project_id,
        space_id = None
        )
    return model


def remove_patterns(text):
    logger.exception("post processing started")
    patterns = [r'\[\/?SYS\]', r'\[\/?INST\]']
    for pattern in patterns:
        text = re.sub(pattern, '', text)
    return text




def extract_invoice_number(text, filename, model_id):
    logger.info("Extraction of Invoice Number started")
    try:
        model = init_model(model_id)
        invoice_prompt = f"""<s>[INST]<<SYS>>
        You are an helpful Entity Extractor AI. There will be various entities in the invoice which is given to you.\
        Your task is to extract the "Invoice Number" which is found in a particular invoice file.\
        
        
        @@@
        Below is a list of further instructions that you need to follow:\
            -Do not display/ generate any greetings.\
            -If you are unable to find or extract any "Invoice Number", then the output should be `Data not available`. Do not pick up random information or make up on your own.\
            -Invoice number will never have any decimal, ".". If you find a decimal in any entity, it is not the invoice number.\
            -"Invoice Number" can sometimes start with Numbers or sometimes may include Alphabets. Invoice Number can also be present as "INVOICE NO.",  "INVOICE", "VOUCHER NUMBER, or "DOCUMENT NO.".\
            -If you find "multiple invoice numbers", give output as `Data not available`
            -Do not explain yourself, only give the FINAL output. Make sure to give only the output.\
            
            
        @@@
        Below are few example sets that will make you familiar with the process:
        
        Example 1-

        Input: ORDER NO. INVOICE NO. INVOICE DATE SOLD TO NO. SOLD TO NAME 1 129642570 82737272 01/01/2023 SOLD BY SOMEONE NAME...
        Assistant: 82737272

        Example 2-

        Input: INVOICE FOR MECHANICAL PARTS of motorvehicle. Invoice Number. Purchase Order Number. Due Date. Contract Number. 4FG6272 827662 03/01/2022 Deliver latest...
        Assistant: 4FG6272

        Example 3-

        Input: 
        INVOICE NUMBER: 45789320 DATE: 2024-06-15 TOTAL AMOUNT: $1,569.45 BILL TO: john doe 123 elm street springfield,\
        il 62704 SHIP TO: acme corporation 456 oak avenue chicago, il 60601 ITEMS: 1. Product Code: A123B - Widget Pro - $299.99 -\
        Quantity: 3 - Total: $899.97 2. Product Code: C456D - Gadget Plus - $149.75 - INVOICE NUMBER: 27827272 Quantity: 2 - Total: $299.50 3. Product Code:\
        E789F - Device Ultra - $185.99 - Quantity: 2 - Total: $371.98 SUBTOTAL: $1,571.45 DISCOUNT: $2.00 SHIPPING:\
        FREE GRAND TOTAL: $1,569.45 PAYMENT TERMS: NET 30 PAYMENT METHOD: INVOICE NUMBER: 27272721 CREDIT CARD PO NUMBER: 789-45612 TAX ID:\
        12-3456789 CONTACT INFO: CUSTOMER SERVICE: (800) 555-1234 EMAIL: support@example.com\
        
        Assistant: Data not available

        Example 4-

        Input: 
        DATE: 2024-06-15 TOTAL AMOUNT: $1,569.45 BILL TO: john doe 123 elm street springfield,\
        il 62704 SHIP TO: acme corporation 456 oak avenue chicago, il 60601 ITEMS: 1. Product Code: A123B - Widget Pro - $299.99 -\
        Quantity: 3 - Total: $899.97 2. Product Code: C456D - Gadget Plus - $149.75 - Quantity: 2 - Total: $299.50 3. Product Code:\
        E789F - Device Ultra - $185.99 - Quantity: 2 - Total: $371.98 SUBTOTAL: $1,571.45 DISCOUNT: $2.00 SHIPPING:\
        INVOICE NUMBER: 45789320 FREE GRAND TOTAL: $1,569.45 PAYMENT TERMS: NET 30 PAYMENT METHOD: CREDIT CARD PO NUMBER: 789-45612 TAX ID:\
        12-3456789 CONTACT INFO: CUSTOMER SERVICE: (800) 555-1234 EMAIL: support@example.com\
        
        Assistant: 45789320

        <</SYS>>
        User: {text}
        Assistant: 
        [/INST]
        """
        
        generated_invoice = model.generate_text(prompt=invoice_prompt, guardrails=False)
        final_output.append(model_id)
        final_output.append(filename)
        final_output.append(generated_invoice)
        extract_due_date(text, model)
    except Exception as e:
        logger.exception("Issue with Invoice number extraction")

        final_output(filename)
        final_output.append("Not able to Process")
        final_output.append("Not able to Process")
        return 



def extract_due_date(text, model):
    logger.info("Extrating Due Date")
    try:
        due_date_prompt = f"""<s>[INST]<<SYS>>
        You are an helpful Entity Extractor AI. There will be various entities in the invoice which is given to you.\
        Your task is to extract the "Due Date" which is found in a particular invoice file.\
        
        @@@
        Below is a list of further instructions that you need to follow:\
            -Do not display/ generate any greetings.\
            -If you are unable to find or extract any "Due Date", then the output should be `Data not available`. Do not pick up random information or make up on your own.\
            -Due date will be present directly or will be given indirectly, such as Net followed by a NUMBER. THIS IS JUST AN EXAMPLE - if the NUMBER is, say 80, it\
                means 80 days from the "Invoice Date"/ "Order Date". Calculate "Due date" accordingly.\
            -If you see the word "NET" in an invoice, get the number next to it and add it to the "Invoice Date"/ "Order Date". That will be the actual "DUE DATE".\
            -In some cases, BOTH the 'Due Date' and 'NET' will be present, in such cases, ignore the NET number and just fetch "due date" as it is.\
            -If the case were "Due Date" is present as "NET", do NOT explain yourself why you came to such a conclusion about the generated due date, just say the due date as it is.\
            -If "Due Date" or "NET" is explicitly not metioned, write as `Data not available`.\
            -If you find "multiple due dates", give output as `Data not available`
            -Do not explain yourself, only give the FINAL output. Make sure to give only the output.\
            
        @@@
        Below are few example sets that will make you familiar with the process:
        
        Example 1-

        Input: ORDER NO. INVOICE NO. INVOICE DATE SOLD TO NO. SOLD TO NAME 1 129642570 82737272 01/05/2024 SOLD BY SOMEONE NAME D ASTON. TERMS NET30 ADDRESS given as 1102 blv...
        Assistant: 01/06/2024

        Example 2-
        
        Input: INVOICE FOR MECHANICAL PARTS of motorvehicle. Invoice Number. Purchase Order Number. Invoice Date. Contract Number. 4FG6272 827662 03/01/2022 Deliver latest today. 31 May 2024 - 4 April 2024.INVOICE OF SERVICES..
        Assistant: 4 April 2024

        Example 3-

        Input: 
        INVOICE NUMBER: 45789320 DATE: 2024-06-15 TOTAL AMOUNT: $1,569.45 BILL TO: john doe 123 elm street springfield,\
        il 62704 SHIP TO: acme corporation 456 oak avenue chicago, il 60601 ITEMS: 1. Product Code: A123B - Widget Pro - $299.99 -\
        Quantity: 3 - Total: $899.97 2. Product Code: C456D - Gadget Plus - $149.75 - Quantity: 2 - Total: $299.50 3. Product Code:\
        E789F - Device Ultra - $185.99 - Quantity: 2 - Total: $371.98 SUBTOTAL: $1,571.45 DISCOUNT: $2.00 SHIPPING:\
        FREE GRAND TOTAL: $1,569.45 PAYMENT TERMS: NET 30 PAYMENT METHOD: CREDIT CARD PO NUMBER: 789-45612 TAX ID:\
        12-3456789 CONTACT INFO: CUSTOMER SERVICE: (800) 555-1234 EMAIL: support@example.com\
        
        Assistant: 2024-07-15

        <</SYS>>
        User: {text}
        Assistant: 
        [/INST]
        """

        generated_due_date = model.generate_text(prompt=due_date_prompt, guardrails=False)
        final_output.append(generated_due_date)
        extract_po_number(text, model)
    except Exception as e:
        logger.exception("issue with Due date")

        final_output.append("Not able to Process")
        return 



def extract_po_number(text, model):
    logger.info("Extracting PO Number")
    try:
        po_prompt = f"""<s>[INST]<<SYS>>
        You are an helpful Entity Extractor AI. There will be various entities in the invoice which is given to you.\
        Your task is to extract the "Purchase Order Number" which is found in a particular invoice file.\
        
        @@@
        Below is a list of further instructions that you need to follow:\
            -Do not display/ generate any greetings.\
            -If you are unable to find or extract any "Purchase-Order", then the output should be `Data not available`. DO NOT pick up random information or make up on your own.\
            -Purchase Order Number can be directly given or also present as "PO number" or "Order No." or "PO" pr "PO NO".\
            -"Sub Contract number" is NOT same as "Purchase Order" number!\
            -If the invoice has both "Order number" and "PO Number", consider the PO number and ignore the term "order number".\
            -If the invoice has multiple "Purchase order" or "PO" numbers, say `Data not available`. Do not give purchase order number in such cases.\
            -Do not explain yourself, only give the FINAL output. Make sure to give only the output.\
            
        @@@
        Below are few example sets that will make you familiar with the process:\

        Example 1-
        Input :
            INVOICE NUMBER: 45789320 DUE DATE: 2024-06-15 TOTAL AMOUNT: $1,569.45 BILL TO: john doe 123 elm street springfield,\
            il 62704 SHIP TO: acme corporation 456 oak avenue chicago, il 60601 ITEMS: 1. Product Code: A123B - Widget Pro - $299.99 -\
            Quantity: 3 - Total: $899.97 2, PO-NUMBER 928383, Product Code: C456D - Gadget Plus - $149.75 - Quantity: 2 - Total: $299.50 3. Product Code: \
            E789F - Device Ultra - $185.99 - Quantity: 2 - Total: $371.98 SUBTOTAL: $1,571.45 DISCOUNT: $2.00 SHIPPING: \
            FREE GRAND TOTAL: $1,569.45 PO 53633 PAYMENT TERMS: NET 30 PAYMENT METHOD: PO-NUMBER 738373 CREDIT CARD PO-NUMBER: 789-45612 TAX ID: \
            12-3456789 CONTACT INFO: CUSTOMER SERVICE: (800) 555-1234 EMAIL: support@example.com\

        Assistant: Data not available


        Example 2-
        Input :
            INVOICE NUMBER: 45789320 DUE DATE: 2024-06-15 TOTAL AMOUNT: $1,569.45 BILL TO: john doe 123 elm street springfield,\
            il 62704 SHIP TO: acme corporation 456 oak avenue chicago, il 60601 ITEMS: 1. Product Code: A123B - Widget Pro - $299.99 -\
            Quantity: 3 - Total: $899.97 2. Product Code: C456D - Gadget Plus - $149.75 - Quantity: 2 - Total: $299.50 3. Product Code:\
            E789F - Device Ultra - $185.99 - Quantity: 2 - Total: $371.98 SUBTOTAL: $1,571.45 DISCOUNT: $2.00 SHIPPING:\
            FREE GRAND TOTAL: $1,569.45 PAYMENT TERMS: NET 30 PAYMENT METHOD: CREDIT CARD PO NUMBER: 789-45612 TAX ID:\
            12-3456789 CONTACT INFO: CUSTOMER SERVICE: (800) 555-1234 EMAIL: support@example.com\

        Assistant: 789-45612


        <</SYS>>
        User: {text}
        Assistant: 
        [/INST]
        """
    


        generated_po = model.generate_text(prompt=po_prompt, guardrails=False)
        final_output.append(generated_po)
        extract_total(text, model)
    except Exception as e:
        logger.exception("Issue with Extracting PO Number")

        final_output.append("Not able to Process")
        return



def extract_total(text, model):
    logger.info("Extracting Total")
    try:
        total_prompt = f"""<s>[INST]<<SYS>>
        You are an helpful Entity Extractor AI. There will be various entities in the invoice which is given to you.\
        Your task is to extract the "Total Amount" which is found in a particular invoice file.\
        
        @@@
        Below is a list of further instructions that you need to follow:\
            -Do not display/ generate any greetings.\
            -If you are unable to find any "Total Amount", then the output should be `Data not available`. Do not pick up random information or make up on your own.\
            -"Total Amount" can be present as "Due Amount", "Charges", "Total Due", "Total USD" etc.\
            -In some cases, the "Total Amount" might be like this: ($ 8929.39), this indicates that the amount due is in negative.\
                If you find such a structure, add a negative sign before the amount like this: - $8929.39.\
            -Do not explain yourself, only give the FINAL output. Make sure to give only the output.\

        <</SYS>>
        User: {text}
        Assistant: 

        [/INST]
        """

        generated_total = model.generate_text(prompt=total_prompt, guardrails=False)
        final_output.append(generated_total)
        classify_doc(text,model)
    except Exception as e:
        logger.exception("Issue with extracting the total")
        final_output.append("Not able to Process")

        return

def classify_doc(text, model):
    logger.info("Classification Strted")
    try:
        classify_prompt = f"""<s>You are a helpful AI which helps in classification of document.\
        [INST]<<SYS>>
        - Do not greet the user. Do not provide any explanations for your output.
        - Classify the given documents correctly as `Invoice`, `Utility Bill`, `Credit Memo`, or a `Statement`.\
        - This classification should be based only on the context provided in its contents.\
        - Only output the classified text value. Do not output any other text or explanation.</SYS>

        <example>
        Input: INVOICE NUMBER: 45789320 DUE DATE: 2024-06-15 TOTAL AMOUNT: $1,569.45 BILL TO: john doe 123 elm street springfield,\
        il 62704 SHIP TO: acme corporation 456 oak avenue chicago, il 60601 ITEMS: 1. Product Code: A123B - Widget Pro - $299.99.\
        
        Output: INVOICE

        Input: STATEMENT DATE: 2024-05-26 CUSTOMER STATEMENT ACCOUNT NUMBER: 1234567890 BILL TO: John Doe ADDRESS: 123 Elm Street\
        Springfield, IL 62704 PREVIOUS BALANCE: $1,200.00 NEW CHARGES:  1. May 2024 Monthly Subscription Fee: $50.00 2. Additional Service Charge: $20.00\
        TOTAL NEW CHARGES: $70.00 PAYMENTS & CREDITS:  1. Payment Received - May 15, 2024: $500.00 2. Credit Adjustment: $50.00 TOTAL PAYMENTS & CREDITS: $550.00\
        
        Output: STATEMENT
        </example>

        Document: {text}
        Assitant:
        [/INST]
        """
        classifed = model.generate_text(prompt=classify_prompt, guardrails=False)
        final_output.append(classifed)
        return final_output[::-1]
    
    except Exception as e:
        logger.exception("Issue with classification")
        final_output.append("Not able to Process")
        return None


def classify_doc_onbuttonclick(model_id, filename):
    classify_data = {}
    classify_list = []

    classify_list.append(filename)
    logger.info("Classification Started")
    try:
        document_ids = retrive_data_to_classify(filename)
        text = get_result_from_discovery(filename, document_ids)
        model = init_model(model_id)
    

        classify_prompt = f"""<s>You are a helpful AI which helps in classification of document.\
        [INST]<<SYS>>
        - Do not greet the user. Do not provide any explanations for your output.
        - Classify the given documents correctly as `Invoice`, `Utility Bill`, `Credit Memo`, or a `Statement`.\
        - This classification should be based only on the context provided in its contents.\
        - Only output the classified text value. Do not output any other text or explanation.</SYS>

        <example>
        Input: INVOICE NUMBER: 45789320 DUE DATE: 2024-06-15 TOTAL AMOUNT: $1,569.45 BILL TO: john doe 123 elm street springfield,\
        il 62704 SHIP TO: acme corporation 456 oak avenue chicago, il 60601 ITEMS: 1. Product Code: A123B - Widget Pro - $299.99.\
        
        Output: INVOICE

        Input: STATEMENT DATE: 2024-05-26 CUSTOMER STATEMENT ACCOUNT NUMBER: 1234567890 BILL TO: John Doe ADDRESS: 123 Elm Street\
        Springfield, IL 62704 PREVIOUS BALANCE: $1,200.00 NEW CHARGES:  1. May 2024 Monthly Subscription Fee: $50.00 2. Additional Service Charge: $20.00\
        TOTAL NEW CHARGES: $70.00 PAYMENTS & CREDITS:  1. Payment Received - May 15, 2024: $500.00 2. Credit Adjustment: $50.00 TOTAL PAYMENTS & CREDITS: $550.00\
        
        Output: STATEMENT
        </example>

        Document: {text}
        Assitant:
        [/INST]
        """

        classified = model.generate_text(prompt=classify_prompt, guardrails=False)

        classify_list.append(classified)
        classify_list[::-1]

        for i in range(len(classify_list)):
            classify_data[classify_keys[i]] = classify_list[i].strip()
        classified_invoices.append(classify_data)
        print(classified_invoices)
        st.write("Document: " + filename + " is an " + classified)
    except Exception as e:
        logger.exception("Issue with classification")
        pass


def get_discovery_params():
    logger.info("Getting Discovery Parameters")
    try:
        print("********* Running process -  *********")
        Discovery_URL = os.getenv("DISCOVERY_URL",default="")
        Discovery_API_KEY = os.getenv("DISCOVERY_API_KEY", default="")
        project_name = os.getenv("DISCOVERY_PROJECT_NAME",default="")
        collection_name = os.getenv("DISCOVERY_COLLECTION_NAME",default="")


        authenticator = IAMAuthenticator(Discovery_API_KEY,
                                        url='https://iam.cloud.ibm.com/identity/token')
        discovery = DiscoveryV2(
        version='2024-02-29',
        authenticator=authenticator
        )
        discovery.set_service_url(Discovery_URL)
        response = discovery.list_projects(
        ).get_result()

        for item in response['projects']:
            if item['name'] == project_name:
                project_id = item['project_id']

        response = discovery.list_collections(
        project_id=project_id
        ).get_result()

        for item in response['collections']:
            if item['name'] == collection_name:
                collection_id = item['collection_id']

        return project_id, discovery, collection_id
    except Exception as e:
        logger.exception("Issue with  in Discovery Param")
        print(e)
        return 



@st.cache_data(ttl=1800, show_spinner=False)
def ingest_pipeline(filename, folder_path):
    try:
        image_paths = convert_pdf_to_image(filename, folder_path)
        ingest_into_discovery(filename, image_paths)
        return True
    except Exception as e:
        print(e)



@st.cache_data(ttl=1800, show_spinner=False)
def extract_classify_pipeline(filename, model_id):
    try:
        logger.info("Extration and classificaation started")
        with st.spinner("Fetching OCR data for: " + filename):
            flag=0
            if os.path.exists(json_filename):
                with open(json_filename, "r") as file:
                    content = file.read().strip()
                    if not content:
                        flag=-1
                    else:
                        data = json.loads(content)
            else:
                flag=-1
                with open(json_filename,"w") as file:
                    pass

            if filename in data and flag==0:
                document_id_list = data[filename]
                api_call(filename, document_id_list) 
                extracted_text(filename, model_id, document_id_list)
    except Exception as e:
        logger.exception("Exctration pipeline Failed")
        print(e)
        return 


def convert_pdf_to_image(filename, folder_path):
    logger.info("converting to Image")
    try:
        list_image_path = []
        pdfs = folder_path+'/'+filename
        pages = convert_from_path(pdfs, 350)
        filename_without_extension = os.path.splitext(filename)[0]

        save_path = "./converted_image/"
    
        with st.spinner("Converting "+ filename +" PDF to Image"):

            if not os.path.exists(save_path):
                os.makedirs(save_path)

            i = 1
            for page in pages:
                image_path = os.path.join(save_path, filename_without_extension + "_image" + str(i)+ ".jpg")
                page.save(image_path, "JPEG")
                i += 1
                list_image_path.append(image_path)
        return list_image_path
    except Exception as e:
        logger.exception("Issue with image conversion")
        return None



def ingest_into_discovery(filename, image_paths):
    try:
        logger.info("Ingestion to Discovey started")
        document_id_list = []
        data={}
        print(filename)
        project_id, discovery, collection_id = get_discovery_params()
        with st.spinner('Ingesting Image for:' + filename + ' in Discovery!'):
            flag=0
            if os.path.exists(json_filename):
                with open(json_filename, "r") as file:
                    content = file.read().strip()
                    if not content:
                        flag=-1
                    else:
                        data = json.loads(content)
            else:
                flag=-1
                with open(json_filename,"w") as file:
                    pass

            if filename in data and flag==0:
                st.info("File: " + filename + ", already ingested in Discovery.")

            else:
                for image in image_paths:
                        image_in_bytes = open(os.path.join(os.getcwd(), image),'rb')
                        time.sleep(2)
                        response = discovery.add_document(
                                project_id=project_id,
                                collection_id=collection_id,
                                file=image_in_bytes,
                                filename=filename,
                                file_content_type='image/jpeg'
                            ).get_result()
                        document_id = response["document_id"]
                        document_id_list.append(document_id)

                data[filename] = document_id_list
                with open(json_filename, "w") as file:
                        json.dump(data, file)
    except Exception as e:
        print(e)
        logger.exception("Issue in ingesting to Discovery")
        return 




def retrive_data_to_classify(filename):
    try:
        logger.info("Retriving data to classiy")
        document_id_list = []
        data={}
        with st.spinner('Retrieving data from discovery...'):
        
            flag=0
            if os.path.exists(json_filename):
                with open(json_filename, "r") as file:
                    content = file.read().strip()
                    if not content:
                        flag=-1
                    else:
                        data = json.loads(content)
            else:
                flag=-1
                with open(json_filename,"w") as file:
                    pass

            if filename in data and flag==0:
                document_id_list = data[filename]
                return document_id_list
            
            else:
                st.warning(filename + " is not present in Watson-Discovery. Please ingest it first!")
    except Exception as e:
        logger.exception("Issue in Retriving data to classiy")




def api_call(filename, document_id_list):  
    try:   
        logger.info("Api call started to check the status")
        for document_id in document_id_list:
                    
            project_id, discovery, collection_id = get_discovery_params()
            response = discovery.get_document(
                project_id=project_id,
                collection_id=collection_id,
                document_id=document_id
            
            ).get_result()

            status = response["status"]
            
            if status in ['pending', 'processing']:
                with st.sidebar:
                    api_status = st.code("Document Status:" + status, language='log')
                    time.sleep(2)
                    api_status.empty()
                # i += 1
                return api_call(filename, document_id_list)
            
            elif status == 'available':
                return
    except Exception as e:
        print(e)
        logger.exception("Issue with Status checking")
        return 
    
    
def get_result_from_discovery(filename, document_id_list):
    logger.info("Getting Results from discovery")
    combined_text = []
    try:
        for document_id in document_id_list:
        
            project_id, discovery, collection_id = get_discovery_params()
            filter = 'document_id:'+document_id
            response = discovery.query(
            project_id=project_id,
            filter=filter
            ).get_result()
            text = response["results"][0]["text"][0]
            combined_text.append(text)
        return '\n'.join(combined_text)
    except IndexError:
        logger.exception("Error in getting results from Discovery")
        pass


def extracted_text(filename, model_id, document_id_list):
    try:
        logger.info("Etraction text function statred")
        invoice_data = {}
        
        global final_output
        print(final_output)
        text = get_result_from_discovery(filename, document_id_list)
        with st.sidebar:
            st.write("Extracted Text for: " + filename)
            st.code(text, language='log')
        extract_invoice_number(text, filename, model_id)  

        for i in range(len(final_output)):
            invoice_data[extract_keys[i]] = final_output[i].strip()
        
        invoices.append(invoice_data)
        final_output = []
    except Exception as e:
        logger.exception("Issue with Ingestion in Extract text")
        print(e)
        return 
    


def session_init(var):
    if var not in st.session_state:
        st.session_state[var]=None

def clear_cache():
    st.cache_data.clear()

def display_ingestion_status(folder_path):
    try:
        logger.info("Display Ingestion Status function started")
        files = os.listdir(folder_path)
        data = {'Filename': files, 'Ingestion Status': [''] * len(files)}
        df = pd.DataFrame(data)

        output = st.empty()

        output.write(df)

        for i, file_name in enumerate(files):
            ingestion_status = ingest_pipeline(file_name, folder_path)
            if ingestion_status:
                df.loc[i, 'Ingestion Status'] = '✔'
            else:
                logger.error("Ingestion Failed")
                st.warning(f"{file_name} ingestion failed!")

            output.write(df)
    except Exception as e:
        logger.exception("Exception Occured in Ingestion")
        print(e)


def main():
    
    try:
        session_init('uploaded_file')
        session_init('llm_options')
        session_init('interface')

        with st.sidebar:
            st.markdown("<h1 style='color: #7289DA;'>Settings</h1>", unsafe_allow_html=True)

            st.session_state.llm_options = st.selectbox(
                'Select LLM:',
                ('ibm/granite-13b-chat-v2','meta-llama/llama-3-70b-instruct' ,'mistralai/mixtral-8x7b-instruct-v01')
            )
            st.session_state.interface = st.selectbox(
                'Select Interface:',
                ('GA' ,'BAM'), disabled= True
            )
            if st.button("Clear Cache"):
                clear_cache()
            st.markdown("<h1 style='color: #7289DA;'>Debugging</h1>", unsafe_allow_html=True)

        
        folder_path = st.text_input("Enter the Path To Folder: ")
        
        user_info = st.empty()
        user_info.info("Make sure to clear the cache from the sidebar before re-running! Cheers!")
        col1, col2, col3 = st.columns([1,2.5,1])

        with col1:
            extract = st.button("Extract Entities")
            
        with col2:
            classify = st.button("Classify Invoices")
            
        with col3:
            ingest = st.button("Ingest into Wx")
            
        # INGEST

        if ingest:
            logger.info("Ingestion started.")
            user_info.empty()
            if folder_path != "":
                try:
                    with st.spinner("Ingesting all documents present in the folder to Discovery!"):
                        display_ingestion_status(folder_path)
                        logger.info("Ingestion Sucessfully Done.")
                except Exception as e:
                    print(e)
                    logger.info("Issue with Ingestion  .")
                    pass

        #EXTRACT
        
        if extract:
            logger.info("Extraction Started")
            user_info.empty()
            try:
                if folder_path != "":
                    files = os.listdir(folder_path)
                    with st.spinner("Getting Entities for all the files present in the directory!"):
                        for file_name in files:

                            model_id = st.session_state.llm_options

                            extract_classify_pipeline(file_name, model_id)
                    try:
                        with st.spinner("Writing data into Excel:"):
                            time.sleep(2)
                            excel_file_path = ".invoice_data.xlsx"
                            if not invoices:
                                st.warning("This output is from the previous run. To re-run on a new directory, please clear the cache from the side-bar and hit extract again!")
                                df = pd.read_excel(excel_file_path)
                                st.write(df)


                            else:
                                output_dict = collections.defaultdict(list)
                                for d in invoices:
                                    
                                    for key in extract_keys: 
                                        value = d.get(key, '')
                                        value=remove_patterns(value)
                                        
                                        if key == 'Invoice_Number':
                                            value = value.replace('[/INST]', '')
                                        
                                        elif key == 'Total_amount' and not value.startswith('-'):
                                            
                                            if 'USD' in value:
                                                value = value.split()[0]  
                                            
                                            if not value.startswith('$'):
                                                value = '$' + str(value)
                                        
                                        elif key == 'Due_Date':
                                            value = value.split('=')[-1].strip() 
                                        
                                        elif key == 'Purchase_Order_Number' and value.startswith('PO #'):
                                            value = value.replace('PO #', '').strip()
                                        output_dict[key].append(value)
                                df = pd.DataFrame(output_dict)
                                logger.info("Done with extraction")
                                excel_file = excel_file_path
                                df.to_excel(excel_file, index=False)
                                st.write(df)

                    except UnboundLocalError:
                        st.warning("Please clear the cache!")
                        
                else:
                    st.warning("Enter a valid path to a directory!")
                    return
            except FileNotFoundError:
                st.error("Path given is not a valid path!")
        

        #CLASSIFY

        if classify:
            user_info.empty()
            
            if folder_path != "":
                    files = os.listdir(folder_path)
                    with st.spinner("Classifying all the files present in the directory!"):
                        for file_name in files:

                            model_id = st.session_state.llm_options

                            classify_doc_onbuttonclick(model_id, file_name)
                            time.sleep(2)
                            st.empty()

                        try:
                            st.set_option('deprecation.showPyplotGlobalUse', False)
                            excel_file_path = "classified_data.xlsx"
                            if not classified_invoices:
                                st.warning("This output is from the previous run. To re-run on a new directory, please clear the cache from the side-bar and hit extract again!")
                                df = pd.read_excel(excel_file_path)
                                st.write(df)
                                filtered_data = df[['File_Name', 'Classification']].dropna()

                                heatmap_data = filtered_data.groupby(['File_Name', 'Classification']).size().unstack(fill_value=0)

                                # Plot HEATMAP
                                plt.figure(figsize=(10, 8))
                                sns.heatmap(heatmap_data, annot=True, cmap="YlGnBu", fmt='g')
                                plt.xlabel('Classification')
                                plt.ylabel('File_Name')
                                plt.title('Heatmap of Document Frequencies')
                                plt.xticks(rotation=45)
                                plt.yticks(rotation=0)
                                plt.tight_layout()
                                st.pyplot()
                                classification_counts = filtered_data['Classification'].value_counts()

                                # Plot PIE CHART
                                fig, ax = plt.subplots()
                                ax.pie(classification_counts, labels=classification_counts.index, autopct='%1.1f%%', startangle=90)
                                ax.axis('equal')
                                plt.title('Distribution of Classifications')
                                st.pyplot(fig)




                            else:
                                #POST PROCESSING OF OUTPUT FROM LLM
                                classify_output_dict = collections.defaultdict(list)
                                for d in classified_invoices:
                                    
                                    for key in classify_keys: 
                                        value = d.get(key, '')
                                        if key == 'Classification':
                                            value = value.replace(' ', '')
                                        classify_output_dict[key].append(value)
                                df = pd.DataFrame(classify_output_dict)

                                excel_file = excel_file_path
                                df.to_excel(excel_file, index=False)
                                st.write(df)
                                filtered_data = df[['File_Name', 'Classification']].dropna()

                                heatmap_data = filtered_data.groupby(['File_Name', 'Classification']).size().unstack(fill_value=0)

                                # Plot HEATMAP
                                plt.figure(figsize=(10, 8))
                                sns.heatmap(heatmap_data, annot=True, cmap="YlGnBu", fmt='g')
                                plt.xlabel('Classification')
                                plt.ylabel('File_Name')
                                plt.title('Heatmap of Document Frequencies')
                                plt.xticks(rotation=45)
                                plt.yticks(rotation=0)
                                plt.tight_layout()
                                st.pyplot()
                                classification_counts = filtered_data['Classification'].value_counts()

                                # Plot PIE CHART
                                fig, ax = plt.subplots()
                                ax.pie(classification_counts, labels=classification_counts.index, autopct='%1.1f%%', startangle=90)
                                ax.axis('equal')
                                plt.title('Distribution of Classifications')
                                st.pyplot(fig)
                        except UnboundLocalError:
                            st.write("Please clear the cache")
    except Exception as e:
        print(e)
        pass

if __name__ == "__main__":
    logger.info("Streamlit application started.")
    main()