import pandas as pd
import pyarrow.parquet as pq
from io import StringIO
from os import listdir
from os.path import isfile, join

def determine_file_type(filename):
    try:
        with open(filename, 'rb') as f:
            # Read the beginning of the file to check for Parquet magic bytes
            magic_bytes = f.read(4)
            f.seek(0)  # Reset file pointer to beginning
            if magic_bytes == b'PAR1':
                return 'Parquet'
            else:
                # Try to parse the content as CSV
                pd.read_csv(filename)
                return 'CSV'
    except Exception as e:
        return 'Unknown'

datafile_location=os.environ["datafile_location"]
onlyfiles = [f for f in listdir(datafile_location) if isfile(join(datafile_location, f))]

for datafile in onlyfiles:
    file_type = determine_file_type(datafile)
    print(f"The file '{datafile}' is of type: {file_type}")
