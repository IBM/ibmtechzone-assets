def upload_csv(file: UploadFile = File(...)):
    if len(uploaded_files) >= MAX_UPLOADED_FILES:
        return CSVUploadResponse(
            message=f"Upload files limit exceeded. Maximum {MAX_UPLOADED_FILES} files allowed. Please delete unnecessary files and retry.",
            status_code=400,
        )

    if not file.filename.endswith(".csv"):
        return CSVUploadResponse(message="File must be a CSV", status_code=400)

    file_name_without_extension = os.path.splitext(file.filename)[0]
    if len(file_name_without_extension) > MAX_FILENAME_LENGTH:
        return CSVUploadResponse(
            message=f"File name is too long. Maximum {MAX_FILENAME_LENGTH} characters allowed (excluding extension).",
            status_code=400,
        )

    file_name = file.filename
    file_path = os.path.join(UPLOAD_DIRECTORY, file_name)

    try:
        # Save the file
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Try to read the CSV file with different encodings
        df = try_read_csv(file_path)

        # Check number of rows and columns
        if df.shape[0] > 300000 or df.shape[1] > 30:
            os.remove(file_path)
            return CSVUploadResponse(
                message=f"CSV file '{file.filename}' exceeds maximum allowed dimensions (300,000 rows and 30 columns)",
                status_code=400,
            )

        # Check for complex data types
        if df.applymap(lambda x: isinstance(x, (list, dict))).any().any():
            os.remove(file_path)
            return CSVUploadResponse(
                message=f"CSV file '{file.filename}' contains complex data types (lists or dictionaries)",
                status_code=400,
            )

        uploaded_files[file_name] = file_path
        return CSVUploadResponse(
            message=f"CSV file '{file.filename}' uploaded and processed successfully",
            file_name=file_name,
            status_code=200,
        )

    except pd.errors.EmptyDataError:
        os.remove(file_path)
        return CSVUploadResponse(
            message=f"The CSV file '{file.filename}' is empty", status_code=400
        )
    except pd.errors.ParserError:
        os.remove(file_path)
        return CSVUploadResponse(
            message=f"Error parsing CSV file '{file.filename}'. Please ensure it's a valid CSV with comma-separated values",
            status_code=400,
        )
    except ValueError as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return CSVUploadResponse(message=str(e), status_code=400)
    
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return CSVUploadResponse(
            message=f"An error occurred while processing the file '{file.filename}': {str(e)}",
            status_code=500,
        )



import csv
import json
import pandas as pd
import chardet
from typing import Tuple, Dict, Any
import logging
import os


class DataDescriptionCreator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def detect_encoding(self, file_path: str) -> str:
        """Detect the encoding of a file."""
        try:
            with open(file_path, "rb") as file:
                raw_data = file.read()
            return chardet.detect(raw_data)["encoding"]
        except IOError as e:
            self.logger.error(f"Error reading file: {e}")
            raise

    def read_csv_file(self, file_path: str, encoding: str) -> Tuple[pd.DataFrame, str]:
        """Read a CSV file and detect its delimiter."""
        delimiters = [",", ";", "\t", "|"]

        for delimiter in delimiters:
            try:
                df = pd.read_csv(file_path, encoding=encoding, sep=delimiter)
                if len(df.columns) > 1:
                    return df, delimiter
            except Exception:
                continue

        try:
            df = pd.read_csv(file_path, encoding=encoding, sep=None, engine="python")
            return df, "inferred"
        except Exception as e:
            self.logger.error(f"Unable to read the CSV file: {e}")
            raise ValueError(
                "Unable to read the CSV file. Please check the file format."
            )

    def create_column_description(self, csv_file_path: str) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """Create a JSON file with column descriptions from a CSV file."""
        try:
            file_encoding = self.detect_encoding(csv_file_path)
            self.logger.info(f"Detected file encoding: {file_encoding}")

            df, delimiter = self.read_csv_file(csv_file_path, file_encoding)
            self.logger.info(f"Detected delimiter: '{delimiter}'")

            column_descriptions = self._generate_column_descriptions(df)

            # Generate JSON file path
            json_file_path = os.path.splitext(csv_file_path)[0] + "_description.json"

            with open(json_file_path, "w", encoding="utf-8") as json_file:
                json.dump(column_descriptions, json_file, indent=2, ensure_ascii=False)

            self.logger.info(
                f"Column descriptions have been written to {json_file_path}"
            )

            return df, column_descriptions
        except Exception as e:
            self.logger.error(f"Error in create_column_description: {e}")
            raise

    def _generate_column_descriptions(self, df: pd.DataFrame) -> Dict[str, str]:
        """Generate descriptions for each column in the DataFrame."""
        column_descriptions = {}
        for column in df.columns:
            data_type = str(df[column].dtype)
            nullable = "Yes" if df[column].isnull().any() else "No"
            example = self._get_example_value(df[column])
            description = f"{column}.\nType: {data_type}\nNullable: {nullable}\nExample: {example}"
            column_descriptions[column] = description
        return column_descriptions

    def _get_example_value(self, series: pd.Series) -> Any:
        """Get a non-null example value from a pandas Series."""
        example = series.dropna().iloc[0] if not series.empty else "N/A"
        if isinstance(example, str):
            example = example[:50] + "..." if len(example) > 50 else example
        return example


def create_description(csv_file_path: str) -> None:
    """Create a column description JSON file from a CSV file."""
    creator = DataDescriptionCreator()
    creator.create_column_description(csv_file_path)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create a JSON file with column descriptions from a CSV file.")
    parser.add_argument("csv_file", help="Path to the input CSV file")
    args = parser.parse_args()

    create_description(args.csv_file)
