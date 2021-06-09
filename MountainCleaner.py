# MountainCleaner.py

import json
from bs4 import BeautifulSoup
from datetime import datetime
import pyspark as ps

spark = ps.sql.SparkSession.builder.master("local[4]").appName("MountainCleaner").getOrCreate()
sc = spark.sparkContext
spark.conf.set("spark.sql.caseSensitive", "true")


class MountainCleaner(object):
	def __init__(self, dataType: str, filePath):
		self.dataType = dataType
		self.filePath = filePath


if __name__ == "__main__":
	routes = spark.read.json("./data/Test Data/Routes.json")
	print(routes)