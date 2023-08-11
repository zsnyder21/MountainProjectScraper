import json
import os
import re
import requests
import selenium.common.exceptions

from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class MountainScraper:
	def __init__(self, webdriverExecutable: str = None) -> None:
		self.webdriverExecutable = webdriverExecutable or "../../chromedriver.exe"
		self.startingPage = None
		self.outputDirectoryRoot = None
		self.outputDirectory = None
		self.areasToScrape = None
		self.useSubDirs = None
		self.areasScraped = set()
		self.parentAreas = list()
		self.implicitWaitTime = 10  # Seconds

		self.chromeOptions = Options()
		# chrome_options.add_argument("--headless")
		self.driver = webdriver.Chrome(options=self.chromeOptions, executable_path=self.webdriverExecutable)
		# self.driver.implicitly_wait(self.implicitWaitTime)
		self.pagesVisited = 0
		self.pagesThreshold = 1000  # Instantiate new webdriver after this many pages have been visited

	def _visit(self, url: str) -> None:
		"""
		Tells the webdriver to visit the supplied url

		:param url: Url to tell the webdriver to visit
		"""
		pageLoaded = False
		while not pageLoaded:
			if self.pagesVisited > self.pagesThreshold:
				print("Refreshing driver...")
				self.driver.quit()
				self.driver = webdriver.Chrome(options=self.chromeOptions, executable_path=self.webdriverExecutable)
				# self.driver.implicitly_wait(self.implicitWaitTime)
				self.pagesVisited = 0

			try:
				self.driver.get(url)
				pageLoaded = WebDriverWait(self.driver, self.implicitWaitTime).until(
					lambda d: d.execute_script("return document.readyState") == "complete"
				)
			except selenium.common.exceptions.TimeoutException as e:
				print(f"Refreshing because took too long to load {url}")
				self.driver.refresh()

			# Check that we didn't get a bad request or server error
			if "502 Server Error" in self.driver.page_source or "Too Many Requests" in self.driver.page_source:
				print(f"{url} responded too many requests for 502 server error - trying again")
				pageLoaded = False

			self.pagesVisited += 1

	@staticmethod
	def getCurrentTime() -> str:
		return str(datetime.now())

	def setInitialState(self, startingPage: any([None, str]) = None, outputDirectoryRoot: str = "./data/Raw/",
				 areasToScrape: set[str] = None, useSubDirs: bool = True):
		self.startingPage = startingPage if startingPage is not None else "https://www.mountainproject.com/route-guide"
		self.outputDirectoryRoot = outputDirectoryRoot
		self.outputDirectory = outputDirectoryRoot
		self.areasToScrape = areasToScrape
		self.useSubDirs = useSubDirs

		os.makedirs(self.outputDirectoryRoot, exist_ok=True)

		if startingPage is None:
			self._visit(self.startingPage)
			# self.driver.get(self.startingPage)
			routeGuide = BeautifulSoup(requests.get(self.startingPage).text, "html.parser").find(id="route-guide")

			for strong in routeGuide.find_all("strong"):
				areaName = strong.find("a").text
				if self.areasToScrape is not None and areaName not in self.areasToScrape or areaName in self.areasScraped:
					continue

				pageURL = strong.find("a")["href"]
				areaId = int(re.search(pattern=r"\d+", string=pageURL).group(0))
				parentAreaId = None
				pageLoaded = False

				while not pageLoaded:
					try:
						self._visit(pageURL)
						# self.driver.get(pageURL)
						pageLoaded = True
					except selenium.common.exceptions.TimeoutException as e:
						print(f"Took too long to load {pageURL}. Trying again...")

				try:
					# commentCount = self.driver.find_element_by_class_name("comment-count")
					commentCount = self.driver.find_element(by=By.CLASS_NAME, value="comment-count")
					hasComments = commentCount.text != "0 Comments"
				except selenium.common.exceptions.NoSuchElementException as e:
					print(f"We cannot locate a comment count element for page {pageURL}, likely due to access issues")
					hasComments = False

				if hasComments:
					commentsFound = False
					while not commentsFound:
						# html = self.driver.find_element_by_tag_name("html")
						html = self.driver.find_element(by=By.TAG_NAME, value="html")
						html.send_keys(Keys.END)

						try:
							WebDriverWait(self.driver, self.implicitWaitTime).until(EC.presence_of_element_located((By.XPATH,
								"//div[@class='comments-body']/div[@class='comment-list']/table[@class='main-comment width100']")))

							commentsFound = True
						except selenium.common.exceptions.TimeoutException as e:
							print(f"AreaId: {areaId}, URL: {pageURL} - could not find comment element")
							self.driver.refresh()

				pageHTML = self.driver.page_source

				pageInfo = {
					"AreaId": areaId,
					"ParentAreaId": parentAreaId,
					"DateScraped": self.getCurrentTime(),
					"URL": pageURL,
					"HTML": pageHTML
				}
				self.areasScraped.add(areaName)
				self.parentAreas.append(pageInfo)

		else:
			pageURL = self.startingPage
			areaId = int(re.search(pattern=r"\d+", string=pageURL).group(0))
			parentAreaId = None
			pageLoaded = False

			while not pageLoaded:
				try:
					self._visit(pageURL)
					# self.driver.get(pageURL)
					pageLoaded = True
				except selenium.common.exceptions.TimeoutException as e:
					print(f"Took too long to load {pageURL}. Trying again...")

			try:
				# commentCount = self.driver.find_element_by_class_name("comment-count")
				commentCount = self.driver.find_element(by=By.CLASS_NAME, value="comment-count")
				hasComments = commentCount.text != "0 Comments"
			except selenium.common.exceptions.NoSuchElementException as e:
				print(f"We cannot locate a comment count element for page {pageURL}, likely due to access issues")
				hasComments = False

			if hasComments:
				commentsFound = False
				while not commentsFound:
					# html = self.driver.find_element_by_tag_name("html")
					html = self.driver.find_element(by=By.TAG_NAME, value="html")
					html.send_keys(Keys.END)

					try:
						WebDriverWait(self.driver, self.implicitWaitTime).until(EC.presence_of_element_located((By.XPATH,
							"//div[@class='comments-body']/div[@class='comment-list']/table[@class='main-comment width100']")))

						commentsFound = True
					except selenium.common.exceptions.TimeoutException as e:
						print(f"AreaId: {areaId}, URL: {pageURL} - could not find comment element")
						self.driver.refresh()

			pageHTML = self.driver.page_source

			pageInfo = {
				"AreaId": areaId,
				"ParentAreaId": parentAreaId,
				"DateScraped": self.getCurrentTime(),
				"URL": pageURL,
				"HTML": pageHTML
			}

			self.parentAreas.append(pageInfo)



	def scrape(self, startingPage: any([None, str]) = None, outputDirectoryRoot: str = "./data/Raw/",
				 areasToScrape: set[str] = None, useSubDirs: bool = True) -> None:
		self.setInitialState(
			startingPage=startingPage,
			outputDirectoryRoot=outputDirectoryRoot,
			areasToScrape=areasToScrape,
			useSubDirs=useSubDirs
		)

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

		self.driver.close()

	def findSubordinateAreas(self, areas: list[dict], parentAreaId: any([None, int]) = None) -> None:
		for area in areas:
			currentAreaId = area["AreaId"]
			soup = BeautifulSoup(area["HTML"], "html.parser")
			subAreaInfo = list()

			# Determine if this is an empty area
			sidebar = soup.find(class_="mp-sidebar")
			if sidebar is None or (sidebar is not None and "This area is empty".upper() in sidebar.text.upper()):
				continue

			# Determine if we have found routes yet
			hasRoutes = soup.find(class_="mp-sidebar").find(id="left-nav-route-table") is not None

			if hasRoutes:
				self.findRoutes(area, currentAreaId)
			else:
				for subArea in soup.find(class_="max-height max-height-md-0 max-height-xs-400").findAll("a"):
					pageURL = subArea["href"]
					areaId = int(re.search(pattern=r"\d+", string=pageURL).group(0))
					pageLoaded = False

					while not pageLoaded:
						try:
							self._visit(pageURL)
							# self.driver.get(pageURL)
							pageLoaded = True
						except selenium.common.exceptions.TimeoutException as e:
							print(f"Took too long to load {pageURL}. Trying again...")

					try:
						# commentCount = self.driver.find_element_by_class_name("comment-count")
						commentCount = self.driver.find_element(by=By.CLASS_NAME, value="comment-count")
						hasComments = commentCount.text != "0 Comments"
					except selenium.common.exceptions.NoSuchElementException as e:
						print(f"We cannot locate a comment count element for page {pageURL}, likely due to access issues")
						hasComments = False

					if hasComments:
						commentsFound = False
						while not commentsFound:
							# html = self.driver.find_element_by_tag_name("html")
							html = self.driver.find_element(by=By.TAG_NAME, value="html")
							html.send_keys(Keys.END)

							try:
								WebDriverWait(self.driver, self.implicitWaitTime).until(EC.presence_of_element_located((By.XPATH,
									"//div[@class='comments-body']/div[@class='comment-list']/table[@class='main-comment width100']")))

								commentsFound = True
							except selenium.common.exceptions.TimeoutException as e:
								print(f"AreaId: {areaId}, URL: {pageURL} - could not find comment element")
								self.driver.refresh()

					pageHTML = self.driver.page_source

					pageInfo = {
						"AreaId": areaId,
						"ParentAreaId": currentAreaId,
						"DateScraped": self.getCurrentTime(),
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
			pageLoaded = False

			while not pageLoaded:
				try:
					self._visit(pageURL)
					# self.driver.get(pageURL)
					pageLoaded = True
				except selenium.common.exceptions.TimeoutException as e:
					print(f"Took too long to load {pageURL}. Trying again...")

			try:
				# commentCount = self.driver.find_element_by_class_name("comment-count")
				commentCount = self.driver.find_element(by=By.CLASS_NAME, value="comment-count")
				hasComments = commentCount.text != "0 Comments"
			except selenium.common.exceptions.NoSuchElementException as e:
				print(f"We cannot locate a comment count element for page {pageURL}, likely due to access issues")
				hasComments = False

			if hasComments:
				commentsFound = False
				while not commentsFound:
					# html = self.driver.find_element_by_tag_name("html")
					html = self.driver.find_element(by=By.TAG_NAME, value="html")
					html.send_keys(Keys.END)

					try:
						WebDriverWait(self.driver, self.implicitWaitTime).until(EC.presence_of_element_located((By.XPATH,
							"//div[@class='comments-body']/div[@class='comment-list']/table[@class='main-comment width100']")))

						commentsFound = True
					except selenium.common.exceptions.TimeoutException as e:
						print(f"RouteId: {routeId}, URL: {pageURL} - could not find comment element")
						self.driver.refresh()

			pageHTML = self.driver.page_source

			pageInfo = {
				"RouteId": routeId,
				"ParentAreaId": parentAreaId,
				"DateScraped": self.getCurrentTime(),
				"URL": pageURL,
				"HTML": pageHTML
			}

			routeInfo.append(pageInfo)

		self.exportToJSON(routeInfo, "Route")

		for route in routeInfo:
			self.findRouteStats(route["RouteId"], route["URL"], route["ParentAreaId"])

	def findRouteStats(self, routeId: int, url: str, parentAreaId: int) -> None:
		pageURL = url.replace("/route/", "/route/stats/")
		pageLoaded = False
		tableFound = False
		allStatsLoaded = False
		while not pageLoaded:
			try:
				self._visit(pageURL)
				# self.driver.get(pageURL)
				pageLoaded = True
			except selenium.common.exceptions.TimeoutException as e:
				print(f"Took too long to load {pageURL}. Trying again...")

		while not tableFound:
			try:
				WebDriverWait(self.driver, self.implicitWaitTime).until(EC.presence_of_element_located((
					By.CLASS_NAME,
					"onx-stats-table"
				)))

				# Once the stats are loaded, we will have exactly 4 elements indicating the number of
				# star ratings, suggested ratings, on to-do lists, and ticks
				statsTable = self.driver.find_element_by_class_name(name="onx-stats-table")
				texts = statsTable.find_elements(by=By.XPATH, value="//div/div/div/h3/span[@class='small text-muted']")
				tableFound = len(texts) == 4

			except selenium.common.exceptions.TimeoutException as e:
				print(f"RouteId: {routeId}, URL: {pageURL} - could not find table element")
				self.driver.refresh()

		totalRows = sum(int(text.text.replace(",", "")) for text in texts)
		buttons = {
			"sc-jSUZER DReUW": None,
			"sc-gswNZR exFoxa": None,
			"sc-gKPRtg bEeJli": None,
			"sc-bcXHqe ZOkfO": None
		}

		while not allStatsLoaded:
			statsTable = self.driver.find_element_by_class_name(name="onx-stats-table")
			html = self.driver.find_element(by=By.TAG_NAME, value="html")
			html.send_keys(Keys.END)

			for buttonId in buttons:
				try:
					buttons[buttonId] = statsTable.find_element(by=By.XPATH, value=f"//div/div/div/div[@class='{buttonId}']/button[@type='button']")
				except selenium.common.exceptions.NoSuchElementException as e:
					buttons[buttonId] = None

			for buttonId, button in buttons.items():
				if buttons[buttonId] is not None and button.is_enabled():
					try:
						button.send_keys(Keys.ENTER)
					except selenium.common.exceptions.ElementNotInteractableException as e:
						pass

			rowsFound = len(statsTable.find_elements(by=By.TAG_NAME, value="tr"))
			allStatsLoaded = rowsFound == totalRows

		routeStats = [
			{
				"RouteId": routeId,
				"ParentAreaId": parentAreaId,
				"URL": pageURL,
				"DateScraped": self.getCurrentTime(),
				"HTML": self.driver.page_source
			}
		]

		self.exportToJSON(routeStats, "Stats")

	def exportToJSON(self, data: list[dict], dataType: str) -> None:
		if dataType.upper() == "Area".upper():
			fileName = self.outputDirectory + "Areas.json"
		elif dataType.upper() == "Route".upper():
			fileName = self.outputDirectory + "Routes.json"
		elif dataType.upper() == "Stats".upper():
			fileName = self.outputDirectory + "Stats.json"
		else:
			return

		with open(fileName, "a") as file:
			for jsonData in data:
				jsonContent = json.dumps(jsonData, indent=None, separators=(",", ":"))
				print(jsonContent, file=file)


if __name__ == "__main__":
	areasToScrape = {
		"Alabama",
		"Alaska",
		"Arizona",
		"Arkansas",
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
		"International",
		"* In Progress"
	}

	scraper = MountainScraper()
	scraper.scrape(
		outputDirectoryRoot="../../data/20230810/Raw/",
		areasToScrape=areasToScrape,
		# startingPage=r"https://www.mountainproject.com/area/105833490/middle-cathedral-rock"
	)
