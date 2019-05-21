#--- ### Header
bl_info = {
           "name": "Bevel",
           "author": "Witold Jaworski, Gerard Moran",
           "version": (1, 0, 3),
           "blender": (2, 5, 9),
           "api": 39307,
           "location": "View3D -> Edit Mode -> Special (W-key)",
           "category": "Mesh",
           "description": "Bevels selected edges",
           "warning": "Beta",
           "tracking_url": "https://github.com/neomonkeus/blender_bevel"
           }

import bpy
from bpy.utils import register_module, unregister_module
from bpy.props import FloatProperty

'''  
    Type declaration: useful for auto-completion 
    Comment before publishing
    edge = bpy.types.MeshEdge
    obj = bpy.types.Object
    obj.modifiers.remove(modifier)
    bevel = bpy.types.BevelModifier
    width = bpy.types.FloatProperty
'''

#--- ###Operator
class Bevel(bpy.types.Operator):
    '''Bevels selected edges of the mesh'''
    bl_idname = "mesh.bevel"
    bl_label = "Bevel"
    bl_description = "Bevel selected edges"
    bl_options = {'REGISTER', 'UNDO'}
    
    #---operator parameters
    width = FloatProperty(name="Width", description="Bevel width",
                          subtype = 'DISTANCE', default = 0.1, min = 0.0, max = 1.0,
                          step = 1, precision = 2)
    
    LAST_WIDTH_USED = "mesh.bevel.last_width"
    BEVEL_MODIFIER = bpy.types.BevelModifier
    PREV_POS_VAL = 0
    DIFFERENCE = 0.0
    
    def __init__(self):
        print("Start")

    def __del__(self):
        print("End")
    
    @classmethod
    def poll(cls, context):
        return(context.mode == "EDIT_MESH")
    
    def invoke(self, context, event):
        print("Invoke() called")
        #refresh data:
        bpy.context.scene.update()  
        selected = 0
        #check edges
        for edge in context.object.data.edges:
            if edge.select:
                selected += 1
                break           
        print("Edges checked: \nMode: " + str(bpy.context.mode))
        #Edit_mode
        if selected > 0:

            #assign weights
            obj = context.active_object
            assign_bevel_weights(obj)
            
            bpy.context.scene.update()
            print("Init Edge: Bevel weights: " + str(obj.data.edges[1].bevel_weight))
            
            #Init mouse position     
            self.PREV_POS_VAL = event.mouse_x
            
            #Setup Bevel modifier 
            bpy.ops.object.modifier_add(type='BEVEL')
            self.BEVEL_MODIFIER = obj.modifiers[-1]
            self.BEVEL_MODIFIER.limit_method = 'WEIGHT'
            self.BEVEL_MODIFIER.edge_weight_method = 'LARGEST'
            
            last_width = context.scene.get(self.LAST_WIDTH_USED, None)
            if last_width:
                self.width = last_width
                self.BEVEL_MODIFIER.width = last_width
            else:
                self.BEVEL_MODIFIER.width = self.width = 1.0
             
            #move modifier to top of the list
            while obj.modifiers[0] != self.BEVEL_MODIFIER:
                bpy.ops.object.modifier_move_up(modifier = self.BEVEL_MODIFIER.name)

            context.window_manager.modal_handler_add(self)
            print("Invoke() finished \nModal() Called")
            return {'RUNNING_MODAL'}
        else:
            self.report(type = "ERROR", message = "No edges selected")
            return {'CANCELLED'}
    
    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':  # Apply
            newvalue = event.mouse_x
            #print("Mouse x:" + str(newvalue))
            self.DIFFERENCE = (self.PREV_POS_VAL - newvalue)/100.0
            #print("Diff: " + str(difference))
            self.BEVEL_MODIFIER.width += self.DIFFERENCE
            self.width += self.DIFFERENCE
            #self.width =  + DIFFERENCE
            #print("Mod Width: " + str(self.BEVEL_MODIFIER.width))
            self.PREV_POS_VAL = newvalue
            context.scene.update()
        elif event.type == 'LEFTMOUSE':  # Confirm
            self.execute(context)
            return {'FINISHED'}
        elif event.type in ('RIGHTMOUSE', 'ESC'):  # Cancel
            print("Cancel Called \nMode: " + str(bpy.context.mode))
            obj = context.active_object
            self.BEVEL_MODIFIER = None
            obj.modifiers.remove(obj.modifiers[0])
            print("Deleted Modifier")
            clear_bevel_weights(obj)
            print("Edges: Bevel weights" + str(obj.data.edges[1].bevel_weight))
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}    

    def execute(self, context):
        print("In execute()")
        print("Bevel.width: " + str(context.active_object.modifiers[0].width))
        bpy.ops.object.editmode_toggle()
        print("Mode: " + str(context.mode))
        print("Bevel.width: " + str(context.active_object.modifiers[0].width))
        bpy.ops.object.modifier_apply(apply_as = 'DATA', modifier = self.BEVEL_MODIFIER.name)
        print("Modifier Applied")
        clear_bevel_weights(context.active_object)
        bpy.ops.object.editmode_toggle()
        print("Edge: Bevel Weight Values:")
        print(context.active_object.data.edges[1].bevel_weight)
        context.scene[self.LAST_WIDTH_USED] = self.width
        return('FINISHED')

def clear_bevel_weights(obj):
    for edge in obj.data.edges:
        if edge.select:
            edge.bevel_weight = 0.0

def assign_bevel_weights(obj):
    for edge in obj.data.edges:
        if edge.select:
            edge.bevel_weight = 1.0

def menu_draw(self, context):
    self.layout.operator_context = 'INVOKE_REGION_WIN'
    self.layout.operator(Bevel.bl_idname, "Bevel")
            
def register():
    register_module(__name__)
    bpy.types.VIEW3D_MT_edit_mesh_specials.prepend(menu_draw)
    
def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_specials.remove(menu_draw)
    unregister_module(__name__)
    
if __name__ == '__main__':
    register()
        
        