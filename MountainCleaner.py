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
            curatedAreaInfo = self.curateAreaInfo(soup)

            areaInfo = {
                "AreaId": fileContents["AreaId"],
                "ParentAreaId": fileContents["ParentAreaId"],
                "AreaName": curatedAreaInfo["AreaName"],
                "Elevation": curatedAreaInfo["Elevation"],
                "ElevationUnits": curatedAreaInfo["ElevationUnits"],
                "Latitude": curatedAreaInfo["Latitude"],
                "Longitude": curatedAreaInfo["Longitude"],
                "ViewsTotal": curatedAreaInfo["ViewsTotal"],
                "ViewsMonth": curatedAreaInfo["ViewsMonth"],
                "SharedOn": curatedAreaInfo["SharedOn"],
                "Description": curatedAreaInfo["Description"],
                "GettingThere": curatedAreaInfo["GettingThere"],
                "URL": fileContents["URL"]
            }
            self.exportToJSON(areaInfo, "Area")
            self.processAreaComments(fileContents["AreaId"], soup)

        file.close()

    @staticmethod
    def curateAreaInfo(soup: BeautifulSoup) -> dict[str]:
        curatedAreaInfo = dict()
        keys = {
            "AreaName",
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

        title = soup.find("h1")
        firstChild = title.findChild()
        childrenWordCount = len(firstChild.text.split()) if firstChild is not None else 0
        allWords = title.text.split()
        areaName = " ".join(word.strip() for word in allWords[:len(allWords) - childrenWordCount])
        curatedAreaInfo["AreaName"] = areaName

        areaInfo = soup.find(class_="description-details")

        if areaInfo is not None:
            areaInfoRows = areaInfo.find_all("tr")

            for row in areaInfoRows:
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

        if pageInfoBlocks is not None:
            for pageInfo in pageInfoBlocks:
                previousSibling = pageInfo.find_previous_sibling()
                sectionTitle = "".join(previousSibling.text.split())

                if "Descript".upper() in sectionTitle.upper().strip():
                    curatedAreaInfo["Description"] = pageInfo.text.strip()

                if "GettingThere".upper() in sectionTitle.upper().strip():
                    curatedAreaInfo["GettingThere"] = pageInfo.text.strip()

        return {key: curatedAreaInfo[key] if key in curatedAreaInfo.keys() else None for key in keys}

    def processAreaComments(self, areaId: int, soup: BeautifulSoup) -> None:
        comments = soup.find_all(class_="main-comment width100")

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
            commentText = " ".join(commentBody.find(id=f"{commentId}-full").text.split())
            commentTime = commentBody.find(class_="comment-time").text.strip()
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

        for line in file:
            fileContents = json.loads(line.strip())
            routeId = fileContents["RouteId"]
            parentAreaId = fileContents["ParentAreaId"]
            routeURL = fileContents["URL"]

            soup = BeautifulSoup(fileContents["HTML"], "html.parser")

            curatedRouteInfo = self.curateRouteInfo(routeId, soup)

            routeInfo = {
                "RouteId": routeId,
                "ParentAreaId": parentAreaId,
                "RouteName": curatedRouteInfo["RouteName"],
                "Difficulty_YDS": curatedRouteInfo["Difficulty_YDS"],
                "Difficulty_French": curatedRouteInfo["Difficulty_French"],
                "Difficulty_ADL": curatedRouteInfo["Difficulty_ADL"],
                "Severity": curatedRouteInfo["Severity"],
                "Type": curatedRouteInfo["Type"],
                "Height": curatedRouteInfo["Height"],
                "HeightUnits": curatedRouteInfo["HeightUnits"],
                "Pitches": curatedRouteInfo["Pitches"],
                "Grade": curatedRouteInfo["Grade"],
                "Description": curatedRouteInfo["Description"],
                "Location": curatedRouteInfo["Location"],
                "Protection": curatedRouteInfo["Protection"],
                "FirstAscent": curatedRouteInfo["FirstAscent"],
                "FirstAscentYear": curatedRouteInfo["FirstAscentYear"],
                "FirstFreeAscent": curatedRouteInfo["FirstFreeAscent"],
                "FirstFreeAscentYear": curatedRouteInfo["FirstFreeAscentYear"],
                "Rating": curatedRouteInfo["Rating"],
                "VoteCount": curatedRouteInfo["VoteCount"],
                "URL": routeURL
            }

            self.exportToJSON(routeInfo, "Route")
            self.processRouteComments(routeId, soup)

    def curateRouteInfo(self, routeId: int, soup: BeautifulSoup) -> dict:
        routeKeys = ["RouteName", "Difficulty_YDS", "Difficulty_French", "Difficulty_ADL", "Severity", "Type",
                     "Height", "HeightUnits", "Pitches", "Grade", "Rating", "VoteCount", "Description", "Location",
                     "Protection", "FirstAscent", "FirstAscentYear", "FirstFreeAscent", "FirstFreeAscentYear"]
        types = {"trad", "sport", "toprope", "boulder", "ice", "aid", "mixed", "alpine"}
        severities = {"G", "PG", "PG13", "PG-13", "R", "X"}
        gradeMap = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7}

        difficultyInfo = self.getRouteDifficulty(soup)
        ratingInfo = soup.find(id=f"starsWithAvgText-{routeId}")
        ratingInfo = ratingInfo.text.split()[1:4:2] if ratingInfo is not None else None
        routeName = soup.find("h1")
        routeName = routeName.text.strip() if routeName is not None else None

        curatedRouteInfo = {
            "RouteName": routeName,
            "Difficulty_YDS": difficultyInfo["YDS"],
            "Difficulty_French": difficultyInfo["French"]
        }

        if difficultyInfo["Additional"]:
            curatedRouteInfo["Severity"] = difficultyInfo["Additional"][-1].strip()\
                if difficultyInfo["Additional"][-1].strip() in severities else None
        else:
            curatedRouteInfo["Severity"] = None

        curatedRouteInfo["Difficulty_ADL"] = " ".join([item.strip() for item in difficultyInfo["Additional"]
                                                if item and item.strip() != curatedRouteInfo["Severity"]])

        routeInfo = soup.find(class_="description-details")

        if routeInfo is not None:
            routeInfoRows = routeInfo.find_all("tr")
            for row in routeInfoRows:
                info = row.text

                if "Type".upper() in info.upper():
                    routeTypeInfo = info.split(":")[1].strip().split(",")
                    while routeTypeInfo:
                        typeInfo = routeTypeInfo.pop(0)

                        if typeInfo.strip().lower() in types:
                            if "Type" in curatedRouteInfo.keys():
                                curatedRouteInfo["Type"] += f", {typeInfo.strip()}"
                            else:
                                curatedRouteInfo["Type"] = typeInfo.strip()

                        if re.match(pattern=r"(\d+\sft|\d+\sm)", string=typeInfo.strip().lower()):
                            heightInfo = re.match(pattern=r"(\d+\sft|\d+\sm)", string=typeInfo.strip()).group(0).split()
                            curatedRouteInfo["Height"] = int(heightInfo[0])
                            curatedRouteInfo["HeightUnits"] = heightInfo[1]

                        if "Pitches".lower() in typeInfo.lower():
                            pitchCount = re.search(pattern=r"\d+", string=typeInfo)
                            if pitchCount:
                                pitchCount = int(pitchCount.group(0))
                                curatedRouteInfo["Pitches"] = pitchCount

                        if "Grade".lower() in typeInfo.lower():
                            grade = re.search(pattern=r"(?<=GRADE)\s(?:I|V)+", string=typeInfo.upper())
                            if grade:
                                curatedRouteInfo["Grade"] = gradeMap[grade.group(0).strip()]

                elif "FA".upper() in info.upper():
                    firstAscentInfo = re.findall(pattern=r"(?<=FA:)[^:]+(?=FFA:)|(?<=FFA:)[^:]+(?=$)|(?<=FA:)[^:]+(?=$)", string=info.strip())
                    if firstAscentInfo:
                        firstAscentText = firstAscentInfo[0]
                        firstAscentYear = re.search(pattern=r"\d{4}", string=firstAscentText)
                        firstAscentYear = int(firstAscentYear.group(0).strip()) if firstAscentYear else None
                        curatedRouteInfo["FirstAscent"] = firstAscentText.strip() if "unknown".upper() not in firstAscentText.upper() else None
                        curatedRouteInfo["FirstAscentYear"] = firstAscentYear

                        if len(firstAscentInfo) > 1:
                            firstFreeAscentText = firstAscentInfo[1]
                            firstFreeAscentYear = re.search(pattern=r"\d{4}", string=firstFreeAscentText)
                            firstFreeAscentYear = int(firstFreeAscentYear.group(0).strip()) if firstFreeAscentYear else None
                            curatedRouteInfo["FirstFreeAscent"] = firstFreeAscentText.strip() if "unknown".upper() not in firstFreeAscentText.upper() else None
                            curatedRouteInfo["FirstFreeAscentYear"] = firstFreeAscentYear

                elif "Page Views".upper() in info.upper():
                    viewInfo = re.findall(pattern=r"(?:\d,?)+(?: total|/month)", string=info)
                    if viewInfo:
                        curatedRouteInfo["ViewsTotal"] = int(viewInfo[0].lower().replace("total", "").replace(",", ""))
                        curatedRouteInfo["ViewsMonth"] = int(viewInfo[1].lower().replace("/month", "").replace(",", ""))

                elif "Shared By".upper() in info.upper():
                    sharedOn = re.findall(pattern=r"\w{3} \d{1,2}, \d{4}", string=info)
                    if sharedOn:
                        curatedRouteInfo["SharedOn"] = re.findall(pattern=r"\w{3} \d{1,2}, \d{4}", string=info)[0]
                else:
                    pass

        pageInfoBlocks = soup.find_all(class_="fr-view")

        if pageInfoBlocks is not None:
            for pageInfo in pageInfoBlocks:
                previousSibling = pageInfo.find_previous_sibling()
                sectionTitle = "".join(previousSibling.text.split())

                if "Descript".upper() in sectionTitle.upper().strip():
                    curatedRouteInfo["Description"] = pageInfo.text.strip()

                if "Location".upper() in sectionTitle.upper().strip():
                    curatedRouteInfo["Location"] = pageInfo.text.strip()

                if "Protection".upper() in sectionTitle.upper().strip():
                    curatedRouteInfo["Protection"] = pageInfo.text.strip()

        curatedRouteInfo["Rating"] = float(ratingInfo[0])
        curatedRouteInfo["VoteCount"] = int(ratingInfo[1].replace(",", ""))

        return {key: curatedRouteInfo[key] if key in curatedRouteInfo.keys() else None for key in routeKeys}

    def processRouteComments(self, routeId: int, soup: BeautifulSoup) -> None:
        comments = soup.find_all(class_="main-comment width100")

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
            commentText = " ".join(commentBody.find(id=f"{commentId}-full").text.split())
            commentTime = commentBody.find(class_="comment-time").text.strip()
            betaVotes = int(commentContent.find(class_="num-likes").text)

            areaCommentInfo = {
                "CommentId": commentId,
                "UserId": userId,
                "RouteId": routeId,
                "UserName": userName,
                "CommentBody": commentText,
                "CommentTime": commentTime,
                "BetaVotes": betaVotes
            }

            self.exportToJSON(areaCommentInfo, "RouteComment")

    @staticmethod
    def getRouteDifficulty(soup: BeautifulSoup) -> dict:
        difficulty = soup.find(class_="inline-block mr-2")
        if difficulty is None:
            return {"YDS": None, "French": None, "Additional": None}

        difficultyText = difficulty.text.split()
        difficultyChildren = difficulty.findChildren("span")
        ratingYDS = difficulty.find(class_="rateYDS")
        ratingFrench = difficulty.find(class_="rateFrench")

        if ratingYDS is not None:
            ratingYDS = " ".join(word for word in ratingYDS.text.split() if word.upper() != "YDS")
        else:
            ratingYDS = None

        if ratingFrench is not None:
            ratingFrench = " ".join(word for word in ratingFrench.text.split() if word.upper() != "FRENCH")
        else:
            ratingFrench = None

        if difficultyChildren is not None:
            difficultyToRemove = set(chain(*[child.text.split() for child in difficultyChildren]))
        else:
            difficultyToRemove = []

        return {
            "YDS": ratingYDS,
            "French": ratingFrench,
            "Additional": [word for word in difficultyText if word not in difficultyToRemove]
        }

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

            ticks = ticksTable.find_all("tr")
            for tick in ticks:
                userPage = tick.find("a")
                if userPage is not None:
                    userName = userPage.text
                    userId = int(re.search(pattern=r"\d+", string=userPage["href"]).group(0))
                else:
                    userName = None
                    userId = None

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

                self.exportToJSON(userTick, "Stats")

    def exportToJSON(self, data: dict, dataType: str) -> None:
        file = open(self.exportFilePaths[dataType.upper()], "a")

        jsonContent = json.dumps(data, indent=None, separators=(",", ":"))
        print(jsonContent, file=file)

        file.close()


if __name__ == "__main__":
    for idx, folder in enumerate(os.walk(r"./RawDataComments")):
        if idx < 1:
            continue

        path = folder[0]

        areaCleaner = MountainCleaner(path + r"/Areas.json", "Area", r"./CleanData/")
        routeCleaner = MountainCleaner(path + r"/Routes.json", "Route", r"./CleanData/")
        statsCleaner = MountainCleaner(path + r"/Stats.json", "Stats", r"./CleanData/")

        areaCleaner.clean()
        routeCleaner.clean()
        statsCleaner.clean()

    # cleaner = MountainCleaner("./data/Areas.json", "Area", "./data/Clean/Areas.json")
    # cleaner.clean()
    #
    # cleaner = MountainCleaner("./SampleData2/Areas.json", "Area", "./SampleData2/Clean/")
    # cleaner = MountainCleaner("./SampleData2/Routes.json", "Route", "./SampleData2/Clean/")
    # cleaner = MountainCleaner("./SampleData2/Stats.json", "Stats", "./SampleData2/Clean")
    # cleaner.clean()
    #
    # cleaner = MountainCleaner("./data2/Stats.json", "Stats", "./data2/Clean2/Stats.json")
    # cleaner.clean()
