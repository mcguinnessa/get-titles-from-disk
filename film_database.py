
import logging
import pymongo

from database import Database


class FilmDatabase(Database):
   """The Film Database"""

   DATABASE_NAME = "FilmDatabase"

   def __init__(self, user, password, server, port):
      """Init"""
      super(FilmDatabase, self).__init__(user, password, server, port) 
#      self.server = server
#      self.port = port
#      self.user = user
#      self.password = password
#      logging.debug("Connecting to "+ self.server+ ":" + self.port + " with user:" + self.user + " and " + self.password)
      self.client = pymongo.MongoClient(self.conn_str)
      self.db = self.client[self.DATABASE_NAME]

   def add_bluray(self, film_name, film_year):
      """Add film title and year as a BR"""
      mycol = self.db["owned"]
      record = { "$set": { "title": film_name, "year": film_year, "bluray": True }}

      query = { 'title': film_name, 'year': film_year}
      #x = mycol.insert_one(mydict)
      res = mycol.update_one(query, record, True)
      logging.debug("Added BluRay - matched:" + str(res.matched_count) + " modified:" + str(res.modified_count) + " upserted_id:" + str(res.upserted_id) + " ack:" + str(res.acknowledged))

   def add_dvd(self, film_name, film_year):
      """Add film title and year as a DVD"""

      mycol = self.db["owned"]
      record = { "$set": { "title": film_name, "year": film_year, "dvd": True }}

      query = { 'title': film_name, 'year': film_year}
      #x = mycol.insert_one(mydict)
      res = mycol.update_one(query, record, True)
      logging.debug("Added DVD - matched:" + str(res.matched_count) + " modified:" + str(res.modified_count) + " upserted_id:" + str(res.upserted_id) + " ack:" + str(res.acknowledged))

   def add_file(self, film_name, film_year):
      """Add film title and year as a file"""

      mycol = self.db["owned"]
      record = { "$set": { "title": film_name, "year": film_year, "dvd": True }}

      query = { 'title': film_name, 'year': film_year}
      #x = mycol.insert_one(mydict)
      res = mycol.update_one(query, record, True)
      logging.debug("Added DVD - matched:" + str(res.matched_count) + " modified:" + str(res.modified_count) + " upserted_id:" + str(res.upserted_id) + " ack:" + str(res.acknowledged))

   def close(self):
      self.client.close()

   def __del__(self):
      self.close()
     
   
