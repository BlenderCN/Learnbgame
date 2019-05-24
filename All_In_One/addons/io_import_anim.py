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
    "name": "Import animation",
    "author": "Jasper van Nieuwenhuizen",
    "version": (0, 1),
    "blender": (2, 7, 0),
    "location": "File > Import > Import animation",
    "description": "Import animation data to matching objects",
    "warning": "wip",
    "wiki_url": "",
    "tracker_url": "",
    "support": 'COMMUNITY',
    "category": "Learnbgame",
}


from os import path
import pickle
import time
from math import radians
import bpy
from bpy.props import (StringProperty,
                       CollectionProperty,
                       BoolProperty)
from bpy_extras.io_utils import ImportHelper


class ImportAnim(bpy.types.Operator, ImportHelper):

    '''Import object(s)'''
    bl_idname = "import_scene.anim"
    bl_label = "Import animation"
    bl_options = {'PRESET', 'UNDO'}

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
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

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.separator()
        #col.label("Import options")
        row = col.row(align=True)
        row.prop(self, "location", toggle=True)
        row.prop(self, "rotation", toggle=True)
        row.prop(self, "scale", toggle=True)
        row = col.row(align=True)
        row.prop(self, "visibility", toggle=True)
        row.prop(self, "only_selected", toggle=True)

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
    #print(int(progress * barlen / total_len), end='\r')
    bar_progress = int((progress - min) * barlen / total_len) * "="
    bar_empty = (barlen - int((progress - min) * barlen / total_len)) * " "
    percentage = "".join((str(int((progress - min) / total_len * 100)), "%"))
    item = "".join(("  --  ", item, 30 * " "))
    print("".join((" [", bar_progress, bar_empty, "]", " ", percentage, item)), end="\r")


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
        #frame_range = eval(f.readline())
        #anim_data = eval(f.readline())
        return (frame_range, anim_data)


def create_action(obj):
    obj_action = bpy.data.actions.new("{obj}_action".format(obj=obj.name))
    if not obj.animation_data:
        obj.animation_data_create()
    obj.animation_data.action = obj_action


def set_keyframes(obj, frame, loc=None, roo=None, rot=None, scale=None, vis=None, use_visibility=False):
    if loc:
        obj.location = (loc[0], -loc[2], loc[1])
        obj.keyframe_insert('location', frame=frame, group="LocRotScale")
    if rot:
        #obj.rotation_mode = roo.upper()
        obj.rotation_mode = convert_roo(roo)
        obj.rotation_euler = (radians(rot[0]), radians(-rot[2]), radians(rot[1]))
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


def import_anim_data(anim_file, use_location, use_rotation, use_scale, use_visibility, only_selected):
    start_time = time.time()
    print("Parsing file...")
    frame_range, anim_data = import_anim_file(anim_file)
    set_frame_range(frame_range)
    if only_selected:
        obj_list = [obj.name for obj in bpy.context.selected_objects]
    else:
        obj_list = bpy.data.objects
    print()
    for i, obj_name in enumerate(anim_data.keys()):
        print_progress(i, max=len(anim_data.keys()) - 1, item=obj_name)
        if obj_name in obj_list:
            #print("Processing {obj}...".format(obj=obj_name))
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
                              use_visibility = use_visibility)
        else:
            if not only_selected:
                print("Skipping {obj}, did not find it in the current scene...".format(obj=obj_name))

    s = time.time() - start_time
    return "Animation data imported from {f} in {s:.2f} seconds\n".format(f=anim_file, s=s)


def menu_func_import(self, context):
    self.layout.operator(ImportAnim.bl_idname, text="Import animation")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
