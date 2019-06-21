from .. materials.Base import BlendChannelMaterial, MaterialBase

class BlendMaterial(
    BlendChannelMaterial,
    
    # MaterialBase needs to be last in this list
    MaterialBase
    ):
    def get_format(self):
        element_name = 'blend'
        
        if self.property_group.a_null:
            a_name = ['blendigo_null']
        else:
            a_name = [self.property_group.a_index]
        
        if self.property_group.b_null:
            b_name = ['blendigo_null']
        else:
            b_name = [self.property_group.b_index]
        
        fmt = {
            'name': [self.material_name],
            element_name: {
                'blend': { 'constant' : [self.property_group.factor] } ,
                'step_blend': [str(self.property_group.step).lower()],
                'a_name': a_name,
                'b_name': b_name,
            }
        }
        
        fmt[element_name].update(self.get_channels())
        
        return fmt