import pandas as pd
import numpy as np
import os
DATA_FILE_NAME = os.environ["data_file"]
if os.path.isfile(DATA_FILE_NAME):
    # If file exists read data from the data file and create data frame
    df = pd.read_csv(DATA_FILE_NAME)
else:
    # No data file exists so just generate some random data
    df = pd.DataFrame(np.random.randint(0,100,size=(100, 4)), columns=list('ABCD'))
# Print summary statistics
print(df.describe())