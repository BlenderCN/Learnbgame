import bge
import importlib
import mathutils
import math
import numbers
import collections
import re
import time
import aud
import os
import random
import sys
import operator

#Persistent maps
class SimpleLoggingDatabase(object):
    class LineBuffer(object):
        def __init__(self, buffer=[]):
            self.buffer = buffer
            self.index = 0
            self.size = len(self.buffer)
        def read(self):
            line = self.buffer[self.index]
            self.index += 1
            return line
        def write(self, line):
            self.buffer.append(line + "\n")
        def has_next(self):
            return self.index < self.size
        def flush(self, file):
            with open(file, "a") as f:
                f.writelines(self.buffer)
    class Serializer(object):
        def read(self, line_reader): raise NotImplemented()
        def write(self, value, line_writer): raise NotImplemented()
        pass
    serializers = {}
    storage_dir = bge.logic.expandPath("//bgelogic/storage")
    shared_dbs = {}
    @classmethod
    def get_or_create_shared_db(cls, fname):
        db = cls.shared_dbs.get(fname)
        if db is None:
            db = SimpleLoggingDatabase(fname)
            cls.shared_dbs[fname] = db
        return db
    @classmethod
    def get_storage_dir(cls):
        return cls.storage_dir

    @classmethod
    def put_value(cls, key, value, buffer):
        type_name = str(type(value))
        serializer = cls.serializers.get(type_name)
        if not serializer: return False
        buffer.write("PUT")
        buffer.write(key)
        buffer.write(type_name)
        serializer.write(value, buffer)

    @classmethod
    def read_existing(cls, fpath, intodic):
        lines = []
        with open(fpath, "r") as f:
            lines.extend(f.read().splitlines())
        buffer = SimpleLoggingDatabase.LineBuffer(lines)
        log_size = 0
        while buffer.has_next():
            op = buffer.read()
            assert op == "PUT"
            key = buffer.read()
            type_id = buffer.read()
            serializer = SimpleLoggingDatabase.serializers.get(type_id)
            value = serializer.read(buffer)
            intodic[key] = value
            log_size += 1
        return log_size

    @classmethod
    def write_put(cls, fname, key, value):
        type_name = str(type(value))
        serializer = cls.serializers.get(type_name)
        if not serializer: return#no serializer for given value type
        if not os.path.exists(cls.get_storage_dir()): os.mkdir(cls.get_storage_dir())
        fpath = os.path.join(cls.get_storage_dir(), "{}.logdb.txt".format(fname))
        buffer = SimpleLoggingDatabase.LineBuffer()
        cls.put_value(key, value, buffer)
        buffer.flush(fpath)

    @classmethod
    def read(cls, fname, intodic):
        fpath = os.path.join(cls.get_storage_dir(), "{}.logdb.txt".format(fname))
        if os.path.exists(fpath):
            return cls.read_existing(fpath, intodic)
        else:
            return 0

    @classmethod
    def compress(cls, fname, data):
        buffer = SimpleLoggingDatabase.LineBuffer()
        for key in data:
            value = data[key]
            cls.put_value(key, value, buffer)
        fpath = os.path.join(cls.get_storage_dir(), "{}.logdb.txt".format(fname))
        with open(fpath, "w") as f: f.writelines(buffer.buffer)

    def __init__(self, file_name):
        self.fname = file_name
        self.data = {}
        log_size = SimpleLoggingDatabase.read(self.fname, self.data)
        if log_size > (5 * len(self.data)):
            print("Compressing sld {}".format(file_name))
            SimpleLoggingDatabase.compress(self.fname, self.data)

    def get(self, key, default_value):
        return self.data.get(key, default_value)

    def put(self, key, value, persist=True):
        old_value = self.data.get(key)
        changed = old_value != value
        self.data[key] = value
        if changed and persist:
            SimpleLoggingDatabase.write_put(self.fname, key, value)
class StringSerializer(SimpleLoggingDatabase.Serializer):
    def write(self, value, line_writer): line_writer.write(value)
    def read(self, line_reader):
        data = line_reader.read()
        return None if data == "None" else data
class FloatSerializer(SimpleLoggingDatabase.Serializer):
    def write(self, value, line_writer): line_writer.write(str(value))
    def read(self, line_reader):
        data = line_reader.read()
        return None if data == "None" else float(data)
class IntegerSerializer(SimpleLoggingDatabase.Serializer):
    def write(self, value, line_writer): line_writer.write(str(value))
    def read(self, line_reader):
        data = line_reader.read()
        return None if data == "None" else int(data)
class ListSerializer(SimpleLoggingDatabase.Serializer):
    def write(self, value, line_writer):
        line_writer.write(str(len(value)))
        for e in value:
            tp = str(type(e))
            serializer = SimpleLoggingDatabase.serializers.get(tp)
            if serializer:
                line_writer.write(tp)
                serializer.write(e, line_writer)
    def read(self, line_reader):
        data = []
        count = int(line_reader.read())
        for i in range(0, count):
            tp = line_reader.read()
            serializer = SimpleLoggingDatabase.serializers.get(tp)
            value = serializer.read(line_reader)
            data.append(value)
        return data
class VectorSerializer(SimpleLoggingDatabase.Serializer):
    def write(self, value, line_writer):
        if value is None: line_writer.write("None")
        else:
            line = ""
            for i in value: line += str(i) + " "
            line_writer.write(line)
    def read(self, line_reader):
        line = line_reader.read()
        if line == "None": return None
        data = line.rstrip().split(" ")
        components = [float(d) for d in data]
        return mathutils.Vector(components)
SimpleLoggingDatabase.serializers[str(type(""))] = StringSerializer()
SimpleLoggingDatabase.serializers[str(type(1.0))] = FloatSerializer()
SimpleLoggingDatabase.serializers[str(type(10))] = IntegerSerializer()
SimpleLoggingDatabase.serializers[str(type([]))] = ListSerializer()
SimpleLoggingDatabase.serializers[str(type((0,0,0)))] = ListSerializer()
SimpleLoggingDatabase.serializers[str(type(mathutils.Vector()))] = VectorSerializer()
#End of persistent maps

LO_AXIS_TO_STRING_CODE = {
    0:"X",1:"Y",2:"Z",
    3:"-X",4:"-Y",5:"-Z",
}

LO_AXIS_TO_VECTOR = {
    0:mathutils.Vector((1,0,0)), 1:mathutils.Vector((0,1,0)), 2:mathutils.Vector((0,0,1)),
    3:mathutils.Vector((-1,0,0)), 4:mathutils.Vector((0,-1,0)), 5:mathutils.Vector((0,0,-1)),
}

LOGIC_OPERATORS =[
    operator.eq,
    operator.ne,
    operator.gt,
    operator.lt,
    operator.ge,
    operator.le]


#distance between objects or vectors or tuples. None if not computable
def compute_distance(parama, paramb):
    if none_or_invalid(parama): return None
    if none_or_invalid(paramb): return None
    if hasattr(parama, "getDistanceTo"): return parama.getDistanceTo(paramb)
    if hasattr(paramb, "getDistanceTo"): return paramb.getDistanceTo(parama)
    va = mathutils.Vector(parama)
    vb = mathutils.Vector(paramb)
    return (va - vb).length

def xrot_to(rotating_object, target_pos, front_axis_code, speed, time_per_frame):
    front_vector = LO_AXIS_TO_VECTOR[front_axis_code]
    direction_vector = rotating_object.getVectTo(target_pos)[1]
    if speed is None:
        if front_axis_code >= 3:
            direction_vector.negate()
            front_axis_code = front_axis_code - 3
        rotating_object.alignAxisToVect(direction_vector, front_axis_code, 1.0)
        rotating_object.alignAxisToVect(LO_AXIS_TO_VECTOR[0], 0, 1.0)
        return True
    else:
        direction_vector = project_vector3(direction_vector, 1, 2)
        direction_vector.normalize()
        front_vector = rotating_object.getAxisVect(front_vector)
        front_vector = project_vector3(front_vector, 1, 2)
        signed_angle = direction_vector.angle_signed(front_vector, None)
        if signed_angle is None: return
        abs_angle = abs(signed_angle)
        if abs_angle < 0.01:
            return True
        angle_sign = (signed_angle > 0) - (signed_angle < 0)
        drot = angle_sign * speed * time_per_frame
        eulers = rotating_object.worldOrientation.to_euler()
        eulers[0] += drot
        rotating_object.worldOrientation = eulers
        return False
def yrot_to(rotating_object, target_pos, front_axis_code, speed, time_per_frame):
    front_vector = LO_AXIS_TO_VECTOR[front_axis_code]
    direction_vector = rotating_object.getVectTo(target_pos)[1]
    if speed is None:
        if front_axis_code >= 3:
            direction_vector.negate()
            front_axis_code = front_axis_code - 3
        rotating_object.alignAxisToVect(direction_vector, front_axis_code, 1.0)
        rotating_object.alignAxisToVect(LO_AXIS_TO_VECTOR[1], 1, 1.0)
        return True
    else:
        direction_vector = project_vector3(direction_vector, 2, 0)
        direction_vector.normalize()
        front_vector = rotating_object.getAxisVect(front_vector)
        front_vector = project_vector3(front_vector, 2, 0)
        signed_angle = direction_vector.angle_signed(front_vector, None)
        if signed_angle is None: return
        abs_angle = abs(signed_angle)
        if abs_angle < 0.01: return True
        angle_sign = (signed_angle > 0) - (signed_angle < 0)
        drot = angle_sign * speed * time_per_frame
        eulers = rotating_object.worldOrientation.to_euler()
        eulers[1] += drot
        rotating_object.worldOrientation = eulers
        return False
    pass
def zrot_to(rotating_object, target_pos, front_axis_code, speed, time_per_frame):
    front_vector = LO_AXIS_TO_VECTOR[front_axis_code]
    direction_vector = rotating_object.getVectTo(target_pos)[1]
    if speed is None:
        if front_axis_code >= 3:
            direction_vector.negate()
            front_axis_code = front_axis_code - 3
        rotating_object.alignAxisToVect(direction_vector, front_axis_code, 1.0)
        rotating_object.alignAxisToVect(LO_AXIS_TO_VECTOR[2], 2, 1.0)
        return True
    else:
        #project in 2d, compute angle diff, set euler rot 2
        direction_vector = project_vector3(direction_vector, 0, 1)
        direction_vector.normalize()
        front_vector = rotating_object.getAxisVect(front_vector)
        front_vector = project_vector3(front_vector, 0, 1)
        signed_angle = direction_vector.angle_signed(front_vector, None)
        if signed_angle is None: return True
        abs_angle = abs(signed_angle)
        if abs_angle < 0.01: return True
        angle_sign = (signed_angle > 0) - (signed_angle < 0)
        drot = angle_sign * speed * time_per_frame
        eulers = rotating_object.worldOrientation.to_euler()
        eulers[2] += drot
        rotating_object.worldOrientation = eulers
        return False
def rot_to(rot_axis_index, rotating_object, target_pos, front_axis_code, speed, time_per_frame):
    if rot_axis_index == 0:
        return xrot_to(rotating_object, target_pos, front_axis_code, speed, time_per_frame)
    elif rot_axis_index == 1:
        return yrot_to(rotating_object, target_pos, front_axis_code, speed, time_per_frame)
    elif rot_axis_index == 2:
        return zrot_to(rotating_object, target_pos, front_axis_code, speed, time_per_frame)
def move_to(moving_object, destination_point, speed, time_per_frame, dynamic, distance):
    if dynamic:
        direction = mathutils.Vector(destination_point) - moving_object.worldPosition
        dst = direction.length
        if(dst <= distance): return True
        direction.z = 0
        direction.normalize()
        velocity = direction * speed
        velocity.z = moving_object.worldLinearVelocity.z
        moving_object.worldLinearVelocity = velocity
        return False
    else:
        direction = mathutils.Vector(destination_point) - moving_object.worldPosition
        dst = direction.length
        if(dst <= distance): return True
        direction.normalize()
        displacement = speed * time_per_frame
        motion = direction * displacement
        moving_object.worldPosition += motion
        return False

def project_vector3(v, xi, yi): return mathutils.Vector((v[xi], v[yi]))

def none_or_invalid(ref):
    if ref is None: return True
    if not hasattr(ref, "invalid"): return False
    return ref.invalid


def invalid(ref):
    if ref is None: return False
    if not hasattr(ref, "invalid"): return False
    return ref.invalid


def _name_query(named_items, query):
    assert len(query) > 0
    postfix = (query[0] == "*")
    prefix = (query[-1] == "*")
    infix = (prefix and postfix)
    if infix:
        token = query[1:-1]
        for item in named_items:
            if token in item.name: return item
    if prefix:
        token = query[:-1]
        for item in named_items:
            if item.name.startswith(token): return item
    if postfix:
        token = query[1:]
        for item in named_items:
            if item.name.endswith(token): return item
    for item in named_items:
        if item.name == query: return item
    return None


_loaded_userlogic_files = {}
def load_user_logic(module_name):
    full_path = bge.logic.expandPath("//bgelogic/cells/{}.py".format(module_name))
    loaded_value = _loaded_userlogic_files.get(full_path)
    if loaded_value: return loaded_value
    import sys
    python_version = sys.version_info
    major = python_version[0]
    minor = python_version[1]
    if (major < 3) or (major == 3 and minor < 3):
        import imp
        loaded_value = imp.load_source(module_name, full_path)
    elif (major == 3) and (minor < 5):
        from importlib.machinery import SourceFileLoader
        loaded_value = SourceFileLoader(module_name, full_path).load_module()
    else:
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, full_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        loaded_value = module
    _loaded_userlogic_files[module_name] = loaded_value
    return loaded_value


def load_user_module(module_name):
    import sys
    exec("import {}".format(module_name))
    return sys.modules[module_name]


class StatefulValueProducer(object):
    def get_value(self): pass
    def has_status(self, status): pass


class LogicNetworkCell(StatefulValueProducer):
    class _Status(object):
        def __init__(self, name):
            self._name = name

        def __repr__(self):
            return self._name

    STATUS_WAITING = _Status("WAITING")
    STATUS_READY = _Status("READY")
    NO_VALUE = _Status("NO_VALUE")

    def __init__(self):
        self._uid = None
        self._status = LogicNetworkCell.STATUS_WAITING
        self._value = None
        self._children = []
        self.network = None
        pass

    def create_subcell(self, get_value_call):
        cell = LogicNetworkSubCell()

    def get_value(self):
        return self._value

    def _set_value(self, value):
        self._value = value

    def setup(self, network):
        """
        This is called by the network once, after all the cells have been loaded into the tree.
        :return: None
        """
        pass

    def stop(self, network):
        pass

    def _set_ready(self):
        self._status = LogicNetworkCell.STATUS_READY

    def _set_status(self, status):
        """
        Check the current status of the cell. Should return True if status equals the current status of the cell.
        :param status:
        :return:
        """
        self._status = status

    def has_status(self, status):
        return status == self._status

    def get_parameter_value(self, param):
        if isinstance(param, StatefulValueProducer):
            if param.has_status(LogicNetworkCell.STATUS_READY):
                return param.get_value()
            else:
                return LogicNetwork.STATUS_WAITING
        else:
            return param

    def reset(self):
        """
        Resets the status of the cell to LogicNetwork.STATUS_WAITING. A cell may override this to reset other states
        or to keep the value at STATUS_READY if evaluation is required to happen only once (or never at all)
        :return:
        """
        self._set_status(LogicNetworkCell.STATUS_WAITING)

    def evaluate(self):
        """
        A logic cell implements this method to do its job. The network evaluates a cell until its status becomes
         LogicNetwor.STATUS_READY. When that happens, the cell is removed from the update queue.
        :return:
        """
        raise NotImplementedError("{} doesn't implement evaluate".format(self.__class__.__name__))

    def _always_ready(self, status): return status is LogicNetworkCell.STATUS_READY
    def _skip_evaluate(self): return
    def deactivate(self):
        self.has_status = self._always_ready
        self.evaluate = self._skip_evaluate
    pass


class LogicNetworkSubCell(StatefulValueProducer):

    def __init__(self, owner, value_getter):
        self.owner = owner
        self.get_value = value_getter

    def has_status(self, status):
        return self.owner.has_status(status)
    pass


class ParameterCell(LogicNetworkCell):
    def __init__(self):
        LogicNetworkCell.__init__(self)


class ActionCell(LogicNetworkCell):
    def __init__(self):
        LogicNetworkCell.__init__(self)
    pass


