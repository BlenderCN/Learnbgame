import bpy
from .primitives import draw_text
from mathutils import Matrix

def draw_display_px(self):
    settings = bpy.context.window_manager.display_settings
    if not settings.enabled:
        return

    #PLOTS
    if self.plots and settings.show_gl_plots:
        for plot in self.plots.values():
            plot.draw()


    ### NAMES
    if not settings.show_text:
        return

    #POINTS
    if self.points and settings.show_text_points:
        for k,v in self.points.items():
            if v:
                draw_text(str(k),v)

    #EDGES
    if self.edges and settings.show_text_edges:
        for k,v in self.edges.items():
            if v:
                draw_text(str(k), (v[0]+v[1])/2)

    #POINT CHAINS
    if self.point_chains and settings.show_text_point_chains:
        for k, v in self.point_chains.items():
            if v:
                draw_text(str(k), (v[0] + v[1]) / 2)

    #MATRIZIES
    if settings.show_text_mats:
        if not self.object_transform == Matrix():
            draw_text('Display Transform', self.object_transform.translation)

        if self.matrizies:
            for k,v in self.matrizies.items():
                draw_text(str(k), v.translation)

    #EULERS
    if settings.show_text_eulers:
        if self.eulers:
            for k in self.eulers.keys():
                draw_text(str(k), self.object_transform.translation)

    #QUATERNIONS
    if settings.show_text_quats:
        if self.quats:
            for k in self.eulers.keys():
                draw_text(str(k), self.object_transform.translation)

    #BMESHS
    if settings.show_text_bm:
        if self.bmeshs:
            for k, bm in self.bmeshs.items():
                #vert indizies
                if len(bm.verts) > 0 and settings.show_text_bm_verts:
                    for v in bm.verts:
                        draw_text(str(v.index), v.co)

                #edge indizies
                if len(bm.edges) > 0 and settings.show_text_bm_edges:
                    for e in bm.edges:
                        draw_text(str(e.index), (e.verts[0].co+e.verts[1].co)/2)


                if len(bm.faces) > 0 and settings.show_text_bm_faces:
                    for f in bm.faces:
                        draw_text(str(f.index), f.calc_center_median())

