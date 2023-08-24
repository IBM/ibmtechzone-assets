from pyspark.sql import SparkSession
APP_NAME = os.environ["app_name"]

spark = SparkSession.builder.appName(APP_NAME).getOrCreate()
print(spark)
rdd=spark.sparkContext.parallelize([1,2,34,4,2,12])
print("RDD count = "+rdd.count())