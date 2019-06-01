import enum
import collections

import inspect

import bpy
import mathutils
from . import livebuild_helper as lh

ElfinObjType = enum.Enum('ElfinObjType', 'NONE MODULE JOINT BRIDGE NETWORK PG_NETWORK')

# translation tolerance in Angstroms - independent of conversion scale
bridge_default_tx_tol = 5.0

class Link(bpy.types.PropertyGroup):
    terminus = bpy.props.StringProperty()
    source_chain_id = bpy.props.StringProperty()
    target_mod = bpy.props.PointerProperty(type=bpy.types.Object)
    target_chain_id = bpy.props.StringProperty()

    def __repr__(self):
        return 'Link => (Src CID={}, Tgt={}, Tgt CID={})'.format(
            self.source_chain_id, self.target_mod, self.target_chain_id)

    def as_dict(self):
        return {
            'terminus': self.terminus,
            'source_chain_id': self.source_chain_id,
            'target_mod': self.target_mod.name,
            'target_chain_id': self.target_chain_id
        }

    def sever(self):
        if self.target_mod:
            tl = self.target_mod.elfin.n_linkage \
                if self.terminus == 'c' else \
                self.target_mod.elfin.c_linkage
            print('Severing: ', repr(self))

            tl.remove(tl.find(self.target_chain_id))

class ObjectPointerWrapper(bpy.types.PropertyGroup):
    obj = bpy.props.PointerProperty(type=bpy.types.Object)

