#!/usr/bin/python

import requests
import json
import logging

IMDB_HOST = "imdb146.p.rapidapi.com"
IMDB_URL = "https://"+IMDB_HOST

DEFAULT_RUNTIME = "0"
DEFAULT_CERTIFICATE = "UNKNOWN"
DEFAULT_RATING = "0"

API_REQUEST_LIMIT_HDR = "X-RateLimit-Requests-Limit"
API_REQUEST_REMAINING_HDR = "X-RateLimit-Requests-Remaining"
API_REQUEST_LIMIT_RESET_HDR = "X-RateLimit-Requests-Reset"


class IMDB:

   class MaxCallsExceededException(Exception):
      pass

   class MaxAPICallsExceededException(Exception):
      pass

   class IMDBResponseException(Exception):
      pass

   class IMDBAPIException(Exception):
      pass

   ###########################################################################################
   #
   # Init
   #
   ###########################################################################################
   def __init__(self, api_key, max_api_calls):

      self.api_key = api_key

      self.max_api_calls = max_api_calls
      self.api_calls = 0

      self.title_calls = 0
      self.title_call_successes = 0
      self.title_call_found = 0
      self.title_call_not_found = 0

      self.detail_calls = 0
      self.detail_call_successes = 0
      self.detail_call_found = 0
      self.detail_call_not_found = 0

      self.api_request_limit = 0
      self.api_request_remaining = 0
      self.api_limit_reset_s = 0

      self.headers = {
         "X-RapidAPI-Key": self.api_key,
         "X-RapidAPI-Host": IMDB_HOST
      }


   ###########################################################################################
   #
   # Parses the headers in the repsonse and sets API limit variables
   #
   ###########################################################################################
   def parse_response_headers(self, headers):
      for hdr_key, hdr_value in headers.items():
         logging.debug("HDR: " + hdr_key + " : " + hdr_value)

         if API_REQUEST_LIMIT_HDR == hdr_key:
            self.api_request_limit = int(hdr_value)

         if API_REQUEST_REMAINING_HDR == hdr_key:
            self.api_request_remaining = int(hdr_value)

         if API_REQUEST_LIMIT_RESET_HDR == hdr_key:
            self.api_limit_reset_s = int(hdr_value)

      logging.debug(API_REQUEST_LIMIT_HDR + ":" + str(self.api_request_limit))
      logging.debug(API_REQUEST_REMAINING_HDR + ":" + str(self.api_request_remaining))
      logging.debug(API_REQUEST_LIMIT_RESET_HDR + ":" + str(self.api_limit_reset_s))

   ##########################################################################################
   #
   # Looks up the film by title and year and cycles through the responses looking for an 
   # exact match
   #
   ##########################################################################################
   def get_titles(self, search_title, year):

      if self.api_calls >= self.max_api_calls:
         raise IMDB.MaxCallsExceededException

      self.api_calls += 1 
      self.title_calls += 1

      search_title = search_title.lower() 
      logging.debug("Looking in IMDB for " + search_title + " Year:" + str(year))

      query_url = IMDB_URL + "/v1/find/"
      query_payload = {"query": search_title}

      logging.debug("url:" + str(query_url))
      logging.debug("Headers:" + str(self.headers))
      logging.debug("payload:" + str(query_payload))

      id = None

      try:
         response = requests.get(query_url, headers=self.headers, params=query_payload)
         self.parse_response_headers(response.headers)

         if response.status_code == 504:
            logging.debug("Request Timed out, usually means quota is depleted")
            return

         if response.status_code == 200:
            logging.debug("Request was successful")
            self.title_call_successes += 1

            resp_json = response.json()
            logging.debug("IMDB Resp:" + str(resp_json))
   
            id = None
            if "titleResults" in resp_json and resp_json["titleResults"]:
               if "results" in resp_json["titleResults"] and resp_json["titleResults"]["results"]:
                  for title in resp_json["titleResults"]["results"]:
                     try:
                        #all() returns true if all are true, so basically, returns true if all exist
                        if all(key in title for key in ('titleNameText', 'titleReleaseText', 'id')):
                           f_title = title["titleNameText"]
                           f_year = title["titleReleaseText"]
                           f_id = title["id"]
                           logging.debug("Title:" + str(f_title))
                           logging.debug("Year:" + str(f_year))
                           logging.debug("imdbid:" + str(f_id))

                           if f_year.isdigit() and len(f_year) == 4:  
                              if int(year) == int(f_year):
                                 logging.debug("Year Match!")
                                 self.title_call_found += 1
                                 id = f_id
                                 break
                           else:
                              logging.debug("Error parsing year:" + str(f_year))

                     except ValueError as e:
                        logging.debug("Error parsing values:" + str(e))
                        raise IMDB.IMDBResponseException("Error parsing values:" + str(e) + " - [" + str(search_title) + " / " + str(year) + "]")
               else:
                  logging.debug("Format Error: results not in titleResults")
                  raise IMDB.IMDBAPIException("results not in titleResults")
            else:
               logging.debug("Format Error: titleResults not in response")
               raise IMDB.IMDBAPIException("titleResults not in response")
      except IMDB.IMDBResponseException as e:
         raise e
      except Exception as e:
         logging.debug("Exception: " + str(e))
         raise IMDB.IMDBAPIException("Error connecting to IMDB API: URL:" + IMDB_URL)

      if not id:
         self.title_call_not_found += 1

         if 0 >= self.api_request_remaining:
            raise IMDB.MaxAPICallsExceededException()

      return id

   ##########################################################################################
   #
   # Looks up the details by the ID
   #
   ##########################################################################################
   def get_data_from_imdbid(self, imdbid):

      if self.api_calls >= self.max_api_calls:
         raise IMDB.MaxCallsExceededException

      self.detail_calls += 1
      self.api_calls += 1

      deets = {}
      title_url = IMDB_URL + "/v1/title/"
      querypayload = {"id": imdbid}

      try:
         response = requests.get(title_url, headers=self.headers, params=querypayload)
         self.parse_response_headers(response.headers)

         if response.status_code == 200:
            logging.debug("Request was successful")
            self.detail_call_successes += 1
 
            resp_json = response.json()
            logging.debug(resp_json)

            if "runtime" in resp_json and resp_json["runtime"]:
               if "seconds" in resp_json["runtime"] and resp_json["runtime"]["seconds"]:
                  runtime = resp_json["runtime"]["seconds"]
                  logging.debug("Runtime:" + str(runtime))
                  deets["runtime"] = runtime
                  deets["imdbid"] = imdbid
                  self.detail_call_found += 1
               else:
                  logging.debug("Format Exception: runtime not formatted as expected in response, using default" + DEFAULT_RUNTIME)
                 #raise IMDB.IMDBResponseException("runtime not formatted as expected in response")
            else:
               logging.debug("Format Exception: runtime not in response, using default:" + DEFAULT_RUNTIME)
               #raise IMDB.IMDBResponseException("runtime not in response")
            if "runtime" not in deets:
               deets["runtime"] = DEFAULT_RUNTIME

            if "certificate" in resp_json and resp_json["certificate"]:
               if "rating" in resp_json["certificate"] and resp_json["certificate"]["rating"]:
                  classification = resp_json["certificate"]["rating"]
                  logging.debug("Classification:" + str(classification))
                  deets["classification"] = classification
               else:
                  logging.debug("Format Exception: certificate not formatted as expected in response, using default:" + DEFAULT_CERTIFICATE)
                  #raise IMDB.IMDBResponseException("certificate not formatted as expected in response")
            else:
               logging.debug("Format Exception: certificate not in response, using default:" + DEFAULT_CERTIFICATE)
               #raise IMDB.IMDBResponseException("certificate not in response")
            if "certificate" not in deets:
               deets["certificate"] = DEFAULT_CERTIFICATE

            if "ratingsSummary" in resp_json and resp_json["ratingsSummary"]:
               if "aggregateRating" in resp_json["ratingsSummary"] and resp_json["ratingsSummary"]["aggregateRating"]:
                  rating = resp_json["ratingsSummary"]["aggregateRating"]
                  logging.debug("Rating:" + str(rating))
                  deets["imdb_rating"] = rating
               else:
                  logging.debug("Format Exception: ratings not formatted as expected in response")
                  #raise IMDB.IMDBResponseException("ratings not formatted as expected in response")
            else:
               logging.debug("Format Exception: ratings not in response, using default:" + DEFAULT_RATING)
               #raise IMDB.IMDBResponseException("ratings not in response, using default:" + DEFAULT_RATING)
            if "imdb_rating" not in deets:
               deets["imdb_rating"] = DEFAULT_RATING

      except IMDB.IMDBResponseException as e:
         raise e
      except Exception as e:
         logging.debug("Exception: " + str(e))
         raise IMDB.IMDBAPIException("Error connecting to IMDB API: URL:" + IMDB_URL)

      if not deets:
         self.detail_call_not_found += 1

      return deets

   ##########################################################################################
   #
   # Gets the ID from the title then looks up the details
   #
   ##########################################################################################
   def get_details_from_title_year(self, title, year):

      deets = {}
      imdbid = self.get_titles(title, year)
      logging.debug("Found imdbid:" + str(imdbid))

      if imdbid:
         deets = self.get_data_from_imdbid(imdbid)

      logging.debug("deets:" + str(deets))
      return deets

   ################################################################################
   # Returns stats as: total calls; title: calls, successes, found, not found; details: calls, successes, found, not found;
   ################################################################################
   def get_stats(self):
      return self.api_calls, self.title_calls, self.title_call_successes, self.title_call_found, self.title_call_not_found, self.detail_calls, self.detail_call_successes, self.detail_call_found, self.detail_call_not_found

   ################################################################################
   # Returns API stats as: Request Limit, Requests Remaining, Limit Reset
   ################################################################################
   def get_api_stats(self):
      return self.api_request_limit, self.api_request_remaining, self.api_limit_reset_s


################################################################################
#
# MAIN
#
################################################################################
if __name__ == "__main__":

   #imdbid = "tt0073195"
   search_title = "12 Years A Slave"
   search_year = 2013

   get_details_from_title_year(search_title, search_year)

#   get_titles(search_title, search_year)
#   get_data_from_imdbid(imdbid)


