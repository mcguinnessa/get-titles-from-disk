
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
         # DO NOT DELETE COMMENT
         #logging.debug([ord(char) for char in filename])


         if "" in filename:
            filename = filename.replace("",':')
            logging.debug("Film[corrected]:" + filename)

         #filename2 = filename.replace("\u61474", ":")
         #logging.debug("Film[editted]:" + filename2)
         ##logging.debug([ord(char) for char in filename2])

         #import re 
         #filename3 = re.sub(r'[^\x00-\x7F]+',' ', filename)
         #filename3 = re.sub("\U00061474",':', filename)
         #filename3 = filename.replace("\U00061474",':')
         filename3 = filename.replace("",':')
         #filename3 = re.sub(r'\xF022',':', filename)
         #logging.debug("Film[editted2]:" + filename3)
         #logging.debug([ord(char) for char in filename3])
         
         titles.append(filename)

      return titles


      
