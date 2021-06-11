# MountainProjectScraper.py

import os
import requests
import re
import json
from bs4 import BeautifulSoup


class MountainScraper(object):
	def __init__(self, startingPage: any([None, str]) = None, outputDirectoryRoot: str = "./RawData/",
				 useSubDirs: bool = True) -> None:
		self.startingPage = startingPage if startingPage is not None else "https://www.mountainproject.com/route-guide"
		self.outputDirectoryRoot = outputDirectoryRoot
		self.outputDirectory = outputDirectoryRoot
		self.useSubDirs = useSubDirs

		os.makedirs(self.outputDirectoryRoot, exist_ok=True)

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
					"ParentAreaId": None,  # Not sure what to put here. We could go fetch it...
					"URL": self.startingPage,
					"HTML": requests.get(self.startingPage).text
				}
			]

		# self.exportToJSON(self.parentAreas, "Area")

	def processParentPages(self) -> None:
		for area in self.parentAreas:
			currentAreaId = area["AreaId"]
			soup = BeautifulSoup(area["HTML"], "html.parser")
			title = soup.find("h1")
			children = [child.text.strip() for child in title.findChildren()]
			areaName = " ".join(word.strip() for word in title.text.split() if word not in children)

			if self.useSubDirs:
				self.outputDirectory = self.outputDirectoryRoot + \
									   ("" if self.outputDirectoryRoot[-1] == "/" else "/") + areaName + "/"

				os.makedirs(self.outputDirectory, exist_ok=True)

			areaInfo = [
				area
			]

			self.exportToJSON(areaInfo, "Area")
			self.findSubordinates(areaInfo)

	def findSubordinates(self, parentAreas: list[dict], parentAreaId: any([None, int]) = None) -> None:
		for area in parentAreas:
			currentAreaId = area["AreaId"]
			soup = BeautifulSoup(area["HTML"], "html.parser")

			# Determine if this is an empty area
			if "This area is empty".upper() in soup.find(class_="mp-sidebar").text.upper():
				continue

			# Determine if we have found routes yet
			hasRoutes = soup.find(class_="mp-sidebar").find(id="left-nav-route-table") is not None

			if hasRoutes:
				self.findRoutes(area, currentAreaId)
			else:
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

	def findRouteStats(self, routeId: int, url: str, parentAreaId: int) -> None:
		url = url.replace("/route/", "/route/stats/")
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

	def exportToJSON(self, data: list[dict], dataType: str) -> None:
		if dataType.upper() == "Area".upper():
			file = open(self.outputDirectory + "Areas.json", "a")
		elif dataType.upper() == "Route".upper():
			file = open(self.outputDirectory + "Routes.json", "a")
		elif dataType.upper() == "Stats".upper():
			file = open(self.outputDirectory + "Stats.json", "a")
		else:
			return

		for jsonData in data:
			jsonContent = json.dumps(jsonData, indent=None, separators=(",", ":"))
			print(jsonContent, file=file)

		file.close()


if __name__ == "__main__":
	# scraper = MountainScraper("https://www.mountainproject.com/area/113804909/southwest-face") # Trad/Aid
	# scraper = MountainScraper("https://www.mountainproject.com/area/105746940/castle-rocklower-falls-ice") # Trad/Ice/Mixed
	# scraper = MountainScraper("https://www.mountainproject.com/area/111951436/andrew-molera-sp-beach") # Bouldering
	# scraper = MountainScraper("https://www.mountainproject.com/area/105810437/first-tier") # Sport
	# scraper = MountainScraper("https://www.mountainproject.com/area/105877031/mount-rainier") # Snow
	# print(scraper.parentAreas)

	# startingPages = [
	# 	"https://www.mountainproject.com/area/105744267/shelf-road",
	# 	"https://www.mountainproject.com/area/105744222/boulder-canyon",
	# 	"https://www.mountainproject.com/area/105833381/yosemite-national-park",
	# 	"https://www.mountainproject.com/area/105720495/joshua-tree-national-park",
	# 	"https://www.mountainproject.com/area/105744246/eldorado-canyon-sp"
	# ]

	# for startingPage in startingPages:
	scraper = MountainScraper(outputDirectoryRoot="./TestFolder/")
	scraper.processParentPages()
