from pyspark.sql import SparkSession
from pyspark import SparkContext


# if SparkContext._active_spark_context:
#     SparkContext._active_spark_context.stop()

spark = SparkSession.builder.appName("OCRPreprocessing").getOrCreate()
0