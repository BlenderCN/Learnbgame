# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Copyright (C) 2017 JOSECONSCO
# Created by JOSECONSCO

import bpy
import rna_keymap_ui
# import sys
# dir = 'C:\\Users\\JoseConseco\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages'
# if not dir in sys.path:
#     sys.path.append(dir )
# import ipdb

class VIEW3D_PT_Hair_Panel(bpy.types.Panel):
    bl_label = "Hair Tool"
    bl_idname = "hair_tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Tools"
    bl_context = "objectmode"

    drawAsMenu = False

    def draw(self, context):
        layout = self.layout
        if self.drawAsMenu:
            layout = self.layout.box()
            layout.label('Hair Tool')
        obj = context.active_object
        if obj is not None:
        # CONVERTERS / GENERATORS
            box = layout.box()
            box.label(  text='Convert/Generate')
            col = box.column(align=True)
            if obj.type == 'CURVE':
                col.operator("object.curve_edit", icon="FILE_REFRESH")
                col.operator("object.braid_make", icon="LINKED")
                if obj.data.bevel_object:
                    op=col.operator("object.curve_uv_refresh", icon="ASSET_MANAGER")
                    op.Seed = obj.hair_settings.uv_seed
                    col.operator("object.generate_ribbons", icon="OUTLINER_OB_SURFACE",text="Adjust Curve Profile")
                    row = col.row(align=True)
                    row.operator("object.ribbon_edit_profile", icon="LINKED")
                    row.operator("object.ribbon_close_profile", icon="UNLINKED")
                    row.operator("object.ribbon_duplicate_profile", icon="COPY_ID", text='')
                else:
                    col.operator("object.generate_ribbons", icon="OUTLINER_OB_SURFACE")
                    row = col.row(align=True)
                    row.operator("object.ribbon_edit_profile", icon="LINKED")
                    row.operator("object.ribbon_close_profile", icon="UNLINKED")
            if context.scene.grease_pencil or context.active_object.grease_pencil:  # true == use scene gp
                row = col.row(align=True)
                row.operator("object.curve_from_gp", icon="GREASEPENCIL")
                row.prop(context.scene, "GPSource", icon="SCENE_DATA", text='')
            if obj.type == 'MESH' and not obj.hair_settings.hair_mesh_parent:  # for non ribbon kind of  mesh
                col.operator("object.curves_from_mesh", icon="MESH_GRID")
                for mod in context.object.modifiers:
                    if mod.type == 'PARTICLE_SYSTEM' and mod.show_viewport and mod.particle_system.settings.type == "HAIR":  # use first visible
                        col.operator("object.hair_to_curves", icon="HAIR")
                        # col.prop_search(obj, "targetObjPointer", context.scene, "objects",icon="STRANDS",text='Target Curve')
                        col.operator("object.ribbons_from_ph_child", icon="HAIR")
                        break
                if context.scene.grease_pencil or context.active_object.grease_pencil:  # true == use scene gp
                    row = col.row(align=True)
                    row.operator("object.particle_from_gp", icon="GREASEPENCIL")
                    row.prop(context.scene, "GPSource", icon="SCENE_DATA", text='')

            if obj.type == 'MESH' and obj.hair_settings.hair_mesh_parent:  # for ribbon mesh
                col.operator("object.ribbon_edit", icon="FILE_REFRESH")
            if len(context.selected_objects)>1:
                col.operator("object.hair_from_curves", icon="FORCE_CURVE")

        # CURVE OPERATIONS
            if obj.type == 'CURVE':
                box = layout.box()
                box.label(text="CURVE OPERATIONS")
                col = box.column(align=True)
                col.operator("object.curve_taper", icon="PARTICLE_POINT")
                col = box.column(align=True)
                col.operator("object.curves_align_tilt", icon="SNAP_NORMAL")
                col.operator("object.embed_roots", icon="MOD_SCREW")
                col.prop_search(obj, "targetObjPointer", context.scene, "objects",icon="SNAP_NORMAL")
                col = box.column(align=True)
                col.operator("object.curves_smooth", icon="MOD_SMOOTH")
                col.operator("object.curves_smooth_tilt", icon="MOD_SMOOTH")
                col.operator("object.curves_smooth_radius", icon="MOD_SMOOTH")
                col.operator("object.curves_randomize_tilt", icon="FORCE_MAGNETIC")
                col.operator("object.curve_resample", icon="HAIR")
                col.operator("object.curve_simplify", icon="HAIR")

                # layout.prop(obj.hair_settings, 'hairUvMethod', icon="MOD_UVPROJECT")

        # MESH RIBBONS OPERATIONS
            if obj.type == 'MESH' and obj.hair_settings.hair_mesh_parent: #for ribbon mesh
                box = layout.box()
                box.label('RIBBONS OPERATIONS')
                col = box.column(align=True)
                col.operator("object.ribbon_weight", icon="WPAINT_HLT")
                col.operator("object.ribbon_vert_color_grad", icon="VPAINT_HLT")
                col.operator("object.ribbon_vert_color_random", icon="VPAINT_HLT")

            # layout.operator("object.cleanup_hair", icon="CANCEL")

# FOR CURVE EDIT MODE
class VIEW3D_EDIT_Hair_Panel(bpy.types.Panel):
    bl_label = "Hair Tool"
    bl_idname = "hair_tool_edit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Tools"

    bl_context = "curve_edit"

    def draw(self, context):
        self.drawAsMenu = False
        VIEW3D_PT_Hair_Panel.draw(self, context)


