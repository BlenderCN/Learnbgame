######################################################################################################
# A simple add-on that show a "Lock Camera To View" button on the 3D View header                     #
# Actualy uncommented (see further version)                                                          #
# Author: Lapineige                                                                                  #
# License: GPL v3                                                                                    #
######################################################################################################

############# Add-on description (use by Blender)

bl_info = {
    "name": "LockCam2View on View 3D header",
    "description": 'Add th option "Lock Camera to View" on the View 3D Header',
    "author": "Lapineige",
    "version": (2, 0),
    "blender": (2, 71, 0),
    "location": "View3D > Header > Lock Camera to View",
    "warning": "",
    "wiki_url": "http://www.le-terrier-de-lapineige.over-blog.com",
    "tracker_url": "http://blenderlounge.fr/forum/viewtopic.php?f=26&p=6724#p6724",
    "category": "Learnbgame"
}

##############

import bpy

# Define the UI items to add

def view3d_lockCamera(self, context):
    layout = self.layout
    if context.space_data.lock_camera:
        layout.prop(context.space_data, "lock_camera", icon = "LOCKED") # icon = "CAMERA_DATA" if you prefer a camera icon
    else:
        layout.prop(context.space_data, "lock_camera", icon = "UNLOCKED")


# Fonction called by BLender on add-on start
def register():
    bpy.types.VIEW3D_HT_header.append(view3d_lockCamera) # Add UI items to 3D View header

# Fonction called by BLender on add-on unistall
def unregister():
    bpy.types.VIEW3D_HT_header.remove(view3d_lockCamera)

if __name__ == "__main__":
    register()
    


