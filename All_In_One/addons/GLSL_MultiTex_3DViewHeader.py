######################################################################################################
# A simple add-on that show a "GLSL/Multitexture" button the 3D View header                          #
# Actualy uncommented (see further version)                                                          #
# Author: Lapineige                                                                                  #
# License: GPL v3                                                                                    #
######################################################################################################

############# Add-on description (use by Blender)

bl_info = {
    "name": "GLSL/Multitexture Menu on View 3D header",
    "description": 'Add th option "Lock Camera to View" on the View 3D Header',
    "author": "Lapineige",
    "version": (1, 0),
    "blender": (2, 7, 2),
    "location": "View3D > Header > GLSL/Multitexture",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "http://www.le-terrier-de-lapineige.over-blog.com",
    "category": "Learnbgame"
}

##############

import bpy

# Define the UI items to add

def view3d_GLSL_shading(self, context):
    layout = self.layout
    if context.scene.render.engine == 'BLENDER_RENDER':
        layout.prop(context.scene.game_settings, "material_mode", text="")


# Fonction called by BLender on add-on start
def register():
    bpy.types.VIEW3D_HT_header.append(view3d_GLSL_shading) # Add UI items to 3D View header

# Fonction called by BLender on add-on unistall
def unregister():
    bpy.types.VIEW3D_HT_header.remove(view3d_GLSL_shading)

if __name__ == "__main__":
    register()
