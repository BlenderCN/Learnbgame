import sys, os.path, logging
import bpy
from bpy.props import BoolProperty, StringProperty

from . import dsf_pose_load

log = logging.getLogger ('import_pose')

bl_info = {
  'name': 'import dsf pose',
  'description': 'import a daz dsf file',
  'author': 'millighost',
  'version': (1, 0),
  'blender': (2,6,3),
  "category": "Learnbgame",
  'warning': '',
  'wiki_url': 'http://nonexistent',
}

def import_dsf_pose_file (filename, context):
  """load the dsf-file and apply it to the current object.
  """
  # parse the dsf-file.
  pose_data = dsf_pose_load.load_pose_file (filename)
  obj = context.active_object
  return pose_data

# the rest defines the gui and the blender operator
class import_dsf_pose (bpy.types.Operator):
  # the doc text is displayed in the tooltip of the menu entry.
  """Load a daz studio 4 dsf file."""
  # the bl_label is displayed in the operator-menu (with space-KEY).
  bl_label = 'import dsf-pose'
  # the bl_idname member is used by blender to call this class.
  bl_idname = 'pose.dsf'
  # the filepath seems to be hidden magic; the file-selector
  # menu places the chosen filename-string into it.
  # (changes sometimes; look for path/dirname/filepath)
  filepath = StringProperty\
      (name = 'file path', description = 'file path for importing dsf-file.',
       maxlen = 1000, default = '')
  filter_glob = StringProperty (default = '*.d[su]f')

  def execute (self, context):
    """display the gui and load a file. This function should be
       called after the menu entry for the file is selected."""
    # call the main import function. This function should work
    # independent of this context-manager/operator logic.
    import_dsf_pose_file (self.properties.filepath, context)
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
  self.layout.operator (import_dsf_pose.bl_idname, text = 'dsf-pose (.d[su]f)')

def register ():
  """add an operator for importing dsf-files and
     registers a menu function for it."""
  bpy.utils.register_class (import_dsf_pose)
  bpy.types.INFO_MT_file_import.append (menu_func)

def unregister ():
  """remove the operator for importing dsf-files."""
  bpy.utils.unregister_class (import_dsf_pose)
  bpy.types.INFO_MT_file_import.remove (menu_func)

example_file = "/images/winshare-ds15/dsdata45/People/Genesis/Poses/M5 Studio Poses/M5 01.dsf"
