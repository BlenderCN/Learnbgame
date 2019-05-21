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
    "name": "Shape Key Extras",
    "description": "A Blender Add-on to manipulate Shape Keys",
    "author": "Christian Brinkmann",
    "version": (0, 1, 9),
    "blender": (2, 76, 0),
    "location": "Properties > Object Data > Shape Keys",
    "tracker_url": "https://github.com/p2or/blender-shapekeyextras/issues",
    "category": "Mesh"
}

import bpy
import random

from bpy.props import (IntProperty,
                       BoolProperty,
                       FloatProperty,
                       StringProperty,
                       PointerProperty,
                       CollectionProperty,
                       EnumProperty
                       )

from bpy.types import (Operator,
                       Panel,
                       UIList,
                       PropertyGroup
                       )

# -------------------------------------------------------------------
# Helper    
# -------------------------------------------------------------------

def search_chars(char_sequence, name):
    if char_sequence:
        
        if char_sequence.endswith(','):
            char_sequence = char_sequence[:-1]
        if char_sequence.startswith(','):
            char_sequence = char_sequence[-1:]
            
        char_list = [i.strip() for i in char_sequence.split(",")]
        if name.startswith(tuple(char_list)) or name.endswith(tuple(char_list)):
            return True
        else: 
            return False
    else: 
        return False

def shape_key_selection(op, context):
    scn = context.scene
    ske = scn.shape_key_extras
    shape_key_names = []
    
    if not ske.sk_only:
        for shapekey in context.object.data.shape_keys.key_blocks:
            exclude_char = search_chars(ske.sk_exclude, shapekey.name)
            if exclude_char is not True:
                if ske.sk_selection == 'ALL':
                    shape_key_names.append(shapekey.name)
                if ske.sk_selection == 'ENABLED':
                    if shapekey.mute is False:
                        shape_key_names.append(shapekey.name)
                if ske.sk_selection == 'DISABLED':
                    if shapekey.mute is True:
                        shape_key_names.append(shapekey.name)                  
    else:
        for shapekey in context.object.data.shape_keys.key_blocks:
            only_char = search_chars(ske.sk_only, shapekey.name)
            if only_char is True:
                if ske.sk_selection == 'ALL':
                    shape_key_names.append(shapekey.name)
                if ske.sk_selection == 'ENABLED':
                    if shapekey.mute is False:
                        shape_key_names.append(shapekey.name)
                if ske.sk_selection == 'DISABLED':
                    if shapekey.mute is True:
                        shape_key_names.append(shapekey.name)    
                
    return shape_key_names

# -------------------------------------------------------------------
# Properties    
# -------------------------------------------------------------------

class SkeSettings(PropertyGroup):

    sk_value = FloatProperty(
        name = "Value",
        description = "Set static value",
        default = 0,
        #min = 0,
        #max =1
        )
    sk_random_min = FloatProperty(
        name = "Min",
        description = "Set minimum random value",
        default = 0,
        #min = 0,
        #max =1
        )
    sk_random_max = FloatProperty(
        name = "Max",
        description = "Set maximum random value",
        default = 1,
        #min = 0,
        #max =1
        )
    sk_exclude = StringProperty (
        name = "Exclude",
        description = "Exclude by first character",
        default = "Basis, #, *"
        )
    sk_only = StringProperty (
        name = "Only",
        description = "Include by first character",
        default = ""
        )
    sk_selection = EnumProperty(
        name="Selection",
        description="Shape Key Selection",
        items = (('ALL', "All", ""),
                ('ENABLED', "Enabled", ""),
                ('DISABLED', "Disabled", ""),
                ),default='ALL')

    sk_set_attributes = BoolProperty(default=False)
    sk_advanced_selection = BoolProperty(default=False)
    vg_uilist_index = IntProperty()
    vg_merge_vgroups = BoolProperty(default=False)


class SkePropertyCollection(PropertyGroup):
    
    collection_id = IntProperty()


# -------------------------------------------------------------------
# Shape Key Operators    
# -------------------------------------------------------------------

