bl_info = {
    "name": "Pie Selection",
    "description": "Select Modes",
    "author": "Vaughan Ling",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
    }

import bpy
from bpy.types import Menu

# Select Pie
class VIEW3D_PIE_SELECT(Menu):
    bl_idname = "pie.select"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        # left
        split = pie.split()
        # Right
        if bpy.context.mode == 'EDIT_MESH':
            pie.operator("mesh.hp_select_border", text="Border", icon='NONE')
        else:
            split = pie.split()
            
        
        # bottom
        pie.operator("object.mode_set", text="Object", icon='MESH_CUBE').mode='OBJECT'
        
        
        # top
        if bpy.context.object.type == "GPENCIL":
            pie.operator('object.mode_set', text = 'GP Edit', icon='EDITMODE_HLT').mode='EDIT_GPENCIL'
        elif bpy.context.object.type == "META":
            pie.operator('object.mode_set', text = 'Edit', icon='META_DATA').mode='EDIT'
        elif bpy.context.object.type == "ARMATURE":
            pie.operator('object.mode_set', text = 'Edit', icon='NONE').mode='EDIT'
        elif bpy.context.object.type == 'LATTICE':
            pie.operator('object.mode_set', text = 'Edit', icon='NONE').mode='EDIT'      
        else:
            pie.operator("object.selectmodesmart", text="Edge", icon='NONE').selectmode='EDGE'
            
            
        # topleft
        if bpy.context.object.type == "GPENCIL":
            pie.operator('object.mode_set', text = 'GP Draw', icon='GREASEPENCIL').mode='PAINT_GPENCIL'
        elif bpy.context.object.type == "ARMATURE":
            pie.operator('object.mode_set', text = 'Pose', icon='NONE').mode='POSE'            
        elif bpy.context.object.type == "META": 
            split = pie.split()
            col = split.column()
            col.scale_x=1.1
            col.label(text="")
        elif bpy.context.object.type == 'LATTICE':
            split = pie.split()
        else:
            pie.operator("object.selectmodesmart", text="Vert", icon='NONE').selectmode='VERT'
            

        # topright
        if bpy.context.object.type == "GPENCIL":
            pie.operator('object.mode_set', text = 'GP Sculpt', icon='SCULPTMODE_HLT').mode='SCULPT_GPENCIL'
        elif bpy.context.object.type == "META": 
            split = pie.split()
            col = split.column()
            col.scale_x=1.1
            col.label(text="")
        elif bpy.context.object.type == 'LATTICE':
            split = pie.split()
        else:
            pie.operator("object.selectmodesmart", text="Face", icon='NONE').selectmode='FACE'

        # bottomleft
        split = pie.split()
        col = split.column()
        col.scale_y=1.5
        if context.mode == 'OBJECT' and context.object.type == 'MESH':
            col.operator("object.select_grouped", text="Similar")
        elif bpy.context.object.type == "GPENCIL":

            col.operator('view3d.gp_canvas', text = 'Side', icon='NONE').type = 'X'
            col.operator('view3d.gp_canvas', text = 'Front', icon='NONE').type = 'Y'
            col.operator('view3d.gp_canvas', text = 'Top', icon='NONE').type = 'Z'
#           col.operator('view3d.gp_canvas', text = 'Top', icon='NONE').type = 'Top'
#           col.operator('view3d.gp_canvas', text = '+', icon='NONE').type = '+'
#           col.operator('view3d.gp_canvas', text = '-', icon='NONE').type = '-'
        else:
            col.operator("mesh.select_similar", text="Similar")
            

        # bottomright
        if bpy.context.mode == 'EDIT_MESH':
            pie.operator("mesh.faces_select_linked_flat", text="Select Flat").sharpness=0.436332
        else:
            split = pie.split()
            col = split.column()
            col.scale_y=1.5
            col.operator('object.sculpt_mode_with_dynotopo', text = 'Sculpt', icon='SCULPTMODE_HLT')
            col.operator('object.mode_set', text = 'Paint', icon='BRUSH_DATA').mode='TEXTURE_PAINT'
