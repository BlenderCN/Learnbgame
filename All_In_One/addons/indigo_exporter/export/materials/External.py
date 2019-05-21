from .. materials.Base import MaterialBase
#from indigo.export import xml_builder

class ExternalMaterial(MaterialBase):
    '''
    This isn't actually a material, but a simple XML element
    '''
    
    def build_xml_element(self, context):
        xml = self.Element('include')
        self.build_subelements(context, self.format, xml)
        return xml
    
    def __init__(self, filename):
        self.format = {
            'pathname': [filename]
        }
