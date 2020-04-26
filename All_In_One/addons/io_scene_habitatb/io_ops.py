# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, Yethiel 2017
#
# ##### END LICENSE BLOCK #####


import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper, axis_conversion
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        StringProperty,
        CollectionProperty,
        IntVectorProperty,
        PointerProperty
        )


class ImportPRM(bpy.types.Operator, ImportHelper):
    """Import from PRM file format (.prm, .m)"""
    bl_idname = "import_scene.prm"
    bl_label = 'Import PRM'
    bl_options = {'UNDO'}

    filename_ext = ".prm"
    filter_glob = StringProperty(
            default="*.prm;*.m", 
            options={'HIDDEN'},
            )

    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))


    def execute(self, context):
        from . import import_prm

        return import_prm.load(
            self, 
            self.properties.filepath, 
            context, 
            axis_conversion(to_up = self.up_axis, 
                            to_forward = self.forward_axis).to_4x4() * self.scale)

class ImportW(bpy.types.Operator, ImportHelper):
    """Import from W file format (.w)"""
    bl_idname = "import_scene.w"
    bl_label = 'Import W'
    bl_options = {'UNDO'}

    filename_ext = ".w"
    filter_glob = StringProperty(
            default="*.w", 
            options={'HIDDEN'},
            )

    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))

    def execute(self, context):
        from . import import_w

        return import_w.load(
            self, 
            self.properties.filepath, 
            context, 
            axis_conversion(to_up = self.up_axis, 
                            to_forward = self.forward_axis).to_4x4() * self.scale)

class ImportNCP(bpy.types.Operator, ImportHelper):
    """Import from NCP file format (.ncp)"""
    bl_idname = "import_scene.ncp"
    bl_label = 'Import NCP'
    bl_options = {'UNDO'}

    filename_ext = ".ncp"
    filter_glob = StringProperty(
            default="*.ncp", 
            options={'HIDDEN'},
            )

    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    
    def execute(self, context):
        from . import import_ncp

        return import_ncp.load(
            self, 
            self.properties.filepath, 
            context, 
            axis_conversion(to_up = self.up_axis, 
                            to_forward = self.forward_axis).to_4x4() * self.scale)

class ImportPOS(bpy.types.Operator, ImportHelper):
    """Import from POS file format (.pan)"""
    bl_idname = "import_scene.pan"
    bl_label = 'Import POS'
    bl_options = {'UNDO'}

    filename_ext = ".pan"
    filter_glob = StringProperty(
            default="*.pan", 
            options={'HIDDEN'},
            )

    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    
    def execute(self, context):
        from . import import_pos

        return import_pos.load(
            self, 
            self.properties.filepath, 
            context, 
            axis_conversion(to_up = self.up_axis, 
                            to_forward = self.forward_axis).to_4x4() * self.scale)


class ExportPRM(bpy.types.Operator, ExportHelper):
    """Export to PRM file format (.prm, .m)"""
    bl_idname = "export_scene.prm"
    bl_label = 'Export PRM'

    filename_ext = ""
    filter_glob = StringProperty(
            default="*.prm;*.m",
            options={'HIDDEN'},
            )

    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
        
    def execute(self, context):
        from . import export_prm
                           
        return export_prm.save(
            self, 
            self.properties.filepath, 
            context, 
            axis_conversion(from_up = self.up_axis, 
                            from_forward = self.forward_axis).to_4x4() * (1 / self.scale))

class ExportW(bpy.types.Operator, ExportHelper):
    """Export to W file format (.w)"""
    bl_idname = "export_scene.w"
    bl_label = 'Export W'

    filename_ext = ""
    filter_glob = StringProperty(
            default="*.w",
            options={'HIDDEN'},
            )

    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
        
    def execute(self, context):
        from . import export_w
                           
        return export_w.save(
            self, 
            self.properties.filepath, 
            context, 
            axis_conversion(from_up = self.up_axis, 
                            from_forward = self.forward_axis).to_4x4() * (1 / self.scale))


class ExportNCP(bpy.types.Operator, ExportHelper):
    """Export to NCP file format (.ncp)"""
    bl_idname = "export_scene.ncp"
    bl_label = 'Export NCP'

    filename_ext = ""
    filter_glob = StringProperty(
            default="*.ncp;*.m",
            options={'HIDDEN'},
            )

    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
        
    def execute(self, context):
        from . import export_ncp
        
                                    
        return export_ncp.save(
            self, 
            self.properties.filepath, 
            context, 
            axis_conversion(from_up = self.up_axis, from_forward = self.forward_axis).to_4x4() * (1 / self.scale))
