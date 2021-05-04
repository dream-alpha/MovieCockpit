#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2021 by dream-alpha
#
# In case of reuse of this source code please do not remove this copyright.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For more information on the GNU General Public License see:
# <http://www.gnu.org/licenses/>.


from Debug import logger
from Version import ID
import os
import json
from urllib2 import Request, urlopen, quote
import cPickle
from __init__ import _
from time import sleep
from Components.config import config
from FileUtils import readFile, writeFile, deleteFile
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit


SELECTION_ID = 1	# tmdb movie id
SELECTION_TYPE = 2	# movie or tvshow
SELECTION_URL = 4	# partial cover url
INFO_COVER_URL = 6	# full cover url
INFO_BACKDROP_URL = 7	# full backdrop url


class MovieTMDB():

	def __init__(self):
		return

	def getInfoPath(self, path):
		logger.debug("path: %s", path)
		info_path = os.path.splitext(path)[0] + ".txt"
		if config.plugins.moviecockpit.cover_flash.value:
			bookmark = MountCockpit.getInstance().getBookmark(ID, info_path)
			if bookmark:
				info_path = config.plugins.moviecockpit.cover_bookmark.value + info_path[len(bookmark):]
		logger.debug("info_path: %s", info_path)
		return info_path

	def saveInfo(self, info_path, info):
		logger.debug("path: %s, info: %s", info_path, info)
		if info:
			if config.plugins.moviecockpit.cover_replace_existing.value and os.path.isfile(info_path):
				deleteFile(info_path)
			if not os.path.isfile(info_path):
				text = cPickle.dumps(info)
				writeFile(info_path, text)

	def loadInfo(self, info_path):
		info = ("", "", "", "", "", "", "", "")
		if os.path.isfile(info_path):
			text = readFile(info_path)
			info = cPickle.loads(text)
		return info

	def fetchData(self, url):
		response = None
		retry = 0
		while response is None and retry < 5:
			try:
				headers = {"Accept": "application/json"}
				request = Request(url, headers=headers)
				jsonresponse = urlopen(request).read()
				response = json.loads(jsonresponse)
			except Exception as e:
				logger.error("exception: %s", e)
				retry += 1
				sleep(0.1)
		return response

	def getMovieList(self, moviename):

		def getMovies(moviename):
			response = self.fetchData("http://api.themoviedb.org/3/search/movie?api_key=3b6703b8734fee1b598de9ed7bbd3b47&query=" + quote(moviename))
			movielist = []
			if response:
				movies = response["results"]
				for movie in movies:
					logger.debug("movie: %s", str(movie))
					if "poster_path" in movie and "title" in movie and "id" in movie and "release_date" in movie and "poster_path" in movie and movie["poster_path"]:
						movielist.append((movie["title"].encode('utf-8') + " - " + _("Videos"), movie["id"], "movie", movie["release_date"].encode('utf-8'), movie["poster_path"].encode('utf-8')))
			return movielist

		def getTvShows(moviename):
			response = self.fetchData("http://api.themoviedb.org/3/search/tv?api_key=3b6703b8734fee1b598de9ed7bbd3b47&query=" + quote(moviename))
			tvshowslist = []
			if response:
				tvshows = response["results"]
				for tvshow in tvshows:
					logger.debug("tvshow: %s", str(tvshow))
					if "poster_path" in tvshow and "first_air" in tvshow and "id" in tvshow and tvshow["poster_path"]:
						tvshowslist.append((tvshow["name"].encode('utf-8') + " - " + _("TV Shows"), tvshow["id"], "tvshow", tvshow["first_air_date"].encode('utf-8'), tvshow["poster_path"].encode('utf-8')))
			return tvshowslist

		return getTvShows(moviename) + getMovies(moviename)

	def getTMDBInfo(self, p_id, cat, lang):

		def getGenre(response):
			genres = ""
			genrelist = response["genres"]
			for genre in genrelist:
				if genres == "":
					genres = genre["name"]
				else:
					genres = genres + ", " + genre["name"]
			return genres.encode('utf-8')

		def getCountries(response, cat):
			countries = ""
			if cat == "movie":
				countrylist = response["production_countries"]
				for country in countrylist:
					if countries == "":
						countries = country["name"]
					else:
						countries = countries + ", " + country["name"]
			if cat == "tvshow":
				countrylist = response["origin_country"]
				for country in countrylist:
					if countries == "":
						countries = country
					else:
						countries = countries + ", " + country
			return countries.encode('utf-8')

		def getRuntime(response, cat):
			runtime = ""
			if cat == "movie":
				runtime = str(response["runtime"])
				if response["runtime"] == 0:
					runtime = ""
			elif cat == "tvshow":
				if response["episode_run_time"]:
					runtime = str(response["episode_run_time"][0])
					if response["episode_run_time"][0] == 0:
						runtime = ""
			logger.debug(runtime)
			return runtime.encode('utf-8')

		def getReleaseDate(response, cat):
			releasedate = ""
			if cat == "movie":
				releasedate = response["release_date"]
			elif cat == "tvshow":
				releasedate = str(response["last_air_date"])
			return releasedate.encode('utf-8')

		def getVote(response):
			vote = str(response["vote_average"])
			if vote == "0.0":
				vote = ""
			return vote.encode('utf-8')

		def parseMovieData(response, cat):
			blurb = response["overview"].encode('utf-8')
			runtime = getRuntime(response, cat)
			releasedate = getReleaseDate(response, cat)
			vote = getVote(response)
			genres = getGenre(response)
			countries = getCountries(response, cat)
			cover_url = response["poster_path"]
			if cover_url is not None:
				cover_url = cover_url.encode('utf-8')
			backdrop_url = response["backdrop_path"]
			if backdrop_url is not None:
				backdrop_url = backdrop_url.encode('utf-8')
			return blurb, runtime, genres, countries, releasedate, vote, cover_url, backdrop_url

		response = None
		if cat == "movie":
			response = self.fetchData("http://api.themoviedb.org/3/movie/" + str(p_id) + "?api_key=3b6703b8734fee1b598de9ed7bbd3b47&language=" + lang)
		if cat == "tvshow":
			response = self.fetchData("http://api.themoviedb.org/3/tv/" + str(p_id) + "?api_key=3b6703b8734fee1b598de9ed7bbd3b47&language=" + lang)

		info = None
		if response:
			logger.debug("response: %s", str(response))
			blurb, runtime, genres, countries, releasedate, vote, cover_url, backdrop_url = parseMovieData(response, cat)
			if cover_url is not None:
				cover_url = "http://image.tmdb.org/t/p/%s%s" % (config.plugins.moviecockpit.cover_size.value, cover_url)
			if backdrop_url is not None:
				backdrop_url = "http://image.tmdb.org/t/p/%s%s" % (config.plugins.moviecockpit.backdrop_size.value, backdrop_url)
			info = (blurb, runtime, genres, countries, releasedate, vote, cover_url, backdrop_url)
		return info
