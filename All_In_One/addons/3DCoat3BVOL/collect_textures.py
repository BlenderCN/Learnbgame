# Collect textures from selected objects and add it to active object.
# Exec "Collect Texture" from space key's menu.

import sys
import bpy

def collect_textures(context):
#    ignorecp = (
#        '__doc__',
#        '__module__',
#        '__slots__',
#        'bl_rna',
#        'name',
#        'output_node',
#        'rna_type',
#    )
    # attributes to copy
    cpattrs = (
        'alpha_factor',
        'ambient_factor',
        'blend_type',
        'bump_method',
        'bump_objectspace',
        'color',
        'default_value',
        'density_factor',
        'diffuse_color_factor',
        'diffuse_factor',
        'displacement_factor',
        'emission_color_factor',
        'emission_factor',
        'emit_factor',
        'hardness_factor',
        'invert',
        'mapping',
        'mapping_x',
        'mapping_y',
        'mapping_z',
        'mirror_factor',
        'normal_factor',
        'normal_map_space',
        'object',
        'offset',
        'raymir_factor',
        'reflection_color_factor',
        'reflection_factor',
        'scale',
        'scattering_factor',
        'specular_color_factor',
        'specular_factor',
        'texture',
        'texture_coords',
        'translucency_factor',
        'transmission_color_factor',
        'use',
        'use_from_dupli',
        'use_from_original',
        'use_map_alpha',
        'use_map_ambient',
        'use_map_color_diffuse',
        'use_map_color_emission',
        'use_map_color_reflection',
        'use_map_color_spec',
        'use_map_color_transmission',
        'use_map_density',
        'use_map_diffuse',
        'use_map_displacement',
        'use_map_emission',
        'use_map_emit',
        'use_map_hardness',
        'use_map_mirror',
        'use_map_normal',
        'use_map_raymir',
        'use_map_reflect',
        'use_map_scatter',
        'use_map_specular',
        'use_map_translucency',
        'use_map_warp',
        'use_rgb_to_intensity',
        'use_stencil',
        'uv_layer',
        'warp_factor'
    )
    
    collectobj = context.active_object
    collectmat = collectobj.active_material
    if collectmat == None:
        # Create new material <- Don't create new one now. Because material settings are necessary.
        # collectmat = bpy.data.materials.new('CollecterMat')
        # collectobj.data.materials.append(collectmat)
        return ({'ERROR'}, "Collector has no materials.")
    
    # start collecting from selected objects
    collected = 0
    for obj in context.selected_objects:
        if obj == collectobj:
            continue
        # from all materials
        for matslots in obj.material_slots:
            # all texture slot settings
            for srcslot in matslots.material.texture_slots:
                if srcslot == None:
                    # Empty slot
                    continue
                if srcslot.use == False:
                    # Disabled slot
                    continue
                # append found one
                try:
                    nslot = collectmat.texture_slots.add()
                except RuntimeError:
                    return ({'ERROR'}, "Collector's texture slot is full.")
                
                for attrname in cpattrs:
                    val = getattr(srcslot, attrname, None)
                    try:
                        setattr(nslot, attrname, val)
                    except (AttributeError, TypeError) as err:
                        # print("{}: {}".format(attrname, err))
                        pass
                collected += 1
    
    return ({'INFO'}, '{} textures collected'.format(collected))

# Operator class
class OBJECT_OT_CollectTextures(bpy.types.Operator):
    bl_idname = "object.collect_textures"
    bl_label = "Collect Textures"
    bl_description = "collect enabled textures from selected objects and add it to active object"
    
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects)
    
    def execute(self, context):
        errtype, msg = collect_textures(context)
        if errtype:
            self.report(errtype, msg)
        #print("err:{}, msg:{}".format(err, msg))
        return {'FINISHED'}

# Registration
def register():
    bpy.utils.register_class(OBJECT_OT_CollectTextures)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_CollectTextures)

if __name__ == "__main__":
    register()