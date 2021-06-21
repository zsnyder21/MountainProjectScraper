# MountainProjectScraper.py

import os
import requests
import re
import json

import selenium.common.exceptions
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class MountainScraper(object):
	def __init__(self, startingPage: any([None, str]) = None, outputDirectoryRoot: str = "./RawData/",
				 areasToScrape: set[str] = None, useSubDirs: bool = True) -> None:
		self.startingPage = startingPage if startingPage is not None else "https://www.mountainproject.com/route-guide"
		self.outputDirectoryRoot = outputDirectoryRoot
		self.outputDirectory = outputDirectoryRoot
		self.areasToScrape = areasToScrape
		self.areasScraped = set()
		self.useSubDirs = useSubDirs
		self.parentAreas = list()

		chrome_options = Options()
		chrome_options.add_argument("--headless")
		self.driver = webdriver.Chrome(options=chrome_options)

		os.makedirs(self.outputDirectoryRoot, exist_ok=True)

		if startingPage is None:
			self.driver.get(self.startingPage)
			routeGuide = BeautifulSoup(requests.get(self.startingPage).text, "html.parser").find(id="route-guide")

			for strong in routeGuide.find_all("strong"):
				areaName = strong.find("a").text
				if self.areasToScrape is not None and areaName not in self.areasToScrape or areaName in self.areasScraped:
					continue

				pageURL = strong.find("a")["href"]
				areaId = int(re.search(pattern=r"\d+", string=pageURL).group(0))
				parentAreaId = None

				self.driver.get(pageURL)

				commentCount = self.driver.find_element_by_class_name("comment-count")
				hasComments = commentCount.text != "0 Comments"

				if hasComments:
					html = self.driver.find_element_by_tag_name("html")
					html.send_keys(Keys.END)
					WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH,
						"//div[@class='comments-body']/div[@class='comment-list']/table[@class='main-comment width100']")))

				pageHTML = self.driver.page_source

				pageInfo = {
					"AreaId": areaId,
					"ParentAreaId": parentAreaId,
					"URL": pageURL,
					"HTML": pageHTML
				}
				self.areasScraped.add(areaName)
				self.parentAreas.append(pageInfo)

		else:
			pageURL = self.startingPage
			areaId = int(re.search(pattern=r"\d+", string=pageURL).group(0))
			parentAreaId = None

			self.driver.get(pageURL)

			commentCount = self.driver.find_element_by_class_name("comment-count")
			hasComments = commentCount.text != "0 Comments"

			if hasComments:
				html = self.driver.find_element_by_tag_name("html")
				html.send_keys(Keys.END)
				WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH,
																					 "//div[@class='comments-body']/div[@class='comment-list']/table[@class='main-comment width100']")))

			pageHTML = self.driver.page_source

			pageInfo = {
				"AreaId": areaId,
				"ParentAreaId": parentAreaId,
				"URL": pageURL,
				"HTML": pageHTML
			}

			self.parentAreas.append(pageInfo)

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

				try:
					os.makedirs(self.outputDirectory, exist_ok=False)
				except FileExistsError as e:
					print(f"This area (AreaId = {area['AreaId']}) has already been scraped during this session.")
					continue

			areaInfo = [
				area
			]

			self.exportToJSON(areaInfo, "Area")
			self.findSubordinateAreas(areaInfo, currentAreaId)

	def findSubordinateAreas(self, areas: list[dict], parentAreaId: any([None, int]) = None) -> None:
		for area in areas:
			currentAreaId = area["AreaId"]
			soup = BeautifulSoup(area["HTML"], "html.parser")
			subAreaInfo = list()

			# Determine if this is an empty area
			if "This area is empty".upper() in soup.find(class_="mp-sidebar").text.upper():
				continue

			# Determine if we have found routes yet
			hasRoutes = soup.find(class_="mp-sidebar").find(id="left-nav-route-table") is not None

			if hasRoutes:
				self.findRoutes(area, currentAreaId)
			else:
				for subArea in soup.find(class_="max-height max-height-md-0 max-height-xs-400").findAll("a"):
					pageURL = subArea["href"]
					areaId = int(re.search(pattern=r"\d+", string=pageURL).group(0))

					self.driver.get(pageURL)

					try:
						commentCount = self.driver.find_element_by_class_name("comment-count")
						hasComments = commentCount.text != "0 Comments"
					except selenium.common.exceptions.NoSuchElementException as e:
						print(f"We cannot locate a comment count element for page {pageURL}, likely due to access issues")
						hasComments = False

					if hasComments:
						html = self.driver.find_element_by_tag_name("html")
						html.send_keys(Keys.END)
						try:
							WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH,
								"//div[@class='comments-body']/div[@class='comment-list']/table[@class='main-comment width100']")))
						except selenium.common.exceptions.TimeoutException as e:
							print(f"AreaId: {areaId} - could not find comment element")
					pageHTML = self.driver.page_source

					pageInfo = {
						"AreaId": areaId,
						"ParentAreaId": currentAreaId,
						"URL": pageURL,
						"HTML": pageHTML
					}

					subAreaInfo.append(pageInfo)

				self.exportToJSON(subAreaInfo, "Area")
				self.findSubordinateAreas(subAreaInfo, currentAreaId)

	def findRoutes(self, area: dict, parentAreaId: int) -> None:
		soup = BeautifulSoup(area["HTML"], "html.parser")
		routeInfo = list()

		for route in soup.find(class_="max-height max-height-md-0 max-height-xs-400").findAll("a"):
			if route["href"] == "#":
				continue

			pageURL = route["href"]
			routeId = int(re.search(pattern=r"\d+", string=pageURL).group(0))

			self.driver.get(pageURL)

			try:
				commentCount = self.driver.find_element_by_class_name("comment-count")
				hasComments = commentCount.text != "0 Comments"
			except selenium.common.exceptions.NoSuchElementException as e:
				print(f"We cannot locate a comment count element for page {pageURL}, likely due to access issues")
				hasComments = False

			if hasComments:
				html = self.driver.find_element_by_tag_name("html")
				html.send_keys(Keys.END)
				try:
					WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH,
						"//div[@class='comments-body']/div[@class='comment-list']/table[@class='main-comment width100']")))
				except selenium.common.exceptions.TimeoutException as e:
					print(f"RouteId: {routeId} - could not find comment element")
			pageHTML = self.driver.page_source

			pageInfo = {
				"RouteId": routeId,
				"ParentAreaId": parentAreaId,
				"URL": pageURL,
				"HTML": pageHTML
			}

			routeInfo.append(pageInfo)

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

	areasToScrape = {
		# "Alabama",
		# "Alaska",
		# "Arizona",
		# "Arkansas",
		"California",
		"Colorado",
		"Connecticut",
		"Delaware",
		"Florida",
		"Georgia",
		"Hawaii",
		"Idaho",
		"Illinois",
		"Indiana",
		"Iowa",
		"Kansas",
		"Kentucky",
		"Louisiana",
		"Maine",
		"Maryland",
		"Massachusetts",
		"Michigan",
		"Minnesota",
		"Mississippi",
		"Missouri",
		"Montana",
		"Nebraska",
		"Nevada",
		"New Hampshire",
		"New Jersey",
		"New Mexico",
		"New York",
		"North Carolina",
		"North Dakota",
		"Ohio",
		"Oklahoma",
		"Oregon",
		"Pennsylvania",
		"Rhode Island",
		"South Carolina",
		"South Dakota",
		"Tennessee",
		"Texas",
		"Utah",
		"Vermont",
		"Virginia",
		"Washington",
		"West Virginia",
		"Wisconsin",
		"Wyoming",
		"International"
		"* In Progress"
	}

	# for startingPage in startingPages:
	scraper = MountainScraper(outputDirectoryRoot="./RawDataComments/", areasToScrape=areasToScrape)
	# scraper = MountainScraper(startingPage=r"https://www.mountainproject.com/area/111860940/south-san-diego-county",
	# 						 outputDirectoryRoot="./RawDataTest")
	scraper.processParentPages()
