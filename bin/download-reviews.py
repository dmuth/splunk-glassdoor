#!/usr/bin/env python3
#
# Vim: :set tabstop=4
#
# Download the comments from 1 or more businesses in Glassdoor
# and write them to one page per file
#


import argparse
import datetime
import json
import logging
import os
import re
import sys
from urllib.parse import urlparse


from bs4 import BeautifulSoup
import requests


logging.basicConfig(level = logging.INFO, format='%(asctime)s.%(msecs)03d: %(levelname)s: %(message)s',
	datefmt = '%Y-%m-%d %H:%M:%S'
	)


parser = argparse.ArgumentParser(description = "Download comments from a Glassdoor page")
parser.add_argument('urls', metavar = 'URL', type = str, nargs = '+',
                    help = '1 or more Glassdoor URLs to download the comments from')

args = parser.parse_args()

log_dir = os.path.dirname(os.path.realpath(__file__)) + "/../logs"


#
# Fetch a specific URL
#
def getHtml(url):

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

	business = soup.title.text.split(" | ")[0]
	business = re.sub(' Reviews$', '', business)
	business = re.sub("[^A-Za-z0-9 ]", "", business)
	
	for review in soup.find_all("li", {"class": "empReview"}):

		row = {}
		
		#
		# There is a timestamp available with seconds, but it's not
		# GMT, and I don't think I really need anything more specific
		# than a date for these purposes.
		#
		try:
			date = review.find_all("time")[0].text
		except IndexError:
			logging.info("Looks like this review doesn't have a timestamp. Probably a Featured Review.  That's fine, but we can't use it.  Skipping!")
			continue

		date_time_obj = datetime.datetime.strptime(date, '%b %d, %Y')
		row["date"] = date_time_obj.strftime("%Y-%m-%dT%H:%M:%S.000")

		row["business"] = business

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
# Get what page we're on from the URL 
#
def getPageFromUrl(url):

	retval = 1

	fields = url.split("_")
	if len(fields) > 1:
		fields = re.match(r'P([0-9]+)', fields[1])
		return( int(fields.group(1)) )

	return(retval)


#
# Take our start URL and a page number, generate a page's URL for it
#
def getUrlFromPage(url, page):

	fields = re.match(r'(.*?)(_P[0-9]+)?(.htm)', url)
	url_start = fields.group(1)
	url_end = fields.group(3)

	retval = url_start + "_P" + str(page) + url_end

	return(retval)


#
# Get a filename from our URL
#
def getFilenameFromUrl(url):

	retval = re.sub('[^0-9a-zA-Z]+', '-', url)
	return(retval)


#
# Download the reviews from a particular business and write them to a file for each page.
# Additional pages of reviews will be followed.
#
def getReviews(url):

	logging.info("Start URL: {}".format(url))

	# Get current logfiles
	files = os.listdir(log_dir)


	while True:
	
		page = getPageFromUrl(url)
		logging.info("Page: " + str(page))

		filename = log_dir + "/" + getFilenameFromUrl(url)
		filename_stop = filename + "-stop"

		#
		# We don't want to fetch pages if we can help it, so we
		# write a stopfile when we've reached the end of the reviews.
		# If we find it, we're done with reviews.
		#
		if os.path.exists(filename_stop):
			logging.info("Stop file {} exists, stopping!".format(filename_stop))
			break
		
		if os.path.exists(filename):
			logging.info("File {} already exists, skipping!".format(filename))
			page += 1
			url = getUrlFromPage(url, page)
			continue

		logging.info("Fetching URL: {}...".format(url))
		html = getHtml(url)
		soup = BeautifulSoup(html, 'html.parser')

		logging.info("Parsing URL: {}...".format(url))
		reviews = parseHtml(soup)
		logging.info("Fetched {} reviews".format(len(reviews)))

		f = open(filename, "w")
		for review in reviews:
			f.write(json.dumps(review) + "\n")
		f.close()
		logging.info("Wrote {} reviews to '{}'".format(len(reviews), filename))

		#
		# Because even the last page has a "next page" link that you can
		# click on, we have to check to see if we're on the last page
		# or else we'll fetch empty pages forever.
		#
		try:
			current_page = soup.find_all("li", 
				{"class": "pagination__PaginationStyle__current"})[0]
			last_page = soup.find_all("li", 
				{"class": "pagination__PaginationStyle__last"})[0]

		except IndexError:
			logging.warn("Caught an IndexError on soup.find_all(), bailing out.  Feel free to try this script again!")
			f = open(filename_stop, "w")
			f.close()
			break

		if current_page == last_page:
			logging.info("Yeah, we're on the last page.  Full stop.")
			f = open(filename_stop, "w")
			f.close()
			break

		#
		# Guess we're going to the next page!
		#
		page += 1
		url = getUrlFromPage(url, page)



#
# Our main entry point.
#
def main(args):

	for url in args.urls:
		getReviews(url)

main(args)


