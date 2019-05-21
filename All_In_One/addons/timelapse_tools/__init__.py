# Copyright 2015 Bassam Kurdali / urchn.org
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
# topsort.py copyright 2014 Sunlight Labs/ written by Paul Tagliometti

bl_info = {
    "name": "Timelapse Toolbox",
    "author": "Bassam Kurdali",
    "version": (1, 0, 5),
    "blender": (2, 80, 0),
    "location": "View3D > Ctrl F1, Add Menu",
    "description": "Tools to Help Timelapse Animators",
    "warning": "",
    "wiki_url": "http://wiki.urchn.org/wiki/timelapse_tools",
    "category": "Learnbgame",
    }

if "bpy" in locals():
    import importlib
    importlib.reload(drive_curves)
    importlib.reload(cutters)
    importlib.reload(maskers)
    importlib.reload(group_shaders)
else:
    from . import drive_curves
    from . import cutters
    from . import maskers
    from . import group_shaders

import bpy

class VIEW3D_PIE_Timelapse_Tools(bpy.types.Menu):
    bl_label = "Timelapse Tools"

    @classmethod
    def poll(cls, context):
        return context.mode in ('OBJECT', 'POSE')

    def draw(self, context):
        pie = self.layout.menu_pie()
        pbone = context.active_pose_bone
        bone_selected = pbone and context.active_object.type == 'ARMATURE'
        if bone_selected and len(pbone.keys()) == 2:
            key = [key for key in pbone.keys() if not key == '_RNA_UI'][0]
            pie.operator_context = 'EXEC_DEFAULT'
            curves_to_drivers = pie.operator(
                "anim.copy_curves_drivers", text="Curves To Drivers")
            curves_to_drivers.driver = key
            curves_to_drivers.forward = True
            drivers_to_curves = pie.operator(
                "anim.copy_curves_drivers", text="Drivers To Curves")
            drivers_to_curves.driver = key
            drivers_to_curves.forward = False
        elif bone_selected and len(pbone.keys()) > 2:
            pie.operator_context = 'INVOKE_DEFAULT'
            pie.operator(
                "anim.copy_curves_drivers", text="Drive Curves").forward = True
            pie.operator(
                "anim.copy_curves_drivers",
                text="Curve Drivers").forward = False
        else:
            pie.operator(
                "anim.copy_curves_drivers",
                text="Activate a Bone").forward = True
            pie.operator(
                "anim.copy_curves_drivers",
                text="Activate a Bone").forward = False
        pie.operator(
            "anim.hide_to_render", text="Render To Display").forward = False
        pie.operator(
            "anim.hide_to_render", text="Display To Render").forward = True
        pie.operator("anim.undrive", text="Un-Drive")
        pie.operator("anim.uncurve", text="Un-Curve")
        pie.operator("object.boolean_state", text="Show Bools")


class NODE_EDITOR_PIE_Timelapse_Tools(bpy.types.Menu):
    bl_label = "Node Timelapse Tools"

    @classmethod
    def poll (cls, context):
        space = context.space_data
        return (
            space.type == 'NODE_EDITOR' and
            space.tree_type == 'ShaderNodeTree')

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator_context = 'INVOKE_DEFAULT'
        pie.operator(
            group_shaders.GroupAnimatedMake.bl_idname,
            text="Create a Time-driven Group")
        pie.operator(
            group_shaders.GroupRamp.bl_idname,
            text="Turn Ramp Node into a Group")
        pie.operator(
            group_shaders.AddRampChannel.bl_idname,
            text="Add a new Channel to ramp group")


def add_hotkey(
            kc, mode_name, space_type, ot, key,
            shift=False, ctrl=False, alt=False):
        km = kc.keymaps.new(name=mode_name, space_type=space_type)
        kmi = km.keymap_items.new(
            ot, key, 'PRESS',
            shift=shift, ctrl=ctrl, alt=alt)


def del_hotkey(kc, mode_name, ot):
    km = kc.keymaps[mode_name]
    for kmi in km.keymap_items:
        if kmi.idname == ot:
            km.keymap_items.remove(kmi)


def menu_func_group_animated(self, context):
    """ Add the Operator to the Menu """
    self.layout.operator(
        group_shaders.GroupAnimatedMake.bl_idname,
        text="Create a Time-driven Group")
    self.layout.operator(
        group_shaders.GroupRamp.bl_idname,
        text= "Turn Ramp Node into a Group")
    self.layout.operator(
        group_shaders.AddRampChannel.bl_idname,
        text="Add a new Channel to ramp group")


def register():
    drive_curves.register()
    cutters.register()
    maskers.register()
    group_shaders.register()
    bpy.utils.register_class(VIEW3D_PIE_Timelapse_Tools)
    bpy.utils.register_class(NODE_EDITOR_PIE_Timelapse_Tools)
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        for mode in ("Object Mode", "Pose"):
            km = kc.keymaps.new(name=mode)
            kmi = km.keymap_items.new(
                'wm.call_menu_pie', type='F1', value='PRESS', ctrl=True)
            kmi.properties.name = 'VIEW3D_PIE_Timelapse_Tools'
        km = kc.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
        kmi = km.keymap_items.new(
            'wm.call_menu_pie', type='F1', value='PRESS', ctrl=True)
        kmi.properties.name = 'NODE_EDITOR_PIE_Timelapse_Tools'
        add_hotkey(
            kc, 'Node Editor', 'NODE_EDITOR',
            group_shaders.GroupAnimatedMake.bl_idname, "T",
            shift=True, ctrl=True)
        add_hotkey(
            kc, 'Node Editor', 'NODE_EDITOR',
            group_shaders.GroupRamp.bl_idname, "R",
            shift=True, ctrl=True)
    bpy.types.NODE_MT_node.append(menu_func_group_animated)

def unregister():
    bpy.types.NODE_MT_node.remove(menu_func_group_animated)
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        for mode in ("Object Mode", "Pose"):
            km = kc.keymaps[mode]
            for kmi in km.keymap_items:
                if kmi.name == 'Call Pie Menu' and\
                        kmi.properties.name == 'VIEW3D_PIE_Timelapse_Tools':
                    km.keymap_items.remove(kmi)
        km = kc.keymaps['Node Editor']
        for kmi in km.keymap_items:
            if (
                    kmi.name == 'Call Pie Menu' and
                    kmi.properties.name == 'NODE_EDITOR_PIE_Timelapse_Tools'):
                km.keymap_items.remove(kmi)
        del_hotkey(
            kc, 'Node Editor', group_shaders.GroupAnimatedMake.bl_idname)
        del_hotkey(kc, 'Node Editor', group_shaders.GroupRamp.bl_idname)
    bpy.utils.unregister_class(VIEW3D_PIE_Timelapse_Tools)
    bpy.utils.unregister_class(NODE_EDITOR_PIE_Timelapse_Tools)
    drive_curves.unregister()
    cutters.unregister()
    maskers.unregister()
    group_shaders.unregister()

if __name__ == "__main__":
    register()
