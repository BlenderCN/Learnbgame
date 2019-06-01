"""
 Exporter for tundra xml format.
"""

import os

import xml.etree.ElementTree as ET

from .info import get_component_info
from .library import library

def attr_name(name):
    """
    Return an attribute name converted into a python attribute name.
    """
    return name.lower().replace(' ', '_')

class RexSceneExporter(object):
    def export(self, scene, filename):
        """
        Export the given scene into given filename.
        """
        root = ET.Element('scene')
        self._dirname = os.path.dirname(filename)
        for idx, obj in enumerate(scene.objects):
            self.export_object(obj, root, idx)
        tree = ET.ElementTree(root)
        tree.write(filename)

    def test(self):
        """
        Export current scene to a test file
        """
        import bpy
        self.export(bpy.context.scene, "/tmp/test.xml")

    def export_object(self, obj, root, idx):
        """
        Export the given blender object into a rex element tree
        """
        entity = ET.SubElement(root, 'entity')
        entity.set('id', str(idx))
        self.export_components(obj, entity)

    def export_components(self, obj, entity):
        """
        Export all components from the given object into a
        rex entity element tree.
        """
        components_info = get_component_info()
        dyn_props = []
        dyn_component = None
        for comp in obj.opensim.components:
            component = ET.SubElement(entity, 'component')
            component.set('type', comp.component_type)
            component.set('sync', '1')
            if comp.component_name:
                component.set('name', comp.component_name)
            for attr in comp.attribute_names:
                value = getattr(comp, attr_name(attr))
                if comp.component_type in components_info:
                    attr_meta = list(filter(lambda s: list(s.keys())[0] == attr,
                                            components_info[comp.component_type]))
                    if attr_meta:
                        attr_meta = list(attr_meta[0].values())[0]
                else:
                    attr_meta = None

                attribute = ET.SubElement(component, 'attribute')
                if attr_meta:
                    if 'internal_name' in attr_meta:
                        name = attr_meta['internal_name']
                    else:
                        name = attr
                    attr_type = attr_meta['type']
                    if attr_type == 'boolean':
                        value = bool(value)
                    elif attr_type == 'jsscript':
                        jscomp = library.get_component('jsscript', value)
                        jscomp.pack(self._dirname)
                        component.set('name', value)
                        value = 'local://'+value+'.js'
                        if jscomp.attributes:
                            dyn_props += jscomp.attributes
                else:
                    name = attr

                attribute.set('name', name)
                attribute.set('value', self.format_attribute(value))
            if comp.component_type == 'EC_DynamicComponent':
                dyn_component = component
        if dyn_props:
            if not dyn_component:
                dyn_component = ET.SubElement(entity, 'component')
                dyn_component.set('type', 'EC_DynamicComponent')
                dyn_component.set('sync', '1')
            for dyn_prop in dyn_props:
                attribute = ET.SubElement(dyn_component, 'attribute')
                attribute.set('name', dyn_prop)
                attribute.set('type', 'bool')
                attribute.set('value', self.format_attribute(False))

    def format_attribute(self, value):
        """
        Format the given value for inclusion into rex xml.
        """
        if value.__class__ == bool:
            if value:
                return 'true'
            else:
                return 'false'
        return str(value)
