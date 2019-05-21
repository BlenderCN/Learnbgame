#!BPY
# -*- coding: UTF-8 -*-
# sync_bone_constraints
#
# Sync Armature's bone's constraints
# And Sync bone's Inverse Kinematics Settings
# 2018.06.06 N(Natukikazemizo)

if "bpy" in locals():
    import imp
    imp.reload(utils_io_csv)
    imp.reload(bone_constraints)
    imp.reload(common)
else:
    from . import utils_io_csv
    from . import bone_constraints
    from . import common

import bpy
import re

class StringValGroup(bpy.types.PropertyGroup):
    string_val = bpy.props.StringProperty()

bpy.utils.register_class(StringValGroup)

class MySettings(bpy.types.PropertyGroup):

#    emotion = bpy.props.EnumProperty(
#        name = "Emotion",
#        description = "Select emotion of registration destination.",
#        items = common.emotions
#    )

#    overwrite_data = bpy.props.BoolProperty(
#        name = "Overwrite Data",
#        description = "Enable or disable overwriting of data.",
#        default = True
#        )

    csv_file_name = bpy.props.StringProperty(
        name = "csv_file_name",
        description = "CSV file name."
    )
    csv_file_directory = bpy.props.StringProperty(subtype="FILE_PATH")

    msg_chk = bpy.props.StringProperty()
    msg_icon = bpy.props.StringProperty()


    msg_x_miller_chk = bpy.props.StringProperty()
    #msg_x_miller_icon = bpy.props.StringProperty()

    # リストで選択されているオブジェクトの名前
    #sel_armaturej= bpy.props.StringProperty()

    # 選択されている値が格納されるプロパティ
    sel_armature = bpy.props.StringProperty()
    sel_string_val = bpy.props.StringProperty()

    # Drop Downリストに表示される値のリスト
    string_val_list = bpy.props.CollectionProperty(type=bpy.types.StringValGroup)

    direction = bpy.props.EnumProperty(
        name = "Direction",
        description = "Select constraints copy dilection.",
        items = common.directions
    )

    def init_val_list(self):
        self.string_val_list.clear()
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE':
                v = self.string_val_list.add()
                v.string_val = obj.name
                v.name = obj.name

    def check(self):
        if self.csv_file_name == "":
            self.msg_chk = bpy.app.translations.pgettext("Select CSV file.")
            self.msg_icon = "ERROR"
        elif self.sel_armature == "":
            self.msg_chk = bpy.app.translations.\
                pgettext("Select target Armature.")
            self.msg_icon = "ERROR"
        else:
            self.msg_chk = "OK"
            self.msg_icon = "INFO"



    # def check_x_miller(self):
    #     self.msg_x_miller_chk = "OK"
    #     self.msg_x_miller_icon = "INFO"

#    def update_val(self, nm):
#        for sv in self.string_val_list:
#            if sv.name == nm:
#                self.sel_string_val = sv.string_val

class SelectCSVFile(bpy.types.Operator):

    bl_idname = "object.select_csv_file"
    bl_label = bpy.app.translations.pgettext("Select CSV File")
    bl_description = bpy.app.translations.pgettext("Select CSV File")
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    filename = bpy.props.StringProperty(name="filename")
    directory = bpy.props.StringProperty(subtype="FILE_PATH")
    # Search Filter
    filter_glob = bpy.props.StringProperty(
        default="*.csv",
        options={'HIDDEN'}
    )

    def execute(self, context):
        self.report(
            {'INFO'},
            " [FilePath] %s, [FileName] %s, [Directory] %s"
            % (self.filepath, self.filename, self.directory)
        )
        props = context.window_manager.sync_bone_constraints_props
        props.csv_file_directory = self.directory
        props.csv_file_name = self.filename
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        # Show File Browser
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}

class NullOperation(bpy.types.Operator):

    bl_idname = "object.null_operation"
    bl_label = "NOP"
    bl_description = "何もしない"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return {'FINISHED'}

