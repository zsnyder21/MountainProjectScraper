#MountainProjectScraper.py

import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

class MountainScraper(object):
	def __init__(self, statesToScrape: any((None, list[str]))) -> None:
		self.statesToScrape = [state.upper() for state in statesToScrape] if statesToScrape is not None else None
		self.parentAreas = {
			strong.find("a").text : strong.find("a")["href"] for strong in BeautifulSoup(requests.get("https://www.mountainproject.com/").text, "html.parser")
				.find(id="route-guide").find_all("strong") if self.statesToScrape is None or strong.find("a").text.upper() in self.statesToScrape
		}

	def findSubAreas(self, parentAreas: dict[str : str], parentAreaId: any([None, int]) = None) -> None:
		for parentArea, url in parentAreas.items():
			areaId = int(re.search(pattern=r"\d+", string=url).group(0))
			soup = BeautifulSoup(requests.get(url).text, "html.parser")

			# Determine if we have found routes yet or not
			hasRoutes = "Routes".upper() in soup.find(class_="mp-sidebar").find("h3").text.upper()

			if hasRoutes:
				self.findRoutes(areaId, url)
			else:
				subAreas = {subArea.text : subArea["href"] for subArea in soup.find(class_="max-height max-height-md-0 max-height-xs-400").findAll("a")}
				print(f"{parentArea} has {'routes' if hasRoutes else 'sub areas'}.")
				self.findSubAreas(subAreas, areaId)

			break

	def findRoutes(self, areaId: int, url: str) -> None:
		soup = BeautifulSoup(requests.get(url).text, "html.parser")

		routes = {route.text : route["href"] for route in soup.find(class_="max-height max-height-md-0 max-height-xs-400").findAll("a") if route["href"] != "#"}



		for route, url in routes.items():
			print(route + ": " + url)
			routeId = int(re.search(pattern=r"\d+", string=url).group(0))
			self.findRouteTicks(routeId, url)

			break


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




if __name__ == "__main__"
	scraper = MountainScraper(["California"])
	scraper.findSubAreas(scraper.parentAreas)