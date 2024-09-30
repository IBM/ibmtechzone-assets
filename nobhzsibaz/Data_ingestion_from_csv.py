# Download all required files to folders for custom libraries
# 1) Hive metadata jar
# 2) Hive metadata common jar
# 3) Iceberg jar


!wget https://repo1.maven.org/maven2/org/apache/hive/hive-metastore/2.3.9/hive-metastore-2.3.9-sources.jar -O /home/spark/shared/user-libs/spark2/hive-metastore-2.3.9.jar

!wget https://repo1.maven.org/maven2/org/apache/hive/hive-common/2.3.9/hive-common-2.3.9-sources.jar -O /home/spark/shared/user-libs/spark2/hive-common-2.3.9.jar
        
!wget https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.4_2.12/1.3.1/iceberg-spark-runtime-3.4_2.12-1.3.1.jar -O /home/spark/shared/user-libs/spark2/iceberg-spark-runtime-3.4_2.12-1.3.1.jar

# !wget https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.3_2.12/1.2.1/iceberg-spark-runtime-3.3_2.12-1.2.1-sources.jar -O /home/spark/shared/user-libs/spark2/iceberg-spark-runtime-3.3_2.12-1.2.1.jar

!wget https://watsonx-data-aws-iceberg-tungpt2612.s3.us-east-2.amazonaws.com/f_account.csv -O /tmp/input_data.csv

!ls /home/spark/shared/user-libs/spark2 -lrt

# Function/hack to restart kernel
from IPython.display import display_html
def restartkernel() :
    display_html("<script>Jupyter.notebook.kernel.restart();Jupyter.notebook.execute_cell_range(3,4);</script>",raw=True)

# Restart the kernel so it now recognizes all the custom JARS
restartkernel()

from pyspark.sql import SparkSession

sc_master = sc.master
sc_app=sc.appName
sc.stop()

spark = SparkSession.builder \
.master(sc_master)\
.appName(sc_app) \
.config("spark.sql.catalogImplementation", "hive") \
.config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
.config("spark.sql.iceberg.vectorization.enabled", "false") \
.config("spark.sql.catalog.iceberg_data", "org.apache.iceberg.spark.SparkCatalog") \
.config("spark.sql.catalog.iceberg_data.type", "hive") \
.config("spark.sql.catalog.iceberg_data.uri", "thrift://ibm-lh-lakehouse-hive-metastore-svc.zen.svc.cluster.local:9083") \
.config("spark.hive.metastore.client.auth.mode", "PLAIN") \
.config("spark.hive.metastore.client.plain.username", "tungpt") \
.config("spark.hive.metastore.client.plain.password", "temp4now") \
.config("spark.hive.metastore.use.SSL", "true") \
.config("spark.hive.metastore.truststore.type", "JKS") \
.config("spark.hive.metastore.truststore.path", "file:///opt/ibm/jdk/lib/security/cacerts") \
.config("spark.hive.metastore.truststore.password", "changeit") \
.config("spark.sql.sources.partitionOverwriteMode", "static") \
.config("spark.hadoop.fs.s3a.endpoint", "http://ibm-lh-lakehouse-minio-svc.zen.svc.cluster.local:9000") \
.config("spark.hadoop.fs.s3a.access.key", "4mexponDorfFDf8mFko1acbv") \
.config("spark.hadoop.fs.s3a.secret.key", "covaxxcEmzveiBdCfs0awb3e") \
.config("spark.hadoop.fs.s3a.path.style.access", "true") \
.getOrCreate()

sc = spark.sparkContext
sc.setLogLevel("DEBUG")


from pyspark.sql.types import StringType
import hashlib
from pyspark.sql.functions import udf
spark.udf.register("md5", lambda x: hashlib.md5(x.encode('utf-8')).hexdigest(), StringType())
df_source = spark.sql("""select md5(concat('IP|BB.USER.INFO|', cast(USER_ID as varchar(80)))) as ip_id,
                    'BB.USER.INFO' as src_stm_code,
                    cast(USER_ID as varchar(80)) as unq_id_in_src_stm,
                    user_name AS ip_nm,
                    20240528 as ppn_dt, 
                    'USER' as ip_tp,
                    cast(create_time as date) as crt_dt,
                    date('2024-05-28') as eff_dt, 
                    date('2099-12-31') as end_dt 
                    from iceberg_data.msb_standardized_zone.bb_user_info""");
df_target = spark.sql("select * from iceberg_data.msb_curated_zone.ip");

df_source.createOrReplaceTempView("df_source");
df_target.createOrReplaceTempView("df_target");

from pyspark.sql.functions import col, when
from pyspark.sql import SparkSession

comparison_query = """
SELECT
    df_source.ip_id,
    df_source.src_stm_code,
    df_source.unq_id_in_src_stm as unq_id_in_src_stm,
    df_source.ip_nm AS ip_nm,
    df_source.ppn_dt AS ppn_dt,
    df_source.ip_tp AS ip_tp,
    df_source.crt_dt as crt_dt,
    coalesce(df_target.eff_dt, df_source.eff_dt) as eff_dt,
    df_source.end_dt as end_dt
FROM
    df_source
LEFT JOIN
    df_target 
ON
    df_source.ip_id = df_target.ip_id
and (coalesce(df_source.ip_nm, '-1') <> coalesce(df_target.ip_nm, '-1')
or coalesce(df_source.crt_dt, '-1') <> coalesce(df_target.crt_dt, '-1')
)
""";

comparison_df = spark.sql(comparison_query);

comparison_df.createOrReplaceTempView("comparison_df");

spark.sql ("select * from comparison_df").show();


spark.sql("""insert into iceberg_data.msb_curated_zone.ip (ip_id, src_stm_code,unq_id_in_src_stm,ip_nm, ppn_dt,ip_tp,    crt_dt,             eff_dt,    end_dt) select    ip_id, src_stm_code,unq_id_in_src_stm,ip_nm, ppn_dt,ip_tp,    crt_dt,             eff_dt,    end_dt from comparison_df """).show();

# spark.sql("""merge into iceberg_data.msb_curated_zone.ip using comparison_df on ip.ip_id = comparison_df.ip_id when matched then update set ip.ip_nm = comparison_df.ip_nm
# when not matched then insert *""").show();

spark.sql("select * from iceberg_data.msb_curated_zone.ip").show()