import json
import re

from bs4 import BeautifulSoup
from src.cleaners.MountainProjectCleaner import MountainCleaner


class RouteRatingsCleaner(MountainCleaner):
    """
    Handles route ticks
    """
    def clean(self):
        with open(self.filePath, "r", encoding="utf8") as file:
            for line in file:
                fileContents = json.loads(line.strip())
                routeId = fileContents["RouteId"]
                statsURL = fileContents["URL"]

                soup = BeautifulSoup(fileContents["HTML"], "html.parser")

                tables = soup.find_all(
                    class_="col-lg-2 col-sm-4 col-xs-12 mt-2 max-height max-height-md-1000 max-height-xs-400")

                for ratingTable in tables:
                    if "Suggested Ratings".upper() in ratingTable.find("h3").text.upper():
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

                    ratingInfos = rating.find_all("td")
                    suggestedRating = ratingInfos[-1].text.split()
                    difficulty = suggestedRating[0]
                    if len(suggestedRating) > 1:
                        severity = suggestedRating[1]
                    else:
                        severity = None

                    userTick = {
                        "RatingId": int(rating["id"].split(".")[1]),
                        "RouteId": routeId,
                        "UserId": userId,
                        "UserName": userName,
                        "Difficulty": difficulty,
                        "Severity": severity,
                        "URL": statsURL,
                    }

                    self.exportToJSON(userTick, "RouteRatings")
