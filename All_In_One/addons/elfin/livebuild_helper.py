import colorsys
import random
import json
import collections
import functools

import bpy
import bmesh
import mathutils
import mathutils.bvhtree
from . import addon_paths
from .elfin_object_properties import ElfinObjType


# Global (Const) Variables -----------------------

blender_pymol_unit_conversion = 10.0

# Color Change Placeholder
#
#   An option for Place/Extrude operator enums so that user can change the
#   color before choosing a module. This makes changing display color fast
#   because once a module is selected via the enum list, changing the display
#   color causes constant re-linking and that causes lag.
color_change_placeholder = '-Change Color-'
color_change_placeholder_enum_tuple = \
    (color_change_placeholder, color_change_placeholder, '')

# Prototype List Empty Placeholder
#  An option to inform the user that the prototype list is empty
empty_list_placeholder = '-List Empty-'
empty_list_placeholder_enum_tuple = \
    (empty_list_placeholder, empty_list_placeholder, '')

nop_enum_selectors = {
    color_change_placeholder,
    empty_list_placeholder
}

# Classes ----------------------------------------

# Singleton Metaclass
# Credits to https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class LivebuildState(metaclass=Singleton):
    def __init__(self):
        self.reset()

    def get_all_extrudables(self, sel_mod):
        self.n_extrudables = get_extrusion_prototype_list(sel_mod, 'n')
        self.c_extrudables = get_extrusion_prototype_list(sel_mod, 'c')
        return self.n_extrudables, self.c_extrudables

    def update_derivatives(self):
        res = [color_change_placeholder_enum_tuple] + \
            [module_enum_tuple(mod_name) for mod_name in self.get_all_module_names()]
        self.placeables = res if len(res) > 1 else [empty_list_placeholder_enum_tuple]

        # Find max hub termini
        self.max_hub_branches = 0
        for hub_name in self.xdb['modules']['hubs']:
            hub_branches = max_hub_free_termini(hub_name, self.xdb)
            self.max_hub_branches = max(hub_branches, self.max_hub_branches)

    def get_all_module_names(self):
        groups = (self.xdb['modules']['singles'], self.xdb['modules']['hubs'])
        xdb_mod_names = {k for group in groups for k in group.keys()}
        return (mod_name for mod_name in self.library if mod_name in xdb_mod_names)

    def load_xdb(self, skip_derivatives_update=False):
        with open(addon_paths.xdb_path, 'r') as file:
            self.xdb = collections.OrderedDict(json.load(file))
        if not skip_derivatives_update:
            self.update_derivatives()
        print('{}: Xdb loaded'.format(__class__.__name__))

    def load_library(self, skip_derivatives_update=False):
        with bpy.types.BlendDataLibraries.load(addon_paths.modlib_path) as (data_from, data_to):
            self.library = data_from.objects
        if not skip_derivatives_update:
            self.update_derivatives()
        print('{}: Module library loaded'.format(__class__.__name__))

    def load_path_guide(self):
        with bpy.types.BlendDataLibraries.load(addon_paths.pguide_path) as (data_from, data_to):
            self.pguide = data_from.objects
        print('{}: Path guide library loaded'.format(__class__.__name__))

    def reset(self):
        self.n_extrudables = [empty_list_placeholder_enum_tuple]
        self.c_extrudables = [empty_list_placeholder_enum_tuple]
        self.placeables = [empty_list_placeholder_enum_tuple]
        self.max_hub_branches = 0
        self.load_all()
        self.num = 3

    def load_all(self):
        self.load_xdb(skip_derivatives_update=True)
        self.load_library(skip_derivatives_update=True)
        self.load_path_guide()
        self.update_derivatives()

