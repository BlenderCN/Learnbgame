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

# <pep8 compliant>

# Tools for project "BERG 2015 - X-Plore"


bl_info = {
    "name": "BERG tools",
    "description": "BERG tools",
    "author": "jasperge",
    "version": (0, 1),
    "blender": (2, 72, 0),
    "location": "View 3D > Toolbar",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}


from os import path
import pickle
import time
from math import radians
import bpy
from bpy.app.handlers import persistent
from bpy.props import (StringProperty,
                       CollectionProperty,
                       BoolProperty,
                       FloatProperty)
from bpy_extras.io_utils import ImportHelper


class SCENE_OT_bergtools_import_anim(bpy.types.Operator, ImportHelper):

    """Import animation and assign to linked objects. Create handler to """
    """assign actions (again) when loading the file."""

    bl_description = "Import animation for linked objects."
    bl_idname = "scene.bergtools_animate_linked_objects"
    bl_label = "Import BERG animation"
    bl_options = {'PRESET', 'UNDO'}

    directory = StringProperty(
        maxlen=1024,
        subtype='DIR_PATH',
        options={'HIDDEN', 'SKIP_SAVE'})
    files = CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'})
    filename_ext = ".anim"
    filter_glob = StringProperty(default="*.anim", options={'HIDDEN'})
    location = BoolProperty(
        name="Location",
        description="Import location data",
        default=True)
    rotation = BoolProperty(
        name="Rotation",
        description="Import rotation data",
        default=True)
    scale = BoolProperty(
        name="Scale",
        description="Import scale data",
        default=False)
    visibility = BoolProperty(
        name="Visibility",
        description="Import visibility data",
        default=True)
    only_selected = BoolProperty(
        name="Only selected",
        description="Import only animation data for the selected objects",
        default=False)

    @classmethod
    def poll(cls, context):
        obj = bpy.context.object
        return obj and obj.dupli_group and obj.dupli_group.library

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.separator()
        row = col.row(align=True)
        row.prop(self, "location", toggle=True)
        row.prop(self, "rotation", toggle=True)
        row.prop(self, "scale", toggle=True)
        row = col.row(align=True)
        row.prop(self, "visibility", toggle=True)
        # row.prop(self, "only_selected", toggle=True)

    def execute(self, context):
        anim_file = path.join(self.directory, self.files[0].name)
        print(import_anim_data(anim_file,
                               self.location,
                               self.rotation,
                               self.scale,
                               self.visibility,
                               self.only_selected))

        return {'FINISHED'}


def print_progress(progress, min=0, max=100, barlen=50, item=""):
    if max <= min:
        return
    total_len = max - min
    bar_progress = int((progress - min) * barlen / total_len) * "="
    bar_empty = (barlen - int((progress - min) * barlen / total_len)) * " "
    percentage = "".join((str(int((progress - min) / total_len * 100)), "%"))
    item = "".join(("  --  ", item))
    bar = "".join(("[", bar_progress, bar_empty, "]", " ", percentage, item))
    bar = "".join((bar, (130 - len(bar)) * " "))
    print(bar, end="\r")


def convert_roo(roo):
    roo_list = list(roo)
    index_x = roo_list.index('x')
    index_y = roo_list.index('y')
    index_z = roo_list.index('z')
    roo_list[index_x] = 'x'
    roo_list[index_y] = 'z'
    roo_list[index_z] = 'y'
    return "".join(roo_list).upper()


def import_anim_file(anim_file):
    if not path.isfile(anim_file):
        raise IOError("{f} not found".format(f=anim_file))
    with open(anim_file, "rb") as f:
        frame_range = pickle.load(f)
        anim_data = pickle.load(f)
        return (frame_range, anim_data)


def create_action(obj):
    obj_action = bpy.data.actions.new("{obj}_action".format(obj=obj.name))
    obj_action.name = "{obj}_action".format(obj=obj.name)
    if not obj.animation_data:
        obj.animation_data_create()
    obj.animation_data.action = obj_action
    # obj_action.use_fake_user = True

    return obj_action


