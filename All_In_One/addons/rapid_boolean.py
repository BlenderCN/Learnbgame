import bpy
import re
from bpy.props import BoolProperty, StringProperty, EnumProperty, CollectionProperty
import rna_keymap_ui


#######################
#CODE STRUCTURE
#######################
#Base Functions Section
#----------------------
#Main Functions Section
#----------------------
#Main Ops Section
#----------------------
#Pie Menu Section
#----------------------
#Addon Preferences
#----------------------
#Register and Unregister
#######################


bl_info = {
    'name' : "Rapid Boolean",
    "description" : "Rapid Boolean Tool",
    "author" : "Kozo Oeda",
    "version" : (1, 2),
    "location" : "",
    "warning" : "",
    "support" : "COMMUNITY",
    'wiki_url' : "",
    "tracker_url" : "",
    "category": "Learnbgame",
}


##########################
# Base Functions Section #
##########################


def override_context(area_type):
    for area in bpy.context.screen.areas:
        if area.type == area_type:
            override = bpy.context.copy()
            override['area'] = area
            return override


def print_to_console(txt):
    ovctx = override_context('CONSOLE')
    try:
        bpy.ops.console.scrollback_append(ovctx, text = str(txt), type = 'OUTPUT')
    except ValueError:
        pass


def match_boolean_pattern(modifier_name):
    if re.match('RapidBoolean.*', modifier_name):
        return True
    else:
        return False


def get_modifier_items(obj):
    return bpy.data.objects[obj.name].modifiers.items()


def get_boolean_modifier_items(obj):
    boolean_items = []
    items = bpy.data.objects[obj.name].modifiers.items()

    for item in items:
        if match_boolean_pattern(item[0]):
            boolean_items.append(item)

    return boolean_items


def get_target_object_from_selected_object(selected_obj):
    objs = bpy.context.scene.objects

    for obj in objs:
        if obj.type == 'MESH':
            items = get_boolean_modifier_items(obj)
            for item in items:
                if item[1].object == selected_obj:
                    return obj

    return None


def get_selected_object_set_boolean_mod(target_obj, selected_obj):
    items = get_boolean_modifier_items(target_obj)

    for item in items:
        if item[1].object == selected_obj:
            return item
    

def get_target_object(is_first):
    selected_objs = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

    if len(selected_objs) < 2:
        return None

    elif len(selected_objs) == 2:
        if is_first:
            for obj in selected_objs:
                if obj.name != bpy.context.active_object.name:
                    return obj

        else:
            for obj in selected_objs:
                if obj.name == bpy.context.active_object.name:
                    return obj
            return None

    elif len(selected_objs) > 2:
        if is_first:
            return None

        else:
            for obj in selected_objs:
                if obj.name == bpy.context.active_object.name:
                    return obj


def get_active_layer_nums():
    layer_nums = []

    for n, layer in enumerate(bpy.context.scene.layers):
        if layer:
            layer_nums.append(n)

    return layer_nums


def get_objects_in_active_layers():
    layer_nums = get_active_layer_nums()
    obj_list = []

    for obj in bpy.context.scene.objects:
        for n, layer in enumerate(obj.layers):
            if layer:
                if n in layer_nums:
                    obj_list.append(obj)

    return obj_list


##########################
# Main Functions Section #
##########################


#operation is 'UNION', 'DIFFERENCE', 'INTERSECT'
def change_selected_object_ops_set_in_boolean(target_obj, selected_obj, operation):
    item = get_selected_object_set_boolean_mod(target_obj, selected_obj)
    item[1].operation = operation


#visibl type is 'BOUNDS', 'WIRE', 'SOLID', 'TEXTURED'
def change_selected_object_visibility(selected_obj, visible_type):
    selected_obj.draw_type = visible_type
    

def hide_object(target_obj):
    if target_obj.hide == False:
        target_obj.hide = True


def toggle_hide_object(targe_obj):
    if targe_obj.hide == False:
        targe_obj.hide = True
    else:
        target_obj.hide = False 


