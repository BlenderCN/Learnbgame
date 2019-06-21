
import bpy

import itertools
from collections import Counter
import os

from .edm.types import *
from .edm.mathtypes import Matrix, vector_to_edm, matrix_to_edm, Vector, MatrixScale, matrix_to_blender
from .edm.basewriter import BaseWriter
from .utils import matrix_string, vector_string, print_edm_graph

from .translation import TranslationGraph, TranslationNode

def get_all_actions(obj):
  """Retrieve all actions given a blender object. Includes NLA-actions"""
  if obj.animation_data:
    if obj.animation_data.action:
      yield obj.animation_data.action
    for track in obj.animation_data.nla_tracks:
      if len(track.strips) > 1:
        print("Warning: Multi-action tracks not supported")
      for strip in track.strips:
        yield strip.action

def is_null_transform(obj):
  """Checks if a blender object has no transform"""
  if obj.location.length > 1e-4:
    return False
  if obj.rotation_quaternion.angle > 2e-4:
    return False
  if (obj.scale - Vector((1,1,1))).length > 1e-4:
    return False
  return True


def convert_node(node):
  # Are we the root node?
  if node.parent is None:
    node.transform = Node()
    node.transform.parent = None
    return

  # If this can be turned into a renderable object, do so now
  if node.blender.type == "MESH" and node.blender.edm.is_renderable:
    node.render = RenderNodeWriter(node.blender)
  if node.blender.type == "MESH" and node.blender.edm.is_collision_shell:
    node.render = ShellNodeWriter(node.blender)
  if node.blender.type == "EMPTY" and node.blender.edm.is_connector:
    node.render = ConnectorWriter(node.blender)


  # Do we have animations? If so, we need to be turned into an animation node
  # Also: If we have children, then they need to be parented to the correct
  #       world position, so we need a transform
  #    ...UNLESS the object HAS no transform. In which case we don't need to offset
  if any(True for _ in get_all_actions(node.blender)) or (node.children and not is_null_transform(node.blender)):
    node.transform = build_animation_node(node.blender)
  else:
    pass

  # IF a connector, then we need a Transform as the parent transform, so if it
  # has already been given one then we need to insert a new child
  if isinstance(node.render, Connector):
    # Create a transform object for this connector
    connTransform = TransformNode()
    # If we have a transform, then we need to insert an extra level of indirection
    if node.transform:
      newParent = node.insert_parent()
      newParent.transform = node.transform
      # The transform should be encoded into the animation, so have an empty transform matrix
      connTransform.matrix = Matrix()      
    else:
      # No animation, transform entirely encoded in the TransformNode
      connTransform.matrix = matrix_to_edm(node.blender.matrix_local)
    node.transform = connTransform
    
  # Decide whether to apply object transform or switch axis on writing, now
  if node.render:
    if isinstance(node.transform, ArgAnimationNode) or node.children:
      node.render.apply_transform = False
    else:
      node.render.apply_transform = True

    if isinstance(node.transform, ArgAnimationNode):
      node.render.convert_axis = False
    else:
      node.render.convert_axis = True
    
  # Handle LOD nodes and children
  if node.blender.type == "EMPTY" and node.blender.edm.is_lod_root:
    # If we already have a transform, then we need to add a new
    # parent to hold it so we can create the LOD control node
    if node.transform:
      parent = node.insert_parent()
      parent.transform = node.transform

    node.transform = LodNode()
    # Now wait until after child processing
    yield
    # Insert a new 'Node' between every child, and collect the LOD data
    levels = []
    for child in list(node.children):
      newNode = child.insert_parent()
      newNode.transform = Node()
      lodMax = 1e30 if child.blender.edm.nouse_lod_distance else child.blender.edm.lod_max_distance
      levels.append((child.blender.edm.lod_min_distance, lodMax))
    node.transform.level = levels

