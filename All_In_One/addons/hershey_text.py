#+
# This addon for Blender 2.7 uses the Hershey fonts to turn a text
# object into a collection of curves. Also needs HersheyPy
# <https://github.com/ldo/hersheypy> to be installed.
#
# Copyright 2015, 2017 Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
# Licensed under CC-BY-SA <http://creativecommons.org/licenses/by-sa/4.0/>.
#-

import math
import sys # debug
import os
import bpy
import mathutils
import hershey_font

bl_info = \
    {
        "name" : "Hershey Text",
        "author" : "Lawrence D'Oliveiro <ldo@geek-central.gen.nz>",
        "version" : (0, 5, 0),
        "blender" : (2, 7, 8),
        "location" : "View 3D > Object Mode > Tool Shelf",
        "description" :
            "Uses a Hershey font to turn a text object into a collection of curves.",
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

def list_hershey_fonts() :
    result = [(" ", "(pick a font)", "")]
    for item in hershey_font.each_name() :
        result.append \
          (
            (item, item, "")
          )
    #end for
    return \
        sorted(result, key = lambda i : i[0])
#end list_hershey_fonts

class HersheyText(bpy.types.Operator) :
    bl_idname = "text.hersheyfy"
    bl_label = "Hershey Text"
    bl_context = "objectmode"
    bl_options = {"REGISTER", "UNDO"}

    font_name = bpy.props.EnumProperty \
      (
        name = "Hershey Font",
        description = "name of Hershey font to use",
        items = list_hershey_fonts(),
      )
    curve_type = bpy.props.EnumProperty \
      (
        name = "Curve Type",
        description = "type of curves to create",
        items =
            (
                ("POLY", "Poly", ""),
                ("BEZIER", "Bézier", ""),
                # others seem to produce empty curves, disable for now
                #("BSPLINE", "B-Spline", ""),
                #("CARDINAL", "Cardinal", ""),
                #("NURBS", "NURBS", ""),
            ),
        default = "BEZIER",
      )
    sharp_angle = bpy.props.FloatProperty \
      (
        name = "Sharp Angle",
        description = "Bézier curve angles below this become corners",
        subtype = "ANGLE",
        default = math.pi / 2,
      )
    delete_text = bpy.props.BoolProperty \
      (
        name = "Delete Original Text",
        description = "delete the original text object",
        default = False
      )

    @classmethod
    def poll(celf, context) :
        active_object = context.scene.objects.active
        return \
            (
                context.mode == "OBJECT"
            and
                active_object != None
            #and
            #    active_object.select
            and
                active_object.type in ("FONT", "CURVE")
            )
    #end poll

    def draw(self, context) :
        the_col = self.layout.column(align = True)
        the_col.label("Hershey Font:")
        the_col.prop(self, "font_name")
        the_col.prop(self, "curve_type")
        the_col.prop(self, "sharp_angle")
        the_col.prop(self, "delete_text")
    #end draw

    def action_common(self, context, redoing) :
        try :
            if not redoing :
                text_object = context.scene.objects.active
                if text_object == None or not text_object.select :
                    raise Failure("no selected object")
                #end if
                if text_object.type != "FONT" or type(text_object.data) != bpy.types.TextCurve :
                    raise Failure("need to operate on a font object")
                #end if
                # save the name of the object so I can find it again
                # when I'm reexecuted. Can't save a direct reference,
                # as that is likely to become invalid. Blender guarantees
                # the name is unique anyway.
                self.orig_object_name = text_object.name
            else :
                text_object = context.scene.objects[self.orig_object_name]
                assert text_object.type == "FONT" and type(text_object.data) == bpy.types.TextCurve
            #end if
            if self.font_name != " " :
                the_font = hershey_font.HersheyGlyphs.load(self.font_name)
            else :
                the_font = None
            #end if
            curve_name = text_object.name + " hersh"
            curve_data = bpy.data.curves.new(curve_name, "CURVE")
            if the_font != None :
                scaling = \
                    (
                        mathutils.Matrix.Scale
                          (
                            -1, # factor
                            4, # size
                            mathutils.Vector((0, 1, 0)), # axis
                          ) # flip Y-axis
                    *
                        mathutils.Matrix.Scale
                          (
                            the_font.scale, # factor
                            4 # size
                          )
                    )
                text_data = text_object.data
                # TODO: text boxes, character formats
                pos = mathutils.Vector((0, 0, 0))
                for ch in text_data.body :
                    if the_font.encoding != None :
                        glyph_nr = the_font.encoding.get(ord(ch))
                    else :
                        glyph_nr = ord(ch)
                    #end if
                    if glyph_nr != None :
                        the_glyph = the_font.glyphs.get(glyph_nr)
                    else :
                        the_glyph = None
                    #end if
                    # note each new curve Spline already seems to have one point to begin with
                    if the_glyph != None :
                        glyph_width = the_glyph.max_x - the_glyph.min_x
                        for pathseg in the_glyph.path :
                            curve_spline = curve_data.splines.new(self.curve_type)
                            is_bezier = self.curve_type == "BEZIER"
                            points = (curve_spline.points, curve_spline.bezier_points)[is_bezier]
                            for i, point in enumerate(pathseg) :
                                if i != 0 :
                                    points.add()
                                #end if
                                points[i].co = \
                                    (
                                        mathutils.Matrix.Scale
                                          (
                                            text_data.size, # factor
                                            4, # size
                                          )
                                    *
                                        mathutils.Matrix.Shear
                                          (
                                            "XZ" , # plane
                                            4, # size
                                            [text_data.shear, 0], # factor
                                          )
                                    *
                                        mathutils.Matrix.Translation(pos)
                                    *
                                        scaling
                                    *
                                        mathutils.Vector((point.x, point.y - the_font.baseline_y, 0))
                                    ).resized((4, 3)[is_bezier])
                            #end for
                            if is_bezier :
                                sharp_angle = self.sharp_angle
                                for i in range(len(pathseg)) :
                                    try :
                                        angle = \
                                            (
                                                (points[(i + 1) % len(pathseg)].co - points[i].co)
                                            .angle
                                                (points[i].co - points[(i - 1) % len(pathseg)].co)
                                            )
                                    except ValueError :
                                        # assume zero-length vector somewhere
                                        angle = 0
                                    #end if
                                    angle = math.pi - angle
                                    if angle < sharp_angle :
                                        # make it a corner
                                        points[i].handle_left_type = "FREE"
                                        points[i].handle_right_type = "FREE"
                                        points[i].handle_left = points[i].co
                                        points[i].handle_right = points[i].co
                                    else :
                                        # make it curve
                                        points[i].handle_left_type = "AUTO"
                                        points[i].handle_right_type = "AUTO"
                                    #end if
                                #end for
                            #end if
                        #end for
                    else :
                        glyph_width = the_font.max.x - the_font.min.x
                        curve_spline = curve_data.splines.new("POLY")
                        curve_spline.points.add(3)
                        for i, corner_x, corner_y in \
                            (
                                (0, the_font.min.x, the_font.min.y),
                                (1, the_font.max.x, the_font.min.y),
                                (2, the_font.max.x, the_font.max.y),
                                (3, the_font.min.x, the_font.max.y),
                            ) \
                        :
                            curve_spline.points[i].co = \
                                (
                                    mathutils.Matrix.Translation(pos)
                                *
                                    scaling
                                *
                                    mathutils.Vector((corner_x, corner_y - the_font.baseline_y, 0))
                                ).resized(4)
                        #end for
                        curve_spline.use_cyclic_u = True
                    #end if
                    pos += mathutils.Vector((glyph_width * the_font.scale, 0, 0))
                #end for
            #end if
            curve_obj = bpy.data.objects.new(curve_name, curve_data)
            context.scene.objects.link(curve_obj)
            curve_obj.matrix_local = text_object.matrix_local
            bpy.ops.object.select_all(action = "DESELECT")
            bpy.data.objects[curve_name].select = True
            context.scene.objects.active = curve_obj
            if self.delete_text :
                context.scene.objects.unlink(text_object)
                bpy.data.objects.remove(text_object)
            #end if
            # all done
            status = {"FINISHED"}
        except Failure as why :
            sys.stderr.write("Failure: {}\n".format(why.msg)) # debug
            self.report({"ERROR"}, why.msg)
            status = {"CANCELLED"}
        #end try
        return \
            status
    #end action_common

    def execute(self, context) :
        return \
            self.action_common(context, True)
    #end execute

    def invoke(self, context, event) :
        return \
            self.action_common(context, False)
    #end invoke

#end HersheyText

def add_invoke_button(self, context) :
    if HersheyText.poll(context) :
        the_col = self.layout.column(align = True) # gives a nicer grouping of my items
        the_col.label("Hersheyfy:")
        the_col.operator(HersheyText.bl_idname, text = "Do It")
    #end if
#end add_invoke_button

def register() :
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_PT_tools_object.append(add_invoke_button)
#end register

def unregister() :
    bpy.utils.unregister_module(__name__)
    bpy.types.VIEW3D_PT_tools_object.remove(add_invoke_button)
#end unregister

if __name__ == "__main__" :
    register()
#end if
