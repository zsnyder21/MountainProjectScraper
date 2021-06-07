#MountainProjectScraper.py

import requests
from bs4 import BeautifulSoup
import re

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

		print(areaId, "\r\n", routes)

		for route, url in routes.items():
			routeId = int(re.search(pattern=r"\d+", string=url).group(0))
			self.findRouteTicks(routeId, url)

			break


	def findRouteTicks(self, routeId: int, url: str) -> None:
		url = url.replace("/route/", "/route/stats/")
		soup = BeautifulSoup(requests.get(url).text, "html.parser")
		pattern = re.compile(r"Ticks\s*")
		ticks = soup.find("h2", text=pattern)
		print(ticks)

# test = requests.get("https://www.mountainproject.com/")
# # print(test.text)
# soup = BeautifulSoup(test.text, "html.parser")
# route_guide = soup.find(id="route-guide")
# strong = route_guide.find_all("strong")
# test = strong[0].find("a")
# print(test.text)

# test = BeautifulSoup(requests.get("https://www.mountainproject.com/").text, "html.parser").find(id="route-guide").find_all("strong")
# print(test)
# print({strong.text : strong["href"] for strong in test})

scraper = MountainScraper(["California"])
scraper.findSubAreas(scraper.parentAreas)