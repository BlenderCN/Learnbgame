bl_info = \
{
    "name" : "Diffuse Color to Image Palette",
    "author" : "Bronson Zgeb <bronson.zgeb@gmail.com>",
    "version" : (1, 0, 0),
    "blender" : (2, 6, 9),
    "location" : "",
    "description" : "",
    "warning" : "",
    "wiki_url" : "",
    "tracker_url" : "",
    "category" : "3D View"
}

import bpy
import math
import bmesh

def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

def hex_to_rgb(rgb_str):
    int_tuple = struct.unpack('BBB', bytes.fromhex(rgb_str))
    return tuple([val/255 for val in int_tuple]) 

class MakeImagePalette(bpy.types.Operator):
    bl_idname = "mesh.make_imagepalette"
    bl_label = "Convert From Diffuse to Image Palette Colors"


    def execute(self, context):
        image_size = 512
        # Build the color map
        color_map = {}
        for obj in bpy.data.objects:
            if not obj.active_material is None:
                if obj.type == 'MESH':
                    if obj.active_material.active_texture is None:
                        color_value = obj.active_material.diffuse_color
                        hex_value = rgb_to_hex( (int(color_value[0] * 255), int(color_value[1] * 255), int(color_value[2] * 255)) )
                        if not hex_value in color_map:
                            color_map[hex_value] = []
                        color_map[hex_value].append(obj)

        # print( color_map )

        # Decide on UV coords for each color
        image_map = {}
        tile_size = 32
        current_x = 0
        current_y = 0
        for hex_color in color_map:
            # print( hex_color )
            if not hex_color in image_map:
                image_map[hex_color] = []

            image_map[hex_color] = ( int(current_x % image_size), int(current_y) )
            current_x += tile_size
            current_y = tile_size * math.floor((current_x / image_size))


        # UV map each face
        scene = bpy.context.scene

        for hex_color in color_map:
            mesh_objs = color_map[hex_color]
            for mesh_obj in mesh_objs:
                scene.objects.active = mesh_obj
                bpy.ops.object.mode_set(mode='EDIT')

                mesh_data = mesh_obj.data
                bm = bmesh.from_edit_mesh(mesh_data)
                uv_layer = bm.loops.layers.uv.verify()
                bm.faces.layers.tex.verify()
                for f in bm.faces:
                    for l in f.loops:
                        luv = l[uv_layer]
                        # apply the location of the color in the palette as the UV
                        luv.uv = ( (image_map[hex_color][0] + (tile_size / 2)) / image_size, (image_map[hex_color][1] + (tile_size / 2)) / image_size )
                        print( "{} {}".format(mesh_obj, luv.uv) )

                bmesh.update_edit_mesh(mesh_data)
                bpy.ops.object.mode_set(mode='OBJECT')




                # for poly in mesh_data.polygons:
                #     # print("Polygon index: %d, length: %d" % (poly.index, poly.loop_total))
                #     for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                #         # print("    Vertex: %d" % mesh_data.loops[loop_index].vertex_index)
                #         if len(mesh_data.uv_layers) < loop_index + 1:
                #             mesh_data.uv_textures.new("palette")

                #         print("UV: %r" % mesh_data.uv_layers[loop_index].data[0].uv)


        # Create image in memory
        image = bpy.data.images.new("Palette", image_size, image_size)

        # Assign pixels based on UV coords
        pixels = [(1.0,1.0,1.0,1.0)] * image_size * image_size
        for hex_color in image_map:
            diffuse_color = color_map[hex_color][0].active_material.diffuse_color
            rgb_color = ( diffuse_color[0], diffuse_color[1], diffuse_color[2], 1.0 )
            # print( "{} {} {} {}".format(rgb_color[0], rgb_color[1], rgb_color[2], rgb_color[3]) )
            x = image_map[hex_color][0]
            y = image_map[hex_color][1]

            for i in range(0,tile_size):
                for j in range(0,tile_size):
                    pixels[ ((y+j) * image_size) + (x + i) ]  = rgb_color

        # Flatten list
        pixels = [chan for px in pixels for chan in px]

        image.pixels = pixels

        # Write to disk
        image.filepath_raw = "/tmp/palette.png"
        image.file_format = 'PNG'
        image.save()





        # for obj in bpy.data.objects:
        #     if not obj.active_material is None:
        #         if obj.type == 'MESH':
        #             if not obj.active_material.active_texture is None:
        #                 obj.active_material.diffuse_color = [1,1,1]

        #             color = obj.active_material.diffuse_color



        #             mesh = obj.data

        #             if not mesh.vertex_colors:
        #                 mesh.vertex_colors.new()

        #             color_layer = mesh.vertex_colors[0]

        #             i = 0
        #             for poly in mesh.polygons:
        #                 for idx in poly.loop_indices:
        #                     color_layer.data[i].color = color
        #                     i += 1
        return {"FINISHED"}



def register():
    bpy.utils.register_class(MakeImagePalette)

def unregister():
    bpy.utils.unregister_class(MakeImagePalette)

if __name__ == "__main__":
    register()
