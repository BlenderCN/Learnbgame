'''Utilities (bpy.utils)
   This module contains utility functions specific to blender but
   not associated with blenders internal data.
   
'''


def app_template_paths(subdir=None):
   '''Returns valid application template paths.
      
      Arguments:
      @subdir (string): Optional subdir.

      @returns (generator): app template paths.
   '''

   return generator

def blend_paths(absolute=False, packed=False, local=False):
   '''Returns a list of paths to external files referenced by the loaded .blend file.
      
      Arguments:
      @absolute (boolean): When true the paths returned are made absolute.
      @packed (boolean): When true skip file paths for packed data.
      @local (boolean): When true skip linked library paths.

      @returns ([str]): path list.
   '''

   return [str]

def escape_identifier(string):
   '''Simple string escaping function used for animation paths.
      
      Arguments:
      @string (string): text

      @returns (str): The escaped string.
   '''

   return str

def keyconfig_set(filepath, report=None):
   

   pass

def load_scripts(reload_scripts=False, refresh_scripts=False):
   '''Load scripts and run each modules register function.
      
      Arguments:
      @reload_scripts (bool): Causes all scripts to have their unregister methodcalled before loading.
      
      @refresh_scripts (bool): only load scripts which are not already loadedas modules.
      

   '''

   pass

def make_rna_paths(struct_name, prop_name, enum_name):
   '''Create RNA "paths" from given names.
      
      Arguments:
      @struct_name (string): Name of a RNA struct (like e.g. "Scene").
      @prop_name (string): Name of a RNA struct's property.
      @enum_name (string): Name of a RNA enum identifier.

      @returns (tuple of strings): A triple of three "RNA paths"(most_complete_path, "struct.prop", "struct.prop:'enum'").
      If no enum_name is given, the third element will always be void.
      
   '''

   return tuple of strings

def manual_map():
   

   pass

def modules_from_path(path, loaded_modules):
   '''Load all modules in a path and return them as a list.
      
      Arguments:
      @path (string): this path is scanned for scripts and packages.
      @loaded_modules (set): already loaded module names, files matching thesenames will be ignored.
      

      @returns (list): all loaded modules.
   '''

   return list

def preset_find(name, preset_path, display_name=False, ext='.py'):
   

   pass

def preset_paths(subdir):
   '''Returns a list of paths for a specific preset.
      
      Arguments:
      @subdir (string): preset subdirectory (must not be an absolute path).

      @returns (list): script paths.
   '''

   return list

def refresh_script_paths():
   '''Run this after creating new script paths to update sys.path
      
   '''

   pass

def register_class(cls):
   '''Register a subclass of a blender type in (bpy.types.Panel,
      bpy.types.UIList, bpy.types.Menu, bpy.types.Header,
      bpy.types.Operator, bpy.types.KeyingSetInfo,
      bpy.types.RenderEngine).
      If the class has a *register* class method it will be called
      before registration.
      .. note::
      ValueError exception is raised if the class is not a
      subclass of a registerable blender class.
      
   '''

   pass

def register_manual_map(manual_hook):
   

   pass

def register_module(module, verbose=False):
   

   pass

def register_submodule_factory(module_name, submodule_names):
   '''Utility function to create register and unregister functions
      which simply load submodules,
      calling their register & unregister functions.
      .. note::
      Modules are registered in the order given,
      unregistered in reverse order.
      
      Arguments:
      @module_name (string): The module name, typically __name__.
      @submodule_names (list of strings): List of submodule names to load and unload.

      @returns (tuple pair of functions): register and unregister functions.
   '''

   return tuple pair of functions

def resource_path(type, major=bpy.app.version[0], minor=bpy.app.version[1]):
   '''Return the base path for storing system files.
      
      Arguments:
      @type (string): string in ['USER', 'LOCAL', 'SYSTEM'].
      @major (int): major version, defaults to current.
      @minor (string): minor version, defaults to current.

      @returns (str): the resource path (not necessarily existing).
   '''

   return str

def script_path_pref():
   '''returns the user preference or None
      
   '''

   pass

def script_path_user():
   '''returns the env var and falls back to home dir or None
      
   '''

   pass

def script_paths(subdir=None, user_pref=True, check_all=False, use_user=True):
   '''Returns a list of valid script paths.
      
      Arguments:
      @subdir (string): Optional subdir.
      @user_pref (bool): Include the user preference script path.
      @check_all (bool): Include local, user and system paths rather just the pathsblender uses.
      

      @returns (list): script paths.
   '''

   return list

def smpte_from_frame(frame, fps=None, fps_base=None):
   '''Returns an SMPTE formatted string from the *frame*:
      HH:MM:SS:FF.
      If *fps* and *fps_base* are not given the current scene is used.
      
      Arguments:
      @frame (int or float.): frame number.

      @returns (str): the frame string.
   '''

   return str

def smpte_from_seconds(time, fps=None):
   '''Returns an SMPTE formatted string from the *time*:
      HH:MM:SS:FF.
      If the *fps* is not given the current scene is used.
      
      Arguments:
      @time (int, float or datetime.timedelta.): time in seconds.

      @returns (str): the frame string.
   '''

   return str

def time_from_frame(frame, fps=None, fps_base=None):
   '''Returns the time from a frame number .
      If *fps* and *fps_base* are not given the current scene is used.
      
      Arguments:
      @frame (int or float.): number.

      @returns (datetime.timedelta): the time in seconds.
   '''

   return datetime.timedelta

def time_to_frame(time, fps=None, fps_base=None):
   '''Returns a float frame number from a time given in seconds or
      as a datetime.timedelta object.
      If *fps* and *fps_base* are not given the current scene is used.
      
      Arguments:
      @time (number or a datetime.timedelta object): time in seconds.

      @returns (float): the frame.
   '''

   return float

def unregister_class(cls):
   '''Unload the python class from blender.
      If the class has an *unregister* class method it will be called
      before unregistering.
      
   '''

   pass

def unregister_manual_map(manual_hook):
   

   pass

def unregister_module(module, verbose=False):
   

   pass

def user_resource(resource_type, path='', create=False):
   '''Return a user resource path (normally from the users home directory).
      
      Arguments:
      @type (string): Resource type in ['DATAFILES', 'CONFIG', 'SCRIPTS', 'AUTOSAVE'].
      @subdir (string): Optional subdirectory.
      @create (boolean): Treat the path as a directory and createit if its not existing.
      

      @returns (str): a path.
   '''

   return str

