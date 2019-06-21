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

# <pep8-80 compliant>

bl_info = {
    "name": "BVH Madness",
    "author": "Campbell Barton",
    "blender": (2, 57, 0),
    "location": "File > Import-Export",
    "description": "Import-Export BVH from armature objects",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
                "Scripts/Import-Export/MotionCapture_BVH",
    "tracker_url": "",
    "support": 'TESTING',
    "category": "Learnbgame",
}

if "bpy" in locals():
    import imp
    if "import_bvh" in locals():
        imp.reload(import_bvh)
    if "export_bvh" in locals():
        imp.reload(export_bvh)
    if "utils" in locals():
        imp.reload(utils)
    if "cmu" in locals():
        imp.reload(cmu)
    if "rescale" in locals():
        imp.reload(rescale)
    if "import2selected" in locals():
        imp.reload(import2selected)
    if "import2selected" in locals():
        imp.reload(action_menu)
    if "posematch" in locals():
        imp.reload(posematch)

import bpy

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       OperatorFileListElement,
                       AddonPreferences,
                      )

from bpy.props import (StringProperty,
                       FloatProperty,
                       IntProperty,
                       BoolProperty,
                       EnumProperty,
                       PointerProperty,
                       CollectionProperty,
                       )
from bpy_extras.io_utils import (ImportHelper,
                                 ExportHelper,
                                 axis_conversion,
                                 )


from .utils import (is_subdir,
                    get_pose_matrix_in_other_space,
                    get_local_pose_matrix,
                    set_pose_translation,
                    set_pose_rotation,
                    set_pose_scale,
                    match_pose_translation,
                    match_pose_rotation,
                    match_pose_scale,
                    add_bone_groups)


from . import (cmu, rescale, import2selected, action_menu, posematch)

from os.path import basename, normpath
#cmu = None
def load_cmu(self, context):
    if self.use_cmu_data:
        from .cmu import CMUMocaps
        cmu = CMUMocaps()
    else:
        cmu = None

def check_cmu_folder(self, context):
    return None


class BVH_AddonPreferences(AddonPreferences):
    bl_idname = "mocap_madness"

    cmu_folder = StringProperty(
            name="CMU Mocap Library",
            subtype='DIR_PATH',
            description="CMU Base Path",
            update=check_cmu_folder,
            )

    use_cmu_data = BoolProperty(
            name="CMU",
            description="Use Carnegie Melon Uni Descriptions",
            update = load_cmu,
            default=False
            )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Mocap Madness", icon='ARMATURE_DATA')
        row = layout.row()
        col = row.column()
        col.alignment = 'LEFT'
        col.prop(self, "use_cmu_data", toggle=True)
        col = row.column()
        col.enabled = self.use_cmu_data
        col.prop(self, "cmu_folder")


prop_dic = {"name": StringProperty(name="Name", description="FileName"),
            "action_only": BoolProperty(default=False)
           }

BVHFile = type("BVHFile", (PropertyGroup,), prop_dic)
bpy.utils.register_class(BVHFile)
# more details for action
prop_dic = {"name": StringProperty(),
            "subject": StringProperty(name="Subject",
                                      description="Action Subject"),
            "description": StringProperty(default="",
                                          description="Action Description")
           }

ActionInfo = type("ActionInfo", (PropertyGroup,), prop_dic)

bpy.utils.register_class(ActionInfo)


class PlayMocapList(Operator):
    bl_idname = 'mocapmadness.playmocap'
    bl_label = 'Play Mocaps'
    createTrack = BoolProperty("CreateTrack", default=False)
    addHipLocator = BoolProperty("AddHipLocator", default=False)
    addtoCompareList = StringProperty("addtoCompareList", default="-")
    action = StringProperty("Action", default="Select Action")

    def execute(self, context):
        #get all the actions that have markers named after the rig
        rig = context.object

        if self.createTrack:
            rig = context.object

            RigTrack, BvhTrack, RigAction = MM_get_tracks(rig)
            action = rig.animation_data.action
            rig.animation_data.action = RigAction
            rig.keyframe_insert("location")
            rig.keyframe_insert("rotation_euler", index=2)
            current_frame = context.scene.frame_current

            actionStrip = BvhTrack.strips.new("Start",
                                              start=current_frame,
                                              action=action)
            rigStrip = RigTrack.strips.new("Rig%sStrip" % rig.name,
                                           start=current_frame,
                                           action=RigAction)
            rig.animation_data.action = None
            RigTrack.strips[0].action_frame_end = actionStrip.frame_end
            return{'FINISHED'}

        if self.addHipLocator:
            rig = context.selected_objects[0]
            AddHipLocator(rig, rig.pose.bones[0])
            return{'FINISHED'}

        action = bpy.data.actions.get(self.action)
        if action is None:
            return{'CANCELLED'}
        '''
        if not rig.animation_data:
            rig.animation_data_create()
        '''
        rig.animation_data.action = action
        context.scene.frame_set(1)
        context.scene.frame_end = action.frame_range[1]
        #bpy.ops.screen.animation_cancel()
        mode = rig.mode
        if mode == "POSE":
            bpy.ops.pose.paths_clear()
            bpy.ops.pose.select_all(action='DESELECT')

            rig.pose.bones[0].bone.select = True
            bpy.ops.pose.paths_calculate()

        self.report({'INFO'}, "Playing %s" % action.name)
        return {'FINISHED'}


