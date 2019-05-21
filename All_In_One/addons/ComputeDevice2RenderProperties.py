######################################################################################################
# A simple add-on that show on the render properties an option to choose the GC to use               #
# Actualy uncommented (see further version)                                                          #
# Author: Lapineige                                                                                  #
# License: GPL v3                                                                                    #
######################################################################################################


############# Add-on description (use by Blender)

bl_info = {
    "name": "Compute Device on Render properties panel",
    "description": 'Allow to choose the compute device on the render properties panel',
    "author": "Lapineige",
    "version": (1, 0),
    "blender": (2, 71, 0),
    "location": "Properties > Render > Render (panel)",
    "warning": "",
    "wiki_url": "http://www.le-terrier-de-lapineige.over-blog.com",
    "tracker_url": "http://blenderlounge.fr/forum/viewtopic.php?f=18&p=7126#p7126",
    "category": "Learnbgame"
}

##############

import bpy

# Define the UI items to add

def ChooseCG(self, context):
    if bpy.context.scene.render.engine == 'CYCLES':
        system = context.user_preferences.system
        layout = self.layout
        if hasattr(system, "compute_device_type"):
            if system.compute_device_type == 'CUDA':
                row = layout.split(percentage=0.332)
                row.label(text="CG Device:")
                row.prop(system, "compute_device", text="")

# Fonction called by BLender on add-on start
def register():
    bpy.types.RENDER_PT_render.append(ChooseCG) # Add UI items to 3D View header

# Fonction called by BLender on add-on unistall
def unregister():
    bpy.types.RENDER_PT_render.remove(ChooseCG)

if __name__ == "__main__":
    register()
    





