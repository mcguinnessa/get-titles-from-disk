#! /usr/bin/python

import logging
import getopt
import sys
import os
import re
#from film_manager.film_uploader import FilmUploader
#from network.script_record import ScriptRecordTable

from film_database import FilmDatabase

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

   mongo_user = os.environ["MONGODB_USER"]
   mongo_pass = os.environ["MONGODB_PASS"]
   mongo_server = os.environ["MONGODB_HOST"]
   mongo_port = os.environ["MONGODB_PORT"]

   db = FilmDatabase(mongo_user, mongo_pass, mongo_server, mongo_port)
   fs = FileSystem(smb_server, smb_user, smb_password)
   br_dir = "\Films\BluRay"
   dvds_dir = "\Films\DVDs"

   br_titles = fs.listDir(br_dir)
   dvd_titles = fs.listDir(dvds_dir)

   #logging.debug("Titles:" + str(titles))

   film_pattern = "(^[^\(]*) \(([^\)]*)"

   for btitle_year in br_titles:
      logging.debug("CHECK:" + btitle_year)
      res = re.match(film_pattern, btitle_year)
      if res:
         title = res.group(1)
         year = res.group(2)
         logging.debug("MATCH TITLE:" + title) 
         logging.debug("       YEAR:" + year)
         db.add_bluray(title, year)

   for dtitle_year in dvd_titles:
      logging.debug("CHECK:" + dtitle_year)
      res = re.match(film_pattern, dtitle_year)
      if res:
         title = res.group(1)
         year = res.group(2)
         logging.debug("MATCH TITLE:" + title) 
         logging.debug("       YEAR:" + year)
         db.add_dvd(title, year)



   




#   if max_records:
#      film_uploader = FilmUploader(num_lookups, max_records)
#   else:
#      film_uploader = FilmUploader(num_lookups)
#
#   film_uploader.upload_films_from_file_system()
#   film_uploader.print_file_update_result()
#
#   status = film_uploader.get_exit_status()
#   summary = film_uploader.get_summary()
#   #logging.debug("summary:" + str(summary))
#   #logging.debug("summary len:" + str(len(str(summary))))
#   #logging.debug(__file__)

   #store in database (__file__, status, summary)
#   script_records = ScriptRecordTable()

#   summary="this is a summary"

#   scriptname = os.path.basename(__file__)
#   script_records.add(scriptname, status, summary)

if __name__ == "__main__":
   main(sys.argv[1:])