class ElfinObjectProperties(bpy.types.PropertyGroup):
    """Represents an elfin object (module/joint/bridge)."""
    obj_type = bpy.props.IntProperty(default=ElfinObjType.NONE.value)
    module_name = bpy.props.StringProperty()
    module_type = bpy.props.StringProperty()
    obj_ptr = bpy.props.PointerProperty(type=bpy.types.Object)

    c_linkage = bpy.props.CollectionProperty(type=Link)
    n_linkage = bpy.props.CollectionProperty(type=Link)
    pg_neighbors = bpy.props.CollectionProperty(type=ObjectPointerWrapper)
    tx_tol = bpy.props.FloatProperty(min=0.0, default=0.0)

    node_walked = bpy.props.BoolProperty(default=False)
    destroy_entered = bpy.props.BoolProperty(default=False)

    def get_available_links(self):
        busy_links = len(self.n_linkage) + len(self.c_linkage)
        return self.get_max_links() - busy_links

    def get_max_links(self):
        """Returns the maximum number of links supported by this module
        """
        max_links = 0
        if self.is_module():
            if self.module_type == 'single':
                max_links = 2
            elif self.module_type == 'hub':
                max_links = lh.max_hub_free_termini(self.module_name)

        return max_links

    def get_neighbor_joint_names(self):
        nbs = []
        for pgn in self.pg_neighbors:
            bridge = pgn.obj
            for other_end_nb in bridge.elfin.pg_neighbors:
                other_end = other_end_nb.obj
                if other_end != self.obj_ptr:
                    nbs.append(other_end.name)
        return nbs

    def as_dict(self):
        data = collections.OrderedDict()

        if self.is_module():
            data['module_name'] = self.module_name
            data['module_type'] = self.module_type
            data['c_linkage'] = [cl.as_dict() for cl in self.c_linkage]
            data['n_linkage'] = [nl.as_dict() for nl in self.n_linkage]
        elif self.is_joint():
            data['occupant'] = '' # a module that has the same COM as this joint
            data['occupant_parent'] = '' # occupant network name
            data['hinge'] = '' # refers to the neighbor that has an occupant
            data['tx_tol'] = 0.0 # translation tolerance in Angstroms

            """
            Rotation tolerance example:
            {
                vector: [v.a, v.b, v.c],
                angle: 10
            }

            This should set up a vector going in the specified direction,
            using the hinge as origin. The bridge is allowed to swing +/- 10
            degrees around this vector.

            This is meant to be entered by the user manually in the exported
            JSON file. In the future a UI might be implemented to better
            facilitate this control.
            """
            data['rt_tol'] = []
            data['neighbors'] = self.get_neighbor_joint_names()
        else:
            raise ValueError('Should not convert this elfin object to dict: {}'.format(self.obj_type))
        
        wm = self.obj_ptr.matrix_world
        
        tran, rot, _ = wm.decompose()
        tran = tran * lh.blender_pymol_unit_conversion
        data['rot'] = list(list(vec) for vec in rot.to_matrix())
        data['tran'] = list(tran)
        
        return data

    def joint_connects_joint(self, other_mod):
        if not self.is_joint() or \
            not other_mod or not other_mod.elfin.is_joint():
            return False

        for nb in self.pg_neighbors:
            if nb.obj.elfin.bridge_connects_joints(self.obj_ptr, other_mod):
                return True

        return False

    def bridge_connects_joints(self, mod_a, mod_b):
        if not self.is_bridge():
            return False

        return tuple((nb.obj for nb in self.pg_neighbors)) in \
            ((mod_a, mod_b), (mod_b, mod_a))

    def find_link(self, mod_b):
        """Tries to find a link between mod_a and mod_b, or returns None if
        not found.
        """
        for cl in self.c_linkage:
            if cl.target_mod == mod_b:
                return cl, self.c_linkage
        for nl in self.n_linkage:
            if nl.target_mod == mod_b:
                return nl, self.n_linkage

        return None

    def is_module(self):
        return self.obj_type == ElfinObjType.MODULE.value

    def is_joint(self):
        return self.obj_type == ElfinObjType.JOINT.value

    def is_bridge(self):
        return self.obj_type == ElfinObjType.BRIDGE.value

    def is_network(self):
        return self.obj_type == ElfinObjType.NETWORK.value

    def is_pg_network(self):
        return self.obj_type == ElfinObjType.PG_NETWORK.value

    def destroy(self):
        """Clean up elfin data of this object, then call delete on the
        associated object.
        """

        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        print('Destroy caller name:', calframe[1][3])

        # Prevent parent calling child destroy infinite loop
        if self.destroy_entered:
            return
        else:
            self.destroy_entered = True

        if not self.obj_ptr:
            print('elfin.destroy() called with self.obj_ptr == None')
            print('Type:', ElfinObjType(self.obj_type).name)
            return

        print('Enter destroy() of', self.obj_ptr)
        parent = self.obj_ptr.parent

        if self.is_module():
            self.cleanup_module()
        elif self.is_joint():
            self.cleanup_joint()
        elif self.is_bridge():
            self.cleanup_bridge()
        elif self.is_network() or self.is_pg_network():
            self.cleanup_network()
        else:
            return # No obj_ptr to delete

        print('Cleaned up', self.obj_ptr)

        self.delete_object(self.obj_ptr)

        if parent and \
            (parent.elfin.is_network() or \
            parent.elfin.is_pg_network()) and \
            len(parent.children) == 0:
            parent.elfin.destroy()

        bpy.context.scene.update() # Flush out dead object

    def delete_object(self, obj):
        """
        Delete the Blender object to which the current elfin object
        PropertyGroup is associated with, preserving selection. 
        """

        # Cache user selection
        selection = [o for o in bpy.context.selected_objects if o != obj]
        bpy.ops.object.select_all(action='DESELECT')

        # Delete using default operator
        obj.hide = False
        obj.hide_select = False
        obj.select = True
        obj.use_fake_user = False

        bpy.ops.object.delete(use_global=False)

        # if obj and obj.name in bpy.data.objects:
        #     bpy.data.objects.remove(obj)

        # Restore selection
        for ob in selection:
            if ob: ob.select = True

    def cleanup_network(self):
        """Delete all children modules."""
        # [!] Do not call destroy on children modules. It will cause infinite
        # call loop.
        for obj in self.obj_ptr.children:
            self.delete_object(obj)

    def cleanup_bridge(self):
        """Remove references of self object and also pointer to joints."""
        # Preserve neighbor joints for pg-network separation
        nb_joints = {}
        for joint_nb in self.pg_neighbors:
            joint = joint_nb.obj
            nb_joints[joint.name] = joint

        # Detach self from parent joint
        self.obj_ptr.parent = None
        for opw in self.pg_neighbors:
            if opw.obj:
                rem_idx = -1
                jnb = opw.obj.elfin.pg_neighbors
                for i in range(len(jnb)):
                    if jnb[i].obj == self.obj_ptr:
                        rem_idx = i
                        break
                if rem_idx != -1:
                    jnb.remove(rem_idx)

        # Separate pg-networks
        while nb_joints:
            name, joint = nb_joints.popitem()
            lh.transfer_network(joint)

    def cleanup_joint(self):
        """Delete connected bridges"""

        # Detach from pg-network
        self.obj_ptr.parent = None
        for nb in self.pg_neighbors:
            bridge = nb.obj
            bridge_nbs = bridge.elfin.pg_neighbors

            # Dereference current joint
            for i in range(len(bridge_nbs)):
                if bridge_nbs[i].obj == self.obj_ptr:
                    break
            bridge_nbs.remove(i)

            bridge.elfin.destroy()

    def cleanup_module(self):
        # Preserve neighbors for network separation
        neighbors = {}
        for lk in self.c_linkage:
            if lk.target_mod:
                neighbors[lk.target_mod.name] = lk.target_mod
        for lk in self.n_linkage:
            if lk.target_mod:
                neighbors[lk.target_mod.name] = lk.target_mod
        old_network = self.obj_ptr.parent
        self.sever_links()

        # Destroy mirrors
        for m in self.mirrors:
            if m and m != self.obj_ptr:
                m.elfin.mirrors = []
                m.elfin.destroy()

        # Remove self from parent
        self.obj_ptr.parent = None

        # Separate networks
        while neighbors:
            name, mod = neighbors.popitem()

            # Could become None in some situations, 
            # such as a deleted mirrors
            if mod and mod.parent == old_network:
                lh.transfer_network(mod)

    def init_network(self, obj, network_type):
        assert network_type in {'module', 'pguide'}
        is_module_network = network_type == 'module'

        self.obj_ptr = obj
        self.obj_type = \
            ElfinObjType.NETWORK.value \
            if is_module_network else \
            ElfinObjType.PG_NETWORK.value
        obj.name = 'network' if is_module_network else 'pg_network'

        # Want to shift focus to new module, not network
        obj.select = False

        # Don't let user click on this object in viewport ?
        # This will disable #snp
        # obj.hide_select = True

        # Always trigger dirty exit so we can clean up
        obj.use_fake_user = True

    def init_bridge(self, obj, joint_a, joint_b):
        self.obj_ptr = obj
        self.obj_type = ElfinObjType.BRIDGE.value

        # Cache locations
        jb_loc = mathutils.Vector(joint_b.location)

        # Move ja and jb to default locations
        joint_b.location = joint_a.location + mathutils.Vector([0, 5, 0])

        bridge = self.obj_ptr
        bridge.parent = joint_b

        bridge.constraints.new(type='COPY_LOCATION').target = joint_a
        bridge.constraints.new(type='COPY_ROTATION').target = joint_a

        stretch_cons = bridge.constraints.new(type='STRETCH_TO')
        stretch_cons.target = joint_b
        stretch_cons.bulge = 0.0

        bridge.elfin.pg_neighbors.add().obj = joint_a
        bridge.elfin.pg_neighbors.add().obj = joint_b
        joint_a.elfin.pg_neighbors.add().obj = bridge
        joint_b.elfin.pg_neighbors.add().obj = bridge

        # Restore joint_b location 
        # 
        # [!] Must call update so that constraints don't bug out. This works
        # normally in Blender console if you copy paste the code of this
        # function but will break in script if update() is not called.
        bpy.context.scene.update()
        joint_b.location = jb_loc

        # Always trigger dirty exit so we can clean up
        obj.use_fake_user = True

        # Give some default tolerance to each bridge
        self.tx_tol = bridge_default_tx_tol

    def init_joint(self, obj):
        self.obj_ptr = obj
        self.obj_type = ElfinObjType.JOINT.value

        # Always trigger dirty exit so we can clean up
        obj.use_fake_user = True

    def init_module(self, obj, mod_name):
        self.obj_ptr = obj
        self.module_name = mod_name

        if lh.mod_is_single(mod_name):
            self.module_type = 'single'
        else:
            if lh.mod_is_hub(mod_name):
                self.module_type = 'hub'
            else:
                raise ValueError('Attempting link a module that is neither single or hub type\n')
        self.obj_type = ElfinObjType.MODULE.value

        # Lock all transformation - only allow network parent to transform
        obj.lock_location = obj.lock_rotation = obj.lock_scale = [True, True, True]
        obj.lock_rotation_w = obj.lock_rotations_4d = True

        # Always trigger dirty exit so we can clean up
        obj.use_fake_user = True

    def new_c_link(self, source_chain_id, target_mod, target_chain_id):
        link = self.c_linkage.add()
        link.name = link.source_chain_id = source_chain_id
        link.terminus = 'c'
        link.target_mod = target_mod
        link.target_chain_id = target_chain_id

    def new_n_link(self, source_chain_id, target_mod, target_chain_id):
        link = self.n_linkage.add()
        link.name = link.source_chain_id = source_chain_id
        link.terminus = 'n'
        link.target_mod = target_mod
        link.target_chain_id = target_chain_id

    def show_links(self):
        print('Links of {}'.format(self.obj_ptr.name))
        print('C links:')
        for cl in self.c_linkage: print(repr(cl))
        print('N links:')
        for nl in self.n_linkage: print(repr(nl))

    def sever_links(self):
        for cl in self.c_linkage: cl.sever()
        for nl in self.n_linkage: nl.sever()

    @property
    def mirrors(self):
        return self.get('_mirrors', [])

    @mirrors.setter
    def mirrors(self, value):
        self['_mirrors'] = value
