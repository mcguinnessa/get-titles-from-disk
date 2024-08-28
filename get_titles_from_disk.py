#!/usr/bin/python3

import logging
import getopt
import sys
import os
import re
from db_populator import DBPopulator
from lookup_imdb import IMDB
from film_api import FilmAPI
from file_system import FileSystem

IMDB_API_MAX_FILMS_PER_MONTH = 500

process_max = sys.maxsize
max_imdb_lookups = 0
#max_imdb_lookups = IMDB_API_MAX_FILMS_PER_MONTH

FILM_DB_SERVER_ENV_NAME = "FILM_WEB_BE_SERVICE_SERVICE_HOST"
FILM_DB_PORT_ENV_NAME = "FILM_WEB_BE_SERVICE_SERVICE_PORT"

#########################################################################################
#
# Usage
#
#########################################################################################
def usage():
#   print("\n")
   print(sys.argv[0]+" <-h> [--log <log level>] [-i <max_imdb_lookups>] [-n <max_records_to_process>")

   print("Requires the following Environment Variables:")
   print("   "+str(FILM_DB_SERVER_ENV_NAME)+" - The location of the Database Service")
   print("   "+str(FILM_DB_PORT_ENV_NAME)+" - The Port the Database Service is listening on")
   print("   SMB_HOST - The Host of the Samba file system")
   print("   SMB_USER - The Samba User")
   print("   SMB_PASS - The Samba Password")
   print("   IMDB_API_KEY - The access key for the IMDB API")

#########################################################################################
#
# Main
#
#########################################################################################
def main(argv):
   global process_max
   global max_imdb_lookups

   try:
       opts, args = getopt.getopt(argv, "li:f:", ["log="])
   except getopt.GetoptError:
      usage()
      sys.exit(2)

   loglevel = "DEBUG"

   for opt, arg in opts:
      if opt in ("-l", "--log"):
         loglevel = arg.upper()
      elif opt in ("-i"):
         max_imdb_lookups = int(arg)
      elif opt in ("-f"):
         process_max = int(arg)

   # Get Environment Variables
   try:
      db_host = os.environ[FILM_DB_SERVER_ENV_NAME]
      db_port = os.environ[FILM_DB_PORT_ENV_NAME]
      smb_user = os.environ["SMB_USER"]
      smb_server = os.environ["SMB_HOST"]
      smb_password = os.environ["SMB_PASS"]
      imdb_api_key = os.environ["IMDB_API_KEY"]
   except KeyError as e:
      logging.debug("Environment Variable not found:" +str(e))
      usage()
      sys.exit(2)

   numeric_log_level = getattr(logging, loglevel, None)

#   logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename='/var/log/film_manager/upload_from_files.log', filemode='w', level=logging.DEBUG)
   logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filemode='w', level=logging.DEBUG)
   logging.getLogger("smbprotocol").setLevel(logging.ERROR)
   console = logging.StreamHandler()

   #console.setLevel(logging.INFO)
   console.setLevel(logging.DEBUG)

   formatter = logging.Formatter('%(levelname)-8s %(message)s')
   console.setFormatter(formatter)

   logging.info("Storing titles from File System")
   logging.info("Max number of titles to process:" + str(process_max))
   logging.info("Max number of IMDB Lookups:" + str(max_imdb_lookups))

   api = FilmAPI(db_host, db_port)
   imdb = IMDB(imdb_api_key, max_imdb_lookups)
   fs = FileSystem(smb_server, smb_user, smb_password)

   br_dir = "\Films\BluRay"
   dvds_dir = "\Films\DVDs"
   files_dir = "\Films\Files"
   offline_dir = "\Films\Offline"

   dvd_titles = fs.listDir(dvds_dir)
   files_titles = fs.listDir(files_dir)
   br_titles = fs.listDir(br_dir)
   offline_titles = fs.listDir(offline_dir)

   populator = DBPopulator(api, imdb, process_max)

   file_processed, file_format_errors, file_not_in_imdb = populator.populate_files(files_titles)
   file_films_lookup, file_films_found, file_films_added = api.get_stats()

   api.reset_counts()
   dvd_processed, dvd_format_errors, dvd_not_in_imdb = populator.populate_dvds(dvd_titles)
   dvd_films_lookup, dvd_films_found, dvd_films_added = api.get_stats()

   api.reset_counts()
   br_processed, br_format_errors, br_not_in_imdb = populator.populate_files(br_titles)
   br_films_lookup, br_films_found, br_films_added = api.get_stats()

   api.reset_counts()
   rip_processed, rip_format_errors, rip_not_in_imdb  = populator.populate_files(offline_titles)
   rip_films_lookup, rip_films_found, rip_films_added = api.get_stats()

   not_found_in_imdb = file_not_in_imdb + dvd_not_in_imdb + br_not_in_imdb + rip_not_in_imdb

   imdb_calls, t_calls, t_success, t_found, t_missed, d_calls, d_success, d_found, d_missed = imdb.get_stats()


   ############################
   # Report
   ############################
   print("Local DB: (lookup, found, added)")
   print("  Files  : " + str(file_processed) + "/" + str(len(files_titles)) + " (l:" + str(file_films_lookup) + " f:" + str(file_films_found) + " a:" + str(file_films_added) + ")")
   if file_format_errors:
      print("    Format Errors: " + str(file_format_errors))
   print("  DVDs   : " + str(dvd_processed) + "/" + str(len(dvd_titles)) + " (l:" + str(dvd_films_lookup) + " f:" + str(dvd_films_found) + " a:" + str(dvd_films_added) + ")")
   if dvd_format_errors:
      print("    Format Errors: " + str(dvd_format_errors))
   print("  BluRays: " + str(br_processed) + "/" + str(len(br_titles)) + " (l:" + str(br_films_lookup) + " f:" + str(br_films_found) + " a:" + str(br_films_added) + ")")
   if br_format_errors:
      print("    Format Errors: " + str(br_format_errors))
   print("  Rips   : " + str(rip_processed) + "/" + str(len(offline_titles)) + " (l:" + str(rip_films_lookup) + " f:" + str(rip_films_found) + " a:" + str(rip_films_added) + ")")
   if rip_format_errors:
      print("    Format Errors: " + str(rip_format_errors))
   print("  Total  : " + str(file_processed + dvd_processed + br_processed + rip_processed) + "/" + str(len(br_titles) + len(dvd_titles) + len(files_titles) + len(offline_titles)))

   if api.added_to_db:
      print("Added to DB: " + str())
      for added in api.added_to_db:
         print("   " + str(added)) 

   print("IMDB")
   print("  API Calls :" + str(imdb_calls))
   print("  (success/lookup found missed)")
   print("  Title     : l:" + str(t_success) + "/" + str(t_calls) + " f:" + str(t_found) + " m:" + str(t_missed))
   print("  Details   : l:" + str(d_success) + "/" + str(d_calls) + " f:" + str(d_found) + " m:" + str(d_missed))
   if not_found_in_imdb:
      print("Not Found In IMDB: " + str(not_found_in_imdb))

#############################################################################################
# MAIN
#############################################################################################
if __name__ == "__main__":
   main(sys.argv[1:])

