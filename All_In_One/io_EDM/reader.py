"""
reader

Contains the central EDM->Blender conversion code
"""

import bpy
import bmesh

from .utils import chdir, print_edm_graph
from .edm import EDMFile
from .edm.mathtypes import *
from .edm.types import *

from .translation import TranslationGraph, TranslationNode

import re
import glob
import fnmatch
import os
import itertools

FRAME_SCALE = 100

def iterate_renderNodes(edmFile):
  """Iterates all renderNodes in an edmFile - whilst ignoring any nesting
  due to e.g. renderNode splitting"""
  for node in edmFile.renderNodes:
    if hasattr(node, "children") and node.children:
      for child in node.children:
        yield child
    else:
      yield node

def iterate_all_objects(edmFile):
  for node in itertools.chain(iterate_renderNodes(edmFile), edmFile.connectors, edmFile.shellNodes, edmFile.lightNodes):
    yield node

def build_graph(edmFile):
  "Build a translation graph object from an EDM file"
  graph = TranslationGraph()
  # The first node is ALWAYS the root ndoe
  graph.root.transform = edmFile.nodes[0]
  nodeLookup = {edmFile.nodes[0]: graph.root}

  # Add an entry for every other transform node
  for tfnode in edmFile.nodes[1:]:
    newNode = TranslationNode()
    newNode.transform = tfnode
    nodeLookup[tfnode] = newNode
    graph.nodes.append(newNode)

  # Make the parent/child links
  for node in graph.nodes:
    if node.transform.parent:
      node.parent = nodeLookup[node.transform.parent]
      node.parent.children.append(node)

  # Verify we only have one root
  assert len([x for x in graph.nodes if not x.parent]) == 1, "More than one root node after reading EDM"

  # Connect every renderNode to it's place in the chain
  for node in iterate_all_objects(edmFile):
    if not hasattr(node, "parent"):
      print("Warning: Node {} has no parent attribute; skipping".format(node))
      continue
    owner = nodeLookup[node.parent]
    newNode = TranslationNode()
    newNode.render = node
    graph.attach_node(newNode, owner)

  # Postprocessing: Any transform node with only one child, and that child
  # is a renderNode ONLY, absorbs the rendernode
  def _absorb_rendernode_child(node):
    # Check for an uncomplicated single child that isn't a parent and is a 
    # rendernode, where this node is ONLY a transformnode, and has no other data
    # - some of these might be automatic, but we might have done other tree
    # work between construction and now, so better to be safe

    if not node.type == "TRANSFORM":
      return

    # Addition: Only count Render children in child count
    renderChildren = [x for x in node.children if x.type == "RENDER"]
    # If we have multiple children, allow a merge IF we have a name AND a child
    # has the same name
    if len(renderChildren) != 1:
      nameMatch = [x for x in renderChildren if x.render.name == node.transform.name]
      if node.transform.name and len(nameMatch) == 1:
        child = nameMatch[0]
      else:
        return
    else:
      child = renderChildren[0]
    if not child.type == "RENDER" or child.children:
      return
    node.render = child.render
    # Rename the child render node if the parent has one; it may have lost it
    # if it was merged with others
    if node.transform.name:
      node.render.name = node.transform.name
    graph.remove_node(child)

  graph.walk_tree(_absorb_rendernode_child)

  return graph


