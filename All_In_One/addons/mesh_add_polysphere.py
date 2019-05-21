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
    "name": "Make PolySphere (Dynamic)",
    "author": "Dealga McArdle",
    "version": (0, 1, 0),
    "blender": (2, 6, 7),
    "location": "View3D > Add > Mesh > Add PolySphere",
    "description": "Adds polysphere you can update before finalizing",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Add Mesh"
}

import bpy, math
from bpy.props import *
from mathutils import Vector, Euler

def remap(value, low1, high1, low2, high2):
    return low2 + (value - low1) * (high2 - low2) / (high1 - low1)
 
def make_polysphere(self):
    
    # slider values to convenience variables
    radius = self.radius
    verts_per_side = self.verts_per_side
    factor = self.sphere_factor

    edge_per_side = verts_per_side - 1
    edge_length = (radius * 2) / edge_per_side

    idx = 0
    Verts, Faces = [], []
    
    eulers = [
        (0.0, 0.0, 0.0), # bottom
        (0.0, math.pi, 0.0), # top
        (math.pi/2, 0.0, 0.0), # side 1
        (-math.pi/2, 0.0, 0.0), # side 2
        (math.pi/2, 0.0, math.pi/2), # side 3
        (math.pi/2, 0.0, -math.pi/2) # side 4
    ]

    # make the cube
    for face, side_rotation in enumerate(eulers):

        for vert_u in range(verts_per_side):
            for vert_v in range(verts_per_side):
                p_x = -radius + (edge_length * vert_u)
                p_y = -radius + (edge_length * vert_v)
                p_z = -radius
                point = Vector((p_x, p_y, p_z))

                xz_euler = Euler(side_rotation, 'XYZ')
                point.rotate(xz_euler)

                Verts.append(point)
        
        
        for i in range(edge_per_side**2):
                
            x = (idx % edge_per_side)
            y = math.floor(idx / edge_per_side)

            level = x + (y*verts_per_side) + (face*verts_per_side)
            idx1 = level
            idx2 = level + 1
            idx3 = level + verts_per_side + 1
            idx4 = level + verts_per_side

            Faces.append([idx1, idx2, idx3, idx4])
            idx += 1

    # force to sphere
    Verts2 = []
    for vert in Verts:
        scaled = radius / vert.length
        # if factor = 0, scaled should be approach 1
        # if factor = 1, scaled should be untouched.
        final_scale = remap(factor, 0.0, 1.0, 1.0, scaled)
        Verts2.append(vert * final_scale)

    return Verts2, Faces
 
    
def create_mesh_object(context, verts, edges, faces, name):

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, edges, faces)
    mesh.update()

    from bpy_extras import object_utils
    return object_utils.object_data_add(context, mesh, operator=None)



class AddPolySphere(bpy.types.Operator):

    bl_idname = "mesh.polysphere_add"
    bl_label = "Add PolySphere"
    bl_options = {'REGISTER', 'UNDO'}

    # the max here is arbitrary, and is to avoid accidentally 
    # setting too high for CPU.
    verts_per_side = IntProperty(name="num profile verts",
        description="how many verts in profile shape",
        default=6, min=3, max=12)

    # these are arbitrary too, if you need higher just edit them
    # but using a scale factor might make more sense.
    radius = FloatProperty(name="radius",
        description="Distance from center to surface",
        default=1.0, min=0.01, max=10.0)

    # control how much to spherize the cube
    sphere_factor = FloatProperty(name="sphere factor",
        description="factor by which to spherize",
        default=1.0, min=0.0, max=1.0)

    def execute(self, context):

        # (hack)
        # this removes the existing mesh data, when user adjusts slider
        if context.object:
            bpy.ops.mesh.delete()

        # this deals with mesh repopulation
        verts, faces = make_polysphere(self)
        base = create_mesh_object(context, verts, [], faces, "PolySphere")
        # context.object.show_wire = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.remove_doubles(threshold=1.0e-5)
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator("mesh.polysphere_add", icon="PLUGIN")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)


if __name__ == "__main__":
    register()