def show_all_objects_in_active_layers():
    objs = get_objects_in_active_layers()
    for obj in objs:
        if obj.hide:
            obj.hide = False


def add_boolean_to_target_with_selected_object(target_obj, selected_obj):
    if bpy.context.active_object:
        prev_active_obj = bpy.context.active_object
    else:
        prev_active_obj = None

    bpy.context.scene.objects.active = target_obj
    bpy.ops.object.modifier_add(type = 'BOOLEAN')
    bpy.context.active_object.modifiers[-1].name = "RapidBoolean"
    bpy.context.active_object.modifiers[-1].object = selected_obj
    bpy.context.scene.objects.active = prev_active_obj


def remove_boolean_with_selected_object_from_target(target_obj, selected_obj):
    items = get_modifier_items(target_obj)

    if bpy.context.active_object:
        prev_active_obj = bpy.context.active_object
    else:
        prev_active_obj = None

    bpy.context.scene.objects.active = target_obj

    for item in reversed(items):
        if match_boolean_pattern(item[0]):
            if item[1].object == selected_obj:
                bpy.ops.object.modifier_remove(modifier = item[1].name)
                bpy.context.scene.objects.active = prev_active_obj
                return 
    

def apply_all_boolean_modifiers(target_obj): 
    boolean_items = get_boolean_modifier_items(target_obj)

    if bpy.context.active_object:
        prev_active_obj = bpy.context.active_object
    else:
        prev_active_obj = None

    bpy.context.scene.objects.active = target_obj

    for b_item in boolean_items:
        if b_item[1].object:
            bpy.ops.object.modifier_apply(apply_as = 'DATA', modifier = b_item[0])
        else:
            bpy.ops.object.modifier_remove(modifier = b_item[1].name)

    bpy.context.scene.objects.active = prev_active_obj 


####################
# Main Ops Section #
#################### 


class SetUnion(bpy.types.Operator):
    bl_idname = "rpbl.set_union"
    bl_label = "Rapid Boolean Set Union"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        addon_prefs.operation_enum = 'UNION'

        selected_objs = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

        for selected_obj in selected_objs:
            target_obj = get_target_object_from_selected_object(selected_obj)

            if target_obj:
                change_selected_object_ops_set_in_boolean(target_obj, selected_obj, 'UNION')

        return {'FINISHED'}


class SetUnionPostSetting(bpy.types.Operator):
    bl_idname = "rpbl.set_union_ps"
    bl_label = "Rapid Boolean Set Union Post Setting"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        target_obj = context.scene.objects[context.scene.rpbl_target_obj_name]
        for selected_obj in bpy.context.selected_objects:
            for prop in context.scene.rpbl_selected_objs_name:
                if selected_obj.name == prop.name:
                    change_selected_object_ops_set_in_boolean(target_obj, selected_obj, 'UNION')
        bpy.ops.wm.call_menu_pie(name = PostSettingPieAppearance.bl_idname)

        return {'FINISHED'}


class SetDifference(bpy.types.Operator):
    bl_idname = "rpbl.set_difference"
    bl_label = "Rapid Boolean Set Difference"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        addon_prefs.operation_enum = 'DIFFERENCE'

        selected_objs = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

        for selected_obj in selected_objs:
            target_obj = get_target_object_from_selected_object(selected_obj)

            if target_obj:
                change_selected_object_ops_set_in_boolean(target_obj, selected_obj, 'DIFFERENCE')

        return {'FINISHED'}


class SetDifferencePostSetting(bpy.types.Operator):
    bl_idname = "rpbl.set_difference_ps"
    bl_label = "Rapid Boolean Set Difference Post Setting"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        target_obj = context.scene.objects[context.scene.rpbl_target_obj_name]
        for selected_obj in bpy.context.selected_objects:
            for prop in context.scene.rpbl_selected_objs_name:
                if selected_obj.name == prop.name:
                    change_selected_object_ops_set_in_boolean(target_obj, selected_obj, 'DIFFERENCE')
        bpy.ops.wm.call_menu_pie(name = PostSettingPieAppearance.bl_idname)

        return {'FINISHED'}