class ActionMenu(bpy.types.Menu):
    bl_idname = "mocapmadness.actionmenu"
    bl_label = "Change Action"


    def draw(self, context):

        layout = self.layout

        rig = context.object
        arm = rig.data
        actions = arm.actions
        for name in actions.keys():
            a = bpy.data.actions.get(name, None)
            if a is not None:
                op = layout.operator("mocapmadness.playmocap",
                                     text=a.info.description)
                op.action = name

        '''
        actions = context.object["MMRig"]
        for Action in Actions:
            name = Action.get("name")
            layout.operator("mocapmadness.playmocap",text=name).action=name
        '''



class MocapMadness3DPanel():
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "BVH"

    @classmethod
    def poll(cls, context):
        return True

    def draw_action_info(self, action):
        layout = self.layout
        info = action.info
        box = layout.box()
        row = box.row()
        row.prop(info, "name")
        row = box.row()
        row.prop(info, "subject")


class MMPlayPanel(MocapMadness3DPanel, Panel):
    bl_idname = "VIEW3D_PT_test_2"
    bl_label = "Play Mocap"

    @classmethod
    def poll(self, context):
        try:
            rig = context.object
            if rig is None:
                return False
            ad = hasattr(rig, "animation_data")

            if ad and rig.type == 'ARMATURE':
                return True

        except:
            return False
        return False

    #Going to be used as a play mocap panel
    def draw(self, context):
        action = None
        Found = False
        subject = "NA"
        bvh = "NA"
        if context.object.animation_data:
            action = context.object.animation_data.action or None
        layout = self.layout
        if action:
            layout.menu("mocapmadness.actionmenu", text=action.info.description)
        else:
            layout.menu("mocapmadness.actionmenu")

        if action:
            self.draw_action_info(action)

from bl_operators.presets import AddPresetBase

class ImportBVH_preset_add(AddPresetBase, bpy.types.Operator):
    """Add a new render preset."""
    bl_idname = 'render.my_preset_add'
    bl_label = 'Add BVH Import Preset'
    bl_options = {'REGISTER', 'UNDO'}
    preset_menu = 'BVHImportPresetMenu_presets'
    preset_subdir = 'import_anim.bvh_mocap_madness'

    preset_defines = [
        "op = bpy.context.active_operator",
        ]

    preset_values = [
        "op.global_scale",
        "op.frame_start",
        "op.use_fps_scale",
        "op.rotate_mode",
        "op.axis_up",
        "op.axis_forward",
        "op.rig_only",
        "op.only_keep_first_rig",
        "op.only_rootbone_location",
        "op.use_frame_step",
        "op.action_only"
        ]

