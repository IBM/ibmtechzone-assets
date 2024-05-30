# LLM With Google Search Demo

This project combines IBM Watson's large language model (LLM) capabilities with Google Search results to provide comprehensive responses. The application is built using Streamlit, making it easy to deploy and use in a web interface.

## Features

- Integration with IBM WatsonX API to utilize a large language model.
- Integration with Google Custom Search API to fetch search results.
- Streamlit interface for user interaction.
- Configurable settings via a `config.py` file.

## Prerequisites

- Python 3.7 or higher
- Streamlit
- IBM Watson Machine Learning credentials
- Google Custom Search API credentials

## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/your-username/llm-google-search-demo.git
    cd llm-google-search-demo
    ```

2. **Create a virtual environment and activate it:**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages:**

    ```sh
    pip install -r requirements.txt
    ```

4. **Set up configuration:**

    Create a file named `config.py` in the project directory and add the following content:

    ```python
    # config.py

    WATSONX_URL = "https://us-south.ml.cloud.ibm.com"
    WATSONX_API_KEY = "<YOUR_IBM_WATSON_API_KEY>"
    WATSONX_MODEL_ID = "meta-llama/llama-2-70b-chat"
    WATSONX_PARAMETERS = {
        "decoding_method": "greedy",
        "max_new_tokens": 200,
        "repetition_penalty": 1
    }
    WATSONX_PROJECT_ID = "<PROJECT_ID>"
    WATSONX_SPACE_ID = None  # Replace with actual space ID if needed

    GOOGLE_API_KEY = "<YOUR_GOOGLE_API_KEY>"
    GOOGLE_ENGINE_ID = "<YOUR_GOOGLE_ENGINE_ID>"
    ```

    Replace `<YOUR_IBM_WATSON_API_KEY>` and `<YOUR_GOOGLE_API_KEY>` with your actual API keys.

## Usage

1. **Run the Streamlit app:**

    ```sh
    streamlit run app.py
    ```

2. **Open your web browser and go to:**

    ```
    http://localhost:8501
    ```

3. **Enter your query in the input box and click "Submit" to get a response.**

## File Structure

- `app.py`: The main Streamlit application file.
- `config.py`: Configuration file for API keys and other parameters.
- `requirements.txt`: Python dependencies.

## Additional Notes

- Ensure you have valid API keys for both IBM Watson and Google Custom Search.
- Customize the Streamlit interface and parameters as needed in `app.py` and `config.py`.