def process_node(node):
  """Processes a single node of the transform graph"""
  # Root node has no processing
  if node.parent is None:
    return

  # Potentially two parts to transformation;
  #   - building the blender world object
  #   - building the transform node
  #   - Applying the transform node to the world object
  # Without a transform node, we can just safely parent onto the next blender
  # world object up the chain.

  # First, create the blender object to apply the animations/transform to
  if node.render:
    if isinstance(node.render, Connector):
      node.blender = create_connector(node.render)
    elif isinstance(node.render, (RenderNode, ShellNode)):
      node.blender = create_object(node.render)
    elif isinstance(node.render, (LightNode)):
      node.blender = create_lamp(node.render)
    else:
      print("Warning: No case yet for object node {}".format(node.render))
  else:
    # In cases where we have a transformation node, but no directly associated
    # render object, we are probably at the root of a tree of other items.
    # Create an empty object to act as the parent of this sub-tree
    ob = bpy.data.objects.new(type(node.transform).__name__, None)
    ob.empty_draw_size = 0.1
    bpy.context.scene.objects.link(ob)
    node.blender = ob

  # Connect this object to the parent object (if there is one)
  if node.parent.blender:
    node.blender.parent = node.parent.blender

  # Apply any material
  if hasattr(node.render, "material"):
    node.blender.data.materials.append(node.render.material.blender_material)

  if node.transform:
    # Now, apply the animation, if there is one
    if isinstance(node.transform, AnimatingNode):
      actions = get_actions_for_node(node.transform)
      if len(actions) > 1:
        print("Warning: More than one action for node not yet integrated")
      if actions:
        node.blender.animation_data_create()
        node.blender.animation_data.action = actions[0]
    # Apply the transformation base
    apply_node_transform(node.transform, node.blender)

    # Look at the empty scale here, and if it == 1 then make the empty_draw_size smaller
    # This tends to make "dummy" connectors not take a huge volume, whilst leaving smaller
    # connectors used for e.g. button volumes
    if node.blender.type == "EMPTY":
      distFromScale = node.blender.scale - Vector((1,1,1))
      if distFromScale.length < 0.01:
        node.blender.empty_draw_size = 0.01

  # If this is an LOD node, we will need to adjust the properties of our
  # children
  if isinstance(node.transform, LodNode):
    yield
    # We are now AFTER the children are processed
    assert node.blender.type == "EMPTY"
    node.blender.edm.is_lod_root = True
    for (start, end), child in zip(node.transform.level, node.children):
      child.blender.edm.lod_min_distance = start
      child.blender.edm.lod_max_distance = end
      child.blender.edm.nouse_lod_distance = end > 1e6

def read_file(filename, options={}):
  # Parse the EDM file
  edm = EDMFile(filename)

  print("Raw file graph:")
  print_edm_graph(edm.transformRoot)

  # Set the required blender preferences
  bpy.context.user_preferences.edit.use_negative_frames = True
  bpy.context.scene.use_preview_range = True
  bpy.context.scene.frame_preview_start = -100
  bpy.context.scene.frame_preview_end = 100
  
  # Convert the materials. These will be used by objects
  # We need to change the directory as the material searcher
  # currently uses the cwd
  with chdir(os.path.dirname(os.path.abspath(filename))):
    for material in edm.root.materials:
      material.blender_material = create_material(material)
      if material.blender_material and options.get("shadeless", False):
        material.blender_material.use_shadeless = True

  # WIP - use a translation graph to read. For now, just use it to print 
  # the file structure
  graph = build_graph(edm)
  graph.print_tree()

  # Walk through every node, and do the node processing
  graph.walk_tree(process_node)

  # Update the scene
  bpy.context.scene.update()

def create_visibility_actions(visNode):
  """Creates visibility actions from an ArgVisibilityNode"""
  actions = []
  for (arg, ranges) in visNode.visData:
    # Creates a visibility animation track
    action = bpy.data.actions.new("Visibility_{}".format(arg))
    actions.append(action)
    action.argument = arg
    # Create f-curves for hide_render
    curve = action.fcurves.new(data_path="hide_render")
    # Probably need an extra keyframe to specify start visibility
    if ranges[0][0] >= -0.995:
      curve.keyframe_points.add()
      curve.keyframe_points[0].co = (-FRAME_SCALE, 1.0)
      curve.keyframe_points[0].interpolation = 'CONSTANT'
    # Create the keyframe data
    for (start, end) in ranges:
      frameStart = int(start*FRAME_SCALE)
      frameEnd = FRAME_SCALE if end > 1.0 else int(end*FRAME_SCALE)
      curve.keyframe_points.add()
      key = curve.keyframe_points[-1]
      key.co = (frameStart, 0.0)
      key.interpolation = 'CONSTANT'
      if frameEnd < FRAME_SCALE:
        curve.keyframe_points.add()
        key = curve.keyframe_points[-1]
        key.co = (frameEnd, 1.0)
        key.interpolation = 'CONSTANT'
  return actions