#class NullOperationMenu(bpy.types.Menu):
#
#    bl_idname = "object.null_operation_menu"
#    bl_label = "NOP Menu"
#    bl_description = "Menu with multiple processes that do nothing"

#    def draw(self, context):
#        layout = self.layout
#        # メニュー項目の追加
#        for i in range(3):
#            layout.operator(NullOperation.bl_idname, text=("項目 %d" % (i)))

class SyncBonesIK(bpy.types.Operator):

    bl_idname = "object.sync_bones_ik"
    bl_label = "SyncBonesIK"
    bl_description = "Sync bones Invese Kinematics Settings."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.window_manager.sync_bone_constraints_props

        fromArmature = bpy.context.object.name
        for x in bpy.data.objects[props.sel_armature].pose.bones:
            if x.name in bpy.data.objects[fromArmature].pose.bones:
                fromBone = bpy.data.objects[fromArmature].pose.bones[x.name]
                x.ik_min_x = fromBone.ik_min_x
                x.ik_min_y = fromBone.ik_min_y
                x.ik_min_z = fromBone.ik_min_z
                x.ik_max_x = fromBone.ik_max_x
                x.ik_max_y = fromBone.ik_max_y
                x.ik_max_z = fromBone.ik_max_z
                x.use_ik_limit_x = fromBone.use_ik_limit_x
                x.use_ik_limit_y = fromBone.use_ik_limit_y
                x.use_ik_limit_z = fromBone.use_ik_limit_z
                x.ik_stretch = fromBone.ik_stretch
                x.lock_ik_x = fromBone.lock_ik_x
                x.lock_ik_y = fromBone.lock_ik_y
                x.lock_ik_z = fromBone.lock_ik_z

        return {'FINISHED'}


# Sync Bone Constraints
class SyncBoneConstraints(bpy.types.Operator):

    bl_idname = "object.sync_bone_constraints"
    bl_label = "Sync"
    bl_description = "Sync bones constraints of Armatures."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ExportBoneConstraints.execute(ExportBoneConstraints, context)
        ImportBoneConstraints.execute(ImportBoneConstraints, context)
        SyncBonesIK.execute(SyncBonesIK, context)
        return {'FINISHED'}

