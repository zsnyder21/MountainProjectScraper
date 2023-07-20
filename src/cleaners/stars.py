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

                # Note that this element has changed class since I scraped the data
                # The new name appears to be
                # "col-lg-6 col-sm-12 col-xs-12 mt-2 max-height max-height-md-1000 max-height-xs-400 max-height-processed"
                ratingTable = soup.find(
                    class_="col-lg-2 col-sm-4 col-xs-12 mt-2 max-height max-height-md-1000 max-height-xs-400")

                if ratingTable is None or "Star Ratings".upper() not in ratingTable.find("h3").text.upper():
                    continue

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