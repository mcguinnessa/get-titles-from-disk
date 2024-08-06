#!/usr/bin/python3

import logging
import getopt
import sys
import os
import re

from lookup_imdb import IMDB
from film_title_tools import FilmTitleTools

from film_api import FilmAPI

from file_system import FileSystem
from film_watched_updater import FilmWatchedUpdater

num_films_processed = 0
process_max = sys.maxsize
max_imdb_lookups = 0


#########################################################################################
#
# Usage
#
#########################################################################################
def usage():
   print("\n")
   print(sys.argv[0]+" <-h> [--log <log level>] [-n <max_records_to_process>")

#########################################################################################
#
# Main
#
#########################################################################################
def main(argv):
   global process_max

   try:
       opts, args = getopt.getopt(argv, "ln:", ["log="])
   except getopt.GetoptError:
      usage()
      sys.exit(2)

   loglevel = "DEBUG"

   for opt, arg in opts:
      if opt in ("-l", "--log"):
         loglevel = arg.upper()
      elif opt in ("-n"):
         process_max = int(arg)

   numeric_log_level = getattr(logging, loglevel, None)

   logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filemode='w', level=logging.DEBUG)
   console = logging.StreamHandler()

   #console.setLevel(logging.INFO)
   console.setLevel(logging.DEBUG)

   formatter = logging.Formatter('%(levelname)-8s %(message)s')
   console.setFormatter(formatter)

   logging.info("Marking films as watched")
   logging.info("Max number of titles to process:" + str(process_max))

   db_host = os.environ["DB_HOST"]
   db_port = os.environ["DB_PORT"]

   api = FilmAPI(db_host, db_port)
   updater = FilmWatchedUpdater(api, process_max) 

   films = []

   filename = "./watched.txt"
   with open(filename, 'r') as file:
      for line in file:
         films.append(line.strip())

   num_processed = updater.set_films_as_watched(films)
   newly_watched, already_watched, found_in_db, not_found_in_db, invalid_format = updater.get_stats()
    
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