class ExportBoneConstraints(bpy.types.Operator):

    bl_idname = "object.export_bone_constraints"
    bl_label = "Export"
    bl_description = "Export bones constraints to CSV File."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bone_data = []
        bone_data.append(bone_constraints.BoneConstraints.header)

        for x in bpy.context.selected_pose_bones:
            # SKIP Special Bone
            if x.name == "Controllers_Root":
                continue

            if len(x.constraints) == 0:
                data = bone_constraints.BoneConstraints()
                data.bone_name = x.name
                bone_data.append(data.row)

            for y in x.constraints:
                data = bone_constraints.BoneConstraints()
                if y.type == "TRANSFORM":
                    print(x.name + ", " + y.name)

                    data.bone_name = x.name
                    data.constraint_name = y.name
                    data.mute = y.mute
                    data.target = y.target.name
                    data.subtarget_bone_name = y.subtarget
                    data.extrapolate = y.use_motion_extrapolate
                    data.from_min_x = y.from_min_x
                    data.from_max_x = y.from_max_x
                    data.from_min_y = y.from_min_y
                    data.from_max_y = y.from_max_y
                    data.from_min_z = y.from_min_z
                    data.from_max_z = y.from_max_z
                    data.map_to_x_from = y.map_to_x_from
                    data.map_to_y_from = y.map_to_y_from
                    data.map_to_z_from = y.map_to_z_from
                    data.map_to = y.map_to

                    if y.map_to == "LOCATION":
                        data.to_min_x = y.to_min_x
                        data.to_max_x = y.to_max_x
                        data.to_min_y = y.to_min_y
                        data.to_max_y = y.to_max_y
                        data.to_min_z = y.to_min_z
                        data.to_max_z = y.to_max_z
                    elif y.map_to == "ROTATION":
                        data.to_min_x = y.to_min_x_rot
                        data.to_max_x = y.to_max_x_rot
                        data.to_min_y = y.to_min_y_rot
                        data.to_max_y = y.to_max_y_rot
                        data.to_min_z = y.to_min_z_rot
                        data.to_max_z = y.to_max_z_rot
                    else:
                        # map_to:SCALE
                        data.to_min_x = y.to_min_x_scale
                        data.to_max_x = y.to_max_x_scale
                        data.to_min_y = y.to_min_y_scale
                        data.to_max_y = y.to_max_y_scale
                        data.to_min_z = y.to_min_z_scale
                        data.to_max_z = y.to_max_z_scale

                    data.target_space = y.target_space
                    data.owner_space = y.owner_space
                    data.influence = y.influence
                    data.type = y.type

                    bone_data.append(data.row)
                elif y.type == "COPY_LOCATION":
                    print(x.name + ", " + y.name)

                    data.bone_name = x.name
                    data.constraint_name = y.name
                    data.mute = y.mute
                    data.target = y.target.name
                    data.subtarget_bone_name = y.subtarget

                    data.from_min_x = y.use_x
                    data.from_max_x = y.invert_x
                    data.from_min_y = y.use_y
                    data.from_max_y = y.invert_y
                    data.from_min_z = y.use_z
                    data.from_max_z = y.invert_z

                    data.target_space = y.target_space
                    data.owner_space = y.owner_space
                    data.influence = y.influence
                    data.type = y.type
                    data.head_tail = y.head_tail
                    data.use_offset = y.use_offset

                    bone_data.append(data.row)

                elif y.type == "COPY_ROTATION":
                    print(x.name + ", " + y.name)

                    data.bone_name = x.name
                    data.constraint_name = y.name
                    data.mute = y.mute
                    data.target = y.target.name
                    data.subtarget_bone_name = y.subtarget

                    data.from_min_x = y.use_x
                    data.from_max_x = y.invert_x
                    data.from_min_y = y.use_y
                    data.from_max_y = y.invert_y
                    data.from_min_z = y.use_z
                    data.from_max_z = y.invert_z

                    data.target_space = y.target_space
                    data.owner_space = y.owner_space
                    data.influence = y.influence
                    data.type = y.type
                    data.use_offset = y.use_offset

                    bone_data.append(data.row)

                elif y.type == "IK":
                    print(x.name + ", " + y.name)

                    data.bone_name = x.name
                    data.constraint_name = y.name
                    data.mute = y.mute
                    data.target = y.target.name
                    data.subtarget_bone_name = y.subtarget

                    data.influence = y.influence
                    data.type = y.type

                    data.pole_target = y.pole_target
                    data.pole_subtarget = y.pole_subtarget
                    data.pole_angle = y.pole_angle
                    data.iterations = y.iterations
                    data.chain_count = y.chain_count
                    data.use_tail = y.use_tail
                    data.use_stretch = y.use_stretch
                    data.use_location = y.use_location
                    data.weight = y.weight
                    data.use_rotation = y.use_rotation
                    data.orient_weight = y.orient_weight

                    bone_data.append(data.row)


        props = context.window_manager.sync_bone_constraints_props
        utils_io_csv.write(props.csv_file_directory,
                           props.csv_file_name,
                            bone_data)
        return {'FINISHED'}

