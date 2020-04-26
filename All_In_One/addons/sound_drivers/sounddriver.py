import bpy

from bpy.types import FCurve, Operator
from bpy.utils import register_class, unregister_class
from mathutils import Vector, Color, Euler, Quaternion

from bpy.app.handlers import persistent

from bpy.props import StringProperty, PointerProperty, BoolProperty,\
    IntProperty, CollectionProperty, FloatProperty,\
    EnumProperty

from bpy.types import PropertyGroup

from sound_drivers.utils import (getSpeaker,
                                 getAction,
                                 remove_handlers_by_prefix,
                                 get_driver_settings,
                                 driver_expr,
                                 bpy_collections,
                                 remove_draw_pend,
                                 )

from sound_drivers import debug
from sound_drivers.driver_manager import DriverManager, SoundDriver
'''
Update methods
'''
def main(self, context, edit_driver, speaker, action, channel_list):
    if context is None or not len(channel_list):
        return False

    space = context.space_data
    search = True
    if action is not None:
        channel = action["channel_name"]
    driver = edit_driver.fcurve

    if driver:
        all_channels, args = get_driver_settings(driver)
        speaker_channels = [ch for ch in all_channels if
                            ch.startswith(channel)]

        diff = set(all_channels) - set(speaker_channels)
        driver = driver.driver
        s = driver.expression
        d = s.find("SoundDrive")
        if d > -1:
            m = s.find(")", d) + 1
            fmt = s.replace(s[d:m], "%s")
        else:
            fmt = "%s"

        # remove vars
        for ch in set(speaker_channels) - set(channel_list):
            var = driver.variables.get(ch)
            if var:
                driver.variables.remove(var)

        extravars = ""
        if self.amplify != 1.0:
            extravars += ",amplify=%0.4f" % self.amplify
        if self.threshold != 0.0:
            extravars += ",threshold=%0.4f" % self.threshold
        if self.op != 'avg':
            extravars += ",op='%s'" % self.op
        channels = diff | set(channel_list)
        channels_list = list(sorted(channels))
        ctxt = str(channels_list).replace("'", "").replace(" ", "")
        new_expr = 'SoundDrive(%s%s)' % (ctxt, extravars)
        new_expr = new_expr.replace("[,", "[")
        if len(new_expr) < 256:
            driver.expression = fmt % new_expr
            for channel in channel_list:
                var = driver.variables.get(channel)
                if var is None:
                    var = driver.variables.new()
                var.type = "SINGLE_PROP"
                var.name = channel
                target = var.targets[0]
                target.id_type = "SPEAKER"
                target.id = speaker.id_data
                target.data_path = '["%s"]' % channel


def update_dm(self, context):
    dns = bpy.app.driver_namespace
    dm = dns.get("DriverManager")

    if dm is not None:
        dm.get_all_drivers_list()

bpy.types.WindowManager.update_dm =\
    BoolProperty(description="Refresh Driver List",
                             update=update_dm)


def toggle_driver_fix(self, context):
    handler = bpy.app.handlers.frame_change_post

    handlers = [f for f in handler if f.__name__ == "mat_driver_fix"]
    for f in handlers:
        handler.remove(f)
    if self.mdf:
        bpy.app.handlers.frame_change_post.append(mat_driver_fix)


def wonk(self, context):
    dm = context.driver_manager
    sp = context.scene.speaker
    a = getAction(sp)  # REFACTO
    a = bpy.data.actions.get(self.action)
    if dm is None or sp is None or a is None:
        return None
    p = self.path_from_id()
    '''
    print(p) #REFACTO
    p = p[:p.find(".channels")]
    print(p)
    gui = self.id_data.path_resolve(p)
    if gui is None:
        print("NO GUI")
        return None

    '''
    gui = self
    idx = int(self.name.split("_")[1])
    #ed = dm.find(dm.filter_dic[gui.collection][gui.object][str(gui.array_index)])
    d = dm.find(idx)
    ed = self
    if ed is None:
        return None
    if d._setting_channels:
        return None
    #cn = a['channel_name']
    cn = self.channel
    if self.rna_type.identifier.startswith('SoundDriverChannel'):
        pass
    elif self.rna_type.identifier.startswith('GUIDriver'):
        channel_list = [ch.name for ch in ed.channels if
                        ch.value and ch.name.startswith(cn)]
        main(self, context, d, sp, a, channel_list)
        # do amplify things etc
        pass
    #main(self, context, speaker, action, channel_list)


