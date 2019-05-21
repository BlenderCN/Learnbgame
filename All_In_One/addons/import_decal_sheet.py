import bpy

bl_info = {
    "name": "Import Decal Sheet",
    "description": "Import a PNG file as a decal sheet. Add a mix shader to the end of the active material and add in the image with alpha mixing.",
    "author": "Johnny Matthews - johnny.matthews@gmail.com",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "File > Import > Import Decal Sheet",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

def read_some_data(self, context):
    ob = bpy.context.object
    mesh = bpy.context.object.data
   
    if len(mesh.uv_layers) == 8 :
        self.report({'ERROR_INVALID_INPUT'},"Maximum UV Maps Already Added")
        return {'FINISHED'}   

    bpy.ops.mesh.uv_texture_add()
    uv = mesh.uv_layers[len(mesh.uv_layers)-1]
    mat = ob.material_slots[ob.active_material_index].material
    if mat.use_nodes == False:    
        mat.use_nodes = True
        
    tree = mat.node_tree
    nodes = tree.nodes
    links = tree.links

    lowest_node = 999999
    lowest_node_height = 0
    
    for node in nodes:
        if node.location[1] < lowest_node:
            lowest_node = node.location[1]
            lowest_node_height = node.height

    output_node = None
    for node in nodes:
        if type(node).__name__ == "ShaderNodeOutputMaterial":
            output_node = node
            break

    if output_node == None:
        self.report({'ERROR_INVALID_INPUT'},"Make sure active material has at least one shader and output connected.")
        return {'FINISHED'} 

    outlink = output_node.inputs[0].links[0]

    from_node = outlink.from_node
    from_socket = outlink.from_socket
    to_node = outlink.to_node
    to_socket = outlink.to_socket

    new_node = nodes.new("ShaderNodeMixShader")
 
    links.remove(from_node.outputs[0].links[0])
    links.new(from_node.outputs[0],new_node.inputs[1])
    links.new(new_node.outputs[0],to_node.inputs[0])

    new_node.location = to_node.location
    to_node.location[0] = to_node.location[0] + 300

    frame = nodes.new("NodeFrame")
    frame.name = uv.name
    frame.label = uv.name + ' Decal Frame'
    frame.label_size = 20
    frame.use_custom_color = True
    frame.color = [0.6,0.7,1.0]
    
    new_dif = nodes.new("ShaderNodeBsdfPrincipled")
    new_dif.location = [new_node.location[0]-200, lowest_node-lowest_node_height-200]
    links.new(new_dif.outputs[0],new_node.inputs[2])
    new_dif.parent = frame

    new_img = nodes.new("ShaderNodeTexImage")
    new_img.location = [new_dif.location[0]-200, new_dif.location[1]]
    links.new(new_img.outputs[0],new_dif.inputs[0])
    links.new(new_img.outputs[1],new_node.inputs[0])
    image = bpy.data.images.load(self.filepath, False)
    new_img.image = image
    new_img.extension = 'EXTEND'
    new_img.parent = frame

    new_uv  = nodes.new("ShaderNodeUVMap")
    new_uv.location = [new_img.location[0]-200, new_img.location[1]]
    links.new(new_uv.outputs[0],new_img.inputs[0])
    new_uv.uv_map = uv.name
    new_uv.parent = frame


    self.report({'INFO'},"UV Decal Map Added to object "+ob.name+" on UV Map "+uv.name)
    return {'FINISHED'}


    

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class gizmoUVApplicator(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "object.uv_applicator"  
    bl_label = "UV Decal Applicator"

    filename_ext = ".png"

    filter_glob = StringProperty(
            default="*.png",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    def execute(self, context):
        return read_some_data(self, context)

    @classmethod
    def poll(cls,context):
        return context.active_object.type == "MESH"

# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(gizmoUVApplicator.bl_idname, text="Import Decal Sheet")


def register():
    bpy.utils.register_class(gizmoUVApplicator)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(gizmoUVApplicator)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
