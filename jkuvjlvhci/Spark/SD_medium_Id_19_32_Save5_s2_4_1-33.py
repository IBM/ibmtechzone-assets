from pyspark.sql import SparkSession
from pyspark.sql.functions import max, col
from pyspark.sql.types import StringType, TimestampNTZType, TimestampType
from inflection import underscore
from functools import reduce
from pyspark.sql import DataFrame
import time

# Initialize Spark session
spark = SparkSession.builder.appName("DataProcessor").getOrCreate()

# Configure log4j logging level
sc = spark.sparkContext
log4jLogger = sc._jvm.org.apache.log4j
log = log4jLogger.LogManager.getLogger(__name__)
log.setLevel(log4jLogger.Level.INFO)


class DataProcessor:
    def __init__(self, spark):
        self.spark = spark

    def read_parquet_data_from_icos(self, uri, read_header=True, infer_schema=True):
        log.info(f"Reading data from Parquet file: {uri}")
        start_time = time.time()
        df = self.spark.read.option("header", read_header).option("inferSchema", infer_schema).parquet(uri)
        end_time = time.time()
        log.info(f"Time taken to read Parquet file: {end_time - start_time:.2f} seconds")
        return df
    
    def transform_data(self, df, symbols:list):
        log.info("Transforming data...")
        start_time = time.time()
        df = df.withColumn("Value", col("Value").cast("double")) \
               .groupBy("Vin", "GPS_TimeStamp_Local", "msec", "DpcCarType", "Latitude", "Longitude") \
               .pivot("Symbol", symbols).max("Value")
        end_time = time.time()
        log.info(f"Time taken to transform data: {end_time - start_time:.2f} seconds")
        return df

    def union_multiple_dataframes(self, dfs):
        log.info("Union multiple DataFrames...")
        start_time = time.time()
        df = reduce(DataFrame.unionAll, dfs)
        end_time = time.time()
        log.info(f"Time taken to union DataFrames: {end_time - start_time:.2f} seconds")
        return df

    def apply_snake_case_column_name(self, df):
        log.info("Applying snake case column names...")
        start_time = time.time()
        rename_dict = {c.name: underscore(c.name) for c in df.schema}
        df = df.selectExpr([f"{c} as {rename_dict.get(c, c)}" for c in df.columns])
        end_time = time.time()
        log.info(f"Time taken to apply snake case column names: {end_time - start_time:.2f} seconds")
        return df

    def cast_timestamp_to_string(self, df):
        log.info("Casting timestamps to string...")
        start_time = time.time()
        for c in df.schema:
            if isinstance(c.dataType, (TimestampNTZType, TimestampType)):
                df = df.withColumn(c.name, df[c.name].cast(StringType()))
        end_time = time.time()
        log.info(f"Time taken to cast timestamps to string: {end_time - start_time:.2f} seconds")
        return df

    def write_tabular_data_to_icos(self, df, output_url, coalesce=1, format="parquet", header=True, mode="overwrite", codec="none"):
        log.info("Writing tabular data...")
        start_time = time.time()
        df\
                .coalesce(coalesce)\
                .write\
                .format(format)\
                .option("header", header)\
                .option("mode", mode)\
                .option("compression", codec)\
                .partitionBy("Vin")\
                .save(output_url)
        end_time = time.time()
        log.info(f"Time taken to write tabular data: {end_time - start_time:.2f} seconds")

    
if __name__ == "__main__":

    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("DataProcessor") \
        .config("spark.hadoop.fs.s3a.bucket.bdpf-jp-pre-poc-data01.endpoint", "https://s3.jp-tok.cloud-object-storage.appdomain.cloud") \
        .config("spark.hadoop.fs.s3a.bucket.bdpf-jp-pre-poc-data01.access.key", "")\
        .config("spark.hadoop.fs.s3a.bucket.bdpf-jp-pre-poc-data01.secret.key", "")\
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()

    # Initialize DataProcessor object
    spark_processor = DataProcessor(spark)
    dataframes = []
    output_url = "s3a://bdpf-jp-pre-poc-data01/Output/SingleDispatchTestcases/medium_transform2/set1/Output_medium_32_DId_19_Save5_s2_set1.parquet"
    list1 = ['']


    # Read data from Parquet file
    for i in range(1, 33):
        uris = f"s3a://bdpf-jp-pre-poc-data01/medium/medium-{str(i).zfill(5)}.parquet"
        df = spark_processor.read_parquet_data_from_icos(uris, read_header=True, infer_schema=True)
        dataframes.append(df)


    combined_df = spark_processor.union_multiple_dataframes(dataframes)

    if combined_df:
        combined_df = spark_processor.transform_data(combined_df,list1)
        # combined_df = spark_processor.postprocess_data(combined_df)
        # combined_df = spark_processor.apply_snake_case_column_name(combined_df)
        # combined_df = spark_processor.cast_timestamp_to_string(combined_df)
        spark_processor.write_tabular_data_to_icos(combined_df, output_url,mode="overwrite")


    # Stop Spark session
    spark.stop()