def callback(driver_objects, collection):
    print("callback", collection)
    return
    dns = bpy.app.driver_namespace
    dm = dns.get("DriverManager")
    if collection.startswith("ob"):
        obdic = dm.get_driven_scene_objects(driver_objects.id_data)
    else:
        obdic = dm.get_collection_dic(collection)
    driven_objects = [o for o in obdic.keys()]
    col = getattr(driver_objects, collection)
    # remove all
    for o in col:
        col.remove(0)

    for o in driven_objects:
        # obdic[o] all drivers for that object
        # obdic[o].keys() all driven datapaths
        x = col.add()
        x.name = o
        '''
        for dp, idic in obdic[o].items():
            for idx, dm_i in idic.items():
                x = col.add()
                x.name = o
                x.data_path = dp
                x.array_index = int(idx)
                x.index = dm_i

        '''

def collection_update_func(prop):
    def update(self, context):
        callback(self, prop)
    return update

'''
Handlers
'''

def set_var_index(self, context):
    return None
    dm = context.driver_manager

    if self.varname == "":
        self.var_index = -1
        return

    dm.query_driver_list(collection=self.collection,
                         object=self.object,
                         data_path=self.data_path,
                         array_index=self.array_index)

    return


def xxxx(self, context):
    id_data = self.id_data
    p = self.path_from_id()
    p = p[:p.find(".channels")]
    driver_gui = self.id_data.path_resolve(p)
    idx = int(driver_gui.name[3:])
    dm = context.driver_manager
    ed = dm.find(idx)
    if ed is not None:
        sp = context.scene.speaker
        a = getAction(sp)
        a = bpy.data.actions.get(driver_gui.action)
        if a is None:
            return None
        cn = a["channel_name"]
        cn = driver_gui.channel

        if not self.value:
            bpy.ops.dm.remove_driver_var(varname=self.name, dindex=ed.index)  # REFACTO
        else:
            channel_list = [ch.name for ch in driver_gui.channels if
                            ch.value and ch.name.startswith(cn)]
            main(driver_gui, context, ed, sp, a, channel_list)

    return None

def load_channels(self, context):
    scene = context.scene
    a = bpy.data.actions.get(self.action)
    dm = context.driver_manager
    driver = dm.find(int(self.name[3:]))
    driver = driver.fcurve.driver

    if a is not None:
        cn = self.channel
        channels = a["Channels"]
        chs = [ch for ch in self.channels if ch.name.startswith(cn)]
        exist = len(chs) == channels
        if not exist:
            # self.channels.clear()
            for ch in chs:
                self.channels.remove(self.channels.find(ch.name))
        if len(chs) != channels:
            for i in range(0, channels):
                channel = chs[i] if exist else self.channels.add()
                channel.name = "%s%d" % (cn, i)
                if channel.name in driver.variables.keys():
                    dvar = driver.variables[channel.name]
                    if dvar.targets[0].id == scene.speaker:
                        channel.value = True
                    else:
                        # variable there but with other speaker alert
                        pass
                else:
                    channel.value = False

    return None

def speaker_channels(self, context):
    channels = []
    if hasattr(context.scene, "speaker"):
        channels = getattr(context.scene.speaker, "channels", [])
    # print(channels)
    return[(ch, ch, "Drive with %s%d" % (ch, 2*i)) for i, ch in enumerate(channels)]

def aget(self):
    actions = [a.name for a in bpy.data.actions if "channel_name" in a.keys() and (
        a.get("channel_name") == self.channel or self.channel in a.get("channels", []))]
    if len(actions):
        return actions[0]
    else:
        return "None"

def gui_type_items(self, context):
    gui_types = [("DRIVER", "", "Standard Driver Settings", 'DRIVER', 1)]
    #("EXPRESSION", "", "Standard Driver Settings", 'FILE_SCRIPT', 16),
    if len(bpy.data.speakers):  # LAZY FIX WITH PROPER
        gui_types.extend([("SOUNDDRIVER", "", "Sound Driver", 'SOUND', 2)])
    if context.scene.speaker is not None:
        gui_types.extend([("ACTION", "", "Show Baked Actions", 'ACTION', 4)])
        #("VISUALISER_UNIT", "", "Visualiser Unit", 'SEQ_HISTOGRAM', 4),
    return gui_types

def enum_up(self, context):
    if 'ACTION' in self.gui_types:
        if 'SOUNDDRIVER' not in self.gui_types:  # is subset
            print("ADDDDD SOUNDDRIVER")
            self.gui_types |= {'SOUNDDRIVER'}

    return None

