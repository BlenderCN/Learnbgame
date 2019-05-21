import os

import bpy            #@UnresolvedImport

from ...extensions_framework import util as efutil

from .. import xml_builder, xml_cdata
from .. materials.spectra import blackbody, rgb, uniform

class MaterialBase(xml_builder):
    
    scene = None
    
    def build_xml_element(self, context, scene=None):
        if scene: self.scene = scene
        xml = self.Element('material')
        self.build_subelements(context, self.get_format(), xml)
        return xml
    
    def __init__(self, obj, name, material_group, property_group):
        self.obj = obj
        self.material_name = name
        self.material_group = material_group
        self.property_group = property_group
    
    def get_format(self):
        self.format['name'] = [self.material_name]
        return self.format
    
    found_textures = []
    found_texture_indices = []
    
    def get_channels(self):
        op = {}
        
        self.found_textures = []
        self.found_texture_indices = []
        
        op.update(self.AlbedoChannel())
        op.update(self.EmissionChannel())
        op.update(self.BumpChannel())
        op.update(self.NormalChannel())
        op.update(self.DisplacementChannel())
        op.update(self.ExponentChannel()) # to delete?
        op.update(self.RoughnessChannel())
        op.update(self.BlendChannel())
        op.update(self.TransmittanceChannel())
        op.update(self.AbsorptionChannel())
        op.update(self.AbsorptionLayerChannel())
        op.update(self.FresnelScaleChannel())
        
        if len(self.found_textures) > 0:
            op.update({
                'texture': tuple(self.found_textures)
            })
        
        return op
    
    def get_channel(self, property_group, channel_name, channel_prop_name):
        d = {}
        
        channel_type = getattr(property_group, channel_prop_name + '_type')
        
        if channel_type == 'spectrum':
            spectrum_type = getattr(property_group, channel_prop_name + '_SP_type')
            if spectrum_type == 'rgb':
                d[channel_name] = {
                    'constant': rgb([i for i in getattr(property_group, channel_prop_name + '_SP_rgb') * getattr(property_group, channel_prop_name + '_SP_rgb_gain', 1.0)])
                }
            elif spectrum_type == 'uniform':
                d[channel_name] = {
                    'constant': uniform([
                        getattr(property_group, channel_prop_name + '_SP_uniform_val') * \
                        10**getattr(property_group, channel_prop_name + '_SP_uniform_exp')
                    ])
                }
            elif spectrum_type == 'blackbody':
                d[channel_name] = {
                    'constant': blackbody(
                        [getattr(property_group, channel_prop_name + '_SP_blackbody_temp')],
                        [getattr(property_group, channel_prop_name + '_SP_blackbody_gain')]
                    )
                }
        
        elif channel_type == 'texture':
            tex_name = getattr(property_group, channel_prop_name + '_TX_texture')
            
            if tex_name: # string is not empty
                if channel_prop_name not in self.found_texture_indices:
                    self.found_texture_indices.append(channel_prop_name)
                    
                    if not tex_name in bpy.data.textures:
                        raise Exception("Texture \"%s\" assigned to material \"%s\" doesn't exist!" %(tex_name, self.material_name))
                    
                    tex_property_group = bpy.data.textures[tex_name].indigo_texture
                    
                    if tex_property_group.image_ref == 'file':
                        relative_texture_path = efutil.path_relative_to_export(
                            getattr(tex_property_group, 'path')
                        )
                    elif tex_property_group.image_ref == 'blender':
                        if not tex_property_group.image in bpy.data.images:
                            raise Exception("Error with image reference on texture \"%s\"" % tex_name)
                        
                        img = bpy.data.images[tex_property_group.image]
                        
                        if img.filepath == '':
                            bl_img_path = 'blendigo_extracted_image_%s.png' % bpy.path.clean_name(tex_name)
                        else:
                            bl_img_path = img.filepath
                        
                        if img.source != 'FILE' or img.packed_file:
                            bl_file_formatted = os.path.splitext(os.path.basename(bl_img_path))[0]
                            bl_file_formatted = '%s.%s' % (bl_file_formatted, self.scene.render.image_settings.file_format)
                            bl_img_path = os.path.join(
                                efutil.export_path,
                                efutil.scene_filename(),
                                bpy.path.clean_name(self.scene.name),
                                '%05d' % self.scene.frame_current,
                                bl_file_formatted
                            )
                            img.save_render(bl_img_path, self.scene)
                        
                        relative_texture_path = efutil.path_relative_to_export(bl_img_path)
                    
                    if not getattr(property_group, channel_prop_name + '_TX_abc_from_tex'):
                        abc_property_group = property_group
                        abc_prefix = channel_prop_name + '_TX_'
                    else:
                        abc_property_group = tex_property_group
                        abc_prefix = ''
                    
                    uv_set_name  = getattr(property_group, channel_prop_name + '_TX_uvset')
                    try:
                        uv_set_index = self.obj.data.uv_textures.keys().index(uv_set_name)
                    except:
                        uv_set_index = 0
                    
                    self.found_textures.append({
                        'uv_set_index':    [uv_set_index], #getattr(property_group, channel_prop_name + '_TX_uv_index')],
                        'path':            [relative_texture_path],
                        'exponent':        [getattr(tex_property_group, 'gamma')],
                        'a':            [getattr(abc_property_group, abc_prefix + 'A')],
                        'b':            [getattr(abc_property_group, abc_prefix + 'B')],
                        'c':            [getattr(abc_property_group, abc_prefix + 'C')],
                        'smooth':        [str(getattr(property_group, channel_prop_name + '_TX_smooth')).lower()]
                    })
                
                d[channel_name] = {
                    'texture': {
                        'texture_index': [ self.found_texture_indices.index(channel_prop_name) ],
                    }
                }
        
        elif channel_type == 'shader':
            try:
                shader_name = getattr(property_group, channel_prop_name + '_SH_text')
                if not shader_name in bpy.data.texts:
                    raise Exception('Referenced Text "%s" for shader on material "%s" not found' % (shader_name, self.material_name))
                
                shader_text = '\n' + bpy.data.texts[shader_name].as_string()
                d[channel_name] = {
                    'shader': {
                        'shader': xml_cdata(shader_text)
                    }
                }
            except:
                pass
        
        return d
    
    # Material types should implement these in subclasses ...
    def AlbedoChannel(self):
        return {}
    def EmissionChannel(self):
        return {}
    def BumpChannel(self):
        return {}
    def NormalChannel(self):
        return {}
    def DisplacementChannel(self):
        return {}
    def ExponentChannel(self):# to delete?
        return {}# to delete?
    def RoughnessChannel(self):
        return {}
    def BlendChannel(self):
        return {}
    def TransmittanceChannel(self):
        return {}
    def AbsorptionChannel(self):
        return {}
    def AbsorptionLayerChannel(self):
        return {}
    def FresnelScaleChannel(self):
        return {}

