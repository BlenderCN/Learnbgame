"""
 RexLogicModule: Support for rex logic system
"""
import math
import os

from .base import SyncModule

from b2rexpkg.tools import rexio
from b2rexpkg.tools.rexio.library import library

from b2rexpkg.b25 import logic
from b2rexpkg.b25.material import RexMaterialIO

#from .props.rexlogic import RexLogicProps

import bpy

class RexComponent(object):
    """
    A rex component present in a blender object.
    """
    def __init__(self, obj, name=''):
        self._obj = obj
        self.component_name = name
    def _get_dummy(self):
        return ""
    def _get_attribute_names(self):
        return self._attribute_names
    attribute_names = property(_get_attribute_names)

class NameComponent(RexComponent):
    """
    Name component proxying a blender object.
    """
    component_type = 'EC_Name'
    _attribute_names = ['name', 'description']
    def _get_name(self):
        return self._obj.name
    name = property(_get_name)
    def _get_description(self):
        return 'blender object'
    description = property(_get_description)

class MeshComponent(RexComponent):
    """
    Mesh component proxying a blender object.
    """
    component_type = 'EC_Mesh'
    _attribute_names = ['Transform', 'Mesh ref', 'Skeleton ref',
                        'Mesh materials', 'Draw distance', 'Cast shadows']
    def _get_dummy(self):
        return ""
    def _get_transform(self):
        return "0,0,0,90,0,180,1,1,1"
    def _get_mesh_ref(self):
        return "file://"+self._obj.data.name+".mesh"
    def _get_mesh_materials(self):
        return "file://"+self._obj.data.name+".material"
    transform = property(_get_transform) # 0,0,0,90,0,180,1,1,1
    mesh_ref = property(_get_mesh_ref) # file://crab_stand_swim.mesh
    skeleton_ref = property(_get_dummy) # file://crab_stand_swim.skeleton
    mesh_materials = property(_get_mesh_materials) # file://crab.material
    draw_distance = property(_get_dummy) # 0
    cast_shadows = property(_get_dummy) # false

class PlaceableComponent(RexComponent):
    """
    Placeable component proxying a blender object.
    """
    component_type = 'EC_Placeable'
    def _get_dummy(self):
        return ""
    _attribute_names = ['Transform', 'Show bounding box']
    def _get_transform(self):
        editor = bpy.b2rex_session
        pos, rot, scale = editor.getObjectProperties(self._obj)
        r = 180.0/math.pi
        # XXX convert angle to degrees?
        if self._obj.parent:
            pos = editor.unapply_position(self._obj, pos,0,0,0)
        else:
            pos = editor.unapply_position(self._obj, pos,0,0,0)
            rot = list(map(lambda s: s*r, rot))
            # rot = editor.unapply_rotation(rot) - asks for euler?
        scale = editor.unapply_scale(self._obj, scale)
        tr = map(lambda s: str(s), pos + rot + scale)
        return ",".join(tr)
    transform = property(_get_transform) # -68,-4.32,80,0,0,0,2,2,2
    show_bounding_box = property(_get_dummy) # false

class GenericComponent(RexComponent):
    """
    A generic component (can hold any other component).
    """
    def __init__(self, obj, component, metadata):
        RexComponent.__init__(self, obj, component.name)
        self._component = component
        self._metadata = metadata
        self.component_type = component.type

    def _get_attribute_names(self):
        attribute_names = []
        for prop in self._metadata:
            name = list(prop.keys())[0]
            attribute_names.append(name)
        return attribute_names
    _attribute_names = property(_get_attribute_names)

    def __getattr__(self, name):
        entity = self._obj.opensim
        pre = str(self._component.id)
        tmp_name = "com_" + pre + name
        return self._obj[tmp_name]

