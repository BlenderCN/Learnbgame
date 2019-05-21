####### hqz exporter for blender V0.3.3 ##############
#
#   Damien Picard 2014

#	HQZ by M. Elizabeth Scott - http://scanlime.org/
#
# Usage:
# - install add-on to blender/2.6x/scripts/addons
# - or zip the folder and go to User Preferences -> Addons -> Install from File...
# - a wild panel appears ! in the View 3D Toolbar.
# - First, check 3D export for freestyle contour rendering.
#   This uses a line module to select lines to render from perspective camera
#   If left unchecked, the drawiwng will be 2D.
# - click "Prepare scene" (and switch to camera view)
# - change settings according to your gneeds
# - write materials to the materials list
# - if you need more materials, add sliders and corresponding stuff to the interface...
# - add mesh objects
# - in the object properties, select the material you wish to assign (default = 0)
# - change light color and intensity : set color value to 0 for white light or choose hue
#   alternatively you can also set hqz_spectral_light to 1 and choose a spectral range between 400 & 700 nm (Start/End)
# - click "Export"
# - that's pretty much it
# - if something doesn't work:
#      click "Prepare scene" again
#      check that you have at least one mesh object and one light object
#      PiOverFour on GitHub
#
#
#  ABOUT 2D MODE :
#
#   object vertices on the XY plane and extruding all edges to Z. this makes sure that only edges
#   on the XY plane are exported, and the normals are more predictable and controlable.
# - add spot or point light objects
# - rotate spots only around the Z axis
#
#
#  ABOUT 3D MODE :
#
# - spot lights are not currently supported in 3D mode. The maths are
#   too damn high.
#
###################################
#
# spectral color cheatsheet
#
#     400        450        500        550        600        650        700   nm -->
#    PURPLE      BLUE    CYAN    GREEN     YELLOW     ORANGE   RED
#
###################################
#
# TODO
# exception if folder not set
# FREESTYLE :
#             spotlights in cam space
#             ignore hidden lights
#
#             custom freestyle contour shaders?
#             option not to check light visibility? or reduce intensity?
#
#
###################################

