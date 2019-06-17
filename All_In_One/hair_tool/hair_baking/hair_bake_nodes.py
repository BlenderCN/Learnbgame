import bpy
from bpy.types import NodeTree, Node, NodeSocket
import numpy as np
import math
from .hair_tree_update import ht_node_tree_update
from bpy.app.handlers import persistent
# import sys
# dir = 'C:\\Users\\JoseConseco\\AppData\Local\\Programs\\Python\Python36\\Lib\\site-packages'
# if not dir in sys.path:
#     sys.path.append(dir )
# import ipdb


# Implementation of custom nodes from Python
#TODO: propagate updates (in socket, and/or possibly   form node level)
#TODO: undo breaks cache.... maybe change hash(node) to hash(node.blname ...)
data_cache = {}


@persistent
def load_handler(dummy):
    print ('Runing load_hander input nodes test')
    textureNodeTrees = [nodeTree for nodeTree in bpy.data.node_groups if nodeTree.bl_idname == 'TextureChannelMixing']
    for nodeTree in textureNodeTrees:
        inputNodes = [node for node in nodeTree.nodes if node.bl_idname == 'InputTexture']
        for node in inputNodes:
            node.execute_node(bpy.context)


bpy.app.handlers.load_post.append(load_handler)

# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
class MyCustomTree(NodeTree):
    # Description string
    '''A custom node tree type that will show up in the node editor header'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'TextureChannelMixing'
    # Label for nice name display
    bl_label = "Texture Channel Mixing"
    # Icon identifier
    bl_icon = 'NODETREE'

    def update(self):
        # ipdb.set_trace()
        ht_node_tree_update(self)

# Mix-in class for all custom nodes in this tree type.
# Defines a poll function to enable instantiation.
class ChannelMixingTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'TextureChannelMixing'


# Custom socket type
class ImgChannelSocket(NodeSocket):
    # Description string
    '''Custom node socket type'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'ImgChannelSocket'
    # Label for nice name display
    bl_label = "Image Channel Socket"

    def socket_update(self,context):
        print('Update  node from inside socket')
        self.node.execute_node(context)
        pass

    channel_color_val: bpy.props.FloatProperty(name = "", description = "", default = 0.0, min = 0, max = 1, update=socket_update)
 
    @staticmethod
    def get_other_socket(socket):
        """
        get socket from another site of link conected to this socket
        """ 
        if not socket.is_linked:
            return None
        if socket.is_output:
            other = socket.links[0].to_socket
        else:
            other = socket.links[0].from_socket

        if other.node.bl_idname == 'NodeReroute':
            if not socket.is_output:
                return socket.get_other_socket(other.node.inputs[0])
            else:
                return socket.get_other_socket(other.node.outputs[0])
        else:  
            return other

    @staticmethod
    def get_socket_hash(socket):
        """Id of socket used for  data_cache"""
        return hash(socket.id_data.name + socket.node.name + socket.identifier)

    def socket_cache_set(self, context,data):
        """sets socket data for socket"""
        global data_cache
        s_id =  self.get_socket_hash(self)
        s_ng = self.id_data.name
        if s_ng not in data_cache:
            data_cache[s_ng] = {}
        data_cache[s_ng][s_id] = data
        output_nodes = set()
        if self.is_linked and self.is_output:
            for node_output_link in self.links:
                output_nodes.add(node_output_link.to_node)
        for node in output_nodes:
            node.execute_node(context)
   
    def socket_cache_get(self, context, deepcopy=True):
        if self.is_linked and not self.is_output: #check inputs for its cache
            global data_cache
            linked_socket = self.get_other_socket(self)  #find socket other end of link
            s_id = self.get_socket_hash(linked_socket)  # hast(linkde_socked) - gives bad result on undo
            s_ng = linked_socket.id_data.name
            if s_ng not in data_cache:
                print('No chache found for node tree %s ' %(s_ng))
                #maybe we should build one...
                ht_node_tree_update(linked_socket.id_data)  #Takes Node Tree
                return np.array([self.channel_color_val], dtype= np.float16) #raise LookupError
            if s_id in data_cache[s_ng]:
                out = data_cache[s_ng][s_id]
                return out
            #cant find socked s_id in cache? should not happend (but haapens with undo anyway) fixed...
            print('No chache found for node tree %s socket %s' %(s_ng,s_id))
            #maybe try calculating node for which tere is no cache (can be empty input image maybe...)
            self.links[0].from_node.execute_node(context)  # get socket.node
            return np.array([self.channel_color_val], dtype= np.float16)
        else:
            return np.array([self.channel_color_val], dtype= np.float16)

        
    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "channel_color_val", text=text)

    # Socket color
    def draw_color(self, context, node):
        return (0.4, 0.4, 0.4, 1.0)


