import os.path, os, json

def find_libdir_head (filepath):
  """get the root of the library directory (directory that contains data).
     filepath is a filename with in the library or a directory.
  """
  if os.path.isdir (filepath):
    path, base = filepath, ''
  else:
    path, base = os.path.split (filepath)
  while len (base) > 0:
    data_neighbor = os.path.join (path, 'data')
    if os.path.isdir (data_neighbor):
      return path
    path, base = os.path.split (path)
  raise Exception ("no library directory found.")

class daz_library (object):
  """class to manage some files within a daz library.
  """
  def __init__ (self, filepath = None, group = ''):
    """initialize with a file within the library.
    """
    self.indent = 2
    self.libdir = find_libdir_head (filepath)
    self.group = group
  def get_abspath (self, libpath):
    """get the absolute filesystem path for a file within the library.
    """
    as_rel = '.' + os.sep + libpath
    return os.path.abspath (os.path.join (self.libdir, as_rel))
  def get_libpath (self, abspath):
    """get the libpath for an absolute path.
    """
    relpath = os.path.relpath (abspath, self.libdir)
    return os.sep + relpath
  def get_data_libpath (self, id):
    """return a libpath for the given id.
    """
    return os.path.join ('/data', self.group, id + '.dsf')
  def create_output_stream (self, libpath):
    """open a file for output in the library, creating intermediate directories
       if necessary.
    """
    abspath = self.get_abspath (libpath)
    ofh = open (abspath, 'w')
    return ofh
  def write_local_file (self, data, libpath):
    """write an object to the local libpath.
    """
    ofh = self.create_output_stream (libpath)
    json.dump (data, ofh, indent = self.indent, sort_keys = True)
    ofh.close ()
    return libpath
  def write_geometry_data (self, id, data):
    """create a file in the library containing geometry definitions for
       a geometry with id.
       Returns the created relative filepath.
    """
    libpath = self.get_data_libpath (id)
    self.write_local_file (data, libpath)
    return libpath

