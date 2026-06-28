from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_timestamp, unix_timestamp, lit, to_json, struct
from pyspark.sql.types import StructType, StructField, StringType, LongType

# Spark
spark = SparkSession.builder \
    .appName("RestaurantStreamingProject") \
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,"
        "org.postgresql:postgresql:42.6.0"
    ) \
    .config("spark.sql.streaming.stopGracefullyOnShutdown", "true") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# kafka
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers",
            "<kafka-bootstrap-server>") \
    .option("subscribe", "base") \
    .option("kafka.security.protocol", "SASL_SSL") \
    .option("kafka.sasl.mechanism", "SCRAM-SHA-512") \
    .option(
        "kafka.sasl.jaas.config",
        'org.apache.kafka.common.security.scram.ScramLoginModule required '
        'username="<username>" password="<password>";'
    ) \
    .option("kafka.ssl.ca.location", "/project/CA.pem") \
    .load()

kafka_console = kafka_df.selectExpr(
    "CAST(key AS STRING)",
    "CAST(value AS STRING)"
).writeStream \
    .format("console") \
    .outputMode("append") \
    .option("truncate", "false") \
    .start()

# Postgres
jdbc_url = "jdbc:postgresql://<postgres-host>:<port>/<database>"

subscribers_df = spark.read \
    .format("jdbc") \
    .option("url", jdbc_url) \
    .option("dbtable", "subscribers_restaurants") \
    .option("user", "<username>") \
    .option("password", "de-student") \
    .option("password", "<password>") \
    .load()

print("=== SUBSCRIBERS TABLE ===")
subscribers_df.show()

# JSON
schema = StructType([
    StructField("restaurant_id", StringType()),
    StructField("adv_campaign_id", StringType()),
    StructField("adv_campaign_content", StringType()),
    StructField("adv_campaign_owner", StringType()),
    StructField("adv_campaign_owner_contact", StringType()),
    StructField("adv_campaign_datetime_start", LongType()),
    StructField("adv_campaign_datetime_end", LongType()),
    StructField("datetime_created", LongType()),
])

json_df = kafka_df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

current_ts = unix_timestamp(current_timestamp())

filtered_df = json_df.filter(
    (col("adv_campaign_datetime_start") <= current_ts) &
    (col("adv_campaign_datetime_end") >= current_ts)
)

filtered_console = filtered_df.writeStream \
    .format("console") \
    .outputMode("append") \
    .start()

# JOIN
joined_df = filtered_df.join(subscribers_df, "restaurant_id")

result_df = joined_df.withColumn(
    "trigger_datetime_created",
    unix_timestamp(current_timestamp())
)

def foreach_batch_function(df, epoch_id):

    if df.rdd.isEmpty():
        return

    # кешируем
    df.cache()

    # Postgres
    df_pg = df.withColumn("feedback", lit(None).cast("string"))

    df_pg.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://localhost:5432/de") \
        .option("dbtable", "subscribers_feedback") \
        .option("user", "jovyan") \
        .option("password", "jovyan") \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()

    # Kafka
    kafka_out = df.select(
        to_json(struct(
            col("restaurant_id"),
            col("adv_campaign_id"),
            col("adv_campaign_content"),
            col("adv_campaign_owner"),
            col("adv_campaign_owner_contact"),
            col("adv_campaign_datetime_start"),
            col("adv_campaign_datetime_end"),
            col("datetime_created"),
            col("client_id"),
            col("trigger_datetime_created")
        )).alias("value")
    )

    kafka_out.write \
        .format("kafka") \
        .option("kafka.bootstrap.servers",
                "<kafka-bootstrap-server>") \
        .option("topic", "base_out") \
        .option("kafka.security.protocol", "SASL_SSL") \
        .option("kafka.sasl.mechanism", "SCRAM-SHA-512") \
        .option(
            "kafka.sasl.jaas.config",
            'org.apache.kafka.common.security.scram.ScramLoginModule required '
            'username="<username>" password="<password>";'
        ) \
        .option("kafka.ssl.ca.location", "/project/CA.pem") \
        .save()

    # очистка памяти
    df.unpersist()

query_main = result_df.writeStream \
    .foreachBatch(foreach_batch_function) \
    .option("checkpointLocation", "/tmp/checkpoints_restaurants") \
    .start()

query_main.awaitTermination()