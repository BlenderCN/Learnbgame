import sys, os.path, logging
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import BoolProperty, StringProperty

from .dsf_geom_load import dsf_geom_load
from .dsf_geom_define import dsf_geom_define

log = logging.getLogger ('dsf_mesh_import')

bl_info = {
  'name': 'import dsf-geom',
  'description': 'import geometry from a dsf file.',
  'author': 'millighost',
  'version': (1, 0),
  'blender': (2,6,3),
  'category': 'Import-Export',
  'warning': '',
  'wiki_url': 'http://nonexistent',
}

def mesh_import (mod, use_mat = True, **kwarg):
  """mod is a mesh-model that is completely initialized.
     if use_mat is set, existing materials are re-used.
  """
  qmod = mesh_convert.create_quad_model (mod)
  msh_dsf = mesh_define.define_model (qmod, use_mat = use_mat, **kwarg)
  return msh_dsf

# create parser-flags from the dictionary props.
def get_parser_flags (props):
  prop_map = {
    'materials': 'm',
    'groups': 'g',
    'uvs': 'vt',
  }
  pflags = list ()
  for prop in props:
    if prop in prop_map:
      pflags.append (prop_map[prop])
  return pflags

def import_dsf_file (filename, props):
  """load the dsf-file and create a mesh. Props is a list containing
     flags to be set. returns the created object.
     groups: define vertex groups.
     materials: assign material indexes.
     use_mat: use existing materials with same name.
  """
  parser_flags = get_parser_flags (props)
  # parse the dsf-file.
  geom = dsf_geom_load.load_file (filename)
  # insert the quad-model into blender.
  log.info ("import_dsf_file (props = %s)" % (str (props)))
  obj = dsf_geom_define.define_model\
        (geom, use_mat = 'use_mat' in props, define_groups = props['groups'])
  obj['dsf-path'] = filename
  return obj

# the rest defines the gui and the blender operator
class import_dsf (bpy.types.Operator):
  # the doc text is displayed in the tooltip of the menu entry.
  """Load a daz studio 4 dsf file."""
  # the bl_label is displayed in the operator-menu (with space-KEY).
  bl_label = 'import dsf-geom'
  # the bl_idname member is used by blender to call this class.
  bl_idname = 'mesh.dsf'
  # the filepath seems to be hidden magic; the file-selector
  # menu places the chosen filename-string into it.
  # (changes sometimes; look for path/dirname/filepath)
  filepath = StringProperty\
      (name = 'file path', description = 'file path for importing dsf-file.',
       maxlen = 1000, default = '')
  filter_glob = StringProperty (default = '*.dsf')
  # the following properties are given to the import_dsf_file function
  # as keyword-arguments.
  prop_materials = BoolProperty\
      (name = 'materials',
       description = 'assign material names to faces',
       default = True)
  prop_use_material = BoolProperty\
      (name = 'use material',
       description = 'use existing materials if available',
       default = True)
  prop_groups = BoolProperty\
      (name = 'groups',
       description = 'assign vertex groups based on face groups',
       default = True)

  def execute (self, context):
    """display the gui and load a file. This function should be
       called after the menu entry for the file is selected."""
    import_props = {
      'materials': self.properties.prop_materials,
      'use_material': self.properties.prop_use_material,
      'groups': self.properties.prop_groups,
      'uvs': True,
    }
    log.info ("execute (path = {0}, kwargs = {1})".format\
                (self.properties.filepath, str (import_props)))
    # call the main import function. This function should work
    # independent of this context-manager/operator logic.
    obj = import_dsf_file (self.properties.filepath, import_props)
    context.scene.objects.active = obj
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
  self.layout.operator (import_dsf.bl_idname, text = 'dsf-geom (.dsf)')

def register ():
  """add an operator for importing dsf-files and
     registers a menu function for it."""
  bpy.utils.register_class (import_dsf)
  bpy.types.INFO_MT_file_import.append (menu_func)

def unregister ():
  """remove the operator for importing dsf-files."""
  bpy.utils.unregister_class (import_dsf)
  bpy.types.INFO_MT_file_import.remove (menu_func)
