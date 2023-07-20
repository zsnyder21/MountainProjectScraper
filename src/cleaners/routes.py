import json
import re

from bs4 import BeautifulSoup
from itertools import chain
from src.cleaners.MountainProjectCleaner import MountainCleaner


class RoutesCleaner(MountainCleaner):
    """
    Handles routes and route comments
    """
    def clean(self):
        with open(self.filePath, "r", encoding="utf8") as file:
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

                self.exportToJSON(routeInfo, "Routes")
                self.processRouteComments(routeId, soup)

    def curateRouteInfo(self, routeId: int, soup: BeautifulSoup) -> dict:
        routeKeys = ["RouteName", "Difficulty_YDS", "Difficulty_French", "Difficulty_ADL", "Severity", "Type",
                     "Height", "HeightUnits", "Pitches", "Grade", "Rating", "VoteCount", "Description", "Location",
                     "Protection", "FirstAscent", "FirstAscentYear", "FirstFreeAscent", "FirstFreeAscentYear"]
        types = {"trad", "sport", "tr", "boulder", "ice", "aid", "mixed", "alpine", "snow"}
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
            curatedRouteInfo["Severity"] = difficultyInfo["Additional"][-1].strip() \
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
                            routeType = "Top Rope" if typeInfo.strip() == "TR" else typeInfo.strip()
                            if "Type" in curatedRouteInfo.keys():
                                curatedRouteInfo["Type"] += f", {routeType}"
                            else:
                                curatedRouteInfo["Type"] = routeType

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
                    firstAscentInfo = re.findall(
                        pattern=r"(?<=FA:)[^:]+(?=FFA:)|(?<=FFA:)[^:]+(?=$)|(?<=FA:)[^:]+(?=$)", string=info.strip())
                    if firstAscentInfo:
                        firstAscentText = firstAscentInfo[0]
                        firstAscentYear = re.search(pattern=r"\d{4}", string=firstAscentText)
                        firstAscentYear = int(firstAscentYear.group(0).strip()) if firstAscentYear else None
                        curatedRouteInfo["FirstAscent"] = firstAscentText.strip() if "unknown".upper() not in firstAscentText.upper() else None
                        curatedRouteInfo["FirstAscentYear"] = firstAscentYear

                        if len(firstAscentInfo) > 1:
                            firstFreeAscentText = firstAscentInfo[1]
                            firstFreeAscentYear = re.search(pattern=r"\d{4}", string=firstFreeAscentText)
                            firstFreeAscentYear = int(
                                firstFreeAscentYear.group(0).strip()) if firstFreeAscentYear else None
                            curatedRouteInfo[
                                "FirstFreeAscent"] = firstFreeAscentText.strip() if "unknown".upper() not in firstFreeAscentText.upper() else None
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

        curatedRouteInfo["Rating"] = float(ratingInfo[0]) if ratingInfo is not None else None
        curatedRouteInfo["VoteCount"] = int(ratingInfo[1].replace(",", "")) if ratingInfo is not None else None

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
            commentTime = commentTime.split("·")
            betaVotes = int(commentContent.find(class_="num-likes").text)

            routeCommentInfo = {
                "CommentId": commentId,
                "RouteId": routeId,
                "UserId": userId,
                "UserName": userName,
                "CommentBody": commentText,
                "CommentTime": (commentTime[0].strip() if "ago".upper() not in commentTime[0].upper() else None),
                "BetaVotes": betaVotes,
                "AdditionalInfo": (commentTime[1].strip() if len(commentTime) > 1 else None)
            }

            self.exportToJSON(routeCommentInfo, "RouteComments")

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

        ratingsYDS = difficulty.find_all(class_="rateYDS")
        if len(ratingsYDS) > 1:
            ratingYDS2 = ratingsYDS[1]
        else:
            ratingYDS2 = None

        if difficultyChildren is not None:
            difficultyToRemove = set(chain(*[child.text.split() for child in difficultyChildren]))
        else:
            difficultyToRemove = set()

        if ratingYDS2 is not None:
            difficultyToRemove.remove(" ".join(word for word in ratingYDS2.text.split() if word.upper() != "YDS"))

        return {
            "YDS": ratingYDS,
            "French": ratingFrench,
            "Additional": [word for word in difficultyText if word not in difficultyToRemove]
        }