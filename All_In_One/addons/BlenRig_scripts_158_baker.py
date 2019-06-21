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
    'name': 'BlenRig script',
    'author': 'Bart Crouch & Juan Pablo Bouza',
    'version': (158,),
    'blender': (2, 69, 8),
    'api': 55057,
    'location': 'View3D > Properties > BlenRig Controls panel',
    'warning': '',
    'description': 'Tools for controlling BlenRig rigs',
    'wiki_url': 'http://www.jpbouza.com.ar',
    'tracker_url': '',
    "category": "Learnbgame",
}


import bpy
rig_name = "BlenRig"


# used for Full Bake
proportions_baker = ["zepam_mesh", "zepam_nails", "blenrig_mesh", "blenrig_mask", "blenrig_mask_jaw", "teeth_up_mesh", "teeth_low_mesh", "cornea_right", "eye_right", "eye_left", "cornea_left"]
reparent = ["blenrig_mask", "blenrig_mask_jaw", "blenrig_mask_rig"]
armature_baker = ["blenrig_mask_rig", "blenrig"]


# bones that should not be baked by Armature Baker
exclude_bones = []

# global group lists
all_bones = hand_l = hand_r = arm_l = arm_r = leg_l = leg_r = foot_l = foot_r = head = torso = []

####### Bones Hiding System #######

from bpy.props import FloatProperty



def bone_auto_hide(context):
    if bpy.context.screen.is_animation_playing == False:      
        arm = bpy.context.active_object.data
        
    # Torso FK/IK    
        prop = int(bpy.context.active_object.ik_torso)
        prop_inv = int(bpy.context.active_object.inv_torso)    
     
        for bone in arm.bones:
            fk_bones_layer_0 = ['spine_1', 'torso_ctrl_fk', 'spine_2', 'spine_3']
            ik_bones_layer_0 = ['torso_ctrl','torso_pivot_point']
            fk_bones_layer_1 = []
            ik_bones_layer_1 = ['spine_ctrl_2', 'spine_ctrl_3', 'spine_ctrl_4']               
            if (bone.name in ik_bones_layer_0):
                if prop == 1 or prop_inv == 1:
                    bone.layers[0] = 0     
                else:
                    bone.layers[0] = 1   
            if (bone.name in ik_bones_layer_1):
                if prop == 1 or prop_inv == 1:
                    bone.layers[1] = 0     
                else:
                    bone.layers[1] = 1    
            if (bone.name in fk_bones_layer_0):
                if prop != 1 or prop_inv == 1:
                    bone.layers[0] = 0     
                else:
                    bone.layers[0] = 1                   
            
    # Torso INV   
        for bone in arm.bones:   
            inv_bones_layer_0 = ['pelvis_inv', 'pelvis_ctrl_fk_inv', 'spine_1_inv', 'spine_2_inv', 'spine_3_inv', 'torso_ctrl_inv']                  
            if (bone.name in inv_bones_layer_0):
                if bone.layers[0] != prop_inv:
                    bone.layers[0] = prop_inv

    # Neck FK/IK          
        prop = int(bpy.context.active_object.ik_head)
        for bone in arm.bones:        
            fk_bones_layer_0 = ['neck_1', 'neck_2', 'neck_3', 'head', 'head_ctrl_fk']   
            ik_bones_layer_0 = ['head_ctrl',]       
            ik_bones_layer_1 = ['neck_ctrl_2', 'neck_ctrl_3', 'neck_ctrl', 'neck_pivot_point']  
            if (bone.name in fk_bones_layer_0):
                if bone.layers[0] != prop:
                    bone.layers[0] = prop     
            if (bone.name in ik_bones_layer_0):
                if bone.layers[0] == prop:
                    bone.layers[0] = not(prop)   
            if (bone.name in ik_bones_layer_1):
                if bone.layers[1] == prop:
                    bone.layers[1] = not(prop)                           
            
    # Arm_L FK/IK            
        prop = int(bpy.context.active_object.ik_arm_L)
        prop_hinge = int(bpy.context.active_object.hinge_hand_L)
        for bone in arm.bones:        
            fk_bones_layer_0 = ['arm_L', 'forearm_L']   
            ik_bones_layer_0 = ['elbow_L', 'elbow_line_L']  
            ik_hand = ['hand_ik_L']  
            fk_hand = ['hand_fk_L'] 
            ik_palm = ['palm_bend_ik_ctrl_L'] 
            fk_palm = ['palm_bend_fk_ctrl_L']    
            if (bone.name in fk_bones_layer_0):
                if bone.layers[0] != prop:
                    bone.layers[0] = prop     
            if (bone.name in ik_bones_layer_0):
                if bone.layers[0] == prop:
                    bone.layers[0] = not(prop)                      

    # HAND_L
            if (bone.name in ik_hand):    
                if prop == 1 and prop_hinge == 0:
                    bone.layers[0] = 0
                else:
                    bone.layers[0] = 1    
            if (bone.name in fk_hand):     
                if bone.layers[0] == prop_hinge:
                    bone.layers[0] = not(prop_hinge)
            if (bone.name in ik_palm):                        
                if prop == 1 or prop_hinge == 0:      
                    bone.layers[0] = 0
                else:
                    bone.layers[0] = 1                        
            if (bone.name in fk_palm):                        
                if prop == 1 or prop_hinge == 0:      
                    bone.layers[0] = 1
                else:
                    bone.layers[0] = 0   
                                                    
    # Fingers_L   
        prop_hinge = int(bpy.context.active_object.hinge_fing_ind_L)
        for bone in arm.bones:   
            finger_hinge_ind = ['fing_ind_hinge_L']
            if (bone.name in finger_hinge_ind):
                if bone.layers[6] != prop_hinge:
                    bone.layers[6] = prop_hinge         
        prop_hinge = int(bpy.context.active_object.hinge_fing_mid_L) 
        for bone in arm.bones:   
            finger_hinge_mid = ['fing_mid_hinge_L']   
            if (bone.name in finger_hinge_mid):
                if bone.layers[6] != prop_hinge:
                    bone.layers[6] = prop_hinge           
#        prop_hinge = int(bpy.context.active_object.hinge_fing_ring_L)   
#        for bone in arm.bones:  
#            finger_hinge_ring = ['fing_ring_hinge_L']     
#            if (bone.name in finger_hinge_ring):
#                if bone.layers[6] != prop_hinge:
#                    bone.layers[6] = prop_hinge                                        
        prop_hinge = int(bpy.context.active_object.hinge_fing_lit_L)  
        for bone in arm.bones:   
            finger_hinge_lit = ['fing_lit_hinge_L']     
            if (bone.name in finger_hinge_lit):
                if bone.layers[6] != prop_hinge:
                    bone.layers[6] = prop_hinge                                   
        prop_hinge = int(bpy.context.active_object.hinge_fing_thumb_L) 
        for bone in arm.bones:   
            finger_hinge_thumb = ['fing_thumb_hinge_L']        
            if (bone.name in finger_hinge_thumb):
                if bone.layers[6] != prop_hinge:
                    bone.layers[6] = prop_hinge        
                       
    # Leg_L FK/IK            
        prop = int(bpy.context.active_object.ik_leg_L)
        for bone in arm.bones:        
            fk_bones_layer_0 = ['thigh_L', 'calf_L', 'foot_L']        
            ik_bones_layer_0 = ['knee_L', 'knee_line_L', 'foot_roll_ctrl_L', 'sole_pivot_point_L', 'foot_ik_ctrl_L', 'sole_ctrl_L']  
            if (bone.name in fk_bones_layer_0):
                if bone.layers[0] != prop:
                    bone.layers[0] = prop     
            if (bone.name in ik_bones_layer_0):
                if bone.layers[0] == prop:
                    bone.layers[0] = not(prop)   
         
    # Foot_L FK/IK            
        prop = int(bpy.context.active_object.ik_foot_L)
        for bone in arm.bones:        
            fk_bones_layer_0 = ['toe_1_L', 'toe_2_L']        
            ik_bones_layer_0 = ['toes_ctrl_mid_L', 'toes_ctrl_L']  
            ik_bones_layer_1 = ['toe_roll_2_L', 'toe_roll_1_L']              
            if (bone.name in fk_bones_layer_0):
                if bone.layers[0] != prop:
                    bone.layers[0] = prop     
            if (bone.name in ik_bones_layer_0):
                if bone.layers[0] == prop:
                    bone.layers[0] = not(prop)           
            if (bone.name in ik_bones_layer_1):
                if bone.layers[1] == prop:
                    bone.layers[1] = not(prop)    
 
 
    # Arm_R FK/IK            
        prop = int(bpy.context.active_object.ik_arm_R)
        prop_hinge = int(bpy.context.active_object.hinge_hand_R)
        for bone in arm.bones:        
            fk_bones_layer_0 = ['arm_R', 'forearm_R']   
            ik_bones_layer_0 = ['elbow_R', 'elbow_line_R']  
            ik_hand = ['hand_ik_R']  
            fk_hand = ['hand_fk_R'] 
            ik_palm = ['palm_bend_ik_ctrl_R'] 
            fk_palm = ['palm_bend_fk_ctrl_R']    
            if (bone.name in fk_bones_layer_0):
                if bone.layers[0] != prop:
                    bone.layers[0] = prop     
            if (bone.name in ik_bones_layer_0):
                if bone.layers[0] == prop:
                    bone.layers[0] = not(prop)                      

    # HAND_R
            if (bone.name in ik_hand):    
                if prop == 1 and prop_hinge == 0:
                    bone.layers[0] = 0
                else:
                    bone.layers[0] = 1    
            if (bone.name in fk_hand):     
                if bone.layers[0] == prop_hinge:
                    bone.layers[0] = not(prop_hinge)
            if (bone.name in ik_palm):                        
                if prop == 1 or prop_hinge == 0:      
                    bone.layers[0] = 0
                else:
                    bone.layers[0] = 1                        
            if (bone.name in fk_palm):                        
                if prop == 1 or prop_hinge == 0:      
                    bone.layers[0] = 1
                else:
                    bone.layers[0] = 0   
                                                    
    # Fingers_R   
        prop_hinge = int(bpy.context.active_object.hinge_fing_ind_R)
        for bone in arm.bones:   
            finger_hinge_ind = ['fing_ind_hinge_R']
            if (bone.name in finger_hinge_ind):
                if bone.layers[6] != prop_hinge:
                    bone.layers[6] = prop_hinge         
        prop_hinge = int(bpy.context.active_object.hinge_fing_mid_R) 
        for bone in arm.bones:   
            finger_hinge_mid = ['fing_mid_hinge_R']   
            if (bone.name in finger_hinge_mid):
                if bone.layers[6] != prop_hinge:
                    bone.layers[6] = prop_hinge           
#        prop_hinge = int(bpy.context.active_object.hinge_fing_ring_R)   
#        for bone in arm.bones:  
#            finger_hinge_ring = ['fing_ring_hinge_R']     
#            if (bone.name in finger_hinge_ring):
#                if bone.layers[6] != prop_hinge:
#                    bone.layers[6] = prop_hinge                                        
        prop_hinge = int(bpy.context.active_object.hinge_fing_lit_R)  
        for bone in arm.bones:   
            finger_hinge_lit = ['fing_lit_hinge_R']     
            if (bone.name in finger_hinge_lit):
                if bone.layers[6] != prop_hinge:
                    bone.layers[6] = prop_hinge                                   
        prop_hinge = int(bpy.context.active_object.hinge_fing_thumb_R) 
        for bone in arm.bones:   
            finger_hinge_thumb = ['fing_thumb_hinge_R']        
            if (bone.name in finger_hinge_thumb):
                if bone.layers[6] != prop_hinge:
                    bone.layers[6] = prop_hinge        
                       
    # Leg_R FK/IK            
        prop = int(bpy.context.active_object.ik_leg_R)
        for bone in arm.bones:        
            fk_bones_layer_0 = ['thigh_R', 'calf_R', 'foot_R']        
            ik_bones_layer_0 = ['knee_R', 'knee_line_R', 'foot_roll_ctrl_R', 'sole_pivot_point_R', 'foot_ik_ctrl_R', 'sole_ctrl_R']  
            if (bone.name in fk_bones_layer_0):
                if bone.layers[0] != prop:
                    bone.layers[0] = prop     
            if (bone.name in ik_bones_layer_0):
                if bone.layers[0] == prop:
                    bone.layers[0] = not(prop)   
         
    # Foot_R FK/IK            
        prop = int(bpy.context.active_object.ik_foot_R)
        for bone in arm.bones:        
            fk_bones_layer_0 = ['toe_1_R', 'toe_2_R']        
            ik_bones_layer_0 = ['toes_ctrl_mid_R', 'toes_ctrl_R']  
            ik_bones_layer_1 = ['toe_roll_2_R', 'toe_roll_1_R']              
            if (bone.name in fk_bones_layer_0):
                if bone.layers[0] != prop:
                    bone.layers[0] = prop     
            if (bone.name in ik_bones_layer_0):
                if bone.layers[0] == prop:
                    bone.layers[0] = not(prop)           
            if (bone.name in ik_bones_layer_1):
                if bone.layers[1] == prop:
                    bone.layers[1] = not(prop)    
                    
