from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession

import os
SOURCE_FILE = os.environ["source_file"]
THRIFT_URL = os.environ["thrift_url"]
IBMLHAPI_KEY = os.environ["ibmlhapi_key"]
ICEBERG_BUCKET = os.environ["iceberg_bucket"]
TARGET_SCHEMA = os.environ["target_schema"]
TARGET_TABLE = os.environ["target_table"]

conf = SparkConf()

# Setting application name
conf.set("spark.app.name", "LakehouseLoader")
conf.set("spark.master", "local[*]")
conf.set("spark.hive.metastore.use.SSL", "true")
conf.set("spark.hive.metastore.truststore.type", "JKS")
conf.set("spark.hive.metastore.truststore.path", "file:///usr/lib/jvm/java-11-openjdk-amd64/lib/security/cacerts")
conf.set("spark.hive.metastore.truststore.password", "changeit")
conf.set("spark.sql.catalogImplementation", "hive")
#conf.set("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
conf.set("spark.sql.iceberg.vectorization.enabled", "false")
conf.set("spark.sql.catalog.lakehouse", "org.apache.iceberg.spark.SparkCatalog")
conf.set("spark.sql.catalog.lakehouse.type", "hive")
conf.set("spark.sql.catalog.lakehouse.uri", THRIFT_URL)
conf.set("spark.hive.metastore.client.auth.mode", "PLAIN")
conf.set("spark.hive.metastore.client.plain.username", "ibmlhapikey")
conf.set("spark.hive.metastore.client.plain.password", IBMLHAPI_KEY)
conf.set("spark.hadoop.fs.s3a.bucket."+ICEBERG_BUCKET+".endpoint", "true")
conf.set("spark.hadoop.fs.s3a.bucket."+ICEBERG_BUCKET+".access.key", "true")
conf.set("spark.hadoop.fs.s3a.bucket."+ICEBERG_BUCKET+".secret.key", "true")
conf.set("spark.jars", "/home/user/iceberg-spark-runtime-3.3_2.12-1.2.1.jar,/home/user/hive-common-2.3.9.jar,/home/user/hive-metastore-2.3.9.jar")

#sc.stop()
sc = SparkContext(conf=conf)
spark = SparkSession.builder.config(conf=conf).getOrCreate()

# ... set other configurations as needed

source_df = spark.read.options(inferSchema='True',delimiter=',', header=True).csv(SOURCE_FILE)
source_df.show(2)
source_df.write.saveAsTable("lakehouse."+TARGET_SCHEMA+"."+TARGET_TABLE,mode="append")