class SetIntersect(bpy.types.Operator):
    bl_idname = "rpbl.set_intersect"
    bl_label = "Rapid Boolean Set Intersect"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        addon_prefs.operation_enum = 'INTERSECT'

        selected_objs = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

        for selected_obj in selected_objs:
            target_obj = get_target_object_from_selected_object(selected_obj)

            if target_obj:
                change_selected_object_ops_set_in_boolean(target_obj, selected_obj, 'INTERSECT')

        return {'FINISHED'}


class SetIntersectPostSetting(bpy.types.Operator):
    bl_idname = "rpbl.set_intersect_ps"
    bl_label = "Rapid Boolean Set Intersect Post Setting"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        target_obj = context.scene.objects[context.scene.rpbl_target_obj_name]
        for selected_obj in bpy.context.selected_objects:
            for prop in context.scene.rpbl_selected_objs_name:
                if selected_obj.name == prop.name:
                    change_selected_object_ops_set_in_boolean(target_obj, selected_obj, 'INTERSECT')
        bpy.ops.wm.call_menu_pie(name = PostSettingPieAppearance.bl_idname)

        return {'FINISHED'}


class SetBounds(bpy.types.Operator):
    bl_idname = "rpbl.set_bounds"
    bl_label = "Rapid Boolean Set Bounds"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        addon_prefs.visible_type_enum = 'BOUNDS'

        selected_objs = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

        for selected_obj in selected_objs:
            change_selected_object_visibility(selected_obj, 'BOUNDS')

        return {'FINISHED'}


class SetBoundsPostSetting(bpy.types.Operator):
    bl_idname = "rpbl.set_bounds_ps"
    bl_label = "Rapid Boolean Set Bounds Post Setting"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        for selected_obj in bpy.context.selected_objects:
            for prop in context.scene.rpbl_selected_objs_name:
                if selected_obj.name == prop.name:
                    change_selected_object_visibility(selected_obj, 'BOUNDS')
        bpy.ops.wm.call_menu_pie(name = PostSettingPieToggleHide.bl_idname)

        return {'FINISHED'}


class SetWire(bpy.types.Operator):
    bl_idname = "rpbl.set_wire"
    bl_label = "Rapid Boolean Set Wire"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        addon_prefs.visible_type_enum = 'WIRE'

        selected_objs = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

        for selected_obj in selected_objs:
            change_selected_object_visibility(selected_obj, 'WIRE')

        return {'FINISHED'}


class SetWirePostSetting(bpy.types.Operator):
    bl_idname = "rpbl.set_wire_ps"
    bl_label = "Rapid Boolean Set Wire Post Setting"
    bl_options = {'INTERNAL'}

    global selected_obj

    def execute(self, context):
        for selected_obj in bpy.context.selected_objects:
            for prop in context.scene.rpbl_selected_objs_name:
                if selected_obj.name == prop.name:
                    change_selected_object_visibility(selected_obj, 'WIRE')
        bpy.ops.wm.call_menu_pie(name = PostSettingPieToggleHide.bl_idname)

        return {'FINISHED'}


class SetSolid(bpy.types.Operator):
    bl_idname = "rpbl.set_solid"
    bl_label = "Rapid Boolean Set Solid"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        addon_prefs.visible_type_enum = 'SOLID'

        selected_objs = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

        for selected_obj in selected_objs:
            change_selected_object_visibility(selected_obj, 'SOLID')

        return {'FINISHED'}


