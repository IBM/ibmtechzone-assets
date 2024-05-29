import re
import pandas as pd
import fitz
from langdetect import detect
from typing import List
pd.set_option('display.max_columns', None)

def extract_text_from_pdf(pdf_path, start_page, output_txt):
    text_list = []  # Initialize the list to store text from each page
    end_page = 0
    try:
        with fitz.open(pdf_path) as pdf_document:
            end_page = len(pdf_document)
            for page_num in range(start_page - 1, end_page, 2):  # Iterate over alternate pages
                page = pdf_document[page_num]
                
                # Get the page size
                page_rect = page.rect
                
                # Define the region excluding a smaller percentage from top and bottom
                region = fitz.Rect(page_rect.x0, page_rect.y0 + page_rect.height * 0.13, page_rect.x1 - page_rect.width * 0.21, page_rect.y1 - page_rect.height * 0.08)
                
                # Extract text from the defined region
                text_data = page.get_text("text", clip=region)
                
                text_list.append(text_data)
        
        # Write extracted text to a file
        with open(output_txt, 'w', encoding='utf-8') as text_file:
            for text in text_list:
                text_file.write(text)
                text_file.write('\n')
        
        print(f"Text extraction from pages {start_page} to {end_page} complete.")
    except Exception as e:
        print(f"Error extracting text: {e}")

def is_english(text: str) -> bool:
    try:
        # Detect the language of the text
        return detect(text) == 'en'
    except Exception as e:
        print(f"Error detecting language: {e}")
        return False

def read_extracted_text(path: str) -> str:
    try:
        with open(path, "r", encoding='utf-8') as file:
            content = file.read()
            if is_english(content):
                return content
            else:
                return ""
    except Exception as e:
        print(f"Error reading text file: {e}")
        return ""

def extract_and_read_text(pdf_path: str, start_page: int, output_txt: str) -> str:
    try:
        extract_text_from_pdf(pdf_path, start_page, output_txt)
        return read_extracted_text(output_txt)
    except Exception as e:
        print(f"Error extracting and reading text: {e}")
        return ""

def extraction(pdf_path, chapter_number):
    output_txt = 'extracted.txt'

    # Specify the range of pages to extract
    start_page = 26
    full_text = extract_and_read_text(pdf_path, start_page, output_txt)
    
    # Look for the chapter in the text
    start_marker = f"CHAPTER {chapter_number}"
    end_marker = f"CHAPTER {int(chapter_number) + 1}"  # Assuming chapters are sequential
    
    start_index = full_text.find(start_marker)
    end_index = full_text.find(end_marker, start_index)

    if start_index != -1:
        chapter_text = full_text[start_index:end_index].strip() if end_index != -1 else full_text[start_index:].strip()
    else:
        return pd.DataFrame(columns=['Chapter', 'Chapter_Header', 'Part', 'Part_Header', 'Section', 'Section_Header', 'Sub_Section', 'Sub_Sub_Section', 'Text'])
    
    # Split text into lines
    lines = chapter_text.split('\n')
    processed_lines = []
    current_line = ''
    for line in lines:
        if line.endswith('.'):
            if current_line:  # if current_line is not empty
                processed_lines.append(current_line + ' ' + line)
                current_line = ''  # reset current line
            else:
                processed_lines.append(line)
        else:
            if current_line:
                current_line += ' ' + line
            else:
                current_line = line

    # Joining processed lines back into text
    processed_text = '\n'.join(processed_lines)
    chapter_regex = r"CHAPTER \d+"
    part_regex = r"Part \d+"

    split_text = processed_text.split('\n')
    part_match = re.search(part_regex, split_text[0])
    if part_match == None:
        def format_chapter(text):
            pattern = r"(CHAPTER \d+)\s+([A-Z\s]+)([A-Z][a-z].*)"
            formatted_text = re.sub(pattern, r"\1\n\2\n\3", text)
            return formatted_text
        formatted_text = format_chapter(split_text[0])
        split_text = formatted_text.split('\n') + split_text[1:]
        split_text = '\n'.join(split_text)
    else:
        # Insert newline characters between "CHAPTER" and next text
        text_with_newlines = re.sub(chapter_regex, lambda match: match.group(0) + "\n", split_text[0])
        # Insert newline characters between next text and "Part"
        text_with_newlines = re.sub(part_regex, lambda match: "\n" + match.group(0), text_with_newlines)
        split_text = text_with_newlines.split('\n') + split_text[1:]
        split_text = '\n'.join(split_text)
        
    pattern_title = re.compile(r'(Part \d+ [^\n]+?)([A-Z][^\n]+)')
    modified_text = pattern_title.sub(r'\1 \n\2', split_text)
    split_sentences = []
    pattern_extra = r"HELPLINE:.*?(?=\(\w\))" # Remove text between "HELPLINE" and numbering point

    text_data = modified_text.split('\n')
    # Loop over the text data
    for line in text_data:
        # Split the text by semicolons
        parts = re.sub(pattern_extra, "", line, flags=re.DOTALL)
        
        parts = re.split(r';\s*', parts)
        
        split_sentences.extend(parts)

    cleaned_text = [text for text in split_sentences if text != '']
    
    df = process_legislation_text(cleaned_text)
    
    return df