def set_keyframes(*args, **kwargs):
    obj = args[0]
    frame = args[1]
    loc = kwargs.setdefault("loc", None)
    roo = kwargs.setdefault("roo", None)
    rot = kwargs.setdefault("rot", None)
    scale = kwargs.setdefault("scale", None)
    vis = kwargs.setdefault("vis", None)
    use_visibility = kwargs.setdefault("use_visibility", False)

    if loc:
        obj.location = (loc[0], -loc[2], loc[1])
        obj.keyframe_insert('location', frame=frame, group="LocRotScale")
    if rot:
        obj.rotation_mode = convert_roo(roo)
        obj.rotation_euler = (radians(rot[0]),
                              radians(-rot[2]),
                              radians(rot[1]))
        obj.keyframe_insert('rotation_euler', frame=frame, group="LocRotScale")
    if scale:
        obj.scale = (scale[0], scale[2], scale[1])
        obj.keyframe_insert('scale', frame=frame, group="LocRotScale")
    if use_visibility:
        obj.hide = obj.hide_render = not(vis)
        obj.keyframe_insert('hide', frame=frame)
        obj.keyframe_insert('hide_render', frame=frame)


def timeline_view_all():
    for window in bpy.context.window_manager.windows:
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type == 'TIMELINE':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            override = {'window': window,
                                        'screen': screen,
                                        'area': area,
                                        'region': region,
                                        'scene': bpy.context.scene}
                            bpy.ops.time.view_all(override)
                            break


def set_frame_range(frame_range):
    start_frame, end_frame = frame_range
    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame
    timeline_view_all()


def write_info_to_scene(anim_file):
    try:
        info = bpy.context.scene["bergtools_animfile_info"].to_dict()
    except KeyError:
        info = dict()
    name = path.basename(anim_file)
    relpath = bpy.path.relpath(anim_file)
    mtime = path.getmtime(anim_file)
    file_info = dict()
    file_info["relpath"] = relpath
    file_info["mtime"] = mtime
    info[name] = file_info
    bpy.context.scene["bergtools_animfile"] = info


# def update_anim():
#     info = bpy.context.scene['bergtools_animfile_info']


def create_load_handler():
    text = """
import bpy

def berg_animation_handler(*args):
    groups = []
    for obj in bpy.context.scene.objects:
        if obj.dupli_group and obj.dupli_group.library:
            groups.append(obj)
    for group in groups:
        group_objects = group.dupli_group.objects
        for action in bpy.data.actions:
            obj_name = action.name[:-7]
            try:
                group_objects[obj_name].animation_data_create()
                group_objects[obj_name].animation_data.action = action
                # print("assigned {} to {}".format(action.name, obj_name))
            except KeyError:
                # print("Could not find object {} in dupli group".format(obj_name))
                pass
    # print("Assigned actions")

try:
    bpy.app.handlers.load_post.remove(berg_animation_handler)
except ValueError:
    pass
bpy.app.handlers.load_post.append(berg_animation_handler)
"""

    if not "berg_animation_handler.py" in bpy.data.texts:
        handler_text = bpy.data.texts.new("berg_animation_handler.py")
        handler_text.use_module = True
        handler_text.from_string(text)