class HP_OT_gp_canvas(bpy.types.Operator):
    bl_idname = "view3d.gp_canvas"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    type: bpy.props.StringProperty(name="Front")
    def execute(self, context):
        vector = (0,0,0)
        if self.type == 'Front':
            bpy.data.objects['GP_Canvas'].rotation_euler = (0,0,1.5708)
        if self.type == 'Top':
            bpy.data.objects['GP_Canvas'].rotation_euler = (0,1.5708,0)
        if self.type == 'Side':
            bpy.data.objects['GP_Canvas'].rotation_euler = (1.5708,0,0)
        if self.type == '+':
            bpy.context.space_data.cursor_location[0] += 1
        if self.type == '-':
            bpy.context.space_data.cursor_location[0] -= 1
        if self.type == 'X':
            bpy.context.tool_settings.gpencil_sculpt.lock_axis = 'AXIS_X'
        if self.type == 'Y':
            bpy.context.tool_settings.gpencil_sculpt.lock_axis = 'AXIS_Y'
        if self.type == 'Z':
            bpy.context.tool_settings.gpencil_sculpt.lock_axis = 'AXIS_Z'
        return {'FINISHED'}
class HP_OT_sculpt_mode_with_dynotopo(bpy.types.Operator):
    bl_idname = "object.sculpt_mode_with_dynotopo"      # unique identifier for buttons and menu items to reference.
    bl_label = ""      # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.
    def invoke(self, context, event):
        bpy.ops.sculpt.sculptmode_toggle()
        bpy.ops.sculpt.dynamic_topology_toggle()
        return {'FINISHED'}
class SelectModeSmart(bpy.types.Operator):
    """SelectModeSmart"""      # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "object.selectmodesmart"        # unique identifier for buttons and menu items to reference.
    bl_label = "Select Mode Smart"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.
    selectmode : bpy.props.StringProperty(name="SelectMode")
    def invoke(self, context, event):
        def select(selectmode):
            bpy.ops.mesh.select_mode(type=selectmode)

        if bpy.context.mode == 'OBJECT':
            if bpy.context.object.type == "MESH":
                bpy.ops.object.mode_set(mode='EDIT')
                select(self.selectmode)
            elif bpy.context.object.type == "GPENCIL":
                bpy.ops.object.mode_set(mode='GPENCIL_PAINT')
            elif bpy.context.object.type in ('CURVE','FONT'):
                bpy.ops.object.mode_set(mode='EDIT')

        elif bpy.context.mode == 'EDIT_MESH':
            select(self.selectmode)
        elif bpy.context.mode == 'GPENCIL_PAINT':
            bpy.context.mode = 'OBJECT'
        else:
            bpy.ops.object.mode_set(mode='EDIT')
                
        # except:
            # self.report({'ERROR'}, "Select An Object First")
        return {'FINISHED'}



class SelectSmartSimilar(bpy.types.Operator):
    """SelectSmartVert"""      # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "view3d.selectsmartsimilar"        # unique identifier for buttons and menu items to reference.
    bl_label = "Select Smart Similar"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def invoke(self, context, event):
        if bpy.context.mode=='OBJECT':
            bpy.ops.object.select_grouped()
        else:
            bpy.ops.mesh.select_similar()


class SelectSmartLinkedAndLoop(bpy.types.Operator):
    """SelectSmartVert"""      # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "mesh.selectsmartlinkedandloop"        # unique identifier for buttons and menu items to reference.
    bl_label = "Select Smart Linked And Loop"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def invoke(self, context, event):
        if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, True, False):
            bpy.ops.mesh.loop_multi_select()
        else:
            bpy.ops.mesh.select_linked(delimit={'SEAM'})
        return {'FINISHED'}
class HP_OT_select_border(bpy.types.Operator):
    """Select Border"""    # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "mesh.hp_select_border"        # unique identifier for buttons and menu items to reference.
    bl_label = "Select Border"        # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def invoke(self, context, event):
        bpy.ops.mesh.select_mode(type='EDGE')
        bpy.ops.mesh.region_to_loop()
        return {'FINISHED'}


classes = (
    VIEW3D_PIE_SELECT,
    SelectModeSmart,
    SelectSmartLinkedAndLoop,
    SelectSmartSimilar,
    HP_OT_sculpt_mode_with_dynotopo,
    HP_OT_gp_canvas,
    HP_OT_select_border,
)
register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
