# A voxel texture's offset and size fit in object's bound box.
# Exec "Fit Voxel data in Bound Box" from space bar's menu.
import sys
import bpy

def fit_voxel_data_in_bound_box(obj):
    ret = 0
    
    # print("{} processing".format(obj.name))
    vmax = [-sys.float_info.max, -sys.float_info.max, -sys.float_info.max]
    vmin = [sys.float_info.max, sys.float_info.max, sys.float_info.max]
    
    for i, v in enumerate(obj.bound_box):
        vmax[0] = max(vmax[0], v[0])
        vmax[1] = max(vmax[1], v[1])
        vmax[2] = max(vmax[2], v[2])
        
        vmin[0] = min(vmin[0], v[0])
        vmin[1] = min(vmin[1], v[1])
        vmin[2] = min(vmin[2], v[2])
    
    #print("min:({}, {}, {})".format(vmin[0], vmin[1], vmin[2]))
    #print("max:({}, {}, {})".format(vmax[0], vmax[1], vmax[2]))
    
    if obj.active_material == None:
        # print("{} has no material", obj.name)
        return ret
    
    for texslot in obj.active_material.texture_slots:
        if texslot == None:
            # print("None texture")
            continue
        if texslot.texture.type != 'VOXEL_DATA':
            # print("Not a Voxel data")
            continue
        
        texslot.offset = (
            (vmax[0] + vmin[0]) * -0.5,
            (vmax[1] + vmin[1]) * -0.5,
            (vmax[2] + vmin[2]) * -0.5
        )
        # Voxel data filles ((-1, -1, -1), (1, 1, 1)) box.
        texslot.scale = (
            2.0 / (vmax[0] - vmin[0]),
            2.0 / (vmax[1] - vmin[1]),
            2.0 / (vmax[2] - vmin[2]),
        )
        ret += 1
        
    return ret

# Operation class
class OBJECT_OT_fit_voxel_data_in_bound_box(bpy.types.Operator):
    bl_idname = "object.fit_voxel_data_in_bound_box"
    bl_label = "Fit Voxel data in Bound Box"
    bl_description = "If texture is Voxel, set offset and size to fit in bound box"
    
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects)
    
    def execute(self, context):
        fitted = 0
        for obj in bpy.context.selected_objects:
            fitted += fit_voxel_data_in_bound_box(obj)
        self.report({'INFO'}, "modified {} textures".format(fitted))
        return {'FINISHED'}

# Registration
def register():
    bpy.utils.register_class(OBJECT_OT_fit_voxel_data_in_bound_box)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_fit_voxel_data_in_bound_box)

if __name__ == "__main__":
    register()