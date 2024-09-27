import pandas as pd
import pymupdf

def extract_tables_from_pdf(input_file, page_ranges):
    """
    Extracts tables from a PDF over the specified page ranges.
    
    Args:
        input_file (str): Path to the PDF file.
        page_ranges (list of tuple): List of page range tuples e.g., [(start_page, end_page)].
        
    Returns:
        pd.DataFrame: return combined tables
    """
    try:

        doc = pymupdf.open("test.pdf")
        all_tables = []

        for start_page, end_page in page_ranges:
            for i in range(start_page, end_page + 1):
                if i >= len(doc):
                    continue
                
                page = doc[i]
                tables = page.find_tables()
                
                for table in tables:
                    df = pd.DataFrame(table.extract())
                    df_cleaned = df[df.apply(lambda row: row.astype(str).str.strip().ne('').any(), axis=1)].reset_index(drop=True)
                    all_tables.append(df_cleaned)
        
        all_tables_df = pd.concat(all_tables, ignore_index=True)
        
        return all_tables_df

    except Exception as e:
        print("Error in extract_tables_from_pdf: ", e)
        return None