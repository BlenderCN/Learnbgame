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
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110 - 1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
"name" : "Gradience",
"author" : "dustractor@gmail.com",
"version" : (0,10000),
"blender" : (2, 6, 9),
"api" : 61000,
"location" : "Gradience Tab",
"description" : "Generates sequences of colors.",
"warning" : "",
"wiki_url" : "",
"tracker_url" : "",
"category" : "Material"
}

from math import modf,sin
import random
from itertools import cycle

import bpy
from bl_operators.presets import AddPresetBase
from mathutils import Color

# import selection_utils

_k = (
        "g_offs",
        "hue_freq",
        "hue_magn",
        "hue_offs",
        "sat_freq",
        "sat_magn",
        "sat_offs",
        "val_freq",
        "val_magn",
        "val_offs")

def gradience_iter(g,n):
    if not n:
        yield StopIteration
    go = g.g_offs
    hf = g.hue_freq
    hm = g.hue_magn
    ho = g.hue_offs
    sf = g.sat_freq
    sm = g.sat_magn
    so = g.sat_offs
    vf = g.val_freq
    vm = g.val_magn
    vo = g.val_offs
    per = 1.0 / n
    hue,sat,val = g.base_color.hsv
    for i in range(n):
        j = go + (per * i)
        hue += sin((j*hf) + ho) * hm
        sat += sin((j*sf) + so) * sm
        val += sin((j*vf) + vo) * vm
        yield (modf(hue)[0],modf(sat)[0],modf(val)[0])


def update_gradience(self,context):
    if not context.active_object:
        return
    gradience = context.active_object.gradience
    total = len(gradience.colors)
    for n,k in enumerate(gradience_iter(gradience,total)):
        gradience.colors[n].color.hsv = k


def gradience_controls(layout,gradience):
    row = layout.row(align=True)
    row.operator("gradience.assign",icon="FORWARD").mode = "MATERIALS"
    row.operator("gradience.assign",icon="FORWARD").mode = "MATERIALS_UNIQUE"
    row.operator("gradience.assign",icon="FORWARD").mode = "VERTEX_COLORS"
    row.operator("gradience.to_ramp")
    box = layout.box()
    row = box.row(align=True)
    row.menu("GRADIENCE_MT_preset_menu")
    row.operator("gradience.add_preset",text="",icon="ZOOMIN")
    row.operator("gradience.add_preset",text="",icon="ZOOMOUT").remove_active=True
    row = box.row(align=True)
    row.label(icon="BLANK1")
    row.label("Hue")
    row.label("Saturation")
    row.label("Value")
    row = box.row(align=True)
    split = row.split(percentage=0.12)
    col = split.column(align=True)
    col.label("Freq")
    col.label("Magn")
    col.label("Offs")
    col = split.column(align=True)
    row = col.row(align=True)
    row.prop(gradience,"hue_freq",text="")
    row.prop(gradience,"hue_magn",text="")
    row.prop(gradience,"hue_offs",text="")
    row = col.row(align=True)
    row.prop(gradience,"sat_freq",text="")
    row.prop(gradience,"sat_magn",text="")
    row.prop(gradience,"sat_offs",text="")
    row = col.row(align=True)
    row.prop(gradience,"val_freq",text="")
    row.prop(gradience,"val_magn",text="")
    row.prop(gradience,"val_offs",text="")
    box.prop(gradience,"g_offs")
    box.operator("gradience.randomize")

def gradience_display(layout,gradience):
    layout.operator("gradience.add",
            text="Colors: %d" % len(gradience.colors),icon="ZOOMIN")
    box = layout.box()
    col = box.column(align=True)
    for n,color in enumerate(gradience.colors):
        row = col.row(align=True)
        row.scale_y = 0.8
        row.prop(color,"color",text="")
        row.operator("gradience.del",icon="X",text="",emboss=False).n = n
    layout.operator("gradience.to_palette")