class SetSolidPostSetting(bpy.types.Operator):
    bl_idname = "rpbl.set_solid_ps"
    bl_label = "Rapid Boolean Set Solid Post Setting"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        for selected_obj in bpy.context.selected_objects:
            for prop in context.scene.rpbl_selected_objs_name:
                if selected_obj.name == prop.name:
                    change_selected_object_visibility(selected_obj, 'SOLID')
        bpy.ops.wm.call_menu_pie(name = PostSettingPieToggleHide.bl_idname)

        return {'FINISHED'}


class SetTextured(bpy.types.Operator):
    bl_idname = "rpbl.set_textured"
    bl_label = "Rapid Boolean Set Textured"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        addon_prefs.visible_type_enum = 'TEXTURED'

        selected_objs = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

        for selected_obj in selected_objs:
            change_selected_object_visibility(selected_obj, 'TEXTURED')

        return {'FINISHED'}


class SetTexturedPostSetting(bpy.types.Operator):
    bl_idname = "rpbl.set_textured_ps"
    bl_label = "Rapid Boolean Set Textured Post Setting"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        for selected_obj in bpy.context.selected_objects:
            for prop in context.scene.rpbl_selected_objs_name:
                if selected_obj.name == prop.name:
                    change_selected_object_visibility(selected_obj, 'TEXTURED')
        bpy.ops.wm.call_menu_pie(name = PostSettingPieToggleHide.bl_idname)

        return {'FINISHED'}


class SetFirst(bpy.types.Operator):
    bl_idname = "rpbl.set_first"
    bl_label = "Rapid Boolean Set First"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        context.user_preferences.addons[__name__].preferences.is_first = True
        return {'FINISHED'}


class SetLast(bpy.types.Operator):
    bl_idname = "rpbl.set_last"
    bl_label = "Rapid Boolean Set Last"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        context.user_preferences.addons[__name__].preferences.is_first = False
        return {'FINISHED'}


class Add(bpy.types.Operator):
    bl_idname = "rpbl.add_obj"
    bl_label = "Rapid Boolean Add Object"
    bl_options = {'INTERNAL'}


    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        is_first = addon_prefs.is_first

        target_obj = get_target_object(is_first)
        selected_objs = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

        if target_obj:
            selected_objs.remove(target_obj)
            context.scene.rpbl_target_obj_name = target_obj.name
            for selected_obj in selected_objs:
                add_boolean_to_target_with_selected_object(target_obj, selected_obj)
                change_selected_object_ops_set_in_boolean(target_obj, selected_obj, addon_prefs.operation_enum)
                change_selected_object_visibility(selected_obj, addon_prefs.visible_type_enum)
        else:
            if len(selected_objs) < 2:
                self.report({'INFO'}, "Select one more object")

            elif len(selected_objs) > 2:
                if is_first:
                    self.report({'INFO'}, "Set Last if you want to add several objects at once")

        context.scene.rpbl_selected_objs_name.clear()
        for selected_obj in selected_objs:
            prop = context.scene.rpbl_selected_objs_name.add()
            prop.name = selected_obj.name

        context.scene.rpbl_modal_first_action_finished = True
        self.report({'INFO'}, "Activated Setting Mode")

        return {'FINISHED'}
            
        
class Remove(bpy.types.Operator):
    bl_idname = "rpbl.remove_obj"
    bl_label = "Rapid Boolean Remove Object"
    bl_options = {'INTERNAL'}

    def execute(self, context):

        selected_objs = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

        for selected_obj in selected_objs:
            target_obj = get_target_object_from_selected_object(selected_obj)

            if target_obj:
                remove_boolean_with_selected_object_from_target(target_obj, selected_obj)

        return {'FINISHED'}
            

class ApplyAllMods(bpy.types.Operator):
    bl_idname = "rpbl.apply_all_mods"
    bl_label = "Rapid Boolean Apply All Mods"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        selected_objs = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

        for selected_obj in selected_objs:
            apply_all_boolean_modifiers(selected_obj)

        return {'FINISHED'}


class Hide(bpy.types.Operator):
    bl_idname = "rpbl.hide"
    bl_label = "Rapid Boolean Hide Selected Objects"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        selected_objs = bpy.context.selected_objects

        for obj in selected_objs:
            hide_object(obj)

        return {'FINISHED'}


