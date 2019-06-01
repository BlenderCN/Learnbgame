import bpy,os
import math
"""TODO: enable AnimaAll"""
import addon_utils
#addon_utils.enable("")


from . import load_mesh

class AnimatePhysika(bpy.types.Operator):
    bl_idname = "physika_operators.animate"
    bl_label = "Animate Physika Simulation"
    bl_description = "Display Physika Simulation Results"
    bl_options = {'REGISTER'}




    
    def execute(self, context):
        scene = context.scene
        obj = scene.objects.active
        para_props = obj.physika.physika_para
        
        ver_num = len(context.object.data.vertices)
        obj_name = scene.objects.active.name
        mesh_loader = load_mesh.MeshLoader(para_props.physika_discrete, obj_name, ver_num);

        obj.select = True
        bpy.data.window_managers["WinMan"].key_points = True


        total_time = para_props.common.total_time
        frame_rate = para_props.common.frame_rate
        frames = int(math.ceil(total_time * frame_rate))
        
        method = para_props.physika_discrete
        ext = eval('para_props.' + method + '.blender.input_format')
        context.scene.frame_end = frames
        context.scene.render.fps = frame_rate
        for frame_id in range(frames):
            scene.frame_set(frame_id)
            
            mesh_loader.import_frame_mesh(frame_id, ext)
            bpy.ops.anim.insert_keyframe_animall()

            
            

        return {"FINISHED"}


def register():
    bpy.utils.register_class(AnimatePhysika)

def unregister():
    bpy.utils.unregister_class(AnimatePhysika)

