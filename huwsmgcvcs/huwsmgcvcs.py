from sqlalchemy import create_engine
import pandas as pd
import os

# Connect to Mysql database
CONN_STRING = os.environ["conn_string"]
my_conn = create_engine(CONN_STRING)

# Create Pandas dataframe from file
INPUT_DATA_FILE = os.environ["input_data_file"]
csv_df=pd.read_csv(INPUT_DATA_FILE)

# Save pandas data frame to MysqL table
TABLE_NAME = os.environ["table_name"]
csv_df.to_sql(TABLE_NAME, my_conn, if_exists='replace', index=False)
