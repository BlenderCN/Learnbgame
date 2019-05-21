#
#    Copyright (c) 2014 Shane Ambler
#
#    All rights reserved.
#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions are met:
#
#    1.  Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#    2.  Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#    A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
#    OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#    EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#    PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#    PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#    LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#    NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

bl_info = {
    "name": "Node Colours",
    "author": "sambler",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "SpaceBar Search -> Turn on/off all node colours",
    "description": "Turn on/off all custom node colours. Currently only for custom node trees.",
    "warning": "",
    "wiki_url": "https://github.com/sambler/addonsByMe/blob/master/node_colours.py",
    "tracker_url": "https://github.com/sambler/addonsByMe/issues",
    "category": "Learnbgame",
    }

import bpy
from bpy.props import BoolProperty

class NodeColourPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    set_custom_nodes : BoolProperty(name="Set custom nodes",
                              description="Include custom nodes",
                              default=True)

    set_compositing_nodes : BoolProperty(name="Set compositing nodes",
                              description="Include compositing nodes",
                              default=True)

    set_material_nodes : BoolProperty(name="Set material nodes",
                            description="Include material nodes",
                            default=True)

    set_texture_nodes : BoolProperty(name="Set texture nodes",
                            description="Include texture nodes",
                            default=True)

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        row = col.row()
        row.prop(self, "set_custom_nodes")
        row = col.row()
        row.prop(self, "set_compositing_nodes")
        row = col.row()
        row.prop(self, "set_material_nodes")
        row = col.row()
        row.prop(self, "set_texture_nodes")

def setNodeColourOption(setOption):
    """Enable/Disable the custom node colour for all nodes"""

    prefs = bpy.context.preferences.addons[__name__].preferences

    if prefs.set_compositing_nodes:
        for n in bpy.context.scene.node_tree.nodes:
            n.use_custom_color = setOption

    if prefs.set_custom_nodes:
        for ng in bpy.data.node_groups:
            for n in ng.nodes:
                n.use_custom_color = setOption

    if prefs.set_material_nodes:
        for mat in bpy.data.materials:
            if mat.node_tree and mat.node_tree.nodes:
                for n in mat.node_tree.nodes:
                    n.use_custom_color = setOption

    if prefs.set_texture_nodes:
        for tex in bpy.data.textures:
            if tex.node_tree and tex.node_tree.nodes:
                for n in tex.node_tree.nodes:
                    n.use_custom_color = setOption

class NodeColourOn(bpy.types.Operator):
    """Turn on custom node colour for all nodes"""
    bl_idname = "node.node_colour_on"
    bl_label = "Turn on all node colours"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'NODE_EDITOR'

    def execute(self, context):
        setNodeColourOption(True)
        return {'FINISHED'}

class NodeColourOff(bpy.types.Operator):
    """Turn off custom node colour for all nodes"""
    bl_idname = "node.node_colour_off"
    bl_label = "Turn off all node colours"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'NODE_EDITOR'

    def execute(self, context):
        setNodeColourOption(False)
        return {'FINISHED'}

class NodeColourPanel(bpy.types.Panel):
    bl_idname = "node_colour_panel"
    bl_label = "Node Colours"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    use_pin = True

    @classmethod
    def poll(cls, context):
        return context.area.type == 'NODE_EDITOR'

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        row = col.row()
        row.operator(NodeColourOn.bl_idname)
        row.operator(NodeColourOff.bl_idname)

def register():
    bpy.utils.register_class(NodeColourPreferences)
    bpy.utils.register_class(NodeColourOn)
    bpy.utils.register_class(NodeColourOff)
    bpy.utils.register_class(NodeColourPanel)

def unregister():
    bpy.utils.unregister_class(NodeColourPreferences)
    bpy.utils.unregister_class(NodeColourOn)
    bpy.utils.unregister_class(NodeColourOff)
    bpy.utils.unregister_class(NodeColourPanel)

if __name__ == "__main__":
    register()

