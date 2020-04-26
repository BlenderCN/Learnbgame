from .. materials.Base import AlbedoChannelMaterial, EmissionChannelMaterial, BumpChannelMaterial, NormalChannelMaterial, DisplacementChannelMaterial, AbsorptionChannelMaterial, MaterialBase

class CoatingMaterial(
    #AlbedoChannelMaterial,
    EmissionChannelMaterial,
    BumpChannelMaterial,
    NormalChannelMaterial,
    DisplacementChannelMaterial,
    AbsorptionChannelMaterial,
    
    # MaterialBase needs to be last in this list
    MaterialBase
    ):
    
    def get_format(self):
        element_name = 'coating'
        
        fmt = {
            'name': [self.material_name],
            'backface_emit': [str(self.material_group.indigo_material_emission.backface_emit).lower()],
            'emission_sampling_factor': [self.material_group.indigo_material_emission.em_sampling_mult],
            element_name: {
                'ior': [self.property_group.ior],
                'interference': [str(self.property_group.interference).lower()],
                'roughness': {
                    'constant': [self.property_group.roughness]
                },
                'thickness': {
                    'constant': [self.property_group.thickness * 0.000001] # Convert to m.
                },
                'fresnel_scale': {
                    'constant': [self.property_group.fresnel_scale]
                },
                'substrate_material_name': [self.property_group.substrate_material_index],
            }
        }
        
        #absorption = self.get_channel(self.material_group.indigo_material_colour, self.property_group.channel_name, 'colour')
        #absorption = self.get_channel(self.material_group.indigo_material_colour, self.property_group.absorption, 'colour')
        
        #absorption = self.get_channel(self.material_group.indigo_material_colour, self.property_group.absorption, 'absorption')
        #print("absorption: " + str(absorption))
        
        #fmt[element_name].update(absorption)
        
        fmt[element_name].update(self.get_channels())
        
        return fmt