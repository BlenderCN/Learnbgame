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

import math
from bisect import bisect_left
import logging
import json

import bpy
import bmesh
import blf
from bpy.types import Operator
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       BoolVectorProperty,
                       PointerProperty,
                       CollectionProperty,
                       EnumProperty)
from bpy_extras import view3d_utils
from mathutils import Vector, Matrix

from molblend.elements_default import ELEMENTS as ELEMENTS_DEFAULT

logger = logging.getLogger(__name__)

class enums():
    object_types = [
        ('NONE', "None", "None"),
        ('ATOM', "Atom", "Atom"),
        ('BOND', "Bond", "Bond"),
        ('UC', "Unit cell", "Unit cell"),
        ('DIPOLE', "Dipole", "Dipole"),
        ('MODE_ARROW', "Mode arrow", "Mode arrow"),
        ('PARENT', "Parent", "Parent"),
        ]
    mesh_types = [
        ('NONE', "None", "None"),
        ('ELEMENT', "Element", "Element"),
        ('BOND', "Bond", "Bond"),
        ]
    text_types = [
        ('NONE', "None", "None"),
        ('MODES', "Modes", "Modes"),
        ]
    radius_types = [
        ('covalent', 'covalent', 'covalent'),
        ('vdw', 'van der Waals', 'van der Waals'),
        ('constant', 'constant', 'constant'),
        ]
    molecule_styles = [
        ('BALLS', 'Balls', 'Space filling'),
        ('BAS', 'Balls and Sticks', 'Balls and Sticks'),
        ('STICKS', 'Sticks', 'Sticks'),
        ]
    bond_material = [
        ('ATOMS', "Atoms", "Same as atoms"),
        ('GENERIC', "Generic" , "Single bond color"),
        ]
    bond_types = [
        ('CONSTRAINT', "constraint", "constrained by the two bonded atoms"),
        ('STATIC', "static", "independent bonds, don't move with atoms"),
        ]
    geometries = [
        ('NONE', "None", "No geometry constraints"),
        ('GENERAL', "General", 
         "Angles are multiples of 30 and 45 deg. in the view plane"),
        ('LINEAR', "Linear", "Linear or sp"),
        ('TRIGONAL', "Trig. planar", "Trigonal planar or sp2"),
        ]
    angstrom_per_unit = [
        ('1.0', "Angstrom", "Angstrom"),
        ('0.529177249', "Bohr", "Bohr"),
        ('0.01', "pm", "Picometer"),
        ('OTHER', "Other", "Custom Unit"),
        ]
    file_types = [
        ('XYZ', "xyz", "xyz format"),
        ('PDB', "pdb", "Protein Databank format"),
        ('B4W', "b4w", "standalone HTML with embedded 3D viewer")
        ]
    mode_file_format = [
        ('ANADDB', "anaddb", "Abinit/anaddb output"),
        ('QE_DYNMAT', "QE dynmat", "Quantum ESPRESSO output"),
        ('XYZ', "xyz", "xyz-style format"),
        ('PHONOPY', "phonopy", "phonopy/v_sim ascii format"),
        ]
    iso_val = [
        ('VOLFRAC', "volume fraction", "iso value by fraction of volume"),
        ('ABSOLUTE', "absolute value", "iso value by absolute value in cube file"),
        ]


#--- Update functions --------------------------------------------------------#

def update_all_meshes(self, context):
    if context.scene.mb.is_initialized:
        # TODO this callback might be too heavy for scenes with lots of meshes
        for me in bpy.data.meshes:
            me.update()

def update_active_mode(self, context):
    if len(self.qvecs) == 0:
        if context.screen.is_animation_playing:
            bpy.ops.screen.animation_play()
            context.scene.frame_current = 1
        return
    
    if self.active_mode == 0:
        self['mode']['freq'] = 'equilibrium'
    else:
        try:
            qpt = json.loads(self.qvecs[self.active_nqpt].mode_txt.as_string())
            self['mode'] = qpt['modes'][self.active_mode-1]
        except:
            logger.error("Problem loading mode from text object.")
            logger.exception("")
            if self.active_mode == 0:
                return
            else:
                self.active_mode = 0
                return
    
    if self.active_mode > 0 and self.active_mode > len(qpt['modes']):
        self.active_mode = len(qpt['modes']) - 1
        # since this calls this callback again, return
        return
    
    for atom in self.objects.atoms:
        update_mode_action(atom, self)
    
    if (self.active_mode == 0 or not self.autoplay_mode_animation):
        # stop animation
        if context.screen.is_animation_playing:
            bpy.ops.screen.animation_play()
        context.scene.frame_current = 1
    else:
        # start animation
        if not context.screen.is_animation_playing:
            context.scene.frame_end = 20
            bpy.ops.screen.animation_play()
    

def update_show_mode_arrows(self, context):
    bpy.ops.mb.toggle_mode_arrows('INVOKE_DEFAULT')

def update_show_unit_cell_arrows(self, context):
    bpy.ops.mb.toggle_unit_cell_arrows('INVOKE_DEFAULT')

def update_show_unit_cell_frame(self, context):
    bpy.ops.mb.toggle_unit_cell_frame('INVOKE_DEFAULT')

def update_atom_element(self, context):
    '''
    assign a mesh, give a new object name etc.
    '''
    # remove all spaces
    if self.element.strip() != self.element:
        self.element = self.element.strip()
        return
    # Comparison is case insensitive
    # get dictionary that maps all lower case elements to exact upper/lower 
    # case as it appears in the list
    elements_map = dict([(element.name.lower(), element.name)
                         for element in context.scene.mb.elements])
    # if element is not yet in scene elements list, add new element. 
    # Use default settings
    if self.element.lower() not in elements_map:
        add_element(context, self.element, ELEMENTS_DEFAULT["Default"])
    # adjust case of entered element to match already existing element
    elif self.element not in elements_map.values():
        self.element = elements_map[self.element.lower()]
        # because this assignment calls this function again, just return
        return
    
    # get object and molecule to change all element specific properties
    atom_ob = self.object
    molecule = self.get_molecule()
    
    # update mesh and material
    me = get_atom_data(self.element, molecule)
    atom_ob.data = me
    assign_atom_material(atom_ob, molecule)
    
    set_atom_drivers(context, atom_ob, molecule)
    
    # update bond materials
    for bond in self.bonds:
        assign_bond_material(bond)
    
    # assign type last, to be able to check if element is newly assigned or
    # just updated
    self.type = 'ATOM'


def update_bond_material(self, context):
    for bond in self.objects.bonds:
        assign_bond_material(bond)


def update_refine_atoms(self, context):
    if self.refine_atoms < 2:
        self.refine_atoms = 2
        return
    replaced_elements = set()
    for mesh in self.meshes:
        if mesh.data.mb.type == "ELEMENT":
            element = mesh.name
            #if not element in replaced_elements:
            data = mesh.data
            # get new temporary atom mesh with new refine value
            new_data = get_atom_data(element, self, type='MESH', 
                                        mesh_name="tmp_mesh")
            # replace mesh data
            bm = bmesh.new()
            bm.from_mesh(new_data)
            bm.to_mesh(data)
            bm.free()
            replaced_elements.add(element)
            # delete temporary mesh
            bpy.data.meshes.remove(new_data)


