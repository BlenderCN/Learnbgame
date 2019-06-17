bl_info = {
    "name": "Easy Model Compositing",
    "author": "Jeffrey Hepburn - John Roper",
    "version": (1, 2,2),
    "blender": (2, 77, 0),
    "location": "Render Panel (Properties editor) > Easy Model Compositing",
    "description": "Generate an easy model composite",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Render"
}

import bpy
from os.path import basename
from bpy.props import *
from bpy_extras.io_utils import ImportHelper, ExportHelper

####################
# Setup Subject(s) #
####################
class ECS_Setup_Subjects(bpy.types.Operator):
    """Setup the subject(s)"""
    bl_idname = "render.ecs_setup_subjects"
    bl_label = "Setup Subject(s)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            obj.pass_index = 100

        return {'FINISHED'}

###########################
# Setup Shadow Catcher(s) #
###########################
class ECS_Setup_Shadow_Catchers(bpy.types.Operator):
    """Setup the shadow catcher(s)"""
    bl_idname = "render.ecs_setup_shadow_catchers"
    bl_label = "Setup Shadow Catcher(s)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            obj.pass_index = 101

        return {'FINISHED'}

#######################
# Set Render Settings #
#######################
class ECS_Set_Render_Settings(bpy.types.Operator):
    """Set the render settings"""
    bl_idname = "render.ecs_set_render_settings"
    bl_label = "Setup Render"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        pimage_op = context.scene.use_pimage
        render_layers = bpy.context.scene.render.layers

        for layer in render_layers:
            layer.use_pass_object_index = True
            layer.use_pass_ambient_occlusion = True
            layer.use_pass_diffuse_direct = True
            layer.use_pass_glossy_indirect = True

        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.scene.cycles.film_transparent = True
        
        addon_dir = bpy.utils.user_resource('SCRIPTS', "addons")
        blendfile = addon_dir + "/easy_model_compositing/node.blend"
        selection = "\\NodeTree\\"
        ngroup = "EasyModelCompositor"

        filepath = blendfile + selection + ngroup
        directory = blendfile + selection
        filename = ngroup

        newNgroup = bpy.ops.wm.append(filepath=filepath, filename=filename, directory=directory)
        
        if pimage_op == True:
            previewImagePath = bpy.path.abspath(context.scene.backgroundFilePath)
            imageName = basename(previewImagePath)
            bpy.data.images.load(previewImagePath)
            pimageWidth = bpy.data.images[imageName].size[0]
            pimageHeight = bpy.data.images[imageName].size[1]
            
        if pimage_op == True and context.scene.pimage_img_dim == True:
            bpy.context.scene.render.resolution_x = pimageWidth
            bpy.context.scene.render.resolution_y = pimageHeight
        
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        nodes=bpy.context.scene.node_tree.nodes

        for node in tree.nodes:
            tree.nodes.remove(node)	
        
        rlayers_node = tree.nodes.new(type='CompositorNodeRLayers')
        rlayers_node.location = -250,0
        
        group = tree.nodes.new("CompositorNodeGroup")
        group.node_tree = bpy.data.node_groups['EasyModelCompositor']
        group.location = 0,0
        
        if pimage_op == True:
            pimage = tree.nodes.new("CompositorNodeImage")
            pimage.location = -250,-350
            pimage.image = bpy.data.images[imageName]
        
        output_node = tree.nodes.new(type='CompositorNodeComposite')
        output_node.location = 250,0
        
        links = tree.links
        link = links.new(rlayers_node.outputs[0], group.inputs[0])
        link = links.new(rlayers_node.outputs[1], group.inputs[1])
        link = links.new(rlayers_node.outputs["AO"], group.inputs[4])
        link = links.new(rlayers_node.outputs["IndexOB"], group.inputs[2])
        link = links.new(rlayers_node.outputs["Diffuse Direct"], group.inputs[3])
        link = links.new(rlayers_node.outputs["Glossy Indirect"], group.inputs[5])
        if pimage_op == True:
            link = links.new(pimage.outputs[0], group.inputs[7])
        link = links.new(group.outputs[0], output_node.inputs[0])

        return {'FINISHED'}

