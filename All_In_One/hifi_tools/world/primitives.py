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

# Primitive Logic for Content from High Fidelity to match source.
# By Matti 'Menithal' Lahtinen


import bpy

import addon_utils

# Utility Script to debug selected edges
def debug_get_selected_edges():
    edges = bpy.context.active_object.data.edges
    selected_edges = []
    
    for idx, edge in enumerate(edges):
        if edge.select == True:
            selected_edges.append(idx)
            
    print('Selected Edges: ', selected_edges)

# Utility Script to debug selected edges
def debug_get_selected_face():
    faces = bpy.context.active_object.data.polygons
    selected_polys = []
    
    for idx, face in enumerate(faces):
        if face.select == True:
            selected_polys.append(idx)
            
    print('Selected Polygons: ', selected_polys)
    
# Utility to select Polygons from the uv_array
def select_polygons(uv_array):    
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_mode(type="FACE")
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')

    polygons = bpy.context.active_object.data.polygons

    for polygon in uv_array:
        polygons[polygon].select = True
        
        
# Utility to select Edges from the uv_array
def select_edges(uv_array):
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_mode(type="EDGE")
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')

    edges = bpy.context.active_object.data.edges

    for edge in uv_array:
        edges[edge].select = True


# Utility to mark selected and then unwrap
def mark_seams_and_uv_unwrap():
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.mark_seam(clear=False)
    bpy.ops.mesh.select_all(action = 'SELECT')
    
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
    
    bpy.context.area.type = 'IMAGE_EDITOR'
    bpy.context.space_data.cursor_location[0] = 0
    bpy.context.space_data.cursor_location[1] = 0
    
    
def ___empty():
    pass

# Utility Set Generics (position, dimensions, and rotation). Then has calls a callback if there are any custom UV unwrap
def set_generic(entity, split = False, entity_specific_uv = ___empty):
    
    entity.blender_object = bpy.context.active_object
    
    # Make sure non Mesh objects do not trip there.
    if entity.blender_object.type == "MESH":
        bpy.ops.object.mode_set(mode = 'EDIT') 
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent()
        if split:  
            bpy.ops.mesh.select_mode(type="EDGE")
            bpy.ops.mesh.mark_sharp()    
            bpy.ops.mesh.select_all(action = 'DESELECT')
        
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.context.object.name = entity.name
    
    # Reset                
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    # Reset "Scale" to ready up pivot point
    bpy.context.object.dimensions = (1,1,1)
    
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # Create Pivot point
    bpy.context.object.location = entity.pivot
    
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    ## Execute Entity specific UV Mapping here
    
    context_area = bpy.context.area.type
    entity_specific_uv()    
    ## Back to generic
    bpy.context.area.type = context_area
    
    bpy.ops.object.mode_set(mode = 'OBJECT')
    
    bpy.context.object.dimensions = entity.dimensions
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)
    bpy.context.object.location = entity.relative_position()
    
    bpy.context.object.rotation_mode = 'QUATERNION'
    bpy.context.object.rotation_quaternion = entity.relative_rotation()
    
    if hasattr(entity, 'material') and entity.material is not None:
        bpy.context.object.data.materials.append(entity.material)
    


def add_box(entity):
    bpy.ops.mesh.primitive_cube_add(location=(0,0,0), enter_editmode=True, calc_uvs=True)
    
    set_generic(entity, True)
    
    return bpy.context.active_object


def add_light(entity):
    bpy.ops.object.lamp_add(type='POINT', radius=1, view_align=False, location=(0, 0, 0))
    
    set_generic(entity)
    bpy.context.object.data.distance = entity.dimensions.length

    return bpy.context.active_object


def add_tetrahedron(entity):
    bpy.ops.mesh.generate_geodesic_dome(base_type='Tetrahedron', orientation='EdgeUp', geodesic_class='Class 1')

    bpy.context.object.rotation_euler[2] = 0.785398
    
    def uv():
        select_edges([0, 1,2])
        mark_seams_and_uv_unwrap()

    set_generic(entity, True, uv)
    
    return bpy.context.active_object
    
    
def add_octahedron(entity):
    bpy.ops.mesh.primitive_solid_add(source='8')

    def uv():
        select_edges([6,7,8,10])
        mark_seams_and_uv_unwrap()
        
    set_generic(entity, True, uv)
    
    
    return bpy.context.active_object


