from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.window import Window

spark = SparkSession.builder.appName("Step4_FriendsVitrina").getOrCreate()

# Чтобы не зависало
spark.conf.set("spark.sql.shuffle.partitions", "200")
spark.conf.set("spark.sql.adaptive.enabled", "true")

events = spark.read.parquet("/user/dudosaa/data/geo/events/date=*")

# Подписки
subscriptions = events.filter(
    F.col("event_type") == "subscription"
).select(
    F.col("event.user").alias("user_id"),
    F.col("event.subscription_channel").alias("channel_id")
).filter(
    F.col("user_id").isNotNull() &
    F.col("channel_id").isNotNull()
).distinct()

channel_sizes = subscriptions.groupBy("channel_id").count()

subscriptions = subscriptions.join(
    channel_sizes.filter(F.col("count") <= 1000),
    "channel_id"
)

subscriptions = subscriptions.repartition("user_id").cache()

# Гео
geo = spark.read.csv(
    "/user/dudosaa/data/geo/geo.csv",
    header=True,
    inferSchema=True,
    sep=";"
).select(
    F.col("lat").alias("geo_lat"),
    F.col("lng").alias("geo_lon"),
    F.trim(F.lower("city")).alias("zone_id")
).filter(F.col("zone_id").isNotNull()).distinct()

# Сообщения
messages = events.select(
    F.col("event.message_from").alias("user_id"),
    F.to_timestamp(F.col("event.datetime")).alias("datetime"),
    "lat",
    "lon"
).filter(
    F.col("user_id").isNotNull() &
    F.col("lat").isNotNull() &
    F.col("lon").isNotNull()
)

# Последняя локация пользователя 
window_user = Window.partitionBy("user_id").orderBy(F.col("datetime").desc())

user_locations = messages.withColumn(
    "rn",
    F.row_number().over(window_user)
).filter("rn = 1").drop("rn").select("user_id", "lat", "lon").distinct()

# Кэшируем
user_locations.cache()
subscriptions.cache()


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

# Гео пользователя 
user_geo = user_locations.crossJoin(F.broadcast(geo)) \
    .filter(
        (F.abs(F.col("lat") - F.col("geo_lat")) < 1) &
        (F.abs(F.col("lon") - F.col("geo_lon")) < 1)
    ) \
    .withColumn(
        "distance",
        haversine("lat", "lon", "geo_lat", "geo_lon")
    )

window_geo = Window.partitionBy("user_id").orderBy("distance")

user_geo = user_geo.withColumn(
    "rn",
    F.row_number().over(window_geo)
).filter("rn = 1").drop("rn").cache()

# Уже взаимодействовавшие 
interactions = events.filter(
    (F.col("event.message_from").isNotNull()) &
    (F.col("event.message_to").isNotNull())
).select(
    F.least("event.message_from", "event.message_to").alias("user_left"),
    F.greatest("event.message_from", "event.message_to").alias("user_right")
).distinct().repartition("user_left")

# Пары
pairs = subscriptions.select("user_id", "channel_id").distinct()

pairs = pairs.alias("u1").join(
    pairs.alias("u2"),
    (F.col("u1.channel_id") == F.col("u2.channel_id")) &
    (F.col("u1.user_id") < F.col("u2.user_id"))
).select(
    F.col("u1.user_id").alias("user_left"),
    F.col("u2.user_id").alias("user_right")
).distinct()

# Расстояние между пользователями
ul = user_locations.alias("ul")
ur = user_locations.alias("ur")

pairs = pairs \
    .join(ul, F.col("user_left") == F.col("ul.user_id")) \
    .join(ur, F.col("user_right") == F.col("ur.user_id")) \
    .withColumn(
        "distance",
        haversine("ul.lat", "ul.lon", "ur.lat", "ur.lon")
    ) \
    .filter(F.col("distance") <= 50)

# Убираем уже общавшихся
pairs = pairs.join(
    interactions,
    ["user_left", "user_right"],
    "left_anti"
)

# Один город
g1 = user_geo.select(
    F.col("user_id").alias("user_left"),
    F.col("zone_id").alias("zone_id_left")
)

g2 = user_geo.select(
    F.col("user_id").alias("user_right"),
    F.col("zone_id").alias("zone_id_right")
)

result = pairs \
    .join(g1, "user_left") \
    .join(g2, "user_right") \
    .filter(
        F.col("zone_id_left").isNotNull() &
        (F.col("zone_id_left") == F.col("zone_id_right"))
    )

# Финальная витрина
result = result.select(
    "user_left",
    "user_right",
    F.current_timestamp().alias("processed_dttm"),
    F.col("zone_id_left").alias("zone_id")
)

# Сохранение 
if __name__ == "__main__":
    result.write.mode("overwrite").parquet(
        "/user/dudosaa/data/analytics/friends_vitrina"
    )