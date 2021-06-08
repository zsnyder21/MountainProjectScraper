# MountainProjectScraper.py

import requests
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime


class MountainScraper(object):
	def __init__(self, startingPage: any([None, str]) = None) -> None:
		self.startingPage = startingPage if startingPage is not None else "https://www.mountainproject.com/route-guide"

		if startingPage is None:
			self.parentAreas = [
				{
					"AreaId": int(re.search(pattern=r"\d+", string=strong.find("a")["href"]).group(0)),
					"ParentAreaId": None,
					"URL": strong.find("a")["href"],
					"HTML": requests.get(strong.find("a")["href"]).text
				}
				for strong in
				BeautifulSoup(requests.get(self.startingPage, params={}).text, "html.parser").find(id="route-guide")
					.find_all("strong")
			]

		else:
			self.parentAreas = [
				{
					"AreaId": int(re.search(pattern=r"\d+", string=self.startingPage).group(0)),
					"ParentAreaId": -1,  # Not sure what to put here. We could go fetch it...
					"URL": self.startingPage,
					"HTML": requests.get(self.startingPage).text
				}
			]

		self.exportToJSON(self.parentAreas, "Area")

	def findSubordinates(self, parentAreas: list[dict], parentAreaId: any([None, int]) = None) -> None:
		for area in parentAreas:
			currentAreaId = area["AreaId"]
			currentURL = area["URL"]
			soup = BeautifulSoup(area["HTML"], "html.parser")

			# Determine if this is an empty area
			if "This area is empty".upper() in soup.find(class_="mp-sidebar").text.upper():
				return

			# Determine if we have found routes yet
			hasRoutes = "Routes".upper() in soup.find(class_="mp-sidebar").find("h3").text.upper()

			if hasRoutes:
				self.findRoutes(area, currentAreaId)
			else:
				subAreas = {subArea.text: subArea["href"] for subArea in
							soup.find(class_="max-height max-height-md-0 max-height-xs-400")
								.findAll("a")}
				subAreaInfo = [
					{
						"AreaId": int(re.search(pattern=r"\d+", string=subArea["href"]).group(0)),
						"ParentAreaId": currentAreaId,
						"URL": subArea["href"],
						"HTML": requests.get(subArea["href"]).text
					}
					for subArea in soup.find(class_="max-height max-height-md-0 max-height-xs-400").findAll("a")
				]
				self.exportToJSON(subAreaInfo, "Area")

				self.findSubordinates(subAreaInfo, currentAreaId)

			# break

	def findRoutes(self, area: dict, parentAreaId: int) -> None:
		soup = BeautifulSoup(area["HTML"], "html.parser")

		routeInfo = [
			{
				"RouteId": int(re.search(pattern=r"\d+", string=route["href"]).group(0)),
				"ParentAreaId": parentAreaId,
				"URL": route["href"],
				"HTML": requests.get(route["href"]).text
			}
			for route in soup.find(class_="max-height max-height-md-0 max-height-xs-400").findAll("a") if
			route["href"] != "#"
		]

		self.exportToJSON(routeInfo, "Route")

		for route in routeInfo:
			self.findRouteStats(route["RouteId"], route["URL"], route["ParentAreaId"])

		return None

		routes = {route.text: route["href"] for route in
				  soup.find(class_="max-height max-height-md-0 max-height-xs-400").findAll("a") if route["href"] != "#"}

		for route, url in routes.items():
			print(route + ": " + url)
			return None
			routeId = int(re.search(pattern=r"\d+", string=url).group(0))
			soup = BeautifulSoup(requests.get(url).text, "html.parser")

			routeType = soup.find(class_="description-details").find("tr").text

			difficultyInfo = self.getRouteDifficulty(url)  # soup.find(class_="inline-block mr-2") # .text.split()
			print(difficultyInfo)

			# print(routeDifficultyInfo)
			routeTypeInfo = routeType.split(":")[1].strip().split(",")
			ratingInfo = soup.find(id=f"starsWithAvgText-{routeId}").text.split()[1:4:2]

	# print(self.curateRouteInfo(route, routeId, routeTypeInfo, routeDifficultyInfo, ratingInfo))
	# grade = soup.find(class_="rateYDS").text.split()[0]
	# safety = soup.find()
	# print(grade)

	# self.findRouteTicks(routeId, url)

	# break

	def findRouteStats(self, routeId: int, url: str, parentAreaId: int) -> None:
		url = url.replace("/route/", "/route/stats/")
		soup = BeautifulSoup(requests.get(url).text, "html.parser")
		# ticksTable = soup.find(
		# 	class_="col-lg-6 col-sm-12 col-xs-12 mt-2 max-height max-height-md-1000 max-height-xs-400")

		# if ticksTable is None:
		# 	return

		routeStats = [
			{
				"RouteId": routeId,
				"ParentAreaId": parentAreaId,
				"URL": url,
				"HTML": requests.get(url).text
			}
		]

		self.exportToJSON(routeStats, "Stats")

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
				"UserName": userName,
				"UserId": userId,
				"TickDate": tickInfo[0],
				"TickDatetime": datetime.strptime(tickInfo[0], "%b %d, %Y") if tickInfo[
																				   0].lower() != "-no date-" else None,
				"TickInfo": None if len(tickInfo) < 2 else tickInfo[1]
			}

			print("     ", userTick)

	def exportToJSON(self, data: list[dict], dataType: str) -> None:
		jsonContent = json.dumps(data, indent=4)

		if dataType.upper() == "Area".upper():
			file = open("./data/Areas.json", "a")
			print(jsonContent, file=file)

		if dataType.upper() == "Route".upper():
			file = open("./data/Routes.json", "a")
			print(jsonContent, file=file)

		if dataType.upper() == "Stats".upper():
			file = open("./data/Stats.json", "a")
			print(jsonContent, file=file)

		file.close()

	def getRouteDifficulty(self, url: str) -> str:
		soup = BeautifulSoup(requests.get(url).text, "html.parser")

	def curateRouteInfo(self, routeName: str, routeId: int, routeInfo: list[str], routeDifficulty: list[str],
						routeRating: list[str]) -> dict:
		routeInfoCopy = routeInfo.copy()
		routeDifficultyCopy = routeDifficulty.copy()
		routeRatingCopy = routeRating.copy()
		curatedRouteInfo = {"Id": routeId, "Name": routeName}
		routeKeys = ["Id", "Name", "Difficulty", "Severity", "Type", "Height", "Pitches", "Grade", "Rating",
					 "VoteCount"]
		types = {"trad", "sport", "toprope", "boulder", "ice", "aid", "mixed", "alpine"}
		difficultyPattern = r"(?:A|C|M|AI|WI|Mod.|Steep|Snow)\d?(?:\+|-)?"
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
			if re.match(pattern=severityPattern, string=routeDifficultyCopy[-1]):
				if re.match(pattern=difficultyPattern, string=routeDifficultyCopy[-2]):
					curatedRouteInfo["Difficulty"] = f"{routeDifficultyCopy[0]} {routeDifficultyCopy[-2]}"
				else:
					curatedRouteInfo["Difficulty"] = routeDifficultyCopy[0]
				curatedRouteInfo["Severity"] = routeDifficultyCopy[-1]
			elif re.match(pattern=difficultyPattern, string=routeDifficultyCopy[-1]):
				curatedRouteInfo["Difficulty"] = f"{routeDifficultyCopy[0]} {routeDifficultyCopy[-1]}"
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

		return {key: curatedRouteInfo[key] if key in curatedRouteInfo.keys() else None for key in routeKeys}


if __name__ == "__main__":
	# scraper = MountainScraper("https://www.mountainproject.com/area/113804909/southwest-face") # Trad/Aid
	# scraper = MountainScraper("https://www.mountainproject.com/area/105746940/castle-rocklower-falls-ice") # Trad/Ice/Mixed
	# scraper = MountainScraper("https://www.mountainproject.com/area/111951436/andrew-molera-sp-beach") # Bouldering
	# scraper = MountainScraper("https://www.mountainproject.com/area/105810437/first-tier") # Sport
	# scraper = MountainScraper("https://www.mountainproject.com/area/105877031/mount-rainier") # Snow
	# print(scraper.parentAreas)

	scraper = MountainScraper()
	scraper.findSubordinates(scraper.parentAreas)
