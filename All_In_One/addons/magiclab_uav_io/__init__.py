bl_info = {
    "name": "MagicLab UAV IO",
    "author": "Bassam Kurdali",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "location": "File->Import-Export",
    "description": "Export/Export Object Animations for UAV Control",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
    }

if "bpy" in locals():
    import importlib
    importlib.reload(uav_export)
    importlib.reload(uav_import)
    importlib.reload(update_mats)
    importlib.reload(volume_import)
else:
    from . import uav_export
    from . import uav_import
    from . import update_mats
    from . import volume_import

import bpy
from bpy.props import StringProperty, FloatProperty


class MagicLabUAVPrefs(bpy.types.AddonPreferences):
    bl_idname = __name__
    module_path = StringProperty(
        default='/usr/lib64/python3.5/site-packages', subtype ='DIR_PATH')

    def draw(self, context):
        layout = self.layout
        layout.label(
            "Blender does not include Yaml, we need to find the module")
        layout.prop(self, "module_path", text="Python Site Packages")


class ConstantifyGlowKeyFrames(bpy.types.Operator):
    """ Make Glow Keyframes Constant type """
    bl_idname = "object.constant_glow_keyframes"
    bl_label = "Make glow keyframes constant"


    @classmethod
    def poll(cls, context):
        return (
            context.active_object and
            context.active_object.animation_data and
            context.active_object.animation_data.action)

    def execute(self, context):
        for fcurve in context.active_object.animation_data.action.fcurves:
            if fcurve.data_path in ("glow", '["glow"]'):
                for kp in fcurve.keyframe_points:
                    kp.interpolation = 'CONSTANT'
        return {'FINISHED'}


class MagicLabAnimation(bpy.types.Panel):
    bl_label = 'Magic Lab Animation'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'MagicLab'

    @classmethod
    def poll(cls, context):
        return (
            context.active_object and
            "channel" in context.active_object.keys())

    def draw(self, context):
        layout = self.layout
        active = context.active_object
        row = layout.row()
        row.prop(active, "glow")
        row.operator(
            ConstantifyGlowKeyFrames.bl_idname,
            text="Make Keframes Constant"
        )
        row = layout.row()
        row.prop(active, "location")
        row = layout.row()


class MagicLabIO(bpy.types.Panel):
    bl_label = 'Magic Lab I/O'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'MagicLab'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator(
            uav_import.ImportInitialUAVs.bl_idname,
            text="Import Waypoints",
            icon='FILE')
        row = layout.row()
        row.operator(
            uav_export.ExportCSVLocations.bl_idname,
            text="Export Waypoints",
            icon='FILE')
        row = layout.row()
        row = layout.row()
        row.operator(
            volume_import.ImportCaptureVolume.bl_idname,
            text="Import Capture Volume",
            icon='FILE')

class MagicLabView(bpy.types.Panel):
    bl_label = 'Magic Lab View'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'MagicLab'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator(
            update_mats.MakeSolidsUpdate.bl_idname,
            text="fast update"
        )
        row.operator(
            update_mats.MakeMaterialUpdate.bl_idname,
            text="slow update"
        )

def register():
    bpy.utils.register_class(MagicLabUAVPrefs)
    def glow_update(self, context):
        if self.active_material and "DRONE" in self.active_material.keys():
            self.active_material.update_tag()
            context.scene.update()
    bpy.types.Object.glow = FloatProperty(
        default=0.0, name="glow",
        min=0.0, max=2.0,
        soft_min=0.0, soft_max=2.0,
        update=glow_update)
    uav_import.register()
    uav_export.register()
    update_mats.register()
    volume_import.register()
    bpy.utils.register_class(ConstantifyGlowKeyFrames)
    bpy.utils.register_class(MagicLabAnimation)
    bpy.utils.register_class(MagicLabIO)
    bpy.utils.register_class(MagicLabView)


def unregister():
    bpy.utils.unregister_class(MagicLabView)
    bpy.utils.unregister_class(MagicLabAnimation)
    bpy.utils.unregister_class(MagicLabIO)
    bpy.utils.unregister_class(ConstantifyGlowKeyFrames)
    volume_import.unregister()
    uav_import.unregister()
    uav_export.unregister()
    update_mats.unregister()
    del(bpy.types.Object.glow)
    bpy.utils.unregister_class(MagicLabUAVPrefs)

if __name__ == "__main__":
    register()
