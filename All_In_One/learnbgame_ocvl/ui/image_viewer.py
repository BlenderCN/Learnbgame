import bpy
from bpy.types import Header, Menu
from bpy.types import IMAGE_HT_header as IMAGE_HT_header_old
from bpy.app.translations import pgettext_iface as iface_


from bpy.types import (
    IMAGE_PT_grease_pencil,
    IMAGE_PT_game_properties,
    IMAGE_PT_grease_pencil_palettecolor,
    IMAGE_PT_tools_grease_pencil_brush,
    IMAGE_PT_tools_grease_pencil_edit,
    IMAGE_PT_tools_grease_pencil_brushcurves,
    IMAGE_PT_tools_grease_pencil_sculpt,
    IMAGE_PT_tools_grease_pencil_draw,
    IMAGE_PT_image_properties,
)



class IMAGE_HT_header_new(Header):
    bl_space_type = 'IMAGE_EDITOR'

    def draw(self, context):
        layout = self.layout

        sima = context.space_data
        ima = sima.image
        iuser = sima.image_user

        row = layout.row(align=True)
        row.label(icon='IMAGE_COL')
        # row.template_header()

        # # menus
        if context.area.show_menus:
            sub = row.row(align=True)
            sub.menu("IMAGE_MT_view_new")
            sub.menu("IMAGE_MT_image_new", text="Image")

        layout.template_ID(sima, "image", new="image.new")

        if ima:
            # layers
            layout.template_image_layers(ima, iuser)

            # draw options
            row = layout.row(align=True)
            row.prop(sima, "draw_channels", text="", expand=True)


class IMAGE_MT_view_new(Menu):
    bl_label = "View"

    def draw(self, context):
        layout = self.layout

        layout.operator("image.properties", icon='MENU_PANEL')
        layout.operator("image.toolshelf", icon='MENU_PANEL')
        layout.separator()

        layout.operator("image.view_zoom_in")
        layout.operator("image.view_zoom_out")

        layout.separator()

        ratios = ((1, 8), (1, 4), (1, 2), (1, 1), (2, 1), (4, 1), (8, 1))

        for a, b in ratios:
            layout.operator("image.view_zoom_ratio", text=iface_("Zoom %d:%d") % (a, b), translate=False).ratio = a / b

        layout.separator()


        layout.operator("image.view_all")

        layout.separator()


        layout.operator("screen.area_dupli")


class IMAGE_MT_image_new(Menu):
    bl_label = "Image"

    def draw(self, context):
        layout = self.layout

        sima = context.space_data
        ima = sima.image

        show_render = sima.show_render

        if ima:

            # layout.operator("image.save")
            layout.operator("image.save_as")
            # layout.operator("image.save_as", text="Save a Copy").copy = True
            # layout.operator("image.external_edit_new", "Edit Externally")

            layout.separator()

            layout.menu("IMAGE_MT_image_invert")



classes_to_unregister = [
    IMAGE_PT_grease_pencil,
    IMAGE_PT_game_properties,
    IMAGE_PT_grease_pencil_palettecolor,
    IMAGE_PT_tools_grease_pencil_brush,
    IMAGE_PT_tools_grease_pencil_edit,
    IMAGE_PT_tools_grease_pencil_brushcurves,
    IMAGE_PT_tools_grease_pencil_sculpt,
    # IMAGE_PT_tools_grease_pencil_draw,
    IMAGE_PT_image_properties,

    IMAGE_HT_header_old,
    ]


classes = [
    IMAGE_HT_header_new,
    IMAGE_MT_view_new,
    IMAGE_MT_image_new,
]