class EnableAllButton (Operator):
    bl_idname = "shapekeyextras.enable_all"
    bl_label = "Enable All"
    bl_description = "Enable all Shape Keys in Selection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        ske = scn.shape_key_extras
        
        if context.object.data.shape_keys:
            shape_keys = (shape_key_selection(self, context))
            for i in shape_keys:
                shapekey = context.object.data.shape_keys.key_blocks[i]
                shapekey.mute = False

            self.report({'INFO'}, "All Shape Keys enabled")
        else: 
             self.report({'WARNING'}, "No shape keys found.")  
             
        return {'FINISHED'}


class DisableAllButton (Operator):
    bl_idname = "shapekeyextras.disable_all"
    bl_label = "Disable All"
    bl_description = "Mute all Shape Keys in Selection"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scn = context.scene
        ske = scn.shape_key_extras
        
        if context.object.data.shape_keys:
            shape_keys = (shape_key_selection(self, context))
            for i in shape_keys:
                shapekey = context.object.data.shape_keys.key_blocks[i]
                shapekey.mute = True

            self.report({'INFO'}, "All Shape Keys disabled")        
        else: 
             self.report({'WARNING'}, "No shape keys found.")
             
        return {'FINISHED'}
   

class ToggleAllButton (Operator):
    bl_idname = "shapekeyextras.toggle_mute"
    bl_label = "Toggle Visibility"
    bl_description = "Toggle Mute State of all Shape Keys in Selection"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scn = context.scene
        ske = scn.shape_key_extras
        
        if context.object.data.shape_keys:
            shape_keys = (shape_key_selection(self, context))
            for i in shape_keys:
                shapekey = context.object.data.shape_keys.key_blocks[i]
                shapekey.mute = not shapekey.mute

            self.report({'INFO'}, "Enabled Shape Keys disabled and Disabled Shape Keys enabled")
        else: 
             self.report({'WARNING'}, "No shape keys found.")
        return {'FINISHED'}
    

class RandomEnableButton (Operator):
    bl_idname = "shapekeyextras.random_visibility"
    bl_label = "Randomize Visibility"
    bl_description = "Randomize Visibility/Mute State for all Shape Keys in Selection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        ske = scn.shape_key_extras
        
        if context.object.data.shape_keys:
            shape_keys = (shape_key_selection(self, context))
            for i in shape_keys:
                shapekey = context.object.data.shape_keys.key_blocks[i]
                shapekey.mute = bool(random.getrandbits(1))

            self.report({'INFO'}, "Ramdomized Shape Key Visibility")
        else:
            self.report({'WARNING'}, "No shape keys found.")    
        return {'FINISHED'}


class RandomizeValueButton (Operator):
    bl_idname = "shapekeyextras.randomize"
    bl_label = "Randomize Shape Key Value"
    bl_description = "Randomize Shape Key Value for all Shape Keys in Selection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        ske = scn.shape_key_extras
        
        if context.object.data.shape_keys:
            shape_keys = (shape_key_selection(self, context))
            for i in shape_keys:
                if i != 'Basis':
                    shapekey = context.object.data.shape_keys.key_blocks[i]
                    shapekey.value = random.uniform(ske.sk_random_min, ske.sk_random_max)

            self.report({'INFO'}, "Values for Shape Keys generated")
        else:
            self.report({'WARNING'}, "No shape keys found.")    
        return {'FINISHED'}


class ResetExcludeProperty (Operator):
    bl_idname = "shapekeyextras.reset_exclude"
    bl_label = "Revert to Default"
    bl_description = "Revert to Default"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        ske = scn.shape_key_extras
        ske.property_unset("sk_exclude")
        return {'FINISHED'}


class ResetOnlyProperty (Operator):
    bl_idname = "shapekeyextras.reset_only"
    bl_label = "Revert to Default"
    bl_description = "Revert to Default"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        ske = scn.shape_key_extras
        ske.property_unset("sk_only")
        return {'FINISHED'}


