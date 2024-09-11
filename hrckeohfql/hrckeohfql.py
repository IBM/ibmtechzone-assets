import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import os
import re
from dotenv import load_dotenv
load_dotenv()
from sentence_transformers import SentenceTransformer
from pymilvus import(
                    utility,
                    FieldSchema,
                    DataType,
                    Collection,
                    CollectionSchema,
                    connections,
                    )

def Milvus_connect():
    """
        Establishes a secure connection to the Milvus server.

        This function sets up the connection to the Milvus server using specified 
        host, port, user credentials, and secure settings such as SSL certificates. 
        It utilizes environment variables for port configuration and connects to 
        the server using secure communication.

        Parameters:
        -----------
        None

        Returns:
        --------
        connections : pymilvus.Connection
            A Milvus connection object that can be used to interact with the server.

        Side Effects:
        -------------
        - Establishes a connection to the Milvus server.
        - Uses environment variables and secure SSL settings for connection setup.

        Notes:
        ------
        - Ensure that the `MILVUS_PORT` environment variable is set before calling 
        this function.
        - The server's SSL certificate path (`presto.crt`) is required for secure 
        communication.
    """
    # Milvus connection settings
    host            = 'useast.services.cloud.techzone.ibm.com'
    port            = os.getenv("MILVUS_PORT")
    user            = 'ibmlhadmin'
    password        = 'password'
    server_pem_path = 'presto.crt'

    connections.connect(alias='default',
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    server_pem_path=server_pem_path,
                    server_name='watsonxdata',
                    secure=True)
    return connections

def MilvusDB(coll_name):

    """
        Creates a Milvus collection with specified fields and an index.

        This function checks if a collection with the given name already exists in the Milvus database. 
        If the collection exists, it is dropped and a new collection is created with a defined schema.
        The schema includes an auto-generated primary key field (`id`), a text field (`passage`), and 
        a vector field (`ques_vector`). After creating the collection, an index is applied to the 
        `ques_vector` field using the IVF_FLAT algorithm and L2 distance metric.

        Parameters:
        -----------
        coll_name : str
            The name of the collection to be created in Milvus.

        Returns:
        --------
        None

        Side Effects:
        -------------
        - Drops the collection if it already exists.
        - Creates a new collection with the specified schema.
        - Creates an index on the `ques_vector` field using the IVF_FLAT algorithm.
        
        Notes:
        ------
        - The schema includes three fields: 
            1. `id`: Primary key, auto-generated (INT64).
            2. `passage`: Text field with a maximum length of 4096 characters (VARCHAR).
            3. `ques_vector`: 768-dimensional vector field (FLOAT_VECTOR).
        - An index is created on the `ques_vector` field for faster retrieval using the L2 distance metric.
        - Use `utility.list_collections()` to view the list of all collections in the Milvus database.
    """

    # Milvus_connect()

    if utility.has_collection(coll_name):
        utility.drop_collection(coll_name)

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True), # Primary key
        FieldSchema(name="passage", dtype=DataType.VARCHAR, max_length=4096,),
        FieldSchema(name="ques_vector", dtype=DataType.FLOAT_VECTOR, dim=768),
    ]

    schema = CollectionSchema(fields, "passages collection schema")
    coll = Collection(coll_name, schema)

    index_params = {
            'metric_type':'L2',
            'index_type':"IVF_FLAT",
            'params':{"nlist":2048}
    }

    coll.create_index(field_name="ques_vector", index_params=index_params)

    # print(utility.list_collections()) # to get the list of all collections in the MilvuDB

def make_partition(coll_name, partitionName):
    """
        Creates one or more partitions in a specified Milvus collection.

        This function loads a specified collection from Milvus and creates partitions within it.
        If a partition with the specified name(s) already exists, it is dropped and recreated.
        The function processes a list of partition names and either drops and recreates each 
        existing partition or creates it if it doesn't exist.

        Parameters:
        -----------
        coll_name : str
            The name of the collection where partitions will be managed.
        partitionName : list of str
            A list of partition names to be created or recreated in the collection.

        Returns:
        --------
        None

        Side Effects:
        -------------
        - Loads the specified collection from Milvus.
        - Checks if each partition exists in the collection.
        - If a partition exists, it is dropped and recreated; if not, it is created.
        - Prints the list of partitions in the collection after the changes are made.
    """
    
    coll = Collection(coll_name)
    coll.load()

    # print(coll.partitions)

    for item in partitionName:
        if utility.has_partition(partition_name=item, collection_name=coll_name):
            coll.drop_partition(item)
            coll.create_partition(item)
        else:
            coll.create_partition(item)
    print(coll.partitions)

