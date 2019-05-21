# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "SpringRTS Export Tiles",
    "author": "Samuel Nicholas",
    "blender": (2, 7, 4),
    "location": "",
    "description": "helper for creation and export of tiles",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

import bpy, os, re
from bpy_extras.io_utils import ExportHelper,ImportHelper
from mathutils import Vector
#from . import (
#    springrts_feature_presets
#)

#############
# Functions #
#############

def render_settings(scene):
    scene.display_settings.display_device = 'None'
    output = scene.render.image_settings
    output.file_format = 'PNG'
    output.color_depth = '16'
    output.color_mode = 'RGBA'
    return

#############
# Operators #
#############
class rts_tile_camera_setup(bpy.types.Operator):
    """ setup camera and render properties """
    bl_idname = "springrts.tile_camera_setup"
    bl_label = "Camera Setup"

    def execute(self, context):
        scn = context.scene
        props = context.scene.rts_tile_props
        render_settings(context.scene)

        try:
            roam = bpy.data.objects[props['roam']]
        except:
            print( "create roam mesh first" )
            return {'FINISHED'}

        try:
            cam = bpy.data.objects[props['camera']]
        except:
            bpy.ops.object.camera_add()
            cam = context.active_object
            cam.name = "rts_tile_cam"
            props['camera'] = cam.name

    
        cam.location = roam.location \
            + Vector( (0 ,0, roam.bound_box[ 1 ][2] + int( props[ 'square_size' ] )) )
        cam.rotation_euler = (0,0,0) 
        cam.data.name = "rts_tile_cam"
        cam.data.type='ORTHO'
        cam.data.ortho_scale = props['square_size'] * props['squares']
        cam.data.draw_size = (roam.bound_box[1][2] + 5) / cam.data.ortho_scale
        
        scn.camera = cam
        scn.render.resolution_x = cam.data.ortho_scale
        scn.render.resolution_y = cam.data.ortho_scale
        scn.render.resolution_percentage = 100
        return {'FINISHED'}
 

class rts_tile_roam_gen(bpy.types.Operator):
    """ Generate Roam Grid """
    bl_idname = "springrts.tile_roam_gen"
    bl_label = "Generate base mesh"

    def execute(self, context):
        props = context.scene.rts_tile_props
        try:
            props['squares']
        except:
            props['squares'] = 4

        try:
            props['square_size']
        except:
            props['square_size'] = 8
        
        divisions = props['squares'] + 1
        radius = props['squares'] * props['square_size'] / 2

        bpy.ops.mesh.primitive_grid_add(
                x_subdivisions = divisions,
                y_subdivisions = divisions,
                radius = radius,
                location=(0,0,0)
                )

        roam = context.active_object
        roam.name = "roam"
        props['roam'] = roam.name
        return {'FINISHED'}

class rts_tile_roam_export_height(bpy.types.Operator):
    """ export height data """
    bl_idname = "springrts.tile_roam_export_height"
    bl_label = "Export Height"

    def execute(self, context):
        props = context.scene.rts_tile_props

        render_settings(context.scene)

        try:
            props['floor']
        except:
            props['floor'] = -64
        floor = props['floor']
        
        try:
            props['ceiling']
        except:
            props['ceiling'] = 256
        ceiling = props['ceiling']

        bpy.ops.image.new("EXEC_DEFAULT",
                name="roam",
                width=props['squares'] + 1, 
                height=props['squares']+1,
                float=True)

        img = bpy.data.images['roam']
        img.colorspace_settings.name = 'Linear'
        img.use_view_as_render = True

        roam = bpy.data.objects[props['roam']]
        i = 0
        for v in roam.data.vertices:
            img.pixels[i] = (v.co[2] - floor) / float(ceiling - floor)
            img.pixels[i+1] = (v.co[2] - floor) / float(ceiling - floor)
            img.pixels[i+2] = (v.co[2] - floor) / float(ceiling - floor)
            i = i + 4
        
        img.save_render("height.png")
        return {'FINISHED'}

class rts_tile_roam_export_type(bpy.types.Operator):
    """ export type data """
    bl_idname = "springrts.tile_roam_export_type"
    bl_label = "Export type"

    def execute(self, context):
        props = context.scene.rts_tile_props
        return {'FINISHED'}

class rts_tile_roam_export_metal(bpy.types.Operator):
    """ export metal data """
    bl_idname = "springrts.tile_roam_export_metal"
    bl_label = "Export metal"

    def execute(self, context):
        props = context.scene.rts_tile_props
        return {'FINISHED'}

class rts_tile_roam_export_all(bpy.types.Operator):
    """ export all data """
    bl_idname = "springrts.tile_roam_export_all"
    bl_label = "Export all"

    def execute(self, context):
        props = context.scene.rts_tile_props
        return {'FINISHED'}

class rts_tile_geom_export(bpy.types.Operator):
    """ export geom to dae """
    bl_idname = "springrts.tile_geom_export"
    bl_label = "Export geometry"

    def execute(self, context):
        props = context.scene.rts_tile_props
        return {'FINISHED'}

#########################
# User Interface Panels #
#########################

class rts_tile_ui(bpy.types.Panel):
    """ Creates a Panel in the tools panel of the 3d view """
    bl_label = "Tile Helper"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = "SpringRTS"

    def draw(self, context):
        layout = self.layout
        props = context.scene.rts_tile_props


        box = layout.box()

        box = layout.box()
        row = box.row()
        row.label("Camera Tools")
        row.prop_search(props, "camera", context.scene, "objects", text="", icon='CAMERA_DATA')
        box.operator('springrts.tile_camera_setup', icon='CAMERA_DATA')

        box = layout.box()
        row = box.row()
        row.label("ROAM Tools")
        row.prop_search(props, "roam", context.scene, "objects", text="", icon='MESH_GRID')
        box.prop(props, 'square_size' )
        box.prop(props, 'squares' )
        box.prop(props, 'floor')
        box.prop(props, 'ceiling')
        box.operator('springrts.tile_roam_gen', icon='MESH_GRID')
        box.operator('springrts.tile_roam_export_height', icon='LIBRARY_DATA_DIRECT')
        box.operator('springrts.tile_roam_export_type', icon='LIBRARY_DATA_DIRECT')
        box.operator('springrts.tile_roam_export_metal', icon='LIBRARY_DATA_DIRECT')
        box.operator('springrts.tile_roam_export_all', icon='LIBRARY_DATA_DIRECT')

        box = layout.box()
        row = box.row()
        row.label("GEOM Tools")
        row.prop_search(props, "geom", bpy.data, "groups", text="")
        box.operator('springrts.tile_geom_export', icon='LIBRARY_DATA_DIRECT')

##########################
# Feature Property Group #
##########################

class rts_tile_props(bpy.types.PropertyGroup):

    square_size = bpy.props.IntProperty(default=8, min=8, subtype='PIXEL' )
    squares = bpy.props.IntProperty(default=4, min=4)
    floor = bpy.props.IntProperty(default = -64, subtype='PIXEL')
    ceiling = bpy.props.IntProperty(default = 256, subtype='PIXEL')
    roam = bpy.props.StringProperty()
    geom = bpy.props.StringProperty()
    camera = bpy.props.StringProperty()


################
# Registration #
################

def register():
    bpy.utils.register_module(__name__)

    bpy.types.Scene.rts_tile_props = bpy.props.PointerProperty(
        type=rts_tile_props)


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.rts_tile_props

if __name__ == "__main__":
    register()
