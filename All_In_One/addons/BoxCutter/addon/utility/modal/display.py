import bpy
from .. import modifier


# TODO: move shape display here
class shape:


    def boolean(ot, display=False):
        bc = bpy.context.window_manager.bc
        show = ot.live if not display else display

        if bc.shape.dimensions[2] > 0.001:
            for obj in ot.datablock['targets']:
                if ot.mode == 'INSET':
                    for mod in reversed(obj.modifiers):
                        if mod.type == 'BOOLEAN' and mod.object.bc.inset:
                            mod.show_viewport = show
                            break

                if modifier.shape_bool(ot, obj):
                    modifier.shape_bool(ot, obj).show_viewport = show if ot.mode != 'INSET' else False

            for obj in ot.datablock['slices']:
                if modifier.shape_bool(ot, obj):
                    modifier.shape_bool(ot, obj).show_viewport = show

        else:
            for obj in ot.datablock['targets']:
                if ot.mode == 'INSET':
                    for mod in reversed(obj.modifiers):
                        if mod.type == 'BOOLEAN' and mod.object.bc.inset:
                            mod.show_viewport = False
                            break

                if modifier.shape_bool(ot, obj):
                    modifier.shape_bool(ot, obj).show_viewport = False

            for obj in ot.datablock['slices']:
                if modifier.shape_bool(ot, obj):
                    modifier.shape_bool(ot, obj).show_viewport = False
