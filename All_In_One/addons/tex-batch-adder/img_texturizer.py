import bpy

# Take image paths and create textures to fill object's material slots
class ImgTexturizer:
    def __init__ (self, texture_names, directory):
        # reference user paths
        self.texture_names = texture_names
        self.dir = directory
        self.material = None    # assign in setup

    def create_img_plane (self, transparent):
        old_area = bpy.context.area.type
        bpy.context.area.type = 'VIEW_3D'
        # add 0th image as plane
        bpy.ops.import_image.to_plane(files=[{'name': self.texture_names[0]}],directory=self.dir)
        # set 0th image's texture properties
        obj = bpy.context.scene.objects.active
        bpy.context.area.type = old_area
        if transparent:
            # set alpha on image
            obj.active_material.active_texture.image.use_alpha = True
            obj.active_material.active_texture.use_preview_alpha = True
            obj.active_material.texture_slots[0].use_map_alpha = True
        obj.active_material.active_texture.extension = 'CLIP'
        # update the reference material
        return obj.active_material

    def setup (self, overwrite_slots, update_existing, use_transparency):
        # track created imgs (array) and number of tex slots filled (counter)
        img_counter = 0
        used_imgs = []

        ## point to object's active material
        if update_existing:
            self.material = bpy.context.scene.objects.active.active_material
        else:
            # create a new img plane and count first img as used
            self.material = self.create_img_plane(use_transparency)
            img_counter += 1

        # add images in material's open texture slots
        for i in range (img_counter, len(self.material.texture_slots)-1):
            # overwrite switches out all texs on a mat - open just checks for empty
            if img_counter < len(self.texture_names) and (overwrite_slots or self.material.texture_slots[i]==None):
                self.fill_tex_slot(i, img_counter, used_imgs, use_transparency)
                # bookkeeping stuff after filling the slot
                used_imgs.append(self.texture_names[img_counter])
                img_counter += 1
            # deactivate all texture slots for this material
            self.material.use_textures[i] = False

        # activate the first texture for this material
        self.material.use_textures[0] = True

        # alpha and transparency for this material
        self.customize_material_params(use_transparency)

        # return uncreated imgs if not all images got turned into texs
        return self.check_if_created_all(img_counter)

    def fill_tex_slot (self, slot_i, img_i, used_imgs_list, transparent):
        # create tex in this slot using the next img
        self.create_texture(slot_i, img_i)
        # load and use imge file for this tex
        self.load_image(img_i, slot_i, used_imgs_list)
        # adjust settings for created tex - assumes it's the active tex
        self.set_texslot_params(self.material.texture_slots[slot_i], transparent)

    def check_if_created_all (self, count_created):
        # verify that all images were loaded into textures
        count_total = len(self.texture_names)
        if count_created >= count_total:
            return {'FINISHED'}
        # return the sublist of uncreated images
        return self.texture_names[count_created:]

    def create_texture (self, empty_slot, img_i):
        # set new location to the next open slot
        self.material.active_texture_index = empty_slot
        # create the new texture in this slot
        created_tex_name = self.strip_img_extension(self.texture_names[img_i])
        created_tex = bpy.data.textures.new (created_tex_name,'IMAGE')
        # update texture slot to hold this texture
        self.material.texture_slots.add()
        self.material.texture_slots[empty_slot].texture = created_tex
        # next step - load image into created tex (separate load method)
        return None

    def build_path (self, filename):
        # concatenate '//directory/path/' and 'filename.ext'
        return self.dir + filename

    def load_image (self, img_index, slot, created_images_list):
        path = self.build_path(self.texture_names[img_index])
        # load image to into blend db
        if self.texture_names[img_index] not in created_images_list:
            bpy.data.images.load(path)
        # point to loaded img
        found_img = bpy.data.images[bpy.data.images.find(self.texture_names[img_index])]
        # use loaded image as this texture's image
        self.material.active_texture.image = found_img

    # output filename string without the file extension (for prettier obj names)
    def strip_img_extension (self, filename):
        short_ext = ['.png','.jpg','.gif','.tif','.bmp','.PNG','.JPG','.GIF','.TIF','.BMP']
        long_ext = ['.jpeg','.JPEG']
        if any(filename.endswith(e) for e in short_ext):
            filename = filename[:-4]
        elif any(filename.endswith(e) for e in long_ext):
            filename = filename[:-5]
        return filename

    # apply settings to the material
    def customize_material_params (self, transparent, custom_settings=True):
        if custom_settings:
            self.material.preview_render_type = 'FLAT'
            self.material.diffuse_intensity = 1.0
            self.material.specular_intensity = 0.0
            self.material.use_transparent_shadows = True
        if transparent:
            self.material.use_transparency = transparent
            self.material.transparency_method = 'Z_TRANSPARENCY'
            self.material.alpha = 0.0
        return None

    # apply settings to each texture created
    def set_texslot_params (self, tex_slot, transparent):
        self.material.active_texture.type = 'IMAGE'
        if transparent:
            tex_slot.use_map_alpha = True
            self.material.active_texture.image.use_alpha = True
            self.material.active_texture.use_preview_alpha = True
        self.material.active_texture.extension = 'CLIP'

def toggle_imgmat_transparency (material):
    # verify that mat, img and tex transparency are aligned
    slot0 = material.texture_slots[0]
    slot1 = material.texture_slots[1]
    tex0 = material.texture_slots[0].texture
    check_align_transp = True
    if material.use_transparency != slot0.use_map_alpha != tex0.use_preview_alpha != tex0.image.use_alpha:
        check_align_transp = False
    if slot1 != None and slot0.texture.image.use_alpha != slot1.texture.image.use_alpha:
        check_align_transp = False
    # if first pass or transparency settings got unaligned, reset to transparent
    if not check_align_transp:
        for slot in material.texture_slots:
            if slot != None and slot.texture.type == 'IMAGE':
                slot.texture.extension = 'CLIP'
                slot.texture.image.use_alpha = True
                slot.texture.use_preview_alpha = True
                slot.use_map_alpha = True
        material.use_transparency = True
        material.transparency_method = 'Z_TRANSPARENCY'
        material.alpha = 0.0
        material.diffuse_intensity = 1.0
        material.specular_intensity = 0.0
        material.use_transparent_shadows = True
        return material
    # toggle transparency for all textures
    for slot in material.texture_slots:
        if slot != None:
            slot.texture.image.use_alpha = not slot.texture.image.use_alpha
            slot.texture.use_preview_alpha = not slot.texture.use_preview_alpha
            slot.use_map_alpha = not slot.use_map_alpha
    # toggle transparency for the material
    material.transparency_method = 'Z_TRANSPARENCY'
    material.alpha = not material.use_transparency
    material.use_transparency = not material.use_transparency
    material.use_transparent_shadows = True
    material.preview_render_type = 'FLAT'
    return material