def insert_in_collection(coll_name,chunks):

    """
        Inserts text chunks and their embeddings into a specified Milvus collection.

        This function loads the specified Milvus collection and uses a pre-trained embedding model 
        to generate embeddings for the given text chunks. The text chunks and their corresponding 
        embeddings are then inserted into the collection. After insertion, the collection is flushed 
        to ensure that the data is persisted.

        Parameters:
        -----------
        coll_name : str
            The name of the collection where the data will be inserted.
        chunks : list of str
            A list of text chunks to be inserted into the collection.

        Returns:
        --------
        None

        Side Effects:
        -------------
        - Loads the specified collection from Milvus.
        - Uses a pre-trained SentenceTransformer model to encode the text chunks into embeddings.
        - Inserts the text chunks and embeddings into the collection.
        - Flushes the collection to ensure data persistence.
        - Prints a success message upon successful data insertion.

        Notes:
        ------
        - The embedding model used in this example is 'pkshatech/GLuCoSE-base-ja', which produces 768-dimensional vectors.
    """

    # Load the collection
    coll = Collection(coll_name)
    coll.load()

    # Load your embedding model
    model = SentenceTransformer('pkshatech/GLuCoSE-base-ja') # 768 dim
    passage_embeddings = model.encode(chunks)

    data = [
        chunks,
        passage_embeddings
    ]

    out = coll.insert(data)
    coll.flush()  # Ensures data persistence
    print('Data insertion successfull in collection: ',coll_name)

def insert_in_partition(coll_name,partitionName,chunks):

    """
        Inserts text chunks and their embeddings into a specified partition of a Milvus collection.

        This function loads the specified Milvus collection and uses a pre-trained embedding model 
        to generate embeddings for the given text chunks. The text chunks and their embeddings are 
        then inserted into a specified partition within the collection. After insertion, the partition 
        is flushed to ensure that the data is persisted.

        Parameters:
        -----------
        coll_name : str
            The name of the collection where the data will be inserted.
        partitionName : str
            The name of the partition where the data will be inserted.
        chunks : list of str
            A list of text chunks to be inserted into the partition.

        Returns:
        --------
        None

        Side Effects:
        -------------
        - Loads the specified collection from Milvus.
        - Uses a pre-trained SentenceTransformer model to encode the text chunks into embeddings.
        - Inserts the text chunks and embeddings into the specified partition.
        - Flushes the partition to ensure data persistence.
        - Prints a success message upon successful data insertion into the partition.

        Notes:
        ------
        - The embedding model used in this example is 'pkshatech/GLuCoSE-base-ja-v2', which produces 768-dimensional vectors.
    """

    coll = Collection(coll_name)
    coll.load()

    model = SentenceTransformer('pkshatech/GLuCoSE-base-ja-v2') # 768 dim
    passage_embeddings = model.encode(chunks)

    data = [
        chunks,
        passage_embeddings
    ]

    coll.insert(data,partition_name=partitionName)
    coll.flush()  # Ensures data persistence
    # print('Data inserted successfully in the partition: ',partitionName)

def query_from_collection(query,coll_name):

    """
        Queries a Milvus collection to find the most similar text chunks to a given query.

        This function loads a specified Milvus collection, vectorizes the input query using a pre-trained 
        embedding model, and performs a similarity search to retrieve the top-K most similar text chunks 
        from the collection. The search results are processed to extract and return the relevant text chunks.

        Parameters:
        -----------
        query : str
            The text query for which similar chunks are to be retrieved.
        coll_name : str
            The name of the collection to be queried.

        Returns:
        --------
        list of str
            A list of the most similar text chunks retrieved from the collection.

        Side Effects:
        -------------
        - Loads the specified collection from Milvus.
        - Uses a pre-trained SentenceTransformer model to encode the query into an embedding.
        - Performs a similarity search in the collection based on the query embedding.
        - Releases the collection after the query to free up resources.
        - Extracts and returns the relevant text chunks from the search results.

        Notes:
        ------
        - The embedding model used in this example is 'pkshatech/GLuCoSE-base-ja-v2', which produces 768-dimensional vectors.
        - The search uses the L2 distance metric and a search parameter `nprobe` set to 10.
        - The top-K number of similar chunks to retrieve is set to 3 by default, but this can be adjusted as needed.
        - The output fields specified in the search results include 'passage', which should match the field names in the collection schema.
    """

    top_K = 3 # Change it acording to your top-k chunks that you want from the milvusDB.

    # Load the collection
    coll = Collection(coll_name)
    coll.load()

    # To vectorize query, use the same embedding model.
    model = SentenceTransformer('pkshatech/GLuCoSE-base-ja-v2') # 768 dim
    query_embeddings = model.encode([query])

    # Search
    search_params = {
        "metric_type": "L2", 
        "params": {"nprobe": 10}
    }

    # Perform the search
    results = coll.search(
        data=query_embeddings, 
        anns_field="ques_vector", # From where to annotate/do the similarity search
        param=search_params,
        limit=top_K,
        expr=None, 
        output_fields=['passage'], # if ypu want multiple fields in output, add the columns name in output_fields list.
    )

    # Release the collection after query. You can comment it down if you are doing multiple query in a sequence.
    coll.release()

    relevant_chunks  = []
    for i in range(top_K):
        relevant_chunks.append(re.sub(r"^.*?\. (.*\.).*$",r"\1",results[0][i].entity.get('passage')))

    return relevant_chunks