def update_refine_bonds(self, context):
    if self.refine_bonds < 2:
        self.refine_bonds = 2
        return
    mesh = self.meshes.get("bond")
    if mesh:
        data = mesh.data
        # get new temporary bond mesh with new refine value
        name = "tmp_mesh"
        new_data = get_bond_data(self, type='MESH', mesh_name="tmp_mesh")
        # replace mesh data
        bm = bmesh.new()
        bm.from_mesh(new_data)
        bm.to_mesh(data)
        bm.free()
        # delete temporary mesh
        bpy.data.meshes.remove(new_data)


def update_export_file_type(self, context):
    """
    Change file extension when filetype is changed. Replace known extensions.
    Append to everything else.
    """
    if self.filepath:
        filetypes = {'XYZ': ".xyz",
                     'PDB': ".pdb"}
        ext = filetypes[self.file_type]
        other_ext = [f for f in filetypes.values() if f != ext]
        
        if self.filepath[-4:] in other_ext:
            self.filepath = self.filepath[:-4] + ext
        else:
            self.filepath = self.filepath + ext


def update_show_bond_lengths(self, context):
    if self.show_bond_lengths:
        bpy.ops.mb.show_bond_lengths()


def update_show_bond_angles(self, context):
    if self.show_bond_angles:
        bpy.ops.mb.show_bond_angles()


def update_radius_type(self, context):
    for atom in self.objects.atoms:
        set_atom_drivers(context, atom, self)


def update_draw_style(self, context):
    for atom in self.objects.atoms:
        set_atom_drivers(context, atom, self)
    
    hide = (self.draw_style == 'BALLS')
    for bond in self.objects.bonds:
        bond.hide = hide


#--- General functions -------------------------------------------------------#

def callback_draw_length(self, context):
    try:
        font_id = 0
        blf.size(font_id, context.scene.mb.globals.bond_length_font_size, 72)
        offset = 0
        
        rv3d = context.space_data.region_3d
        width = context.region.width
        height = context.region.height
        persp_mat = rv3d.perspective_matrix
        persinv = persp_mat.inverted()
        
        for ob in context.selected_objects:
            if ob.mb.type == "BOND":
                locs = [o.mb.world_location for o in ob.mb.bonded_atoms]
                co_3d = (locs[0] + locs[1]) / 2.
                prj = persp_mat * co_3d.to_4d()
                x = width/2 + width/2 * (prj.x / prj.w)
                y = height/2 + height/2 * (prj.y / prj.w)
                blf.position(font_id, x, y, 0)
                blf.draw(font_id, "{:6.4f}".format((locs[1]-locs[0]).length))
        #ob = context.object
        #if ob.type == "MESH":
            #for v in ob.data.vertices:
                #prj = persp_mat * v.co.to_4d()
                #x = width/2 + width/2 * (prj.x / prj.w)
                #y = height/2 + height/2 * (prj.y / prj.w)
                #blf.position(font_id, x, y, 0)
                #blf.draw(font_id, "{}".format(v.index))
                
    except:
        logger.exception('')
        context.scene.mb.globals.show_bond_lengths = False

def add_element(context, element, element_dict):
    '''
    add element data to scene
    '''
    default = ELEMENTS_DEFAULT["Default"]
    
    new = context.scene.mb.elements.add()
    new.name = element
    new.element = element
    new.element_name = element_dict.get("element name", 
                                        default["element name"])
    new.atomic_number = element_dict.get("atomic number", 
                                         default["atomic number"])
    new.color = element_dict.get("color", default["color"])
    new.covalent = element_dict.get("covalent", default["covalent"])
    if "vdw1" in element_dict or "vdw2" in element_dict:
        new.vdw = (element_dict["vdw1"] if element_dict["vdw1"] != 0.0 
                   else (element_dict["vdw2"] if element_dict["vdw2"] != 0.0 
                         else element_dict["covalent"]))
    else:
        new.vdw = element_dict.get("covalent", default["covalent"])
    new.constant = 1.0
    return new


def initialize_elements(context):
    for element, data in ELEMENTS_DEFAULT.items():
        add_element(context, element, data)


#--- Viewport functions ------------------------------------------------------#

def get_region_data(context, x, y):
    
    for area in context.screen.areas:
        if area.type != 'VIEW_3D':
            continue
        is_quadview = len(area.spaces.active.region_quadviews) != 0
        i = -1
        for region in area.regions:
            if region.type == 'WINDOW':
                i += 1
                if (x > region.x and
                    y > region.y and
                    x < region.width + region.x and
                    y < region.height + region.y):
                    
                    if is_quadview:
                        rv3d = area.spaces.active.region_quadviews[i]
                    else:
                        rv3d = area.spaces.active.region_3d
                    return (region, rv3d)
    return (None, None)

def mouse_2d_to_location_3d(context, mouse2d, depth=Vector((0, 0, 0)),
                            region=None, rv3d=None):
    x, y = mouse2d
    
    # Get region and region data from mouse position.
    # If region is given, passed rv3d is ignored.
    if region == None:
        region, rv3d = get_region_data(context, x, y)
    
    # mouse coordinates relative to region
    coord2d = (x - region.x, y - region.y)
    if depth:
        depth_location = depth
    else:
        depth_location = context.scene.cursor_location.copy()
    return view3d_utils.region_2d_to_location_3d(region, rv3d, coord2d, 
                                                 depth_location)


def return_cursor_object(context, event, ray_max=10000.0, exclude=None, 
                         mb_type=''):
    """ This is a function that can be run from a modal operator
        to select the 3D object the mouse is hovered over.
    """
    exclude = exclude or []
    # get the context arguments
    scene = context.scene
    x, y = event.mouse_x, event.mouse_y
    region, rv3d = get_region_data(context, x, y)
    if not rv3d:
        return None
    coord2d = (x - region.x, y - region.y)
    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord2d)
    
    # have ray origin a little in front of actual origin, otherwise it might 
    # not get all of the objects
    ray_origin = (view3d_utils.region_2d_to_origin_3d(region, rv3d, coord2d) +
                  0.5 * view_vector * ray_max)
    ray_target = ray_origin - (view_vector * ray_max)
    
    def visible_objects_and_duplis():
        """Loop over (object, matrix) pairs (mesh only)"""
        for obj in context.visible_objects:
            if obj.type == 'MESH':
                if (mb_type and mb_type == obj.mb.type) or mb_type == '':
                    yield (obj, obj.matrix_world.copy())

    def obj_ray_cast(obj, matrix):
        """Wrapper for ray casting that moves the ray into object space"""
        try:
            # get the ray relative to the object
            matrix_inv = matrix.inverted()
            ray_origin_obj = matrix_inv * ray_origin
            ray_target_obj = matrix_inv * ray_target
            
            # cast the ray
            result, hit, normal, face_index = obj.ray_cast(ray_origin_obj, 
                                                           ray_target_obj)
            if face_index != -1:
                return hit, normal, face_index
            else:
                return None, None, None
        except ValueError as e:
            logger.error("in obj_ray_cast: {}: {}".format(obj.name, e))
            return None, None, None
        finally:
            pass

    # cast rays and find the closest object
    best_length_squared = ray_max * ray_max
    best_obj = None
    for obj, matrix in visible_objects_and_duplis():
        if obj not in exclude and obj.type == 'MESH':
            if len(obj.data.vertices) >= 4:
                hit, normal, face_index = obj_ray_cast(obj, matrix)
                if hit is not None:
                    hit_world = matrix * hit
                    length_squared = (hit_world - ray_origin).length_squared
                    if length_squared < best_length_squared:
                        best_length_squared = length_squared
                        best_obj = obj
    # now we have the object under the mouse cursor,
    # we could do lots of stuff but for the example just select.
    return best_obj

