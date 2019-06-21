import bpy
from .utils import process_stroke_verts_linearly


class GREASEPENCIL_OT_stippleit(bpy.types.Operator):
    bl_label = "Stipple It"
    bl_idname = "grease_writer.stippleit"
    bl_description = "Stipples the strokes of the Grease pencil layer"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        obj = bpy.context.view_layer.objects.active
        gpencil = obj.data
        if len(gpencil.layers) > 0:
                return True
        else:
            return False

    def execute(self, context):
        scene = context.scene
        obj = bpy.context.view_layer.objects.active
        gpencil = obj.data

        stipple_length = gpencil.stipple_length

        thicknesses = []
        layer = gpencil.layers[0]
        frame = layer.frames[-1]
        glyph_strokes = []
        for stroke in frame.strokes:
            verts = []
            thicknesses.append(stroke.line_width)
            for point in stroke.points:
                verts.append([point.co.x, point.co.y, point.co.z])
            glyph_strokes.append(verts)

        layer.clear()

        stippled_strokes = []
        remaining = 0
        x = 0
        stipple_skip = gpencil.stipple_skip + 1
        for i in range(len(glyph_strokes)):
            stroke_verts = glyph_strokes[i]
            framed_strokes, remaining = process_stroke_verts_linearly(stroke_verts, stipple_length, remaining=remaining, stipple=True)

            if x % stipple_skip > 0:
                x %= stipple_skip
            else:
                x = 0
            while x < len(framed_strokes):
                if x % stipple_skip == 0:
                    stippled_strokes.append(framed_strokes[x])
                x += 1

        frame = layer.frames.new(0)
        for stroke_verts in stippled_strokes:
            stroke = frame.strokes.new()
            stroke.line_width = thicknesses[i]
            stroke.display_mode = '3DSPACE'

            for vert in stroke_verts:
                stroke.points.add(1)
                stroke.points[-1].co.x = vert[0]
                stroke.points[-1].co.y = vert[1]
                stroke.points[-1].co.z = vert[2]


        return {"FINISHED"}
