import bpy
from mathutils import Vector
from mathutils.geometry import intersect_line_line_2d
import math


class TextureData:
    def __init__(self, img_name, texture_object, bounds_px, bounds_rel, width, height):
        self.img_name = img_name
        self.texture_object = texture_object
        self.bounds_px = bounds_px
        self.bounds_rel = bounds_rel
        self.width = width
        self.height = height


class TextureSlot:
    def __init__(self, x, y, texture_data):
        self.x = x
        self.y = y
        self.texture_data = texture_data


class TextureAtlas:
    def __init__(self, name, width, height, max_width, max_height, margin=1, square=True, output_scale=1.0):
        self.name = name
        self.width = width
        self.height = height
        self.max_width = max_width
        self.max_height = max_height
        self.margin = margin
        self.square = square
        self.texture_slots = []
        self.create_new_slot(self.margin, self.margin)
        self.output_scale = output_scale

    def create_new_slot(self, x, y):
        texture_slot = TextureSlot(x, y, None)
        self.texture_slots.append(texture_slot)
        self.texture_slots = sorted(self.texture_slots, key=lambda slot: slot.x, reverse=True)
        self.texture_slots = sorted(self.texture_slots, key=lambda slot: slot.y, reverse=False)
        return texture_slot

    def cleanup_slots(self):
        del self.texture_slots[:]
        self.create_new_slot(self.margin, self.margin)


