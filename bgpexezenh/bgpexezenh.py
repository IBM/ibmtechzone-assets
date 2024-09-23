# File: csv_qa_chatbot/chatbot.py
import pandas as pd
import numpy as np
import json
import os
import io
import sys
import logging
from contextlib import redirect_stdout, redirect_stderr
from langchain_openai import ChatOpenAI
from langchain_ibm import ChatWatsonx, WatsonxLLM
from dotenv import load_dotenv
import matplotlib
matplotlib.use('Agg')


class CSVQAChatbot:
    def __init__(self, csv_file_path, max_attempts=3, log_level=logging.INFO):
        self.setup_logging(log_level)
        self.logger.info(f"Initializing CSVQAChatbot with file: {csv_file_path}")
        self.df = self._read_csv_to_dataframe(csv_file_path)
        self.schema = self._create_schema()
        self.max_attempts = max_attempts
        load_dotenv()
        # self.llm = ChatOpenAI(
        #     base_url=os.getenv("URL"),
        #     api_key=os.getenv("KEY"),
        #     model=os.getenv("MODEL"),
        # )
        self.llm = WatsonxLLM(
            apikey=os.getenv("WATSONX_API"),
            model_id=os.getenv("WATSONX_MID"),
            url=os.getenv("WATSONX_URL"),
            project_id=os.getenv("WATSONX_PID"),
            params={
                "decoding_method": "sample",
                "max_new_tokens": 200,
                "min_new_tokens": 1,
                "stop_sequences": ["</ASSISTANT>",]
            },
        )
        self.logger.info("CSVQAChatbot initialized successfully")

    def setup_logging(self, log_level):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _read_csv_to_dataframe(self, file_path):
        self.logger.info(f"Reading CSV file: {file_path}")
        try:
            df = pd.read_csv(file_path)
            self.logger.info(f"CSV file read successfully. Shape: {df.shape}")
            return df
        except Exception as e:
            self.logger.error(f"Error reading CSV file: {str(e)}")
            raise

    def _create_schema(self):
        self.logger.info("Creating schema from DataFrame")
        schema = {}
        for column in self.df.columns:
            column_type = self.df[column].dtype
            is_numeric = np.issubdtype(column_type, np.number)
            is_datetime = pd.api.types.is_datetime64_any_dtype(self.df[column])

            column_info = f"{column}\n"
            column_info += f"Type: {column_type}\n"
            column_info += f"Numeric: {'Yes' if is_numeric else 'No'}\n"
            column_info += f"DateTime: {'Yes' if is_datetime else 'No'}\n"
            column_info += (
                f"Null: {'Yes' if self.df[column].isnull().any() else 'No'}\n"
            )

            if is_numeric:
                column_info += f"Min: {self.df[column].min()}\n"
                column_info += f"Max: {self.df[column].max()}\n"
                column_info += f"Mean: {self.df[column].mean()}\n"
            elif is_datetime:
                column_info += f"Earliest: {self.df[column].min()}\n"
                column_info += f"Latest: {self.df[column].max()}\n"
            else:
                column_info += f"Unique Values: {self.df[column].nunique()}\n"

            non_null_value = (
                self.df[column].dropna().iloc[0]
                if not self.df[column].isnull().all()
                else None
            )
            column_info += f"Example: {non_null_value}"

            schema[column] = column_info

        self.logger.info("Schema created successfully")
        return json.dumps(schema, indent=2)

    def _execute_code(self, code):
        self.logger.info("Executing generated code")
        output = io.StringIO()
        error = io.StringIO()

        try:
            with redirect_stdout(output), redirect_stderr(error):
                exec(
                    code,
                    {
                        "df": self.df,
                        "pd": pd,
                        "np": np,
                        "plt": __import__("matplotlib.pyplot"),
                    },
                )
            self.logger.info("Code executed successfully")
            return output.getvalue(), None
        except Exception as e:
            self.logger.error(f"Error executing code: {str(e)}")
            return None, f"{str(e)}\n{error.getvalue()}"

    def _get_llm_response(self, question, error=None):
        self.logger.info(f"Generating LLM response for question: {question}")
        system_prompt = f"""<SYSTEM>\nYou are an expert data analyst and Python programmer specializing in pandas DataFrame operations and data analysis. Your task is to generate Python code to answer questions about a DataFrame based on the provided schema.

DataFrame Schema:
{self.schema}

Instructions:
1. Analyze the question carefully and determine the most efficient pandas operations to solve the task.
2. Provide only executable Python code as your response. Do not include any explanations or comments outside the code block.
3. A L W A Y S write the code inside triple backticks with the python language specifier.
4. Assume the DataFrame is already loaded and named 'df'.
5. Use pandas, numpy, and matplotlib libraries for data manipulation, analysis, and visualization.
6. Handle different data types appropriately:
   - For numeric columns, consider operations like mean, median, sum, min, max, etc.
   - For datetime columns, consider operations like filtering by date ranges, resampling, etc.
   - For categorical columns, consider operations like value counts, grouping, etc.
7. When creating plots:
   a. Save the plot to the 'images/' directory with a descriptive filename.
   b. Use plt.savefig() instead of plt.show().
   c. Close the plot with plt.close() to free up memory.
8. Ensure your code is efficient, following pandas best practices.
9. Handle potential errors or edge cases in your code (e.g., check for column existence, handle NaN values).
10. If the question requires multiple steps, use intermediate variables and split the operations for clarity.
11. If the question is ambiguous, make reasonable assumptions and implement the most likely interpretation.
12. Always include code to create the 'images/' directory if it doesn't exist, when saving plots.
13. Print the final result or a summary of the operation performed.
14. Use appropriate data visualization techniques based on the data types and question:
    - For numeric data, consider scatter plots, line charts, or histograms.
    - For categorical data, consider bar charts or pie charts.
    - For time series data, consider line charts with appropriate time-based x-axis.
15. When dealing with large datasets, consider using efficient pandas operations like:
    - .value_counts(normalize=True) for percentage distributions
    - .groupby() with appropriate aggregations
    - .agg() for multiple aggregations in one operation
16. For text data, consider basic text analysis like word counts or length statistics if relevant.
17. Always handle potential missing data appropriately, using methods like .dropna() or .fillna() as needed.



To submit your response use this format:
```python
code cell
print(...)
```



Example:
Question: Analyze the distribution of ages and create a histogram, also provide summary statistics.

Answer:
```python
import pandas as pd
import matplotlib.pyplot as plt
import os

if 'Age' in df.columns:
    # Summary statistics
    age_stats = df['Age'].describe()
    print("Age Summary Statistics:")
    print(age_stats)
    
    # Create histogram
    plt.figure(figsize=(10, 6))
    df['Age'].hist(bins=20, edgecolor='black')
    plt.title('Distribution of Ages')
    plt.xlabel('Age')
    plt.ylabel('Frequency')
    
    # Create 'images/' directory if it doesn't exist
    os.makedirs('images', exist_ok=True)
    
    # Save the plot
    plt.savefig('images/age_distribution_histogram.png')
    plt.close()
    
    print("Histogram saved as 'images/age_distribution_histogram.png'")
else:
    print("Error: 'Age' column not found in the DataFrame.")
```</SYSTEM>"""

        user_prompt = f"<USER>\nQuestion: {question}\n</USER>"

        if error:
            user_prompt += f"\n\nThe previous code generated an error. Please fix it and try again. Error details:\n{error}"

        assistant_prompt = "<ASSISTANT>\nAnswer:"

        full_prompt = system_prompt + "\n\n" + user_prompt + "\n\n" + assistant_prompt

        response = self.llm.invoke(full_prompt)#.content

        # Ensure the response ends with triple backticks
        if not response.strip().endswith("```"):
            response += "\n```"

        self.logger.info("LLM response generated successfully")
        return response

    def ask(self, question):
        self.logger.info(f"Processing question: {question}")
        for attempt in range(self.max_attempts):
            self.logger.info(f"Attempt {attempt + 1} of {self.max_attempts}")
            response = self._get_llm_response(
                question, error=None if attempt == 0 else error
            )
            self.logger.info(f"Response from LLM:\n{response}")

            # Extract code from the response
            code = response.split("```python")[1].split("```")[0].strip()
            self.logger.info(f"Generated code:\n{code}")

            # Execute the code
            output, error = self._execute_code(code)

            if error is None:
                self.logger.info("Code executed successfully")
                return {"status": "success", "output": output, "code": code}
            else:
                self.logger.warning(f"Error in attempt {attempt + 1}: {error}")
                if attempt == self.max_attempts - 1:
                    self.logger.error("Max attempts reached")
                    return {
                        "status": "error",
                        "message": f"Max attempts ({self.max_attempts}) reached. Please rephrase your question and try again.",
                        "error": error,
                        "code": code,
                    }

        # This should never be reached, but just in case
        self.logger.error("Unexpected error occurred")
        return {"status": "error", "message": "Unexpected error occurred."}