random.seed()
class ColorWheel(metaclass=Singleton):
    hue_diff = 0.14
    lightness_base = 0.4
    lightness_variance = 0.3
    saturation_base = 0.8
    saturation_variance = .2
    def __init__(self):
        self.hue = random.random()
    
    def next_color(self, ):
        self.hue += (self.hue_diff / 2) + random.random() * (1 - self.hue_diff)
        lightness = self.lightness_base + \
            random.random() * self.lightness_variance
        saturation = self.saturation_base + \
            random.random() * self.saturation_variance
        return colorsys.hls_to_rgb(
            self.hue % 1.0, 
            lightness % 1.0, 
            saturation % 1.0
        )

# Decorator for functions that receive a Blender object
class object_receiver:
    """Passes object to func by argument if specified, otherwise use the
    selected object.
    """
    def __init__(self, func):
        self.func = func
        functools.update_wrapper(self, func)

    def __call__(self, obj=None, *args, **kwargs):
        if not obj:
            if get_selection_len() == 0:
                print('No object specified nor selected.')
                return
            return [self.func(obj, *args, **kwargs) for obj in get_selected(-1)]
        else:
            return self.func(obj, *args, **kwargs)

# Quick Access Methods ---------------------------

@object_receiver
def get_mirrors(obj):
    return obj.elfin.mirrors

@object_receiver
def get_elfin(obj):
    return obj.elfin

@object_receiver
def show_links(obj):
    obj.elfin.show_links()

def count_obj():
    return len(bpy.data.objects)

def get_xdb():
    return LivebuildState().xdb

def hub_is_symmetric(hub_name):
    return LivebuildState().xdb['modules']['hubs'][hub_name]['symmetric']

def get_n_to_c_tx(mod_a, chain_a, mod_b, chain_b):
    xdb = get_xdb()
    if mod_is_single(mod_a):
        meta_a = xdb['modules']['singles'][mod_a]
    elif mod_is_hub(mod_a):
        meta_a = xdb['modules']['hubs'][mod_a]

    tx_id = meta_a['chains'][chain_a]['c'][mod_b][chain_b]
    tx_json = xdb['n_to_c_tx'][tx_id]

    tx = mathutils.Matrix(tx_json['rot']).to_4x4()
    tx.translation = tx_json['tran']
    return tx

def mod_is_hub(mod_name):
    return mod_name in get_xdb()['modules']['hubs']

def mod_is_single(mod_name):
    return mod_name in get_xdb()['modules']['singles']

def get_selection_len():
    return len(bpy.context.selected_objects)

def get_selected(n=1):
    """
    Return the first n selected object, or None if nothing is selected.
    """
    if get_selection_len():
        selection = bpy.context.selected_objects
        if n == 1:
            return selection[0]
        elif n == -1:
            return selection[:]
        else:
            return selection[:n]
    else:
        return []

# Helpers ----------------------------------------

def add_module(mod_name, color, follow_selection=True):
    lmod = import_module(mod_name)

    give_module_new_color(lmod, color)

    # Cache active_object because it changes with create_network()
    location = [0, 0, 0]
    if follow_selection and get_selection_len():
        location = bpy.context.active_object.\
            matrix_world.translation.copy()
        for s in get_selected(-1):
            s.select = False

    # Imported objects are hidden by default.
    lmod.hide = False

    # Create a new empty object as network parent.
    network_parent = create_network('module')
    network_parent.matrix_world.translation = location
    lmod.parent = network_parent

    # Select new object.
    lmod.select = True

    # If not set to lmod, it would be the parent, which will lead to
    # failure when trying to select parent via Shift-G + P
    bpy.context.scene.objects.active = lmod

    return lmod

def get_ordered_selection():
    # Returns objects such that obj_a was selected before obj_b.
    obj_a, obj_b = None, None
    if get_selection_len() == 2:
        obj_a, obj_b = get_selected(-1)
        if bpy.context.active_object == obj_a:
            obj_a, obj_b = obj_b, obj_a
    return obj_a, obj_b

def max_hub_free_termini(mod_name, xdb=None):
    free_termini = 0
    if not xdb:
        xdb = get_xdb()
    hub_meta = xdb['modules']['hubs'][mod_name]
    for chain_id, termini_meta in hub_meta['chains'].items():
        free_termini += \
            (len(termini_meta['n']) > 0) + (len(termini_meta['c']) > 0)
    return free_termini