def register_props():
    BPY_COLLECTION_TYPE = type(bpy.data.objects)
    prop_dict = {}
    '''
    bpy_collections.clear()
    for name in dir(bpy.data):
        o = getattr(bpy.data, name)
        if isinstance(o, BPY_COLLECTION_TYPE):
            prop_dict[name] = BoolProperty(default=False)
            bpy_collections.append(name)

    '''
    for name in bpy_collections:
        prop_dict[name] = BoolProperty(default=False)
    filters = type('Filters', (PropertyGroup,), prop_dict)
    #expanders = type('Expand', (PropertyGroup,), prop_dict)

    ch_dic = {}
    ch_dic["value"] = FloatProperty(default=0.0)
    #ch_dic["rna_type"] = StringProperty()

    DriverVar = type('DriverVar', (PropertyGroup,), ch_dic)
    register_class(DriverVar)

    ch_dic = {}
    #ch_dic["name"] = StringProperty(default="driver")
    ch_dic["value"] = BoolProperty(default=False, update=xxxx)

    SoundDriverChannel = type('SoundDriverChannel', (PropertyGroup,), ch_dic)
    register_class(SoundDriverChannel)

    prop_dic = {}

    prop_dic["collection"] = StringProperty(default="",
                                            description="Driven Object Collection")  # MFD
    prop_dic["object"] = StringProperty(default="",
                                        description="Driven Object")  # MFD

    prop_dic["data_path"] = StringProperty(default="")
    prop_dic["array_index"] = IntProperty(default=0)
    prop_dic["channels"] = CollectionProperty(type=SoundDriverChannel)
    prop_dic["vars"] = CollectionProperty(type=DriverVar)
    amplify = FloatProperty(name="Amplify",
                            default=1.0,
                            min=-1000,
                            max=1000,
                            description="Amplify the output",
                            update=wonk,
                            soft_min=-10.0,
                            soft_max=10.0)

    prop_dic["amplify"] = amplify
    prop_dic["use_threshold"] = BoolProperty(default=False)
    threshold = FloatProperty(name="Threshold",
                              default=0.0,
                              min=0.0,
                              max=1000,
                              description="Only calculate when input is greater\
                              than threshold",
                              update=wonk,
                              soft_max=10.0)
    prop_dic["threshold"] = threshold
    prop_dic["varname"] = StringProperty(default="var",
                                         name="Driver Variable Name",
                                         update=set_var_index)
    prop_dic["var_index"] = IntProperty(default=-1,
                                        name="Driver Variable Index")
    op = EnumProperty(items=(
        ("sum", "SUM", "Sum Values"),
        ("avg", "AVERAGE", "Average Value"),
        ("min", "MIN", "Minimum Value"),
        ("max", "MAX", "Maximum Value")
    ),
        name="Function",
        default="avg",
        description="Method for Channel List",
        update=wonk,
    )

    gui_types = EnumProperty(items=gui_type_items,
        name="Driver Display",
        # default={'DRIVER'},  # default can't be set when items is a func.
        description="Driver Details to Display (Multi Select)",
        options={'HIDDEN', 'ENUM_FLAG'},
        update=enum_up,
        # update=wonk,
    )

    gui_type = EnumProperty(items=(
        ("STD", "Standard", "Standard Interface", 'DRIVER', 0),
        ("SPK", "SoundDriver", "Sound Driver", 'SOUND', 1)
    ),
        name="Choose Interface",
        default="STD",
        description="Driver GUI Type",
        # update=wonk,
    )

    #prop_dic["channel"] = StringProperty(default="", update=load_channels)
    prop_dic["channel"] = EnumProperty(items=speaker_channels,
                                       name="ActionBakeChannel",
                                       description="Baked Channel",
                                       )
    prop_dic["action"] = property(aget)
    prop_dic["gui_types"] = gui_types
    prop_dic["gui_type"] = gui_type
    prop_dic["op"] = op
    prop_dic["value"] = FloatProperty(default=0.0, options={'ANIMATABLE'})
    prop_dic["array_index"] = IntProperty(default=0)

    GUIDriver = type('GUIDriver', (PropertyGroup,), prop_dic)
    register_class(GUIDriver)

    register_class(filters)
    # register_class(expanders)
    # remove it for reload same file.
    # unload should be called from pre load handler
    # SOUND_DRIVERS_unload(dummy)
    '''
    print("Setting Up Driver Manager")

    dm = bpy.app.driver_namespace.get("DriverManager")
    if not dm:
        dm = DriverManager()
        bpy.app.driver_namespace["DriverManager"] = dm
    else:
        dm.edit_driver = None

    '''
    prop_dic = {"drivers": CollectionProperty(type=GUIDriver)}

    GUIDrivers = type('GUIDrivers', (PropertyGroup,), prop_dic)

    register_class(GUIDrivers)

    prop_dict = {}
    prop_dict["use_filters"] = BoolProperty(default=False)
    prop_dict["filters"] = PointerProperty(type=filters)

    for col in bpy_collections:
        propname = "search_%s" % col
        prop_dict[propname] = BoolProperty(default=False, description="Search for %s drivers" % col, update=collection_update_func(col))
        prop_dict["active_%s_index" % col] = IntProperty()
        prop_dict[col] = CollectionProperty(type=GUIDrivers)

    COLLS = type("COLLS", (PropertyGroup,), prop_dict)
    register_class(COLLS)

    bpy.types.Scene.driver_objects = PointerProperty(type=COLLS)
    bpy.types.WindowManager.mdf = BoolProperty(update=toggle_driver_fix)


