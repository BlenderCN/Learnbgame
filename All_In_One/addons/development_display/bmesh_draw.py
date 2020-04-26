import bpy, bmesh
from .primitives import *

def draw_bm(bm):
    if not isinstance(bm, bmesh.types.BMesh):
        print('Not a bmesh type', str(bm))
        return
    
    settings = bpy.context.window_manager.display_settings

    if settings.show_gl_bm_faces:
        for face in bm.faces:
            draw_face([v.co for v in face.verts], color=settings.color_faces)

    edges = [[e.verts[0].co, e.verts[1].co] for e in bm.edges]
    for e in edges:
        draw_edge(*e, color=settings.color_edges)

    draw_verts([v.co for v in bm.verts], color=settings.color_points)
