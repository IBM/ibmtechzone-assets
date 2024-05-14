#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#from pymongo import MangoClient
import pymongo
import pandas as pd
client = pymongo.MongoClient('mongodb://user1:user1password@111.22.333.444:12345/users')

database = client["users"]  # Replace your database with your actual database name
collection = database["incident"]


# Retrieve all documents in the collection
cursor = collection.find()

# Convert cursor to list of dictionaries
documents_list = list(cursor)

# Close the MongoDB connection
client.close()

# df = pd.DataFrame(documents_list)

# Normalize the nested documents into flat table (DataFrame)
df = pd.json_normalize(documents_list)

# Print the DataFrame
# print(df)


# Specify the file path to save the CSV file
csv_file_path = "mangodb_output.csv"

# Save DataFrame to CSV
df.to_csv(csv_file_path, index=False)

