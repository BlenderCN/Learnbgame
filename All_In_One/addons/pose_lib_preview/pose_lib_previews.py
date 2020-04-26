if "bpy" in locals():
    import importlib
    if "prefs" in locals():
        importlib.reload(prefs)
else:
    from . import prefs


import os
import re
import bpy
from bpy.props import (StringProperty,
                       BoolProperty,
                       EnumProperty)
import bpy.utils.previews


# Dict to hold the ui previews collection
preview_collections = {}


# create the previews and an enum with label,
# tooltip and preview as custom icon
def generate_previews(self, context):
    enum_items = []

    if context is None:
        return enum_items

    obj = self
    pose_lib = obj.pose_library
    directory = pose_lib.pose_previews_dir

    pcoll = preview_collections["pose_previews"]

    if not obj.pose_previews_refresh:
        if directory == pcoll.pose_previews_dir:
            return pcoll.pose_previews

    num_pose_markers = len(pose_lib.pose_markers)

    if directory and os.path.isdir(bpy.path.abspath(directory)):
        if pcoll:
            pcoll.clear()
        image_paths = []
        for fn in os.listdir(bpy.path.abspath(directory)):
            if os.path.splitext(fn)[-1].lower() == ".png":
                image_paths.append(fn)

        # Only show as much thumbnails as there are poses
        if len(image_paths) >= num_pose_markers:
            image_paths = image_paths[:num_pose_markers]
        # If there are more poses then thumbnails, add placeholder
        if len(image_paths) < num_pose_markers:
            no_thumbnail = os.path.join(os.path.dirname(__file__),
                                        "thumbnails",
                                        "no_thumbnail.png")
            image_paths.append(no_thumbnail)

        # Determine how many extra placeholders are needed
        len_diff = num_pose_markers - len(image_paths)

        for i, name in enumerate(image_paths):
            filepath = os.path.join(bpy.path.abspath(directory), name)
            thumb = pcoll.load(filepath, filepath, 'IMAGE')

            label = os.path.splitext(name)[0]
            match = re.match(r"([0-9]+)[-_\.]?(.*)?", label)
            try:
                num = int(match.groups()[0])
            except (ValueError, TypeError, IndexError, AttributeError):
                num = i + 1
            try:
                pose_name = match.groups()[1]
            except (TypeError, IndexError, AttributeError):
                pose_name = "(no thumbnail)"
            if pose_name:
                pose_name = re.sub(r"[_\.]", " ", pose_name)
            label = "{num} {pose_name}".format(num=num, pose_name=pose_name)

            enum_items.append((label, label, label, thumb.icon_id, i))
            # Add extra placeholder thumbnails if needed
            if name == image_paths[-1]:
                for j in range(len_diff):
                    label = "{num} (no thumbnail)".format(num=i + j + 2)
                    enum_items.append((label, label, label,
                                       thumb.icon_id,
                                       i + j + 1))

    pcoll.pose_previews = enum_items
    pcoll.pose_previews_dir = directory
    return pcoll.pose_previews


def get_pose_bone_groups(self, context):
    enum_items = []

    if context is None:
        return enum_items

    obj = self
    bone_groups = obj.pose.bone_groups
    if bone_groups:
        for bg in bone_groups:
            enum_items.append((bg.name, bg.name, ""))

    return enum_items


def filepath_update(self, context):
    bpy.ops.poselib.refresh_thumbnails()


def update_pose(self, context):
    value = self['pose_previews']
    obj = self

    if obj.pose_apply_options in ('ALL', 'BONEGROUP'):
        selected_bones = [pb.name for pb in context.selected_pose_bones]

    if obj.pose_apply_options == 'ALL':
        for bone in obj.data.bones:
            bone.select = True
    elif obj.pose_apply_options == 'BONEGROUP':
        for bone in obj.data.bones:
            bone.select = False
        bone_group = obj.pose_bone_groups
        for bone in obj.pose.bones:
            try:
                if bone.bone_group.name.lower() == bone_group.lower():
                    obj.data.bones[bone.name].select = True
            except AttributeError:
                pass

    if self.pose_library.pose_markers:
        bpy.ops.poselib.apply_pose(pose_index=value)

    if obj.pose_apply_options in ('ALL', 'BONEGROUP'):
        for bone in obj.data.bones:
            if bone.name in selected_bones:
                bone.select = True
            else:
                bone.select = False


class PoseLibSearch(bpy.types.PropertyGroup):
    pose = bpy.props.StringProperty(name="previews search", default="")


class PoseLibPreviewRefresh(bpy.types.Operator):

    """Refresh Pose Library thumbnails of active Pose Library"""

    bl_description = "Refresh Pose Library thumbnails"
    bl_idname = "poselib.refresh_thumbnails"
    bl_label = "Refresh"
    bl_space_type = 'PROPERTIES'

    def execute(self, context):
        obj = context.object
        obj.pose_previews_refresh = True
        enum_items = generate_previews(context.object, context)
        obj.pose_previews_refresh = False
        scene = context.scene
        scene.pose_search.clear()
        for i in enum_items:
            item = scene.pose_search.add()
            item.name = i[0]

        return {'FINISHED'}


