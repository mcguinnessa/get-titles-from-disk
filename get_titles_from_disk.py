#! /usr/bin/python

import logging
import getopt
import sys
import os
#from film_manager.film_uploader import FilmUploader
#from network.script_record import ScriptRecordTable

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
   logging.getLogger("imdbpy").setLevel(logging.ERROR)
   logging.getLogger("smbprotocol").setLevel(logging.ERROR)
   console = logging.StreamHandler()

   #console.setLevel(logging.INFO)
   console.setLevel(logging.DEBUG)

   formatter = logging.Formatter('%(levelname)-8s %(message)s')
   console.setFormatter(formatter)
   logging.getLogger('').addHandler(console)

   logging.info("Storing titles from File System")

   smb_user = os.environ["SMB_USER"]
   smb_server = os.environ["SMB_HOST"]
   smb_password = os.environ["SMB_PASS"]


   fs = FileSystem(smb_server, smb_user, smb_password)
   titles = fs.listDir("dir")
   logging.debug("Titles:" + str(titles))

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

