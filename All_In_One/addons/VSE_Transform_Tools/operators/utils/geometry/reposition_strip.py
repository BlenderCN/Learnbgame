import bpy
from .get_strip_box import get_strip_box

def reposition_strip(strip, group_box):
    """
    Reposition a (non-transform) strip.

    After adjusting scene resolution, strip sizes will be
    discombobulated. This function will reset a strip's size and
    position to how it was relative to the group box prior to the
    resolution change.

    Args
        :strip:     A strip (bpy.types.Sequence)
        :group_box: The group bounding box prior to the scene resolution
                    change. (list of int: ie [left, right, bottom, top])
    """
    scene = bpy.context.scene

    min_left, max_right, min_bottom, max_top = group_box

    total_width = max_right - min_left
    total_height = max_top - min_bottom

    res_x = scene.render.resolution_x
    res_y = scene.render.resolution_y

    available_width = res_x - total_width
    available_height = res_y - total_height

    if strip.use_translation:
        strip.transform.offset_x -= min_left
        strip.transform.offset_y -= min_bottom
    
    # While this part works, it makes the strip blurry. Users shouldn't use this technique.
    """
    if strip.type == "META":
        left, right, bottom, top = get_strip_box(strip)
        width = right - left
        height = top - bottom
        
        fac_x = width / res_x
        fac_y = height / res_y
        
        new_crop_left = int(strip.crop.min_x * fac_x)
        new_crop_right = int(strip.crop.max_x * fac_x)
        new_crop_top = int(strip.crop.max_y * fac_y)
        new_crop_bottom = int(strip.crop.min_y * fac_y)
        
        strip.crop.min_x = new_crop_left
        strip.crop.max_x = new_crop_right
        strip.crop.min_y = new_crop_bottom
        strip.crop.max_y = new_crop_top
        
        strip.use_float = True

        bpy.ops.sequencer.select_all(action='DESELECT')
        scene.sequence_editor.active_strip = strip
        bpy.ops.sequencer.effect_strip_add(type="TRANSFORM")

        transform_strip = bpy.context.scene.sequence_editor.active_strip
        transform_strip.name = "[TR]-%s" % strip.name

        transform_strip.blend_type = 'ALPHA_OVER'
        transform_strip.blend_alpha = strip.blend_alpha
        
        strip.mute = True
            
        if strip.use_translation:
            transform_strip.scale_start_x = 1.0
            transform_strip.scale_start_y = 1.0

            offset_x = strip.transform.offset_x
            offset_y = strip.transform.offset_y

            flip_x = 1
            if strip.use_flip_x:
                flip_x = -1

            flip_y = 1
            if strip.use_flip_y:
                flip_y = -1
            
            delta_x = ((width / 2) / fac_x) - (width / 2)
            pos_x = offset_x + (width / 2) - (res_x / 2) + delta_x
            pos_x *= flip_x

            delta_y = ((height / 2) / fac_y) - (height / 2)
            pos_y = offset_y + (height / 2) - (res_y / 2) + delta_y
            pos_y *= flip_y

            if transform_strip.translation_unit == 'PERCENT':
                pos_x = (pos_x / res_x) * 100
                pos_y = (pos_y / res_y) * 100

            transform_strip.translate_start_x = pos_x
            transform_strip.translate_start_y = pos_y

            strip.use_translation = False
    """
    
    if not hasattr(strip, 'elements') and strip.use_crop:
        if strip.crop.min_x < available_width:
            available_width -= strip.crop.min_x
            strip.crop.min_x = 0
        else:
            strip.crop.min_x -= available_width
            available_width = 0

        if strip.crop.min_y < available_height:
            available_height -= strip.crop.min_y
            strip.crop.min_y = 0
        else:
            strip.crop.min_y -= available_height
            available_height = 0

        strip.crop.max_x -= available_width
        strip.crop.max_y -= available_height
