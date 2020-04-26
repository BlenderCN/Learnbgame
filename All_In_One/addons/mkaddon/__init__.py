# mkaddon  (c) 2014 dustractor@gmail.com
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
"name":"mkaddon",
"author":"Shams Kitz",
"description":"This may or may not have been a good idea.",
"category": "Learnbgame",
}

import itertools
import sys
import bpy
import re
import os
import string

vis_icns = "RESTRICT_VIEW_ON","RESTRICT_VIEW_OFF"

def remove_extra_blank_lines(text):
    # the silly way
    match_two_newlines_in_a_row = '(^$){2}'
    text_length = len(text)
    atmatch_locations = bytearray( (1,) * text_length )
    last_time = -1
    matches = re.finditer(match_two_newlines_in_a_row,text,flags=re.M)
    for match_object in matches:
        (this_time,_) = match_object.span()
        if (
                ( last_time > -1 ) and
                ( ( last_time + 1 ) == this_time ) and 
                (this_time != text_length)):
            atmatch_locations[this_time] = False
        last_time = this_time
    return "".join(itertools.compress(text,atmatch_locations))


class MKA_UL_mkaddon(bpy.types.UIList):
    def draw_item(self,context,layout,data,item,icon,actvdata,actvprop):
        layout.label(item.txtname)
        row = layout.row(align=True)
        row.prop(item.sections.gpl,"useme",text="gpl",toggle=True)
        row.prop(item.sections.bl_info,"useme",text="info",toggle=True)
        row.prop(item.sections.imports,"useme",text="imports",toggle=True)
        row.prop(item.sections.operators,"useme",text="op",toggle=True)
        row.prop(item.sections.ui_panels,"useme",text="panel",toggle=True)
        row.prop(item.sections.registration,"useme",text="reg",toggle=True)


class MKA_PT_mkaddon_panel(bpy.types.Panel):
    bl_label = "mkaddon"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    def draw(self,context):
        layout = self.layout
        mka = context.window_manager.mka
        active = mka.active
        layout.operator("mkaddon.add",text="mkaddon",icon="PLUS")
        layout.template_list("MKA_UL_mkaddon","",mka,"addons",mka,"i",rows=2)
        if active:
            layout.prop(active,"modname")
            layout.separator()
            layout.label(active.name)
            box = layout.box()
            box.label("Sections:")
            if active.sections.bl_info.useme:
                col = box.box()
                row = col.row()
                row.prop(
                        active.sections.bl_info,"vis",
                        icon=vis_icns[active.sections.bl_info.vis],
                        text="Blender Addon Information",toggle=True)
                if active.sections.bl_info.vis:
                    col.prop(active.sections.bl_info,"name")
                    col.prop(active.sections.bl_info,"description")
                    col.prop(active.sections.bl_info,"author")
                    col.prop(active.sections.bl_info,"version")
                    col.prop(active.sections.bl_info,"blender")
                    col.prop(active.sections.bl_info,"location")
                    col.prop(active.sections.bl_info,"warning")
                    col.prop(active.sections.bl_info,"wiki_url")
                    col.prop(active.sections.bl_info,"category")
            if active.sections.imports.useme:
                col = box.box()
                row = col.row()
                row.prop(
                        active.sections.imports,"vis",
                        icon=vis_icns[active.sections.imports.vis],
                        text="Python Module Imports",toggle=True)
                if active.sections.imports.vis:
                    col.prop(active.sections.imports,"commonpythonmodules")
            if active.sections.operators.useme:
                col = box.box()
                row = col.row()
                row.prop(
                        active.sections.operators,"vis",
                        icon=vis_icns[active.sections.operators.vis],
                        text="Operator",toggle=True)
                if active.sections.operators.vis:
                    col.prop(active.sections.operators,"myname")
            if active.sections.ui_panels.useme:
                col = box.box()
                row = col.row()
                row.prop(
                        active.sections.ui_panels,"vis",
                        icon=vis_icns[active.sections.ui_panels.vis],
                        text="Interface Panel",toggle=True)
                if active.sections.ui_panels.vis:
                    col.prop(active.sections.ui_panels,"myname")
                    col.prop(active.sections.ui_panels,"spacetype")
                    col.prop(active.sections.ui_panels,"regiontype")
                    col.prop(active.sections.ui_panels,"paneloptions")
                    col.prop(active.sections.ui_panels,"bl_category")
                    col.prop(active.sections.ui_panels,"label")
            if active.sections.registration.useme:
                col = box.box()
                row = col.row()
                row.prop(
                        active.sections.registration,"vis",
                        icon=vis_icns[active.sections.registration.vis],
                        text="Registration",toggle=True)
                if active.sections.registration.vis:
                    col.prop(active.sections.registration,"attachments")
                    col.prop(active.sections.registration,"detachments")
            layout.separator()
            savbox = layout.box()
            savbox.prop(active,"saveto")
            if active.saveto == 'other':
                savbox.prop(active,"other_saveto")
            elif active.saveto == 'scripts':
                savbox.prop(active,"scripts_saveto")
            savbox.label(active.saving_to)
            if active.saving_to:
                savbox.operator('mkaddon.save')


