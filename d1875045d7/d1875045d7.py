import os

value1 = os.environ["pre_1"]
value2 = os.environ["pre_2"]

def hello():
  print("hello world!")
  print(value1,value2)

hello()