def check_ob_dimensions(ob):
    if ob.dimensions.x < 0.0001: #< ob.mb.get_molecule().bond_radius:
        toggle = {'PLANE_X': 'PLANE_Z', 'PLANE_Z': 'PLANE_X'}
        c = ob.constraints.get("mb.stretch", None)
        if c:
            c.keep_axis = toggle[c.keep_axis]

#--- Add object functions ----------------------------------------------------#
def get_atom_id(mol_name, atom_index):
    return "{}.{:>04d}".format(mol_name, atom_index)

def add_atom(context, location, element, atom_name, atom_index, molecule):
    # get new unique name for object
    name = "atom_{}".format(get_atom_id(molecule.name, atom_index))
    mesh_data = get_atom_data(element, molecule)
    new_atom = bpy.data.objects.new(name, mesh_data)
    context.scene.objects.link(new_atom)
    new_atom.location = location
    
    # set mb properties
    new_atom.mb.name = new_atom.name
    new_atom.mb.atom_name = atom_name
    
    # parent to molecule origin
    new_atom.parent = molecule.objects.parent
    new_atom.mb.parent = molecule.objects.parent
    
    # updating the element will call update_atom_element, which assigns a mesh,
    # and sets all the drivers
    new_atom.mb.element = element
    # add atom object and mesh to molecule collections
    molecule.add_object(new_atom)
    
    return new_atom


def add_bond(context, first_atom, second_atom, bond_type="CONSTRAINT"):
    if first_atom == second_atom:
        logger.warning('add_bond: first_atom == second_atom')
        return None
    for b in first_atom.mb.bonds:
        if b != None:
            for ba in b.mb.bonded_atoms:
                if ba == second_atom:
                    logger.warning(
                        "add_bond: Bond {}-{} already exists".format(
                            first_atom.mb.index, second_atom.mb.index),
                        )
                    return None
    # get new unique name for bond
    first_mol = first_atom.mb.get_molecule()
    second_mol = second_atom.mb.get_molecule()
    name = "bond_{}-{}".format(
        get_atom_id(first_mol.name, first_atom.mb.index), 
        get_atom_id(second_mol.name, second_atom.mb.index)
        )
    bond_mesh = get_bond_data(first_mol)
    new_bond = bpy.data.objects.new(name, bond_mesh)
    context.scene.objects.link(new_bond)
    new_bond.hide = (first_mol.draw_style == 'BALLS')
    
    # set mb properties
    new_bond.mb.type = 'BOND'
    new_bond.mb.name = new_bond.name
    new_bond.mb.add_bonded_atom(first_atom)
    new_bond.mb.add_bonded_atom(second_atom)
    
    # add bond to atoms mb props
    first_atom.mb.add_bond(new_bond)
    second_atom.mb.add_bond(new_bond)
    
    # add it to first molecule collection
    first_mol.add_object(new_bond)
    new_bond.mb.parent = first_mol.objects.parent

    if bond_type == "CONSTRAINT":
        # don't parent, as parenting also affects the scale
        c = new_bond.constraints.new('COPY_LOCATION')
        c.name = "mb.parent"
        c.target = first_atom
        
        c = new_bond.constraints.new('STRETCH_TO')
        c.name = "mb.stretch"
        c.rest_length = 1.0
        c.volume = 'NO_VOLUME'
        c.target = second_atom

    elif bond_type == "STATIC":
        y_axis = Vector((0,1,0))
        loc1 = first_atom.location
        loc2 = second_atom.location
        # Location
        location = loc1
        vec = (loc2 - loc1)
        angle = vec.angle(y_axis, 0)
        # vector of rotation
        axis = y_axis.cross(vec)
        new_bond.rotation_euler = Matrix.Rotation(angle, 4, axis).to_euler()
        new_bond.location = loc1
        new_bond.scale[1] = vec.length
        
    assign_bond_material(new_bond)
    set_bond_drivers(context, new_bond, new_bond.mb.get_molecule())
    new_bond.parent = first_mol.objects.parent
    
    return new_bond


#--- Get Mesh functions ------------------------------------------------------#

def get_atom_data(element, molecule, type='MESH', mesh_name=""):
    """
    Retrieve mesh for a certain element. If mesh_name is given, the mesh is 
    retrieved from bpy.data.meshes if it exists, or created and assigned that
    name. Otherwise the mesh is retrieved from molecule.meshes.
    """
    if type == 'MESH':
        if mesh_name:
            me = bpy.context.blend_data.meshes.get(mesh_name)
        else:
            element = element.capitalize()
            atom_name = "atom_mesh_{}.{}".format(molecule.name, element)
            item = molecule.meshes.get(element)
            if item:
                me = item.data
            else:
                me = None
        if not me:
            # save last selection to restore later
            selected = bpy.context.selected_objects
            last_active = bpy.context.object
            
            refine = molecule.refine_atoms
            # create uv sphere and get mesh data
            bpy.ops.mesh.primitive_uv_sphere_add(
                location=(0,0,0), segments=refine*2, ring_count=refine)
            new_atom = bpy.context.object
            bpy.ops.object.shade_smooth()
            me = new_atom.data
            me.name = mesh_name or atom_name
            me.mb.type = "ELEMENT"
            if not mesh_name:
                item = molecule.meshes.add()
                item.name = element
                item.data = me
            # adds material slot to mesh, but don't assign material yet
            new_atom.data.materials.append(None)
            
            # finally delete object and return mesh data
            bpy.context.scene.objects.unlink(new_atom)
            bpy.data.objects.remove(new_atom)
            
            # restore old selection
            for o in selected:
                o.select = True
            bpy.context.scene.objects.active = last_active
        return me