def write_file(filename, options={}):

  # Get a set of all objects to be exported as renderables
  allExport = _get_all_objects_to_export()  
  print("Writing {} objects".format(len(allExport)))

  # Build a graph from ALL blender objects we want ported across
  graph = TranslationGraph.from_blender_objects(allExport)
  print("Blender graph we are exporting:")
  graph.print_tree()

  graph.walk_tree(convert_node, include_root=True)


  # Generate the materials for every renderable
  edmMaterials = {}
  materials = []
  def _create_materials(node):
    if not node.render or not hasattr(node.render, "material") or not node.render.material:
      return
    blendMaterial = node.render.material
    if blendMaterial in edmMaterials:
      edmMaterial = edmMaterials[blendMaterial]
    else:
      edmMaterial = create_material(blendMaterial)
      edmMaterial.index = len(materials)
      materials.append(edmMaterial)
      edmMaterials[blendMaterial] = edmMaterial
    node.render.material = edmMaterial
  graph.walk_tree(_create_materials)
  del edmMaterials


  print("After converting nodes")
  graph.print_tree()
  
  # Now set all the transform parents, both for blender objects AND transforms
  # RenderNodes get connected to their associated transform
  # Transform nodes get connected to the parent transform node
  def _connect_parents(node):
    # Set the render node's parent - at most one level away
    if node.render and node.transform:
      node.render.parent = node.transform
    elif node.render and node.parent.transform:
      node.render.parent = node.parent.transform
    if node.transform and node.parent:
      # Should never have a transform parented to anything else
      assert node.parent.transform
      node.transform.parent = node.parent.transform

  graph.walk_tree(_connect_parents)


  # Calculate materials for every RenderNode
  # materials = {}
  # def _calculate_materials(node):
  #   if not isinstance(node.render, RenderNode):
  #     continue
  #   material
  # graph.walk_tree(_calculate_materials)

  # # Now dump a load of information on our calculated base transforms
  # def _inspect_animarg(node, prefix):
  #   if not node.transform or not isinstance(node.transform, ArgAnimationNode):
  #     return
  #   node.transform.print_summary(prefix)    
  # print("Animation base transforms:")
  # graph.print_tree(_inspect_animarg)

  # Now do enmeshing
  def _enmesh(node):
    if node.render and hasattr(node.render, "calculate_mesh"):
      node.render.calculate_mesh(options)
  graph.walk_tree(_enmesh)

  # Build the linear list of transformation nodes and render nodes
  allNodes = {x: [] for x in NodeCategory}
  def _flatten_graph(node):
    # Tie the edm-only objects toether into a graph to let us iterate it
    if node.render and not hasattr(node.render, "children"):
      node.render.children = []
    if node.transform and not hasattr(node.transform, "children"):
      node.transform.children = []

    if node.render:
      allNodes[node.render.category].append(node.render)
      node.render.parent.children.append(node.render)
    if node.transform:
      if not node.transform in allNodes[NodeCategory.transform]:
        allNodes[NodeCategory.transform].append(node.transform)
      if node.transform.parent:
        node.transform.parent.children.append(node.transform)
  graph.walk_tree(_flatten_graph, include_root=True)

  # We should now have an entirely separate tree ready for writing
  print("Final EDM Graph for writing:")
  print_edm_graph(allNodes[NodeCategory.transform][0])


  # Let's build the root node
  root = RootNodeWriter()
  root.set_bounding_box_from(allExport)
  root.materials = materials
  
  # And finally the wrapper
  file = EDMFile()
  file.root = root
  file.nodes = allNodes[NodeCategory.transform]
  file.renderNodes = allNodes[NodeCategory.render]
  file.connectors = allNodes[NodeCategory.connector]
  file.shellNodes = allNodes[NodeCategory.shell]
  file.lightNodes = allNodes[NodeCategory.light]
  
  writer = BaseWriter(filename)
  file.write(writer)
  writer.close()

def _get_all_objects_to_export():
  """Get all blender objects that will be exported as edm objects"""
  all_export = set()
  for obj in bpy.context.scene.objects:
    if obj.type == "MESH" and (obj.edm.is_renderable or obj.edm.is_collision_shell):
      all_export.add(obj)
    elif obj.type == "EMPTY" and obj.edm.is_connector:
      all_export.add(obj)
  return all_export

