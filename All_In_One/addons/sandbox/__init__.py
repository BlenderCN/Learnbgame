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

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2014
# Coding Standards:    See http://www.makehuman.org/node/165

"""
Abstract
Collection of experimental and undocumented MakeHuman tools
"""

bl_info = {
    "name": "MH Sandbox",
    "author": "Thomas Larsson",
    "version": (0, "001"),
    "blender": (2,6,9),
    "location": "View3D > Tools > MH Sandbox",
    "description": "Collection of experimental and undocumented MakeHuman tools",
    "warning": "",
    #'wiki_url': "http://www.makehuman.org/doc/node.???.html",
    "category": "Learnbgame",
}

# To support reload properly, try to access a package var, if it's there, reload everything
if "bpy" in locals():
    print("Reloading MH Sandbox")
    import imp
    imp.reload(io_json)
    imp.reload(drivers)
    imp.reload(markers)
    imp.reload(facerig)
    imp.reload(visemes)
    imp.reload(merge)
    imp.reload(points)
    print("MH Sandbox reloaded")
else:
    print("Loading MH Sandbox")
    import bpy, os
    from bpy_extras.io_utils import ImportHelper
    from bpy.props import *

    from . import io_json
    from . import drivers
    from . import markers
    from . import facerig
    from . import visemes
    from . import merge
    from . import points
    print("MH Sandbox loaded")


def inset(layout):
    split = layout.split(0.05)
    split.label("")
    return split.column()

########################################################################
#
#   class MainPosePanel(bpy.types.Panel):
#

class MainPosePanel(bpy.types.Panel):
    bl_label = "MH Sandbox v %d.%s: Main" % bl_info["version"]
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        layout.prop(scn, "MHFaceRig")
        if scn.MHFaceRig:
            ins = inset(layout)
            ins.operator("mp.load_trc_file")
            ins.operator("mp.load_txt_file")
            ins.prop(scn, "MpFrameStart")
            ins.prop(scn, "MpFrameEnd")
            ins.prop(scn, "MpScale")
            ins.prop(scn, "MpDeltaY")

            ins.separator()
            ins.operator("mp.save_facerig")
            ins.operator("mp.load_facerig")
            ins.operator("mp.transfer_face_anim")

        layout.separator()
        layout.label("Edit")
        layout.operator("mp.average_fcurves")


########################################################################
#
#   class SetupPanel(bpy.types.Panel):
#

class SetupPanel(bpy.types.Panel):
    bl_label = "MH Sandbox: Setup"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if context.object:
            return True

    def draw(self, context):
        layout = self.layout
        ob = context.object

        if ob.type == 'ARMATURE':
            layout.operator("mp.create_expression_drivers")
            layout.operator("mp.create_hide_drivers")
            layout.operator("mp.reset_expression_keys")

        elif ob.type == 'MESH':
            layout.operator("mp.merge_objects")
            layout.separator()
            layout.operator("mp.copy_point_cache")

        return

        props = list(rig.keys())
        props.sort()

        layout.separator()
        layout.label("Mhh")
        for prop in props:
            if prop[0:3] == "Mhh":
                layout.prop(rig, '["%s"]' % prop, text=prop[3:])

        layout.separator()
        layout.label("Mhs")
        for prop in props:
            if prop[0:3] == "Mhs":
                row = layout.split(0.8)
                row.prop(rig, '["%s"]' % prop, text=prop[3:])
                row.operator("mp.pin_expression_key").key = prop

        layout.separator()
        layout.label("Mht")
        for prop in props:
            if prop[0:3] == "Mht":
                row = layout.split(0.8)
                row.prop(rig, '["%s"]' % prop, text=prop[3:])
                row.operator("mp.pin_expression_key").key = prop

        return

        if not rig.MPVisemeDriversAssigned:
            layout.operator("mp.create_viseme_drivers")
            return

        layout.operator("mp.clear_visemes")
        for key in visemes.Visemes.keys():
            layout.prop(rig, "MP"+key)


#
#    init
#

def init():

    bpy.types.Scene.MHFaceRig = BoolProperty(
        name="Face Rig",
        description="Use face rig",
        default=False)


def register():
    init()
    visemes.init()
    markers.init()
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()


