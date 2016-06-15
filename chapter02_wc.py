import os
import sys
import platform

import py4j

import pyspark
from pyspark.context import SparkContext
from pyspark.sql import SQLContext, HiveContext
from pyspark.storagelevel import StorageLevel

# init - create SparkContext on Azure HdInsight
# on Azure HdInsight master was deafult to yarn
sc = SparkContext(appName="wc")

print "sys.argv[1]: ", sys.argv[1] 

wc = sc.textFile(sys.argv[1]) \
  .map( lambda x: x.replace(',',' ').replace('.',' ').replace('-',' ').lower()) \
  .flatMap(lambda x: x.split(" ")) \
  .map(lambda x: (x, 1)) \
  .reduceByKey(lambda x, y: x + y)

print wc.collect()
