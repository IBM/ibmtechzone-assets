import os
from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.retrievers.document_compressors import DocumentCompressorPipeline
from langchain.retrievers import ContextualCompressionRetriever
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.document_transformers import EmbeddingsRedundantFilter
from langchain.retrievers.document_compressors import EmbeddingsFilter

import logging.config
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
})

import warnings
warnings.filterwarnings("ignore")


## inputs
CONTEXT = os.environ["context"]
QUERY = os.environ["query"]

is_context_file = 0
if CONTEXT == '' and QUERY == '':
    CONTEXT = """Generative artificial intelligence (generative AI, GenAI, or GAI) is artificial intelligence capable of generating text, images, videos, or other data using generative models, often in response to prompts. Generative AI models learn the patterns and structure of their input training data and then generate new data that has similar characteristics.
Improvements in transformer-based deep neural networks, particularly large language models (LLMs), enabled an AI boom of generative AI systems in the early 2020s. These include chatbots such as ChatGPT, Copilot, Gemini and LLaMA, text-to-image artificial intelligence image generation systems such as Stable Diffusion, Midjourney and DALL-E, and text-to-video AI generators such as Sora. Companies such as OpenAI, Anthropic, Microsoft, Google, and Baidu as well as numerous smaller firms have developed generative AI models.
Generative AI has uses across a wide range of industries, including software development, healthcare, finance, entertainment, customer service, sales and marketing, art, writing, fashion, and product design. However, concerns have been raised about the potential misuse of generative AI such as cybercrime, the use of fake news or deepfakes to deceive or manipulate people, and the mass replacement of human jobs"""
    QUERY = "What is GenAI?"

elif os.path.isfile(CONTEXT):
    CONTEXT = TextLoader(CONTEXT).load()
    is_context_file = 1


## process data
text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=25)
if is_context_file:
    data = text_splitter.split_documents(CONTEXT)
else:
    data = [Document(page_content=x) for x in text_splitter.split_text(CONTEXT)]


## Helper function for printing docs
def pretty_print_docs(docs):
    print(
        f"\n{'-' * 100}\n".join(
            [f"Document {i+1}:  " + d.page_content for i, d in enumerate(docs)]
        )
    )

################################# Execute #######################################
# initialize embedding model
embeddings_model = HuggingFaceBgeEmbeddings()

# vector store and base retriever
vectorstore = FAISS.from_documents(data, embeddings_model)
b_retriever = vectorstore.as_retriever(search_kwargs={"k": 3}, verbose=False)

docs = b_retriever.get_relevant_documents(QUERY)

pretty_print_docs(docs)
print("\n\n{}\n\n".format('='*100))

# contextual compression
''' TODO :: allow different methods
def compression_retriever(method='DocumentCompressorPipeline', retriever=None, embeddings=None, llm=None):
    
    if method == 'LLMChainExtractor':
        
        compressor = LLMChainExtractor.from_llm(llm)
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=retriever
        )
        return compression_retriever
    
    elif method == 'EmbeddingsFilter':
        embeddings = HuggingFaceBgeEmbeddings()
        embeddings = embeddings
        embeddings_filter = EmbeddingsFilter(embeddings=embeddings, similarity_threshold=0.76)
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=embeddings_filter, base_retriever=retriever
        )
        return compression_retriever

    elif method == 'DocumentCompressorPipeline':

        embeddings = HuggingFaceBgeEmbeddings() #embeddings #
        splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0, separator=". ")
        redundant_filter = EmbeddingsRedundantFilter(embeddings=embeddings)
        relevant_filter = EmbeddingsFilter(embeddings=embeddings, similarity_threshold=0.76)
        pipeline_compressor = DocumentCompressorPipeline(
            transformers=[splitter, redundant_filter, relevant_filter]
        )

        compression_retriever = ContextualCompressionRetriever(
            base_compressor=pipeline_compressor, base_retriever=retriever
        )
        return compression_retriever
    
    else:  #LLMLingua

        node_postprocessor = LongLLMLinguaPostprocessor(
            model_name='NousResearch/Llama-2-7b-hf', #'NousResearch/Nous-Hermes-2-Mixtral-8x7B-SFT',
            device_map='cpu',
            instruction_str="Given the context, please answer the final question",
            target_token=300,
            rank_method="longllmlingua",
            additional_compress_kwargs={
                "condition_compare": True,
                "condition_in_question": "after",
                "context_budget": "+100",
                "reorder_context": "sort",  # enable document reorder,
                "dynamic_context_compression_ratio": 0.3,
            },
        )
        return node_postprocessor
'''
    
splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0, separator=". ")
redundant_filter = EmbeddingsRedundantFilter(embeddings=embeddings_model)
relevant_filter = EmbeddingsFilter(embeddings=embeddings_model, similarity_threshold=0.76)
pipeline_compressor = DocumentCompressorPipeline(
    transformers=[splitter, redundant_filter, relevant_filter]
)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=pipeline_compressor, base_retriever=b_retriever
)

compressed_docs = compression_retriever.get_relevant_documents(QUERY)[:6]

pretty_print_docs(compressed_docs)
print("\n\n{}\n\n".format('='*100))

# compression comparision
original_contexts_len = len("\n\n".join([d.page_content for i, d in enumerate(docs)]))
compressed_contexts_len = len("\n\n".join([d.page_content for i, d in enumerate(compressed_docs)]))

print("Original context length:", original_contexts_len)
print("Compressed context length:", compressed_contexts_len)
print("Compressed Ratio:", f"{original_contexts_len/(compressed_contexts_len + 1e-5):.2f}x")

# for more details, please do refer to this git repo: https://github.ibm.com/Sourav-Verma/Contextual-Compression