######### Hanlder for update on fram change #########

if bpy.app.handlers.frame_change_post:
    bpy.app.handlers.frame_change_post[0] = bone_auto_hide
    bpy.app.handlers.load_post[0] = bone_auto_hide
else:
    bpy.app.handlers.frame_change_post.append(bone_auto_hide)
    bpy.app.handlers.load_post.append(bone_auto_hide)
    
######### Update Function for Properties ##########

def prop_update(self, context):
    bone_auto_hide(context)

######### Properties Creation ############

#FK/IK

bpy.types.Object.ik_head = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="ik_head"
)
bpy.types.Object.hinge_head_accessory = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_head_accessory"
)
bpy.types.Object.hinge_head_accessory_2 = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_head_accessory_2"
)
bpy.types.Object.ik_torso = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="ik_torso"
)
bpy.types.Object.inv_torso = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="inv_torso"
)
bpy.types.Object.ik_arm_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="ik_arm_L"
)
bpy.types.Object.ik_arm_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="ik_arm_R"
)
bpy.types.Object.ik_leg_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="ik_leg_L"
)
bpy.types.Object.ik_foot_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="ik_foot_L"
)
bpy.types.Object.ik_leg_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="ik_leg_R"
)
bpy.types.Object.ik_foot_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="ik_foot_R"
)

# HINGE

bpy.types.Object.hinge_head = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_head"
)
bpy.types.Object.hinge_arm_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_arm_L"
)
bpy.types.Object.hinge_arm_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_arm_R"
)
bpy.types.Object.hinge_hand_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_hand_L"
)
bpy.types.Object.hinge_fing_ind_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_fing_ind_L"
)
bpy.types.Object.hinge_fing_mid_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_fing_mid_L"
)
bpy.types.Object.hinge_fing_ring_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_fing_mid_L"
)
bpy.types.Object.hinge_fing_lit_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_fing_lit_L"
)
bpy.types.Object.hinge_fing_thumb_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_fing_thumb_L"
)
bpy.types.Object.hinge_hand_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_hand_R"
)
bpy.types.Object.hinge_fing_ind_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_fing_ind_R"
)
bpy.types.Object.hinge_fing_mid_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_fing_mid_R"
)
bpy.types.Object.hinge_fing_ring_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_fing_mid_R"
)
bpy.types.Object.hinge_fing_lit_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_fing_lit_R"
)
bpy.types.Object.hinge_fing_thumb_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_fing_thumb_R"
)
bpy.types.Object.hinge_accessory_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_hand_L"
)
bpy.types.Object.hinge_accessory_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_hand_R"
)
bpy.types.Object.hinge_leg_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_leg_L"
)
bpy.types.Object.hinge_leg_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="hinge_leg_R"
)            

####### MISC
bpy.types.Object.look_switch = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    options={'ANIMATABLE'},
    description="Change to Update",
    update=prop_update,
    name="look_switch"
)      