class SetRangeButton (Operator):
    bl_idname = "shapekeyextras.set_range"
    bl_label = "Set Shape Key Range"
    bl_description = "Set Range Values for Shape Keys in Selection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        ske = scn.shape_key_extras
        
        if context.object.data.shape_keys:
            shape_keys = (shape_key_selection(self, context))
            for i in shape_keys:
                if i != 'Basis':
                    shapekey = context.object.data.shape_keys.key_blocks[i]
                    shapekey.slider_min = ske.sk_random_min
                    shapekey.slider_max = ske.sk_random_max
                    
            self.report({'INFO'}, "Range Values adjusted")
        else:
            self.report({'WARNING'}, "No shape keys found.")    
        return {'FINISHED'}
    

class ApplyValueButton (Operator):
    bl_idname = "shapekeyextras.set_values"
    bl_label = "Set Shape Key Values"
    bl_description = "Assign static Values to all Shape Keys in Selection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        ske = scn.shape_key_extras
        
        if context.object.data.shape_keys:
            shape_keys = (shape_key_selection(self, context))
            for i in shape_keys:
                if i != 'Basis':
                    shapekey = context.object.data.shape_keys.key_blocks[i]
                    shapekey.value = ske.sk_value
                    
            self.report({'INFO'}, "Value assigned to Shape Keys")        
        else:
            self.report({'WARNING'}, "No shape keys found.")    
        return {'FINISHED'}
    

class RemoveDriversFromShapeKeysButton (Operator):
    bl_idname = "shapekeyextras.remove_drivers"
    bl_label = "Remove Drivers"
    bl_description = "Remove Drivers from Shapekeys in Selection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.object.data.shape_keys:
            shape_keys = (shape_key_selection(self, context))
            for i in shape_keys:
                if i != 'Basis':
                    context.object.data.shape_keys.key_blocks[i].driver_remove("value")
            
            self.report({'INFO'}, "Drivers Removed")
        else:
            self.report({'WARNING'}, "No shape keys found.")    
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class AddDriversToShapeKeysButton (Operator):
    bl_idname = "shapekeyextras.add_drivers"
    bl_label = "Add Drivers"
    bl_description = "Add Drivers to Shapekeys in Selection"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if context.object.data.shape_keys:      
            shape_keys = (shape_key_selection(self, context))
            for i in shape_keys:
                if i != 'Basis':
                    context.object.data.shape_keys.key_blocks[i].driver_add("value")
            
            self.report({'INFO'}, "Drivers added")
        else:
            self.report({'WARNING'}, "No shape keys found.")    
        return {'FINISHED'}


# http://stackoverflow.com/questions/7977550/how-to-change-the-value-of-the-shape-key-in-blender-script
class InsertKeyframeButton (Operator):
    bl_idname = "shapekeyextras.insert_keyframe"
    bl_label = "Insert Value Keyframe"
    bl_description = "Insert Keyframe (Shape Key Value) for all Shape Keys in Selection"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if context.object.data.shape_keys:       
            shape_keys = (shape_key_selection(self, context))
            for i in shape_keys:
                if i != 'Basis':
                    context.object.data.shape_keys.key_blocks[i].keyframe_insert(data_path="value")
            
            self.report({'INFO'}, "Keyframes inserted")
        else:
            self.report({'WARNING'}, "No shape keys found.")    
        return {'FINISHED'}


class DeleteKeyframeButton (Operator):
    bl_idname = "shapekeyextras.delete_keyframe"
    bl_label = "Remove current Keyframe"
    bl_description = "Remove current Keyframe for all Shape Keys in Selection"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if context.object.data.shape_keys:       
            shape_keys = (shape_key_selection(self, context))
            for i in shape_keys:
                if i != 'Basis':
                    try:
                        context.object.data.shape_keys.key_blocks[i].keyframe_delete(data_path="value")
                        self.report({'INFO'}, "Keyframes deleted.")
                    except:
                        self.report({'WARNING'}, "No Keyframe to remove.")
        else:
            self.report({'WARNING'}, "No shape keys found.")    
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


