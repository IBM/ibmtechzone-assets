from faker import Factory
COUNTRY_NAME = os.environ["country_name"]
fake = Factory.create(COUNTRY_NAME)
print(fake.street_address())
print(fake.postcode())