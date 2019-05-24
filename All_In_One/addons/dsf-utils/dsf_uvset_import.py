import sys, os.path, logging
import bpy
from bpy.props import StringProperty

from .dsf_uvset_load import dsf_uvset_load
from .dsf_uvset_define import dsf_uvset_define

log = logging.getLogger ('import_uvset')

bl_info = {
  'name': 'import dsf uvset',
  'description': 'import a daz dsf file',
  'author': 'millighost',
  'version': (1, 0),
  'blender': (2,6,3),
  "category": "Learnbgame",
  'warning': '',
  'wiki_url': 'http://nonexistent',
}

def import_dsf_uvset_file (filename, context):
  """load the dsf-file and insert it as a blender uvset.
  """
  # parse the dsf-file.
  uvlib = dsf_uvset_load.read_dsf_data (filename)
  obj = context.active_object
  dsf_uvset_define.define_uvset (obj, uvlib)

# the rest defines the gui and the blender operator
class import_dsf_uvset (bpy.types.Operator):
  # the doc text is displayed in the tooltip of the menu entry.
  """Load a daz studio 4 dsf file."""
  # the bl_label is displayed in the operator-menu (with space-KEY).
  bl_label = 'import dsf-uvset'
  # the bl_idname member is used by blender to call this class.
  bl_idname = 'uv.dsf'
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
    import_dsf_uvset_file (self.properties.filepath, context)
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
  self.layout.operator (import_dsf_uvset.bl_idname, text = 'dsf-uvset (.dsf)')

def register ():
  """add an operator for importing dsf-files and
     registers a menu function for it."""
  bpy.utils.register_class (import_dsf_uvset)
  bpy.types.INFO_MT_file_import.append (menu_func)

def unregister ():
  """remove the operator for importing dsf-files."""
  bpy.utils.unregister_class (import_dsf_uvset)
  bpy.types.INFO_MT_file_import.remove (menu_func)