def import_anim_data(*args):
    anim_file = args[0]
    use_location = args[1]
    use_rotation = args[2]
    use_scale = args[3]
    use_visibility = args[4]
    only_selected = args[5]

    error_list = []
    start_time = time.time()
    print("Parsing file...")
    frame_range, anim_data = import_anim_file(anim_file)
    set_frame_range(frame_range)
    # if only_selected:
    #     obj_list = [obj.name for obj in bpy.context.selected_objects]
    # else:
    #     obj_list = bpy.data.objects
    obj_list = [obj.name for obj in bpy.context.object.dupli_group.objects]
    print()
    for i, obj_name in enumerate(anim_data.keys()):
        print_progress(i, max=len(anim_data.keys()) - 1, item=obj_name)
        if obj_name in obj_list:
            obj = bpy.data.objects[obj_name]
            create_action(obj)
            for info in anim_data[obj_name]:
                frame, loc, roo, rot, scale, vis = info
                set_keyframes(obj, frame,
                              loc=loc * use_location,
                              roo=roo,
                              rot=rot * use_rotation,
                              scale=scale * use_scale,
                              vis=vis,
                              use_visibility=use_visibility)
        else:
            if not only_selected:
                error_list.append(obj_name)

    s = time.time() - start_time
    write_info_to_scene(anim_file)
    create_load_handler()
    print()
    for obj_name in error_list:
        print("Skipped {obj}, did not find it in the current scene...".format(obj=obj_name))
    return "Animation data imported from {f} in {s:.2f} seconds\n".format(f=anim_file, s=s)


class SetNormalAngle(bpy.types.Operator):
    """Set the normal angle of the selected objects and turn on auto smooth"""
    bl_idname = "object.bergtools_set_normal_angle"
    bl_label = "Set normal angle"
    bl_options = {'REGISTER', 'UNDO'}

    normal_angle = FloatProperty(
        name="Angle",
        default=40,
        min=0,
        max=180)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        wm = bpy.context.window_manager
        self.normal_angle = wm.berg_tools_settings.normal_angle
        for obj in bpy.context.selected_objects:
            bpy.ops.object.shade_smooth()
            try:
                obj.data.use_auto_smooth = True
                obj.data.auto_smooth_angle = radians(self.normal_angle)
            except AttributeError:
                pass
        return {'FINISHED'}


class HideRelationshipLines(bpy.types.Operator):
    """Hide relationship lines in every 3D View"""
    bl_idname = "wm.bergtools_hide_relationship_lines"
    bl_label = "Hide relationship lines"

    def execute(self, context):
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.show_relationship_lines = False
        return {'FINISHED'}


class ShowRelationshipLines(bpy.types.Operator):
    """Show relationship lines in every 3D View"""
    bl_idname = "wm.bergtools_show_relationship_lines"
    bl_label = "Show relationship lines"

    def execute(self, context):
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.show_relationship_lines = True
        return {'FINISHED'}


class BergToolsSettings(bpy.types.PropertyGroup):
    normal_angle = FloatProperty(
        name="Angle",
        default=40,
        min=0,
        max=180)


class BergToolsPanel(bpy.types.Panel):
    bl_label = "BERG tools"
    bl_idname = "VIEW3D_PT_berg_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Tools'

    def draw(self, context):

        layout = self.layout
        wm = bpy.context.window_manager

        col = layout.column()
        col.operator("scene.bergtools_animate_linked_objects")
        col.separator()
        row = col.row(align=True)
        row.operator("object.bergtools_set_normal_angle")
        row.prop(wm.berg_tools_settings, "normal_angle")
        col.separator()
        col.label("Relationship lines:")
        row = col.row(align=True)
        row.operator("wm.bergtools_show_relationship_lines", text="On")
        row.operator("wm.bergtools_hide_relationship_lines", text="Off")


# @persistent
# def update_berg_settings(context):
#     wm = bpy.context.window_manager
#     bt_settings = wm.berg_tools_settings
#     bt_settings.normal_angle = bpy.data.scenes[0].get(
#         "jasperge_tools_file_version", 1)


def menu_func_import(self, context):
    self.layout.operator(SCENE_OT_bergtools_import_anim.bl_idname,
                         text="Import BERG animation")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.WindowManager.berg_tools_settings = bpy.props.PointerProperty(type=BergToolsSettings)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    del bpy.types.WindowManager.berg_tools_settings


if __name__ == "__main__":
    register()
