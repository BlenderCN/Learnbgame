'''
Blender 2.5 export script.

Aim: get the stuff out of blender so it can be processed in a friendlier development environment
(eg. eclipse + python 3). Will also make it simpler to have good unit tests.
'''

import bpy
import os
import errno
import shutil

def get_info_for_mesh(meshinfo, meshname):
    if meshname in meshinfo:
        return meshinfo[meshname]
    info = {}
    meshinfo[meshname] = info
    return info

def mkdir(path):
    try:
        os.makedirs(path)
        print("Made dir: ", path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

def getdir(path):
    mkdir(path)
    return path

def write_floats(file, seq):
    for i in seq:
        file.write(' %s ' % repr(i))

def write_faces_with_texcoord(file, mesh):
    # TODO: one can have multiple uv layers pr mesh
    uv_layer = mesh.uv_textures[0]
    if len(uv_layer.data) != len(mesh.faces):
        raise Exception('Not all faces have texture coordinates', mesh)
    for f, texface in zip(mesh.faces, uv_layer.data):
        file.write('v')
        for v in f.vertices: file.write(' %i' % v)
        file.write(' f %i' % f.material_index)
        if not f.use_smooth:
            no = f.normal
            file.write(' n ')
            write_floats(file, (no.x, no.y, no.z))
        file.write(' u ')
        write_floats(file, texface.uv_raw)
        file.write('\n')

def write_faces_no_texcoord(file, mesh):
    for f in mesh.faces:
        file.write('v')
        for v in f.vertices: file.write(' %i' % v)
        file.write(' f %i' % f.material_index)
        if not f.use_smooth:
            no = f.normal
            file.write(' n ')
            write_floats(file, (no.x, no.y, no.z))
        file.write('\n')

def write_faces(meshinfo, file, mesh):
    if len(mesh.uv_textures) == 0:
        get_info_for_mesh(meshinfo, mesh.name)['uv'] = False
        write_faces_no_texcoord(file, mesh)
    else:
        get_info_for_mesh(meshinfo, mesh.name)['uv'] = True
        write_faces_with_texcoord(file, mesh)

def write_vertices(file, mesh):
    for v in mesh.vertices:
        no = v.normal
        write_floats(file, (v.co.x, v.co.y, v.co.z, no.x, no.y, no.z))
        file.write('\n')

def get_face_material(mesh):
    if not mesh.materials:
        return None
    materials = set()
    for f in mesh.faces:
        materials.add(f.material_index)
    if len(materials) > 1:
        print('Warning: at most one material pr mesh is supported (name: %s)' % mesh.name)
    for index in materials:
        mat = mesh.materials[index]
        if mat:
            return mat 
    return None

def get_target_file(dir, filepath):
    # Note: relative paths in blender for some obscure reason start with '//'
    if filepath.startswith('//'):
        relative = filepath[2:]
        blenddir = os.path.dirname(get_blendfile())
        filepath = os.path.join(blenddir, relative)
    target = os.path.join(dir, os.path.basename(filepath))
    if os.path.isfile(target):
        print('Note: skipping copy as the file exists:\n', target)
        return target
    if not os.path.isfile(filepath):
        raise Exception('Cannot copy to target, file does not exist:', filepath)
    print('Copying: ', filepath, ' -> ', target)
    shutil.copy(filepath, target)
    return target

def write_meshgeometry(meshinfo, dir, mesh):
    facefile = open(os.path.join(dir, "face.txt"), 'w')
    vertfile = open(os.path.join(dir, "vertex.txt"), 'w')
    try:
        write_faces(meshinfo, facefile, mesh)
        write_vertices(vertfile, mesh)
    finally:
        facefile.close()
        vertfile.close()

def write_meshesdata(meshinfo, dir):
    meshes_dir = getdir(os.path.join(dir, "meshes"))
    for mesh in bpy.data.meshes:
        mesh_dir = getdir(os.path.join(meshes_dir, mesh.name))
        write_meshgeometry(meshinfo, mesh_dir, mesh)

def write_camera(f, obj):
    f.write('  "%s" : {\n' % obj.name)
    f.write('    "name"        : "%s",\n' % obj.name)
    f.write('    "type"        : "%s",\n' % obj.type)
    f.write('    "lens"        : %s,\n' % repr(obj.lens))
    f.write('    "angle"       : %s,\n' % repr(obj.angle))
    f.write('  },\n')

def get_object_properties(obj):
    props = {}
    for prop in obj.getAllProperties():
        props[prop.name] = prop.data
    return props

def matrix(mat):
    return tuple([tuple(v) for v in mat])
    
def write_object(f, obj):
    f.write('  "%s" : {\n' % obj.name)
    f.write('    "name"        : "%s",\n' % obj.name)
    f.write('    "data_name"   : "%s",\n' % obj.data.name)
    f.write('    "type"        : "%s",\n' % obj.type)
    f.write('    "matrix"      : %s,\n' % repr(matrix(obj.matrix_world)))
    f.write('    "position"    : %s,\n' % repr(tuple(obj.location)))
    f.write('    "scale"       : %s,\n' % repr(tuple(obj.scale)))
    f.write('    "rotation"    : %s,\n' % repr(tuple(obj.rotation_euler)))
    f.write('    "color"       : %s,\n' % repr(tuple(obj.color)))
    f.write('  },\n')

def write_mesh(meshinfo, f, mesh):
    material = get_face_material(mesh)
    if material:
        f.write('  "%s" : {\n' % mesh.name)
        f.write('    "name"        : "%s",\n' % mesh.name)
        f.write('    "material"    : "%s",\n' % material.name)
        f.write('    "info"        : %s,\n' % get_info_for_mesh(meshinfo, mesh.name))
        f.write('  },\n')
    else:
        print('WARNING: skipping mesh with no material: %s' % mesh.name)

def write_material(f, mat):
    f.write('  "%s" : {\n' % mat.name)
    f.write('    "name"        : "%s",\n' % mat.name)
    f.write('    "shader"      : "%s",\n' % mat.get('shader', 'default'))
    f.write('    "textures"    :\n')
    f.write('    (\n')
    for slot in mat.texture_slots:
        if slot and slot.use and slot.texture:
            f.write('      "%s",\n' % slot.texture.name)
    f.write('    ),\n')
    f.write('  },\n')
    
def write_textures_images(f):
    images = set()
    imagedir = getdir(os.path.join(os.path.dirname(f.name), 'images'))
    f.write('textures = {\n')
    for tex in [tex for tex in bpy.data.textures if tex.type == 'IMAGE' and tex.image]:
        try:
            filename = os.path.basename(get_target_file(imagedir, tex.image.filepath))
            images.add((tex.image, filename))
            f.write('  "%s" : {\n' % tex.name)
            f.write('    "name"        : "%s",\n' % tex.name)
            f.write('    "image"       : "%s",\n' % tex.image.name)
            f.write('  },\n')
        except Exception as e:
            print('Error: ', e)
    f.write('}\n')
    f.write('images = {\n')
    for image, filename in images:
        f.write('  "%s" : {\n' % image.name)
        f.write('    "name"        : "%s",\n' % image.name)
        f.write('    "file"        : "%s",\n' % filename)
        f.write('  },\n')
    f.write('}\n')
    
def write_meshes(meshinfo, f):
    f.write('meshes = {\n')
    for mesh in bpy.data.meshes:
        write_mesh(meshinfo, f, mesh)
    f.write('}\n')

def write_materials(f):
    f.write('materials = {\n')
    for mat in bpy.data.materials:
        write_material(f, mat)
    f.write('}\n')

def write_cameras(f):
    f.write('cameras = {\n')
    for obj in bpy.data.cameras:
        write_camera(f, obj)
    f.write('}\n')
        
def write_objects(f):
    f.write('objects = {\n')
    for obj in bpy.data.objects:
        write_object(f, obj)
    f.write('}\n')
    
def get_3d_view_matrices():
    m = []
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        m.append(matrix(space.region_3d.view_matrix))
    return m

def write_sceneinfo(f):
    f.write('scene = {\n')
    f.write('  "name"           : "%s",\n' % bpy.context.scene.name)
    f.write('  "camera"         : "%s",\n' % bpy.context.scene.camera.name)
    f.write('  "views"          : \n')
    f.write('  (\n')
    matrices = get_3d_view_matrices()
    zero = (0.0,0.0,0.0,0.0)
    for m in [m for m in matrices if m.count(zero) < 4]:
        f.write('    %s,\n' % repr(m))
    for m in [m for m in matrices if m.count(zero) >= 4]:
        f.write('    %s,\n' % repr(m))
    f.write('  ),\n')
    f.write('}\n')
    
def write_scene(meshinfo, dir):
    f = open(os.path.join(dir, 'scene.py'), 'w')
    try:
        write_sceneinfo(f)
        write_meshes(meshinfo, f)
        write_materials(f)
        write_textures_images(f)
        write_cameras(f)
        write_objects(f)
    finally:
        f.close()

def get_scenedirname():
    blendfile = bpy.data.filepath
    if os.path.isfile(blendfile):
        return os.path.basename(blendfile) + '.proz'
    return 'unsaved'

def get_projectdir():
    # note, was before: os.path.dirname(os.path.abspath( __file__ ))
    # this is not useful when the script is a symbolic link in the blender dir
    return os.path.expanduser("~/prozess")

def prozess():
    projectdir = getdir(get_projectdir())
    dir = getdir(os.path.join(projectdir, 'scenes'))
    scenedirname = get_scenedirname()
    dir = getdir(os.path.join(dir, scenedirname))
    print('Target directory for generated files: ', dir)
    print('Exporting...')
    meshinfo = {}
    write_meshesdata(meshinfo, dir)
    write_scene(meshinfo, dir)
    print('Done.')
    print(meshinfo)