class MKA_OT_mk_addon_add(bpy.types.Operator):
    bl_label = "mkaddon:add"
    bl_idname = "mkaddon.add"
    bl_options = {"INTERNAL"}
    def execute(self,context):
        mka = context.window_manager.mka
        addon = mka.addons.add()
        addon.txtname = bpy.data.texts.new('mka_addon.py').name
        mka.i += 1
        return {"FINISHED"}


class MKA_OT_mk_addon_save(bpy.types.Operator):
    bl_label = "mkaddon:save"
    bl_idname = "mkaddon.save"
    bl_options = {"INTERNAL"}
    def execute(self,context):
        addon = context.window_manager.mka.active
        if not addon:
            return {"CANCELLED"}
        savto = addon.saving_to
        text = addon.toString()
        with open(savto,'w') as f:
            f.write(text)
        self.report({'INFO'},savto)
        return {"FINISHED"}


def propupdate(self,context):
    context.window_manager.mka.i = context.window_manager.mka.i

def read_template(
        template,
        here=lambda f,root=os.path.dirname(__file__):os.path.join(root,f)):
    return string.Template(open(here(template),"r").read()).safe_substitute

def EnumItems(*items):
    return [(e,e,e) for e in items]


class AddonSection:
    @property
    def templated(self):
        return self.template(
                {k:getattr(self,k) for k in self.myall}) if self.useme else ""


class GPLSection(bpy.types.PropertyGroup,AddonSection):
    myall = []
    template = read_template("gpl_block.txt")


class InfoSection(bpy.types.PropertyGroup,AddonSection):
    myall = ["name","description","author","version_str","blender_str",
            "location","warning","wiki_url","category"]
    template = read_template("bl_info_template.txt")
    name = bpy.props.StringProperty(default="AddonName",update=propupdate)
    description = bpy.props.StringProperty(default="",update=propupdate)
    author = bpy.props.StringProperty(default="",update=propupdate)
    version = bpy.props.IntVectorProperty(size=2,default=(0,1),
            update=propupdate)
    blender = bpy.props.IntVectorProperty(size=3,default=(2,65,0),
            update=propupdate)
    location = bpy.props.StringProperty(default="",update=propupdate)
    warning = bpy.props.StringProperty(default="",update=propupdate)
    wiki_url = bpy.props.StringProperty(default="",update=propupdate)
    category = bpy.props.EnumProperty(default="Development",update=propupdate,
            items=EnumItems(
                "3D View", "Add Mesh", "Add Curve", "Animation",
                "Compositing", "Game Engine", "Import-Export", "Lighting",
                "Material", "Mesh", "Object", "Physics ",
                "Render", "System", "Development", "Text Editor"))
    @property
    def version_str(self):
        return ",".join(map(str,self.version))
    @property
    def blender_str(self):
        return ",".join(map(str,self.blender))


class ImportsSection(bpy.types.PropertyGroup,AddonSection):
    myall = "imports",
    template = read_template("imports_template.txt")
    commonpythonmodules = bpy.props.EnumProperty(
            items=EnumItems(
                #max 32 items (should be more than enough)
                "bpy","os","sys","mathutils","bgl","blf","itertools"
                ),default={'bpy'},options={'ENUM_FLAG'},update=propupdate)
    @property
    def imports(self):
        if len(self.commonpythonmodules):
            return os.linesep.join(
                    sorted(map("import %s".__mod__,self.commonpythonmodules)))
        return ""


class ModNamed:
    @property
    def opclassname(self):
        return self.id_data.mka.active.modname.upper() + "_OT_" + \
                self.myname.lower().replace(" ","_")
    @property
    def panelclassname(self):
        return self.id_data.mka.active.modname.upper() + "_PT_" + \
                self.myname.lower().replace(" ","_")
    @property
    def idname(self):
        return self.id_data.mka.active.modname.lower() + "." + \
                self.myname.lower().replace(" ","_")
    @property
    def label(self):
        return self.id_data.mka.active.modname.title() + ":" + \
                self.myname.title()
    @property
    def options(self):
        if len(self.paneloptions):
            return "bl_options = " + repr(self.paneloptions)
        return ""


