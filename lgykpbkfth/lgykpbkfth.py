
import fitz # install pymupdf using 'pip3 install pymupdf'

input_dir_path=""  #pass the path of your input directory
output_dir_path="" #pass the path of your output directory

def highlight(filename,words_to_highlight):
    input_file=input_dir_path+filename
    output_file_path=output_dir_path+filename
    doc = fitz.open(input_file)
    for word in words_to_highlight:
        for page in doc:
                text_instances = page.search_for(word)
                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.update()

    doc.save(output_file_path, garbage=4, deflate=True, clean=True)  #new pdf will be created that highlights the words that are passed in "words_to_highlight" parameter.
    

words_to_highlight=["Bob","23456"] # We can pass a list of words that we need to highlight in pdf
highlight("tracebility_document.pdf",words_to_highlight)
    


    
    
 




