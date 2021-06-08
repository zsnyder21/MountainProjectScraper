#MountainProjectScraper.py

import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

class MountainScraper(object):
	def __init__(self, statesToScrape: any((None, list[str])), startingPage: any([None, str]) = None) -> None:
		self.statesToScrape = [state.upper() for state in statesToScrape] if statesToScrape is not None else None
		self.startingPage = startingPage if startingPage is not None else "https://www.mountainproject.com/"

		if startingPage is None:
			self.parentAreas = {
				strong.find("a").text : strong.find("a")["href"] for strong in BeautifulSoup(requests.get(self.startingPage).text, "html.parser")
					.find(id="route-guide").find_all("strong") if self.statesToScrape is None or strong.find("a").text.upper() in self.statesToScrape
			}
		else:
			self.parentAreas = {
				" ".join(BeautifulSoup(requests.get(self.startingPage).text, "html.parser").find("h1").text.split()): self.startingPage
			}


	def findSubordinates(self, parentAreas: dict[str : str], parentAreaId: any([None, int]) = None) -> None:
		for parentArea, url in parentAreas.items():
			areaId = int(re.search(pattern=r"\d+", string=url).group(0))
			soup = BeautifulSoup(requests.get(url).text, "html.parser")

			# Determine if we have found routes yet or not
			hasRoutes = "Routes".upper() in soup.find(class_="mp-sidebar").find("h3").text.upper()

			print(f"{parentArea} has {'routes' if hasRoutes else 'sub areas'}.")

			if hasRoutes:
				self.findRoutes(areaId, url)
			else:
				subAreas = {subArea.text : subArea["href"] for subArea in soup.find(class_="max-height max-height-md-0 max-height-xs-400").findAll("a")}
				self.findSubordinates(subAreas, areaId)

			# break

	def findRoutes(self, areaId: int, url: str) -> None:
		soup = BeautifulSoup(requests.get(url).text, "html.parser")

		routes = {route.text : route["href"] for route in soup.find(class_="max-height max-height-md-0 max-height-xs-400").findAll("a") if route["href"] != "#"}

		for route, url in routes.items():
			print(route + ": " + url)
			routeId = int(re.search(pattern=r"\d+", string=url).group(0))
			soup = BeautifulSoup(requests.get(url).text, "html.parser")

			routeType = soup.find(class_="description-details").find("tr").text

			difficultyInfo = soup.find(class_="inline-block mr-2").text.split()
			routeTypeInfo = routeType.split(":")[1].strip().split(",")
			ratingInfo = soup.find(id=f"starsWithAvgText-{routeId}").text.split()[1:4:2]

			print(self.curateRouteInfo(route, routeTypeInfo, difficultyInfo, ratingInfo))
			# grade = soup.find(class_="rateYDS").text.split()[0]
			# safety = soup.find()
			# print(grade)

			# self.findRouteTicks(routeId, url)

			# break


	def findRouteTicks(self, routeId: int, url: str) -> None:
		url = url.replace("/route/", "/route/stats/")
		soup = BeautifulSoup(requests.get(url).text, "html.parser")
		pattern = re.compile(r"Ticks ")
		ticksTable = soup.find(class_="col-lg-6 col-sm-12 col-xs-12 mt-2 max-height max-height-md-1000 max-height-xs-400")

		if ticksTable is None:
			return

		tickCount = int(re.search(pattern=r"\d+", string=ticksTable.find("h3").text).group(0))
		print(f"Total ticks: {tickCount}.")

		ticks = ticksTable.find_all("tr")
		for tick in ticks:
			userPage = tick.find("a")
			if userPage is not None:
				userName = userPage.text
				userId = int(re.search(pattern=r"\d+", string=userPage["href"]).group(0))
			else:
				userName = None
				userId = None

			# print(userPage.text, userId)
			tickInfo = tick.find(class_="small max-height max-height-md-120 max-height-xs-120").find("div").text
			tickInfo = [info.strip() for info in tickInfo.split("·")]

			userTick = {
				"UserName" : userName,
				"UserId" : userId,
				"TickDate" : tickInfo[0],
				"TickDatetime" : datetime.strptime(tickInfo[0], "%b %d, %Y"),
				"TickInfo" : None if len(tickInfo) < 2 else tickInfo[1]
			}

			print("     ", userTick)

	def exportToCSV(self, dictionary : dict, ):
		pass

	def curateRouteInfo(self, routeName: str, routeInfo: list[str], routeDifficulty: list[str], routeRating: list[str]) -> dict:
		routeInfoCopy = routeInfo.copy()
		routeDifficultyCopy = routeDifficulty.copy()
		routeRatingCopy = routeRating.copy()
		curatedRouteInfo = {"Name": routeName}
		types = {"trad", "sport", "toprope", "boulder", "ice", "aid", "mixed", "alpine"}
		difficultyPattern = r"(?:A|C|M)\d(?:\+|-)?"
		severityPattern = r"(G|PG|PG-?13|R|X)"
		difficulty = set()

		if len(routeDifficultyCopy) == 1:
			curatedRouteInfo["Difficulty"] = routeDifficultyCopy[0]
		elif len(routeDifficultyCopy) < 3:
			if re.match(pattern=difficultyPattern, string=routeDifficultyCopy[-1]):
				curatedRouteInfo["Difficulty"] = f"{routeDifficultyCopy[0]} {routeDifficultyCopy[-1]}"
			elif re.match(pattern=severityPattern, string=routeDifficultyCopy[-1]):
				curatedRouteInfo["Severity"] = routeDifficultyCopy[-1]
		else:
			if re.match(pattern=difficultyPattern, string=routeDifficultyCopy[-1]):
				curatedRouteInfo["Difficulty"] = f"{routeDifficultyCopy[0]} {routeDifficultyCopy[-1]}"
			elif re.match(pattern=severityPattern, string=routeDifficultyCopy[-1]):
				if re.match(pattern=difficultyPattern, string=routeDifficultyCopy[-2]):
					curatedRouteInfo["Difficulty"] = f"{routeDifficultyCopy[0]} {routeDifficultyCopy[-2]}"
				else:
					curatedRouteInfo["Difficulty"] = routeDifficultyCopy[0]
				curatedRouteInfo["Severity"] = routeDifficultyCopy[-1]
			else:
				curatedRouteInfo["Difficulty"] = routeDifficultyCopy[0]

		while routeInfoCopy:
			info = routeInfoCopy.pop(0)

			if info.strip().lower() in types:
				if "Type" in curatedRouteInfo.keys():
					curatedRouteInfo["Type"] += f", {info.strip()}"
				else:
					curatedRouteInfo["Type"] = info.strip()

			if re.match(pattern=r"\d+\sft", string=info.strip().lower()):
				curatedRouteInfo["Height"] = info.strip()

			if "Pitches".lower() in info.lower():
				curatedRouteInfo["Pitches"] = info.strip()

			if "Grade".lower() in info.lower():
				curatedRouteInfo["Grade"] = info.strip()

		curatedRouteInfo["Rating"] = routeRatingCopy[0]
		curatedRouteInfo["VoteCount"] = routeRatingCopy[1]

		return curatedRouteInfo




if __name__ == "__main__":
	scraper = MountainScraper(["California"], "https://www.mountainproject.com/area/113804909/southwest-face")
	# scraper = MountainScraper(["Colorado"], "https://www.mountainproject.com/area/105746940/castle-rocklower-falls-ice")
	scraper.findSubordinates(scraper.parentAreas)