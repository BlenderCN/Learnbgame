# io_import_minecraft

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

# <pep8 compliant>

bl_info = {
    "name": "Import Minecraft",
    "description": "Importer for viewing Minecraft world/region data",
    "author": "Adam Crossan (acro)",
    "version": (1,0),
    "blender": (2, 6, 0),
    "api": 41226,
    "location": "File > Import > Minecraft",
    "warning": '', # used for warning icon and text in addons panel
    "category": "Learnbgame"
}

#import os
#import bpy
#CHECK OUT API Pages for these! ....
#from bpy.props import CollectionProperty, StringProperty, BoolProperty
#from io_utils import ImportHelper, ExportHelper
# To support reload properly, try to access a package var, if it's there, reload everything
if "bpy" in locals():
    import imp
    if "mineregion" in locals():
        imp.reload(mineregion)

import bpy
from bpy.props import StringProperty, FloatProperty, IntProperty, BoolProperty, EnumProperty
from . import mineregion


#Menu 'button' for the import menu (which calls the world selector)...

class MinecraftWorldSelector(bpy.types.Operator):
    """An operator defining a dialogue for choosing one on-disk Minecraft world to load.
This supplants the need to call the file selector, since Minecraft worlds require
a given folder structure and multiple files and cannot be selected singly."""

    bl_idname = "mcraft.selectworld"
    bl_label = "Select Minecraft World"
    
    #bl_space_type = "PROPERTIES"
    #Possible placements for these:
    bl_region_type = "WINDOW"

    mcLoadAtCursor = bpy.props.BoolProperty(name='Load at 3D Cursor', description='Loads chunks around relative position of cursor in 3D View from (0,0,0), instead of loading saved player position.', default=False)

    #TODO: Make this much more intuitive for the user!
    mcLoadRadius = bpy.props.IntProperty(name='Load Radius', description="""The half-width of the load range around load-pos.
e.g, 4 will load 9x9 chunks around the load centre
WARNING! Above 10, this gets slow and eats LOTS of memory!""", min=1, max=50, step=1, default=5, subtype='UNSIGNED')    #soft_min, soft_max?
    #optimiser algorithms..

    mcOmitStone = bpy.props.BoolProperty(name='Omit Stone', description='Check this to not load stone blocks (block id 1). Speeds up loading and viewport massively', default=True)

    mcShowSlimeSpawns = bpy.props.BoolProperty(name='Slime Spawns', description='Check this to display chunk outlines which, based on your world seed, indicate where slimes will spawn', default=False)
    
    # omit Dirt toggle option.
    
    # height-limit option (only load down to a specific height) -- could be semi-dynamic and delve deeper when air value for the 
    # column in question turns out to be lower than the loading threshold anyway.
    
    #surfaceOnly ==> only load surface, discard underground areas. Doesn't count for nether.
    
    # Load Nether (only available if selected world has nether)
    # need to poll for whether selected world has nether??
    
    #When specifying a property of type EnumProperty, ensure you call the constructing method correctly.
    #Note that items is a set of (identifier, value, description) triples, and default is a string unless you switch on options=ENUM_FLAG in which case make default a set of 1 string.
    #Need a better way to handle this variable: (possibly set it as a screen property)
    
    from . import mineregion
    wlist = mineregion.getWorldSelectList()
    if wlist is not None:
        mcWorldSelectList = bpy.props.EnumProperty(items=wlist[::-1], name="World", description="Which Minecraft save should be loaded?")	#default='0', 
    else:
        mcWorldSelectList = bpy.props.EnumProperty(items=[], name="World", description="Which Minecraft save should be loaded?")

    #my_worldlist = bpy.props.EnumProperty(items=[('0', "A", "The A'th item"), ('1', 'B', "Bth item"), ('2', 'C', "Cth item"), ('3', 'D', "dth item"), ('4', 'E', 'Eth item')][::-1], default='2', name="World", description="Which Minecraft save should be loaded?")


    def execute(self, context): 
        print("I got value: " + str(self.mcWorldSelectList))
        #print(self.my_float)
        self.report({"INFO"}, "I got value: " + str(self.mcWorldSelectList))
        
        #thread.sleep(30)
        #self.report({"WARNING"}, "Foo!")
        
        #from . import mineregion
        #toggleOptions = { 'loadSlime': mcShowSlimeSpawns }
        opts = {"omitstone": self.mcOmitStone, "showslimes": self.mcShowSlimeSpawns, "atcursor": self.mcLoadAtCursor}
        mineregion.readMinecraftWorld(str(self.mcWorldSelectList), self.mcLoadRadius, opts)
        for s in bpy.context.area.spaces: # iterate all space in the active area
            if s.type == "VIEW_3D": # check if space is a 3d-view
                space = s
                space.clip_end = 10000.0
        #run minecraftLoadChunks
        
        return {'FINISHED'}


    def invoke(self, context, event):
        context.window_manager.invoke_props_dialog(self, width=350,height=250)
        return {'RUNNING_MODAL'}


    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Choose import options")

        row = col.row()
        row.prop(self, "mcLoadAtCursor")
        row.prop(self, "mcOmitStone")
        
        row = col.row()
        
        row.prop(self, "mcShowSlimeSpawns")
        
        row.prop(self, "mcLoadRadius")

        row = layout.row()
        row.prop(self, "mcWorldSelectList")
        col = layout.column()


class MineMenuItemOperator(bpy.types.Operator):
    bl_idname = "mcraft.launchselector"
    bl_label = "Needs label but label not used"

    def execute(self, context):
        bpy.ops.mcraft.selectworld('INVOKE_DEFAULT')
        return {'FINISHED'}

bpy.utils.register_class(MinecraftWorldSelector)
bpy.utils.register_class(MineMenuItemOperator)

def mcraft_filemenu_func(self, context):
    self.layout.operator("mcraft.launchselector", text="Minecraft (.region)", icon='MESH_CUBE')


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(mcraft_filemenu_func)	# adds the operator action func to the filemenu

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(mcraft_filemenu_func)	# removes the operator action func from the filemenu

if __name__ == "__main__":
    register()