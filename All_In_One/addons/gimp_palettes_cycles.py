#+
# This add-on script for Blender 2.7 loads a set of colours from a Gimp .gpl
# file and creates a set of simple Cycles materials that use them, assigned to
# swatch objects created in a separate scene in the current document. From there
# they may be browsed and reused in other objects as needed.
#
# Copyright 2012-2016 Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
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
        "name" : "Gimp Palettes (Cycles version)",
        "author" : "Lawrence D'Oliveiro <ldo@geek-central.gen.nz>",
        "version" : (0, 4, 0),
        "blender" : (2, 7, 7),
        "location" : "View3D > Add > External Materials > Load Palette...",
        "description" :
            "loads colours from a Gimp .gpl file into a set of swatch objects",
        "warning" : "",
        "wiki_url" : "",
        "tracker_url" : "",
        "category" : "Object",
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
    the_scene.render.engine = "CYCLES"
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
    # Create material with a node group containing a single diffuse shader
    # and an input RGB colour. That way colour can be varied across
    # each swatch, while contents of common node group can be easily changed by user
    # into something more elaborate.
    common_group = bpy.data.node_groups.new("palette material common", "ShaderNodeTree")
    group_inputs = common_group.nodes.new("NodeGroupInput")
    group_inputs.location = (-300, 0)
    common_group.inputs.new("NodeSocketColor", "Colour")
    shader = common_group.nodes.new("ShaderNodeBsdfDiffuse")
    shader.location = (0, 0)
    common_group.links.new(group_inputs.outputs[0], shader.inputs[0])
    # group will contain material output directly
    material_output = common_group.nodes.new("ShaderNodeOutputMaterial")
    material_output.location = (300, 0)
    common_group.links.new(shader.outputs[0], material_output.inputs[0])
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
        the_material = bpy.data.materials.new(material_name)
          # TODO: option to reuse existing material?
        the_material.use_nodes = True
        material_tree = the_material.node_tree
        for node in list(material_tree.nodes) :
          # clear out default nodes
            material_tree.nodes.remove(node)
        #end for
        the_material.diffuse_color = colour[0] # used in viewport
        group_node = material_tree.nodes.new("ShaderNodeGroup")
        group_node.node_tree = common_group
        group_node.location = (0, 0)
        in_colour = material_tree.nodes.new("ShaderNodeRGB")
        in_colour.location = (-300, 0)
        in_colour.outputs[0].default_value = colour[0] + (1,)
        material_tree.links.new(in_colour.outputs[0], group_node.inputs[0])
        if swatch_material != None :
            # replace existing material slot
            for i in range(0, len(swatch.data.materials)) :
                if swatch.data.materials[i] == swatch_material :
                    swatch.data.materials[i] = the_material
                #end if
            #end for
        else :
            swatch.data.materials.append(the_material)
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
        description = "Material in swatch object to replace with colour",
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