def add_position_fcurves(action, keys, transform_left, transform_right):
  "Adds position fcurve data to an animation action"
  maxFrame = max(abs(x.frame) for x in keys) or 1.0
  frameScale = float(FRAME_SCALE) / maxFrame
  # Create an fcurve for every component  
  curves = []
  for i in range(3):
    curve = action.fcurves.new(data_path="location", index=i)
    curves.append(curve)

  # Loop over every keyframe in this animation
  for framedata in keys:
    frame = int(frameScale*framedata.frame)
    
    # Calculate the rotation transformation
    newPosMat = transform_left * Matrix.Translation(framedata.value) * transform_right
    newPos = newPosMat.decompose()[0]

    for curve, component in zip(curves, newPos):
      curve.keyframe_points.add()
      curve.keyframe_points[-1].co = (frame, component)
      curve.keyframe_points[-1].interpolation = 'LINEAR'

def add_rotation_fcurves(action, keys, transform_left, transform_right):
  "Adds rotation fcurve action to an animation action"
  maxFrame = max(abs(x.frame) for x in keys) or 1.0
  frameScale = float(FRAME_SCALE) / maxFrame
  
  # Create an fcurve for every component  
  curves = []
  for i in range(4):
    curve = action.fcurves.new(data_path="rotation_quaternion", index=i)
    curves.append(curve)

  # Loop over every keyframe in this animation
  for framedata in keys:
    frame = int(frameScale*framedata.frame)
    
    # Calculate the rotation transformation
    newRot = transform_left * framedata.value * transform_right

    for curve, component in zip(curves, newRot):
      curve.keyframe_points.add()
      curve.keyframe_points[-1].co = (frame, component)
      curve.keyframe_points[-1].interpolation = 'LINEAR'

def create_arganimation_actions(node):
  "Creates a set of actions to represent an ArgAnimationNode"
  actions = []

  # Calculate the base transform data for the node

  # Rotation quaternion for rotating -90 degrees around the X
  # axis. It seems animation data is not transformed into the
  # DCS world space automatically, and so we need to 'undo' the
  # transformation that was initially applied to the vertices when
  # reading into blender.
  RX = Quaternion((0.707, -0.707, 0, 0))
  RXm = RX.to_matrix().to_4x4()

  # Work out the transformation chain for this object
  aabS = MatrixScale(node.base.scale)
  aabT = Matrix.Translation(node.base.position)
  q1  = node.base.quat_1
  q2  = node.base.quat_2
  q1m = q1.to_matrix().to_4x4()
  q2m = q2.to_matrix().to_4x4()
  mat = node.base.matrix

  # Calculate the transform matrix quaternion part for pure rotations
  matQuat = matrix_to_blender(mat).decompose()[1]

  # With:
  #   aabT = Matrix.Translation(argNode.base.position)
  #   aabS = argNode.base.scale as a Scale Matrix
  #   q1m  = argNode.base.quat_1 as a Matrix (e.g. fixQuat1)
  #   q2m  = argNode.base.quat_2 as a Matrix (e.g. fixQuat2)
  #   mat  = argNode.base.matrix
  #   m2b  = matrix_to_blender e.g. swapping Z -> -Y

  # Save the 'null' transform onto the node, because we will need to
  # apply it to any object using this node's animation.

  #               Geometry is in Blender-space in-file already, and the import
  #                  procedure over-rotated it into an undefined space. Rotate 
  #                                                    back into Blender-space
  #                                                                      |
  #                                Transforms SAVED in blender-space     |
  #                                                   |     |      |     |
  #             Rotates geometry into file-space      |     |      |     |
  #                                           |       |     |      |     |
  # Neutralizes rotation into file-space,     |       |     |      |     |
  # keeping other transforms in blender       |       |     |      |     |
  #                               |           |       |     |      |     |
  dcLoc, dcRot, dcScale = (matrix_to_blender(mat) * aabT * q1m * aabS * RXm).decompose()
  node.zero_transform = dcLoc, dcRot, dcScale
  
  # Split a single node into separate actions based on the argument
  for arg in node.get_all_args():
    # Filter the animation data for this node to just this action
    posData = [x[1] for x in node.posData if x[0] == arg]
    rotData = [x[1] for x in node.rotData if x[0] == arg]
    scaleData = [x[1] for x in node.scaleData if x[0] == arg]
    # Create the action
    action = bpy.data.actions.new("AnimationArg{}".format(arg))
    actions.append(action)
    action.argument = arg
    
    # Calculate the pre and post-animation-value transforms
    leftRotation = matQuat * q1
    rightRotation = RX
    # At the moment, we don't understand the position transform
    leftPosition = matrix_to_blender(mat) * aabT
    rightPosition = aabS

    # Build the f-curves for the action
    for pos in posData:
      add_position_fcurves(action, pos, leftPosition, rightPosition)
    for rot in rotData:
      add_rotation_fcurves(action, rot, leftRotation, rightRotation)
  # Return these new actions
  return actions


