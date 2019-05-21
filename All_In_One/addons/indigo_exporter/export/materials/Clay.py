from .. import xml_builder
from .. materials.spectra import rgb

class ClayMaterial(xml_builder):
    '''
    A dummy/placeholder 'clay' material
    '''
    
    def build_xml_element(self, context):
        xml = self.Element('material')
        self.build_subelements(
            context,
            {
                'name': ['blendigo_clay'],
                'diffuse': {
                    'albedo': {
                        'constant':  rgb([0.8, 0.8, 0.8])
                    }
                }
            },
            xml
        )
        return xml

class NullMaterialDummy(xml_builder):
    '''
    The Null material
    '''
    
    def build_xml_element(self, context):
        xml = self.Element('material')
        self.build_subelements(
            context,
            {
                'name': ['blendigo_null'],
                'null_material': {}
            },
            xml
        )
        return xml
    