def selection_check(
    selection=None, 
    n_modules=0, 
    n_joints=0, 
    n_bridges=0, 
    n_networks=0, 
    n_pg_networks=0):
    """Counts objects in all (or provided) selection and checks whether all
    expected counts are met.
    """

    if selection is None:
        selection = get_selected(-1)

    for obj in selection:
        if obj.elfin.is_module():
            n_modules -= 1
            if n_modules < 0: return False
        elif obj.elfin.is_joint():
            n_joints -= 1
            if n_joints < 0: return False
        elif obj.elfin.is_bridge():
            n_bridges -= 1
            if n_bridges < 0: return False
        elif obj.elfin.is_network():
            n_networks -= 1
            if n_networks < 0: return False
        elif obj.elfin.is_pg_network():
            n_pg_networks -= 1
            if n_pg_networks < 0: return False

    return n_modules == n_joints == n_bridges == n_networks == n_pg_networks == 0

def find_symmetric_hub(network_parents):
    """Returns the symmetric hub center piece if there is one, else None.
    """
    xdb = get_xdb()
    walkers = [walk_network(np.children[0]) for np in network_parents]
    for walker in walkers:
        for m in walker:
            m_name = m.elfin.module_name
            if m_name in xdb['modules']['hubs'] and hub_is_symmetric(m_name):
                return m

    return None

def transfer_network(mod, existing_network=None):
    """Move all modules or pguides on the same network as mod under a new
    network parent object.
    """
    old_network = mod.parent
    if old_network.elfin.is_network():
        network_type = 'module'
    elif old_network.elfin.is_pg_network():
        network_type = 'pguide'
    else:
        print('Invalid object passed to transfer_network():', mod)
        return

    new_network = create_network(network_type)

    # Gather all network objects into a list and calculate COM
    com = mathutils.Vector([0, 0, 0])
    network_obj = []

    walker = walk_network if network_type == 'module' else walk_pg_network
    # old network must be walked instead of using children because when
    # severing, we rely on link information to decide whether to split
    # networks.
    for m in walker(mod):
        network_obj.append(m)
        com += m.matrix_world.translation

    existing_network_children = existing_network.children if existing_network else ()
    for c in existing_network_children:
        network_obj.append(c)
        com += c.matrix_world.translation

    com = com / len(network_obj)
    new_network.location = com
    bpy.context.scene.update() # Mandatory update to reflect new parent transform
    for m in network_obj:
        change_parent_preserve_transform(m, new_network)

    if not old_network.children:
        print('---First network destroy:', old_network.name)
        old_network.elfin.destroy()

    if existing_network and \
        existing_network != old_network and \
        not existing_network.children:
        print('---Second network destroy:', existing_network.name)
        existing_network.elfin.destroy()

def create_network(network_type):
    """Creates and returns a new arrow object as a network parent object, preserving
    selection.
    """
    selection = get_selected(-1)
    for s in selection: s.select = False

    bpy.ops.object.empty_add(type='ARROWS')
    nw = get_selected()
    nw.select = False
    nw.elfin.init_network(nw, network_type)

    for s in selection: s.select = True

    return nw

def check_network_integrity(network):
    """Returns the network (list of modules) consists of a single network and
    is spatially well formed, meaning all interfaces of the network must be
    the way they were found by elfin as elfin had placed them via extrusion.
    Network level transformations should not destroy well-formed-ness.
    """
    ... # Currently not needed
    return NotImplementedError

def import_joint():
    """Links a bridge object and initializes it using two end joints."""
    joint = None
    try:
        with bpy.data.libraries.load(addon_paths.pguide_path) as (data_from, data_to):
            data_to.objects = ['joint']

        joint = bpy.context.scene.objects.link(data_to.objects[0]).object
        joint.elfin.init_joint(joint)

        return joint
    except Exception as e:
        if joint: 
            # In case something went wrong before this line in try
            joint.elfin.obj_ptr = joint
            joint.elfin.destroy()
        raise e