class InterfacePanelSection(bpy.types.PropertyGroup,AddonSection,ModNamed):
    myall = (
            "panelclassname","spacetype","regiontype","options","label","op",
            "toolcategory")
    template = read_template("interface_panel_template.txt")
    myname = bpy.props.StringProperty(default="myname",update=propupdate)
    spacetype = bpy.props.EnumProperty(
            items=EnumItems(
                "EMPTY", "VIEW_3D", "TIMELINE", "GRAPH_EDITOR",
                 "DOPESHEET_EDITOR", "NLA_EDITOR", "IMAGE_EDITOR",
                 "SEQUENCE_EDITOR", "CLIP_EDITOR", "TEXT_EDITOR",
                 "NODE_EDITOR", "LOGIC_EDITOR", "PROPERTIES",
                 "OUTLINER", "USER_PREFERENCES", "INFO",
                 "FILE_BROWSER", "CONSOLE" ),
            default="VIEW_3D",
            update=propupdate)
    regiontype = bpy.props.EnumProperty(
            items=EnumItems( "WINDOW", "HEADER", "CHANNELS", "TEMPORARY",
            "UI", "TOOLS", "TOOL_PROPS", "PREVIEW"),
            default="TOOLS",update=propupdate)
    bl_category = bpy.props.StringProperty(default="Quux",update=propupdate)
    paneloptions = bpy.props.EnumProperty(
            items=EnumItems("HIDE_HEADER","DEFAULT_CLOSED"),
            options={"ENUM_FLAG"},update=propupdate)
    label = bpy.props.StringProperty(default="MyLabel",update=propupdate)
    @property
    def op(self):
        active = self.id_data.mka.active
        if active:
            ops = active.sections.operators
            if ops.useme:
                return 'layout.operator("%s")' % ops.idname
        return ""
    @property
    def toolcategory(self):
        if self.spacetype == 'VIEW_3D' and self.regiontype == 'TOOLS':
            if len(self.bl_category):
                return 'bl_category = "%s"' % self.bl_category
        return ""


class OperatorSection(bpy.types.PropertyGroup,AddonSection,ModNamed):
    myall = "opclassname","myname","idname","label"
    template = read_template("operator_template.txt")
    myname = bpy.props.StringProperty(default="myname",update=propupdate)


class RegistrationSection(bpy.types.PropertyGroup,AddonSection):
    myall = "attachments","detachments"
    template = read_template("registration_template.txt")
    attachments = bpy.props.StringProperty(default="",update=propupdate)
    detachments = bpy.props.StringProperty(default="",update=propupdate)


for cls in AddonSection.__subclasses__():
    cls.useme = bpy.props.BoolProperty(update=propupdate)
    cls.vis = bpy.props.BoolProperty(default=True,update=propupdate)


class AddonSections(bpy.types.PropertyGroup):
    myall = [
            "gpl","bl_info","imports",
            "operators","ui_panels","registration"]
    gpl = bpy.props.PointerProperty(type=GPLSection)
    bl_info = bpy.props.PointerProperty(type=InfoSection)
    imports = bpy.props.PointerProperty(type=ImportsSection)
    operators = bpy.props.PointerProperty(type=OperatorSection)
    ui_panels = bpy.props.PointerProperty(type=InterfacePanelSection)
    registration = bpy.props.PointerProperty(type=RegistrationSection)
    @property
    def data(self):
        return {k:getattr(self,k).templated for k in self.myall}


class MKAddon(bpy.types.PropertyGroup):
    @property
    def saving_to(self):
        if self.saveto == 'other':
            return self.other_saveto
        name = self.modname + ".py"
        if self.saveto == 'desktop':
            return os.path.join(os.path.expanduser('~/Desktop'),name)
        elif self.saveto == 'scripts':
            if self.scripts_saveto == 'pref':
                return os.path.join(bpy.utils.script_path_pref(),'addons',name)
            if self.scripts_saveto == 'user':
                return os.path.join(bpy.utils.script_path_user(),'addons',name)
    template = read_template("addon_template.txt")
    txtname = bpy.props.StringProperty()
    modname = bpy.props.StringProperty(default='foo',update=propupdate)
    saveto = bpy.props.EnumProperty(
            items=EnumItems("desktop","scripts","other"),default="desktop")
    scripts_saveto = bpy.props.EnumProperty(
            items=EnumItems("user","pref"),default="pref")
    other_saveto = bpy.props.StringProperty(subtype='FILE_PATH')
    sections = bpy.props.PointerProperty(type=AddonSections)
    def toString(self):
        return remove_extra_blank_lines(self.template(self.sections.data))


def update(self,context):
    if self.active != None:
        mytxt = bpy.data.texts[self.active.txtname]
        mytxt.from_string(self.active.toString())
        context.area.spaces[0].text = mytxt
        bpy.ops.text.jump()


class MKAProp(bpy.types.PropertyGroup):
    addons = bpy.props.CollectionProperty(type=MKAddon)
    i = bpy.props.IntProperty(min=-1,default=-1,update=update)
    @property
    def active(self):
        return self.addons[self.i] if 0 <= self.i < len(self.addons) else None


def register():
    bpy.utils.register_module(__name__)
    bpy.types.WindowManager.mka = bpy.props.PointerProperty(type=MKAProp)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.WindowManager.mka
