# Databricks notebook source
from pyspark.sql import functions as F

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

trips = spark.table("samples.nyctaxi.trips")
daily = trips.groupBy(F.to_date("tpep_pickup_datetime").alias("pickup_date")).agg(
    F.count("*").alias("trips"),
    F.round(F.sum("fare_amount"), 2).alias("total_fare"),
)
daily.write.mode("overwrite").saveAsTable(f"{catalog}.{schema}.trips_daily")
