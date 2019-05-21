import sys, os.path, logging, json
import bpy

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

from . import dsf_armature
from .rig import rig_define

log = logging.getLogger ("dsf-arm-imp")

def load_node_lib (filepath):
  """load the dsf file, check that there is a node lib in it and return it.
  """
<<<<<<< HEAD
  from . import dsf_io
  jdata = dsf_io.read_json_data (filepath, encoding = 'latin1')
=======
  import dsf.dsf_io
  jdata = dsf.dsf_io.read_json_data (filepath, encoding = 'latin1')
>>>>>>> 64d1a8da577389e9f24c88afd6ababff31e37f34
  if 'node_library' in jdata:
    return jdata['node_library']
  else:
    raise KeyError ("data does not contain armature.")

class import_dsf_arm (bpy.types.Operator):
  """operator to import a dsf armature.
  """
  bl_label = 'import dsf-arm'
  bl_idname = 'armature.dsf'

  filepath = StringProperty\
      ('file path', description = 'file path for dsf armature.',\
         maxlen = 1000, default = '')
  filter_glob = StringProperty (default = '*.dsf')
  split_twist = BoolProperty\
      ('split twist', description = 'separate the inner (twist) axis.',
       default = True)
  split_main = BoolProperty\
      ('split main', description = 'separate the outer (main) axis.',
       default = False)
  scale = BoolProperty ('scale', description = 'import scaling bone.',
                        default = False)

  def define_arm (self, ctx, jdata):
    """define the armature from the loaded json data.
    """
    log.info ("define: %s", self.properties.filepath)
    arm = dsf_armature.armature (jdata)
    (armobj, bmap) = rig_define.define_armature (arm, ctx)
  def execute (self, ctx):
    """load the armature from a dsf and insert it into blender.
    """
    log.info ("loading: %s", self.properties.filepath)
    nlib = load_node_lib (self.properties.filepath)
    self.define_arm (ctx, nlib)
    return {'FINISHED'}
  def invoke (self, ctx, event):
    """called by the menu entry or the operator menu.
    """
    ctx.window_manager.fileselect_add (self)
    return {'RUNNING_MODAL'}

def menu_func (self, ctx):
  """render the menu entry.
  """
  self.layout.operator (import_dsf_arm.bl_idname, text = 'dsf-armature (.dsf)')

def register ():
  """add the operator to blender.
  """
  bpy.utils.register_class (import_dsf_arm)
  bpy.types.INFO_MT_file_import.append (menu_func)

def unregister ():
  """remove the operator from blender.
  """
  bpy.utils.unregister_class (import_dsf_arm)
  bpy.types.INFO_MT_file_import.remove (menu_func)
  
genesis = '/images/winshare/dsdata4/data/DAZ 3D/Genesis/Base/Genesis.dsf'