# FOR HOTKEY
class HairToolMenu(bpy.types.Menu):
    bl_idname = "object.hair_tool_menu"
    bl_label = "Hair Tool Menu Panel"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' or context.mode == 'EDIT' or context.mode=='EDIT_CURVE' or context.mode=='PAINT_VERTEX' or context.mode=='PAINT_WEIGHT'

    def draw(self, context):
        self.drawAsMenu = True
        if context.mode=='EDIT_CURVE':
            layout = self.layout
            obj = context.active_object

            box = layout.box()
            box.label(text="CURVE OPERATIONS")
            col = box.column(align=True)
            col.operator("object.curve_taper", icon="PARTICLE_POINT")
            col = box.column(align=True)
            col.operator("object.curves_align_tilt", icon="SNAP_NORMAL")
            col.operator("object.embed_roots", icon="MOD_SCREW")
            col.prop_search(obj, "targetObjPointer", context.scene, "objects", icon="SNAP_NORMAL")
            col = box.column(align=True)
            col.operator("object.curves_smooth", icon="MOD_SMOOTH")
            col.operator("object.curves_smooth_tilt", icon="MOD_SMOOTH")
            col.operator("object.curves_smooth_radius", icon="MOD_SMOOTH")
            col.operator("object.curves_randomize_tilt", icon="FORCE_MAGNETIC")
            col.operator("object.curve_resample", icon="HAIR")
            col.operator("object.curve_simplify", icon="HAIR")
            # layout.prop(obj.hair_settings, 'hairUvMethod', icon="MOD_UVPROJECT")
        else:
            VIEW3D_PT_Hair_Panel.draw(self, context)

    def check(self, context):
        return True
##########################         Addon Prefernedces                ###############################################

class hairToolPreferences(bpy.types.AddonPreferences):
    bl_idname = 'hair_tool'
    # expandCurveOper = bpy.props.BoolProperty( name="", description="",  default=False)
    # expandGenerators = bpy.props.BoolProperty( name="", description="",  default=False)
    flipUVRandom = bpy.props.BoolProperty( name="flip UV Randomly", description="Alter the ribbon look by randomly fliping uv on X axis",  default=True)
    hideGPStrokes = bpy.props.BoolProperty( name="Hide GP strokes", description="Hide Grease pencil strokes after converting\n "
                                                                                "them to curve or particle hair",  default=True)


    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'flipUVRandom')
        layout.prop(self, 'hideGPStrokes')
        box = layout.box()
        split = box.split()
        col = split.column()
        col.label('Hotkey')
        col.separator()
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        km = kc.keymaps['3D View']
        kmi = get_hotkey_entry_item(km, 'wm.call_menu_pie', "object.hair_tool_menu")
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
            col.operator(HairTool_Clear_Hotkeys.bl_idname, text="Clear hotkeys", icon='ZOOMOUT')
        else:
            col.label("No hotkey entry found")
            col.operator(HairTool_Add_Hotkey.bl_idname, text="Add hotkey entry", icon='ZOOMIN')

        row = layout.row()
        col = row.column()

        subcol = col.column(align = True)
        # subcol.label("Preferences:")
        # subcol.separator()
#### end  MOve TO pref file ####################################

addon_keymaps = []

def get_hotkey_entry_item(km, kmi_name, kmi_value):
    '''
    returns hotkey of specific type, with specific properties.name (keymap is not a dict, so referencing by keys is not enough
    if there are multiple hotkeys!)
    '''
    for i, km_item in enumerate(km.keymap_items):
        if km.keymap_items.keys()[i] == kmi_name:
            if km.keymap_items[i].properties.name == kmi_value:
                return km_item  #TODO: maybe this should return multiple keymaps...
    return None

def register_keymap():
    global addon_keymaps
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('wm.call_menu_pie', 'H', 'PRESS', ctrl=True, shift = True)
    kmi.properties.name = "object.hair_tool_menu"
    kmi.active = True
    addon_keymaps.append((km, kmi))
    km2 = kc.keymaps.new(name='Curve', space_type = 'VIEW_3D')
    kmi2 = km2.keymap_items.new('wm.call_menu_pie', 'H', 'PRESS', ctrl=True, shift=True)
    kmi2.properties.name = "object.hair_tool_menu"
    kmi2.active = True
    addon_keymaps.append((km2, kmi2))
    km3 = kc.keymaps.new(name='Vertex Paint', space_type='VIEW_3D')
    kmi3 = km3.keymap_items.new('wm.call_menu_pie', 'H', 'PRESS', ctrl=True, shift=True)
    kmi3.properties.name = "object.hair_tool_menu"
    kmi3.active = True
    addon_keymaps.append((km3, kmi3))
    km4 = kc.keymaps.new(name='Weight Paint', space_type='VIEW_3D')
    kmi4 = km4.keymap_items.new('wm.call_menu_pie', 'H', 'PRESS', ctrl=True, shift=True)
    kmi4.properties.name = "object.hair_tool_menu"
    kmi4.active = True
    addon_keymaps.append((km4, kmi4))


class HairTool_Add_Hotkey(bpy.types.Operator):
    ''' Add hotkey entry '''
    bl_idname = "hairtool.add_hotkey"
    bl_label = "Addon Preferences Example"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        register_keymap()
        self.report({'INFO'}, "Hotkey added in User Preferences -> Input -> 3D view")
        return {'FINISHED'}

class HairTool_Clear_Hotkeys(bpy.types.Operator):
    ''' Add hotkey entry '''
    bl_idname = "hairtool.clear_hotkey"
    bl_label = "Addon Preferences Example"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        unregister_keymap()
        self.report({'INFO'}, "Hotkey removed in User Preferences -> Input ")
        return {'FINISHED'}

def unregister_keymap():  #this only unregisters obj mode hotkey (what about curve mode hotkey)
    global addon_keymaps
    wm = bpy.context.window_manager
    for km,kmi in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        if km in wm.keyconfigs.addon.keymaps.values():
            wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()
