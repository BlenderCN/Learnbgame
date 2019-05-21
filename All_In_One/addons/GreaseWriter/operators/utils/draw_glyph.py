import bpy
from .process_stroke_verts_linearly import process_stroke_verts_linearly

def draw_glyph(obj, glyph_strokes, thicknesses=None):
    scene = bpy.context.scene
    gpencil = obj.data
    speed = scene.gw_speed / 10
    thickness = scene.gw_thickness

    if len(gpencil.layers) > 0:
            layer = gpencil.layers[0]
            layer.clear()
    else:
        layer = gpencil.layers.new('strokes', set_active=True)

    frame = layer.frames.new(bpy.context.scene.frame_current)

    bpy.context.scene.frame_current += 1

    mat_index = None
    remaining = 0
    for i in range(len(glyph_strokes)):
        stroke_verts = glyph_strokes[i]
        framed_strokes, remaining = process_stroke_verts_linearly(stroke_verts, speed, remaining=remaining)

        # Give extra frames between strokes
        if i > 0:
            last_vert = glyph_strokes[i - 1][-1]
            new_vert = glyph_strokes[i][0]
            count = len(process_stroke_verts_linearly([last_vert, new_vert], speed)) - 1
            bpy.context.scene.frame_current += count

        stopper = 0
        if i == len(glyph_strokes) - 1:
            stopper = 1

        for x in range(len(framed_strokes) - stopper):
            frame = layer.frames.new(bpy.context.scene.frame_current)

            for y in range(i):
                stroke = frame.strokes.new()
                if thicknesses == None:
                    stroke.line_width = thickness
                else:
                    stroke.line_width = thicknesses[i]
                stroke.display_mode = '3DSPACE'

                for vert in glyph_strokes[y]:
                    stroke.points.add(1)
                    stroke.points[-1].co.x = vert[0]
                    stroke.points[-1].co.y = vert[1]
                    stroke.points[-1].co.z = vert[2]

            stroke = frame.strokes.new()
            if thicknesses == None:
                stroke.line_width = thickness
            else:
                stroke.line_width = thicknesses[i]
            stroke.display_mode = '3DSPACE'

            for vert in framed_strokes[x]:
                stroke.points.add(1)
                stroke.points[-1].co.x = vert[0]
                stroke.points[-1].co.y = vert[1]
                stroke.points[-1].co.z = vert[2]

            bpy.context.scene.frame_current += 1

    frame = layer.frames.new(bpy.context.scene.frame_current)
    for i in range(len(glyph_strokes)):
        stroke_verts = glyph_strokes[i]
        stroke = frame.strokes.new()
        if thicknesses == None:
            stroke.line_width = thickness
        else:
            stroke.line_width = thicknesses[i]
        stroke.display_mode = '3DSPACE'

        for vert in stroke_verts:
            stroke.points.add(1)
            stroke.points[-1].co.x = vert[0]
            stroke.points[-1].co.y = vert[1]
            stroke.points[-1].co.z = vert[2]

