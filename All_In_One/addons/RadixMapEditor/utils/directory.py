import bpy
import os


def browse(
    directory,
    extension='',
    blacklist=None,
    recursive=False,
    files=True,
    nested=True,
    hideExtension=False
  ):
  blacklist = blacklist or []
  prefs = bpy.context.user_preferences.addons[__package__.rpartition(".")[0]].preferences
  dataDir = os.path.expanduser(prefs.dataDir)
  entries = {}

  if not directory or not os.path.isdir(dataDir):
    return entries

  path = os.path.join(dataDir, directory)

  if os.path.isdir(path):
    for entry in os.listdir(path):
      if entry not in blacklist:
        if os.path.isfile(os.path.join(path, entry)) and files:
          if hideExtension:
            key = os.path.splitext(entry)[0]
          else:
            key = entry

          if extension:
            if entry.endswith("." + extension):
              entries[key] = entry.rstrip("." + extension)
          else:
            entries[key] = entry
        elif os.path.isdir(path):
          if not files:
            entries[entry] = entry

          if recursive:
            recrsiveDir = os.path.join(directory, entry)
            entries[entry] = browse(
              directory=recrsiveDir,
              extension=extension,
              blacklist=blacklist,
              recursive=recursive,
              files=files,
              nested=True,
              hideExtension=hideExtension
            )

  if nested:
    return entries
  else:
    return dictTransformKeys(entries)


def dictTransformKeys(data, prefix=""):
  """Convert dictionary keys to as single string"""
  values = {}
  for k, v in data.items():
    if prefix and not prefix.endswith("/"):
      prefix = prefix + "/"

    if isinstance(v, dict):
      values.update(dictTransformKeys(v, prefix + k))
    else:
      values.update({prefix + k: prefix + v})
  return values