# Derived from the Node base type.
class OutputTextureNode(Node, ChannelMixingTreeNode):
    '''A custom node'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'OutputTexture'
    # Label for nice name display
    bl_label = "Output Texture"
    # Icon identifier
    bl_icon = 'SOUND'


    def execute_node(self, context):
        print('Update node run from %s' %(self.name))
        suffix = 'png' if self.output_format=='PNG' else 'tga'
        imgName = self.img +'.'+suffix
        if imgName not in bpy.data.images.keys():
            bpy.data.images.new(imgName, width=128, height=128, alpha=True, float_buffer=False)
        outputImg = bpy.data.images[imgName]
        # outputImg.file_format = outputImg.file_format
        channels = []
        for i,input_socket in enumerate(self.inputs):
            channels.append(input_socket.socket_cache_get(context)) #what if error was raised (eg cache was cleared....)
        input_res = int(math.sqrt(max(channels[0].shape[0], channels[1].shape[0],channels[2].shape[0],channels[3].shape[0])))
        np_out_img = np.zeros((input_res*input_res,4), dtype = np.float16)
        outputImg.generated_width = input_res
        outputImg.generated_height = input_res
        for i,channel in enumerate(channels):
            np_out_img[:,i] = np.resize(channel,input_res*input_res)
        outputImg.pixels = np_out_img.ravel()

    # def update(self):  #executed on ony tree change - even in not related to this node directly....
    #     #Review linked outputs.
    #     print('Update node run from %s' %(self.name))

    # def insert_link(self,link):  #works only on link insert - wont work of lind delete
    #     print('LInk changed from %s to %s' %(link.from_node.name, link.to_node.name))

    img: bpy.props.StringProperty(name="Image", description="Output image name", default = "Output",  update=execute_node)
    img_path: bpy.props.StringProperty(name="Path", subtype='DIR_PATH', default= "//textures/")
    
    my_items = (
        ('PNG', "PNG", ""),
        ('TARGA', "TGA", "")
    )
    output_format: bpy.props.EnumProperty(name="Format", description="Format", items=my_items, default='PNG', update=execute_node)

    # === Optional Functions ===
    # Initialization function, called when a new node is created.
    # This is the most common place to create the sockets for a node, as shown below.
    # NOTE: this is not the same as the standard __init__ function in Python, which is
    #       a purely internal Python method and unknown to the node system!
    def init(self, context):
        self.inputs.new('ImgChannelSocket', "R")
        self.inputs.new('ImgChannelSocket', "G")
        self.inputs.new('ImgChannelSocket', "B")
        self.inputs.new('ImgChannelSocket', "A")


    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.prop(self, "img_path")
        row = layout.row(align=True)
        row.prop(self, "img")
        op = row.operator('image.save_img', text='', icon='FILE_TICK')
        op.image_name = self.img
        op.image_path = self.img_path
        op.image_format = self.output_format
        layout.prop(self, "output_format")


    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically
    def draw_label(self):
        return "Output texture"


# Derived from the Node base type.
class InputTextureNode(Node, ChannelMixingTreeNode):
    '''A custom node'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'InputTexture'
    # Label for nice name display
    bl_label = "Input Texture"
    # Icon identifier
    bl_icon = 'SOUND'


    def execute_node(self, context):
        print('Update node run from %s' %(self.name))
        if self.img[:3] == '   ':
            self['img'] = self.img[3:]

        if self.img != '' and self.img in bpy.data.images.keys():
            node_img = bpy.data.images[self.img]
            np_input_img = np.array(node_img.pixels[:])
            np_input_img.shape = (node_img.size[0]*node_img.size[1],4)
            for i,output_socket in enumerate(self.outputs):
                output_socket.socket_cache_set(context,np_input_img[:,i])
        else:
            empty_img = np.zeros(32*32*4, dtype= np.float16) #just output to cache anything
            for i,output_socket in enumerate(self.outputs):
                output_socket.socket_cache_set(context,empty_img)
            return 
        #bpy.data.node_groups['NodeTree'].nodes['Input Texture'].outputs['R'].is_linked  - give socket node
        #bpy.data.node_groups['NodeTree'].nodes['Input Texture'].outputs['R'].node  - give socket node
        #bpy.data.node_groups['NodeTree'].nodes['Input Texture'].outputs['R'].links[0].
        #bpy.data.node_groups['NodeTree'].nodes['Input Texture'].outputs['R'].links[0].to_node, from_node, to_socket, from_socket etc.
        # self.outputs["A"].default_value = np_out_img[:,3].tolist()
        # self.update()

    # def insert_link(self,link):
    #     print('LInk changed from %s to %s' %(link.from_node.name, link.to_node.name))

    # def update(self):
    #     #Review linked outputs.
    #     print('Update node run from %s' %(self.name))

    img: bpy.props.StringProperty(name = "", description = "", default = "",  update=execute_node)

    # === Optional Functions ===
    # Initialization function, called when a new node is created.
    # This is the most common place to create the sockets for a node, as shown below.
    # NOTE: this is not the same as the standard __init__ function in Python, which is
    #       a purely internal Python method and unknown to the node system!
    def init(self, context):
        self.outputs.new('ImgChannelSocket', "R")
        self.outputs.new('ImgChannelSocket', "G")
        self.outputs.new('ImgChannelSocket', "B")
        self.outputs.new('ImgChannelSocket', "A")
    
    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.label(text="Node settings")
        layout.prop_search(self, "img", bpy.data, "images", text='Texture')


### Node Categories ###
# Node categories are a python system for automatically
# extending the Add menu, toolbar panels and search operator.
# For more examples see release/scripts/startup/nodeitems_builtins.py

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

# our own base class with an appropriate poll function,
# so the categories only show up in our own tree type
class ImageNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'TextureChannelMixing'


# all categories in a list
node_categories = [
    # identifier, label, items list
    ImageNodeCategory('TEXTUREMIX', "Images", items=[
        NodeItem("OutputTexture"),
        NodeItem("InputTexture"),
    ])
]


def registerNode():
    # nodeitems_utils.register_node_categories('CUSTOM_NODES', node_categories)
    nodeitems_utils.register_node_categories('CHANNEL_MIX', node_categories)

def unregisterNode():
    # nodeitems_utils.unregister_node_categories('CUSTOM_NODES')
    nodeitems_utils.unregister_node_categories('CHANNEL_MIX')



