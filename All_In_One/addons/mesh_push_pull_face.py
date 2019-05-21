### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

# Contact for more information about the Addon:
# Email:    germano.costa@ig.com.br
# Twitter:  wii_mano @mano_wii

bl_info = {
    "name": "Push Pull Face",
    "author": "Germano Cavalcante",
    "version": (0, 1),
    "blender": (2, 75, 0),
    "location": "View3D > TOOLS > Tools > Mesh Tools > Add: > Extrude Menu (Alt + E)",
    "description": "Push and pull face entities to sculpt 3d models",
    #"wiki_url" : "http://blenderartists.org/forum/",
    "category": "Learnbgame"
}

import bpy
import bmesh

class Push_Pull_Face(bpy.types.Operator):
    """Push and pull face entities to sculpt 3d models"""
    bl_idname = "mesh.push_pull_face"
    bl_label = "Push/Pull Face"

    @classmethod
    def poll(cls, context):
        return context.mode is not 'EDIT_MESH'

    def execute(self, context):
        mesh = context.object.data
        bm = bmesh.from_edit_mesh(mesh)
        try:
            selection = bm.select_history[0]
        except:
            for face in bm.faces:
                if face.select == True:
                    selection = face
            #else:
                #selection = None
        if not isinstance(selection, bmesh.types.BMFace):
            raise SelectionError('The selection is not a face')
        else:
            face = selection
            geom = []
            for edge in face.edges:
                #print(edge.calc_face_angle()- 1.5707963267948966)
                if abs(edge.calc_face_angle(0) - 1.5707963267948966) < 0.001:
                    geom.append(edge)

            dict = bmesh.ops.extrude_discrete_faces(bm, faces = [face])
            bpy.ops.mesh.select_all(action='DESELECT')
            for face in dict['faces']:
                face.select = True
            bmesh.ops.dissolve_edges(bm, edges = geom, use_verts=True, use_face_split=False)
            bmesh.update_edit_mesh(mesh, tessface=True, destructive=True)
            bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=(False, False, True), constraint_orientation='NORMAL')
        return {'FINISHED'}

def operator_draw(self,context):
    layout = self.layout
    col = layout.column(align=True)
    col.operator("mesh.push_pull_face", text="Push/Pull Face")

def register():
    bpy.utils.register_class(Push_Pull_Face)
    bpy.types.VIEW3D_MT_edit_mesh_extrude.append(operator_draw)

def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_extrude.remove(operator_draw)
    bpy.utils.unregister_class(Push_Pull_Face)

if __name__ == "__main__":
    register()