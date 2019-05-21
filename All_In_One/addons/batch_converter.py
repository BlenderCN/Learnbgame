# Author: Tamir Lousky

# Changes:
# V0.002: Added ability to keep source resolution, fixed bug that causes
#         cropping when using a render percentage under 100%.

# Known issues:
# 1. When images are packed into the blendfile and the file was saved, the
#    script cannot load images and only packed images will be converted and saved.

bl_info = {
    "name"        : "Batch Converter",
    "author"      : "Tamir Lousky",
    "blender"     : (2, 74, 0),
    "version"     : (0, 0, 0, 2),
    "location"    : "3D View > Toolbox",
    "description" : "Batch convert image file formats",
    "category"    : "Convert"
}

import bpy
from os import listdir
from os.path import join, isdir, isfile

class batch_convert(bpy.types.Operator):
    bl_idname      = "render.batch_convert"
    bl_label       = "Batch Convert"
    bl_description = "Batch convert source images to destination format"
    bl_options     = {'REGISTER', 'UNDO'}

    @classmethod
    def poll( self, context ):
        ''' Make sure both source and destination folders are valid '''
        props = context.scene.batch_convertor_properties
        sourceDirValid      = isdir( props.source_folder )
        destinationDirValid = isdir( props.destination_folder )
        return sourceDirValid and destinationDirValid

    def execute(self, context):
        C = bpy.context
        S = C.scene
        props = context.scene.batch_convertor_properties

        S.use_nodes = True
        t = S.node_tree

        # Clear node tree
        for n in t.nodes:
            t.nodes.remove( n )

        # Generate nodes
        for ntype in [
            'CompositorNodeImage',
            'CompositorNodeComposite',
            'CompositorNodeScale'
        ]:
            t.nodes.new( ntype )

        out     = t.nodes['Composite']
        scale   = t.nodes['Scale']
        imgNode = t.nodes['Image']

        # Connect nodes
        t.links.new( out.inputs[0],   scale.outputs[0]   )
        t.links.new( scale.inputs[0], imgNode.outputs[0] )

        source     = props.source_folder
        sourceImgs = [
            f for f in listdir( source ) if isfile( join( source, f ) )
        ]

        bpy.ops.image.open(
            filepath      = join( source, sourceImgs[0] ),
            directory     = source,
            files         = [ { 'name' : sourceImgs[0] } ],
            relative_path = False
        )

        img           = bpy.data.images[ sourceImgs[0] ]
        imgNode.image = img

        extension   = S.render.file_extension
        destination = props.destination_folder

        if not props.keepOriginalRes:
            p = S.render.resolution_percentage / 100
            for axis in ['X','Y']:
                scale.inputs[ axis ].default_value = p

        for f in sourceImgs:
            newname           = props.prefix + f[:-4] + props.suffix + extension
            img.filepath      = join( source, f )
            S.render.filepath = join( destination, newname )

            if props.keepOriginalRes:
                imgX, imgY = img.size
                S.render.resolution_x          = imgX
                S.render.resolution_y          = imgY
                S.render.resolution_percentage = 100

            bpy.ops.render.render( write_still = True )

        return {'FINISHED'}

class batchConverterPanel(bpy.types.Panel):
    ''' Batch converter '''
    bl_label       = "Batch Converter"
    bl_idname      = "batch_converter"
    bl_category    = "Convert"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout
        col    = layout.column()

        S = context.scene
        P = S.batch_convertor_properties

        b  = col.box()
        bc = b.column()

        bc.label( text = "Warning: pressing 'Batch Convert'" )
        bc.label( text = "will delete your render node setup!" )

        b  = col.box()
        bc = b.column()
        bc.prop( P, "source_folder"      )
        bc.prop( P, "destination_folder" )

        bc.prop( P, "prefix" )
        bc.prop( P, "suffix" )

        bc.prop( P, "keepOriginalRes"    )

        col.operator( 'render.batch_convert' )

class batchConverterProps( bpy.types.PropertyGroup ):
    source_folder = bpy.props.StringProperty(
        description = "Folder of source files",
        name        = "Source folder",
        subtype     = 'FILE_PATH'
    )

    destination_folder = bpy.props.StringProperty(
        description = "Folder of destination files",
        name        = "Destination folder",
        subtype     = 'FILE_PATH'
    )

    keepOriginalRes = bpy.props.BoolProperty(
        description = "Keep original image's resolution",
        name        = "Keep Original Resolution",
        default     = False
    )

    prefix = bpy.props.StringProperty(
        description = "Add a prefix before each filename",
        name        = "Prefix"
    )

    suffix = bpy.props.StringProperty(
        description = "Add a suffix after each filename",
        name        = "Suffix"
    )

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.batch_convertor_properties = bpy.props.PointerProperty(
        type = batchConverterProps
    )

def unregister():
    bpy.utils.unregister_module(__name__)