def query_from_partition(query,coll_name,partitionName):

    """
        Queries a specific partition of a Milvus collection to find the most similar text chunks to a given query.

        This function loads a specified Milvus collection, vectorizes the input query using a pre-trained 
        embedding model, and performs a similarity search within a specified partition of the collection 
        to retrieve the top-K most similar text chunks. The search results are processed to extract and 
        return the relevant text chunks.

        Parameters:
        -----------
        query : str
            The text query for which similar chunks are to be retrieved.
        coll_name : str
            The name of the collection to be queried.
        partitionName : str
            The name of the partition within the collection where the search will be performed.

        Returns:
        --------
        list of str
            A list of the most similar text chunks retrieved from the specified partition.

        Side Effects:
        -------------
        - Loads the specified collection from Milvus.
        - Uses a pre-trained SentenceTransformer model to encode the query into an embedding.
        - Performs a similarity search within the specified partition based on the query embedding.
        - Releases the collection after the query to free up resources.
        - Extracts and returns the relevant text chunks from the search results.

        Notes:
        ------
        - The embedding model used in this example is 'pkshatech/GLuCoSE-base-ja-v2', which produces 768-dimensional vectors.
        - The search uses the L2 distance metric and a search parameter `nprobe` set to 10.
        - The top-K number of similar chunks to retrieve is set to 3 by default, but this can be adjusted as needed.
        - The output fields specified in the search results include 'passage', which should match the field names in the collection schema.
    """

    top_K = 3 # Change it acording to your top-k chunks that you want from the milvusDB.

    # Load the collection
    coll = Collection(coll_name)
    coll.load()

    # To vectorize query, use the same embedding model.
    model = SentenceTransformer('pkshatech/GLuCoSE-base-ja-v2') # 768 dim
    query_embeddings = model.encode([query])

    # Search
    search_params = {
        "metric_type": "L2", 
        "params": {"nprobe": 10}
    }

    # Perform the search
    results = coll.search(
        data=query_embeddings, 
        anns_field="ques_vector", # From where to annotate/do the similarity search
        param=search_params,
        limit=top_K,
        expr=None, 
        partition_names=partitionName,
        output_fields=['passage'], # if ypu want multiple fields in output, add the columns name in output_fields list.
    )

    # Release the collection after query. You can comment it down if you are doing multiple query in a sequence.
    coll.release()

    relevant_chunks  = []
    for i in range(top_K):
        relevant_chunks.append(re.sub(r"^.*?\. (.*\.).*$",r"\1",results[0][i].entity.get('passage')))

    return relevant_chunks

