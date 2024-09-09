import logging
#import re
from lookup_imdb import IMDB

from film_title_tools import FilmTitleTools

class DBPopulator:

   DVD = "DVD"
   BLURAY = "BluRay"
   FILE = "File"
   RIP = "Rip"

   def __init__(self, local_db_api, imdb, max_titles_to_add_to_db, max_titles_to_process, imdbid_map):

      self.imdb = imdb
      self.local_db = local_db_api
      #self.not_found_in_imdb = []

      self.imdbid_map = imdbid_map
      if not self.imdbid_map:
         self.imdbid_map = {}

      self.max_titles_to_add_to_db = max_titles_to_add_to_db
      self.max_titles_to_process = max_titles_to_process
      self.num_films_processed = 0
      self.num_films_added_to_db = 0

   def populate_files(self, array_of_films):
      return self.populate_from_array(array_of_films, self.FILE)

   def populate_dvds(self, array_of_films):
      return self.populate_from_array(array_of_films, self.DVD)

   def populate_blurays(self, array_of_films):
      return self.populate_from_array(array_of_films, self.BLURAY)

   def populate_rips(self, array_of_films):
      return self.populate_from_array(array_of_films, self.RIP)

###########################################################################
#
# Processes a list of records of a given type
#
###########################################################################
   def populate_from_array(self, array_of_films, type):
      pattern_mismatches = []
      num_processed = 0
      not_found_in_imdb = []

      #process_max = 10
      try_imdb = True

      for title_year in array_of_films:

         logging.debug("added:" + str(self.num_films_added_to_db) + "/" + str(self.max_titles_to_add_to_db))
         if self.num_films_added_to_db >= self.max_titles_to_add_to_db:
            logging.debug("Max records added:" + str(self.max_titles_to_add_to_db))
            break

         logging.debug("processed:" + str(self.num_films_processed) + "/" + str(self.max_titles_to_process))
         if self.num_films_processed >= self.max_titles_to_process:
            logging.debug("Max records processed:" + str(self.num_films_processed))
            break
         else:
            num_processed += 1
            self.num_films_processed += 1

         try:             
            title, year = FilmTitleTools.split_title_year(title_year)
          # if title and year:

            res = self.local_db.lookup_by_title_year(title, year)
            logging.debug("Found in DB:" + str(res))

            if len(res) > 0 and res[0]["imdbid"] != None:
               logging.debug("First Film ("+str(title_year)+") found in DB [0]:" + str(res[0]))
            else:
               logging.debug("Not Found in DB: " + str(title_year))


               try:
                  if try_imdb:
                     if title_year in self.imdbid_map:
                        imdbid = self.imdbid_map[title_year]
                        logging.debug(title_year + " is in local override file, not looking in IMDB, using " + str(imdbid))
                        details = self.imdb.get_data_from_imdbid(imdbid)
                        logging.debug("Details:" + str(details)) 
                     else:
                        details = self.imdb.get_details_from_title_year(title, year)

                     if len(details):
                        logging.debug("Found "+title_year+" in IMDB:" + str(details))

                        if self.local_db.add_film(title, year, type, False, details):
                           self.num_films_added_to_db += 1
                        else:
                           logging.debug("Failed to add to DB:" + str(title_year))
                     else:
                        logging.debug("Failed to find in IMDB:" + str(title_year))
                        not_found_in_imdb.append(title_year)
               except IMDB.IMDBResponseException as e:
                  logging.debug("Error parsing response from IMDB")
                  not_found_in_imdb.append(title_year)
               except IMDB.MaxCallsExceededException as e:
                  logging.debug("Max IMDB limit reached, not looking up")
                  try_imdb = False
               except IMDB.MaxAPICallsExceededException as e:
                  logging.debug("Hard Max API limit reached, not looking up")
                  try_imdb = False
               except IMDB.IMDBAPIException as e:
                  logging.debug("Can't access IMDB")
                  try_imdb = False
         except FilmTitleTools.FilmFormatException as e:
            logging.debug("Cannot process due to pattern mismatch:" + title_year)
            pattern_mismatches.append(title_year)

      logging.debug("Total: " + str(num_processed) + " IMDB Lookups:" + str(self.imdb.api_calls) + " Format Errors:" + str(len(pattern_mismatches)))
      return num_processed, pattern_mismatches, not_found_in_imdb

###########################################################################
#
# Processes a list of records of a given type
#
###########################################################################
   def update_oldest_records(self, num_records):
      pattern_mismatches = []
      num_processed = 0
      #updated_in_imdb = []
      failed_to_update = []
      try_imdb = True

      to_update = self.local_db.get_oldest_records(num_records)

      logging.debug("To Update:" + str(to_update))

      try:

         #for imdbid, title_year in to_update.items():
         for imdbid, title_year in to_update.items():
            if try_imdb:
               details = self.imdb.get_data_from_imdbid(imdbid)
               if len(details):
                  logging.debug("Found "+str(title_year)+" in IMDB:" + str(details))
                      
                  t = title_year[0]
                  y = title_year[1]
                  #self.local_db.add_film(t, y, type, False, details)
                  if not self.local_db.update_film(imdbid, details):
                     failed_to_update.append(title_year)
     
                  #title_year = f"{t} ({y})" 
                  #updated_in_imdb.append(title_year)
               else:
                  logging.debug("Failed to find in IMDB:" + str(title_year))
                  #not_found_in_imdb.append(title_year)
                  failed_to_update.append(title_year)

      except IMDB.IMDBResponseException as e:
         logging.debug("Error parsing response from IMDB")
         #not_found_in_imdb.append(title_year)
      except IMDB.MaxCallsExceededException as e:
         logging.debug("Max IMDB limit reached, not looking up")
         try_imdb = False
      except IMDB.IMDBAPIException as e:
         logging.debug("Can't access IMDB")
         try_imdb = False

      return failed_to_update