class RexLogicModule(SyncModule):
    """
    b2rex module taking care of tundra components and the component editor.
    """
    component_data = None
    def register(self, parent):
        """
        Register this module with the editor
        """
        setattr(bpy.types.B2RexObjectProps, 'components',
                property(self.get_entity_components))

    def getPanelName(self):
        return 'Components'

    def reload_components(self, context):
        props = context.scene.b2rex_props
        for subdir in ['Tooltip', 'Door', 'Avatar']:
            dest = os.path.join(props.tundra_path, 'scenes', subdir)
            library.add_path(dest, True)

    def unregister(self, parent):
        """
        Unregister this module from the editor
        """
        if hasattr(bpy.types.B2RexObjectProps, 'components'):
            delattr(bpy.types.B2RexObjectProps, 'components')

    def find_components(self, obj):
        """
        Return components in the given object.
        """
        # base components
        components = [NameComponent(obj), PlaceableComponent(obj), MeshComponent(obj)]

        # user defined components
        coms_info = rexio.get_component_info()
        for bcomp in obj.opensim.component_data:
            metadata = coms_info[bcomp.type]
            component = GenericComponent(obj, bcomp, metadata)
            components.append(component)

        return components

    def get_entity_components(self, opensim_data):
        """
        Get components from the given opensim data.
        """
        if not opensim_data.uuid:
            return []
        obj = self._parent.findWithUUID(opensim_data.uuid)
        return self.find_components(obj)

    #parent.registerCommand('CoarseLocationUpdate', self.processCoarseLocationUpdate)

    def _add_component(self, context):
        """
        Add component operator.
        """
        entity = self._get_entity()
        component = entity.component_data.add()
        component.id = entity.next_component_idx
        entity.next_component_idx += 1

        if entity.selected_component:
            component.name = entity.selected_component
        else:
            component.name = 'default'
        entity.selected_component = component.name

        obj = self._parent.getSelected()[0]
        self._initialize_component(obj, component)

    def _initialize_component(self, obj, component):
        """
        Initialize component operator.
        """
        coms_info = rexio.get_component_info()
        com_info = coms_info[component.type]
        pre = str(component.id)
        for prop in com_info:
            name = list(prop.keys())[0]
            data = list(prop.values())[0]
            tmp_name = "com_" + pre + name
            if not tmp_name in obj:
                if 'default' in data:
                    val = data['default']
                elif data['type'] == 'integer':
                    val = 0
                elif data['type'] == 'string':
                    val = "bla"
                elif data['type'] == 'jsscript':
                    val = ""
                elif data['type'] == 'boolean':
                    val = True
                elif data['type'] == 'key':
                    val = "bla"
                elif data['type'] == 'float':
                    val = 0.0
                obj[tmp_name] = val


    def _delete_component(self, context):
        """
        Delete component operator.
        """
        entity = self._get_entity()

    def _get_entity(self):
        """
        Get the current active entity.
        """
        editor = self._parent
        objs = editor.getSelected()
        obj = objs[0]
        return obj.opensim

    def set_component_type(self, context, new_type):
        """
        Set the component type.
        """
        entity = self._get_entity()
        component = entity.component_data[entity.selected_component]
        component.type = new_type

        obj = self._parent.getSelected()[0]
        self._initialize_component(obj, component)

    def draw_object(self, box, editor, obj):
        """
        Component editor.
        """
        if not self.expand(box):
            return False
        mainbox = box.box()
        box = mainbox.row()
        main_row = mainbox.row()
        #box = box.box()
        box.label("Components")
        props = obj.opensim
        # draw state list
        row = box.row()
        if not props.component_data or (props.selected_component and not
                                    props.selected_component in props.component_data):
            row.operator('b2rex.entity', text='', icon='ZOOMIN').action = '_add_component'
        elif props.component_data:
            row.operator('b2rex.entity', text='', icon='ZOOMOUT').action = '_delete_component'
        row.prop_search(props, 'selected_component', props, 'component_data')

        # draw sensor list
        if not props.selected_component or not props.selected_component in props.component_data:
            return
        box = main_row.column()
        box.label("Current component")
        component = props.component_data[props.selected_component]

        #box.prop(curractuator, 'name')
        row = box.row()
        row.alignment = 'LEFT'
        row.label(text='Type:')
        row.operator_menu_enum('b2rex.component_type',
                               'type',
                               text=component.type, icon='BLENDER')

        coms_info = rexio.get_component_info()
        com_info = coms_info[component.type]
        pre = str(component.id)
        for prop in com_info:
            name = list(prop.keys())[0]
            data = list(prop.values())[0]
            if data['type'] == 'hardcoded':
                continue
            tmp_name = "com_" + pre + name
            if tmp_name in obj:
                if data['type'] == 'jsscript':
                    row = box.row()
                    row.prop(obj, '["'+tmp_name+'"]', text=name)
                    try:
                        comp = library.get_component('jsscript', obj[tmp_name])
                        row.label('', icon='FILE_TICK')
                    except KeyError:
                        pass
                elif data['type'] == 'boolean':
                    box.prop(obj, '["'+tmp_name+'"]', text=name, toggle=True)
                else:
                    box.prop(obj, '["'+tmp_name+'"]', text=name)


