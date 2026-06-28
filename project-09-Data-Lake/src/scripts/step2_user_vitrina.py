from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.window import Window
from pyspark.sql.functions import broadcast

spark = SparkSession.builder.appName("Step2_UserVitrina").getOrCreate()

# События
events = spark.read.parquet("/user/dudosaa/data/geo/events/date=*").select(
    F.col("event.message_from").alias("user_id"),
    F.to_timestamp("event.datetime").alias("event_time"),
    F.col("lat"),
    F.col("lon")
).filter(
    F.col("user_id").isNotNull() &
    F.col("event_time").isNotNull() &
    F.col("lat").isNotNull() &
    F.col("lon").isNotNull()
)

# Справочник
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

# Привязка города
geo_join = events.crossJoin(broadcast(geo)).withColumn(
    "distance",
    haversine(
        F.col("lat"),
        F.col("lon"),
        F.col("geo_lat"),
        F.col("geo_lon")
    )
)

window_geo = Window.partitionBy(
    "user_id", "event_time", "lat", "lon"
).orderBy("distance")

geo_events = geo_join.withColumn(
    "rn",
    F.row_number().over(window_geo)
).filter("rn = 1").select(
    "user_id",
    "event_time",
    "zone_id"
)

# Текущий город
window_last = Window.partitionBy("user_id").orderBy(F.col("event_time").desc())

current_city = geo_events.withColumn(
    "rn",
    F.row_number().over(window_last)
).filter("rn = 1").select(
    "user_id",
    F.col("zone_id").alias("current_city"),
    F.col("event_time").alias("local_time")
)

# Домашний город
geo_events_days = geo_events.select(
    "user_id",
    F.to_date("event_time").alias("event_date"),
    "zone_id"
).distinct()

w = Window.partitionBy("user_id").orderBy("event_date")

# Непрерывные даты
geo_events_days = geo_events_days.withColumn(
    "rn",
    F.row_number().over(w)
).withColumn(
    "grp",
    F.date_sub(F.col("event_date"), F.col("rn"))
)

# Длины серий
periods = geo_events_days.groupBy(
    "user_id", "zone_id", "grp"
).agg(
    F.count("*").alias("days"),
    F.min("event_date").alias("start_date"),
    F.max("event_date").alias("end_date")
)

# >= 27 дней
periods_27 = periods.filter(F.col("days") >= 27)

# последняя серия >= 27 дней
window_home = Window.partitionBy("user_id").orderBy(F.col("end_date").desc())

home_city = periods_27.withColumn(
    "rn",
    F.row_number().over(window_home)
).filter("rn = 1").select(
    "user_id",
    F.col("zone_id").alias("home_city")
)

# Путешествия
window_travel = Window.partitionBy("user_id").orderBy("event_time")

travel = geo_events.withColumn(
    "prev_city",
    F.lag("zone_id").over(window_travel)
).withColumn(
    "is_travel",
    F.when(
        (F.col("prev_city").isNotNull()) &
        (F.col("zone_id") != F.col("prev_city")),
        1
    ).otherwise(0)
)

travel_agg = travel.groupBy("user_id").agg(
    F.sum("is_travel").alias("travel_count"),
    F.collect_set("zone_id").alias("travel_array")
)

# Финальная витрина
user_vitrina = current_city \
    .join(home_city, "user_id", "left") \
    .join(travel_agg, "user_id", "left") \
    .withColumn(
        "travel_count",
        F.coalesce(F.col("travel_count"), F.lit(0))
    )

# Сохранение
if __name__ == "__main__":
    user_vitrina.write.mode("overwrite").parquet(
        "/user/dudosaa/data/analytics/users_geo"
    )