import sys, os.path, logging
import bpy
from bpy.props import BoolProperty, StringProperty

from . import dsf_morph_load
from . import dsf_skey_define

log = logging.getLogger ('import_morph')

bl_info = {
  'name': 'import dsf morph',
  'description': 'import a daz dsf file',
  'author': 'millighost',
  'version': (1, 0),
  'blender': (2,6,3),
  'category': 'Import-Export',
  'warning': '',
  'wiki_url': 'http://nonexistent',
}

def import_dsf_morph_file (filename, context):
  """load the dsf-file and create a shapekey.
  """
  # parse the dsf-file.
  mod_lib = dsf_morph_load.read_dsf_data (filename)
  # apply the shapekeys from the modifier lib to the current object.
  obj = context.active_object
  dsf_skey_define.define_shapekeys (obj, mod_lib)

# the rest defines the gui and the blender operator
class import_dsf_morph (bpy.types.Operator):
  # the doc text is displayed in the tooltip of the menu entry.
  """Load a daz studio 4 dsf file."""
  # the bl_label is displayed in the operator-menu (with space-KEY).
  bl_label = 'import dsf-morph'
  # the bl_idname member is used by blender to call this class.
  bl_idname = 'shape.dsf'
  # the filepath seems to be hidden magic; the file-selector
  # menu places the chosen filename-string into it.
  # (changes sometimes; look for path/dirname/filepath)
  filepath = StringProperty\
      (name = 'file path', description = 'file path for importing dsf-file.',
       maxlen = 1000, default = '')
  filter_glob = StringProperty (default = '*.dsf')

  def execute (self, context):
    """display the gui and load a file. This function should be
       called after the menu entry for the file is selected."""
    # call the main import function. This function should work
    # independent of this context-manager/operator logic.
    import_dsf_morph_file (self.properties.filepath, context)
    return { 'FINISHED' }
  def invoke (self, context, event):
    """The invoke function should be called when the menu-entry for
       this operator is selected. It displays a file-selector and
       waits for execute() to be called."""
    context.window_manager.fileselect_add (self)
    return {'RUNNING_MODAL'}

def menu_func (self, context):
  """display the menu entry for calling the importer."""
  # the first parameter is the operator to call (by its bl_idname),
  # the text parameter is displayed in the menu.
  self.layout.operator (import_dsf_morph.bl_idname, text = 'dsf-morph (.dsf)')

def register ():
  """add an operator for importing dsf-files and
     registers a menu function for it."""
  bpy.utils.register_class (import_dsf_morph)
  bpy.types.INFO_MT_file_import.append (menu_func)

def unregister ():
  """remove the operator for importing dsf-files."""
  bpy.utils.unregister_class (import_dsf_morph)
  bpy.types.INFO_MT_file_import.remove (menu_func)
