import ast, time, sys
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local").appName("lhloader").getOrCreate()
DATA_FILE_NAME = os.environ["data_file_name"]
df = spark.read.csv(DATA_FILE_NAME)
df.printSchema()
df
