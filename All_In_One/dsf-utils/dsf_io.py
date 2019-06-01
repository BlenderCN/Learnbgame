import json, gzip, codecs, os, os.path

def open_text_file (filename, encoding = 'latin1'):
  """open a binary file and return a readable handle.
     check for compressed files and open with decompression.
  """
  first_bytes = open (filename, 'rb').read (2)
  if first_bytes == b'\x1f\x8b':
    # looks like a gzipped file.
    ifh = gzip.open (filename, 'rb')
  else:
    ifh = open (filename, 'rb')
  return codecs.getreader (encoding) (ifh)

def read_json_data (filename, **kwarg):
  """open the (possibly compressed) file and return its json data.
     the only supported kw-arg at the moment is 'encoding'
  """
  return json.load (open_text_file (filename, **kwarg))

def parent_dirs (path):
  """return the dirname of path, and its parents from bottom to up.
     if path is a directory, returns path, too.
  """
  if os.path.isdir (path):
    pdir = os.path.abspath (path)
  else:
    pdir = os.path.abspath (os.path.dirname (path))
  yield pdir
  ppdir = os.path.dirname (pdir)
  while ppdir != pdir:
    pdir = ppdir
    ppdir = os.path.dirname (pdir)
    yield pdir
  
def mkdir_p (dir):
  """mkdir -p equivalent."""
  if os.path.isdir (dir):
    return
  else:
    os.makedirs (dir, exist_ok = True)

def write_json_data (jdata, filepath, **kwarg):
  dirname, filename = os.path.split (filepath)
  if not os.path.isdir (dirname) and 'mkdir' in kwarg:
    mkdir_p (dirname)
  ofh = open (filepath, 'w')
  json.dump (jdata, ofh, indent = 2)
  ofh.close ()
                         
def find_data_parent (path):
  """given a path of a file or directory, find in the directory
     hierarchy upwards the lowest directory containing 'data'.
  """
  for dir in parent_dirs (path):
    candidate = os.path.join (dir, 'data')
    if os.path.isdir (candidate):
      return dir
  return None
