from sentence_transformers import SentenceTransformer, util
import pandas as pd

sentence_model = SentenceTransformer("all-MiniLM-L6-v2")

# Function to transform sentences into embeddings
def transform_sentences(sentences):
    # Get the embedding for the current sentence
    embedding = sentence_model.encode(sentences, convert_to_tensor=True)

    #return sentence embedding
    return embedding


# Function to calculate the similarity score between two sentences
def similarity_score_calculator(gt_value, infer_value):
    # Generate sentence embeddings for ground truth and inference
    ground_truth_embedding = transform_sentences(gt_value)
    infer_embedding = transform_sentences(infer_value)

    # calculate respective cosine similarity between two sentence embeddings
    embedding_based_similarity_score = util.cos_sim(
        ground_truth_embedding, infer_embedding
    )

    # returning cosine similarity value between two given sentences
    return embedding_based_similarity_score[0].item()


# Highlight the setence within the given text based on higher similarity score
def highlight_similarity(grd_truth,inference):
    # split the entire text into setences array
    infer_sentence_list = inference.split(".")

    # create an empty array for storing similarity text
    similarity_score_arr = []
    
    # iterate each sentence for calculating similarity score and add it to array as tuple value
    try:
        for infer_text in infer_sentence_list:
            similarity_score = similarity_score_calculator(grd_truth,infer_text)
            similarity_score_arr.append(similarity_score)
        max_similarity_value = max(similarity_score_arr)
        similarity_index = similarity_score_arr.index(max_similarity_value)
        similarity_tuple = (infer_sentence_list[similarity_index],"MATCH "+str(int(max_similarity_value*100))+" %")
        infer_sentence_list[similarity_index] = similarity_tuple

    # catch the exception if araised
    except Exception as err:
        return err
    
    # returning sentence similarity highlight with respect to the given sentences
    return infer_sentence_list[:-1]