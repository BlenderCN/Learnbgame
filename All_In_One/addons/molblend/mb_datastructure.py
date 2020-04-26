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

if "bpy" in locals():
    import importlib
    importlib.reload(mb_utils)
else:
    from molblend import mb_utils

import os
import string
import random
import logging
import numpy as np

import bpy
from bpy.types import (PropertyGroup,
                       UIList)
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       IntVectorProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       BoolVectorProperty,
                       PointerProperty,
                       CollectionProperty,
                       EnumProperty)

logger = logging.getLogger(__name__)

def get_object_list(colprop):
    all_obs = []
    delete = []
    for i, item in enumerate(colprop):
        if item.object and item.object.name in bpy.context.scene.objects:
            all_obs.append(item.object)
        else:
            delete.append(i)
    for d in delete[::-1]:
        try:
            colprop.remove(d)
        except AttributeError:
            pass
    return all_obs

class mb_object_pointer(PropertyGroup):
    #name = StringProperty(name="Object name")
    object = PointerProperty(name="Object", type=bpy.types.Object)
    @property
    def name(self):
        return self.object.name

class mb_element_mesh(PropertyGroup):
    name = StringProperty(name="Element")
    data = PointerProperty(name="Mesh", type=bpy.types.Mesh)
    #def get_data(self):
        #return bpy.data.meshes.get(self.name)

class atom_scale(PropertyGroup):
    name = StringProperty()
    val = FloatProperty(name="Atom scale", default=0.4, min=0.0, max=5.0,
                        precision=2, update=mb_utils.update_all_meshes)

class mb_mesh(PropertyGroup):
    type = EnumProperty(
        name="type", description="Identifies the mesh type",
        items=mb_utils.enums.mesh_types, default='NONE')

class mb_atom_mode(PropertyGroup):
    name = IntProperty(name="index")
    index = IntProperty(name="index")
    freq = FloatProperty(name="frequency")
    vec = FloatVectorProperty(name="vector", subtype="XYZ")

class mb_dipole(PropertyGroup):
    origin = PointerProperty(name="origin", type=bpy.types.Object)    
    target = PointerProperty(name="Dipole", type=bpy.types.Object)
    
    pvt_objects = CollectionProperty(name="Dipole arrow objects", 
                                     type=mb_object_pointer)
    @property
    def objects(self):
        return get_object_list(self.pvt_objects)
    
class mb_unit_cell(PropertyGroup):
    origin = PointerProperty(name="origin", type=bpy.types.Object)
    a = PointerProperty(name="a", type=bpy.types.Object)
    b = PointerProperty(name="b", type=bpy.types.Object)
    c = PointerProperty(name="c", type=bpy.types.Object)
    
    pvt_objects = CollectionProperty(name="Unit cell objects", 
                                     type=mb_object_pointer)
    @property
    def objects(self):
        return get_object_list(self.pvt_objects)


class mb_mode_arrows(PropertyGroup):
    pvt_objects = CollectionProperty(name="Mode arrows",
                                     type=mb_object_pointer)
    @property
    def objects(self):
        return get_object_list(self.pvt_objects)


class mb_molecule_objects(PropertyGroup):
    pvt_atoms = CollectionProperty(name="Atoms", type=mb_object_pointer)
    pvt_bonds = CollectionProperty(name="Bonds", type=mb_object_pointer)
    parent = PointerProperty(name="Parent", type=bpy.types.Object)
    dipole = PointerProperty(name="Dipole", type=mb_dipole)
    unit_cell = PointerProperty(name="Unit cell objects", type=mb_unit_cell)
    pvt_other = CollectionProperty(name="Bonds", type=mb_object_pointer)
    mode_arrows = PointerProperty(name="Mode arrows", type=mb_mode_arrows)
                                  
    @property
    def atoms(self):
        return get_object_list(self.pvt_atoms)

    @property
    def bonds(self):
        return get_object_list(self.pvt_bonds)
    
    @property
    def other(self):
        return get_object_list(self.pvt_other)
    
    def get_all_objects(self, with_parent=True):
        all_obs = []
        if self.parent and with_parent:
            all_obs.append(self.parent)
        all_obs.extend(self.atoms)
        all_obs.extend(self.bonds)
        all_obs.extend(self.other)
        for ob in (self.dipole.origin,
                   self.dipole.target,
                   self.dipole.objects,
                   self.unit_cell.origin,
                   self.unit_cell.a,
                   self.unit_cell.b,
                   self.unit_cell.c):
            if ob:
                all_obs.append(ob)
        all_obs.extend(self.unit_cell.objects)
        return all_obs