def get_bond_data(molecule, type='MESH', mesh_name=""):
    new_bond = None
    if type == 'MESH':
        if mesh_name:
            me = bpy.context.blend_data.meshes.get(mesh_name)
        else:
            bond_name = "bond"
            item = molecule.meshes.get(bond_name)
            if item:
                me = item.data
            else:
                me = None
        if not me:
            # save last selection to restore later
            selected = bpy.context.selected_objects
            last_active = bpy.context.object
            
            bpy.ops.mesh.primitive_cylinder_add(
                location=(0,0,0), vertices=molecule.refine_bonds*2, 
                depth=1, radius=1.0)#, end_fill_type="NOTHING")
            new_bond = bpy.context.object
            for i in range(2):
                new_bond.data.materials.append(None)
            
            me = new_bond.data
            me.name = mesh_name or "bond_mesh_{}".format(molecule.name)
            me.mb.type = "BOND"
            bm = bmesh.new()
            bm.from_mesh(me)
            
            # rotate and shrink first, then add another row of vertices
            for vert in bm.verts:
                # rotate 90 degrees around x, and shift along y axis
                tmp_co = vert.co.copy()
                vert.co.y = -tmp_co.z + .5
                vert.co.z = -tmp_co.y
                if vert.co.y > 0.01:
                    vert.select = False
            new_verts = []
            bm.edges.ensure_lookup_table()
            for edge in bm.edges:
                if abs(edge.verts[0].co.y - edge.verts[1].co.y) > .5:
                    #if hasattr(edge, "ensure_lookup_table"):
                        #edge.ensure_lookup_table()
                    e, v = bmesh.utils.edge_split(edge, edge.verts[0], 0.5)
                    new_verts.append(v)
            n_verts = len(new_verts)
            
            # bad hack, but don't understand how bmesh.utils.face_split works
            # remove all faces
            for f in bm.faces:
                bm.faces.remove(f)
            # now sort bm.verts
            # v.co.y is either 0, 0.5, or 1.0. 
            # So multiply y with at least 4pi to sort by y value first
            key = lambda v: v.co.y * 15 + math.atan2(v.co.x, v.co.z)
            verts_sorted = sorted((v for v in bm.verts), key=key)
            for i, v in enumerate(verts_sorted):
                v.index = i
            
            # add new faces and assign the two different material slots
            for i in range(2*n_verts):
                v1 = verts_sorted[i]
                v2 = verts_sorted[(i + 1)%n_verts + n_verts*(i//n_verts)]
                v3 = verts_sorted[(i + 1)%n_verts + n_verts*(i//n_verts + 1)]
                v4 = verts_sorted[i + n_verts]
                f = bm.faces.new((v1, v2, v3, v4))
                f.material_index = i//n_verts # gives 0 or 1
                f.smooth = True
            
            # again, sort by center.y first, than angle
            key = lambda f: (f.calc_center_median().y * 15 +
                             math.atan2(f.normal.x, f.normal.z))
            half_faces = len(bm.faces)/2
            for i, f in enumerate(sorted((f for f in bm.faces), key=key)):
                f.index = i
            
            bm.to_mesh(me)
            bm.free()
            me.update()
    
            # finally delete object and reselect old selection
            bpy.context.scene.objects.unlink(new_bond)
            bpy.data.objects.remove(new_bond)
            for o in selected:
                o.select = True
            bpy.context.scene.objects.active = last_active
            if not mesh_name:
                item = molecule.meshes.add()
                item.name = bond_name
                item.data = me
    return me


def get_arrow_data(type='MESH', name="arrow",
                   radius = 0.1, ring_y = 0.9, ring_scale = 2):
    if type == 'MESH':
        data = bpy.context.blend_data.meshes.get(name)
        if not data:
            # Make arrow mesh
            bpy.ops.mesh.primitive_cylinder_add(
                location=(0,0,0), radius=radius, vertices=8, depth=1,
                end_fill_type="TRIFAN")
            ob = bpy.context.object
            ob.data.materials.append(None)
            
            # convert cylinder to arrow
            bm = bmesh.new()
            bm.from_mesh(ob.data)
            
            # rotate and shrink first, then add another row of vertices
            for vert in bm.verts:
                # rotate 90 degrees around x, and shift along y axis
                tmp_co = vert.co.copy()
                vert.co.y = -tmp_co.z + .5
                vert.co.z = tmp_co.y
                if vert.co.y > 0.01:
                    vert.select = False
            new_verts = []
            for edge in bm.edges:
                if edge.calc_length() == 1.0:
                    if hasattr(edge, "ensure_lookup_table"):
                        edge.ensure_lookup_table()
                    e, v = bmesh.utils.edge_split(edge, edge.verts[0], 0.5)
                    new_verts.append(v)
            n_verts = len(new_verts)
            
            # bad hack, but don't understand how bmesh.utils.face_split works
            # remove faces with 6 verts
            for f in bm.faces:
                if len(f.verts) == 6:
                    bm.faces.remove(f)
            
            # now sort bm.verts
            # v.co.y is either 0, 0.5, or 1.0.
            # So multiply y with at least 4pi to sort by y value first
            key = lambda v: v.co.y * 15 + math.atan2(v.co.x, v.co.z)
            verts_sorted = sorted(
                (v for v in bm.verts if (0 < v.co.length and v.co.length != 1.0)), 
                key=key
                )
            
            # add new faces
            for i in range(2*n_verts):
                v1 = verts_sorted[i]
                v2 = verts_sorted[(i + 1)%n_verts + n_verts*(i//n_verts)]
                v3 = verts_sorted[(i + 1)%n_verts + n_verts*(i//n_verts + 1)]
                v4 = verts_sorted[i + n_verts]
                f = bm.faces.new((v1, v2, v3, v4))
            
            # now shape the arrow head
            for vert in bm.verts:
                if vert.co.y == 1.0 and not vert.co.length == 1.0:
                    vert.co.y = ring_y
                    vert.co.x = vert.co.x * ring_scale
                    vert.co.z = vert.co.z * ring_scale
                elif vert.co.y == 0.5:
                    vert.co.y = ring_y
            
            # make everything smooth
            for f in bm.faces:
                f.smooth = True
            
            bm.to_mesh(ob.data)
            bm.free()
            data = ob.data
            data.name = name
            bpy.context.scene.objects.unlink(ob)
        return data


def get_arrow_head_data(name="arrow_head",
                        radius=0.2, depth=0.5):
    data = bpy.context.blend_data.meshes.get(name)
    if not data:
        bpy.ops.mesh.primitive_cone_add(
            location=(0,0,0), radius1=radius, 
            vertices=16, depth=depth,
            end_fill_type="NGON")
        ob = bpy.context.active_object
        bpy.ops.object.shade_smooth()
        data = ob.data
        for v in data.vertices:
            v.co[2] -= depth/2.
        data.name = name
        bpy.context.scene.objects.unlink(ob)
    return data


def get_arrow_bevel_circle(name="arrow_bevel",
                           radius=0.1):
    ob = bpy.context.blend_data.objects.get(name)
    if not ob:
        bpy.ops.curve.primitive_bezier_circle_add(
            location=(0,0,0), radius=radius)
        ob = bpy.context.active_object
        ob.name = name
    return ob


#--- Driver setting functions ------------------------------------------------#

def set_atom_drivers(context, atom, molecule):
    fc_list = atom.driver_add('scale', -1) # add new driver
    for fcurve in fc_list:
        drv = fcurve.driver
        drv.type = 'SCRIPTED'
        drv.show_debug_info = True
        
        var = drv.variables.get('atom_radius')
        if not var:
            var = drv.variables.new()
            var.name = 'atom_radius' # name to use in scripting
            var.type = 'SINGLE_PROP'
        targ = var.targets[0]
        targ.id_type = 'SCENE'
        targ.id = context.scene
        targ.data_path = 'mb.elements["{}"].{}'.format(atom.mb.element, 
                                                       molecule.radius_type)
        
        var = drv.variables.get('atom_scale')
        if not var:
            var = drv.variables.new()
            var.name = 'atom_scale' # name to use in scripting
            var.type = 'SINGLE_PROP'
        targ = var.targets[0]
        targ.id_type = 'OBJECT'
        targ.id = atom
        targ.data_path = 'mb.parent.mb.molecule.atom_scales["{}"].val'.format(
                            molecule.draw_style)
        
        var = drv.variables.get('bond_radius')
        if not var:
            var = drv.variables.new()
            var.name = 'bond_radius' # name to use in scripting
            var.type = 'SINGLE_PROP'
        targ = var.targets[0]
        targ.id_type = 'OBJECT'
        targ.id = atom
        targ.data_path = 'mb.parent.mb.molecule.bond_radius'.format(molecule.name)
        
        if molecule.draw_style == 'BALLS':
            drv.expression = "atom_radius * atom_scale"
        elif molecule.draw_style == 'BAS':
            drv.expression = "max(atom_radius * atom_scale, bond_radius)"
        elif molecule.draw_style == 'STICKS':
            drv.expression = "bond_radius"


def set_bond_drivers(context, bond, molecule):
    fc_x = bond.driver_add('scale', 0)
    fc_z = bond.driver_add('scale', 2)
    for fcurve in (fc_x, fc_z):
        drv = fcurve.driver
        drv.type = 'AVERAGE'
        drv.show_debug_info = True
        
        var = drv.variables.get('bond_radius')
        if not var:
            var = drv.variables.new()
            var.name = 'bond_radius' # name to use in scripting
            var.type = 'SINGLE_PROP'
        targ = var.targets[0]
        targ.id_type = 'OBJECT'
        targ.id = bond
        targ.data_path = 'mb.parent.mb.molecule.bond_radius'.format(
                            molecule.name)


def calculate_displacement_t0(qvec, sc, evec):
    qR = qvec[0]*sc[0] + qvec[1]*sc[1] + qvec[2]*sc[2]
    T = 20
    Re = evec[0]
    Im = evec[1]
    
    vec = []
    t0s = []
    for dim in range(3):
        # t_max == time of maximum (positive) displacement
        tmax = T*(qR - math.atan2(Im[dim], Re[dim])/(2*math.pi))
        t0s.append(tmax)
        arg = 2*math.pi*(qR-tmax/T)
        cos_max = math.cos(arg)
        sin_max = math.sin(arg)
        vec.append(Re[dim]*cos_max - Im[dim]*sin_max)
    return Vector(vec), t0s


def update_mode_action(atom_ob, mol, nmode=None):
    T = 20
    action = atom_ob.animation_data.action
    t = (mol.mode_arrows_phase%2.)/2. * T
    if action:
        iq = mol.active_nqpt
        qvec = mol.qvecs[iq].qvec
        sc = atom_ob.mb.supercell
        if nmode is None:
            nmode = mol.active_mode
        if nmode == 0:
            realvec = (0,0,0)
            t_max = (0,0,0)
        else:
            disp = mol['mode']['displacements']
            evec = disp[atom_ob.mb.index%len(disp)]
            realvec, t_max = calculate_displacement_t0(qvec, sc, evec)
    
        for dim in range(3):
            # t0 == start time of animation, needs to be a negative number,
            # so that the animation is well underway at frame 0
            t0 = (t_max[dim] - T/4)
            t0 = t0 - T*(t0//T) - T
            fcu = action.fcurves[dim]
            vec = realvec[dim]
            for p in range(11):
                frame = 1 + t0 + 5*p - 5
                disp = pow(-1, p//2)*vec * mol.mode_scale
                coords = disp if p%2 else 0.
                fcu.keyframe_points[p].co = (frame, coords)
    else:
        msg = "Trying to update mode action on "
        msg += "object {}, but it has no existing action.".format(atom_ob.name)
        msg += " Did you change the molecule after importing the modes?"
        logger.error(msg)


def create_mode_action(context, atom_ob, molecule):
    anim_data = atom_ob.animation_data_create()
    atom_id = get_atom_id(molecule.name, atom_ob.mb.index)
    acname = "mode_{}".format(atom_id)
    oldaction = bpy.data.actions.get(acname)
    if oldaction:
        bpy.data.actions.remove(oldaction)
    action = bpy.data.actions.new(acname)
    anim_data.action = action
    # make new group
    atom_ob.update_tag(refresh={'OBJECT'})
    ag = action.groups.new("Delta_location")
    for dim in range(3):
        fcu = action.fcurves.new(data_path="delta_location", index=dim)
        fcu.group = ag
        fcu.keyframe_points.add(11)
        # We need two revolutions so that one full period is within 20 frames
        # The offset of -5 puts the equilibrium for q=0 to frame 1
        for p in range(11):
            fcu.keyframe_points[p].co = 1.0 + 5*p - 5, 0.
            fcu.keyframe_points[p].interpolation = 'SINE'
            if p == 0:
                fcu.keyframe_points[p].easing = "EASE_IN_OUT"
            if p%2 == 0:
                fcu.keyframe_points[p].easing = "EASE_OUT"
            else:
                fcu.keyframe_points[p].easing = "AUTO"
        fcu.update()


def create_mode_arrow(context, atom_ob, mol, type='3D'):
    
    if type not in ("3D", ):
        logger.error("type '{}' not recognized in draw_mode_arrow".format(type))
        return None
    try:
        atom_ob.animation_data.action.fcurves[2]
    except:
        msg = "atom object '{}' has no action to drive mode arrow."
        logger.error(msg.format(atom_ob.format))
        return None
    
    material = bpy.data.materials.get('mode_arrows_{}'.format(mol.name))
    if not material:
        material = new_material('mode_arrows_{}'.format(mol.name),
                                color=(.8,0,0))
    
    if type == '3D':
        mesh_name = "mode_arrow_{}".format(mol.name)
        arrow_ob = atom_ob.mb.mode_arrow
        if not arrow_ob:
            me = get_arrow_data(type='MESH', name=mesh_name,
                                radius = 0.05, ring_y = 0.75, ring_scale = 2)
            ob_name = "mode_vec_{}".format(get_atom_id(mol.name, atom_ob.mb.index))
            arrow_ob = bpy.data.objects.new(ob_name, me)
            arrow_ob.parent = atom_ob
            arrow_ob.material_slots[0].material = material
            context.scene.objects.link(arrow_ob)
            atom_ob.mb.mode_arrow = arrow_ob
            mol.add_object(arrow_ob, parent_to_mol=False, type='MODE_ARROW')
        
        arrow_ob.hide = not mol.show_mode_arrows
        arrow_ob.hide_render = not mol.show_mode_arrows
        arrow_ob.rotation_mode = 'QUATERNION'
    
    fc_list = arrow_ob.driver_add('scale', -1)
    for dim, fcurve in enumerate(fc_list):
        drv = fcurve.driver
        drv.type = 'SCRIPTED'
        drv.show_debug_info = True
        drv.use_self = True
        
        var = drv.variables.get('arrow_scale')
        if not var:
            var = drv.variables.new()
            var.name = 'arrow_scale'
            var.type = 'SINGLE_PROP'
        targ = var.targets[0]
        targ.id_type = 'OBJECT'
        targ.id = atom_ob
        targ.data_path = "mb.parent.mb.molecule.mode_arrows_scale"
        
        expr = ("(Vector([fcu.evaluate(frame+1) for fcu in {fcus}])"
                "-Vector([fcu.evaluate(frame-1) for fcu in {fcus}])).length"
                "* arrow_scale")
        expr = expr.format(fcus="self.parent.animation_data.action.fcurves")
        drv.expression = expr
        
    fc_list = arrow_ob.driver_add('rotation_quaternion', -1) # add new driver
    for dim, fcurve in enumerate(fc_list):
        drv = fcurve.driver
        drv.type = 'SCRIPTED'
        drv.show_debug_info = True
        drv.use_self = True
        
        expr = ("Vector((0,1,0)).rotation_difference("
                "(Vector([fcu.evaluate(frame+1) for fcu in {fcus}])"
                "-Vector([fcu.evaluate(frame-1) for fcu in {fcus}]))"
                "[{dim}]")
        expr = expr.format(fcus="self.parent.animation_data.action.fcurves",
                           dim=dim)
        drv.expression = expr
    return arrow_ob


def remove_mode_arrows(mol, context):
    for ob in mol.objects.mode_arrows.objects:
        mol.remove_object(ob)
        if ob.name in context.scene.objects:
            context.scene.objects.unlink(ob)
        bpy.data.objects.remove(ob)

def draw_dipole(mol, dipole_vec, context):
    
    remove_dipole(mol, context)
    
    radius = 0.08
    head_radius = .2
    head_depth = .5
    
    all_obs = []
    # add empty as origin
    origin_ob = bpy.data.objects.new("Dipole_{}".format(mol.name), 
                                     None)
    origin_ob.empty_draw_size = 0.5
    context.scene.objects.link(origin_ob)
    origin_ob.parent = mol.objects.parent
    mol.objects.dipole.origin = origin_ob
    origin_ob.mb.parent = mol.objects.parent
    all_obs.append(origin_ob)
    
    # add empty as stretch target
    dipole_ob = bpy.data.objects.new(
        "dipole_target_{}".format(mol.name), None)
    dipole_ob.empty_draw_type = 'SINGLE_ARROW'
    dipole_ob.empty_draw_size = 0.5
    context.scene.objects.link(dipole_ob)
    mol.objects.dipole.target = dipole_ob
    dipole_ob.location = dipole_vec
    dipole_ob.parent = origin_ob
    dipole_ob.mb.parent = mol.objects.parent
    all_obs.append(dipole_ob)
    
    material = bpy.data.materials.get('dipole_{}'.format(mol.name))
    if not material:
        material = new_material('dipole_{}'.format(mol.name),
                                color=(.8,0,0))
    head_mesh = get_arrow_head_data(
            name='dipole_head_{}'.format(mol.name),
            radius=head_radius, depth=head_depth
            )
    bevel_ob = get_arrow_bevel_circle(
        radius=radius,
        name="dipole_bevel_{}".format(mol.name)
        )
    # add arrow object
    curve_ob, head_ob = draw_arrow(
        context, origin_ob, dipole_ob, head_mesh, bevel_ob, material=material,
        name_pre="dipole", name_post=mol.name
        )
    
    for ob in (bevel_ob, curve_ob, head_ob):
        ob.parent = origin_ob
        all_obs.append(ob)
        mol.add_object(ob, parent_to_mol=False, type='DIPOLE')
    
    return [origin_ob, dipole_ob, curve_ob, head_ob]
#--- Unit cell functions -----------------------------------------------------#


def draw_arrow(context, origin, target, head_mesh, bevel_ob,
               material=None,
               name_pre="", name_post=""):
    if name_pre:
        name_pre = "{}_".format(name_pre)
    if name_post:
        name_post = "_{}".format(name_post)
    
    cu = bpy.data.curves.new(
        "{}bz{}".format(name_pre, name_post),
        type='CURVE'
        )
    cu.dimensions = '3D'
    cu.resolution_u = 1
    cu.use_fill_caps = True
    bz = cu.splines.new('BEZIER')
    bz.bezier_points.add(2-len(bz.bezier_points))
    bz.bezier_points[0].co = (0, 0, 0)
    
    # add driver to second point
    bp = bz.bezier_points[1]
    fc_list = bp.driver_add("co", -1)
    for dim, fcurve in enumerate(fc_list):
        drv = fcurve.driver
        drv.type = 'AVERAGE'
        drv.show_debug_info = True

        var_name = name_pre
        var = drv.variables.get(var_name)
        if not var:
            var = drv.variables.new()
            var.name = var_name
            var.type = 'TRANSFORMS'
        targ = var.targets[0]
        targ.id = target
        targ.transform_type = "LOC_{}".format('XYZ'[dim])
        targ.transform_space = 'LOCAL_SPACE'
    
    curve_ob = bpy.data.objects.new(
        "{}bz{}".format(name_pre, name_post), cu)
    context.scene.objects.link(curve_ob)
    if material:
        curve_ob.data.materials.append(None)
        curve_ob.material_slots[0].link = 'OBJECT'
        curve_ob.material_slots[0].material = material
    
    head_ob = bpy.data.objects.new(
        "{}arrowhead{}".format(name_pre, name_post),
        head_mesh)
    context.scene.objects.link(head_ob)
    if material:
        head_ob.data.materials.append(None)
        head_ob.material_slots[0].link = 'OBJECT'
        head_ob.material_slots[0].material = material
    mod = head_ob.modifiers.new(name='mb.bevel', type='BEVEL')
    mod.width = 0.01
    mod.segments = 3
    mod.limit_method = 'ANGLE'
    mod.angle_limit = 90
    
    # The next two constraints are needed to keep arrowhead in place
    # even if unit cell is moved
    c = head_ob.constraints.new('COPY_LOCATION')
    c.name = "mb.loc"
    c.target = curve_ob
    c.target_space = 'LOCAL'
    c.owner_space = 'WORLD'
    
    c = head_ob.constraints.new('COPY_ROTATION')
    c.name = "mb.rot"
    c.target = curve_ob
    c.target_space = 'LOCAL'
    c.owner_space = 'WORLD'
    
    # puts the arrow head at the end of the path
    c = head_ob.constraints.new('FOLLOW_PATH')
    c.name = "mb.head"
    c.target = curve_ob
    c.use_curve_follow = True
    c.use_fixed_location = True
    c.offset_factor = 1.0
    c.forward_axis = 'FORWARD_Z'
    c.up_axis = 'UP_Y'
    
    cu.bevel_object = bevel_ob
    cu.bevel_factor_mapping_start = 'SPLINE'
    cu.bevel_factor_mapping_end = 'SPLINE'
    # add driver to bevel end so that bevel ends just after head begins
    fcurve = cu.driver_add('bevel_factor_end')
    drv = fcurve.driver
    drv.type = 'SCRIPTED'
    drv.show_debug_info = True

    var_name = 'length'
    var = drv.variables.get(var_name)
    if not var:
        var = drv.variables.new()
        var.name = var_name
        var.type = 'LOC_DIFF'
    targ = var.targets[0]
    targ.id = origin
    targ = var.targets[1]
    targ.id = target
    drv.expression = "1 - {}/length + 0.01".format(head_ob.dimensions[2])
    
    return [curve_ob, head_ob]

def draw_unit_cell(molecule, context, draw_style='ARROWS'):

    mol_uc = molecule.objects.unit_cell

    # first remove old unit cell if present
    remove_unit_cell(molecule, context)
    
    all_obs = []
    special_obs = []
    
    if not "unit_cells" in molecule or not molecule["unit_cells"]:
        logger.error("No unit cell information present")
        return None
    
    unit_vectors = Matrix(molecule["unit_cells"][0])
    
    # first create new empty as origin
    uc_origin = bpy.data.objects.new("Unit_cell_{}".format(molecule.name), 
                                     None)
    uc_origin.empty_draw_type = "CUBE"
    uc_origin.empty_draw_size = 0.3
    context.scene.objects.link(uc_origin)
    uc_origin.parent = molecule.objects.parent
    special_obs.append(uc_origin)
    mol_uc.origin = uc_origin
    
    # now create the unit cell frame
    # upper case so it shows up at the top of the outliner list
    me = bpy.data.meshes.new("Unit_cell_{}".format(molecule.name))
    # setting the coordinates is technically unneccesary, since I'm adding 
    # drivers later. It does look nicer though then setting everything to 0.
    coords = (
        (0,0,0), #0, O
        unit_vectors[0], #1, x
        unit_vectors[0] + unit_vectors[1], #2, xy
        unit_vectors[1], #3, y
        unit_vectors[2], #4, z
        unit_vectors[0] + unit_vectors[2], #5, xz
        unit_vectors[1] + unit_vectors[2], #6, yz
        unit_vectors[0] + unit_vectors[1] + unit_vectors[2], #7, xyz
        )
    faces = (
        (0, 3, 2, 1),
        (0, 4, 6, 3),
        (0, 1, 5, 4),
        (7, 6, 4, 5),
        (7, 5, 1, 2),
        (7, 2, 3, 6),
        )
    me.from_pydata(coords, [], faces)
    uc_cube = bpy.data.objects.new("uc_frame_{}".format(molecule.name), me)
    context.scene.objects.link(uc_cube)
    uc_cube.parent = uc_origin

    # instead of drawing in wireframe, add wireframe modifier, so it's ready
    # to be rendered
    mod = uc_cube.modifiers.new("mb.wireframe", 'WIREFRAME')
    mod.thickness = 0.1
    mod.crease_weight = 1.0
    mod.offset = -1
    
    all_obs.append(uc_cube)

    # add empties
    for axdim, ax in enumerate(unit_vectors):
        uc_empty = bpy.data.objects.new(
            "{}_uc_{}".format("abc"[axdim], molecule.name), None)
        uc_empty.empty_draw_type = 'ARROWS'
        uc_empty.empty_draw_size = 0.5
        context.scene.objects.link(uc_empty)
        uc_empty.location = ax
        uc_empty.parent = uc_origin
        special_obs.append(uc_empty)
        setattr(mol_uc, "abc"[axdim], uc_empty)
        
        if len(molecule["unit_cells"]) > 1:
            anim_data = uc_empty.animation_data_create()
            action = bpy.data.actions.new(
                name="frames_{}".format(uc_empty.name)
                )
            anim_data.action = action
            ag = action.groups.new("Location")
            
            for dim in range(3):
                fcu = action.fcurves.new(data_path="location", index=dim)
                fcu.group = ag
                for nf in range(len(molecule["unit_cells"])):
                    loc = molecule["unit_cells"][nf][axdim][dim]
                    fcu.keyframe_points.add(1)
                    fcu.keyframe_points[-1].co = nf + 1, loc
                    fcu.keyframe_points[-1].interpolation = 'LINEAR'
    
    # Now set drivers of vertex coordinates to empties
    for i, axes in enumerate((
        #[], #0, O
        [0], #1, x
        [0, 1], #2, xy
        [1], #3, y
        [2], #4, z
        [0, 2], #5, xz
        [1, 2], #6, yz
        [0, 1, 2], #7, xyz
        )):
        
        v = me.vertices[i+1]
        fc_list = v.driver_add("co", -1)
        for dim, fcurve in enumerate(fc_list):
            drv = fcurve.driver
            drv.type = 'SCRIPTED'
            drv.show_debug_info = True
            
            expr = []
            
            for axdim in axes:
                var_name = "{}_{}".format('abc'[axdim], 'xyz'[dim])
                var = drv.variables.get(var_name)
                if not var:
                    var = drv.variables.new()
                    var.name = var_name
                    var.type = 'TRANSFORMS'
                targ = var.targets[0]
                #targ.id_type = 'OBJECT'
                targ.id = getattr(mol_uc, "abc"[axdim])
                targ.transform_type = "LOC_{}".format('XYZ'[dim])
                targ.transform_space = 'LOCAL_SPACE'
                
                expr.append(var_name)
                
            drv.expression = " + ".join(expr)
    vg = []
    vg.append(uc_cube.vertex_groups.new('a'))
    vg[-1].add([1], 1, 'REPLACE')
    vg.append(uc_cube.vertex_groups.new('b'))
    vg[-1].add([3], 1, 'REPLACE')
    vg.append(uc_cube.vertex_groups.new('c'))
    vg[-1].add([4], 1, 'REPLACE')
    
    if 'ARROWS' in draw_style:
        radius = 0.08
        head_radius = .2
        head_depth = .5
        # get material
        material = bpy.data.materials.get('axes_{}'.format(molecule.name))
        if not material:
            material = new_material('axes_{}'.format(molecule.name),
                                    color=(1,0,0))
        
        # add sphere at origin
        bpy.ops.mesh.primitive_uv_sphere_add(location=(0,0,0), size=radius, 
                                             segments=8, ring_count=8)
        sphere_ob = context.object
        sphere_ob.name = "unit_cell_origin_{}".format(molecule.name)
        #ob.parent_type = 'VERTEX'
        sphere_ob.data.materials.append(None)
        sphere_ob.material_slots[0].link = 'OBJECT'
        sphere_ob.material_slots[0].material = material
        all_obs.append(sphere_ob)
        
        head_mesh = get_arrow_head_data(
            name='arrow_head_{}'.format(molecule.name),
            radius=head_radius, depth=head_depth
            )
        bevel_ob = get_arrow_bevel_circle(
            radius=radius,
            name="arrow_bevel_{}".format(molecule.name)
            )
        all_obs.append(bevel_ob)
        for axdim, vec in enumerate(unit_vectors):
            origin = uc_origin
            target = getattr(mol_uc, "abc"[axdim])

            arrow_obs = draw_arrow(context, origin, target,
                                   head_mesh, bevel_ob, material=material,
                                   name_pre="{}_uc".format("abc"[axdim]),
                                   name_post=molecule.name)
            all_obs.extend(arrow_obs)
    
    for ob in all_obs:
        ob.parent = uc_origin
        ob.mb.parent = molecule.objects.parent
        molecule.add_object(ob, parent_to_mol=False, type='UC')
    
    for ob in special_obs:
        ob.mb.type = 'UC'
        ob.mb.parent = molecule.objects.parent
    
    return all_obs + special_obs


def remove_dipole(mol, context):
    for o in ("origin", "target"):
        ob = getattr(mol.objects.dipole, o, None)
        if ob:
            if ob.name in context.scene.objects:
                context.scene.objects.unlink(ob)
            bpy.data.objects.remove(ob)
        setattr(mol.objects.dipole, o, None)
    for ob in mol.objects.dipole.objects:
        mol.remove_object(ob)
        if ob.name in context.scene.objects:
            context.scene.objects.unlink(ob)
        bpy.data.objects.remove(ob)


def remove_unit_cell(mol, context):
    mol_uc = mol.objects.unit_cell
    ob = mol_uc.origin
    if ob:
        if ob.name in context.scene.objects:
            context.scene.objects.unlink(ob)
        bpy.data.objects.remove(ob)
    for ax in "abc":
        ob = getattr(mol_uc, ax, None)
        if ob:
            if ob.name in context.scene.objects:
                context.scene.objects.unlink(ob)
            bpy.data.objects.remove(ob)
        setattr(mol_uc, ax, None)
    for ob in mol_uc.objects:
        mol.remove_object(ob)
        if ob.name in context.scene.objects:
            context.scene.objects.unlink(ob)
        bpy.data.objects.remove(ob)

#--- Material functions ------------------------------------------------------#

def new_material(name, color=(0.8, 0.8, 0.8, 1.0)):
    '''
    creates new material.
    '''
    material = bpy.data.materials.new(name)
    
    if bpy.context.scene.render.engine == 'CYCLES':
        material.use_nodes = True
        # add driver to rendered color to be the same as display color
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        nodes.clear()
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.name = "mb.principled"
        try:
            principled.inputs[0].default_value = color
        except:
            color_alpha = (color[0], color[1], color[2], 1.0)
            principled.inputs[0].default_value = color_alpha
        output_mat = nodes.new(type='ShaderNodeOutputMaterial')
        
        links.new(principled.outputs[0], output_mat.inputs[0])
        
        for i in range(3): # not for alpha channel
            fcurve =  material.driver_add('diffuse_color', i)
            drv = fcurve.driver
            drv.type = 'AVERAGE'
            drv.show_debug_info = True
            
            var = drv.variables.new()
            var.name = 'diffuse_color' # name to use in scripting
            var.type = 'SINGLE_PROP'
            targ = var.targets[0]
            targ.id_type = 'MATERIAL'
            targ.id = material
            targ.data_path = ('node_tree.nodes["mb.principled"].inputs[0]'
                              + '.default_value[{}]'.format(i))
    else:
        material.diffuse_color = color[:3]

    return material


def assign_atom_material(ob, molecule):
    # make sure there is at least one material slot
    if len(ob.material_slots) < 1:
        ob.data.materials.append(None)
    
    # get element and molecule name (ident) of atom to make unique material name
    element = ob.mb.element
    material_name = "mat_{}_{}".format(element, molecule.name)
    
    # get or create element material per molecule
    material = bpy.data.materials.get(material_name)
    if not material:
        scn_elements = bpy.context.scene.mb.elements
        color = scn_elements.get(element, scn_elements["Default"]).color
        # get material color from elements list, and Default if not an element
        material = new_material(material_name, color=color)
    
    # finally, assign material to first slot.
    ob.material_slots[0].link = 'DATA'
    ob.material_slots[0].material = material


def assign_bond_material(ob):
    bond_type = 'MESH'
    
    bond_mol = ob.mb.get_molecule()
    
    first_atom = ob.mb.bonded_atoms[0]
    second_atom = ob.mb.bonded_atoms[1]
    
    first_mol = first_atom.mb.get_molecule()
    second_mol = second_atom.mb.get_molecule()
    
    first_mat = None
    second_mat = None
    
    # the molecule properties of the two bonded atoms are used.
    # to use the bond_mol properties change accordingly
    if first_mol.bond_material == 'ATOMS':
        first_mat = first_atom.material_slots[0].material
    elif first_mol.bond_material == 'GENERIC':
        first_mat = first_mol.bond_generic_material
        if not first_mat:
            first_mat_name = "mat_bond_{}".format(first_mol.name)
            first_mat = bpy.data.materials.get(first_mat_name)
            if not first_mat:
                first_mat = new_material(first_mat_name)
            first_mol.bond_generic_material = first_mat
    if second_mol.bond_material == 'ATOMS':
        second_mat = second_atom.material_slots[0].material
    elif second_mol.bond_material == 'GENERIC':
        second_mat = second_mol.bond_generic_material
        if not second_mat:
            second_mat_name = "mat_bond_{}".format(second_mol.name)
            second_mat = bpy.data.materials.get(second_mat_name)
            if not second_mat:
                second_mat = new_material(second_mat_name)
            second_mol.bond_generic_material = second_mat
            
    # make sure to have at least two material slots
    for i in range(2 - len(ob.material_slots)):
        ob.data.materials.append(None)
    
    ob.material_slots[0].link = 'OBJECT'
    ob.material_slots[1].link = 'OBJECT'
    ob.material_slots[0].material = first_mat
    ob.material_slots[1].material = second_mat


def is_inside_of_planes(planes, loc, flip=False):
    l0 = Vector(loc)
    for n, p0 in planes:
        vec = p0 - l0
        if (vec).dot(n) < 0:
            # point lies outside of plane
            return flip
    else:
        return not flip
