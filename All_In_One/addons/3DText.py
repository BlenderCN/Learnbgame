bl_info = {
    "name": "3D Text",
    "author": "DrawFun",
    "version": (0, 0, 0),
    "blender": (2, 7, 8),
    "location" : "View3D > Add > Mesh > 3D Text",
    "description": "Make 3D Text Effect",
    "category": "Learnbgame",
}

import bpy
import math
import mathutils

_3D_TEXT_OBJECT_NAME = "3DText_Text"

# Menu Functions
def menu_func(self, context):
    self.layout.operator(Object3DText.bl_idname)


# Helper Functions
def look_at(obj_camera, point):
    loc_camera = obj_camera.matrix_world.to_translation()
    direction = point - loc_camera
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')

    # assume we're using euler rotation
    obj_camera.rotation_euler = rot_quat.to_euler()


# Objects
def create_plane():
    # Define vertices and faces
    verts = [(0, 0, 0), (0, 50, 0), (50, 50, 0), (50, 0, 0)]
    faces = [(0, 1, 2, 3)]

    # Define mesh and object variables
    my_mesh = bpy.data.meshes.new("3DText_Plane_Mesh")
    my_plane = bpy.data.objects.new("3DText_Plane", my_mesh)

    # Set location and scene of object
    my_plane.location = (-25, -25, -0.03)

    # Create mesh
    my_mesh.from_pydata(verts, [], faces)
    my_mesh.update(calc_edges = True)

    bpy.context.scene.objects.link(my_plane)
    return my_plane


def create_3dtext(text_body):
    bpy.ops.object.text_add()
    text = bpy.context.object
    text.name = _3D_TEXT_OBJECT_NAME
    text.location = (0, 0, 0)
    text.rotation_euler = (math.pi / 2, 0, 0)
    text.data.body = text_body
    text.data.extrude = 0.1
    text.data.bevel_depth = 0.02
    text.data.offset = -0.01
    text.data.align_x = 'CENTER'
    return text


def create_3d_emission_text(text_body):
    bpy.ops.object.text_add()
    text = bpy.context.object
    text.name = "3DText_EMISSION_Text"
    text.location = (0, 0.1, 0)
    text.rotation_euler = (math.pi / 2, 0, 0)
    text.data.body = text_body
    text.data.align_x = 'CENTER'
    return text


# Materials
def create_3d_text_material():
    # Create material
    scn = bpy.context.scene
    # Set cycles render engine if not selected
    if not scn.render.engine == 'CYCLES':
        scn.render.engine = 'CYCLES'

    mat = bpy.data.materials.new("3DText Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # clear all nodes to start clean
    for node in nodes:
        nodes.remove(node)

    node = nodes.new(type='ShaderNodeBsdfGlass')
    node.inputs['Color'].default_value = [0.8, 0.1, 0.18, 0]
    node.inputs['Roughness'].default_value = 0.2

    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    links = mat.node_tree.links
    links.new(node.outputs[0], node_output.inputs[0])
    return mat


def create_3d_text_emission_material():
    # Create material
    scn = bpy.context.scene
    # Set cycles render engine if not selected
    if not scn.render.engine == 'CYCLES':
        scn.render.engine = 'CYCLES'

    mat = bpy.data.materials.new("3DText Emission Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # clear all nodes to start clean
    for node in nodes:
        nodes.remove(node)

    node = nodes.new(type='ShaderNodeEmission')
    node.inputs['Color'].default_value = [1, 1, 1, 0]
    node.inputs['Strength'].default_value = 1.5

    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    links = mat.node_tree.links
    links.new(node.outputs[0], node_output.inputs[0])
    return mat


def create_plane_material():
    # Create material
    scn = bpy.context.scene
    # Set cycles render engine if not selected
    if not scn.render.engine == 'CYCLES':
        scn.render.engine = 'CYCLES'

    mat = bpy.data.materials.new("Plane Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # clear all nodes to start clean
    for node in nodes:
        nodes.remove(node)

    diffuse_shader = nodes.new(type='ShaderNodeBsdfDiffuse')
    diffuse_shader.inputs['Color'].default_value = [0.0, 0.4, 0.8, 1]
    diffuse_shader.inputs['Roughness'].default_value = 0.0

    glass_shader = nodes.new(type='ShaderNodeBsdfGlossy')
    glass_shader.inputs['Color'].default_value = [0.26, 0.26, 0.26, 1]
    glass_shader.inputs['Roughness'].default_value = 0.0

    mix_shader = nodes.new(type='ShaderNodeMixShader')

    links = mat.node_tree.links
    links.new(glass_shader.outputs[0], mix_shader.inputs[2])
    links.new(diffuse_shader.outputs[0], mix_shader.inputs[1])

    node_output = nodes.new(type='ShaderNodeOutputMaterial')

    links.new(mix_shader.outputs[0], node_output.inputs[0])
    return mat


class Object3DText(bpy.types.Operator):
    """Object 3D Text"""
    bl_idname = "object.3d_text"
    bl_label = "3D Text"
    bl_options = {'REGISTER', 'UNDO'}

    text_body = bpy.props.StringProperty(name="Text to Show",
                                         description="The text string you wish to be showed.",
                                         default="Text")

    def execute(self, context):
        text = create_3dtext(self.text_body)
        text_material = create_3d_text_material()
        if len(text.data.materials):
            text.data.materials[0] = text_material
        else:
            text.data.materials.append(text_material)
        text_emission = create_3d_emission_text(self.text_body)
        text_emission_material = create_3d_text_emission_material()
        if len(text_emission.data.materials):
            text_emission.data.materials[0] = text_emission_material
        else:
            text_emission.data.materials.append(text_emission_material)
        plane = create_plane()
        plane_material = create_plane_material()
        if len(plane.data.materials):
            plane.data.materials[0] = plane_material
        else:
            plane.data.materials.append(plane_material)
        camera = bpy.data.objects["Camera"]
        camera.location = (0, -5, 2)
        look_at(camera, mathutils.Vector((0, -0, 0)))
        return {'FINISHED'}


def register():
    bpy.utils.register_class(Object3DText)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(Object3DText)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()
    #camera = bpy.data.objects["Camera"]
    #camera.location = (0, -5, 2)
    #look_at(camera, mathutils.Vector((0, -0, 0)))