def palette_display(layout,palette):
    box = layout.box()
    col = box.column(align=True)
    for color in palette.colors:
        row = col.row(align=True)
        row.prop(color,"color",text="")
    box = layout.box()
    row = box.row(align=True)
    row.menu("GRADIENCE_MT_palette_preset_menu")
    row.operator("gradience.add_palette_preset",
            text="",icon="ZOOMIN")
    row.operator("gradience.add_palette_preset",
            text="",icon="ZOOMOUT").remove_active=True


class colour(bpy.types.PropertyGroup):
    rgba = property(fget=lambda s:tuple(s.color)+(1.0,))
    color = bpy.props.FloatVectorProperty(min=0.0,max=1.0,subtype="COLOR")


class PaletteProperty(bpy.types.PropertyGroup):
    colors = bpy.props.CollectionProperty(type=colour)


class GradienceProperty(bpy.types.PropertyGroup):
    display = bpy.props.BoolProperty()
    base_color = bpy.props.FloatVectorProperty(
            default=(0.0,0.0,0.0),
            min=0.0,max=1.0,
            precision=7,subtype="COLOR",update=update_gradience)
    colors = bpy.props.CollectionProperty(type=colour)
    defaultd = dict(update=update_gradience,subtype="UNSIGNED",precision=7)
    hue_freq = bpy.props.FloatProperty(default=1.0,**defaultd)
    hue_magn = bpy.props.FloatProperty(default=1.0,**defaultd)
    hue_offs = bpy.props.FloatProperty(default=0.0,**defaultd)
    sat_freq = bpy.props.FloatProperty(default=0.0,**defaultd)
    sat_magn = bpy.props.FloatProperty(default=1.0,**defaultd)
    sat_offs = bpy.props.FloatProperty(default=1.5,**defaultd)
    val_freq = bpy.props.FloatProperty(default=0.0,**defaultd)
    val_magn = bpy.props.FloatProperty(default=1.0,**defaultd)
    val_offs = bpy.props.FloatProperty(default=1.5,**defaultd)
    g_offs = bpy.props.FloatProperty(default=0.0,**defaultd)


class GRADIENCE_OT_to_palette(bpy.types.Operator):
    bl_idname = "gradience.to_palette"
    bl_label = "gradience to palette"
    def execute(self,context):
        gradience = context.active_object.gradience
        palette = context.active_object.palette
        while len(palette.colors) > len(gradience.colors):
            palette.colors.remove(palette.colors[-1])
        while len(palette.colors) < len(gradience.colors):
            palette.colors.add()
        for g,p in zip(gradience.colors,palette.colors):
            p.color = g.color
        return {"FINISHED"}


class GRADIENCE_OT_add(bpy.types.Operator):
    bl_idname = "gradience.add"
    bl_label = "add gradience slot"
    def execute(self,context):
        gradience = context.active_object.gradience
        gradience.colors.add()
        update_gradience(None,context)
        return {"FINISHED"}


class GRADIENCE_OT_del(bpy.types.Operator):
    bl_idname = "gradience.del"
    bl_label = "delete gradience slot"
    n = bpy.props.IntProperty()
    def execute(self,context):
        context.active_object.gradience.colors.remove(self.n)
        return {"FINISHED"}


class GRADIENCE_OT_assign(bpy.types.Operator):
    bl_idname = "gradience.assign"
    bl_label = "assign  gradience to selected"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    mode = bpy.props.EnumProperty(
            items=[(_,)*3 for _ in (
                "MATERIALS","MATERIALS_UNIQUE","VERTEX_COLORS")],
            default="MATERIALS")
    def execute(self,context):
        gradience = context.active_object.gradience
        colorx = cycle([each.color for each in gradience.colors])
        get_color = colorx.__next__


        if self.mode =="VERTEX_COLORS":
            ob = context.object
            me = ob.data
            vcols = me.vertex_colors.active.data
            for vx in vcols:
                c = get_color()
                vx.color = (c[0],c[1],c[2])
        else:
            if self.mode == "MATERIALS_UNIQUE":
                bpy.ops.object.make_single_user(
                        type="SELECTED_OBJECTS", material=True)
            selected_objects = [
                    ob for ob in bpy.data.objects
                    if ob.select and ob.type in {"LAMP","MESH","CURVE"}]
            for ob in selected_objects:
                if ob.type in {"CURVE","MESH"}:
                        if not len(ob.data.materials):
                            mat = bpy.data.materials.new("cw_mat")
                            ob.data.materials.append(mat)
                        else:
                            mat = ob.data.materials[0]
                        mat.diffuse_color = get_color()
                elif ob.type == "LAMP":
                    ob.data.color = get_color()
        return {"FINISHED"}


