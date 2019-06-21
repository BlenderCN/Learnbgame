#+
# This add-on script for Blender 2.6 loads a set of colours from
# a Gimp .gpl file and creates a set of simple materials that use
# them, assigned to swatch objects created in a separate scene
# in the current document. From there they may be browsed and reused
# in other objects as needed.
#
# Copyright 2012 Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#-

import sys # debug
import math
import bpy
import mathutils

bl_info = \
    {
        "name" : "Gimp Palettes",
        "author" : "Lawrence D'Oliveiro <ldo@geek-central.gen.nz>",
        "version" : (0, 3, 3),
        "blender" : (2, 6, 1),
        "location" : "View3D > Add > External Materials > Load Palette...",
        "description" :
            "loads colours from a Gimp .gpl file into a set of swatch objects",
        "warning" : "",
        "wiki_url" : "",
        "tracker_url" : "",
        "category": "Learnbgame",
    }

class Failure(Exception) :

    def __init__(self, msg) :
        self.msg = msg
    #end __init__

#end Failure

# Empty string as identifier for an enum item results in item
# appearing as disabled, which is why I use a single space instead
no_object = " "
no_material = " "

def import_palette(parms) :
    try :
        palette_file = open(parms.filepath, "r")
    except IOError as why :
        raise Failure(str(why))
    #end try
    if palette_file.readline().strip() != "GIMP Palette" :
        raise Failure("doesn't look like a GIMP palette file")
    #end if
    name = "Untitled"
    while True :
        line = palette_file.readline()
        if len(line) == 0 :
            raise Failure("palette file seems to be empty")
        #end if
        line = line.rstrip("\n")
        if line.startswith("Name: ") :
            name = line[6:].strip()
        #end if
        if line.startswith("#") :
            break
    #end while
    colours = []
    while True :
        line = palette_file.readline()
        if len(line) == 0 :
            break
        if not line.startswith("#") :
            line = line.rstrip("\n")
            components = line.split("\t", 1)
            if len(components) == 1 :
                components.append("") # empty name
            #end if
            try :
                colour = tuple(int(i.strip()) / 255.0 for i in components[0].split(None, 2))
            except ValueError :
                raise Failure("bad colour on line %s" % repr(line))
            #end try
            colours.append((colour, components[1]))
        #end if
    #end while
  # all successfully loaded
    prev_scene = bpy.context.scene
    bpy.ops.object.select_all(action = "DESELECT")
    bpy.ops.scene.new(type = "NEW")
    the_scene = bpy.context.scene
    the_scene.name = parms.scene_name
    the_scene.world = prev_scene.world
    if parms.base_object != no_object and parms.base_object in bpy.data.objects :
        swatch_object = bpy.data.objects[parms.base_object]
    else :
        swatch_object = None
    #end if
    if swatch_object != None :
        swatch_material = bpy.data.materials[parms.base_material]
        x_offset, y_offset = tuple(x * 1.1 for x in tuple(swatch_object.dimensions.xy))
    else :
        swatch_material = None
        x_offset, y_offset = 2.2, 2.2 # nice margins assuming default mesh size of 2x2 units
    #end if
    per_row = math.ceil(math.sqrt(len(colours)))
    row = 0
    col = 0
    layers = (True,) + 19 * (False,)
    for colour in colours :
        bpy.ops.object.select_all(action = "DESELECT") # ensure materials get added to right objects
        location = mathutils.Vector((row * x_offset, col * y_offset, 0.0))
        if swatch_object != None :
            swatch = swatch_object.copy()
            swatch.data = swatch.data.copy() # ensure material slots are not shared
            the_scene.objects.link(swatch)
            swatch.layers = layers
            swatch.location = location
        else :
            bpy.ops.mesh.primitive_plane_add \
              (
                layers = layers,
                location = location
              )
            swatch = bpy.context.selected_objects[0]
        #end if
        col += 1
        if col == per_row :
            col = 0
            row += 1
        #end if
        material_name = "%s_%s" % (name, colour[1])
        if swatch_material != None :
            material = swatch_material.copy()
            for i in range(0, len(swatch.data.materials)) :
                if swatch.data.materials[i] == swatch_material :
                    swatch.data.materials[i] = material
                    swatch.active_material_index = i
                #end if
            #end for
            material.name = material_name
        else :
            material = bpy.data.materials.new(material_name)
            swatch.data.materials.append(material)
        #end if
        if parms.use_as_diffuse :
            material.diffuse_intensity = parms.diffuse_intensity
            material.diffuse_color = colour[0]
        #end if
        if parms.use_as_specular :
            material.specular_intensity = parms.specular_intensity
            material.specular_color = colour[0]
        #end if
        if parms.use_as_mirror :
            material.raytrace_mirror.reflect_factor = parms.mirror_reflect
            material.mirror_color = colour[0]
        #end if
        if parms.use_as_sss :
            material.subsurface_scattering.color = colour[0]
        #end if
    #end for