def _create_material_map(blender_objects):
  """Creates an list, and indexed material map from a list of blender objects.
  The map will connect material names to the edm-Material instance.
  In addition, each Material instance will know it's own .index"""
  
  all_Materials = [obj.material_slots[0].material for obj in blender_objects]
  materialMap = {m.name: create_material(m) for m in all_Materials}
  materials = []
  for i, bMat in enumerate(all_Materials):
    mat = materialMap[bMat.name]
    mat.index = i
    materials.append(mat)
  return materials, materialMap


def _build_transform(node):
  """Given a translation node, creates the parent transform nodes for that 
  blender object. If more than one parent transform, takes care of stitching
  them into the end graph."""

  # Skip any nodes that are not JUST blender objects
  if not node.type == "BLEND":
    return
  transforms = build_parent_nodes(node.blender)
  if transforms:
    node.transform = transforms[-1]
    for parent in transforms[:-1]:
      parentNode = node.insert_parent()
      parentNode.transform = parent


def build_animation_node(obj):
  """Inspects an object's actions to build a parent transform node."""

  actions = set(get_all_actions(obj))
  assert len(actions) <= 1, "Do not support multiple actions on object export at this time"

  # If no animation data, return an animation node without keys
  if not actions:
    return create_animation_base(obj)

  # Verify each action handles a separate argument, otherwise merges need to happen
  arguments = Counter(action.argument for action in actions)
  if any(x > 1 for x in arguments.values()):
    raise RuntimeError("More than one action on an object share arguments. Not sure how to deal with this")

  action = next(iter(actions))

  # Check that all the keyframe data is known
  ALL_KNOWN = {"location", "rotation_quaternion"} # "scale", "hide_render"
  data_categories = set(x.data_path for x in action.fcurves)
  if not data_categories <= ALL_KNOWN:
    print("WARNING: Action has animated keys ({}) that ioEDM can not translate yet!".format(data_categories-ALL_KNOWN))
  
  # do we need to make an ArgAnimationNode?
  if data_categories & {"location", "rotation_quaternion", "scale"}:
    return create_arganimation_node(obj, [action])

def create_animation_base(object):
  node = ArgAnimationNodeBuilder(name=object.name)

  # Build the base transforms.
  node.base.matrix = matrix_to_edm(object.matrix_parent_inverse)
  
  sM = MatrixScale(object.scale)
  rM = object.rotation_quaternion.to_matrix().to_4x4()
  tM = Matrix.Translation(object.location)
  # Verify this
  buildVec = object.matrix_parent_inverse * tM * rM * sM * Vector((1,1,1,1))
  localVec = object.matrix_local * Vector((1,1,1,1))
  delta = localVec - buildVec
  # print("Delta vector = {}".format(delta.length))
  if delta.length > 0.01:
    print("Incorrect local matrix calculation")
    import pdb
    pdb.set_trace()

  pos, rot, sca = object.matrix_basis.decompose()
  node.base.position = pos #object.location
  node.base.scale = sca #object.scale
  node.base.quat_1 = rot #object.rotation_quaternion

  # This swaps edm-space to blender space - rotate -ve around x 90 degrees
  RX = Quaternion((0.707, -0.707, 0, 0))
  RXm = RX.to_matrix().to_4x4()

  # ON THE OTHER SIDE
  # vector_to_blender - z = y, y = -z - positive rotation around X == RPX
  # actual data transformed is RPX * file
  # Base transform is reasonably standard;
  #
  #          ________________Direct values from node
  #         |     |      |
  # mat * aabT * q1m * aabS * [RX * RPX] * file
  # mat *   T  *  R  *  S         *        file
  # 
  # e.g. all transforms are applied in file-space

  # Calculate what we think that the importing script should see
  # zero_transform = matrix_to_blender(node.base.matrix) \
  #       * Matrix.Translation(node.base.position) \
  #       * node.base.quat_1.to_matrix().to_4x4() \
  #       * MatrixScale(node.base.scale) \
  #       * RXm
  # print("   Expected zeroth")
  # print("     Location: {}\n     Rotation: {}\n     Scale: {}".format(*zero_transform.decompose()))
  # This appears to match the no-rot case. What doesn't match is when rotations are applied

  return node