# http://blender.stackexchange.com/questions/5827/get-shape-key-from-action-or-fcurve-in-python
class DeleteAllKeyframesButton (Operator):
    bl_idname = "shapekeyextras.delete_all_keyframes"
    bl_label = "Remove Animation"
    bl_description = "Remove all Value Keyframes for all Shape Keys in Selection"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        sce = context.scene
        if context.object.data.shape_keys:
            shape_keys = (shape_key_selection(self, context))
            sk_data = context.object.data.shape_keys
            for i in shape_keys:
                if i != 'Basis' and sk_data.animation_data is not None:
                    for f in range(sce.frame_start, sce.frame_end+1):
                        if sk_data.animation_data.action:
                            sk_data.key_blocks[i].keyframe_delete(data_path="value", frame=f) #returns a bool

            self.report({'INFO'}, "All Keyframes removed.")
        else:
            self.report({'WARNING'}, "No shape keys found.")    
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class RemoveSelectedKeysButton (Operator):
    bl_idname = "shapekeyextras.remove_selection"
    bl_label = "Remove Shape Keys"
    bl_description = "Remove all Shape Keys in Selection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        ske = scn.shape_key_extras
        
        if context.object.data.shape_keys:
            shape_keys = (shape_key_selection(self, context))
            if len(shape_keys) > 0:
                for i in shape_keys:            
                    shapekey_index = context.object.data.shape_keys.key_blocks.keys().index(i)
                    context.object.active_shape_key_index = shapekey_index
                    bpy.ops.object.shape_key_remove()
                              
                self.report({'INFO'}, "Selected Shape Keys removed")
            else:
                self.report({'INFO'}, "Nothing to remove")
        else:
            self.report({'WARNING'}, "No shape keys found.")    
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class PrintShapeKeySelectionButton (Operator):
    bl_idname = "shapekeyextras.print_shape_key_selection"
    bl_label = "Print Selection to Console"
    bl_description = "Print Shape Key Selection to the Console"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        if context.object.data.shape_keys:       
            shape_keys = (shape_key_selection(self, context))
            self.report({'INFO'}, ('Selection: %s' % (', '.join(shape_keys))))
            print ("Selection:", ', '.join(shape_keys))
        else:
            self.report({'WARNING'}, "No shape keys found.")    
        return {'FINISHED'}


class MoveShapeKey(bpy.types.Operator):
    bl_idname = "shapekeyextras.move_shapekey"
    bl_label = "Move Shape Key"
    bl_description = "Move Shape Key up or down by certain amount"
    bl_options = {'REGISTER', 'UNDO'}
    
    steps = IntProperty()
    action = EnumProperty(
        items=(
        ('DOWN','Down','', 'TRIA_DOWN', 1),
        ('UP','Up','', 'TRIA_UP', 2)
        ))
    
    @classmethod
    def poll(cls, context):
        return context.object.active_shape_key

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout
        row.prop(self, "steps", text="Steps")
        row.prop(self, "action", expand=True)
        row.separator()
        
    def execute(self, context):
        if context.object.active_shape_key:
            old_id = context.object.active_shape_key_index
            for i in range(self.steps):
                if self.action == 'DOWN':
                    bpy.ops.object.shape_key_move(type="DOWN")
                else:
                    bpy.ops.object.shape_key_move(type="UP")
            
            new_id = context.object.active_shape_key_index
            info = 'Shape Key moved from %s to %s' % (old_id + 1, new_id + 1)
            self.report({'INFO'}, info)
            return {'FINISHED'}


# -------------------------------------------------------------------
# Vertex Group Operators    
# -------------------------------------------------------------------

class MergeVertexGroupUiList(Operator):
    bl_idname = "shapekeyextras.merge_vg_ui_list"
    bl_label = "Merge Groups"
    bl_description = "Merge all Groups in List"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.active_object.type == 'MESH' and 
            context.mode == 'OBJECT' and
            len(context.active_object.vertex_groups) > 1)
    
    def execute(self, context):
        group_input = {i.name for i in context.scene.shape_key_extras_collection if i.name}
        ob = bpy.context.active_object

        group_lookup = {g.index: g.name for g in ob.vertex_groups}
        group_candidates = {n for n in group_lookup.values() if n in group_input}
        
        if len(group_candidates) > 1:
            # iterate through the vertices and sum the weights per group
            vertex_weights = {}
            for vert in ob.data.vertices:
                if len(vert.groups):  
                    for item in vert.groups:
                        vg = ob.vertex_groups[item.group]
                        if vg.name in group_candidates:
                            if vert.index in vertex_weights:    
                                vertex_weights[vert.index] += vg.weight(vert.index)
                            else:
                                vertex_weights[vert.index] = vg.weight(vert.index)
                        
            # create new vertex group
            vgroup = ob.vertex_groups.new(name="+".join(group_candidates))
            
            # add the values to the group                       
            for key, value in vertex_weights.items():
                vgroup.add([key], value ,'REPLACE') #'ADD','SUBTRACT'
            
            self.report({'INFO'}, ('Merged: %s' % (', '.join(group_candidates))))
            return{'FINISHED'}
        
        else:
            self.report({'WARNING'}, "No Groups to merge.")
            return{'CANCELLED'}


