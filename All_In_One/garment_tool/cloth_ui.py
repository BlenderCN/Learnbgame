'''
Copyright (C) 2017 JOSECONSCO
Created by JOSECONSCO

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy

class GTOOL_PT_ClothTools(bpy.types.Panel):
    bl_idname = "GTOOL_PT_ClothTools"
    bl_label = "Pattern Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Garment'
    # bl_context = 'objectmode'

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw(self, context):
        cloth_garment_data = context.scene.cloth_garment_data
        layout = self.layout

        row = layout.row(align=True)
        row.operator('curve.curve_symmetrize', icon='ARROW_LEFTRIGHT')
        row.operator('curve.curve_split_gm', icon='MOD_BEVEL')
        row = layout.row(align=True)
        row.operator('curve.pattern_flip', icon='MOD_MIRROR')
        row.operator('curve.duplicate_sewed', icon='DUPLICATE')


class GTOOL_PT_ClothPanel(bpy.types.Panel):
    bl_idname = "GTOOL_PT_ClothPanel"
    bl_label = "Garment Tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Garment'
    bl_context = 'objectmode'

    def draw(self, context):
        cloth_garment_data = context.scene.cloth_garment_data
        layout = self.layout
        row = layout.row(align=True)
        row.label(text='GARMENTS')
        row.alignment = 'RIGHT'
        row.operator('garment.add_garment', text='', icon='ADD')
        for garment_index, garment in enumerate(cloth_garment_data):
            
            box1 = layout.box()
            row = box1.row(align=True)
            row.alignment = 'EXPAND'
            tri_ico = 'TRIA_DOWN' if garment.expand_garment else "TRIA_RIGHT"
            
            row.prop(garment, "expand_garment", icon=tri_ico, icon_only=True,  emboss=False)
            row.alignment = 'EXPAND'
            row.prop(garment, 'name', text="")
            row.operator('garment.remove_garment', icon='REMOVE', text='').garment_index = garment_index
            oper = row.operator('cloth.raycast_edit_sewing', icon='LINKED', text='')
            oper.garment_index = garment_index
            oper.edit_patter_sewing = -1
            row.operator("garment.cleanup", text="", icon="GHOST_ENABLED").garment_index = garment_index

            row = box1.row(align=True)
            row.operator('garment.simulate_cloth', icon='PREVIEW_RANGE').garment_index = garment_index
            row.operator('cloth.save_to_shape', icon='OUTLINER_OB_ARMATURE').garment_index = garment_index

            row = box1.row(align=True)
            garment_convert_ico = 'MOD_CLOTH' if garment.tri_convert_ok else 'ERROR'
            row.operator('garment.garment_to_mesh', icon=garment_convert_ico).garment_index = garment_index
            
            row.prop(garment, 'cloth_res', text='Resolution')
            if garment.output_vert_count > 10000:
                row.label(text='', icon = 'ERROR')
            
            # row.operator("garment.cleanup", text="", icon="GHOST_ENABLED").garment_index = garment_index
            if garment.expand_garment:
                ######################################################################################################
                row = box1.row(align=True)
                row.operator('garment.setup_keyframes').garment_index = garment_index
                row.prop(garment, 'sim_time')
                
                # row = box1.row(align=True)
                # row.prop(garment, 'merge_patterns', expand=True)

                row = box1.row(align=True)
                # row.prop(garment, 'smooth_strength')  #apply this automatically (smooth = 10)
                row.label(text='Triangulation method')
                row.prop(garment, 'triangulation_method', text='')  # apply this automatically (smooth = 10)

                box2 = box1.box()
                row = box2.row(align=True)
                row.alignment = 'EXPAND'
                tri_ico = 'TRIA_DOWN' if garment.expand_patterns else "TRIA_RIGHT"
                row.prop(garment, "expand_patterns", icon=tri_ico, icon_only=True, text=f'Sewing Patterns ({len(garment.sewing_patterns)})', emboss=False)
                row.operator('garment.garment_meshes_add', icon='ADD', text='').garment_index = garment_index
                
                if garment.expand_patterns and len(garment.sewing_patterns) > 0:
                    for pattern_idx, sewing_patterns in enumerate(garment.sewing_patterns):
                        row = box2.row(align=True)
                        row.prop(sewing_patterns, "pattern_obj", text='')
                        row.prop(sewing_patterns, 'add_lattice', text='', icon='MOD_LATTICE')
                        row.prop(sewing_patterns, 'add_bend_deform', text='', icon='MOD_SIMPLEDEFORM')
                        oper = row.operator('cloth.raycast_edit_sewing', icon='LINKED', text='')
                        oper.garment_index = garment_index
                        oper.edit_patter_sewing = pattern_idx
                        oper = row.operator("garment.remove_pattern_sewings", text="", icon="UNLINKED")
                        oper.garment_index = garment_index
                        oper.pattern_idx = pattern_idx
                        oper = row.operator('garment.garment_meshes_remove', icon='REMOVE', text='')
                        oper.garment_index = garment_index
                        oper.pattern_idx = pattern_idx

                box2 = box1.box()
                row = box2.row(align=True)
                row.alignment = 'EXPAND'
                tri_ico = 'TRIA_DOWN' if garment.expand_sewings else "TRIA_RIGHT"
                row.prop(garment, "expand_sewings", icon=tri_ico, icon_only=True, text=f'{garment.name} Sewings ({len(garment.garment_sewings)})', emboss=False)
                row.operator('sewing.sewing_add', icon='ADD', text='').garment_index = garment_index
                oper = row.operator('cloth.raycast_edit_sewing', icon='LINKED', text='')
                oper.garment_index = garment_index
                oper.edit_patter_sewing = -1
                if garment.expand_sewings and len(garment.garment_sewings) > 0:
                    for sewing_index, garment_sewing in enumerate(garment.garment_sewings):
                        row_main = box2.row(align=True)
                        col = row_main.column(align=True)
                        subrow = col.row(align=True)
                        subrow.prop(garment_sewing, "source_obj",  text='')
                        subrow.prop(garment_sewing, "segment_id_from")

                        subrow  = col.row(align=True)
                        subrow.prop(garment_sewing, "target_obj", text='')
                        subrow.prop(garment_sewing, "segment_id_to")
                        
                        col = row_main.column(align=True)
                        subrow = col.row(align=True)
                        subrow.prop(garment_sewing, "flip", text='', icon='CENTER_ONLY')
                        subrow = col.row(align=True)
                        pair = subrow.operator('sewing.sewing_remove', icon='REMOVE', text='')
                        pair.garment_index = garment_index
                        pair.sewing_index = sewing_index


                box2 = box1.box()
                row = box2.row(align=True)
                row.alignment = 'EXPAND'
                tri_ico = 'TRIA_DOWN' if garment.expand_vgroups else "TRIA_RIGHT"
                row.prop(garment, "expand_vgroups", icon=tri_ico, icon_only=True, text=f'Vertex groups ({len(garment.generated_vgroups)})', emboss=False)
                row.operator('garment.vg_add', icon='ADD', text='').garment_index = garment_index
                # row.operator('garment.update_vgroups').garment_index = garment_index
                row.prop(garment, 'add_border_mask', icon='FULLSCREEN_ENTER', emboss=True, text='')
                row.prop(garment, 'add_non_border_mask', icon='FULLSCREEN_EXIT', emboss=True, text='')
                if garment.expand_vgroups:
                    for vg_idx, vg in enumerate(garment.generated_vgroups):
                        row = box2.row(align=True)
                        row.prop(vg, 'name')
                        row.prop_menu_enum(vg, 'vgroups_patterns')
                        row.prop(vg, 'add_bend_deform', text='', icon='MOD_SIMPLEDEFORM')
                        row.prop(vg, 'add_lattice', text='', icon='MOD_LATTICE')
                        # row.prop(vg, 'add_bend_deform', text='', icon='MOD_SIMPLEDEFORM')
                        pair = row.operator('garment.vg_remove', icon='REMOVE', text='')
                        pair.garment_index = garment_index
                        pair.vg_idx = vg_idx


                box2 = box1.box()
                row = box2.row(align=True)
                row.alignment = 'EXPAND'
                tri_ico = 'TRIA_DOWN' if garment.expand_pockets else "TRIA_RIGHT"
                row.prop(garment, "expand_pockets", icon=tri_ico, icon_only=True, text=f'Pockets ({len(garment.pockets)})', emboss=False)
                row.operator('garment.pocket_add', icon='ADD', text='').garment_index = garment_index
                row.operator('garment.raycast_edit_pocket', icon='LINKED', text='').garment_index = garment_index
                enable_pockets = 'RADIOBUT_ON' if garment.enable_pockets else "RADIOBUT_OFF"
                row.prop(garment, 'enable_pockets', icon=enable_pockets, text='')
                if garment.expand_pockets and len(garment.pockets) > 0:
                    for pocket_idx, garment_pocket in enumerate(garment.pockets):
                        box3 = box2.box()
                        row = box3.row(align=True)
                        row.prop(garment_pocket, "pocketObj", text='Pocket Obj')
                        row.prop(garment_pocket, "target_pattern")
                        row.prop_menu_enum(garment_pocket, "pocket_sewing")
                        oper = row.operator('garment.pocket_remove', icon='REMOVE', text='')
                        oper.garment_index = garment_index
                        oper.pocket_idx = pocket_idx

                box2 = box1.box()
                row = box2.row(align=True)
                row.alignment = 'EXPAND'
                tri_ico = 'TRIA_DOWN' if garment.expand_pins else "TRIA_RIGHT"
                row.prop(garment, "expand_pins", icon=tri_ico, icon_only=True, text=f'Pins ({len(garment.pins)})', emboss=False)
                row.operator('garment.pin_add', icon='ADD', text='').garment_index = garment_index
                row.operator('cloth.raycast_edit_pins', icon='LINKED', text='').garment_index = garment_index
                enable_pins = 'RADIOBUT_ON' if garment.enable_pins else "RADIOBUT_OFF"
                row.prop(garment, 'enable_pins', icon=enable_pins, text='')
                if garment.expand_pins and len(garment.pins) > 0:
                    for pin_idx, garment_pin in enumerate(garment.pins):
                        box3 = box2.box()
                        row = box3.row(align=True)
                        row.prop(garment_pin, "source_obj")
                        row.prop(garment_pin, "source_co")
                        row = box3.row(align=True)
                        row.prop(garment_pin, "target_obj")
                        row.prop(garment_pin, "target_co")
                        oper = row.operator('garment.pin_remove', icon='REMOVE', text='')
                        oper.garment_index = garment_index
                        oper.pin_idx = pin_idx


            layout.separator()
        


class GTOOL_OT_UpdateOldVGroups(bpy.types.Operator):
    bl_idname = "garment.update_vgroups"
    bl_label = "garment update vgroups"
    bl_description = 'update_vgroups'
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty()

    def execute(self, context):
        garment = context.scene.cloth_garment_data[self.garment_index]
        for i, new_vgroup in enumerate(garment.new_vgroups):  # remove sewing that are using removed mesh pattern
            if len(garment.generated_vgroups) - 1 < i:
                garment.generated_vgroups.add()
            garment.generated_vgroups[i].name = new_vgroup.name
            garment.generated_vgroups[i].vgroups_patterns = new_vgroup.vgroups_patterns
            garment.generated_vgroups[i].add_bend_deform = new_vgroup.add_bend_deform
            garment.generated_vgroups[i].add_lattice = new_vgroup.add_lattice

        return {'FINISHED'}


class GTOOL_OT_SewingPatterAdd(bpy.types.Operator):
    bl_idname = "garment.add_garment"
    bl_label = "Add Garment"
    bl_description = 'Add Garment'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cloth_garment_data = context.scene.cloth_garment_data
        cloth_garment_data.add()
        return {'FINISHED'}


class GTOOL_OT_SewingPatterRemove(bpy.types.Operator):
    bl_idname = "garment.remove_garment"
    bl_label = "Remove Garment"
    bl_description = "Remove Garment"
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty()

    def execute(self, context):
        cloth_garment_data = context.scene.cloth_garment_data
        cloth_garment_data.remove(self.garment_index)
        return {'FINISHED'}


class GTOOL_OT_SewingPatterPairAdd(bpy.types.Operator):
    bl_idname = "garment.garment_meshes_add"
    bl_label = "Add Pattern"
    bl_description = 'Add Pattern curve to garment'
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty()

    def execute(self, context):
        cloth_garment_data = context.scene.cloth_garment_data[self.garment_index]
        cloth_garment_data.sewing_patterns.add()
        return {'FINISHED'}


class GTOOL_OT_GarmetnPocketAdd(bpy.types.Operator):
    bl_idname = "garment.pocket_add"
    bl_label = "Add Pocket"
    bl_description = 'Add Pocket curve to garment'
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty()

    def execute(self, context):
        cloth_garment_data = context.scene.cloth_garment_data[self.garment_index]
        cloth_garment_data.pockets.add()
        return {'FINISHED'}


class GTOOL_OT_GarmetnPinAdd(bpy.types.Operator):
    bl_idname = "garment.pin_add"
    bl_label = "Add Pin"
    bl_description = 'Add Pin curve to garment'
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty()

    def execute(self, context):
        cloth_garment_data = context.scene.cloth_garment_data[self.garment_index]
        cloth_garment_data.pins.add()
        return {'FINISHED'}

class GTOOL_OT_VGAdd(bpy.types.Operator):
    bl_idname = "garment.vg_add"
    bl_label = "Generate vertex group"
    bl_description = 'Generate new vertex group and assign patterns to it'
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty()

    def execute(self, context):
        cloth_garment_data = context.scene.cloth_garment_data[self.garment_index]
        cloth_garment_data.generated_vgroups.add()
        return {'FINISHED'}


class GTOOL_OT_VGRemove(bpy.types.Operator):
    bl_idname = "garment.vg_remove"
    bl_label = "Remove Vertex Group"
    bl_description = 'Remove merged vertex group'
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty()
    vg_idx: bpy.props.IntProperty()

    def execute(self, context):
        cloth_garment_data = context.scene.cloth_garment_data[self.garment_index]
        cloth_garment_data.generated_vgroups.remove(self.vg_idx)
        return {'FINISHED'}


class GTOOL_OT_SewingPatterPairRemove(bpy.types.Operator):
    bl_idname = "garment.garment_meshes_remove"
    bl_label = "Remove Pattern"
    bl_description = 'Remove Pattern curve from garment (also removes sewing assigned to this Patternt)'
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty()
    pattern_idx: bpy.props.IntProperty()

    def execute(self, context):
        garment_settings = context.scene.cloth_garment_data[self.garment_index]
        garment_mesh = garment_settings.sewing_patterns[self.pattern_idx].pattern_obj
        sewing_to_remove = []
        for i,sewing_data in enumerate(garment_settings.garment_sewings): #remove sewing that are using removed mesh pattern
            if sewing_data.source_obj == garment_mesh or sewing_data.target_obj == garment_mesh:
                sewing_to_remove.append(i)
        for sewing_id in reversed(sewing_to_remove):
            garment_settings.garment_sewings.remove(sewing_id)
        garment_settings.sewing_patterns.remove(self.pattern_idx)

        return {'FINISHED'}

class GTOOL_OT_GarmentPocketRemove(bpy.types.Operator):
    bl_idname = "garment.pocket_remove"
    bl_label = "Remove Pocket"
    bl_description = 'Remove Pocket curve from garment (also removes sewing assigned to this Patternt)'
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty()
    pocket_idx: bpy.props.IntProperty()

    def execute(self, context):
        garment_settings = context.scene.cloth_garment_data[self.garment_index]
        garment_settings.pockets.remove(self.pocket_idx)
        return {'FINISHED'}


class GTOOL_OT_GarmentPinRemove(bpy.types.Operator):
    bl_idname = "garment.pin_remove"
    bl_label = "Remove pin"
    bl_description = 'Remove pin from garment'
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty()
    pin_idx: bpy.props.IntProperty()

    def execute(self, context):
        garment_settings = context.scene.cloth_garment_data[self.garment_index]
        garment_settings.pins.remove(self.pin_idx)
        return {'FINISHED'}


class GTOOL_OT_SewingAdd(bpy.types.Operator):
    bl_idname = "sewing.sewing_add"
    bl_label = "Add Sewing"
    bl_description = 'Add Sewing to garment'
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty()
    do_modal: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        garment = context.scene.cloth_garment_data[self.garment_index]
        garment.garment_sewings.add()
        if self.do_modal:
            bpy.ops.cloth.raycast_edit_sewing('INVOKE_DEFAULT',garment_index=self.garment_index, sewing_index=len(garment.garment_sewings)-1)
        return {'FINISHED'}


class GTOOL_OT_SewingRemove(bpy.types.Operator):
    bl_idname = "sewing.sewing_remove"
    bl_label = "Remove Sewing"
    bl_description = 'Remove Sewing from garment'
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty()
    sewing_index: bpy.props.IntProperty()

    def execute(self, context):
        context.scene.cloth_garment_data[self.garment_index].garment_sewings.remove(self.sewing_index)
        return {'FINISHED'}



class GTOOL_OT_GarmentObjectPicker(bpy.types.Operator):
    bl_idname = "curve.curve_picker"
    bl_label = "Use Selected Object"
    bl_description = 'Use Selected Object'
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty()
    pattern_idx: bpy.props.IntProperty()

    def execute(self, context):
        if context.active_object and context.active_object.select_get() and context.active_object.type == 'CURVE':
            context.scene.cloth_garment_data[self.garment_index].sewing_patterns[self.pattern_idx].pattern_obj = context.active_object
        return {'FINISHED'}



class GTOOL_OT_PatternRemoveSewings(bpy.types.Operator):
    bl_idname = "garment.remove_pattern_sewings"
    bl_label = "Remove sewings from pattern"
    bl_description = 'Remove sewings attached to current pattern'
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty()
    pattern_idx: bpy.props.IntProperty()

    def execute(self, context):
        garment = context.scene.cloth_garment_data[self.garment_index]
        pattern_obj = garment.sewing_patterns[self.pattern_idx].pattern_obj
        sewing_to_remove = []
        for i,sewing_data in enumerate(garment.garment_sewings): #remove sewing that are using removed mesh pattern
            if sewing_data.source_obj == pattern_obj or sewing_data.target_obj == pattern_obj:
                sewing_to_remove.append(i)
        for sewing_id in reversed(sewing_to_remove):
            garment.garment_sewings.remove(sewing_id)
        return {'FINISHED'}


