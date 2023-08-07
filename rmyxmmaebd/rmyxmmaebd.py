from geopy.geocoders import Nominatim
import os
geolocator = Nominatim(user_agent="get_geolocation")
ADDRESS_INFO = os.environ["address_info"]
location = geolocator.geocode(ADDRESS_INFO)
print(location.address)
print((location.latitude, location.longitude))
print(location.raw)