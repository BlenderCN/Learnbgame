# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "Import Maya Cache (.xml, .mc)",
    "author": "Jasper van Nieuwenhuizen",
    "version": (0, 1),
    "blender": (2, 6, 0),
    "location": "File > Import > Maya cache (.xml, .mc)",
    "description": "Imports Maya Cache to Objects",
    "warning": "wip",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

if "bpy" in locals():
    import imp
    if "import_mc" in locals():
        imp.reload(import_mc)
    if "export_mc" in locals():
        imp.reload(export_mc)


import bpy
from bpy.props import (BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       )
from bpy_extras.io_utils import (ExportHelper,
                                 ImportHelper,
                                 path_reference_mode,
                                 axis_conversion,
                                 )


class ImportMC(bpy.types.Operator, ImportHelper):
    """Load a Maya Cache file"""
    bl_idname = "import_shape.mc"
    bl_label = "Import Maya Cache"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".xml"
    filter_glob = StringProperty(
            default="*.xml;*.mc",
            options={'HIDDEN'},
            )

    use_selection = BoolProperty(
            name="Selection Only",
            description="Import cache for selected objects only",
            default=False,
            )

    interpolation = EnumProperty(
            name="Interpolation",
            items=(('LINEAR', "Linear", ""),
                   ('NONE', "None", ""),
                   )
            )

    time_mode = EnumProperty(
            name="Method to control playback time",
            items=(('FRAME', "Frame", "Control playback using a frame number"\
                    " (ignoring time FPS and start frame from the file"),
                   ('TIME', "Time", "Control playback using time in seconds"),
                   ('FACTOR', "Factor", "Control playback using a value"\
                    " between [0, 1]"),
                  )
            )

    play_mode = EnumProperty(
            name="Play mode",
            items=(('SCENE', "Scene", "Use the time from the scene"),
                   ('CUSTOM', "Custom", "Use the modifiers own time"\
                    " evaluation"),
                  )
            )

    frame_start = FloatProperty(
            name="Frame Start",
            description="Add this to the start frame",
            )

    frame_scale = FloatProperty(
            name="Frame Scale",
            description="Evaluation time in seconds",
            )

    eval_frame = FloatProperty(
            name="Evaluation Frame",
            description="The frame to evaluate (starting at 0)",
            )

    eval_time = FloatProperty(
            name="Evaluation Time",
            description="Evaluation time in seconds",
            )

    eval_factor = FloatProperty(
            name="Evaluation Factor",
            description="Evaluation factor",
            )

    forward_axis = EnumProperty(
            name="Forward",
            items=(('X', "+X", ""),
                   ('Y', "+Y", ""),
                   ('Z', "+Z", ""),
                   ('-X', "-X", ""),
                   ('-Y', "-Y", ""),
                   ('-Z', "-Z", ""),
                   ),
            default='-Z',
            )

    up_axis = EnumProperty(
            name="Up",
            items=(('X', "+X", ""),
                   ('Y', "+Y", ""),
                   ('Z', "+Z", ""),
                   ('-X', "-X", ""),
                   ('-Y', "-Y", ""),
                   ('-Z', "-Z", ""),
                   ),
            default='Y',
            )

    def execute(self, context):
        import imp
        from . import import_mc
        imp.reload(import_mc)

        keywords = self.as_keywords(ignore=("forward_axis",
                                            "up_axis",
                                            "filter_glob",
                                            ))

        global_matrix = axis_conversion(from_forward=self.forward_axis,
                                        from_up=self.up_axis,
                                        ).to_4x4()
        keywords["global_matrix"] = global_matrix

        return import_mc.load(self, context, **keywords)

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "use_selection")

        layout.label(text="Time Mapping:")

        row = layout.row()
        row.prop(self, "time_mode", expand=True)
        row = layout.row()
        row.prop(self, "play_mode", expand=True)
        if self.play_mode == 'SCENE':
            layout.prop(self, "frame_start")
            layout.prop(self, "frame_scale")
        else:
            time_mode = self.time_mode
            if time_mode == 'FRAME':
                layout.prop(self, "eval_frame")
            elif time_mode == 'TIME':
                layout.prop(self, "eval_time")
            elif time_mode == 'FACTOR':
                layout.prop(self, "eval_factor")

        layout.label(text="Axis Mapping:")
        split = layout.split(percentage=0.5, align=True)
        split.alert = (self.forward_axis[-1] == self.up_axis[-1])
        split.label("Forward/Up Axis:")
        split.prop(self, "forward_axis", text="")
        split.prop(self, "up_axis", text="")
        #split = layout.split(percentage=0.5)
        #split.label(text="Flip Axis:")
        #row = split.row()
        #row.prop(self, "flip_axis")


def menu_func_import(self, context):
    self.layout.operator(ImportMC.bl_idname, text="Maya Cache (.xml, .mc)")


#def menu_func_export(self, context):
#    self.layout.operator(ExportMC.bl_idname, text="Maya Cache (.xml, .mc)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)
    #bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    #bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
