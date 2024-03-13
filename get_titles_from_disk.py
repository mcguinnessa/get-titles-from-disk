#!/usr/bin/python3

import logging
import getopt
import sys
import os
import re
#from film_manager.film_uploader import FilmUploader
#from network.script_record import ScriptRecordTable

from lookup_imdb import get_titles
from lookup_imdb import get_details_from_title_year
from lookup_imdb import print_stats as print_imdb_stats

from film_api import FilmAPI

#from film_database import FilmDatabase
#from film_database import FilmDatabase

from file_system import FileSystem

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
   try:
       opts, args = getopt.getopt(argv, "ln:m:", ["log="])
   except getopt.GetoptError:
      usage()
      sys.exit(2)

   loglevel = "DEBUG"
   num_lookups = -1
   max_records = None

   for opt, arg in opts:
      if opt in ("-l", "--log"):
         loglevel = arg.upper()
      elif opt in ("-n"):
         num_lookups = int(arg)
      elif opt in ("-m"):
         max_records = int(arg)

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

   smb_user = os.environ["SMB_USER"]
   smb_server = os.environ["SMB_HOST"]
   smb_password = os.environ["SMB_PASS"]

#   mongo_user = os.environ["MONGODB_USER"]
#   mongo_pass = os.environ["MONGODB_PASS"]
#   mongo_server = os.environ["MONGODB_HOST"]
#   mongo_port = os.environ["MONGODB_PORT"]

#   db = FilmDatabase(mongo_user, mongo_pass, mongo_server, mongo_port)
 
   server = "192.168.0.160"
   port = "80"
   api = FilmAPI(server, port)
   fs = FileSystem(smb_server, smb_user, smb_password)
   br_dir = "\Films\BluRay"
   dvds_dir = "\Films\DVDs"
   files_dir = "\Films\Files"
   offline_dir = "\Films\Offline"

#   import time
#   time.sleep(600)

   br_titles = fs.listDir(br_dir)
   dvd_titles = fs.listDir(dvds_dir)

   #logging.debug("Titles:" + str(titles))
   #logging.debug("Titles:" + str(titles[0]))

   film_pattern = "(^[^\(]*) \(([^\)]*)"

   num = 0
   for btitle_year in br_titles:
      if num >= 2:
         break
      logging.debug("CHECK:" + btitle_year)
      res = re.match(film_pattern, btitle_year)
      if res:
         title = res.group(1)
         year = res.group(2)
         logging.debug("MATCH TITLE:" + title) 
         logging.debug("       YEAR:" + year)

         res = api.get_film(title, year)
         logging.debug("Found in DB:" + str(res))
         logging.debug("len Res:" + str(len(res)))

         if len(res) > 0 and res[0]["imdbid"] != None:
            logging.debug("First Film in DB [0]:" + str(res[0]))
            logging.debug("Found film in DB")
         else:
            logging.debug("Not Found in DB")
            details = get_details_from_title_year(title, year)
            if len(details):
               logging.debug("Found in IMDB:" + str(details))
               api.add_film(title, year, "BluRay", details)
       
 #        db.add_bluray(title, year)
         num += 1

   print_imdb_stats()
   api.print_stats()


if __name__ == "__main__":
   main(sys.argv[1:])