def main():

    """
        Main function to demonstrate the process of setting up a Milvus collection, inserting data, and querying it.

        This function performs the following steps:
        1. Defines a list of question-answer pairs related to Machine Learning.
        2. Concatenates questions and answers into a list of text chunks.
        3. Connects to the Milvus database.
        4. Defines the collection and partition names.
        5. Creates a new Milvus collection with the specified schema.
        6. Creates partitions within the collection.
        7. Inserts the text chunks into the defined partitions.
        8. Performs a similarity search in the partitions based on a query.
        9. Prints the search results.

        Steps:
        -------
        - Initializes a list of question-answer pairs.
        - Prepares the text chunks by combining questions and answers.
        - Connects to Milvus using the `Milvus_connect` function.
        - Retrieves collection and partition names from environment variables.
        - Creates a collection with a predefined schema using `MilvusDB`.
        - Creates partitions within the collection using `make_partition`.
        - Inserts data into the partitions using `insert_in_partition`.
        - Queries the collection to find similar text chunks to a given question using `query_from_partition`.
        - Outputs the results of the query.

        Notes:
        ------
        - Ensure that Milvus and the required environment variables (e.g., `COLLECTION_NAME`) are properly configured.
        - Adjust the `partition_names` and data chunking logic as needed based on your use case.
        - The function `query_from_partition` will search across all specified partitions. To limit the search to a specific partition, modify the `partitionName` parameter.
    """

    qa_list = [
    ["What is Machine Learning?", 
     "Machine Learning is a field of artificial intelligence that focuses on the development of algorithms and statistical models that enable computers to perform tasks without explicit instructions, by learning from data."],
    
    ["What are the types of Machine Learning?", 
     "The three main types of Machine Learning are Supervised Learning, Unsupervised Learning, and Reinforcement Learning."],
    
    ["What is Supervised Learning?", 
     "Supervised Learning is a type of Machine Learning where the algorithm is trained on labeled data. The model learns from the input-output pairs to predict the output for new inputs."],
    
    ["What is Unsupervised Learning?", 
     "Unsupervised Learning is a type of Machine Learning where the algorithm is trained on unlabeled data. The model tries to find hidden patterns or intrinsic structures in the input data."],
    
    ["What is Reinforcement Learning?", 
     "Reinforcement Learning is a type of Machine Learning where an agent learns to make decisions by performing actions and receiving rewards or penalties based on the outcomes of those actions."],
    
    ["What is overfitting in Machine Learning?", 
     "Overfitting occurs when a machine learning model learns not only the underlying pattern in the training data but also the noise or random fluctuations, leading to poor generalization to new data."],
    
    ["What is underfitting in Machine Learning?", 
     "Underfitting occurs when a machine learning model is too simple to capture the underlying pattern in the data, resulting in poor performance on both the training and test data."],
    
    ["What is a neural network?", 
     "A neural network is a computational model inspired by the human brain, consisting of layers of interconnected 'neurons'. These networks are used for tasks like classification, regression, and feature extraction."],
    
    ["What is a decision tree?", 
     "A decision tree is a supervised learning algorithm used for classification and regression. It splits the data into branches based on feature values, leading to a decision or prediction."],
    
    ["What is a confusion matrix?", 
     "A confusion matrix is a table used to evaluate the performance of a classification model by comparing actual labels with predicted labels. It contains True Positives, True Negatives, False Positives, and False Negatives."],
    
    ["What is cross-validation?", 
     "Cross-validation is a technique used to evaluate the performance of a machine learning model. It involves partitioning the data into subsets, training the model on some subsets, and testing it on others to ensure generalization."],
    
    ["What is gradient descent?", 
     "Gradient Descent is an optimization algorithm used to minimize the cost function in machine learning models. It iteratively adjusts the model's parameters in the direction that reduces the error."],
    
    ["What is the difference between classification and regression?", 
     "Classification is the task of predicting a discrete label or category, whereas regression is the task of predicting a continuous value or quantity."],
    
    ["What is feature engineering?", 
     "Feature engineering is the process of creating new features or transforming existing features to improve the performance of machine learning models."],
    
    ["What is regularization?", 
     "Regularization is a technique used to prevent overfitting by adding a penalty to the model's complexity, such as L1 or L2 regularization, which discourages large weights."],
    
    ["What is the bias-variance tradeoff?", 
     "The bias-variance tradeoff refers to the balance between a model's ability to generalize (low bias) and its flexibility (low variance). High bias can lead to underfitting, while high variance can lead to overfitting."],
    
    ["What is the purpose of a learning rate in machine learning?", 
     "The learning rate is a hyperparameter that controls how much the model's parameters are adjusted with respect to the error during each iteration of the training process."],
    
    ["What is a support vector machine (SVM)?", 
     "A Support Vector Machine (SVM) is a supervised learning algorithm used for classification and regression tasks. It works by finding the hyperplane that best separates the data into classes."],
    
    ["What is PCA (Principal Component Analysis)?", 
     "PCA (Principal Component Analysis) is a dimensionality reduction technique that transforms a dataset into a lower-dimensional space by selecting the most important features (principal components)."],
    
    ["What is the difference between bagging and boosting?", 
     "Bagging and boosting are ensemble methods. Bagging reduces variance by training multiple models on different subsets of the data, while boosting reduces bias by sequentially training models, giving more weight to misclassified examples."]
    ]

    all_chunks = [item[0]+item[1] for item in qa_list]

    Milvus_connect()
    # Define collection and partition names.
    collectio_name = os.getenv("COLLECTION_NAME")
    partition_names = ['part1','part2']

    # Create the collection.
    MilvusDB(coll_name=collectio_name)

    # Create the partition in collection.
    make_partition(coll_name=collectio_name, partitionName= partition_names)

    # Data insertion in the partitions.
    insert_in_partition(coll_name=collectio_name, partitionName=partition_names[0],chunks=all_chunks[:len(all_chunks)//2])
    insert_in_partition(coll_name=collectio_name, partitionName=partition_names[1],chunks=all_chunks[len(all_chunks)//2:])


    # Query from the partitions.
    question = 'What is the difference between Reinforcement learnign and Deep learning?'
    # it will search in both partitions. If you want to search from an individual partition, pass that partition name in a list.
    res = query_from_partition(query=question,coll_name=collectio_name,partitionName=partition_names)
    print(res)

if __name__ == "__main__":
    main()