bl_info = {
    "name": "HQZ exporter",
    "author": "Damien Picard",
    "version": (0, 4, 0),
    "blender": (2, 7, 0),
    "location": "View3D > Tool Shelf > HQZ Exporter",
    "description": "Export scene to HQZ renderer",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

import bpy
# import bpy_extras
from mathutils import Vector
from math import pi, floor, degrees
from bpy_extras.object_utils import world_to_camera_view
import os
import json


# UTILITY FUNCTIONS

def color_to_wavelength(color):
    '''Convert RGB color to a wavelength from 400 to 700nm (approximative).
    From https://fr.mathworks.com/matlabcentral/answers/17011-color-wave-length-and-hue#answer_22936'''
    if color.s == 0:
        return 0
    else:
        wavelength = 650 - color.h * 262.5
        if color.s == 1.0:
            return wavelength
        else:
            w_min = wavelength - 300 * (1-color.s)
            w_max = wavelength + 300 * (1-color.s)
            return [w_min, w_max]


def get_normal_from_points(sc, obj, p1, p2):
    '''Given two points, return their 2d normal vector in camera view.'''
    cam = sc.camera
    rp = sc.render.resolution_percentage / 100.0
    p1_cam = world_to_camera_view(sc, cam, p1)
    p2_cam = world_to_camera_view(sc, cam, p2)

    normal = (p2_cam - p1_cam).xy
    normal.x *= sc.render.resolution_x * rp
    normal.y *= sc.render.resolution_y * rp
    normal = normal.normalized()
    return normal


def get_object_rot(scene, object):
    '''Get 2d rotation for object in argument.'''
    p1 = object.matrix_world.to_translation()
    p2 = object.matrix_world.inverted()[2].xyz
    p2 *= -1
    normal = get_normal_from_points(scene, object, p1, p2)
    rot = degrees(Vector((1.0, 0.0)).angle_signed(normal))
    return rot


def write_batch_script(hqz_params, frame_range):
    """Write script for rendering multiple images"""
    platform = os.sys.platform
    shell_path = hqz_params.directory + 'batch'
    if 'win' in platform:
        shell_path += '.bat'
        shell_script = 'ECHO off\n\n'
        for frame in frame_range:
            if hqz_params.ignore:
                shell_script += (
                    'if exist "{image}.png" (\n'
                    '    ECHO "Ignoring existing file"\n'
                    ') else (\n'
                    ).format(
                        image=(hqz_params.directory + hqz_params.file
                               + '_' + str(frame).zfill(4)
                               )
                )
            shell_script += (
                '    ECHO "Rendering image {image}..."\n'
                '    "{engine_path}" "{image}.json" "{image}.png"\n'
            ).format(image=(hqz_params.directory + hqz_params.file
                            + '_' + str(frame).zfill(4)),
                     engine_path=hqz_params.engine_path + 'hqz')
            if hqz_params.ignore:
                shell_script += ')'
            shell_script += '\n'
    else:
        shell_path += '.sh'
        shell_script = '#!/bin/bash\n\n'
        for frame in frame_range:
            if hqz_params.ignore:
                shell_script += (
                    'if [ -f "{image}.png" ]\n'
                    'then\n'
                    '    echo "Ignoring existing file"\n'
                    'else\n'
                    ).format(
                        image=(hqz_params.directory + hqz_params.file
                               + '_' + str(frame).zfill(4)
                               )
                        )
            shell_script += (
                '    echo "Rendering image {image}..."\n'
                '    "{engine_path}" "{image}.json" "{image}.png"\n'
            ).format(image=(hqz_params.directory + hqz_params.file
                            + '_' + str(frame).zfill(4)),
                     engine_path=hqz_params.engine_path + 'hqz')
            if hqz_params.ignore:
                shell_script += 'fi'
            shell_script += '\n'

    file = open(shell_path, 'w')
    file.write(shell_script)
    file.close()


# START WRITING
def export(context):
    '''Create export data and write to file.'''
    sc = context.scene
    cam = sc.camera
    hqz_params = context.scene.hqz_parameters
    rp = sc.render.resolution_percentage / 100.0

    if hqz_params.animation:
        start_frame = sc.frame_start
        frame_range = range(sc.frame_start, sc.frame_end + 1)
    else:
        start_frame = sc.frame_current
        frame_range = (start_frame,)

    if hqz_params.batch:
        write_batch_script(hqz_params, frame_range)

    for frame in frame_range:
        print('Exporting frame', frame)

        export_data = {}

        if hqz_params.animation:
            sc.frame_set(frame)

        export_data['resolution'] = [
            int(sc.render.resolution_x * rp),
            int(sc.render.resolution_y * rp)]
        export_data['viewport'] = [
            0, 0,
            sc.render.resolution_x * rp,
            sc.render.resolution_y * rp]
        export_data['exposure'] = hqz_params.exposure
        export_data['gamma'] = hqz_params.gamma
        export_data['rays'] = hqz_params.rays
        if hqz_params.time != 0.0:
            export_data['timelimit'] = hqz_params.time
        export_data['seed'] = hqz_params.seed

        # LIGHTS
        export_data['lights'] = []
        for lamp in sc.objects:
            if lamp.type == 'LAMP' and lamp.is_visible(sc):
                lamp_obstacle = False

                if not lamp_obstacle:
                    light = []
                    use_spectral = lamp.data.hqz_lamp.use_spectral_light
                    spectral_start = lamp.data.hqz_lamp.spectral_start
                    spectral_end = lamp.data.hqz_lamp.spectral_end
                    wav = color_to_wavelength(lamp.data.color)
                    lamp_loc = lamp.matrix_world.to_translation()
                    x, y, z = world_to_camera_view(
                        sc, cam,
                        lamp_loc)
                    x *= sc.render.resolution_x * rp
                    y *= sc.render.resolution_y * rp

                    # Check that lamp is not behind camera
                    if z > 0:
                        y = sc.render.resolution_y * rp - y
                        light.append(lamp.data.energy)
                        light.append(x)
                        light.append(y)
                        if lamp.data.type == 'SPOT':
                            lamp_angle = get_object_rot(sc, lamp)
                            lamp_size = degrees(lamp.data.spot_size) / 2.0
                            lamp_min = (lamp_angle - lamp_size)
                            lamp_max = (lamp_angle + lamp_size)
                            light.append([lamp_min, lamp_max])
                        else:
                            light.append([0, 360])
                        light_start = (
                            lamp.data.hqz_lamp.light_start
                            * (sc.render.resolution_y * rp))
                        light_end = (
                            lamp.data.hqz_lamp.light_end
                            * (sc.render.resolution_y * rp))
                        light.append([light_start,
                                      light_end])
                        if lamp.data.type == 'SPOT':
                            light.append([lamp_min, lamp_max])
                        else:
                            light.append([0, 360])
                        if use_spectral:
                            light.append([spectral_start, spectral_end])
                        else:
                            light.append(wav)
                    export_data['lights'].append(light)

        export_data['objects'] = []

        # get Blender edge list
        edge_list = []
        for obj in sc.objects:
            if obj.type == 'MESH' and obj.is_visible(sc):
                mesh = bpy.data.meshes.new_from_object(
                    sc, obj, apply_modifiers=True, settings='PREVIEW')
                for edge in mesh.edges:
                    if edge.use_freestyle_mark:
                        continue
                    edgev = {}
                    vertices = list(edge.vertices)
                    edgev["material"] = obj.hqz_material_id
                    v1 = obj.matrix_world * mesh.vertices[vertices[0]].co
                    v2 = obj.matrix_world * mesh.vertices[vertices[1]].co
                    v1_cam = world_to_camera_view(
                        sc, cam, v1)
                    v2_cam = world_to_camera_view(
                        sc, cam, v2)
                    edgev["v1"] = v1_cam
                    edgev["v2"] = v2_cam
                    if hqz_params.normals_export:
                        v1_normal_offset = (
                            v1 + obj.matrix_world
                            * mesh.vertices[vertices[0]].normal
                            )
                        v2_normal_offset = (
                            v2 + obj.matrix_world
                            * mesh.vertices[vertices[1]].normal
                            )
                        n1 = get_normal_from_points(sc, obj, v1, v1_normal_offset)
                        n1_angle = degrees(Vector((1.0, 0.0)).angle_signed(n1))
                        n2 = get_normal_from_points(sc, obj, v2, v2_normal_offset)
                        n2_angle = degrees(n1.angle_signed(n2))
                        if hqz_params.normals_invert:
                            n1_angle += 180
                            n2_angle += 180
                        edgev["n1"] = n1_angle
                        edgev["n2"] = n2_angle

                    edge_list.append(edgev)
                bpy.data.meshes.remove(mesh)

        # OBJECTS
        for edge in edge_list:
            # if check_inside(
            #         context,
            #         edge["v1"].x * sc.render.resolution_x * rp,
            #         edge["v1"].y * sc.render.resolution_y * rp
            #         ):
            edge_data = []
            # MATERIAL
            edge_data.append(edge["material"])
            # VERT1 XPOS
            edge_data.append(
                edge["v1"].x
                * sc.render.resolution_x * rp)
            # VERT1 YPOS
            edge_data.append(
                (1 - edge["v1"].y) * sc.render.resolution_y * rp)
            # VERT1 NORMAL
            if hqz_params.normals_export:
                edge_data.append(edge["n1"])
            # VERT2 DELTA XPOS
            edge_data.append(
                (edge["v2"].x - edge["v1"].x)
                * sc.render.resolution_x * rp
            )
            # VERT2 DELTA YPOS
            edge_data.append(
                (edge["v1"].y - edge["v2"].y)
                * sc.render.resolution_y * rp
            )
            # VERT2 NORMAL
            if hqz_params.normals_export:
                edge_data.append(edge["n2"])

            export_data['objects'].append(edge_data)

        # Materials
        export_data['materials'] = []
        for material in hqz_params.materials:
            mat_data = []
            mat_data.append([material.diffuse, "d"])
            mat_data.append([material.transmission, "t"])
            mat_data.append([material.specular, "r"])
            export_data['materials'].append(mat_data)

        save_path = hqz_params.directory + hqz_params.file + '_' + str(frame).zfill(4) + '.json'

        d = os.path.dirname(save_path)
        os.makedirs(d, exist_ok=True)

        file = open(save_path, 'w')
        file.write(json.dumps(
            export_data, indent=None if hqz_params.debug else 2, sort_keys=True))
        file.close()


# Operators

class HQZExport(bpy.types.Operator):
    bl_label = "Export scene"
    bl_idname = "view3d.hqz_export"

    def execute(self, context):
        export(context)
        return {'FINISHED'}


class HQZMaterialAdd(bpy.types.Operator):
    bl_label = "Export scene"
    bl_idname = "material.hqz_add"

    def execute(self, context):
        mat = context.scene.hqz_parameters.materials.add()
        mat.name = "Material"
        return {'FINISHED'}


class HQZMaterialDelete(bpy.types.Operator):
    bl_label = "Export scene"
    bl_idname = "material.hqz_delete"

    index = bpy.props.IntProperty()

    def execute(self, context):
        context.scene.hqz_parameters.materials.remove(self.index)
        return {'FINISHED'}


# UI definitions

class HQZ_Materials_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item,
                  icon, active_data, active_propname, index):
        layout.prop(item, "name", text="",
                    emboss=False, translate=False, icon="MATERIAL")


