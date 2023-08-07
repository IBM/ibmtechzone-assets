from faker import Faker
import os
fake = Faker()
NUMBER_OF_NAMES = int(os.environ["number_of_names"])
for i in range(1,NUMBER_OF_NAMES):
  print(fake.name())
