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

                tables = soup.find(class_="onx-stats-table").findChild("div").findChildren("div", recursive=False)
                for toDosTable in tables:
                    if "On To-Do Lists".upper() in toDosTable.find("h3").text.upper():
                        break

                toDos = toDosTable.find_all("tr")
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