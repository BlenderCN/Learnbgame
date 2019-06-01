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
    "name": "QuickPrefs",
    "author": "Sean Olson",
    "version": (1,0),
    "blender": (2, 5, 8),
    "api": 37702,
    "location": "3DView->Properties Panel (N-Key)",
    "description": "Add often changed User Preference options to Properties panel",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

import bpy

##########################################
####### General Functions ################
##########################################
def values(scn):
    bpy.types.Scene.lights = bpy.props.BoolProperty(name='Lights', default=False)
    bpy.types.Scene.interface = bpy.props.BoolProperty(name='Interface', default=False)

def opengl_lamp_buttons(column, lamp):
    split = column.split(percentage=0.1)

    split.prop(lamp, "use", text="", icon='OUTLINER_OB_LAMP' if lamp.use else 'LAMP_DATA')

    col = split.column()
    col.active = lamp.use
    row = col.row()
    row.label(text="Diffuse:")
    row.prop(lamp, "diffuse_color", text="")
    row = col.row()
    row.label(text="Specular:")
    row.prop(lamp, "specular_color", text="")

    col = split.column()
    col.active = lamp.use
    col.prop(lamp, "direction", text="")


    
##########################################
####### GUI and registration #############
##########################################
#Panel for tools
class PANEL(bpy.types.Panel):
    bl_label = 'Quick Preferences'
    bl_space_type = 'VIEW_3D'
    bl_context = "mesh_edit"
    bl_region_type = 'UI'
    
    def draw(self, context):        
        scn = bpy.context.scene
        system = context.user_preferences.system
        inputs = context.user_preferences.inputs
        edit = context.user_preferences.edit
        layout = self.layout
        split = layout.split()

        #lights
        box = layout.box().column(align=False)
        box.prop(scn,'lights')
        if scn.lights:

            split = box.split(percentage=0.1)
            split.label()
            split.label(text="Colors:")
            split.label(text="Direction:")

            lamp = system.solid_lights[0]
            opengl_lamp_buttons(box, lamp)

            lamp = system.solid_lights[1]
            opengl_lamp_buttons(box, lamp)

            lamp = system.solid_lights[2]
            opengl_lamp_buttons(box, lamp)

            box.separator()
            box.separator()
            box.separator()
           
        box = layout.box().column(align=True)
        box.prop(scn,'interface')
        if scn.interface:
            #Select with
            boxrow=box.row()
            boxrow.label(text="Select With:")
            boxrow=box.row()
            boxrow.prop(inputs, "select_mouse", expand=True)

            #Orbit
            boxrow=box.row()
            boxrow.label(text="Orbit Style:")
            boxrow=box.row()
            boxrow.prop(inputs, "view_rotate_method", expand=True)
        
            #continuous grab
            boxrow=box.row()
            boxrow.prop(inputs, "use_mouse_continuous")

            #Color Picker
            boxrow=box.row()
            boxrow.label(text="Color Picker Type")
            boxrow=box.row()
            boxrow.row().prop(system, "color_picker_type", text="")

            #Align To
            boxrow=box.row()
            boxrow.label(text="Align New Objects To:")
            boxrow=box.row()
            boxrow.prop(edit, "object_align", text="")



              
##########################################
####### Regitration Functions ################
##########################################
def register():
    bpy.utils.register_class(PANEL)
    values(bpy.context.scene)
    
# unregistering and removing menus
def unregister():
    bpy.utils.register_class(PANEL)


if __name__ == "__main__":
    register()
    
