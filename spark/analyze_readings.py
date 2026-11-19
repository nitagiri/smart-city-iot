
import json
import os
import ssl
import urllib.request

from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, count, round as spark_round

API_URL = "https://10.10.2.2:8000/readings?limit=10000"
API_KEY = os.environ["SENSOR_API_KEY"]
CERT_FILE = "/certs/server.crt"

# Retrieve sensor data securely through FastAPI.
context = ssl.create_default_context(cafile=CERT_FILE)

request = urllib.request.Request(
    API_URL,
    headers={"X-API-Key": API_KEY}
)

with urllib.request.urlopen(
    request, context=context, timeout=30
) as response:
    payload = json.load(response)

readings = payload["readings"]

if not readings:
    raise RuntimeError("No sensor readings returned by API")

spark = (
    SparkSession.builder
    .appName("SmartCitySensorAnalysis")
    .master("spark://spark-master:7077")
    .getOrCreate()
)

try:
    # Parallelize readings across the two Spark workers.
    rdd = spark.sparkContext.parallelize(readings, 2)
    df = spark.createDataFrame(rdd)

    df.createOrReplaceTempView("sensor_readings")

    result = spark.sql("""
        SELECT
            sensor_id,
            COUNT(*) AS reading_count,
            ROUND(AVG(temperature), 2) AS avg_temperature,
            ROUND(AVG(humidity), 2) AS avg_humidity,
            ROUND(AVG(light), 2) AS avg_light,
            ROUND(AVG(voltage), 3) AS avg_voltage
        FROM sensor_readings
        GROUP BY sensor_id
        ORDER BY sensor_id
    """)

    print("\nSMART CITY SENSOR ANALYSIS")
    result.show(100, truncate=False)

    print("Total readings analyzed:", df.count())

finally:
    spark.stop()
