import bpy
from . import selection_sets


def reset_intensity():
    objects_list = selection_sets.meshes_with_materials()
    for obj in objects_list:
        for mat in obj.data.materials:
            mat.diffuse_intensity = 1
    return {'FINISHED'}


def reset_color_value():
    objects_list = selection_sets.meshes_with_materials()
    for obj in objects_list:
        for mat in obj.data.materials:
            mat.diffuse_color = (1, 1, 1)
    return {'FINISHED'}


def reset_spec_value():
    objects_list = selection_sets.meshes_with_materials()
    for obj in objects_list:
        for mat in obj.data.materials:
            mat.specular_color = (0, 0, 0)
            mat.specular_intensity = 1
    return {'FINISHED'}


def reset_alpha_value():
    objects_list = selection_sets.meshes_with_materials()
    for obj in objects_list:
        for mat in obj.data.materials:
            mat.transparency_method = 'Z_TRANSPARENCY'
            mat.alpha = 1
            mat.use_transparency = False
    return {'FINISHED'}


def use_textured_solid(self, context):
    objects_list = selection_sets.meshes_with_materials()
    for obj in objects_list:
        mesh = obj.data
        context.scene.objects.active = obj
        # if in EDIT Mode switch to OBJECT
        if obj.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        for matID in range(len(mesh.materials)):
            mat = mesh.materials[matID]

            # this set active texture for each material face assignation

            for texSlot in range(len(mat.texture_slots)):
                # diffuse mode
                if self.set_texture_type == 0:
                    # check if : there is a texture, if it used diffuse channel, if it use uv coord, if mesh has an uv chan
                    if mat.texture_slots[texSlot] != None \
                            and mat.texture_slots[texSlot].use_map_color_diffuse \
                            and mat.texture_slots[texSlot].texture_coords == "UV" \
                            and len(mesh.uv_textures) > 0 \
                            and obj.data.uv_textures[self.set_texture_type] is not None:
                        # select mesh first UV channel
                        mesh.uv_textures[0].active = True
                        # set active texture as diffuse texture
                        mat.active_texture_index = texSlot
                # lightmap mode
                if self.set_texture_type == 1:
                    if mat.texture_slots[texSlot] != None \
                            and mat.texture_slots[texSlot].use_map_ambient \
                            and mat.texture_slots[texSlot].texture_coords == "UV" \
                            and len(mesh.uv_textures) > 1 \
                            and obj.data.uv_textures[self.set_texture_type] is not None:
                        # select mesh UV2 channel
                        mesh.uv_textures[1].active = True
                        # set active texture as ambient texture
                        mat.active_texture_index = texSlot

            # this set texture face

            if mat.active_texture != None:
                texSlot = mat.active_texture_index
                img = mat.active_texture
                # some check to sync active UVmap and images associate
                if not is_editmode \
                    and img.type == "IMAGE" \
                    and (mat.texture_slots[texSlot].uv_layer == mesh.uv_layers.active.name
                         or mat.texture_slots[texSlot].uv_layer == ""):
                    # assign image according to material assignation
                    for f in mesh.polygons:
                        if f.material_index == matID:
                            uvtex.data[f.index].image = img.image

    return {'FINISHED'}


if __name__ == "__main__":
    reset_intensity()
    reset_color_value()
