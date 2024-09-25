from pymilvus import Collection, connections, utility, AnnSearchRequest, RRFRanker, WeightedRanker
from sentence_transformers import SentenceTransformer
import time 
def query_milvus_multimodal(query, sub_product_group, num_results, img_weight=0.2, desc_weight=0.1, generated_query_weight=0.7, milvus_creds):
    host, port, password = milvus_creds['host'], milvus_creds['port'], milvus_creds['password']
    connections.connect(
            host=host,
            port=port,
            secure=True,
            user="ibmlhapikey",
            password=password)
    

    print("Predicted sub group:", sub_product_group, file=sys.stdout)

    expr = f'SubProductGroup in {json.dumps(sub_product_group)}'
         
    model = SentenceTransformer('intfloat/multilingual-e5-large')  # 384 dim model
    text_model_clip = SentenceTransformer('sentence-transformers/clip-ViT-B-32-multilingual-v1')
    
    search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
    num_results = 50

    start_time = time.time()
    query_text_embeddings_e5 = model.encode([query])
    print("Time taken to generate text embeddings using e5-large: ", time.time() - start_time, file=sys.stdout)


    start_time = time.time()
    query_text_embeddings_clip = text_model_clip.encode([query])
    print("Time taken to generate text embeddings using clip model: ", time.time() - start_time, file=sys.stdout)

    
    req_list = []

    search_param_e5 = {
        "data": query_text_embeddings_e5,
        "anns_field": "prod_desc_embeddings",
        "param": search_params,
        "limit": num_results,
        "expr": expr
    }
    req_e5 = AnnSearchRequest(**search_param_e5)
    req_list.append(req_e5)

    search_param_clip = {
        "data": query_text_embeddings_e5,
        "anns_field": "embeddings",
        "param": search_params,
        "limit": num_results,
        "expr": expr
    }
    req_clip = AnnSearchRequest(**search_param_clip)
    req_list.append(req_clip)

    search_param_image = {
        "data": query_text_embeddings_clip,  
        "anns_field": "image_embeddings",
        "param": search_params,
        "limit": num_results,
        "expr": expr
    }
    req_image = AnnSearchRequest(**search_param_image)
    req_list.append(req_image)

    weights = [desc_weight, generated_query_weight, img_weight]
    # Perform hybrid search using WeightedRanker
    print("\n=== Hybrid Search with WeightedRanker ===", file=sys.stdout)


    start_time = time.time()
    hybrid_res = ellos_collection.hybrid_search(req_list, WeightedRanker(*weights), num_results, output_fields=['ArticleColorId', 'GeneratedQueries', 'ProductDisplayDescription'])
    print("Time taken for hybrid semantic search: ", time.time() - start_time, file=sys.stdout)

    
    return hybrid_res