class PoseLibPreviewPanel(bpy.types.Panel):

    """Creates a Panel in the armature context of the properties editor"""
    bl_label = "Pose Library Previews"
    bl_idname = "DATA_PT_pose_previews"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        user_prefs = context.user_preferences
        addon_prefs = user_prefs.addons[__package__].preferences
        obj = context.object

        return (obj and obj.type == 'ARMATURE'
                and addon_prefs.add_3dview_prop_panel)

    def draw(self, context):
        user_prefs = context.user_preferences
        addon_prefs = user_prefs.addons[__package__].preferences
        show_labels = addon_prefs.show_labels
        obj = context.object
        pose = obj.pose
        rows = 4
        pose_lib = obj.pose_library

        layout = self.layout
        col = layout.column(align=False)
        col.template_ID(obj, "pose_library")
        if obj.pose_library:
            col.separator()
            sub_col = col.column(align=True)
            sub_col.template_icon_view(obj, "pose_previews",
                                       show_labels=show_labels)
            sub_col.prop_search(obj, "pose_previews",
                                context.scene, "pose_search",
                                text="", icon='VIEWZOOM')
            col.separator()
            row = col.row()
            row.prop(obj, "pose_apply_options", expand=True)
            # col.template_list("UI_UL_list", "bone_groups", pose, "bone_groups", pose.bone_groups, "active_index", rows=rows)
            # col.prop_menu_enum(obj.pose, "bone_groups")
            row = col.row()
            row.prop(obj, "pose_bone_groups", text="")
            if obj.pose_apply_options == 'BONEGROUP':
                row.enabled = True
            else:
                row.enabled = False
            col.separator()
            col.operator("poselib.refresh_thumbnails", icon='FILE_REFRESH')
            col.prop(pose_lib, "pose_previews_dir")
        if not obj.mode == 'POSE':
            layout.enabled = False


class PoseLibPreviewPropertiesPanel(bpy.types.Panel):

    """Creates a Panel in the 3D View Properties panel"""
    bl_label = "Pose Library"
    bl_idname = "VIEW3D_PT_pose_previews"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        user_prefs = context.user_preferences
        addon_prefs = user_prefs.addons[__package__].preferences
        obj = context.object

        return (obj and obj.type == 'ARMATURE'
                and addon_prefs.add_3dview_prop_panel)

    def draw(self, context):
        user_prefs = context.user_preferences
        addon_prefs = user_prefs.addons[__package__].preferences
        show_labels = addon_prefs.show_labels
        obj = context.object
        pose = obj.pose
        rows = 4
        pose_lib = obj.pose_library

        layout = self.layout
        col = layout.column(align=False)
        col.template_ID(obj, "pose_library")
        if obj.pose_library:
            col.separator()
            sub_col = col.column(align=True)
            sub_col.template_icon_view(obj, "pose_previews",
                                       show_labels=show_labels)
            sub_col.prop_search(obj, "pose_previews",
                                context.scene, "pose_search",
                                text="", icon='VIEWZOOM')
            col.separator()
            row = col.row()
            row.prop(obj, "pose_apply_options", expand=True)
            # col.template_list("UI_UL_list", "bone_groups", pose, "bone_groups", pose.bone_groups, "active_index", rows=rows)
            # col.prop_menu_enum(obj.pose, "bone_groups")
            row = col.row()
            row.prop(obj, "pose_bone_groups", text="")
            if obj.pose_apply_options == 'BONEGROUP':
                row.enabled = True
            else:
                row.enabled = False
            col.separator()
            col.operator("poselib.refresh_thumbnails", icon='FILE_REFRESH')
            col.prop(pose_lib, "pose_previews_dir")
        if not obj.mode == 'POSE':
            layout.enabled = False


def register():
    bpy.types.Scene.pose_search = bpy.props.CollectionProperty(
        type=PoseLibSearch)
    bpy.types.Object.pose_previews = EnumProperty(
        items=generate_previews,
        update=update_pose)
    bpy.types.Object.pose_previews_refresh = BoolProperty(
        name="Refresh thumbnails",
        default=False)
    bpy.types.Object.pose_apply_options = EnumProperty(
        name="Apply pose to",
        items=[('ALL', 'All', 'Apply the pose to all bones'),
               ('SELECTED', 'Selected', 'Apply the pose to the selected bones'),
               ('BONEGROUP', 'Bone Group', 'Apply the pose to the bones in a bone group')],
        default='ALL')
    bpy.types.Object.pose_bone_groups = EnumProperty(
        name="Bone Group",
        items=get_pose_bone_groups)
    bpy.types.Action.pose_previews_dir = StringProperty(
        name="Thumbnail Path",
        subtype='DIR_PATH',
        default="",
        update=filepath_update)

    pcoll = bpy.utils.previews.new()
    pcoll.pose_previews_dir = ""
    pcoll.pose_previews = ()
    preview_collections["pose_previews"] = pcoll


def unregister():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    del bpy.types.Object.pose_previews
    del bpy.types.Action.pose_previews_dir
