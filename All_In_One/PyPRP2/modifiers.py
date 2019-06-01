#    This file is part of PyPRP2.
#    
#    Copyright (C) 2010 PyPRP2 Project Team
#    See the file AUTHORS for more info about the team.
#    
#    PyPRP2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    
#    PyPRP2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with PyPRP2.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.props import *
import os
import os.path
import sys

mod_types = []

def getModTypes(self, context):
    l = []
    for mod_type in mod_types:
        l.append((mod_type, mod_type, ''))
    return l

def add_mod_menu(mod):
    return lambda self, context: self.layout.operator(mod.bl_idname, text=mod.bl_label)

def getClassFromModType(modtype):
    return getattr(bpy.types, 'OBJECT_OT_' + modtype)

def getModFromLink(modlink, scene):
    collection = getattr(scene.plasma_modifiers, modlink.modclass)
    return collection[modlink.name]

def getModifierApplication(modlink):
    return getClassFromModType(modlink.modclass).application

def cleanLinkList(ob, context):
    pl = ob.plasma_settings
    modlinks = pl.modifiers
    i = 0
    while i < len(modlinks):
        modlink = modlinks[i]
        if not modlink.name:
            pass
        elif modDataExists(modlink, context.scene):
            mod = getModFromLink(modlink, context.scene)
            app = getModifierApplication(modlink)
            if app == 'single':
                if mod.owner != ob.name:
                    modlinks.remove(i)
                    continue
        #data doesn't exist
        else:
            modlinks.remove(i)
            continue
        i+=1
    if not pl.activemodifier < len(modlinks):
        pl.activemodifier = len(modlinks)-1

def cleanUnusedModLinks(context):
    for ob in context.scene.objects:
        cleanLinkList(ob, context)

def modDataExists(modlink, scene):
    if modlink.modclass == 'pltypeunset':
        return False
    collection = getattr(scene.plasma_modifiers, modlink.modclass)
    return modlink.name in collection.keys()

def modLinkNameUpdate(self, context):
    if self.modclass == 'pltypeunset' or not modDataExists(self, context.scene):
        return
    mod_app = getModifierApplication(self)
    if mod_app == 'single':
        mod = getModFromLink(self, context.scene)
        #check if we already have another owner and delete the old link if we do
        obname = context.object.name
        if mod.owner == obname:
            return
        if mod.owner == '':
            mod.owner = obname 

class PlasmaModifierMenu(bpy.types.Menu):
    bl_idname = 'PlasmaModifierMenu'
    bl_label = 'Add Modifier'
    bl_description = 'Add a new modifier'

    submenus = []

    __menuid = 'PlasmaModifierCat{0}'
    __menucls = "class {0}(bpy.types.Menu):\n    bl_idname = '{0}'\n    bl_label = '{1}'\n    def draw(self, context):\n        self.layout.operator_context = 'EXEC_AREA'\nbpy.utils.register_class({0})"

    @staticmethod
    def AddCategory(name):
        mnuid = PlasmaModifierMenu.__menuid.format(name)
        mnucls = PlasmaModifierMenu.__menucls.format(mnuid, name)
        exec(mnucls) #EVIL Hack

        PlasmaModifierMenu.submenus.append(mnuid)

    @staticmethod
    def AddModifier(mod):
        mnuid = PlasmaModifierMenu.__menuid.format(mod.category)
        if not mnuid in PlasmaModifierMenu.submenus:
            PlasmaModifierMenu.AddCategory(mod.category)

        getattr(bpy.types, mnuid).append(add_mod_menu(mod))

    def draw(self, context):
        layout = self.layout
        
        for mnu in PlasmaModifierMenu.submenus:
            layout.menu(mnu)

class PlasmaModifiers(bpy.types.PropertyGroup):
    pass

class PlasmaModifierLink(bpy.types.PropertyGroup):
    name = StringProperty(update=modLinkNameUpdate)
    modclass = EnumProperty(items=getModTypes,
                            name="Modifier Type",
                            description="Modifier Type")

class PlasmaModifierRemove(bpy.types.Operator):
    bl_idname = 'object.plremovemodifier'
    bl_label = 'Remove Modifier'
    bl_description = 'Remove the active modifier'

    @classmethod
    def poll(self, context):
        return context.active_object != None
        
    def execute(self, context):
        ob = context.object
        pl = ob.plasma_settings
        pl.modifiers.remove(pl.activemodifier)
        pl.activemodifier -= 1
        return {'FINISHED'}