@persistent
def SOUND_DRIVERS_load(dummy):
    debug.print("SOUND_DRIVERS_load")

    register_props()

    # remove it for reload same file.
    # unload should be called from pre load handler
    # SOUND_DRIVERS_unload(dummy)
    print("Setting Up Driver Manager")

    dm = bpy.app.driver_namespace.get("DriverManager")
    if not dm:
        dm = DriverManager()
        bpy.app.driver_namespace["DriverManager"] = dm
    else:
        dm.edit_driver = None

@persistent
def SOUND_DRIVERS_unload(dummy):
    debug.print("SPEAKER_TOOLS_unload")

    try:
        #global dm
        dm = bpy.app.driver_namespace.get("DriverManager")
        if dm:
            dm.clear()
            debug.print("Clearing Driver Manager")
        if hasattr(dummy, "driver_objects"):
            for x in dummy.driven_objects:
                x.clear()
    except:
        debug.print("PROBLEM UNLOADING DM")
        pass

# this is ugly and needs fixing

def mat_driver_fix(scene):
    frame = scene.frame_current
    fcurves = [fcurve for mat in bpy.data.materials
               if hasattr(mat, "animation_data") and
               mat.animation_data is not None
               for fcurve in mat.animation_data.drivers]

    for fcurve in fcurves:
        mat = fcurve.id_data
        attr = fcurve.data_path
        print("test ", attr)
        sp = attr.split(".")
        if len(sp) > 1:
            attr = sp.pop()
            mat = mat.path_resolve(".".join(sp))
        index = fcurve.array_index
        value = fcurve.evaluate(frame)
        ob = mat.path_resolve(attr)
        if type(ob).__name__ in ["Vector", "Color", "bpy_props_array"]:
            ob[index] = value
            print(ob, index, value)
        else:
            print(mat.name, attr, value)
            setattr(mat, attr, value)
        return None

'''
Operators
'''

class DriverManager_DriverOp():
    dindex = IntProperty(default=-1,
                         options={'SKIP_SAVE'},
                         description="Driver Manager driver index")

    def get_driver(self):
        dns = bpy.app.driver_namespace
        dm = dns.get("DriverManager")
        if dm is None:
            return None
        return dm.find(self.dindex)

    driver = property(get_driver)

    @classmethod
    def poll(cls, context):
        return cls.driver is not None


class CopyDriverToSelectedObjects(DriverManager_DriverOp, Operator):
    """Copy Driver to Selected Objects"""
    bl_idname = "driver.copy_to_selected_objects"
    bl_label = "Copy to Selected Objects"

    def execute(self, context):
        dm = context.driver_manager
        d = self.driver
        for obj in context.selected_objects:
            try:
                o = obj.path_resolve(d.data_path)
            except:
                continue

            if o is None:
                continue

            if obj.name == d.fcurve.id_data.name:
                continue
            if d.is_vector:
                td = obj.driver_add(d.data_path, d.array_index)
            else:
                td = obj.driver_add(d.data_path)
            dm.copy_driver(d, td)

        dm.get_all_drivers_list()
        return {'FINISHED'}

class SoundDriverActivateChannel(DriverManager_DriverOp, Operator):
    """Activate Channel"""
    bl_idname = "driver.sound_channel_activate"
    bl_label = "Sound Action Channel"
    channel = StringProperty(default="AA")

    def execute(self, context):
        gui = self.driver.driver_gui(context.scene)
        ch = gui.channels.add()
        ch.name = self.channel
        ch.value = True
        return {'FINISHED'}

class SoundDriverAction(DriverManager_DriverOp, Operator):
    """Choose Sound Action Channel"""
    bl_idname = "driver.sound_action"
    bl_label = "Sound Action Channel"
    channel = StringProperty(default="AA")

    def execute(self, context):
        gui = self.driver.driver_gui(context.scene)
        gui.channel = self.channel
        return {'FINISHED'}

class AddDriverVar(DriverManager_DriverOp, Operator):
    """Add Driver Variable"""
    bl_idname = "driver.new_var"
    bl_label = "Add Driver Variable"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        d = self.driver
        if not d:
            return {'CANCELLED'}
        # check if var is in variables
        name = "var"
        i = 1
        if d:
            while name in d.fcurve.driver.variables.keys():
                name = "var%d" % i
                i += 1
        v = d.fcurve.driver.variables.new()
        v.name = name
        gui = d.driver_gui(context.scene)
        gui.varname = v.name
        gui.var_index = d.fcurve.driver.variables.find(v.name)
        return {'FINISHED'}