class ImportBVH(Operator, ImportHelper):
    """Load BVH motion capture file(s)"""
    bl_idname = "import_anim.bvh_mocap_madness"
    bl_label = "Import BVH"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".bvh"
    filter_glob = StringProperty(default="*.bvh", options={'HIDDEN'})

    files = CollectionProperty(
        name="BVH files",
        type=OperatorFileListElement,
        )

    file_collect = CollectionProperty(
        name="BVH files",
        type=BVHFile,
        )
    directory = StringProperty(subtype='DIR_PATH')

    target = EnumProperty(items=(
            ('ARMATURE', "Armature", ""),
            ('OBJECT', "Object", ""),
            ),
                name="Target",
                description="Import target type",
                default='ARMATURE')

    global_scale = FloatProperty(
            name="Scale",
            description="Scale the BVH by this value",
            min=0.0001, max=1000000.0,
            soft_min=0.001, soft_max=100.0,
            default=1.0,
            )
    frame_start = IntProperty(
            name="Start Frame",
            description="Starting frame for the animation",
            default=1,
            )
    use_fps_scale = BoolProperty(
            name="Scale FPS",
            description=("Scale the framerate from the BVH to "
                         "the current scenes, otherwise each "
                         "BVH frame maps directly to a Blender frame"),
            default=True,
            )
    use_cyclic = BoolProperty(
            name="Loop",
            description="Loop the animation playback",
            default=False,
            )
    rotate_mode = EnumProperty(
            name="Rotation",
            description="Rotation conversion",
            items=(('QUATERNION', "Quaternion",
                    "Convert rotations to quaternions"),
                   ('NATIVE', "Euler (Native)", ("Use the rotation order "
                                                 "defined in the BVH file")),
                   ('XYZ', "Euler (XYZ)", "Convert rotations to euler XYZ"),
                   ('XZY', "Euler (XZY)", "Convert rotations to euler XZY"),
                   ('YXZ', "Euler (YXZ)", "Convert rotations to euler YXZ"),
                   ('YZX', "Euler (YZX)", "Convert rotations to euler YZX"),
                   ('ZXY', "Euler (ZXY)", "Convert rotations to euler ZXY"),
                   ('ZYX', "Euler (ZYX)", "Convert rotations to euler ZYX"),
                   ),
            default='NATIVE',
            )

    axis_forward = EnumProperty(
            name="Forward",
            items=(('X', "X Forward", ""),
                   ('Y', "Y Forward", ""),
                   ('Z', "Z Forward", ""),
                   ('-X', "-X Forward", ""),
                   ('-Y', "-Y Forward", ""),
                   ('-Z', "-Z Forward", ""),
                   ),
            default='-Z',
            )

    axis_up = EnumProperty(
            name="Up",
            items=(('X', "X Up", ""),
                   ('Y', "Y Up", ""),
                   ('Z', "Z Up", ""),
                   ('-X', "-X Up", ""),
                   ('-Y', "-Y Up", ""),
                   ('-Z', "-Z Up", ""),
                   ),
            default='Y',
            )
    use_frame_step = BoolProperty(default=True,
                     name="Unit Frame Step",
                     description="Keyframe approx every frame")
    only_rootbone_location = BoolProperty(default=True,
                     name="Only Rootbone Locs",
                     description="Only add Location to Root Bone")

    rig_only = BoolProperty(
            name="Only Create Rig",
            description="Do Not Create any Action",
            default=False,
            )

    action_only = BoolProperty(
            name="Only Save Actions",
            description="Do Not Create any Rigs",
            default=False,
            )

    save_action = BoolProperty(
            name="Save the Action (Fake User)",
            description="Use Fake user to save action",
            default=True,
            )

    use_bone_groups = BoolProperty(
            name="Bone Groups",
            description="Group the Action Fcurves by bone name",
            default=True,
            )

    only_keep_first_rig = BoolProperty(
            name="Single Rig",
            description="Only Keep the First Rig",
            default=False,
            )

    count = 0

    def draw(self, context):
        layout = self.layout

        col = layout.column_flow(align=True)
        col.label('BVH Import Presets:')
        row = col.row(align=True)
        row.menu("BVHImportPresetMenu_presets",
                 text=bpy.types.BVHImportPresetMenu_presets.bl_label)
        row.operator("render.my_preset_add", text="", icon='ZOOMIN')
        row.operator("render.my_preset_add", text="", icon='ZOOMOUT').remove_active = True


        # check whether it's a subdir of CMU
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        '''
        if len(self.files) > 1:
            layout.label("FILES")
            for f in self.files:
                layout.label(f.name)
        '''
        row = layout.row()
        row.prop(self, "target")
        row = layout.row()
        row.prop(self, "axis_up")
        row = layout.row()
        row.prop(self, "axis_forward")
        row = layout.row()
        row.prop(self, "rotate_mode")
        row = layout.row()
        row.prop(self, "global_scale")
        box = layout.box()
        box.enabled = not self.action_only
        row = box.row()
        row.label("Rig", icon='ARMATURE_DATA')
        row = box.row()
        row.prop(self, "rig_only", toggle=True)
        row = box.row()
        #row.enabled = (len(self.files) > 1 and not self.action_only)
        row.prop(self, "only_keep_first_rig", toggle=True)

        box = layout.box()
        box.enabled = not self.rig_only
        row = box.row()
        row.label("Action", icon='ACTION')
        row = box.row()
        row.prop(self, "action_only", toggle=True)
        row = box.row()
        row.prop(self, "save_action", toggle=True)
        row = box.row()
        row.prop(self, "use_bone_groups", toggle=True)
        #row.enabled = self.only_keep_first_rig
        row = box.row()
        row.prop(self, "frame_start", toggle=True)
        row = box.row()
        row.prop(self, "use_fps_scale", toggle=True)
        if self.use_fps_scale:
            row = box.row()
            row.prop(self, "use_frame_step", toggle=True)
        row = box.row()
        row.prop(self, "only_rootbone_location", toggle=True)
        row = box.row()
        row.prop(self, "use_cyclic", toggle=True)
        '''


        cmubox = layout.box()
        cmubox.label("CMU", icon='INFO')
        if is_subdir(self.directory, addon_prefs.cmu_folder):
            row = box.row()
            #row.label("CMU")
            #row.label(basename(normpath(self.directory)))
            sub = "%s_01" % basename(normpath(self.directory))
            from .cmu import CMUMocaps
            cmu = CMUMocaps()
            found, subject, title = cmu.namefromcmu(sub)

            row.label("CMU: %s" % subject)
            for s in cmu.subjects():
                row = layout.row()
                row.label("SUBJECT %s" % s)

        elif addon_prefs.cmu_folder != "":
            row = box.row()
            op = row.operator("file.select_bookmark", text="CMU Base")
            op.dir = addon_prefs.cmu_folder

        '''

    def cmu(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        return addon_prefs.use_cmu_data

    invoke = ImportHelper.invoke
    '''
    def invoke(self, context, event):
        return {'FINISHED'}

    '''
    def execute(self, context):

        if self.cmu(context):
            from .cmu import CMUMocaps
            cmu = CMUMocaps()
        rna = {}
        kws = self.as_keywords(ignore=("files", "file_collect", "filter_glob",))
        for kw in kws:
            rna[kw] = getattr(self, kw)

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "file_collect",
                                            "action_only",
                                            "use_bone_groups",
                                            "save_action",
                                            "only_keep_first_rig",
                                            ))

        global_matrix = axis_conversion(from_forward=self.axis_forward,
                                        from_up=self.axis_up,
                                        ).to_4x4()

        keywords["global_matrix"] = global_matrix

        from . import import_bvh
        rigs = import_bvh.load(self, context, **keywords)
        # ONLY ACTION ONLY FIRST RIG ETC
        scene = context.scene
        scene.objects.active = rigs[0]
        # action settings
        actions_list = []
        for rig in rigs:
            actions_dic = {}
            rig.select = True
            arm = rig.data
            action = rig.animation_data.action
            # assoc rig with action
            found, subject, title = cmu.namefromcmu(action.name)
            actions_dic["name"] = action.name
            actions_dic["subject"] = subject
            actions_dic["description"] = title
            actions_list.append(actions_dic)
            action_info = arm.actions.add()
            action_info.name = action.name
            action_info.description = title

            action.info.name = action.name
            action.info.description = title
            action.info.subject = subject
            arm["bvh_import_settings"] = True
            arm["_RNA_UI"] = {"bvh_import_settings":rna}

            # save actions
            if self.save_action:
                action.use_fake_user = True
            # add the bone group names
            if self.use_bone_groups:
                zlb = [b.name for b in rig.pose.bones
                       if hasattr(b, "zero")
                      ]
                add_bone_groups(action, zlb)
        s = -1
        arm = None
        if self.action_only:
            s = 0
        elif self.only_keep_first_rig:
            arm = rigs[0].data
            arm['actions'] = actions_list
            s = 1
        if s > -1:
            for rig in rigs[s:]:
                scene.objects.unlink(rig)
                bpy.data.objects.remove(rig)
        return {'FINISHED'}


