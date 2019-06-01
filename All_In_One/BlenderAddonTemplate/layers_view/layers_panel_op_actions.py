"""
    This file contains all actions which the operators defined in layers_panel perform outside the UI
"""
import bpy
from materials_mgr.material_mgr import MaterialMgr

class LayersPanelOpActions:
    def __init__(self, context, report):
        self.context = context
        self.report = report

    def print_all(self):
        #scn = self.context.scene
        #for i in scn.custom:
        #    print(i.name, i.id)
        print("PRINT ALL8")
        MaterialMgr.create_new_material_for_active_obj("TheName2")
        return {'FINISHED'}

    def selectAllItems(self):
        scn = self.context.scene
        bpy.ops.object.select_all(action='DESELECT')
        obj = bpy.data.objects[scn.custom[scn.custom_index].name]
        obj.select = True

        return {'FINISHED'}

    def clearAllItems(self):
        scn = self.context.scene
        lst = scn.custom
        current_index = scn.custom_index

        if len(lst) > 0:
            # reverse range to remove last item first
            for i in range(len(lst) - 1, -1, -1):
                scn.custom.remove(i)
            self.report({'INFO'}, "All items removed")

        else:
            self.report({'INFO'}, "Nothing to remove")

        return {'FINISHED'}
