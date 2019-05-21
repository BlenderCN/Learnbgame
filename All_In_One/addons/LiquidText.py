bl_info = {
    "name": "Liquid Text",
    "author": "DrawFun",
    "version": (0, 0, 0),
    "blender": (2, 7, 8),
    "location" : "View3D > Add > Mesh > 3D Text",
    "description": "Make Liquid Text Effect",
    "category": "Learnbgame"
}

import bpy
import math
import mathutils

LIQUID_TEXT_OBJECT_NAME = "LiquidText_Text"

# Menu Functions
def menu_func(self, context):
    self.layout.operator(ObjectLiquidText.bl_idname)


# Helper Functions
def look_at(obj_camera, point):
    loc_camera = obj_camera.matrix_world.to_translation()
    direction = point - loc_camera
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')

    # assume we're using euler rotation
    obj_camera.rotation_euler = rot_quat.to_euler()


# Physics
def create_liquid_text_canvas():
    bpy.ops.object.modifier_add(type='DYNAMIC_PAINT')
    bpy.ops.dpaint.type_toggle(type='CANVAS')
    bpy.context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].frame_start = 1
    bpy.context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].frame_end = 120
    bpy.context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].surface_type = 'WAVE'
    bpy.context.object.modifiers["Dynamic Paint"].canvas_settings.canvas_surfaces["Surface"].wave_damping = 0.07


def create_liquid_text_brush():
    bpy.ops.object.modifier_add(type='DYNAMIC_PAINT')
    bpy.context.object.modifiers["Dynamic Paint"].ui_type = 'BRUSH'
    bpy.ops.dpaint.type_toggle(type='BRUSH')


# Materials
def create_liquid_text_material():
    # Create material
    scn = bpy.context.scene
    # Set cycles render engine if not selected
    if not scn.render.engine == 'CYCLES':
        scn.render.engine = 'CYCLES'

    mat = bpy.data.materials.new("Liquid Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # clear all nodes to start clean
    for node in nodes:
        nodes.remove(node)

    node = nodes.new(type='ShaderNodeBsdfGlass')
    node.inputs['Color'].default_value = (0.603827, 0.708376, 0.799103, 1)

    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    links = mat.node_tree.links
    links.new(node.outputs[0], node_output.inputs[0])
    return mat


def create_uv_sphere_material():
    # Create material
    scn = bpy.context.scene
    # Set cycles render engine if not selected
    if not scn.render.engine == 'CYCLES':
        scn.render.engine = 'CYCLES'

    mat = bpy.data.materials.new("Liquid Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # clear all nodes to start clean
    for node in nodes:
        nodes.remove(node)

    node = nodes.new(type='ShaderNodeBsdfGlass')
    node.inputs['Color'].default_value = (0.332452, 0.0168074, 0, 1)
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

    node = nodes.new(type='ShaderNodeBsdfDiffuse')
    node.inputs['Color'].default_value = [0.196, 0.196, 0.196, 1]

    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    links = mat.node_tree.links
    links.new(node.outputs[0], node_output.inputs[0])
    return mat


# Objects
def create_liquid_text(text_body):
    bpy.ops.object.text_add()
    text = bpy.context.object
    text.name = LIQUID_TEXT_OBJECT_NAME
    text.location = (0, 0, 0)
    text.rotation_euler = (math.pi / 2, 0, 0)
    text.data.body = text_body
    text.data.extrude = 0.1
    text.data.bevel_depth = 0.02
    text.data.offset = 0
    text.data.bevel_resolution = 3
    bpy.ops.object.convert(target='MESH')
    modifier = text.modifiers.new('remesh', type='REMESH')
    modifier.use_remove_disconnected = False
    modifier.octree_depth = 8
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.vertices_smooth(repeat=10)
    bpy.ops.object.editmode_toggle()
    liquid_material = create_liquid_text_material()
    if len(text.data.materials):
        text.data.materials[0] = liquid_material
    else:
        text.data.materials.append(liquid_material)
    create_liquid_text_canvas()
    return text


def create_uv_sphere():
    bpy.ops.mesh.primitive_uv_sphere_add(size=1, view_align=False, enter_editmode=False,
                                         location=(-0.5, 0, 0), layers=(
        True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
        False, False, False, False))
    uv_sphere = bpy.data.objects['Sphere']
    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.context.object.modifiers["Subsurf"].levels = 2
    bpy.ops.object.shade_smooth()
    bpy.ops.transform.resize(value=(0.1, 0.1, 0.1), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
    uv_sphere_material = create_uv_sphere_material()
    if len(uv_sphere.data.materials):
        uv_sphere.data.materials[0] = uv_sphere_material
    else:
        uv_sphere.data.materials.append(uv_sphere_material)
    create_liquid_text_brush()


def create_animation():
    bpy.context.scene.frame_end = 120
    bpy.context.scene.frame_current = 1
    bpy.ops.anim.keyframe_insert_menu(type='Location')
    bpy.context.scene.frame_current = 40
    bpy.ops.transform.translate(value=(5, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
    bpy.ops.anim.keyframe_insert_menu(type='Location')


def create_plane():
    bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=False,
                                     location=(0, 0, -0.1), layers=(
        True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
        False, False, False, False))
    plane = bpy.data.objects['Sphere']
    bpy.ops.transform.resize(value=(2, 2, 2), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
    plane_material = create_plane_material()
    if len(plane.data.materials):
        plane.data.materials[0] = plane_material
    else:
        plane.data.materials.append(plane_material)


# Operators
class ObjectLiquidText(bpy.types.Operator):
    """Object 3D Text"""
    bl_idname = "object.liquid_text"
    bl_label = "Liquid Text"
    bl_options = {'REGISTER', 'UNDO'}

    text_body = bpy.props.StringProperty(name="Text to Show",
                                         description="The text string you wish to be showed.",
                                         default="Water")

    def execute(self, context):
        create_liquid_text(self.text_body)
        create_uv_sphere()
        create_animation()
        create_plane()
        camera = bpy.data.objects["Camera"]
        camera.location = (0, -5, 2)
        look_at(camera, mathutils.Vector((0, -0, 0)))
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ObjectLiquidText)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ObjectLiquidText)
    bpy.types.VIEW3D_MT_object.remove(menu_func)



if __name__ == "__main__":
    register()