class ConditionCell(LogicNetworkCell):
    def __init__(self):
        LogicNetworkCell.__init__(self)


class AudioSystem(object):
    def __init__(self):
        self.device = None
        self.factories = {}
    def get_or_create_audio_factory(self, fpath):
        if self.device is None:
            self.device = aud.device()
        fac = self.factories.get(fpath, None)
        fpath = bge.logic.expandPath(fpath)
        if fac is None:
            fac = aud.Factory(fpath)
        return fac
    def create_sound_handle(self, fpath):
        factory = self.get_or_create_audio_factory(fpath)
        handle = self.device.play(factory)
        return handle
    def compute_listener_velocity(self, listener):
        return (0,0,0)
    def update(self, network):
        device = self.device
        if not device: return#do not update if no sound has been installed
        #update the listener data
        scene = network._owner.scene
        listener = scene.active_camera
        device.listener_location = listener.worldPosition
        device.listener_orientation = listener.worldOrientation.to_quaternion()
        device.listener_velocity = self.compute_listener_velocity(listener)
        pass


class LogicNetwork(LogicNetworkCell):
    def __init__(self):
        LogicNetworkCell.__init__(self)
        self._cells = []
        self._iter = collections.deque()
        self._lastuid = 0
        self._owner = None
        self._max_blocking_loop_count = 0
        self.keyboard = None
        self.mouse = None
        self.keyboard_events = None
        self.active_keyboard_events = None
        self.mouse_events = None
        self.stopped = False
        self.timeline = 0.0
        self._time_then = None
        self.time_per_frame = 0.0
        self._last_mouse_position = [bge.logic.mouse.position[0], bge.logic.mouse.position[1]]
        self.mouse_motion_delta = [0.0, 0.0]
        self.mouse_wheel_delta = 0
        self.audio_system = AudioSystem()
        self.sub_networks = []#a list of networks updated by this network
        self.capslock_pressed = False
        pass

    def ray_cast(self, caster_object, ray_origin, ray_destination, property, distance):
        now = time.time()
        cached_data = caster_object.get("_NL_ray_cast_data")
        if cached_data is not None:
            data_time = cached_data[0]
            data_origin = cached_data[1]
            data_destination = cached_data[2]
            data_property = cached_data[3]
            data_distance = cached_data[4]
            d_time = now - data_time
            if d_time < 0.01:#only if we are in the same frame, otherwise scenegraph might have changed
                if (data_origin == ray_origin) and (data_destination == ray_destination) and (data_property == property) and (data_distance == distance):
                    return cached_data[5]
            pass
        obj, point, normal = None, None, None
        if property is not None:
            obj, point, normal = caster_object.rayCast(ray_destination, ray_origin, distance, property)
        else:
            obj, point, normal = caster_object.rayCast(ray_destination, ray_origin, distance)
        cached_data = (now, ray_origin, ray_destination, property, distance, (obj, point, normal))
        caster_object["_NL_ray_cast_data"] = cached_data
        return obj, point, normal

    def set_mouse_position(self, screen_x, screen_y):
        self.mouse.position = (screen_x, screen_y)
        self._last_mouse_position = [screen_x, screen_y]
        pass

    def get_owner(self):
        return self._owner

    def setup(self):
        self.time_per_frame = 0.0
        for cell in self._cells:
            cell.network = self
            cell.setup(self)
        self._last_mouse_position[:] = bge.logic.mouse.position

    def is_running(self):
        return not self.stopped

    def is_stopped(self):
        return self.stopped

    def stop(self, network=None):
        if self.stopped: return
        self._time_then = None
        self.stopped = True
        for cell in self._cells:
            cell.stop(self)

    def _generate_cell_uid(self):
        self._lastuid += 1
        return self._lastuid

    def add_cell(self, cell):
        self._cells.append(cell)
        self._iter.append(cell)
        self._max_blocking_loop_count = len(self._cells) * len(self._cells)
        cell._uid = self._generate_cell_uid()
        return cell

    def evaluate(self):
        now = time.time()
        if self._time_then is None: self._time_then = now
        dtime = now - self._time_then
        self._time_then = now
        self.timeline += dtime
        self.time_per_frame = dtime
        if self._owner.invalid:
            print("Network Owner removed from game. Shutting down the network")
            return True
        self.keyboard = bge.logic.keyboard
        self.mouse = bge.logic.mouse
        #compute mouse translation since last frame (or initialization)
        curr_mpos = self.mouse.position
        last_mpos = self._last_mouse_position
        mpos_delta = self.mouse_motion_delta
        mpos_delta[0] = curr_mpos[0] - last_mpos[0]
        mpos_delta[1] = curr_mpos[1] - last_mpos[1]
        last_mpos[:] = curr_mpos
        #store mouse and keyboard events to be used by cells
        self.keyboard_events = self.keyboard.events.copy()
        self.active_keyboard_events = self.keyboard.active_events.copy()
        caps_lock_event = self.keyboard_events[bge.events.CAPSLOCKKEY]
        if(caps_lock_event == bge.logic.KX_INPUT_JUST_RELEASED):
            self.capslock_pressed = not self.capslock_pressed
        me = self.mouse.events
        self.mouse_wheel_delta = 0
        if(me[bge.events.WHEELUPMOUSE] == bge.logic.KX_INPUT_JUST_ACTIVATED): self.mouse_wheel_delta = 1
        elif(me[bge.events.WHEELDOWNMOUSE] == bge.logic.KX_INPUT_JUST_ACTIVATED): self.mouse_wheel_delta = -1
        self.mouse_events = me
        #update the cells
        cells = self._iter
        max_loop_count = len(cells)
        loop_index = 0
        while cells:
            if loop_index == self._max_blocking_loop_count:
                print("Network found a blocking condition (due to unconnected or non responsive cell)")
                print("Cells awaiting evaluation: ")
                for c in cells: print(c)
                print("Stopping network...")
                self.stop()
                return
            cell = cells.popleft()
            cell.evaluate()
            if not cell.has_status(LogicNetworkCell.STATUS_READY):
                cells.append(cell)
            loop_index += 1
        if(loop_index > max_loop_count):
            print("Wrong sorting alghorythm..itm..ymthf..ssss", loop_index, max_loop_count)
        for cell in self._cells:
            cell.reset()
            if cell.has_status(LogicNetworkCell.STATUS_WAITING):
                cells.append(cell)
        #update the sound system
        self.audio_system.update(self)
        #pulse subnetworks
        for network in self.sub_networks:
            if network._owner.invalid:
                self.sub_networks.remove(network)
            elif network.is_running():
                network.evaluate()
        pass

    def install_subnetwork(self, owner_object, node_tree_name, initial_status):
        #transform the tree name into a NL module name
        valid_characters = "abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        stripped_name = "".join([c for c in node_tree_name if c in valid_characters])
        if stripped_name in owner_object:
            print("Network {} already installed for {}".format(stripped_name, owner_object.name))
            if(initial_status is True): owner_object[node_tree_name].stopped = False
        else:
            print("Installing sub network...")
            initial_status_key = 'NL_{}_initial_status'.format(node_tree_name)
            owner_object[initial_status_key] = initial_status
            module_name = 'bgelogic.NL{}'.format(stripped_name)
            module = load_user_module(module_name)
            module._initialize(owner_object)
            subnetwork = owner_object[node_tree_name]
            self.sub_networks.append(subnetwork)
    pass

#Parameter Cells
class ParamOwnerObject(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)

    def setup(self, network):
        ParameterCell.setup(self, network)
        self._set_status(LogicNetworkCell.STATUS_READY)
        self._set_value(network.get_owner())

    def reset(self): pass

    def evaluate(self): pass


