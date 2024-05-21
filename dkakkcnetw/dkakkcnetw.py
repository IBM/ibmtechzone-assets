tokenizer = AutoTokenizer.from_pretrained("thenlper/gte-base")
model = AutoModel.from_pretrained("thenlper/gte-base")

def average_pool(last_hidden_states: Tensor,
                attention_mask: Tensor) -> Tensor:
    last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

def gte_rank(df, query):
  """
  This function gives the similarity score for chunks and answer
  """

    # temp_data = pd.DataFrame([(query, doc.page_content, doc.metadata['heading'], doc.metadata['doc_id'], doc.metadata['index']) for doc in docs], columns=['query', 'page_content', 'heading', 'doc_id', 'index'])
    pairs1 = [[df.iloc[i,1], query] for i in range(len(df))]

    for i, input_text in enumerate(pairs1):
        batch_dict = tokenizer(input_text, max_length=512, padding=True, truncation=True, return_tensors='pt')

        outputs = model(**batch_dict)
        embeddings = average_pool(outputs.last_hidden_state, batch_dict['attention_mask'])

        # (Optionally) normalize embeddings
        embeddings = F.normalize(embeddings, p=2, dim=1)
        score = (embeddings[:1] @ embeddings[1:].T) * 100
        df.loc[i, 'Score'] = score.tolist()[0][0]

    
    return df.sort_values('Score', ascending=False).reset_index(drop=True)

# Get the environment details from IBM cloud storage
COS_HMAC_ACCESS_KEY_ID=os.getenv("COS_HMAC_ACCESS_KEY_ID", None)
COS_HMAC_SECRET_ACCESS_KEY=os.getenv("COS_HMAC_SECRET_ACCESS_KEY", None)
COS_ENDPOINT_URL=os.getenv("COS_ENDPOINT_URL", None)
COS_BUCKET=os.getenv("COS_BUCKET", None)


cos_client = ibm_boto3.client(
            service_name = "s3",
            aws_access_key_id = COS_HMAC_ACCESS_KEY_ID,
            aws_secret_access_key = COS_HMAC_SECRET_ACCESS_KEY,
            endpoint_url = COS_ENDPOINT_URL
        )

def get_file_from_cos(key_name: str):
        try:
            bucket_name = COS_BUCKET
            key_name = key_name
            http_method = 'get_object'
            expiration = 3600
            signedUrl = cos_client.generate_presigned_url(http_method, Params={
                                       'Bucket': bucket_name, 'Key': key_name}, ExpiresIn=expiration)
            return(signedUrl)
        except Exception as e:
            return {"error": str(e)}


def get_source_link(df,query):
    # Get the similarity between chunks and answer with a threshold=85. This can be changed based on your requirement
    score_df = gte_rank(df,query)
    filtered_df = score_df[score_df['Score'] > 85]
    if not filtered_df.empty:
        
        pdf_name = score_df['metadata'].iloc[0]['filename']
        page_no = score_df['metadata'].iloc[0]['page_number']
        url =get_file_from_cos(pdf_name)
        link = f"{url}#page={page_no}"
        return f"Source: <a href =\"{link}\">{pdf_name}</a>, Page {page_no}"

    else:
        return ""