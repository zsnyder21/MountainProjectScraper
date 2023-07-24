import json
import re

from bs4 import BeautifulSoup
from src.cleaners.MountainProjectCleaner import MountainCleaner


class RouteStarRatingsCleaner(MountainCleaner):
    """
    Handles route ratings
    """
    def clean(self):
        with open(self.filePath, "r", encoding="utf8") as file:
            for line in file:
                fileContents = json.loads(line.strip())
                routeId = fileContents["RouteId"]
                statsURL = fileContents["URL"]

                soup = BeautifulSoup(fileContents["HTML"], "html.parser")

                tables = soup.find(class_="onx-stats-table").findChild("div").findChildren("div", recursive=False)
                for ratingTable in tables:
                    if "Star Ratings".upper() in ratingTable.find("h3").text.upper():
                        break

                ratings = ratingTable.find_all("tr")
                for rating in ratings:
                    userPage = rating.find("a")
                    if userPage is not None:
                        userName = userPage.text
                        userId = int(re.search(pattern=r"\d+", string=userPage["href"]).group(0))
                    else:
                        userName = None
                        userId = None

                    starsParent = rating.find(class_="sc-dkrFOg eSLrh")
                    ratingId = int(starsParent.parent.parent["id"].split(".")[1])
                    starClasses = {
                        "scoreStars": 0,
                        "sc-eDvSVe kSLVic": 1,
                        "sc-eDvSVe kSLVfA": 2,
                        "sc-eDvSVe kSLViz": 3,
                        "sc-eDvSVe ikgMEI": 4
                    }
                    for cls, userRouteRating in starClasses.items():
                        if starsParent.find(class_=cls):
                            break

                    userRating = {
                        "RatingId": ratingId,
                        "RouteId": routeId,
                        "UserId": userId,
                        "UserName": userName,
                        "Rating": userRouteRating,
                        "URL": statsURL
                    }

                    self.exportToJSON(userRating, "RouteStarRatings")