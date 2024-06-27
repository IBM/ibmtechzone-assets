import json
import os
from neo4j import GraphDatabase
import requests
import zipfile

URI = os.environ["neo4j_uri"]
username = os.environ["neo4j_username"]
pwd = os.environ["neo4j_pwd"]
DATABASE = os.environ["database"]
print(username, pwd, "authenticationnn")

AUTH = (username, pwd)
# URI = "neo4j://localhost"
# AUTH = ("neo4j", "your_password")
# DATABASE = "neo4j"

            
# Here in we are creating a Knowledge graph given we have a JSON of triples given. Neo4j desktop was used for this implementation. To be able to use the json, the json 
# file should be first imported into the import folder of the KG DB. The JSON contains triples which is in each dict where in the first key is the node label with the value being the 
# name property of that node label, the second key value being the relationship and the 3rd key being the node label and the 3rd key value being the name property of that node label.

def main():
    
    # The following part is to download a file from a given url
    # Define the URL to download
    wget_url = os.environ["file_path"]
    # Create the 'data' directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Change the current working directory to 'data'
    os.chdir('data')

    # Get the current working directory
    CWD = os.getcwd()

    # Download the file from the URL
    response = requests.get(wget_url)
    file_name = wget_url.split('/')[-1]
    file_path = os.path.join(CWD, file_name)

    # Write the downloaded content to a file
    with open(file_path, 'wb') as file:
        file.write(response.content)

    # Iterate through all files in the current working directory
    for file in os.listdir(CWD):
        if file.endswith('.zip'):
            # Unzip the file
            with zipfile.ZipFile(file, 'r') as zip_ref:
                zip_ref.extractall(CWD)
    
    driver = GraphDatabase.driver(URI, auth=AUTH)

    with driver.session(database=DATABASE) as session:
    

        with open(file_path, "rb") as file:
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