class ParameterBoneStatus(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self.armature = None
        self.bone_name = None
        self._prev_armature = LogicNetworkCell.NO_VALUE
        self._prev_bone = LogicNetworkCell.NO_VALUE
        self._channel = None
        self._pos = mathutils.Vector((0,0,0))
        self._rot = mathutils.Euler((0,0,0), "XYZ")
        self._sca = mathutils.Vector((0,0,0))
        self.XYZ_POS = LogicNetworkSubCell(self, self._get_pos)
        self.XYZ_ROT = LogicNetworkSubCell(self, self._get_rot)
        self.XYZ_SCA = LogicNetworkSubCell(self, self._get_sca)
    def _get_pos(self):
        return self._pos
    def _get_sca(self):
        return self._sca
    def _get_rot(self):
        return self._rot
    def evaluate(self):
        armature = self.get_parameter_value(self.armature)
        bone_name = self.get_parameter_value(self.bone_name)
        if armature is LogicNetworkCell.STATUS_WAITING: return
        if bone_name is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(armature): return
        if not bone_name: return
        channel = None
        if (armature is self._prev_armature) and (bone_name == self._prev_bone):
            channel = self._channel
        else:
            self._prev_armature = armature
            self._prev_bone = bone_name
            self._channel = armature.channels[bone_name]
            channel = self._channel
        if channel.rotation_mode is bge.logic.ROT_MODE_QUAT:
            self._rot[:] = mathutils.Quaternion(channel.rotation_quaternion).to_euler()
        else:
            self._rot[:] = channel.rotation_euler
        self._pos[:] = channel.location
        self._sca[:] = channel.scale


class ParameterCurrentScene(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self._set_ready()

    def get_value(self):
        return bge.logic.getCurrentScene()

    def reset(self): pass
    def evaluate(self): pass


class ParameterParentGameObject(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self.game_object = None
    def evaluate(self):
        self._set_ready()
        go = self.get_parameter_value(self.game_object)
        if none_or_invalid(go): return self._set_value(None)
        self._set_value(go.parent)


class ParameterSwitchValue(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self.param_a = None
        self.param_b = None
        self.switch_condition = None

    def evaluate(self):
        a = self.get_parameter_value(self.param_a)
        b = self.get_parameter_value(self.param_b)
        cond = self.get_parameter_value(self.switch_condition)
        if a is LogicNetworkCell.STATUS_WAITING: return
        if b is LogicNetworkCell.STATUS_WAITING: return
        if cond is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        self._set_value(a if cond else b)


class ParameterObjectProperty(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self.game_object = None
        self.property_name = None
        self.property_default = None

    def evaluate(self):
        game_object = self.get_parameter_value(self.game_object)
        property_name = self.get_parameter_value(self.property_name)
        property_default = self.get_parameter_value(self.property_default)
        if game_object is LogicNetworkCell.STATUS_WAITING: return
        if property_name is LogicNetworkCell.STATUS_WAITING: return
        if property_default is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(game_object) or (not property_name):
            self._set_value(property_default)
        else:
            self._set_value(game_object.get(property_name, property_default))


class ParameterActiveCamera(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self.scene = None
    def evaluate(self):
        scene = self.get_parameter_value(self.scene)
        if scene is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(scene):
            self._set_value(None)
        else:
            self._set_value(scene.active_camera)


class ParameterScreenPosition(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self.game_object = None
        self.camera = None
        self.xposition = LogicNetworkSubCell(self, self._get_xposition)
        self.yposition = LogicNetworkSubCell(self, self._get_yposition)
        self._xpos = None
        self._ypos = None
    def _get_xposition(self): return self._xpos
    def _get_yposition(self): return self._ypos
    def evaluate(self):
        self._set_ready()
        game_object = self.get_parameter_value(self.game_object)
        camera = self.get_parameter_value(self.camera)
        if none_or_invalid(game_object) or none_or_invalid(camera):
            self._xpos = None
            self._ypos = None
            self._set_value(None)
            return
        position = camera.getScreenPosition(game_object)
        self._set_value(position)
        self._xpos = position[0]
        self._ypos = position[1]
        pass
    pass


class ParameterWorldPosition(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self.camera = None
        self.screen_x = None
        self.screen_y = None
        self.world_z = None
    def evaluate(self):
        self._set_ready()
        camera = self.get_parameter_value(self.camera)
        screen_x = self.get_parameter_value(self.screen_x)
        screen_y = self.get_parameter_value(self.screen_y)
        world_z = self.get_parameter_value(self.world_z)
        if none_or_invalid(camera) or (screen_x is None) or (screen_y is None) or (world_z is None):
            self._set_value(None)
        else:
            direction = camera.getScreenVect(screen_x, screen_y)
            origin = direction + camera.worldPosition
            point = origin + (direction * -world_z)
            self._set_value(point)
        pass
    pass


class ParameterPythonModuleFunction(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self.IN0 = None
        self.IN1 = None
        self.IN2 = None
        self.IN3 = None
        self.OUT0 = LogicNetworkSubCell(self, self.get_out_0)
        self.OUT1 = LogicNetworkSubCell(self, self.get_out_1)
        self.OUT2 = LogicNetworkSubCell(self, self.get_out_2)
        self.OUT3 = LogicNetworkSubCell(self, self.get_out_3)
        self.inputs = [None, None, None, None]
        self.outputs = [None, None, None, None]
        self.module_name = None
        self.module_func = None
        self._old_mod_name = None
        self._old_mod_fun = None
        self._module = None
        self._modfun = None

    def get_out_0(self): return self.outputs[0]
    def get_out_1(self): return self.outputs[1]
    def get_out_2(self): return self.outputs[2]
    def get_out_3(self): return self.outputs[3]

    def evaluate(self):
        mname = self.get_parameter_value(self.module_name)
        mfun = self.get_parameter_value(self.module_func)
        in0 = self.get_parameter_value(self.IN0)
        in1 = self.get_parameter_value(self.IN1)
        in2 = self.get_parameter_value(self.IN2)
        in3 = self.get_parameter_value(self.IN3)
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        if mname is STATUS_WAITING: return
        if mfun is STATUS_WAITING: return
        if in0 is STATUS_WAITING: return
        if in1 is STATUS_WAITING: return
        if in2 is STATUS_WAITING: return
        if in3 is STATUS_WAITING: return
        self._set_ready()
        if (not mname) or (not mfun):
            if in0: print("Debug {} {} {} {}".format(in0, in1, in2, in3))
            return
        if mname and (self._old_mod_name != mname):
            exec("import {}".format(mname))
            self._old_mod_name = mname
            self._module = eval(mname)
        if self._old_mod_fun != mfun:
            self._modfun = getattr(self._module, mfun)
            self._old_mod_fun = mfun
        inputs = self.inputs
        inputs[:] = (in0, in1, in2, in3)
        self._modfun(self)


class ParameterTime(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self.network = None
        self.TIME_PER_FRAME = LogicNetworkSubCell(self, self.get_time_per_frame)
        self.TIMELINE = LogicNetworkSubCell(self, self.get_timeline)
    def get_time_per_frame(self): return self.network.time_per_frame
    def get_timeline(self): return self.network.timeline
    def setup(self, network):
        self.network = network
    def has_status(self, status): return status is LogicNetworkCell.STATUS_READY
    def evaluate(self): pass


class ParameterObjectAttribute(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self.game_object = None
        self.attribute_name = None
    def evaluate(self):
        game_object = self.get_parameter_value(self.game_object)
        attribute_name = self.get_parameter_value(self.attribute_name)
        if game_object is LogicNetworkCell.STATUS_WAITING: return
        if attribute_name is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(game_object): return
        self._set_value(getattr(game_object, attribute_name))


class ParameterArithmeticOp(ParameterCell):
    @classmethod
    def op_by_code(cls, str):
        import operator
        opmap = {
            "ADD":operator.add,
            "SUB":operator.sub,
            "DIV":operator.truediv,
            "MUL":operator.mul
        }
        return opmap.get(str)
    def __init__(self):
        ParameterCell.__init__(self)
        self.operand_a = None
        self.operand_b = None
        self.operator = None
    def evaluate(self):
        a = self.get_parameter_value(self.operand_a)
        b = self.get_parameter_value(self.operand_b)
        if a is LogicNetworkCell.STATUS_WAITING: return
        if b is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if (a is None) or (b is None):
            self._set_value(None)
        else:
            self._set_value(self.operator(a, b))


class ParameterValueFilter3(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self.opcode = None
        self.parama = None
        self.paramb = None
        self.paramc = None
    def evaluate(self):
        opcode = self.get_parameter_value(self.opcode)
        parama = self.get_parameter_value(self.parama)
        paramb = self.get_parameter_value(self.paramb)
        paramc = self.get_parameter_value(self.paramc)
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        if opcode is STATUS_WAITING: return
        if parama is STATUS_WAITING: return
        self._set_ready()
        if opcode == 1:#limit a between b and c
            if parama is None: return
            if paramb is None: return
            if paramc is None: return
            self._set_value(parama)
            if parama < paramb: self._set_value(paramb)
            if parama > paramc: self._set_value(paramc)


class ParameterActionStatus(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self.game_object = None
        self.action_layer = None
        self._action_name = ""
        self._action_frame = 0.0
        self.NOT_PLAYING = LogicNetworkSubCell(self, self.get_not_playing)
        self.ACTION_NAME = LogicNetworkSubCell(self, self.get_action_name)
        self.ACTION_FRAME = LogicNetworkSubCell(self, self.get_action_frame)

    def get_action_name(self):
        return self._action_name

    def get_action_frame(self):
        return self._action_frame
    
    def get_not_playing(self):
        return not self.get_value()

    def evaluate(self):
        game_object = self.get_parameter_value(self.game_object)
        action_layer = self.get_parameter_value(self.action_layer)
        if game_object is LogicNetworkCell.STATUS_WAITING: return
        if action_layer is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(game_object):
            self._action_name = ""
            self._action_frame = 0.0
            self._set_value(False)
        else:
            self._set_value(game_object.isPlayingAction(action_layer))
            self._action_name = game_object.getActionName(action_layer)
            self._action_frame = game_object.getActionFrame(action_layer)


class ParameterMouseData(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self.MX = LogicNetworkSubCell(self, self.getmx)
        self.MY = LogicNetworkSubCell(self, self.getmy)
        self.MDX = LogicNetworkSubCell(self, self.getmdx)
        self.MDY = LogicNetworkSubCell(self, self.getmdy)
        self.MDWHEEL = LogicNetworkSubCell(self, self.getmdwheel)
        self.MXY0 = LogicNetworkSubCell(self, self.getmxyz)
        self.MDXY0 = LogicNetworkSubCell(self, self.getmdxyz)

    def getmx(self): return self.network._last_mouse_position[0]
    def getmy(self): return self.network._last_mouse_position[1]
    def getmdx(self): return self.network.mouse_motion_delta[0]
    def getmdy(self): return self.network.mouse_motion_delta[1]
    def getmdwheel(self): return self.network.mouse_wheel_delta
    def getmxyz(self):
        mp = self.network._last_mouse_position
        return mathutils.Vector((mp[0], mp[1], 0))
    def getmdxyz(self):
        mp = self.network.mouse_motion_delta
        return mathutils.Vector((mp[0], mp[1], 0))
    def evaluate(self):
        self._set_ready()
    def has_status(self, status):
        return status is LogicNetworkCell.STATUS_READY


class ParameterOrientation(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self.source_matrix = None
        self.input_x = None
        self.input_y = None
        self.input_z = None
        self.OUTX = LogicNetworkSubCell(self, self.get_out_x)
        self.OUTY = LogicNetworkSubCell(self, self.get_out_y)
        self.OUTZ = LogicNetworkSubCell(self, self.get_out_z)
        self.OUTEULER = LogicNetworkSubCell(self, self.get_out_euler)
        self._matrix = mathutils.Matrix.Identity(3)
        self._eulers = mathutils.Euler((0,0,0), "XYZ")
        pass

    def get_out_x(self): return self._eulers[0]
    def get_out_y(self): return self._eulers[1]
    def get_out_z(self): return self._eulers[2]
    def get_out_euler(self): return self._eulers

    def evaluate(self):
        source_matrix = self.get_parameter_value(self.source_matrix)
        input_x = self.get_parameter_value(self.input_x)
        input_y = self.get_parameter_value(self.input_y)
        input_z = self.get_parameter_value(self.input_z)
        if source_matrix is LogicNetworkCell.STATUS_WAITING: return
        if input_x is LogicNetworkCell.STATUS_WAITING: return
        if input_y is LogicNetworkCell.STATUS_WAITING: return
        if input_z is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        matrix = self._matrix
        eulers = self._eulers
        eulers.zero()
        matrix.identity()
        if source_matrix is not None:
            matrix[:] = source_matrix
        eulers.rotate(matrix)
        mutate = False
        if (input_x is not None):
            eulers[0] = input_x
            mutate = True
        if (input_y is not None):
            eulers[1] = input_y
            mutate = True
        if (input_z is not None):
            eulers[2] = input_z
            mutate = True
        if mutate:
            matrix = eulers.to_matrix()
        self._set_value(matrix)


class ParameterVector(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self.input_vector = None
        self.input_x = None
        self.input_y = None
        self.input_z = None
        self.output_vector = mathutils.Vector()
        self.OUTX = LogicNetworkSubCell(self, self.get_out_x)
        self.OUTY = LogicNetworkSubCell(self, self.get_out_y)
        self.OUTZ = LogicNetworkSubCell(self, self.get_out_z)
        self.OUTV = LogicNetworkSubCell(self, self.get_out_v)
        self.NORMVEC = LogicNetworkSubCell(self, self.get_normalized_vector)

    def get_out_x(self): return self.output_vector.x
    def get_out_y(self): return self.output_vector.y
    def get_out_z(self): return self.output_vector.z
    def get_out_v(self): return self.output_vector.copy()
    def get_normalized_vector(self): return self.output_vector.normalized()

    def evaluate(self):
        self._set_ready()
        x = self.get_parameter_value(self.input_x)
        y = self.get_parameter_value(self.input_y)
        z = self.get_parameter_value(self.input_z)
        v = self.get_parameter_value(self.input_vector)
        if v is not None: self.output_vector[:] = v#TODO: zero vector if v is None?
        if x is not None: self.output_vector.x = x
        if y is not None: self.output_vector.y = y
        if z is not None: self.output_vector.z = z
        self._set_value(self.output_vector)

class ParameterVector4(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self.in_x = None
        self.in_y = None
        self.in_z = None
        self.in_w = None
        self.in_vec = None
        self.out_x = 0
        self.out_y = 0
        self.out_z = 0
        self.out_w = 1
        self.out_vec = mathutils.Vector((0,0,0,1))
        self.OUTX = LogicNetworkSubCell(self, self._get_out_x)
        self.OUTY = LogicNetworkSubCell(self, self._get_out_y)
        self.OUTZ = LogicNetworkSubCell(self, self._get_out_z)
        self.OUTW = LogicNetworkSubCell(self, self._get_out_w)
        self.OUTVEC = LogicNetworkSubCell(self, self._get_out_vec)
    def _get_out_x(self): return self.out_x
    def _get_out_y(self): return self.out_y
    def _get_out_z(self): return self.out_z
    def _get_out_w(self): return self.out_w
    def _get_out_vec(self): return self.out_vec.copy()
    def get_parameter_value(self, param, default_value):
        if param is None: return default_value
        elif hasattr(param, "get_value"):
            value = param.get_value()
            if(value is LogicNetwork.STATUS_WAITING): raise "Unexpected error in tree"
            else: return value
        else: return param
    def evaluate(self):
        self._set_ready()
        x = self.get_parameter_value(self.in_x, None)
        y = self.get_parameter_value(self.in_y, None)
        z = self.get_parameter_value(self.in_z, None)
        w = self.get_parameter_value(self.in_w, None)
        vec = self.get_parameter_value(self.in_vec, None)
        if(vec is not None):
            #out is vec with vec components replaced by non null x,y,z,w
            self.out_x = vec.x if x is None else x
            self.out_y = vec.y if y is None else y
            self.out_z = vec.z if z is None else z
            self.out_w = 1
            if(len(vec) >= 4):
                self.out_w = vec.w if w is None else w
            elif(w is not None):
                self.out_w = w
            self.out_vec[:] = (self.out_x, self.out_y, self.out_z, self.out_w)
        else:
            #in vec is None
            self.out_x = 0 if x is None else x
            self.out_y = 0 if y is None else y
            self.out_z = 0 if z is None else z
            self.out_w = 1 if w is None else w
            self.out_vec[:] = (self.out_x, self.out_y, self.out_z, self.out_w)
            pass
        pass
    pass

class ParameterSound(ParameterCell):
    class SoundHandleController():
        def __init__(self, ps_cell):
            self.owner = ps_cell
            self.handle = None
        def update(self, location, orientation_quat, velocity, pitch, volume, loop_count, attenuation, distance_ref, distance_max):
            handle = self.handle
            if handle is None: return
            if not (handle.status == aud.AUD_STATUS_PLAYING): return
            if location is not None: handle.location = location
            if orientation_quat is not None: handle.orientation = orientation_quat
            if velocity is not None: handle.velocity = velocity
            if volume is not None: handle.volume = volume
            if pitch is not None: handle.pitch = pitch
            if loop_count is not None: handle.loop_count = loop_count
            if attenuation is not None: handle.attenuation = attenuation
            if distance_ref is not None: handle.distance_reference = distance_ref
            if distance_max is not None: handle.distance_maximum = distance_max
        def play(self, location, orientation_quat, velocity, pitch, volume, loop_count, attenuation, distance_ref, distance_max):
            handle = self.handle
            if handle is None or (handle.status == aud.AUD_STATUS_STOPPED) or (handle.status == aud.AUD_STATUS_INVALID):
                handle = self.owner.create_handle()
                handle.relative = False
                self.handle = handle
            elif handle.status == aud.AUD_STATUS_PLAYING:
                handle.position = 0.0
            if handle.status == aud.AUD_STATUS_PAUSED:
                handle.resume()
            if location is not None: handle.location = location
            if orientation_quat is not None: handle.orientation = orientation_quat
            if velocity is not None: handle.velocity = velocity
            if volume is not None: handle.volume = volume
            if pitch is not None: handle.pitch = pitch
            if loop_count is not None: handle.loop_count = loop_count
            if attenuation is not None: handle.attenuation = attenuation
            if distance_ref is not None: handle.distance_reference = distance_ref
            if distance_max is not None: handle.distance_maximum = distance_max
        def stop(self):
            handle = self.handle
            if handle is not None:
                if handle.status == aud.AUD_STATUS_INVALID:
                    self.handle = None
                else:
                    handle.stop()
                    self.handle = None
        def pause(self):
            handle = self.handle
            if handle is not None:
                if handle.status == aud.AUD_STATUS_INVALID:
                    self.handle = None
                else:
                    handle.pause()
        def is_playing(self):
            handle = self.handle
            if handle is None: return False
            if handle.status == aud.AUD_STATUS_PLAYING:
                return True
            return False
        def get_frame(self):
            if self.is_playing():
                return self.handle.position
            return 0.0
        pass

    def __init__(self):
        ParameterCell.__init__(self)
        self.file_path = None
        self._loaded_path = None
        self._file_path_value = None
        self._factory = None
        self.network = None
        self.controller = self.__class__.SoundHandleController(self)
        self.IS_PLAYING = LogicNetworkSubCell(self, self._is_playing)
        self.CURRENT_FRAME = LogicNetworkSubCell(self, self._current_frame)
    def _is_playing(self):
        return self.controller.is_playing()
    def _current_frame(self):
        return self.controller.get_frame()
    def create_handle(self):
        return self.network.audio_system.create_sound_handle(self._file_path_value)
    def get_value(self):
        return self.controller
    def setup(self, network):
        self.network = network
    def dispose_loaded_audio(self):
        if not self._loaded_path: return
        self._loaded_path = None
        self._handle = None
    def load_audio(self, fpath):
        self._loaded_path = fpath
        self._factory = self.network.audio_system.get_or_create_audio_factory(fpath)
    def evaluate(self):
        file_path = self.get_parameter_value(self.file_path)
        if file_path is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if file_path != self._loaded_path:
            self._file_path_value = file_path
            self.dispose_loaded_audio()
            self.load_audio(file_path)
            pass


#Condition cells
class ConditionAlways(ConditionCell):
    def __init__(self):
        ConditionCell.__init__(self)
        self.repeat = False
        self._set_status(LogicNetworkCell.STATUS_READY)
        self._value = True

    def reset(self):
        if not self.repeat: self._value = False
        pass

    def evaluate(self):
        pass
    pass


class ConditionOnce(ConditionCell):

    def __init__(self):
        ConditionCell.__init__(self)
        self.input_condition = None
        self._consumed = False

    def has_status(self, status):
        if self._consumed:
            return status is LogicNetworkCell.STATUS_READY
        else:
            return ConditionCell.has_status(self, status)

    def reset(self):
        if self._consumed:
            self._set_status(LogicNetworkCell.STATUS_READY)
            self._set_value(False)
        else:
            self._set_status(LogicNetworkCell.STATUS_WAITING)

    def evaluate(self):
        input_condition = self.get_parameter_value(self.input_condition)
        if input_condition is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if input_condition:
            self._consumed = True
            self._set_value(True)


class ConditionNot(ConditionCell):
    def __init__(self):
        ConditionCell.__init__(self)
        self.condition = None
        self.pulse = None
        self._old_condition = None

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        pulse = self.get_parameter_value(self.pulse)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        if pulse is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if (not pulse) and (condition is self._old_condition):
            self._set_value(False)
        else:
            self._set_value(not condition)
            self._old_condition = condition


class ConditionLNStatus(ConditionCell):
    def __init__(self):
        ConditionCell.__init__(self)
        self.game_object = None
        self.tree_name = None
        self._running = False
        self._stopped = False
        self.IFRUNNING = LogicNetworkSubCell(self, self.get_running)
        self.IFSTOPPED = LogicNetworkSubCell(self, self.get_stopped)

    def get_running(self): return self._running
    def get_stopped(self): return self._stopped

    def evaluate(self):
        game_object = self.get_parameter_value(self.game_object)
        tree_name = self.get_parameter_value(self.tree_name)
        if game_object is LogicNetworkCell.STATUS_WAITING: return
        if tree_name is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        self._running = False
        self._stopped = False
        if none_or_invalid(game_object): return
        tree = game_object.get(tree_name)
        if tree is None: return
        self._running = tree.is_running()
        self._stopped = tree.is_stopped()


class ConditionMouseScrolled(ConditionCell):
    def __init__(self):
        ConditionCell.__init__(self)
        self.wheel_direction = None
    def evaluate(self):
        wd = self.get_parameter_value(self.wheel_direction)
        if wd is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if wd is None: return
        elif wd == 1:#UP
            self._set_value(self.network.mouse_wheel_delta == 1)
        elif wd == 2:#DOWN
            self._set_value(self.network.mouse_wheel_delta == -1)
        elif wd == 3:#UP OR DOWN
            self._set_value(self.network.mouse_wheel_delta != 0)


class ConditionValueChanged(ConditionCell):
    def __init__(self):
        ConditionCell.__init__(self)
        self._previous_value = None
        self._current_value = None
        self.current_value = None
        self.initialize = False
        self.PREVIOUS_VALUE = LogicNetworkSubCell(self, self.get_previous_value)
        self.CURRENT_VALUE = LogicNetworkSubCell(self, self.get_current_value)
    def get_previous_value(self):
        return self._previous_value
    def get_current_value(self):
        return self._current_value
    def reset(self):
        ConditionCell.reset(self)
        self._set_value(False)
        self._previous_value = self._current_value
    def evaluate(self):
        curr = self.get_parameter_value(self.current_value)
        if curr is LogicNetworkCell.STATUS_WAITING: return
        self._current_value = curr
        self._set_ready()
        if self.initialize:
            self._previous_value = curr
            self._set_value(False)
            self.initialize = False
        else:
            changed = self._previous_value != curr
            if changed:
                self._set_value(changed)


class ConditionValueTrigger(ConditionCell):
    def __init__(self):
        super().__init__()
        self.monitored_value = None
        self.trigger_value = None
        self._last_value = LogicNetworkCell.NO_VALUE

    def evaluate(self):
        monitored_value = self.get_parameter_value(self.monitored_value)
        trigger_value = self.get_parameter_value(self.trigger_value)
        if monitored_value is LogicNetworkCell.STATUS_WAITING: return
        if trigger_value is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if self._last_value is LogicNetworkCell.NO_VALUE:#initialize the value
            self._last_value = monitored_value
            self._set_value(False)
            pass
        else:
            value_changed = (monitored_value != self._last_value)
            is_trigger = (monitored_value == trigger_value)
            if value_changed:
                self._last_value = monitored_value
                self._set_value(is_trigger)
            else:
                self._set_value(False)


class ConditionLogicOp(ConditionCell):
    def __init__(self):
        ConditionCell.__init__(self)
        self.param_a = None
        self.param_b = None
        self.operator = None

    def evaluate(self):
        a = self.get_parameter_value(self.param_a)
        b = self.get_parameter_value(self.param_b)
        operator = self.get_parameter_value(self.operator)
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        if a is STATUS_WAITING: return
        if b is STATUS_WAITING: return
        if operator is STATUS_WAITING: return
        self._set_ready()
        if operator > 1:#eq and neq ar valid for None
            if a is None: return
            if b is None: return
        if operator is None: return
        self._set_value(LOGIC_OPERATORS[operator](a, b))


class ConditionDistanceCheck(ConditionCell):
    def __init__(self):
        ConditionCell.__init__(self)
        self.param_a = None
        self.param_b = None
        self.operator = None
        self.dist = None
        self.hyst = None
        self._check = self._strict_check
    def _strict_check(self, opindex, value, hyst, threshold):
        v = LOGIC_OPERATORS[opindex](value, threshold)
        if v is True:
            self._set_value(True)
        else:
            self._set_value(False)
            self._check = self._hyst_check
        pass
    def _hyst_check(self, opindex, value, hyst, threshold):
        if (opindex == 2) or (opindex == 4):
            v = LOGIC_OPERATORS[opindex](value, threshold + hyst)
            if v is True:
                self._set_value(True)
                self._check = self._strict_check
            else:
                self._set_value(False)
        elif (opindex == 3) or (opindex == 5):
            v = LOGIC_OPERATORS[opindex](value, threshold - hyst)
            if v is True:
                self._set_value(True)
                self._check = self._strict_check
            else:
                self._set_value(False)
    def evaluate(self):
        a = self.get_parameter_value(self.param_a)
        b = self.get_parameter_value(self.param_b)
        op = self.get_parameter_value(self.operator)
        dist = self.get_parameter_value(self.dist)
        hyst = self.get_parameter_value(self.hyst)
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        if a is STATUS_WAITING: return
        if b is STATUS_WAITING: return
        if op is STATUS_WAITING: return
        if dist is STATUS_WAITING: return
        if hyst is STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(a): return
        if none_or_invalid(b): return
        if op is None: return
        if dist is None: return
        distance = compute_distance(a, b)
        if distance is None: return self._set_value(False)
        if hyst is None:#plain check, no threshold
            v = LOGIC_OPERATORS[op](distance, dist)
            self._set_value(v)
        else:#check with hysteresys value, if >, >=, <, <=
            self._check(op, distance, hyst, dist)

class ConditionAnd(ConditionCell):
    def __init__(self):
        ConditionCell.__init__(self)
        self.condition_a = None
        self.condition_b = None

    def evaluate(self):
        ca = self.get_parameter_value(self.condition_a)
        cb = self.get_parameter_value(self.condition_b)
        if ca is LogicNetworkCell.STATUS_WAITING: return
        if cb is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        self._set_value(ca and cb)
    pass


class ConditionNotNone(ConditionCell):

    def __init__(self):
        ConditionCell.__init__(self)
        self.checked_value = None

    def evaluate(self):
        value = self.get_parameter_value(self.checked_value)
        if value is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        self._set_value(value != None)


class ConditionNone(ConditionCell):
    def __init__(self):
        ConditionCell.__init__(self)
        self.checked_value = None
    def evaluate(self):
        self._set_ready()
        value = self.get_parameter_value(self.checked_value)
        self._set_value(value == None)
        pass
    pass


class ConditionOr(ConditionCell):
    def __init__(self):
        ConditionCell.__init__(self)
        self.condition_a = None
        self.condition_b = None

    def evaluate(self):
        ca = self.get_parameter_value(self.condition_a)
        cb = self.get_parameter_value(self.condition_b)
        if ca is LogicNetworkCell.STATUS_WAITING: return
        if cb is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        self._set_value(ca or cb)


class ConditionOrList(ConditionCell):
    def __init__(self):
        ConditionCell.__init__(self)
        self.ca = False
        self.cb = False
        self.cc = False
        self.cd = False
        self.ce = False
        self.cf = False
    def evaluate(self):
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        ca = self.get_parameter_value(self.ca)
        cb = self.get_parameter_value(self.cb)
        cc = self.get_parameter_value(self.cc)
        cd = self.get_parameter_value(self.cd)
        ce = self.get_parameter_value(self.ce)
        cf = self.get_parameter_value(self.cf)
        if ca is STATUS_WAITING: return
        if cb is STATUS_WAITING: return
        if cc is STATUS_WAITING: return
        if cd is STATUS_WAITING: return
        if ce is STATUS_WAITING: return
        if cf is STATUS_WAITING: return
        self._set_ready()
        self._set_value(ca or cb or cc or cd or ce or cf)
class ConditionAndList(ConditionCell):
    def __init__(self):
        ConditionCell.__init__(self)
        self.ca = True
        self.cb = True
        self.cc = True
        self.cd = True
        self.ce = True
        self.cf = True
    def evaluate(self):
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        ca = self.get_parameter_value(self.ca)
        cb = self.get_parameter_value(self.cb)
        cc = self.get_parameter_value(self.cc)
        cd = self.get_parameter_value(self.cd)
        ce = self.get_parameter_value(self.ce)
        cf = self.get_parameter_value(self.cf)
        if ca is STATUS_WAITING: return
        if cb is STATUS_WAITING: return
        if cc is STATUS_WAITING: return
        if cd is STATUS_WAITING: return
        if ce is STATUS_WAITING: return
        if cf is STATUS_WAITING: return
        self._set_ready()
        self._set_value(ca and cb and cc and cd and ce and cf)
        pass
    pass

class ConditionKeyPressed(ConditionCell):
    def __init__(self, pulse=False, key_code=None):
        ConditionCell.__init__(self)
        self.pulse = pulse
        self.key_code = key_code
        self.network = None

    def setup(self, network):
        self.network = network
        pass

    def evaluate(self):
        keycode = self.get_parameter_value(self.key_code)
        if keycode is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        keystat = self.network.keyboard_events[keycode]
        if self.pulse:
            self._set_value(keystat == bge.logic.KX_INPUT_JUST_ACTIVATED or keystat == bge.logic.KX_INPUT_ACTIVE)
        else:
            self._set_value(keystat == bge.logic.KX_INPUT_JUST_ACTIVATED)
        pass


class ActionKeyLogger(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self._key_logged = None
        self._key_code = None
        self._character = None
        self.KEY_LOGGED = LogicNetworkSubCell(self, self.get_key_logged)
        self.KEY_CODE = LogicNetworkSubCell(self, self.get_key_code)
        self.CHARACTER = LogicNetworkSubCell(self, self.get_character)
    def get_key_logged(self):
        return self._key_logged
    def get_key_code(self):
        return self._key_code
    def get_character(self):
        return self._character
    def reset(self):
        LogicNetworkCell.reset(self)
        self._key_logged = False
        self._key_code = None
        self._character = None
    def evaluate(self):
        self._set_ready()
        condition = self.get_parameter_value(self.condition)
        if not condition: return
        network = self.network
        keyboard_status = network.keyboard_events
        left_shift_status = keyboard_status[bge.events.LEFTSHIFTKEY]
        right_shift_status = keyboard_status[bge.events.RIGHTSHIFTKEY]
        shift_down = (
            (left_shift_status == bge.logic.KX_INPUT_JUST_ACTIVATED) or
            (left_shift_status == bge.logic.KX_INPUT_ACTIVE) or
            (right_shift_status == bge.logic.KX_INPUT_JUST_ACTIVATED) or
            (right_shift_status == bge.logic.KX_INPUT_ACTIVE) or
            network.capslock_pressed
        )
        active_events = network.active_keyboard_events
        for keycode in active_events:
            event = active_events[keycode]
            if(event is bge.logic.KX_INPUT_JUST_ACTIVATED):
                #something has been pressed
                self._character = bge.events.EventToCharacter(keycode, shift_down)
                self._key_code = keycode
                self._key_logged = True
                return
            pass
        pass
        
        


class ConditionMouseTargeting(ConditionCell):
    def __init__(self):
        ConditionCell.__init__(self)
        self.game_object = None
        self._mouse_entered_status = False
        self._mouse_exited_status = False
        self._mouse_over_status = False
        self._point = None
        self._normal = None
        self.MOUSE_ENTERED = LogicNetworkSubCell(self, self._get_mouse_entered)
        self.MOUSE_EXITED = LogicNetworkSubCell(self, self._get_mouse_exited)
        self.MOUSE_OVER = LogicNetworkSubCell(self, self._get_mouse_over)
        self.POINT = LogicNetworkSubCell(self, self._get_point)
        self.NORMAL = LogicNetworkSubCell(self, self._get_normal)
        self._last_target = None

    def _get_mouse_entered(self): return self._mouse_entered_status
    def _get_mouse_exited(self): return self._mouse_exited_status
    def _get_mouse_over(self): return self._mouse_over_status
    def _get_point(self): return self._point
    def _get_normal(self): return self._normal

    def evaluate(self):
        game_object = self.get_parameter_value(self.game_object)
        if game_object is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(game_object):
            self._mouse_entered_status = False
            self._mouse_exited_status = False
            self._mouse_over_status = False
            self._point = None
            self._normal = None
            return
        scene = game_object.scene
        camera = scene.active_camera
        distance = 2.0 * camera.getDistanceTo(game_object)
        mouse = bge.logic.mouse
        mouse_position = mouse.position
        vec = 10.0 * camera.getScreenVect(*mouse_position)
        ray_target = camera.worldPosition - vec
        #target, point, normal = camera.rayCast(ray_target, None, distance)
        target, point, normal = self.network.ray_cast(camera, None, ray_target, None, distance)
        if not (target is self._last_target):#mouse over a new object
            if self._last_target is game_object:#was target, now it isn't -> exited
                self._mouse_exited_status = True
                self._mouse_over_status = False
                self._mouse_entered_status = False
                self._point = None
                self._normal = None
            elif (target is game_object):#wasn't target, now it is -> entered
                self._mouse_entered_status = True
                self._mouse_over_status = False
                self._mouse_exited_status = False
                self._point = point
                self._normal = normal
            self._last_target = target
        else:#the target has not changed
            if self._last_target is game_object:#was target, still target -> over
                self._mouse_entered_status = False
                self._mouse_exited_status = False
                self._mouse_over_status = True
                self._point = point
                self._normal = normal
            else:#wans't target, still isn't target -> clear
                self._mouse_entered_status = False
                self._mouse_exited_status = False
                self._mouse_over_status = False
                self._point = None
                self._normal = None


class ConditionTimeElapsed(ConditionCell):

    def __init__(self):
        ConditionCell.__init__(self)
        self.repeat = None
        self.delta_time = None
        self._then = None
        self.network = None
        self._consumed = False

    def setup(self, network):
        self.network = network

    def reset(self):
        if self._consumed:
            self._set_value(False)
            self._set_ready()
        else:
            ConditionCell.reset(self)

    def evaluate(self):
        repeat = self.get_parameter_value(self.repeat)
        delta_time = self.get_parameter_value(self.delta_time)
        if repeat is LogicNetworkCell.STATUS_WAITING: return
        if delta_time is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        now = self.network.timeline
        if self._then is None:
            self._then = now
        delta = now - self._then
        if delta >= delta_time:
            self._set_value(True)
            self._then = now
            if not repeat:
                self._consumed = True
        else:
            self._set_value(False)


class ConditionKeyReleased(ConditionCell):
    def __init__(self):
        ConditionCell.__init__(self)
        self.pulse = False
        self.key_code = None
        self.network = None
    def setup(self, network):
        self.network = network
    def evaluate(self):
        keycode = self.get_parameter_value(self.key_code)
        if keycode is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        keystat = self.network.keyboard_events[keycode]
        if self.pulse:
            self._set_value(keystat == bge.logic.KX_INPUT_JUST_RELEASED or keystat == bge.logic.KX_INPUT_NONE)
        else:
            self._set_value(keystat == bge.logic.KX_INPUT_JUST_RELEASED)
    pass


class ConditionMousePressed(ConditionCell):
    def __init__(self):
        ConditionCell.__init__(self)
        self.pulse = False
        self.mouse_button_code = None
    def evaluate(self):
        mouse_button = self.get_parameter_value(self.mouse_button_code)
        if mouse_button is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        mstat = self.network.mouse_events[mouse_button]
        if self.pulse:
            self._set_value(mstat == bge.logic.KX_INPUT_JUST_ACTIVATED or mstat == bge.logic.KX_INPUT_ACTIVE)
        else:
            self._set_value(mstat == bge.logic.KX_INPUT_JUST_ACTIVATED)
    pass


class ConditionMousePressedOn(ConditionCell):
    def __init__(self):
        ConditionCell.__init__(self)
        self.game_object = None
        self.mouse_button = None
    def evaluate(self):
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        mouse_button = self.get_parameter_value(self.mouse_button)
        game_object = self.get_parameter_value(self.game_object)
        if mouse_button is STATUS_WAITING: return
        if game_object is STATUS_WAITING: return
        self._set_ready()
        if mouse_button is None: return
        if none_or_invalid(game_object): return
        mstat = self.network.mouse_events[mouse_button]
        if not mstat == bge.logic.KX_INPUT_JUST_ACTIVATED:
            self._set_value(False)
            return
        mpos = bge.logic.mouse.position
        camera = bge.logic.getCurrentScene().active_camera
        vec = 10 * camera.getScreenVect(*mpos)
        ray_target = camera.worldPosition - vec
        distance = camera.getDistanceTo(game_object) * 2.0
        t, p, n = self.network.ray_cast(camera, None, ray_target, None, distance)
        self._set_value(t == game_object)


class ConditionMouseUp(ConditionCell):
    def __init__(self, repeat=None):
        ConditionCell.__init__(self)
        self.network = None
        self.repeat = repeat
        self._consumed = False

    def setup(self, network):
        self.network = network

    def reset(self):
        if self._consumed:
            self._set_value(False)
            self._set_status(LogicNetworkCell.STATUS_READY)
        else:
            ConditionCell.reset(self)

    def evaluate(self):
        repeat = self.get_parameter_value(self.repeat)
        if repeat is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        dy = self.network.mouse_motion_delta[1]
        self._set_value(dy < 0)
        if not self.repeat:
            self._consumed = True


class ConditionMouseDown(ConditionCell):
    def __init__(self, repeat=None):
        ConditionCell.__init__(self)
        self.network = None
        self.repeat = repeat
        self._consumed = False

    def setup(self, network):
        self.network = network

    def reset(self):
        if self._consumed:
            self._set_value(False)
            self._set_status(LogicNetworkCell.STATUS_READY)
        else:
            ConditionCell.reset(self)

    def evaluate(self):
        repeat = self.get_parameter_value(self.repeat)
        if repeat is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        dy = self.network.mouse_motion_delta[1]
        self._set_value(dy > 0)
        if not self.repeat:
            self._consumed = True


class ConditionMouseLeft(ConditionCell):
    def __init__(self, repeat=None):
        ConditionCell.__init__(self)
        self.network = None
        self.repeat = repeat
        self._consumed = False

    def setup(self, network):
        self.network = network

    def reset(self):
        if self._consumed:
            self._set_value(False)
            self._set_status(LogicNetworkCell.STATUS_READY)
        else:
            ConditionCell.reset(self)

    def evaluate(self):
        repeat = self.get_parameter_value(self.repeat)
        if repeat is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        dx = self.network.mouse_motion_delta[0]
        self._set_value(dx > 0)
        if not self.repeat:
            self._consumed = True


class ConditionMouseRight(ConditionCell):
    def __init__(self, repeat=None):
        ConditionCell.__init__(self)
        self.network = None
        self.repeat = repeat
        self._consumed = False

    def setup(self, network):
        self.network = network

    def reset(self):
        if self._consumed:
            self._set_value(False)
            self._set_status(LogicNetworkCell.STATUS_READY)
        else:
            ConditionCell.reset(self)

    def evaluate(self):
        repeat = self.get_parameter_value(self.repeat)
        if repeat is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        dx = self.network.mouse_motion_delta[0]
        self._set_value(dx < 0)
        if not self.repeat:
            self._consumed = True


class ConditionMouseReleased(ConditionCell):
    def __init__(self):
        ConditionCell.__init__(self)
        self.pulse = False
        self.mouse_button_code = None
        self.network = None
    def setup(self, network):
        self.network = network
    def evaluate(self):
        mouse_button = self.get_parameter_value(self.mouse_button_code)
        if mouse_button is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        mstat = self.network.mouse_events[mouse_button]
        if self.pulse:
            self._set_value(mstat == bge.logic.KX_INPUT_JUST_RELEASED or mstat == bge.logic.KX_INPUT_NONE)
        else:
            self._set_value(mstat == bge.logic.KX_INPUT_JUST_RELEASED)
    pass


class ActionRepeater(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.input_value = None
        self.output_cells = []
        self.output_value = None
    def setup(self, network):
        super(ActionCell, self).setup(network)
        for cell in self.output_cells:
            cell.setup(network)
    def evaluate(self):
        self._set_ready()
        condition = self.get_parameter_value(self.condition)
        if not condition: return
        input_value = self.get_parameter_value(self.input_value)
        if isinstance(input_value, numbers.Number):
            for e in range(0, input_value):
                self._set_value(e)
                for cell in self.output_cells: cell.evaluate()
        else:
            for e in input_value:
                self._set_value(e)
                for cell in self.output_cells: cell.evaluate()
                pass
            pass
        for cell in self.output_cells:
            cell.reset()
            pass
        pass
    pass


class ConditionCollision(ConditionCell):
    def __init__(self):
        ConditionCell.__init__(self)
        self.game_object = None
        self._set_value("False")
        self._target = None
        self._point = None
        self._normal = None
        self._collision_triggered = False
        self._last_monitored_object = None
        self._objects = []
        self._opn_set = []
        self.TARGET = LogicNetworkSubCell(self, self.get_target)
        self.POINT = LogicNetworkSubCell(self, self.get_point)
        self.NORMAL = LogicNetworkSubCell(self, self.get_normal)
        self.OBJECTS = LogicNetworkSubCell(self, self.get_objects)
        self.OPN_SET = LogicNetworkSubCell(self, self.get_opn_set)

    def get_point(self): return self._point

    def get_normal(self): return self._normal

    def get_target(self): return self._target

    def get_objects(self): return self._objects

    def get_opn_set(self): return self._opn_set

    def _collision_callback(self, obj, point, normal):
        self._collision_triggered = True
        self._target = obj
        self._point = point
        self._normal = normal
        self._objects.append(obj)
        self._opn_set.append((obj, point, normal))

    def reset(self):
        LogicNetworkCell.reset(self)
        self._collision_triggered = False
        self._objects = []
        self._opn_set = []

    def _reset_last_monitored_object(self, new_monitored_object_value):
        if none_or_invalid(new_monitored_object_value): new_monitored_object_value = None
        if self._last_monitored_object == new_monitored_object_value:
            return
        if not isinstance(new_monitored_object_value, bge.types.KX_GameObject):
            if self._last_monitored_object is not None:
                self._last_monitored_object.collisionCallbacks.remove(self._collision_callback)
                self._last_monitored_object = None
        else:
            if self._last_monitored_object is not None:
                self._last_monitored_object.collisionCallbacks.remove(self._collision_callback)
            if new_monitored_object_value is not None:
                new_monitored_object_value.collisionCallbacks.append(self._collision_callback)
                self._last_monitored_object = new_monitored_object_value
        self._set_value(False)
        self._target = None
        self._point = None
        self._normal = None
        self._collision_triggered = False

    def evaluate(self):
        game_object = self.get_parameter_value(self.game_object)
        self._reset_last_monitored_object(game_object)
        if game_object is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        self._set_value(self._collision_triggered)


#Action Cells
class ActionAddObject(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.name = None
        self.life = None
        self.condition = None
        self.scene = None

    def evaluate(self):
        condition_value = self.get_parameter_value(self.condition)
        if condition_value is LogicNetworkCell.STATUS_WAITING: return
        if not condition_value:
            self._set_ready()
            return
        life_value = self.get_parameter_value(self.life)
        name_value = self.get_parameter_value(self.name)
        scene = self.get_parameter_value(self.scene)
        if life_value is LogicNetworkCell.STATUS_WAITING: return
        if name_value is LogicNetworkCell.STATUS_WAITING: return
        if scene is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(scene): return
        if life_value is None: return
        if name_value is None: return
        try:
            self._set_value(scene.addObject(name_value, None, life_value))
        except ValueError as ex:
            print("ActionAddObject: cannot find {} in the inactive layers.".format(name_value))


class ActionSetGameObjectGameProperty(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.game_object = None
        self.property_name = None
        self.property_value = None

    def evaluate(self):
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        condition_value = self.get_parameter_value(self.condition)
        if condition_value is STATUS_WAITING: return
        if condition_value is False:
            self._set_ready()
            return
        game_object_value = self.get_parameter_value(self.game_object)
        property_name_value = self.get_parameter_value(self.property_name)
        property_value_value = self.get_parameter_value(self.property_value)
        if game_object_value is STATUS_WAITING: return
        if property_name_value is STATUS_WAITING: return
        if property_value_value is STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(game_object_value): return
        if condition_value:
            game_object_value[property_name_value] = property_value_value


class ActionEndGame(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
    def evaluate(self):
        self._set_ready()
        condition = self.get_parameter_value(self.condition)
        if condition:bge.logic.endGame()
        pass
    pass

class ActionStartGame(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.file_name = None
    def evaluate(self):
        self._set_ready()
        condition = self.get_parameter_value(self.condition)
        file_name = self.get_parameter_value(self.file_name)
        if condition: bge.logic.startGame(file_name)
        pass
    pass

class ActionRestartGame(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
    def evaluate(self):
        self._set_ready()
        condition = self.get_parameter_value(self.condition)
        if condition: bge.logic.restartGame();


class ActionSetObjectAttribute(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.game_object = None
        self.attribute_name = None
        self.attribute_value = None

    def evaluate(self):
        condition_value = self.get_parameter_value(self.condition)
        if condition_value is LogicNetworkCell.STATUS_WAITING: return
        game_object_value = self.get_parameter_value(self.game_object)
        if game_object_value is LogicNetworkCell.STATUS_WAITING: return
        attribute_name_value = self.get_parameter_value(self.attribute_name)
        if attribute_name_value is LogicNetworkCell.STATUS_WAITING: return
        attribute_value_value = self.get_parameter_value(self.attribute_value)
        if attribute_value_value is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(game_object_value): return
        if condition_value:
            setattr(game_object_value, attribute_name_value, attribute_value_value)
    pass

class ActionInstalSubNetwork(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.target_object = None
        self.tree_name = None
        self.initial_status = None
        self._network = None

    def setup(self, network):
        self._network = network

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        target_object = self.get_parameter_value(self.target_object)
        tree_name = self.get_parameter_value(self.tree_name)
        initial_status = self.get_parameter_value(self.initial_status)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        if target_object is LogicNetworkCell.STATUS_WAITING: return
        if tree_name is LogicNetworkCell.STATUS_WAITING: return
        if initial_status is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(target_object): return
        if condition:
            self._network.install_subnetwork(target_object, tree_name, initial_status)


class ActionStartLogicNetwork(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.game_object = None
        self.logic_network_name = None

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        if not condition:
            self._set_ready()
            return
        game_object = self.get_parameter_value(self.game_object)
        if game_object is LogicNetworkCell.STATUS_WAITING: return
        logic_network_name = self.get_parameter_value(self.logic_network_name)
        if logic_network_name is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(game_object): return
        network = game_object.get(logic_network_name)
        if network is not None:
            network.stopped = False


class ActionStopLogicNetwork(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.game_object = None
        self.logic_network_name = None

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        game_object = self.get_parameter_value(self.game_object)
        if game_object is LogicNetworkCell.STATUS_WAITING: return
        logic_network_name = self.get_parameter_value(self.logic_network_name)
        if logic_network_name is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(game_object): return
        if condition:
            network = game_object.get(logic_network_name)
            network.stop()


class ActionFindObject(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.scene = None
        self.from_parent = None
        self.query = None
        self._branch_root = None
        self._parent_object = None
        self.PARENT = LogicNetworkSubCell(self, self.get_parent)
        self.BRANCH_ROOT = LogicNetworkSubCell(self, self.get_branch_root)

    def get_parent(self):
        if not none_or_invalid(self._value):
            return self._value.parent
        else:
            return None

    def get_branch_root(self):
        if not none_or_invalid(self._value):
            p = self._value
            while p.parent is not None:
                p = p.parent
            return p
        else:
            return None

    def evaluate(self):
        self._set_ready()
        condition = self.get_parameter_value(self.condition)
        if (condition is None) and (not none_or_invalid(self._value)):
            #if no condition, early out
            return self._value
        self._set_value(None)#remove invalid objects, if any
        if condition is False:#no need to evaluate
            return
        #condition is either True or None
        scene = self.get_parameter_value(self.scene)
        parent = self.get_parameter_value(self.from_parent)
        query = self.get_parameter_value(self.query)
        if (query == None) or (query == ""):
            return
        if not none_or_invalid(scene):
            #find from scene
            self._set_value(_name_query(scene.objects, query))
        elif not none_or_invalid(parent):
            #find from parent
            self._set_value(_name_query(parent.childrenRecursive, query))
        pass
    pass


class ActionLibLoad(ActionCell):

    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.path = None
        self._set_value(False)

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        path = self.get_parameter_value(self.path)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        if path is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if condition:
            if path.startswith("//"): path = bge.logic.expandPath(path)
            if not path in bge.logic.LibList():
                bge.logic.LibLoad(path, "Scene", load_actions=True)
            self._set_value(True)
        else:
            self._set_value(False)


class ActionSetGameObjectVisibility(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.game_object = None
        self.visible = None
        self.recursive = None
    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        if condition is STATUS_WAITING: return
        if not condition:
            self._set_ready()
            return
        game_object = self.get_parameter_value(self.game_object)
        visible = self.get_parameter_value(self.visible)
        recursive = self.get_parameter_value(self.recursive)
        if game_object is STATUS_WAITING: return
        if visible is STATUS_WAITING: return
        if recursive is STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(game_object): return
        if visible is None: return
        if recursive is None: return
        game_object.setVisible(visible, recursive)



class ActionRayPick(ActionCell):

    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.origin = None
        self.destination = None
        self.property_name = None
        self.distance = None
        self._picked_object = None
        self._point = None
        self._normal = None
        self._direction = None
        self.PICKED_OBJECT = LogicNetworkSubCell(self, self.get_picked_object)
        self.POINT = LogicNetworkSubCell(self, self.get_point)
        self.NORMAL = LogicNetworkSubCell(self, self.get_normal)
        self.DIRECTION = LogicNetworkSubCell(self, self.get_direction)
        self.network = None

    def setup(self, network):
        self.network = network

    def get_picked_object(self):
        return self._picked_object

    def get_point(self):
        return self._point

    def get_normal(self):
        return self._normal

    def get_direction(self):
        return self._direction

    def _compute_direction(self, origin, dest):
        if hasattr(origin, "worldPosition"): origin = origin.worldPosition
        if hasattr(dest, "worldPosition"): dest = dest.worldPosition
        d = dest - origin
        d.normalize()
        return d

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        if not condition:
            self._set_ready()
            self._set_value(False)
            self._out_normal = None
            self._out_object = None
            self._out_point = None
            return
        origin = self.get_parameter_value(self.origin)
        destination = self.get_parameter_value(self.destination)
        property_name = self.get_parameter_value(self.property_name)
        distance = self.get_parameter_value(self.distance)

        if origin is LogicNetworkCell.STATUS_WAITING: return
        if destination is LogicNetworkCell.STATUS_WAITING: return
        if property_name is LogicNetworkCell.STATUS_WAITING: return
        if distance is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        caster = self.network._owner
        obj, point, normal = None, None, None
        if not property_name:
            obj, point, normal = caster.rayCast(destination, origin, distance)
        else:
            obj, point, normal = caster.rayCast(destination, origin, distance, property_name)
        self._set_value(obj is not None)
        self._picked_object = obj
        self._point = point
        self._normal = normal
        self._direction = self._compute_direction(origin, destination)


class ActionLibFree(ActionCell):

    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.path = None
        self._set_value(False)

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        #CONDITION IS TRUE
        path = self.get_parameter_value(self.path)
        if path is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if not condition:
            self._set_value(False)
            return
        if path.startswith("//"): path = bge.logic.expandPath(path)
        bge.logic.LibFree(path)
        self._set_value(True)


class ActionMousePick(ActionCell):

    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.distance = None
        self.property = None
        self.camera = None
        self._set_value(False)
        self._out_object = None
        self._out_normal = None
        self._out_point = None
        self.OUTOBJECT = LogicNetworkSubCell(self, self.get_out_object)
        self.OUTNORMAL = LogicNetworkSubCell(self, self.get_out_normal)
        self.OUTPOINT = LogicNetworkSubCell(self, self.get_out_point)

    def get_out_object(self): return self._out_object
    def get_out_normal(self): return self._out_normal
    def get_out_point(self): return self._out_point

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        distance = self.get_parameter_value(self.distance)
        property_name = self.get_parameter_value(self.property)
        camera = self.get_parameter_value(self.camera)
        if distance is LogicNetworkCell.STATUS_WAITING: return
        if property is LogicNetworkCell.STATUS_WAITING: return
        if camera is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if not condition:
            self._set_value(False)
            self._out_normal = None
            self._out_object = None
            self._out_point = None
            return
        if none_or_invalid(camera): return
        mpos = bge.logic.mouse.position
        vec = 10 * camera.getScreenVect(*mpos)
        ray_target = camera.worldPosition - vec
        target, point, normal = self.network.ray_cast(camera, None, ray_target, property_name, distance)
        self._set_value(target is not None)
        self._out_object = target
        self._out_normal = normal
        self._out_point = point


class ActionCameraPick(ActionCell):

    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.camera = None
        self.aim = None
        self.property_name = None
        self.distance = None
        self._picked_object = None
        self._picked_point = None
        self._picked_normal = None
        self.PICKED_OBJECT = LogicNetworkSubCell(self, self.get_picked_object)
        self.PICKED_POINT = LogicNetworkSubCell(self, self.get_picked_point)
        self.PICKED_NORMAL = LogicNetworkSubCell(self, self.get_picked_normal)

    def get_picked_object(self):
        return self._picked_object

    def get_picked_point(self):
        return self._picked_point

    def get_picked_normal(self):
        return self._picked_normal

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        camera = self.get_parameter_value(self.camera)
        aim = self.get_parameter_value(self.aim)
        property_name = self.get_parameter_value(self.property_name)
        distance = self.get_parameter_value(self.distance)
        if camera is LogicNetworkCell.STATUS_WAITING: return
        if aim is LogicNetworkCell.STATUS_WAITING: return
        if property_name is LogicNetworkCell.STATUS_WAITING: return
        if distance is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if not condition:
            self._set_value(False)
            self._out_normal = None
            self._out_object = None
            self._out_point = None
            return
        if none_or_invalid(camera): return
        if none_or_invalid(aim): return
        obj, point, normal = None, None, None
        if isinstance(aim, mathutils.Vector) and len(aim) == 2:#assume screen coordinates
            vec = 10 * camera.getScreenVect(aim[0], aim[1])
            ray_target = camera.worldPosition - vec
            aim = ray_target
        if not property_name:
            obj, point, normal = camera.rayCast(aim, None, distance)
        else:
            obj, point, normal = camera.rayCast(aim, None, distance, property_name)
        self._set_value(obj is not None)
        self._picked_object = obj
        self._picked_point = point
        self._picked_normal = normal


class ActionSetActiveCamera(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.scene = None
        self.camera = None

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        scene = self.get_parameter_value(self.scene)
        if scene is LogicNetworkCell.STATUS_WAITING: return
        camera = self.get_parameter_value(self.camera)
        if camera is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if not condition: return
        if none_or_invalid(camera): return
        if none_or_invalid(scene): return
        scene.active_camera = camera
        pass


class ActionSetParent(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.child_object = None
        self.parent_object = None
        self.compound = True
        self.ghost = True

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        if not condition:
            self._set_ready()
            return
        child_object = self.get_parameter_value(self.child_object)
        parent_object = self.get_parameter_value(self.parent_object)
        compound = self.get_parameter_value(self.compound)
        ghost = self.get_parameter_value(self.ghost)
        if child_object is LogicNetworkCell.STATUS_WAITING: return
        if parent_object is LogicNetworkCell.STATUS_WAITING: return
        if compound is LogicNetworkCell.STATUS_WAITING: return
        if ghost is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(child_object): return
        if none_or_invalid(parent_object): return
        if child_object.parent is parent_object: return
        if condition:
            child_object.setParent(parent_object, compound, ghost)


class ActionRemoveParent(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.child_object = None
    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        if not condition:
            self._set_ready()
            return
        child_object = self.get_parameter_value(self.child_object)
        if child_object is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(child_object): return
        if not child_object.parent: return
        if condition:
            child_object.removeParent()


class ActionEditArmatureConstraint(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.armature = None
        self.constraint_name = None
        self.enforced_factor = None
        self.primary_target = None
        self.secondary_target = None
        self.active = None
        self.ik_weight = None
        self.ik_distance = None
        self.distance_mode = None

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        if not condition:
            self._set_ready()
            return
        armature = self.get_parameter_value(self.armature)
        constraint_name = self.get_parameter_value(self.constraint_name)
        enforced_factor = self.get_parameter_value(self.enforced_factor)
        primary_target = self.get_parameter_value(self.primary_target)
        secondary_target = self.get_parameter_value(self.secondary_target)
        active = self.get_parameter_value(self.active)
        ik_weight = self.get_parameter_value(self.ik_weight)
        ik_distance = self.get_parameter_value(self.ik_distance)
        distance_mode = self.get_parameter_value(self.distance_mode)
        if armature is LogicNetworkCell.STATUS_WAITING: return
        if constraint_name is LogicNetworkCell.STATUS_WAITING: return
        if enforced_factor is LogicNetworkCell.STATUS_WAITING: return
        if primary_target is LogicNetworkCell.STATUS_WAITING: return
        if secondary_target is LogicNetworkCell.STATUS_WAITING: return
        if active is LogicNetworkCell.STATUS_WAITING: return
        if ik_weight is LogicNetworkCell.STATUS_WAITING: return
        if ik_distance is LogicNetworkCell.STATUS_WAITING: return
        if distance_mode is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(armature): return
        if invalid(primary_target): primary_target = None
        if invalid(secondary_target): secondary_target = None
        constraint = armature.constraints[constraint_name]
        changed = False
        if (enforced_factor is not None) and (constraint.enforce != enforced_factor):
            constraint.enforce = enforced_factor
            changed = True
        if constraint.target != primary_target:
            constraint.target = primary_target
            changed = True
        if constraint.subtarget != secondary_target:
            constraint.subtarget = secondary_target
            changed = True
        if constraint.active != active:
            constraint.active = active
            changed = True
        if (ik_weight is not None) and (constraint.ik_weight != ik_weight):
            constraint.ik_weight = ik_weight
            changed = True
        if (ik_distance is not None) and (constraint.ik_distance != ik_distance):
            constraint.ik_distance = ik_distance
            changed = True
        if (distance_mode is not None) and (constraint.ik_mode != distance_mode):
            constraint.ik_mode = distance_mode
            changed = True
        armature.update()


class ActionEditBone(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.armature = None
        self.bone_name = None
        self.set_translation = None
        self.set_orientation = None
        self.set_scale = None
        self.translate = None
        self.rotate = None
        self.scale = None
        self._eulers = mathutils.Euler((0,0,0), "XYZ")
        self._vector = mathutils.Vector((0,0,0))

    def _convert_orientation(self, ch, xyzrot):
        eulers = self._eulers
        eulers[:] = xyzrot
        if ch.rotation_mode is bge.logic.ROT_MODE_QUAT:
            return eulers.to_quaternion()
        else:
            return xyzrot

    def _set_orientation(self, ch, rot):
        orientation = self._convert_orientation(ch, rot)
        if ch.rotation_mode is bge.logic.ROT_MODE_QUAT:
            ch.rotation_quaternion = orientation
        else:
            ch.rotation_euler = orientation

    def _rotate(self, ch, xyzrot):
        orientation = self._convert_orientation(ch, xyzrot)
        if ch.rotation_mode is bge.logic.ROT_MODE_QUAT:
            ch.rotation_quaternion = mathutils.Quaternion(ch.rotation_quaternion) * orientation
        else:
            ch.rotation_euler = ch.rotation_euler.rotate(orientation)

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        if not condition:
            self._set_ready()
            return
        armature = self.get_parameter_value(self.armature)
        bone_name = self.get_parameter_value(self.bone_name)
        set_translation = self.get_parameter_value(self.set_translation)
        set_orientation = self.get_parameter_value(self.set_orientation)
        set_scale = self.get_parameter_value(self.set_scale)
        translate = self.get_parameter_value(self.translate)
        rotate = self.get_parameter_value(self.rotate)
        scale = self.get_parameter_value(self.scale)
        if armature is LogicNetworkCell.STATUS_WAITING: return
        if bone_name is LogicNetworkCell.STATUS_WAITING: return
        if set_translation is LogicNetworkCell.STATUS_WAITING: return
        if set_orientation is LogicNetworkCell.STATUS_WAITING: return
        if set_scale is LogicNetworkCell.STATUS_WAITING: return
        if translate is LogicNetworkCell.STATUS_WAITING: return
        if rotate is LogicNetworkCell.STATUS_WAITING: return
        if scale is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(armature): return
        if not bone_name: return
        #TODO cache the bone index
        bone_channel = armature.channels[bone_name]
        if set_translation is not None:
            bone_channel.location = set_translation
        if set_orientation is not None:
            self._set_orientation(bone_channel, set_orientation)
        if set_scale is not None:
            bone_channel.scale = set_scale
        if translate is not None:
            vec = self._vector
            vec[:] = translate
            bone_channel.location = bone_channel.location + vec
        if scale is not None:
            vec = self._vector
            vec[:] = scale
            bone_channel.scale = bone_channel.scale + vec
        if rotate is not None:
            self._rotate(bone_channel, rotate)
        armature.update()


class ActionTimeFilter(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.delay = None
        self._triggered = False
        self._triggered_time = None
        self._trigger_delay = None
    def evaluate(self):
        if self._triggered is True:
            self._set_ready()
            delta = self.network.timeline - self._triggered_time
            if delta < self._trigger_delay:
                self._set_value(False)
                return
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        condition = self.get_parameter_value(self.condition)
        delay = self.get_parameter_value(self.delay)
        if condition is STATUS_WAITING: return
        if delay is STATUS_WAITING: return
        self._set_ready()
        self._set_value(False)
        if delay is None: return
        if condition is None: return
        if condition:
            self._triggered = True
            self._triggered_time = self.network.timeline
            self._trigger_delay = delay
            self._set_value(True)


class ActionTimeBarrier(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.delay = None
        self.repeat = None
        self._trigger_delay = None
        self._triggered_time = None
        self._triggered = False
        self._condition_true_time = 0.0
    def evaluate(self):
        if self._triggered:
            self._set_ready()
            self._set_value(False)
            delta = self.network.timeline - self._triggered_time
            if delta < self._trigger_delay: return
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        condition = self.get_parameter_value(self.condition)
        delay = self.get_parameter_value(self.delay)
        repeat = self.get_parameter_value(self.repeat)
        if condition is STATUS_WAITING: return
        if delay is STATUS_WAITING: return
        if repeat is STATUS_WAITING: return
        self._set_ready()
        if condition is None: return
        if delay is None: return
        if repeat is None: return
        self._set_value(False)
        if not condition:
            self._condition_true_time = 0.0
            return
        if condition:
            self._condition_true_time += self.network.time_per_frame
            if self._condition_true_time >= delay:
                self._triggered = True
                self._trigger_delay = delay
                self._triggered_time = self.network.timeline
                self._set_value(True)

class ActionSetDynamics(ActionCell):
    def __init__(self):
        self.condition = None
        self.game_object = None
        self.ghost = None
        self.activate = False

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        if not condition:
            self._set_ready()
            return
        game_object = self.get_parameter_value(self.game_object)
        ghost = self.get_parameter_value(self.ghost)
        activate = self.get_parameter_value(self.activate)
        if game_object is LogicNetworkCell.STATUS_WAITING: return
        if ghost is LogicNetworkCell.STATUS_WAITING: return
        if activate is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(game_object): return
        if condition:
            if activate:
                game_object.restoreDynamics()
            else:
                game_object.suspendDynamics(ghost)


class ActionEndObject(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.scene = None
        self.game_object = None

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        game_object = self.get_parameter_value(self.game_object)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        if game_object is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if not condition: return
        if none_or_invalid(game_object): return
        game_object.endObject()


class ActionEndScene(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.scene = None

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        scene = self.get_parameter_value(self.scene)
        if scene is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(scene): return
        if not condition: return
        scene.end()


class ActionSetMousePosition(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.screen_x = None
        self.screen_y = None
        self.network = None

    def setup(self, network):
        self.network = network

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        screen_x = self.get_parameter_value(self.screen_x)
        screen_y = self.get_parameter_value(self.screen_y)
        if screen_x is LogicNetworkCell.STATUS_WAITING: return
        if screen_y is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if condition:
            self.network.set_mouse_position(screen_x, screen_y)


class ActionSetMouseCursorVisibility(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.visibility_status = None

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        visibility_status = self.get_parameter_value(self.visibility_status)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        if visibility_status is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if condition:
            bge.logic.mouse.visible = visibility_status


class ActionApplyGameObjectValue(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.game_object = None
        self.movement = None
        self.rotation = None
        self.force = None
        self.torque = None
        self.local = False

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        game_object = self.get_parameter_value(self.game_object)
        if game_object is LogicNetworkCell.STATUS_WAITING: return
        movement = self.get_parameter_value(self.movement)
        rotation = self.get_parameter_value(self.rotation)
        force = self.get_parameter_value(self.force)
        torque = self.get_parameter_value(self.torque)
        local = self.local
        if movement is LogicNetworkCell.STATUS_WAITING: return
        if rotation is LogicNetworkCell.STATUS_WAITING: return
        if force is LogicNetworkCell.STATUS_WAITING: return
        if torque is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if not condition: return
        if none_or_invalid(game_object): return
        if movement: game_object.applyMovement(movement, local)
        if rotation:
            if len(rotation) == 3:
                game_object.applyRotation(rotation, local)
            else:
                game_object.applyRotation(rotation.to_euler("XYZ"), local)
        if force: game_object.applyForce(force, local)
        if torque: game_object.applyTorque(torque, local)
    pass


class ActionAddScene(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.scene_name = None
        self.overlay = None

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        scene_name = self.get_parameter_value(self.scene_name)
        if scene_name is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if not condition: return
        if self.overlay is None:
            bge.logic.addScene(scene_name)
        else:
            bge.logic.addScene(scene_name, self.overlay)
    pass


class ActionPlayAction(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.game_object = None
        self.action_name = None
        self.start_frame = None
        self.end_frame = None
        self.layer = None
        self.priority = None
        self.play_mode = None
        self.layer_weight = None
        self.speed = None
        self.blendin = None
        self.blend_mode = None
        self._started = False
        self._running = False
        self._finished = False
        self._frame = 0.0
        self._finish_notified = False
        self.STARTED = LogicNetworkSubCell(self, self._get_started)
        self.FINISHED = LogicNetworkSubCell(self, self._get_finished)
        self.RUNNING = LogicNetworkSubCell(self, self._get_running)
        self.FRAME = LogicNetworkSubCell(self, self._get_frame)

    def _get_started(self): return self._started
    def _get_finished(self): return self._finished
    def _get_running(self): return self._running
    def _get_frame(self): return self._frame
    def _reset_subvalues(self):
        self._started = False
        self._finished = False
        self._running = False
        self._frame = 0.0
        self._finish_notified = False
    def _notify_finished(self):
        if not self._finish_notified:
            self._finish_notified = True
            self._finished = True
        else:
            self._finished = False

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        game_object = self.get_parameter_value(self.game_object)
        action_name = self.get_parameter_value(self.action_name)
        start_frame = self.get_parameter_value(self.start_frame)
        end_frame = self.get_parameter_value(self.end_frame)
        layer = self.get_parameter_value(self.layer)
        priority = self.get_parameter_value(self.priority)
        play_mode = self.get_parameter_value(self.play_mode)
        layer_weight = self.get_parameter_value(self.layer_weight)
        speed = self.get_parameter_value(self.speed)
        blendin = self.get_parameter_value(self.blendin)
        blend_mode = self.get_parameter_value(self.blend_mode)
        if game_object is LogicNetworkCell.STATUS_WAITING: return
        if action_name is LogicNetworkCell.STATUS_WAITING: return
        if start_frame is LogicNetworkCell.STATUS_WAITING: return
        if end_frame is LogicNetworkCell.STATUS_WAITING: return
        if layer is LogicNetworkCell.STATUS_WAITING: return
        if priority is LogicNetworkCell.STATUS_WAITING: return
        if play_mode is LogicNetworkCell.STATUS_WAITING: return
        if layer_weight is LogicNetworkCell.STATUS_WAITING: return
        if speed is LogicNetworkCell.STATUS_WAITING: return
        if blendin is LogicNetworkCell.STATUS_WAITING: return
        if blend_mode is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(game_object):#can't play
            self._reset_subvalues()
        else:
            #Condition might be false and the animation running because it was started in a previous evaluation
            playing_action = game_object.getActionName(layer)
            playing_frame = game_object.getActionFrame(layer)
            min_frame = start_frame
            max_frame = end_frame
            if end_frame < start_frame:
                min_frame = end_frame
                max_frame = max_frame
            if (playing_action == action_name) and (playing_frame >= min_frame) and (playing_frame <= max_frame):
                self._started = False
                self._running = True
                is_near_end = False
                #TODO: the meaning of start-end depends also on the action mode
                if end_frame > start_frame:#play 0 to 100
                    is_near_end = (playing_frame >= (end_frame - 0.5))
                else:#play 100 to 0
                    print(playing_frame, end_frame)
                    is_near_end = (playing_frame <= (end_frame + 0.5))
                if is_near_end: self._notify_finished()
                pass
            elif condition:#start the animation if the condition is True
                game_object.playAction(
                    action_name, start_frame, end_frame, layer=layer, priority=priority, blendin=blendin,
                    play_mode=play_mode, speed=speed, layer_weight=layer_weight, blend_mode=blend_mode)
                self._started = True
                self._running = True
                self._finished = False
                self._frame = start_frame
                self._finish_notified = False
            else:#game_object is existing and valid but condition is False
                self._reset_subvalues()


class ActionStopAnimation(ActionCell):

    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.game_object = None
        self.action_layer = None

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if not condition:
            self._set_ready()
            return
        game_object = self.get_parameter_value(self.game_object)
        action_layer = self.get_parameter_value(self.action_layer)
        if game_object is LogicNetworkCell.STATUS_WAITING: return
        if action_layer is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(game_object): return
        if none_or_invalid(action_layer): return
        game_object.stopAction(action_layer)


class ActionSetAnimationFrame(ActionCell):

    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.game_object = None
        self.action_layer = None
        self.action_frame = None
        self.action_name = None

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if not condition:
            self._set_ready()
            return
        game_object = self.get_parameter_value(self.game_object)
        action_layer = self.get_parameter_value(self.action_layer)
        action_frame = self.get_parameter_value(self.action_frame)
        action_name = self.get_parameter_value(self.action_name)
        self._set_ready()
        if none_or_invalid(game_object): return
        if none_or_invalid(action_layer): return
        if none_or_invalid(action_frame): return
        if not action_name: return
        game_object.playAction(action_name, action_frame, action_frame, action_layer)


class ActionFindScene(ActionCell):

    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.query = None

    def has_status(self, status):
        found_scene = self.get_value()
        if (self.condition is None) and (found_scene is not None) and (not found_scene.invalid) and (found_scene is not None):
            return status is LogicNetworkCell.STATUS_READY
        else:
            return ActionCell.has_status(self, status)

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        query = self.get_parameter_value(self.query)
        if query is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if self.condition is None:
            scene = _name_query(bge.logic.getSceneList(), query)
            self._set_value(scene)
        if condition:
            scene = _name_query(bge.logic.getSceneList(), query)
            self._set_value(scene)


class ActionDynamicObjectController(ActionCell):

    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.head_object = None
        self.body_object = None
        self.rotate_head_up = None
        self.rotate_head_down = None
        self.rotate_body_left = None
        self.rotate_body_right = None
        self.strafe_left = None
        self.strafe_right = None
        self.move_forth = None
        self.move_back = None
        self.jump = None
        self.run = None
        self.head_rot_arc_size = None
        self.head_rot_speed = None
        self.body_rot_speed = None
        self.walk_speed = None
        self.run_speed = None
        self.jump_force = None
        self.network = None

    def setup(self, network):
        self.network = network

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        head_object = self.get_parameter_value(self.head_object)
        body_object = self.get_parameter_value(self.body_object)
        rotate_head_up = self.get_parameter_value(self.rotate_head_up)
        rotate_head_down = self.get_parameter_value(self.rotate_head_down)
        rotate_body_left = self.get_parameter_value(self.rotate_body_left)
        rotate_body_right = self.get_parameter_value(self.rotate_body_right)
        strafe_left = self.get_parameter_value(self.strafe_left)
        strafe_right = self.get_parameter_value(self.strafe_right)
        move_forth = self.get_parameter_value(self.move_forth)
        move_back = self.get_parameter_value(self.move_back)
        jump = self.get_parameter_value(self.jump)
        run = self.get_parameter_value(self.run)
        head_rot_arc_size = self.get_parameter_value(self.head_rot_arc_size)
        head_rot_speed = self.get_parameter_value(self.head_rot_speed)
        body_rot_speed = self.get_parameter_value(self.body_rot_speed)
        walk_speed = self.get_parameter_value(self.walk_speed)
        run_speed = self.get_parameter_value(self.run_speed)
        jump_force = self.get_parameter_value(self.jump_force)
        if head_object is LogicNetworkCell.STATUS_WAITING: return
        if body_object is LogicNetworkCell.STATUS_WAITING: return
        if rotate_head_up is LogicNetworkCell.STATUS_WAITING: return
        if rotate_head_down is LogicNetworkCell.STATUS_WAITING: return
        if rotate_body_left is LogicNetworkCell.STATUS_WAITING: return
        if rotate_body_right is LogicNetworkCell.STATUS_WAITING: return
        if strafe_left is LogicNetworkCell.STATUS_WAITING: return
        if strafe_right is LogicNetworkCell.STATUS_WAITING: return
        if move_forth is LogicNetworkCell.STATUS_WAITING: return
        if move_back is LogicNetworkCell.STATUS_WAITING: return
        if jump is LogicNetworkCell.STATUS_WAITING: return
        if run is LogicNetworkCell.STATUS_WAITING: return
        if head_rot_arc_size is LogicNetworkCell.STATUS_WAITING: return
        if head_rot_speed is LogicNetworkCell.STATUS_WAITING: return
        if body_rot_speed is LogicNetworkCell.STATUS_WAITING: return
        if walk_speed is LogicNetworkCell.STATUS_WAITING: return
        if run_speed is LogicNetworkCell.STATUS_WAITING: return
        if jump_force is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if not condition: return
        tpf = self.network.time_per_frame
        if not none_or_invalid(body_object):
            body_rot_direction = rotate_body_right - rotate_body_left
            body_move_direction = move_forth - move_back
            body_strafe_direction = strafe_right - strafe_left
            if jump:
                z_vel = abs(body_object.worldLinearVelocity.z)
                if z_vel < 0.05:
                    body_object.applyForce((0,0,jump_force), False)
            if run:
                walk_speed = run_speed
            walk_speed *= tpf
            body_rot_speed *= tpf
            if body_rot_direction:
                body_object.applyRotation((0, 0, body_rot_speed * body_rot_direction), False)
            if body_move_direction or body_strafe_direction:
                body_object.applyMovement((walk_speed * body_strafe_direction, walk_speed * body_move_direction, 0), True)
        if not none_or_invalid(head_object):
            head_rot_direction = rotate_head_up - rotate_head_down
            if head_rot_direction:
                head_zero_eulers = head_object.get("_NL_zero rotation_", None)
                if head_zero_eulers is None:
                    head_zero_eulers = head_object.localOrientation.to_euler()
                    head_object["_NL_zero rotation_"] = head_zero_eulers
                current_head_eulers = head_object.localOrientation.to_euler()
                max_head_rot = head_zero_eulers[0] + (head_rot_arc_size / 2.0)
                min_head_rot = head_zero_eulers[0] - (head_rot_arc_size / 2.0)
                head_delta_rot = head_rot_speed * tpf * head_rot_direction
                new_head_rot = current_head_eulers[0] + head_delta_rot
                if new_head_rot > max_head_rot: new_head_rot = max_head_rot
                if new_head_rot < min_head_rot: new_head_rot = min_head_rot
                current_head_eulers[0] = new_head_rot
                head_object.localOrientation = current_head_eulers


class ActionStartSound(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.sound = None
        self.loop_count = None
        self.location = None
        self.orientation = None
        self.velocity = None
        self.pitch = None
        self.volume = None
        self.attenuation = None
        self.distance_ref = None
        self.distance_max = None
        self._euler = mathutils.Euler((0,0,0), "XYZ")
        self._prev_loop_count = None
    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        if not condition:
            self._set_ready()
            return
        sound = self.get_parameter_value(self.sound)
        location = self.get_parameter_value(self.location)
        orientation = self.get_parameter_value(self.orientation)
        velocity = self.get_parameter_value(self.velocity)
        pitch = self.get_parameter_value(self.pitch)
        loop_count = self.get_parameter_value(self.loop_count)
        volume = self.get_parameter_value(self.volume)
        attenuation = self.get_parameter_value(self.attenuation)
        distance_ref = self.get_parameter_value(self.distance_ref)
        distance_max = self.get_parameter_value(self.distance_max)
        self._set_ready()
        if sound is None:
            return
        if orientation is not None:
            if hasattr(orientation, "to_quaternion"):
                orientation = orientation.to_quaternion()
            else:#assume xyz tuple
                euler = self._euler
                euler[:] = orientation
                orientation = euler.to_quaternion()
        if loop_count != self._prev_loop_count:
            self._prev_loop_count = loop_count
        else:
            loop_count = None
        sound.play(location, orientation, velocity, pitch, volume, loop_count, attenuation, distance_ref, distance_max)


class ActionUpdateSound(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.sound = None
        self.location = None
        self.orientation = None
        self.velocity = None
        self.pitch = None
        self.volume = None
        self.attenuation = None
        self.distance_ref = None
        self.distance_max = None
        self._euler = mathutils.Euler((0,0,0), "XYZ")
    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        if not condition:
            self._set_ready()
            return
        sound = self.get_parameter_value(self.sound)
        location = self.get_parameter_value(self.location)
        orientation = self.get_parameter_value(self.orientation)
        velocity = self.get_parameter_value(self.velocity)
        pitch = self.get_parameter_value(self.pitch)
        volume = self.get_parameter_value(self.volume)
        attenuation = self.get_parameter_value(self.attenuation)
        distance_ref = self.get_parameter_value(self.distance_ref)
        distance_max = self.get_parameter_value(self.distance_max)
        self._set_ready()
        if sound is None:
            return
        if orientation is not None:
            if hasattr(orientation, "to_quaternion"):
                orientation = orientation.to_quaternion()
            else:#assume xyz tuple
                euler = self._euler
                euler[:] = orientation
                orientation = euler.to_quaternion()
        sound.update(location, orientation, velocity, pitch, volume, None, attenuation, distance_ref, distance_max)


class ActionStopSound(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.sound = None

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        if not condition:
            self._set_ready()
            return
        sound = self.get_parameter_value(self.sound)
        if sound is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if sound is None: return
        sound.stop()


class ActionPauseSound(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.sound = None

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        if condition is LogicNetworkCell.STATUS_WAITING: return
        if not condition:
            self._set_ready()
            return
        sound = self.get_parameter_value(self.sound)
        if sound is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        if sound is None: return
        sound.pause()


class ParameterGetGlobalValue(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self.data_id = None
        self.key = None
        self.default_value = None
    def evaluate(self):
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        data_id = self.get_parameter_value(self.data_id)
        key = self.get_parameter_value(self.key)
        default_value = self.get_parameter_value(self.default_value)
        if data_id is STATUS_WAITING: return
        if key is STATUS_WAITING: return
        if default_value is STATUS_WAITING: return
        self._set_ready()
        db = SimpleLoggingDatabase.get_or_create_shared_db(data_id)
        self._set_value(db.get(key, default_value))


class ParameterConstantValue(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self._status = LogicNetworkCell.STATUS_READY
        self.value = None
    def get_value(self): return self.value
    def reset(self): self._set_ready()
    def has_status(self, status): return status == LogicNetworkCell.STATUS_READY
    def evaluate(self): return self._set_ready()


class ParameterFormattedString(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self.format_string = None
        self.value_a = None
        self.value_b = None
        self.value_c = None
        self.value_d = None
    def evaluate(self):
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        format_string = self.get_parameter_value(self.format_string)
        value_a = self.get_parameter_value(self.value_a)
        value_b = self.get_parameter_value(self.value_b)
        value_c = self.get_parameter_value(self.value_c)
        value_d = self.get_parameter_value(self.value_d)
        if format_string is STATUS_WAITING: return
        if value_a is STATUS_WAITING: return
        if value_b is STATUS_WAITING: return
        if value_c is STATUS_WAITING: return
        if value_d is STATUS_WAITING: return
        self._set_ready()
        if format_string is None: return
        result = format_string.format(value_a, value_b, value_c, value_d)
        self._set_value(result)


class ActionSetGlobalValue(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.data_id = None
        self.persistent = None
        self.key = None
        self.value = None
    def evaluate(self):
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        condition = self.get_parameter_value(self.condition)
        if condition is STATUS_WAITING: return
        if condition is False:
            self._set_ready()
            return
        data_id = self.get_parameter_value(self.data_id)
        persistent = self.get_parameter_value(self.persistent)
        key = self.get_parameter_value(self.key)
        value = self.get_parameter_value(self.value)
        if data_id is STATUS_WAITING: return
        if key is STATUS_WAITING: return
        if persistent is STATUS_WAITING: return
        if value is STATUS_WAITING: return
        self._set_ready()
        if self.condition is None or condition:
            if data_id is None: return
            if persistent is None: return
            if key is None: return
            db = SimpleLoggingDatabase.get_or_create_shared_db(data_id)
            db.put(key, value, persistent)
            if self.condition is None:
                self.deactivate()


class ActionRandomValues(ActionCell):
    def __init__(self):
        self.condition = None
        self.min_value = None
        self.max_value = None
        self._output_a = 0
        self._output_b = 0
        self._output_c = 0
        self._output_d = 0
        self.OUT_A = LogicNetworkSubCell(self, self._get_output_a)
        self.OUT_B = LogicNetworkSubCell(self, self._get_output_b)
        self.OUT_C = LogicNetworkSubCell(self, self._get_output_c)
        self.OUT_D = LogicNetworkSubCell(self, self._get_output_d)
    def _get_output_a(self): return self._output_a
    def _get_output_b(self): return self._output_b
    def _get_output_c(self): return self._output_c
    def _get_output_d(self): return self._output_d
    def evaluate(self):
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        condition = self.get_parameter_value(self.condition)
        if condition is STATUS_WAITING: return
        if not condition:
            self._set_ready()
            return
        min_value = self.get_parameter_value(self.min_value)
        max_value = self.get_parameter_value(self.max_value)
        if min_value is STATUS_WAITING: return
        if max_value is STATUS_WAITING: return
        self._set_ready()
        if (min_value is None) and (max_value is None):
            min_value = 0.0
            max_value = 1.0
        elif min_value is None:
            if isinstance(max_value, int): min_value = -(sys.maxsize)
            elif isinstance(max_value, float): min_value = sys.float_info.min
        elif max_value is None:
            if isinstance(min_value, int): max_value = sys.maxsize
            elif isinstance(min_value, float): max_value = sys.float_info.max
        do_int = isinstance(min_value, int) and isinstance(max_value, int)
        if do_int:
            self._output_a = random.randint(min_value, max_value)
            self._output_b = random.randint(min_value, max_value)
            self._output_c = random.randint(min_value, max_value)
            self._output_d = random.randint(min_value, max_value)
        else:
            delta = max_value - min_value
            self._output_a = min_value + (delta * random.random())
            self._output_b = min_value + (delta * random.random())
            self._output_c = min_value + (delta * random.random())
            self._output_d = min_value + (delta * random.random())


class ActionTranslate(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.moving_object = None
        self.dx = None
        self.dy = None
        self.dz = None
        self.speed = None
        self._t = None
        self._old_values = None
        self.local = None
    def evaluate(self):
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        condition = self.get_parameter_value(self.condition)
        if condition is STATUS_WAITING: return
        if not condition:
            self._set_value(False)
            return self._set_ready()
        moving_object = self.get_parameter_value(self.moving_object)
        dx = self.get_parameter_value(self.dx)
        dy = self.get_parameter_value(self.dy)
        dz = self.get_parameter_value(self.dz)
        speed = self.get_parameter_value(self.speed)
        local = self.get_parameter_value(self.local)
        if moving_object is STATUS_WAITING: return
        if dx is STATUS_WAITING: return
        if dy is STATUS_WAITING: return
        if dz is STATUS_WAITING: return
        if speed is STATUS_WAITING: return
        if local is STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(moving_object): return
        if dx is None: return
        if dy is None: return
        if dz is None: return
        if speed is None: return
        if local is None: return
        new_values = (moving_object, dx, dy, dz, speed, local)
        if new_values != self._old_values:
            start_pos = moving_object.localPosition if local else moving_object.worldPosition
            end_pos = mathutils.Vector((start_pos.x + dx, start_pos.y + dy, start_pos.z + dz))
            distance = (start_pos - end_pos).length
            time_to_destination = distance / speed
            t_speed = 1.0 / time_to_destination
            self._old_values = new_values
            self._start_pos = start_pos.copy()
            self._end_pos = end_pos.copy()
            self._d_pos = (end_pos - start_pos)
            self._t_speed = t_speed
            self._t = 0.0
        t = self._t
        dt = self._t_speed * self.network.time_per_frame
        t += dt
        if t >= 1.0:
            self._set_value(True)
            self._t = 0.0
            if local:
                moving_object.localPosition = self._end_pos.copy()
            else:
                moving_object.worldPosition = self._end_pos.copy()
        else:
            npos = self._start_pos + (self._d_pos * t)
            if local: moving_object.localPosition = npos
            else: moving_object.worldPosition = npos;
            self._t = t
            self._set_value(False)


#Action "Move To": an object will follow a point
class ActionMoveTo(ActionCell):

    def __init__(self):
        ActionCell.__init__(self)
        #list of parameters of this action
        self.condition = None
        self.moving_object = None
        self.destination_point = None
        self.speed = None
        self.distance = None
        self.dynamic = None

    def evaluate(self):#the actual execution of this cell
        condition = self.get_parameter_value(self.condition)
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        if condition is STATUS_WAITING: return self._set_value(False)
        if not condition:
            self._set_value(False)
            return self._set_ready()
        moving_object = self.get_parameter_value(self.moving_object)
        destination_point = self.get_parameter_value(self.destination_point)
        speed = self.get_parameter_value(self.speed)
        distance = self.get_parameter_value(self.distance)
        dynamic = self.get_parameter_value(self.dynamic)
        if moving_object is STATUS_WAITING: return
        if destination_point is STATUS_WAITING: return
        if speed is STATUS_WAITING: return
        if distance is STATUS_WAITING: return
        if dynamic is STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(moving_object): return self._set_value(False)
        if none_or_invalid(destination_point): return self._set_value(False)
        if speed is None: return self._set_value(False)
        if distance is None: return self._set_value(False)
        self._set_value(move_to(
            moving_object,
            destination_point,
            speed,
            self.network.time_per_frame,
            dynamic,
            distance))


class ActionRotateTo(ActionCell):
    def __init__(self):
        self.condition = None
        self.moving_object = None
        self.target_point = None
        self.rot_axis = None
        self.front_axis = None
        self.speed = None
    def evaluate(self):
        self._set_value(False)
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        condition = self.get_parameter_value(self.condition)
        if condition is STATUS_WAITING: return
        if not condition:  return self._set_ready()
        moving_object = self.get_parameter_value(self.moving_object)
        target_point = self.get_parameter_value(self.target_point)
        speed = self.get_parameter_value(self.speed)
        rot_axis = self.get_parameter_value(self.rot_axis)
        front_axis = self.get_parameter_value(self.front_axis)
        if moving_object is STATUS_WAITING: return
        if target_point is STATUS_WAITING: return
        if speed is STATUS_WAITING: return
        if rot_axis is STATUS_WAITING: return
        if front_axis is STATUS_WAITING: return
        self._set_ready()
        if not condition: return
        if none_or_invalid(moving_object): return
        if none_or_invalid(target_point): return
        if rot_axis is None: return
        if front_axis is None: return
        if rot_axis == 0:
            self._set_value(xrot_to(moving_object, target_point, front_axis, speed, self.network.time_per_frame))
        elif rot_axis == 1:
            self._set_value(yrot_to(moving_object, target_point, front_axis, speed, self.network.time_per_frame))
        elif rot_axis == 2:
            self._set_value(zrot_to(moving_object, target_point, front_axis, speed, self.network.time_per_frame))


class ActionNavigateWithNavmesh(ActionCell):
    class MotionPath(object):
        def __init__(self):
            self.points = []
            self.cursor = 0
            self.destination = None
            pass
        def next_point(self):
            if self.cursor < len(self.points):
                return self.points[self.cursor]
            else:
                return None
        def destination_changed(self, new_destination):
            return self.destination != new_destination
        def advance(self):
            self.cursor += 1
            return self.cursor < len(self.points)
        pass
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.moving_object = None
        self.rotating_object = None
        self.navmesh_object = None
        self.destination_point = None
        self.move_dynamic = None
        self.linear_speed = None
        self.reach_threshold = None
        self.look_at = None
        self.rot_axis = None
        self.front_axis = None
        self.rot_speed = None
        self._motion_path = None
    def evaluate(self):
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        condition = self.get_parameter_value(self.condition)
        if condition is STATUS_WAITING: return
        if not condition:
            self._set_ready()
            return
        moving_object = self.get_parameter_value(self.moving_object)
        rotating_object = self.get_parameter_value(self.rotating_object)
        navmesh_object = self.get_parameter_value(self.navmesh_object)
        destination_point = self.get_parameter_value(self.destination_point)
        move_dynamic = self.get_parameter_value(self.move_dynamic)
        linear_speed = self.get_parameter_value(self.linear_speed)
        reach_threshold = self.get_parameter_value(self.reach_threshold)
        look_at = self.get_parameter_value(self.look_at)
        rot_axis = self.get_parameter_value(self.rot_axis)
        front_axis = self.get_parameter_value(self.front_axis)
        rot_speed = self.get_parameter_value(self.rot_speed)
        if moving_object is STATUS_WAITING: return
        if rotating_object is STATUS_WAITING: return
        if navmesh_object is STATUS_WAITING: return
        if destination_point is STATUS_WAITING: return
        if move_dynamic is STATUS_WAITING: return
        if linear_speed is STATUS_WAITING: return
        if reach_threshold is STATUS_WAITING: return
        if look_at is STATUS_WAITING: return
        if rot_axis is STATUS_WAITING: return
        if front_axis is STATUS_WAITING: return
        if rot_speed is STATUS_WAITING: return
        self._set_ready()
        self._set_value(False)
        if none_or_invalid(moving_object): return
        if none_or_invalid(navmesh_object): return
        if none_or_invalid(rotating_object): rotating_object = None
        if destination_point is None: return
        if move_dynamic is None: return
        if linear_speed is None: return
        if reach_threshold is None: return
        if look_at is None: return
        if rot_axis is None: return
        if front_axis is None: return
        if (self._motion_path is None) or (self._motion_path.destination_changed(destination_point)):
            points = navmesh_object.findPath(moving_object.worldPosition, destination_point)
            motion_path = ActionNavigateWithNavmesh.MotionPath()
            motion_path.points = points[1:]
            motion_path.destination = mathutils.Vector(destination_point)
            self._motion_path = motion_path
        next_point = self._motion_path.next_point()
        if next_point:
            tpf = self.network.time_per_frame
            if look_at and (rotating_object is not None):
                rot_to(rot_axis, rotating_object, next_point, front_axis, rot_speed, tpf)
            reached = move_to(moving_object, next_point, linear_speed, tpf, move_dynamic, reach_threshold)
            if reached:
                has_more = self._motion_path.advance()
                if not has_more:
                    self._set_value(True)
        pass


class ActionFollowPath(ActionCell):
    class MotionPath(object):
        def __init__(self):
            self.points = []
            self.cursor = 0
            self.loop = False
            self.loop_start = 0
            pass
        def next_point(self):
            if self.cursor < len(self.points):
                return self.points[self.cursor]
            else:
                return None
        def advance(self):
            self.cursor += 1
            if self.cursor < len(self.points):
                return True
            else:
                if self.loop:
                    self.cursor = self.loop_start
                    return True
                return False
        pass
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.moving_object = None
        self.rotating_object = None
        self.path_parent = None
        self.loop = None
        self.navmesh_object = None
        self.move_dynamic = None
        self.linear_speed = None
        self.reach_threshold = None
        self.look_at = None
        self.rot_axis = None
        self.front_axis = None
        self.rot_speed = None
        self._motion_path = None
    def evaluate(self):
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        condition = self.get_parameter_value(self.condition)
        if condition is STATUS_WAITING: return
        if not condition:
            self._motion_path = None
            self._set_ready()
            return
        moving_object = self.get_parameter_value(self.moving_object)
        rotating_object = self.get_parameter_value(self.rotating_object)
        path_parent = self.get_parameter_value(self.path_parent)
        navmesh_object = self.get_parameter_value(self.navmesh_object)
        move_dynamic = self.get_parameter_value(self.move_dynamic)
        linear_speed = self.get_parameter_value(self.linear_speed)
        reach_threshold = self.get_parameter_value(self.reach_threshold)
        look_at = self.get_parameter_value(self.look_at)
        rot_axis = self.get_parameter_value(self.rot_axis)
        front_axis = self.get_parameter_value(self.front_axis)
        rot_speed = self.get_parameter_value(self.rot_speed)
        loop = self.get_parameter_value(self.loop)
        if moving_object is STATUS_WAITING: return
        if rotating_object is STATUS_WAITING: return
        if path_parent is STATUS_WAITING: return
        if navmesh_object is STATUS_WAITING: return
        if move_dynamic is STATUS_WAITING: return
        if linear_speed is STATUS_WAITING: return
        if reach_threshold is STATUS_WAITING: return
        if look_at is STATUS_WAITING: return
        if rot_axis is STATUS_WAITING: return
        if front_axis is STATUS_WAITING: return
        if rot_speed is STATUS_WAITING: return
        if loop is None: return
        self._set_ready()
        self._set_value(False)
        if none_or_invalid(moving_object): return
        if none_or_invalid(navmesh_object): navmesh_object = None
        if none_or_invalid(path_parent): return
        if move_dynamic is None: return
        if linear_speed is None: return
        if reach_threshold is None: return
        if look_at is None: return
        if rot_axis is None: return
        if front_axis is None: return
        if (self._motion_path is None) or (self._motion_path.loop != loop):
            self.generate_path(moving_object.worldPosition, path_parent, navmesh_object, loop)
        next_point = self._motion_path.next_point()
        if next_point:
            tpf = self.network.time_per_frame
            if look_at:
                rot_to(rot_axis, rotating_object, next_point, front_axis, rot_speed, tpf)
            reached = move_to(moving_object, next_point, linear_speed, tpf, move_dynamic, reach_threshold)
            if reached:
                has_more = self._motion_path.advance()
                if not has_more:
                    self._set_value(True)
        pass
    def generate_path(self, start_position, path_parent, navmesh_object, loop):
        children = sorted(path_parent.children, key=lambda o : o.name)
        if not children:
            return self._motion_path.points.clear()
        path = ActionFollowPath.MotionPath()
        path.loop = loop
        points = path.points
        self._motion_path = path
        if not navmesh_object:
            points.append(mathutils.Vector(start_position))
            if loop: path.loop_start = 1
            for c in children: points.append(c.worldPosition.copy())
        else:
            last = children[-1]
            mark_loop_position = loop
            for c in children:
                subpath = navmesh_object.findPath(start_position, c.worldPosition)
                if c is last:
                    points.extend(subpath)
                else:
                    points.extend(subpath[:-1])
                if mark_loop_position:
                    path.loop_start = len(points)
                    mark_loop_position = False
                start_position = c.worldPosition
            if loop:
                subpath = navmesh_object.findPath(last.worldPosition, children[0].worldPosition)
                points.extend(subpath[1:])
        pass


class ParameterDistance(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self.parama = None
        self.paramb = None
    def evaluate(self):
        parama = self.get_parameter_value(self.parama)
        paramb = self.get_parameter_value(self.paramb)
        if parama is LogicNetworkCell.STATUS_WAITING: return
        if paramb is LogicNetworkCell.STATUS_WAITING: return
        self._set_ready()
        self._set_value(compute_distance(parama, paramb))


class ActionSwapParent(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.child_object = None
        self.parent_name = None
        self.condition = None
    def evaluate(self):
        STATUS_WAITING = LogicNetworkCell.STATUS_WAITING
        condition = self.get_parameter_value(self.condition)
        if condition is STATUS_WAITING: return
        if not condition:
            return self._set_ready()
        parent_name = self.get_parameter_value(self.parent_name)
        child_object = self.get_parameter_value(self.child_object)
        if parent_name is STATUS_WAITING: return
        if child_object is STATUS_WAITING: return
        self._set_ready()
        if none_or_invalid(child_object): return
        current_parent = child_object.parent
        if current_parent is None: return
        if current_parent.name == parent_name: return
        child_orientation = child_object.worldOrientation.copy()
        new_parent = child_object.scene.addObject(parent_name)
        new_parent.worldPosition = current_parent.worldPosition.copy()
        new_parent.worldOrientation = current_parent.worldOrientation.copy()
        child_object.setParent(new_parent, False, False)
        child_object.localPosition = mathutils.Vector((0,0,0))
        child_object.worldOrientation = child_orientation
        current_parent.endObject()


class ActionReplaceMesh(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.target_game_object = None
        self.new_mesh_name = None
        self.use_display = None
        self.use_physics = None
        pass

    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        self._set_ready()
        if not condition: return
        target = self.get_parameter_value(self.target_game_object)
        mesh = self.get_parameter_value(self.new_mesh_name)
        display = self.get_parameter_value(self.use_display)
        physics = self.get_parameter_value(self.use_physics)
        if target is None or target.invalid: return
        if mesh is None: return
        if display is None: return
        if physics is None: return
        target.replaceMesh(mesh, display, physics)


class ActionAlignAxisToVector(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.game_object = None
        self.vector = None
        self.axis = None
        self.factor = None
        pass
    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        self._set_ready()
        if not condition: return
        game_object = self.get_parameter_value(self.game_object)
        vector = self.get_parameter_value(self.vector)
        axis = self.get_parameter_value(self.axis)
        factor = self.get_parameter_value(self.factor)
        if (game_object is None) or (game_object.invalid): return
        if vector is None: return
        if axis is None: return
        if factor is None: return
        game_object.alignAxisToVect(vector, axis, factor)


class ActionUpdateBitmapFontQuads(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.game_object = None
        self.text = None
        self.grid_size = None
        self.condition = None
    def evaluate(self):#no status waiting, test
        condition = self.get_parameter_value(self.condition)
        if not condition: return self._set_ready()
        self._set_ready()
        game_object = self.get_parameter_value(self.game_object)
        text = eval(self.get_parameter_value(self.text))
        grid_size = self.get_parameter_value(self.grid_size)
        if none_or_invalid(game_object): return
        if text is None: text = ""
        if grid_size is None: return
        uv_size = 1.0 / grid_size
        mesh = game_object.meshes[0]
        quad_count = int(mesh.getVertexArrayLength(0) / 4)
        text_size = len(text)
        char_index = 0
        ASCII_START = 32
        for i in range(0, quad_count):
            row = 0
            column = 0
            if char_index < text_size:
                ascii_code = ord(text[char_index])
                grid_code = ascii_code - ASCII_START
                row = int(grid_code / grid_size)
                column = int(grid_code % grid_size)
                char_index += 1
            v0 = mesh.getVertex(0, i * 4)
            v1 = mesh.getVertex(0, i * 4 + 1)
            v2 = mesh.getVertex(0, i * 4 + 2)
            v3 = mesh.getVertex(0, i * 4 + 3)
            xmin = uv_size * column
            xmax = uv_size * (column + 1)
            ymax = 1.0 - (uv_size * row)
            ymin = 1.0 - (uv_size * (row + 1))
            v0.u = xmin
            v0.v = ymin
            v1.u = xmax
            v1.v = ymin
            v2.u = xmax
            v2.v = ymax
            v3.u = xmin
            v3.v = ymax


class ActionSetCurrentScene(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.condition = None
        self.scene_name = None
    def evaluate(self):
        condition = self.get_parameter_value(self.condition)
        self._set_ready()
        if not condition: return
        scene_name = self.get_parameter_value(self.scene_name)
        if scene_name is None: return
        current_scene = bge.logic.getCurrentScene()
        current_scene_name = current_scene.name
        if current_scene_name != scene_name:
            bge.logic.addScene(scene_name)
            current_scene.end()
            pass
        pass

class ParameterKeyboardKeyCode(ParameterCell):
    def __init__(self):
        ParameterCell.__init__(self)
        self.key_code = None
    def evaluate(self):
        self._set_ready()
        key_code = self.get_parameter_value(self.key_code)
        self._set_value(key_code)
        pass
    pass

class ActionStringOp(ActionCell):
    def __init__(self):
        ActionCell.__init__(self)
        self.opcode = None
        self.condition = None
        self.input_string = None
        self.input_param_a = None
        self.input_param_b = None
    def evaluate(self):
        self._set_ready()
        code = self.get_parameter_value(self.opcode)
        condition = self.get_parameter_value(self.condition)
        input_string = self.get_parameter_value(self.input_string)
        input_param_a = self.get_parameter_value(self.input_param_a)
        input_param_b = self.get_parameter_value(self.input_param_b)
        if not condition: return
        if input_string is None: return
        input_string = str(input_string)
        if code == 0:#postfix
            self._set_value(input_string + str(input_param_a))
        elif code == 1:#prefix
            self._set_value(str(input_param_a) + input_string)
        elif code == 2:#infix
            self._set_value(str(input_param_a) + input_string + str(input_param_b))
        elif code == 3:#remove last
            self._set_value(input_string[:-1])
        elif code == 4:#remove first
            self._set_value(input_string[1:])
        elif code == 5:#replace a with b in string
            self._set_value(input_string.replace(str(input_param_a), str(input_param_b)))
        elif code == 6:#upper case
            self._set_value(input_string.upper())
        elif code == 7:#lower case
            self._set_value(input_string.lower())
        elif code == 8:#remove range
            self._set_value(input_string[:input_param_a]+input_string[input_param_b:])
        elif code == 9:#insert at
            self._set_value(input_string[:input_param_b] + str(input_param_a) + input_string[input_param_b:])
        elif code == 10:#length
            self._set_value(len(input_string))
        elif code == 11:#substring
            self._set_value(input_string[input_param_a:input_param_b])
        elif code == 12:#first index of
            self._set_value(input_string.find(str(input_param_a)))
        elif code == 13:#last index of
            self._set_value(input_string.rfind(str(input_param_a)))
        pass
    pass

class ParameterMathFun(ParameterCell):
    @classmethod
    def signum(cls, a): return (a > 0) - (a < 0)
    @classmethod
    def curt(cls, a):
        if a > 0: return a**(1./3.)
        else: return -(-a)**(1./3.)
    def __init__(self):
        ParameterCell.__init__(self)
        self.a = None
        self.b = None
        self.c = None
        self.d = None
        self.formula = ""
        self._previous_values = [None, None, None, None]
        self._formula_globals = globals();
        self._formula_locals = {
            "exp":math.exp,
            "pow":math.pow,
            "log":math.log,
            "log10":math.log10,
            "acos":math.acos,
            "asin":math.asin,
            "atan":math.atan,
            "atan2":math.atan2,
            "cos":math.cos,
            "hypot":math.hypot,
            "sin":math.sin,
            "tan":math.tan,
            "degrees":math.degrees,
            "radians":math.radians,
            "acosh":math.acosh,
            "asinh":math.asinh,
            "atanh":math.atanh,
            "cosh":math.cosh,
            "sinh":math.sinh,
            "tanh":math.tanh,
            "pi":math.pi,
            "e":math.e,
            "ceil":math.ceil,
            "sign":ParameterMathFun.signum,
            "abs":math.fabs,
            "floor":math.floor,
            "mod":math.fmod,
            "sqrt":math.sqrt,
            "curt":ParameterMathFun.curt,
            "str":str,
            "int":int,
            "float":float
        }
    def evaluate(self):
        self._set_ready()
        a = self.get_parameter_value(self.a)
        b = self.get_parameter_value(self.b)
        c = self.get_parameter_value(self.c)
        d = self.get_parameter_value(self.d)
        olds = self._previous_values
        do_update = (
            (a != olds[0]) or
            (b != olds[1]) or
            (c != olds[2]) or
            (d != olds[3]))
        if do_update:
            formula_locals = self._formula_locals
            formula_locals["a"] = a
            formula_locals["b"] = b
            formula_locals["c"] = c
            formula_locals["d"] = d
            out = eval(self.formula, self._formula_globals, formula_locals)
            olds[0] = a
            olds[1] = b
            olds[2] = c
            olds[3] = d
            self._set_value(out);
            pass