import bpy

class GREASEPENCIL_OT_trace(bpy.types.Operator):
    bl_label = "Trace"
    bl_idname = "grease_writer.trace"
    bl_description = "Trace the strokes with a given object to the X Y & Z coords of the drawing"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        obj = bpy.context.view_layer.objects.active
        gpencil = obj.data
        if (len(gpencil.layers) > 0 and
            len(gpencil.layers[0].frames) > 0 and
            gpencil.tracer_obj != ''):
                return True
        else:
            return False

    def execute(self, context):
        obj = bpy.context.view_layer.objects.active
        gpencil = obj.data
        layer = gpencil.layers[0]

        tracer = bpy.data.objects[gpencil.tracer_obj]

        for i in range(len(layer.frames)):
            frame = layer.frames[i]
            if i == 1:
                vertex = frame.strokes[-1].points[0]
                tracer.location[0] = vertex.co.x + obj.location[0]
                tracer.location[1] = vertex.co.y + obj.location[1]
                tracer.keyframe_insert(data_path="location", index=0, frame=frame.frame_number - 1)
                tracer.keyframe_insert(data_path="location", index=1, frame=frame.frame_number - 1)

                if not gpencil.trace2d:
                    tracer.location[2] = vertex.co.z + obj.location[2]
                    tracer.keyframe_insert(data_path="location", index=2, frame=frame.frame_number - 1)

            if (len(frame.strokes) > 0):
                vertex = frame.strokes[-1].points[-1]
                tracer.location[0] = vertex.co.x + obj.location[0]
                tracer.location[1] = vertex.co.y + obj.location[1]
                tracer.keyframe_insert(data_path="location", index=0, frame=frame.frame_number - 1)
                tracer.keyframe_insert(data_path="location", index=1, frame=frame.frame_number - 1)

                if not gpencil.trace2d:
                    tracer.location[2] = vertex.co.z + obj.location[2]
                    tracer.keyframe_insert(data_path="location", index=2, frame=frame.frame_number - 1)

        return {"FINISHED"}

