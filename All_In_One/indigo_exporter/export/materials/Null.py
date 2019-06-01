from .. materials.Base import EmissionChannelMaterial, MaterialBase

class NullMaterial(
        EmissionChannelMaterial,
        MaterialBase
        ):
    '''
    The Null material
    '''
    
    def get_format(self):
        element_name = 'null_material'
        
        fmt = {
            'name': [self.material_name],
            'backface_emit': [str(self.material_group.indigo_material_emission.backface_emit).lower()],
            'emission_sampling_factor': [self.material_group.indigo_material_emission.em_sampling_mult],
            element_name: {}
        }        
        return fmt