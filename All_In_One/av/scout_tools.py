import bpy

bl_info = {
    'name': 'scout_tools',
    'description': 'Contains functions to build shapes and materials',
    'author': 'morgan',
    'version': (1, 0),
    'blender': (2, 73, 0),
    }

def createPlane(origin, length, width, rotation):
    bpy.ops.mesh.primitive_plane_add(location=origin)
    plane = bpy.context.active_object
    plane.scale = (length, width, 1)
    plane.rotation_mode = 'XYZ'
    plane.rotation_euler = rotation
    return plane

def createCylinder(origin, radius, height, rotation, **kwargs):
    bpy.ops.mesh.primitive_cylinder_add(location=origin, vertices=100)
    cylinder = bpy.context.active_object
    cylinder.scale = (radius, radius, height/2)
    cylinder.rotation_mode = 'XYZ'
    cylinder.rotation_euler = rotation
    return cylinder

def createCone(origin, top_radius, bot_radius, length, rotation):
    bpy.ops.mesh.primitive_cone_add(radius2=top_radius, radius1=bot_radius,
                                    depth=length, vertices=100, location=origin)
    cone = bpy.context.active_object
    cone.rotation_mode = 'XYZ'
    cone.rotation_euler = rotation
    return cone

def createCube(origin, x, y, z, rotation):
    bpy.ops.mesh.primitive_cube_add(location=origin)
    cube = bpy.context.active_object
    cube.scale = (x, y, z)
    cube.rotation_mode = 'XYZ'
    cube.rotation_euler = rotation
    return cube

def difference(first, second):
    modifier = first.modifiers.new('Modifier', 'BOOLEAN')
    modifier.object = second
    modifier.operation = 'DIFFERENCE'
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modifier.name)
    scene = bpy.context.scene
    scene.objects.unlink(second)

def union(first, second):
    modifier = first.modifiers.new('Modifier', 'BOOLEAN')
    modifier.object = second
    modifier.operation = 'UNION'
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modifier.name)

def makeMaterial(name, diffuse, specular, alpha):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5
    mat.alpha = alpha
    mat.use_transparency = True
    mat.ambient = 1
    return mat

def setMaterial(ob, mat):
    me = ob.data
    me.materials.append(mat)

def join(obj1, obj2):
    bpy.ops.object.select_all(action='DESELECT')
    scn = bpy.context.scene
    scn.objects.active = scn.objects[obj1.name]
    bpy.data.objects[obj1.name].select = True
    bpy.data.objects[obj2.name].select = True
    bpy.ops.object.join()
    bpy.ops.object.select_all(action='DESELECT')

def name_clean_transform(name, rot_angle, rot_axis):
    # deselect all elements
    bpy.ops.object.select_all(action='DESELECT')
    scn = bpy.context.scene
    obj_to_add = [obj.name for obj in scn.objects if obj.type == 'MESH']
    for obj_name in obj_to_add:
        if not obj_name.startswith('scout'):
            scn.objects.active = scn.objects[obj_name]
            bpy.data.objects[obj_name].select = True
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        else:
            bpy.data.objects[obj_name].select = False
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH' and not obj.name.startswith('scout'):
            obj.name = name
    bpy.ops.transform.rotate(value=rot_angle, axis=rot_axis)
    
def sum_tuple(tup1, tup2):
    return tuple( sum(pair) for pair in zip(tup1, tup2))
