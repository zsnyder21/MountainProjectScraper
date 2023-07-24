import os
from src.cleaners import getCleaner

for idx, folder in enumerate(os.walk(r"../data/20230721/Raw")):
    if idx < 5:
        # First folder is root - skip it
        continue

    path = folder[0]
    fileMap = (
        # ("Areas", "Areas"),
        # ("Routes", "Routes"),
        ("Stats", "RouteStarRatings"),
        ("Stats", "RouteRatings"),
        ("Stats", "RouteToDos"),
        ("Stats", "RouteTicks"),
    )

    print(f"Processing {path}...")
    for file, dataType in fileMap:
        print("\t", f"{dataType}...")
        cleanerClass = getCleaner(dataType=dataType)
        cleaner = cleanerClass(filePath=f"{path}/{file}.json", dataType=dataType, exportDir=r"../data/20230721/Clean")

        cleaner.clean()

    break


