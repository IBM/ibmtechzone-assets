import os
import pandas as pd
import csv
import json
from tokenizers import Tokenizer
from semantic_text_splitter import TextSplitter

class SemanticChunking:
    def __init__(self, filename, config_path='config.json', folder_path=None):
        self.filename = filename
        self.folder_path = folder_path or '/default/folder/path'  # default folder path if none provided

        # Load configuration
        with open(config_path, 'r') as file:
            config = json.load(file)

        self.embedding_method = config['default']['model']
        max_tokens = config.get('max_tokens', 1000)  # Default to 1000 if not specified in config

        # Load tokenizer
        self.tokenizer = Tokenizer.from_pretrained(config.get('tokenizer', "bert-base-multilingual-cased"))

        # Initialize TextSplitter with the tokenizer
        self.splitter = TextSplitter.from_huggingface_tokenizer(self.tokenizer, max_tokens)

    def read_text_from_file(self):
        """ Reads text from the specified file. """
        with open(self.filename, 'r', encoding='utf-8') as file:
            return file.read()

    def perform_semantic_chunking_and_save(self):
        """ Performs semantic chunking and saves the chunks to a CSV file. """

        # Read the text from the file
        document_text = self.read_text_from_file()

        # Perform semantic chunking using the TextSplitter
        chunks = self.splitter.chunks(document_text)

        # Construct output file name
        chunk_filename = os.path.splitext(os.path.basename(self.filename))[0]
        output_csv = f"{chunk_filename}_semantic_{self.embedding_method.split('/')[-1]}.csv"

        # Write chunks to CSV
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Chunk'])  # Header row
            for chunk in chunks:
                csv_writer.writerow([chunk])

        # Load into a pandas DataFrame for further processing or confirmation
        df = pd.read_csv(output_csv)
        print(df)

        # Save the DataFrame to the specified folder path
        file_path = os.path.join(self.folder_path, output_csv)
        df.to_csv(file_path, index=False)

        return file_path

# Usage Example:
# chunker = SemanticChunking('example.txt', folder_path='/path/to/save/csvs')
# chunker.perform_semantic_chunking_and_save()
