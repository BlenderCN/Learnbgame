import bpy
from mathutils import Vector 

def rescale_action(rig, action):
    axes = [0, 1, 2]
    for axis in axes:
        scale_factor = rig.scale[axis]
        # get all the coord points that are locs
        cos = [kp.co for f in action.fcurves if f.array_index == axis and f.data_path.endswith('location') for kp in f.keyframe_points ]
        for co in cos:
            co[1] *= scale_factor

def rescale_rig(rig):
    # if it's a global scale factor add it to the settings.
    if rig.scale.x == rig.scale.y and rig.scale.y == rig.scale.z and rig.scale.y == rig.scale.z:
        if 'bvh_import_settings' in rig.data.keys():
            imp_scale = rig.data['_RNA_UI']["bvh_import_settings"].to_dict().setdefault("global_scale", 1.0)
            rig.data['_RNA_UI']["bvh_import_settings"]['global_scale'] = imp_scale * rig.scale.x
    # apply the scale


class RescaleRigAnimation(bpy.types.Operator):
    """Apply scale to rig and actions"""
    bl_idname = "mocap_madness.rescale"
    bl_label = "Rescale Animation"

    @classmethod
    def poll(cls, context):
        # has to be an armature
        ob = context.active_object
        if ob is None or not ob.type.startswith('ARMATURE'):
            return False
        if (ob.scale - Vector((1,1,1))).length < 0.0000001:
            return False
        return hasattr(ob, "animation_data")

    def execute(self, context):
        #rig = context.object
        scene = context.scene
        rigs = [rig for rig in context.selected_objects if rig.type == 'ARMATURE']
        for rig in rigs:
            for a in rig.data.actions:
                action = bpy.data.actions.get(a.name)
                if action is None:
                    continue
                rescale_action(rig, action)
            rescale_rig(rig)
        c = context.copy()
        c["selected_objects"] = rigs
        bpy.ops.object.transform_apply(c, scale=True)
        # scene update
        scene.frame_set(scene.frame_current)
        return {'FINISHED'}




class ApplyScale2AnimationPanel(bpy.types.Panel):
    """Rescale Panel"""
    bl_label = "Apply Scale"
    
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "BVH"

    @classmethod
    def poll(cls, context):
        return bpy.ops.mocap_madness.rescale.poll()
    
    def draw(self, context):
        layout = self.layout

        scene = context.scene
        row = layout.row()
        # Create a simple row.
        op = row.operator("mocap_madness.rescale")

def register():
    print("REGISTER RESCALE")
    bpy.utils.register_class(RescaleRigAnimation)
    bpy.utils.register_class(ApplyScale2AnimationPanel)


def unregister():
    bpy.utils.unregister_class(ApplyScale2AnimationPanel)
    bpy.utils.unregister_class(RescaleRigAnimation)


if __name__ == "__main__":
    register()
