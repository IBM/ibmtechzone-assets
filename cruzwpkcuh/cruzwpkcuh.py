from typing import List
from transformers import AutoTokenizer,AutoModel, PreTrainedModel,PretrainedConfig
from typing import Dict
import torch
import os
from langchain.schema import Document

def convert_to_probability(similarity_scores):
    # Find the minimum and maximum scores
    min_score = min(similarity_scores)
    max_score = max(similarity_scores)
    
    # Normalize the scores to the range [0, 1]
    div = (max_score - min_score)
    div = 1 if div ==0 else div
    normalized_scores = [(score - min_score) / div for score in similarity_scores]
    
    return normalized_scores

def get_env_var(name):
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Environment variable {name} not found")
    return value

def split_into_paragraphs(text):
    text = text.replace('\\n', '\n')
    # print(text)
    return [para.strip() for para in text.split('\n') if para.strip()]

def create_langchain_documents(paragraphs):
    return [Document(page_content=para) for para in paragraphs]

class Reranker:

    def __init__(self) -> None:
        pass

    def refine_results(self, query, chunks, top_n, thresold=0):

            class ColBERTConfig(PretrainedConfig):
                model_type = "ColBERT"
                bert_model: str
                compression_dim: int = 768
                dropout: float = 0.0
                return_vecs: bool = False
                trainable: bool = True

            class ColBERT(PreTrainedModel):
                """
                ColBERT model from: https://arxiv.org/pdf/2004.12832.pdf
                We use a dot-product instead of cosine per term (slightly better)
                """
                config_class = ColBERTConfig
                base_model_prefix = "bert_model"

                def __init__(self,
                            cfg) -> None:
                    super().__init__(cfg)

                    self.bert_model = AutoModel.from_pretrained(cfg.bert_model)

                    for p in self.bert_model.parameters():
                        p.requires_grad = cfg.trainable

                    self.compressor = torch.nn.Linear(self.bert_model.config.hidden_size, cfg.compression_dim)

                def forward(self,
                            query: Dict[str, torch.LongTensor],
                            document: Dict[str, torch.LongTensor]):

                    query_vecs = self.forward_representation(query)
                    document_vecs = self.forward_representation(document)

                    score = self.forward_aggregation(query_vecs,document_vecs,query["attention_mask"],document["attention_mask"])
                    return score

                def forward_representation(self,
                                        tokens,
                                        sequence_type=None) -> torch.Tensor:

                    vecs = self.bert_model(**tokens)[0] # assuming a distilbert model here
                    vecs = self.compressor(vecs)

                    # if encoding only, zero-out the mask values so we can compress storage
                    if sequence_type == "doc_encode" or sequence_type == "query_encode":
                        vecs = vecs * tokens["tokens"]["mask"].unsqueeze(-1)

                    return vecs

                def forward_aggregation(self,query_vecs, document_vecs,query_mask,document_mask):

                    # create initial term-x-term scores (dot-product)
                    score = torch.bmm(query_vecs, document_vecs.transpose(2,1))

                    # mask out padding on the doc dimension (mask by -1000, because max should not select those, setting it to 0 might select them)
                    exp_mask = document_mask.bool().unsqueeze(1).expand(-1,score.shape[1],-1)
                    score[~exp_mask] = - 10000

                    # max pooling over document dimension
                    score = score.max(-1).values

                    # mask out paddding query values
                    score[~(query_mask.bool())] = 0

                    # sum over query values
                    score = score.sum(-1)

                    return score

            
            tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased") # honestly not sure if that is the best way to go, but it works :)
            model_colbert = ColBERT.from_pretrained("sebastian-hofstaetter/colbert-distilbert-margin_mse-T2-msmarco")
            query_input = tokenizer(query)
            l=[]
            for i,v in enumerate(chunks):
                
                d = tokenizer(v.page_content,return_tensors="pt",truncation=True)
                l.append(d)


            query_input.input_ids += [103] * 8 # [MASK]
            query_input.attention_mask += [1] * 8
            query_input["input_ids"] = torch.LongTensor(query_input.input_ids).unsqueeze(0)
            query_input["attention_mask"] = torch.LongTensor(query_input.attention_mask).unsqueeze(0)


            l1=[]

            for i in l:
            
                score_for_p1 = model_colbert.forward(query_input,i).squeeze(0)
                l1.append(float(score_for_p1))
                
            reranked = sorted(zip([doc_i for doc_i in range(len(chunks))],l1),key=lambda x:-x[1])[:top_n]
            scores_ = [a[1] for a in reranked]
            scores_ = convert_to_probability(scores_)
            print("scores:", scores_)
            reranked_res = [doc_i for i, (doc_i,scores) in enumerate(reranked) if scores_[i] >= thresold]
            return reranked_res
    
if __name__ == "__main__":

    query = get_env_var('query')
    contexts = get_env_var('contexts')
    top_n = int(os.getenv('top_n', '1'))
    threshold = os.getenv('threshold', 0)
    
    # Split contexts into paragraphs
    paragraphs = split_into_paragraphs(contexts)
    # print(paragraphs)
    # Convert paragraphs into langchain documents
    documents = create_langchain_documents(paragraphs)

    ids = Reranker().refine_results(query, documents, top_n=top_n, thresold=threshold)
    for id in ids:
        print(paragraphs[id])