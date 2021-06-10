# MountainCleaner.py

import json
import re
from bs4 import BeautifulSoup
from itertools import chain


class MountainCleaner(object):
    def __init__(self, filePath: str, dataType: str, exportPath: str):
        self.filePath = filePath
        self.dataType = dataType
        self.exportPath = exportPath

    def clean(self) -> None:
        if self.dataType.upper() == "Route".upper():
            self.cleanRouteInfo()
        elif self.dataType.upper() == "Area".upper():
            self.cleanAreaInfo()
        elif self.dataType.upper() == "Stats".upper():
            self.cleanStatsInfo()
        else:
            return

    def cleanAreaInfo(self) -> None:
        file = open(self.filePath, "r", encoding="utf8")

        for line in file:
            fileContents = json.loads(line.strip())
            areaInfo = {
                    "AreaId": fileContents["AreaId"],
                    "ParentAreaId": fileContents["ParentAreaId"],
                    "URL": fileContents["URL"]
                }
            self.exportToJSON(areaInfo)
        file.close()

    def cleanRouteInfo(self) -> None:
        file = open(self.filePath, "r", encoding="utf8")

        for line in file:
            fileContents = json.loads(line.strip())
            routeId = fileContents["RouteId"]
            parentAreaId = fileContents["ParentAreaId"]
            routeURL = fileContents["URL"]

            soup = BeautifulSoup(fileContents["HTML"], "html.parser")
            routeTypeInfo = soup.find(class_="description-details").find("tr").text.split(":")[1].strip().split(",")
            difficultyInfo = self.getRouteDifficulty(soup)
            ratingInfo = soup.find(id=f"starsWithAvgText-{routeId}").text.split()[1:4:2]
            routeName = soup.find("h1").text.strip()

            routeInfo = self.curateRouteInfo(routeId, parentAreaId, routeName, routeURL, routeTypeInfo, difficultyInfo, ratingInfo)

            self.exportToJSON(routeInfo)

    @classmethod
    def curateRouteInfo(cls, routeId: int, parentAreaId: int, routeName: str, routeURL: str, routeTypeInfo: list[str],
                        difficultyInfo: dict, ratingInfo: list[str]) -> dict:
        routeKeys = ["RouteId", "ParentAreaId", "Name", "URL", "Difficulty", "Difficulty_ADL", "Severity", "Type",
                     "Height", "HeightUnits", "Pitches", "Grade", "Rating", "VoteCount"]
        types = {"trad", "sport", "toprope", "boulder", "ice", "aid", "mixed", "alpine"}
        severities = {"G", "PG", "PG13", "PG-13", "R", "X"}
        routeInfo = {"RouteId": routeId, "ParentAreaId": parentAreaId, "Name": routeName, "URL": routeURL,
                     "Difficulty": difficultyInfo["YDS"]}

        if difficultyInfo["Additional"]:
            routeInfo["Severity"] = difficultyInfo["Additional"][-1].strip()\
                if difficultyInfo["Additional"][-1].strip() in severities else None
        else:
            routeInfo["Severity"] = None

        routeInfo["Difficulty_ADL"] = " ".join([item.strip() for item in difficultyInfo["Additional"]
                                                if item and item.strip() != routeInfo["Severity"]])

        while routeTypeInfo:
            info = routeTypeInfo.pop(0)

            if info.strip().lower() in types:
                if "Type" in routeInfo.keys():
                    routeInfo["Type"] += f", {info.strip()}"
                else:
                    routeInfo["Type"] = info.strip()

            if re.match(pattern=r"(\d+\sft|\d+\sm)", string=info.strip().lower()):
                heightInfo = re.match(pattern=r"(\d+\sft|\d+\sm)", string=info.strip()).group(0).split()
                routeInfo["Height"] = int(heightInfo[0])
                routeInfo["HeightUnits"] = heightInfo[1]

            if "Pitches".lower() in info.lower():
                routeInfo["Pitches"] = info.strip()

            if "Grade".lower() in info.lower():
                routeInfo["Grade"] = info.strip()

        routeInfo["Rating"] = float(ratingInfo[0])
        routeInfo["VoteCount"] = int(ratingInfo[1].replace(",", ""))

        return {key: routeInfo[key] if key in routeInfo.keys() else None for key in routeKeys}

    @classmethod
    def getRouteDifficulty(cls, soup: BeautifulSoup) -> dict:
        difficulty = soup.find(class_="inline-block mr-2")
        difficultyText = difficulty.text.split()
        difficultyChildren = difficulty.findChildren("span")
        YDS = difficulty.find(class_="rateYDS")

        if YDS is not None:
            YDS = YDS.text.split()[0]
        else:
            YDS = None

        if difficultyChildren is not None:
            difficultyToRemove = set(chain(*[child.text.split() for child in difficultyChildren]))
        else:
            difficultyToRemove = []

        return {"YDS": YDS, "Additional": [word for word in difficultyText if word not in difficultyToRemove]}

    def cleanStatsInfo(self) -> None:
        file = open(self.filePath, "r", encoding="utf8")

        for line in file:
            fileContents = json.loads(line.strip())
            routeId = fileContents["RouteId"]
            parentAreaId = fileContents["ParentAreaId"]
            statsURL = fileContents["URL"]

            soup = BeautifulSoup(fileContents["HTML"], "html.parser")

            ticksTable = soup.find(
                class_="col-lg-6 col-sm-12 col-xs-12 mt-2 max-height max-height-md-1000 max-height-xs-400")

            if ticksTable is None:
                continue

            tickCount = int(re.search(pattern=r"\d+", string=ticksTable.find("h3").text).group(0))
            ticks = ticksTable.find_all("tr")
            for tick in ticks:
                userPage = tick.find("a")
                if userPage is not None:
                    userName = userPage.text
                    userId = int(re.search(pattern=r"\d+", string=userPage["href"]).group(0))
                else:
                    userName = None
                    userId = None

                # print(userPage.text, userId)
                tickInfo = tick.find(class_="small max-height max-height-md-120 max-height-xs-120").find("div").text
                tickInfo = [info.strip() for info in tickInfo.split("·")]

                userTick = {
                    "UserId": userId,
                    "UserName": userName,
                    "RouteId": routeId,
                    "ParentAreaId": parentAreaId,
                    "URL": statsURL,
                    "TickDate": tickInfo[0],
                    # "TickDatetime": datetime.strptime(tickInfo[0], "%b %d, %Y")
                    # if tickInfo[0].lower() != "-no date-" else None,
                    "TickInfo": None if len(tickInfo) < 2 else tickInfo[1]
                }

                self.exportToJSON(userTick)

    def exportToJSON(self, data: dict) -> None:
        file = open(self.exportPath, "a")

        jsonContent = json.dumps(data, indent=None, separators=(",", ":"))
        print(jsonContent, file=file)

        file.close()


if __name__ == "__main__":
    # cleaner = MountainCleaner("./data2/Areas.json", "Area", "./data2/Clean/Areas.json")
    # cleaner.clean()

    cleaner = MountainCleaner("./data2/Routes.json", "Route", "./data2/Clean/Routes.json")
    cleaner.clean()

    # cleaner = MountainCleaner("./data2/Stats.json", "Stats", "./data2/Clean/Stats.json")
    # cleaner.clean()


    # routes = spark.read.json("./data2/Routes.json")
    # areas = spark.read.json("./data2/Areas.json")
    # routeStats = spark.read.json("./data2/Stats.json")
    #
    # routes.createOrReplaceTempView("routes")
    # areas.createOrReplaceTempView("areas")
    # routeStats.createOrReplaceTempView("stats")
    #
    # # noinspection SqlDialectInspection
    # query = """
    # select  RouteId,
    #         ParentAreaId,
    #         URL
    #     from routes
    # """
    # results = spark.sql(query)
    #
    # results.show(100, False)
