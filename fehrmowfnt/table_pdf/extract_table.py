
import pandas as pd # install package pandas; pip install pandas
import pymupdf  # install package PyMuPDF; pip install PyMuPDF


# Provide the path/file (PDF)contains the table.
input_file = " "

def extract_table(input_file):
    try:
        doc = pymupdf.open(input_file)
        # print("Total number of Pages:",len(doc))
        for i in range(len(doc)):
            page = doc[i]
            tabs = page.find_tables()
            # print("Total number of table",len(tabs.tables))
            if len(tabs.tables)>0:
                for j in range(len(tabs.tables)):
                    tab=tabs[j]
                    df = pd.DataFrame(tab.extract())
                    df_cleaned = df[df.apply(lambda row: row.astype(str).str.strip().ne('').any(), axis=1)]
                    df_cleaned.reset_index(drop=True, inplace=True)
                    print("Page Number: ", i, "Table Number: ", j)
                    print(df_cleaned)
        return "Table Extracted !!"
    except Exception as e:
        print("Error in extract_noborder_table: ", e)
        return e


print(extract_table(input_file))