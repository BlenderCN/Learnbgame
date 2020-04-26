import json
import pickle
import itertools as it
import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator
from . import utils as ut

class ExportSprycle(Operator, ExportHelper):
    """Export sprycle animation data (.spry)"""
    bl_idname = "export_scene.spry"
    bl_label = "Export to .spry"

    filename_ext = ".spry"

    filter_glob = StringProperty(
                    default="*.spry",
                    options={'HIDDEN'},
                    )

    mode = EnumProperty(
    		name="Export",
    		description="",
    		items=(
    			("All", "All", "Export to internal display and file"),
    			("Internal", "Internal", "Export only to internal display plane")),
    		default='All',
    		)

    def frame(self, obj):
        return [list(uv) for uv in ut.uvs(obj)]


    def dump_to_textblock(self, spry, display):
        text_name = "frames_{:s}".format(display.name.split("_")[1])
        if text_name in bpy.data.texts:
            text = bpy.data.texts[text_name]
        else:
            text = bpy.data.texts.new(text_name)
        if not len(display.game.controllers):
            bpy.ops.logic.controller_add(type="PYTHON", object=display.name)
        display.game.controllers[0].text = text
        text.clear()
        text.write(str(pickle.dumps(spry)))


    def execute(self, context):
        scene = context.scene

        display = [o for o in scene.objects if "display_" in o.name][0]

        frames = [o for o in scene.objects if o is not display]
        groups = it.groupby(frames, lambda o: ut.base_name(o))

        spry = {n: sorted(g, key=lambda o: o.matrix_world.translation.x) 
                for n, g in groups}

        for n, lst in spry.items():
            spry[n] = [self.frame(o) for o in lst]

        self.dump_to_textblock(spry, display)

        if self.mode == "Internal":
            return {'FINISHED'}

        with open(self.filepath, "w") as f:
            json.dump(spry, f)

        return {'FINISHED'}


def menu_func_export(self, context):
    self.layout.operator(ExportSprycle.bl_idname, text="sprycle (.spry)")


def register():
    bpy.utils.register_class(ExportSprycle)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportSprycle)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