class ImportBoneConstraints(bpy.types.Operator):

    bl_idname = "object.import_bone_constraints"
    bl_label = "Import"
    bl_description = "Import bones constraints from CSV file."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.window_manager.sync_bone_constraints_props
        target = props.sel_armature
        props = context.window_manager.sync_bone_constraints_props
        header, data = utils_io_csv.read(props.csv_file_directory, \
                           props.csv_file_name)

        for row in data:
            if bpy.data.objects.find(target) == -1:
                print("Object not found. Object name is " + target)
                break

            con = bone_constraints.BoneConstraints(row)

            if bpy.data.objects[target].pose.bones.find(con.bone_name) == -1:
                print("Bone not found. Bone name is " + con.bone_name)
                break
            bone = bpy.data.objects[target].pose.bones[con.bone_name]
            for x in bone.constraints:
                bone.constraints.remove(x)

        for row in data:

            con = bone_constraints.BoneConstraints(row)

            bone = bpy.data.objects[target].pose.bones[con.bone_name]

            if con.constraint_name is None or con.constraint_name == "":
                continue

            if bone.constraints.find(con.constraint_name) == -1:
                constraint = bone.constraints.new(type=con.type)
                constraint.name = con.constraint_name

            constraint = bone.constraints[con.constraint_name]

            print("bone:" + bone.name + " constraint:" + constraint.name)

            constraint.mute = con.mute == "True"
            constraint.target = bpy.data.objects[target]
            constraint.subtarget = con.subtarget_bone_name

            if con.type == "TRANSFORM":
                constraint.use_motion_extrapolate = con.extrapolate == "True"

                constraint.from_min_x = float(con.from_min_x)
                constraint.from_max_x = float(con.from_max_x)
                constraint.from_min_y = float(con.from_min_y)
                constraint.from_max_y = float(con.from_max_y)
                constraint.from_min_z = float(con.from_min_z)
                constraint.from_max_z = float(con.from_max_z)

                constraint.map_to_x_from = con.map_to_x_from
                constraint.map_to_y_from = con.map_to_y_from
                constraint.map_to_z_from = con.map_to_z_from
                constraint.map_to = con.map_to
                if constraint.map_to == "LOCATION":
                    constraint.to_min_x = float(con.to_min_x)
                    constraint.to_max_x = float(con.to_max_x)
                    constraint.to_min_y = float(con.to_min_y)
                    constraint.to_max_y = float(con.to_max_y)
                    constraint.to_min_z = float(con.to_min_z)
                    constraint.to_max_z = float(con.to_max_z)
                elif constraint.map_to == "ROTATION":
                    constraint.to_min_x_rot = float(con.to_min_x)
                    constraint.to_max_x_rot = float(con.to_max_x)
                    constraint.to_min_y_rot = float(con.to_min_y)
                    constraint.to_max_y_rot = float(con.to_max_y)
                    constraint.to_min_z_rot = float(con.to_min_z)
                    constraint.to_max_z_rot = float(con.to_max_z)
                else:
                    # map_to:SCALE
                    constraint.to_min_x_scale = float(con.to_min_x)
                    constraint.to_max_x_scale = float(con.to_max_x)
                    constraint.to_min_y_scale = float(con.to_min_y)
                    constraint.to_max_y_scale = float(con.to_max_y)
                    constraint.to_min_z_scale = float(con.to_min_z)
                    constraint.to_max_z_scale = float(con.to_max_z)
            elif con.type == "COPY_LOCATION":
                constraint.use_x = con.from_min_x == "True"
                constraint.invert_x = con.from_max_x == "True"
                constraint.use_y = con.from_min_y == "True"
                constraint.invert_y = con.from_max_y == "True"
                constraint.use_z = con.from_min_z == "True"
                constraint.invert_z = con.from_max_z == "True"
                constraint.head_tail = float(con.head_tail)
                constraint.use_offset = con.use_offset
            elif con.type == "COPY_ROTATION":
                constraint.use_x = con.from_min_x == "True"
                constraint.invert_x = con.from_max_x == "True"
                constraint.use_y = con.from_min_y == "True"
                constraint.invert_y = con.from_max_y == "True"
                constraint.use_z = con.from_min_z == "True"
                constraint.invert_z = con.from_max_z == "True"
                constraint.use_offset = con.use_offset

            if con.type == "TRANSFORM" or con.type == "COPY_LOCATION" or \
                    con.type == "COPY_ROTATION":
                constraint.target_space = con.target_space
                constraint.owner_space = con.owner_space

            constraint.influence = con.influence

            if con.type == "IK":
                if con.pole_target != "":
                    constraint.pole_target = bpy.data.objects[target]
                    if con.pole_subtarget != "":
                        constraint.pole_subtarget = con.pole_subtarget
                constraint.pole_angle = con.pole_angle
                constraint.iterations = con.iterations
                constraint.chain_count = con.chain_count
                constraint.use_tail = con.use_tail
                constraint.use_stretch = con.use_stretch
                constraint.use_location = con.use_location
                constraint.weight = con.weight
                constraint.use_rotation = con.use_rotation
                constraint.orient_weight = con.orient_weight

        return {'FINISHED'}


