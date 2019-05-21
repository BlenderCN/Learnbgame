import bpy
from .cache_class import PropCache, ComboCache, ComboListCache
from .modifier_proxy import ModifierProxy


"""Trigger Flows"""
#restore_from_combo_list_cache => restore_from_combo_cache => restore_from_prop_cache
#store_to_combo_list_cache => store_to_combo_cache => store_to_prop_cache


class ModifierCombo:
    def __init__(self):
        self.modifier_list = []

    def add_mod(self, mod_proxy):
        self.modifier_list.append(mod_proxy)

    def remove_mod(self):
        self.modifier_list.pop()

    def store_to_combo_cache(self, combo_cache):
        for num, mod in enumerate(self.modifier_list):
            combo_cache.add()
            combo_cache[num].mod_type = self.modifier_list[num].mod_type

            self.modifier_list[num].store_to_prop_cache(combo_cache[num].props)

    def restore_from_combo_cache(self, combo_cache):
        if not self.modifier_list:
            for mod_cache in combo_cache:
                mod_proxy = ModifierProxy(mod_cache = mod_cache)
                self.modifier_list.append(mod_proxy)


class ComboList:
    def __init__(self):
        self.combo_list = []
        self.combo_name_list = []

    def add_combo(self, mod_combo):
        self.combo_list.append(mod_combo)
        self.combo_name_list.append("")

    def remove_mod(self, num):
        self.combo_list.pop(num)
        self.combo_name_list.pop(num)

    def store_to_combo_list_cache(self):
        bpy.context.scene.combo_list_cache.clear()
        for num, combo in enumerate(self.combo_list):
            bpy.context.scene.combo_list_cache.add()

            #if bpy.context.scene.combo_list_cache[num].combo_name == '':
            if self.combo_name_list[num] == "":
                for modproxy in self.combo_list[num].modifier_list:
                    bpy.context.scene.combo_list_cache[num].combo_name += modproxy.mod_type + ", "
            else:
                bpy.context.scene.combo_list_cache[num].combo_name = self.combo_name_list[num]

            self.combo_list[num].store_to_combo_cache(bpy.context.scene.combo_list_cache[num].combo)

    def restore_from_combo_list_cache(self):
        combo_list_cache = bpy.context.scene.combo_list_cache
        if not self.combo_list:
            for combo_cache in combo_list_cache:
                combo = ModifierCombo()
                combo.restore_from_combo_cache(combo_cache.combo)

                self.combo_list.append(combo)
                self.combo_name_list.append(combo_cache.combo_name)

