import logging
import re
from lookup_imdb import IMDB

class DBPopulator:

   DVD = "DVD"
   BLURAY = "BluRay"
   FILE = "File"
   RIP = "Rip"

   def __init__(self, local_db_api, imdb, max_titles_to_process):

      self.imdb = imdb
      self.local_db = local_db_api
      self.not_found_in_imdb = []

      self.max_titles_to_process = max_titles_to_process
      self.num_films_processed = 0

   def populate_files(self, array_of_films):
      return self.populate_from_array(array_of_films, self.FILE)

   def populate_dvds(self, array_of_films):
      return self.populate_from_array(array_of_films, self.DVD)

   def populate_blurays(self, array_of_films):
      return self.populate_from_array(array_of_films, self.BLURAY)

   def populate_rips(self, array_of_films):
      return self.populate_from_array(array_of_films, self.RIP)

   def populate_from_array(self, array_of_films, type):
      pattern_mismatches = []
      num_processed = 0

      #process_max = 10
      try_imdb = True

      film_pattern = "(^[^\(]*) \(([^\)]*)"
      for title_year in array_of_films:

         if self.num_films_processed < self.max_titles_to_process:

            self.num_films_processed += 1
            num_processed += 1

            logging.debug("CHECK:" + title_year)
            res = re.match(film_pattern, title_year)
            if res:
               title = res.group(1)
               year = res.group(2)
               logging.debug(" TITLE:" + title)
               logging.debug("  YEAR:" + year)

               res = self.local_db.lookup_by_title_year(title, year)
               logging.debug("Found in DB:" + str(res))
   
               if len(res) > 0 and res[0]["imdbid"] != None:
                  logging.debug("First Film in DB [0]:" + str(res[0]))
                  logging.debug("Found film in DB")
               else:
                  logging.debug("Not Found in DB")

                  try:
                     if try_imdb:
                        details = self.imdb.get_details_from_title_year(title, year)
                        if len(details):
                           logging.debug("Found in IMDB:" + str(details))
                           self.local_db.add_film(title, year, type, False, details)
                        else:
                           logging.debug("Failed to find in IMDB:" + str(title_year))
                           self.not_found_in_imdb.append(title_year)
                  except IMDB.MaxCallsExceededException as e:
                     logging.debug("Max IMDB limit reached, not looking up")
                     try_imdb = False
                     #break

            else:
               logging.debug("Cannot process due to pattern mismatch:" + title_year)
               pattern_mismatches.append(title_year)

      logging.debug("Total: " + str(num_processed) + " IMDB Lookups:" + str(self.imdb.api_calls) + " Format Errors:" + str(len(pattern_mismatches)))
      return num_processed, pattern_mismatches

