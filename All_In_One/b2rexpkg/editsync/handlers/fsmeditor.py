"""
 Finite state machine editor.
"""

from .base import SyncModule
from b2rexpkg.tools.llsd_logic import generate_llsd, get_llsd_info

import bpy

class FsmEditorModule(SyncModule):
    """
    Fsm editor able to generate llsd scripts.
    """
    def _add_state(self, context):
        """
        Add state operator
        """
        fsm = self._get_fsm()
        state = fsm.states.add()
        if fsm.selected_state:
            state.name = fsm.selected_state
        else:
            state.name = 'default'
        fsm.selected_state = state.name

    def _add_sensor(self, context):
        """
        Add sensor operator
        """
        fsm, state = self._get_fsm_state()
        sensor = state.sensors.add()
        sensor.name = sensor.type

    def _up_actuator(self, context):
        """
        Move actuator up operator
        """
        fsm, sensor = self._get_fsm_sensor()
        sel = fsm.selected_actuator
        sensor.actuators.move(sel, sel-1)
        fsm.selected_actuator -= 1

    def _down_actuator(self, context):
        """
        Move actuator down operator
        """
        fsm, sensor = self._get_fsm_sensor()
        sel = fsm.selected_actuator
        sensor.actuators.move(sel, sel+1)
        fsm.selected_actuator += 1

    def _get_fsm(self):
        """
        Get the current active fsm.
        """
        editor = self._parent
        objs = editor.getSelected()
        obj = objs[0]
        fsm = obj.opensim.fsm
        return fsm

    def _get_fsm_state(self):
        """
        Get the current active fsm and state
        """
        fsm = self._get_fsm()
        state = fsm.states[fsm.selected_state]
        return fsm, state

    def _get_fsm_sensor(self):
        """
        Get the current active fsm and sensor
        """
        fsm, state = self._get_fsm_state()
        sensor = state.sensors[fsm.selected_sensor]
        return fsm, sensor

    def _add_actuator(self, context):
        """
        Add actuator operator
        """
        editor = self._parent
        obj = editor.getSelected()[0]
        fsm, sensor = self._get_fsm_sensor()
        actuator = sensor.actuators.add()
        actuator.name = actuator.type
        if not "b2rex_next_id" in obj:
            obj["b2rex_next_id"] = 0
        actuator.id = obj["b2rex_next_id"]
        obj["b2rex_next_id"] += 0
        self._initialize_actuator(obj, actuator)

    def _delete_state(self, context):
        """
        Delete state operator
        """
        fsm = self._get_fsm()
        fsm.states.remove(fsm.selected_state)
        if len(fsm.states):
            fsm.selected_state = fsm.states[0].name
        else:
            fsm.selected_state = ""

    def _delete_sensor(self, context):
        """
        Delete sensor operator
        """
        fsm, state = self._get_fsm_state()
        state.sensors.remove(fsm.selected_sensor)
        fsm.selected_sensor = 0

    def _delete_actuator(self, context):
        """
        Delete actuator operator
        """
        fsm, sensor = self._get_fsm_sensor()
        sensor.actuators.remove(fsm.selected_actuator)
        fsm.selected_actuator = 0

    def _generate_llsd(self, context):
        """
        Generate script operator
        """
        editor = self._parent
        obj = editor.getSelected()[0]
        fsm = obj.opensim.fsm
        print(generate_llsd(fsm, obj))

    def set_sensor_type(self, context, type):
        """
        Set sensor type operator
        """
        editor = self._parent
        obj = editor.getSelected()[0]
        fsm, sensor = self._get_fsm_sensor()
        sensor.type = type
        sensor.name = type

    def set_actuator_type(self, context, type):
        """
        Set actuator type operator
        """
        editor = self._parent
        obj = editor.getSelected()[0]
        fsm, sensor = self._get_fsm_sensor()
        actuator = sensor.actuators[fsm.selected_actuator]
        actuator.type = type
        actuator.name = type
        self._initialize_actuator(obj, actuator)

    def _initialize_actuator(self, obj, actuator):
        llsd_info = get_llsd_info()["Actuators"]
        act_info = llsd_info[actuator.type]
        pre = str(actuator.id)
        for prop in act_info:
            name = list(prop.keys())[0]
            data = list(prop.values())[0]
            tmp_name = "tmp_" + pre + name
            if not tmp_name in obj:
                if 'default' in data:
                    val = data['default']
                elif data['type'] == 'integer':
                    val = 0
                elif data['type'] == 'string':
                    val = "bla"
                elif data['type'] == 'key':
                    val = "bla"
                elif data['type'] == 'float':
                    val = 0.0
                obj[tmp_name] = val

    def draw_object(self, box, editor, obj):
        """
        Draw scripting section in the object panel.
        """
        if not self.expand(box):
            return False
        mainbox = box.box()
        box = mainbox.row()
        main_row = mainbox.row()
        #box = box.box()
        box.label("State")
        props = obj.opensim.fsm
        # draw state list
        row = box.row()
        if not props.states or (props.selected_state and not props.selected_state in props.states):
            row.operator('b2rex.fsm', text='', icon='ZOOMIN').action = '_add_state'
        elif props.states:
            row.operator('b2rex.fsm', text='', icon='ZOOMOUT').action = '_delete_state'
        row.prop_search(props, 'selected_state', props, 'states')

        # draw sensor list
        if not props.selected_state or not props.selected_state in props.states:
            return
        box = main_row.column()
        box.label("Sensors")
        currstate = props.states[props.selected_state]
        box.template_list(currstate,
                          'sensors',
                          props,
                          'selected_sensor')
        row = box.row()
        row.operator('b2rex.fsm', text='', icon='ZOOMIN').action = '_add_sensor'
        if currstate.sensors:
            row.operator('b2rex.fsm', text='', icon='ZOOMOUT').action = '_delete_sensor'
        mainbox.operator('b2rex.fsm', text='Generate', icon='SCRIPT').action = '_generate_llsd'
        if props.selected_sensor >= len(currstate.sensors):
            return
        #box = box.box()
        currsensor = currstate.sensors[props.selected_sensor]
        row = box.row()
        row.alignment = 'LEFT'
        row.label(text='Type:')
        row.operator_menu_enum('b2rex.fsm_sensortype',
                               'type',
                               text=currsensor.type, icon='BLENDER')

        box = main_row.column()
        box.label("Actions")
        # draw current sensor controls

        if currsensor.actuators:
            box.template_list(currsensor,
                          'actuators',
                          props,
                          'selected_actuator')

        row = box.row()
        row.operator('b2rex.fsm', text='', icon='ZOOMIN').action = '_add_actuator'
        if currsensor.actuators:
            row.operator('b2rex.fsm', text='', icon='ZOOMOUT').action = '_delete_actuator'
            if props.selected_actuator > 0:
                row.operator('b2rex.fsm', text='', icon='TRIA_UP').action = '_up_actuator'
            if props.selected_actuator < len(currsensor.actuators) -1:
                row.operator('b2rex.fsm', text='', icon='TRIA_DOWN').action = '_down_actuator'

        if props.selected_actuator >= len(currsensor.actuators):
            return

        curractuator = currsensor.actuators[props.selected_actuator]
        #box.prop(curractuator, 'name')
        row = box.row()
        row.alignment = 'LEFT'
        row.label(text='Type:')
        row.operator_menu_enum('b2rex.fsm_actuatortype',
                               'type',
                               text=curractuator.type, icon='BLENDER')

        llsd_info = get_llsd_info()["Actuators"]
        act_info = llsd_info[curractuator.type]
        pre = str(curractuator.id)
        for prop in act_info:
            name = list(prop.keys())[0]
            data = list(prop.values())[0]
            tmp_name = "tmp_" + pre + name
            if tmp_name in obj:
                box.prop(obj, '["'+tmp_name+'"]', text=name)
        # draw actuators one by one
        #for actuator in currstate.sensors[props.selected_sensor].actuators:
            #    box.label(text=str(actuator))


