#!BPY

bl_info = {
    "name": "Select Non-manifold edges",
    "author": "Yorik van Havre <yorik@uncreated.net>",
    "description": "Selects non-manifold edges in the active mesh object",
    "version": (0, 3),
    "blender": (2, 5, 6),
    "category": "Mesh",
    "location": "Mesh > Edges > Select non-manifold edges",
    "warning": '',
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/Modeling/Select_nonmanifold_edges",
    "tracker_url": "https://projects.blender.org/tracker/index.php?https://projects.blender.org/tracker/index.php?func=detail&aid=21421"
    }


# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See th
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****

import bpy

def search(mymesh):
        culprits=[]
        for e in mymesh.edges:
                e.select = False
                shared = 0
                for f in mymesh.faces:
                        for vf1 in f.vertices:
                                if vf1 == e.vertices[0]:
                                        for vf2 in f.vertices:
                                                if vf2 == e.vertices[1]:
                                                        shared = shared + 1
                if (shared > 2):
                        # edge is shared by more than 2 faces? it's non-manifold!
                        culprits.append(e)
                        e.select = True
                if (shared < 2):
                        # edge has only one face? it's open!
                        culprits.append(e)
                        e.select = True
        return culprits


#makes CheckManifolds an operator
class CheckManifolds(bpy.types.Operator):
    '''Checks a mesh for non-manifold edges.'''
    bl_idname = "mesh.select_nonmanifold_edges"
    bl_label = "Select Non-manifold edges"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
            # Get the active object
            ob_act = bpy.context.active_object
            if not ob_act or ob_act.type != 'MESH':
                    self.report({'ERROR'}, "No mesh selected!")
                    return {'CANCELLED'}
            # getting current edit mode
            currMode = ob_act.mode
            # switching to object mode and edge select
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.tool_settings.mesh_select_mode[1] = True
            bpy.context.tool_settings.mesh_select_mode[0] = False
            bpy.context.tool_settings.mesh_select_mode[2] = False
            mymesh = ob_act.data
            culprits = search(mymesh)
            if len(culprits) == 0:
                    self.report({'INFO'}, "This mesh is manifold, nothing selected")
            else:
                    self.report({'WARNING'}, str(len(culprits)) + " non-manifold edges found.")
            # restoring original editmode
            bpy.ops.object.mode_set(mode=currMode)
            return {'FINISHED'}

# Register the operator
def checkmanifolds_menu_func(self, context):
        self.layout.operator(CheckManifolds.bl_idname, text="Select non-manifold edges", icon='PLUGIN')

def register():
        # Add "Check Manifolds" menu to the "Mesh" menu.
        bpy.types.VIEW3D_MT_edit_mesh_edges.append(checkmanifolds_menu_func)

def unregister():
        # Remove "Check Manifolds" menu entry from the "Mesh" menu.
        bpy.types.VIEW3D_MT_edit_mesh_edges.remove(checkmanifolds_menu_func)

if __name__ == "__main__":
        register()