class ToggleHidePostSetting(bpy.types.Operator):
    bl_idname = "rpbl.toggle_hide_ps"
    bl_label = "Rapid Boolean Toggle Hide Post Setting"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        for selected_obj in bpy.context.selected_objects:
            for prop in context.scene.rpbl_selected_objs_name:
                if selected_obj.name == prop.name:
                    toggle_hide_object(selected_obj)
        context.scene.rpbl_post_modal_locked = False

        return {'FINISHED'}


class ShowAllObjects(bpy.types.Operator):
    bl_idname = "rpbl.show_all_objects"
    bl_label = "Rapid Boolean Show All Objects in Active Layers"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        show_all_objects_in_active_layers()
        return {'FINISHED'}


class SkipPostSettingPieBooleanType(bpy.types.Operator):
    bl_idname = "rpbl.skip_ps_pie_boolean_type"
    bl_label = "Skip Boolen Type Pie"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name = PostSettingPieAppearance.bl_idname)
        return {'FINISHED'}


class SkipPostSettingPieAppearance(bpy.types.Operator):
    bl_idname = "rpbl.skip_ps_pie_appearance"
    bl_label = "Skip Appearance Pie"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name = PostSettingPieToggleHide.bl_idname)
        return {'FINISHED'}


class SkipPostSettingPieToggleHide(bpy.types.Operator):
    bl_idname = "rpbl.skip_ps_pie_toggle_hide"
    bl_label = "Skip ToggleHide Pie"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        context.scene.rpbl_post_modal_locked = False
        return {'FINISHED'}


####################       
# Pie Menu Section #
####################       


