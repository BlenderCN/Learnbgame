import bpy
from .operatorShared import SharedOperatorBase
from .shared import COLOUR_MAP, getOrCreateProp

class GenerateCPU(bpy.types.Operator, SharedOperatorBase):
    bl_idname = "mesh.stfu_generate_cpu"
    bl_label = "Random Planet (CPU)"
    bl_options = {"REGISTER", "UNDO"}

    def processHeightmap(self, context, hm):
        mat = getOrCreateProp(bpy.data.materials, "__ Terrain Vertex Colouring")
        mat.use_vertex_color_paint = True
        mat.emit = .2
        if not mat.name in context.object.data.materials:
            context.object.data.materials.append(mat)
        
        # scale verts according to height value
        for vdata in context.object.data.vertices:
            vdata.co.length = 1 + hm(vdata.co)
        
        # assign colors - vertices need to be colored in every face separately
        colors = getOrCreateProp(context.object.data.vertex_colors, "__ Terrain Colours")
        colors.active = True
        colors.active_render = True
        for poly in context.object.data.polygons:
            for vid, vlid in zip(poly.vertices, poly.loop_indices):
                vdata = context.object.data.vertices[vid]
                height = vdata.co.length - 1 # assuming unit sphere
                colors.data[vlid].color = getColor(height)
        
        # water shouldn't have dips, so we remove those
        if self.fillOceans:
            for vdata in context.object.data.vertices:
                if vdata.co.length < 1:
                    vdata.co.normalize()

#############################################

def getColor(height):
    for href, col in COLOR_MAP:
        if height < href:
            return col
    return COLOR_MAP[-1][1]