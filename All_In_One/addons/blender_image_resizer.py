# -*- coding: utf-8 -*-

# BismillahirRahmanirRahim

# project_name: 'blender_image_resizer'
# project_web: 'https://github.com/erdinc-me/blender_image_resizer'
# file_web: 'https://github.com/erdinc-me/blender_image_resizer/blob/master/blender_image_resizer.py'
# date: '06/28/16'
# author, maintainer : 'Erdinç Yılmaz'
# author_web: 'http://erdinc.me'
# author_github: 'https://github.com/erdinc-me/'
# email: '@'
# license: 'GPLv3, see LICENSE for more details'
# LICENSE: 'https://github.com/erdinc-me/blender_image_resizer/blob/master/LICENSE'
# copyright: '(C) 2016 Erdinç Yılmaz.'
# version: '1.0 RC'
# status: 'Release Candidate'

bl_info = {
    "name": "Image Resizer",
    "description": "Resize and save your images from blender.",
    "author": "Erdinc Yilmaz",
    "version": (1, 0, 0),
    "blender": (2, 70, 0),
    "location": "Node Editor > Tool Shelf (T)",
    "warning": "If python module Pillow(PIL) is not installed this addon will not work!",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

import os.path
import bpy
# from numpy import interp

from bl_operators.presets import AddPresetBase

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       EnumProperty,
                       )

try:
    from PIL import Image

    is_pil_imported = True

    # ---------------------------------------------------------------------
    def resize_image_with_pil(context, src_img_path, remained):

        # src_img_path = context.active_node.image.filepath
        img_resizer = context.scene.ImageResizer

        # src_image = context.active_node.image

        wm = context.window_manager
        wm.progress_begin(0, remained)
        wm.progress_update(remained)
        # img_resizer.progress = "Please wait !"

        if img_resizer.is_custom_save_path:
            save_dir = img_resizer.custom_save_path
        else:
            save_dir = os.path.dirname(src_img_path)

        img_format = img_resizer.image_format_menu
        if img_format == "TARGA":
            img_format = "tga"
        ext_dict = {"JPEG": "jpg",
                    "TIFF": "tif",
                    "PNG": "png",
                    "tga": "tga"}
        ext = ext_dict[img_format]

        # img_format = img_resizer.image_format_menu

        # TODO: implement 16 bit tiff + png for pil
        # !!! for now, it is not possible because of pil. it does not support saving 16 bit files
        #  hopefully in the future..
        # if img_format in ["png", "tiff"]:
        #     depth = img_resizer.depth_menu
        # else:
        #     depth = "8"

        jpg_quality = img_resizer.jpg_quality
        png_compression = img_resizer.png_compression_pil

        is_create_texture_node = img_resizer.is_create_texture_node
        is_unlink = img_resizer.is_unlink

        res_x = img_resizer.res_x
        res_y = img_resizer.res_y

        # print(sys.getsizeof(gl))

        active_node = bpy.context.active_node
        height = active_node.dimensions[1]

        bpy.context.scene.ImageResizer.locationX = active_node.location[0]
        bpy.context.scene.ImageResizer.locationY = active_node.location[1] - height - 15

        img = Image.open(src_img_path, 'r')
        # mode = img.mode
        # aa = None
        # if mode == "RGB":
        #     rr, gg, bb = img.split()
        # elif mode == "RGBA":
        #     rr, gg, bb, aa = img.split()
        # else:
        #     return

        basename_without_extension = os.path.splitext(os.path.basename(src_img_path))[0]

        # PIL.Image.NEAREST,
        # PIL.Image.BILINEAR,
        # PIL.Image.BICUBIC,
        # PIL.Image.LANCZOS. It defaults to PIL.Image.BICUBIC.
        if img_resizer.is_keep_aspect_ratio:
            img.thumbnail(size=(res_x, res_y), resample=Image.LANCZOS)
            newfilename = "{}_{}x{}.{}".format(basename_without_extension, img.size[0], img.size[1], ext)
        else:
            img = img.resize(size=(res_x, res_y), resample=Image.LANCZOS)
            newfilename = "{}_{}x{}.{}".format(basename_without_extension, res_x, res_y, ext)

        new_img_path = os.path.join(save_dir, newfilename)

        if img_format == "JPEG":
            img.save(new_img_path, img_format, quality=jpg_quality)
        elif img_format == "PNG":
            img.save(new_img_path, img_format, compress_level=png_compression)
        # elif img_format== "TIFF":
        #     img.mode = 'I'
        #     img.point(lambda i: i * (1. / 256)).convert('L').save(new_img_path, img_format)
        else:
            img.save(new_img_path, img_format)

        if not is_unlink:
            load_image_and_create_node(context, new_img_path, is_create_texture_node)

        # TODO: do we need close ?
        # "This function is only required to close images
        # that have not had their file read and closed by the load() method."
        img.close()
        del img
        remained -= 1
        wm.progress_update(remained)

        wm.progress_end()
        # context.scene.ImageResizer.progress = "All Done!"