class PrintVertexGroupUiList(Operator):
    bl_idname = "shapekeyextras.print_vg_ui_list"
    bl_label = "Print Selection"
    bl_description = "Print Vertex Group Selection to Console"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        selection = {i.name for i in context.scene.shape_key_extras_collection if i.name}
        if selection:
            self.report({'INFO'}, ", ".join(selection)) 
        else:
            self.report({'INFO'}, "Nothing in Selection")
        return{'FINISHED'}


class AddAllGroupsToUiList(Operator):
    bl_idname = "shapekeyextras.add_all_vg_ui_list"
    bl_label = "Add All Groups"
    bl_description = "Add all Vertex Groups to the List"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        ske = scn.shape_key_extras
        colprop = scn.shape_key_extras_collection
        idx = ske.vg_uilist_index
                    
        try:
            item = colprop[idx]
        except IndexError:
            pass
        
        for idx, item in enumerate(colprop):
            if not item.name:
                colprop.remove(idx)
                
        items = 0
        for g in context.active_object.vertex_groups:
            if g.name not in scn.shape_key_extras_collection:
                item = colprop.add()
                item.collection_id = len(colprop)
                item.name = g.name
                ske.vg_uilist_index = (len(colprop)-1)
                items += 1
        
        if items: info = '%s Vertex Groups added to the list' % (items)
        else: info = 'Nothing to add'
        self.report({'INFO'}, info)
        return{'FINISHED'}


class ClearVertexGroupUiList(Operator):
    bl_idname = "shapekeyextras.clear_vg_ui_list"
    bl_label = "Clear List"
    bl_description = "Clear all Items in Vertex Group list"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        ske = scn.shape_key_extras
        coll = scn.shape_key_extras_collection
                
        if len(coll) > 0:
             # reverse range to remove last item first
            for i in range(len(coll)-1,-1,-1):
                coll.remove(i)
            self.report({'INFO'}, "All items removed")
        else:
            self.report({'INFO'}, "Nothing to remove")   
        return{'FINISHED'}


# -------------------------------------------------------------------
# Ui
# -------------------------------------------------------------------