def add_icosahedron(entity):
    bpy.ops.mesh.generate_geodesic_dome(geodesic_types='Geodesic', orientation='EdgeUp', base_type='Icosahedron', geodesic_class='Class 1')
    
    def uv():
        bpy.ops.object.mode_set(mode = 'EDIT') 
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.cylinder_project(direction="VIEW_ON_POLES",scale_to_bounds=True, align='POLAR_ZY')

        
    set_generic(entity, True, uv)
    
    return bpy.context.active_object

    
def add_docadehedron(entity):
    bpy.ops.mesh.primitive_solid_add(source='12')
    bpy.ops.transform.rotate(value=1.5708, axis=(0, 0, 1), constraint_axis=(False, False, True), constraint_orientation='GLOBAL')
    
    def uv():
        bpy.ops.object.mode_set(mode = 'EDIT') 
        select_edges([0, 1, 3, 4, 6, 7, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 31, 32, 33, 34, 37, 39, 40])
        
        bpy.ops.object.mode_set(mode = 'EDIT') 
        bpy.ops.mesh.mark_sharp()
        
        mark_seams_and_uv_unwrap()
        
        bpy.ops.object.mode_set(mode = 'OBJECT') 
        
    set_generic(entity, False ,uv)
    
    return bpy.context.active_object


def add_quad(entity):
    bpy.ops.mesh.primitive_plane_add(radius=1,  location=(0, 0, 0),  calc_uvs=True)
    set_generic(entity, True)
    
    return bpy.context.active_object


def add_circle(entity):
    bpy.ops.mesh.primitive_circle_add(view_align=False, enter_editmode=True, location=(0, 0, 0))
    bpy.ops.mesh.edge_face_add()
    set_generic(entity, True)
    
    return bpy.context.active_object


def add_cone(entity):   
    bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2, view_align=False, enter_editmode=False, location=(0, 0, 0), calc_uvs=True)
    
    def sharp():
            bpy.ops.object.mode_set(mode = 'OBJECT')
            select_polygons([32])
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.mark_sharp()

    set_generic(entity, False, sharp)
    
    return bpy.context.active_object


def add_cylinder(entity):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, location=(0,0,0), calc_uvs=True)
    
    def sharp():
        bpy.ops.object.mode_set(mode = 'OBJECT')
        select_polygons([30, 33])
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.mark_sharp()

    
    set_generic(entity, False, sharp)
    
    return bpy.context.active_object


def add_hexagon(entity):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, location=(0,0,0), calc_uvs=True)
      
    set_generic(entity, True)
    
    return bpy.context.active_object


def add_triangle(entity):
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, location=(0,0,0), calc_uvs=True)
    bpy.ops.transform.rotate(value=-1.5708, axis=(0, 0, 1), constraint_axis=(False, False, True), constraint_orientation='GLOBAL')

    set_generic(entity, True)
    
    return bpy.context.active_object


def add_octagon(entity):
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, location=(0,0,0), enter_editmode=True, calc_uvs=True)
    
    set_generic(entity, True)
    
    return bpy.context.active_object

def add_uv_sphere(entity):
    bpy.ops.mesh.primitive_uv_sphere_add(location=(0,0,0), enter_editmode=False, calc_uvs=True)
    bpy.ops.object.mode_set(mode = 'EDIT')
    
    bpy.ops.mesh.faces_shade_smooth()
    
    set_generic(entity, False)
    
    return bpy.context.active_object

def add_sphere(entity):
    bpy.ops.mesh.primitive_cube_add(location=(0,0,0), enter_editmode=False, calc_uvs=True)
    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.context.object.modifiers["Subsurf"].levels = 3
    bpy.context.object.modifiers["Subsurf"].use_subsurf_uv = False

    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")
    bpy.ops.object.modifier_add(type='SMOOTH')
    bpy.context.object.modifiers["Smooth"].factor = 3.5
    bpy.context.object.modifiers["Smooth"].iterations = 1

    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Smooth")
    bpy.ops.object.mode_set(mode = 'EDIT')
    
    bpy.ops.mesh.faces_shade_smooth()
    
    set_generic(entity, False)
    
    return bpy.context.active_object
