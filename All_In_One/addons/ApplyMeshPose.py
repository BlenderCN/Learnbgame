bl_info = {
        'name': 'ApplyMeshPose',
        'author': 'bay raitt',
        'version': (0, 1),
        'blender': (2, 80, 0),
        'category': 'Pose',
        'location': 'W > Appy current pose as rest for armature and all parented objects',
        'wiki_url': ''}

import bpy


def main(context):
    obj = bpy.context.object    
    if obj.type == 'ARMATURE':
        armt = obj.data
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')
        ch = [child for child in obj.children if child.type == 'MESH' and child.find_armature()]
        for ob in ch:
            bpy.ops.object.select_all(action='DESELECT')
            ob.select_set(state=True)
            bpy.context.view_layer.objects.active = ob
            context.scene.update()
            for mod in [m for m in ob.modifiers if m.type == 'ARMATURE']:
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
            ob.select_set(state=False)
        obj.select_set(state=True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bpy.ops.pose.armature_apply()
        # bpy.ops.poselib.apply_pose(pose_index=-2)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')
        for ob in ch:
            ob.select_set(state=True)
            bpy.context.view_layer.objects.active = ob
            ob.modifiers.new(name = 'Skeleton', type = 'ARMATURE')
            ob.modifiers['Skeleton'].object = obj
        bpy.ops.object.mode_set(mode='SCULPT', toggle=False)

                    
class BR_OT_apply_mesh_pose(bpy.types.Operator):
    """Set current pose and shape as rest bind shape"""
    bl_idname = "view3d.apply_mesh_pose"
    bl_label = "Apply Pose as Rest Pose with Mesh "

    def execute(self, context):
        main(context)
        return {'FINISHED'}
 

def menu_draw(self, context):
    self.layout.operator(BR_OT_apply_mesh_pose.bl_idname)



def register():
    bpy.utils.register_class(BR_OT_apply_mesh_pose)
    bpy.types.VIEW3D_MT_pose_apply.prepend(menu_draw)  

def unregister():
    bpy.utils.unregister_class(BR_OT_apply_mesh_pose)
    bpy.types.VIEW3D_MT_pose_apply.remove(menu_draw)  

    if __name__ != "__main__":
        bpy.types.VIEW3D_MT_pose_appy.remove(menu_draw)

if __name__ == "__main__":
    register()