def shapekey_panel_append(self, context):
    
    if (context.object.data.shape_keys and
        context.mode == 'OBJECT'):
        
        scn = context.scene
        ske = scn.shape_key_extras
        layout = self.layout

        layout.separator()
        box_set_attributes = layout.box()
        row = box_set_attributes.row()
        row.prop(ske, "sk_set_attributes",
            icon="TRIA_DOWN" if ske.sk_set_attributes else "TRIA_RIGHT",
            icon_only=True, emboss=False)

        row.label(text="Set Shape Key Properties")
        if ske.sk_set_attributes:
            
            row = box_set_attributes.row()
            col = row.column(align=True)
            rowsub = col.row(align=True)
            rowsub.operator("shapekeyextras.enable_all", icon="RESTRICT_VIEW_OFF")
            rowsub.operator("shapekeyextras.disable_all", icon="RESTRICT_VIEW_ON")
            col.operator("shapekeyextras.toggle_mute", icon="FILE_REFRESH")
            col.operator("shapekeyextras.random_visibility", icon="GROUP_VERTEX")
            col.separator()

            #row = box_set_attributes.row()
            col = box_set_attributes.column(align=True)
            rowsub = col.row(align=True)
            rowsub.prop(ske, "sk_selection", expand=True)

            box_selection = col.box()
            row = box_selection.row()
            row.prop(ske, "sk_advanced_selection",
                icon="TRIA_DOWN" if ske.sk_advanced_selection else "TRIA_RIGHT",
                icon_only=True, emboss=False)

            row.label(text="Custom Selection")
            if ske.sk_advanced_selection:
                row = box_selection.row()
                col = row.column(align=True)
                
                sub = col.row(align=True)
                sub.prop(ske, "sk_exclude")
                sub.operator("shapekeyextras.reset_exclude", text="", icon="DOT")
                sub = col.row(align=True)
                sub.prop(ske, "sk_only")
                sub.operator("shapekeyextras.reset_only", text="", icon="DOT")
                row = box_selection.row(align=True)
                row.operator("shapekeyextras.print_shape_key_selection", icon="CONSOLE")
            
            col.separator()
            row = box_set_attributes.row()
            col = row.column(align=True)
            col.prop(ske, "sk_value")
            col.operator("shapekeyextras.set_values", icon="KEY_HLT")
            rowsub = col.row(align=True)
            rowsub.prop(ske, "sk_random_min")
            rowsub.prop(ske, "sk_random_max")
            col.operator("shapekeyextras.randomize", icon="KEYINGSET")
            col.operator("shapekeyextras.set_range", icon="SORTSIZE")
            col.separator()

            row = box_set_attributes.row()
            col = row.column(align=True)
            rowsub = col.row(align=True)
            rowsub.operator("shapekeyextras.insert_keyframe", icon="ACTION")
            rowsub = col.row(align=True)
            rowsub.operator("shapekeyextras.delete_keyframe", icon="PANEL_CLOSE")
            rowsub.operator("shapekeyextras.delete_all_keyframes", icon="PANEL_CLOSE")
            col.separator()

            row = box_set_attributes.row()
            col = row.column(align=True)
            rowsub = col.row(align=True)
            rowsub.operator("shapekeyextras.add_drivers", icon="DRIVER")
            rowsub.operator("shapekeyextras.remove_drivers", icon="PANEL_CLOSE")
            rowsub = col.row(align=True)
            rowsub.operator("shapekeyextras.remove_selection", icon="CANCEL")

        layout.separator()


