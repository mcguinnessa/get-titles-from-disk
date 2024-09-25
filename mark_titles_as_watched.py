#!/usr/bin/python3

import logging
import getopt
import sys
import os
import re

from film_title_tools import FilmTitleTools

from film_api import FilmAPI

from file_system import FileSystem
from film_watched_updater import FilmWatchedUpdater

num_films_processed = 0
process_max = sys.maxsize
max_imdb_lookups = 0


FILM_DB_SERVER_ENV_NAME = "FILM_WEB_BE_SERVICE_SERVICE_HOST"
FILM_DB_PORT_ENV_NAME = "FILM_WEB_BE_SERVICE_SERVICE_PORT"


#########################################################################################
#
# Usage
#
#########################################################################################
def usage():
   #print("\n")
   print(sys.argv[0]+" <-h> [--log <log level>] [-n <max_records_to_process>")

   print("Requires the following Environment Variables:")
   print("   "+str(FILM_DB_SERVER_ENV_NAME)+" - The location of the Database Service")
   print("   "+str(FILM_DB_PORT_ENV_NAME)+" - The Port the Database Service is listening on")
   print("   SMB_HOST - The Host of the Samba file system")
   print("   SMB_USER - The Samba User")
   print("   SMB_PASS - The Samba Password")


#########################################################################################
#
# Main
#
#########################################################################################
def main(argv):
   global process_max

   try:
       opts, args = getopt.getopt(argv, "l:n:", ["log="])
   except getopt.GetoptError:
      usage()
      sys.exit(2)

   loglevel = "DEBUG"

   for opt, arg in opts:
      if opt in ("-l", "--log"):
         loglevel = arg.upper()
      elif opt in ("-n"):
         process_max = int(arg)

   # Get Environment Variables
   try:
      db_host = os.environ[FILM_DB_SERVER_ENV_NAME]
      db_port = os.environ[FILM_DB_PORT_ENV_NAME]
      smb_user = os.environ["SMB_USER"]
      smb_server = os.environ["SMB_HOST"]
      smb_password = os.environ["SMB_PASS"]
   except KeyError as e:
      logging.debug("Environment Variable not found:" +str(e))
      usage()
      sys.exit(2)

   numeric_log_level = getattr(logging, loglevel, None)

   logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filemode='w', level=logging.DEBUG)
   console = logging.StreamHandler()

   #console.setLevel(logging.INFO)
   console.setLevel(logging.DEBUG)

   logging.getLogger("smbprotocol").setLevel(logging.ERROR)
   formatter = logging.Formatter('%(levelname)-8s %(message)s')
   console.setFormatter(formatter)

   logging.info("Marking films as watched")
   logging.info("Max number of titles to process:" + str(process_max))

   logging.debug(FILM_DB_SERVER_ENV_NAME+":" + str(db_host))
   logging.debug(FILM_DB_PORT_ENV_NAME+":" + str(db_host))
   logging.debug("SMB_USER:" + str(smb_user))
   logging.debug("SMB_HOST:" + str(smb_server))
   logging.debug("SMB_PASS:" + str(smb_password))

   fs = FileSystem(smb_server, smb_user, smb_password)
   api = FilmAPI(db_host, db_port)
   updater = FilmWatchedUpdater(api, process_max) 

   films = []

   filename = "/Films/watched.txt"
   films = fs.readFile(filename)

   num_processed = updater.set_films_as_watched(films)
   newly_watched, already_watched, found_in_db, not_found_in_db, invalid_format, failed_to_update = updater.get_stats()
    
   print("Found in DB:")
   if found_in_db:
      for f in found_in_db:
         print("   " + f)

   print("Already Watched:")
   if already_watched:
      for w in already_watched:
         print("   " + w)

   ############################
   # Report
   ############################
   print("\nProcessed            : " + str(num_processed))
   print("Found in Local DB    : " + str(len(found_in_db)))
   print("Not Found in Local DB: " + str(len(not_found_in_db)))
   if not_found_in_db:
      for nf in not_found_in_db:
         print("   " + nf)
   print("Invalid Title Format : " + str(len(invalid_format)))
   if invalid_format:
      for inf in invalid_format:
         print("   " + inf)
   print("Failed To Update     : " + str(len(failed_to_update)))
   if failed_to_update:
      for ftu in failed_to_update:
         print("   " + ftu)
   print("Already Watched      : " + str(len(already_watched)))
   print("Marked as Watched    : " + str(len(newly_watched)))
   if newly_watched:
      for nw in newly_watched:
         print("   " + nw)

#################################################################################################
# MAIN
#################################################################################################
if __name__ == "__main__":
   main(sys.argv[1:])

