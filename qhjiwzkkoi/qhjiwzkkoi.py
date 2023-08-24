import pandas as pd
from sqlalchemy import create_engine

CONN_STRING = os.environ["conn_string"]
TABLE_NAME = os.environ["table_name"]
query="SELECT * FROM "+TABLE_NAME

my_conn = create_engine(CONN_STRING)

df = pd.read_sql(query,my_conn)
df.describe(include='all').transpose()