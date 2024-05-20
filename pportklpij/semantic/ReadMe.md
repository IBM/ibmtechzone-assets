# Semantic Comparison README

## Introduction

This repository contains a Python script and a Markdown file to perform semantic comparison between two given texts using sentence embeddings.

## Usage

1. Install required libraries by running `pip install -r requirements.txt` in your terminal.
2. Run the script `semantic_comparison.py` with two text files as command-line arguments, for example: `python semantic_comparison.py`.
3. The script will output a score indicating the similarity between the two texts.

## Code Explanation

The Python script uses the `transformers` library to load pre-trained sentence embeddings and calculates the cosine similarity between the two input texts.

### Requirements

* Python 3.x
* `transformers` library (install using `pip install transformers`)
* Two text files as command-line arguments (`text1.txt` and `text2.txt`)

### Output Format

The script outputs a single score indicating the semantic similarity between the two input texts. The higher the score, the more similar the texts are.

## Notes

* This script is designed to work with plain text files containing sentences or paragraphs.
* You can adjust the pre-trained sentence embedding model used in the script by modifying the `model_name` variable at the top of the script.

### Features
### --------

*   **Highlighting Feature**: This feature generates a line-by-line comparison report, highlighting any changes or differences between the two text
*   **Semantic comparison**: By breaking down meaning of respective texts this program help the user to semantically compare two gien text.