except ImportError:
    is_pil_imported = False


# ---------------------------------------------------------------------
def load_image_and_create_node(context, bw_img_path, is_create_texture_node):
    # img.file_format = img_format

    # img = bpy.data.images.load(bw_img_path, check_existing=True)
    # check_existing=True implemented in 2, 76, 1 version of blender. To support older versions we will not use it.
    # instead;
    img = None
    for i in bpy.data.images:
        if i.filepath_raw == bw_img_path:
            i.reload()
            img = i
            # return
            break
    if not img:
        img = bpy.data.images.load(bw_img_path)

    if is_create_texture_node:

        tree_type = context.space_data.tree_type
        # node_tree = context.scene.node_tree
        # node_tree = context.space_data.node_tree
        nodes = context.space_data.node_tree.nodes

        for n in nodes:
            if n.label == img.name:
                return

        if tree_type == 'ShaderNodeTree':
            # # active_node = bpy.context.active_node
            # mat = bpy.context.object.active_material
            # # get the nodes
            # nodes = mat.node_tree.nodes
            node_texture = nodes.new(type='ShaderNodeTexImage')

        if tree_type == 'CompositorNodeTree':
            node_texture = nodes.new(type='CompositorNodeImage')

        if tree_type == 'TextureNodeTree':
            node_texture = nodes.new(type='TextureNodeImage')

        # node_texture = nodes.new(type='ShaderNodeTexImage')
        node_texture.image = img
        node_texture.name = "Image Texture"
        node_texture.label = img.name
        # node_texture.color_space = "NONE"
        # node_texture.location = active_node.location[0], active_node.location[1] - active_node.bl_height_min
        node_texture.hide = True
        node_texture.select = False
        node_texture.location = bpy.context.scene.ImageResizer.locationX, \
                                bpy.context.scene.ImageResizer.locationY

        bpy.context.scene.ImageResizer.locationY -= 40
        node_texture.width_hidden = bpy.context.active_node.width
        # node_texture.select = True
        # nodes.active = node_texture


# ---------------------------------------------------------------------
# storing properties in the active scene
########################################################################
class ImageResizerPanelSettings(PropertyGroup):
    locationX = IntProperty(
        name="locationX",
        default=0
    )

    locationY = IntProperty(
        name="locationY",
        default=0
    )

    res_x = IntProperty(
        name="locationY",
        default=1024,
        subtype="PIXEL"
    )

    res_y = IntProperty(
        name="locationY",
        default=1024,
        subtype="PIXEL"
    )

    is_keep_aspect_ratio = BoolProperty(
        name="Keep Aspect Ratio",
        description="Keeps aspect ratio if selected.",
        default=True
    )

    is_create_texture_node = BoolProperty(
        name="Create Texture Node",
        description="Check this to create texture nodes loaded with newly created images.",
        default=True
    )

    # is_unload_original = BoolProperty(
    #     name="Unlink",
    #     description="Check this to unlink separated channel images from blender after creating and saving them.",
    #     default=False
    # )

    is_unlink = BoolProperty(
        name="Unlink",
        description="Check this to unlink separated channel images from blender after creating and saving them.",
        default=False
    )

    image_formats = [('TIFF', 'tif', '', 1),
                     ('TARGA', 'tga', '', 2),
                     ('PNG', 'png', '', 3),
                     ('JPEG', 'jpg', '', 4),
                     ]

    image_format_menu = bpy.props.EnumProperty(
        items=image_formats,
        name="Format",
        description="image format to save: ",
        default="JPEG",
        # update=update_func
    )

    # For now pil does not support 16 bit file saving.
    # depth_menu = bpy.props.EnumProperty(
    #     items=[('8', '8', '', 1), ('16', '16', '', 2)],
    #     name="Depth",
    #     description="Channel depth: ",
    #     default="8",
    # )

    # png_compression_blender = bpy.props.IntProperty(
    #     name="Compression",
    #     description="Amount of time to determine best compression:"
    #                 " 0 = no compression with fast file output, "
    #                 "100 = maximum lossless compression with slow file output.",
    #     default=15,
    #     subtype="PERCENTAGE",
    #     min=0, max=100)

    # pil uses 0-9 range, blender uses 0-100 range for png compression.
    # we can remap ranges with this
    # png_compression = int(interp(ics.png_compression_blender, [1, 100], [1, 9]))
    # but user will not know that there is no difference between forex. 100 and 90.
    # so png_compression_pil is created.

    png_compression_pil = bpy.props.IntProperty(
        name="Compression",
        description="ZLIB compression level, a number between 0 and 9: 1 gives best speed,"
                    " 9 gives best compression, 0 gives no compression at all. Default is 6.",
        default=6,
        min=0, max=9)

    jpg_quality = bpy.props.IntProperty(
        name="Quality",
        description="Quality for image formats that supports lossy compression.",
        default=90,
        subtype="PERCENTAGE",
        min=0, max=100)

    is_custom_save_path = BoolProperty(
        name="",
        description="Check this to set custom save path",
        default=False
    )

    custom_save_path = StringProperty(
        name="",
        description="Choose a directory:",
        default=os.path.expanduser("~"),
        maxlen=1024,
        subtype='DIR_PATH')

    # progress = StringProperty(
    #     name="",
    #     description="progress",
    #     default="",
    #     maxlen=1024,
    # )


