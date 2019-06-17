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
    "name": "oenvoyage Toolset",
    "author": "Olivier Amrein",
    "version": (0, 3, 0),
    "blender": (2, 79),
    "location": "Everywhere !!!",
    "description": "A collection of tools and settings to improve productivity (based on Amaranth)",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Scene"}


import sys, os, bpy
sys.path.append(os.path.dirname(__file__)) 
from bpy.types import Operator, AddonPreferences, Panel, Menu
from bpy.props import BoolProperty
from oenvoyage_utils import *

# Preferences
class OenvoyageToolsetPreferences(AddonPreferences):
    bl_idname = __name__
    use_render_estimate = BoolProperty(
            name="Estimate Render time",
            description="show the panel with render estimation",
            default=True,
            )

    def draw(self, context):
        layout = self.layout

        layout.label(
            text="Here you can enable or disable specific tools, "
                 "in case they interfere with others or are just plain annoying")

        split = layout.split(percentage=0.25)

        col = split.column()
        sub = col.column(align=True)
        sub.label(text="Render Options", icon="RENDER_STILL")
        sub.prop(self, "use_render_estimate")

# Properties
def init_properties():

    scene = bpy.types.Scene
    
    scene.average_rendertime = bpy.props.FloatProperty(min=0, default=5, max = 200)

def clear_properties():
    props = (
        "use_render_estimate",
    )
    
    wm = bpy.context.window_manager
    for p in props:
        if p in wm:
            del wm[p]

class OBJECT_MT_multioptions_menu(bpy.types.Menu):
    bl_label = "MultiOptions Menu"
    bl_idname = "OBJECT_MT_multioptions_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("wm.open_mainfile")
        layout.operator("wm.save_as_mainfile")

# PIE menu

class VIEW3D_PIE_oenvoyage(Menu):
    bl_label = "Oenvoyage PIE"

    def draw(self, context):
        layout = self.layout
        #mode = context.object.mode
        pie = layout.menu_pie()
        pie.operator("view3d.manipulator_set", icon='MAN_TRANS', text="Translate").type = 'TRANSLATE'
        pie.operator("view3d.view_selected")
        pie.operator("view3d.wm.call_menu")
        pie.operator("view3d.render_playblast", icon='RENDER_ANIMATION')
        pie.prop(context.space_data, "show_manipulator")

# make a quick opengl rendering by enabling Show Only Render is display + making ogl render

class render_PlayBlast(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "view3d.render_playblast"
    bl_label = "OpenGL playblast"

    @classmethod
    def poll(cls, context):
        return 1

    def execute(self, context):
        mainfile = bpy.data.filepath
        filename = os.path.splitext(os.path.basename(mainfile))[0]
        bpy.ops.wm.save_mainfile()        

        render = context.scene.render
        space = bpy.context.space_data
        rsettings = render.image_settings
        # pre preview
        #change settings and render OGL
        render.use_stamp = True
        space.show_only_render = True
        render.resolution_percentage = 50

        render.filepath = "//playblasts/"+filename
        render.image_settings.file_format = "H264" 
        render.ffmpeg.format = 'MPEG4'
        render.ffmpeg.codec = 'H264'
        
        bpy.ops.render.opengl(animation = True)

        # post preview and reset settings to original
        bpy.ops.render.play_rendered_anim()
        
        bpy.ops.wm.open_mainfile(filepath=mainfile)
        self.report({'INFO'},"OpenGL playblast preview finished")

        return {'FINISHED'}
    

# FEATURE: Select camera target (TrackTo like constraints)
class SelectCameraTarget(bpy.types.Operator):
    bl_idname = "view3d.select_camera_target"
    bl_label = "Select Camera Target"

    @classmethod
    def poll(cls, context):
        return context.active_object.type == 'CAMERA'

    def execute(self, context):
        if context.active_object.constraints:
            for const in context.active_object.constraints:
                print(const.type)
                if const.type in ('DAMPED_TRACK','LOCKED_TRACK','TRACK_TO'):
                    if const.target:
                        bpy.ops.object.select_all()
                        const.target.select = True
                        bpy.context.scene.objects.active = const.target
                    else:
                        self.report({'WARNING'},"No target for constraint found")
        else:
            self.report({'WARNING'},"No constraints found")

        return {'FINISHED'}


# FEATURE: Additional options in W special key
def special_key_options(self, context):

    obj = context.active_object
    scene = context.scene
    layout = self.layout
    
    if obj.type =='CAMERA':
        layout.separator()
        layout.operator("view3d.select_camera_target", icon="CONSTRAINT")   

    layout.operator("view3d.render_playblast",icon='RENDER_ANIMATION')   


# // FEATURE: Additional options in W


# FEATURE: Motion paths buttons in W special key
def motion_path_buttons(self, context):

    obj = context.active_object
    scene = context.scene

    self.layout.separator()
    if obj.motion_path:
        self.layout.operator("object.paths_update", text="Update Object Paths")
        self.layout.operator("object.paths_clear", text="Clear Object Paths")
    else:
        self.layout.operator("object.paths_calculate", text="Calculate Object Paths")
# // FEATURE: Motion paths buttons in W

addon_keymaps = []

def register():

    init_properties()

    #bpy.utils.register_module(__name__)

    bpy.utils.register_class(OenvoyageToolsetPreferences)

    # register Operators
    bpy.utils.register_class(SelectCameraTarget)
    bpy.utils.register_class(render_PlayBlast)

    # register menus
    bpy.utils.register_class(VIEW3D_PIE_oenvoyage)
    bpy.utils.register_class(OBJECT_MT_multioptions_menu)

    
    # UI: Register the panels
    bpy.types.RENDER_PT_render.append(estimate_render_animation_time)
    bpy.types.VIEW3D_MT_object_specials.append(special_key_options)
    bpy.types.VIEW3D_MT_object_specials.append(motion_path_buttons)
    
    wm = bpy.context.window_manager

    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='Object Non-modal')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'Q', 'PRESS', shift=True)
        kmi.properties.name = 'VIEW3D_PIE_oenvoyage'

        
        addon_keymaps.append(km)

def unregister():

    #bpy.utils.unregister_module(__name__)

    bpy.utils.unregister_class(OenvoyageToolsetPreferences)

    # unregister Operators
    bpy.utils.unregister_class(SelectCameraTarget)
    bpy.utils.unregister_class(render_PlayBlast)

    # runegister menus
    bpy.utils.unregister_class(VIEW3D_PIE_oenvoyage)
    bpy.utils.unregister_class(OBJECT_MT_multioptions_menu)


    # UI: Unregister the panels
    bpy.types.RENDER_PT_render.remove(estimate_render_animation_time)
    bpy.types.VIEW3D_MT_object_specials.remove(special_key_options)
    bpy.types.VIEW3D_MT_object_specials.remove(motion_path_buttons)
    
    clear_properties()

if __name__ == "__main__":
    print("LOADING SPLIT ADDON")
    register()