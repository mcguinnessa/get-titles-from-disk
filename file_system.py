
import smbclient
import logging


class FileSystem:
   """The NAS file system"""

   #################################################################
   #
   # Init for SAMBA connection
   #
   #################################################################
   def __init__(self, server, user, password):
      """Init"""
      self.server = server
      self.user = user
      self.password = password
      logging.debug("Connecting to "+ self.server+ " with user:" + self.user + " and " + self.password)
      smbclient.register_session(self.server, username=self.user, password=self.password)
     

   #################################################################
   #
   # Reads a file from the Samba share
   #
   #################################################################
   def readFile(self, filename):
      """Read File"""

      lines = []
      smb_file = r"\\" +self.server+ filename
      logging.debug("Reading file:" + smb_file)
      with smbclient.open_file(smb_file, mode="r") as fd:
         for line in fd:
            line = line.strip()
            logging.debug("line:" + line)
            lines.append(line)

      return lines

   #################################################################
   #
   # Reads a directory listing from the SAMBA Share
   #
   #################################################################
   def listDir(self, directory):
      """Lists the contents of the give directory"""

      titles = []
      #smbclient.register_session(self.server, username=self.user, password=self.password)

      smb_directory = r"\\" +self.server+ directory
      logging.debug("Listing directory:" + smb_directory)

      # List the files/directories inside a dir
      for filename in smbclient.listdir(smb_directory):
         logging.debug("Film:" + filename)
         titles.append(filename)

      return titles


      
