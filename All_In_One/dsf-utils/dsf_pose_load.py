from . import dsf_io
import re, collections

# object reference after 
# (see dson_spec/format_description/asset_addressing/start):
# general syntax:
# [<scheme>:/]<node_path>:<file_path>#<asset_id>[?<property_path>]
# not really an uri, so urllib.parse not well applicable
# these kind of references seem to occur in the files:
#
# "E:/NewProjects/!GENESIS/!Bracers/valBracersDragon_Bump.jpg"
#  - bad case of a filepath containing a windows drive letter.
# "/Runtime/textures/RawArt/Raw_Bloodbeast/3_BBeast-Limbs_SSS.jpg"
#  - an absolute filename
# "name://@selection#materials:?extra/studio_material_channels/layer2/value"
#  - scheme = name
# "name://@selection/hip:?rotation/z/value"
#  - scheme = name
# "#default"
#  - reference within the same file
# "#Taiga:?value"
#  - reference to a value within the same file? 'Taiga' refers to an id
# "lHand#CTRLlRingBend:?value"
#  - reference to a value. This is used by pose files to reference values
#    in other figures. CtrllRingBend is an id, lHand a body part.
# "Trunk_Tip_0:/data/RawArt/EleBeast/Eletrunk.dsf#Trunk_Tip?scale/z"
#  - Trunk_Tip is an id of a node in the Eletrunk.dsf; 'Trunk_Tip_0' does
#    not seem to exist anywhere; the path also is wrong (path component missing)
# "rFoot:?scale/z"
#  - a standard transformation value (no id). This is similar
#    to "lHand#CTRLlRingBend:?value", but without the id.
# "?scale/z"
#  - a reference to a transformation value within the same file/node.
# : property path (after the ?) applies to the thing left of the qmark
# : rest is eg: <name>:<path>#<id>, #<id>:, #<id>, <name>:, <name>#<id>:
# - an <id> is after the '#'
# - a <name> is before the <id>
# - an optional path is somewhere between
# 

objref_re = re.compile\
  ('(?:(?P<scheme>\\w+):/)?'
   + '(?P<node_path>[^:?#]+):'
   + '(?P<file_path>[^?#]*)'
   + '(?:\\#(?P<asset_id>[^?]+))?'
   + '(?:\\?(?P<property_path>.*))?$')

objref_type = collections.namedtuple ('objref_type',\
   ['scheme', 'node_path', 'file_path', 'asset_id', 'property_path'])

def match_bone (bone, ref):
  """return true, iff the bone matches the given reference.
  """
  bname = bone.name
  (bname_base, _, bname_suff) = bname.partition ('.')
  return bname_base.endswith (ref)

def armature_find_bone (arm, ref):
  """find a bone of an armature object.
     returns None if no bone could be matched.
  """
  for pbone in arm.pose.bones:
    if match_bone (pbone, ref):
      return pbone
  return None

def bone_set_property (pbone, ref, value):
  """set a property of a pose bone to the given value.
  """
  pass

def search_object_reference (bobj, ref):
  """search for an blender object instance within blender object bobj.
     (for armatures this should result in a bone or property).
  """
  if bobj.type == 'ARMATURE':
    # usually we are searching for a bone here.
    return armature_find_bone (bobj, ref)
  else:
    pass

def parse_objref (ref):
  """parse an object reference into its components:
     scheme, node_path, file_path, asset_id, property_path
  """
  # first strip off the property_path; property_path is only a logical
  # construct which needs to be handled specially. The body_part refers
  # to some object instance (bone, skey, ...).
  (body_part_ref, _, property_path) = ref.partition ('?')
  mat = objref_re.match (ref)
  if mat is not None:
    parsed_ref = objref_type (**mat.groupdict ())
    return parsed_ref
  else:
    return None
  
def load_pose_file (filepath):
  """read the data from a pose file and return a pose object
     which can be applied to objects in blender.
  """
  jdata = dsf_io.read_json_data (filepath)
  try:
    anim_datas = jdata['scene']['animations']
  except KeyError as e:
    raise Exception ("data does not contain a pose.")
  for anim_data in anim_datas:
    parsed = parse_objref (anim_data['url'])
    print ("url:", anim_data['url'], "parsed:", parsed, anim_data['keys'])

"lHand#CTRLlFingersFist:?value"