def create_arganimation_node(object, actions):
  # For now, let's assume single-action
  node = create_animation_base(object)

  # Secondary variables for calculation
  #  
  # This swaps blender space to EDM-space - rotate +ve around x 90 degrees
  RPX = Quaternion((0.707, 0.707, 0, 0))
  # This swaps edm-space to blender space - rotate -ve around x 90 degrees
  RX = Quaternion((0.707, -0.707, 0, 0))
  RXm = RX.to_matrix().to_4x4()
  inverse_base_rotation = node.base.quat_1.inverted()
  matQuat = matrix_to_blender(node.base.matrix).decompose()[1]
  invMatQuat = matQuat.inverted()

  assert len(actions) == 1
  for action in actions:
    curves = set(x.data_path for x in action.fcurves)
    rotCurves = [x for x in action.fcurves if x.data_path == "rotation_quaternion"]
    posCurves = [x for x in action.fcurves if x.data_path == "location"]
    argument = action.argument

    # What we should scale to - take the maximum keyframe value as '1.0'
    scale = 1.0 / (max(abs(x) for x in get_all_keyframe_times(posCurves + rotCurves)) or 100.0)
    
    if "location" in curves:
      # Build up a set of keys
      posKeys = []
      # Build up the key data for everything
      for time in get_all_keyframe_times(posCurves):
        position = get_fcurve_position(posCurves, time, node.base.position) - node.base.position
        key = PositionKey(frame=time*scale, value=position)
        posKeys.append(key)
      node.posData.append((argument, posKeys))
    if "rotation_quaternion" in curves:
      rotKeys = []
      for time in get_all_keyframe_times(rotCurves):
        actual = get_fcurve_quaternion(rotCurves, time)
        rotation = inverse_base_rotation * invMatQuat * actual
        key = RotationKey(frame=time*scale, value=rotation)
        rotKeys.append(key)

# leftRotation = matQuat * q1
#     rightRotation = RX
        # Extra RX because the vertex data on reading has had an extra
        # RPX rotation applied
        # predict = matQuat * node.base.quat_1 * rotation * RPX 
        # print("   Quat at time {:6}: {}".format(time, predict))
        # print("                Desired {}".format(actual))
      node.rotData.append((argument, rotKeys))
    if "scale" in curves:
      raise NotImplementedError("Curves not totally understood yet")

  # Now we've processed everything
  return node


def get_all_keyframe_times(fcurves):
  """Get all fixed-point times in a collection of keyframes"""
  times = set()
  for curve in fcurves:
    for keyframe in curve.keyframe_points:
      times.add(keyframe.co[0])
  return sorted(times)

def get_fcurve_quaternion(fcurves, frame):
  """Retrieve an evaluated quaternion for a single action at a single frame"""
  # Get each channel for the quaternion
  all_quat = [x for x in fcurves if x.data_path == "rotation_quaternion"]
  # Really, quaternion rotation without all channels is stupid
  assert len(all_quat) == 4, "Incomplete quaternion rotation channels in action"
  channels = [[x for x in all_quat if x.array_index == index][0] for index in range(4)]
  return Quaternion([channels[i].evaluate(frame) for i in range(4)])

def get_fcurve_position(fcurves, frame, basis=None):
  """Retrieve an evaluated fcurve for position"""
  all_quat = [x for x in fcurves if x.data_path == "location"]
  channelL = [[x for x in all_quat if x.array_index == index] for index in range(3)]
  # Get an array of lookups to get the channel value, or zero
  channels = []
  for index in range(3):
    if channelL[index]:
      channels.append(channelL[index][0].evaluate(frame))
    elif basis:
      channels.append(basis[index])
    else:
      channels.append(0)
  return Vector(channels)

def calculate_edm_world_bounds(objects):
  """Calculates, in EDM-space, the bounding box of all objects"""
  mins = [1e38, 1e38, 1e38]
  maxs = [-1e38, -1e38, -1e38]
  for obj in objects:
    points = [vector_to_edm(obj.matrix_world * Vector(x)) for x in obj.bound_box]
    for index in range(3):
      mins[index] = min([point[index] for point in points] + [mins[index]])
      maxs[index] = max([point[index] for point in points] + [maxs[index]])
  return Vector(mins), Vector(maxs)

