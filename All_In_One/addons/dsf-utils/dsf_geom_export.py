import logging, json

import bpy
from bpy.props import StringProperty

log = logging.getLogger ('dsf-geom-exp')

# the rest defines the gui and the blender operator
class export_dsf_geom (bpy.types.Operator):
  """Export a mesh as a dsf-geometry"""
  # the doc text is displayed in the tooltip of the menu entry.
  # the bl_label is displayed in the operator-menu (with space-KEY).
  bl_label = 'export dsf-geom'
  # the bl_idname member is used by blender to call this class.
  bl_idname = 'mesh.dsf_exp'
  # the filepath seems to be hidden magic; the file-selector
  # menu places the chosen filename-string into it.
  # (changes sometimes; look for path/dirname/filepath)
  filepath = StringProperty\
      (name = 'file path', description = 'file path for exporting dsf-file.',
       maxlen = 1000, default = '')
  filter_glob = StringProperty (default = '*.*')

  def execute (self, context):
    """display the gui and load a file. This function should be
       called after the menu entry for the file is selected."""
    # call the main import function. This function should work
    # independent of this context-manager/operator logic.
    filename = self.properties.filepath
    log.info ("user selected %s", filename)
    self.export_file (filename, context = context)
    return { 'FINISHED' }

  def invoke (self, context, event):
    """The invoke function should be called when the menu-entry for
       this operator is selected. It displays a file-selector and
       waits for execute() to be called."""
    context.window_manager.fileselect_add (self)
    return {'RUNNING_MODAL'}

  def export_file (self, filename, context = None):
    """write the currently selected mesh to the given filename.
    """
    pass

def menu_func (self, context):
  """display the menu entry for calling the importer."""
  # the first parameter is the operator to call (by its bl_idname),
  # the text parameter is displayed in the menu.
  self.layout.operator (export_dsf_morph.bl_idname, text = 'dsf-geom (.dsf)')

def register ():
  bpy.utils.register_class (export_dsf_geom)
  bpy.types.INFO_MT_file_export.append (menu_func)

def unregister ():
  bpy.utils.unregister_class (export_dsf_geom)
  bpy.types.INFO_MT_file_export.remove (menu_func)
