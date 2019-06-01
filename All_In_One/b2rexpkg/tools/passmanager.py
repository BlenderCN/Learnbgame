"""
Password Manager
"""

from .user import home
import os
import json

class PasswordManager(object):
    def __init__(self, realm):
        self.config = {}
        realm = "."+realm
        appdir = os.path.join(home, realm)
        if not os.path.exists(appdir):
            os.makedirs(appdir)
        self.appfile = os.path.join(appdir, "connections")
        if os.path.exists(self.appfile):
            self.load_config()
    def load_config(self):
        """
        Load the configuration.
        """
        f = open(self.appfile, "r")
        data = f.read()
        f.close()
        self.config = json.loads(data)

    def save_config(self):
        """
        Save the configuration.
        """
        if self.config:
            f = open(self.appfile, "w")
            data = f.write(json.dumps(self.config))
            f.close()

    def get_credentials(self, url, username=""):
        """
        Get the credentials for a certain server.
        """
        if url in self.config:
            for con_user in self.config[url]:
                if con_user == username or not username:
                    return (username, self.config[url][con_user])
        return ("", "")
    def set_credentials(self, url, username, password):
        """
        Set the credentials for a certain server.
        """
        if not url in self.config:
            self.config[url] = {}
        self.config[url][username] = password
        self.save_config()

