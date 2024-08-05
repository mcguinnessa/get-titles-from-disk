import re
import logging


FILM_PATTERN = re.compile("([^()]*) \((.*)\)$")

class FilmTitleTools:

   class FilmFormatException(Exception):
      pass

   ###############################################################
   #
   #  Splits the film name in the format Title (Year)
   #
   ###############################################################
   @staticmethod
   def split_title_year(title_year):
      logging.debug("CHECK:" + title_year)
#      film_pattern = "(^[^\(]*) \(([^\)]*)"

      title = None
      year = None

      res = re.match(FILM_PATTERN, title_year)
      if res:
         title = res.group(1)
         year = res.group(2)
         logging.debug(" TITLE:" + title)
         logging.debug("  YEAR:" + year)
      else:
         raise FilmTitleTools.FilmFormatException("Invalid title format:" + str(title_year))

      return title, year

