import os


AUDIO = {}
BLACKLIST = []


def preload():
  global AUDIO
  AUDIO = os.path.browse(
    directory="audio", extension="ogg", blacklist=BLACKLIST, recursive=True, nested=False
  )


def reload():
  AUDIO.clear()
  preload()