########################################################################
class ResizeImageButton(bpy.types.Operator):
    bl_idname = "image_resizer.resize_button"
    bl_label = "Resize and Save"

    # ---------------------------------------------------------------------
    @classmethod
    def poll(cls, context):

        # space = context.space_data
        # return space.type == 'NODE_EDITOR'
        if hasattr(context.active_node.image, "filepath_raw"):
            # if not "Render Result" is selected
            if context.active_node.image.filepath:
                return True

    # ---------------------------------------------------------------------
    def execute(self, context):
        img_resizer = context.scene.ImageResizer

        if img_resizer.is_custom_save_path:
            if not os.path.isdir(img_resizer.custom_save_path):
                msg = 'Custom save path could not be found!: "{}". Please correct the path and retry.'.format(
                    img_resizer.custom_save_path)
                self.report({'WARNING'}, msg)
                return {'FINISHED'}

        src_img_path = context.active_node.image.filepath_raw
        if src_img_path.startswith("//"):
            if not bpy.data.is_saved:
                # if not context.scene.ImageResizer.is_custom_save_path:
                msg = 'To process an image with relative path like this, ' \
                      'you should save the blend file first.\n({})'.format(src_img_path)
                self.report({'WARNING'}, msg)
                return {'FINISHED'}

            src_img_path = bpy.path.abspath(src_img_path)

            # blend_file_path = bpy.data.filepath
            # directory = os.path.dirname(blend_file_path)
            # img_path = os.path.normpath(os.path.join(directory, img_path))

        if not os.path.exists(src_img_path):
            msg = 'Could not find file: {}'.format(src_img_path)
            self.report({'WARNING'}, msg)
            return {'FINISHED'}

        # to prevent possible "/../../" relative path issue..
        src_img_path = os.path.abspath(src_img_path)

        remained = 1

        resize_image_with_pil(context, src_img_path, remained)

        # return {'RUNNING_MODAL'}
        return {'FINISHED'}


