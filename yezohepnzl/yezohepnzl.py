import pandas as pd
import numpy as np
import os
if os.path.isfile("/data/my_data_file.csv"):
    # If file exists read data from the data file and create data frame
    df = pd.read_csv('/data/my_data_file.csv')
else:
    # No data file exists so just generate some random data
    df = pd.DataFrame(np.random.randint(0,100,size=(100, 4)),columns=list('ABCD'))
# Print summary statistics
print(df.describe())
