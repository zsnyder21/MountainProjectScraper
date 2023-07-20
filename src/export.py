import os

from dotenv import load_dotenv
from src.exporters import getExporter

load_dotenv()
password = os.getenv("POSTGRESQL_PASSWORD")

fileMap = (
    ("../data/20230719/Clean/Areas.json", "Areas"),
    ("../data/20230719/Clean/AreaComments.json", "AreaComments"),
    ("../data/20230719/Clean/Routes.json", "Routes"),
    ("../data/20230719/Clean/RouteComments.json", "RouteComments"),
    ("../data/20230719/Clean/RouteRatings.json", "RouteRatings"),
    ("../data/20230719/Clean/RouteStarRatings.json", "RouteStarRatings"),
    ("../data/20230719/Clean/RouteToDos.json", "RouteToDos"),
    ("../data/20230719/Clean/RouteTicks.json", "RouteTicks"),
    ("../data/Reference/DifficultyReference.json", "DifficultyReference"),
    ("../data/Reference/SeverityReference.json", "SeverityReference"),
)

for file, dataType in fileMap:
    print(f"Processing {file}...")
    exporterClass = getExporter(dataType=dataType)
    exporter = exporterClass(
        username="postgres",
        password=password,
        host="127.0.0.1",
        port="5432",
        database="MountainProject",
        dataType=dataType,
        chunkSize=200,
    )

    exporter.postToSQL(file=file, commit=True)
