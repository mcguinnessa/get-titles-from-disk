#!/usr/bin/python3

import logging
import getopt
import sys
import os
import re
#from film_manager.film_uploader import FilmUploader
#from network.script_record import ScriptRecordTable

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
   print(sys.argv[0]+" <-h> [--log <log level>] [-n <max_imdb_lookups>] [-m <max_records_to_process>")

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
   imdb = IMDB()
   fs = FileSystem(smb_server, smb_user, smb_password)
   br_dir = "\Films\BluRay"
   dvds_dir = "\Films\DVDs"
   files_dir = "\Films\Files"
   offline_dir = "\Films\Offline"

   br_titles = fs.listDir(br_dir)
   dvd_titles = fs.listDir(dvds_dir)
   files_titles = fs.listDir(files_dir)
   offline_titles = fs.listDir(offline_dir)

   parse_films(dvd_titles, "DVDs", api, imdb)
   parse_films(br_titles, "BluRay", api, imdb)
   parse_films(files_titles, "File", api, imdb)
   parse_films(offline_titles, "Rip", api, imdb)

   api.print_stats()

def parse_films(array_of_films, media_type, local_db, imdb):
   global num_films_processed
   global process_max
   global max_imdb_lookups

   film_pattern = "(^[^\(]*) \(([^\)]*)"
   for title_year in array_of_films:
      if process_max and num_films_processed >= process_max:
         break

      logging.debug("CHECK:" + title_year)
      res = re.match(film_pattern, title_year)
      if res:
         title = res.group(1)
         year = res.group(2)
         logging.debug(" TITLE:" + title) 
         logging.debug("  YEAR:" + year)

         res = local_db.get_film(title, year)
         logging.debug("Found in DB:" + str(res))

         if len(res) > 0 and res[0]["imdbid"] != None:
            logging.debug("First Film in DB [0]:" + str(res[0]))
            logging.debug("Found film in DB")
         else:
            logging.debug("Not Found in DB")
            
            if imdb.api_calls <= max_imdb_lookups:
               details = imdb.get_details_from_title_year(title, year)
               if len(details):
                  logging.debug("Found in IMDB:" + str(details))
                  local_db.add_film(title, year, media_type, False, details)
            else:
               logging.debug("Max IMDB limit reached, not looking up")
               break
    
         num_films_processed += 1

      logging.debug("Total: " + str(num_films_processed) + " IMDB Lookups:" + str(imdb.api_calls))

   imdb.print_stats()


if __name__ == "__main__":
   main(sys.argv[1:])

