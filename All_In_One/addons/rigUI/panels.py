import bpy
#import collections
import inspect
from . import func_picker as mod

class PickerMakerPanel(bpy.types.Panel):
    bl_label = "Rig UI"
    bl_category = "RIG Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        ob = context.object
        scene = context.scene

        layout = self.layout
        col = layout.column(align=False)
        col.prop_search(context.scene.UI,'rig',context.scene,'objects',text = 'Rig ')
        col.prop_search(context.scene.UI,'canevas',context.scene,'objects',text = 'Canevas ')
        col.prop_search(context.scene.UI,'symmetry',context.scene,'objects',text = 'Symmetry ')


        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("rigui.create_shape",icon = 'MESH_DATA',text = 'Create shape')
        row.operator("rigui.mirror_shape",icon = 'ARROW_LEFTRIGHT',text = 'Mirror shape')
        col.operator("rigui.name_from_bone",icon = 'SORTALPHA' ,text = 'Name from bones')

        row = layout.row(align=True)

        row.operator("rigui.store_ui_data", icon = 'PASTEDOWN',text = 'Store shape')

        row = layout.row(align=True)

        if ob :
            col = layout.column(align=False)

            material_row = col.row(align = True)
            material_row.operator("rigui.remove_mat",icon='ZOOMOUT',text='')
            material_row.operator("rigui.add_mat",icon='ZOOMIN',text='')
            mat = False
            if ob.type in ('MESH','CURVE','FONT') and ob.data.materials :
                mat = ob.data.materials[0]
                if mat and mat.node_tree:
                    emission_nodes = [n for n in mat.node_tree.nodes if n.type =='EMISSION']
                    if emission_nodes :
                        material_row.prop(emission_nodes[0].inputs[0],'default_value',text='')
                        mat = True
            if not mat :
                material_row.label('No Material')
            material_row.operator("rigui.eye_dropper_mat",icon='EYEDROPPER',text='')

            shape_type_row = col.row(align = True)
            shape_type_row.prop(ob.UI,'shape_type',expand = True)
            shape_type_row.operator('rigui.select_shape_type',text='',icon = 'RESTRICT_SELECT_OFF')


            if ob.UI.shape_type == 'FUNCTION' :
                col.prop(ob.UI,'name',text='Tooltip')
                function_row = col.row(align = True)
                function_row.prop(ob.UI,'function',text='Function')
                function_row.operator("rigui.function_selector",text='',icon='COLLAPSEMENU')
                if ob.UI.function :
                    col.label("Arguments : (%s)"%inspect.getdoc(getattr(mod,ob.UI.function)))
                    col.prop(ob.UI,'arguments',text='')
                    col.prop(ob.UI,'shortcut',text='Shortcut')
            if ob.UI.shape_type == 'BONE' :
                if scene.UI.rig :
                    col.prop_search(ob.UI,'name',scene.UI.rig.pose,'bones',text='Bone')
