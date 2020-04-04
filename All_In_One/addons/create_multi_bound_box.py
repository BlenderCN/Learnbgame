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
# http://blender.stackexchange.com/q/14070/935
#
# NOTE:
# Non-render objects have a zero size bounding box
# when only one of these objects is selected you will get
# a zero sized cube. Such as camera, lamp, lattice, armature, empty

bl_info = {
    "name": "Create multi Bounding Box",
    "author": "sambler",
    "version": (1,2),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > Create Bounding Box",
    "description": "Create an individual mesh cube matching the bounding box of each selected object",
    "warning": "",
    "wiki_url": "https://github.com/sambler/addonsByMe/blob/master/create_multi_bound_box.py",
    "tracker_url": "https://github.com/sambler/addonsByMe/issues",
    "category": "Learnbgame",
}

import bpy
import bmesh
from bpy.props import BoolProperty, FloatVectorProperty
import mathutils
from bpy_extras import object_utils

class CreateMultiBoundingBox(bpy.types.Operator, object_utils.AddObjectHelper):
    """Create a mesh cube that encompasses all selected objects"""
    bl_idname = "mesh.multi_boundbox_add"
    bl_label = "Create Multi Bounding Box"
    bl_description = "Create a bounding box around each selected object"
    bl_options = {'REGISTER', 'UNDO'}

    # generic transform props
    view_align : BoolProperty(
            name="Align to View",
            default=False,
            )
    location : FloatVectorProperty(
            name="Location",
            subtype='TRANSLATION',
            )
    rotation : FloatVectorProperty(
            name="Rotation",
            subtype='EULER',
            )

    @classmethod
    def poll(cls, context):
        if len(context.selected_objects) == 0:
            return False
        return True

    def execute(self, context):

        workobjs = [o.name for o in bpy.context.selected_objects]
        faces = [(0, 1, 2, 3),
                 (4, 7, 6, 5),
                 (0, 4, 5, 1),
                 (1, 5, 6, 2),
                 (2, 6, 7, 3),
                 (4, 0, 3, 7),
                ]

        for objname in workobjs:
            obj = bpy.data.objects[objname]
            mesh = bpy.data.meshes.new("BoundingBox")
            bm = bmesh.new()
            for v_co in obj.bound_box:
                bm.verts.new(v_co)

            bm.verts.ensure_lookup_table()

            for f_idx in faces:
                bm.faces.new([bm.verts[i] for i in f_idx])

            bm.to_mesh(mesh)
            mesh.update()

            self.location = obj.location
            self.rotation = obj.rotation_euler
            bbox = object_utils.object_data_add(context, mesh, operator=self)
            # does a bounding box need to display more than the bounds??
            bbox.display_type = 'BOUNDS'
            bbox.scale = obj.scale
            bbox.hide_render = True

        return {'FINISHED'}

def menu_boundbox(self, context):
    self.layout.operator(CreateMultiBoundingBox.bl_idname, text=CreateMultiBoundingBox.bl_label, icon="PLUGIN")

def register():
    bpy.utils.register_class(CreateMultiBoundingBox)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_boundbox)

def unregister():
    bpy.utils.unregister_class(CreateMultiBoundingBox)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_boundbox)

if __name__ == "__main__":
    register()
