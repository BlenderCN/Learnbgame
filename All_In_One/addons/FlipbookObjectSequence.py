bl_info = {
        'name': 'FlipbookSelectedObjects"',
        'author': 'bay raitt',
        'version': (0, 1),
        'blender': (2, 80, 0),
        'category': 'Animation',
        'location': 'Object > Animation > Flipbook Selected Objects',
        'wiki_url': ''}


import bpy
from math import *
from mathutils import *


                
class BR_OT_flipbook_selected_objects(bpy.types.Operator):
    """Flipbook Selected Objects"""
    bl_idname = "view3d.flipbook_selected_objects"
    bl_label = "Flipbook Selected Objects"


    def execute(self, context):                
        hold = 2
        fBuff = 0
        
        currentStart =  bpy.context.scene.frame_current
        currentF =  bpy.context.scene.frame_current


        # get objects selected in the viewport
        viewport_selection = bpy.context.selected_objects

        # get export objects
        obj_list = viewport_selection
#        if self.use_selection_setting == False:
        obj_list = [i for i in bpy.context.scene.objects]

        # deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        for myobj in obj_list:
            myobj.select_set(state=True)
            bpy.context.view_layer.objects.active = myobj


            # Clear all previous animation data
            myobj.animation_data_clear()
            
            if len(obj_list) > 0:
                for i in range(len(obj_list)):
                    if (myobj == obj_list[i - 1]):

                        fBuff = currentStart
                        
                        # Set frame 
#                        bpy.context.scene.frame_set(fBuff)

                        # Set current scale
                        myobj.scale.x = 1.0
                        myobj.scale.y = 1.0
                        myobj.scale.z = 1.0

                        # Insert new keyframe for scale
                        myobj.keyframe_insert(data_path="scale", frame = fBuff)
#                        myobj.keyframe_insert(data_path="hide_render")
#                        myobj.keyframe_insert(data_path="hide")

                        fBuff = currentStart + hold

                        # Insert new keyframe for scale
                        myobj.keyframe_insert(data_path="scale", frame = fBuff)
                        
                        fBuff = currentStart + hold + 1

                        # Set current scale
                        myobj.scale.x = 0.001
                        myobj.scale.y = 0.001
                        myobj.scale.z = 0.001

                        # Insert new keyframe for scale
                        myobj.keyframe_insert(data_path="scale", frame = fBuff)

                        fBuff = currentStart - 1
                        
                        # Insert new keyframe for scale
                        myobj.keyframe_insert(data_path="scale", frame = fBuff)
                        
                        fcurves = myobj.animation_data.action.fcurves
                        for fcurve in fcurves:
                            for kf in fcurve.keyframe_points:
                                kf.interpolation = 'CONSTANT'

                        
                currentStart =  currentStart + hold + 1              
            myobj.select_set(state=False)
            bpy.context.scene.frame_set(currentF)
        return {'FINISHED'}

def menu_draw(self, context):
    self.layout.operator(BR_OT_flipbook_selected_objects.bl_idname)



def register():
    bpy.utils.register_class(BR_OT_flipbook_selected_objects)
    bpy.types.VIEW3D_MT_object_animation.prepend(menu_draw)  

def unregister():
    bpy.utils.unregister_class(BR_OT_flipbook_selected_objects)
    bpy.types.VIEW3D_MT_object_animation.remove(menu_draw)  

    if __name__ != "__main__":
        bpy.types.VIEW3D_MT_object_animation.remove(menu_draw)

if __name__ == "__main__":
    register()


