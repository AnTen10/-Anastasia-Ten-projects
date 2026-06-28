from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.window import Window
from pyspark.sql.functions import broadcast

spark = SparkSession.builder \
    .appName("Step3_ZoneVitrina") \
    .getOrCreate()

# Данные
events = spark.read.parquet("/user/dudosaa/data/geo/events/date=*").select(
    F.col("event.message_from").alias("user_id"),
    F.col("event_type"),
    F.to_timestamp(F.col("event.datetime")).alias("datetime"),
    F.col("lat"),
    F.col("lon")
).filter(
    F.col("user_id").isNotNull() &
    F.col("datetime").isNotNull()
)

geo = spark.read.csv(
    "/user/dudosaa/data/geo/geo.csv",
    header=True,
    inferSchema=True,
    sep=";"
).select(
    F.col("lat").alias("geo_lat"),
    F.col("lng").alias("geo_lon"),
    F.trim(F.lower("city")).alias("zone_id")
)

# События с координатами
geo_events = events.filter(
    F.col("lat").isNotNull() &
    F.col("lon").isNotNull()
)

# Расстояние
def haversine(lat1, lon1, lat2, lon2):
    r = 6371
    return 2 * r * F.asin(
        F.sqrt(
            F.pow(F.sin((F.radians(lat2) - F.radians(lat1)) / 2), 2) +
            F.cos(F.radians(lat1)) *
            F.cos(F.radians(lat2)) *
            F.pow(F.sin((F.radians(lon2) - F.radians(lon1)) / 2), 2)
        )
    )

# Город
geo_join = geo_events.crossJoin(broadcast(geo)).withColumn(
    "distance",
    haversine(
        F.col("lat"),
        F.col("lon"),
        F.col("geo_lat"),
        F.col("geo_lon")
    )
)

window_geo = Window.partitionBy(
    "user_id", "datetime", "lat", "lon"
).orderBy("distance")

geo_join = geo_join.withColumn(
    "rn",
    F.row_number().over(window_geo)
).filter("rn = 1").drop("rn", "distance")

# Регистрации
window_user = Window.partitionBy("user_id").orderBy("datetime")

geo_join = geo_join.withColumn(
    "rn_user",
    F.row_number().over(window_user)
).withColumn(
    "is_registration",
    F.when(F.col("rn_user") == 1, 1).otherwise(0)
).drop("rn_user")

# Временные признаки
geo_join = geo_join.withColumn(
    "month",
    F.date_trunc("month", "datetime")
).withColumn(
    "week",
    F.date_trunc("week", "datetime")
)

# Агрегация
zone_vitrina = geo_join.groupBy("month", "week", "zone_id").agg(

    F.count(F.when(F.col("event_type") == "message", 1)).alias("week_message"),
    F.count(F.when(F.col("event_type") == "reaction", 1)).alias("week_reaction"),
    F.count(F.when(F.col("event_type") == "subscription", 1)).alias("week_subscription"),
    F.sum("is_registration").alias("week_user"),

    F.count(F.when(F.col("event_type") == "message", 1)).alias("month_message"),
    F.count(F.when(F.col("event_type") == "reaction", 1)).alias("month_reaction"),
    F.count(F.when(F.col("event_type") == "subscription", 1)).alias("month_subscription"),
    F.sum("is_registration").alias("month_user")
)

# Сохранение
if __name__ == "__main__":
    zone_vitrina.write.mode("overwrite").parquet(
        "/user/dudosaa/data/analytics/zone_vitrina"
    )