def import_bridge(joint_a, joint_b):
    """Links a bridge object and initializes it using two end joints."""
    bridge = None
    try:
        with bpy.data.libraries.load(addon_paths.pguide_path) as (data_from, data_to):
            data_to.objects = ['bridge']

        bridge = bpy.context.scene.objects.link(data_to.objects[0]).object
        bridge.elfin.init_bridge(bridge, joint_a, joint_b)

        return bridge
    except Exception as e:
        if bridge: 
            # In case something went wrong before this line in try
            bridge.elfin.obj_ptr = bridge
            bridge.elfin.destroy()
        raise e

def module_menu(self, context): 
    self.layout.menu("INFO_MT_elfin_add", icon="PLUGIN")

def walk_pg_network(joint, initial=True):
    """A generator that traverses the path guide network depth-first and
    yields each object on the way, without repeating.
    """
    if not joint.elfin.is_joint():
        joint = joint.elfin.pg_neighbors[0].obj;

    if initial:
        for pg in joint.parent.children:
            pg.elfin.node_walked = False

    yield joint
    joint.elfin.node_walked = True

    for bridge_nb in joint.elfin.pg_neighbors:
        bridge = bridge_nb.obj
        for other_end_nb in bridge.elfin.pg_neighbors:
            other_end = other_end_nb.obj
            if not other_end.elfin.node_walked:
                yield from walk_pg_network(other_end, initial=False)

def walk_network(module, initial=True):
    """A generator that traverses the module network depth-first and yields
    each object on the way, without repeating.
    """

    if not module.elfin.is_module():
        return

    if initial:
        for pg in module.parent.children:
            pg.elfin.node_walked = False

    yield module
    module.elfin.node_walked = True

    # Walk n-terminus first
    for n_obj in module.elfin.n_linkage:
        if not n_obj.target_mod.elfin.node_walked:
            yield from walk_network(module=n_obj.target_mod, initial=False)

    # Then c-terminus
    for c_obj in module.elfin.c_linkage:
        if not c_obj.target_mod.elfin.node_walked:
            yield from walk_network(module=c_obj.target_mod, initial=False)