class RapidBooleanPie(bpy.types.Menu):
    bl_idname = "RapidBooleanPie"
    bl_label =  "Rapid Bool Pie"

    def is_union(self, operation):
        if operation == 'UNION':
            return 'CHECKBOX_HLT'
        else:
            return 'CHECKBOX_DEHLT'

    def is_difference(self, operation):
        if operation == 'DIFFERENCE':
            return 'CHECKBOX_HLT'
        else:
            return 'CHECKBOX_DEHLT'

    def is_intersect(self, operation):
        if operation == 'INTERSECT':
            return 'CHECKBOX_HLT'
        else:
            return 'CHECKBOX_DEHLT'
        
    def is_bounds(self, visible_type):
        if visible_type == 'BOUNDS':
            return 'CHECKBOX_HLT'
        else:
            return 'CHECKBOX_DEHLT'

    def is_wire(self, visible_type):
        if visible_type == 'WIRE':
            return 'CHECKBOX_HLT'
        else:
            return 'CHECKBOX_DEHLT'

    def is_solid(self, visible_type):
        if visible_type == 'SOLID':
            return 'CHECKBOX_HLT'
        else:
            return 'CHECKBOX_DEHLT'

    def is_textured(self, visible_type):
        if visible_type == 'TEXTURED':
            return 'CHECKBOX_HLT'
        else:
            return 'CHECKBOX_DEHLT'

    def is_first(self, is_first):

        if is_first:
            return 'CHECKBOX_HLT'
        else:
            return 'CHECKBOX_DEHLT'

    def is_last(self, is_first):

        if is_first:
            return 'CHECKBOX_DEHLT'
        else:
            return 'CHECKBOX_HLT'

    def draw(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences

        operation = addon_prefs.operation_enum
        visible_type = addon_prefs.visible_type_enum
        is_first = addon_prefs.is_first
        
        layout = self.layout
        pie = layout.menu_pie()

        #West
        col = pie.column()
        props = col.operator(SetFirst.bl_idname, text = "First", icon = self.is_first(is_first))
        props = col.operator(SetLast.bl_idname, text = "Last", icon = self.is_last(is_first))

        #East
        col = pie.column()
        props = col.operator(SetUnion.bl_idname, text = "Union", icon = self.is_union(operation))
        props = col.operator(SetDifference.bl_idname, text = "Difference", icon = self.is_difference(operation))
        props = col.operator(SetIntersect.bl_idname, text = "Intersect", icon = self.is_intersect(operation))

        #South
        props = pie.operator(Remove.bl_idname, text = "Remove", icon = 'X')

        #North
        props = pie.operator(Add.bl_idname, text = "Add", icon = 'MOD_BOOLEAN')

        #North West
        col = pie.column()
        props = col.operator(SetBounds.bl_idname, text = "Bounds", icon = self.is_bounds(visible_type))
        props = col.operator(SetWire.bl_idname, text = "Wire", icon = self.is_wire(visible_type))
        props = col.operator(SetSolid.bl_idname, text = "Solid", icon = self.is_solid(visible_type))
        props = col.operator(SetTextured.bl_idname, text = "Textured", icon = self.is_textured(visible_type))

        #North East 
        props = pie.operator(ApplyAllMods.bl_idname, text = "Apply All Rapid Booleans", icon = 'FILE_TICK')

        #South West
        col = pie.column()
        props = col.operator(Hide.bl_idname, text = "Hide", icon = 'RESTRICT_VIEW_ON')
        props = col.operator(ShowAllObjects.bl_idname, text = "Show All", icon = 'RESTRICT_VIEW_OFF')


class PostSettingPieBooleanType(bpy.types.Menu):
    bl_idname = "PostSettingPieBooleanType"
    bl_label =  "Post Setting Pie Boolean Tyepe"

    def draw(self, context):

        layout = self.layout
        pie = layout.menu_pie()

        props = pie.operator(SetUnionPostSetting.bl_idname, text = "Union", icon = 'NONE') 
        props = pie.operator(SetDifferencePostSetting.bl_idname, text = "Difference", icon = 'NONE') 
        props = pie.operator(SetIntersectPostSetting.bl_idname, text = "Intersect", icon = 'NONE') 
        props = pie.operator(SkipPostSettingPieBooleanType.bl_idname, text = "Next", icon = 'NONE') 


class PostSettingPieAppearance(bpy.types.Menu):
    bl_idname = "PostSettingPieAppearance"
    bl_label =  "Post Setting Pie Appearance"

    def draw(self, context):

        layout = self.layout
        pie = layout.menu_pie()

        props = pie.operator(SetBoundsPostSetting.bl_idname, text = "Bounds", icon = 'NONE') 
        props = pie.operator(SetWirePostSetting.bl_idname, text = "Wire", icon = 'NONE') 
        props = pie.operator(SetSolidPostSetting.bl_idname, text = "Solid", icon = 'NONE') 
        props = pie.operator(SkipPostSettingPieAppearance.bl_idname, text = "Next", icon = 'NONE') 
        props = pie.operator(SetTexturedPostSetting.bl_idname, text = "Textured", icon = 'NONE') 


class PostSettingPieToggleHide(bpy.types.Menu):
    bl_idname = "PostSettingPieToggleHide"
    bl_label =  "Post Setting Pie Toggle Hide"

    def draw(self, context):

        layout = self.layout
        pie = layout.menu_pie()

        props = pie.operator(ToggleHidePostSetting.bl_idname, text = "Hide/Show", icon = 'NONE') 
        props = pie.operator(SkipPostSettingPieToggleHide.bl_idname, text = "End", icon = 'NONE') 


class RapidBooleanPieTrigger(bpy.types.Operator):
    bl_idname = "wm.rapid_bool_pie_trigger"
    bl_label = "Rapid Boolean Pie Trigger"
    bl_options = {'INTERNAL'}

    def __init__(self):
        self._first_trigger = True 
        self._click_counter = 0
        bpy.context.scene.rpbl_modal_first_action_finished = False
        bpy.context.scene.rpbl_post_modal_locked = False

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        if event.ctrl and context.scene.rpbl_modal_first_action_finished:
            if event.value == 'PRESS':
                for ob in bpy.context.selected_objects:
                    for prop in context.scene.rpbl_selected_objs_name:
                        if ob.name == prop.name:
                            if not context.scene.rpbl_post_modal_locked:
                                context.scene.rpbl_post_modal_locked = True
                                bpy.ops.wm.call_menu_pie(name = PostSettingPieBooleanType.bl_idname)

                    return {'PASS_THROUGH'}

        if self._first_trigger:
            bpy.ops.wm.call_menu_pie(name = RapidBooleanPie.bl_idname)
            self._first_trigger = False 

        if event.type == 'RIGHTMOUSE':
                context.scene.rpbl_post_modal_locked = False 

        if event.type == 'ESC':
            self.report({'INFO'}, "Diactivated Setting Mode")
            return {'CANCELLED'}

        return {'PASS_THROUGH'} 



#####################
# Addon Preferences #
#####################


def get_keymap_item(km, kmi_idname):
    for keymap_item in km.keymap_items:
        if keymap_item.idname == kmi_idname:
            return keymap_item
    return None


class ManageRapidBooleanKeymap(bpy.types.AddonPreferences):
    bl_idname = __name__

    operation_items = [
        ('UNION', 'Union', '', 1), 
        ('DIFFERENCE', 'Difference', '', 2), 
        ('INTERSECT', 'Intersect', '', 3),
    ]

    visible_type_items = [
        ('BOUNDS', 'Bounds', '', 1), 
        ('WIRE', 'Wire', '', 2), 
        ('SOLID', 'Solid', '', 3), 
        ('TEXTURED', 'Textured', '', 4) 
    ]

    operation_enum = EnumProperty(items = operation_items, default = 'DIFFERENCE')
    visible_type_enum = EnumProperty(items = visible_type_items, default = 'WIRE')
    is_first = BoolProperty(default = True)
    post_change = BoolProperty(default = True)

    def draw(self, context):
        layout = self.layout
        idname = RapidBooleanPieTrigger.bl_idname
        keymap_name = '3D View'

        wm = context.window_manager
        kc = wm.keyconfigs.user
        kms = kc.keymaps
        km = kms[keymap_name]
        kmi = get_keymap_item(km, idname)

        box = layout.box()
        split = box.split()
        col = split.column(align = True)
        col.prop(self, 'operation_enum', "Boolean Type")
        col.prop(self, 'visible_type_enum', "Maximum Draw Type")
        col.prop(self, 'is_first', "The main object is first selected one")

        #core draw
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            register_keymap()


###########################
# Register and Unregister #
###########################


class SelectedObjsName(bpy.types.PropertyGroup):
    name = StringProperty()


addon_keymaps = []
addon_modal_keymaps = []


def register_keymap():
    name_spacetype = ('3D View', 'VIEW_3D')
    wm = bpy.context.window_manager

    km = wm.keyconfigs.addon.keymaps.new(name = name_spacetype[0], space_type = name_spacetype[1])

    kmi = km.keymap_items.new(RapidBooleanPieTrigger.bl_idname, 'NONE', 'PRESS', head = True)
    kmi.active = True

    addon_keymaps.append((km, kmi))


def unregister_keymap():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.rpbl_modal_first_action_finished = BoolProperty(default = False)
    bpy.types.Scene.rpbl_post_modal_locked = BoolProperty(default = False)
    bpy.types.Scene.rpbl_target_obj_name = StringProperty()
    bpy.types.Scene.rpbl_selected_objs_name = CollectionProperty(type = SelectedObjsName)
    register_keymap()


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.rpbl_modal_first_action_finished
    del bpy.types.Scene.rpbl_post_modal_locked
    del bpy.types.Scene.rpbl_target_obj_name
    del bpy.types.Scene.rpbl_selected_objs_name
    unregister_keymap()


if __name__ == '__main__':
    register()