########### User interface
class BlenRigInterface(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'BlenRig Controls (V 158)'
    
    @classmethod
    def poll(cls, context):
        if not bpy.context.active_object:
            return False
        return (context.active_object.type in ["ARMATURE", "MESH"])

    def draw(self, context):
        global all_bones, hand_l, hand_r, arm_l, arm_r, leg_l, leg_r, foot_l, foot_r, head, torso

        layout = self.layout
        arm = context.active_object.data
        armobj = context.active_object
        props = context.window_manager.blenrig_props
        
        try:
            selected_bones = [bone.name for bone in context.selected_pose_bones]
        except:
            selected_bones = []
        try:
            blenrig = context.active_object.data["rig_name"]==rig_name
        except:
            blenrig = False
        
        def is_selected(names):
            for name in names:
                if name in selected_bones:
                    return True
            return False
        
        if context.mode=="POSE" and blenrig:
            
######### Bone groups used for Inherit Scale Checkboxes & Sensible to Selection Sliders Display
            if not all_bones:
                all_bones = []
                for bone in armobj.pose.bones:
                     all_bones.append(bone.name)

                hand_l=[]
                for bone in all_bones[:]:
                    if bone.count("_L"):
                        if bone.count("fing"):
                            hand_l.append(bone)
                hand_r=[]
                for bone in all_bones[:]:
                    if bone.count ("_R"):
                        if bone.count("fing"):
                            hand_r.append(bone)
                  
                arm_l=[]
                for bone in all_bones[:]:
                    if bone.count ("_L"):
                        if bone.count("arm") or bone.count("elbow") or bone.count("shoulder") or bone.count("hand") or bone.count("wrist"):
                            arm_l.append(bone)

                arm_r=[]
                for bone in all_bones[:]:
                    if bone.count ("_R"):
                        if bone.count("arm") or bone.count("elbow") or bone.count("shoulder") or bone.count("hand") or bone.count("wrist"):
                            arm_r.append(bone)

                leg_l=[]
                for bone in all_bones[:]:
                    if bone.count ("_L"):
                        if bone.count("butt") or bone.count("knee") or bone.count("thigh") or bone.count("calf"):
                            leg_l.append(bone)

                leg_r=[]
                for bone in all_bones[:]:
                    if bone.count ("_R"):
                        if bone.count("butt") or bone.count("knee") or bone.count("thigh") or bone.count("calf"):
                            leg_r.append(bone)

                foot_l=[]
                for bone in all_bones[:]:
                    if bone.count ("_L"):
                        if bone.count("toe") or bone.count("foot") or bone.count("heel") or bone.count("sole") or bone.count("floor"):
                            foot_l.append(bone)

                foot_r=[]
                for bone in all_bones[:]:
                    if bone.count ("_R"):
                        if bone.count("toe") or bone.count("foot") or bone.count("heel") or bone.count("sole") or bone.count("floor"):
                            foot_r.append(bone)

                head=[]
                for bone in all_bones[:]:
                    if bone.count("look") or bone.count("head") or bone.count("neck") or bone.count("maxi") or bone.count("cheek") or bone.count("chin") or bone.count("lip") or bone.count("ear_") or bone.count("tongue") or bone.count("eyelid") or bone.count("forehead") or bone.count("brow") or bone.count("nose") or bone.count("nostril") or bone.count("mouth") or bone.count("eye") or bone.count("gorro") or bone.count("teeth") or bone.count("hat") or bone.count("glasses") or bone.count("anteojos") or bone.count("hair") or bone.count("pelo"):
                        head.append(bone)

                torso=['master']
                for bone in all_bones[:]:
                    if bone.count("spine") or bone.count("pelvis") or bone.count("torso") or bone.count("omoplate") or bone.count("chest") or bone.count("body") or bone.count("ball") or bone.count("dicky") or bone.count("butt") or bone.count("back") or bone.count("clavi") or bone.count("look") or bone.count("hip"):
                        torso.append(bone)
            

########### Armature Layers
            if "gui_layers" in arm:
                box = layout.box()
                col = box.column()             
                row = col.row()
            if "gui_layers" in arm and arm["gui_layers"]:
                row.operator("armature.blenrig_gui", icon="TRIA_DOWN").tab = "gui_layers"
                row.label(text="ARMATURE LAYERS", icon='RENDERLAYERS')
                # expanded box
                col.separator()
                col2 = box.column()
                col2.scale_y=0.85                  
                body = col2.row()
                body.prop(arm, "layers", index=0 , toggle=True, text="BODY")
                body.prop(arm, "layers", index=1, toggle=True, text="BODY EXTRAS")              
                col2.separator()   
                body = col2.row()
                body.prop(arm, "layers", index=6, toggle=True, text="FINGERS")                                                                  
                col2.separator()                   
                body = col2.row()                               
                body.prop(arm, "layers", index=3, toggle=True, text="FACIAL")
                col2.separator()
                body = col2.row()                
                body.prop(arm, "layers", index=19, toggle=True, text="FACIAL EXTRAS I")
                body.prop(arm, "layers", index=4, toggle=True, text="FACIAL EXTRAS II")
                col2.separator()
                body = col2.row()                                
                body.prop(arm, "layers", index=16 , toggle=True, text="TOON")
                body.prop(arm, "layers", index=17 , toggle=True, text="TOON EXTRAS")    
                col2.separator()                           
                body = col2.row()          
                body.prop(arm, "layers", index=18 , toggle=True, text="SCALE")
                col2.separator()
                body = col2.row()                
                bodycol = body.column()
                bodycol2 = bodycol.row()                 
                bodycol3 = body.column()    
                bodycol3.scale_x = 0.25                  
                bodycol2.prop(arm, "layers", index=5 , toggle=True, text="EXTRAS")    
                bodycol3.prop(arm, "layers", index=2, toggle=True, text="IK-FK")                                                                                
                col2.separator()   
             
                # collapsed box
            elif "gui_layers" in arm:
                row.operator("armature.blenrig_gui", icon="TRIA_RIGHT").tab = "gui_layers"
                row.label(text="ARMATURE LAYERS", icon='RENDERLAYERS')    
########### IK - FK box
            #if is_selected(arm_l + arm_r + leg_l + foot_l + leg_r + foot_r + torso + head) or arm["gui_ik_all"]:
            if "gui_ik" in arm:
                box = layout.box()
                col = box.column()
                row = col.row()
            # expanded box
            if "gui_ik" in arm and arm["gui_ik"]:
                # general
                row.operator("armature.blenrig_gui", icon="TRIA_DOWN").tab = "gui_ik"
                row.label(text="IK / FK", icon='OUTLINER_OB_ARMATURE')
                row = row.row()
                row.alignment = "RIGHT"
                row.prop(props, "gui_ik_all", text="All")
                row = col.row()
                row.label("IK")
                row = row.row()
                row.alignment = "RIGHT"
                row.label("FK")
                    
                # properties
                col.prop(armobj, 'inv_torso', "Invert Torso", slider=True)       
                col.separator()                             
                col.prop(props, "ik_meta", text="All", slider=True)           
                col.separator()
                if is_selected(head) or props.gui_ik_all:
                    col.prop(armobj, 'ik_head', "Head", slider=True)
                if is_selected(torso) or props.gui_ik_all:
                    col.prop(armobj, 'ik_torso', "Torso", slider=True)  
                if is_selected(arm_l + hand_l) or props.gui_ik_all:
                    col.prop(armobj, 'ik_arm_L', "Arm_Left", slider=True)
                if is_selected(arm_r + hand_r) or props.gui_ik_all:
                    col.prop(armobj, 'ik_arm_R', "Arm_Right", slider=True)
                if is_selected(leg_l + foot_l) or props.gui_ik_all:
                    col.prop(armobj, 'ik_leg_L', "Leg_Left", slider=True)
                if is_selected(foot_l + leg_l) or props.gui_ik_all:
                    col.prop(armobj, 'ik_foot_L', "Foot_Left", slider=True)
                if is_selected(leg_r + foot_r) or props.gui_ik_all:
                    col.prop(armobj, 'ik_leg_R', "Leg_Right", slider=True)
                if is_selected(foot_r + leg_r) or props.gui_ik_all:
                    col.prop(armobj, 'ik_foot_R', "Foot_Right", slider=True)
                    
                if is_selected(head) or props.gui_ik_all:
                    layout.label("SNAP HEAD")  
                    box = layout.box()      
                    col = box.column()
                    row = col.row() 
                    col2 = row.column()           
                    row.operator("head_snap.fk_ik", text="FK >> IK", icon="NONE")  
                    col2.operator("head_snap.ik_fk", text="IK >> FK", icon="NONE")  
                    row2 = col.row()
                    row2.alignment = 'CENTER'        
                    row2.scale_x = 0.5          
                    row2.operator("head.fk_select", text="FK", icon="NONE") 
                    row2.operator("head.ik_select", text="IK", icon="NONE") 
                    
                if is_selected(torso) or props.gui_ik_all:     
                    layout = self.layout      
                    layout.label("SNAP TORSO")  
                    box = layout.box()      
                    col = box.column()
                    row = col.row() 
                    col2 = row.column()  
                    row.operator("torso_snap.fk_ik", text="FK >> IK", icon="NONE")  
                    col2.operator("torso_snap.ik_fk", text="IK >> FK", icon="NONE") 
                    row = col.row() 
                    col2 = row.column()                
                    row.operator("torso_snap.up_inv", text="UP >> INV", icon="NONE")  
                    col2.operator("torso_snap.inv_up", text="INV >> UP", icon="NONE") 
                    row2 = col.row()
                    row2.alignment = 'CENTER'        
                    row2.scale_x = 0.5
                    row2.operator("torso.fk_select", text="Fk", icon="NONE")  
                    row2.operator("torso.ik_select", text="IK", icon="NONE") 
                    row2.operator("torso.inv_select", text="INV", icon="NONE")   
                                                                          
                if is_selected(arm_l + hand_l) or props.gui_ik_all:
                    layout.label("SNAP ARM LEFT")  
                    box = layout.box()      
                    col = box.column()
                    row = col.row() 
                    col2 = row.column()             
                    row.operator("arm_l_snap.fk_ik", text="FK >> IK", icon="NONE")  
                    col2.operator("arm_l_snap.ik_fk", text="IK >> FK", icon="NONE")  
                    row2 = col.row()
                    row2.alignment = 'CENTER'        
                    row2.scale_x = 0.5           
                    row2.operator("arm_l.fk_select", text="FK", icon="NONE") 
                    row2.operator("arm_l.ik_select", text="IK", icon="NONE") 
                    
                if is_selected(arm_r + hand_r) or props.gui_ik_all:   
                    layout.label("SNAP ARM RIGHT")  
                    box = layout.box()      
                    col = box.column()
                    row = col.row() 
                    col2 = row.column()           
                    row.operator("arm_r_snap.fk_ik", text="FK >> IK", icon="NONE")  
                    col2.operator("arm_r_snap.ik_fk", text="IK >> FK", icon="NONE") 
                    row2 = col.row()
                    row2.alignment = 'CENTER'        
                    row2.scale_x = 0.5    
                    row2.operator("arm_r.fk_select", text="FK", icon="NONE") 
                    row2.operator("arm_r.ik_select", text="IK", icon="NONE")                       
                                
                if is_selected(leg_l + foot_l) or props.gui_ik_all:   
                    layout.label("SNAP LEG LEFT")  
                    box = layout.box()      
                    col = box.column()
                    row = col.row() 
                    col2 = row.column()                  
                    row.operator("leg_l_snap.fk_ik", text="FK >> IK", icon="NONE")  
                    col2.operator("leg_l_snap.ik_fk", text="IK >> FK", icon="NONE")
                    row2 = col.row()
                    row2.alignment = 'CENTER'        
                    row2.scale_x = 0.5            
                    row2.operator("leg_l.fk_select", text="FK", icon="NONE") 
                    row2.operator("leg_l.ik_select", text="IK", icon="NONE")                     
                                     
                if is_selected(leg_r + foot_r) or props.gui_ik_all:  
                    layout.label("SNAP LEG RIGHT")  
                    box = layout.box()      
                    col = box.column()
                    row = col.row() 
                    col2 = row.column()            
                    row.operator("leg_r_snap.fk_ik", text="FK >> IK", icon="NONE")  
                    col2.operator("leg_r_snap.ik_fk", text="IK >> FK", icon="NONE")   
                    row2 = col.row()
                    row2.alignment = 'CENTER'        
                    row2.scale_x = 0.5   
                    row2.operator("leg_r.fk_select", text="FK", icon="NONE") 
                    row2.operator("leg_r.ik_select", text="IK", icon="NONE")                      
                                                     

            # collapsed box
            elif "gui_ik" in arm:
                row.operator("armature.blenrig_gui", icon="TRIA_RIGHT").tab = "gui_ik"
                row.label(text="IK / FK", icon='MOD_ARMATURE')

########### Hinge box
            #if is_selected(torso + hand_l + hand_r + arm_l + arm_r + head) or arm["gui_hinge_all"]:
            if "gui_hinge" in arm:
                box = layout.box()
                col = box.column()
                row = col.row()
            # expanded box
            if "gui_hinge" in arm and arm["gui_hinge"]:
                # general
                row.operator("armature.blenrig_gui", icon="TRIA_DOWN").tab = "gui_hinge"
                row.label(text="HINGE", icon='OUTLINER_DATA_ARMATURE')
                row = row.row()
                row.alignment = "RIGHT"
                row.prop(props, "gui_hinge_all", text="All")
                row = col.row()
                row.label("No")
                row = row.row()
                row.alignment = "RIGHT"
                row.label("Yes")

                # properties
                if is_selected(head + torso) or props.gui_hinge_all:
                    col.prop(armobj, 'hinge_head', "Head", slider=True)
                if is_selected(arm_l) or props.gui_hinge_all:
                    col.prop(armobj, 'hinge_arm_L', "Arm_Left", slider=True)
                if is_selected(arm_r) or props.gui_hinge_all:
                    col.prop(armobj, 'hinge_arm_R', "Arm_Right", slider=True)
                if is_selected(arm_l + hand_l) or props.gui_hinge_all:
                    col.prop(armobj, 'hinge_hand_L', "Hand_Left", slider=True)
                if is_selected(arm_r + hand_r) or props.gui_hinge_all:
                    col.prop(armobj, 'hinge_hand_R', "Hand_Right", slider=True)
                if is_selected(leg_l + foot_l) or props.gui_hinge_all:
                    col.prop(armobj, 'hinge_leg_L', "Leg_Left", slider=True)               
                if is_selected(leg_r + foot_r) or props.gui_hinge_all:
                    col.prop(armobj, 'hinge_leg_R', "Leg_Right", slider=True)
                    col.separator()                                                       
                if is_selected(hand_l) or props.gui_hinge_all:
                    col.prop(props, "hinge_fing_L_meta", "All_Fingers_Left", slider=True)
                    col.separator()
                if is_selected(hand_l) or props.gui_hinge_all:
                    col.prop(armobj, 'hinge_fing_thumb_L', "Thumb_Left", slider=True)
                if is_selected(hand_l) or props.gui_hinge_all:
                    col.prop(armobj, 'hinge_fing_ind_L', "Index_Left", slider=True)
                if is_selected(hand_l) or props.gui_hinge_all:
                    col.prop(armobj, 'hinge_fing_mid_L', "Middle_Left", slider=True)
                if is_selected(hand_l) or props.gui_hinge_all:
                    col.prop(armobj, 'hinge_fing_ring_L', "Ring_Left", slider=True)
                if is_selected(hand_l) or props.gui_hinge_all:
                    col.prop(armobj, 'hinge_fing_lit_L', "Little_Left", slider=True)
                    col.separator()
                if is_selected(hand_r) or props.gui_hinge_all:
                    col.prop(props, "hinge_fing_R_meta", "All_Fingers_Right", slider=True)
                    col.separator()
                if is_selected(hand_r) or props.gui_hinge_all:
                    col.prop(armobj, 'hinge_fing_thumb_R', "Thumb_Right", slider=True)
                if is_selected(hand_r) or props.gui_hinge_all:
                    col.prop(armobj, 'hinge_fing_ind_R', "Index_Right", slider=True)
                if is_selected(hand_r) or props.gui_hinge_all:
                    col.prop(armobj, 'hinge_fing_mid_R', "Middle_Right", slider=True)
                if is_selected(hand_r) or props.gui_hinge_all:
                    col.prop(armobj, 'hinge_fing_ring_R', "Ring_Right", slider=True)
                if is_selected(hand_r) or props.gui_hinge_all:
                    col.prop(armobj, 'hinge_fing_lit_R', "Little_Right", slider=True)
            # collapsed box
            elif "gui_hinge" in arm:
                row.operator("armature.blenrig_gui", icon="TRIA_RIGHT").tab = "gui_hinge"
                row.label(text="HINGE", icon='ARMATURE_DATA')

########### Toon System box
            if "gui_toon" in arm:
                box = layout.box()
                col = box.column()
                row = col.row()
            # expanded box
            if "gui_toon" in arm and arm["gui_toon"]:
                row.operator("armature.blenrig_gui", icon="TRIA_DOWN").tab = "gui_toon"
                row.label(text="TOON", icon='CURVE_BEZCURVE')
                col = box.column()
                row = col.row()
                row.alignment = "LEFT"                
                row.label("Stretchy IK")
                col.prop(armobj, '["toon_head"]', "Head", slider=True)
                col.prop(armobj, '["toon_torso"]', "Torso", slider=True)
                col.prop(armobj, '["toon_arm_L"]', "Arm_Left", slider=True)
                col.prop(armobj, '["toon_arm_R"]', "Arm_Right", slider=True)
                col.prop(armobj, '["toon_leg_L"]', "Leg_Left", slider=True)
                col.prop(armobj, '["toon_leg_R"]', "Leg_Right", slider=True)
                box.separator()                               
                col = box.column()
                row = col.row()
                row.label("Follow Smile")
                col.prop(armobj, '["toon_teeth_up"]', "Teeth_Upper", slider=True)
                col.prop(armobj, '["toon_teeth_low"]', "Teeth_Lower", slider=True)

               
            # collapsed box
            elif "gui_muscle" in arm:
                row.operator("armature.blenrig_gui", icon="TRIA_RIGHT").tab = "gui_toon"
                row.label(text="TOON", icon='CURVE_BEZCURVE')                

########### Miscellaneous
            if "gui_misc" in arm:
                box = layout.box()
                col = box.column()
                row = col.row()
            # expanded box
            if "gui_misc" in arm and arm["gui_misc"]:
                row.operator("armature.blenrig_gui", icon="TRIA_DOWN").tab = "gui_misc"
                row.label(text="MISCELLANEOUS", icon='RESTRICT_VIEW_OFF')
                # Model Resolution
                col = box.column()
                col.prop(armobj, '["model_res"]', "Model_Resolution", toggle=True)
                
                # Eyes part
                col = box.column()
                row = col.row()
                row.label("Free")
                row.label("Body")
                row.label("Torso")
                row = row.row()
                row.alignment = "RIGHT"
                row.label("Head")
                col.prop(armobj, 'look_switch', "Look", slider=True)
                
                box.separator()
                
                # Head Accessories
                col = box.column()
                row = col.row()
                row.label("Free")
                row = row.row()
                row.alignment = "RIGHT"
                row.label("Head")
                col.prop(armobj, 'hinge_head_accessory', "Hat", slider=True)
                col.prop(armobj, 'hinge_head_accessory_2', "Glasses", slider=True)
                 
                box.separator()
                
                # Hands Accessories
                col = box.column()
                row = col.row()
                row.label("Free")
                row = row.row()
                row.alignment = "RIGHT"
                row.label("Hand")
                col.prop(armobj, 'hinge_accessory_L', "Item_Hand_Left", slider=True)
                col.prop(armobj, 'hinge_accessory_R', "Item_Hand_Right", slider=True)
              
                box.separator()

            # collapsed box
            elif "gui_misc" in arm:
                row.operator("armature.blenrig_gui", icon="TRIA_RIGHT").tab = "gui_misc"
                row.label(text="MISCELLANEOUS", icon='RESTRICT_VIEW_OFF')

########### Muscle System box
            if "gui_muscle" in arm:
                box = layout.box()
                col = box.column()
                row = col.row()
            # expanded box
            if "gui_muscle" in arm and arm["gui_muscle"]:
                row.operator("armature.blenrig_gui", icon="TRIA_DOWN").tab = "gui_muscle"
                row.label("MUSCLE SYSTEM", 'FORCE_LENNARDJONES')
                # System Toggle
                col = box.column()
                row = col.row()
                row.label("Off")
                row = row.row()
                row.alignment = "RIGHT"
                row.label("On")
                col.prop(armobj, '["mus_sys"]', "Muscles", toggle=True)

                box.separator()

                # Extras Deformation
                col = box.column()
                col.prop(armobj, '["mus_extras"]', "Extras", toggle=True)                

                box.separator()

                # Resolution
                col = box.column()
                col.prop(armobj, '["mus_res"]', "Resolution", toggle=True)
            # collapsed box
            elif "gui_muscle" in arm:
                row.operator("armature.blenrig_gui", icon="TRIA_RIGHT").tab = "gui_muscle"
                row.label("MUSCLE SYSTEM", 'FORCE_LENNARDJONES')

########### Inherit scale box
#            if "gui_scale" in arm:
#                box = layout.box()
#                col = box.column()
#                row = col.row()
#            # expanded box
#            if "gui_scale" in arm and arm["gui_scale"]:
#                # general
#                row.operator("armature.blenrig_gui", icon="TRIA_DOWN").tab = "gui_scale"
#                row.label("INHERIT SCALE", 'GROUP_BONE')
#                row = col.split(percentage=0.15)
#                col_left = row.column()
#                col_right = row.column()
#                col_left.separator()
#                col_right.separator()
#                # properties
#                #Toggle ALL
#                #col_right.label("All")
#                #if arm["scale_meta"]:
#                #    col_left.operator("armature.scale_inherit", icon="CHECKBOX_HLT").group = "scale_meta"
#                #else:
#                #    col_left.operator("armature.scale_inherit", icon="CHECKBOX_DEHLT").group = "scale_meta"
#                #col_right.separator()
#                #col_left.separator()
#                #
#                col_right.label("Uniform Sacle")
#                if arm["inherit_scale"]:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_HLT").group = "inherit_scale"
#                else:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_DEHLT").group = "inherit_scale"
#                col_right.label("Head")                    
#                if arm["scale_head"]:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_HLT").group = "scale_head"
#                else:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_DEHLT").group = "scale_head"
#                    
#                col_right.label("Torso")
#                body = col.row()
#                if arm["scale_torso"]:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_HLT").group = "scale_torso"
#                else:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_DEHLT").group = "scale_torso"
#                col_right.label("Arm_Left")
#                if arm["scale_arm_L"]:
#                        col_left.operator("armature.scale_inherit", icon="CHECKBOX_HLT").group = "scale_arm_L"
#                else:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_DEHLT").group = "scale_arm_L"
#                col_right.label("Hand_Left")
#                if arm["scale_hand_L"]:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_HLT").group = "scale_hand_L"
#                else:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_DEHLT").group = "scale_hand_L"
#                col_right.label("Arm_Right")
#                if arm["scale_arm_R"]:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_HLT").group = "scale_arm_R"
#                else:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_DEHLT").group = "scale_arm_R"
#                col_right.label("Hand_Right")
#                if arm["scale_hand_R"]:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_HLT").group = "scale_hand_R"
#                else:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_DEHLT").group = "scale_hand_R"
#                col_right.label("Leg_Left")
#                if arm["scale_leg_L"]:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_HLT").group = "scale_leg_L"
#                else:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_DEHLT").group = "scale_leg_L"
#                col_right.label("Foot_Left")
#                if arm["scale_foot_L"]:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_HLT").group = "scale_foot_L"
#                else:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_DEHLT").group = "scale_foot_L"
#                col_right.label("Leg_Right")
#                if arm["scale_leg_R"]:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_HLT").group = "scale_leg_R"
#                else:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_DEHLT").group = "scale_leg_R"
#                col_right.label("Foot_Right")
#                if arm["scale_foot_R"]:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_HLT").group = "scale_foot_R"
#                else:
#                    col_left.operator("armature.scale_inherit", icon="CHECKBOX_DEHLT").group = "scale_foot_R"
#
#            # collapsed box
#            elif "gui_scale" in arm:
#                row.operator("armature.blenrig_gui", icon="TRIA_RIGHT").tab = "gui_scale"
#                row.label("INHERIT SCALE", 'GROUP_BONE')
#                                
########### Reproportion box
            #if is_selected(arm_l + hand_l + arm_r + hand_r + leg_l + foot_l + leg_r + foot_r + torso + head) or arm["gui_stretch_all"]:
            if "gui_stretch" in arm:
                box = layout.box()
                col = box.column()
                row = col.row()
            # expanded box
            if "gui_stretch" in arm and arm["gui_stretch"]:
                # general
                row.operator("armature.blenrig_gui", icon="TRIA_DOWN").tab = "gui_stretch"
                row.label(text="REPROPORTION", icon='POSE_HLT')
                row = row.row()
                row.alignment = "RIGHT"
                row.prop(props, "gui_stretch_all", text="All")
                row = col.row()
                row.label("No")
                row = row.row()
                row.alignment = "RIGHT"
                row.label("Yes")

                # properties
                col.prop(props, "str_meta", "All", slider=True)
                col.separator()
                if is_selected(head) or props.gui_stretch_all:
                    col.prop(armobj, '["str_head"]', "Head", slider=True)
                if is_selected(torso) or props.gui_stretch_all:
                    col.prop(armobj, '["str_torso"]', "Torso", slider=True)
                if is_selected(arm_l) or props.gui_stretch_all:
                    col.prop(armobj, '["str_arm_L"]', "Arm_Left", slider=True)
                if is_selected(hand_l) or props.gui_stretch_all:
                    col.prop(armobj, '["str_hand_L"]', "Hand_Left", slider=True)
                if is_selected(arm_r) or props.gui_stretch_all:
                    col.prop(armobj, '["str_arm_R"]', "Arm_Right", slider=True)
                if is_selected(hand_r) or props.gui_stretch_all:
                    col.prop(armobj, '["str_hand_R"]', "Hand_Right", slider=True)
                if is_selected(leg_l) or props.gui_stretch_all:
                    col.prop(armobj, '["str_leg_L"]', "Leg_Left", slider=True)
                if is_selected(foot_l) or props.gui_stretch_all:
                    col.prop(armobj, '["str_foot_L"]', "Foot_Left", slider=True)
                if is_selected(leg_r) or props.gui_stretch_all:
                    col.prop(armobj, '["str_leg_R"]', "Leg_Right", slider=True)
                if is_selected(foot_r) or props.gui_stretch_all:
                    col.prop(armobj, '["str_foot_R"]', "Foot_Right", slider=True)
            # collapsed box
            elif "gui_stretch" in arm:
                row.operator("armature.blenrig_gui", icon="TRIA_RIGHT").tab = "gui_stretch"
                row.label(text="REPROPORTION", icon='OUTLINER_DATA_POSE')

####### Rigging & Baking
        box = layout.box()
        col = box.column()
        row = col.row()
        try:
            gui_bake = arm["gui_bake"]
        except:
            gui_bake = -1
        if gui_bake:
            if gui_bake < 0:
                grey_out = row.column()
                grey_out.enabled = False
                grey_out.operator("armature.blenrig_gui", icon="TRIA_DOWN").tab = "gui_bake"
            else:
                row.operator("armature.blenrig_gui", icon="TRIA_DOWN").tab = "gui_bake"
            row.label(text="RIGGING & BAKING", icon='LAMP_SPOT')
            col.separator()
            col.label("CHARACTER BAKING")
            row = col.row()
            row.operator("armature.proportions_baker", text="Proportions").bake_selected = True
            row.operator("armature.armature_baker", text="Armature")
            row = col.row()
            row.operator("armature.full_bake", text="Full Bake")
            col.separator()
            col.label("ARMATURE EXTRAS")
            split = col.split()
           #row = split.row(align=True)
           #if context.active_object.type == 'ARMATURE':
               #row.prop_enum(arm, "pose_position", 'POSE', text="Pose")
               #row.prop_enum(arm, "pose_position", 'REST', text="Rest")
           #else:
               #row.active = False
               #row.label('Pose positions')       
            row = split.row()
            row.operator("armature.reset_constraints")
            col.separator()
            col.label("REALISTIC JOINTS")            
            col.separator()
            if "rj_arms" in armobj and armobj["rj_arms"]:   
                col.prop(armobj, '["rj_arms"]', "Arms", slider=True)    
                col.prop(armobj, '["rj_hands"]', "Hands", slider=True)   
                col.prop(armobj, '["rj_legs"]', "Legs", slider=True)   
                col.prop(armobj, '["rj_feet"]', "Feet", slider=True)       
                col.separator()
            if "rig_name" in arm and arm["rig_name"]:                
                col.label("RIGGING LAYERS")
                col.prop(context.active_object.data, "layers", index=15, toggle=True, text="WP Bones")
                col.separator()
                body = col.row()
                body.prop(arm, "layers", index=7 , toggle=True, text="REPROPORTION")                                                 
                  
            
        else:
            row.operator("armature.blenrig_gui", icon="TRIA_RIGHT").tab = "gui_bake"
            row.label(text="RIGGING & BAKING", icon='LAMP_SPOT')


# Display or hide tabs (sets the appropriate id-property)
class ARMATURE_OT_blenrig_gui(bpy.types.Operator):
    "Display tab"
    bl_label = ""
    bl_idname = "armature.blenrig_gui"

    tab = bpy.props.StringProperty(name="Tab", description="Tab of the gui to expand")
    
    def invoke(self, context, event):
        arm = bpy.context.active_object.data
        if self.properties.tab in arm:
            arm[self.properties.tab] = not arm[self.properties.tab]
        return{'FINISHED'}


# Toggle scale-inherit property of all bones in group
#class ARMATURE_OT_scale_inherit(bpy.types.Operator):
#    "Mass toggle for the Inherit Scale property"
#    bl_label = ""
#    bl_idname = "armature.scale_inherit"
#
#    group = bpy.props.StringProperty(name="Group")
#    
#    def invoke(self, context, event):
#        global all_bones, hand_l, hand_r, arm_l, arm_r, leg_l, leg_r, foot_l, foot_r, head, torso
#
#        group = self.properties.group
#        arm = bpy.context.active_object.data
#        arm[group] = not arm[group]
#        
#        toggles = []
#        #Toggle All
#        #if group == "scale_meta":
#        #    toggles = hand_l + s_hand_l + hand_r + s_hand_r + s_arm_l + arm_l + s_arm_r + arm_r + leg_l + s_leg_l + leg_r + s_leg_r + foot_l + s_foot_l + foot_r + s_foot_r + s_head + head + s_torso + torso
#        #    all_groups = ["scale_hand_L", "scale_hand_R", "scale_arm_L", "scale_arm_R", "scale_leg_L", "scale_leg_R", "scale_foot_L", "scale_foot_R", "scale_head", "scale_torso"]
#        #    for g in all_groups:
#        #        arm[g] = arm[group]
#        if group == "scale_hand_L":
#            toggles = hand_l
#        elif group == "scale_hand_R":
#            toggles = hand_r
#        elif group == "scale_arm_L":
#            toggles = arm_l
#        elif group == "scale_arm_R":
#            toggles = arm_r
#        elif group == "scale_leg_L":
#            toggles = leg_l
#        elif group == "scale_leg_R":
#            toggles = leg_r 
#        elif group == "scale_foot_L":
#            toggles = foot_l 
#        elif group == "scale_foot_R":
#            toggles = foot_r 
#        elif group == "scale_head":
#            toggles = head
#        elif group == "scale_torso":
#            toggles = torso
#
#        for bone in toggles:
#            arm.bones[bone].use_inherit_scale = arm[group]
#        return{'FINISHED'}
#
# Toggle scale-inherit property of all bones in group
class ARMATURE_OT_scale_inherit(bpy.types.Operator):
    "Mass toggle for the Inherit Scale property"
    bl_label = ""
    bl_idname = "armature.scale_inherit"

    group = bpy.props.StringProperty(name="Group")
    
    def invoke(self, context, event):
        global all_bones, hand_l, hand_r, arm_l, arm_r, leg_l, leg_r, foot_l, foot_r, head, torso

        group = self.properties.group
        arm = bpy.context.active_object.data
        arm[group] = not arm[group]
        
        toggles = []
        #Toggle All
        #if group == "scale_meta":
        #    toggles = hand_l + s_hand_l + hand_r + s_hand_r + s_arm_l + arm_l + s_arm_r + arm_r + leg_l + s_leg_l + leg_r + s_leg_r + foot_l + s_foot_l + foot_r + s_foot_r + s_head + head + s_torso + torso
        #    all_groups = ["scale_hand_L", "scale_hand_R", "scale_arm_L", "scale_arm_R", "scale_leg_L", "scale_leg_R", "scale_foot_L", "scale_foot_R", "scale_head", "scale_torso"]
        #    for g in all_groups:
        #        arm[g] = arm[group]
        if group == "scale_hand_L":
            toggles = hand_l
        elif group == "scale_hand_R":
            toggles = hand_r
        elif group == "scale_arm_L":
            toggles = arm_l
        elif group == "scale_arm_R":
            toggles = arm_r
        elif group == "scale_leg_L":
            toggles = leg_l
        elif group == "scale_leg_R":
            toggles = leg_r 
        elif group == "scale_foot_L":
            toggles = foot_l 
        elif group == "scale_foot_R":
            toggles = foot_r 
        elif group == "scale_head":
            toggles = head
        elif group == "scale_torso":
            toggles = torso
        elif group == "inherit_scale":
            toggles = all_bones    

        for bone in toggles:
            arm.bones[bone].use_inherit_scale = arm[group]
        return{'FINISHED'}



# Proportions Baker operator
class ARMATURE_OT_proportions_baker(bpy.types.Operator):
    bl_label = "Proportions Baker"
    bl_idname = "armature.proportions_baker"
    bl_description = "Bake the proportions to the meshes"
    
    # set to False to bake the meshes defined in "proportions_baker"
    bake_selected = bpy.props.BoolProperty(name="Bake selected", default=True, description="Bake the meshes that are selected in the 3d-view") 
    
    @classmethod
    def poll(cls, context):
        if not bpy.context.object:
            return False
        return (bpy.context.object.type == "MESH" and context.mode=='OBJECT')
    
    def restore_shape_settings(self, old_shape, new_shape):
        new_shape.interpolation = old_shape["interpolation"]
        new_shape.mute = old_shape["mute"]
        new_shape.name = old_shape["name"]
        new_shape.relative_key = old_shape["relative_key"]
        new_shape.slider_max = old_shape["slider_max"]
        new_shape.slider_min = old_shape["slider_min"]
        new_shape.value = old_shape["value"]
        new_shape.vertex_group = old_shape["vertex_group"]
    
    def bake(self, context):
        old_ob = bpy.context.active_object
        if self.properties.bake_selected:
            bake_meshes = [ob.name for ob in bpy.context.selected_objects if ob.type=="MESH"]
        else:
            bake_meshes = proportions_baker[:]
        for name in bake_meshes:
            if name in bpy.data.objects:
                ob = bpy.data.objects[name]
            else:
                continue
            bpy.context.scene.objects.active = ob
            
            # store shapekeys
            mesh = ob.data
            key = mesh.shape_keys
            if key:
                slurph = key.slurph
                use_relative = key.use_relative
                reference = key.reference_key.name
                data_reference = dict([[i, shapekeypoint.co.copy()] for i, shapekeypoint in enumerate(key.reference_key.data)])
                
                store_shapes = []
                shapes = key.key_blocks
                for shape in shapes:
                    cur_shape = {}
                    cur_shape["data"] = dict([[i, shapekeypoint.co - data_reference[i]] for i, shapekeypoint in enumerate(shape.data)])
                    cur_shape["interpolation"] = shape.interpolation
                    cur_shape["mute"] = shape.mute
                    cur_shape["name"] = shape.name
                    cur_shape["relative_key"] = shape.relative_key
                    cur_shape["slider_max"] = shape.slider_max
                    cur_shape["slider_min"] = shape.slider_min
                    cur_shape["value"] = shape.value
                    cur_shape["vertex_group"] = shape.vertex_group
                    store_shapes.append(cur_shape)
                
                # remove shapekeys
                for i in range(len(shapes) - 1, -1, -1):
                    ob.active_shape_key_index = i
                    bpy.ops.object.shape_key_remove()
            else:
                store_shapes = False
            
            # apply modifiers
            mods = []
            for i in range(len(ob.modifiers)):
                mod = ob.modifiers[i]
                if mod.type in ['ARMATURE', 'MESH_DEFORM']:
                    mods.append([mod, i])
            for data in mods:
                mod, i = data
                vg = mod.vertex_group
                invert = mod.invert_vertex_group
                name = mod.name
                bpy.ops.object.modifier_copy(modifier=mod.name)
                bpy.ops.object.modifier_apply(modifier=mod.name)
                new_mod = ob.modifiers[i]
                new_mod.name = name
                new_mod.vertex_group = vg
                new_mod.invert_vertex_group = invert
            
            # restore shapekeys
            if store_shapes:
                # base key
                bpy.ops.object.shape_key_add()
                key = mesh.shape_keys
                key.slurph = slurph
                key.use_relative = use_relative
                
                old_shape = [shape for shape in store_shapes if shape["name"] == reference][0]
                new_shape = key.key_blocks[0]
                self.restore_shape_settings(old_shape, new_shape)
                data_reference = dict([[vertex.index, vertex.co.copy()] for vertex in mesh.vertices])
                
                # other keys
                for old_shape in store_shapes:
                    if old_shape["name"] == reference:
                        continue
                    bpy.ops.object.shape_key_add()
                    new_shape = key.key_blocks[-1]
                    self.restore_shape_settings(old_shape, new_shape)
                    ob.active_shape_key_index = len(key.key_blocks) - 1
                    for i, shapekeypoint in enumerate(new_shape.data):
                        shapekeypoint.co = old_shape["data"][i] + data_reference[i]
        
        bpy.context.scene.objects.active = old_ob
    
    def invoke(self, context, event):
        self.bake(context)
        self.report({'INFO'}, "Baking done")
        return{'FINISHED'}
    
    def execute(self, context):
        self.bake(context)
        return{'FINISHED'}


# Armature Baker operator
class ARMATURE_OT_armature_baker(bpy.types.Operator):
    bl_label = "Armature Baker"
    bl_idname = "armature.armature_baker"
    bl_description = "Bake the current pose to the edit-mode armature"
    
    @classmethod
    def poll(cls, context):
        if not bpy.context.object:
            return False
        else:
            return (bpy.context.object.type == "ARMATURE")
    
    def bake(self, context):
        old_edit_matrices = {}
        old_pose_matrices = {}
        
        bpy.ops.object.mode_set(mode='EDIT')
        editbones = bpy.context.object.data.edit_bones
        for name in exclude_bones:
            b = editbones[name]
            old_edit_matrices[name] = [b.head[:], b.tail[:], b.roll]
        
        bpy.ops.object.mode_set(mode='POSE')
        posebones = bpy.context.object.pose.bones
        for name in exclude_bones:
            b = posebones[name]
            old_pose_matrices[name] = [b.location[:], b.rotation_quaternion.copy(), b.scale[:]]
        
        bpy.ops.pose.armature_apply()
        
        bpy.ops.object.mode_set(mode='EDIT')
        for name in exclude_bones:
            b = editbones[name]
            b.head, b.tail, b.roll = old_edit_matrices[name]
        
        bpy.ops.object.mode_set(mode='POSE')
        for name in exclude_bones:
            b = posebones[name]
            b.location, b.rotation_quaternion, b.scale = old_pose_matrices[name]
        
        arm = bpy.context.object.data
        bpy.ops.object.mode_set(mode='EDIT')
        old_active = arm.edit_bones.active.name
        old_layers = [i for i in arm.layers]
        arm.layers = [True]*32
        for b in posebones:
            for con in b.constraints:
                if con.type not in ['LIMIT_DISTANCE', 'STRETCH_TO', 'CHILD_OF']:
                    continue
                if con.type == 'LIMIT_DISTANCE':
                    con.distance = 0
                elif con.type == 'STRETCH_TO':
                    con.rest_length = 0
                elif con.type == 'CHILD_OF':
                    bpy.ops.object.mode_set(mode='EDIT')
                    arm.edit_bones.active = arm.edit_bones[b.name]
                    bpy.ops.object.mode_set(mode='POSE')
                    bpy.ops.constraint.childof_clear_inverse(constraint=con.name, owner='BONE')
                    bpy.ops.constraint.childof_set_inverse(constraint=con.name, owner='BONE')
                    # somehow it only works if you run it twice
                    bpy.ops.constraint.childof_set_inverse(constraint=con.name, owner='BONE')
                    bpy.ops.object.mode_set(mode='EDIT')
                    arm.edit_bones[b.name].select = False
        bpy.ops.object.mode_set(mode='EDIT')
        arm.edit_bones.active = arm.edit_bones[old_active]
        arm.layers = old_layers
        bpy.ops.object.mode_set(mode='POSE')

    def invoke(self, context, event):
        self.bake(context)
        self.report({'INFO'}, "Baking done")
        return{'FINISHED'}

    def execute(self, context):
        self.bake(context)
        return{'FINISHED'}


# Full Bake operator
class ARMATURE_OT_full_bake(bpy.types.Operator):
    bl_label = "Full Bake"
    bl_idname = "armature.full_bake"
    bl_description = "Full automatic proportion and armature baking"
    
    @classmethod
    def poll(cls, context):
        return bpy.context.active_object

    def invoke(self, context, event):
        if proportions_baker[0] not in bpy.data.objects:
            self.report({'ERROR'}, "Couldn't find zepam mesh, bake not started.")
            return{'CANCELLED'}
        
        # preparing scene
        bpy.ops.object.mode_set(mode='OBJECT')
        old_active = bpy.context.active_object
        old_selected = bpy.context.selected_objects
        old_layers = [i for i in bpy.context.scene.layers]
        for ob in old_selected:
            ob.select = False
        bpy.context.scene.objects.active = bpy.data.objects[proportions_baker[0]]

        # baking proportions
        bpy.ops.armature.proportions_baker(bake_selected=False)

        # unparenting
        parent_pairs = []
        for name in reparent:
            if name in bpy.data.objects:
                ob = bpy.data.objects[name]
            else:
                continue
            bpy.context.scene.layers = ob.layers
            bpy.context.scene.objects.active = ob
            ob.select = True
            parent_pairs.append([ob, ob.parent, ob.parent_bone])
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
            ob.select = False

        # baking armatures
        for name in armature_baker:
            if name in bpy.data.objects:
                ob = bpy.data.objects[name]
            else:
                continue
            bpy.context.scene.layers = ob.layers
            bpy.context.scene.objects.active = ob
            bpy.ops.armature.armature_baker()

        # re-parenting
        for pp in parent_pairs:
            ob, parent, bone = pp
            ob.parent = parent
            ob.parent_type = 'BONE'
            ob.parent_bone = bone

        # cleaning up        
        for ob in bpy.context.selected_objects:
            ob.select = False
        bpy.context.scene.layers = old_layers
        bpy.context.scene.objects.active = old_active
        for ob in old_selected:
            ob.select = True
        
        self.report({'INFO'}, "Baking done")
        return{'FINISHED'}


class ARMATURE_OT_reset_constraints(bpy.types.Operator):
    bl_label = "Reset Constraints"
    bl_idname = "armature.reset_constraints"
    bl_description = "Reset all posebone constraints"
    
    @classmethod
    def poll(cls, context):
        if not bpy.context.object:
            return False
        else:
            return (bpy.context.object.type=='ARMATURE' and \
                context.mode=='POSE')
    
    def invoke(self, context, event):
        pbones = context.active_object.pose.bones
        if len(pbones) < 1:
            self.report({'INFO'}, "No bones found")
            return{'FINISHED'}
        
        amount = 0
        for pbone in pbones:
            for con in pbone.constraints:
                if con.type == 'LIMIT_DISTANCE':
                    amount += 1
                    con.distance = 0
                elif con.type == 'STRETCH_TO':
                    amount += 1
                    con.rest_length = 0
        self.report({'INFO'}, str(amount) + " constraints reset")
        
        return{'FINISHED'}


######### SNAPPING OPERATORS #############################################

##### TORSO #####

class Operator_Torso_Snap_FK_IK(bpy.types.Operator):    
    
    bl_idname = "torso_snap.fk_ik"     
    bl_label = "BlenRig Torso Snap FK IK"      
    
    def execute(self, context):  
        arm_data = bpy.context.active_object.data
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
        arm_data.layers[10] = True
        arm_data.layers[0] = True
        arm_data.layers[1] = True                      
        Bone1 = arm.pose.bones['spine_1']
        Bone2 = arm.pose.bones['spine_ik_1']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        Bone1 = arm.pose.bones['spine_2']
        Bone2 = arm.pose.bones['spine_ik_2']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        Bone1 = arm.pose.bones['spine_3']
        Bone2 = arm.pose.bones['spine_ik_3']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()    
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['spine_1', 'spine_2', 'spine_3', 'torso_ctrl_fk']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
                arm_data.bones['spine_1'].layers[0] = True
                arm_data.bones['spine_2'].layers[0] = True
                arm_data.bones['spine_3'].layers[0] = True      
                arm_data.bones['torso_ctrl_fk'].layers[0] = True                 
            
            
        arm_data.layers[10] = False        
               
        return {"FINISHED"}            

class Operator_Torso_Snap_IK_FK(bpy.types.Operator):    
    
    bl_idname = "torso_snap.ik_fk"     
    bl_label = "BlenRig Torso Snap IK FK"      
    
    def execute(self, context):  
        arm_data = bpy.context.active_object.data
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
        arm_data.layers[10] = True
        arm_data.layers[0] = True
        arm_data.layers[1] = True     
        Bone1 = arm.pose.bones['torso_ctrl']
        Bone2 = arm.pose.bones['torso_fk_pivot']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1     
        bpy.ops.pose.copy_pose_vis_loc()        
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0

        Bone1 = arm.pose.bones['spine_ctrl_4']
        Bone2 = arm.pose.bones['neck_1']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()
        Bone1.bone.select = 0
        Bone2.bone.select = 0        
        
        Bone1 = arm.pose.bones['spine_ctrl_3']
        Bone2 = arm.pose.bones['spine_3']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()   
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        Bone1 = arm.pose.bones['spine_ctrl_2']
        Bone2 = arm.pose.bones['spine_2']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()    
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['spine_ctrl_2', 'spine_ctrl_3', 'spine_ctrl_4', 'torso_ctrl']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
                arm_data.bones['spine_ctrl_2'].layers[1] = True
                arm_data.bones['spine_ctrl_3'].layers[1] = True
                arm_data.bones['spine_ctrl_4'].layers[1] = True
                arm_data.bones['torso_ctrl'].layers[0] = True                
            
            
        arm_data.layers[10] = False        
               
        return {"FINISHED"}      

class Operator_Torso_Snap_UP_INV(bpy.types.Operator):    
    
    bl_idname = "torso_snap.up_inv"     
    bl_label = "BlenRig Torso Snap UP INV"      
    
    def execute(self, context):  
        arm_data = bpy.context.active_object.data
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
        arm_data.layers[10] = True
        arm_data.layers[0] = True
        arm_data.layers[1] = True            
        Bone1 = arm.pose.bones['pelvis_ctrl']
        Bone2 = arm.pose.bones['pelvis_ctrl_inv']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()        
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0

        Bone1 = arm.pose.bones['spine_1']
        Bone2 = arm.pose.bones['spine_1_inv_rot']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()        
        Bone1.bone.select = 0
        Bone2.bone.select = 0        
        
        Bone1 = arm.pose.bones['spine_2']
        Bone2 = arm.pose.bones['spine_2_inv_rot']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()           
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        Bone1 = arm.pose.bones['spine_3']
        Bone2 = arm.pose.bones['spine_3_inv']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()    
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        bpy.ops.torso_snap.ik_fk()
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['pelvis_ctrl', 'spine_1', 'spine_2', 'spine_3','spine_ctrl_2', 'spine_ctrl_3', 'spine_ctrl_4', 'torso_ctrl']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
                ob = bpy.context.active_object
                cust_prop = ob.items()
                for prop in cust_prop:
                    if prop[0] == 'ik_torso' and prop[1] == 0.0:                        
                        arm_data.bones['pelvis_ctrl'].layers[0] = True
                        arm_data.bones['spine_ctrl_2'].layers[1] = True
                        arm_data.bones['spine_ctrl_3'].layers[1] = True
                        arm_data.bones['spine_ctrl_4'].layers[1] = True
                        arm_data.bones['torso_ctrl'].layers[0] = True
                        arm_data.bones['pelvis_ctrl'].layers[0] = True
                        arm_data.bones['spine_1'].layers[0] = False
                        arm_data.bones['spine_2'].layers[0] = False
                        arm_data.bones['spine_3'].layers[0] = False                       
                    elif prop[0] == 'ik_torso' and prop[1] == 1.0:                          
                        arm_data.bones['pelvis_ctrl'].layers[0] = True
                        arm_data.bones['spine_1'].layers[0] = True
                        arm_data.bones['spine_2'].layers[0] = True
                        arm_data.bones['spine_3'].layers[0] = True
                        arm_data.bones['spine_ctrl_2'].layers[1] = False
                        arm_data.bones['spine_ctrl_3'].layers[1] = False
                        arm_data.bones['spine_ctrl_4'].layers[1] = False
                        arm_data.bones['torso_ctrl'].layers[0] = False                    
            
            
        arm_data.layers[10] = False        
               
        return {"FINISHED"}   

class Operator_Torso_Snap_INV_UP(bpy.types.Operator):    
    
    bl_idname = "torso_snap.inv_up"     
    bl_label = "BlenRig Torso Snap INV UP"      
    
    def execute(self, context):  
        arm_data = bpy.context.active_object.data
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
        arm_data.layers[10] = True
        arm_data.layers[0] = True
        arm_data.layers[1] = True        
        Bone1 = arm.pose.bones['torso_ctrl_inv']
        Bone2 = arm.pose.bones['torso_ctrl_inv_loc']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()  
        bpy.ops.pose.copy_pose_vis_rot()               
        Bone1.bone.select = 0
        Bone2.bone.select = 0                
        
        Bone1 = arm.pose.bones['spine_3_inv']
        Bone2 = arm.pose.bones['spine_3']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()        
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        Bone1 = arm.pose.bones['spine_2_inv']
        Bone2 = arm.pose.bones['spine_2_rot_inv']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        Bone1 = arm.pose.bones['spine_1_inv']
        Bone2 = arm.pose.bones['spine_1_rot_inv']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()    
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        Bone1 = arm.pose.bones['pelvis_inv']
        Bone2 = arm.pose.bones['pelvis']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()    
        Bone1.bone.select = 0
        Bone2.bone.select = 0        
        
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['pelvis_inv', 'spine_1_inv', 'spine_2_inv', 'spine_3_inv']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
            if (Bones.name in select_bones):
                Bones.bone.select = 1
                arm_data.bones['pelvis_inv'].layers[0] = True
                arm_data.bones['spine_1_inv'].layers[0] = True
                arm_data.bones['spine_2_inv'].layers[0] = True
                arm_data.bones['spine_3_inv'].layers[0] = True                  
            
            
        arm_data.layers[10] = False        
               
        return {"FINISHED"}   

##### HEAD #####
    

class Operator_Head_Snap_FK_IK(bpy.types.Operator):    
    
    bl_idname = "head_snap.fk_ik"     
    bl_label = "BlenRig Head Snap FK IK"      
    
    def execute(self, context):  
        arm_data = bpy.context.active_object.data
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
        arm_data.layers[10] = True
        arm_data.layers[0] = True
        arm_data.layers[1] = True     
        Bone1 = arm.pose.bones['neck_1']
        Bone2 = arm.pose.bones['neck_ik_1']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        Bone1 = arm.pose.bones['neck_2']
        Bone2 = arm.pose.bones['neck_ik_2']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        Bone1 = arm.pose.bones['neck_3']
        Bone2 = arm.pose.bones['neck_ik_3']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()    
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        Bone1 = arm.pose.bones['head']
        Bone2 = arm.pose.bones['head_ctrl']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()    
        Bone1.bone.select = 0
        Bone2.bone.select = 0        
        
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['neck_1', 'neck_2', 'neck_3', 'head']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
                arm_data.bones['neck_1'].layers[0] = True
                arm_data.bones['neck_2'].layers[0] = True
                arm_data.bones['neck_3'].layers[0] = True
                arm_data.bones['head'].layers[0] = True                 
            
            
        arm_data.layers[10] = False        
               
        return {"FINISHED"} 

class Operator_Head_Snap_IK_FK(bpy.types.Operator):    
    
    bl_idname = "head_snap.ik_fk"     
    bl_label = "BlenRig Head Snap IK FK"      
    
    def execute(self, context):  
        arm_data = bpy.context.active_object.data
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
        arm_data.layers[10] = True
        arm_data.layers[0] = True
        arm_data.layers[1] = True        
        Bone1 = arm.pose.bones['neck_ctrl']
        Bone2 = arm.pose.bones['neck_fk_pivot']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0

        Bone1 = arm.pose.bones['head_ctrl']
        Bone2 = arm.pose.bones['head']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()
        bpy.ops.pose.copy_pose_vis_rot()        
        Bone1.bone.select = 0
        Bone2.bone.select = 0        
        
        Bone1 = arm.pose.bones['neck_ctrl_3']
        Bone2 = arm.pose.bones['neck_3']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()   
        bpy.ops.pose.copy_pose_vis_rot()           
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        Bone1 = arm.pose.bones['neck_ctrl_2']
        Bone2 = arm.pose.bones['neck_2']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()    
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['neck_ctrl', 'head_ctrl', 'neck_ctrl_3', 'neck_ctrl_2']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
                arm_data.bones['head_ctrl'].layers[0] = True
                arm_data.bones['neck_ctrl_3'].layers[1] = True
                arm_data.bones['neck_ctrl_2'].layers[1] = True          
                arm_data.bones['neck_ctrl'].layers[1] = True                             
            
            
        arm_data.layers[10] = False        
               
        return {"FINISHED"}      


##### ARM L #####


class Operator_Arm_L_Snap_FK_IK(bpy.types.Operator):    
    
    bl_idname = "arm_l_snap.fk_ik"     
    bl_label = "BlenRig Hand L Snap FK IK"      
    
    def execute(self, context):  
        arm_data = bpy.context.active_object.data
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
        arm_data.layers[10] = True
        arm_data.layers[0] = True
        arm_data.layers[1] = True          
        Bone1 = arm.pose.bones['arm_L']
        Bone2 = arm.pose.bones['arm_ik_L']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        Bone1 = arm.pose.bones['forearm_L']
        Bone2 = arm.pose.bones['forearm_ik_L']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0

        ob = bpy.context.active_object
        cust_prop = ob.items()
        for prop in cust_prop:
            if prop[0] == 'hinge_hand_L' and prop[1] == 1.0: 
                Bone1 = arm.pose.bones['hand_fk_L']
                Bone2 = arm.pose.bones['hand_ik_L']
                #set Bone2 as active
                arm.data.bones.active = Bone2.bone
                Bone1.bone.select = 1
                bpy.ops.pose.copy_pose_vis_rot()    
                Bone1.bone.select = 0
                Bone2.bone.select = 0 
        
#        Bone1 = arm.pose.bones['palm_bend_fk_ctrl_L']
#        Bone2 = arm.pose.bones['palm_bend_ik_L']
#        #set Bone2 as active
#        arm.data.bones.active = Bone2.bone
#        Bone1.bone.select = 1
#        bpy.ops.pose.copy_pose_vis_rot()    
#        Bone1.bone.select = 0
#        Bone2.bone.select = 0         
        
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['arm_L', 'forearm_L', 'hand_fk_L']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
                arm_data.bones['arm_L'].layers[0] = True
                arm_data.bones['forearm_L'].layers[0] = True       
                ob = bpy.context.active_object
                cust_prop = ob.items()
                for prop in cust_prop:
                    if prop[0] == 'hinge_hand_L' and prop[1] == 0.0:                        
                        arm_data.bones['hand_fk_L'].layers[0] = True                                                     
            
        arm_data.layers[10] = False        
               
        return {"FINISHED"} 


class Operator_Arm_L_Snap_IK_FK(bpy.types.Operator):    
    
    bl_idname = "arm_l_snap.ik_fk"     
    bl_label = "BlenRig Hand L Snap IK FK"      
    
    def execute(self, context):  
        arm_data = bpy.context.active_object.data
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
        arm_data.layers[10] = True
        arm_data.layers[0] = True
        arm_data.layers[1] = True         
        Bone1 = arm.pose.bones['hand_ik_L']
        Bone2 = arm.pose.bones['hand_fk_L']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()        
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
#        Bone1 = arm.pose.bones['palm_bend_ik_ctrl_L']
#        Bone2 = arm.pose.bones['palm_bend_fk_L']
#        #set Bone2 as active
#        arm.data.bones.active = Bone2.bone
#        Bone1.bone.select = 1
#        bpy.ops.pose.copy_pose_vis_rot()
#        Bone1.bone.select = 0
#        Bone2.bone.select = 0        
        
        Bone1 = arm.pose.bones['elbow_L']
        Bone2 = arm.pose.bones['elbow_fk_L']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['hand_ik_L', 'elbow_L']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
                arm_data.bones['elbow_L'].layers[0] = True
                arm_data.bones['elbow_line_L'].layers[0] = True
                arm_data.bones['hand_ik_L'].layers[0] = True                     
                     
        arm_data.layers[10] = False        
               
        return {"FINISHED"} 

##### ARM R #####


class Operator_Arm_R_Snap_FK_IK(bpy.types.Operator):    
    
    bl_idname = "arm_r_snap.fk_ik"     
    bl_label = "BlenRig Hand R Snap FK IK"      
    
    def execute(self, context):  
        arm_data = bpy.context.active_object.data
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
        arm_data.layers[10] = True
        arm_data.layers[0] = True
        arm_data.layers[1] = True          
        Bone1 = arm.pose.bones['arm_R']
        Bone2 = arm.pose.bones['arm_ik_R']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        Bone1 = arm.pose.bones['forearm_R']
        Bone2 = arm.pose.bones['forearm_ik_R']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        ob = bpy.context.active_object
        cust_prop = ob.items()
        for prop in cust_prop:
            if prop[0] == 'hinge_hand_R' and prop[1] == 1.0: 
                Bone1 = arm.pose.bones['hand_fk_R']
                Bone2 = arm.pose.bones['hand_ik_R']
                #set Bone2 as active
                arm.data.bones.active = Bone2.bone
                Bone1.bone.select = 1
                bpy.ops.pose.copy_pose_vis_rot()    
                Bone1.bone.select = 0
                Bone2.bone.select = 0 
        
#        Bone1 = arm.pose.bones['palm_bend_fk_ctrl_R']
#        Bone2 = arm.pose.bones['palm_bend_ik_R']
#        #set Bone2 as active
#        arm.data.bones.active = Bone2.bone
#        Bone1.bone.select = 1
#        bpy.ops.pose.copy_pose_vis_rot()    
#        Bone1.bone.select = 0
#        Bone2.bone.select = 0            
        
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['arm_R', 'forearm_R', 'hand_fk_R']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
                arm_data.bones['arm_R'].layers[0] = True
                arm_data.bones['forearm_R'].layers[0] = True       
                ob = bpy.context.active_object
                cust_prop = ob.items()
                for prop in cust_prop:
                    if prop[0] == 'hinge_hand_R' and prop[1] == 0.0:                        
                        arm_data.bones['hand_fk_R'].layers[0] = True                      
            
            
        arm_data.layers[10] = False        
               
        return {"FINISHED"} 


class Operator_Arm_R_Snap_IK_FK(bpy.types.Operator):    
    
    bl_idname = "arm_r_snap.ik_fk"     
    bl_label = "BlenRig Hand R Snap IK FK"      
    
    def execute(self, context):  
        arm_data = bpy.context.active_object.data
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
        arm_data.layers[10] = True
        arm_data.layers[0] = True
        arm_data.layers[1] = True         
        Bone1 = arm.pose.bones['hand_ik_R']
        Bone2 = arm.pose.bones['hand_fk_R']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()        
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
#        Bone1 = arm.pose.bones['palm_bend_ik_ctrl_R']
#        Bone2 = arm.pose.bones['palm_bend_fk_R']
#        #set Bone2 as active
#        arm.data.bones.active = Bone2.bone
#        Bone1.bone.select = 1
#        bpy.ops.pose.copy_pose_vis_rot()
#        Bone1.bone.select = 0
#        Bone2.bone.select = 0       
        
        Bone1 = arm.pose.bones['elbow_R']
        Bone2 = arm.pose.bones['elbow_fk_R']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['hand_ik_R', 'elbow_R']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
                arm_data.bones['elbow_R'].layers[0] = True
                arm_data.bones['elbow_line_R'].layers[0] = True
                arm_data.bones['hand_ik_R'].layers[0] = True                 
            
            
        arm_data.layers[10] = False        
               
        return {"FINISHED"} 

##### LEG L #####


class Operator_Leg_L_Snap_FK_IK(bpy.types.Operator):    
    
    bl_idname = "leg_l_snap.fk_ik"     
    bl_label = "BlenRig Leg L Snap FK IK"      
    
    def execute(self, context):  
        arm_data = bpy.context.active_object.data
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
        arm_data.layers[10] = True
        arm_data.layers[0] = True
        arm_data.layers[1] = True      
        Bone1 = arm.pose.bones['thigh_L']
        Bone2 = arm.pose.bones['thigh_ik_L']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        Bone1 = arm.pose.bones['calf_L']
        Bone2 = arm.pose.bones['calf_ik_L']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        Bone1 = arm.pose.bones['foot_L']
        Bone2 = arm.pose.bones['foot_ik_L']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()    
        Bone1.bone.select = 0
        Bone2.bone.select = 0 

        Bone1 = arm.pose.bones['toe_1_L']
        Bone2 = arm.pose.bones['toe_1_ik_L']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()    
        Bone1.bone.select = 0
        Bone2.bone.select = 0  
    
        Bone1 = arm.pose.bones['toe_2_L']
        Bone2 = arm.pose.bones['toe_2_ik_L']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()    
        Bone1.bone.select = 0
        Bone2.bone.select = 0                  
       
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['thigh_L', 'calf_L', 'foot_L', 'toe_1_L', 'toe_2_L']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
                arm_data.bones['thigh_L'].layers[0] = True
                arm_data.bones['calf_L'].layers[0] = True
                arm_data.bones['foot_L'].layers[0] = True      
                arm_data.bones['toe_1_L'].layers[0] = True     
                arm_data.bones['toe_2_L'].layers[0] = True                                           
            
            
        arm_data.layers[10] = False        
               
        return {"FINISHED"} 


class Operator_Leg_L_Snap_IK_FK(bpy.types.Operator):    
    
    bl_idname = "leg_l_snap.ik_fk"     
    bl_label = "BlenRig Leg L Snap IK FK"      
    
    def execute(self, context):  
        arm_data = bpy.context.active_object.data
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
        arm_data.layers[10] = True
        arm_data.layers[0] = True
        arm_data.layers[1] = True        
        Bone1 = arm.pose.bones['sole_ctrl_L']
        Bone2 = arm.pose.bones['sole_ctrl_fk_L']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()        
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0
                
        Bone1 = arm.pose.bones['foot_ik_ctrl_L']
        Bone2 = arm.pose.bones['foot_L']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()
        bpy.ops.pose.copy_pose_vis_rot()        
        Bone1.bone.select = 0
        Bone2.bone.select = 0          
                
        Bone1 = arm.pose.bones['toes_ctrl_L']
        Bone2 = arm.pose.bones['toes_ctrl_fk_L']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()
        bpy.ops.pose.copy_pose_vis_rot()        
        Bone1.bone.select = 0
        Bone2.bone.select = 0  
        
        Bone1 = arm.pose.bones['toes_ctrl_mid_L']
        Bone2 = arm.pose.bones['toes_ctrl_mid_fk_L']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()
        bpy.ops.pose.copy_pose_vis_rot()        
        Bone1.bone.select = 0
        Bone2.bone.select = 0               
        
        Bone1 = arm.pose.bones['knee_L']
        Bone2 = arm.pose.bones['knee_fk_L']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()
        Bone1.bone.select = 0
        Bone2.bone.select = 0        
        
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['sole_ctrl_L', 'knee_L', 'toes_ctrl_L', 'toes_ctrl_mid_L', 'foot_ik_ctrl_L']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
                arm_data.bones['sole_ctrl_L'].layers[0] = True
                arm_data.bones['knee_L'].layers[0] = True
                arm_data.bones['knee_line_L'].layers[0] = True
                arm_data.bones['foot_ik_ctrl_L'].layers[0] = True    
                arm_data.bones['sole_pivot_point_L'].layers[0] = True
                arm_data.bones['foot_roll_ctrl_L'].layers[0] = True
                arm_data.bones['calf_ik_L'].layers[1] = True        
                arm_data.bones['toes_ctrl_L'].layers[0] = True
                arm_data.bones['toes_ctrl_mid_L'].layers[0] = True                                             
            
            
        arm_data.layers[10] = False        
               
        return {"FINISHED"} 


##### LEG R #####


class Operator_Leg_R_Snap_FK_IK(bpy.types.Operator):    
    
    bl_idname = "leg_r_snap.fk_ik"     
    bl_label = "BlenRig Leg R Snap FK IK"      
    
    def execute(self, context):  
        arm_data = bpy.context.active_object.data
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
        arm_data.layers[10] = True
        arm_data.layers[0] = True
        arm_data.layers[1] = True      
        Bone1 = arm.pose.bones['thigh_R']
        Bone2 = arm.pose.bones['thigh_ik_R']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        Bone1 = arm.pose.bones['calf_R']
        Bone2 = arm.pose.bones['calf_ik_R']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0
        
        Bone1 = arm.pose.bones['foot_R']
        Bone2 = arm.pose.bones['foot_ik_R']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()    
        Bone1.bone.select = 0
        Bone2.bone.select = 0 

        Bone1 = arm.pose.bones['toe_1_R']
        Bone2 = arm.pose.bones['toe_1_ik_R']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()    
        Bone1.bone.select = 0
        Bone2.bone.select = 0  
    
        Bone1 = arm.pose.bones['toe_2_R']
        Bone2 = arm.pose.bones['toe_2_ik_R']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_rot()    
        Bone1.bone.select = 0
        Bone2.bone.select = 0           
        
        
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['thigh_R', 'calf_R', 'foot_R', 'toe_1_R', 'toe_2_R']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
                arm_data.bones['thigh_R'].layers[0] = True
                arm_data.bones['calf_R'].layers[0] = True
                arm_data.bones['foot_R'].layers[0] = True      
                arm_data.bones['toe_1_R'].layers[0] = True     
                arm_data.bones['toe_2_R'].layers[0] = True                   
            
            
        arm_data.layers[10] = False        
               
        return {"FINISHED"} 


class Operator_Leg_R_Snap_IK_FK(bpy.types.Operator):    
    
    bl_idname = "leg_r_snap.ik_fk"     
    bl_label = "BlenRig Leg R Snap IK FK"      
    
    def execute(self, context):  
        arm_data = bpy.context.active_object.data
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
        arm_data.layers[10] = True
        arm_data.layers[0] = True
        arm_data.layers[1] = True    
        Bone1 = arm.pose.bones['sole_ctrl_R']
        Bone2 = arm.pose.bones['sole_ctrl_fk_R']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()        
        bpy.ops.pose.copy_pose_vis_rot()
        Bone1.bone.select = 0
        Bone2.bone.select = 0
                
        Bone1 = arm.pose.bones['foot_ik_ctrl_R']
        Bone2 = arm.pose.bones['foot_R']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()
        bpy.ops.pose.copy_pose_vis_rot()        
        Bone1.bone.select = 0
        Bone2.bone.select = 0          
                
        Bone1 = arm.pose.bones['toes_ctrl_R']
        Bone2 = arm.pose.bones['toes_ctrl_fk_R']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()
        bpy.ops.pose.copy_pose_vis_rot()        
        Bone1.bone.select = 0
        Bone2.bone.select = 0   
        
        Bone1 = arm.pose.bones['toes_ctrl_mid_R']
        Bone2 = arm.pose.bones['toes_ctrl_mid_fk_R']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()
        bpy.ops.pose.copy_pose_vis_rot()        
        Bone1.bone.select = 0
        Bone2.bone.select = 0                
        
        Bone1 = arm.pose.bones['knee_R']
        Bone2 = arm.pose.bones['knee_fk_R']
        #set Bone2 as active
        arm.data.bones.active = Bone2.bone
        Bone1.bone.select = 1
        bpy.ops.pose.copy_pose_vis_loc()
        Bone1.bone.select = 0
        Bone2.bone.select = 0        
        
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['sole_ctrl_R', 'knee_R', 'toes_ctrl_R', 'toes_ctrl_mid_R', 'foot_ik_ctrl_R']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
                arm_data.bones['sole_ctrl_R'].layers[0] = True
                arm_data.bones['knee_R'].layers[0] = True
                arm_data.bones['knee_line_R'].layers[0] = True
                arm_data.bones['foot_ik_ctrl_R'].layers[0] = True    
                arm_data.bones['sole_pivot_point_R'].layers[0] = True
                arm_data.bones['foot_roll_ctrl_R'].layers[0] = True
                arm_data.bones['calf_ik_R'].layers[1] = True        
                arm_data.bones['toes_ctrl_R'].layers[0] = True
                arm_data.bones['toes_ctrl_mid_R'].layers[0] = True               
            
        arm_data.layers[10] = False        
               
        return {"FINISHED"} 

################# SELECTION OPERATORS #############################################

class Operator_Torso_FK_Select(bpy.types.Operator):    
    
    bl_idname = "torso.fk_select"     
    bl_label = "BlenRig Torso FK Select"      
    
    def execute(self, context):  
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['spine_1', 'spine_2', 'spine_3', 'torso_ctrl_fk']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
        return {"FINISHED"}       
    
class Operator_Torso_IK_Select(bpy.types.Operator):    
    
    bl_idname = "torso.ik_select"     
    bl_label = "BlenRig Torso IK Select"       
    
    def execute(self, context):  
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['spine_ctrl_2', 'spine_ctrl_3', 'spine_ctrl_4', 'torso_ctrl']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
        return {"FINISHED"}                   

class Operator_Torso_INV_Select(bpy.types.Operator):    
    
    bl_idname = "torso.inv_select"     
    bl_label = "BlenRig Torso INV Select"       
    
    def execute(self, context):  
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['pelvis_inv', 'spine_1_inv', 'spine_2_inv', 'spine_3_inv', 'torso_ctrl_inv', 'pelvis_ctrl_fk_inv']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
        return {"FINISHED"}  
    
class Operator_Head_FK_Select(bpy.types.Operator):    
    
    bl_idname = "head.fk_select"     
    bl_label = "BlenRig Head FK Select"      
    
    def execute(self, context):  
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['neck_1', 'neck_2', 'neck_3', 'head', 'head_ctrl_fk']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
        return {"FINISHED"}       
    
class Operator_Head_IK_Select(bpy.types.Operator):    
    
    bl_idname = "head.ik_select"     
    bl_label = "BlenRig Head IK Select"       
    
    def execute(self, context):  
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['neck_ctrl', 'head_ctrl', 'neck_ctrl_3', 'neck_ctrl_2']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
        return {"FINISHED"}          

class Operator_Arm_L_FK_Select(bpy.types.Operator):    
    
    bl_idname = "arm_l.fk_select"     
    bl_label = "BlenRig Arm L FK Select"       
    
    def execute(self, context):  
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['arm_L', 'forearm_L', 'hand_fk_L']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
        return {"FINISHED"}   
    
class Operator_Arm_L_IK_Select(bpy.types.Operator):    
    
    bl_idname = "arm_l.ik_select"     
    bl_label = "BlenRig Arm L IK Select"       
    
    def execute(self, context):  
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['hand_ik_L', 'elbow_L']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
        return {"FINISHED"}  
    
class Operator_Arm_R_FK_Select(bpy.types.Operator):    
    
    bl_idname = "arm_r.fk_select"     
    bl_label = "BlenRig Arm R FK Select"       
    
    def execute(self, context):  
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['arm_R', 'forearm_R', 'hand_fk_R']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
        return {"FINISHED"}   
    
class Operator_Arm_R_IK_Select(bpy.types.Operator):    
    
    bl_idname = "arm_r.ik_select"     
    bl_label = "BlenRig Arm R IK Select"       
    
    def execute(self, context):  
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['hand_ik_R', 'elbow_R']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
        return {"FINISHED"}          

class Operator_Leg_L_FK_Select(bpy.types.Operator):    
    
    bl_idname = "leg_l.fk_select"     
    bl_label = "BlenRig Leg L FK Select"       
    
    def execute(self, context):  
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['thigh_L', 'calf_L', 'foot_L', 'toe_1_L', 'toe_2_L']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
        return {"FINISHED"}   
    
class Operator_Leg_L_IK_Select(bpy.types.Operator):    
    
    bl_idname = "leg_l.ik_select"     
    bl_label = "BlenRig Leg L IK Select"       
    
    def execute(self, context):  
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['sole_ctrl_L', 'knee_L', 'toes_ctrl_L', 'foot_ik_ctrl_L', 'toes_ctrl_mid_L']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
        return {"FINISHED"}  

class Operator_Leg_R_FK_Select(bpy.types.Operator):    
    
    bl_idname = "leg_r.fk_select"     
    bl_label = "BlenRig Leg R FK Select"       
    
    def execute(self, context):  
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['thigh_R', 'calf_R', 'foot_R', 'toe_1_R', 'toe_2_R']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
        return {"FINISHED"}   
    
class Operator_Leg_R_IK_Select(bpy.types.Operator):    
    
    bl_idname = "leg_r.ik_select"     
    bl_label = "BlenRig Leg R IK Select"       
    
    def execute(self, context):  
        arm = bpy.context.object
        for Bones in arm.pose.bones:
            Bones.bone.select = 0
            select_bones = ['sole_ctrl_R', 'knee_R', 'toes_ctrl_R', 'foot_ik_ctrl_R', 'toes_ctrl_mid_R']
            if (Bones.name in select_bones):
                Bones.bone.select = 1
        return {"FINISHED"}  


# function to drive the meta-sliders
def update_meta(self, context, group):
    arm = context.active_object
    props = context.window_manager.blenrig_props
    
    if group == 'ik':
        meta_value = props.ik_meta
        sliders = ["ik_meta_old", "ik_arm_L", "ik_arm_R", "ik_leg_L", "ik_foot_L",
            "ik_leg_R", "ik_foot_R", "ik_torso", "ik_head"]
    elif group == 'hinge_fing_L':
        meta_value = props.hinge_fing_L_meta
        sliders = ["hinge_fing_meta_old_L", "hinge_fing_ind_L", "hinge_fing_ind_L",
            "hinge_fing_mid_L", "hinge_fing_ring_L", "hinge_fing_lit_L",
            "hinge_fing_thumb_L"]
    elif group == 'hinge_fing_R':
        meta_value = props.hinge_fing_R_meta
        sliders = ["hinge_fing_meta_old_R", "hinge_fing_ind_R", "hinge_fing_ind_R",
        "hinge_fing_mid_R", "hinge_fing_ring_R", "hinge_fing_lit_R",
        "hinge_fing_thumb_R"]
    elif group == 'str':
        meta_value = props.str_meta
        sliders = ["str_meta_old", "str_head", "str_torso", "str_arm_L",
            "str_hand_L", "str_arm_R", "str_hand_R", "str_leg_L", "str_foot_L",
            "str_leg_R", "str_foot_R"]
    
    for slider in sliders:
        arm[slider] = meta_value


# Needed for property registration
class BlenrigProps(bpy.types.PropertyGroup):
    gui_ik_all = bpy.props.BoolProperty(default=False, description="Display all, regardless of selection in the 3d-view")
    gui_hinge_all = bpy.props.BoolProperty(default=False, description="Display all, regardless of selection in the 3d-view")
    gui_stretch_all = bpy.props.BoolProperty(default=False, description="Display all, regardless of selection in the 3d-view")
    
    i = 1 # used for lambda-trick, to pass argument to update function
    j = 2 # used for lambda-trick, to pass argument to update function
    ik_meta = bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0, precision=3, update=lambda i,j = i: update_meta(False, bpy.context, group='ik'))
    hinge_fing_L_meta = bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0, precision=3, update=lambda i,j = i: update_meta(False, bpy.context, group='hinge_fing_L'))
    hinge_fing_R_meta = bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0, precision=3, update=lambda i,j = i: update_meta(False, bpy.context, group='hinge_fing_R'))
    str_meta = bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0, precision=3, update=lambda i,j = i: update_meta(False, bpy.context, group='str'))


