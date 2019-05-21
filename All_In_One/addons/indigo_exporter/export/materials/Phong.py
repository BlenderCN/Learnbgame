from ... extensions_framework import util as efutil

from .. materials.Base import AlbedoChannelMaterial, EmissionChannelMaterial, BumpChannelMaterial, NormalChannelMaterial, DisplacementChannelMaterial, ExponentChannelMaterial, RoughnessChannelMaterial, FresnelScaleChannelMaterial, MaterialBase

class PhongMaterial(
    AlbedoChannelMaterial,
    EmissionChannelMaterial,
    BumpChannelMaterial,
    NormalChannelMaterial,
    DisplacementChannelMaterial,
    #ExponentChannelMaterial, # to delete?
    RoughnessChannelMaterial,
    FresnelScaleChannelMaterial,
    
    # MaterialBase needs to be last in this list
    MaterialBase
    ):
    def get_format(self):
        element_name = 'phong'
        
        fmt = {
            'name': [self.material_name],
            'backface_emit': [str(self.material_group.indigo_material_emission.backface_emit).lower()],
            'emission_sampling_factor': [self.material_group.indigo_material_emission.em_sampling_mult],
            element_name: {
                'ior': [self.property_group.ior],
                'fresnel_scale': {
                    'constant': [self.property_group.fresnel_scale]
                },
            }
        }
                
        if self.property_group.use_roughness:
            fmt[element_name]['roughness'] = {'constant': [self.property_group.roughness]}
        else:
            fmt[element_name]['exponent'] = {'constant': [self.property_group.exponent]}
        
        fmt[element_name].update(self.get_channels())
        
        if self.property_group.specular_reflectivity:
            fmt[element_name]['specular_reflectivity'] = fmt[element_name]['diffuse_albedo']
            del fmt[element_name]['diffuse_albedo']
            del fmt[element_name]['ior']
        
        if self.property_group.nk_data_type == 'file' and self.property_group.nk_data_file != '':
            fmt[element_name]['nk_data'] = [efutil.path_relative_to_export(self.property_group.nk_data_file)]
            try:
                # doesn't matter if these keys don't exist, but remove them if they do
                del fmt[element_name]['ior']
                del fmt[element_name]['diffuse_albedo']
                del fmt[element_name]['specular_reflectivity']
            except: pass
            
        if self.property_group.nk_data_type == 'preset':
            fmt[element_name]['nk_data'] = [self.property_group.nk_data_preset]
            try:
                # doesn't matter if these keys don't exist, but remove them if they do
                del fmt[element_name]['ior']
                del fmt[element_name]['diffuse_albedo']
                del fmt[element_name]['specular_reflectivity']
            except: pass
        
        return fmt