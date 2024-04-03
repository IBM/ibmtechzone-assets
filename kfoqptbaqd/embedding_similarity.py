from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_similarity(expected_answers, llm_answers):
    expected_embeddings = model.encode(expected_answers, convert_to_tensor=True)
    llm_embeddings = model.encode(llm_answers, convert_to_tensor=True)
    similarity_scores = util.pytorch_cos_sim(expected_embeddings, llm_embeddings)
    return similarity_scores.diagonal().tolist()