class mb_qvec(PropertyGroup):
    iqpt = IntProperty(name="nqpt", default=1)
    qvec = FloatVectorProperty(name="q vector", default=(0,0,0))
    mode_txt = PointerProperty(type=bpy.types.Text)

class MB_UL_modes(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, 
                  active_propname, index):
        split = layout.split(0.18)
        col = split.column()
        col.label(str(item.iqpt))
        col = split.column()
        col.label("q=({:5.3f}, {:5.3f}, {:5.3f})".format(*item.qvec))

def get_material_props(ob=None, node_name="mb.principled", material=None):
    try:
        mat = material or ob.material_slots[0].material
        if bpy.context.scene.render.engine == 'CYCLES':
            data = mat.node_tree.nodes[node_name].inputs[0]
            prop = "default_value"
        else:
            data = mat
            prop = "diffuse_color"
        return data, prop
    except IndexError:
        return "{} has no material".format(ob.name), None
    except AttributeError as e:
        if "no attribute 'node_tree'" in e.args[0]:
            msg = "{} has no material".format(ob.name)
        else:
            msg = "from get_material_props: {}".format(e)
        return msg, None
    except KeyError as e:
        msg = "Material {} has no node with name {}".format(mat.name, node_name)
        return msg, None

class mb_molecule(PropertyGroup):
    index = IntProperty(name="Molecule index")
    name = StringProperty(name="Molecule identifier")
    # index that increases with each added atom in the molecule, 
    # or is set to max index of imported file. It doesn't 
    # decrease when atom is deleted. => Not an indicator of size of molecule! 
    # Only guarantees uniqueness for atom names
    atom_index = IntProperty(name="Atom counter")
    objects = PointerProperty(name="Molecule objects", 
                              type=mb_molecule_objects)
    meshes = CollectionProperty(name="Meshes", type=mb_element_mesh)
    
    # display properties
    bond_material = EnumProperty(
        name="Bond material", description="Choose bond material",
        items=mb_utils.enums.bond_material, default='ATOMS',
        update=mb_utils.update_bond_material
        )
    bond_generic_material = PointerProperty(type=bpy.types.Material)
    draw_style = EnumProperty(
        name="Display style", description="Style to draw atoms and bonds",
        items=mb_utils.enums.molecule_styles, default='BAS',
        update=mb_utils.update_draw_style
        )
    radius_type = EnumProperty(
        name="Radius type", description="Type of radius to use as reference",
        items=mb_utils.enums.radius_types, default='covalent', 
        update=mb_utils.update_radius_type
        )
    bond_radius = FloatProperty(
        name="Bond radius", description="Radius for bond objects",
        default=0.1, min=0.0, max=3.0,
        update=mb_utils.update_all_meshes
        )
    atom_scales = CollectionProperty(type=atom_scale)
    refine_atoms = IntProperty(
        name="Refine atoms", description="Refine value for atom meshes", 
        default=8, min=2, max=64,
        update=mb_utils.update_refine_atoms
        )
    refine_bonds = IntProperty(
        name="Refine bonds", description="Refine value for atom meshes", 
        default=8, min=2, max=64,
        update=mb_utils.update_refine_bonds
        )
    
    # vibrational modes
    qvecs = CollectionProperty(name="Modes", type=mb_qvec)
    active_nqpt = IntProperty(
        name="Active q-point",
        description="Active q-point",
        default=0, min=0,
        update=mb_utils.update_active_mode
        )
    max_mode = IntProperty(
        name="Number of modes", 
        description="Number of vibrational modes of molecule",
        default=0, min=0,
        )
    active_mode = IntProperty(
        name="Active Mode",
        description="Active Mode to display. 0 = equilibrium position",
        default=0, min=0,
        update=mb_utils.update_active_mode
        )
    mode_scale = FloatProperty(
        name="Mode Scale", description="Scale of normal mode displacement",
        default=1.0,
        update=mb_utils.update_active_mode
        )
    mode_arrows_scale = FloatProperty(
        name="Arrow Scale", description="Scale of mode arrows",
        default=25.0, min=-1000.0, max=1000.0, 
        #update=mb_utils.update_active_mode
        )
    show_mode_arrows = BoolProperty(
        name="Show arrows", default=False,
        description="Show arrows for mode eigenvectors",
        update=mb_utils.update_show_mode_arrows
        )
    mode_arrows_phase = FloatProperty(
        name="Arrow phase", default=0.,
        description="Mode phase in units of pi",
        update=mb_utils.update_active_mode
        )
    autoplay_mode_animation= BoolProperty(
        name="Autoplay", default=True,
        description="Automatically start animation on mode change",
        update=mb_utils.update_active_mode
        )
    
    show_unit_cell_frame = BoolProperty(
        name="Show frame", default=True,
        description="Show unit cell frame",
        update=mb_utils.update_show_unit_cell_frame
        )
    show_unit_cell_arrows = BoolProperty(
        name="Show arrows", default=True,
        description="Show unit cell arrows",
        update=mb_utils.update_show_unit_cell_arrows
        )
    
    def draw_vibrations(self, layout):
        
        layout.operator("mb.import_modes")
        if self.qvecs:
            layout.template_list("MB_UL_modes", "", self, "qvecs", self, 
                              "active_nqpt", rows=1)
            layout.prop(self, "active_mode")
            if not 'mode' in self:
                layout.label("mode wasn't loaded correctly.")
                return None
            layout.label("Frequency: {}".format(self['mode']["freq"]))
            #layout.prop(self['qpts'][self.active_nqpt]['modes'][self.active_mode], 
                        #"symmetry", text="Symmetry")
            layout.prop(self, "mode_scale", slider=False)
            # The play/pause etc buttons are copy/pasted from space_time.py
            row = layout.row(align=True)
            row.operator("screen.frame_jump", text="", icon='REW').end = False
            row.operator("mb.frame_skip", text="", icon='PREV_KEYFRAME').next = False
            screen = bpy.context.screen
            scene = bpy.context.scene
            if not screen.is_animation_playing:
                # if using JACK and A/V sync:
                #   hide the play-reversed button
                #   since JACK transport doesn't support reversed playback
                if scene.sync_mode == 'AUDIO_SYNC' and context.user_preferences.system.audio_device == 'JACK':
                    sub = row.row(align=True)
                    sub.scale_x = 2.0
                    sub.operator("screen.animation_play", text="", icon='PLAY')
                else:
                    row.operator("screen.animation_play", text="", icon='PLAY_REVERSE').reverse = True
                    row.operator("screen.animation_play", text="", icon='PLAY')
            else:
                sub = row.row(align=True)
                sub.scale_x = 2.0
                sub.operator("screen.animation_play", text="", icon='PAUSE')
            row.operator("mb.frame_skip", text="", icon='NEXT_KEYFRAME').next = True
            row.operator("screen.frame_jump", text="", icon='FF').end = True
            row.prop(self, "autoplay_mode_animation", text="Autoplay")
            
            layout.prop(self, "show_mode_arrows", text="Arrows")
            row = layout.row()
            row.active = self.show_mode_arrows
            row.prop(self, 'mode_arrows_scale')
            row = layout.row()
            row.active = self.show_mode_arrows
            row.prop(self, 'mode_arrows_phase')
            
    def draw_properties(self, layout):
        layout.prop(self.objects.parent, "name")
        layout.label("(id: '{}')".format(self.name))
        if 'unit_cells' in self and len(self['unit_cells']) > 1:
            layout.label("Number of frames: {}".format(len(self['unit_cells'])))
        if self.objects.parent:
            col = layout.column()
            col.prop(self.objects.parent, "location", 
                     text="Parent location")
        layout.operator("mb.center_mol_parent")

    def draw_dipole_props(self, layout):
        if (self.objects.dipole.target and 
            self.objects.dipole.target.name in bpy.context.scene.objects):
            col = layout.column()
            col.prop(self.objects.dipole.target, "location", 
                     text="")
            for ob in self.objects.dipole.objects:
                if ob.material_slots:
                    mat = ob.material_slots[0].material
                    break
            data, prop = get_material_props(ob)
            if data:
                layout.prop(data, prop, text="Color")
            layout.operator("mb.remove_dipole")
        else:
            layout.operator("mb.draw_dipole")
    
    def draw_unit_cell_props(self, layout):
        if (self.objects.unit_cell.a 
                and self.objects.unit_cell.b
                and self.objects.unit_cell.c):
            row = layout.row()
            col = row.column()
            avec = self.objects.unit_cell.a
            bvec = self.objects.unit_cell.b
            cvec = self.objects.unit_cell.c
            col.prop(avec, "location", text="a")
            col = row.column()
            col.prop(bvec, "location", text="b")
            col = row.column()
            col.prop(cvec, "location", text="c")
            
            # unit cell volume
            vol = np.absolute(np.dot(avec.location, 
                                     np.cross(bvec.location,
                                              cvec.location)))
            layout.label("Volume: {:5.3f} {}".format(vol, u"\u212B\u00B3"))
            
            ob_frame = None
            ob_not_frame = None
            for ob in self.objects.unit_cell.objects:
                if 'frame' in ob.name:
                    ob_frame = ob
                elif 'arrowhead' in ob.name:
                    ob_arrow = ob
            
            if ob_arrow and ob_arrow.material_slots:
                data, prop = get_material_props(ob_arrow)
                if data:
                    layout.prop(data, prop, text="Color")
            
            layout.prop(ob_frame.modifiers['mb.wireframe'], 'thickness',
                        text="Frame thickness")
            
            layout.prop(self, "show_unit_cell_arrows")
            layout.prop(self, "show_unit_cell_frame")
            layout.operator("mb.remove_unit_cell")
        else:
            layout.operator("mb.draw_unit_cell")
    
    def draw_styles(self, layout):
        props = {
            "Atom scale": [self.atom_scales[self.draw_style], "val", 10],
            "Bond radius": [self, "bond_radius", 20],
            "Radius type": [self, "radius_type", 30],
            "Display style": [self, "draw_style", 40],
            "Bond material": [self, "bond_material", 50],
            "Refine atoms": [self, "refine_atoms", 70],
            "Refine bonds": [self, "refine_bonds", 80],
            }
        
        data, prop = get_material_props(material=self.bond_generic_material)
        props.update({'Bond color': [data, prop, 60]})
        
        for label, (data, prop, i) in sorted(props.items(), 
                                             key=lambda t: t[-1][-1]):
            try:
                layout.prop(data, prop, text=label)
            except TypeError:
                #get_material_props returns a string if no material was found
                layout.label("{}: {}".format(label, data))

        
    def add_object(self, ob, parent_to_mol=True, type=None):
        '''
        Add an object to the molecule's atoms collection and return the
        collection item. If object is already in collection, just return the
        collection item.
        '''
        if type != None:
            ob.mb.type = type
        ob.mb.parent = self.objects.parent
        if parent_to_mol and not ob.parent == self.id_data:
            ob.parent = self.id_data
            ob.matrix_parent_inverse = self.id_data.matrix_world.inverted()
        collection = {
            'ATOM': self.objects.pvt_atoms,
            'BOND': self.objects.pvt_bonds,
            'UC': self.objects.unit_cell.pvt_objects,
            'DIPOLE': self.objects.dipole.pvt_objects,
            'MODE_ARROW': self.objects.mode_arrows.pvt_objects,
            'NONE': self.objects.pvt_other
            }
        objects = collection[ob.mb.type]
        
        for existing in objects:
            if existing.object == ob:
                item = existing
                break
        else:
            item = objects.add()
            item.object = ob
            if ob.type == 'ATOM':
                self.atom_index = max(self.atom_index, ob.mb.index)
        return item
    
    def remove_object(self, ob):
        if ob.parent == self.objects.parent:
            mat = ob.matrix_world.copy()
            ob.parent = None
            ob.matrix_world = mat
        collection = {
            'ATOM': self.objects.pvt_atoms,
            'BOND': self.objects.pvt_bonds,
            'UC': self.objects.unit_cell.pvt_objects,
            'DIPOLE': self.objects.dipole.pvt_objects,
            'MODE_ARROW': self.objects.mode_arrows.pvt_objects,
            'NONE': self.objects.pvt_other
            }
        objects = collection[ob.mb.type]
        for i, item in enumerate(objects):
            if item.object == ob:
                objects.remove(i)
                return
    
    def get_mode(self, n_mode=None, n_qpt=None):
        if n_mode is None:
            n_mode = self.active_mode
        if n_qpt is None:
            n_qpt = self.active_nqpt
        try:
            qpt = json.loads(self.qvecs[n_qpt].mode_txt.as_string())
        except:
            logger.error("Problem loading mode from text object. Check console")
            logger.exception("")
            return None
        return qpt['modes'][n_mode-1]


