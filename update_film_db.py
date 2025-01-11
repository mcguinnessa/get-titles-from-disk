#!/usr/bin/python3

import logging
import getopt
import sys
import os
import re

from film_api import FilmAPI

from file_system import FileSystem
from film_watched_updater import FilmWatchedUpdater

FILM_DB_SERVER_ENV_NAME = "FILM_WEB_BE_SERVICE_SERVICE_HOST"
FILM_DB_PORT_ENV_NAME = "FILM_WEB_BE_SERVICE_SERVICE_PORT"

OP_GET = "get"
OP_SET = "set"
OP_ADD = "add"


#########################################################################################
#
# Usage
#
#########################################################################################
def usage():
   #print("\n")
   print(sys.argv[0]+" <-h> -o get|set|add -i <imdbid> -r <rating> -s <runtime> -c <classification> -t <title> -y <year> -w <watched>")

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
       opts, args = getopt.getopt(argv, "o:l:i:r:c:t:y:s:w:", ["log=", "imdbid=", "op=", "runtime_in_seconds=", "cert=", "rating=", "year=", "title=", "watched="])
   except getopt.GetoptError:
      usage()
      sys.exit(2)

   loglevel = "DEBUG"

   imdbid = None
   runtime = None
   rating = None
   cert = None
   year = None
   title = None
   op = None
   watched = None
   for opt, arg in opts:
      if opt in ("-l", "--log"):
         loglevel = arg.upper()
      elif opt in ("-i", "--imdbid"):
        imdbid  = str(arg)
        print("IMDBID:" + str(imdbid))
      elif opt in ("-s", "--runtime"):
        runtime  = int(arg)
        print("RUNTIME:" + str(runtime))
      elif opt in ("-r", "--rating"):
        rating  = arg
        print("RATING:" + str(rating))
      elif opt in ("-c", "--cert"):
        cert  = arg
        print("CLASSIFICATION:" + str(cert))
      elif opt in ("-t", "--title"):
        title  = arg
        print("TITLE:" + str(title))
      elif opt in ("-y", "--year"):
        year  = arg
        print("YEAR:" + str(year))
      elif opt in ("-w", "--watched"):
        watched  = arg
        print("WATCHED:" + str(watched))
      elif opt in ("-o", "--op"):
        op  = arg

   if not op:
      print("Operation needs to be supplied")
      usage()
      sys.exit(2)
   elif op not in [ OP_GET, OP_SET, OP_ADD ]:
      print("Unknown Operation:" + op)
      usage()
      sys.exit(2)

   # Get Environment Variables
   try:
      db_host = os.environ[FILM_DB_SERVER_ENV_NAME]
      db_port = os.environ[FILM_DB_PORT_ENV_NAME]
   except KeyError as e:
      logging.debug("Environment Variable not found:" +str(e))
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

   api = FilmAPI(db_host, db_port)
   if op.lower() == OP_GET:
      print("Getting")
      if imdbid:
         deets = api.get_film_by_id(imdbid)
         print(deets)

   elif op.lower() == OP_ADD:
      print("Adding")
      if imdbid and title and year:
         details = {}
         details["imdbid"] = imdbid
         watched = "false"
         media_type = "N/A"
         
         if runtime:
            details["runtime"] = runtime
         if rating:
            details["imdb_rating"] = rating
         if cert:
            details["classification"] = cert
         if api.add_film(title, year, media_type, watched, details):
            print("SUCCESSFULLY ADDED")
         else:
            print("FAILED TO ADD")

   elif op.lower() == OP_SET:
      if imdbid:

         details = {}
         if runtime:
            details["runtime"] = runtime
         if rating:
            details["imdb_rating"] = rating
         if cert:
            details["classification"] = cert
         if title:
            details["title"] = title
         if year:
            details["year"] = year
         if watched:
            print("WAtched is non None")
            details["watched"] = watched

         print("Updating:" + str(details))

         if(api.update_film(imdbid, details)):
            print("SUCCESSFULLY UPDATED")
         else:
            print("FAILED TO UPDATE")

#################################################################################################
# MAIN
#################################################################################################
if __name__ == "__main__":
   main(sys.argv[1:])

