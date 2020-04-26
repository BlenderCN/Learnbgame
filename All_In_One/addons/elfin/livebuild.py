import bpy
import mathutils
from bpy_extras import view3d_utils

from . import addon_paths
from .livebuild_helper import *
from .elfin_object_properties import ElfinObjType

# Path guide operators ---------------------------
class SetTranslationToleranceSetting(bpy.types.Operator):
    bl_idname = 'elfin.translation_tolerance_setting'
    bl_label = 'Set bridge translation tolerance (#bxt)'
    bl_options = {'REGISTER', 'UNDO'}
    
    title = bpy.props.StringProperty(default='Bridge Translation Tolerance')
    icon = bpy.props.StringProperty(default='QUESTION')

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout
        row.label(self.title, icon=self.icon)

        sel_obj = context.selected_objects[0]
        row.prop(sel_obj.elfin, 'tx_tol', text='Mobility (Å)')

    @classmethod
    def poll(cls, context):
        return get_selection_len() == 1 and \
            context.selected_objects[0].elfin.is_bridge()

class AddBridge(bpy.types.Operator):
    bl_idname = 'elfin.add_bridge'
    bl_label = 'Add a bridge between two joints (#addb)'
    bl_options = {'REGISTER', 'UNDO'}

    not_a_joint_error = 'Could not bridge because {} is not a joint.'
    max_branch_error = ('Could not bridge because {} already has or '
                    'exceeds the maximum number of bridges possible.')
    already_bridged_error = 'Joints {} and {} are already bridged.'

    def clean_up(self):
        for b in self.bridges:
            if b:
                b.elfin.destroy()

    def add_bridge(self, jt_a, jt_b):
        msg = None

        max_hub_branches = LivebuildState().max_hub_branches
        if not jt_a.elfin.is_joint():
            msg = self.not_a_joint_error.format(jt_a.name)
        elif not jt_b.elfin.is_joint():
            msg = self.not_a_joint_error.format(jt_b.name)
        elif len(jt_a.elfin.pg_neighbors) >= max_hub_branches:
            msg = self.max_branch_error.format(jt_a.name)
        elif len(jt_b.elfin.pg_neighbors) >= max_hub_branches:
            msg = self.max_branch_error.format(jt_b.name)
        elif jt_a.elfin.joint_connects_joint(jt_b):
            msg = self.already_bridged_error.format(jt_a.name, jt_b.name)
        else:
            transfer_network(jt_a, jt_b.parent)
            bridge = import_bridge(jt_a, jt_b)
            self.bridges.append(bridge)

        return msg

    def modal(self, context, event):
        # allow selection events from mouse to pass through
        ret = {'PASS_THROUGH'} 
        if get_selection_len() >= 2:
            jt_a, jt_b = get_selected(2)
            if jt_a not in self.last_selected or \
                jt_b not in self.last_selected:

                # need to save active object identity because bridging shifts
                # active object to pg network
                active_object = context.active_object
                msg = self.add_bridge(jt_a, jt_b)

                if msg:
                    self.report({'ERROR'}, msg)
                    ret = {'CANCELLED'}
                else:
                    print('active:', active_object)
                    if jt_a == active_object:
                        jt_b.select = False
                    elif jt_b == active_object:
                        jt_a.select = False
                    else:
                        if jt_a in self.last_selected:
                            jt_b.select = False
                        elif jt_b in self.last_selected:
                            jt_a.select = False
                    while len(context.selected_objects) > 1:
                        context.selected_objects[-1].select = False
                    self.last_selected = {jt_a, jt_b}

        elif event.type == 'RIGHTMOUSE':
            ret = {'FINISHED'}
        elif event.type == 'ESC':
            self.clean_up()
            ret = {'CANCELLED'}

        if 'CANCELLED' in ret or 'FINISHED' in ret:
            bpy.context.window.cursor_modal_restore()

        return ret

    def invoke(self, context, event):
        self.last_selected = {}
        self.bridges = []
        bpy.context.window.cursor_modal_set('HAND')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class ExtrudeJoint(bpy.types.Operator):
    bl_idname = 'elfin.extrude_joint'
    bl_label = 'Extrude a path guide joint (#exj)'
    bl_options = {'REGISTER', 'UNDO'}

    def create_new_joint(self):
        self.joints = []
        for joint_a in get_selected(-1):
            joint_b = import_joint()
            joint_b.parent = joint_a.parent
            bridge = import_bridge(joint_a, joint_b)
            joint_b.location = [0,5,0]

            self.joints.append(
                (
                    joint_a,
                    joint_b
                )
            )

    def execute(self, context):
        #Contextual active object, 2D and 3D regions
        region = bpy.context.region
        region3D = bpy.context.space_data.region_3d

        mouse_offset = self.mouse

        # The direction indicated by the mouse position from the current view
        view_vector = view3d_utils.region_2d_to_vector_3d(region, region3D, mouse_offset)
        # The 3D location in this direction
        offset = view3d_utils.region_2d_to_location_3d(region, region3D, mouse_offset, view_vector)

        mw = self.active_joint.matrix_world.inverted()
        mouse_offset_from_first_ja = mw * offset
        for ja, jb in self.joints:
            jb.location = ja.location + mouse_offset_from_first_ja

        # Update active object so the next #exj will get the correct cursor
        # offset
        if jb:
            bpy.context.scene.objects.active = jb

        return {'FINISHED'}

    def modal(self, context, event):
        ret = {'RUNNING_MODAL'}
        if event.type == 'MOUSEMOVE':
            self.mouse = (event.mouse_region_x, event.mouse_region_y)
            self.execute(context)
        elif event.type == 'LEFTMOUSE':
            for s in get_selected(-1): 
                s.select = False
            for ja, jb in self.joints: 
                ja.select, jb.select = False, True
            ret = {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            for _, jb in self.joints:
                # Don't leave joints stacked on ja
                jb.elfin.destroy()
            ret = {'CANCELLED'}

        return ret

    def invoke(self, context, event):
        self.joints = []

        self.create_new_joint()
        self.mouse_origin = (event.mouse_region_x, event.mouse_region_y)

        # Redirect active object (which might not be in selection)
        if context.active_object and not context.active_object.elfin.is_joint():
            self.active_joint = get_selected(-1)[-1]
        else:
            self.active_joint = context.active_object
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    @classmethod
    def poll(cls, context):
        if get_selection_len() > 0:
            max_hub_branches = LivebuildState().max_hub_branches
            for s in get_selected(-1):
                if not s.elfin.is_joint() or \
                    len(s.elfin.pg_neighbors) >= max_hub_branches:
                    return False
            else:
                return True
        return False

class JointToModule(bpy.types.Operator):
    bl_idname = 'elfin.joint_to_module'
    bl_label = 'Move a joint to the COM of a module (#jtm).'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        joint, module = get_selected(-1)
        if joint.elfin.is_module():
            joint, module = module, joint

        joint.matrix_world.translation = \
            module.matrix_world.translation.copy()

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return selection_check(n_modules=1, n_joints=1)

class AddJoint(bpy.types.Operator):
    bl_idname = 'elfin.add_joint'
    bl_label = 'Add a path guide joint (#addj)'
    bl_options = {'REGISTER', 'UNDO'}

    def add_joint(self, at_mod=None):
        network = create_network('pguide')
        joint = import_joint()
        joint.parent = network

        network.location = [0, 0, 0]

        if at_mod:
            network.location = at_mod.matrix_world.translation.copy()

        joint.select = True

    def execute(self, context):
        # Put a joint on each of the selected modules
        sel = get_selected(-1)

        if sel:
            for o in sel:
                o.select = False
                if o.elfin.is_module():
                    self.add_joint(o)
        else:
            self.add_joint()

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        # Forbid adding joint on top of existing joint
        for s in get_selected(-1):
            if s.elfin.is_joint():
                return False
        return True

# Module network operators -----------------------
class JoinNetworks(bpy.types.Operator):
    bl_idname = 'elfin.join_networks'
    bl_label = 'Join two compatible networks (#jnw)'
    bl_property = "way_selector"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def relevant_extrudables(cls, extrudables, mod_name):
        res = []
        for ext in extrudables:
            if ext != color_change_placeholder_enum_tuple and \
                ext[0].split('.')[1] == mod_name:
                res.append(ext)
        return res

    def get_ways(self, context):
        # Check whether an extrusion is possible from mod_a to mod_b
        no_way = [empty_list_placeholder_enum_tuple]
        if get_selection_len() != 2:
            return no_way

        # mod_b is always the fixed module
        mod_a, mod_b = get_selected(-1)
        if context.active_object == mod_a:
            mod_a, mod_b = mod_b, mod_a

        # disable joining with a network containing symmetric hub
        if find_symmetric_hub([mod_a.parent, mod_b.parent]):
            return no_way

        a_mod_name = mod_a.elfin.module_name
        b_mod_name = mod_b.elfin.module_name

        # Don't allow pull-join on symmetric hubs (yet?)
        if mod_a.elfin.module_type == 'hub':
            if hub_is_symmetric(a_mod_name):
                return no_way
        if mod_b.elfin.module_type == 'hub':
            if hub_is_symmetric(b_mod_name):
                return no_way

        # Plan: get n/c extrudables for both modules, then find out the
        # shared termini and let the user choose
        n_extrudables, c_extrudables = LivebuildState().get_all_extrudables(mod_a)
        an_extrudables = JoinNetworks.relevant_extrudables(n_extrudables, b_mod_name)
        ac_extrudables = JoinNetworks.relevant_extrudables(c_extrudables, b_mod_name)

        if len(an_extrudables) == 0 and len(ac_extrudables) == 0: 
            return no_way

        n_extrudables, c_extrudables = LivebuildState().get_all_extrudables(mod_b)
        bn_extrudables = JoinNetworks.relevant_extrudables(n_extrudables, a_mod_name)
        bc_extrudables = JoinNetworks.relevant_extrudables(c_extrudables, a_mod_name)

        an_chains = {ane[0].split('.')[2] for ane in an_extrudables}
        ac_chains = {ace[0].split('.')[0] for ace in ac_extrudables}
        bn_chains = {bne[0].split('.')[2] for bne in bn_extrudables}
        bc_chains = {bce[0].split('.')[0] for bce in bc_extrudables}

        ways = []
        join_sign = ' <--> '

        # selector format:
        # moving_mod_chain.fixed_mod_chain.which_term_of_fixed_mod
        for an_ch in an_chains:
            for bc_ch in bc_chains:
                left = '.{}:{}({})'.format(mod_a.name, an_ch, 'N')
                right = '({}){}:{}.'.format('C', bc_ch, mod_b.name)
                an_bc = left + join_sign + right
                selector = '.'.join([an_ch, bc_ch, 'c'])
                ways.append((selector, an_bc, ''))

        for ac_ch in ac_chains:
            for bn_ch in bn_chains:
                left = '.{}:{}({})'.format(mod_a.name, ac_ch, 'C')
                right = '({}){}:{}.'.format('N', bn_ch, mod_b.name)
                ac_bn = left + join_sign + right
                selector = '.'.join([ac_ch, bn_ch, 'n'])
                ways.append((selector, ac_bn, ''))

        return ways if len(ways) > 0 else no_way

    way_selector = bpy.props.EnumProperty(items=get_ways)

    def execute(self, context):
        if not self.way_selector in nop_enum_selectors:
            # Execute pull-join (a to b)
            mod_a, mod_b = get_selected(-1)
            if context.active_object == mod_a:
                mod_a, mod_b = mod_b, mod_a

            moving_mod_chain, fixed_mod_chain, which_term = \
                self.way_selector.split('.')

            old_network = mod_a.parent
            a_network_mods = []
            for mod in walk_network(mod_a):
                a_network_mods.append(mod)

            a_mw = mod_a.matrix_world.copy()
            a_rot, a_tran = scaleless_rot_tran(mod_a)
            a_rot.transpose()
            a_tran.translation *= -1
            a_tx = a_rot * a_tran 

            rel_type = (mod_b.elfin.module_type, mod_a.elfin.module_type)
            tx = get_tx(
                fixed_mod=mod_b, 
                extrude_from=fixed_mod_chain,
                extrude_into=moving_mod_chain,
                ext_mod=mod_a, 
                which_term=which_term, 
                mod_types=rel_type
                )

            old_network.matrix_world = tx * a_tx * old_network.matrix_world
            context.scene.update() # mandatory update to reflect the loc/roc settings
            transfer_network(mod_a, mod_b.parent)

            mod_b_link_func = mod_b.elfin.new_n_link \
                if which_term == 'n' else mod_b.elfin.new_c_link
            mod_a_link_func = mod_a.elfin.new_c_link \
                if which_term == 'n' else mod_a.elfin.new_n_link
            mod_b_link_func(fixed_mod_chain, mod_a, moving_mod_chain)
            mod_a_link_func(moving_mod_chain, mod_b, fixed_mod_chain)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return selection_check(n_modules=2)

class SeverNetwork(bpy.types.Operator):
    bl_idname = 'elfin.sever_network'
    bl_label = 'Sever one network into two at the specific point (#svnw)'
    bl_options = {'REGISTER', 'UNDO'}

    link_info = None
    ordered_selection = (None, None)

    def sever(self, link, linkage, mod_a):
        mod_b = link.target_mod

        link.sever()
        linkage.remove(linkage.find(link.source_chain_id))

        # Move both sub-networks under new parents that has the correct COM
        transfer_network(mod_a)
        transfer_network(mod_b)

    def execute(self, context):
        # mod_b is always the fixed module
        mod_a, mod_b = self.ordered_selection
        if not mod_a:
            self.report(
                {'ERROR'}, 
                'Error: selection lost')
            return {'CANCELLED'}

        if not self.link_info:
            self.report(
                {'ERROR'}, 
                'Error: link_info is '.format(self.link_info))
            return {'CANCELLED'}
        
        link, linkage = self.link_info

        should_warn_mirrors = False

        symhub = find_symmetric_hub([mod_a.parent])
        if symhub and symhub == mod_a or symhub == mod_b:
            arm_mod = mod_a if symhub == mod_b else mod_b
            for m in arm_mod.elfin.mirrors:
                # Not making assumption that a symmetric hub's immediate
                # neighbors are identical, although they should be probably
                # are..
                m_link, m_linkage = symhub.elfin.find_link(m)
                self.sever(m_link, m_linkage, symhub)
        else:
            term = link.terminus
            src_chain_id = link.source_chain_id

            to_sever = []
            if mod_a.elfin.mirrors:
                for m in mod_a.elfin.mirrors:
                    if term == 'c':
                        m_linkage = m.elfin.c_linkage
                    else:
                        m_linkage = m.elfin.n_linkage
                    for l in m_linkage:
                        if l.source_chain_id == src_chain_id:
                            to_sever.append((l, m_linkage, m))
            else:
                for l in linkage:
                    if l.source_chain_id == src_chain_id:
                        to_sever.append((l, linkage, mod_a))

            if mod_b.elfin.mirrors:
                # Warn user.
                should_warn_mirrors = True

            for ts in to_sever:
                self.sever(*ts)

        self.ordered_selection = (None, None)
        self.link_info = None

        if should_warn_mirrors:
            # Could use WARNING, but it doesn't pop (shows at the top-right corner).
            self.report(
                {'ERROR'},
                ('Warning (not an error): second module ({}) has mirrors.\n\n'
                    'This operator only considers mirrors in the first selected module.')
                .format(mod_b.name))
            return {'FINISHED'}
        else:
            MessagePrompt.message_lines=['Operation successful']
            bpy.ops.elfin.message_prompt('INVOKE_DEFAULT',
                title='Sever network',
                icon='INFO')

            return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        # Objects don't really need to be ordered but it's convenient.
        objs = get_ordered_selection()

        # Check whether the two selected moduels are next to each other in network.
        if objs[0] is not None:
            SeverNetwork.ordered_selection = objs
            SeverNetwork.link_info = objs[0].elfin.find_link(objs[1])
            if SeverNetwork.link_info:
                return True

        return False

class SelectNetworkParent(bpy.types.Operator):
    bl_idname = 'elfin.select_network_parent'
    bl_label = 'Select network parent (#snp)'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for s in get_selected(-1):
            s.select = False
            s.parent.select = True
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        """This is intended to work for both module and pguide networks"""
        return get_selection_len() > 0

class SelectNetworkObjects(bpy.types.Operator):
    bl_idname = 'elfin.select_network_objects'
    bl_label = 'Select all objects in network (#sno)'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for s in get_selected(-1):
            walker = walk_pg_network \
                    if s.elfin.is_joint() or s.elfin.is_bridge() else \
                    walk_network

            for mod in walker(s):
                mod.select = True
                
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        """This is intended to work for both module and pguide networks"""
        return get_selection_len() > 0

# Mirror linking operators -----------------------
class SelectMirrors(bpy.types.Operator):
    bl_idname = 'elfin.select_mirrors'
    bl_label = 'Select mirrors (all mirror-linked modules) (#smr)'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if get_selection_len() > 0:
            for sm in get_selected(n=-1):
                for m in sm.elfin.mirrors:
                    m.select = True
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return get_selection_len() > 0

class ListMirrors(bpy.types.Operator):
    bl_idname = 'elfin.list_mirrors'
    bl_label = 'List mirror links of one selected module (#lmr)'
    bl_options = {'REGISTER'}

    def execute(self, context):
        mirrors = get_selected().elfin.mirrors
        mirror_strs = []
        for i in range(len(mirrors)):
            mirror_strs.append('[{}] {}'.format(i, mirrors[i].name))
        if len(mirror_strs) == 0:
            mirror_strs.append('No mirrors!')
        MessagePrompt.message_lines=mirror_strs
        bpy.ops.elfin.message_prompt('INVOKE_DEFAULT',
            title='List Mirror Result',
            icon='INFO')
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return get_selection_len() == 1 and  \
            get_selected().elfin.is_module()

class UnlinkMirrors(bpy.types.Operator):
    bl_idname = 'elfin.unlink_mirrors'
    bl_label = 'Unlink mirrors from all selected modules (#ulm)'
    bl_options = {'REGISTER', 'UNDO'}

    def unlink_mirrors(self, mirrors, recursive):
        if recursive:
            for o in get_selected(-1):
                for m in o.elfin.mirrors:
                    if m != o: m.elfin.mirrors = []
                o.elfin.mirrors = []
        else:
            for o in get_selected(-1):
                o.elfin.mirrors = []

        MessagePrompt.message_lines=['Operation successful']
        bpy.ops.elfin.message_prompt('INVOKE_DEFAULT',
            title='Unlink Mirrors',
            icon='INFO')

    def execute(self, context):
        self.unlink_mirrors(get_selected(-1), True)

        # Can't think of a reason to not recursively unlink..
        # mirrors = get_selected(-1) 
        # YesNoPrmopt.callback_true = \
        #     YesNoPrmopt.Callback(self.unlink_mirrors, [mirrors, True])
        # YesNoPrmopt.callback_false = \
        #     YesNoPrmopt.Callback(self.unlink_mirrors, [mirrors, False])
        # bpy.ops.elfin.yes_no_prompt('INVOKE_DEFAULT',
        #     option=True,
        #     title='Unlink recursively?',
        #     message='Yes')

        return {'FINISHED'}

    @classmethod
    def poll(self, context):
        if get_selection_len() > 0:
            for s in get_selected(-1):
                if len(s.elfin.mirrors) > 0:
                    return True
        return False

class LinkByMirror(bpy.types.Operator):
    bl_idname = 'elfin.link_by_mirror'
    bl_label = 'Link multiple modules of the same prototype by mirror (#lbm)'
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def can_link(cls):
        """Only show operator if selected objects are of the same prototype
        """
        if get_selection_len() > 1:
            selection = get_selected(-1)
            if selection:
                mod_name = selection[0].elfin.module_name
                for o in selection:
                    if not o.elfin.is_module() or o.elfin.module_name != mod_name:
                        return False
                return True
        return False

    def unlink_then_link(self, mirrors):
        self.unlink_mirrors(mirrors)
        self.link_by_mirror(mirrors)

    def unlink_mirrors(self, mirrors):
        for m in mirrors:
            for _m in m.elfin.mirrors:
                _m.elfin.mirrors = []

    def link_by_mirror(self, mirrors):
        for m in mirrors:
            m.elfin.mirrors = mirrors
        MessagePrompt.message_lines=['Operation successful']
        bpy.ops.elfin.message_prompt('INVOKE_DEFAULT',
            title='Link by Mirror',
            icon='INFO')

    def execute(self, context):
        if not LinkByMirror.can_link():
            self.report(
                {'ERROR'}, 
                ('Selection is not homogenous i.e. some selected modules '
                    ' have a different prototype'))
            return {'CANCELLED'}

        mirrors = get_selected(-1)

        # Check for existing mirrors and warn user about it
        existing = False
        for m in mirrors:
            if m.elfin.mirrors:
                existing = True
                break

        if existing:
            YesNoPrmopt.callback_true = \
                YesNoPrmopt.Callback(self.unlink_then_link, [mirrors])
            bpy.ops.elfin.yes_no_prompt('INVOKE_DEFAULT',
                option=False,
                title='{} already has mirrors. Unlink mirror group and replace?'.format(m.name),
                message='Yes, replace.')
        else:
            self.link_by_mirror(mirrors)

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return cls.can_link()

# Module manipulation operators ------------------
class ModuleToJoint(bpy.types.Operator):
    bl_idname = 'elfin.module_to_joint'
    bl_label = 'Move a module and its network to a joint (#mtj)'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        joint, module = get_selected(-1)
        if joint.elfin.is_module():
            joint, module = module, joint

        trans = joint.matrix_world.translation - module.matrix_world.translation
        trans_m = mathutils.Matrix.Translation(trans)

        p_mw = module.parent.matrix_world
        module.parent.matrix_world = trans_m * p_mw
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return selection_check(n_modules=1, n_joints=1)

class ExtrudeModule(bpy.types.Operator):
    bl_idname = 'elfin.extrude_module'
    bl_label = 'Extrude module (#exm)'
    bl_property = "terminus_selector"
    bl_options = {'REGISTER'}

    def get_available_termini(self, context):
        available_termini = []

        # suitable_for_extrusion() gurantees homogeneity so we get just take
        # the first object in selection
        sel_mod = get_selected()
        n_extrudables, c_extrudables = LivebuildState().get_all_extrudables(sel_mod)
        if len(n_extrudables) > 0:
            available_termini.append(('N', 'N', ''))
        if len(c_extrudables) > 0:
            available_termini.append(('C', 'C', ''))

        return available_termini if len(available_termini) > 0 else [empty_list_placeholder_enum_tuple]

    terminus_selector = bpy.props.EnumProperty(items=get_available_termini)

    def execute(self, context):
        if self.terminus_selector in nop_enum_selectors:
            return {'FINISHED'}
        if self.terminus_selector.lower() == 'n':
            return bpy.ops.elfin.extrude_nterm('INVOKE_DEFAULT')
        elif self.terminus_selector.lower() == 'c':
            return bpy.ops.elfin.extrude_cterm('INVOKE_DEFAULT')
        else:
            raise ValueError('Unknown terminus selector:', self.terminus_selector)
            return {'CANCELLED'}

    def invoke(self, context, event):
        self.color = ColorWheel().next_color()
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return suitable_for_extrusion(context)

class ExtrudeNTerm(bpy.types.Operator):
    bl_idname = 'elfin.extrude_nterm'
    bl_label = 'Extrude N (add a module to the nterm)'
    bl_property = "nterm_ext_module_selector"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    nterm_ext_module_selector = bpy.props.EnumProperty(
        items=lambda self, context: LivebuildState().n_extrudables)
    color = bpy.props.FloatVectorProperty(name="Display Color", 
                                        subtype='COLOR', 
                                        default=[0,0,0])

    def execute(self, context):
        return execute_extrusion(
            which_term='n',
            selector=self.nterm_ext_module_selector, 
            color=self.color,
            reporter=self)

    def invoke(self, context, event):
        self.color = ColorWheel().next_color()
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

class ExtrudeCTerm(bpy.types.Operator):
    bl_idname = 'elfin.extrude_cterm'
    bl_label = 'Extrude C (add a module to the cterm)'
    bl_property = "cterm_ext_module_selector"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    cterm_ext_module_selector = bpy.props.EnumProperty(
        items=lambda self, context: LivebuildState().c_extrudables)
    color = bpy.props.FloatVectorProperty(name="Display Color", 
                                        subtype='COLOR', 
                                        default=[0,0,0])

    def execute(self, context):
        return execute_extrusion(
            which_term='c',
            selector=self.cterm_ext_module_selector, 
            color=self.color,
            reporter=self)

    def invoke(self, context, event):
        self.color = ColorWheel().next_color()
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

class CheckCollisionAndDelete(bpy.types.Operator):
    bl_idname = 'elfin.check_collision_and_delete'
    bl_label = 'Check collision and delete if positive (#ccd)'

    # Allow keyword specification
    object_name = bpy.props.StringProperty(default='__unset__')

    def execute(self, context):
        found_overlap = False
        check_against = [o for o in context.scene.objects if o.elfin.is_module()]

        try:
            object_is_valid = True
            ob = bpy.data.objects[self.object_name]
            if ob.elfin.is_module():
                found_overlap |= delete_if_overlap(ob, check_against)
        except KeyError:
            object_is_valid = False

        if not object_is_valid:
            # No valid object_name specified - try using selection
            objs = get_selected(-1)

            # Nothing selected - use all objects
            if len(objs) == 0:
                objs = context.scene.objects

            for ob in objs:
                if ob.elfin.is_module():
                    found_overlap |= delete_if_overlap(ob, check_against)

        if found_overlap:
            MessagePrompt.message_lines=['Collision was detected and modules were deleted.']
            bpy.ops.elfin.message_prompt('INVOKE_DEFAULT')
            
        return {'FINISHED'}

    def invoke(self, context, event):
        self.object_name = ''
        return self.execute(context)

class AddModule(bpy.types.Operator):
    bl_idname = 'elfin.add_module'
    bl_label = 'Add (place) a module (#addm)'
    bl_property = 'module_to_place'
    bl_options = {'REGISTER', 'UNDO'}

    ask_prototype = bpy.props.BoolProperty(default=True, options={'HIDDEN'})
    module_to_place = bpy.props.EnumProperty(items=LivebuildState().placeables)
    color = bpy.props.FloatVectorProperty(name="Display Color", 
                                        subtype='COLOR', 
                                        default=[0,0,0])

    def execute(self, context):
        if self.module_to_place in nop_enum_selectors:
            return {'FINISHED'}

        print('Placing module {}'.format(self.module_to_place))
        
        sel_mod_name = self.module_to_place.split('.')[1]

        add_module(sel_mod_name, color=self.color)

        self.ask_prototype = True
            
        # Gurantees newly added module is both selected and active.
        return {'FINISHED'}

    def invoke(self, context, event):
        self.color = ColorWheel().next_color()

        if self.ask_prototype:
            context.window_manager.invoke_search_popup(self)
        else:
            return self.execute(context)

        return {'FINISHED'}

# Utility operators ------------------------------
class DestroyObject(bpy.types.Operator):
    bl_idname = 'elfin.destroy_object'
    bl_label = 'Destroys an elfin object gracefully'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    
    name = bpy.props.StringProperty()

    def execute(self, context):
        bpy.data.objects[self.name].elfin.destroy()
        return {'FINISHED'}

class LoadXdb(bpy.types.Operator):
    bl_idname = 'elfin.load_xdb'
    bl_label = '(Re)load xdb'

    def execute(self, context):
        LivebuildState().load_xdb()
        return {'FINISHED'}

class LoadModuleLibrary(bpy.types.Operator):
    bl_idname = 'elfin.load_module_library'
    bl_label = '(Re)load module library'

    def execute(self, context):
        LivebuildState().load_library()
        return {'FINISHED'}

class MessagePrompt(bpy.types.Operator):
    """Elfin Module Collision Message"""
    bl_idname = 'elfin.message_prompt'
    bl_label = 'Prompts a message with an OK button'
    bl_options = {'REGISTER', 'INTERNAL'}

    title = bpy.props.StringProperty(default='Elfin Message')
    icon = bpy.props.StringProperty(default='ERROR')
    message_lines = []

    def execute(self, context):
        # Manually reset values
        self.message_lines = []
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self)
 
    def draw(self, context):
        self.layout.label(self.title, icon=self.icon)
        row = self.layout.column()
        for l in self.message_lines:
            row.label(l)

