import requests
RAW_FILE_URL = os.environ["raw_file_url"]
OUTPUT_FILE_NAME = os.environ["output_file_name"]

resp = requests.get(RAW_FILE_URL)
open(OUTPUT_FILE_NAME,'wb').write(resp.content)