def get_actions_for_node(node):
  """Accepts a node and gets or creates actions to apply their animations"""
  
  # Don't do this twice
  if hasattr(node, "actions") and node.actions:
    actions = node.actions
  else:
    actions = []
    if isinstance(node, ArgVisibilityNode):
      actions = create_visibility_actions(node)
    if isinstance(node, ArgAnimationNode):
      actions = create_arganimation_actions(node)
    # Save these actions on the node
    node.actions = actions

  return actions


def _find_texture_file(name):
  """
  Searches for a texture file given a basename without extension.

  The current working directory will be searched, as will any
  subdirectories called "textures/", for any file starting with the
  designated name '{name}.'
  """
  files = glob.glob(name+".*")
  if not files:
    matcher = re.compile(fnmatch.translate(name+".*"), re.IGNORECASE)
    files = [x for x in glob.glob("*.*") if matcher.match(x)]
    if not files:
      files = glob.glob("textures/"+name+".*")
      if not files:
        matcher = re.compile(fnmatch.translate("textures/"+name+".*"), re.IGNORECASE)
        files = [x for x in glob.glob("textures/*.*") if matcher.match(x)]
        if not files:
          print("Warning: Could not find texture named {}".format(name))
          return None
  # print("Found {} as: {}".format(name, files))
  if len(files) > 1:
    print("Warning: Found more than one possible match for texture named {}. Using {}".format(name, files[0]))
    files = [files[0]]
  textureFilename = files[0]
  return os.path.abspath(textureFilename)

def create_material(material):
  """Create a blender material from an EDM one"""
  # Find the actual file for the texture name
  if len(material.textures) == 0:
    return None

  diffuse_texture = next(x for x in material.textures if x.index == 0)

  name = diffuse_texture.name
  tex = bpy.data.textures.get(name)
  if not tex:
    filename = _find_texture_file(name)
    tex = bpy.data.textures.new(name, type="IMAGE")
    if filename:
      tex.image = bpy.data.images.load(filename)
      tex.image.use_alpha = False

  # Create material
  mat = bpy.data.materials.new(material.name)
  mat.specular_shader = "PHONG"
  # mat.use_shadeless = True
  mat.edm_material = material.material_name
  mat.edm_blending = str(material.blending)
  mat.use_cast_shadows_only = material.shadows.cast_only
  mat.use_shadows = material.shadows.receive
  mat.use_cast_shadows = material.shadows.cast
  # Read uniform values
  mat.diffuse_intensity = material.uniforms.get("diffuseValue", 1.0)
  mat.specular_intensity = material.uniforms.get("specFactor", mat.specular_intensity)
  
  # Convert power to blender 'hardness'
  # Actual range is (0-100) but basic step is 0.01 so at least this way every
  # distinct edm setting (up to 510) gets a distinct hardness
  specPower = material.uniforms.get("specPower", None)
  if specPower is not None:
    mat.specular_hardness = (specPower * 100) + 1

  reflection = material.uniforms.get("reflectionValue", 0.0)
  if reflection > 0.0:
    mat.raytrace_mirror.use = True
    mat.raytrace_mirror.reflect_factor = reflection
    mat.raytrace_mirror.gloss_factor = 1 - material.uniforms.get("reflectionBlurring", 0.0)

  mtex = mat.texture_slots.add()
  mtex.texture = tex
  mtex.texture_coords = "UV"
  mtex.use_map_color_diffuse = True

  return mat


def create_connector(connector):
  """Create an empty object representing a connector"""
  ob = bpy.data.objects.new(connector.name, None)
  ob.empty_draw_type = "CUBE"
  ob.edm.is_connector = True
  bpy.context.scene.objects.link(ob)
  return ob