def create_texture(source):
  # Get the texture name stripped of ALL extensions
  texName = os.path.basename(source.texture.image.filepath)
  texName = texName[:texName.find(".")]
  
  # Work out the channel for this texture
  if source.use_map_color_diffuse:
    index = 0
  elif source.use_map_normal:
    index = 1
  elif source.use_map_specular:
    index = 2

  # For now, assume identity transformation until we understand
  matrix = Matrix()
  return Texture(index=index, name=texName, matrix=matrix)

def create_material(source):
  mat = Material()
  mat.blending = int(source.edm_blending)
  mat.material_name = source.edm_material
  mat.name = source.name

  # Convert material 'hardness' to a specular power-like value
  specPower = (float(source.specular_hardness) - 1.0) / 100.0
  mat.uniforms = PropertiesSet({
    "specPower": specPower,
    "specFactor": source.specular_intensity,
    "diffuseValue": source.diffuse_intensity,
    "reflectionValue": 0.0, # Always in uniforms, so keep here for compatibility
  })
  # No ide what this corresponds to yet:
  # "diffuseShift": Vector((0,0)),
  if source.raytrace_mirror.use:
    mat.uniforms["reflectionValue"] = source.raytrace_mirror.reflect_factor
    mat.uniforms["reflectionBlurring"] = 1.0-source.raytrace_mirror.gloss_factor
  mat.shadows.recieve = source.use_shadows
  mat.shadows.cast = source.use_cast_shadows
  mat.shadows.cast_only = source.use_cast_shadows_only

  mat.vertex_format = VertexFormat({
    "position": 4,
    "normal": 3,
    "tex0": 2
    })
  
  mat.texture_coordinates_channels = [0] + [-1]*11
  # Find the textures for each of the layers
  # Find diffuse - this will sometimes also include a translucency map
  try:
    diffuseTex = [x for x in source.texture_slots if x is not None and x.use_map_color_diffuse]
  except:
    print("ERROR: Can not find diffuse texture")
  # normalTex = [x for x in source.texture_slots if x.use_map_normal]
  # specularTex = [x for x in source.texture_slots if x.use_map_specular]

  assert len(diffuseTex) == 1
  mat.textures.append(create_texture(diffuseTex[0]))

  return mat

def create_mesh_data(source, material=None, vertex_format=None, options={}):
  """Takes an object and converts it to a mesh suitable for writing"""
  # Always remesh, because we will want to apply transformations
  mesh = source.to_mesh(bpy.context.scene,
    apply_modifiers=options.get("apply_modifiers", False),
    settings="RENDER", calc_tessface=True)

  # Use the material's vertex format if not otherwise specified
  if vertex_format is None and material:
    vertex_format = material.vertex_format

  print("Enmeshing ", source.name)
  # Apply the local transform. IF there are no parents, then this should
  # be identical to the world transform anyway
  if options.get("apply_transform", True):
    mesh.transform(source.matrix_local)
    print("  Applying local transform")
  else:
    print("  Skipping transform application")

  # if vertex_format:

  # if material:
  #   vfPosition = 3
  #   vfNormal = True
  #   vfTexture = True
  # else:
  #   vfNormal = False
  #   vfTexture = False

  if vertex_format.ntexture:
    # Should be more complicated for multiple layers, but will do for now
    uv_tex = mesh.tessface_uv_textures.active.data

  if options.get("convert_axis", True):
    print("  Converting axis")
  else:
    print("  NOT Converting axis")

  newVertices = []
  newIndexValues = []
  # Loop over every face, and the UV data for that face
  for faceIndex, face in enumerate(mesh.tessfaces):
    # What are the new index values going to be?
    newFaceIndex = [len(newVertices)+x for x in range(len(face.vertices))]
    if vertex_format.ntexture:
      uvFace = uv_tex[faceIndex]

    # Build the new vertex data
    for i, vtxIndex in enumerate(face.vertices):
      vtxParts = []
      if options.get("convert_axis", True):
        position = vector_to_edm(mesh.vertices[vtxIndex].co)
        normal = vector_to_edm(mesh.vertices[vtxIndex].normal)
      else:
        position = mesh.vertices[vtxIndex].co
        normal = mesh.vertices[vtxIndex].normal
      if vertex_format.nposition == 3:
        vtxParts.append(list(position))
      else:
        vtxParts.append(list(position)+[0.0])
      if vertex_format.nnormal:
        vtxParts.append(normal)
      if vertex_format.ntexture:
        uv = [uvFace.uv[i][0], 1-uvFace.uv[i][1]]
        vtxParts.append(uv)

      newVertices.append(tuple(itertools.chain(*vtxParts)))

    # We either have triangles or quads. Split into triangles, based on the
    # vertex index subindex in face.vertices
    if len(face.vertices) == 3:
      triangles =  ((0, 1, 2),)
    else:
      triangles = ((0, 1, 2),(2, 3, 0))

    # Write each vertex of each triangle
    for tri in triangles:
      for i in tri:
        newIndexValues.append(newFaceIndex[i])

  # Cleanup
  bpy.data.meshes.remove(mesh)

  return newVertices, newIndexValues

