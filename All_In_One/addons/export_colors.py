
bl_info = {
    "name": "Export Colors",
    "author": "Sorin Covor",
    "version": (1, 0),
    "blender": (2, 7, 9),
    "location": "File > Export > Export Colors",
    "description": "Exports an image file with all the colors in the scene.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

import bpy

# creates a grid of pixels
def grid(width, height, x, y):
    origList = []
    for i in range(width * height):
        origList.append(i)
    
    splitList = [origList[i : i + width] for i in range(0, len(origList), width)]
  
    return splitList[y][x]

def drawPixel(image, w, h, x, y, R, G, B):
    # multiplied by 4 because of RGBA pattern
    pixelNumber = grid(w, h, x, y) * 4
    
    # iterate through the color channels
    image.pixels[pixelNumber] = R
    image.pixels[pixelNumber + 1] = G
    image.pixels[pixelNumber + 2] = B
    image.pixels[pixelNumber + 3] = 1.0
    
def drawRectangle(image, w, h, size, x1, y1, R, G, B):
    size = int(size)
    for x in range(x1, x1 + size):
        for y in range(y1, y1 + size):
            drawPixel(image, w, h, x, y, R, G, B)

def write_data(context, filepath, size, tiles_x, tiles_y):
    
    tiles_x = int(tiles_x)
    tiles_y = int(tiles_y)
    size = int(size)

    width = tiles_x * size
    height = tiles_y * size

    image = bpy.data.images.new("image", width = width, height = height)
    materials = bpy.data.materials
    index = 0   

    # used for gamma correction
    # gamma = 1 / 2.2 -> WINDOWS
    # gamma = 1 / 1.8 -> MAC
    gamma = 1 / 2.2

    for y in range(0, tiles_y):
        y = y * size
        for x in range(0, tiles_x):
            x = x * size
            if len(materials) > index:
                color = materials[index].diffuse_color
                r = pow(color.r, gamma)
                g = pow(color.g, gamma)
                b = pow(color.b, gamma)
                drawRectangle(image, width, height, size, x, y, r, g, b)
                index = index + 1

    image.filepath_raw = filepath
    image.file_format = 'PNG'
    #image.scale(width, height)
    image.save()

    return {'FINISHED'}

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

class ExportColors(Operator, ExportHelper):
    bl_idname = "object.move_operator"  
    bl_label = "Export Colors" 

    # ExportHelper mixin class uses this
    filename_ext = ".png"

    # tile size
    size = EnumProperty(
            name = "Tile Size",
            description = "Choose the tile size for the colors in the texture.",
            items = (('4', "4px", ""),
                     ('8', "8px", ""),
                     ('16', "16px", ""),
                     ('32', "32px", ""),
                     ('64', "64px", "")),
            default = '4'
        )

    tiles_x = EnumProperty(
            name = "Tiles X",
            description = "Choose the number of tiles.",
            items = (('2', "2 tiles", ""),
                     ('3', "3 tiles", ""),
                     ('4', "4 tiles", ""),
                     ('5', "5 tiles", ""),
                     ('6', "6 tiles", ""),
                     ('7', "7 tiles", ""),
                     ('8', "8 tiles", "")),
            default = '4'
        )

    tiles_y = EnumProperty(
        name = "Tiles Y",
        description = "Choose the number of tiles.",
        items = (('2', "2 tiles", ""),
                 ('3', "3 tiles", ""),
                 ('4', "4 tiles", ""),
                 ('5', "5 tiles", ""),
                 ('6', "6 tiles", ""),
                 ('7', "7 tiles", ""),
                 ('8', "8 tiles", "")),
        default = '4'
    )

    def execute(self, context):
        return write_data(context, self.filepath, self.size, self.tiles_x, self.tiles_y)

def add_object_button(self, context):
    self.layout.operator(ExportColors.bl_idname, text = "Export Colors", icon = "COLORSET_02_VEC")

def register():  
    bpy.utils.register_class(ExportColors)
    bpy.types.INFO_MT_file_export.prepend(add_object_button)
    # prepend -> adds at the top of the menu
    # append -> adds at the bottom of the menu

def unregister():
    bpy.utils.unregister_class(ExportColors)
    bpy.types.INFO_MT_file_export.remove(add_object_button)

if __name__ == "__main__":  
    register()