class PlasmaModifierDataRemove(bpy.types.Operator):
    bl_idname = 'object.plremovemodifierdata'
    bl_label = 'Remove Modifier Data'
    bl_description = 'Remove modifier settings'

    @classmethod
    def poll(self, context):
        return context.active_object != None
        
    def execute(self, context):
        ob = context.object
        pl = ob.plasma_settings
        ml = pl.modifiers[pl.activemodifier]
        if modDataExists(ml, context.scene):
            mod = getModFromLink(ml, context.scene)
            collection = getattr(context.scene.plasma_modifiers, mod.type)
            m_index = collection.keys().index(mod.name)
            collection.remove(m_index)
            cleanLinkList(ob, context)
        return {'FINISHED'}

class PlasmaModifierPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'constraint'
    bl_label = 'Plasma Modifiers'

    def draw(self, context):
        layout = self.layout

        ob = context.object
        layout.label(text = 'Attached Modifiers:')
        row = layout.row()
        col = row.column()

        pl = ob.plasma_settings

        #keep last entry is blank
        i = 0
        while i < len(pl.modifiers):
            if pl.modifiers[i].name == "" and (i != len(pl.modifiers)-1):
                pl.modifiers.remove(i)
            else:
                i+=1;
        if len(pl.modifiers) == 0:
            pl.modifiers.add()
        elif pl.modifiers[-1].name != "":
            pl.modifiers.add()
        
        #get rid of un-linked ref
        cleanLinkList(ob, context)
        
        col.template_list(ob.plasma_settings, 'modifiers', ob.plasma_settings, 'activemodifier', rows = 2)

        col = row.column(align = True)
        col.menu('PlasmaModifierMenu', icon = 'ZOOMIN', text = '')
        col.operator('object.plremovemodifier', icon = 'ZOOMOUT', text = '')

        mod_link = pl.modifiers[pl.activemodifier]

        layout.label(text='Link')
        box = layout.box()
        if mod_link.modclass != 'pltypeunset':
            box.prop_search(mod_link, 'name', context.scene.plasma_modifiers, mod_link.modclass, text = '')
        box.prop(mod_link, 'modclass', text = 'Type')

        if mod_link.name and modDataExists(mod_link, context.scene):
            mod = getModFromLink(mod_link, context.scene)
            layout.label(text='Data')
            box = layout.box()
            row = box.row()
            row.operator('object.plremovemodifierdata', icon = 'PANEL_CLOSE', text = '')
            c = getClassFromModType(mod_link.modclass)
            box.prop(mod, 'name', text = 'Name')
            c.Draw(box, ob, mod)


def register():
    global mod_types

    bpy.utils.register_class(PlasmaModifierMenu)
    bpy.utils.register_class(PlasmaModifierLink)
    bpy.utils.register_class(PlasmaModifierDataRemove)
    bpy.utils.register_class(PlasmaModifiers)
    bpy.utils.register_class(PlasmaModifierRemove)
    bpy.utils.register_class(PlasmaModifierPanel)
    
    mod_types = ['pltypeunset']
    modpath = os.path.join(os.path.split(__file__)[0],"mods/")
    mods = [fname[:-3] for fname in os.listdir(modpath) if fname.endswith('.py')]
    if not modpath in sys.path:
        sys.path.append(modpath)
    modifiers = [__import__(mname) for mname in mods]
    modifier_operators = []
    for mod in modifiers:
        registered = mod.register()
        for bmod, bmod_data in registered:
            PlasmaModifierMenu.AddModifier(bmod)
            typename = bmod.bl_idname.split(".")[1]
            prop = CollectionProperty(typename, type = bmod_data)
            setattr(PlasmaModifiers, typename, prop)
            mod_types.append(typename)
    bpy.types.Scene.plasma_modifiers = PointerProperty(type = PlasmaModifiers)

def unregister():
    modpath = os.path.join(os.path.split(__file__)[0],"mods/")
    mods = [fname[:-3] for fname in os.listdir(modpath) if fname.endswith('.py')]
    if not modpath in sys.path:
        sys.path.append(modpath)
    modifiers = [__import__(mname) for mname in mods]
    [mod.unregister() for mod in modifiers]
    bpy.utils.unregister_class(PlasmaModifierPanel)
    bpy.utils.unregister_class(PlasmaModifierDataRemove)
    bpy.utils.unregister_class(PlasmaModifierRemove)
    bpy.utils.unregister_class(PlasmaModifiers)
    bpy.utils.unregister_class(PlasmaModifierLink)
    bpy.utils.unregister_class(PlasmaModifierMenu)
