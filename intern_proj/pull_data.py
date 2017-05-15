from pyspark import SparkContext
from pyspark.sql import HiveContext, DataFrame
import pandas
import os

sc = SparkContext()
hc = HiveContext(sc)

df = hc.read.parquet('/eng/mti/ww/be/msb/assembly_quality/twodid/2017-05-08_a/*.parquet')

filepath = os.path.join("/home/hdfsbe/auto-diagnostics", 'sample_z.csv')
df.toPandas().to_csv(filepath)
