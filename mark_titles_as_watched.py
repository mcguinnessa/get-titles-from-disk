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


FILM_PATTERN = re.compile("([^()]*) \((.*)\)$")

#########################################################################################
#
# Usage
#
#########################################################################################
def usage():
   print("\n")
   print(sys.argv[0]+" <-h> [--log <log level>] [-n <max_imdb_lookups>] [-m <max_records_to_process>")

class FilmFormatException(Exception):
   pass

#########################################################################################
#
# Main
#
#########################################################################################
def main(argv):
#   global process_max
#   global max_imdb_lookups



   try:
       opts, args = getopt.getopt(argv, "ln:", ["log="])
   except getopt.GetoptError:
      usage()
      sys.exit(2)

   loglevel = "DEBUG"

   for opt, arg in opts:
      if opt in ("-l", "--log"):
         loglevel = arg.upper()
      elif opt in ("-i"):
         num_process = int(arg)
#      elif opt in ("-f"):
#         process_max = int(arg)

   numeric_log_level = getattr(logging, loglevel, None)

#   logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename='/var/log/film_manager/upload_from_files.log', filemode='w', level=logging.DEBUG)
   logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filemode='w', level=logging.DEBUG)
#   logging.getLogger("imdbpy").setLevel(logging.ERROR)
#   logging.getLogger("smbprotocol").setLevel(logging.ERROR)
   console = logging.StreamHandler()

   #console.setLevel(logging.INFO)
   console.setLevel(logging.DEBUG)

   formatter = logging.Formatter('%(levelname)-8s %(message)s')
   console.setFormatter(formatter)
#   logging.getLogger('').addHandler(console)

   filename = "./watched.txt"

   logging.info("Marking films as watched")
   pfilms = read_file(filename)

   server = "192.168.0.160"
   port = "80"
   api = FilmAPI(server, port)


   not_found_in_db = []
   for film in pfilms:
      deets = api.get_film(film[0], film[1])

      if deets:
         print("Details:" + str(deets))
      else:
         not_found_in_db.append(f"{film[0]} {film[1]}")

   for nf in not_found_in_db:
      print("Failed to find in DB:" + str(nf))


def read_file(filename):

   # Open the file using 'with' statement to ensure proper resource management
   with open(filename, 'r') as file:

      films = []
      invalid_format = []

      for line in file:
         
         try:
            title_year = line.strip()
            print(title_year)
            title, year = split_title(title_year)

            print("Title:" + title)
            print("Year:" + year)
         
            films.append([title, year])
         except FilmFormatException as e:
            invalid_format.append(title_year)

      print("Invalid Format:" + str(invalid_format))  
      return films



def split_title(title_year):

   m = FILM_PATTERN.match(title_year)
   if m:
      title = str(m.group(1))
      year = str(m.group(2))
#      print("Title:" + title)
#      print("Year:" + year)
      return title, year
   else:
     raise FilmFormatException

  



if __name__ == "__main__":
   main(sys.argv[1:])