# ---------------------------------------------------------------------
# PANEL
########################################################################
class ImageResizerPanel(Panel):
    # bl_idname = "ImageResizerPanel"
    # bl_idname = "NODE_PT_image_resizer_panel"
    bl_label = "Image Resizer"
    bl_category = "Image"
    # bl_category = "img_resizer"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'TOOLS'

    # bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'CYCLES'
        # tree_type = context.space_data.tree_type
        # if tree_type == 'ShaderNodeTree' and context.scene.render.engine == 'CYCLES':
        #     return True

    # ---------------------------------------------------------------------
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        img_resizer = scene.ImageResizer

        box = layout.box()

        if is_pil_imported:
            # if context.active_node and context.active_node.bl_idname
            #     in ["ShaderNodeTexEnvironment", "ShaderNodeTexImage"]:
            if context.active_node \
                    and hasattr(context.active_node, 'image') \
                    and hasattr(context.active_node.image, "filepath_raw"):
                # if is_pil_imported:
                #     img = Image.open(context.active_node.image.filepath_raw, 'r')
                #     if img.mode == "RGBA":
                #         draw_alpha = True
                #     img.close()

                # row = box.row()

                col = box.column_flow(align=True)
                # col.label('Image Resizer Presets:')
                row = col.row(align=True)
                row.menu("IMAGE_RESIZER_MT_presets_menu",
                         text=bpy.types.IMAGE_RESIZER_MT_presets_menu.bl_label)
                row.operator("image_resizer.image_resize_preset_add", text="", icon='ZOOMIN')
                row.operator("image_resizer.image_resize_preset_add", text="", icon='ZOOMOUT').remove_active = True

                row = box.row()
                row.prop(img_resizer, "res_x", text="X")
                row = box.row()
                row.prop(img_resizer, "res_y", text="Y")

                row = box.row()
                row.prop(img_resizer, "is_keep_aspect_ratio")

                row = box.row()
                row.prop(img_resizer, "is_create_texture_node", text="Create Texture Node")
                if img_resizer.is_unlink:
                    row.enabled = False

                row = box.row()
                row.prop(img_resizer, "is_unlink", text="Unlink After Save")
                if img_resizer.is_create_texture_node:
                    row.enabled = False
                row = box.row()
                # rowCustomPath.prop(img_resizer, "is_custom_save_path", text="")
                # img_resizer.custom_save_path = context.active_node.image.filepath
                row.prop(img_resizer, "is_custom_save_path", text="Custom Save Directory")
                if img_resizer.is_custom_save_path:
                    row = box.row()
                    row.prop(img_resizer, "custom_save_path")
                row = box.row()
                row.prop(img_resizer, "image_format_menu")

                # For now pil does not support 16 bit file saving.
                # if img_resizer.image_format_menu in ["PNG", "TIFF"]:
                #     row = box.row()
                #     row.prop(img_resizer, "depth_menu", expand=True)

                if img_resizer.image_format_menu == "PNG":
                    row = box.row()
                    row.prop(img_resizer, 'png_compression_pil', slider=True)

                elif img_resizer.image_format_menu == "JPEG":
                    row = box.row()
                    row.prop(img_resizer, 'jpg_quality', slider=True)

                row = box.row()
                row.operator("image_resizer.resize_button", text="Resize And Save", icon="RENDER_STILL")
                # row = box.row()
                # row.prop(img_resizer, "progress")

            else:
                row = box.row()
                row.label(text='Please select an image node with a loaded image', icon='IMAGE_RGB')
        else:
            row = box.row()
            row.label(text='Python module Pillow(PIL) could not be found! Please install it and retry.',
                      icon='ERROR')


########################################################################
class ImageResizerPresetAdd(AddPresetBase, bpy.types.Operator):
    """Add a new render preset."""
    bl_idname = 'image_resizer.image_resize_preset_add'
    bl_label = 'Add Image Resizer Preset'
    bl_options = {'REGISTER', 'UNDO'}
    preset_menu = 'IMAGE_RESIZER_MT_presets_menu'
    preset_subdir = 'image_resizer_presets'

    preset_defines = [
        "img_resizer = bpy.context.scene.ImageResizer"
        ]

    preset_values = [
        "img_resizer.res_x",
        "img_resizer.res_y",
        ]


########################################################################
class ImageResizerPresetsMenu(bpy.types.Menu):
    """Presets for render settings."""
    # bl_idname = "image_resizer.presets_menu"
    bl_idname = "IMAGE_RESIZER_MT_presets_menu"
    bl_label = "Presets"
    preset_subdir = "image_resizer_presets"
    preset_operator = "script.execute_preset"

    draw = bpy.types.Menu.draw_preset


# ------------------------------------------------------------------------
# register and unregister functions
# ---------------------------------------------------------------------
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.ImageResizer = PointerProperty(type=ImageResizerPanelSettings)


# ---------------------------------------------------------------------
def unregister():
    del bpy.types.Scene.ImageResizer
    bpy.utils.unregister_module(__name__)


# ---------------------------------------------------------------------
if __name__ == "__main__":
    register()

# register()
