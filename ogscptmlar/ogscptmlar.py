import base64 
import configparser
config = configparser.ConfigParser()

string_to_encode = os.environ["username"]+":"+os.environ["apikey"]
string_to_encode_bytes = string_to_encode.encode("ascii") 
  
base64_bytes = base64.b64encode(string_to_encode_bytes) 
base64_string = base64_bytes.decode("ascii") 
config['CP4D'] = {'TOKEN': base64_string}
