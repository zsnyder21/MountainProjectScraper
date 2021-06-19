# MountainCleaner.py

import json
import re
import os
from bs4 import BeautifulSoup
from itertools import chain


class MountainCleaner(object):
    def __init__(self, filePath: str, dataType: str, exportDir: str):
        self.filePath = filePath
        self.dataType = dataType
        self.exportDir = exportDir.strip()
        self.exportDir += (r"/" if self.exportDir[-1] != r"/" else "")
        self.areaExportPath = self.exportDir + "Areas.json"
        self.areaCommentsExportPath = self.exportDir + "AreaComments.json"
        self.routeExportPath = self.exportDir + "Routes.json"
        self.routeCommentsExportPath = self.exportDir + "RouteComments.json"
        self.statsExportPath = self.exportDir + "Stats.json"
        self.exportFilePaths = {
            "Area".upper(): self.areaExportPath,
            "AreaComment".upper(): self.areaCommentsExportPath,
            "Route".upper(): self.routeExportPath,
            "RouteComment".upper(): self.routeCommentsExportPath,
            "Stats".upper(): self.statsExportPath
        }

        os.makedirs(self.exportDir, exist_ok=True)

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

            soup = BeautifulSoup(fileContents["HTML"], "html.parser")
            title = soup.find("h1")
            children = [child.text.strip() for child in title.findChildren()]
            areaName = " ".join(word.strip() for word in title.text.split() if word not in children)
            areaInfo = self.curateAreaInfo(soup)

            areaInfo = {
                "AreaId": fileContents["AreaId"],
                "ParentAreaId": fileContents["ParentAreaId"],
                "AreaName": areaName,
                "Elevation": areaInfo["Elevation"],
                "ElevationUnits": areaInfo["ElevationUnits"],
                "Latitude": areaInfo["Latitude"],
                "Longitude": areaInfo["Longitude"],
                "ViewsTotal": areaInfo["ViewsTotal"],
                "ViewsMonth": areaInfo["ViewsMonth"],
                "SharedOn": areaInfo["SharedOn"],
                "Description": areaInfo["Description"],
                "GettingThere": areaInfo["GettingThere"],
                "URL": fileContents["URL"]
            }
            self.exportToJSON(areaInfo, "Area")
            self.processAreaComments(fileContents["AreaId"], soup)
            break
        file.close()

    @staticmethod
    def curateAreaInfo(soup: BeautifulSoup) -> dict[str]:
        curatedAreaInfo = dict()
        keys = {
            "Elevation",
            "ElevationUnits",
            "Latitude",
            "Longitude",
            "ViewsTotal",
            "ViewsMonth",
            "SharedOn",
            "Description",
            "GettingThere"
        }

        routeInfo = soup.find(class_="description-details")
        routeInfoRows = routeInfo.find_all("tr")

        for row in routeInfoRows:
            info = row.text
            if "Elevation".upper() in info.upper():
                elevationInfo = re.search(pattern=r"(-?(\d,?)+\sft|(\d,?)+\sm)", string=info.strip())
                if elevationInfo:
                    elevationInfo = elevationInfo.group(0).split()
                    curatedAreaInfo["Elevation"] = float(elevationInfo[0].replace(",", ""))
                    curatedAreaInfo["ElevationUnits"] = elevationInfo[1]
            elif "GPS".upper() in info.upper():
                gpsInfo = re.findall(pattern=r"-?\d+\.?(?:\d+)?,\s?-?\d+\.?(?:\d+)?", string=info.strip())
                if gpsInfo:
                    gpsInfo = gpsInfo[0].split(",")
                    curatedAreaInfo["Latitude"] = float(gpsInfo[0])
                    curatedAreaInfo["Longitude"] = float(gpsInfo[1])
            elif "Page Views".upper() in info.upper():
                viewInfo = re.findall(pattern=r"(?:\d,?)+(?: total|/month)", string=info)
                if viewInfo:
                    curatedAreaInfo["ViewsTotal"] = int(viewInfo[0].lower().replace("total", "").replace(",", ""))
                    curatedAreaInfo["ViewsMonth"] = int(viewInfo[1].lower().replace("/month", "").replace(",", ""))
            elif "Shared By".upper() in info.upper():
                sharedOn = re.findall(pattern=r"\w{3} \d{1,2}, \d{4}", string=info)
                if sharedOn:
                    curatedAreaInfo["SharedOn"] = re.findall(pattern=r"\w{3} \d{1,2}, \d{4}", string=info)[0]
            else:
                pass

        pageInfoBlocks = soup.find_all(class_="fr-view")
        for pageInfo in pageInfoBlocks:
            previousSibling = pageInfo.find_previous_sibling()
            sectionTitle = "".join(previousSibling.text.split())

            if "Descript".upper() in sectionTitle.upper().strip():
                curatedAreaInfo["Description"] = pageInfo.text.strip()

            if "GettingThere".upper() in sectionTitle.upper().strip():
                curatedAreaInfo["GettingThere"] = pageInfo.text.strip()

        return {key: curatedAreaInfo[key] if key in curatedAreaInfo.keys() else None for key in keys}

    def processAreaComments(self, areaId: int, soup: BeautifulSoup) -> None:
        commentsBlock = soup.find(class_="comment-list")
        comments = soup.find_all(class_="main-comment width100")
        print(soup)
        print(comments)
        for comment in comments:
            commentId = int(re.search(pattern=r"\d+", string=comment["id"]).group(0))
            userInfo = comment.find(class_="pl-1 py-1 user hidden-xs-down")
            userPage = userInfo.find("a")
            if userPage is not None:
                userId = int(re.search(pattern=r"\d+", string=userPage["href"]).group(0))
                userName = userPage.text.strip()
            else:
                userId = None
                userName = None

            commentContent = comment.find(class_="p-1")
            commentBody = commentContent.find(class_="comment-body")
            commentText = " ".join(commentBody.text.split())
            commentTime = commentBody.find(class_="comment-time").text
            betaVotes = int(commentContent.find(class_="num-likes").text)

            areaCommentInfo = {
                "CommentId": commentId,
                "UserId": userId,
                "AreaId": areaId,
                "UserName": userName,
                "CommentBody": commentText,
                "CommentTime": commentTime,
                "BetaVotes": betaVotes
            }

            self.exportToJSON(areaCommentInfo, "AreaComment")

    def cleanRouteInfo(self) -> None:
        file = open(self.filePath, "r", encoding="utf8")
        zeroDataCount = 0

        for line in file:
            # try:
                fileContents = json.loads(line.strip())
                routeId = fileContents["RouteId"]
                parentAreaId = fileContents["ParentAreaId"]
                routeURL = fileContents["URL"]

                if not fileContents["HTML"]:
                    zeroDataCount += 1
                    continue

                soup = BeautifulSoup(fileContents["HTML"], "html.parser")
                routeDetails = soup.find(class_="description-details")
                if routeDetails is None:
                    zeroDataCount += 1
                    continue

                routeTypeInfo = routeDetails.find("tr").text.split(":")[1].strip().split(",")
                difficultyInfo = self.getRouteDifficulty(soup)
                if difficultyInfo["YDS"] is None:
                    zeroDataCount += 1
                    continue
                ratingInfo = soup.find(id=f"starsWithAvgText-{routeId}").text.split()[1:4:2]
                routeName = soup.find("h1").text.strip()

                routeInfo = self.curateRouteInfo(routeId, parentAreaId, routeName, routeURL, routeTypeInfo, difficultyInfo, ratingInfo)

                self.exportToJSON(routeInfo)
            # except Exception as e:
            #     print(e)
            #     print(routeURL)
                # return

        print(f"Missing data for {zeroDataCount} routes.")

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
        if difficulty is None:
            return {"YDS": None, "Additional": None}

        difficultyText = difficulty.text.split()
        difficultyChildren = difficulty.findChildren("span")
        YDS = difficulty.find(class_="rateYDS")

        if YDS is not None:
            YDS = " ".join(word for word in YDS.text.split() if word.upper() != "YDS")
        else:
            YDS = None

        if difficultyChildren is not None:
            difficultyToRemove = set(chain(*[child.text.split() for child in difficultyChildren]))
        else:
            difficultyToRemove = []

        return {"YDS": YDS, "Additional": [word for word in difficultyText if word not in difficultyToRemove]}

    def cleanStatsInfo(self) -> None:
        file = open(self.filePath, "r", encoding="utf8")
        zeroDataCount = 0

        for line in file:
            fileContents = json.loads(line.strip())
            routeId = fileContents["RouteId"]
            parentAreaId = fileContents["ParentAreaId"]
            statsURL = fileContents["URL"]

            if not fileContents["HTML"]:
                zeroDataCount += 1
                continue

            soup = BeautifulSoup(fileContents["HTML"], "html.parser")

            ticksTable = soup.find(
                class_="col-lg-6 col-sm-12 col-xs-12 mt-2 max-height max-height-md-1000 max-height-xs-400")

            if ticksTable is None:
                continue

            # tickCount = int(re.search(pattern=r"\d+", string=ticksTable.find("h3").text).group(0))
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
                    "TickDate": tickInfo[0] if tickInfo[0].lower() != "-no date-" else None,
                    # "TickDatetime": datetime.strptime(tickInfo[0], "%b %d, %Y")
                    # if tickInfo[0].lower() != "-no date-" else None,
                    "TickInfo": None if len(tickInfo) < 2 else tickInfo[1]
                }

                self.exportToJSON(userTick)

        print(f"Missing route statistics for {zeroDataCount} routes.")

    def exportToJSON(self, data: dict, dataType: str) -> None:
        file = open(self.exportFilePaths[dataType.upper()], "a")

        jsonContent = json.dumps(data, indent=None, separators=(",", ":"))
        print(jsonContent, file=file)

        file.close()


if __name__ == "__main__":
    # cleaner = MountainCleaner("./data/Areas.json", "Area", "./data/Clean/Areas.json")
    # cleaner.clean()
    #
    cleaner = MountainCleaner("./SampleData/Areas.json", "Area", "./SampleData/Clean2/")
    cleaner.clean()

    # cleaner = MountainCleaner("./data2/Stats.json", "Stats", "./data2/Clean2/Stats.json")
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
