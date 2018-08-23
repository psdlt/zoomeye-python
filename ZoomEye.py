#!/usr/bin/env python3

import requests
import dateutil.parser


class ZoomEye:

    def __init__(self, query, username, password, page=1, restart_at=None, verbose=True):
        # Validate input

        if page < 1 or page > 500:
            raise ValueError("'page' must be between 1 and 500")

        # Assign

        self.query = query
        self.username = username
        self.password = password
        self.page = page
        self.restart_at = restart_at
        self.verbose = verbose

        # Some defaults
        self.access_token = None
        self.api_url = "https://api.zoomeye.org"
        self.total = 0
        self.available = 0
        self.iteration = 1
        self.facets = "ip"
        self.last_date = None

    def login(self):
        # if we already have access token - return it

        if self.access_token:
            return self.access_token

        # otherwise - try to login

        url = "%s/user/login" % self.api_url
        data = '{{"username": "{}", "password": "{}"}}'.format(self.username,
                                                               self.password)

        request = requests.post(url, data)
        if request.status_code != 200:
            raise ConnectionError("Login failed with status code %s" % request.status_code)

        if "access_token" in request.json():
            self.access_token = request.json().get("access_token")
            return self.access_token
        else:
            raise ConnectionError("Login failed, access token missing")

    def next_page(self):
        try:
            self.login()
        except ConnectionError as err:
            # Bubble Up
            raise ConnectionError(err)

        search_query = self.query
        if self.restart_at:
            search_query = '%s +before:"%s"' % (self.query, self.restart_at)

        url = "%s/host/search" % self.api_url
        url_query = {"query": search_query, "page": self.page, "facets": self.facets}
        headers = {'Authorization': 'JWT %s' % self.access_token}
        request = requests.get(url, params=url_query, headers=headers)

        if request.status_code != 200:
            raise ConnectionError("Fetching results page failed with status code %s" % request.status_code)

        data = request.json()

        if "matches" not in data:
            # Not an exception, it's simply the end of results
            return []

        self.total = data["total"]
        self.available = data["available"]

        results = []

        for item in data["matches"]:
            result = {
                "ip": item["ip"],
                "port": item["portinfo"]["port"],
                "country": item["geoinfo"]["country"]["code"]
            }
            results.append(result)

            # Find the last date, useful when we want to iterate over more than 500 pages
            date = dateutil.parser.parse(item["timestamp"])
            if not self.last_date or date < self.last_date:
                self.last_date = date

        self.print_log(
            "Iteration #%s, Page #%s, Search query: [%s], Results in this page: %s, "
            "Total results: %s, Available: %s, Last date: %s, Request took: %s" % (
                self.iteration, self.page, search_query, len(data["matches"]), self.total, self.available,
                self.last_date.strftime("%Y-%m-%d %H:%M"), request.elapsed))

        self.page = self.page + 1

        # Next iteration
        if self.page > 500:
            self.page = 1
            self.iteration = self.iteration + 1
            self.restart_at = self.last_date.strftime("%Y-%m-%d %H:%M")

        return results

    def resource_info(self):
        try:
            self.login()
        except ConnectionError as err:
            # Bubble Up
            raise ConnectionError(err)

        url = "%s/resources-info" % self.api_url
        headers = {'Authorization': 'JWT %s' % self.access_token}
        request = requests.get(url, headers=headers)

        if request.status_code != 200:
            raise ConnectionError("Failed to get resources info with status code %s" % request.status_code)

        data = request.json()

        return data["resources"]["search"]

    def print_log(self, line):
        if not self.verbose:
            return

        print(line)