IncompatibleModuleError = ValueError('Modules are not compatible!')
def extrude_terminus(which_term, selector, sel_mod, color, reporter):
    """Extrudes selector module at the which_term of sel_mod"""
    assert which_term in {'n', 'c'}

    all_ext_mods = []
    result_signal = {'FINISHED'}
    ext_mod = None
    try:
        sel_mod_name = sel_mod.elfin.module_name
        sel_mod.select = False

        # Extract chain IDs and module name
        c_chain, ext_mod_name, n_chain = \
            selector.split('.')
        ext_mod = import_module(ext_mod_name)
        all_ext_mods.append(ext_mod)

        extrude_from = n_chain if which_term == 'n' else c_chain
        extrude_into = c_chain if which_term == 'n' else n_chain
        sel_ext_type_pair = (sel_mod.elfin.module_type, ext_mod.elfin.module_type)

        print(('Extruding module {to_mod} (chain {to_chain})'
            ' from {from_mod}\'s {terminus}-Term (chain {from_chain})').format(
            to_mod=selector, 
            to_chain=extrude_into,
            from_mod=sel_mod_name,
            terminus=which_term.upper(),
            from_chain=extrude_from))

        def project_extruded_mod(fixed_mod, ext_mod, src_chain=extrude_from):
            tx = get_tx(
                fixed_mod, 
                src_chain,
                extrude_into,
                ext_mod, 
                which_term, 
                sel_ext_type_pair
                )
            if not tx and reporter is not None:
                reporter.report({'ERROR'}, str(IncompatibleModuleError))
                raise IncompatibleModuleError

            ext_mod.matrix_world = tx * ext_mod.matrix_world

            # touch up
            bpy.context.scene.update() # Update to get the correct matrices
            change_parent_preserve_transform(ext_mod, fixed_mod.parent)

            give_module_new_color(ext_mod, color)
            ext_mod.hide = False # Unhide (default is hidden)
            if which_term == 'n':
                fixed_mod.elfin.new_n_link(src_chain, ext_mod, extrude_into)
                ext_mod.elfin.new_c_link(extrude_into, fixed_mod, src_chain)
            else:
                fixed_mod.elfin.new_c_link(src_chain, ext_mod, extrude_into)
                ext_mod.elfin.new_n_link(extrude_into, fixed_mod, src_chain)
            ext_mod.select = True

            return [ext_mod] # for mirror linking

        xdb = get_xdb()
        if sel_ext_type_pair in {('single', 'single'), ('single', 'hub')}:
            project_extruded_mod(sel_mod, ext_mod)

            if sel_mod.elfin.mirrors:
                all_ext_mods += mirrored_extrude(
                    root_mod=sel_mod, 
                    new_mirrors=[ext_mod], 
                    ext_mod_name=ext_mod_name, 
                    extrude_func=project_extruded_mod)
        elif sel_ext_type_pair == ('hub', 'single'):
            #
            # Extrude from hub to single.
            #
            hub_meta = xdb['modules']['hubs'][sel_mod_name]
            def extrude_hub_single(sel_mod, new_mod):
                project_extruded_mod(sel_mod, new_mod, src_chain=extrude_from)

                mirrors = [new_mod]

                if hub_meta['symmetric']:
                    # Calculate non-occupied chain IDs
                    hub_all_chains = set(hub_meta['chains'].keys())
                    if which_term == 'n':
                        hub_busy_chains = set(sel_mod.elfin.n_linkage.keys()) 
                    else:
                        hub_busy_chains = set(sel_mod.elfin.c_linkage.keys())
                    hub_free_chains = hub_all_chains - hub_busy_chains

                    imported = mirrored_symhub_extrude(
                        sel_mod,
                        mirrors,
                        hub_free_chains,
                        ext_mod_name,
                        project_extruded_mod)

                    all_ext_mods.extend(imported)
                
                return mirrors

            first_mirror_group = extrude_hub_single(sel_mod, ext_mod)

            if sel_mod.elfin.mirrors:
                all_ext_mods += mirrored_extrude(
                    root_mod=sel_mod,
                    new_mirrors=first_mirror_group,
                    ext_mod_name=ext_mod_name,
                    extrude_func=extrude_hub_single)

        elif sel_ext_type_pair == ('hub', 'hub'):
            #
            # Extrude from hub to hub is NOT allowed.
            #
            raise NotImplementedError
        else:
            raise ValueError('Invalid sel_ext_type_pair: {}'.format(sel_ext_type_pair))

    except Exception as e:
        if ext_mod:
            # In case something went wrong before this line in try
            ext_mod.elfin.obj_ptr = ext_mod
            ext_mod.elfin.destroy()
        sel_mod.select = True # Restore selection

        if e != IncompatibleModuleError:
            raise e

        result_signal = {'CANCELLED'}

    return all_ext_mods, result_signal

def execute_extrusion(which_term, selector, color, reporter):
    """Executes extrusion respecting mirror links and filers mirror selections
    """
    if selector in nop_enum_selectors:
        return {'FINISHED'}

    filter_mirror_selection()
    for sel_mod in get_selected(-1): 
        _, signal = extrude_terminus(
                which_term, 
                selector, 
                sel_mod, 
                color, 
                reporter)
        return signal

    return {'FINISHED'}

