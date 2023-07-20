import json
import re

from bs4 import BeautifulSoup
from src.cleaners.MountainProjectCleaner import MountainCleaner


class RouteToDosCleaner(MountainCleaner):
    """
    Handles route ToDos
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
                statsTables = soup.find_all(
                    class_="col-lg-2 col-sm-4 col-xs-12 mt-2 max-height max-height-md-1000 max-height-xs-400"
                )

                for statTable in statsTables:
                    if "On To-Do Lists".upper() in statTable.find("h3").text.upper():
                        toDos = statTable.find_all("tr")

                        for toDo in toDos:
                            userPage = toDo.find("a")
                            if userPage is not None:
                                userName = userPage.text
                                userId = int(re.search(pattern=r"\d+", string=userPage["href"]).group(0))
                            else:
                                userName = None
                                userId = None

                            userToDo = {
                                "RouteId": routeId,
                                "UserId": userId,
                                "UserName": userName,
                                "URL": statsURL
                            }

                            self.exportToJSON(userToDo, "RouteToDos")