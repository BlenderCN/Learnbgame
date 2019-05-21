from .. materials.Base import EmissionChannelMaterial, BumpChannelMaterial, NormalChannelMaterial, DisplacementChannelMaterial, TransmittanceChannelMaterial, MaterialBase

class DoubleSidedThinMaterial(
    EmissionChannelMaterial,
    BumpChannelMaterial,
    NormalChannelMaterial,
    DisplacementChannelMaterial,
    TransmittanceChannelMaterial,
    
    # MaterialBase needs to be last in this list
    MaterialBase
    ):
    
    def get_format(self):
        element_name = 'double_sided_thin'
        
        fmt = {
            'name': [self.material_name],
            'backface_emit': [str(self.material_group.indigo_material_emission.backface_emit).lower()],
            'emission_sampling_factor': [self.material_group.indigo_material_emission.em_sampling_mult],
            element_name: {
                'ior': [self.property_group.ior],
                'front_roughness': {
                    'constant': [self.property_group.front_roughness]
                },
                'back_roughness': {
                    'constant': [self.property_group.back_roughness]
                },
                'r_f': {
                    'constant': [self.property_group.r_f]
                },
                'front_fresnel_scale': {
                    'constant': [self.property_group.front_fresnel_scale]
                },
                'back_fresnel_scale': {
                    'constant': [self.property_group.back_fresnel_scale]
                },
                'front_material_name': [self.property_group.front_material_index],
                'back_material_name': [self.property_group.back_material_index],
            }
        }
        
        fmt[element_name].update(self.get_channels())
        
        return fmt