class ExportBVH(Operator, ExportHelper):
    """Save a BVH motion capture file from an armature"""
    bl_idname = "export_anim.bvh"
    bl_label = "Export BVH"

    filename_ext = ".bvh"
    filter_glob = StringProperty(
            default="*.bvh",
            options={'HIDDEN'},
            )

    global_scale = FloatProperty(
            name="Scale",
            description="Scale the BVH by this value",
            min=0.0001, max=1000000.0,
            soft_min=0.001, soft_max=100.0,
            default=1.0,
            )
    frame_start = IntProperty(
            name="Start Frame",
            description="Starting frame to export",
            default=0,
            )
    frame_end = IntProperty(
            name="End Frame",
            description="End frame to export",
            default=0,
            )
    rotate_mode = EnumProperty(
            name="Rotation",
            description="Rotation conversion",
            items=(('NATIVE', "Euler (Native)",
                    "Use the rotation order defined in the BVH file"),
                   ('XYZ', "Euler (XYZ)", "Convert rotations to euler XYZ"),
                   ('XZY', "Euler (XZY)", "Convert rotations to euler XZY"),
                   ('YXZ', "Euler (YXZ)", "Convert rotations to euler YXZ"),
                   ('YZX', "Euler (YZX)", "Convert rotations to euler YZX"),
                   ('ZXY', "Euler (ZXY)", "Convert rotations to euler ZXY"),
                   ('ZYX', "Euler (ZYX)", "Convert rotations to euler ZYX"),
                   ),
            default='NATIVE',
            )
    root_transform_only = BoolProperty(
            name="Root Transform Only",
            description="Only write out transform channels for the root bone",
            default=False,
            )

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'ARMATURE'

    def invoke(self, context, event):
        self.frame_start = context.scene.frame_start
        self.frame_end = context.scene.frame_end

        return super().invoke(context, event)

    def execute(self, context):
        if self.frame_start == 0 and self.frame_end == 0:
            self.frame_start = context.scene.frame_start
            self.frame_end = context.scene.frame_end

        keywords = self.as_keywords(ignore=("check_existing", "filter_glob"))

        from . import export_bvh
        return export_bvh.save(self, context, **keywords)

