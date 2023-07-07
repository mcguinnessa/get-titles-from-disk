
import smbclient
import logging


class FileSystem:
   """The NAS file system"""

   def __init__(self, server, user, password):
      """Init"""
      self.server = server
      self.user = user
      self.password = password
      logging.debug("Connecting to "+ self.server+ " with user:" + self.user + " and " + self.password)
      

   def listDir(self, directoryo):
      """Lists the contents of the give directory"""

      titles = []

      smbclient.register_session(self.server, username=self.user, password=self.password)

      directory = r"\\" +self.server+ "\Films\BluRay"
      logging.debug("Listing directory:" + directory)

      # List the files/directories inside a dir
      for filename in smbclient.listdir(directory):
         logging.debug("Film:" + filename)
         titles.append(filename)

      return titles


      
