import os
import subprocess
import warnings

warnings.filterwarnings('ignore')

# Give file name
item_name = "*.doc"

# Give directory name
temp_dir = "/xx"

# Determine the file extension
_, file_extension = os.path.splitext(item_name)

if file_extension.lower() in [".doc", ".docx"]:
    # Define the output PDF file path
    temp_file_path = os.path.join(temp_dir, item_name)
    subprocess.call(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", temp_dir, temp_file_path])