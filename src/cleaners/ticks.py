import json
import re

from bs4 import BeautifulSoup
from src.cleaners.MountainProjectCleaner import MountainCleaner


class RouteTicksCleaner(MountainCleaner):
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

                # Note that this element has changed class since I scraped the data
                # The new name appears to be
                # "col-lg-6 col-sm-12 col-xs-12 mt-2 max-height max-height-md-1000 max-height-xs-400 max-height-processed"
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

                    tickInfos = tick.find("div").find_all("div")
                    splitChar = "•" if userId is None else "·"  # Bolded cdot for anonymous cowards it seems...
                    for tickInfo in tickInfos:
                        tickInfoIndividual = [info.strip() for info in tickInfo.text.split(splitChar)]
                        tickYear = re.search(pattern=r"\d{4}", string=tickInfoIndividual[0])

                        if tickYear:
                            if int(tickYear.group(0)) < 1900:
                                tickInfoIndividual[0] = None
                        else:
                            tickInfoIndividual[0] = None

                        userTick = {
                            "TickId": int(tick["id"].split(".")[1]),
                            "RouteId": routeId,
                            "UserId": userId,
                            "UserName": userName,
                            "TickDate": tickInfoIndividual[0],
                            "TickInfo": (None if len(tickInfoIndividual) < 2 else tickInfoIndividual[1]),
                            "URL": statsURL,
                        }

                        self.exportToJSON(userTick, "RouteTicks")
