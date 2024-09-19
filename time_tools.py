import logging


SECONDS_IN_YEAR   = 86400 * 365
SECONDS_IN_DAY    = 86400
SECONDS_IN_HOUR   = 3600
SECONDS_IN_MINUTE = 60


class TimeTools:

   class FilmFormatException(Exception):
      pass

   #################################################################
   #
   #  Converts a number of seconds to a string showing weeks, days,
   #  hours, minutes and seconds
   #
   #################################################################
   @staticmethod
   def convert_seconds_to_string(seconds):

      days = seconds // SECONDS_IN_DAY
      hours = (seconds % SECONDS_IN_DAY) // SECONDS_IN_HOUR
      minutes = (seconds % SECONDS_IN_HOUR) // SECONDS_IN_MINUTE
      seconds = seconds % SECONDS_IN_MINUTE

      result = []
      if days > 0:
         result.append(f"{days} day{'s' if days > 1 else ''}")
      if hours > 0:
         result.append(f"{hours} hour{'s' if hours > 1 else ''}")
      if minutes > 0:
         result.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
      if seconds > 0:
         result.append(f"{seconds} second{'s' if seconds > 1 else ''}")

      return ', '.join(result)


   #################################################################
   #
   #  Gets the number of days from seconds
   #
   #################################################################
   @staticmethod
   def get_days(seconds):
      return seconds // SECONDS_IN_DAY

