import os
#Import Faker
from faker import Faker

# How many fake customer records do you want
NUM_RECORDS = os.environ["num_records"]

#Create faker object
fake = Faker()

for x in range(NUM_RECORDS):
  #Print dummy data
  print("Name:", fake.name())
  print("Email:", fake.email())
  print("Address:", fake.address())
  print("Country:", fake.country())
  print("URL:", fake.url())
