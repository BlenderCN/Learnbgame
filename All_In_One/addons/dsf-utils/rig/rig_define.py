import math, logging
import mathutils
import bpy

log = logging.getLogger ('rig-def')

def create_blender_armature (name, ctx):
  """create an empty armature data and object, put the armature
     into edit-mode and return the data object. The armature
     object will be the active object.
  """
  scene = ctx.scene
  armdat = bpy.data.armatures.new (name = name)
  armobj = bpy.data.objects.new (name = name, object_data = armdat)
  scene.objects.link (armobj)
  scene.objects.active = armobj
  armdat.show_axes = True
  return armobj

def transform_bone (orient, origin, bbone):
  """place and orient the blender bone bbone.
  """
  xyz_angles = [math.radians (angle) for angle in orient]
  orient_tf = mathutils.Euler (xyz_angles, 'XYZ').to_matrix ().to_4x4 ()
  bbone.transform (orient_tf)
  # somehow translating the bone with a combined matrix does not
  # work; the bone will always rotate a bit. So use the translate()-method.
  bbone.translate (mathutils.Vector (origin))

class bbone_map (dict):
  """stores mapping from a blender bone to an armature bone.
     attributes per mapping include:
     bone - a link to the armature bone
     roots - names of the blender bone that is to be used as a child for other
       blender bones connecting to the armature bone.
     leaf - name of the blender bone that is to be used as a parent for other
       blender bones connecting to the armature bone.
     axes - list of bone axis names that this bone represents.
  """
  def __init__ (self, *arg, **kwarg):
    """initialize an empty bone map.
    """
    super (bbone_map, self).__init__ (*arg, **kwarg)
  def get_leaf (self, id):
    """get the blender bone that represents the tail of the bones
       that were created for the bone with the id.
    """
    for b_info in self.values ():
      if b_info.bone.get ('id') == id:
        return b_info.leaf
    return None

class bone_info (object):
  """store data on a created bone or bones.
     this is for the case when a single input bone would result in multiple
     blender bones to be created.
  """
  def __init__ (self, bone = None, bname = None):
    """create a new entry for the given blender bone name bname.
       bone is the armature bone that lead to creation of this entry.
       bname is the name of the blender bone (which is also used as a key).
    """
    assert (bone)
    assert (bname)
    self.bone = bone
    self.bname = bname
    self.roots = []
    self.leaf = None
    self.axes = []

def insert_bone (si_bone, armdat):
  """insert the bone object into the armature data armdat and returns
     a bone_info object created for this bone.
     created bones are name 'def-<bodypart>.<axes>'
     si_bone must provide these attributes:
     orientation, origin - basic position data of the bone used to create
       the transformation of the bone in armature-space.
  """
  bname = "def-%s.xyz" % (si_bone.get ('id'))
  b_info = bone_info (bone = si_bone, bname = bname)
  b_bone = armdat.edit_bones.new (name = bname)
  orient = si_bone.get ('orientation')
  origin = si_bone.get ('origin')
  # create an initial orientation by setting the tail of
  # the bone to 0,1,0. This leaves the bone pointing in the y-orientation,
  # so the local space is the same as the global space.
  b_bone.head = (0, 0, 0)
  b_bone.tail = (0, si_bone.get ('length'), 0)
  transform_bone (orient, origin, b_bone)
  b_info.roots.append (bname)
  b_info.leaf = bname
  return [b_info]
  
def insert_bones (si_arm, armdat):
  """traverse the bones of the armature in preorder (parent before
     children) and insert them into the armature data.
     Returns a mapping of the names of the inserted bones to their definition.
  """
  bone_mapping = bbone_map ()
  # the parent queue holds bone_info-objects whose children still 
  # need to get created.
  parent_queue = [None]
  while len (parent_queue) > 0:
    parent = parent_queue.pop ()
    log.info ("inserting children of %s", parent)
    if parent is not None:
      # the parent is a b-info object and the b-infos end-attribute contains
      # the blender-bone to which children need to get linked to.
      children = list (si_arm.get_children (parent.get ('id')))
      parent_bname = bone_mapping.get_leaf (parent.get ('id'))
      parent_bbone = armdat.edit_bones[parent_bname]
    else:
      children = list (si_arm.get_children (None))
      parent_bbone = None
    for child in children:
      # create the bbones representing the child. This returns a list
      # of b-info records.
      b_infos = insert_bone (child, armdat)
      # link all blender bones to the parent
      for b_info in b_infos:
        # a blender bone might have multiple roots. assign the parent
        # to each of them.
        for bname in b_info.roots:
          bbone_start = armdat.edit_bones[bname]
          bbone_start.parent = parent_bbone
        bone_mapping[b_info.bname] = b_info
      parent_queue.append (child)
  return bone_mapping

# poser/daz bones are always based on euler rotations and might contain
# scale components. They might also contain translations, but those seem
# to be not fully complete bones, but are folded somehow into the
# standard bones (ie they have no weightmap).

def configure_bones (armdat, bone_mapping, armobj):
  """perform final fixups on the created bones.
  """
  pose_bones = armobj.pose.bones
  for (bname, b_info) in bone_mapping.items ():
    bbone = pose_bones[bname]
    si_bone = b_info.bone
    order = si_bone.get ('rotation_order')
    bbone.rotation_mode = order

def define_armature (si_arm, ctx):
  """create a blender-armature object from the given armature-data.
     blender-function.
     ctx is the context for defining the armature in.
     Returns the created armature object and a bone-mapping, the latter
     could be used to create a matching weight-paint.
  """
  armobj = create_blender_armature ('imported-arm', ctx)
  bpy.ops.object.mode_set (mode = 'EDIT')
  bone_map = insert_bones (si_arm, armobj.data)
  bpy.ops.object.mode_set (mode = 'OBJECT')
  configure_bones (si_arm, bone_map, armobj)
  return (armobj, bone_map)