# Credits to:
# https://blender.stackexchange.com/questions/73286/how-to-call-a-confirmation-dialog-box
class YesNoPrmopt(bpy.types.Operator):
    bl_idname = 'elfin.yes_no_prompt'
    bl_label = 'Confirm option'
    bl_options = {'REGISTER', 'INTERNAL'}
    
    title = bpy.props.StringProperty(default='Confirm?')
    icon = bpy.props.StringProperty(default='QUESTION')

    message = bpy.props.StringProperty(default='No')
    option = bpy.props.BoolProperty(default=True)

    class Callback:
        def __init__(self, func=None, args=[], kwargs=[]):
            self.func = func
            self.args = args
            self.kwargs = kwargs

    callback_true = Callback()
    callback_false = Callback()

    def execute(self, context):
        if self.option and self.callback_true.func:
            self.callback_true.func(
                *self.callback_true.args, 
                *self.callback_true.kwargs)
        elif self.callback_false.func:
            self.callback_false.func(
                *self.callback_false.args, 
                *self.callback_false.kwargs)

        # Manually reset values
        self.callback_true = self.Callback()
        self.callback_false = self.Callback()
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout
        row.label(self.title, icon=self.icon)
        row.prop(self, 'option', text=self.message)

class INFO_MT_mesh_elfin_add(bpy.types.Menu):
    bl_idname = 'INFO_MT_elfin_add'
    bl_label = 'elfin'
    def draw(self, context):
        layout = self.layout

        for mod_tuple in LivebuildState().placeables:
            if mod_tuple in nop_enum_selectors:
                continue
            mod_name = mod_tuple[0]
            props = layout.operator('elfin.add_module', text=mod_name)
            props.module_to_place = mod_name
            props.ask_prototype = False

# Panels -----------------------------------------
class LivebuildPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Livebuild'
    bl_context = 'objectmode'
    bl_category = 'Elfin'

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        col = row.column()
        col.prop(context.scene.elfin, 'disable_auto_collision_check', text='Disable Auto Collision Check')
        col.operator('elfin.add_module', text='Place a module into scene')
        col.operator('elfin.extrude_module', text='Extrude Module')
        col.operator('elfin.select_mirrors', text='Select Mirrors')
        col.operator('elfin.select_network', text='Select Network')
        col.operator('elfin.list_mirrors', text='List Mirrors')
        col.operator('elfin.unlink_mirrors', text='Unlink Mirrors')
        col.operator('elfin.link_by_mirror', text='Link by Mirror')
        col.operator('elfin.add_joint', text='Add Joint')
        col.operator('elfin.extrude_joint', text='Extrude Joint')
        col.operator('elfin.add_bridge', text='Bridge two Joints')
        col.operator('elfin.joint_to_module', text='Move Joint to Module')
        # col.operator('elfin.join_networks', text='Join Networks')