#end import_palette

def list_objects(self, context) :
    return \
        (
            (
                (no_object, "<Default Simple Plane>", ""),
            )
        +
            tuple
              (
                (o.name, o.name, "")
                    for o in bpy.data.objects
                    if
                            o.type == "MESH"
                        and
                            len(o.data.materials) != 0
                        and
                            o.name.find(self.base_object_match) >= 0
              )
        )
#end list_objects

def list_object_materials(self, context) :
    the_object_name = self.base_object
    if the_object_name != no_object and the_object_name in bpy.data.objects :
        the_object = bpy.data.objects[the_object_name]
        result = tuple \
          (
            (m.name, m.name, "") for m in the_object.data.materials
          )
    else :
        result = ((no_material, "<Default Material>", ""),)
    #end if
    return \
        result
#end list_object_materials

def object_selected(self, context) :
    context.area.tag_redraw()
#end object_selected

class LoadPalette(bpy.types.Operator) :
    bl_idname = "material.load_gimp_palette"
    bl_label = "Load Gimp Palette"
    # bl_context = "object"
    # bl_options = set()

    # underscores not allowed in filename/filepath property attrib names!
    # filename = bpy.props.StringProperty(subtype = "FILENAME")
    filepath = bpy.props.StringProperty(subtype = "FILE_PATH")
    scene_name = bpy.props.StringProperty(name = "New Scene Name", default = "Swatches")
    base_object = bpy.props.EnumProperty \
      (
        items = list_objects,
        name = "Swatch Object",
        description = "Object to duplicate to create swatches",
        update = object_selected
      )
    base_object_match = bpy.props.StringProperty(name = "Only Names Matching")
    base_material = bpy.props.EnumProperty \
      (
        items = list_object_materials,
        name = "Swatch Material",
        description = "Material in swatch object to show colour",
      )
    use_as_diffuse = bpy.props.BoolProperty \
      (
        name = "Use as Diffuse",
        description = "Whether to apply as material diffuse colour",
        default = True
      )
    diffuse_intensity = bpy.props.FloatProperty \
      (
        name = "Diffuse Intensity",
        description = "material diffuse intensity, only if applying as diffuse colour",
        min = 0.0,
        max = 1.0,
        default = 0.8
      )
    use_as_specular = bpy.props.BoolProperty \
      (
        name = "Use as Specular",
        description = "Whether to apply as material specular colour",
        default = False
      )
    specular_intensity = bpy.props.FloatProperty \
      (
        name = "Specular Intensity",
        description = "material specular intensity, only if applying as specular colour",
        min = 0.0,
        max = 1.0,
        default = 0.5
      )
    use_as_mirror = bpy.props.BoolProperty \
      (
        name = "Use for Mirror",
        description = "Whether to apply as material raytrace mirror colour",
        default = False
      )
    mirror_reflect = bpy.props.FloatProperty \
      (
        name = "Mirror Reflection Factor",
        description = "Reflection factor, only if applying as raytrace mirror colour",
        min = 0.0,
        max = 1.0,
        default = 0.8
      )
    use_as_sss = bpy.props.BoolProperty \
      (
        name = "Use for Subsurface Scattering",
        description = "Whether to apply as material subsurface scattering colour",
        default = False
      )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
    #end invoke

    def execute(self, context):
        try :
            import_palette(self)
            status = {"FINISHED"}
        except Failure as why :
            sys.stderr.write("Failure: %s\n" % why.msg) # debug
            self.report({"ERROR"}, why.msg)
            status = {"CANCELLED"}
        #end try
        return status
    #end execute

#end LoadPalette

class LoaderMenu(bpy.types.Menu) :
    bl_idname = "material.load_ext_materials"
    bl_label = "External Materials"

    def draw(self, context) :
        self.layout.operator(LoadPalette.bl_idname, text = "Load Palette...", icon = "COLOR")
    #end draw

#end LoaderMenu

def add_invoke_item(self, context) :
    self.layout.menu(LoaderMenu.bl_idname, icon = "MATERIAL")
      # note that trying to directly add item to self.layout instead of submenu
      # doesn't work: its execute method gets run instead of invoke.
#end add_invoke_item

def register() :
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_add.append(add_invoke_item)
#end register

def unregister() :
    bpy.types.INFO_MT_add.remove(add_invoke_item)
    bpy.utils.unregister_module(__name__)
#end unregister

if __name__ == "__main__" :
    register()
#end if
