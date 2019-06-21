#!/usr/bin/env python3
#
# Vim: :set tabstop=4
#
# Download the comments from 1 or more venues in Yelp and write them to stdout
#


import argparse
import datetime
import json
import logging
import re
import sys
from urllib.parse import urlparse


from bs4 import BeautifulSoup
import requests


logging.basicConfig(level = logging.INFO, format='%(asctime)s.%(msecs)03d: %(levelname)s: %(message)s',
	datefmt = '%Y-%m-%d %H:%M:%S'
	)


parser = argparse.ArgumentParser(description = "Download comments from a Yelp page")
parser.add_argument('urls', metavar = 'URL', type = str, nargs = '+',
                    help = '1 or more Yelp URLs to download the comments from')

args = parser.parse_args()


#
# Fetch a specific URL
#
def getHtml(url):

	#r = requests.get(url)
	headers = {
		"User-Agent": "Splunk Glassdoor/1.0 http://github.com/dmuth"
		}
	r = requests.get(url, headers = headers)
	if r.status_code != 200:
		raise Exception("Non-200 HTTP response on URL {}: {}".format(url, r.status_code))

	return(r.text)


#
# Parse HTML from a specific review and return an array of reviews
#
def parseHtml(soup):

	retval = []

	venue = soup.title.text.split(" | ")[0]
	venue = re.sub("[^A-Za-z0-9 ]", "", venue)
	
	for review in soup.find_all("li", {"class": "empReview"}):

		row = {}
		
		#
		# There is a timestamp available with seconds, but it's not
		# GMT, and I don't think I really need anything more specific
		# than a date for these purposes.
		#
		date = review.find_all("time")[0].text
		date_time_obj = datetime.datetime.strptime(date, '%b %d, %Y')
		row["date"] = date_time_obj.strftime("%Y-%m-%dT%H:%M:%S.000")

		row["venue"] = venue

		row["rating"] = review.find_all("span", {"class": "value-title"})[0]["title"]

		text = review.find_all("div", {"class": "mt-md"})
		row["pros"] = text[0].find_all("p")[1].text
		row["cons"] = text[1].find_all("p")[1].text
		row["advice_to_management"] = ""
		if len(text) >= 3:
			row["advice_to_management"] = text[2].find_all("p")[1].text

		retval.append(row)


	return(retval)


#
# Download the reviews from a particular venue.
# Additional pages of reviews will be followed. 
#
def getReviews(url):

	retval = []

	#
	# Grab the base URL since next page links are relative
	#
	parsed_uri = urlparse(url)
	url_base = parsed_uri.scheme + "://" + parsed_uri.netloc

	while True:

		logging.info("Fetching URL: {}...".format(url))
		html = getHtml(url)
		soup = BeautifulSoup(html, 'html.parser')

		logging.info("Parsing URL: {}...".format(url))
		reviews = parseHtml(soup)
		logging.info("Fetched {} reviews".format(len(reviews)))
		retval = retval + reviews

		next_page = soup.find_all("a", {"class": "pagination__ArrowStyle__nextArrow"})
		url = url_base + next_page[0]["href"]

		#
		# Because even the last page has a "next page" link that you can
		# click on, we have to check to see if we're on the last page
		# or else we'll fetch empty pages forever.
		#
		current_page = soup.find_all("li", {"class": "pagination__PaginationStyle__current"})[0]
		last_page = soup.find_all("li", {"class": "pagination__PaginationStyle__last"})[0]

		if current_page == last_page:
			logging.info("Yeah, we're on the last page.  Full stop.")
			break

		elif next_page:
			logging.info("Found next page: {}".format(url))

		else:
			logging.info("No more pages found, bailing out!")
			break


	return(retval)


#
# Print up our reviews as JSON, one event per line.
#
def printReviews(reviews):

	for review in reviews:
		print(json.dumps(review))


#
# Our main entry point.
#
def main(args):

	for url in args.urls:
		reviews = getReviews(url)
		logging.info("Fetched {} reviews in total from URL {}".format(len(reviews), url))
		printReviews(reviews)


main(args)