class mb_object(PropertyGroup):
    index = IntProperty(name="Index")
    name = StringProperty(name="Object name")
    type = EnumProperty(
        name="type", description="Select the object type",
        items=mb_utils.enums.object_types, default='NONE')
    
    parent = PointerProperty(name="Molecule parent",
                             type=bpy.types.Object)
    
    # used by type == 'ATOM'
    pvt_bonds = CollectionProperty(type=mb_object_pointer)
    @property
    def bonds(self):
        return get_object_list(self.pvt_bonds)

    atom_name = StringProperty(name="Atom name")
    element = StringProperty(
        name="Element", description="Element Symbol",
        update=mb_utils.update_atom_element)
    element_long = StringProperty(
        name="Element name", description="Full element name")
    mode_arrow = PointerProperty(type=bpy.types.Object)
    
    # used by type == 'BOND'
    pvt_bonded_atoms = CollectionProperty(type=mb_object_pointer)
    @property
    def bonded_atoms(self):
        return get_object_list(self.pvt_bonded_atoms)
    
    supercell = IntVectorProperty(name="supercell", default=(0,0,0),
                                  size=3)
    
    # used by type == 'PARENT'
    molecule = PointerProperty(type=mb_molecule)
    
    @property
    def object(self):
        return self.id_data
    @property
    def world_location(self):
        return self.id_data.matrix_world.to_translation()
    
    def get_molecule(self):
        try:
            return self.parent.mb.molecule
        except AttributeError:
            return None
    
    def add_bond(self, ob):
        """Add object to bond collection and return new collection item."""
        if not self.type == 'ATOM':
            logger.warning("Something is trying to add bond to "
                           "non-ATOM type object")
            return None
        
        bond = None
        for existing in self.bonds:
            if existing == ob:
                bond = existing
                break
        else:
            bond = self.pvt_bonds.add()
            bond.object = ob
        return bond
    
    def remove_bond(self, ob):
        if not self.type == 'ATOM':
            logger.warning("Something is trying to remove bond from "
                           "non-ATOM type object")
            return None
        for i, b in enumerate(self.bonds):
            if b == ob:
                self.pvt_bonds.remove(i)
                return
    
    def add_bonded_atom(self, ob):
        if not self.type == 'BOND':
            logger.warning("Something is trying to add bonded_atom to "
                           "non-BOND type object")
            return
        
        atom = None
        for existing in self.bonded_atoms:
            if existing == ob:
                atom = existing
                break
        else:
            atom = self.pvt_bonded_atoms.add()
            atom.object = ob
        return atom
    
    def remove_bonded_atom(self, ob):
        if not self.type == 'BOND':
            logger.warning("Something is trying to remove bonded_atom "
                           "{} ({}) from non-BOND type object {} ({})".format(
                           ob.name, ob.mb.type, self.name, self.type))
            return
        
        for i, a in enumerate(self.bonded_atoms):
            if a == ob:
                self.pvt_bonded_atoms.remove(i)
                return
    
    def draw_properties(self, context, layout, ob):
        element = context.scene.mb.elements[self.element]
        
        props = {
            "Element": [self, "element", 10],
            "Name": [self, "atom_name", 20],
            "Covalent radius": [element, "covalent", 30],
            "vdW radius": [element, "vdw", 40],
            "constant radius": [element, "constant", 50],
            #"Atom color": atom_color,
            }
        data, prop = get_material_props(ob)
        props.update({'Atom color': [data, prop, 60]})
        
        for label, (data, prop, i) in sorted(props.items(),
                                             key=lambda t: t[-1][-1]):
            try:
                layout.prop(data, prop, text=label)
            except TypeError:
                layout.label("{}: {}".format(label, data))