'''
Retargeting Operators / Panels
'''

class RemoveRestPoseRig(Operator):
    """ Creates a new set of bones with current pose as rest pose
    """
    bl_idname = "anim.remove_target_pose"
    bl_label = "Remove Rest Pose to Rig"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE':
            return False
        bones = [b for b in ob.pose.bones
                 if "bvh" in b.keys()]
        return len(ob.pose.bones) == 2 * len(bones)

    def execute(self, context):
        ob = context.object
        bones = [b.name for b in ob.pose.bones
                 if "bvh" in b.keys()]

        mode = ob.mode
        bpy.ops.object.mode_set(mode='EDIT')
        for b in bones:
            eb = ob.data.edit_bones[b]
            ob.data.edit_bones.remove(eb)
        bpy.ops.object.mode_set(mode=mode)
        return {'FINISHED'}


class CreateRestPoseRig(Operator):
    """ Creates a new set of bones with current pose as rest pose
    """
    bl_idname = "anim.target_pose"
    bl_label = "New Rest Pose to Rig"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE':
            return False
        bones = [b for b in ob.pose.bones
                 if "bvh" in b.keys()]
        return len(ob.pose.bones) != 2 * len(bones)

    def execute(self, context):
        try:
            ###################################################
            # dupe rig
            # for copy
            # add prop to point to original bone
            # make current pose the rest pose
            # join to original
            ####################################################

            scene = context.scene

            # original bvh rig
            bvhrig = context.active_object

            bpy.ops.object.mode_set()  # object mode
            bpy.ops.object.duplicate()
            ob = scene.objects.active
            print("DUPE", ob)

            #add a custom prop for each bone in the copy

            for bone in ob.pose.bones:
                bone['bvh'] = bone.name

            # apply the pose as rest pose
            bpy.ops.object.mode_set(mode='POSE')

            bpy.ops.pose.armature_apply()

            bpy.ops.object.mode_set(mode='OBJECT')

            # join back to original
            ob.select = True
            scene.objects.active = bvhrig
            scene.objects.active.select = True

            bpy.ops.object.join()

        except:
            print("ERROR")

        return {'FINISHED'}


