from . import xml_builder

class light_layer_xml(xml_builder):
    
    def build_xml_element(self, scene, idx, layer_name):
        xml = self.Element('layer_setting')
        if idx == 0: #default layer
            l=scene.indigo_lightlayers
            ls = {}
            if l.default_SP_type == 'rgb':
                ls = {
                    'rgb': {
                        'rgb': ['{} {} {}'.format(l.default_SP_rgb[0], l.default_SP_rgb[1], l.default_SP_rgb[2])],
                        'gain': [l.default_SP_rgb_gain],
                    }
                }
            elif l.default_SP_type == 'blackbody':
                ls = {
                    'blackbody': {
                        'temperature': ['{}'.format(l.default_blackbody_temp)],
                        'gain': [l.default_blackbody_gain],
                    }
                }
            elif l.default_SP_type == 'xyz':
                ls = {
                    'xyz': {
                        'xyz': ['{} {} {}'.format(l.default_SP_xyz[0], l.default_SP_xyz[1], l.default_SP_xyz[2])],
                        'gain': [l.default_SP_xyz_gain],
                    }
                }
                
            self.build_subelements(
                scene,
                {
                    'name':  ['default'],
                    'enabled': ['true'],
                    'layer_scale': ls,
                },
                xml
            )
        else:
            layer = scene.indigo_lightlayers.lightlayers.get(layer_name)
            
            ls = {}
            if layer.lightlayer_SP_type == 'rgb':
                ls = {
                    'rgb': {
                        'rgb': ['{} {} {}'.format(layer.lightlayer_SP_rgb[0], layer.lightlayer_SP_rgb[1], layer.lightlayer_SP_rgb[2])],
                        'gain': [layer.lightlayer_SP_rgb_gain],
                    }
                }
            elif layer.lightlayer_SP_type == 'blackbody':
                ls = {
                    'blackbody': {
                        'temperature': ['{}'.format(layer.lightlayer_blackbody_temp)],
                        'gain': [layer.lightlayer_blackbody_gain],
                    }
                }
            elif layer.lightlayer_SP_type == 'xyz':
                ls = {
                    'xyz': {
                        'xyz': ['{} {} {}'.format(layer.lightlayer_SP_xyz[0], layer.lightlayer_SP_xyz[1], layer.lightlayer_SP_xyz[2])],
                        'gain': [layer.lightlayer_SP_xyz_gain],
                    }
                }
                
            self.build_subelements(
                scene,
                {
                    'name':  [layer_name],
                    'enabled': [str(layer.lg_enabled).lower()],
                    'layer_scale': ls,
                },
                xml
            )
        return xml