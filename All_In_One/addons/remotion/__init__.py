"""
Re : motion by Nicolas Candia <ncandia.pro@gmail.com>

Copyright (C) 2018 Nicolas Candia
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import bpy
import subprocess

from shutil import copy2
from bpy_extras.io_utils import ImportHelper, ExportHelper
from tempfile import gettempdir

bl_info = {
    "name": "Re:motion",
    "author": "Nicolas Candia",
    "blender": (2, 79, 0),
    "version": (0, 1, 0),
    "location": "Tools > Re:motion",
    "description": "Fix motion animation using machine learning prediction",
    "warning": "",
    "support": "TESTING",
    "category": "Animation",
}

# Panels ----------------------------------------

class MotionFixAnimPanel(bpy.types.Panel):
    bl_label = "Re:motion - Animation"
    bl_idname = "MOTIONFIX_ANIM_PANEL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MotionFix"

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        box = layout.box()
        row = box.row(align=True)
        row.prop(scene.motionfix, "asf_file")
        row.operator("motionfix.browse_asf", icon="FILE_FOLDER", text="")

        row = box.row()
        row.operator("motionfix.import_asf", icon="IMPORT", text="Import skeleton")

        box = layout.box()
        row = box.row(align=True)
        row.prop(scene.motionfix, "amc_file")
        row.operator("motionfix.browse_amc", icon="FILE_FOLDER", text="")

        row = box.row()
        row.operator("motionfix.import_amc", icon="IMPORT", text="Import animation")

class MotionFixCorrectorPanel(bpy.types.Panel):
    bl_label = "Re:motion - Tools"
    bl_idname = "MOTIONFIX_CORRECTOR_PANEL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MotionFix"

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        row = layout.row()
        row.prop(scene.motionfix_corrector, "motion_type")

        row = layout.row()
        row.prop(scene.motionfix_corrector, "accuracy")

        box = layout.box()
        row = box.row()
        row.prop(scene.motionfix_corrector, "src_frame")
        row.prop(scene.motionfix_corrector, "predicted_frame")

        row = layout.row()
        row.prop(scene.motionfix_corrector, "fixall")

        if not scene.motionfix_corrector.fixall:
            box = layout.box()
            row = box.row()
            row.prop(scene.motionfix_corrector, "start_frame")
            row.prop(scene.motionfix_corrector, "end_frame")

        row = layout.row()
        row.operator("motionfix.run", icon="FILE_TICK", text="Apply correction")
        row.operator("motionfix.export_amc", icon="DISK_DRIVE", text="Export to AMC")

class MotionFixPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    python_env = bpy.props.StringProperty(name="Python binary", subtype='FILE_PATH')

    predict_app = bpy.props.StringProperty(name="Predict Script", subtype='FILE_PATH')

    tmp_folder = bpy.props.StringProperty(name="Temporary folder", default=gettempdir())

    gpu_accelerated = bpy.props.BoolProperty(name="GPU accelerated (require cuDNN)")

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, "python_env")

        row = layout.row()
        row.prop(self, "predict_app")

        row = layout.row()
        row.prop(self, "tmp_folder")

        row = layout.row()
        row.prop(self, "gpu_accelerated")

# Properties ------------------------------------

class MotionFixAnimProperty(bpy.types.PropertyGroup):
    asf_file = bpy.props.StringProperty(name="ASF File")
    amc_file = bpy.props.StringProperty(name="AMC File")

class MotionFixCorrectorProperty(bpy.types.PropertyGroup):
    motion_type = bpy.props.EnumProperty(name="Motion Type", items={("walk", "walk", "Walk"), ("jump", "jump", "jump")})

    fixall = bpy.props.BoolProperty(name="Pass over all animation", default=True)

    start_frame = bpy.props.IntProperty(name="Start frame")
    end_frame = bpy.props.IntProperty(name="End frame")

    accuracy = bpy.props.FloatProperty(name="Tolerance", min=0.01, step=1.0, default=5.0)

    src_frame = bpy.props.IntProperty(name="# Source frame", default=50)
    predicted_frame = bpy.props.IntProperty(name="# Predicted frame", default=10)

    tmp_amc_file = bpy.props.StringProperty("Temporary AMC File", options={"HIDDEN"})

# Operators -------------------------------------

class MotionFix_OT_FileBrowserASF(bpy.types.Operator, ImportHelper):
    bl_idname = "motionfix.browse_asf"
    bl_label = "Open browser and get ASF file"

    filter_glob = bpy.props.StringProperty(default="*.asf", options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        scene.motionfix.asf_file = self.properties.filepath
        return {"FINISHED"}

class MotionFix_OT_FileBrowserAMC(bpy.types.Operator, ImportHelper):
    bl_idname = "motionfix.browse_amc"
    bl_label = "Open browser and get AMC file"

    filter_glob = bpy.props.StringProperty(default="*.amc", options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        scene.motionfix.amc_file = self.properties.filepath
        return {"FINISHED"}

class MotionFix_OT_ImportASF(bpy.types.Operator):
    bl_idname = "motionfix.import_asf"
    bl_label = "Import ASF File from MotionFix"

    def execute(self, context):
        scene = context.scene
        bpy.ops.import_anim.asf(filepath=scene.motionfix.asf_file)
        return {"FINISHED"}

class MotionFix_OT_ImportAMC(bpy.types.Operator):
    bl_idname = "motionfix.import_amc"
    bl_label = "Import AMC File from MotionFix"

    def execute(self, context):
        scene = context.scene
        bpy.ops.import_anim.amc(filepath=scene.motionfix.amc_file)
        return {"FINISHED"}

class MotionFix_OT_ExportAMC(bpy.types.Operator, ExportHelper):
    bl_idname = "motionfix.export_amc"
    bl_label = "Save AMC"

    filename_ext = ".amc"

    def execute(self, context):
        scene = context.scene
        copy2(scene.motionfix_corrector.tmp_amc_file, self.properties.filepath)
        return {"FINISHED"}

class MotionFix_OT_Run(bpy.types.Operator):
    bl_idname = "motionfix.run"
    bl_label = "Run MotionFix on selected animation file"

    def execute(self, context):
        scene = context.scene

        addon_prefs = context.user_preferences.addons[__name__].preferences

        scene.motionfix_corrector.tmp_amc_file = addon_prefs.tmp_folder + "/motionfix.tmp"
        
        call_args = []

        call_args.append(addon_prefs.python_env)
        call_args.append(addon_prefs.predict_app)

        call_args.append("-i")
        call_args.append(scene.motionfix.amc_file)

        call_args.append("-o")
        call_args.append(scene.motionfix_corrector.tmp_amc_file)

        call_args.append("-t")
        call_args.append(scene.motionfix_corrector.accuracy)

        if not scene.motionfix_corrector.fixall:
            call_args.append("--start-frame")
            call_args.append(scene.motionfix_corrector.start_frame)
            call_args.append("--end-frame")
            call_args.append(scene.motionfix_corrector.end_frame)

        call_args.append("-fi")
        call_args.append(scene.motionfix_corrector.src_frame)
        call_args.append("-fo")
        call_args.append(scene.motionfix_corrector.predicted_frame)

        if addon_prefs.gpu_accelerated:
            call_args.append("--gpu")
            call_args.append("1")

        call_args.append(scene.motionfix_corrector.motion_type)

        for i in range(len(call_args)):
            call_args[i] = str(call_args[i])

        subprocess.check_call(call_args)

        bpy.ops.import_anim.amc(filepath=scene.motionfix_corrector.tmp_amc_file)

        return {"FINISHED"}

# Run -------------------------------------------

def register():
    scene = bpy.types.Scene
    
    bpy.utils.register_module(__name__)

    scene.motionfix = bpy.props.PointerProperty(type=MotionFixAnimProperty)
    scene.motionfix_corrector = bpy.props.PointerProperty(type=MotionFixCorrectorProperty)

    print("MotionFix is enabled.")


def unregister():
    bpy.utils.unregister_module(__name__)

    del bpy.types.Scene.motionfix
    del bpy.types.Scene.motionfix_corrector

    print("MotionFix is now disabled.")