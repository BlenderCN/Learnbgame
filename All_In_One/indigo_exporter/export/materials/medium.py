from .. import xml_builder
from .. materials.Base        import MaterialBase
from .. materials.spectra    import rgb, uniform

class medium_xml(xml_builder):
    
     def build_xml_element(self, scene,medium_name, medium_data ):
        xml = self.Element('medium')
        self.build_subelements(scene, self.get_format(), xml)
        return xml
    
     def __init__(self, scene,medium_name, medium_index, medium_data):
        self.medium_name = medium_name
        self.medium_index = medium_index
        self.medium_data = medium_data
    
     def get_format(self):
        medium_data = self.medium_data.medium_type
        
        fmt = {
            'name': [self.medium_name + '_medium'],
            'uid': [self.medium_index + 10000 ],
            'precedence': [self.medium_data.precedence],
            self.medium_data.medium_type: {}
        }
        
        if self.medium_data.medium_type == 'basic':
            fmt[self.medium_data.medium_type] = {
                'ior': [self.medium_data.medium_ior],
                'cauchy_b_coeff': [self.medium_data.medium_cauchy_b],
                'fast_sss': [str(self.medium_data.fast_sss).lower()],
            }
            if self.medium_data.medium_type_SP_type == 'rgb':
                fmt[self.medium_data.medium_type]['absorption_coefficient_spectrum'] = rgb([(1.0-i)*self.medium_data.medium_type_SP_rgb_gain for i in self.medium_data.medium_type_SP_rgb])
            elif self.medium_data.medium_type_SP_type == 'uniform':
                fmt[self.medium_data.medium_type]['absorption_coefficient_spectrum'] = uniform([
                    self.medium_data.medium_type_SP_uniform_val * \
                    10**self.medium_data.medium_type_SP_uniform_exp
                ])
            
            if self.medium_data.sss:
                 if self.medium_data.sss_scatter_SP_type == 'rgb':
                    SCS = rgb([i*self.medium_data.sss_scatter_SP_rgb_gain for i in self.medium_data.sss_scatter_SP_rgb])
                 elif self.medium_data.sss_scatter_SP_type == 'uniform':
                    SCS = uniform([
                        self.medium_data.sss_scatter_SP_uniform_val * \
                        10**self.medium_data.sss_scatter_SP_uniform_exp
                    ])
                
                 if self.medium_data.sss_phase_function == 'uniform':
                    PF = { 'uniform': {} }
                 elif self.medium_data.sss_phase_function == 'hg':
                    if self.medium_data.sss_phase_hg_SP_type == 'rgb':
                        PF_HG_GS = rgb([i*self.medium_data.sss_phase_hg_SP_rgb_gain for i in self.medium_data.sss_phase_hg_SP_rgb])
                    elif self.medium_data.sss_phase_hg_SP_type == 'uniform':
                        PF_HG_GS = uniform([
                            self.medium_data.sss_phase_hg_SP_uniform_val * \
                            10**self.medium_data.sss_phase_hg_SP_uniform_exp
                        ])
                    PF = {
                        'henyey_greenstein': {
                            'g_spectrum': PF_HG_GS
                        }
                    }
                 fmt[self.medium_data.medium_type]['subsurface_scattering'] = {
                    'scattering_coefficient_spectrum': SCS,
                    'phase_function': PF,
                }
         
        elif self.medium_data.medium_type == 'dermis':
            fmt[self.medium_data.medium_type] = {
                'hemoglobin_fraction': [self.medium_data.medium_haemoglobin],
            }
        elif self.medium_data.medium_type == 'epidermis':
            fmt[self.medium_data.medium_type] = {
                'melanin_fraction': [self.medium_data.medium_melanin],
                'melanin_type_blend': [self.medium_data.medium_eumelanin],
            }
        elif self.medium_data.medium_type == 'atmosphere':
            fmt[self.medium_data.medium_type] = {
                'turbidity': [self.medium_data.medium_turbidity],
                'center': [ str(self.medium_data.medium_posx) + ' ' + str(self.medium_data.medium_posy) + ' ' + str(self.medium_data.medium_posz)],
            }
        return fmt