def get_extrusion_prototype_list(sel_mod, which_term):
    """Generates a prototype list appropriately filtered for extrusion.
    """
    assert which_term in {'n', 'c'}

    enum_tuples = [color_change_placeholder_enum_tuple]

    # Selection length is guranteed by poll()
    sel_mod_name = sel_mod.elfin.module_name
    sel_mod_type = sel_mod.elfin.module_type

    xdb = get_xdb()
    if sel_mod_type == 'hub':
        hub_meta = xdb['modules']['hubs'][sel_mod_name]
        if which_term == 'n':
            occupied_termini = sel_mod.elfin.n_linkage.keys()
        else:
            occupied_termini = sel_mod.elfin.c_linkage.keys()

        for src_chain_id, chain_meta in hub_meta['chains'].items():
            if src_chain_id in occupied_termini: 
                continue

            for single_name in chain_meta[which_term]:
                single_chains = chain_meta[which_term][single_name]
                assert(len(single_chains) == 1)
                dst_chain_id = list(single_chains.keys())[0]

                enum_tuples.append(
                    module_enum_tuple(
                        single_name, 
                        extrude_from=src_chain_id, 
                        extrude_into=dst_chain_id,
                        direction=which_term))

            # Only allow one chain to be extruded because other
            # "mirrors" will be generated automatically
            if hub_meta['symmetric']: 
                break
    elif sel_mod_type == 'single':
        # Checks for occupancy by counting n/c termini links
        if which_term == 'n':
            link_len = len(sel_mod.elfin.n_linkage)
        else:
            link_len = len(sel_mod.elfin.c_linkage)

        if link_len == 0:
            single_meta = xdb['modules']['singles'][sel_mod_name]
            chain_meta = single_meta['chains']
            chain_id_list = list(chain_meta.keys())
            assert len(chain_id_list) == 1

            single_chain_name = chain_id_list[0]
            term_meta = chain_meta[single_chain_name][which_term]
            for ext_mod_name in term_meta:
                for ext_mod_chain_name in term_meta[ext_mod_name]:
                    enum_tuples.append(
                        module_enum_tuple(
                            ext_mod_name,
                            extrude_from=single_chain_name,
                            extrude_into=ext_mod_chain_name,
                            direction=which_term))
    else:
        raise ValueError('Unknown module type: ', sel_mod_type)

    # Remove color change placeholder if nothing can be extruded
    return enum_tuples if len(enum_tuples) > 1 else []

def change_parent_preserve_transform(child, new_parent):
    mw = child.matrix_world.copy()
    child.parent = new_parent
    child.matrix_world = mw

def get_tx(
    fixed_mod, 
    extrude_from,
    extrude_into,
    ext_mod, 
    which_term, 
    mod_types
    ):
    """Returns the transformation matrix for when ext_mod is extruded from
    fixed_mod's which_term.
    """
    assert which_term in {'n', 'c'}

    fixed_mod_name = fixed_mod.elfin.module_name
    ext_mod_name = ext_mod.elfin.module_name
    xdb = get_xdb()

    tx = None
    try:
        if which_term == 'n':
            mod_params = (ext_mod_name, extrude_into, fixed_mod_name, extrude_from)
        else:
            mod_params = (fixed_mod_name, extrude_from, ext_mod_name, extrude_into)

        n_to_c_tx = get_n_to_c_tx(*mod_params)

        if mod_types == ('single', 'single'):
            tx = scale_and_shift(n_to_c_tx, which_term == 'n', fixed_mod)

        elif mod_types == ('single', 'hub'):
            # dbgen.py only creates Hub-to-Single transforms. Single-to-Hub is
            # therefore always the inverse.
            tx = scale_and_shift(n_to_c_tx, True, fixed_mod)

        elif mod_types == ('hub', 'single'):
            tx = scale_and_shift(n_to_c_tx, False, fixed_mod)

        else:
            raise ValueError('Invalid mod_types: ({}, {})'.format(*mod_types))

    except KeyError as ke:
        tx = None
        raise ke

    return tx

def unlink_mirror(modules=None):
    mods = modules[:] if modules else bpy.context.selected_objects[:]
    if not mods: return
    for m in mods: 
        m.elfin.mirrors = None

