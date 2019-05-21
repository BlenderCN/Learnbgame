#+
# This script uses Fontconfig <https://www.freedesktop.org/wiki/Software/fontconfig/>,
# the standard Linux font-matching API, to let the user load a font into a
# Blender document by specifying suitable identifying information.
#
# Copyright 2017 by Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
# Licensed under CC-BY-SA <http://creativecommons.org/licenses/by-sa/4.0/>.
#-

import sys
import os
import ctypes as ct
import bpy

fc = ct.cdll.LoadLibrary("libfontconfig.so.1")

fc.FcInit.restype = ct.c_bool
fc.FcNameParse.argtypes = (ct.c_char_p,)
fc.FcNameParse.restype = ct.c_void_p
fc.FcConfigSubstitute.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_int)
fc.FcConfigSubstitute.restype = ct.c_bool
fc.FcDefaultSubstitute.argtypes = (ct.c_void_p,)
fc.FcDefaultSubstitute.restype = None
fc.FcFontMatch.restype = ct.c_void_p
fc.FcFontMatch.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p)
fc.FcPatternDestroy.argtypes = (ct.c_void_p,)
fc.FcPatternDestroy.restype = None
fc.FcPatternGetString.restype = ct.c_uint
fc.FcPatternGetString.argtypes = (ct.c_void_p, ct.c_char_p, ct.c_int, ct.POINTER(ct.c_void_p))

class FC :
    # minimal Fontconfig interface, just sufficient for my needs.

    MatchPattern = 0
    ResultMatch = 0
    ResultNoMatch = 1
    ResultTypeMismatch = 2

#end FC

class FcPatternManager :
    # context manager which collects a list of FcPattern objects requiring disposal.

    def __init__(self) :
        self.to_dispose = []
    #end __init__

    def __enter__(self) :
        return \
            self
    #end __enter__

    def collect(self, pattern) :
        "collects another FcPattern reference to be disposed."
        # c_void_p function results are peculiar: they return integers
        # for non-null values, but None for null.
        if pattern != None :
            self.to_dispose.append(pattern)
        #end if
        return \
            pattern
    #end collect

    def __exit__(self, exception_type, exception_value, traceback) :
        for pattern in self.to_dispose :
            fc.FcPatternDestroy(pattern)
        #end for
    #end __exit__

#end FcPatternManager

bl_info = \
    {
        "name" : "Fontfinder",
        "author" : "Lawrence D'Oliveiro <ldo@geek-central.gen.nz>",
        "version" : {0, 5},
        "blender" : (2, 7, 8),
        "location" : "Properties > Font",
        "description" : "load a font by matching a pattern",
        "category" : "Object",
    }

class Failure(Exception) :

    def __init__(self, msg) :
        self.msg = msg
    #end __init__

#end Failure

class FontFinder(bpy.types.Operator) :
    bl_idname = "font.finder"
    bl_label = "Font Finder"
    bl_context = "objectmode"
      # could also allow "curve_edit"? Or whatever it is with edit mode on a font object?
      # valid values can be found in source/blender/blenkernel/intern/context.c

    def invoke(self, context, event) :
        try :
            fontspec = context.scene.find_font_spec
            with FcPatternManager() as patterns :
                search_pattern = patterns.collect(fc.FcNameParse(fontspec.encode("utf-8")))
                if search_pattern == None :
                    raise Failure("cannot parse FontConfig name pattern")
                #end if
                if not fc.FcConfigSubstitute(None, search_pattern, FC.MatchPattern) :
                    raise Failure("cannot substitute Fontconfig configuration")
                #end if
                fc.FcDefaultSubstitute(search_pattern)
                match_result = ct.c_int()
                found_pattern = patterns.collect(fc.FcFontMatch(None, search_pattern, ct.byref(match_result)))
                if found_pattern == None or match_result.value != FC.ResultMatch :
                    raise Failure("Fontconfig cannot match font name")
                #end if
                strptr = ct.c_void_p()
                status = fc.FcPatternGetString(found_pattern, b"file", 0, ct.byref(strptr))
                if status == FC.ResultTypeMismatch :
                    raise Failure("Fontconfig value is not of expected type")
                elif status != FC.ResultMatch :
                    raise Failure("Fontconfig pattern has no filename property")
                #end if
                filepath = ct.cast(strptr, ct.c_char_p).value.decode()
            #end with
            bpy.data.fonts.load(filepath = filepath)
            msg = "%s => %s" % (fontspec, filepath)
            sys.stderr.write("Font Finder: %s\n" % msg) # debug
            self.report({"INFO"}, msg)
            status = {"FINISHED"}
        except Failure as why :
            self.report({"ERROR"}, why.msg)
            status = {"CANCELLED"}
        #end try
        return \
            status
    #end invoke

#end FontFinder

def add_my_panel(self, context) :
    the_col = self.layout.column(align = True)
    the_col.separator()
    the_col.prop(context.scene, "find_font_spec", text = "Find Font")
    the_col.separator()
    the_col.operator(FontFinder.bl_idname, "Find & Load")
#end add_my_panel

def register() :
    if not fc.FcInit() :
        raise RuntimeError("failed to initialize Fontconfig.")
    #end if
    bpy.types.Scene.find_font_spec = bpy.props.StringProperty \
      (
        name = "Font Spec",
        description = "find fonts matching this Fontconfig pattern"
      )
    bpy.utils.register_class(FontFinder)
    bpy.types.DATA_PT_font.append(add_my_panel)
#end register

def unregister() :
    bpy.types.DATA_PT_font.remove(add_my_panel)
    bpy.utils.unregister_class(FontFinder)
    delattr(bpy.types.Scene, "find_font_spec")
#end unregister

if __name__ == "__main__" :
    register()
#end if
