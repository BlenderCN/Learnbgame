import bpy

# global group lists
all_bones = hand_l = hand_r = arm_l = arm_r = leg_l = leg_r = foot_l = foot_r = head = torso = []

class BlenRig_5_Interface(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = "Tools"
    bl_context = ".posemode"
    bl_label = 'BlenRig 5 Controls'
    bl_ui_units_x = 25


    @classmethod
    def poll(cls, context):
        if not bpy.context.active_object:
            return False
        if (bpy.context.active_object.type in ["ARMATURE"]):
            for prop in bpy.context.active_object.data.items():
                if prop[0] == 'rig_name' and prop[1] == 'BlenRig_5':
                    return True

    def draw_armature_layers(self, layout, arm):
        row = layout.row()
        row.operator("gui.blenrig_5_tabs", icon="RENDERLAYERS", emboss = 1).tab = "gui_layers"
        row.label(text="ARMATURE LAYERS")
        if not arm["gui_layers"]:
            return


        layer_number = arm["layers_count"]
        layer_names = arm["layer_list"].split(", ")

        row_layers = layout.row()
        col = row_layers.column(align = 0)
        col.scale_y = 0.75
        col.prop(arm, "layers", index=0 , toggle=True, text =layer_names[0])
        if layer_number > 3:
            col.prop(arm, "layers", index=3, toggle=True, text=layer_names[3])
        if layer_number > 6:
            col.prop(arm, "layers", index=6, toggle=True, text=layer_names[6])
        if layer_number > 9:
            col.prop(arm, "layers", index=17, toggle=True, text=layer_names[9])
        if layer_number > 12:
            col.prop(arm, "layers", index=20, toggle=True, text=layer_names[12])
        if layer_number > 15:
            col.prop(arm, "layers", index=23, toggle=True, text=layer_names[15])
        if layer_number > 18:
            col.prop(arm, "layers", index=10, toggle=True, text=layer_names[18])
        if layer_number > 21:
            col.prop(arm, "layers", index=13, toggle=True, text=layer_names[21])
        if layer_number > 24:
            col.prop(arm, "layers", index=24, toggle=True, text=layer_names[24])
        if layer_number > 27:
            col.prop(arm, "layers", index=27, toggle=True, text=layer_names[27])
        if layer_number > 30:
            col.prop(arm, "layers", index=30, toggle=True, text=layer_names[30])

        col = row_layers.column(align = 0)
        col.scale_y = 0.75
        if layer_number > 1:
            col.prop(arm, "layers", index=1, toggle=True, text=layer_names[1])
        if layer_number > 4:
            col.prop(arm, "layers", index=4, toggle=True, text=layer_names[4])
        if layer_number > 7:
            col.prop(arm, "layers", index=7, toggle=True, text=layer_names[7])
        if layer_number > 10:
            col.prop(arm, "layers", index=18, toggle=True, text=layer_names[10])
        if layer_number > 13:
            col.prop(arm, "layers", index=21, toggle=True, text=layer_names[13])
        if layer_number > 16:
            col.prop(arm, "layers", index=8, toggle=True, text=layer_names[16])
        if layer_number > 19:
            col.prop(arm, "layers", index=11, toggle=True, text=layer_names[19])
        if layer_number > 22:
            col.prop(arm, "layers", index=14, toggle=True, text=layer_names[22])
        if layer_number > 25:
            col.prop(arm, "layers", index=25, toggle=True, text=layer_names[25])
        if layer_number > 28:
            col.prop(arm, "layers", index=28, toggle=True, text=layer_names[28])
        if layer_number > 31:
            col.prop(arm, "layers", index=31, toggle=True, text=layer_names[31])

        col = row_layers.column(align = 0)
        col.scale_y = 0.75
        if layer_number > 2:
            col.prop(arm, "layers", index=2 , toggle=True, text=layer_names[2])
        if layer_number > 5:
            col.prop(arm, "layers", index=5 , toggle=True, text=layer_names[5])
        if layer_number > 8:
            col.prop(arm, "layers", index=16 , toggle=True, text=layer_names[8])
        if layer_number > 11:
            col.prop(arm, "layers", index=19 , toggle=True, text=layer_names[11])
        if layer_number > 14:
            col.prop(arm, "layers", index=22 , toggle=True, text=layer_names[14])
        if layer_number > 17:
            col.prop(arm, "layers", index=9 , toggle=True, text=layer_names[17])
        if layer_number > 20:
            col.prop(arm, "layers", index=12 , toggle=True, text=layer_names[20])
        if layer_number > 23:
            col.prop(arm, "layers", index=15 , toggle=True, text=layer_names[23])
        if layer_number > 26:
            col.prop(arm, "layers", index=26 , toggle=True, text=layer_names[26])
        if layer_number > 29:
            col.prop(arm, "layers", index=29 , toggle=True, text=layer_names[29])

    def draw_main_bone_properties(self, layout, arm, bones_by_name):
        row = layout.row()
        row.operator("gui.blenrig_5_tabs", icon="OUTLINER_OB_ARMATURE", emboss = 1).tab = "gui_picker_body"
        row.label(text="BONE PROPERTIES")

        if not arm["gui_picker_body"]:
            return

        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        bones = bones_by_name

        col.prop(bones['properties_head'], 'look_switch', text="Eyes Target", slider=True)

        subcol = col.column(align=True)
        center_label(subcol, "Torso")
        subcol.prop(bones['properties_torso'], 'inv_torso', text="Invert")
        subcol.prop(bones['properties_torso'], 'ik_torso', text="IK=0 FK=1")
        subcol.prop(bones['properties_torso'], 'toon_torso', text="Str IK")

        subcol = col.column(align=True)
        center_label(subcol, "Head")
        subcol.prop(bones['properties_head'], 'ik_head', text="IK=0 FK=1")
        subcol.prop(bones['properties_head'], 'hinge_head', text="Hinge")
        subcol.prop(bones['properties_head'], 'toon_head', text="Str IK")
        subcol.prop(bones['properties_head'], 'hinge_neck', text="Hinge")

        row = col.row()
        left = row.column()
        right = row.column()

        subcol = right.column(align=True)
        subcol.label(text="Right Arm")
        subcol.prop(bones['properties_arm_R'], 'ik_arm_R', text="IK=0 FK=1")
        subcol.prop(bones['properties_arm_R'], 'hinge_arm_R', text="Hinge")
        subcol.prop(bones['properties_arm_R'], 'toon_arm_R', text="Str IK")
        subcol.prop(bones['properties_arm_R'], 'hinge_hand_R', text="Hinge")
        subcol.prop(bones['properties_arm_R'], 'ik_fing_all_R', text="IK=1 FK=0")
        subcol.prop(bones['properties_arm_R'], 'hinge_fing_all_R', text="Hinge")

        subcol = right.column(align=True)
        subcol.label(text="Right Leg")
        subcol.prop(bones['properties_leg_R'], 'ik_leg_R', text="IK=0 FK=1")
        subcol.prop(bones['properties_leg_R'], 'hinge_leg_R', text="Hinge")
        subcol.prop(bones['properties_leg_R'], 'toon_leg_R', text="Str IK")
        subcol.prop(bones['properties_leg_R'], 'ik_toes_all_R', text="IK=0 FK=1")
        subcol.prop(bones['properties_leg_R'], 'hinge_toes_all_R', text="Hinge")

        subcol = left.column(align=True)
        subcol.label(text="Left Arm")
        subcol.prop(bones['properties_arm_L'], 'ik_arm_L', text="IK=0 FK=1")
        subcol.prop(bones['properties_arm_L'], 'hinge_arm_L', text="Hinge")
        subcol.prop(bones['properties_arm_L'], 'toon_arm_L', text="Str IK")
        subcol.prop(bones['properties_arm_L'], 'hinge_hand_L', text="Hinge")
        subcol.prop(bones['properties_arm_L'], 'ik_fing_all_L', text="FK=0 IK=1")
        subcol.prop(bones['properties_arm_L'], 'hinge_fing_all_L', text="Hinge")

        subcol = left.column(align=True)
        subcol.label(text="Left Leg")
        subcol.prop(bones['properties_leg_L'], 'ik_leg_L', text="IK=0 FK=1")
        subcol.prop(bones['properties_leg_L'], 'hinge_leg_L', text="Hinge")
        subcol.prop(bones['properties_leg_L'], 'toon_leg_L', text="Str IK")
        subcol.prop(bones['properties_leg_L'], 'ik_toes_all_L', text="IK=0 FK=1")
        subcol.prop(bones['properties_leg_L'], 'hinge_toes_all_L', text="Hinge")

    def draw_snapping(self, layout, selected_bone_names):
        props = bpy.context.window_manager.blenrig_5_props
        row = layout.row()
        row.prop(props, "gui_snap", text="IK/FK Snapping")
        if not props.gui_snap:
            return

        row.prop(props, "gui_snap_all", text="ALL")

        def is_any_selected(names):
            return any(name in selected_bone_names for name in names)

        def display_snap_ops(*bone_name_lists):
            return props.gui_snap_all or any(is_any_selected(names) for names in bone_name_lists)

        if display_snap_ops(head):
            col = layout.column(align=True)
            col.label(text="Head")
            row = col.row()
            row.operator("head_snap.fk_ik", text="FK >> IK")
            row.operator("head_snap.ik_fk", text="IK >> FK")

        if display_snap_ops(torso):
            col = layout.column(align=True)
            col.label(text="Torso")
            row = col.row()
            row.operator("torso_snap.fk_ik", text="FK >> IK")
            row.operator("torso_snap.ik_fk", text="IK >> FK")
            row = col.row()
            row.operator("torso_snap.up_inv", text="UP >> INV")
            row.operator("torso_snap.inv_up", text="INV >> UP")

        row = layout.row()
        left = row.column()
        right = row.column()

        if display_snap_ops(arm_l, hand_l):
            col = left.column(align=True)
            col.label(text="Left Arm")
            row = col.row(align=True)
            row.operator("arm_l_snap.fk_ik", text="to IK")
            row.operator("arm_l_snap.fk_ik", text="", icon="DECORATE_KEYFRAME").do_switch = True
            row = col.row(align=True)
            row.operator("arm_l_snap.ik_fk", text="to FK")
            row.operator("arm_l_snap.ik_fk", text="", icon="DECORATE_KEYFRAME").do_switch = True

        if display_snap_ops(arm_r, hand_r):
            col = right.column(align=True)
            col.label(text="Right Arm")
            subcol = col.row(align=True)
            subcol.operator("arm_r_snap.fk_ik", text="to IK")
            subcol.operator("arm_r_snap.fk_ik", text="", icon="DECORATE_KEYFRAME").do_switch = True
            subcol = col.row(align=True)
            subcol.operator("arm_r_snap.ik_fk", text="to FK")
            subcol.operator("arm_r_snap.ik_fk", text="", icon="DECORATE_KEYFRAME").do_switch = True

        if display_snap_ops(leg_l, foot_l):
            col = left.column(align=True)
            col.label(text="Left Leg")
            subcol = col.row(align=True)
            subcol.operator("leg_l_snap.fk_ik", text="to IK")
            subcol.operator("leg_l_snap.fk_ik", text="", icon="DECORATE_KEYFRAME").do_switch = True
            subcol = col.row(align=True)
            subcol.operator("leg_l_snap.ik_fk", text="to FK")
            subcol.operator("leg_l_snap.ik_fk", text="", icon="DECORATE_KEYFRAME").do_switch = True

        if display_snap_ops(leg_r, foot_r):
            col = right.column(align=True)
            col.label(text="Right Leg")
            subcol = col.row(align=True)
            subcol.operator("leg_r_snap.fk_ik", text="to IK")
            subcol.operator("leg_r_snap.fk_ik", text="", icon="DECORATE_KEYFRAME").do_switch = True
            subcol = col.row(align=True)
            subcol.operator("leg_r_snap.ik_fk", text="to FK")
            subcol.operator("leg_r_snap.ik_fk", text="", icon="DECORATE_KEYFRAME").do_switch = True

    def draw_extra_properties(self, layout, arm, bones_by_name, props):
        row = layout.row()
        row.operator("gui.blenrig_5_tabs", icon="SETTINGS", emboss = 1).tab = "gui_misc"
        row.label(text="EXTRA PROPERTIES")

        if not arm["gui_misc"]:
            return

        bones = bones_by_name

        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False

        col.prop(props, "gui_extra_props_head", text="Head")
        if props.gui_extra_props_head:
            subcol = col.column(align=True)
            center_label(subcol, "Teeth - Follow Smile")
            subcol.prop(bones['properties_head'], '["toon_teeth_up"]', text="Upper Teeth", slider=True)
            subcol.prop(bones['properties_head'], '["toon_teeth_low"]', text="Lower Teeth", slider=True)
            center_label(subcol, "Fleshy Eyes")
            subcol.prop(bones['look_R'], '["FLESHY_EYE_R"]', text="Eye_R", slider=True)
            subcol.prop(bones['look_L'], '["FLESHY_EYE_L"]', text="Eye_L", slider=True)

        col.prop(props, "gui_extra_props_arms", text="Arms")
        if props.gui_extra_props_arms:
            subcol = col.column(align=True)
            center_label(subcol, "Curved Arms")
            subcol.prop(bones['properties_arm_R'], '["curved_arm_R"]', text="Curve R", slider=True)
            subcol.prop(bones['properties_arm_R'], '["curved_arm_tweak_R"]', text="Tweak R", slider=True)
            subcol.prop(bones['properties_arm_L'], '["curved_arm_L"]', text="Curve L", slider=True)
            subcol.prop(bones['properties_arm_L'], '["curved_arm_tweak_L"]', text="Tweak L", slider=True)
            center_label(subcol, "Elbow Poles")
            subcol.prop(bones['elbow_pole_R'], '["FOLLOW_TORSO_R"]', text="Follow Torso R", slider=True)
            subcol.prop(bones['elbow_pole_L'], '["FOLLOW_TORSO_L"]', text="Follow Torso L", slider=True)

        col.prop(props, "gui_extra_props_fingers", text="Fingers")
        if props.gui_extra_props_fingers:
            subcol = col.column()
            subcol.use_property_split = False

            row = subcol.row()
            row.label(text="")
            row.label(text="IK L")
            row.label(text="Hinge L")
            row.label(text="IK R")
            row.label(text="Hinge R")

            row = subcol.row()
            row.label(text="All")
            row.prop(bones['properties_arm_L'], 'ik_fing_all_L', text="")
            row.prop(bones['properties_arm_L'], 'hinge_fing_all_L', text="")
            row.prop(bones['properties_arm_R'], 'ik_fing_all_R', text="")
            row.prop(bones['properties_arm_R'], 'hinge_fing_all_R', text="")

            row = subcol.row()
            row.label(text="Thumb")
            row.prop(bones['properties_arm_L'], 'ik_fing_thumb_L', text="")
            row.prop(bones['properties_arm_L'], 'hinge_fing_thumb_L', text="")
            row.prop(bones['properties_arm_R'], 'ik_fing_thumb_R', text="")
            row.prop(bones['properties_arm_R'], 'hinge_fing_thumb_R', text="")

            row = subcol.row()
            row.label(text="Index")
            row.prop(bones['properties_arm_L'], 'ik_fing_ind_L', text="")
            row.prop(bones['properties_arm_L'], 'hinge_fing_ind_L', text="")
            row.prop(bones['properties_arm_R'], 'ik_fing_ind_R', text="")
            row.prop(bones['properties_arm_R'], 'hinge_fing_ind_R', text="")

            row = subcol.row()
            row.label(text="Middle")
            row.prop(bones['properties_arm_L'], 'ik_fing_mid_L', text="")
            row.prop(bones['properties_arm_L'], 'hinge_fing_mid_L', text="")
            row.prop(bones['properties_arm_R'], 'ik_fing_mid_R', text="")
            row.prop(bones['properties_arm_R'], 'hinge_fing_mid_R', text="")

            row = subcol.row()
            row.label(text="Ring")
            row.prop(bones['properties_arm_L'], 'ik_fing_ring_L', text="")
            row.prop(bones['properties_arm_L'], 'hinge_fing_ring_L', text="")
            row.prop(bones['properties_arm_R'], 'ik_fing_ring_R', text="")
            row.prop(bones['properties_arm_R'], 'hinge_fing_ring_R', text="")

            row = subcol.row()
            row.label(text="Little")
            row.prop(bones['properties_arm_L'], 'ik_fing_lit_L', text="")
            row.prop(bones['properties_arm_L'], 'hinge_fing_lit_L', text="")
            row.prop(bones['properties_arm_R'], 'ik_fing_lit_R', text="")
            row.prop(bones['properties_arm_R'], 'hinge_fing_lit_R', text="")

        col.prop(props, "gui_extra_props_legs", text="Legs")
        if props.gui_extra_props_legs:
            subcol = col.column(align=True)
            center_label(subcol, "Curved Legs")
            subcol.prop(bones['properties_leg_R'], '["curved_leg_R"]', text="Curve R", slider=True)
            subcol.prop(bones['properties_leg_R'], '["curved_leg_tweak_R"]', text="Tweak R", slider=True)
            subcol.prop(bones['properties_leg_L'], '["curved_leg_L"]', text="Curve L", slider=True)
            subcol.prop(bones['properties_leg_L'], '["curved_leg_tweak_L"]', text="Tweak L", slider=True)
            center_label(subcol, "Knee Poles")
            subcol.prop(bones['knee_pole_R'], '["FOLLOW_FOOT_R"]', text="Follow Foot R", slider=True)
            subcol.prop(bones['knee_pole_L'], '["FOLLOW_FOOT_L"]', text="Follow Foot L", slider=True)

        col.prop(props, "gui_extra_props_accessories", text="Accessories")
        if props.gui_extra_props_accessories:
            subcol = col.column(align=True)
            subcol.prop(bones['properties_head'], '["hat_free"]', text="Hat")
            subcol.prop(bones['properties_arm_R'], '["hand_accessory_R"]', text="Hand_R", slider=True)
            subcol.prop(bones['properties_head'], '["glasses_free"]', text="Glasses")
            subcol.prop(bones['properties_arm_L'], '["hand_accessory_L"]', text="Hand_L", slider=True)

    def draw_custom_properties(self, layout, arm, act_bone, props, arm_bones):
        row = layout.row()
        row.operator("gui.blenrig_5_tabs", icon="SETTINGS", emboss = 1).tab = "gui_cust_props"
        row.label(text="CUSTOM PROPERTIES")

        if not arm["gui_cust_props"]:
            return

        if "ROT_MODE" in act_bone:
            layout.prop(act_bone, '["ROT_MODE"]', text="Active Bone Rotation Order")

        col = layout.column()
        col.prop(props, "gui_cust_props_all", text="All")
        excluded = {"_RNA_UI", "ROT_MODE"}
        if props.gui_cust_props_all:
            for bone in arm_bones:
                if "properties" not in bone.name:
                    for prop_name in bone.keys():
                        if prop_name not in excluded:
                            col.prop(bone, f'["{prop_name}"]', text=f'{bone.name} ["{prop_name}"]')
        else:
            for prop_name in act_bone.keys():
                if prop_name not in excluded:
                    col.prop(act_bone, f'["{prop_name}"]', text=f'["{prop_name}"]')

    def draw_muscle_system(self, layout, arm, bones_by_name):
        row = layout.row()
        row.operator("gui.blenrig_5_tabs", icon="FORCE_LENNARDJONES", emboss = 1).tab = "gui_muscle"
        row.label(text="MUSCLE SYSTEM")

        if not arm["gui_muscle"]:
            return

        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(bones_by_name['properties'], '["muscle_system"]', text="Muscles")
        col.prop(bones_by_name['properties'], '["muscle_res"]', text="Muscle Resolution")
        col.prop(bones_by_name['properties'], '["deformation_extras"]', text="Deformation Extras")

    def draw(self, context):
        global all_bones, hand_l, hand_r, arm_l, arm_r, leg_l, leg_r, foot_l, foot_r, head, torso

        if bpy.context.mode not in ("POSE", "EDIT_ARMATURE"):
            return

        layout = self.layout
        props = context.window_manager.blenrig_5_props
        arm = bpy.context.active_object.data
        armobj = bpy.context.active_object
        arm_bones = bpy.context.active_object.pose.bones
        act_bone = bpy.context.active_pose_bone
        bones_by_name = {bone.name : bone for bone in arm_bones}

        try:
            selected_bone_names = {bone.name for bone in bpy.context.selected_pose_bones}
        except:
            selected_bone_names = set()

        def find_bone_names(all_of=tuple(), any_of=tuple()):
            names = []
            for name in bones_by_name.keys():
                if all(part in name for part in all_of):
                    if len(any_of) == 0 or any(part in name for part in any_of):
                        names.append(name)
            return names


        if not all_bones:
            all_bones = [bone.name for bone in armobj.pose.bones]

            hand_l = find_bone_names(["_L", "fing"])
            hand_r = find_bone_names(["_R", "fing"])
            arm_l =  find_bone_names(["_L"], ["arm", "elbow", "shoulder", "hand", "wrist"])
            arm_r =  find_bone_names(["_R"], ["arm", "elbow", "shoulder", "hand", "wrist"])
            leg_l =  find_bone_names(["_L"], ["butt", "knee", "thigh", "shin"])
            leg_r =  find_bone_names(["_R"], ["butt", "knee", "thigh", "shin"])
            foot_l = find_bone_names(["_L"], ["toe", "foot", "heel", "sole", "floor"])
            foot_r = find_bone_names(["_R"], ["toe", "foot", "heel", "sole", "floor"])
            head =   find_bone_names([], [
                "look", "head", "neck", "maxi", "cheek", "chin", "lip", "ear_",
                "tongue", "eyelid", "forehead", "brow", "nose", "nostril", "mouth",
                "eye", "gorro", "teeth", "hat", "glasses", "anteojos", "hair", "pelo"])
            torso =  find_bone_names([], [
                "master", "spine", "pelvis", "torso", "omoplate", "chest", "body",
                "ball", "dicky", "butt", "back", "clavi", "look", "hip"])


        self.draw_armature_layers(layout, arm)
        self.draw_main_bone_properties(layout, arm, bones_by_name)
        self.draw_snapping(layout, selected_bone_names)
        self.draw_extra_properties(layout, arm, bones_by_name, props)
        self.draw_custom_properties(layout, arm, act_bone, props, arm_bones)
        self.draw_muscle_system(layout, arm, bones_by_name)


def center_label(layout, text):
    row = layout.row(align=True)
    row.alignment = 'CENTER'
    row.label(text=text)
