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

OP_GET = "get"
OP_SET = "set"
OP_ADD = "add"


#########################################################################################
#
# Usage
#
#########################################################################################
def usage():
   print(sys.argv[0]+" <-h> ")

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
       opts, args = getopt.getopt(argv, "l:", ["log="])
   except getopt.GetoptError:
      usage()
      sys.exit(2)

   loglevel = "DEBUG"

   for opt, arg in opts:
      if opt in ("-l", "--log"):
         loglevel = arg.upper()

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

   d_str = datetime.now().strftime("%Y%m%d%H%M%S-Films.json")
   logging.debug("DATE:" + d_str)

   api = FilmAPI(db_host, db_port)
   print("Getting")
   all_films = api.get_all()

   with open(d_str, 'w') as f:
      json.dump(all_films, f)

   count = 0
   for film in all_films:
      count += 1
      print(str(count) + ":" + str(film))

#################################################################################################
# MAIN
#################################################################################################
if __name__ == "__main__":
   main(sys.argv[1:])

