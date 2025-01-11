#!/usr/bin/python3

import logging
import getopt
import sys
import os
import re
from datetime import datetime
import json

from film_api import FilmAPI

from file_system import FileSystem
from film_watched_updater import FilmWatchedUpdater

FILM_DB_SERVER_ENV_NAME = "FILM_WEB_BE_SERVICE_SERVICE_HOST"
FILM_DB_PORT_ENV_NAME = "FILM_WEB_BE_SERVICE_SERVICE_PORT"

#OP_GET = "get"
#OP_SET = "set"
#OP_ADD = "add"


#########################################################################################
#
# Usage
#
#########################################################################################
def usage():
   print(sys.argv[0]+" <-h> <-n number of films to process> -f filename")

   print("Requires the following Environment Variables:")
   print("   "+str(FILM_DB_SERVER_ENV_NAME)+" - The location of the Database Service")
   print("   "+str(FILM_DB_PORT_ENV_NAME)+" - The Port the Database Service is listening on")


#########################################################################################
#
# Main
#
#########################################################################################
def main(argv):

   try:
       opts, args = getopt.getopt(argv, "l:f:n:", ["log=", "file=", "num="])
   except getopt.GetoptError:
      usage()
      sys.exit(2)

   loglevel = "DEBUG"
   number_to_process = 10
   filename = None

   for opt, arg in opts:
      if opt in ("-l", "--log"):
         loglevel = arg.upper()
      elif opt in ("-f", "--file"):
         filename = arg
      elif opt in ("-n", "--num"):
         number_to_process = int(arg)

   # Get Environment Variables
   try:
      db_host = os.environ[FILM_DB_SERVER_ENV_NAME]
      db_port = os.environ[FILM_DB_PORT_ENV_NAME]
   except KeyError as e:
      logging.debug("Environment Variable not found:" +str(e))
      usage()
      sys.exit(2)

   if not filename:
      logging.debug("filename argument is required")
      usage()
      sys.exit(2)

   numeric_log_level = getattr(logging, loglevel, None)

   logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filemode='w', level=logging.DEBUG)
   console = logging.StreamHandler()

   #console.setLevel(logging.INFO)
   console.setLevel(logging.DEBUG)

   formatter = logging.Formatter('%(levelname)-8s %(message)s')
   console.setFormatter(formatter)

   logging.debug(FILM_DB_SERVER_ENV_NAME+":" + str(db_host))
   logging.debug(FILM_DB_PORT_ENV_NAME+":" + str(db_host))

   d_str = datetime.now().strftime("%Y%m%d%H%M%S-Films.json")
   logging.debug("DATE:" + d_str)

   with open(filename, 'r') as file:
      data = json.load(file)

   if not isinstance(data, list):
      print("JSON file is not a list")

   api = FilmAPI(db_host, db_port)
      
   print("JSON file is a list")
   count = 0
   for film in data:
      count += 1
      print("FILM " + str(count) + ":" + str(film))

      imdbid = film["imdbid"]
      title = film["title"]
      year = film["year"]
      media_type = film["media_type"]
      watched = film["watched"]
      details = {}

      if year != None and title != None and imdbid != None:
         print("Adding")

         print(" IMDBID:" + imdbid)
         print(" title:" + title)
         print(" year:" + str(year))

         details["imdbid"] = imdbid

         if film["runtime"]: 
            details["runtime"] = film["runtime"]
         if film["imdb_rating"]: 
            details["imdb_rating"] = film["imdb_rating"]
         if film["classification"]: 
            details["classification"] = film["classification"]
         if film["updated"]: 
            details["updated"] = film["updated"]

         if api.add_film(title, year, media_type, watched, details):
            print("SUCCESSFULLY ADDED")
         else:
            print("FAILED TO ADD")
            
         print(" details:" + str(details))

      if count >= number_to_process:
         break
#      if imdbid and title and year:
#         details = {}
#         details["imdbid"] = imdbid
#         watched = "false"
#         media_type = "N/A"
#
#         if runtime:
#            details["runtime"] = runtime
#         if rating:
#            details["imdb_rating"] = rating
#         if cert:
#            details["classification"] = cert
#
  
#         if api.add_film(title, year, media_type, watched, details):
#            print("SUCCESSFULLY ADDED")
#         else:
#            print("FAILED TO ADD")

   # Print the data to verify
   #print(data)
   

#   api = FilmAPI(db_host, db_port)
#   print("Getting")
#   all_films = api.get_all()
#
#   with open(d_str, 'w') as f:
#      json.dump(all_films, f)
#
#   count = 0
#   for film in all_films:
#      count += 1
#      print(str(count) + ":" + str(film))

#################################################################################################
# MAIN
#################################################################################################
if __name__ == "__main__":
   main(sys.argv[1:])

