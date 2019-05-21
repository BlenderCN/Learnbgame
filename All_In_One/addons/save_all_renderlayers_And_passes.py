# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

#
#  Author            : Tamir Lousky [ tlousky@gmail.com, tamir@pitchipoy.tv ]
#
#  Homepage(Wiki)    : http://bioblog3d.wordpress.com/
#  Studio (sponsor)  : Pitchipoy Animation Productions (www.pitchipoy.tv)
# 
#  Start of project              : 2013-04-04 by Tamir Lousky
#  Last modified                 : 2013-06-08
#
#  Acknowledgements 
#  ================
#  PitchiPoy: Niv Spigel (for coming up with the idea)
#  Blender Institute: Brecht van Lommel (fixing a bug with the file
#                     output node within 30 minutes of my reporting it!)

bl_info = {    
    "name"       : "Save Layers and Passes in respectively named folders.",
    "author"     : "Tamir Lousky (Original Author), Luciano Muñoz (added folder creation functionality)",
    "version"    : (0, 0, 3),
    "blender"    : (2, 68, 0),
    "category"   : "Render",
    "location"   : "Node Editor >> Tools",
    "wiki_url"   : "https://github.com/Tlousky/production_scripts/wiki/save_all_renderlayers_And_passes.py",
    "tracker_url": "https://github.com/Tlousky/production_scripts/blob/master/save_all_renderlayers_and_passes.py",
    "description": "Save all render layers and passes to files in respectively named folders."
}

import bpy, re

class save_images(bpy.types.Panel):
    bl_idname      = "SaveImages"
    bl_label       = "Save Images"
    bl_space_type  = 'NODE_EDITOR'
    bl_region_type = 'TOOLS'

    def draw( self, context) :
        folder_props = context.scene.folder_props

        layout = self.layout
        layout.operator( 'render.create_file_output_nodes' )
        layout.prop( folder_props, 'create_folders' )

       
class create_nodes( bpy.types.Operator ):
    """ Create a file output node for each pass in each renderlayer """
    bl_idname      = "render.create_file_output_nodes"
    bl_label       = "Create File Nodes"
    bl_description = "Create file output nodes for all render layers and passes"
    bl_options     = {'REGISTER', 'UNDO' }

    @classmethod
    def poll( self, context ):
        return context.scene.use_nodes

    def find_base_name( self ):
        blendfile = bpy.path.basename(bpy.data.filepath)
        
        pattern   = '^([\d\w_-]+)(\.blend)$'
        re_match  = re.match(pattern, blendfile)
        basename  = 'scene'  # Default to avoid empty strings
        
        if re_match:
            if len( re_match.groups() ) > 0:
                basename  = re_match.groups()[0]
            
        return( basename )        

    def get_layers_and_passes( self, context, basename ):
        rl = context.scene.render.layers
        use_folders = context.scene.folder_props.create_folders
        
        layers = {}

        pass_attr_str = 'use_pass_'
        
        for l in rl:
            imagebase = basename + "_" + l.name
            layers[l.name] = []

            # List all the attributes of the render layer pass with dir
            # then isolate all the render pass attributes
            passes = [ p for p in dir(l) if pass_attr_str in p ]
            
            for p in passes:
                # If render pass is active (True) - create output
                if getattr( l, p ):
                    pass_name = p[len(pass_attr_str):]

                    if use_folders:
                        # Distribute into subfolders for each layer and pass
                        # Example: Scene/RenderLayer/ambient_occlusion/...
                        file_path = context.scene.name + "/" + l.name + "/" + \
                                    pass_name + "/" + l.name + "_" + pass_name
                    else:
                        file_path = imagebase + "_" + pass_name
                    pass_info = {
                        'filename' : file_path,
                        'output'   : pass_name
                    }
                    layers[l.name].append( pass_info )
            
        return layers

    def execute( self, context):
        basename    = self.find_base_name()
        layers      = self.get_layers_and_passes( context, basename )

        # create references to node tree and node links
        tree  = bpy.context.scene.node_tree
        links = tree.links

        rl_nodes_y   = 0
        file_nodes_x = 0

        output_number = 0
        node = ''  # Initialize node so that it would exist outside the loop

        node_types = {
            67 : {
                'RL' : 'CompositorNodeRLayers',
                'OF' : 'CompositorNodeOutputFile',
                'OC' : 'CompositorNodeComposite'
            },
            66 : {
                'RL' : 'R_LAYERS',
                'OF' : 'OUTPUT_FILE',
                'OC' : 'COMPOSITE'
            },
        }
        
        # Renderlayer pass names and renderlayer node output names do not match
        # which is why we're using this dictionary (and some regular expressions
        # later to match the two)
        output_dict = {
            'ambient_occlusion' : 'AO',
            'material_index'    : 'IndexMA',
            'object_index'      : 'IndexOB',
            'reflection'        : 'Reflect',
            'refraction'        : 'Refract',
            'combined'          : 'Image'
        }

        # Get blender version
        version = bpy.app.version[1]

        for rl in layers:
            # Create a new render layer node
            node = ''
            if version > 66:
                node = tree.nodes.new( type = node_types[67]['RL'] )
            else:
                node = tree.nodes.new( type = node_types[66]['RL'] )

            # Set node location, label and name
            node.location = 0, rl_nodes_y
            node.label    = rl
            node.name     = rl
            
            # Select the relevant render layer
            node.layer = rl
            
            for rpass in layers[rl]:
                ## Create a new file output node
                
                # Create file output node
                output_node = ''
                if version > 66:
                    output_node = tree.nodes.new( type = node_types[67]['OF'] )
                else:
                    output_node = tree.nodes.new( type = node_types[66]['OF'] )

                # Select and activate file output node
                output_node.select = True
                tree.nodes.active  = output_node

                # Set node position x,y values
                file_node_x = 500 
                file_node_y = 200 * output_number
                
                name = rl + "_" + rpass['output']
                
                # Set node location, label and name
                output_node.location = file_node_x, file_node_y
                output_node.label    = name
                output_node.name     = name                
                
                # Set up file output path
                output_node.file_slots[0].path = rpass['filename']
                output_node.base_path          = context.scene.render.filepath

                output  = ''
                passout = rpass['output']

                if passout in output_dict.keys():
                    output = output_dict[ passout ]
                elif "_" in passout:
                    wl = passout.split("_") # Split to list of words
                    # Capitalize first char in each word and rejoin with spaces
                    output = " ".join( s[0].capitalize() + s[1:] for s in wl )
                else: # If one word, just capitlaize first letter
                    output = passout[0].capitalize() + passout[1:]

                # Set up links
                if output:
                    links.new( node.outputs[ output ], output_node.inputs[0] )

                output_number += 1
                
            rl_nodes_y += 300

        # Create composite node, just to enable rendering
        cnode = ''
        if version > 66:
            cnode = tree.nodes.new( type = node_types[67]['OC'] )
        else:
            cnode = tree.nodes.new( type = node_types[66]['OC'] )
        
        # Link composite node with the last render layer created
        links.new( node.outputs[ 'Image' ], cnode.inputs[0] )
        
        return {'FINISHED'}

class folder_options( bpy.types.PropertyGroup ):
    create_folders = bpy.props.BoolProperty(
        description = "Create a folder for each render pass",
        name        = "Create Folders",
        default     = True
    )

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.folder_props = bpy.props.PointerProperty( 
        type = folder_options
    )
    
def unregister():
    bpy.utils.unregister_module(__name__)