class XMillerTransformations(bpy.types.Operator):

    bl_idname = "object.x_miller_transformations"
    bl_label = "XMillerTransformations"
    bl_description = "X-Axis Miller Bone Transformation constraings."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        props = context.window_manager.sync_bone_constraints_props

        props.msg_x_miller_chk = bpy.app.translations.pgettext("Start.")

        if props.direction == "l2r":
            key = r"\.L($|\.|_)"
            other_side = "R"
        else:
            key = r"\.R($|\.|_)"
            other_side = "L"

        for x in bpy.context.selected_pose_bones:

            # SKIP Other side & Center bones
            if re.search(key, x.name) is None:
                continue

            print(re.search(key, x.name) == False)

            if len(x.constraints) == 0:
                continue

            for y in x.constraints:
                if y.type == "TRANSFORM":
                    print(x.name + ", " + y.name)

                    # search other side bone & constraint
                    other_side_bone_name =\
                        common.get_otherside_name(key, other_side, x.name)

                    if re.search(key, y.subtarget) is None:
                        continue

                    other_side_tgt_name =\
                        common.get_otherside_name(key, other_side, y.subtarget)

                    x2 = x.id_data.pose.bones[other_side_bone_name]
                    y2 = x2.constraints[y.name]


                    # data.bone_name = x.name
                    # data.constraint_name = y.name
                    y2.mute = y.mute
                    # y2.target = y.target.name
                    y2.subtarget = other_side_tgt_name
                    y2.use_motion_extrapolate = y.use_motion_extrapolate
                    y2.from_min_x = y.from_min_x
                    y2.from_max_x = y.from_max_x
                    y2.from_min_y = y.from_min_y
                    y2.from_max_y = y.from_max_y
                    y2.from_min_z = y.from_min_z
                    y2.from_max_z = y.from_max_z
                    y2.map_to_x_from = y.map_to_x_from
                    y2.map_to_y_from = y.map_to_y_from
                    y2.map_to_z_from = y.map_to_z_from
                    y2.map_to = y.map_to

                    if y.map_to == "LOCATION":
                        y2.to_min_x = y.to_min_x
                        y2.to_max_x = y.to_max_x
                        y2.to_min_y = y.to_min_y
                        y2.to_max_y = y.to_max_y
                        y2.to_min_z = y.to_min_z
                        y2.to_max_z = y.to_max_z
                    elif y.map_to == "ROTATION":
                        y2.to_min_x_rot = y.to_min_x_rot
                        y2.to_max_x_rot = y.to_max_x_rot
                        y2.to_min_y_rot = y.to_min_y_rot
                        y2.to_max_y_rot = y.to_max_y_rot
                        y2.to_min_z_rot = y.to_min_z_rot
                        y2.to_max_z_rot = y.to_max_z_rot
                    else:
                        # map_to:SCALE
                        y2.to_min_x_scale = y.to_min_x_scale
                        y2.to_max_x_scale = y.to_max_x_scale
                        y2.to_max_y_scale = y.to_max_y_scale
                        y2.to_min_y_scale = y.to_min_y_scale
                        y2.to_min_z_scale = y.to_min_z_scale
                        y2.to_max_z_scale = y.to_max_z_scale

                    y2.target_space = y.target_space
                    y2.owner_space = y.owner_space
                    y2.influence = y.influence
                    # y2.type = y.type

        props.msg_x_miller_chk = bpy.app.translations.pgettext("Finished.")

        return {'FINISHED'}



