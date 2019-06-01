#------------------------------------------------------------------------------
# Reynolds-Blender | The Blender add-on for Reynolds, an OpenFoam toolbox.
#------------------------------------------------------------------------------
# Copyright|
#------------------------------------------------------------------------------
#     Deepak Surti       (dmsurti@gmail.com)
#     Prabhu R           (IIT Bombay, prabhu@aero.iitb.ac.in)
#     Shivasubramanian G (IIT Bombay, sgopalak@iitb.ac.in)
#------------------------------------------------------------------------------
# License
#
#     This file is part of reynolds-blender.
#
#     reynolds-blender is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     reynolds-blender is distributed in the hope that it will be useful, but
#     WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
#     Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with reynolds-blender.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------

# -----------
# bpy imports
# -----------
import bpy, bmesh
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       IntVectorProperty,
                       FloatVectorProperty,
                       CollectionProperty
                       )
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       UIList
                       )
from bpy.path import abspath
from mathutils import Matrix, Vector

# --------------
# python imports
# --------------
import operator
import os

# ------------------------
# reynolds blender imports
# ------------------------

from reynolds_blender.gui.register import register_classes, unregister_classes
from reynolds_blender.gui.attrs import set_scene_attrs, del_scene_attrs
from reynolds_blender.gui.custom_operator import create_custom_operators
from reynolds_blender.gui.renderer import ReynoldsGUIRenderer

# ----------------
# reynolds imports
# ----------------
from reynolds.dict.parser import ReynoldsFoamDict
from reynolds.foam.cmd_runner import FoamCmdRunner

# ------------------------------------------------------------------------
#    operators
# ------------------------------------------------------------------------

def load_mesh_objs(self, context):
    print ('load list of mesh objs from case dir')

    scene = context.scene
    case_dir = bpy.path.abspath(scene.case_dir_path)
    wmr = FoamCmdRunner(cmd_name='writeMeshObj', case_dir=case_dir)

    for info in wmr.run():
        self.report({'WARNING'}, info)

    if wmr.run_status:
        index = 0
        item_coll = scene.mesh_objs
        item_idx = scene.mesh_rindex
        item_coll.clear()
        for file in os.listdir(case_dir):
            if file.endswith(".obj"):
                item = item_coll.add()
                scene.mesh_rindex = index
                item.name = file
                index += 1
        print(scene.mesh_rindex, scene.mesh_objs)
        self.report({'INFO'}, 'Generated mesh objs')
    else:
        self.report({'INFO'}, 'Could not generate mesh objs')

    return {'FINISHED'}

def show_mesh_obj(self, context):
    print("Showing mesh obj")

    scene = context.scene
    obj = context.active_object

    item = scene.mesh_objs[scene.mesh_rindex]
    print('File to load: ' + item.name)

    case_dir = bpy.path.abspath(scene.case_dir_path)
    obj_file_path = case_dir + item.name
    bpy.ops.import_scene.obj(filepath=obj_file_path)

    return{'FINISHED'}

# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------

class ShowMeshObjOperator(bpy.types.Operator):
    bl_idname = "reynolds.of_show_mesh_obj_panel"
    bl_label = "Visualize Mesh"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    bl_context = "objectmode"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}

    # Return True to force redraw
    def check(self, context):
        return True

    def invoke(self, context, event):
        load_mesh_objs(self, context)
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # ---------------------------------------
        # Render Block Panel using YAML GUI Spec
        # ---------------------------------------

        gui_renderer = ReynoldsGUIRenderer(scene, layout,
                                           'mesh_objs.yaml')
        gui_renderer.render()


# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    register_classes(__name__)
    set_scene_attrs('mesh_objs.yaml')
    create_custom_operators('mesh_objs.yaml', __name__)

def unregister():
    unregister_classes(__name__)
    del_scene_attrs('mesh_objs.yaml')

if __name__ == "__main__":
    register()