################
# Import Titan #
################
class ImportTitan(bpy.types.Operator):
    """Import the Titan model"""
    bl_idname = "scene.add_titan_model"
    bl_label = "Import Titan Model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon_dir = bpy.utils.user_resource('SCRIPTS', "addons")
        blendfile = addon_dir + "/easy_model_compositing/node.blend"
        selection = "\\Object\\"
        objectName = "Titan"

        filepath = blendfile + selection + objectName
        directory = blendfile + selection
        filename = objectName

        titanModel = bpy.ops.wm.append(filepath=filepath, filename=filename, directory=directory)

        return {'FINISHED'}

###################
# Import PBR Node #
###################
class ImportPBR(bpy.types.Operator):
    """Import the pbr node"""
    bl_idname = "scene.add_pbr_node"
    bl_label = "Import PBR Node"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon_dir = bpy.utils.user_resource('SCRIPTS', "addons")
        blendfile = addon_dir + "/easy_model_compositing/node.blend"
        selection = "\\NodeTree\\"
        ngroup = "SubstancePBR"
        
        filepath = blendfile + selection + ngroup
        directory = blendfile + selection
        filename = ngroup

        pbrNode = bpy.ops.wm.append(filepath=filepath, filename=filename, directory=directory)
        
        materials = bpy.context.active_object.data.materials
        nMat = len(materials)
        isEmpty = not materials
        if isEmpty:
            bpy.data.materials.new("Substance PBR Material")
            mat = bpy.data.materials.get("Substance PBR Material")
            bpy.context.active_object.data.materials.append(mat)
        
        activeMat = bpy.context.active_object.active_material

        activeMat.use_nodes = True
        nodes = activeMat.node_tree.nodes

        group = nodes.new("ShaderNodeGroup")
        group.node_tree = bpy.data.node_groups['SubstancePBR']
        group.location = 0,0

        return {'FINISHED'}

class ECSRenderPanel(bpy.types.Panel):
    """Creates a Panel in the render tab of the properties editor"""
    bl_label = "Easy Model Compositing"
    bl_idname = "RENDER_PT_ecs"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        
        if bpy.context.scene.render.engine == 'BLENDER_RENDER':
            row = layout.row()
            row.label("Please Enable Cycles To Use This Addon", icon="ERROR")
        else:
            row = layout.row()
            row.operator("render.ecs_setup_subjects", icon='ZOOMIN')

            row = layout.row()
            row.operator("render.ecs_setup_shadow_catchers", icon='ZOOMIN')
            
            row = layout.row()
            row.separator()
            
            row = layout.row()
            row.prop(context.scene, 'use_pimage')
            
            if context.scene.use_pimage == True:
                row.prop(context.scene, 'pimage_img_dim')
                row = layout.row()
                row.prop(context.scene, 'backgroundFilePath')

            row = layout.row()
            row.scale_y = 1.2
            row.operator("render.ecs_set_render_settings", icon='RENDER_STILL')
            
            row = layout.row()
            row.separator()

            row = layout.row()
            row.label("Extras:", icon='FILE_TICK')
            
            row = layout.row()
            row.operator("scene.add_titan_model", icon='APPEND_BLEND')

            row = layout.row()
            row.operator("scene.add_pbr_node", icon='APPEND_BLEND')

################
# Registration #
################
def register():
    bpy.types.Scene.use_pimage = bpy.props.BoolProperty(
        name="Use Preview Background",
        description="Use the preview image option",
        default=False,
    )
    
    bpy.types.Scene.pimage_img_dim = bpy.props.BoolProperty(
        name="Use Image Dimensions",
        description="Use the preview image dimensions as the render dimensions",
        default=False,
    )
    
    bpy.types.Scene.backgroundFilePath = bpy.props.StringProperty \
      (
      name = "Select The Background Preview Image",
      default = "",
      description = "Define the image file",
      subtype = 'FILE_PATH'
      )

    bpy.utils.register_class(ECS_Setup_Subjects)
    bpy.utils.register_class(ECS_Setup_Shadow_Catchers)
    bpy.utils.register_class(ECS_Set_Render_Settings)
    bpy.utils.register_class(ImportTitan)
    bpy.utils.register_class(ImportPBR)
    bpy.utils.register_class(ECSRenderPanel)

def unregister():
    bpy.utils.unregister_class(ECS_Setup_Subjects)
    bpy.utils.unregister_class(ECS_Setup_Shadow_Catchers)
    bpy.utils.unregister_class(ECS_Set_Render_Settings)
    bpy.utils.unregister_class(ImportTitan)
    bpy.utils.unregister_class(ImportPBR)
    bpy.utils.unregister_class(ECSRenderPanel)

if __name__ == "__main__":
    register()
