import bpy
import math
import mathutils
import json

def extract_armature(armature_object):
    translation = armature_object.matrix_world * bone.head
    matrix = bone.matrix
    # matrix = armature_object.matrix_world * bone.matrix

    if parent_index == -1:
      X_ROT = mathutils.Matrix.Rotation(-math.pi/2, 4, 'X')
      #matrix = X_ROT * armature_object.matrix_world * bone.matrix
    
    scale = matrix.to_scale()
    orientation = matrix.to_quaternion()
    bones_data.append({
      "name" : bone.name, 
      "parent" : parent_index,
      "scale" : {"x" : scale.x, "y" : scale.y, "z" : scale.z},
      "translation" : {"x" : translation.x, "y" : translation.y, "z" : translation.z},
      "orientation" : {"x" : orientation.x, "y" : orientation.y, "z" : orientation.z, "w" : orientation.w }
    })
    armature_data = {"name" : armature_object.name, "bones" : bones_data}
    return armature_data

def extract_bone_(bone, armature, matrix_world):
  parent_index = -1;
  if bone.parent != None:
    bone_index = 0
    for bone_data in armature.bones:
      if bone_data.name == bone.parent.name:
        parent_index = bone_index
        break
      bone_index = bone_index + 1

  translation = matrix_world * bone.head
  matrix = matrix_world.to_3x3() * bone.matrix

  if parent_index == -1:
    X_ROT = mathutils.Matrix.Rotation(-math.pi/2, 4, 'X')
    matrix = X_ROT.to_3x3() * matrix_world.to_3x3() * bone.matrix
  
  scale = matrix.to_scale()
  orientation = matrix.to_quaternion()

  return {
    "name":bone.name, 
    "parent":parent_index,
    "scale" : {"x" : scale.x, "y" : scale.y, "z" : scale.z},
    "translation" : {"x" : translation.x, "y" : translation.y, "z" : translation.z},
    "orientation" : {"x" : orientation.x, "y" : orientation.y, "z" : orientation.z, "w" : orientation.w }
    }

def extract_armature_(armature_object):
  armature = bpy.data.armatures[armature_object.name]
  bones_data = list(map(lambda bone: extract_bone_(bone, armature, armature_object.matrix_world), armature.bones))
  return {"name":"Armature", "bones" : bones_data}

def extract_submesh_(mesh_object):
  temporary_meshes = []
  mesh = mesh_object.to_mesh(bpy.context.scene, True, 'RENDER')
  X_ROT = mathutils.Matrix.Rotation(-math.pi/2, 4, 'X')
  mesh.transform(X_ROT * mesh_object.matrix_world)
  mesh.update(calc_tessface=True)
  mesh.calc_normals()

  armature = None
  armature_name = ""

  if mesh_object.parent and mesh_object.parent.type == 'ARMATURE':
    armature = mesh_object.parent
    armature_name = mesh_object.parent.name

  vertices = []
  normals = []
  weights = []
  vertex_groups = []

  for group in mesh_object.vertex_groups:
    vertex_groups.append({"name":group.name,"index":group.index})

  for vertex in mesh.vertices:
    v = vertex.co
    vertices.append(v.x)
    vertices.append(v.y)
    vertices.append(v.z)

    n = vertex.normal
    n.normalize()

    normals.append(n.x)
    normals.append(n.y)
    normals.append(n.z)

    vertex_weights = []
    for group in vertex.groups:
      bone_name = mesh_object.vertex_groups[group.group].name

      bone_index = 0
      if armature != None:
        for bone in armature.pose.bones:
          if (bone.name == bone_name):
            vertex_weights.append({"index":bone_index, "weight":group.weight})
          bone_index = bone_index + 1
      
    weights.append(vertex_weights)

  indices = []
  for polygon in mesh.polygons:
    if len(polygon.vertices) == 4:
      a = polygon.vertices[0]
      b = polygon.vertices[1]
      c = polygon.vertices[2]
      d = polygon.vertices[3]

      indices.append(a)
      indices.append(b)
      indices.append(c)
      indices.append(c)
      indices.append(d)
      indices.append(a)

    if len(polygon.vertices) == 3:
      a = polygon.vertices[0]
      b = polygon.vertices[1]
      c = polygon.vertices[2]

      indices.append(a)
      indices.append(b)
      indices.append(c)

  for temp_mesh in temporary_meshes:
    bpy.data.meshes.remove(temp_mesh)

  return {
    "armature": armature_name, 
    "vertices": vertices, 
    "normals": normals, 
    "indices": indices, 
    "weights": weights,
    "groups": vertex_groups
  }