class EditTextFieldOperator(DriverManager_DriverOp, Operator):
    """Edit Text Field in Popup"""
    bl_idname = "drivermanager.input_text"
    bl_label = "Text Input"

    def draw(self, context):
        edit_driver = self.driver
        driver = edit_driver.fcurve.driver
        layout = self.layout
        row = layout.row()

        row.label("Driver Scripted Expression", icon='DRIVER')
        row = layout.row()
        row.prop(driver, "expression", text="")
        for var in driver.variables:
            row = layout.row()
            row.label(var.name)

    def check(self, context):
        return True

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=800)

    def execute(self, context):
        return {'FINISHED'}


class UpdateDriverlistOperator(DriverManager_DriverOp, Operator):
    """Driver Manager Update"""
    bl_idname = "drivermanager.update"
    bl_label = "Driver Manager Update"
    name = StringProperty(default="")

    def execute(self, context):
        dm = bpy.app.driver_namespace.get("DriverManager")
        if not dm:
            SOUND_DRIVERS_load(context.scene)
        '''
        else:
            # update the driver list.
            dm.driver_dict = dm.get_driver_dict()
        #global dm
        '''
        return {'FINISHED'}


def test(self, prop):
    return None

class DriverSelectorOperator(DriverManager_DriverOp, Operator):
    """Select Driver"""
    bl_idname = "driver.edit"
    bl_label = "Select Driver"
    #bl_options = {'REGISTER', 'UNDO'}
    array_index = IntProperty(default=0)
    data_path = StringProperty(default="")
    col = StringProperty(default="")
    name = StringProperty(default="")
    toggle = BoolProperty(default=False, options={'SKIP_SAVE'})
    update = BoolProperty(default=False, options={'SKIP_SAVE'})
    x = BoolProperty(default=False, options={'SKIP_SAVE'}, update=test)

    def draw(self, context):
        dm = bpy.app.driver_namespace.get("DriverManager")
        #dm.draw_layout(self.layout, context, [dm.edit_driver])
        self.layout.prop(self, "x")

    def invoke(self, context, event):
        scene = context.scene

        driver = self.driver
        is_open = getattr(driver, "is_open", False)

        if self.update:
            driver.set_edit_driver_gui(scene, create=True)
            return {'FINISHED'}

        elif self.toggle:
            setattr(driver, 'is_open', not is_open)  # REFACTOR
            if driver.is_open:
                #dm.edit_driver = driver
                #driver.set_edit_driver_gui(scene, create=True)
                driver.set_edit_driver_gui(scene)
                #dm.set_edit_driver_gui(context, create=True)
                return {'FINISHED'}

        return self.execute(context)

    def execute(self, context):

        return {'FINISHED'}


