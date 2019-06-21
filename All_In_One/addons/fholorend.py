bl_info = {
    "name": "FHologramRenderer",
    "description": "Renders 4 side hologram animation of selected object and camera as front view",
    "author": "Fma",
    "version": (1, 0),
    "blender": (2, 76, 0),
    "location": "Render > 2 > Mesh",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"
                "Scripts/My_Script",
    "category": "Learnbgame",
}

import bpy
from mathutils import *
from math import *

class FHologramRenderer(bpy.types.Operator):
    """F-Hologram Video Frame Renderer"""      # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "render.fholorend"        # unique identifier for buttons and menu items to reference.
    bl_label = "F Hologram Frame Render"         # display name in the interface.
    bl_options = {'REGISTER'}

    def execute(self, context):        # execute() is called by blender when running the operator.

        # The original script
        scene = context.scene

        cam = None
        mesh = None
        # get selected meshed and cameras
        for obj in context.selected_objects:
            if obj.select:
                if obj.type == 'CAMERA':
                    cam = obj
                elif obj.type == 'MESH':
                    mesh = obj

        if cam is None or mesh is None:
            print('Cam or Mesh not selected')
            return {'CANCELLED'}

        center = mesh.location # set mesh as center
        dx, dy, dz = cam.location - center # get distance vector

        rad90 = radians(90)

        cam_count = 4
        bpy.context.scene.camera = cam # set camera

        frame_curr_org = scene.frame_current # store current frame
        # generate frames with respect to user frame settings (start step etc)
        for frame in range(scene.frame_start, scene.frame_end+1, scene.frame_step):
            scene.frame_current = frame
            for step in range(0, cam_count):
                out_path = '/tmp/holo/c%d/%04d.jpg' % (step+1, frame)
                bpy.data.scenes["Scene"].render.filepath = out_path
                bpy.ops.render.render( write_still=True )

                # rotate camera locations in cw
                tmp = -dx
                dx = dy
                dy = tmp
                cam.location = center + Vector([dx, dy, dz])

                # rotate camera 90 degs on z-axis
                cam.rotation_euler.z -= rad90
        scene.frame_current = frame_curr_org # restore current frame

        return {'FINISHED'}            # this lets blender know the operator finished successfully.


def register():
    bpy.utils.register_class(FHologramRenderer)


def unregister():
    bpy.utils.unregister_class(FHologramRenderer)


# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == "__main__":
    register()
