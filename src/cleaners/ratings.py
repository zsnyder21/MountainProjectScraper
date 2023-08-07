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

                tables = soup.find(class_="onx-stats-table").findChild("div").findChildren("div", recursive=False)
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
                    if len(suggestedRating) < 1:
                        continue  # Unknown with empty rating - nothing to do

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
