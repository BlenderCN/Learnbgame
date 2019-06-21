'''Path Utilities (bpy.path)
   This module has a similar scope to os.path, containing utility
   functions for dealing with paths in Blender.
   
'''


def abspath(path, start=None, library=None):
   '''Returns the absolute path relative to the current blend file
      using the "//" prefix.
      
      Arguments:
      @start (string or bytes): Relative to this path,when not set the current filename is used.
      
      @library (bpy.types.Library): The library this path is from. This is only included forconvenience, when the library is not None its path replaces *start*.
      

   '''

   pass

def basename(path):
   '''Equivalent to os.path.basename, but skips a "//" prefix.
      Use for Windows compatibility.
      
   '''

   pass

def clean_name(name, replace='_'):
   '''Returns a name with characters replaced that
      may cause problems under various circumstances,
      such as writing to a file.
      All characters besides A-Z/a-z, 0-9 are replaced with "_"
      or the *replace* argument if defined.
      
   '''

   pass

def display_name(name):
   '''Creates a display string from name to be used menus and the user interface.
      Capitalize the first letter in all lowercase names,
      mixed case names are kept as is. Intended for use with
      filenames and module names.
      
   '''

   pass

def display_name_from_filepath(name):
   '''Returns the path stripped of directory and extension,
      ensured to be utf8 compatible.
      
   '''

   pass

def display_name_to_filepath(name):
   '''Performs the reverse of display_name using literal versions of characters
      which aren't supported in a filepath.
      
   '''

   pass

def ensure_ext(filepath, ext, case_sensitive=False):
   '''Return the path with the extension added if it is not already set.
      
      Arguments:
      @ext (string): The extension to check for, can be a compound extension. Shouldstart with a dot, such as '.blend' or '.tar.gz'.
      
      @case_sensitive (bool): Check for matching case when comparing extensions.

   '''

   pass

def is_subdir(path, directory):
   '''Returns true if *path* in a subdirectory of *directory*.
      Both paths must be absolute.
      
      Arguments:
      @path (string or bytes): An absolute path.

   '''

   pass

def module_names(path, recursive=False):
   '''Return a list of modules which can be imported from *path*.
      
      Arguments:
      @path (string): a directory to scan.
      @recursive (bool): Also return submodule names for packages.

      @returns (list): a list of string pairs (module_name, module_file).
   '''

   return list

def native_pathsep(path):
   '''Replace the path separator with the systems native os.sep.
      
   '''

   pass

def reduce_dirs(dirs):
   '''Given a sequence of directories, remove duplicates and
      any directories nested in one of the other paths.
      (Useful for recursive path searching).
      
      Arguments:
      @dirs (sequence): Sequence of directory paths.

      @returns (list): A unique list of paths.
   '''

   return list

def relpath(path, start=None):
   '''Returns the path relative to the current blend file using the "//" prefix.
      
      Arguments:
      @path (string or bytes): An absolute path.
      @start (string or bytes): Relative to this path,when not set the current filename is used.
      

   '''

   pass

def resolve_ncase(path):
   '''Resolve a case insensitive path on a case sensitive system,
      returning a string with the path if found else return the original path.
      
   '''

   pass

