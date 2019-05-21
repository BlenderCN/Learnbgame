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
    "name": "Spring Coil",
    "author": "Dealga McArdle",
    "version": (0, 1, 0),
    "blender": (2, 6, 7),
    "location": "View3D > Add > Mesh > Add Spring",
    "description": "Add a coil/spring",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "https://gist.github.com/zeffii/5488993",
    "category": "Add Mesh"
}

import bpy
from bpy.props import *
from math import sin, cos, pi, atan2
from mathutils import Vector, Euler  
 
def make_coil(self):
    
    # variables and shortnames
    amp = self.profile_radius
    n_verts = self.num_verts
    n_turns = self.num_turns
    th = self.height / n_turns
    ipt = self.iterations_per_turn
    radius = self.coil_radius

    diameter = radius * 2
    two_pi = 2.0 * pi
    section_angle = two_pi / n_verts
    rad_slice = two_pi / ipt
    total_segments = (ipt * n_turns) + 1
    z_jump = self.height / total_segments

    x_rotation = atan2(th / 2, diameter)

    n = n_verts        
    Verts = []
    for segment in range(total_segments):
        rad_angle = rad_slice * segment    
    
        for i in range(n):
            
            # create the vector
            this_angle = section_angle * i
            x_float = amp * sin(this_angle) + radius
            z_float = amp * cos(this_angle)
            v1 = Vector((x_float, 0.0, z_float))
            
            # rotate it
            xz_euler = Euler((-x_rotation, 0.0, -rad_angle), 'XYZ')
            v1.rotate(xz_euler)
            
            # add extra z height per segment
            v1 += Vector((0, 0, (segment * z_jump)))
            
            # append it
            Verts.append(v1)
 
    Faces = []
    # skin it, normals facing outwards
    for t in range(total_segments-1):
        for i in range(n-1):
            p0 = i + (n*t) 
            p1 = i + (n*t) + 1
            p2 = i + (n*t + n) + 1 
            p3 = i + (n*t + n)
            Faces.append([p3,p2,p1,p0])
        p0 = n*t
        p1 = n*t + n
        p2 = n*t + (2 * n) - 1
        p3 = n*t + n-1
        Faces.append([p3,p2,p1,p0])
 
    return Verts, Faces
 
    
def create_mesh_object(context, verts, edges, faces, name):

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, edges, faces)
    mesh.update()

    from bpy_extras import object_utils
    return object_utils.object_data_add(context, mesh, operator=None)



class AddSpringObject(bpy.types.Operator):

    bl_idname = "mesh.spring_add"
    bl_label = "Add Spring"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    num_verts = IntProperty(name="num profile verts",
        description="how many verts in profile shape",
        default=12, min=3, max=30)

    profile_radius = FloatProperty(name="profile radius",
        description="Radius of profile shape",
        default=1.0, min=0.001, max=20.0)

    coil_radius = FloatProperty(name="coil radius",
        description="Coil radius measured from center of profile shape",
        default=4.0, min=0.001, max=20.0)

    iterations_per_turn = IntProperty(name="num segments per turn",
        description="how many profile segments per turn",
        default=20, min=4, max=30)

    num_turns = IntProperty(name="total turns in coil",
        description="how many turns in coil",
        default=4, min=1, max=30)

    height = FloatProperty(name="coil height",
        description="Coil height measured from first to last profile centers.",
        default=8.0, min=2.0, max=20.0)


    def execute(self, context):

        verts, faces = make_coil(self)
        base = create_mesh_object(context, verts, [], faces, "Spring")

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator("mesh.spring_add", icon="PLUGIN")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)


if __name__ == "__main__":
    register()