def link_by_mirror(modules=None):
    mirrors = modules[:] if modules else bpy.context.selected_objects[:]
    if not mirrors: return
    m0 = mirrors[0]
    for i in range(1, len(mirrors)):
        if mirrors[i].elfin.module_name != m0.elfin.module_name:
            print('Error: selected modules are not of the same prototype')
            return
    for m in mirrors:
        m.elfin.mirrors = mirrors[:]

def mirrored_symhub_extrude(
    root_symhub,
    new_mirrors,
    hub_free_chains,
    ext_mod_name,
    extrude_func):
    imported = []

    for src_chain_id in hub_free_chains:
        mirror_mod = import_module(ext_mod_name)
        imported.append(mirror_mod)

        # Assign to the same network.
        mirror_mod.parent = root_symhub.parent
        extrude_func(root_symhub, mirror_mod, src_chain_id)

    new_mirrors += imported
    for m in new_mirrors:
        m.elfin.mirrors = new_mirrors

    return imported

def mirrored_extrude(
    root_mod, 
    new_mirrors, 
    ext_mod_name,
    extrude_func):
    imported = []

    for m in root_mod.elfin.mirrors:
        if m != root_mod:
            mirror_mod = import_module(ext_mod_name)
            imported.append(mirror_mod)

            # Assign to the same network.
            mirror_mod.parent = m.parent
            new_mirrors += extrude_func(m, mirror_mod)

    for m in new_mirrors:
        m.elfin.mirrors = new_mirrors

    return imported

def filter_mirror_selection():
    for s in bpy.context.selected_objects:
        if s.select and s.elfin.mirrors:
            for m in s.elfin.mirrors:
                # Note that m could be the next s!
                if m and m != s: m.select = False

def suitable_for_extrusion(context):
    """Checks selection is not none and is homogenous.
    """
    selection = context.selected_objects
    n_objs = len(selection)
    if n_objs == 0:
        return False

    # In object mode?
    if selection[0].mode != 'OBJECT':
        return False

    # Homogenous?
    first_mod_name = selection[0].elfin.module_name
    for o in selection:
        if not o.elfin.is_module() or o.elfin.module_name != first_mod_name:
            return False
    return True

def give_module_new_color(mod, new_color=None):
    mat = bpy.data.materials.new(name='mat_' + mod.name)
    mat.diffuse_color = new_color if new_color else ColorWheel().next_color()
    mod.data.materials.append(mat)
    mod.active_material = mat

def overlapping_module_exists():
    """Determines whether there is any overlapping module.
    """
    bpy.context.scene.update()
    mods = [o for o in bpy.context.scene.objects if o.elfin.is_module()]

    for mod in mods:
        if find_overlap(mod, mods):
            return True
            
    return False

def delete_if_overlap(obj, obj_list):
    """
    Delete obj if it overlaps with any object in obj_list.

    Caller is responsible for providing the right object and list. No module
    check is done.
    """

    # Update must be called first because operations like extrude will first
    # transform the object.
    bpy.context.scene.update()
    if find_overlap(obj, obj_list):
        obj.elfin.destroy()
        return True
    return False

def find_overlap(test_obj, obj_list, scale_factor=0.85):
    """
    Tests whether an object's mesh overlaps with any mesh in obj_list.

    Caller is responsible for providing the right object and list. No module
    check is done.

    Args: 
     - test_obj - the object under test.
     - obj_list - optional; the list of objects to test against.
     - scale_factor - optional; the scale to apply before testing.

    Returns:
     - bool - whether or not a collision (overlap) was found.
    """
    scale = mathutils.Matrix.Scale(scale_factor, 4)

    mod_bm = bmesh.new()
    mod_bm.from_mesh(test_obj.data)
    mod_bm.transform(test_obj.matrix_world * scale)
    mod_bvh_tree = mathutils.bvhtree.BVHTree.FromBMesh(mod_bm)
    for ob in obj_list:
        if ob == test_obj:
            continue

        ob_bm = bmesh.new()
        ob_bm.from_mesh(ob.data)
        ob_bm.transform(ob.matrix_world * scale)
        ob_bvh_tree = mathutils.bvhtree.BVHTree.FromBMesh(ob_bm)

        overlaps = mod_bvh_tree.overlap(ob_bvh_tree)

        if len(overlaps) > 0:
            return ob

    return None

