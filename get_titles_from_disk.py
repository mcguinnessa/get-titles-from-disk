#!/usr/bin/python3

import logging
import getopt
import sys
import os
import re
#from film_manager.film_uploader import FilmUploader
#from network.script_record import ScriptRecordTable
from db_populator import DBPopulator

#from lookup_imdb import get_titles
#from lookup_imdb import get_details_from_title_year
#from lookup_imdb import print_stats as print_imdb_stats
from lookup_imdb import IMDB

from film_api import FilmAPI

#from film_database import FilmDatabase
#from film_database import FilmDatabase

from file_system import FileSystem

num_films_processed = 0
process_max = None
max_imdb_lookups = 0

#########################################################################################
#
# Usage
#
#########################################################################################
def usage():
   print("\n")
   print(sys.argv[0]+" <-h> [--log <log level>] [-i <max_imdb_lookups>] [-n <max_records_to_process>")

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

   numeric_log_level = getattr(logging, loglevel, None)

#   logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename='/var/log/film_manager/upload_from_files.log', filemode='w', level=logging.DEBUG)
   logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filemode='w', level=logging.DEBUG)
#   logging.getLogger("imdbpy").setLevel(logging.ERROR)
   logging.getLogger("smbprotocol").setLevel(logging.ERROR)
   console = logging.StreamHandler()

   #console.setLevel(logging.INFO)
   console.setLevel(logging.DEBUG)

   formatter = logging.Formatter('%(levelname)-8s %(message)s')
   console.setFormatter(formatter)
#   logging.getLogger('').addHandler(console)

   logging.info("Storing titles from File System")
   logging.info("Max number of titles to process:" + str(process_max))
   logging.info("Max number of IMDB Lookups:" + str(max_imdb_lookups))

   smb_user = os.environ["SMB_USER"]
   smb_server = os.environ["SMB_HOST"]
   smb_password = os.environ["SMB_PASS"]

   server = "192.168.0.160"
   port = "80"
   api = FilmAPI(server, port)
   imdb = IMDB(0)
   fs = FileSystem(smb_server, smb_user, smb_password)
   br_dir = "\Films\BluRay"
   dvds_dir = "\Films\DVDs"
   files_dir = "\Films\Files"
   offline_dir = "\Films\Offline"

   dvd_titles = fs.listDir(dvds_dir)
   files_titles = fs.listDir(files_dir)
   br_titles = fs.listDir(br_dir)
   offline_titles = fs.listDir(offline_dir)

   populator = DBPopulator(api, imdb)
   file_format_errors = populator.populate_files(files_titles)
   file_films_lookup, file_films_found, file_films_added = api.get_stats()

   api.reset_counts()
   dvd_format_errors = populator.populate_dvds(dvd_titles)
   dvd_films_lookup, dvd_films_found, dvd_films_added = api.get_stats()

   api.reset_counts()
   br_format_errors = populator.populate_files(br_titles)
   br_films_lookup, br_films_found, br_films_added = api.get_stats()

   api.reset_counts()
   rip_format_errors = populator.populate_files(offline_titles)
   rip_films_lookup, rip_films_found, rip_films_added = api.get_stats()




#   parse_films(dvd_titles, "DVDs", api, imdb)
#   parse_films(br_titles, "BluRay", api, imdb)
#   parse_films(files_titles, "File", api, imdb)
#   parse_films(offline_titles, "Rip", api, imdb)
#
#   api.print_stats()

   ############################
   # Report
   ############################
   print("Files  : " + str(len(files_titles)) + " (l:" + str(file_films_lookup) + " f:" + str(file_films_found) + " a:" + str(file_films_added) + ")")
   if file_format_errors:
      print("  Format Errors: " + str(file_format_errors))
   print("DVDs   : " + str(len(dvd_titles)) + " (l:" + str(dvd_films_lookup) + " f:" + str(dvd_films_found) + " a:" + str(dvd_films_added) + ")")
   if dvd_format_errors:
      print("  Format Errors: " + str(dvd_format_errors))
   print("BluRays: " + str(len(br_titles)) + " (l:" + str(br_films_lookup) + " f:" + str(br_films_found) + " a:" + str(br_films_added) + ")")
   if br_format_errors:
      print("  Format Errors: " + str(br_format_errors))
   print("Rips   : " + str(len(offline_titles)) + " (l:" + str(rip_films_lookup) + " f:" + str(rip_films_found) + " a:" + str(rip_films_added) + ")")
   if rip_format_errors:
      print("  Format Errors: " + str(rip_format_errors))
   print("Total  : " + str(len(br_titles) + len(dvd_titles) + len(files_titles) + len(offline_titles)))


if __name__ == "__main__":
   main(sys.argv[1:])