class HQZMaterialPanel(bpy.types.Panel):
    bl_label = "HQZ Material"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        layout = self.layout

        sc = context.scene
        hqz_params = sc.hqz_parameters
        ob = context.object
        row = layout.row()
        row.template_list("HQZ_Materials_List", "",
                          hqz_params, "materials",
                          ob, "hqz_material_id", rows=1)
        col = row.column(align=True)
        col.operator("material.hqz_add", icon='ZOOMIN', text="")
        op = col.operator("material.hqz_delete", icon='ZOOMOUT', text="")
        op.index = ob.hqz_material_id

        layout.separator()
        col = layout.column(align=True)
        active_mat = ob.hqz_material_id
        col.prop(hqz_params.materials[active_mat], "diffuse")
        col.prop(hqz_params.materials[active_mat], "specular")
        col.prop(hqz_params.materials[active_mat], "transmission")


class HQZLampPanel(bpy.types.Panel):
    bl_label = "HQZ Lamp"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.lamp

    def draw(self, context):
        lamp = context.object.data
        layout = self.layout

        col = layout.column(align=True)
        col.prop(lamp.hqz_lamp, 'light_start')
        col.prop(lamp.hqz_lamp, 'light_end')

        col.separator()
        col.prop(lamp.hqz_lamp, 'use_spectral_light')
        sub = col.column(align=True)
        sub.active = lamp.hqz_lamp.use_spectral_light
        sub.prop(lamp.hqz_lamp, 'spectral_start')
        sub.prop(lamp.hqz_lamp, 'spectral_end')