class mb_text(PropertyGroup):
    type = EnumProperty(
        name="type", description="Select the text type",
        items=mb_utils.enums.text_types, default='NONE')
    parent = PointerProperty(type=bpy.types.Object)
    
class mb_element(PropertyGroup):
    name = StringProperty(name="Element")
    element = StringProperty(name="Element")
    element_name = StringProperty(name="Element name")
    atomic_number = IntProperty(name="Atomic number")
    color = FloatVectorProperty(name="Color", subtype='COLOR', size=3)
    covalent = FloatProperty(
        name="Covalent radius",
        description="Scene wide covalent radius",
        min=0.0, max=5.0, 
        update=mb_utils.update_all_meshes)
    vdw = FloatProperty(
        name="vdW radius", 
        description="Scene wide van der Waals radius",
        min=0.0, max=5.0, 
        update=mb_utils.update_all_meshes)
    constant = FloatProperty(
        name="Constant radius",
        min=0.0, max=5.0,
        update=mb_utils.update_all_meshes)


class mb_scn_import(PropertyGroup):
    filepath = StringProperty(
        name="Import file", 
        description="Filepath to molecule file to import (.xyz, .pdb)",
        default=os.getcwd() + "/", subtype="FILE_PATH")
    modes = BoolProperty(
        name="Modes", 
        description="Import normal modes of molecule as keyframes.",
        default=False)
    n_q = IntProperty(name="q point", default=1,
        min=1, description="Import modes of 'n_q'th q point in file")
    modes_path = StringProperty(
        name="Modes file",
        description="Filepath to modes file to import "
                    "(In Quantum Espresso: dynmat.out)", 
        default="", subtype="FILE_PATH")