class Bake2FCurveOperator(DriverManager_DriverOp, Operator):
    """(un)Bake Driver to Action"""
    bl_idname = "editdriver.bake2fcurves"
    bl_label = "Bake to FCurve"
    option = EnumProperty(items=(('BAKE', 'BAKE', 'BAKE'),
                                 ('UNBAKE', 'UNBAKE', 'UNBAKE'),
                                 ('TOGGLE', 'TOGGLE', 'TOGGLE')
                                 ),
                          default='TOGGLE')

    selection = BoolProperty(default=False, options={'SKIP_SAVE'})

    def get_drivers(self, context):
        # REFACTO
        if self.selection:
            dm = context.driver_manager
            return [d for d in dm.all_drivers_list]
        return [self.driver]

    chunks = 10  # split into 10 parts
    chunks = 4
    chunks = 1
    wait = 0
    #driver = None
    drivers = None
    _timer = None
    pc = 0
    _pc = 0  # where we're up to
    f = 0  # start frame
    bakeframes = []

    def is_baking(self):
        return self.pc < self.chunks

    baking = property(is_baking)

    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            return self.cancel(context)

        if self.wait > 0:
            self.wait -= 1
            return {'PASS_THROUGH'}

        if self.pc >= self.chunks:
            return self.finished(context)

        # REFACTO BAKE
        if event.type == 'TIMER':
            for d in self.drivers:
                self.dindex = d.index
                self.bake(context)
            self.f += self.bakeframes[self.pc]
            self.pc += 1
            self.wait = 5

        return {'PASS_THROUGH'}

    def remove(self, context, driver):
        # remove the fcurve if there is one and return finished.
        driver = driver.fcurve
        obj = driver.id_data
        if obj.animation_data.action is not None:
            raction = obj.animation_data.action

            fcurves = [fcurve for fcurve in raction.fcurves
                       if fcurve.data_path == driver.data_path and
                       fcurve.array_index == driver.array_index]
            if len(fcurves):
                # remove the fcurve and return
                raction.fcurves.remove(fcurves[0])
                # remove the action if empty
                if not len(raction.fcurves):
                    obj.animation_data.action = None
                    if not raction.users:
                        bpy.data.actions.remove(raction)
                return True
        return False

    def bake(self, context, samples=False):
        ''' bake a driver to an action fcurve'''

        # REFACTO add flag to convert between kfs and samples
        def get_action_fcurve(driver):
            obj = driver.fcurve.id_data
            action = obj.animation_data.action  # will have animation_data from driver
            if action is None:
                action = obj.animation_data.action = bpy.data.actions.new("%s (BFD)" % obj.name)
            fc = [fc for fc in action.fcurves if fc.data_path == driver.fcurve.data_path and fc.array_index == driver.fcurve.array_index]
            if len(fc):
                return fc[0]
            fc = action.fcurves.new(driver.data_path, driver.array_index)
            return fc

        scene = context.scene
        frame = self.f
        frame_end = self.f + self.bakeframes[self.pc] - 1
        # bake to scene frame range
        self.driver.edit_driver_baking = True
        setattr(self.driver, "bake_pc", self.pc / self.chunks)
        driver = self.driver.fcurve
        obj = driver.id_data

        #action = speaker.animation_data.action

        # make an unbaked fcurve for the driver.
        # check whether there is already an fcurve

        coords = []
        while frame <= frame_end:
            scene.frame_set(frame)
            co = (frame, self.driver.value)
            v = Vector(co)
            if len(coords) > 1:  # enough to linear test
                v1 = Vector(coords[-1]) - v
                v2 = Vector(coords[-2]) - v
                if v1.length and v2.length and v1.angle(v2) < 0.001:
                    coords[-1] = co
                else:
                    coords.append(co)
            else:
                coords.append(co)
            # quick fix try array, then without
            # REFACTO
            frame += 1
            '''
            # frame by frame kfi
            if self.driver.is_vector:
                driver.id_data.keyframe_insert(driver.data_path,
                                               index=driver.array_index)
            else:
                driver.id_data.keyframe_insert(driver.data_path)

            frame += 1 # REFACTO
            '''

        fc = get_action_fcurve(self.driver)
        l = len(coords)
        # x = []  # refactor got keyframe_points.foreach_set
        for i in range(l):
            fc.keyframe_points.insert(*coords[i])

        if samples:
            fc.convert_to_samples(self.f, frame_end)
        return True

    def execute(self, context):
        scene = context.scene

        self.drivers = self.get_drivers(context)
        r = []
        # REFACTO BAKE
        for d in self.drivers:
            if self.remove(context, d):
                r.append(d)

        if self.option in ('UNBAKE', 'TOGGLE'):
            for d in r:
                self.drivers.remove(d)

        if not len(self.drivers) or self.option == 'UNBAKE':
            return {'FINISHED'}

        self.scene_frame = scene.frame_current
        self.f = scene.frame_start
        frames = scene.frame_end - scene.frame_start
        bakeframes = [frames // self.chunks for i in range(self.chunks)]
        bakeframes[-1] += frames % self.chunks
        self.bakeframes = bakeframes

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.001, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def finished(self, context):
        for d in self.drivers:
            delattr(d, "edit_driver_baking")
            delattr(d, "bake_pc")
        scene = context.scene
        scene.frame_set(self.scene_frame)
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

        return {'FINISHED'}

    def cancel(self, context):
        # scene.frame_set(scene_frame)
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        print("Baking cancelled")
        return {'CANCELLED'}


class RemoveDriverVarOperator(DriverManager_DriverOp, Operator):
    """Remove Driver Variable"""
    bl_idname = "dm.remove_driver_var"
    bl_label = "Remove Driver Variable"
    varname = StringProperty(default="", options={'SKIP_SAVE'})

    def execute(self, context):
        edit_driver = self.driver
        if edit_driver is not None:
            fcurve = edit_driver.fcurve
            d = fcurve.driver
            var = d.variables.get(self.varname)
            if var is None:
                return {'CANCELLED'}

            d.variables.remove(var)

            gui = edit_driver.driver_gui(context.scene)
            if gui is not None:
                if self.varname == gui.varname:
                    gui.varname = d.variables[0].name if len(d.variables) else ""
                    gui.var_index = 0 if len(d.variables) else -1

            channels, args = get_driver_settings(fcurve)
            if self.varname not in channels:
                return {'FINISHED'}
            # remove the channel if one exists for it.
            channel = gui.channels.get(self.varname)
            if channel is not None:
                channel.driver_remove("value")
                index = gui.channels.find(channel.name)
                gui.channels.remove(index)

            channels.pop(channels.index(self.varname))

            d.expression = driver_expr(d.expression, channels, args)
            edit_driver.set_edit_driver_gui(context.scene)  # REFACTO

        return {'FINISHED'}


class EditDriverVarOperator(DriverManager_DriverOp, Operator):
    """Edit Driver Variable"""
    bl_idname = "dm.edit_driver_var"
    bl_label = "Remove Driver Variable"
    varname = StringProperty(default="", options={'SKIP_SAVE'})

    def execute(self, context):
        scene = context.scene
        edit_driver = self.driver
        if edit_driver is not None:
            gui = edit_driver.driver_gui(scene)
            if gui is not None:
                gui.varname = self.varname
                gui.var_index = edit_driver.fcurve.driver.variables.find(self.varname)
            else:
                debug.print("NO GUI")
            # dm.set_edit_driver_gui(context)

        return {'FINISHED'}

class RGBColorFCurves(Operator):
    """Add RGB Color FCurves"""
    bl_idname = "drivermanager.rgb_color_fcurves"
    bl_label = "RGB Color FCurves"

    @classmethod
    def poll(cls, context):
        dm = bpy.app.driver_namespace["DriverManager"]
        return dm is not None

    def execute(self, context):
        dm = bpy.app.driver_namespace["DriverManager"]
        color_drivers = [d for d in dm.all_drivers_list
                         if d.fcurve is not None
                         and (d.is_color or d.is_rgba_color)
                         and d.array_index < 3]
        for d in color_drivers:
            d.fcurve.color = (0, 0, 0)
            d.fcurve.color[d.array_index] = 1
        # main(context)
        return {'FINISHED'}


class DriverManagerDemonkify(Operator):
    """Fix (Remove) Monkeys"""
    bl_idname = "drivermanager.demonkify"
    bl_label = "Demonkify"
    driver_index = IntProperty(default=-1, options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        dm = bpy.app.driver_namespace.get('DriverManager')
        if dm is None:
            print("No Driver Manager")
            return {'CANCELLED'}
        if self.driver_index >= 0:
            monkeys = [dm.all_drivers_list[self.driver_index]]
        else:
            monkeys = [m for m in dm.all_drivers_list if m.is_monkey]
        for m in monkeys:
            var = m.fcurve.driver.variables.get("var")
            m.fcurve.driver.variables.remove(var)
        return {'FINISHED'}

class DriverManagerSettings(Operator):
    """Driver Manager Settings"""
    bl_idname = "driver_manager.settings"
    bl_label = "Tools"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return bpy.ops.wm.call_menu(name="drivermanager.tools_menu")
'''
Panels
'''

class DriverRemoveModifier(DriverManager_DriverOp, Operator):
    """Remove Modifer"""
    bl_idname = "editdriver.remove_modifier"
    bl_label = "Remove Modifier"
    idx = IntProperty(name="Modifier Index", default=0)

    def execute(self, context):
        ed = self.driver
        if ed is None:
            return {'CANCELLED'}
        mod = ed.fcurve.modifiers[self.idx]
        ed.fcurve.modifiers.remove(mod)
        return {'FINISHED'}


class DriverAddModifier(DriverManager_DriverOp, Operator):
    """Add Generator Modifer"""
    bl_idname = "editdriver.add_modifier"
    bl_label = "Add GENERATOR"
    # change to enum property. get list from mod types.
    type = StringProperty(default='GENERATOR')

    def execute(self, context):
        ed = self.driver
        if ed is None:
            return {'CANCELLED'}
        ed.fcurve.modifiers.new(type=self.type)
        return {'FINISHED'}


'''
Menus
'''


class DriverMangagerToolMenu(bpy.types.Menu):
    bl_label = "Driver Manager Tools"
    bl_idname = "drivermanager.tools_menu"

    def draw(self, context):
        scene = context.scene
        wm = context.window_manager
        layout = self.layout

        layout.menu("speaker.select_contextspeaker", icon='SPEAKER')
        layout.menu("soundtest.menu", icon="ACTION")

        op = layout.operator("editdriver.bake2fcurves", icon='FCURVE', text="Bake All")
        op.selection = True
        op.option = 'BAKE'
        op = layout.operator("editdriver.bake2fcurves", icon='FCURVE', text="UnBake All")
        op.selection = True
        op.option = 'UNBAKE'
        layout.operator("drivermanager.rgb_color_fcurves", icon='COLOR')
        layout.operator("drivermanager.demonkify", icon='MONKEY')

        # use an operator enum property to populate a sub-menu
        layout.operator_menu_enum("object.select_by_type",
                                  property="type",
                                  text="Select All by Type...",
                                  )

        # REFACTO
        layout.prop(wm,
                    "mdf",
                    icon='MATERIAL_DATA')


class SimpleCustomMenu(bpy.types.Menu):
    bl_label = "Driver Manager"
    bl_idname = "drivermanager.menu"

    def draw(self, context):
        layout = self.layout
        dm = context.driver_manager
        if dm is None:
            return
        area = context.area
        space = context.space_data
        ctxt = 'NONE'
        if hasattr(space, "context"):
            ctxt = space.context

        # dm.draw_spitter(context) REFACTO 12
        if area.type.startswith('PROPERTIES'):
            layout.label(space.context)
            if space.context.startswith('DATA'):
                layout.label('DATA')
            if space.context.startswith('OBJECT'):
                layout.label('OBJECT')
            if space.context.startswith('MATERIAL'):
                layout.label('MATERIAL')
            if space.context.startswith('TEXTURE'):
                layout.label('TEXTURE')
            if space.context.startswith('MODIFIER'):
                layout.label('MODIFIERS')

###########################################################
'''
Property Methods
'''


def driver_minmax(driver_fcurve):
    scene = bpy.context.scene
    # get the minmax of the driver over playback range.
    '''
    THIS IS FAR TOO HEAVY TO RUN AS A PROPERTY
    o = driver.id_data
    i = driver.array_index
    dp =driver.data_path
    o.path_resolve(dp)
    '''
    v = []
    for f in range(scene.frame_start, scene.frame_end):
        scene.frame_set(f)
        v.append(driver_fcurve.evaluate(f))
    '''
    #v = [driver_fcurve.evaluate(f)
    for f in range(scene.frame_start, scene.frame_end)]
    '''
    _min = min(v)
    _max = max(v)
    return ((_min, _max), (v.index(_min), v.index(_max)))


def fcurve_minmax(self):
    # return ((min, max), (min_index, max_index))
    # it thru keyframe_points
    if len(self.keyframe_points):
        col = self.keyframe_points
    elif len(self.sampled_points):
        col = self.sampled_points
    else:
        return ((0, 0), (0, 0))
        return(driver_minmax(self))
    # check for modifiers
    mods = [mod for mod in self.modifiers if not mod.mute and mod.is_valid]
    if len(mods):
        v = [self.evaluate(p.co[0]) for p in col]
    else:
        v = [p.co[1] for p in col]
    _min = min(v)
    _max = max(v)
    return ((_min, _max), (v.index(_min), v.index(_max)))

'''
Property Groups
'''


def register():
    bpy.types.FCurve.minmax = property(fcurve_minmax)
    register_class(DriverSelectorOperator)
    register_class(Bake2FCurveOperator)
    register_class(EditTextFieldOperator)
    register_class(UpdateDriverlistOperator)
    register_class(RemoveDriverVarOperator)
    register_class(EditDriverVarOperator)
    register_class(DriverManagerDemonkify)
    register_class(DriverManagerSettings)
    register_class(SimpleCustomMenu)
    register_class(DriverMangagerToolMenu)
    register_class(AddDriverVar)
    register_class(DriverAddModifier)
    register_class(DriverRemoveModifier)
    register_class(SoundDriverAction)
    register_class(SoundDriverActivateChannel)
    register_class(CopyDriverToSelectedObjects)
    register_class(RGBColorFCurves)

    # get rid of any handlers floating around.
    remove_handlers_by_prefix('SOUND_DRIVERS_')
    bpy.app.handlers.load_post.append(SOUND_DRIVERS_load)
    bpy.app.handlers.load_pre.append(SOUND_DRIVERS_unload)

    # set up the driver manager
    def dm_start_button(self, context):
        if getattr(context, "driver_manager", None) is None:
            self.layout.operator("drivermanager.update", text="", icon='DRIVER')

    bpy.types.PROPERTIES_HT_header.prepend(dm_start_button)

def unregister():
    unregister_class(DriverSelectorOperator)
    unregister_class(Bake2FCurveOperator)
    unregister_class(EditTextFieldOperator)
    unregister_class(UpdateDriverlistOperator)
    unregister_class(RemoveDriverVarOperator)
    unregister_class(EditDriverVarOperator)
    unregister_class(RGBColorFCurves)
    unregister_class(DriverManagerDemonkify)
    unregister_class(DriverManagerSettings)
    unregister_class(DriverMangagerToolMenu)
    unregister_class(SimpleCustomMenu)
    unregister_class(AddDriverVar)
    unregister_class(SoundDriverAction)
    unregister_class(SoundDriverActivateChannel)
    unregister_class(CopyDriverToSelectedObjects)
    unregister_class(DriverAddModifier)
    unregister_class(DriverRemoveModifier)
    # We don't want these hanging around.
    remove_handlers_by_prefix('SOUND_DRIVERS_')
    remove_draw_pend(bpy.types.PROPERTIES_HT_header, "dm_")

    dm = bpy.app.driver_namespace.get("DriverManager")
    if dm is not None:
        dm.clear()
        print("Driver Manager Cleared")
        # del(dm)
