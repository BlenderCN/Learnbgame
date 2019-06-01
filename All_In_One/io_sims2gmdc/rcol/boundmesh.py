'''
Copyright (C) 2018 SmugTomato

Created by SmugTomato

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import bpy
import bmesh


class BoundMesh:
    """Create a bounding mesh for a static object"""


    def __init__(self, vertices, faces):
        self.vertices = vertices
        self.faces    = faces


    @staticmethod
    def create(objects, decimate_amount=1.0, custom=False):
        # First deselect everything
        bpy.ops.object.select_all(action='DESELECT')

        vert_offset = 0
        vertices = []
        faces = []

        # If custom mesh exists, use it and skip next section
        if custom:
            mesh = custom.data
            for v in mesh.vertices:
                vertices.append((-v.co[0], -v.co[1], v.co[2]))

            for f in mesh.polygons:
                faces.append((f.vertices[0], f.vertices[1],f.vertices[2]))

            return BoundMesh(vertices, faces)


        # Select all non shadow mesh objects
        for ob in objects:
            # Skip shadow meshes
            if 'shadow' in ob.name:
                continue

            vert_offset = len(vertices)

            # Temporarily add decimate modifier
            ob.modifiers.new("dec", 'DECIMATE')
            ob.modifiers["dec"].ratio = decimate_amount
            ob.modifiers["dec"].use_collapse_triangulate = True

            # Make a clone of the mesh
            mesh = ob.to_mesh(bpy.context.scene, True, 'RENDER', False, False)

            # Remove decimate modifier now that the mesh is cloned
            ob.modifiers.remove( ob.modifiers["dec"] )

            # Add verts and faces to arrays
            for v in mesh.vertices:
                vertices.append((-v.co[0], -v.co[1], v.co[2]))

            for f in mesh.polygons:
                faces.append((
                    f.vertices[0] + vert_offset,
                    f.vertices[1] + vert_offset,
                    f.vertices[2] + vert_offset
                ))

            # Remove cloned mesh
            bpy.data.meshes.remove(mesh)

        return BoundMesh(vertices, faces)
