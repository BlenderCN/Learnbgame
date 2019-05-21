bl_info = {
    "name": "Rename output and input nodes",
    "author": "Tal Hershkovich ",
    "version": (0, 2),
    "blender": (2, 78, 0),
    "location": "Node Editor > Tool Shelf > Render > Rename Outputs",
    "description": "replace strings of inputs and output nodes in node editor as well as the render output",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Render/Rename_Outputs",
    "category": "Learnbgame"
}

import bpy
   
def replace_outputs(self, context):
    old_str = bpy.context.scene.old_string
    new_str = bpy.context.scene.new_string
    inputs = bpy.context.scene.inputs
    outputs = bpy.context.scene.outputs
    for scene in bpy.data.scenes:
        
        if scene.use_nodes:
            
            for node in scene.node_tree.nodes:
                if node.type == 'OUTPUT_FILE' and outputs == True:
                    node.base_path = node.base_path.replace(old_str, new_str)          
                    node.file_slots[0].path = node.file_slots[0].path.replace(old_str, new_str)
                    node.name = node.name.replace(old_str, new_str)
                    
                elif node.type == 'IMAGE' and inputs == True:
                    node.image.filepath = node.image.filepath.replace(old_str, new_str)
                    node.image.name = node.image.name.replace(old_str, new_str)
                    node.name = node.name.replace(old_str, new_str)
                
        if outputs == True:
            scene.render.filepath = scene.render.filepath.replace(old_str, new_str)
        
class Rename_Output(bpy.types.Operator):
    """Rename a string in all your render and compositing outputs"""
    bl_label = "Rename"
    bl_idname = "rename.outputs"
    bl_options = {'REGISTER', 'UNDO'}
    
    bpy.types.Scene.outputs = bpy.props.BoolProperty(name="Output Nodes", description="Affect output nodes", default=True, options={'HIDDEN'})
    
    bpy.types.Scene.inputs = bpy.props.BoolProperty(name="Input nodes", description="Affect input nodes", default=False, options={'HIDDEN'})  
    
    bpy.types.Scene.old_string = bpy.props.StringProperty(name="Find", description="The string that you want to be replaced")
    
    bpy.types.Scene.new_string = bpy.props.StringProperty(name="Replace", description="The string that you want to be replaced")
        
    def execute(self, context):
        replace_outputs(self, context)
        return {'FINISHED'} 
    
class Rename_Output_Panel(bpy.types.Panel):
    """Rename a string in all your render and compositing outputs"""
    bl_label = "Rename Outputs"
    bl_idname = "renameoutputs.panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "Render"
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        row = col.row()
        row.prop(context.scene, 'inputs')
        row.prop(context.scene, 'outputs')
        row = col.row()
        row.label(text="Rename String")
        row = col.row()
        row.prop(context.scene, 'old_string')
        row = col.row()
        row.prop(context.scene, 'new_string')
        row = col.row()
        row.operator("rename.outputs")   

def register():
    bpy.utils.register_class(Rename_Output)
    bpy.utils.register_class(Rename_Output_Panel)

def unregister():
    bpy.utils.unregister_class(Rename_Output)
    bpy.utils.unregister_class(Rename_Output_Panel)

if __name__ == "__main__":
    register()                                  