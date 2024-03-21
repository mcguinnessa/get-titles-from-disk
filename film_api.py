
import logging
import requests
import json


class FilmAPI:
   """The Film API"""

   #DATABASE_NAME = "FilmDatabase"
#   url = "http://192.168.0.160"
#   port = "80"
#   url = "http://192.168.0.121"
#   port = "8080"
   protocol = "http://"

   film_lookup = 0
   film_found = 0
   film_added = 0


   def __init__(self, server, port):
      """Init"""
      self.server = server
      self.port = port
#      logging.debug("Connecting to "+ self.server+ ":" + self.port + " with user:" + self.user + " and " + self.password)


#   def add_film(self, title, year, imdbid=None, runtime=None, classification=None, rating=None, media_type=None):
   def add_film(self, title, year, media_type, details):
      """Add film to database"""

      print("Adding film, title:" + str(title) + " year:" + str(year) + " media_type:" + str(media_type) + " details:" + str(details))
 
      endpoint = "/api/film"
      jobj = {}
      jobj["title"] = title
      jobj["year"] = year
 
      if "imdbid" in details:
         jobj["imdbid"] = details["imdbid"]
      if "runtime" in details:
         jobj["runtime"] = details["runtime"]
      if "classification" in details:
         jobj["classification"] = details["classification"]
      if "imdb_rating" in details:
         jobj["imdb_rating"] = details["imdb_rating"]
      if media_type: 
         jobj["media_type"] = media_type

      logging.debug("Adding Film:" + str(jobj))
      headers = {"Content-Type": "application/json"}
      logging.debug("obj:" + str(jobj))

      output = requests.post(self.protocol + self.server + ":" +self.port + endpoint, json=jobj, headers=headers)
      self.film_added += 1
      logging.debug("Added Film:" + str(output))


   def get_film(self, film_name, film_year):
      """Looking for film with name / year """
  
      self.film_lookup += 1
 
      endpoint = "/api/film"

      jobj = {}
      jobj["title"] = film_name
      jobj["year"] = film_year

      logging.debug("Looking for Film:" + str(film_name) + " Year:" + str(film_year))
      headers = {"Content-Type": "application/json"}
      logging.debug("obj:" + str(jobj))
      output = requests.get(self.protocol + self.server + ":" +self.port + endpoint, params=jobj, headers=headers)
      logging.debug("Returned:" + str(output))
      logging.debug("  Body:" + str(output.content))

      rc = {}

      if output.status_code == 200:
         logging.debug("Status:" + str(output.status_code))
 
         rc = json.loads(output.content.decode("utf-8"))

         print("rc=" + str(rc))
         if len(rc) > 0:
            if "imdbid" in rc[0]:
               self.film_found += 1

      return rc

   def print_stats(self):
      print("DB Stats")
      print("Title Lookups:" + str(self.film_lookup))
      print("Films Found  :" + str(self.film_found))
      print("Films Added  :" + str(self.film_added))