classes = [ARMATURE_OT_reset_constraints,
    ARMATURE_OT_full_bake,
    ARMATURE_OT_armature_baker,
    ARMATURE_OT_proportions_baker,
    ARMATURE_OT_scale_inherit,
    ARMATURE_OT_blenrig_gui,
    BlenRigInterface,
    BlenrigProps
    ]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.WindowManager.blenrig_props = bpy.props.PointerProperty(type = BlenrigProps)
    bpy.utils.register_class(Operator_Torso_Snap_FK_IK)
    bpy.utils.register_class(Operator_Torso_Snap_IK_FK) 
    bpy.utils.register_class(Operator_Head_Snap_FK_IK)  
    bpy.utils.register_class(Operator_Head_Snap_IK_FK)    
    bpy.utils.register_class(Operator_Torso_Snap_UP_INV)            
    bpy.utils.register_class(Operator_Torso_Snap_INV_UP)  
    bpy.utils.register_class(Operator_Arm_L_Snap_FK_IK)     
    bpy.utils.register_class(Operator_Arm_L_Snap_IK_FK)   
    bpy.utils.register_class(Operator_Arm_R_Snap_FK_IK)     
    bpy.utils.register_class(Operator_Arm_R_Snap_IK_FK)   
    bpy.utils.register_class(Operator_Leg_L_Snap_FK_IK)  
    bpy.utils.register_class(Operator_Leg_L_Snap_IK_FK)
    bpy.utils.register_class(Operator_Leg_R_Snap_FK_IK)  
    bpy.utils.register_class(Operator_Leg_R_Snap_IK_FK)   
    bpy.utils.register_class(Operator_Torso_FK_Select)    
    bpy.utils.register_class(Operator_Torso_IK_Select)        
    bpy.utils.register_class(Operator_Torso_INV_Select)  
    bpy.utils.register_class(Operator_Head_FK_Select)  
    bpy.utils.register_class(Operator_Head_IK_Select)  
    bpy.utils.register_class(Operator_Arm_L_FK_Select)  
    bpy.utils.register_class(Operator_Arm_L_IK_Select)  
    bpy.utils.register_class(Operator_Arm_R_FK_Select)  
    bpy.utils.register_class(Operator_Arm_R_IK_Select)  
    bpy.utils.register_class(Operator_Leg_L_FK_Select)  
    bpy.utils.register_class(Operator_Leg_L_IK_Select)  
    bpy.utils.register_class(Operator_Leg_R_FK_Select)     
    bpy.utils.register_class(Operator_Leg_R_IK_Select)                                     

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    bpy.utils.register_class(Operator_Torso_Snap_FK_IK)
    bpy.utils.register_class(Operator_Torso_Snap_IK_FK) 
    bpy.utils.register_class(Operator_Head_Snap_FK_IK)  
    bpy.utils.register_class(Operator_Head_Snap_IK_FK)    
    bpy.utils.register_class(Operator_Torso_Snap_UP_INV)            
    bpy.utils.register_class(Operator_Torso_Snap_INV_UP)  
    bpy.utils.register_class(Operator_Arm_L_Snap_FK_IK)     
    bpy.utils.register_class(Operator_Arm_L_Snap_IK_FK)   
    bpy.utils.register_class(Operator_Arm_R_Snap_FK_IK)     
    bpy.utils.register_class(Operator_Arm_R_Snap_IK_FK)   
    bpy.utils.register_class(Operator_Leg_L_Snap_FK_IK)  
    bpy.utils.register_class(Operator_Leg_L_Snap_IK_FK)
    bpy.utils.register_class(Operator_Leg_R_Snap_FK_IK)  
    bpy.utils.register_class(Operator_Leg_R_Snap_IK_FK)   
    bpy.utils.register_class(Operator_Torso_FK_Select)    
    bpy.utils.register_class(Operator_Torso_IK_Select)        
    bpy.utils.register_class(Operator_Torso_INV_Select)  
    bpy.utils.register_class(Operator_Head_FK_Select)  
    bpy.utils.register_class(Operator_Head_IK_Select)  
    bpy.utils.register_class(Operator_Arm_L_FK_Select)  
    bpy.utils.register_class(Operator_Arm_L_IK_Select)  
    bpy.utils.register_class(Operator_Arm_R_FK_Select)  
    bpy.utils.register_class(Operator_Arm_R_IK_Select)  
    bpy.utils.register_class(Operator_Leg_L_FK_Select)  
    bpy.utils.register_class(Operator_Leg_L_IK_Select)  
    bpy.utils.register_class(Operator_Leg_R_FK_Select)     
    bpy.utils.register_class(Operator_Leg_R_IK_Select)                                     

if __name__ == "__main__":
    register()