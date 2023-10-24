import os
#Import Faker
from faker import Faker

# How many fake customer records do you want
NUM_RECORDS = int(os.environ["num_records"])

#Create faker object
fake = Faker()
f = open("customers.csv", "a")
f.write("Name,Email,Address,Country,URL\n")

for x in range(NUM_RECORDS):
  #Print dummy data
  f.write(fake.name()+","+fake.email()+","+fake.address()+","+fake.country()+","+fake.url()+"\n")
  
f.close()