def apply_node_transform(node, obj):
  """Assigns the transform to a given node"""
  assert node.category is NodeCategory.transform

  obj.rotation_mode = "QUATERNION"

  if isinstance(node, TransformNode):
    loc, rot, scale = matrix_to_blender(node.matrix).decompose()
    obj.location            = loc
    obj.rotation_quaternion = rot
    obj.scale               = scale
  elif isinstance(node, AnimatingNode):
    if hasattr(node, "zero_transform"):
      obj.location, obj.rotation_quaternion, obj.scale = node.zero_transform
    elif not isinstance(node, ArgVisibilityNode):
      # Vis nodes don't have transforms, but otherwise they should
      print("Warning: Transform {} has no zero-tranform".format(node))


def _create_mesh(vertexData, indexData, vertexFormat):
  """Creates a blender mesh object from vertex, index and format data"""

  # We need to reduce the vertex set to match the index set
  all_index = sorted(list(set(indexData)))
  new_vertices = [vertexData[x] for x in all_index]
  # new_indices = [i for i, _ in enumerate(all_index)]
  indexMap = {idx: i for i, idx in enumerate(all_index)}
  new_indices = [indexMap[x] for x in indexData]
  # Make sure we have the right number of indices...
  assert len(new_indices) % 3 == 0

  bm = bmesh.new()

  # Extract where the indices are
  posIndex = vertexFormat.position_indices
  normIndex = vertexFormat.normal_indices
  # Create the BMesh vertices, optionally with normals
  for i, vtx in enumerate(new_vertices):
    pos = vector_to_blender(Vector(vtx[x] for x in posIndex))
    vert = bm.verts.new(pos)
    if normIndex:
      vert.normal = vector_to_blender(Vector(vtx[x] for x in normIndex))

  bm.verts.ensure_lookup_table()

  # Prepare for texture information
  uvIndex = vertexFormat.texture_indices
  if uvIndex:
    # Ensure a UV layer exists before creating faces
    uv_layer = bm.loops.layers.uv.verify()
    bm.faces.layers.tex.verify()  # currently blender needs both layers.
  
  # Generate faces, with texture coordinate information
  for face in [new_indices[i:i+3] for i in range(0, len(new_indices), 3)]:
  # for face, uvs in zip(indexData, uvData):
    try:
      f = bm.faces.new([bm.verts[i] for i in face])
      # Add UV data if we have any
      if uvIndex:
        uvData = [[new_vertices[x][y] for y in uvIndex] for x in face]
        for loop, uv in zip(f.loops, uvData):
          loop[uv_layer].uv = (uv[0], 1-uv[1])
    except ValueError as e:
      print("Error: {}".format(e))

  # Create the mesh object
  mesh = bpy.data.meshes.new("Mesh")
  bm.to_mesh(mesh)
  mesh.update()

  return mesh

def create_object(node):
  """Accepts an edm renderable and returns a blender object"""

  if not isinstance(node, (RenderNode, ShellNode)):
    print("WARNING: Do not understand creating types {} yet".format(type(node)))
    return

  if isinstance(node, RenderNode):
    vertexFormat = node.material.vertex_format
  elif isinstance(node, ShellNode):
    vertexFormat = node.vertex_format

  # Create the mesh
  mesh = _create_mesh(node.vertexData, node.indexData, vertexFormat)
  mesh.name = node.name

  # Create and link the object
  ob = bpy.data.objects.new(node.name, mesh)
  ob.edm.is_collision_shell = isinstance(node, ShellNode)
  ob.edm.is_renderable      = isinstance(node, RenderNode)
  ob.edm.damage_argument = -1 if not isinstance(node, RenderNode) else node.damage_argument
  bpy.context.scene.objects.link(ob)

  return ob

def create_lamp(node):
  """Creates a blender lamp from an edm renderable LampNode"""
  data = bpy.data.lamps.new(name=node.name, type='POINT')
  obj = bpy.data.objects.new(name=node.name, object_data=data)
  print("Warning: Light nodes created, but not populated from edm data")
  bpy.context.scene.objects.link(obj)
  return obj