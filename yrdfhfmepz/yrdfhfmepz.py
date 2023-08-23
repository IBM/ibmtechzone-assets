import os
#Import Faker
from faker import Faker
import os

# How many fake customer records do you want
NUM_RECORDS = int(os.environ["num_records"])

#Create faker object
fake = Faker()
f = open("democustomer.txt", "a")

for x in range(NUM_RECORDS):
  #Print dummy data
  f.write("Name:"+fake.name())
  f.write("Email:"+fake.email())
  f.write("Address:"+fake.address())
  f.write("Country:"+fake.country())
  f.write("URL:"+fake.url())
  
f.close()