# Add "Auto Breakdown" tab on Tool Shelf
class VIEW3D_PT_AutoBreakdown(bpy.types.Panel):

    bl_label = bpy.app.translations.pgettext("Sync Bone Constraints")
              # String on TAB
    bl_space_type = 'VIEW_3D'           # Area which show menu
    bl_region_type = 'TOOLS'            # Region which show menu
    bl_category = bpy.app.translations.pgettext("Auto Breakdown")
            # String displayed in the header of the menu that opened the tab
    bl_context = "posemode"            # Context which show panel

    # 本クラスの処理が実行可能かを判定する
    @classmethod
    def poll(cls, context):
        # オブジェクトが選択されている時のみメニューを表示させる
        for o in bpy.data.objects:
            if o.select:
                return True
        return False

    # ヘッダーのカスタマイズ
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='PLUGIN')

    # メニューの描画処理
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = context.window_manager.sync_bone_constraints_props


        # ファイルブラウザを表示する
        layout.label(text = props.csv_file_directory)
        layout.label(text = props.csv_file_name)
        layout.operator(SelectCSVFile.bl_idname)

#        # CharacterName
#        layout.label(text = bpy.app.translations.pgettext("Character Name:"))
#        layout.label(text = bpy.path.abspath("//"))

#        # display the properties
#        layout.prop(props, "emotion", \
#            text=bpy.app.translations.pgettext("Emotion"))

#        layout.separator()

#        layout.prop(props, "overwrite_data", \
#            text=bpy.app.translations.pgettext("Overwrite Data"))


#        layout.prop_search(props, "sel_obj", context.scene, \
#            "objects", text="Objects")
#        row = layout.row()
#        row.prop_search(props, "sel_obj", context.scene, "objects", text="Objects")
#        row = layout.row()
#        row.prop(props, "sel_obj")

        row = layout.row()

        props.init_val_list()

        row.prop_search(props, "sel_armature", props,
                        "string_val_list",
                        text = bpy.app.translations.pgettext("Target"),
                        icon="OUTLINER_OB_ARMATURE")

#        row = layout.row()
#        row.prop(props, "sel_armature")

 #       props.update_val(props.sel_armature)
#        row.prop(props, "sel_string_val")

        layout.separator()

        row = layout.row()
        box = row.box()
        box_row = box.row()

        props.check()

        box_row.label(text = props.msg_chk, icon=props.msg_icon)

        layout.operator(SyncBoneConstraints.bl_idname, \
            text = bpy.app.translations.pgettext("Sync"))

#        layout.separator()

#        layout.operator(ExportBoneConstraints.bl_idname, \
#            text = bpy.app.translations.pgettext("Write CSV"))

#        layout.separator()

#        layout.operator(ImportBoneConstraints.bl_idname, \
#            text = bpy.app.translations.pgettext("Read CSV"))

#        layout.separator()

#        layout.operator(SyncBonesIK.bl_idname, \


# Add X-Miller Function Panel
class VIEW3D_PT_XMiller(bpy.types.Panel):

    bl_label = bpy.app.translations.pgettext("X-Miller Bone Transformations")
              # String on TAB
    bl_space_type = 'VIEW_3D'           # Area which show menu
    bl_region_type = 'TOOLS'            # Region which show menu
    bl_category = bpy.app.translations.pgettext("Auto Breakdown")
            # String displayed in the header of the menu that opened the tab
    bl_context = "posemode"            # Context which show panel

    # 本クラスの処理が実行可能かを判定する
    @classmethod
    def poll(cls, context):
        # オブジェクトが選択されている時のみメニューを表示させる
        for o in bpy.data.objects:
            if o.select:
                return True
        return False

    # ヘッダーのカスタマイズ
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='PLUGIN')

    # メニューの描画処理
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = context.window_manager.sync_bone_constraints_props


        layout.prop(props, "direction", \
            text=bpy.app.translations.pgettext("direction"))

        layout.separator()

        row = layout.row()
        box = row.box()
        box_row = box.row()

        # props.check_x_miller()

        box_row.label(text = props.msg_x_miller_chk, icon="NONE")

        layout.operator(XMillerTransformations.bl_idname, \
            text = bpy.app.translations.pgettext("Copy"))

#            text = bpy.app.translations.pgettext("Sync IK"))
