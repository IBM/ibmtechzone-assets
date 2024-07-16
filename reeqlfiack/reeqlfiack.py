# SingleStore_Wrapper.py
import struct
import numpy as np
from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer
from uuid import uuid4
from backend.secret import connection_user, connection_password, connection_host, connection_port

class SingleStoreWrapper:
    def __init__(self, database_name, embedding_model_name, table_name_for_upload, table_name_for_search, device="cpu"):
        connection_url = f"singlestoredb://{connection_user}:{connection_password}@{connection_host}:{connection_port}"
        self.engine = create_engine(connection_url)
        self.database_name = database_name
        self.database_name_for_search = database_name
        self.table_name_for_upload = table_name_for_upload
        self.table_name_for_search = table_name_for_search
        self.model = self.load_model(embedding_model_name, device)
        #self.create_collection()

    def load_model(self, embedding_model_name, device="cpu"):
        model = SentenceTransformer(embedding_model_name, device=device, trust_remote_code=True)
        model.max_seq_length = 8192
        return model

    def create_collection(self):
        column_name = 'Name_1_Embedding'
        column_name_in_table = 'Name 1'
        with self.engine.connect() as conn:
            #conn.execute(text("CREATE DATABASE IF NOT EXISTS " + self.database_name))
            conn.execute(text(f"USE {self.database_name};"))

            '''
            result = conn.execute(text(f"SELECT `{column_name_in_table}` FROM {self.table_name_for_search}"))  # Replace with your table name
            names = result.fetchall()
            i=0
            for name_row in names:
                name = name_row[0]
                embedding = self.model.encode(name).astype("float32")
                binary_embedding = struct.pack(f'{len(embedding)}f', *embedding)
                print(name)
                #print(name_row)
                #print(binary_embedding)
                conn.execute(text(f"UPDATE {self.table_name_for_search} SET {column_name} = :embedding WHERE `{column_name_in_table}` = :name"), {'embedding': binary_embedding, 'name': name})
            '''
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name_for_upload}(
                    id BIGINT AUTO_INCREMENT,
                    chunk TEXT,
                    chunk_embedding VARBINARY(6144),  # Adjusted data type
                    PRIMARY KEY (id)
                );
            """))

            #conn.execute(text(f"""
            #    ALTER TABLE {self.table_name_for_search} ADD COLUMN {column_name} VARBINARY(6144);
            #"""))

            #conn.execute(text(f"""
            #    CREATE TABLE IF NOT EXISTS {self.table_name_for_search}(
            #        id BIGINT AUTO_INCREMENT,
            #        supplier_name TEXT,
            #        supplier_name_embedding VARBINARY(6144),
            #        payment_term BIGINT,
            #        PRIMARY KEY (id)
            #    );
            #"""))


    def add_object_to_collection_for_upload(self, chunk_content):
        embedding = self.model.encode(chunk_content).astype("float32")
        
        binary_embedding = struct.pack(f'{len(embedding)}f', *embedding)
        with self.engine.connect() as conn:
            conn.execute(text(f"USE {self.database_name};"))
            conn.execute(text(f"""
                INSERT INTO {self.table_name_for_upload} (id, chunk, chunk_embedding)
                VALUES (NULL, :chunk, :chunk_embedding)
            """), {
                'chunk': chunk_content,
                'chunk_embedding': binary_embedding  # Use the binary format directly
            })
    
    '''
    def add_object_to_collection_for_search(self, supplier_Name, Payment_Term):
        #embedding = self.model.encode(supplier_Name).astype("float32")
        
        #binary_embedding = struct.pack(f'{len(embedding)}f', *embedding)
        with self.engine.connect() as conn:
            conn.execute(text(f"USE {self.database_name_for_search};"))
            # Check if the supplier name already exists
            result = conn.execute(text(f"""
            SELECT COUNT(*) FROM {self.table_name_for_search} 
            WHERE supplier_name = :supplier_name
        """), {'supplier_name': supplier_Name}).scalar()

        # Only insert if the supplier name does not exist
            if result == 0:
                conn.execute(text(f"""
                INSERT INTO {self.table_name_for_search} (id, Document_Name, supplier_name, payment_term, Date_Uploaded, Supplier_ID)
                VALUES (NULL, NULL, :supplier_name, :payment_term, NULL, NULL)
            """), {
                'supplier_name': supplier_Name,
                #'supplier_name_embedding': binary_embedding,  # Use the binary format directly,
                'payment_term': Payment_Term
            })'''
    
    def add_object_to_collection_for_search(self, supplier_Name, payment_Term, document_Name):
        with self.engine.connect() as conn:
            conn.execute(text(f"USE {self.database_name_for_search};"))

            conn.execute(text("""
            UPDATE ib_procurement_poc.Contracts
            SET Supplier_Name = :supplier_name, Payment_Terms = :payment_term
            WHERE Document_Name = :document_name
            """), {
            'supplier_name': supplier_Name,
            'payment_term': payment_Term,
            'document_name': document_Name}
            )

    def perform_similarity_search_for_upload(self, query):
        query_embedding = self.model.encode(query).astype("float32")
        binary_embedding = struct.pack(f'{len(query_embedding)}f', *query_embedding)
    
        with self.engine.connect() as conn:
            conn.execute(text(f"USE {self.database_name};"))
            result = conn.execute(text(f"""
                SELECT chunk
                FROM {self.table_name_for_upload}
                ORDER BY DOT_PRODUCT(chunk_embedding, :query_vector) DESC
                LIMIT 3;
            """), {'query_vector': binary_embedding})

            # Correctly accessing the rows in the result set
            chunks = [row[0] for row in result]
        return chunks
    
    '''
    def perform_similarity_search_for_search(self, query):
        query_embedding = self.model.encode(query).astype("float32")
        binary_embedding = struct.pack(f'{len(query_embedding)}f', *query_embedding)

        with self.engine.connect() as conn:
            conn.execute(text(f"USE {self.database_name};"))
            result = conn.execute(text(f"""
                SELECT *
                FROM {self.table_name_for_search}
                ORDER BY DOT_PRODUCT(Name_1_Embedding, :query_vector) DESC
                LIMIT 5;
            """), {'query_vector': binary_embedding})
           # Convert each row to a dictionary with column names as keys
            results = [dict(zip(result.keys(), row)) for row in result]
        return results
    '''


    
    def perform_similarity_search_for_search(self, query):
        query_embedding = self.model.encode(query).astype("float32")
        binary_embedding = struct.pack(f'{len(query_embedding)}f', *query_embedding)

        with self.engine.connect() as conn:
            conn.execute(text(f"USE {self.database_name};"))

            # Set the query vector
            conn.execute(text("""
                SET @query_vec = :query_vector;
            """), {'query_vector': binary_embedding})

            # Perform similarity search using DOT_PRODUCT
            result = conn.execute(text(f"""
                SELECT *,
                    DOT_PRODUCT(Name_1_Embedding, @query_vec) AS sim_score
                FROM {self.table_name_for_search}
                WHERE DOT_PRODUCT(Name_1_Embedding, @query_vec) > :threshold
                ORDER BY sim_score DESC
                LIMIT 10;
            """), {'threshold': 294})

            # Convert each row to a dictionary with column names as keys
            results = [dict(zip(result.keys(), row)) for row in result]
        return results
    
    

    def delete_all_data(self, table_name):
        with self.engine.connect() as conn:
            conn.execute(text(f"USE {self.database_name};"))
            # Using TRUNCATE to remove all records from the specified table.
            conn.execute(text(f"TRUNCATE TABLE {table_name};"))