class HQZExportPanel(bpy.types.Panel):
    bl_label = "HQZ Exporter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Export"
    bl_context = "objectmode"

    def draw(self, context):
        hqz_params = context.scene.hqz_parameters
        layout = self.layout

        col = layout.column(align=True)
        col.prop(hqz_params, "engine_path")
        col.prop(hqz_params, "directory")
        col.prop(hqz_params, "file")
        col.prop(hqz_params, "batch")
        col.prop(hqz_params, "ignore")

        col = layout.column()
        col = layout.column(align=True)
        col.prop(hqz_params, "debug")
        row = col.row(align=True)
        row.prop(hqz_params, "exposure")
        row.prop(hqz_params, "gamma")
        col.prop(hqz_params, "rays")
        row = col.row(align=True)
        row.prop(hqz_params, "seed")
        row.prop(hqz_params, "time")
        col.prop(hqz_params, "animation")

        row = col.row(align=True)
        row.prop(hqz_params, "normals_export")
        sub = row.column()
        sub.prop(hqz_params, "normals_invert")
        sub.active = hqz_params.normals_export
        # col.prop(hqz_params, "outside_limit")

        col = layout.column()
        col = layout.column()
        col.operator("view3d.hqz_export", text="Export scene")


class HQZLamp(bpy.types.PropertyGroup):
    light_start = bpy.props.FloatProperty(
        name='Light Start', min=0.0)
    light_end = bpy.props.FloatProperty(
        name='Light End', min=0.0)
    use_spectral_light = bpy.props.BoolProperty(
        name='Spectral Light')
    spectral_start = bpy.props.FloatProperty(
        name='Spectral Start', min=400.0, max=700.0,
        default=400.0, step=20)
    spectral_end = bpy.props.FloatProperty(
        name='Spectral End',  min=400.0, max=700.0,
        default=700.0, step=20)


