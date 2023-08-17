import os
from second import imported_function

print("This was printed in first file!")
imported_function(os.environ["msg"])
