import json
import mathutils
import re
from io_mesh_jax.common_jax import *

def export_object_to_file(operator, context, properties):
  options = {
    'scale': properties.scale,
    'flip_yz': properties.flip_yz,
    
    'vertices': properties.vertices,
    'normals': properties.normals,
    'colors': properties.colors,
    'textureCoords': properties.texture_coords
  }
  scene = context.scene
  ob = scene.objects.active

  mesh = ob.to_mesh(scene, True, 'RENDER')
  if not mesh: raise Exception("Could not collect mesh data from object '%s'" % ob.name)
  class_name = ob.name.replace('.', '')
  export = { class_name : export_mesh(mesh, options) }

  filepath = properties.filepath
  if re.search('\\.json', filepath) == None: filepath = filepath + ".json"
  
  out = open(filepath, 'w')
  out.write(json.dumps(export))
  out.close()
  
  return {'FINISHED'}

def normalize_options(options):
  if not 'vertices' in options: options['vertices'] = True
  if not 'scale' in options: options['scale'] = 1
  if not 'normals' in options: options['normals'] = True
  if not 'colors'  in options: options['colors']  = True
  if not 'textureCoords' in options: options['textureCoords'] = True
  if not 'indices' in options: options['indices'] = True
  if not 'flip_yz' in options: options['flip_yz'] = False
  return options
  
def export_mesh(mesh, options):
  normalize_options(options)
  mesh.calc_normals();
  mesh.transform(mathutils.Matrix.Scale(options['scale'], 4))
  
  result = {
    'vertices': [],
    'colors': [],
    'textureCoords': [],
    'normals': [],
    'indices': []
  }
  
  indexLookup = {}

  faceUV = (len(mesh.uv_textures) > 0)
  vertexUV = (len(mesh.sticky) > 0)
  vertexColors = (len(mesh.vertex_colors) > 0)
  
  if len(mesh.vertex_colors) == 0 or not mesh.vertex_colors.active: options['colors'] = False
  if len(mesh.uv_textures)   == 0 or not mesh.uv_textures.active:   options['textureCoords'] = False
  
  def push(mesh, face, order, result, indexLookup, options):
    VERTICES, COLORS, TEXCOORDS, NORMALS = 0, 1, 2, 3
    
    # finds the index in indexLookup of the next combination of data, and uses it; if it doesn't
    # exist, a new index is created and used. We can't simply reply on face.vertices[] for indices
    # because we need to duplicate the vertex data to produce flat normals.
    first = True
    for i in order:
      # reset key
      key = [[],[],[],[]]

      # construct key
      if options['vertices']:
        if options['flip_yz']:
          key[VERTICES].extend(vec3(x = mesh.vertices[face.vertices[i]].co[0],
                                    y = mesh.vertices[face.vertices[i]].co[2],
                                    z = mesh.vertices[face.vertices[i]].co[1]))
        else:
          key[VERTICES].extend(vec3(v = mesh.vertices[face.vertices[i]].co))
      if options['colors']:
        color = getattr(mesh.vertex_colors.active.data[face.index], "color%i" % (i+1))
        key[COLORS].append(vec3(color))
      if options['textureCoords']:
        uv = getattr(mesh.uv_textures.active.data[face.index], "uv%i" % (i+1))
        key[TEXCOORDS].append(vec2(uv))
      if options['normals']:
        if face.use_smooth:
          if options['flip_yz']:
            normal = mesh.vertices[face.vertices[i]].normal
            key[NORMALS].extend(vec3(x = normal[0], y = normal[2], z = normal[1]))
          else:
            key[NORMALS].extend(vec3(mesh.vertices[face.vertices[i]].normal))
        else:
          if options['flip_yz']:
            normal = face.normal
            key[NORMALS].extend(vec3(x = normal[0], y = normal[2], z = normal[1]))
          else:
            key[NORMALS].extend(vec3(face.normal))
        
      # make key hashable
      for i in range(0, 4): key[i] = tuple(key[i])
      key = tuple(key)
      
      # find or create key
      if key in indexLookup:
        index = indexLookup[key]
      else:
        index = len(indexLookup.keys())
        indexLookup[key] = index
        # add data for the new index
        result['vertices'].extend(key[VERTICES])
        result['normals'].extend(key[NORMALS])
        for j in range(0, len(key[COLORS])):
          while len(result['colors']) <= j: result['colors'].append([])
          result['colors'][j].extend(key[COLORS][j])
        for j in range(0, len(key[TEXCOORDS])):
          while len(result['textureCoords']) <= j: result['textureCoords'].append([])
          result['textureCoords'][j].extend(key[TEXCOORDS][j])
  
      if options['indices']: result['indices'].append(index)
      first = False
  
  for face in mesh.faces:
    if len(face.vertices) == 4: # quad
      push(mesh, face, [1,2,0], result, indexLookup, options)
      push(mesh, face, [0,2,3], result, indexLookup, options)
    else: # tri
      push(mesh, face, [0,1,2], result, indexLookup, options)

  return result
