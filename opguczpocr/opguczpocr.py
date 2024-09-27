import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def create_embedding(text, model):
    """
    Generate embeddings for the given text using the SentenceTransformer model.
    """
    return model.encode(text)

def create_embeddings(data, model, weights):
    """
    Create embeddings for a set of data using the provided model and weights.
    
    Args:
        data (dict): Dictionary where keys are the data labels and values are dictionaries of items to embed.
        model (SentenceTransformer): Pre-trained SentenceTransformer model for embedding generation.
        weights (dict): Dictionary of weights for each section of the data.
    
    Returns:
        dict: Dictionary of embeddings with applied weights.
    """
    embeddings = {}
    for key, item in data.items():
        weight = weights.get(key, 1.0)  # Default weight is 1.0 if not specified
        embeddings[key] = weight * create_embedding(" ".join(map(str, item.values())), model)
    return embeddings

def create_faiss_index(embeddings):
    """
    Create a Faiss index and add normalized embeddings to it.
    
    Args:
        embeddings (dict): Dictionary of embeddings to be added to the FAISS index.
    
    Returns:
        faiss.IndexFlatL2: A Faiss index with the normalized embeddings added.
    """
    dimension = list(embeddings.values())[0].shape[0]
    index = faiss.IndexFlatL2(dimension)

    embedding_array = np.array(list(embeddings.values()))
    faiss.normalize_L2(embedding_array)
    index.add(embedding_array)

    return index

def find_relevant_entries(query_embedding, index, k=5):
    """
    Find the k nearest neighbors in the Faiss index for a given query embedding.
    
    Args:
        query_embedding (np.array): The query embedding for which neighbors are to be found.
        index (faiss.IndexFlatL2): The Faiss index to search in.
        k (int): Number of nearest neighbors to return.
    
    Returns:
        list: List of indices of the most similar entries in the index.
    """
    _, idx = index.search(np.array([query_embedding]), k)
    return idx[0]

def calculate_similarity_score(query_embedding, target_embedding):
    """
    Calculate the similarity score (Euclidean distance) between two embeddings.
    
    Args:
        query_embedding (np.array): Embedding of the query.
        target_embedding (np.array): Embedding of the target.
    
    Returns:
        float: Euclidean distance between the two embeddings.
    """
    return np.linalg.norm(np.abs(np.subtract(query_embedding, target_embedding)))

def process_data(query_data, target_data, model, weights, k=5):
    """
    Process query and target data to find the most relevant matches based on similarity scores.
    
    Args:
        query_data (dict): Data for which similar items are to be found.
        target_data (list): List of dictionaries representing the target items (e.g., resumes).
        model (SentenceTransformer): Pre-trained embedding model.
        weights (dict): Dictionary of weights for sections of the data.
        k (int): Number of top results to return.
    
    Returns:
        list: List of dictionaries containing the most relevant items and their similarity scores.
    """
    query_embeddings = create_embeddings(query_data, model, weights)
    target_embeddings = create_embeddings({item['Name']: item for item in target_data}, model, weights)

    # Create Faiss index
    faiss_index = create_faiss_index(target_embeddings)

    # Perform similarity search for the query
    similar_entries_indices = find_relevant_entries(query_embeddings[list(query_data.keys())[0]], faiss_index, k)

    # Collect the most relevant entries and their similarity scores
    most_relevant_entries = []
    for idx in similar_entries_indices:
        if idx == -1:
            most_relevant_entries.append({"Name": "-", "Similarity Score": "-"})
        elif idx < len(target_embeddings):
            name = list(target_embeddings.keys())[idx]
            similarity_score = calculate_similarity_score(query_embeddings[list(query_data.keys())[0]], target_embeddings[name])
            most_relevant_entries.append({"Name": name, "Similarity Score": similarity_score})
        else:
            most_relevant_entries.append({"Name": f"Index {idx} out of range", "Similarity Score": "-"})
    
    return most_relevant_entries

def load_model(model_name='all-MiniLM-L6-v2'):
    """
    Load the SentenceTransformer model.
    
    Args:
        model_name (str): Name of the SentenceTransformer model to load.
    
    Returns:
        SentenceTransformer: Loaded model.
    """
    return SentenceTransformer(model_name)

def export_results(results, output_format="json"):
    """
    Export the results in the specified format.
    
    Args:
        results (list): List of dictionaries containing the results.
        output_format (str): The format in which to export results (e.g., 'json', 'csv').
    
    Returns:
        None
    """
    # Convert numpy float32 to native Python float
    def convert_numpy_floats(obj):
        if isinstance(obj, np.float32):
            return float(obj)
        if isinstance(obj, dict):
            return {k: convert_numpy_floats(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert_numpy_floats(i) for i in obj]
        return obj

    results = convert_numpy_floats(results)

    if output_format == "json":
        import json
        with open("results.json", "w") as f:
            json.dump(results, f)
    elif output_format == "csv":
        import csv
        keys = results[0].keys()
        with open("results.csv", "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)


def main(job_description, resumes, weights, model_name='all-MiniLM-L6-v2', output_format="json", k=5):
    """
    Main function to process job descriptions and resumes, find relevant matches, and export results.
    
    Args:
        job_description (dict): Dictionary containing job description data.
        resumes (list): List of dictionaries containing resume data.
        weights (dict): Weights to apply to different sections of the data.
        model_name (str): Name of the SentenceTransformer model to use for embedding generation.
        output_format (str): Format for exporting results ('json', 'csv').
        k (int): Number of top results to return.
    
    Returns:
        None
    """
    # Load the model
    model = load_model(model_name)

    # Process job description and resumes
    relevant_resumes = process_data(job_description, resumes, model, weights, k)

    # Export results
    export_results(relevant_resumes, output_format)
    print("Results exported successfully.")

# Example usage
if __name__ == "__main__":
    # Example input data
    job_description = {
        "required_skills": {"technical_skills": ["python", "java"], "education": ["Bachelors degree in CS"]},
        "Years_of_Experience": {"total_years_experience": 3},
    }

    resumes = [
        {"Name": "John", "technical_skills": {"programming_languages": ["python", "java"]}, "Years_of_Experience": {"total_years_experience": 3}},
        {"Name": "Jane", "technical_skills": {"programming_languages": ["java"]}, "Years_of_Experience": {"total_years_experience": 5}},
    ]

    # Assign weights
    weights = {"required_skills": 2.0, "Years_of_Experience": 1.5}

    # Run main function
    main(job_description, resumes, weights, output_format="json", k=3)