class mb_scn_export(PropertyGroup):
    filepath = StringProperty(name="Export file", default="", 
        subtype="FILE_PATH",
        description="Filepath to exported molecule file (.xyz, .pdb)")
    selection_only = BoolProperty(name="Selected Objects", default=True,
        description="Only export selected objects")
    file_type = EnumProperty(
        name="File type", default="XYZ", items=mb_utils.enums.file_types,
        description="File format to export to", 
        update=mb_utils.update_export_file_type)
    length_unit = EnumProperty(
        name="Unit", default='1.0', items=mb_utils.enums.angstrom_per_unit,
        description="Unit in output file (to convert to from Angstrom)")
    length_unit_other = FloatProperty(
        name="Custom Unit", default=1.0, min=0.000001,
        description="Enter unit of export file as Angstrom/unit")


class mb_scn_globals(PropertyGroup):
    draw_style = EnumProperty(
        name="Draw style", description="Style to draw atoms and bonds",
        items=mb_utils.enums.molecule_styles, default='BAS',
        )
    radius_type = EnumProperty(
        name="Radius type", 
        items=mb_utils.enums.radius_types, default='covalent')
    bond_radius = FloatProperty(
        name="Bond radius",
        description="Radius of bonds for Sticks, and Ball and Sticks", 
        default=0.1, min=0.0, max=3.0)
    atom_scales = CollectionProperty(type=atom_scale)
    import_props = PointerProperty(type=mb_scn_import)
    export_props = PointerProperty(type=mb_scn_export)
    show_bond_lengths = BoolProperty(
        name="Show bond lengths", default=False,
        description="Display bond length of selected bonds",
        update=mb_utils.update_show_bond_lengths
        )
    bond_length_font_size = IntProperty(
        name="Bond length font size", default=12,
        description="Font size of bond lengths")
    #show_bond_angles = BoolProperty(
        #name="Show bond angles", default=False, 
        #description="Display bond angle of selected bonds",
        #update=mb_utils.update_show_bond_angles)
    element_to_add = StringProperty(
        name="Element", description="Element to add to scene", 
        default="C")
    geometry_to_add = EnumProperty(
        name="Geometry",
        description="Geometry the new bond should be in relative to "
                    "existing bonds.", 
        items=mb_utils.enums.geometries, default='NONE')


