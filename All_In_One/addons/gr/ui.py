# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any laTter version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


##########################################################################################################
##########################################################################################################

import bpy, os, addon_utils
from mathutils import Vector
from math import sqrt
from bpy.types import Panel, Operator
from bpy.props import StringProperty, IntProperty, FloatProperty, EnumProperty, BoolProperty
from functools import reduce
import bpy.utils.previews
from .utils import calculate_pole_target_location_pbone
from .utils import lerp
from .utils import report
from .utils import popup
from .utils import get_active_action


class PG_GYAZ_GameRig(bpy.types.PropertyGroup):
    switch_when_snap: BoolProperty(name='Switch when snap',
                                   default=True
                                   )
    show_switch_visible: BoolProperty(name='Swow switch/visible',
                                      default=True
                                      )
    show_low_level_props: BoolProperty(name='Swow low-level visible',
                                       default=True
                                       )
  
# SNAP
#mode: 'FK_to_IK', 'IK_to_FK'
#key = False, True    
#switch: False, True
#module_detection: 'AUTO', 'MANUAL'
#module_name: string - only used if module_detection is 'MANUAL'
def snap (mode, key, switch, module_detection, module_name, force_visibility):
            
    def main (module):         
    
        scene = bpy.context.scene  
        rig = bpy.context.object
        pbones = rig.pose.bones
        # name of module bone (bone that contains all props of the module)
        prop_bone = pbones['module_props__' + module]
        ctx = bpy.context.copy ()
        key_attributes = 'Rotation' if mode == 'FK_to_IK' else 'BUILTIN_KSI_LocRot'
        
        # MAKE SURE BONES ARE VISIBLE
        if force_visibility:
            if mode == 'IK_to_FK':                    
                prop_name = 'visible_ik_'+module
                if prop_name in prop_bone:
                    if prop_bone[prop_name] != 1:
                        prop_bone[prop_name] = 1
                    
            elif mode =='FK_to_IK':
                prop_name = 'visible_fk_'+module
                if prop_name in prop_bone:
                    if prop_bone[prop_name] != 1:
                        prop_bone[prop_name] = 1
        
        def key_bones (bone_names):
            if key == True:
                ctx['selected_pose_bones'] = [pbones[name] for name in bone_names if name != 'None']
                bpy.ops.anim.keyframe_insert_menu (ctx, type=key_attributes)
                
        def switch_controls (switch_mode):
            prop_name = 'switch_'+module
            if prop_name in prop_bone:
                if switch_mode == 'to_FK':
                    if prop_bone[prop_name] != 0:
                        prop_bone[prop_name] = 0
                         
                elif switch_mode == 'to_IK':
                    if prop_bone[prop_name] != 1:
                        prop_bone[prop_name] = 1
        
        bone_custom_props = prop_bone.keys ()
        
        # order matters, bones higher in hierarchy should come sooner in this list
        snap_infos = [prop for prop in bone_custom_props if prop.startswith ('snapinfo')]
                       
        for prop in snap_infos:
            if prop.startswith ('snapinfo_3bonelimb'):

                # prop on prop_bone that has snap info
                snap_info = prop_bone[prop]
                fk_b1, fk_b2, fk_b3, ik_b1, ik_b2, ik_b3 = snap_info[:6]
                
                pole_target = snap_info[6]
                pole_target_distance = float( snap_info[7] )
                snap_pole_target = snap_info[8]
                ik_snap_target_b3 = snap_info[9]
                ik_main_b3 = snap_info[10]
                ik_roll = snap_info[11]

                if mode == 'IK_to_FK':           

                    rig = bpy.context.object  
                        
                    # SNAP:

                    # ik_target
                    pbone = pbones[ik_main_b3]
                    
                    pbone.matrix = pbones[ik_snap_target_b3].matrix
                    scene.update ()

                    # pole_target
                    calc_pole_pos = calculate_pole_target_location_pbone (fk_b1, fk_b2, fk_b3, pole_target_distance)
                    snap_target = pbones[snap_pole_target]
                    pole_target_pos = snap_target.matrix.translation
                    a = pbones[fk_b1].matrix.translation
                    b = pbones[fk_b2].matrix.translation
                    c = pbones[fk_b3].matrix.translation
                    v1 = b - a 
                    v2 = c - b
                    v1.normalize ()
                    v2.normalize ()
                    alpha = v1.dot(v2)
                    alpha = max (min(alpha, 1), 0)
                    pole_pos = lerp (calc_pole_pos, pole_target_pos, alpha)
                    
                    pbone = pbones[pole_target]
                    scene.update ()
                    pbone.matrix.translation = pole_pos                    
                    scene.update ()
                    
                    if ik_roll != 'None':
                        pbones[ik_roll].rotation_quaternion = (1, 0, 0, 0)
                        scene.update ()
                    
                    # INSERT KEYS
                    key_bones ([ik_b3, pole_target, ik_main_b3, ik_roll])                           

                    
                elif mode == 'FK_to_IK': 
                    pbones[fk_b1].matrix = pbones[ik_b1].matrix
                    scene.update () 
                    pbones[fk_b2].matrix = pbones[ik_b2].matrix
                    scene.update () 
                    pbones[fk_b3].matrix = pbones[ik_b3].matrix
                    scene.update ()
                    key_bones ([fk_b1, fk_b2, fk_b3])
        
                
            elif prop.startswith ('snapinfo_singlebone'):
                
                # prop on prop_bone that has snap info
                snap_info = prop_bone[prop]
                
                fk_b = snap_info[0]
                ik_b = snap_info[1]
                
                if mode == 'IK_to_FK':
                    pbones[ik_b].matrix = pbones[fk_b].matrix
                    scene.update ()
                    key_bones ([ik_b])
                     
                elif mode == 'FK_to_IK':        
                    pbones[fk_b].matrix = pbones[ik_b].matrix
                    scene.update ()
                    key_bones ([fk_b])
                    
            elif prop.startswith ('snapinfo_simpletobase'):
                
                snap_info = prop_bone[prop]
                
                if mode == 'FK_to_IK':
                    pbones = rig.pose.bones
                    for name in snap_info:
                        pbones['fk_'+name].matrix = pbones[name].matrix
                        scene.update ()
                    key_bones (['fk_'+name for name in snap_info])
        
        # SWITCH MODE      
        if switch == True:
            if len (snap_infos) > 0:
                if mode == 'FK_to_IK':
                    switch_controls (switch_mode='to_FK')
                elif mode == 'IK_to_FK':
                    switch_controls (switch_mode='to_IK')
                
    
    if module_detection == 'AUTO':
        # get module name of active bone
        active_bone = bpy.context.active_pose_bone
        if 'module' not in active_bone:
            popup (item="Bone is not part of any module.", icon='ERROR')
        else:
            module = active_bone['module']
            main (module)
            
    elif module_detection == 'MANUAL':
        main (module=module_name)

    