class TextureAtlasGenerator:
    @staticmethod
    def get_texture_bounds(obj, output_scale):
        uvs = obj.data.uv_layers[0].data
        textures = obj.data.uv_textures[0].data

        texture = None
        for mat_slot in obj.material_slots:
            if mat_slot.material != None:
                material = mat_slot.material
                for tex_slot in material.texture_slots:
                    if tex_slot.texture != None:
                        texture = tex_slot.texture
                        break
                if texture != None:
                    break
        if texture != None:
            img_size = texture.image.size
            bottom_left_x = 1.0
            bottom_left_y = 1.0
            top_right_x = 0.0
            top_right_y = 0.0
            for uv in uvs:
                bottom_left_x = min(bottom_left_x, uv.uv[0])
                bottom_left_y = min(bottom_left_y, uv.uv[1])
                top_right_x = max(top_right_x, uv.uv[0])
                top_right_y = max(top_right_y, uv.uv[1])

            bounds_rel = [bottom_left_x, bottom_left_y, top_right_x, top_right_y]
            bounds_px = [img_size[0] * bottom_left_x, img_size[1] * bottom_left_y, img_size[0] * top_right_x,
                         img_size[1] * top_right_y]

            for i, value in enumerate(bounds_px):
                bounds_px[i] = int(bounds_px[i] * output_scale)
            width = abs((bounds_px[2] - bounds_px[0]))
            height = abs((bounds_px[3] - bounds_px[1]))
            texture_data = TextureData(texture.image.name, obj, bounds_px, bounds_rel, width, height)
            return texture_data
        return None

    @staticmethod
    def get_sorted_texture_data(objs, output_scale):
        texture_data_list = []
        for obj in objs:
            if obj.type == "MESH":
                texture_data = TextureAtlasGenerator.get_texture_bounds(obj, output_scale)
                if texture_data != None:
                    texture_data_list.append(texture_data)
        texture_data_list = sorted(texture_data_list,
                                   key=lambda x: x.width * x.height + math.pow(x.width, 1) + math.pow(x.height, 1),
                                   reverse=True)
        return texture_data_list

    @staticmethod
    def texture_intersects_others(texture_data, texture_slot, atlas_data):
        tex_fits_width = texture_slot.x + (texture_data.width + atlas_data.margin) < atlas_data.width
        tex_fits_height = texture_slot.y + (texture_data.height + atlas_data.margin) < atlas_data.height
        if tex_fits_width == False or tex_fits_height == False:
            return True
        for slot in atlas_data.texture_slots:
            if slot.texture_data != None and slot != texture_slot:

                r1 = []
                r1.append(texture_slot.x)
                r1.append(texture_slot.y)
                r1.append(texture_slot.x + texture_data.width)
                r1.append(texture_slot.y + texture_data.height)
                r2 = []
                r2.append(slot.x)
                r2.append(slot.y)
                r2.append(slot.x + slot.texture_data.width)
                r2.append(slot.y + slot.texture_data.height)

                points_a = []
                points_a.append(Vector((r1[0], r1[1])))
                points_a.append(Vector((r1[2], r1[1])))
                points_a.append(Vector((r1[2], r1[3])))
                points_a.append(Vector((r1[0], r1[3])))
                lines_a = [[points_a[0], points_a[1]], [points_a[1], points_a[2]], [points_a[2], points_a[3]],
                           [points_a[3], points_a[0]]]

                points_b = []
                points_b.append(Vector((r2[0], r2[1])))
                points_b.append(Vector((r2[2], r2[1])))
                points_b.append(Vector((r2[2], r2[3])))
                points_b.append(Vector((r2[0], r2[3])))
                lines_b = [[points_b[0], points_b[1]], [points_b[1], points_b[2]], [points_b[2], points_b[3]],
                           [points_b[3], points_b[0]]]

                for line_a in lines_a:
                    for line_b in lines_b:
                        i = intersect_line_line_2d(line_a[0], line_a[1], line_b[0], line_b[1])
                        if i != None:
                            return True

        return False

    @staticmethod
    def create_texture_atlas_data(texture_data_list, atlas_name, width, height, max_width, max_height, margin=0,
                                  square=True, output_scale=1.0):
        atlas_data = TextureAtlas(atlas_name, width, height, max_width, max_height, margin, square, output_scale)
        objects = []
        for texture_data in texture_data_list:
            objects.append(texture_data.texture_object)

        restart_generation = True
        decrease_scale = False
        while restart_generation == True:

            if restart_generation == True:
                if decrease_scale:
                    atlas_data.output_scale *= 0.95
                    decrease_scale = False
                texture_data_list = TextureAtlasGenerator.get_sorted_texture_data(objects, atlas_data.output_scale)
                atlas_data.cleanup_slots()
                restart_generation = False

            for i, texture_data in enumerate(texture_data_list):
                if restart_generation:
                    break
                for j, texture_slot in enumerate(atlas_data.texture_slots):
                    if texture_slot.texture_data == None:
                        tex_intersects_other = TextureAtlasGenerator.texture_intersects_others(texture_data,
                                                                                               texture_slot, atlas_data)
                        if tex_intersects_other and j == len(atlas_data.texture_slots) - 1:
                            if atlas_data.width == atlas_data.height and atlas_data.height < atlas_data.max_height:
                                atlas_data.height *= 2
                                if atlas_data.square:
                                    if atlas_data.width < atlas_data.height:
                                        atlas_data.width *= 2
                            elif atlas_data.height > atlas_data.width and atlas_data.width < atlas_data.max_width:
                                atlas_data.width *= 2

                            if atlas_data.width >= atlas_data.max_width and atlas_data.height >= atlas_data.max_height:
                                decrease_scale = True
                                print("Max Atlas size of ", atlas_data.width, "x", atlas_data.height,
                                      " reached. Decreasing texture size and restarting generation.")
                            else:
                                print("Current Atlas size is to small. Increasing to", atlas_data.width, "x", atlas_data.height,
                                      " and restarting generation.")
                            restart_generation = True

                        if restart_generation:
                            break
                        if not tex_intersects_other:
                            texture_slot.texture_data = texture_data
                            x1 = texture_slot.x + texture_data.width
                            y1 = texture_slot.y
                            x2 = texture_slot.x
                            y2 = texture_slot.y + texture_data.height
                            atlas_data.create_new_slot(x1 + margin, y1)
                            atlas_data.create_new_slot(x2, y2 + margin)
                            break

        return atlas_data

    @staticmethod
    def generate_uv_layout(name="texture_atlas", objects=None, width=256, height=256, max_width=2048, max_height=2048,
                           margin=1, texture_bleed=0, square=True, output_scale=1.0):
        context = bpy.context

        ### Extract texture data from given objects. Gives texture width, height and boundaries
        texture_data_list = TextureAtlasGenerator.get_sorted_texture_data(objects, output_scale)


        ### Generates Atlas data which is later used to create uv data
        atlas_data = TextureAtlasGenerator.create_texture_atlas_data(texture_data_list, name, width, height, max_width,
                                                                     max_height, margin, square, output_scale)

        ### create new object with atlas uv layout
        for slot in atlas_data.texture_slots:
            if slot.texture_data != None:

                obj = slot.texture_data.texture_object
                uv_map = obj.data.uv_textures.new(name="COA_UV_ATLAS")
                uv_layer = obj.data.uv_layers["COA_UV_ATLAS"]

                uv_old_width = slot.texture_data.bounds_rel[2] - slot.texture_data.bounds_rel[0]
                uv_old_height = slot.texture_data.bounds_rel[3] - slot.texture_data.bounds_rel[1]
                uv_old_pos = Vector((slot.texture_data.bounds_rel[0], slot.texture_data.bounds_rel[1]))

                uv_new_width = slot.texture_data.width / atlas_data.width
                uv_new_height = slot.texture_data.height / atlas_data.height
                uv_new_pos = Vector((slot.x / atlas_data.width, slot.y / atlas_data.height))

                scale_x = uv_new_width / uv_old_width
                scale_y = uv_new_height / uv_old_height

                uv_flip_y = (1.0 - uv_new_height) - 2 * (uv_new_pos.y)

                for uv_data in uv_layer.data:
                    uv = uv_data.uv
                    uv -= uv_old_pos
                    uv[0] *= scale_x
                    uv[1] *= scale_y
                    uv += uv_new_pos
                    uv_data.uv += Vector((0, uv_flip_y))

        if len(context.selected_objects) > 1:
            bpy.ops.object.join()
        merged_uv_obj = context.active_object
        merged_uv_obj.data.uv_textures.active = merged_uv_obj.data.uv_textures["COA_UV_ATLAS"]
        atlas_img = bpy.data.images.new(atlas_data.name, atlas_data.width, atlas_data.height, alpha=True)
        for vert in merged_uv_obj.data.vertices:
            vert.select = True
            vert.hide = False
        for uv_data in merged_uv_obj.data.uv_textures["COA_UV_ATLAS"].data:
            uv_data.image = atlas_img

        ### bake uv atlas
        context.scene.render.bake_type = "TEXTURE"
        context.scene.render.use_bake_selected_to_active = False
        context.scene.render.use_bake_clear = True
        context.scene.render.bake_margin = texture_bleed
        bpy.ops.object.bake_image()
        return atlas_img, merged_uv_obj, atlas_data


# TextureAtlasGenerator.generate_uv_layout(name="texture_atlas", objects=bpy.context.selected_objects, width=256,height=256, max_width=1024, max_height=1024, margin=1, texture_bleed=0,square=True, output_scale=1.0)