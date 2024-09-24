import os
from elasticsearch import Elasticsearch
from langchain_community.vectorstores.elasticsearch import ElasticsearchStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ibm import WatsonxLLM

class LLMQueryProcessor:
    def __init__(self, es_url, es_user, es_password, es_index, watsonx_api_key, project_id):
        self.es_url = es_url
        self.es_user = es_user
        self.es_password = es_password
        self.es_index = es_index
        self.watsonx_api_key = watsonx_api_key
        self.project_id = project_id
        self.embeddings_model = self._initialize_embeddings_model()
        self.es_connection = self._initialize_elasticsearch_connection()
        self.elastic_vector_search = self._initialize_vector_search()

    def _initialize_embeddings_model(self):
        model_kwargs = {'device': 'cpu'}
        return HuggingFaceEmbeddings(
            model_name="intfloat/multilingual-e5-base",
            model_kwargs=model_kwargs
        )

    def _initialize_elasticsearch_connection(self):
        return Elasticsearch(
            [self.es_url],
            basic_auth=(self.es_user, self.es_password),
            verify_certs=False
        )

    def _initialize_vector_search(self):
        return ElasticsearchStore(
            es_connection=self.es_connection,
            index_name=self.es_index,
            embedding=self.embeddings_model
        )

    def get_llm_response(self, llm_query, source_path):
        full_source_path = f"src/data/{source_path}"
        filter_query = [{"term": {"metadata.source.keyword": f"{full_source_path}"}}]

        # Search for similar documents using the query
        similar_docs = self.elastic_vector_search.similarity_search(llm_query, k=10, filter=filter_query)

        # Prepare the context from the retrieved documents
        context = self._prepare_context(similar_docs)

        # Generate the LLM prompt
        prompt = self._make_prompt(context, llm_query)

        # Set environment variables for Watsonx API key
        os.environ["WATSONX_APIKEY"] = self.watsonx_api_key

        # Define LLM parameters
        parameters = {
            "decoding_method": "sample",
            "min_new_tokens": 50,
            "max_new_tokens": 1500,
            "stop_sequences": ["#"],
            "temperature": 0.7,
            "repetition_penalty": 1
        }

        # Create Watsonx LLM client and get the response
        watsonx_llm = WatsonxLLM(
            model_id="meta-llama/llama-3-70b-instruct",
            url="https://us-south.ml.cloud.ibm.com",
            project_id=self.project_id,
            params=parameters
        )

        return watsonx_llm.invoke(prompt)

    def _prepare_context(self, similar_docs):
        # Create context from similar documents
        texts = [
            f"From {doc.metadata['source']}, Page {doc.metadata['page'] + 1}: {doc.page_content}"
            for doc in similar_docs
        ]
        return "\n\n".join(texts)

    def _make_prompt(self, context, query):
        prompt = (
            """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
            <|eot_id|><|start_header_id|>user<|end_header_id|>
            Context: """ + context + " Question: " + query + 
            "<|eot_id|><|start_header_id|>assistant<|end_header_id|> Answer: "
        )
        return prompt


if __name__ == "__main__":
    # Instantiate the class with appropriate credentials and settings
    processor = LLMQueryProcessor(
        es_url="https://your-elasticsearch-url",
        es_user="your-es-username",
        es_password="your-es-password",
        es_index="your-es-index",
        watsonx_api_key="your-watsonx-api-key",
        project_id="your-project-id"

       

    )

    # Get LLM response based on a query and source path
    response = processor.get_llm_response("question?", "abc.pdf")
    print(response)
