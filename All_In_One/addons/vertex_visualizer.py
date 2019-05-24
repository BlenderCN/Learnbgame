#+
# This Blender addon displays information about a mesh that
# can be useful in debugging mesh-construction code, namely
# the indexes of the vertices and attached edges and faces.
#
# Copyright 2017 by Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
# Licensed under CC-BY-SA <http://creativecommons.org/licenses/by-sa/4.0/>.
#-

import sys # debug
import types
import bpy
import bmesh
import mathutils
import bgl
import blf
from bpy_extras import \
    view3d_utils

bl_info = \
    {
        "name" : "Vertex Visualizer",
        "author" : "Lawrence D'Oliveiro <ldo@geek-central.gen.nz>",
        "version" : (0, 5),
        "blender" : (2, 7, 8),
        "location" : "View 3D > Properties Shelf",
        "description" :
            "Shows information about a mesh that can be useful in"
            " debugging mesh-construction code, namely the indexes"
            " of the vertices and attached edges and faces.",
        "warning" : "",
        "wiki_url" : "",
        "tracker_url" : "",
        "category": "Learnbgame",
    }

#+
# Useful stuff
#-

def gen_gl() :
    # Funny thing: the OpenGL specs document all routines and
    # constants *without* “gl” and “GL_” prefixes. It makes
    # sense to add these in a language that does not have
    # namespaces, like C. In Python, it does not. So this
    # routine takes apart the contents of the bgl module
    # into two separate modules, one (called “gl”) containing
    # all the routines and the other (called “GL”) containing
    # all the constants, with those unnecessary prefixes
    # stripped. So instead  of calling bgl.glClear(), say,
    # you can call gl.Clear(). And instead of referring to
    # bgl.GL_ACCUM, you can use GL.ACCUM instead.
    # Much more concise all round.
    gl = types.ModuleType("gl", doc = "OpenGL routines")
    GL = types.ModuleType("GL", doc = "OpenGL constants")
    glu = types.ModuleType("glu", doc = "OpenGL routines")
    for name in dir(bgl) :
        if name.startswith("glu") :
            setattr(glu, name[3:], getattr(bgl, name))
        elif name.startswith("gl") :
            setattr(gl, name[2:], getattr(bgl, name))
        elif name.startswith("GL_") :
            setattr(GL, name[3:], getattr(bgl, name))
        else :
            sys.stderr.write("ignoring bgl.%s\n" % name) # debug
        #end if
    #end for
    return \
        gl, GL, glu
#end gen_gl
gl, GL, glu = gen_gl()
del gen_gl # your work is done

#+
# The panel
#-

def draw_vertex_info(context) :

    font_id = 0
    dpi = 72

    region = context.region
    view3d = context.space_data.region_3d
    obj = context.object
    pos_2d = lambda v : \
        view3d_utils.location_3d_to_region_2d(region, view3d, obj.matrix_world * v)
    xform = view3d.perspective_matrix
    xlate = xform.translation

    def face_visible(face) :
        # face is a BMFace; checks if it is oriented toward the camera.
        # fixme: not quite right for perspective view, OK for orthographic view.
        orient = xform * face.normal - xlate
        #sys.stderr.write("face %d normal %s transforms to %s\n" % (face.index, face.normal, orient)) # debug
        return \
            orient.z < 0
    #end face_visible

    def draw_label(coords, text) :
        pos = pos_2d(coords)
        blf.position(font_id, pos.x, pos.y, 0)
        blf.draw(font_id, text)
    #end draw_label

