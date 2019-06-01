import os


MAPS = {}
BLACKLIST = []


def preload():
  global MAPS
  MAPS = os.path.browse(
    directory="maps",
    extension="xml",
    blacklist=BLACKLIST,
    recursive=True,
    nested=False,
    hideExtension=True
  )


def reload():
  MAPS.clear()
  preload()
