#!/usr/bin/python

import smbclient
import os

user = os.environ["SMB_USER"]
server = os.environ["SMB_HOST"]
password = os.environ["SMB_PASS"]


# Optional - specify the default credentials to use on the global config object
smbclient.ClientConfig(username=user, password=password)

# Optional - register the credentials with a server (overrides ClientConfig for that server)
smbclient.register_session(server, username=user, password=password)

#smbclient.mkdir(r"\\server\share\directory", username=user, password=password)

#file = r"\\192.168.0.130\Music\file2.txt"
#with smbclient.open_file(file, mode="w") as fd:
#    fd.write(u"file contents")

#directory = r"\\192.168.0.130\Films\BluRay"
directory = r"\\" +server+ "\Films\BluRay"

# List the files/directories inside a dir
for filename in smbclient.listdir(directory):
    print(filename)
