from sentence_transformers import SentenceTransformer, util
import pandas as pd

sentence_model = SentenceTransformer("all-MiniLM-L6-v2")

def similarity_score_calculator(gt_value, infer_value):
    ground_truth_embedding = sentence_model.encode(gt_value, convert_to_tensor=True)
    infer_embedding = sentence_model.encode(infer_value, convert_to_tensor=True)
    embedding_based_similarity_score = util.cos_sim(
        ground_truth_embedding, infer_embedding
    )
    return embedding_based_similarity_score[0].item()

def load_ground_truth(text, subsystem):
    file_location = "../ground_truth/Complex_Requirements.xlsx"
    pd_file = pd.read_excel(file_location, sheet_name = "TELECOM")
    index = 0
    try:
        for txt_index in pd_file['Primary Text']:
            if(text[0:30] in txt_index):
                topic = 1
                for topic in range(4):
                    compare_txt = subsystem[0:3].lower()
                    if(compare_txt in pd_file.loc[index,'Subsystem '+str(topic+1)].lower()):
                        pd_file.loc[index,'Child Requirement '+str(topic+1)]
                        return pd_file.loc[index,'Child Requirement '+str(topic+1)]
            else:
                index +=1
    except Exception as err:
        return err
    return


def calculate_sim(text,subsystem,inference):
    grd_truth = load_ground_truth(text,subsystem)
    similarity_score_arr = []
    infer_sentence_list = inference.split(".")
    highlight_text = []
    error_code = 101
    try:
        for infer_text in infer_sentence_list:
            similarity_score = similarity_score_calculator(grd_truth,infer_text)
            similarity_score_arr.append(similarity_score)
        max_similarity_value = max(similarity_score_arr)
        similarity_index = similarity_score_arr.index(max_similarity_value)
        similarity_tuple = (infer_sentence_list[similarity_index],"MATCH "+str(int(max_similarity_value*100))+" %")
        infer_sentence_list[similarity_index] = similarity_tuple
    except Exception as err:
        return error_code, err
    return infer_sentence_list, similarity_score_calculator(grd_truth,inference)