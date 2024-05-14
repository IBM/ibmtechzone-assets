import deepsearch as ds
import os
import json
import tempfile
from zipfile import ZipFile
import logging
import pexpect
from tqdm import tqdm
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('deepsearch_table_extraction.log')
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

def get_tablecell_span(cell, ix):
    span = set([s[ix] for s in cell['spans']])
    if len(span) == 0:
        return 1, None, None
    return len(span), min(span), max(span)



def write_table(item):
    """
    Convert the JSON table representation to HTML, including column and row spans.
    
    Parameters
    ----------
    item :
        JSON table
    doc_cellsdata :
        Cells document provided by the Deep Search conversion
    ncols : int, Default=3
        Number of columns in the display table.
    """
    
    table = item
    body = ""

    nrows = table['#-rows']
    ncols = table['#-cols']

    body += "<table>\n"
    for i in range(nrows):
        body += "  <tr>\n"
        for j in range(ncols):
            cell = table['data'][i][j]

            rowspan,rowstart,rowend = get_tablecell_span(cell, 0)
            colspan,colstart,colend = get_tablecell_span(cell, 1)

            if rowstart is not None and rowstart != i: continue
            if colstart is not None and colstart != j: continue

            if rowstart is None:
                rowstart = i
            if colstart is None:
                colstart = j

            content = cell['text']
            if content == '':
                content = '&nbsp;'

            label = cell['type']
            label_class = 'body'
            if label in ['row_header', 'row_multi_header', 'row_title']:
                label_class = 'header'
            elif label in ['col_header', 'col_multi_header']:
                label_class = 'header'
            
            
            celltag = 'th' if label_class == 'header' else 'td'
            style = 'style="text-align: center;"' if label_class == 'header' else ''

            body += f'    <{celltag} rowstart="{rowstart}" colstart="{colstart}" rowspan="{rowspan}" colspan="{colspan}" {style}>{content}</{celltag}>\n'

        body += "  </tr>\n"

    body += "</table>"

    return body

def extract_document_tables(doc_jsondata):
    """
    Visualize the tables idenfitied in the converted document.
    
    Parameters
    ----------
    doc_jsondata :
        Converted document
    """

    
    pdf_tables = {}
    # Iterate through all the tables identified in the converted document
    for table in doc_jsondata.get("tables", []):
        prov = table["prov"][0]
        page = prov["page"]
        pdf_tables.setdefault(page, "")
        
        output_html = write_table(table)
        pdf_tables[page] = pdf_tables[page]+"\n\n" + output_html 
    return pdf_tables




class DeepSearchTableExtraction:
    """
    A class to handle table extraction using DeepSearch.

    Args:
        login_cmd (str): Command to log in to DeepSearch.
        api_key (str): API key for authentication with DeepSearch.
        proj_key (str): Project key for identifying the specific project in DeepSearch.

    Methods:
        login() -> dict:
            Logs in to DeepSearch using provided command and API key.
            Returns a dictionary with the status of the login attempt.
        
        extract_table(file_path: str) -> None:
            Extracts tables from the document specified by the file path.
    
    Limitations : 
        Currently does not support OCR Extraction. Will be updated soon. 
    """
    def __init__(self) -> None:
        login_response = self.login()
        if login_response['status'] :
            logger.info('Connection Established with DeepSearch')
            self.api = ds.CpsApi.from_env()
        else :
            logger.error("Deepserch Connection Issue ",login_response['exception'])
            
    def login(self) -> dict:
        try:
            # Run shell command
            command = os.getenv('login_cmd') 
            process = pexpect.spawn(command)

            # Enter password
            api_key = os.getenv('deepsearch_api_key') # Copy API Key from deepsearch

            # Send password to the shell command
            process.expect("Api key:")
            process.sendline(api_key)

            # Wait for the command to finish and get output
            process.expect(pexpect.EOF)
            return {"status" : True}
        except Exception as exp:
            return {"status" : False, "exception" : exp}
        
    def extract_table(self, file_path) :

        try : 
            logger.info("Processing : %s", file_path)
            documents = ds.convert_documents(
                                                api=self.api,
                                                proj_key=os.getenv('project_key'), # you can project key with ```print([p.key for p in api.projects.list()])```
                                                source_path=file_path,
                                                progress_bar=True
                                            )  

            output_dir = tempfile.mkdtemp()

            documents.download_all(result_dir=output_dir, progress_bar=True)

            for output_file in Path(output_dir).rglob("json*.zip"):
                with ZipFile(output_file) as archive:
                    all_files = archive.namelist()
                    
                    for name in all_files:
                        if not name.endswith(".json"):
                            continue
                        
                        basename = name.split(".json")[0]
                        doc_jsondata = json.loads(archive.read(f"{basename}.json"))
                        tables = extract_document_tables(doc_jsondata)
            return tables
        except Exception as exp :
            logger.error("Extraction Failed : ",exp)
            
            
    