class UpdateAction(Operator):
    """ Creates a new set of bones with current pose as rest pose
    """
    bl_idname = "anim.update_action"
    bl_label = "BVH action to new restpose rig"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE':
            return False
        bones = [b for b in ob.pose.bones
                 if "bvh" in b.keys()]
        return ((len(ob.pose.bones) == 2 * len(bones))
                and hasattr(ob, "animation_data")
                and hasattr(ob.animation_data, "action")
                and "bvh" not in ob.animation_data.action.keys())


    def execute(self, context):
        scene = context.scene
        TOL = 0.005

        ###########################################
        # action part
        ###########################################

        bvhrig = context.scene.objects.active
        bvh_arm = bvhrig.data

        action = bvhrig.animation_data.action

        newbones = [bone for bone
                    in bvhrig.pose.bones
                    if bone.get('bvh') is not None]
        # bone groups.. slows it down
        #USEBONEGROUPS = False
        USEBONEGROUPS = True

        if USEBONEGROUPS:
            # make a bone group
            bpy.ops.object.mode_set(mode='POSE')
            bvhgroup = bvhrig.pose.bone_groups.get("bvh")
            if bvhgroup is None:
                bpy.ops.pose.group_add()
                bvhgroup = bvhrig.pose.bone_groups.active
                bvhgroup.name = "bvh"
                bvhgroup.color_set = 'THEME04'

            # add to group

            for bone in newbones:
                bone.bone_group = bvhgroup

        frame = action.frame_range[0]

        while frame <= action.frame_range[1]:
            scene.frame_set(frame)
            #scene.update()
            for bone in newbones:
                apb = bvhrig.pose.bones.get(bone["bvh"])
                pb = bone

                if pb.parent is None:
                    match_pose_translation(pb, apb)
                    pb.keyframe_insert('location')

                if True:
                    match_pose_rotation(pb, apb)
                    #bpy.ops.object.mode_set(mode='POSE')
                    if pb.rotation_mode == 'QUATERNION':
                        pb.keyframe_insert('rotation_quaternion')

                    elif pb.rotation_mode == 'AXIS_ANGLE':
                        pb.keyframe_insert('rotation_axis_angle')

                    else:
                        pb.keyframe_insert('rotation_euler')

                    #match_pose_translation(pb, apb)
                    #bpy.ops.object.mode_set()
                    #match_pose_scale(pb, apb)
            frame = frame + 1

        action["bvh"] = True
        return {'FINISHED'}


class RetargetBVHRestPose(Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "New Rest Pose from Pose"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "BVH"

    def draw(self, context):
        layout = self.layout
        '''
        row = layout.row()
        row.operator("pose.snap_bones")
        '''
        row = layout.row()
        row.operator("anim.target_pose")
        row = layout.row()
        row.operator("anim.remove_target_pose")
        row = layout.row()
        row.operator("anim.update_action")


class SnapPoseboneVisual(Operator):
    """ Snaps selected bones to the visual transforms of the active bone.
    """
    bl_idname = "pose.snap_bones"
    bl_label = "Snap Bones to Bone"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.active_object != None and context.mode == 'POSE')

    def execute(self, context):
        use_global_undo = context.user_preferences.edit.use_global_undo
        context.user_preferences.edit.use_global_undo = False
        try:
            apb = context.active_pose_bone
            bones_sorted = []
            for bone in context.selected_pose_bones:
                bones_sorted += [bone]
            bones_sorted.sort(key=lambda bone: len(bone.parent_recursive))
            for pb in context.selected_pose_bones:
                if pb != apb:
                    match_pose_translation(pb, apb)
                    match_pose_rotation(pb, apb)
                    match_pose_scale(pb, apb)
        finally:
            context.user_preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}


class BVHImportPresetMenu_presets(bpy.types.Menu):
    '''Presets for render settings.'''
    bl_label = "BVH Import Presets"
    bl_idname = "BVHImportPresetMenu_presets"
    preset_subdir = "import_anim.bvh_mocap_madness"
    preset_operator = "script.execute_preset"

    draw = bpy.types.Menu.draw_preset
'''
Menu functions
'''


def menu_func_import(self, context):
    layout = self.layout
    layout.operator(ImportBVH.bl_idname,
                    text="(Enhanced) Motion Capture (.bvh)")


def menu_func_export(self, context):
    self.layout.operator(ExportBVH.bl_idname,
                         text="(Enhanced) Motion Capture (.bvh)")


def _get_action_info(self):
    print(self.name)
    return None

def register():
    bpy.types.Action.info = PointerProperty(type=ActionInfo)
    bpy.types.Armature.actions = CollectionProperty(type=ActionInfo)
    #cmu.register()
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)
    #cmu.unregister()

    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