def process_legislation_text(lines):
    chapter = []
    chapter_header = []
    part = []
    part_header = []
    section = []
    section_header = []
    sub_section = []
    sub_sub_section = []
    text_content = []
    
    # Regular expressions for identifying different parts of the text
    #chapter
    chapter_regex = r"CHAPTER (\d+)"

    #part
    part_regex = r"Part (\d+) (.+)$"
    
    #section
    section_regex = r"(\d+)\."
    section_regex1 = r"(.+) (\d+)\. (.*)"
   
    #subsection
    subsection_regex =  r"\((\d+)\)"
    subsection_regex1 = r"(\d+)\. \((\d+)\)"
    subsection_regex2 = r"(\d+)\. \((\d+)\)(.*)" 
    subsection_regex3 = r"(.+) (\d+)\. \((\d+)\)(.*)"
    
    #subsubsection
    subsubsection_regex = r"\(([a-z])\)"
    subsubsection_regex1 = r"\((\d+)\) \(([a-z])\)" #text after
    subsubsection_regex2 = r"\(([a-z]+)\)"
    subsubsection_regex3 = r"([\w\s]+) \(([a-z])\)"
    subsubsection_regex4 = r"([\w\s]+) (\d+)\. \((\d+)\) \(([a-z])\)"
    subsubsection_regex5 = r"(\d+)\. \((\d+)\) \(([a-z])\)"

    # variables to hold the current context
    current_chapter = ''
    current_chapter_header = ''
    current_part = ''
    current_part_header = ''
    current_section = ''
    current_section_header = ''
    current_text = ''
    current_sub_section = ''
    current_sub_sub_section = ''
    
    # variables to hold the previous context
    prev_sub_sub_section = ''
    
    chapter_match = re.match(chapter_regex, lines[0])
    if chapter_match:
        current_chapter = chapter_match.group(1)

    current_chapter_header = lines[1]

    for line in lines[2:]:
        # Check for part
        part_match = re.match(part_regex, line)
        if part_match:
            current_part = part_match.group(1).strip()
            current_part_header = part_match.group(2)
            # Reset section when a new part is found
            current_section = ''
            continue
        
        # Check for section
        section_match = re.match(section_regex, line)
        section_match1 = re.match(section_regex1, line)
        if section_match:
            current_section = section_match.group(1)
            # Assume no sub-sections at the beginning of a new section
            current_sub_section = ''
            current_sub_sub_section = ''
        elif section_match1:
            current_section = section_match1.group(2).strip()
            current_section_header = section_match1.group(1)
            # Assume no sub-sections at the beginning of a new section
            current_sub_section = ''
            current_sub_sub_section = ''

            
        # Check for subsection
        subsection_match = re.match(subsection_regex, line)
        subsection_match1 = re.match(subsection_regex1, line)
        subsection_match2 = re.match(subsection_regex2, line)
        subsection_match3 = re.match(subsection_regex3, line)
        if subsection_match:
            current_sub_section = subsection_match.group(1).strip()
        elif subsection_match1:
            current_sub_section = subsection_match1.group(2)
        elif subsection_match2:
            current_sub_section = subsection_match2.group(2)
        elif subsection_match3:
            current_sub_section = subsection_match3.group(3)
        else:
            current_sub_section = ''

        # subsubsection
        subsubsection_match = re.match(subsubsection_regex, line)
        subsubsection_match1 = re.match(subsubsection_regex1, line)
        subsubsection_match2 = re.match(subsubsection_regex2, line)
        subsubsection_match3 = re.match(subsubsection_regex3, line)
        subsubsection_match4 = re.match(subsubsection_regex4, line)
        subsubsection_match5 = re.match(subsubsection_regex5, line)
        if subsubsection_match:
            current_sub_sub_section = subsubsection_match.group(1)
        elif subsubsection_match1:
            current_sub_sub_section = subsubsection_match1.group(2)
        elif subsubsection_match2:
            current_sub_sub_section = subsubsection_match2.group(1)
        elif subsubsection_match3:
            current_sub_sub_section = subsubsection_match3.group(2)
        elif subsubsection_match4:
            current_sub_sub_section = subsubsection_match4.group(4)
        elif subsubsection_match5:
            current_sub_sub_section = subsubsection_match5.group(3)
        else:
            current_sub_sub_section = ''
            
        # Additional check for 'b' without 'a'
        if current_sub_sub_section == 'b' and prev_sub_sub_section != 'a':
            # Insert 'a' in the previous row's Sub_Sub_Section without replacing the existing value
            idx = len(sub_sub_section) - 1
            sub_sub_section[idx] = 'a' + sub_sub_section[idx]
        
        # Update the previous subsubsection for the next iteration
        prev_sub_sub_section = current_sub_sub_section
        
        # Append the data to lists
        chapter.append(current_chapter)
        chapter_header.append(current_chapter_header)
        part.append(current_part)
        part_header.append(current_part_header)
        section.append(current_section)
        section_header.append(current_section_header)
        sub_section.append(current_sub_section)
        sub_sub_section.append(current_sub_sub_section)
        text_content.append(line)
    
    # Create a DataFrame
    df = pd.DataFrame({
        'Chapter': chapter,
        'Chapter_Header': chapter_header,
        'Part': part,
        'Part_Header': part_header,
        'Section': section,
        'Section_Header': section_header,
        'Sub_Section': sub_section,
        'Sub_Sub_Section': sub_sub_section,
        'Text': text_content
    })
    
    df_filtered = df[df['Sub_Sub_Section'].str.match(r'^[a-t]$')]

    # Find missing rows
    missing_rows = df[df['Sub_Sub_Section'] == '']

    # Merge missing rows with filtered rows
    df_final = pd.concat([df_filtered, missing_rows]).sort_index().reset_index(drop=True)

    return df_final