class HQZMaterial(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty()
    diffuse = bpy.props.FloatProperty(name='Diffuse', min=0.0, max=1.0)
    specular = bpy.props.FloatProperty(name='Specular', min=0.0, max=1.0)
    transmission = bpy.props.FloatProperty(name='Transmission',
                                           min=0.0, max=1.0)


class HQZParameters(bpy.types.PropertyGroup):
    materials = bpy.props.CollectionProperty(type=HQZMaterial)
    engine_path = bpy.props.StringProperty(
        name="Engine path",
        subtype="FILE_PATH")
    directory = bpy.props.StringProperty(
        name="Export directory",
        subtype="DIR_PATH")
    file = bpy.props.StringProperty(
        name="File name")
    batch = bpy.props.BoolProperty(
        name="Export batch file",
        default=True)
    ignore = bpy.props.BoolProperty(
        name="Ignore existing file",
        default=False)

    exposure = bpy.props.FloatProperty(
        name="Exposure",
        default=0.5,
        min=0)
    gamma = bpy.props.FloatProperty(
        name="Gamma",
        default=2.2,
        min=0)
    rays = bpy.props.IntProperty(
        name="Number of rays",
        default=100000,
        min=0)
    seed = bpy.props.IntProperty(
        name="Seed",
        default=0,
        min=0)
    time = bpy.props.IntProperty(
        name="Max render time (0 for infinity)",
        default=0,
        min=0)
    animation = bpy.props.BoolProperty(
        name="Export animation",
        default=False)
    normals_export = bpy.props.BoolProperty(
        name="Export normals",
        default=True)
    normals_invert = bpy.props.BoolProperty(
        name="Invert normals",
        default=False)
    debug = bpy.props.BoolProperty(
        name="Debug",
        description="Remove all newlines to read with wireframe.html",
        default=False)
    # outside_limit = bpy.props.FloatProperty(
    #     name="Object outside view by (px)",
    #     description="Do not export invisible points. Use negative value to export all",
    #     default=-1.0)


def register():
    bpy.utils.register_class(HQZMaterial)
    bpy.utils.register_class(HQZLamp)
    bpy.utils.register_class(HQZParameters)
    bpy.types.Scene.hqz_parameters = bpy.props.PointerProperty(
        type=HQZParameters)
    bpy.types.Lamp.hqz_lamp = bpy.props.PointerProperty(type=HQZLamp)
    bpy.utils.register_class(HQZ_Materials_List)
    bpy.utils.register_class(HQZExport)
    bpy.utils.register_class(HQZMaterialPanel)
    bpy.utils.register_class(HQZLampPanel)
    bpy.utils.register_class(HQZExportPanel)
    bpy.utils.register_class(HQZMaterialAdd)
    bpy.utils.register_class(HQZMaterialDelete)
    bpy.types.Object.hqz_material_id = bpy.props.IntProperty(
        name='HQZ Material')


def unregister():
    bpy.utils.unregister_class(HQZParameters)
    del bpy.types.Scene.hqz_parameters
    bpy.utils.unregister_class(HQZ_Materials_List)
    bpy.utils.unregister_class(HQZMaterial)
    bpy.utils.unregister_class(HQZLamp)
    bpy.utils.unregister_class(HQZExport)
    bpy.utils.unregister_class(HQZMaterialPanel)
    bpy.utils.unregister_class(HQZLampPanel)
    bpy.utils.unregister_class(HQZExportPanel)
    bpy.utils.unregister_class(HQZMaterialAdd)
    bpy.utils.unregister_class(HQZMaterialDelete)
    del bpy.types.Scene.hqz_material_id
    del bpy.types.Scene.hqz_lamp


if __name__ == "__main__":
    register()
