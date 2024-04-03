import pandas as pd

def check_non_null(row):
    if pd.notnull(row['numerical entities expected']) or pd.notnull(row['numerical entities expected']):
        return 'review numerical values'
    else:
        return None