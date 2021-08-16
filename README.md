# Mountain Project Scraper

## Motivation
Data is a great way to gain insight into many things. The goal of this project is to use data sourced from the climbing
community to gain insights into the distributions of route completions, to-dos and average onsight/flash/redpoint
grades.

## The Data
I webscraped ~99% of the data contained on MountainProject area, route, and statistics pages. Unfortunately, since
comments are not loaded on a page until you scroll down to them, I was not able to obtain them via a simple requests
call. Instead, I used Selenium to scroll down on the page, wait for the comments to load, and then extract the HTML.
From the scraped HTML I extracted the content I was interested in. This includes:

* ~58k areas
  
* ~52k area comments

* ~250k routes

* ~315k route comments

* ~2.7M explicit route ratings

* ~5.5M route completions

* ~4.6M route to-dos

These features are extracted from the raw HTML and are dumped into JSON files.

From the JSON files, I populate a PostgreSQL database so that the data can be easily accessed.

## Statistical Analysis
