import bpy
from .. functions import *

class VersionFix(bpy.types.Operator):
    bl_idname = "asset_sketcher.version_fix"
    bl_label = "Asset Sketcher 1.0 Version Fix"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        wm = context.window_manager
        
        ### update all assets in scene
        for obj in bpy.data.objects:
            if "asset" in obj and not "as_asset" in obj:
                print(obj.name)
                obj["as_asset"] = obj["asset"]
                del(obj["asset"])
            if "asset_name" in obj and not "as_asset_name" in obj:
                obj["as_asset_name"] = obj["asset_name"]
                del(obj["asset_name"])
            if "type" in obj and not "as_type" in obj:
                obj["as_type"] = obj["type"]
                del(obj["type"])
                
        ### convert old asset list to new        
        for item in wm.sketch_assets_list:
            if item.name not in wm.asset_sketcher.asset_list:
                new_item = wm.asset_sketcher.asset_list.add()
                new_item.name = item.name
                new_item.make_single_user = item.make_single_user
                new_item.asset_distance = item.distance
                new_item.z_offset = item.z_offset
                new_item.slope_threshold = item.slope_threshold
                new_item.surface_orient = item.surface_orient
                new_item.rot_x = item.rot_x
                new_item.rot_y = item.rot_y
                new_item.rot_z = item.rot_z
                new_item.rand_rot_x = item.rand_rot_x
                new_item.rand_rot_y = item.rand_rot_y
                new_item.rand_rot_z = item.rand_rot_z
                new_item.stroke_orient = item.stroke_orient
                new_item.scale = item.scale
                new_item.scale_pressure = item.scale_pressure
                new_item.rand_scale_x = item.rand_scale_x
                new_item.rand_scale_y = item.rand_scale_y
                new_item.rand_scale_z = item.rand_scale_z
                new_item.constraint_rand_scale = item.constraint_rand_scale
                new_item.type = item.type
                if item.type == "GROUP" and item.name in bpy.data.groups:
                    for obj in bpy.data.groups[item.name].objects:
                        group_obj = new_item.group_objects.add()
                        group_obj.name = obj.name
        update_category_display(wm.asset_sketcher,context)        
                
                
        self.report({'INFO'},"All Assets have been updated for v1.0")
        return {"FINISHED"}
        