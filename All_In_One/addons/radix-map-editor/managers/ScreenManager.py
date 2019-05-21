import os


SCREEN = {}
BLACKLIST = []


def preload():
  global SCREEN
  SCREEN = os.path.browse(
    directory="screens",
    extension="xml",
    blacklist=BLACKLIST,
    recursive=False,
    nested=False,
    hideExtension=True
  )


def reload():
  SCREEN.clear()
  preload()
