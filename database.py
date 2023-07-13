
import logging
import pymongo


class Database:
   """The Database"""

   def __init__(self, user, password, server, port):
      """Init"""
      self.server = server
      self.port = port
      self.user = user
      self.password = password
      logging.debug("Connecting to "+ self.server+ ":" + self.port + " with user:" + self.user + " and " + self.password)
      self.conn_str = "mongodb://"+self.user+":"+self.password+"@"+self.server+":" + self.port+ "/"

#   def add_film(self, film_name, film_year):
#      """Add film title and year"""
#
#      myclient = pymongo.MongoClient("mongodb://"+self.user+":"+self.password+"@"+self.server+":" + self.port+ "/")
#      mydb = myclient["FilmDatabase"]
#      mycol = mydb["owned"]
#
#      record = { "$set": { "title": film_name, "year": film_year }}
#
#      query = { 'title': film_name, 'year': film_year}
#      #x = mycol.insert_one(mydict)
#      x = mycol.update_one(query, record, True)

