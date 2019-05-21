import bpy
from bpy.types import Operator
 
class PTM_MappingOperator(Operator):
    bl_idname = "object.ptm_mapping_op"
    bl_label = "Map textures"
    bl_description = "Connect PBR textures to the Principled shader" 
    bl_options = {'REGISTER', 'UNDO'} 

    def add_link_by_index(self, tree, node, node2, output_name, input_index):
        tree.links.new(node.outputs[output_name], node2.inputs[input_index])       
    
    def add_link(self, tree, node, node2, output_name, input_name, non_color_data = False):
        
        tree.links.new(node.outputs[output_name], node2.inputs[input_name])
        
        if(hasattr(node, "color_space")):
            if(non_color_data):
                node.color_space = "NONE"
            else:
                node.color_space = "COLOR"
    
    def create_normal_map(self, tree):
        return tree.nodes.new('ShaderNodeNormalMap')

    def create_emission_shader(self, tree):
        return tree.nodes.new('ShaderNodeEmission')

    def create_add_shader(self, tree):
        node = tree.nodes.new('ShaderNodeAddShader')
        return node
             
    def execute(self, context):
        
        tree = context.space_data.node_tree
        
        shader_principled_node  = None

        mat_output_node  = None

        texture_nodes = []

        for node in tree.nodes:
            if node.type == "BSDF_PRINCIPLED":
                shader_principled_node = node
            elif node.type == "TEX_IMAGE":
                texture_nodes.append(node)
            elif node.type == "OUTPUT_MATERIAL":
                mat_output_node = node
        
        if(shader_principled_node == None or len(texture_nodes) == 0):
            return {'CANCELLED'} 
        
           
        for node in texture_nodes:
            
            lower_name = node.image.name.lower()
            
            if any(name in lower_name for name in ["diffuse", "albedo"]):            
                self.add_link(tree, node, shader_principled_node, "Color", "Base Color")
                
            elif("metallic" in lower_name):
                self.add_link(tree, node, shader_principled_node, "Color", "Metallic", True)
                
            elif("roughness" in lower_name):
                self.add_link(tree, node, shader_principled_node, "Color", "Roughness", True)

            elif any(name in lower_name for name in ["emission", "emissive"]): 
                emission_node = self.create_emission_shader(tree)
                add_shader_node = self.create_add_shader(tree)

                self.add_link(tree, node, emission_node, "Color", "Color", False)
                self.add_link_by_index(tree, emission_node, add_shader_node, "Emission", 1)
                self.add_link_by_index(tree, shader_principled_node, add_shader_node, "BSDF", 0)
                self.add_link(tree, add_shader_node, mat_output_node, "Shader", "Surface", True)
                   
            elif("normal" in lower_name):
                
                if(len(node.outputs["Color"].links) == 0):
                    
                    normal_node = self.create_normal_map(tree)
                    
                    self.add_link(tree, node, normal_node, "Color", "Color", True)
                    self.add_link(tree, normal_node, shader_principled_node, "Normal", "Normal")
                
        return {'FINISHED'}