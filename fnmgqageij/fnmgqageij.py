import re
import json

def parse_cobol(cobol_code):
    lines = cobol_code.split('\n')
    outline = {"name": "PROGRAM", "type": "program", "children": []}
    current_division = None
    current_section = None
    current_function = None

    # Pattern to match lines to ignore
    ignore_pattern = re.compile(r'^\d{2}\d{4}\*|^\d{2}\d{4}\/\*|\*.*\*$')

    for line in lines:
        stripped_line = line.strip()
        
        # Ignore lines that match the ignore pattern
        if ignore_pattern.match(stripped_line):
            continue

        indent_level = len(line) - len(line.lstrip())

        # Check for divisions
        if 'DIVISION' in stripped_line:
            current_division = next((child for child in outline["children"] if child["name"] == stripped_line.split('.')[0]), None)
            if not current_division:
                current_division = {
                    "type": "division",
                    "name": stripped_line.split('.')[0],
                    "content": [],
                    "sections": [],
                    "functions": []
                }
                outline["children"].append(current_division)
            current_section = None
            current_function = None
        elif 'SECTION.' in stripped_line and current_division:
            current_section = next((section for section in current_division["sections"] if section["name"] == stripped_line.split('.')[0]), None)
            if not current_section:
                current_section = {
                    "type": "section",
                    "name": stripped_line.split('.')[0],
                    "content": []
                }
                current_division["sections"].append(current_section)
            current_function = None
        elif current_division and stripped_line and not current_section and not current_function:
            # Detecting function start (assuming a function name ends with a period)
            function_name = stripped_line.split('.')[0]
            current_function = {
                "type": "function",
                "name": function_name,
                "content": []
            }
            current_division["functions"].append(current_function)
        elif current_function:
            current_function["content"].append(line)
            if 'EXIT.' in stripped_line:
                current_function = None
        elif current_section:
            current_section["content"].append(line)  # Append line with indentation intact
        elif current_division:
            current_division["content"].append(line)  # Append line with indentation intact

    return outline


def generate_outline(cobol_code):
    outline = parse_cobol(cobol_code)
    return outline
    
if __name__ =="__main__":

    # Example usage
    # cobol_code = """
    # IDENTIFICATION DIVISION.
    # PROGRAM-ID. InventoryCRUD.
    # DATA DIVISION.
    # FILE SECTION.
    # FD  INVENTORY-FILE.
    # 01  INVENTORY-RECORD.
    #     05  PRODUCT-ID         PIC X(10).
    #     05  PRODUCT-NAME       PIC X(50).
    #     05  QUANTITY-IN-STOCK  PIC 9(5).

    # WORKING-STORAGE SECTION.
    # 01  OPERATION             PIC X.
    #     88  CREATE            VALUE 'C'.
    #     88  READ              VALUE 'R'.
    #     88  UPDATE            VALUE 'U'.
    #     88  DELETE            VALUE 'D'.
    # 01  NEW-PRODUCT-ID        PIC X(10).
    # 01  NEW-PRODUCT-NAME      PIC X(50).
    # 01  NEW-QUANTITY          PIC 9(5).

    # PROCEDURE DIVISION.
    # BEGIN.
    #     DISPLAY 'SELECT OPERATION (C/R/U/D): '
    #     ACCEPT OPERATION

    #     EVALUATE OPERATION
    #         WHEN CREATE
    #             PERFORM CREATE-PRODUCT
    #         WHEN READ
    #             PERFORM READ-PRODUCT
    #         WHEN UPDATE
    #             PERFORM UPDATE-PRODUCT
    #         WHEN DELETE
    #             PERFORM DELETE-PRODUCT
    #         WHEN OTHER
    #             DISPLAY 'INVALID OPERATION'
    #     END-EVALUATE

    #     STOP RUN.

    # CREATE-PRODUCT.
    #     DISPLAY 'ENTER NEW PRODUCT ID: '
    #     ACCEPT NEW-PRODUCT-ID
    #     DISPLAY 'ENTER PRODUCT NAME: '
    #     ACCEPT NEW-PRODUCT-NAME
    #     DISPLAY 'ENTER QUANTITY IN STOCK: '
    #     ACCEPT NEW-QUANTITY
    #     OPEN OUTPUT INVENTORY-FILE
    #     MOVE NEW-PRODUCT-ID TO PRODUCT-ID OF INVENTORY-RECORD
    #     MOVE NEW-PRODUCT-NAME TO PRODUCT-NAME OF INVENTORY-RECORD
    #     MOVE NEW-QUANTITY TO QUANTITY-IN-STOCK OF INVENTORY-RECORD
    #     WRITE INVENTORY-RECORD
    #     CLOSE INVENTORY-FILE
    #     DISPLAY 'PRODUCT CREATED'.

    # READ-PRODUCT.
    #     DISPLAY 'ENTER PRODUCT ID TO READ: '
    #     ACCEPT NEW-PRODUCT-ID
    #     OPEN INPUT INVENTORY-FILE
    #     READ INVENTORY-FILE INTO INVENTORY-RECORD
    #         AT END
    #             DISPLAY 'PRODUCT NOT FOUND'
    #         NOT AT END
    #             DISPLAY 'PRODUCT FOUND: ' PRODUCT-NAME OF INVENTORY-RECORD
    #                 ', QUANTITY: ' QUANTITY-IN-STOCK OF INVENTORY-RECORD
    #     END-READ
    #     CLOSE INVENTORY-FILE.

    # UPDATE-PRODUCT.
    #     DISPLAY 'ENTER PRODUCT ID TO UPDATE: '
    #     ACCEPT NEW-PRODUCT-ID
    #     DISPLAY 'ENTER NEW QUANTITY: '
    #     ACCEPT NEW-QUANTITY
    #     OPEN I-O INVENTORY-FILE
    #     START INVENTORY-FILE KEY IS EQUAL TO NEW-PRODUCT-ID
    #     READ INVENTORY-FILE NEXT RECORD INTO INVENTORY-RECORD
    #         INVALID KEY
    #             DISPLAY 'PRODUCT NOT FOUND'
    #         NOT INVALID KEY
    #             MOVE NEW-QUANTITY TO QUANTITY-IN-STOCK OF INVENTORY-RECORD
    #             REWRITE INVENTORY-RECORD
    #             DISPLAY 'PRODUCT UPDATED'
    #     END-READ
    #     CLOSE INVENTORY-FILE.

    # DELETE-PRODUCT.
    #     DISPLAY 'ENTER PRODUCT ID TO DELETE: '
    #     ACCEPT NEW-PRODUCT-ID
    #     OPEN I-O INVENTORY-FILE
    #     DELETE INVENTORY-RECORD RECORD KEY IS NEW-PRODUCT-ID
    #         INVALID KEY
    #             DISPLAY 'PRODUCT NOT FOUND'
    #         NOT INVALID KEY
    #             DISPLAY 'PRODUCT DELETED'
    #     CLOSE INVENTORY-FILE.
    # """

    encodings = ['utf-8', 'iso-8859-1', 'cp1252', 'ascii']

    for encoding in encodings:
        try:
            with open('path_to_cobol_file', 'r', encoding=encoding) as file:
                cobol_code = file.read()
            print(f"Successfully read with {encoding} encoding")
            break
        except UnicodeDecodeError:
            print(f"Failed to read with {encoding} encoding")

    outline = generate_outline(cobol_code)
    with open("path_to_output_json_file",'w', encoding='utf-8') as f:
        json.dump(outline, f, ensure_ascii=False, indent=2)