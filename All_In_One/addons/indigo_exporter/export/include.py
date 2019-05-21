from .. export import xml_builder

class xml_include(xml_builder):
    
    def build_xml_element(self, context):
        xml = self.Element('include')
        self.build_subelements(context, self.format, xml)
        return xml
    
    def __init__(self, filename):
        self.format = {
            'pathname': [filename]
        }