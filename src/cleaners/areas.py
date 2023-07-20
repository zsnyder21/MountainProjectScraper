import json
import re

from bs4 import BeautifulSoup
from src.cleaners.MountainProjectCleaner import MountainCleaner


class AreasCleaner(MountainCleaner):
    """
    Handles areas and area comments
    """
    def clean(self):
        with open(self.filePath, "r", encoding="utf8") as file:
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
                    "Overview": curatedAreaInfo["Overview"],
                    "Description": curatedAreaInfo["Description"],
                    "GettingThere": curatedAreaInfo["GettingThere"],
                    "URL": fileContents["URL"]
                }
                self.exportToJSON(areaInfo, "Areas")
                self.processAreaComments(fileContents["AreaId"], soup)

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
            "Overview",
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
                        curatedAreaInfo["ViewsTotal"] = int(
                            viewInfo[0].lower().replace("total", "").replace(",", ""))
                        curatedAreaInfo["ViewsMonth"] = int(
                            viewInfo[1].lower().replace("/month", "").replace(",", ""))
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

                if "Overview".upper() in sectionTitle.upper().strip():
                    curatedAreaInfo["Overview"] = pageInfo.text.strip()

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
            commentTime = commentTime.split("·")

            betaVotes = int(commentContent.find(class_="num-likes").text)

            areaCommentInfo = {
                "CommentId": commentId,
                "AreaId": areaId,
                "UserId": userId,
                "UserName": userName,
                "CommentBody": commentText.strip(),
                "CommentTime": (commentTime[0].strip() if "ago".upper() not in commentTime[0].upper() else None),
                "BetaVotes": betaVotes,
                "AdditionalInfo": (commentTime[1].strip() if len(commentTime) > 1 else None)
            }

            self.exportToJSON(areaCommentInfo, "AreaComments")