
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
      

   def listDir(self, directory):
      """Lists the contents of the give directory"""

      titles = []

      smbclient.register_session(self.server, username=self.user, password=self.password)

      smb_directory = r"\\" +self.server+ directory
      logging.debug("Listing directory:" + smb_directory)

      # List the files/directories inside a dir
      for filename in smbclient.listdir(smb_directory):
         logging.debug("Film:" + filename)
         titles.append(filename)

      return titles


      