#begin draw_vertex_info
    meshb = None # to begin with
    if (
            (
                context.window_manager.vertex_vis_show_faces
            or
                context.window_manager.vertex_vis_show_edges
            or
                context.window_manager.vertex_vis_show_verts
            )
        and
            context.area.type == "VIEW_3D"
        and
            obj != None
        and
            type(obj.data) == bpy.types.Mesh
    ) :
        mesh = obj.data
        if context.mode == "EDIT_MESH" :
            meshb = bmesh.from_edit_mesh(mesh)
        elif context.mode == "OBJECT" :
            meshb = bmesh.new()
            meshb.from_mesh(mesh)
        #end if
    #end if
    if meshb != None :
        show_unselected = not context.window_manager.vertex_vis_selected_only
        gl.Enable(GL.BLEND)
        blf.size(font_id, 12, dpi)
        label_colours = \
            {
                "face" : (0.66, 0.75, 0.37, 1),
                "edge" : (0.25, 0.63, 0.75, 1),
                "vert" : (0.56, 0.75, 0.56, 1),
            }
        meshb.faces.index_update()
        meshb.edges.index_update()
        meshb.verts.index_update()
          # do I need these?
        meshb.faces.ensure_lookup_table()
        meshb.edges.ensure_lookup_table()
        meshb.verts.ensure_lookup_table()
          # seems I need these
        if context.window_manager.vertex_vis_show_faces :
            gl.Color4f(*label_colours["face"])
            for f in meshb.faces :
                if (
                        (show_unselected or f.select)
                    and
                        (context.window_manager.vertex_vis_show_backface or face_visible(f))
                ) :
                    draw_label(f.calc_center_median(), "f%d" % f.index)
                #end if
            #end for
        #end if
        if context.window_manager.vertex_vis_show_edges :
            if not context.window_manager.vertex_vis_show_backface :
                edge_faces = {}
                for f in meshb.faces :
                    for e in f.edges :
                        e = e.index
                        if e not in edge_faces :
                            edge_faces[e] = set()
                        #end if
                        edge_faces[e].add(f.index)
                    #end for
                #end for
            else :
                edge_faces = None
            #end if
            gl.Color4f(*label_colours["edge"])
            for e in meshb.edges :
                if (
                        (show_unselected or e.select)
                    and
                        (
                            context.window_manager.vertex_vis_show_backface
                        or
                                e.index in edge_faces
                            and
                                any(face_visible(meshb.faces[f]) for f in edge_faces[e.index])
                        )
                ) :
                    draw_label \
                      (
                            (meshb.verts[e.verts[0].index].co + meshb.verts[e.verts[1].index].co)
                        /
                            2,
                        "e%d" % e.index
                      )
                #end if
            #end for
        #end if
        if context.window_manager.vertex_vis_show_verts :
            if not context.window_manager.vertex_vis_show_backface :
                vert_faces = {}
                for f in meshb.faces :
                    for v in f.verts :
                        v = v.index
                        if v not in vert_faces :
                            vert_faces[v] = set()
                        #end if
                        vert_faces[v].add(f.index)
                    #end for
                #end for
            else :
                vert_faces = None
            #end if
            gl.Color4f(*label_colours["vert"])
            for v in meshb.verts :
                if (
                        (show_unselected or v.select)
                    and
                        (
                            context.window_manager.vertex_vis_show_backface
                        or
                                v.index in vert_faces
                            and
                                any(face_visible(meshb.faces[f]) for f in vert_faces[v.index])
                        )
                ) :
                    draw_label(v.co, "v%d" % v.index)
                #end if
            #end for
        #end if
        gl.Disable(GL.BLEND)
        gl.Color4f(0, 0, 0, 1)
    #end if
#end draw_vertex_info

def add_props(self, context) :
    the_col = self.layout.column(align = True) # gives a nicer grouping of my items
    the_col.label("Vertex Visualizer:")
    for propsuffix in ("verts", "edges", "faces", "backface") :
        the_col.prop \
          (
            context.window_manager,
            "vertex_vis_show_%s" % propsuffix,
            "Show %s" % propsuffix.title()
          )
    #end for
    the_col.prop \
      (
        context.window_manager,
        "vertex_vis_selected_only",
        "Selected Only"
      )
    if (
            not hasattr(bpy.types.WindowManager, "_vertex_vis_draw_handler")
        or
            bpy.types.WindowManager._vertex_vis_draw_handler == None
    ) :
        bpy.types.WindowManager._vertex_vis_draw_handler = bpy.types.SpaceView3D.draw_handler_add \
          (
            draw_vertex_info, # func
            (context,), # args
            "WINDOW", # region type
            "POST_PIXEL" # event type
          )
        #context.area.tag_redraw() # unneeded
    #end if
#end add_props

def register():
    for propsuffix in ("verts", "edges", "faces", "backface") :
        propname = "vertex_vis_show_%s" % propsuffix
        setattr \
          (
            bpy.types.WindowManager,
            propname,
            bpy.props.BoolProperty(name = propname, default = False)
          )
    #end for
    bpy.types.WindowManager.vertex_vis_selected_only = bpy.props.BoolProperty \
      (
        name = "vertex_vis_selected_only",
        default = False
      )
    bpy.types.VIEW3D_PT_view3d_display.append(add_props)
#end register

def unregister() :
    bpy.types.VIEW3D_PT_view3d_display.remove(add_props)
    if hasattr(bpy.types.WindowManager, "_vertex_vis_draw_handler") :
        if bpy.types.WindowManager._vertex_vis_draw_handler != None :
            bpy.types.SpaceView3D.draw_handler_remove \
              (
                bpy.types.WindowManager._vertex_vis_draw_handler,
                "WINDOW" # region type
              )
        #end if
        del bpy.types.WindowManager._vertex_vis_draw_handler
    #end if
    for propsuffix in ("verts", "edges", "faces", "backface") :
        try :
            delattr(bpy.types.WindowManager, "vertex_vis_show_%s" % propsuffix)
        except AttributeError :
            pass
        #end try
    #end for
#end unregister

if __name__ == "__main__" :
    register()
#end if