# snap fk to ik
class Op_GYAZGameRig_SnapFKtoIK (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_game_rigger_snap_fk_to_ik"  
    bl_label = "GYAZ Game Rigger: Snap FK to IK"
    bl_description = "Snap FK to IK"
    
    # operator function
    def execute(self, context):

        rig = bpy.context.active_object
        owner = bpy.context.scene.gyaz_rig
        sel_bones = bpy.context.selected_pose_bones
        if len (sel_bones) == 0:
            report (self, 'No selected bones.', 'WARNING')
        else:
            
            switch = owner.switch_when_snap
            snap (mode='FK_to_IK', key=False, switch=switch, module_detection='AUTO', module_name='', force_visibility=True)
                
        # end of operator
        return {'FINISHED'}
    
    # when the buttons should show up    
    @classmethod
    def poll(cls, context):       
        return context.mode == 'POSE'

    
# snap ik to fk
class Op_GYAZGameRig_SnapIKtoFK (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_game_rigger_snap_ik_to_fk"  
    bl_label = "GYAZ Game Rigger: Snap IK to FK"
    bl_description = "Snap IK to FK"
    
    # operator function
    def execute(self, context):
        
        rig = bpy.context.active_object
        owner = bpy.context.scene.gyaz_rig
        sel_bones = bpy.context.selected_pose_bones
        if len (sel_bones) == 0:
            report (self, 'No selected bones.', 'WARNING')
        else:        
        
            switch = owner.switch_when_snap
            snap (mode='IK_to_FK', key=False, switch=switch, module_detection='AUTO', module_name='', force_visibility=True)            
            
        # end of operator
        return {'FINISHED'}
    
    # when the buttons should show up    
    @classmethod
    def poll(cls, context):       
        return context.mode == 'POSE'

    
class Op_GYAZGameRig_SnapAndKey (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_game_rigger_snap_and_key"  
    bl_label = "GYAZ Game Rigger: Snap and Key"
    bl_description = ""
    
    def draw (self, context):
        lay = self.layout
        lay.label (text='Sure?')
    
    def invoke (self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog (self)
    
    # operator function
    def execute (self, context):
        scene = bpy.context.scene
        rig = bpy.context.active_object
        
        start = rig["snap_start"]
        end = rig["snap_end"]
        
        for module in rig.data["snappable_modules"]:
            prop_bone = rig.pose.bones["module_props__"+module]
            fk_ik = prop_bone["snap_n_key__fk_ik"] if "snap_n_key__fk_ik" in prop_bone else 0
            should_snap = prop_bone["snap_n_key__should_snap"]
            if should_snap:                
                
                switch_ = False
                force_visibility_ = False                
                
                for n in range (start, end+1):
                    
                    if n == end:
                        switch_ = True
                        force_visibility_ = True                       
                    
                    scene.frame_set (n)                    
                    if fk_ik == 1:
                        snap (mode='IK_to_FK', key=True, switch=switch_, module_detection='MANUAL', module_name=module, force_visibility=force_visibility_)
                    elif fk_ik == 0:
                        snap (mode='FK_to_IK', key=True, switch=switch_, module_detection='MANUAL', module_name=module, force_visibility=force_visibility_)
                                        
            
        # end of operator
        return {'FINISHED'}

    # when the buttons should show up    
    @classmethod
    def poll(cls, context):     
        return context.mode == 'POSE'    


# GLOBAL SWITCH
class Op_GYAZGameRig_Switch (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_game_rigger_switch"  
    bl_label = "GYAZ Game Rigger: Switch"
    bl_description = "Bind all base bones of the low-level rig to fk, ctrl/ik or nothing"

    mode: EnumProperty(
        name = 'mode',
        items = (
            ('FK', 'FK', ''),
            ('IK/CTRL', 'IK/CTRL', ''),
            ('BASE', 'BASE', '')
            ),
        default = "FK",
        description = "")
        
    is_local: BoolProperty (default=False)
    
    # operator function
    def execute(self, context):
    
        mode = self.mode
        is_local = self.is_local
        
        rig = bpy.context.active_object
        scene = bpy.context.scene
        pbones = rig.pose.bones
        
        def set_module_props (pbone, module_name):
            
            prop_name = 'switch_' + module_name
            prop_list = pbone.keys()        
            prop = pbone[prop_name] if prop_name in prop_list else None
            if prop != None:
                
                def set_vis (name):
                    vis_name = 'visible_' + name + '_' + module_name
                    vis = pbone[vis_name] if vis_name in prop_list else None
                    if vis != None:
                        pbone[vis_name] = 1
            
                if mode == 'FK':
                    pbone[prop_name] = 0
                    set_vis ('fk')
                    
                elif mode == 'IK/CTRL':
                    pbone[prop_name] = 1
                    set_vis ('ik')                  
                    set_vis ('ctrl')                  
                
                elif mode == 'BASE':
                    if not is_local:    
                    
                        pbone[prop_name] = 2
                        
                        general_module_bone = pbones.get ('module_props__general')
                        if general_module_bone != None:
                            vis_name = 'visible_base_bones'
                            vis = general_module_bone[vis_name] if vis_name in general_module_bone.keys () else None
                            if vis != None:
                                 general_module_bone[vis_name] = 1
                                 rig.show_in_front = True      
        
                            
        if is_local:
            pbone = bpy.context.active_pose_bone
            sel_bones = bpy.context.selected_pose_bones
            if len (sel_bones) == 0:
                report (self, 'No selected bones.', 'WARNING')
            else:
                
                if pbone != None:
                    if 'module' in pbone.keys ():
                        module_name = pbone['module']
                        module_pbone_name = 'module_props__' + module_name
                        module_pbone = pbones.get (module_pbone_name)
                        if module_pbone != None:
                            pbone = module_pbone
                            set_module_props (pbone, module_name)
                    else:
                        popup (item="Bone is not part of any module.", icon='ERROR')
                        
        else:
            for pbone in pbones:
                if pbone.name.startswith ('module_props__'):
                    module_name = pbone.name[14:]
                    set_module_props (pbone, module_name)                        
        
        # force scene update                    
        bpy.ops.object.mode_set (mode='OBJECT')
        bpy.ops.object.mode_set (mode='POSE')
            
        # end of operator
        return {'FINISHED'}

    
#  Visibility
class Op_GYAZGameRig_SetVisible (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_game_rigger_set_visible"  
    bl_label = "GYAZ Game Rigger: Set Visible"
    bl_description = "Show/Hide FK, IK/CTRL, Touch"

    mode: EnumProperty(
        name = 'mode',
        items = (
            ('SHOW_FK', 'SHOW_FK', ''),
            ('HIDE_FK', 'HIDE_FK', ''),
            ('SHOW_IK/CTRL', 'SHOW_IK/CTRL', ''),
            ('HIDE_IK/CTRL', 'HIDE_IK/CTRL', ''),
            ),
        default = "SHOW_FK",
        description = "")
        
    is_local: BoolProperty (default=False)
    
    # operator function
    def execute(self, context):
    
        mode = self.mode
        is_local = self.is_local
        
        rig = bpy.context.active_object
        scene = bpy.context.scene
        
        pbones = rig.pose.bones
        
        def set_module_props (pbone, module_name):
            
            prop_list = pbone.keys()
            
            def set_vis (name):
                
                prop_name = 'visible_' + name + '_' + module_name
                prop = pbone[prop_name] if prop_name in prop_list else None
                if prop != None:
                
                    if is_local:
                        if pbone[prop_name] == 0:
                            pbone[prop_name] = 1
                        else:
                            pbone[prop_name] = 0
                        
                    else:    
                        if mode.startswith ('SHOW'):
                            pbone[prop_name] = 1
                        elif mode.startswith ('HIDE'):
                            pbone[prop_name] = 0
                        
                    
            if mode.endswith ('FK'):
                
                set_vis ('fk')
                            
            elif mode.endswith ('IK/CTRL'):
                
                set_vis ('ik')
                set_vis ('ctrl')

        
        if is_local:
            pbone = bpy.context.active_pose_bone
            sel_bones = bpy.context.selected_pose_bones
            if bpy.context.active_pose_bone not in sel_bones:
                sel_bones.append (bpy.context.active_pose_bone)
            
            if len (sel_bones) == 0:
                report (self, 'No selected bones.', 'WARNING')
            else:
                
                if 'module' in pbone.keys ():
                    module_name = pbone['module']
                    module_pbone_name = 'module_props__' + module_name
                    module_pbone = pbones.get (module_pbone_name)
                    if module_pbone != None:
                        pbone = module_pbone
                        set_module_props (pbone, module_name)
                else:
                    popup (item="Bone is not part of any module.", icon='ERROR')
                        
        else:
            for pbone in pbones:
                if pbone.name.startswith ('module_props__'):
                    module_name = pbone.name[14:]
                    set_module_props (pbone, module_name)
                
        
        # force scene update
        bpy.ops.object.mode_set (mode='OBJECT')
        bpy.ops.object.mode_set (mode='POSE')
            
        # end of operator
        return {'FINISHED'}
    

class Op_GYAZGameRig_SetSnapPropToCurrentFrame (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_game_rigger_set_snap_prop_to_current_frame"  
    bl_label = "GYAZ Game Rigger: Set Snap Prop To Current Frame"
    bl_description = ""

    prop_name: StringProperty(
        name = 'prop_name',
        default = "snap_start",
        description = "")
    
    # operator function
    def execute(self, context):
        prop_name = self.prop_name
        rig = bpy.context.active_object
        rig[prop_name] = bpy.context.scene.frame_current     
            
        # end of operator
        return {'FINISHED'}
    
class Op_GYAZGameRig_SetSnapPropFKIK (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_game_rigger_set_snap_prop_fk_ik"  
    bl_label = "GYAZ Game Rigger: Set Snap Prop FK IK"
    bl_description = ""

    module: StringProperty(
        name = 'module',
        default = '',
        description = "")
    
    # operator function
    def execute(self, context):
        module = self.module
        rig = bpy.context.active_object
        if rig.pose.bones['module_props__'+module]["snap_n_key__fk_ik"] == 0:
            rig.pose.bones['module_props__'+module]["snap_n_key__fk_ik"] = 1
        elif rig.pose.bones['module_props__'+module]["snap_n_key__fk_ik"] == 1:
            rig.pose.bones['module_props__'+module]["snap_n_key__fk_ik"] = 0
            
        # end of operator
        return {'FINISHED'}

    
class Op_GYAZGameRig_SetSnapPropActive (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_game_rigger_set_snap_prop_active"  
    bl_label = "GYAZ Game Rigger: Set Snap Prop Active"
    bl_description = ""

    module: StringProperty(
        name = 'module',
        default = '',
        description = "")
    
    # operator function
    def execute(self, context):
        module = self.module
        rig = bpy.context.active_object
        if rig.pose.bones['module_props__'+module]["snap_n_key__should_snap"] == 0:
            rig.pose.bones['module_props__'+module]["snap_n_key__should_snap"] = 1
        elif rig.pose.bones['module_props__'+module]["snap_n_key__should_snap"] == 1:
            rig.pose.bones['module_props__'+module]["snap_n_key__should_snap"] = 0
            
        # end of operator
        return {'FINISHED'}
    

class Op_GYAZGameRig_HideSelectCharacterMeshes (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_game_rigger_hide_select_character_meshes"  
    bl_label = "GYAZ Game Rigger: Hide Select Character Meshes"
    bl_description = "Enable/Disable selecion of meshes"
    
    hidden: BoolProperty(
        name = 'hidden',
        default = False)
    
    # operator function
    def execute(self, context):
        hidden = self.hidden
        rig = bpy.context.active_object
        meshes = []
        for child in rig.children:
            if child.type == 'MESH':
                meshes.append (child)
                   
        for mesh in meshes:
            mesh.hide_select = hidden
            
        # end of operator
        return {'FINISHED'}

    
class Op_GYAZGameRig_AppendSourceRig (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_game_rigger_append_source_rig"  
    bl_label = "GYAZ Game Rigger: Append Source Rig"
    bl_description = ""
    
    # operator function
    def execute(self, context):
        
        def append (obj_name, filepath):
            # append, set to true to keep the link to the original file
            link = False
            # link
            with bpy.data.libraries.load(filepath, link=link) as (data_from, data_to):
                data_to.objects = [name for name in data_from.objects if name.endswith(obj_name)]
            # link object to current scene
            scene = bpy.context.scene
            for obj in data_to.objects:
                if obj is not None:
                   scene.collection.objects.link(obj)
            return data_to.objects

        source_path = os.path.dirname(__file__) + "/source_rigs.blend"
        
        objects = append (obj_name = "GYAZ_source_rig__biped", filepath = source_path)
        for obj in objects:
            obj.select_set (True)
        bpy.context.view_layer.objects.active = objects[0]
            
        # end of operator
        return {'FINISHED'}

    
def add_source_rig_button(self, context):
    self.layout.operator(
        Op_GYAZGameRig_AppendSourceRig.bl_idname,
        text="GYAZ Source Rig: Biped",
        icon='ARMATURE_DATA')


def set_prop (prop):
    rig_data = bpy.context.active_object.data
    if rig_data[prop] == 0:
        rig_data[prop] = 1
    elif rig_data[prop] == 1:
        rig_data[prop] = 0

    
class Op_GYAZGameRig_SelectModuleBones (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_game_rigger_select_module_bones"  
    bl_label = "GYAZ Game Rigger: Select Module Bones"
    bl_description = ""
    
    # operator function
    def execute(self, context):
        
        rig = bpy.context.active_object
        bones = rig.data.bones
        pbones = rig.pose.bones
        
        # get selected bones
        selected_pbones = bpy.context.selected_pose_bones
        if len (selected_pbones) == 0:
            report (self, 'No selected bones.', 'WARNING')
        else:
            
            for pbone in selected_pbones:
                if "module" in pbone:
                    module = pbone["module"]
                    
                    # get type of pbone
                    type = ""
                    if "bone_type" in pbone:
                        type = pbone['bone_type']
                    
                    # get bones from the same module
                    for pbone in pbones:
                        if "module" in pbone:
                            if pbone["module"] == module:
                                # filter it against type
                                if type != "":
                                    if 'bone_type' in pbone:
                                        if pbone['bone_type'] == type:
                                            if not pbone.name.startswith ('target_line'):
                                                bones[pbone.name].select = True
                                else:
                                    bones[pbone.name].select = True
                          
        # end of operator
        return {'FINISHED'}
    
    # when the buttons should show up    
    @classmethod
    def poll(cls, context):      
        return bpy.context.mode == 'POSE'


class Op_GYAZGameRig_SavePropsToAction (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_game_rigger_save_props_to_action"  
    bl_label = "GYAZ Game Rigger: Save Props To Action"
    bl_description = "Save all props to active action / Load all props from active action"
    
    mode: EnumProperty (items=(('SAVE', 'Save', ''), ('LOAD', 'Load', '')), default='SAVE', options={'SKIP_SAVE'})
    
    def draw (self, context):
        lay = self.layout
        if self.mode == 'SAVE':
            lay.label (text='Save props to action?')
        else:
            lay.label (text='Load props from action?')
    
    def invoke (self, context, event):
        wm = bpy.context.window_manager
        return  wm.invoke_props_dialog (self)
    
    # operator function
    def execute(self, context):
        
        mode = self.mode
        rig = bpy.context.active_object
        pbones = rig.pose.bones
        save_prop_name = 'gyaz_game_rig_save_props'
        scene = bpy.context.scene
        
        action = get_active_action (rig)
        
        if action is not None:
            
            if mode == 'SAVE':
            
                prop_info = []
                
                for pbone in pbones:
                    for key in pbone.keys():
                        if key != '_RNA_UI' and key != 'bone_type' and key != 'module' and key != 'snap_n_key__should_snap' and not key.startswith ('snapinfo'):
                            info = {'bone': pbone.name, 'key': key, 'value': pbone[key]}
                            prop_info.append (info)
                        
                action[save_prop_name] = prop_info
               
               
            elif mode == 'LOAD':
                
                if save_prop_name in action:
                    prop_info = action[save_prop_name]
                    
                    for item in prop_info:
                        pbone = pbones.get (item['bone'])
                        if pbone != None:
                            key = item['key']
                            if key in pbone:
                                pbone[key] = item['value']
                                
                    bpy.ops.object.mode_set (mode='OBJECT')
                    bpy.ops.object.mode_set (mode='POSE')
                                
                else:
                    report (self, 'Props were not saved for this action.', 'WARNING')
                    
        else:
            report (self, 'No action.', 'WARNING')
                    
        # end of operator
        return {'FINISHED'}
    
    # when the buttons should show up    
    @classmethod
    def poll(cls, context):      
        return bpy.context.mode == 'POSE'
    
    
class Op_GYAZGameRig_ResetProps (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_game_rigger_reset_props"  
    bl_label = "GYAZ Game Rigger: ResetProps"
    bl_description = "Reset all props or prop by name to default value"
    
    all: BoolProperty (name='All', default=True)
    name: StringProperty (name='Prop Name:', default='')
    
    def invoke (self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    # operator function
    def execute(self, context):
        
        all = self.all
        prop_name = self.name
        rig = bpy.context.active_object
        pbones = rig.pose.bones

        prop_info = rig.data['prop_defaults']
        
        if all:
            
            for item in prop_info:
                pbone = pbones.get (item['bone'])
                if pbone != None:
                    key = item['key']
                    if key in pbone:
                        pbone[key] = item['value']
                        
        else:
            
            for item in prop_info:
                if item['key'] == prop_name:
                    pbone = pbones.get (item['bone'])
                    if pbone != None:
                        key = item['key']
                        if key in pbone:
                            pbone[key] = item['value']   
                    
        # end of operator
        return {'FINISHED'}
    
    # when the buttons should show up    
    @classmethod
    def poll(cls, context):      
        return bpy.context.mode == 'POSE'
    
    
class Op_GYAZGameRig_Button (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_game_rigger_button"  
    bl_label = "GYAZ Game Rigger: Button"
    bl_description = "Set switch"
    
    # operator function
    def execute(self, context):
                                    
        # end of operator
        return {'FINISHED'}

    
#######################################################
#######################################################
    
#UI

class BONE_PT_GYAZGameRig (Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'bone'
    bl_label = 'GYAZ Game Rig'  
    
    # add ui elements here
    def draw (self, context):
                
        lay = self.layout                
        rig = bpy.context.active_object
        pbones = rig.pose.bones
        rig_data = rig.data
        
        owner = bpy.context.scene.gyaz_rig
        
        # low-level rig properties
        row = lay.row (align=True)
        row.label (text="Low-level Rig:")
        row.prop (owner, 'show_low_level_props', text='', icon='TRIA_UP' if owner.show_low_level_props else 'TRIA_DOWN', emboss=False)
        if owner.show_low_level_props:
            col = lay.column (align=True)           
            bone_name = 'module_props__' + 'general'
            if pbones.get (bone_name) != None:
                pbone = pbones[bone_name]
                for prop in pbone.keys():
                    if prop != '_RNA_UI':
                        slider = False if prop.startswith ('switch') or prop.startswith ('visible') or prop.startswith ('limit') else True
                        col.prop (pbone, '["'+prop+'"]', slider=slider)
               
        row = lay.row (align=True)     
        row.prop (rig, 'show_in_front')
        row.prop (rig_data, 'show_bone_custom_shapes', text='Shapes')
        row.operator (Op_GYAZGameRig_HideSelectCharacterMeshes.bl_idname, text='Meshes', icon='UNLOCKED').hidden = False 
        row.operator (Op_GYAZGameRig_HideSelectCharacterMeshes.bl_idname, text='', icon='LOCKED').hidden = True  
        
        row = lay.row (align=True)
        row.label (text='Props:')        
        row.operator (Op_GYAZGameRig_SavePropsToAction.bl_idname, text='Save').mode='SAVE'
        row.operator (Op_GYAZGameRig_SavePropsToAction.bl_idname, text='Load').mode='LOAD'
        row.operator (Op_GYAZGameRig_ResetProps.bl_idname, text='Default')        
        
        lay.label (text="Global:")

        row = lay.row (align=True)
        op = row.operator (Op_GYAZGameRig_Switch.bl_idname, text="FK", icon_value=custom_icons["switch_fk"].icon_id)
        op.is_local, op.mode = False, 'FK'
        op = row.operator (Op_GYAZGameRig_Switch.bl_idname, text="IK/CTRL", icon_value=custom_icons["switch_ik"].icon_id)
        op.is_local, op.mode = False, 'IK/CTRL'
        op = row.operator (Op_GYAZGameRig_Switch.bl_idname, text="BASE", icon_value=custom_icons["switch_base"].icon_id)
        op.is_local, op.mode = False, 'BASE'
        
        col = lay.column (align=True)
        row = col.row (align=True)
        op = row.operator (Op_GYAZGameRig_SetVisible.bl_idname, text="FK", icon_value=custom_icons["visible_fk"].icon_id)
        op.is_local, op.mode = False, 'SHOW_FK'
        op = row.operator (Op_GYAZGameRig_SetVisible.bl_idname, text="FK", icon_value=custom_icons["invisible_fk"].icon_id)
        op.is_local, op.mode = False, 'HIDE_FK'
        row.separator ()
        op = row.operator (Op_GYAZGameRig_SetVisible.bl_idname, text="IK/CTRL", icon_value=custom_icons["visible_ik"].icon_id)
        op.is_local, op.mode = False, 'SHOW_IK/CTRL'
        op = row.operator (Op_GYAZGameRig_SetVisible.bl_idname, text="IK/CTRL", icon_value=custom_icons["invisible_ik"].icon_id)
        op.is_local, op.mode = False, 'HIDE_IK/CTRL'

        enabled = True if context.mode == 'POSE' else False
        
        row = lay.row (align=True)
        row.label (text="Module:")
        row.prop (owner, 'switch_when_snap')
        row.prop (owner, 'show_switch_visible', icon='TRIA_UP' if owner.show_switch_visible else 'TRIA_DOWN', emboss=False, text='')
        row = lay.row ()
        row.enabled = enabled
        col = row.column (align=True)
        op = col.operator (Op_GYAZGameRig_Switch.bl_idname, text="Switch to FK", icon_value=custom_icons["switch_fk"].icon_id)
        op.is_local, op.mode = True, 'FK'
        op = col.operator (Op_GYAZGameRig_Switch.bl_idname, text="Switch to IK/CTRL", icon_value=custom_icons["switch_ik"].icon_id)
        op.is_local, op.mode = True, 'IK/CTRL' 
        
        col = row.column (align=True)
        col.enabled = enabled
        op = col.operator (Op_GYAZGameRig_SetVisible.bl_idname, text="Show/Hide FK", icon_value=custom_icons["visible_fk"].icon_id)
        op.is_local, op.mode = True, 'SHOW_FK'
        op = col.operator (Op_GYAZGameRig_SetVisible.bl_idname, text="Show/Hide IK/CTRL", icon_value=custom_icons["visible_ik"].icon_id)
        op.is_local, op.mode = True, 'SHOW_IK/CTRL'
        
        row = lay.row (align=True)
        row.operator (Op_GYAZGameRig_SnapFKtoIK.bl_idname, text="Snap FK to IK", icon_value=custom_icons["snap_fk"].icon_id)
        row.operator (Op_GYAZGameRig_SnapIKtoFK.bl_idname, text="Snap IK to FK", icon_value=custom_icons["snap_ik"].icon_id)
        col = lay.column ()
        col.scale_y = 2
        col.operator (Op_GYAZGameRig_SelectModuleBones.bl_idname, text="Select Module Bones", icon_value=custom_icons["select_bone"].icon_id)
        
        # module properies
        if context.mode == 'POSE':
            col = lay.column (align=True)
            if bpy.context.active_pose_bone != None:
                active_bone = bpy.context.active_pose_bone
                if 'module' in active_bone:
                    module = active_bone['module']
                    bone_name = 'module_props__' + module
                    if pbones.get (bone_name) != None:
                        pbone = pbones[bone_name]            
                        for prop in pbone.keys():
                            if (prop.startswith('switch') or prop.startswith('visible')) and owner.show_switch_visible:
                                col.prop (pbone, '["'+prop+'"]')

                
            # bone properties
            col = lay.column (align=True)
            pbone = bpy.context.active_pose_bone
            if pbone != None:
                for key in pbone.keys():
                    if key != '_RNA_UI' and key != 'bone_type' and key != 'module' and key != 'source_bone':
                        slider = False if key.startswith ('limit') or key.startswith ('active') else True
                        col.prop (pbone, '["'+key+'"]', slider=slider)
                        
        
        if addon_utils.check ('GYAZ_export_tools') == (True, True):
            row = lay.row ()
            row.scale_x, row.scale_y = 2, 1
            row.label (text='')
            row.operator ('object.gyaz_export_export', text='', icon='EXPORT').asset_type_override='ANIMATIONS'
            row.operator ('object.gyaz_export_select_file_in_explorer', text='', icon='VIEWZOOM').path=context.scene.gyaz_export.path_to_last_export
            
   
    # when the buttons should show up    
    @classmethod
    def poll(cls, context):
        ao = bpy.context.active_object
        if ao is not None:      
            return ao.type == 'ARMATURE' and "GYAZ_rig" in ao.data and 'GYAZ_rig_generated' in ao.data
    
    
class BONE_PT_GYAZGameRigSnapAndKey (Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'bone'
    bl_label = 'GYAZ Snap&Key'     
    
    # add ui elements here
    def draw (self, context):
                
        lay = self.layout        
        rig = bpy.context.active_object
        pbones = rig.pose.bones
        rig_data = rig.data
        
        row = lay.row (align=True)
        row.prop (rig, '["snap_start"]', text='')
        row.operator (Op_GYAZGameRig_SetSnapPropToCurrentFrame.bl_idname, text='', icon='EYEDROPPER').prop_name='snap_start'
        row.separator ()
        row.prop (rig, '["snap_end"]', text='')
        row.operator (Op_GYAZGameRig_SetSnapPropToCurrentFrame.bl_idname, text='', icon='EYEDROPPER').prop_name='snap_end'
        
        col = lay.column (align=True)
        if 'snappable_modules' in rig_data:
            for module in rig_data['snappable_modules']:           
                if pbones.get ('module_props__'+module) != None:
                    row = col.row ()
                    icon = "CHECKBOX_DEHLT" if pbones['module_props__'+module]["snap_n_key__should_snap"] == 0 else "CHECKBOX_HLT"
                    row.operator (Op_GYAZGameRig_SetSnapPropActive.bl_idname, text=module+':', icon=icon, emboss=False).module=module
                    pbone = pbones['module_props__'+module]
                    fk_ik = 'snap_n_key__fk_ik'
                    if fk_ik in pbone:
                        icon = 'snap_fk' if pbone[fk_ik] == 0 else 'snap_ik'
                        text = 'FK to IK' if pbone[fk_ik] == 0 else 'IK to FK'
                        row.operator (Op_GYAZGameRig_SetSnapPropFKIK.bl_idname, text=text, icon_value=custom_icons[icon].icon_id, emboss=False).module=module
                    else:
                        row.operator (Op_GYAZGameRig_Button.bl_idname, icon_value=custom_icons['snap_fk'].icon_id, text='FK to CTRL', emboss=False)
                    
        lay.operator (Op_GYAZGameRig_SnapAndKey.bl_idname, text='Snap and Key', icon_value=custom_icons["snow"].icon_id)            

   
    # when the buttons should show up    
    @classmethod
    def poll(cls, context):
        ao = bpy.context.active_object
        if ao is not None:      
            return ao.type == 'ARMATURE' and "GYAZ_rig" in ao.data and 'GYAZ_rig_generated' in ao.data


#######################################################
#######################################################

#REGISTER
#everything should be registeres here

def register():
    
    # custom icons
    custom_icon_names = ['switch_fk', 'switch_ik', 'visible_fk', 'visible_ik', 'snap_fk', 'snap_ik', 'select_bone', 'switch_base', 'invisible_fk', 'invisible_ik', 'snow']
    
    global custom_icons
    custom_icons = bpy.utils.previews.new ()
    icons_dir = os.path.join ( os.path.dirname (__file__), "icons" )
    for icon_name in custom_icon_names:
        custom_icons.load ( icon_name, os.path.join (icons_dir, icon_name+'.png'), 'IMAGE' )
    # referencing icons:
    # icon_value = custom_icons["custom_icon"].icon_id 
    
    bpy.utils.register_class(PG_GYAZ_GameRig)
    bpy.types.Scene.gyaz_rig = bpy.props.PointerProperty(type=PG_GYAZ_GameRig)
    
    
    bpy.utils.register_class (Op_GYAZGameRig_SnapFKtoIK)  
    bpy.utils.register_class (Op_GYAZGameRig_SnapIKtoFK) 
    bpy.utils.register_class (Op_GYAZGameRig_SnapAndKey) 
    bpy.utils.register_class (Op_GYAZGameRig_Switch)  
    bpy.utils.register_class (Op_GYAZGameRig_SetVisible)  
    bpy.utils.register_class (Op_GYAZGameRig_SetSnapPropToCurrentFrame)  
    bpy.utils.register_class (Op_GYAZGameRig_SetSnapPropFKIK)  
    bpy.utils.register_class (Op_GYAZGameRig_SetSnapPropActive)  
    bpy.utils.register_class (Op_GYAZGameRig_HideSelectCharacterMeshes)
    bpy.utils.register_class (Op_GYAZGameRig_AppendSourceRig)   
    bpy.utils.register_class (Op_GYAZGameRig_SelectModuleBones)         
    bpy.utils.register_class (Op_GYAZGameRig_SavePropsToAction)         
    bpy.utils.register_class (Op_GYAZGameRig_ResetProps)         
    bpy.utils.register_class (Op_GYAZGameRig_Button)         
    bpy.utils.register_class (BONE_PT_GYAZGameRig)      
    bpy.utils.register_class (BONE_PT_GYAZGameRigSnapAndKey)  
    bpy.types.VIEW3D_MT_armature_add.append(add_source_rig_button)      

def unregister ():
    
    # custom icons
    global custom_icons
    bpy.utils.previews.remove (custom_icons) 
    
    del bpy.types.Scene.gyaz_rig
    bpy.utils.unregister_class(PG_GYAZ_GameRig)
    
    
    bpy.utils.unregister_class (Op_GYAZGameRig_SnapFKtoIK)
    bpy.utils.unregister_class (Op_GYAZGameRig_SnapIKtoFK)
    bpy.utils.unregister_class (Op_GYAZGameRig_SnapAndKey)
    bpy.utils.unregister_class (Op_GYAZGameRig_Switch)
    bpy.utils.unregister_class (Op_GYAZGameRig_SetVisible)
    bpy.utils.unregister_class (Op_GYAZGameRig_SetSnapPropToCurrentFrame)
    bpy.utils.unregister_class (Op_GYAZGameRig_SetSnapPropFKIK)
    bpy.utils.unregister_class (Op_GYAZGameRig_SetSnapPropActive)
    bpy.utils.unregister_class (Op_GYAZGameRig_HideSelectCharacterMeshes)
    bpy.utils.unregister_class (Op_GYAZGameRig_AppendSourceRig)
    bpy.utils.unregister_class (Op_GYAZGameRig_SelectModuleBones)
    bpy.utils.unregister_class (Op_GYAZGameRig_SavePropsToAction)
    bpy.utils.unregister_class (Op_GYAZGameRig_ResetProps)
    bpy.utils.unregister_class (Op_GYAZGameRig_Button)
    bpy.utils.unregister_class (BONE_PT_GYAZGameRig)
    bpy.utils.unregister_class (BONE_PT_GYAZGameRigSnapAndKey)
    bpy.types.VIEW3D_MT_armature_add.remove(add_source_rig_button)
  
if __name__ == "__main__":   
    register()