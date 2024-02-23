import pandas as pd
import pyarrow.parquet as pq
from io import StringIO
from os import listdir
from os.path import isfile, join
import os

def determine_file_type(filename):
    try:
        with open(filename, 'rb') as f:
            # Read the beginning of the file to check for Parquet magic bytes
            print("Starting to read")
            magic_bytes = f.read(4)
            f.seek(0)  # Reset file pointer to beginning
            print(magic_bytes)
            if magic_bytes == b'PAR1':
                return 'Parquet'
            else:
                try:
                    # Try to parse the content as JSON
                    pd.read_json(filename)
                    return 'JSON'
                except Exception as e:
                    try:
                        # Try to parse the content as ORC
                        pd.read_orc(filename)
                        return 'ORC'
                    except Exception as e:
                        # Try to parse the content as CSV
                        pd.read_csv(filename)
                        return 'CSV'
    except Exception as e:
        print(e)
        return 'Unknown'

datafile_location=os.environ["datafile_location"]
onlyfiles = [f for f in listdir(datafile_location) if isfile(join(datafile_location, f))]

for datafile in onlyfiles:
    print(join(datafile_location, datafile))
    file_type = determine_file_type(join(datafile_location, datafile))
    print(f"The file '{datafile}' is of type: {file_type}")
