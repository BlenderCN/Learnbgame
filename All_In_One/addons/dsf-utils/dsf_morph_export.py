import logging, json

import bpy
from bpy.props import StringProperty

from .dsf_skey_fetch import dsf_skey_fetch
from .dsf_morph_create import dsf_morph_create

log = logging.getLogger ('export-morph-dsf')

bl_info = {
  'name': 'export dsf morph',
  'description': 'export dsf morph file',
  'author': 'millighost',
  'version': (1, 0),
  'blender': (2,6,3),
  "category": "Learnbgame",
  'warning': '',
  'wiki_url': 'http://nonexistent',
}

def export_dsf_morph_file (filename, context = None):
  """main function for importing something. Called after the user
     has selected some filename.
  """
  # if the to be loaded file affects the currently selected object,
  # use this to get it:
  active_obj = context.active_object
  morph_data = dsf_skey_fetch.convert (active_obj)
  morph_file_data = dsf_morph_create.make_morph_file (shape_key = morph_data)
  ofh = open (filename, 'w', encoding = 'latin1')
  json.dump (morph_file_data, ofh, indent = 2)
  ofh.close ()

# the rest defines the gui and the blender operator
class export_dsf_morph (bpy.types.Operator):
  """Export a shape key as a dsf file."""
  # the doc text is displayed in the tooltip of the menu entry.
  # the bl_label is displayed in the operator-menu (with space-KEY).
  bl_label = 'export dsf-morph'
  # the bl_idname member is used by blender to call this class.
  bl_idname = 'export.dsfm'
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
    export_dsf_morph_file (filename, context = context);
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
  self.layout.operator (export_dsf_morph.bl_idname, text = 'dsf-morph (.dsf)')

def register ():
  bpy.utils.register_class (export_dsf_morph)
  bpy.types.INFO_MT_file_export.append (menu_func)

def unregister ():
  bpy.utils.unregister_class (export_dsf_morph)
  bpy.types.INFO_MT_file_export.remove (menu_func)