class GRADIENCE_OT_gradience_to_ramp(bpy.types.Operator):
    bl_label = "Ramp"
    bl_idname = "gradience.to_ramp"
    constant = bpy.props.BoolProperty()
    def invoke(self,context,event):
        self.constant = event.shift or event.alt or event.oskey or event.ctrl
        return self.execute(context)
    def execute(self,context):
        colors = context.active_object.gradience.colors
        colorcount = len(colors)
        if not colorcount:
            return {"CANCELLED"}
        r = None
        mat = context.active_object.data.materials[0]
        mat.use_diffuse_ramp = True
        r = mat.diffuse_ramp
        if self.constant:
            r.interpolation = "CONSTANT"
        ramp = r.elements
        while len(ramp) > 1:
            ramp.remove(ramp[-1])
        ramp[0].position = 0.0
        ramp[0].color = colors[0].rgba
        inc = 1.0 / (colorcount-1)
        for j in range(1,colorcount):
            n = ramp.new(j*inc)
            n.color=colors[j].rgba
        return {"FINISHED"}


class GRADIENCE_OT_randomize(bpy.types.Operator):
    bl_idname = "gradience.randomize"
    bl_label = "randomize"
    def execute(self,context):
        gradience = context.active_object.gradience
        for att in _k:
            setattr(gradience,att,random.random())
        return {"FINISHED"}


class GRADIENCE_MT_palette_preset_menu(bpy.types.Menu):
    bl_label = "Gradience Palettes"
    bl_idname= "GRADIENCE_MT_palette_preset_menu"
    preset_subdir = "gradience_palettes"
    preset_operator = "script.execute_preset"
    draw = bpy.types.Menu.draw_preset


class GRADIENCE_MT_preset_menu(bpy.types.Menu):
    bl_label = "Gradience Presets"
    bl_idname= "GRADIENCE_MT_preset_menu"
    preset_subdir = "gradience"
    preset_operator = "script.execute_preset"
    draw = bpy.types.Menu.draw_preset


class GRADIENCE_OT_palette_preset_add(AddPresetBase,bpy.types.Operator):
    bl_idname = "gradience.add_palette_preset"
    bl_label = "add palette preset"
    preset_menu = "GRADIENCE_MT_palette_preset_menu"
    preset_subdir = "gradience_palettes"
    preset_defines = [ "palette = bpy.context.active_object.palette" ]
    preset_values = ["palette.colors"]


class GRADIENCE_OT_preset_add(AddPresetBase,bpy.types.Operator):
    bl_idname = "gradience.add_preset"
    bl_label = "add preset"
    preset_menu = "GRADIENCE_MT_preset_menu"
    preset_subdir = "gradience"
    preset_defines = [ "gradience = bpy.context.active_object.gradience" ]
    preset_values = ["gradience.colors"] + ["gradience.%s" % _ for _ in _k]


class GRADIENCE_PT_gradience(bpy.types.Panel):
    bl_label = "Gradience"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Gradience"
    bl_options = {"HIDE_HEADER"}
    def draw_header(self,context):
        row = self.layout.row(align=True)
        row.label(icon="COLOR")
    def draw(self,context):
        layout = self.layout
        layout.separator()
        gradience = context.active_object.gradience
        palette = context.active_object.palette
        gradience_controls(layout,gradience)
        gradience_display(layout,gradience)
        palette_display(layout,palette)


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Object.gradience = bpy.props.PointerProperty(type=GradienceProperty)
    bpy.types.Object.palette = bpy.props.PointerProperty(type=PaletteProperty)

def unregister():
    del bpy.types.Object.gradience
    del bpy.types.Object.palette
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()