class RenderNodeWriter(RenderNode):
  def __init__(self, obj):
    super(RenderNodeWriter, self).__init__(name=obj.name)
    self.source = obj
    self.parent = None
    self.material = obj.material_slots[0].material if obj.material_slots else None

  def calculate_mesh(self, options):
    assert self.material
    assert self.source
    opt = dict(options)
    opt["apply_transform"] = self.apply_transform
    opt["convert_axis"] = self.convert_axis
    self.vertexData, self.indexData = create_mesh_data(self.source, material=self.material, options=opt)

class ShellNodeWriter(ShellNode):
  def __init__(self, obj):
    super(ShellNodeWriter, self).__init__(name=obj.name)
    self.source = obj
    self.parent = None

  def calculate_mesh(self, options):
    assert self.source
    opt = dict(options)
    opt["apply_transform"] = self.apply_transform
    opt["convert_axis"] = self.convert_axis
    self.vertex_format = VertexFormat({"position":3})
    self.vertexData, self.indexData = create_mesh_data(self.source, vertex_format=self.vertex_format, options=opt)

class RootNodeWriter(RootNode):
  def __init__(self, *args, **kwargs):
    super(RootNodeWriter, self).__init__(*args, **kwargs)

  def set_bounding_box_from(self, objectList):
    bboxmin, bboxmax = calculate_edm_world_bounds(objectList)
    self.boundingBoxMin = bboxmin
    self.boundingBoxMax = bboxmax

class ConnectorWriter(Connector):
  def __init__(self, blender):
    super(ConnectorWriter, self).__init__()
    self.source = blender
    self.name = blender.name

class ArgAnimationNodeBuilder(ArgAnimationNode):
  def __init__(self, *args, **kwargs):
    super(ArgAnimationNodeBuilder, self).__init__(*args, **kwargs)

  def apply_transform(self, matrix):
    """Apply an extra transformation to the local space of this 
    transform node. This is because of parenting issues"""
    raise NotImplementedError()

  def print_summary(self, prefix=""):
    print(prefix + "Base (pre-animation) data:")
    print(prefix + "Position:", vector_string(self.base.position))
    print(prefix + "Rotation:", vector_string(self.base.quat_1))
    print(prefix + "Scale:   ", vector_string(self.base.scale))
    print(matrix_string(self.base.matrix, prefix=prefix, title="Matrix:  "))

    # Calculate what the decomposed values will be
    RX = Quaternion((0.707, -0.707, 0, 0))
    RXm = RX.to_matrix().to_4x4()
    zeroth =  matrix_to_blender(self.base.matrix) * \
              Matrix.Translation(self.base.position) * \
              self.base.quat_1.to_matrix().to_4x4() * \
              MatrixScale(self.base.scale) * RXm
    zPos, zRot, zSca = zeroth.decompose()
    print(prefix + "Expected Zeroth Pos:", vector_string(zPos))
    print(prefix + "                Rot:", vector_string(zRot))
    print(prefix + "              Scale:", vector_string(zSca))
    
    if self.rotData:
      print(prefix + "  Rotation Anim Data:")
      for key in self.rotData[0][1]:
        print(prefix + "    {:-6.3f}: {}".format(key.frame, key.value))
