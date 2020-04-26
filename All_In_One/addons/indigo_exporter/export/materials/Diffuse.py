from .. materials.Base import AlbedoChannelMaterial, EmissionChannelMaterial, BumpChannelMaterial, NormalChannelMaterial, DisplacementChannelMaterial, MaterialBase

class DiffuseMaterial(
    AlbedoChannelMaterial,
    EmissionChannelMaterial,
    BumpChannelMaterial,
    NormalChannelMaterial,
    DisplacementChannelMaterial,
    
    # MaterialBase needs to be last in this list
    MaterialBase
    ):
    def get_format(self):
        if self.property_group.transmitter:
            element_name = 'diffuse_transmitter'
        else:
            if self.property_group.sigma > 0:
                element_name = 'oren_nayar'
            else:
                element_name = 'diffuse'
        
        fmt = {
            'name': [self.material_name],
            'backface_emit': [str(self.material_group.indigo_material_emission.backface_emit).lower()],
            'emission_sampling_factor': [self.material_group.indigo_material_emission.em_sampling_mult],
            element_name: self.get_channels()
        }
        
        if element_name == 'oren_nayar':
            fmt[element_name].update({
                'sigma': [self.property_group.sigma]
            })

        if self.property_group.shadow_catcher:
            fmt['shadow_catcher'] = ['true']
        
        return fmt