class ActionsVertexGroupUiList(Operator):
    bl_idname = "shapekeyextras.action_vg_ui_list"
    bl_label = "Vertex Group List Actions"
    bl_options = {'REGISTER', 'UNDO'}

    action = EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""),
        )
    )

    def invoke(self, context, event):
        scn = context.scene
        ske = scn.shape_key_extras
        colprop = scn.shape_key_extras_collection
        idx = ske.vg_uilist_index

        try:
            item = colprop[idx]
        except IndexError:
            pass

        else:
            if self.action == 'DOWN' and idx < len(colprop) - 1:
                item_next = colprop[idx+1].name
                ske.vg_uilist_index += 1
                info = 'Item %d selected' % (ske.vg_uilist_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = colprop[idx-1].name
                ske.vg_uilist_index -= 1
                info = 'Item %d selected' % (ske.vg_uilist_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                            
                first_item = True if ske.vg_uilist_index == 0 else False
                
                if colprop[ske.vg_uilist_index].name:
                    info = '%s removed from list' % (colprop[ske.vg_uilist_index].name)
                else:
                    info = 'Item %s removed from list' % (ske.vg_uilist_index +1)
                
                if first_item:
                    ske.vg_uilist_index = 0
                else:
                    ske.vg_uilist_index -= 1
                
                self.report({'INFO'}, info)
                colprop.remove(idx)

        if self.action == 'ADD':
            item = colprop.add()
            item.collection_id = len(colprop)
            #item.collection_name = ""
            ske.vg_uilist_index = (len(colprop)-1)
            #info = '%s added to list' % ("Empty group item")
            #self.report({'INFO'}, info)

        return {"FINISHED"}


class VertexGroupUiList(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(.1)
        split.scale_y = 1.1
        split.label(str(index+1))
        split.prop_search(item, "name", context.active_object, "vertex_groups", text="")


def vertexgroup_panel_append(self, context):
        
    if (context.active_object.type == 'MESH' and 
        len(context.active_object.vertex_groups) > 1 and
        context.mode == 'OBJECT'):
        
        scn = context.scene
        ske = scn.shape_key_extras
        layout = self.layout

        box_merge_vgroups = layout.box()
        row = box_merge_vgroups.row()
        row.prop(ske, "vg_merge_vgroups",
            icon="TRIA_DOWN" if ske.vg_merge_vgroups else "TRIA_RIGHT",
            icon_only=True, emboss=False
        )
        row.label(text="Merge Vertex Groups")
        if ske.vg_merge_vgroups:

            rows = 4
            row = box_merge_vgroups.row() 
            row.template_list("VertexGroupUiList", "", scn, "shape_key_extras_collection", ske, "vg_uilist_index", rows=rows)
            
            col = row.column(align=True)
            col.operator("shapekeyextras.action_vg_ui_list", icon='ZOOMIN', text="").action = 'ADD'
            col.operator("shapekeyextras.action_vg_ui_list", icon='ZOOMOUT', text="").action = 'REMOVE'
            col.separator()
            col.operator("shapekeyextras.action_vg_ui_list", icon='TRIA_UP', text="").action = 'UP'
            col.operator("shapekeyextras.action_vg_ui_list", icon='TRIA_DOWN', text="").action = 'DOWN'

            row = box_merge_vgroups.row()
            col = row.column(align=True)
            rowsub = col.row(align=True)
            #rowsub.operator("shapekeyextras.print_vg_ui_list", icon="WORDWRAP_ON")
            rowsub.operator("shapekeyextras.add_all_vg_ui_list", icon="WORDWRAP_ON")
            rowsub.operator("shapekeyextras.clear_vg_ui_list", icon="X")
            col.operator("shapekeyextras.merge_vg_ui_list", icon="STICKY_UVS_LOC")

        layout.separator()


def shapekey_specials_append(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.operator("shapekeyextras.move_shapekey", icon="PHYSICS")


class DrawShapeKeyListItem:
    
    def draw(self, context, layout, data, item, icon, active_data, active_propname, index):
        obj = active_data
        key_block = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            
            split = layout.split(.1)
            split.label(str(index+1))
            #split = split.split(.1)
            #split.label(str(index+1))
            row = split.row(align=True)
            row.prop(key_block, "name", text="", emboss=False, icon_value=icon)
            
            row = split.row(align=True)
            if key_block.mute or (obj.mode == 'EDIT' and not (obj.use_shape_key_edit_mode and obj.type == 'MESH')):
                row.active = False
            if not item.id_data.use_relative:
                row.prop(key_block, "frame", text="", emboss=False)
            elif index > 0:
                row.prop(key_block, "value", text="", emboss=False)
            else:
                row.label(text="")
            row.prop(key_block, "mute", text="", emboss=False)
        
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

    # built-in method ../startup/bl_ui/properties_data_mesh.py
    _draw = bpy.types.MESH_UL_shape_keys.draw_item


# -------------------------------------------------------------------
# Register
# -------------------------------------------------------------------

def register():
    bpy.utils.register_module(__name__)
    bpy.types.DATA_PT_shape_keys.append(shapekey_panel_append)
    bpy.types.DATA_PT_vertex_groups.append(vertexgroup_panel_append)
    bpy.types.Scene.shape_key_extras = PointerProperty(type=SkeSettings)
    bpy.types.Scene.shape_key_extras_collection = CollectionProperty(type=SkePropertyCollection)
    bpy.types.MESH_UL_shape_keys.draw_item = DrawShapeKeyListItem.draw
    bpy.types.MESH_MT_shape_key_specials.append(shapekey_specials_append)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.DATA_PT_shape_keys.remove(shapekey_panel_append)
    bpy.types.DATA_PT_vertex_groups.remove(vertexgroup_panel_append)
    bpy.types.MESH_MT_shape_key_specials.remove(shapekey_specials_append)
    bpy.types.MESH_UL_shape_keys.draw_item = DrawShapeKeyListItem._draw
    del bpy.types.Scene.shape_key_extras_collection
    del bpy.types.Scene.shape_key_extras

if __name__ == "__main__":
    register()