class mb_git_commit(PropertyGroup):
    commit_id = StringProperty(name="git commit id")
    date = StringProperty(name="git commit date")
    time_stamp = StringProperty(name="git commit time stamp")


class mb_scn_info(PropertyGroup):
    git_commits = CollectionProperty(type=mb_git_commit)


class mb_scene(PropertyGroup):
    is_initialized = BoolProperty(default=False)
    elements = CollectionProperty(type=mb_element)
    # index that increases with each added molecule, but doesn't decrease when
    # molecule is deleted.
    molecule_count = IntProperty(name="Molecule counter")
    globals = PointerProperty(type=mb_scn_globals)
    info = PointerProperty(type=mb_scn_info)
    # store last active object for modal operator
    modal_last_active = PointerProperty(name="Last active", 
                                        type=bpy.types.Object)
    
    #@class
    def id_generator(self, size=6,
                     chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
    
    def new_molecule(self,
                     name_mol="Molecule",
                     draw_style=None,
                     radius_type=None,
                     bond_radius=None,
                     refine_atoms=None,
                     refine_bonds=None,
                     atom_scales=None):
        
        # create new empty that will be the parent for the molecule
        parent_ob = bpy.data.objects.new(name_mol, None)
        parent_ob.empty_draw_type = 'SPHERE'
        parent_ob.empty_draw_size = 0.3
        parent_ob.mb.type = 'PARENT'
        parent_ob.mb.parent = parent_ob
        self.id_data.objects.link(parent_ob)
        
        # now populate the molecule data
        mol = parent_ob.mb.molecule
        new_id = self.id_generator()
        mol.name = new_id
        
        mol.index = self.molecule_count
        self.molecule_count += 1
        mol.draw_style = draw_style or self.globals.draw_style
        mol.radius_type = radius_type or self.globals.radius_type
        mol.bond_radius = bond_radius or self.globals.bond_radius
        if refine_atoms:
            mol.refine_atoms = refine_atoms
        if refine_bonds:
            mol.refine_bonds = refine_bonds
        for scale in (atom_scales or self.globals.atom_scales):
            new_scale = mol.atom_scales.add()
            new_scale.name = scale.name
            new_scale.val = scale.val
        
        mol.objects.parent = parent_ob
        
        return mol
    
    def remove_molecule(self, mol, only_if_empty=False):
        """only_if_empty: only remove if it has no atoms or bonds
        """
        if ((not mol.objects.atoms and not mol.objects.bonds)
            or not only_if_empty):
            parent = mol.objects.parent
            
            for ob in mol.objects.get_all_objects():
                if ob != parent:
                    self.id_data.objects.unlink(ob)
                    bpy.data.objects.remove(ob)
            if parent:
                if parent.name in self.id_data.objects:
                    self.id_data.objects.unlink(parent)
                bpy.data.objects.remove(parent)


def register():
    bpy.types.Object.mb = PointerProperty(type=mb_object)
    bpy.types.Mesh.mb = PointerProperty(type=mb_mesh)
    bpy.types.Scene.mb = PointerProperty(type=mb_scene)
    bpy.types.Text.mb = PointerProperty(type=mb_text)


def unregister():
    del bpy.types.Object.mb
    del bpy.types.Mesh.mb
    del bpy.types.Scene.mb
