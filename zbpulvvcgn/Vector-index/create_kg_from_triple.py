import json
import shutil
import os
from neo4j import GraphDatabase


URI = "neo4j://localhost"
AUTH = ("neo4j", "your_password")


# Here in we are creating a Knowledge graph given we have a JSON of triples given. Neo4j desktop was used for this implementation. To be able to use the json, the json 
# file should be first imported into the import folder of the KG DB. The JSON contains triples which is in each dict where in the first key is the node label with the value being the 
# name property of that node label, the second key value being the relationship and the 3rd key being the node label and the 3rd key value being the name property of that node label.

def main():
    
    driver = GraphDatabase.driver(URI, auth=AUTH)

    with driver.session(database="neo4j") as session:
        
        # Moving the json file to the import folder for the KG DB of the user. The folder paths would have to be edited to that which is in your system
        
        # Source file path (the JSON file you want to copy)
        source_file_path = os.getcwd() + '/data/triplets_with_source.json'
        # Destination folder path (Neo4j import folder)
        destination_folder_path = '/Users/albint/Library/Application Support/Neo4j Desktop/Application/relate-data/dbmss/dbms-f08056e8-b1f2-49d9-b021-90b5f3c03ae5/import'
        # Copy the JSON file to the Neo4j import folder
        shutil.copy(source_file_path, destination_folder_path)
        
        file_path = "data/triplets_with_source.json"
        with open(file_path, "r") as file:
            data = json.load(file)
        
        # We create nodes and relationship for each triple which is a dict in the JSON
        for item in data:
            keys_list = list(item.keys())
            first_key = keys_list[0]
            second_key = keys_list[2]
            query = f"""MERGE (n1:{first_key} {{name: '{item[first_key]}'}}) MERGE (n2:{second_key} {{name: '{item[second_key]}'}}) MERGE (n1)-[:{item['predicate']}]->(n2)"""
            session.run(query)
        
        
        
        driver.close()
        
        
if __name__ == "__main__":
    main()