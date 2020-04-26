import urllib.request
import sys

url = r"https://bootstrap.pypa.io/get-pip.py"
urllib.request.urlretrieve(url, "get-pip.py")