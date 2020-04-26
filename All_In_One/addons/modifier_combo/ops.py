import bpy
from .modifier_combo import ModifierCombo, ComboList, ModifierProxy
from .gui import ComboMenu


class RegisterCombo(bpy.types.Operator):
    bl_idname = "modifier_combo.register_combo"
    bl_label = "Register Combo"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        if not context.object.modifiers:
            return {'FINISHED'}
            
        modifier_combo = ModifierCombo()
        combo_list = ComboList()
        combo_list.restore_from_combo_list_cache()

        for mod in context.object.modifiers:
            modproxy = ModifierProxy(mod = mod)
            modifier_combo.add_mod(modproxy)

        combo_list.add_combo(modifier_combo)
        combo_list.store_to_combo_list_cache()

        return {'FINISHED'}


class UnregisterCombo(bpy.types.Operator):
    bl_idname = "modifier_combo.unregister_combo"
    bl_label = "Unregister Combo"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        combo_list_cache = bpy.context.scene.combo_list_cache
        index = bpy.context.scene.combo_list_selected_index
        combo_list_cache.remove(index)

        if len(bpy.context.scene.combo_list_cache) == index:
            bpy.context.scene.combo_list_selected_index -= 1
        
        return {'FINISHED'}


class MakeCombo(bpy.types.Operator):
    bl_idname = "modifier_combo.make_combo"
    bl_label = "Make Combo"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        combo_list = ComboList()
        combo_list.restore_from_combo_list_cache()
        index = bpy.context.scene.combo_list_selected_index
        flag = False

        if combo_list.combo_list:
            for modproxy in combo_list.combo_list[index].modifier_list:
                if modproxy.mod_type == 'MULTIRES': 
                    for mod in bpy.context.object.modifiers:
                        if mod.type == modproxy.mod_type:
                            flag = True

                    if flag:
                        self.report({'INFO'}, "Modifier requires original data")
                    else:
                        bpy.ops.object.modifier_add(type = modproxy.mod_type)
                        modproxy.apply(bpy.context.object.modifiers[0]) #The multires modifier is always on the top of stack

                else:
                    bpy.ops.object.modifier_add(type = modproxy.mod_type)
                    modproxy.apply(bpy.context.object.modifiers[-1])

        return {"FINISHED"}


class SwapUp(bpy.types.Operator):
    bl_idname = "modifier_combo.swap_up"
    bl_label = "Modifier Combo List Swap up"
    bl_options = {'INTERNAL'}

    def swap_up(self):
        selected_index = bpy.context.scene.combo_list_selected_index
        if selected_index > 0:
            combo_list = ComboList()
            combo_list.restore_from_combo_list_cache()
            combo_list.combo_list[selected_index], combo_list.combo_list[selected_index - 1] = combo_list.combo_list[selected_index - 1], combo_list.combo_list[selected_index]
            combo_list.combo_name_list[selected_index], combo_list.combo_name_list[selected_index - 1] = combo_list.combo_name_list[selected_index - 1], combo_list.combo_name_list[selected_index]
            combo_list.store_to_combo_list_cache()
            bpy.context.scene.combo_list_selected_index -= 1

    def execute(self, context):
        self.swap_up()
        return {'FINISHED'}


class SwapDown(bpy.types.Operator):
    bl_idname = "modifier_combo.swap_down"
    bl_label = "Modifier Combo List Swap Down"
    bl_options = {'INTERNAL'}

    def swap_down(self):
        selected_index = bpy.context.scene.combo_list_selected_index
        if selected_index < len(bpy.context.scene.combo_list_cache) - 1:
            combo_list = ComboList()
            combo_list.restore_from_combo_list_cache()
            combo_list.combo_list[selected_index], combo_list.combo_list[selected_index + 1] = combo_list.combo_list[selected_index + 1], combo_list.combo_list[selected_index]
            combo_list.combo_name_list[selected_index], combo_list.combo_name_list[selected_index + 1] = combo_list.combo_name_list[selected_index + 1], combo_list.combo_name_list[selected_index]
            combo_list.store_to_combo_list_cache()
            bpy.context.scene.combo_list_selected_index += 1

    def execute(self, context):
        self.swap_down()
        return {'FINISHED'}

class MakeComboViaMenu(bpy.types.Operator):
    bl_idname = "modifier_combo.make_combo_via_menu"
    bl_label = "Modifier Combo via Menu"
    bl_options = {'INTERNAL'}

    index = bpy.props.IntProperty()

    def execute(self, context):
        combo_list = ComboList()
        combo_list.restore_from_combo_list_cache()
        flag = False

        if combo_list.combo_list:
            for modproxy in combo_list.combo_list[self.index].modifier_list:
                if modproxy.mod_type == 'MULTIRES': 
                    for mod in bpy.context.object.modifiers:
                        if mod.type == modproxy.mod_type:
                            flag = True

                    if flag:
                        self.report({'INFO'}, "Modifier requires original data")
                    else:
                        bpy.ops.object.modifier_add(type = modproxy.mod_type)
                        modproxy.apply(bpy.context.object.modifiers[0]) #The multires modifier is always on the top of stack

                else:
                    bpy.ops.object.modifier_add(type = modproxy.mod_type)
                    modproxy.apply(bpy.context.object.modifiers[-1])
        return {'FINISHED'}


class ModifierComboMenuTrigger(bpy.types.Operator):
    bl_idname = "modifier_combo.trigger_menu"
    bl_label = "Modifier Combo Menu Trigger"

    def execute(self, context):
        bpy.ops.wm.call_menu(name = ComboMenu.bl_idname)
        return {'FINISHED'}