def scale_and_shift(n_to_c_tx, invert=False, fixed_mod=None):
    tx = pymol_to_blender_scale(n_to_c_tx)

    if invert:
        tran = tx.translation.copy()
        tx.translation = [0, 0, 0]
        tx.transpose()
        tx.translation = tx * -tran

    if fixed_mod != None:
        tx = equalize_frame(tx, fixed_mod)
    return tx

def equalize_frame(tx, fixed_mod):
    trans, rot, _ = fixed_mod.matrix_world.decompose()
    delta = rot.to_matrix().to_4x4()
    delta.translation = trans
    return delta * tx

def scaleless_rot_tran(obj):
    mw = obj.matrix_world.copy()

    # Decompose matrix_world to remove 0.1 scale
    tran = mathutils.Matrix.Translation(mw.translation)
    rot = mw.to_euler().to_matrix().to_4x4()

    return rot, tran

def pymol_to_blender_scale(n_to_c_tx):
    tx = mathutils.Matrix(n_to_c_tx)
    for i in range(0, 3):
        tx[i][3] /= blender_pymol_unit_conversion
    return tx

def get_compatible_hub_chains(hub_name, single_term, single_name):
    assert single_term in {'n', 'c'}

    hub_term = { 'n': 'c', 'c': 'n' }[single_term]

    chain_meta = get_xdb()['modules']['hubs'][hub_name]['chains']

    compat_hub_chains = []
    for chain_name in chain_meta:
        if single_name in chain_meta[chain_name][hub_term].keys():
            compat_hub_chains.append(chain_name)
    return compat_hub_chains

def module_enum_tuple(mod_name, extrude_from=None, extrude_into=None, direction=None):
    """Creates an enum tuple storing the single module selector, prefixed or
    suffixed by the terminus of a hub from/to which the single module is
    extruded.

    Enum selector format: C-Chain ID, Module, N-Chain ID

    Example context:    
        Let module A receive an extrusion opereation which attempts to add B
        to A's n-terminus. 
    args:
     - mod_name: module B's name.
     - extrude_from: module A's chain ID that is receiving extrusion.
     - extrude_into: module B's chain ID that is complementing the extrusion.
     - direction: is B being added to A's c-terminus or n-terminus.

    """
    if direction is not None:
        assert direction in {'n', 'c'}
        assert extrude_from is not None
        if extrude_into is None:
            extrude_into = ''

    # Keep the selector format: n_chain, mod, c_chain
    if direction == 'c':
        mod_sel = '.'.join([extrude_from, mod_name, extrude_into])
        display = ':{}(C) -> (N){}:{}.'.format(extrude_from, extrude_into, mod_name)
    elif direction == 'n':
        mod_sel = '.'.join([extrude_into, mod_name, extrude_from])
        display = ':{}(N) -> (C){}:{}.'.format(extrude_from, extrude_into, mod_name)
    else:
        mod_sel = '.'.join(['', mod_name, ''])
        display = mod_sel

    return (mod_sel, display, '')

def import_module(mod_name):
    """Links a module object from library.blend. Supports all module types."""
    lmod = None
    try:
        with bpy.data.libraries.load(addon_paths.modlib_path) as (data_from, data_to):
            data_to.objects = [mod_name]

        lmod = bpy.context.scene.objects.link(data_to.objects[0]).object

        lmod.elfin.init_module(lmod, mod_name)

        return lmod
    except Exception as e:
        if lmod: 
            # In case something went wrong before this line in try
            lmod.elfin.obj_ptr = lmod
            lmod.elfin.destroy()
        raise e
