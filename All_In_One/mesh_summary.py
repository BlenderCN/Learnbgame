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

# made in response to --
# from http://blender.stackexchange.com/q/13757/935

bl_info = {
    "name": "Mesh Summary",
    "author": "sambler",
    "version": (1,2),
    "blender": (2, 80, 0),
    "location": "Properties > Scene > Object Info Panel",
    "description": "Summarize details about the mesh objects in this file.",
    "warning": "",
    "wiki_url": "https://github.com/sambler/addonsByMe/blob/master/mesh_summary.py",
    "tracker_url": "https://github.com/sambler/addonsByMe/issues",
    "category": "Learnbgame",
}

import bpy
import bmesh
from bpy.props import IntProperty, BoolProperty
from operator import itemgetter

class MeshSummaryPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    display_limit : IntProperty(name="Display limit",
                        description="Maximum number of items to list",
                        default=5, min=2, max=20)
    calculate_modifier_verts : BoolProperty(name="Calculate mod. vertices",
                        description="Calculate vertex count after applying modifiers.",
                        default=False)

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        row = col.row()
        row.prop(self,"calculate_modifier_verts")
        row = col.row()
        row.prop(self, "display_limit")
        col = row.column() # this stops the button stretching

def us(qty):
    """
    Convert qty to truncated string with unit suffixes.
    eg turn 12345678 into 12.3M
    """

    if qty<1000:
        return str(qty)

    for suf in ['K','M','G','T','P','E']:
        qty /= 1000
        if qty<1000:
            return "%3.1f%s" % (qty, suf)

choice_types = [
    ('ALL','All','Show information for all mesh objects',1),
    ('SELECTED','Selected','Show information for selected mesh objects',2),
    ('VISIBLE','Visible','Show information for visible mesh objects',3),
    ]

class Properties_meshinfo(bpy.types.Panel):
    bl_label = "Mesh Information"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        prefs = context.preferences.addons[__name__].preferences
        layout = self.layout

        row = layout.row()
        row.prop(context.scene, 'show_choice', text='Show')

        if context.scene.show_choice == 'SELECTED':
            meshes = [o for o in context.scene.objects
                        if o.type == 'MESH' and o.select_get() == True]
            choice_desc = 'selected '
            total_desc = 'Selected Totals:'
        elif context.scene.show_choice == 'VISIBLE':
            meshes = [o for o in context.scene.objects
                        if o.type == 'MESH' and o.hide_viewport == False]
            choice_desc = 'visible '
            total_desc = 'Visible Totals:'
        else:
            meshes = [o for o in context.scene.objects if o.type == 'MESH']
            choice_desc = ''
            total_desc = 'Scene Totals:'

        row = layout.row()
        if len(meshes) == 1:
            row.label(text="1 {}mesh object in this scene.".format(choice_desc), icon='OBJECT_DATA')
        else:
            row.label(text=us(len(meshes))+" {}mesh objects in this scene.".format(choice_desc), icon='OBJECT_DATA')
            row = layout.row()
            if len(meshes) > prefs.display_limit:
                row.label(text="Top {} {}mesh objects.".format(prefs.display_limit,choice_desc))
            else:
                row.label(text="Top {} {}mesh objects.".format(len(meshes), choice_desc))

        row = layout.row()
        row.prop(prefs,"calculate_modifier_verts")

        if len(meshes) > 0:
            dataCols = []
            row = layout.row()
            dataCols.append(row.column()) # name
            dataCols.append(row.column()) # verts
            dataCols.append(row.column()) # verts after modifiers
            dataCols.append(row.column()) # edges
            dataCols.append(row.column()) # faces

            topMeshes = [(o, o.name, len(o.data.vertices), len(o.data.edges), len(o.data.polygons)) for o in meshes]
            topMeshes = sorted(topMeshes, key=itemgetter(2), reverse=True)[:prefs.display_limit]

            headRow = dataCols[0].row()
            headRow.label(text="Name")
            headRow = dataCols[1].row()
            headRow.label(text="Verts")
            headRow = dataCols[2].row()
            headRow.label(text="(mod.)")
            headRow = dataCols[3].row()
            headRow.label(text="Edges")
            headRow = dataCols[4].row()
            headRow.label(text="Faces")

            for mo in topMeshes:
                detailRow = dataCols[0].row()
                detailRow.label(text=mo[1])
                detailRow = dataCols[1].row()
                detailRow.label(text=us(mo[2]))
                if prefs.calculate_modifier_verts:
                    detailRow = dataCols[2].row()
                    bm = bmesh.new()
                    bm.from_object(mo[0], context.depsgraph)
                    detailRow.label(text="("+us(len(bm.verts))+")")
                    bm.free()
                detailRow = dataCols[3].row()
                detailRow.label(text=us(mo[3]))
                detailRow = dataCols[4].row()
                detailRow.label(text=us(mo[4]))

            vTotal = sum([len(o.data.vertices) for o in meshes])
            eTotal = sum([len(o.data.edges) for o in meshes])
            fTotal = sum([len(o.data.polygons) for o in meshes])

            totRow = dataCols[0].row()
            totRow.label(text=total_desc)
            totRow = dataCols[1].row()
            totRow.label(text=us(vTotal))
            totRow = dataCols[3].row()
            totRow.label(text=us(eTotal))
            totRow = dataCols[4].row()
            totRow.label(text=us(fTotal))

def register():
    bpy.utils.register_class(MeshSummaryPreferences)
    bpy.utils.register_class(Properties_meshinfo)
    bpy.types.Scene.show_choice = bpy.props.EnumProperty(items=choice_types, default='ALL')

def unregister():
    bpy.utils.unregister_class(MeshSummaryPreferences)
    bpy.utils.unregister_class(Properties_meshinfo)
    del bpy.types.Scene.show_choice

if __name__ == "__main__":
    register()