def extract_posed_armature_(armature_object):
  armature = bpy.data.armatures[armature_object.name]
  bones_data = []
  for bone in armature_object.pose.bones:
    parent_index = -1;
    if bone.parent != None:
      bone_index = 0
      for bone_data in armature_object.pose.bones:
        if bone_data.name == bone.parent.name:
          parent_index = bone_index
          break
        bone_index = bone_index + 1

    X_ROT = mathutils.Matrix.Rotation(-math.pi/2, 4, 'X')
    translation = bone.head
    matrix = bone.matrix

    if parent_index == -1:
      translation = X_ROT * armature_object.matrix_world * bone.head
      matrix = X_ROT * armature_object.matrix_world * bone.matrix
    
    scale = matrix.to_scale()
    orientation = matrix.to_quaternion()
    bones_data.append({
      "name" : bone.name, 
      "parent" : parent_index,
      "scale" : {"x" : scale.x, "y" : scale.y, "z" : scale.z},
      "translation" : {"x" : translation.x, "y" : translation.y, "z" : translation.z},
      "orientation" : {"x" : orientation.x, "y" : orientation.y, "z" : orientation.z, "w" : orientation.w }
    })
  return {"name" : armature_object.name, "bones" : bones_data}

def extract_frame_(frame_index, start_frame_index):
  fps = bpy.data.scenes[0].render.fps
  time = (frame_index - start_frame_index) / fps
  bpy.data.scenes[0].frame_set(frame_index)

  armature_objects = filter(lambda o: o.type == 'ARMATURE', bpy.data.objects)
  armatures_data = list(map(extract_posed_armature_, armature_objects))

  return {"armatures" : armatures_data, "time" : time}

def extract_animation_(action):
  end_frame = int(action.frame_range[1])
  start_frame = int(action.frame_range[0])
  frame_length = end_frame - start_frame
  frames_data = list(map(lambda frame_index: extract_frame_(frame_index, start_frame), range(start_frame, end_frame)))

  return {"name" : action.name, "frames" : frames_data}

def do_export(filepath):

  current_frame = bpy.data.scenes[0].frame_current
  bpy.data.scenes[0].frame_set(0)

  armature_objects = filter(lambda o: o.type == 'ARMATURE', bpy.data.objects)
  armatures_data = list(map(extract_armature_, armature_objects))

  mesh_objects = filter(lambda o: o.type == 'MESH', bpy.data.objects)
  submeshes_data = list(map(extract_submesh_, mesh_objects))

  animation_data = list(map(extract_animation_, bpy.data.actions))

  # animations = []
  # ##### Animation
  # fps = bpy.data.scenes[0].render.fps

  # for action in bpy.data.actions:
  #   end_frame = int(action.frame_range[1])
  #   start_frame = int(action.frame_range[0])
  #   frame_length = end_frame - start_frame

  #   frames_data = []
  #   for frame_index in range(start_frame, end_frame):
  #     time = (frame_index - start_frame) / fps

  #     bpy.data.scenes[0].frame_set(frame_index)
  #     armatures_data = []
  #     for obj in bpy.data.objects:
  #       if obj.type == 'ARMATURE':
  #         armature = obj
  #         armature_data = extract_armature(armature)
  #         armatures_data.append(armature_data)
  #       frame_data = {"time":time, "armatures" : armatures_data}
  #       frames_data.append(frame_data)

  #   animation = {"name" : action.name, "frames" : frames_data}
  #   animations.append(animation)
  bpy.data.scenes[0].frame_set(current_frame)

  mesh_data = {"submeshes" : submeshes_data, "armatures" : armatures_data, "animations" : animation_data}
  content = json.dumps(mesh_data, sort_keys=True, indent=4, separators=(',', ': '))
  out = open(filepath, "w", encoding="utf-8")
  out.write(content)
  out.close()