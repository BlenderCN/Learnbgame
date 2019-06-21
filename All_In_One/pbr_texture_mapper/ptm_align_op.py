import bpy
from bpy.types import Operator
from bpy.props import IntProperty


class PTM_AlignOperator(Operator):
    bl_idname = "object.ptm_align_op"
    bl_label = "Align nodes"
    bl_description = "Align nodes to active" 
    bl_options = {'REGISTER', 'UNDO'} 
    
    # 0 = Left, 1 = Right, 2 = Up, 3 = Down, 4 = Same width
    align = IntProperty(name="Alignment", options={'HIDDEN'}, default=0)
    
        
    @classmethod
    def poll(cls, context):        
        return True
         
    def execute(self, context):
        
        tree = context.space_data.node_tree  
                            
        selected_nodes = [ n for n in tree.nodes if n.select ]
        
        active_node = tree.nodes.active
         
        for node in selected_nodes:
            
            # left align
            if(self.align == 0):
                node.location.x = active_node.location.x
            
            # right align
            elif(self.align == 1):
                node.location.x = active_node.location.x + active_node.width - node.width
            
            # top align
            elif(self.align == 2):
                node.location.y = active_node.location.y
            
            # bottom align
            elif(self.align == 3):
                node.location.y = active_node.location.y + active_node.height - node.height
                
            # same width
            elif(self.align == 4):
                node.width = active_node.width

        return {'FINISHED'}