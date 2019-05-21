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


bl_info = {
    "name": "Compositing Presets",
    "author": "Fabio Russo (ruesp83) <ruesp83@libero.it>",
    "version": (0, 3),
    "blender": (2, 5, 6),
    "api": 35035,
    "location": "Node Editor > Properties",
    "description": "Presets of nodes for the Compositing Nodes.",
    "category": "Compositing",
    'wiki_url': "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/"\
                "Compositing/Compositing_Presets",
    'tracker_url': "http://projects.blender.org/tracker/?func=detail&aid=25621"
}


import bpy
import os
import math
from bpy.props import *


def Div_Description(desc, width):
    car = math.floor(width / 7)
    return [desc[i:i + car] for i in range(0, len(desc), car)]


def PresetsDir(typePath):
    scriptPath = os.path.dirname(__file__)
    scriptPath = os.path.join(scriptPath, "presets")
    presetsPath = [os.path.join(scriptPath, typePath)]
    #dir = []
    #for directory in presetsPath:
    #    dir.extend([(f, os.path.join(directory, f))
    #                       for f in os.listdir(directory)])
    #dir.sort()
    #return dir
    return presetsPath


class NODE_EDITOR_MT_presets(bpy.types.Menu):
    bl_label = "Group Presets"
    preset_operator = "script.execute_preset"
    presetsPath = []

    def draw(self, context):
        #listPath = [self.presetsPath]
        self.path_menu(self.presetsPath, self.preset_operator)


class NODE_EDITOR_PT_preset(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_label = "Group Presets"

    @classmethod
    def poll(cls, context):
        view = context.space_data
        return (view)

    def draw(self, context):
        layout = self.layout
        view = context.space_data
        scene = context.scene
        desc = scene.bf_description
        cat = scene.bf_class
        author = scene.bf_author

        if (view.tree_type == 'MATERIAL') and (view.id.use_nodes):
            col = layout.column(align=True)
            dir = PresetsDir("material")
            NODE_EDITOR_MT_presets.presetsPath = dir
            col.menu("NODE_EDITOR_MT_presets",
                        text=NODE_EDITOR_MT_presets.bl_label)

        if (view.tree_type == 'TEXTURE') and (view.id.use_nodes):
            col = layout.column(align=True)
            dir = PresetsDir("texture")
            NODE_EDITOR_MT_presets.presetsPath = dir
            col.menu("NODE_EDITOR_MT_presets",
                        text=NODE_EDITOR_MT_presets.bl_label)

        if (view.tree_type == 'COMPOSITING') and (view.id.use_nodes):
            col = layout.column(align=True)
            dir = PresetsDir("compositing")
            NODE_EDITOR_MT_presets.presetsPath = dir
            col.menu("NODE_EDITOR_MT_presets",
                        text=NODE_EDITOR_MT_presets.bl_label)
            #row.operator("render.preset_add", text="", icon="ZOOMIN")
            #row.operator("render.preset_add", text="",
            #            icon="ZOOMOUT").remove_active = True

        layout.separator()
        col = layout.column()
        row = col.row()
        row.label("Author: ", icon='GREASEPENCIL')
        if (type(author).__name__ == 'str'):
            row.label(author)
        row = col.row()
        row.label("Category: ", icon='SORTALPHA')
        if (type(cat).__name__ == 'str'):
            row.label(cat)
        col.label("Description: ", icon='INFO')
        if (type(desc).__name__ == 'str'):
            l_desc = Div_Description(desc, context.region.width)
            for line_s in l_desc:
                col.label(line_s)


def register():
    bpy.types.Scene.bf_description = StringProperty(name="Description",
        description="Description of the preset",
        default="")
    bpy.types.Scene.bf_class = StringProperty(name="Category",
        description="Description of the category",
        default="")
    bpy.types.Scene.bf_author = StringProperty(name="Author",
        description="Name of the author",
        default="")
    bpy.utils.register_class(NODE_EDITOR_MT_presets)
    bpy.utils.register_class(NODE_EDITOR_PT_preset)
    pass


def unregister():
    del bpy.types.Scene.bf_description
    del bpy.types.Scene.bf_class
    del bpy.types.Scene.bf_author
    bpy.utils.unregister_class(NODE_EDITOR_MT_presets)
    bpy.utils.unregister_class(NODE_EDITOR_PT_preset)
    pass


if __name__ == "__main__":
    register()
