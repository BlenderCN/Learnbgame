import bpy, bmesh
from .primitives import *
from .bmesh_draw import draw_bm
from mathutils import Vector, Matrix


def draw_display_view(self):
    settings = bpy.context.window_manager.display_settings
    if not settings.enabled:
        return
    if not settings.show_gl:
        return

    glEnable(GL_BLEND)
    glShadeModel(GL_FLAT)

    #POINTS
    if self.points and settings.show_gl_points:
        draw_verts(self.points.values(), color=settings.color_points)

    #EDGES
    if self.edges and settings.show_gl_edges:
        for k,v in self.edges.items():
            draw_edge(*v, color=settings.color_edges)

    #POINT CHAINS
    if self.point_chains and settings.show_gl_point_chains:
        for k,v in self.point_chains.items():
            if v:
                draw_point_chain(v, color=settings.color_point_chains)

    #PLOTS
    #are drawn in pixel (2D)
                
    #MATRIZIES
    if settings.show_gl_mats:
        if not self.object_transform == Matrix():
            draw_matrix(self.object_transform)

        if self.matrizies:
            for k,v in self.mats.items():
                draw_matrix(v)

    #EULERS
    if self.eulers and settings.show_gl_eulers:
        for k, eul in self.eulers.items():
            mat = eul.to_matrix().to_4x4()
            mat.translation = self.object_transform.translation
            draw_matrix(mat)

    #QUATERNIONS
    if self.quats and settings.show_gl_quats:
        for k, quat in self.quats.items():
            mat = quat.to_matrix().to_4x4()
            mat.translation = self.object_transform.translation
            draw_matrix(mat)

    #BMESH
    if self.bmeshs and settings.show_gl_bm:
        for bm in self.bmeshs.values():
            draw_bm(bm)

