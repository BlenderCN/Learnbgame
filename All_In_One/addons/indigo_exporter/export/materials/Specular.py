import bpy

from .. import xml_builder
from .. materials.Base        import EmissionChannelMaterial, BumpChannelMaterial, NormalChannelMaterial, DisplacementChannelMaterial, ExponentChannelMaterial, RoughnessChannelMaterial, AbsorptionLayerChannelMaterial, MaterialBase
from .. materials.spectra    import rgb, uniform



class SpecularMaterial(
    AbsorptionLayerChannelMaterial,
    EmissionChannelMaterial,
    BumpChannelMaterial,
    NormalChannelMaterial,
    DisplacementChannelMaterial,
    #ExponentChannelMaterial, # to delete?
    RoughnessChannelMaterial,
    
    # MaterialBase needs to be last in this list
    MaterialBase
    ):
    def get_format(self):
        # will be specular or glossy_transparent
        element_name = self.property_group.type
        medium_name = self.property_group.medium_chooser 
        # get medium index
        medium_index = bpy.context.scene.indigo_material_medium.medium.find(medium_name)
        # TODO:
        # medium check <-> name
        if (len(medium_name) == 0) or  (medium_index == -1):
            medium_name = "basic"
            #medium_index = 10190137
            medium_index = -1
                     
        else:
            medium_name = medium_name + '_medium'
            
        fmt = {
            'name': [self.material_name],
            'backface_emit': [str(self.material_group.indigo_material_emission.backface_emit).lower()],
            'emission_sampling_factor': [self.material_group.indigo_material_emission.em_sampling_mult],
            element_name: {
                'internal_medium_uid': [ +medium_index + 10000 ]
            }
        }
        
        if element_name == 'specular':
            if self.property_group.transparent:
                fmt[element_name]['transparent'] = ['true']
            else:
                fmt[element_name]['transparent'] = ['false']
                
            if self.property_group.arch_glass:
                fmt[element_name]['arch_glass'] = ['true']
            else:
                fmt[element_name]['arch_glass'] = ['false']

            if self.property_group.single_face and self.property_group.arch_glass:
                fmt[element_name]['single_face'] = ['true']
            else:
                fmt[element_name]['single_face'] = ['false']
        else:
            if self.property_group.use_roughness:
                fmt[element_name]['roughness'] = {'constant': [self.property_group.roughness]}
            else:
                fmt[element_name]['exponent'] = [self.property_group.exponent]
        
        fmt[element_name].update(self.get_channels())
        
        return fmt