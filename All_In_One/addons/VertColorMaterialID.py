bl_info = {
    "name": "Vertex IDs from Material",
    "description": "Stores Material IDs in Vertex Colors",
    "author": "OlesenJonas",
    "version": (1, 3),
    "blender": (2, 80, 0),
    "location": "Object Mode -> Toolbar",
    "category": "Learnbgame",
}

import bpy
from bpy.props import *


#########################################  END PRE STUFF #####################################################

class idTransfer(bpy.types.Operator):
    """idTransfer class"""
    bl_idname = "myops.add_idtransfer"
    bl_label = "Transfer to Vert Color"

    def execute(self,context):
        #
        #has to start in object mode
        #
        bpy.ops.object.mode_set(mode = 'OBJECT')
    

        context = bpy.context
        obj = context.object
        mesh = obj.data

        #preset color palette
        cols = [
            [0.0,0.0,1.0],
            [0.0,1.0,0.0],
            [1.0,0.0,0.0],
            [1.0,1.0,1.0],
            [1.0,1.0,0.0],
            [1.0,0.0,1.0],
            [0.0,1.0,1.0],
            [0.0,0.0,0.0]
        ]

        #create vert color layer if not already
        if not mesh.vertex_colors:
            mesh.vertex_colors.new()

        #Cancel if object has no materials
        if len(obj.material_slots) == 0:
            bpy.context.window_manager.popup_menu(idTransfer.drawErr, title="No Material Data to transfer", icon='ERROR')
            return {"CANCELLED"}

        #iterate faces                                              
        for poly in mesh.polygons:
            mat = obj.material_slots[poly.material_index].material
            if mat is None:
                bpy.context.window_manager.popup_menu(idTransfer.drawErr, title="No Material Data to transfer", icon='ERROR')
                return {"CANCELLED"}
            if context.scene.useViewpCol == True:
                rgb = mat.diffuse_color
            else:
                rgb = cols[poly.material_index % 8]
            for loop_index in poly.loop_indices:
                mesh.vertex_colors.active.data[loop_index].color[0] = rgb[0]
                mesh.vertex_colors.active.data[loop_index].color[1] = rgb[1]
                mesh.vertex_colors.active.data[loop_index].color[2] = rgb[2]

        if context.scene.resetAfter == True:
            #after transfer set viewport colors to white:
            for poly in mesh.polygons:
                if obj.material_slots[poly.material_index].material.diffuse_color != [1.0,1.0,1.0]:
                    obj.material_slots[poly.material_index].material.diffuse_color = [1.0,1.0,1.0]

        #at end switch to vertex paint to see change
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        if (context.scene.resetAfter == False) and (context.scene.useViewpCol == True):
            bpy.context.window_manager.popup_menu(idTransfer.drawFin, title="Done!", icon='FILE_TICK')
        return {"FINISHED"}

    def drawErr(self, context):
        self.layout.label(text = "One or more faces have no material assigned")

    def drawFin(self, context):
        self.layout.label(text = "Change viewport color back to white to see result")


##############################     END FUNCTIONALITY CLASS    #################################################################



class idTransferPanel(bpy.types.Panel):
    #creating Panel
    bl_label = "ID Transfer Panel"
    bl_idname = "VIEW3D_OT_idtran"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "VertColTransfer"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        
        layout.prop(scn, "useViewpCol")
        layout.prop(scn, "resetAfter")

        row = layout.row()
        row.operator("myops.add_idtransfer")


###########################################    END UI-PANEL CLASS   ########################################################


classes = (
    idTransfer,
    idTransferPanel,
)


def register():

    bpy.types.Scene.useViewpCol = BoolProperty(
        name = "Use Viewport Colors", description="Uses Material Viewport Colors when true, otherwise generate Colors (up to 8)", default = True)
    bpy.types.Scene.resetAfter = BoolProperty(
        name = "Reset after Transfer", description="Clears viewport colors after transfer", default = True)

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():

    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)

    del bpy.types.Scene.useViewpCol
    del bpy.types.Scene.resetAfter


if __name__ == '__main__':
    register()
