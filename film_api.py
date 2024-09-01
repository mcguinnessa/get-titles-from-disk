
import logging
import requests
import json


class FilmAPI:
   """The Film API"""

   protocol = "http://"
   headers = {"Content-Type": "application/json"}

   def __init__(self, server, port):
      """Init"""
      self.server = server
      self.port = port

      self.film_lookup = 0
      self.film_found = 0
      self.film_added = 0
      self.film_updated = 0
      
      self.added_to_db = []
      self.updated_in_db = []

   ###################################################################################
   #
   # Adds a Film to the DB
   #
   ###################################################################################
   def update_film(self, imdbid, details):
      """Update film in database"""

      logging.info("Updating film, imdbid:" + str(imdbid) + " details:" + str(details))
 
      endpoint = "/api/film/" + str(imdbid)
      rc = False

      jobj = {}
      jobj["imdbid"] = imdbid
      #jobj["watched"] = watched
 
      if "runtime" in details:
         jobj["runtime"] = details["runtime"]
      if "classification" in details:
         jobj["classification"] = details["classification"]
      if "imdb_rating" in details:
         jobj["imdb_rating"] = details["imdb_rating"]

      logging.debug("Updating Film:" + str(jobj))
      logging.debug("obj:" + str(jobj))

      output = requests.patch(self.protocol + self.server + ":" +self.port + endpoint, json=jobj, headers=self.headers)
      logging.debug("Code:" + str(output.status_code)) 
      logging.debug("  Body:" + str(output.content))
      resp_json = output.json()
      logging.debug("  Body:" + str(resp_json))
      #if output.status_code == 201: #Created
      if output.status_code == 200:
         rc = True
         self.film_updated += 1
         logging.debug("Updated Film Successfully:" + str(output))
         self.updated_in_db.append(resp_json["title"] + " (" + str(resp_json["year"]) + ")")
      else:
         logging.debug("Failed to update film, reponse::" + str(output.status_code))

      #return output.status_code
      return rc


   ###################################################################################
   #
   # Adds a Film to the DB
   #
   ###################################################################################
   def add_film(self, title, year, media_type, watched, details):
      """Add film to database"""

      logging.info("Adding film, title:" + str(title) + " year:" + str(year) + " media_type:" + str(media_type) + " details:" + str(details))
      rc = False
 
      endpoint = "/api/film"
      jobj = {}
      jobj["title"] = title
      jobj["year"] = year
      jobj["watched"] = watched
 
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
      #headers = {"Content-Type": "application/json"}
      logging.debug("obj:" + str(jobj))

      output = requests.post(self.protocol + self.server + ":" +self.port + endpoint, json=jobj, headers=self.headers)
      if output.status_code == 201: #Created
         self.film_added += 1
         logging.debug("Added Film Successfully:" + str(output))
         self.added_to_db.append(title + " (" + str(year) + ")")
         rc = True
      else:
         logging.debug("Failed to add film, reponse::" + str(output.status_code))

      #return output.status_code
      return rc

   ###################################################################################
   #
   # Looks up a file on title and year
   #
   ###################################################################################
   def lookup_by_title_year(self, film_name, film_year):
      """Looking for film with name / year """
  
      self.film_lookup += 1
 
      endpoint = "/api/film"

      jobj = {}
      jobj["title"] = film_name
      jobj["year"] = film_year

      logging.debug("Looking for Film:" + str(film_name) + " Year:" + str(film_year))
      logging.debug("obj:" + str(jobj))
      output = requests.get(self.protocol + self.server + ":" +self.port + endpoint, params=jobj, headers=self.headers)
      logging.debug("Returned:" + str(output))
      logging.debug("  Body:" + str(output.content))

      rc = {}

      if output.status_code == 200:
         logging.debug("Status:" + str(output.status_code))
         rc = json.loads(output.content.decode("utf-8"))

         logging.debug("rc=" + str(rc))
         if len(rc) > 0:
            if "imdbid" in rc[0]:
               self.film_found += 1

      return rc

   ###################################################################################
   #
   # Gets the oldest records from the local DB
   #
   ###################################################################################
   def get_oldest_records(self, num_records):
      """Get Oldest records"""

      logging.debug("Oldest " + str(num_records)+ " records")
      #endpoint = "/api/films" + "?sort=updated&limit=10&asc=true"

      #url = f"{self.protocol}{self.server}:{+self.port}/api/films?sort=updated&limit={num_records}&asc=true"
      url = f"{self.protocol}{self.server}:{self.port}/api/films?sort=updated&limit={num_records}&asc=true"

      rc = {}
      #output = requests.get(self.protocol + self.server + ":" +self.port + endpoint, headers=self.headers)
      output = requests.get(url, headers=self.headers)

      if output.status_code == 200: #Success
         records = output.json()
         for record in records:
            logging.debug("Record:" + str(record))

            t = record["title"]
            y = record["year"]
 
            #rc[record["imdbid"]] = f"{t} ({y})"
            rc[record["imdbid"]] = [t, y]

      return rc


   ###################################################################################
   #
   # Sets film to watched
   #
   ###################################################################################
   def update_watched_for_film(self, imdbid, watched):
      """Update watched status of film"""

      logging.debug("Looking for imdbid:" + str(imdbid))
      endpoint = "/api/film/" + str(imdbid)

      rc = False
      jobj = {}
      jobj["watched"] = str(watched)

      logging.debug("Marking for Film:" + str(imdbid))
      logging.debug("obj:" + str(jobj))
      output = requests.patch(self.protocol + self.server + ":" +self.port + endpoint, json=jobj, headers=self.headers)
      logging.debug("Returned:" + str(output))
      logging.debug("  Body:" + str(output.content))

      if output.status_code == 200:
         logging.debug("Status:" + str(output.status_code))
         rc = True
         #rc = json.loads(output.content.decode("utf-8"))

      return rc

   ###################################################################################
   #
   # Returns the stats: lookups, found, added
   #
   ###################################################################################
   def get_stats(self):
      return self.film_lookup, self.film_found, self.film_added

   ###################################################################################
   #
   # Resets counters
   #
   ###################################################################################
   def reset_counts(self):
      self.film_lookup = 0
      self.film_found = 0
      self.film_added = 0