# ... by also inheriting from the following as needed (multiple inheritance FTW)
class AlbedoChannelMaterial(object):
    #['diffuse', 'phong']
    def AlbedoChannel(self):
        return self.get_channel(self.material_group.indigo_material_colour, self.property_group.channel_name, 'colour')

class EmissionChannelMaterial(object):
    #['diffuse', 'phong', 'specular']
    def EmissionChannel(self):
        epg = self.material_group.indigo_material_emission
        if epg.emission_enabled:
            ems = self.get_channel(epg, 'emission', 'emission')
            ems['base_emission'] = {
                'constant': uniform([
                    epg.emit_power * epg.emit_gain_val * (10**epg.emit_gain_exp)
                ]),
            }
            
            if self.scene.indigo_lightlayers.ignore:
                ems['layer'] = [0]
            else:
                lls = self.scene.indigo_lightlayers.enumerate()
                valid_layers = lls.keys()
                ems['layer'] = [lls[epg.emit_layer]] if epg.emit_layer in valid_layers else [0]
            return ems
        else:
            return {}

class BumpChannelMaterial(object):
    #['diffuse', 'phong', 'specular']
    def BumpChannel(self):
        if self.material_group.indigo_material_bumpmap.bumpmap_enabled:
            return self.get_channel(self.material_group.indigo_material_bumpmap, 'bump', 'bumpmap')
        else:
            return {}
            
class NormalChannelMaterial(object):
    #['diffuse', 'phong', 'specular']
    def NormalChannel(self):
        if self.material_group.indigo_material_normalmap.normalmap_enabled:
            return self.get_channel(self.material_group.indigo_material_normalmap, 'normal_map', 'normalmap')
        else:
            return {}

class DisplacementChannelMaterial(object):
    #['diffuse', 'phong', 'specular']
    def DisplacementChannel(self):
        if self.material_group.indigo_material_displacement.displacement_enabled:
            return self.get_channel(self.material_group.indigo_material_displacement, 'displacement', 'displacement')
        else:
            return {}

class ExponentChannelMaterial(object): # to delete?
    #['phong', 'specular::glossy_transparent']
    def ExponentChannel(self):
        if (self.material_group.indigo_material_exponent.exponent_enabled and self.material_group.type == 'phong') or \
           (self.material_group.indigo_material_exponent.exponent_enabled and self.material_group.type == 'specular' and self.material_group.indigo_material_specular.type == 'glossy_transparent'):
            return self.get_channel(self.material_group.indigo_material_exponent, 'exponent', 'exponent')
        else:
            return {}
class RoughnessChannelMaterial(object):
    #['phong', 'specular::glossy_transparent', 'fastsss']
    def RoughnessChannel(self):
        if (self.material_group.indigo_material_roughness.roughness_enabled and self.material_group.type in ['phong', 'fastsss']) or \
           (self.material_group.indigo_material_roughness.roughness_enabled and self.material_group.type == 'specular' and self.material_group.indigo_material_specular.type == 'glossy_transparent'):
            return self.get_channel(self.material_group.indigo_material_roughness, 'roughness', 'roughness')
        else:
            return {}

class BlendChannelMaterial(object):
    #['blend']
    def BlendChannel(self):
        if self.material_group.indigo_material_blendmap.blendmap_enabled:
            return self.get_channel(self.material_group.indigo_material_blendmap, 'blend', 'blendmap')
        else:
            return {}

class TransmittanceChannelMaterial(object):
    #['doublesidedthin']
    def TransmittanceChannel(self):
        return self.get_channel(self.material_group.indigo_material_transmittance, 'transmittance', 'transmittance')

class AbsorptionChannelMaterial(object):
    #['caoting']
    def AbsorptionChannel(self):
        return self.get_channel(self.material_group.indigo_material_absorption, 'absorption', 'absorption')

class AbsorptionLayerChannelMaterial(object):
    #['specular']
    def AbsorptionLayerChannel(self):
        if self.material_group.indigo_material_absorption_layer.absorption_layer_enabled:
            return self.get_channel(self.material_group.indigo_material_absorption_layer, 'absorption_layer_transmittance', 'absorption_layer')
        else:
            return {}
        
class FresnelScaleChannelMaterial(object):
    #['phong']
    def FresnelScaleChannel(self):
        if self.material_group.indigo_material_fresnel_scale.fresnel_scale_enabled:
            return self.get_channel(self.material_group.indigo_material_fresnel_scale, 'fresnel_scale', 'fresnel_scale')
        else:
            return {}