import os

value1 = os.environ["pre_requisite_1"]
value2 = os.environ["pre_requisite_2"]

def hello():
  print("Hello from UI")
  print(value1,value2)
  
hello()
