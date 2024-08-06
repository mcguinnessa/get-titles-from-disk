
from film_title_tools import FilmTitleTools
import logging


class FilmWatchedUpdater:


   def __init__(self, local_db, process_max):
      self.local_db = local_db
      self.process_max = process_max

      self.invalid_format = []
      self.not_found_in_db = []
      self.found_in_db = []
      self.already_watched = []
      self.newly_watched = []

   def get_stats(self):
      return self.newly_watched, self.already_watched, self.found_in_db, self.not_found_in_db, self.invalid_format


   def set_films_as_watched(self, film_list):
      num_processed = 0

      for title_year in film_list:

         logging.debug("Count:" + str(num_processed) + "/" + str(self.process_max))
         if num_processed < self.process_max:
            num_processed += 1
         else:
            break

         try:
            title, year = FilmTitleTools.split_title_year(title_year)
            logging.debug("Title:" + title)
            logging.debug("Year:" + year)

            deets = self.local_db.lookup_by_title_year(title, year)
            if deets:
               self.found_in_db.append(title_year)
               logging.debug("Found Film Details:" + str(deets))
               watched = deets[0]['watched'] 
               #id = deets[0]['_id'] 
               imdbid = deets[0]['imdbid'] 
               logging.debug("Watched:" + str(watched))
               #logging.debug("ID:" + str(id))
               logging.debug("IMDBID:" + str(imdbid))

               if watched:
                  logging.debug(title_year + " already marked as watched")
                  self.already_watched.append(title_year)

               else:
                  logging.debug(title_year + " newly marked as watched")
                  self.local_db.update_watched_for_film(imdbid, True)
                  self.newly_watched.append(title_year)
                   
            else:
               self.not_found_in_db.append(title_year)

         except FilmTitleTools.FilmFormatException as e:
            self.invalid_format.append(title_year)
            logging.debug("Invalid Format:" + str(title_year))
 
      return num_processed 
