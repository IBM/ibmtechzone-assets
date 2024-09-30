### Sample code to ingest data from datastage to watsonx.data using spark
# Import required libraries
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf

# Variables required to load data
# Add jars files in box folder
BOX_PATH_TO_JARS="https://ibm.box.com/shared/static"
LAKEHOUSE_SOURCE_DATA_FILE="s3a://datastage-output-folder/iris.csv"

# Function/hack to restart kernel
from IPython.display import display_html
def restartkernel() :
    display_html("<script>Jupyter.notebook.kernel.restart();Jupyter.notebook.execute_cell_range(4,14);</script>",raw=True)

# Download all required files to folders for custom libraries
# 1) Hive metadata jar
# 2) Hive metadata common jar
# 3) Iceberg jar

# !wget $BOX_PATH_TO_JARS/qrzw8nmct1lzrwm3vzqt059034ierhy2.tgz -O /home/spark/shared/user-libs/spark2/hive-metastore-2.3.9.jar

# !wget $BOX_PATH_TO_JARS/fg5jrgvzrn3buu3haenltx8v5z4q6e7r.tgz -O /home/spark/shared/user-libs/spark2/hive-common-2.3.9.jar
    
# !wget $BOX_PATH_TO_JARS/fks9l5vcltool3iv8wh0on0wnjw5ylr9.tgz -O /home/spark/shared/user-libs/spark2/iceberg-spark-runtime-3.3_2.12-1.2.1.jar

# !wget $LAKEHOUSE_SOURCE_DATA_FILE -O /tmp/input_data.csv

# !ls /home/spark/shared/user-libs/spark2 -lrt

# Variables required to load data
BOX_PATH_TO_JARS="https://ibm.box.com/shared/static"
LAKEHOUSE_HMS_URI='thrift://<YOUR_HMS_ENDPOINT>'
LAKEHOUSE_HMS_PASSWORD="<YOUR_HMS_PASSWORD>"
LAKEHOUSE_S3_ENDPOINT='s3.us-west.cloud-object-storage.test.appdomain.cloud'
LAKEHOUSE_S3_ACCESS_KEY='<YOUR_S3_ACCESS_KEY>'
LAKEHOUSE_S3_SECRET_KEY='<YOUR_S3_SECRET_KEY>'
LAKEHOUSE_SOURCE_DATA_FILE="s3a://datastage-output-folder/iris.csv"
LAKEHOUSE_TARGET_TABLE_NAME="ingest.demo.my_iceberg_table"

# Create/update spark config, the default spark-defaults.conf file will not have specific information about the IBM Lakehouse instance
conf = SparkConf().setAppName("SparkForLakehouse").setMaster("local[*]")\
        .set("spark.hive.metastore.use.SSL", "true")\
        .set("spark.hive.metastore.truststore.type", "JKS")\
        .set("spark.hive.metastore.truststore.path", "file:///opt/ibm/jdk/lib/security/cacerts")\
        .set("spark.hive.metastore.truststore.password", "changeit")\
        .set("spark.sql.catalogImplementation", "hive")\
        .set("spark.sql.extensions","org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")\
        .set("spark.sql.iceberg.vectorization.enabled", "false")\
        .set("spark.sql.catalog.ingest", "org.apache.iceberg.spark.SparkCatalog")\
        .set("spark.sql.catalog.ingest.type", "hive")\
        .set("spark.sql.catalog.ingest.uri", LAKEHOUSE_HMS_URI)\
        .set("spark.hive.metastore.uris",LAKEHOUSE_HMS_URI)\
        .set("spark.hive.metastore.client.auth.mode", "PLAIN")\
        .set("spark.hive.metastore.client.plain.username", "ibmlhapikey")\
        .set("spark.hive.metastore.client.plain.password", LAKEHOUSE_HMS_PASSWORD)\
        .set("spark.hadoop.fs.s3a.bucket.dpak-wxd-storage.endpoint", LAKEHOUSE_S3_ENDPOINT)\
        .set("spark.hadoop.fs.s3a.bucket.dpak-wxd-storage.access.key", LAKEHOUSE_S3_ACCESS_KEY)\
        .set("spark.hadoop.fs.s3a.bucket.dpak-wxd-storage.secret.key ", LAKEHOUSE_S3_SECRET_KEY)\
        .set("spark.hadoop.fs.s3a.bucket.datastage-output-folder.endpoint", LAKEHOUSE_S3_ENDPOINT)\
        .set("spark.hadoop.fs.s3a.bucket.datastage-output-folder.access.key", LAKEHOUSE_S3_ACCESS_KEY)\
        .set("spark.hadoop.fs.s3a.bucket.datastage-output-folder.secret.key ", LAKEHOUSE_S3_SECRET_KEY)

# Update spark config with new details
spark.stop()
spark = SparkSession.builder.config(conf=conf).getOrCreate()

# Display the spark config so we know all changes have taken effect
configurations = spark.sparkContext.getConf().getAll()
for item in configurations: print(item)

# Connect to catalog, schema and display list of tables to test connectivity
spark.sql("use ingest")
spark.sql("use demo")
spark.sql("show tables").show()

# Create data frame with new data file (produced by DataStage)
#input_df = spark.read.option("header",True).csv("/tmp/input_data.csv")
input_df = spark.read.option("header",True).csv(LAKEHOUSE_SOURCE_DATA_FILE)

# Write input data file as a new table in the IBM Lakehouse
input_df.write.saveAsTable(LAKEHOUSE_TARGET_TABLE_NAME,mode="append")

print("Required data copied/saved to the target table in the IBM Lakehouse ! \nCurrent row count in target table below ")

spark.sql("SELECT COUNT(*) FROM " + LAKEHOUSE_TARGET_TABLE_NAME).show()

