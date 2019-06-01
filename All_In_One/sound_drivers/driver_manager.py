bl_info = {
    "name": "Driver Manager",
    "author": "batFINGER",
    #"location": "",
    "description": "Manage Drivers across blend.",
    "warning": "Still in Testing",
    "wiki_url": "http://wiki.blender.org/index.php/\
                User:BatFINGER/Addons/Sound_Drivers",
    "version": (1, 1),
    "blender": (2, 7, 6),
    "tracker_url": "",
    "icon": 'DRIVER',
    "support": 'TESTING',
    "category": "Learnbgame",
}
import bpy
from bpy.types import AddonPreferences
from bpy.props import IntProperty, BoolProperty
from sound_drivers.utils import (bpy_collections,
                                 get_icon,
                                 format_data_path,
                                 get_driver_settings,
                                 copy_driver,
                                 getAction,
                                 getSpeaker,
                                 remove_draw_pend,
                                 split_path
                                )
from sound_drivers import debug
from sound_drivers.icons import icon_value
from mathutils import Vector, Color, Euler, Quaternion
from math import sqrt, degrees

class DriverManagerAddonPreferences(AddonPreferences):
    ''' Driver Manager Prefs '''
    bl_idname = __name__

    # toggle to view drivers
    view_drivers = BoolProperty(default=False)
    driver_manager_update_speed = IntProperty(
                                  name="Driver Manager Update Speed",
                                  min=1,
                                  max=100,
                                  description="Update timer, lower value = faster updates, higher value slow self update use refresh",
                                  default=10)

    def draw_all_drivers(self, context):
        if not self.view_drivers:
            return
        layout = self.layout
        dm = context.driver_manager
        dic = dm.get_filter_dic()
        for collection in dic:
            layout.label(collection)
            collectionbox = layout.box()
            for object in dic[collection]:
                objectrow = collectionbox.row()
                objectrow.label(object)
                
                #objectrow.label(strdic[collection][object])
                driverscol = collectionbox.column()
                #for dp in dic[collection][object]:
                    #driverscol.label(dp)
                dm.draw_layout(collectionbox.column(), context, dic[collection][object])
    def draw(self, context):
        def icon(test):
            if test:
                icon = 'FILE_TICK'
            else:
                icon = 'ERROR'
            return icon

        layout = self.layout
        test = getattr(context, "driver_manager", None)
        row = layout.row()
        row.label("DriverManager Started", icon=icon(test))
        row = layout.row()
        if not test:
            row.operator("drivermanager.update")
        else:
            row.prop(self, "driver_manager_update_speed", slider=True)
            row = layout.row()
            dm = context.driver_manager
            row.label("There are %d drivers in blend" % len(dm.all_drivers_list))
            row.prop(self, "view_drivers", toggle=True, text="View", emboss=False)
            self.draw_all_drivers(context)

#icon_value = bpy.types.UILayout.icon 

# need to seperate driver from sounddriver.
class Driver:
    pass

class SoundDriver():
    _index = 0
    _min = 0
    _edit_driver_gui = None


    def get_is_baked(self):
        if self.fcurve is None:
            return False
        ob = self.fcurve.id_data
        if ob is None:
            return False
        action = ob.animation_data.action
        if action is None:
            return False

        return action.fcurves.find(self.data_path, self.array_index) is not None

    is_baked = property(get_is_baked)

    is_color = False
    # REFACTO NEW
    def get_value(self):
        prop = getattr(self.driven_object, self.prop, None)
        if self.is_vector:
            return  prop[self.array_index]

        return prop

    value = property(get_value)

    def edit_draw(self, layout, context):
        ''' DRAWS THE SPEAKER TOOLS GUI'''
        scene = context.scene
        sp = scene.speaker
        action = getAction(sp)

        # REFACTO FIX THIS 
        if not len(context.scene.soundspeakers):
            box = layout.box()
            box.label("NO DRIVER SPEAKERS")
            speakers = [s for s in context.scene.objects
                        if s.type == 'SPEAKER']
            if len(speakers):
                row = box.row()
                row.label("Please set up the speaker")
            else:
                box.operator("object.speaker_add")
            return None
        elif sp is None:
            box = layout.box()
            box.label("NO CONTEXT SPEAKER")
            box.menu("speaker.select_contextspeaker")
            return None


        if sp is None or action is None:
            return None

        edr = self
        if edr is None:
            row = layout.row()
            row.label("NO EDIT DRIVER")

        area = context.area
        space = context.space_data

        # make a new gui for edit driver
        eds = [edr.driver_gui(scene)]
        for ed in eds:
            action = bpy.data.actions.get(ed.action)
            if ed is None:
                layout.label("NO GUI")
                return
            #if True:

            speaker_box = layout.box()
            speaker_box.label("Context Speaker")
            if sp:
                text = "%s (%s)" % (sp.name, sp.sound.name)
                speaker_box.menu("speaker.select_contextspeaker", text=text)
            else:
                speaker_box.menu("speaker.select_contextspeaker")
            if 'ACTION' in ed.gui_types:
                action_box = layout.box()
                sa = getAction(sp)
                # TODO get the draw method from SoundActionPanel
                row = action_box.row()
                row.label("Sound Action", icon='ACTION')
                row = action_box.row()
                sub = row.row()
                sub.alignment = 'LEFT'
                #col.alignment = 'LEFT'
                channel_name = sa["channel_name"]
                sub.menu("soundtest.menu", text=channel_name)
                #sub = row.row()
                row.prop(sa, "name", text="")

                row = action_box.row()
                row.enabled = action.normalise != 'NONE'
                row.prop(sa, "normalise_range", text="", expand=True)

                row = action_box.row(align=True)
                row.prop(sa, "normalise", expand=True)

            box = layout.box()

            
            row = box.row()
            row.label("SoundDriver", icon='SOUND')
            #REFACTO CORRECTO

            row = box.row()
            a = bpy.data.actions.get(ed.action)
            #row.label(a.get("channel_name","AA"))
            row.prop(ed, "channel")
            '''
            op = row.operator("driver.sound_action")
            op.dindex = self.index 
            op.channel = "AA"
            '''
            if a is None or "channel_name" not in a.keys():
                row = box.row()
                row.label("ERROR WITH ACTION", icon='ERROR')
                return None
            # REFACTO
            #cn = a['channel_name']
            cn = ed.channel
            channels = a['Channels']
            channels = len(a.fcurves)
            cols = min(int(sqrt(channels)), 16)
            #cf = row.column_flow(columns=cols, align=True)

            chs = [(i, "%s%d" % (cn, i)) for i in range(channels)]
            chs = [(i, fc.data_path.strip('["]')) for i, fc in enumerate(a.fcurves)]
            for i, ch in chs:

                channel = ed.channels.get(ch)
                #print("\nchannel", channel, "\nch", ch, "\ncn", cn, "\nchannels", channels, "\ned.channels", ed.channels)
                if ch.startswith(cn):
                    channel_number = int(ch.strip(cn))
                else:
                    continue # TODO fix
                    channel_number = int(ch[2:])
                if not i % cols:
                    row = box.row()
                #col = cf.row()
                col = row.column()
                #col.scale_y = 0.5
                # col.label(ch.name)
                if channel is not None:
                    col.prop(channel, 'value', text=str(channel_number), toggle=True)
                else:
                    op = col.operator("driver.sound_channel_activate", text="%d" % channel_number)
                    op.channel = ch
                    op.dindex = self.index

                if False: # FIXME add flag to show props here
                    r = col.row()
                    r.scale_y = 0.4

                    r.prop(sp, '["%s"]' % channel.name, slider=True, text="")
            row = box.row()
            row.label("Extra Settings")
            row = box.row()
            row.prop(ed, "op", text="")
            row.prop(ed, "amplify")
            row.prop(ed, "threshold")
        row = layout.row()
        row.scale_y = 0.5

    def driver_edit_draw(self, layout, context):
        scene = context.scene
        ''' Draws the edit driver '''
        box = layout
        d = self
        if getattr(d, "is_open", False):
            #return None
            ed = True
            row = box.row(align=True)
            leftcol = row.column()
            leftcol.alignment = 'LEFT'

            gui = d.driver_gui(scene)
            if gui is not None:
                leftcol.prop(gui, "gui_types",
                             text="",
                             expand=True,
                             icon_only=True)

            if d.is_monkey:
                op = leftcol.operator("drivermanager.demonkify", text="",
                                      icon='MONKEY')
                op.driver_index = d.index

            if d.is_baked:
                option = 'UNBAKE'
                icon = 'FCURVE'
            else:
                option = 'BAKE'
                icon = 'ACTION'

            op = leftcol.operator("editdriver.bake2fcurves",
                                  text="", icon=icon)
            op.dindex = d.index
            
            if len(context.selected_objects) > 1:
                op = leftcol.operator("driver.copy_to_selected_objects",
                             text="", icon='PASTEDOWN')
                op.dindex = d.index

            rightcol = row.column()

            ebox = rightcol.column()
            '''
            if getattr(d, "edit_driver_baking", False):
                d.baking_draw(ebox)

            '''
            ebox.enabled = not getattr(d, "edit_driver_baking", False)

            if True: # TODO fix this no longer gui_type
                UserPrefs = context.user_preferences
                if not UserPrefs.system.use_scripts_auto_execute:
                    ebox.label("AUTO SCRIPTS NOT ENABLED", icon='ERROR')
                    row = ebox.row()
                    row.prop(UserPrefs.system, "use_scripts_auto_execute")

                else:
                    gui = self.driver_gui(context.scene)
                    if gui is None:
                        return None
                    if True : #  if 'DRIVER' in gui.gui_types: REFACTO
                        driver_box = ebox.column()
                        d.edit(driver_box, context)


    def driver_gui(self, scene):
        col = getattr(scene.driver_objects, self.collection_name)
        if col is None:
            return None
        obj = col.get(self.object_name, None)
        if obj is None:
            return None
        return obj.drivers.get("DM_%d" % self.index)

    def set_edit_driver_gui(self, scene, create=False):
        #create = False
        self._setting_channels = True
        col = getattr(scene.driver_objects, self.collection_name, None)
        ed = col.get(self.object_name, None)
        if ed is None:
            create=True
            ed = col.add()
            ed.name = self.object_name

        driver_gui = ed.drivers.get("DM_%d" % (self.index), None)

        if driver_gui is None:
            driver_gui = ed.drivers.add()
            driver_gui.name = "DM_%d" % (self.index)

        dummy, args = get_driver_settings(self.fcurve)

        if create:
            # add a driver to the value
            driver_gui.driver_remove('value')
            test_driver = driver_gui.driver_add('value')
            copy_driver(self, test_driver) # REFACTO
            test_driver.driver.type = 'SCRIPTED'
            test_driver.driver.expression = 'GetLocals(%d, locals(), DriverManager)' % self.index
            setattr(self, "gui_driver", test_driver) # REFACTO
            #setattr(self, "gui", driver_gui)
            cs = scene.speaker
            #a = getAction(cs) # REFACTO
            a = bpy.data.actions.get(driver_gui.action)

            for arg in args:
                k, v = arg.split("=")
                if k in ed.bl_rna.properties.keys():
                    # get the prop type
                    p = ed.bl_rna.properties.get(k)
                    if p.rna_type.identifier.startswith("FloatP"):
                        setattr(driver_gui, k, float(v))
                    elif p.rna_type.identifier.startswith("IntP"):
                        setattr(driver_gui, k, int(v))
                    elif p.rna_type.identifier.startswith("Enum"):
                        setattr(driver_gui, k, v.strip("'"))
                    else:
                        setattr(driver_gui, k, v)

            # set up channels
            # REFACTO ___OUT 
            dummy, args = get_driver_settings(self.fcurve)

            if a is not None and cs is not None:
                cn = a["channel_name"]
                channels = a["Channels"]
                chs = [ch for ch in driver_gui.channels if ch.name.startswith(cn)]
                '''
                exist = len(chs) == channels
                if not exist:
                    for ch in chs:
                        driver_gui.channels.remove(ed.channels.find(ch.name))
                '''
                driver = self.fcurve.driver
                for i in range(0, channels):
                    channel_name = "%s%d" % (cn, i)
                    channel = driver_gui.channels.get(channel_name)
                    if channel is None and channel_name in driver.variables.keys():
                        channel = driver_gui.channels.add()
                        channel.name = channel_name
                        dvar = driver.variables[channel.name]
                        if dvar.targets[0].id == cs:
                            channel.value = True
                        else:
                            # variable there but with other speaker alert
                            pass
                    '''
                    else:
                        channel.value = False
                    '''

        
        self._setting_channels = False
        return None


    #REFACTO OUT
    #edit_driver = property(get_edit_driver_gui)

    def check_driver(self, scene):
        ''' check driver against gui driver '''
        # could flag the bad var here.
        dic = {}
        from_driver = self
        td = self.fcurve.driver
        #gui_driver = self.driver_gui(scene)
        gui_driver = getattr(self, "gui_driver", None)
        if gui_driver is None:
            return False

        fd = gui_driver.driver

        if fd is None:
            return False

        if td.type != fd.type:
            return False
        #td.expression = fd.expression
        for var in fd.variables:
            v = td.variables.get(var.name)
            if v is None:
                dic[var.name] = False
                return False
            if v.name != var.name:
                return False
            if v.type != var.type:
                return False
            for i, target in var.targets.items():
                if var.type == 'SINGLE_PROP':
                    if v.targets[i].data_path != target.data_path:
                        return False
                if v.targets[i].id != target.id:
                    return False
                if v.targets[i].transform_type != target.transform_type:
                    return False
                if v.targets[i].transform_space != target.transform_space:
                    return False
                if v.targets[i].bone_target != target.bone_target:
                    return False
        return True

    def _get_is_monkey(self):
        if self.fcurve is None:
            return False
        driver = self.fcurve.driver
        if len(driver.variables) == 1 \
                and driver.variables[0].name == "var" \
                and driver.variables[0].targets[0].id is None:
            return True
        return False
    is_monkey = property(_get_is_monkey)

    def demonkify(self):
        var = self.fcurve.driver.variables.get("var")
        if var:
            self.fcurve.driver.variables.remove(var)

    is_rgba_color = False
    _driven_object = "None"

    def _set_driven_object(self, obj):
        ''' set the driven object of driver '''
        if (self.is_node
                and (self.collection_name == "scenes"
                     or self.collection_name == "lamps"
                     or self.collection_name == "materials"
                     or self.collection_name == "textures")
                and obj is not None):
            self._driven_object = "%s.node_tree" % repr(obj)
            return

        if obj is not None:
            txt = repr(obj)
            if txt.find("...") > 0:
                if self.fcurve is not None:
                    txt = "%s.%s" % (self.fcurve.id_data, self.data_path)
                elif self.is_node:
                    txt = 'bpy.data.node_groups["%s"]' %\
                        (self.object_name)
                    self.text = "NODEEEE"

            self._driven_object = txt

    def _get_driven_object(self):
        try:
            return(eval(self._driven_object))
        except:
            return None

    driven_object = property(_get_driven_object, _set_driven_object)

    def validate(self):
        '''
        Check if the Driver is Valid
        '''
        try:
            if self.is_node:
                if self.collection_name == "scenes":
                    self.driven_object.path_resolve(self.data_path)
                else:
                    self.driven_object.path_resolve(self.data_path)
            else:
                self.fcurve.id_data.path_resolve(self.fcurve.data_path)
        except:
            return False
        return True

    _vd = {}

    def get_driver_fcurve(self):
        # fix for nodes
        if self.is_node:
            if self.collection_name == "scenes":
                obj = self.driven_object
            else:
                obj = self.driven_object
        else:
            obj = getattr(bpy.data, self.collection_name).get(self.object_name)
        if obj is None:
            return None
        ad = getattr(obj, "animation_data")
        if ad is None:
            return None
        drivers = [d for d in ad.drivers
                   if d.data_path == self.data_path and
                   d.array_index == self.array_index]
        if not len(drivers):
            return None

        if self.is_node:
            pass

        return drivers[0]

    fcurve = property(get_driver_fcurve)

    def _get_is_modifier(self):
        return self.data_path.startswith("modifiers")

    is_modifier = property(_get_is_modifier)

    def _get_is_constraint(self):
        return self.data_path.startswith("constraints")

    is_constraint = property(_get_is_constraint)

    def _getvariabledict(self):
        vars = self.fcurve.driver.variables
        vd = self._vd = {}
        for v in vars:
            t = v.targets[0].id
            if t:
                tn = vd.get(t.name)
                if not tn:
                    tn = vd[t.name] = []
                tn.append(v)
            else:
                nn = vd.get("None")
                if not nn:
                    nn = vd["None"] = []
                nn.append(v)

        return vd

    vd = property(_getvariabledict)

    def _getmin(self):
        do = self.driven_object
        mo = eval(self.default_value)
        x = self.fcurve.evaluate(0)
        if x < self._min:
            self._min = x
        return self._min

    def _getmax(self):
        x = self.fcurve.evaluate(0)
        if x >= self._max:
            self._max = x
        return self._max

    max = property(_getmax)
    min = property(_getmin)

    prop = ""
    is_vector = False
    text = ""

    def draw_error(self, layout):
        row = layout.row()
        row.label(text="", icon="ERROR")
        row.label(text="BAD PATH")

    def draw_default(self, layout):
        fcurve = self.fcurve
        do = self.driven_object
        if not do:
            return(self.draw_error(layout))
        layout.prop(do, self.prop, index=fcurve.array_index, slider=True)

    def draw_node_slider(self, layout, context):
        l = self.data_path.split(".")
        length = len(l)
        if length > 2:
            value = l[-1]
            input_ = l[-2]
            x = ""
            for s in l[:length - 2]:
                x = "%s.%s" % (x, s)
            node = x.strip(".")

        elif length == 2:
            value = ""
            input_ = l[1]
            node = l[0]

        node = self.driven_object.path_resolve(node) # REFACTO
        row = layout.row() # REFACTO
        row.label(node.rna_type.identifier + str(l)) # REFACTO
        if length == 2:
            layout.prop(node, l[1])
            return None
        # check for connector

        node_input = node.path_resolve(input_)
        layout.enabled = not getattr(node_input, "is_linked", False)
        # row.label(str(node_input.is_linked))
        val = node_input.path_resolve(value)
        #node_input.draw(context, layout, node, node_input.name)
        fmt_str = "%s:%s"

        ni_name = getattr(node_input, "name", "NO_name")
        if ni_name.lower().startswith("color"):
            fmt_str = "%%s: %c %%s" % "RGBA"[self.array_index]
        name = fmt_str % (getattr(node, "name", "No Node Name"), ni_name)
        layout.prop(node_input, "default_value", index=self.array_index,
                    text=name)
        #node_input.draw(context, row, node, "")
        #node_input.draw(context, layout, node, self.text)
        #layout.template_node_socket(color=(0.0, 0.0, 1.0, 1.0))

    def draw_slider(self, layout):
        fcurve = self.fcurve
        do = self.driven_object

        if getattr(self, "edit_driver_baking", False):
            self.baking_draw(layout)
            return None

        if not do:
            return(self.draw_error(layout))

        if self.is_idprop and self.prop.strip('["]') not in do.keys():
            return(self.draw_error(layout))

        layout.prop(do, self.prop,
                    text=self.text,
                    index=self.fcurve.array_index,
                    slider=True)

    def draw_outputs(self, layout):
        edr = self
        row = layout.row()
        row.label("FCurve Modifiers")
        row = layout.row(align=True)
        # NEEDS REFACTOR
        d = edr.fcurve
        mods = getattr(d, "modifiers", None)
        gm = None
        if mods is not None:
            for mi, m in enumerate(mods):
                if m.type == 'GENERATOR':
                    gm = m
                    break
        if gm is not None:
            row.prop(gm, "coefficients", text="offset", index=0)
            row.prop(gm, "coefficients", text="amplify", index=1)
            sub = row.row()
            sub.alignment = 'RIGHT'
            op = sub.operator("editdriver.remove_modifier", icon='X', text="")
            op.idx = mi
        else:
            op = row.operator("editdriver.add_modifier")

        op.dindex = self.index
            # op.type = 'GENERATOR' #  it's the default

    def baking_draw(self, layout, scale_y=0.5):
        d = self
        # BAKE DRIVE DRAW METHOD NEEDED FOR DRIVER CLASS
        #row = layout.row(align=True)
        row = layout
        pc = getattr(d, "bake_pc", 0.0)
        split = row.split(pc, align=True)
        split.scale_y = layout.scale_y
        #split.prop(d.fcurve, "color", text="")
        if d.is_vector:
            split.prop(d.fcurve.id_data,
                       d.data_path,
                       index=d.array_index,
                       slider=True,
                       text="")
        else:
            if d.is_modifier:
                split.prop(d.driven_object, d.prop, slider=True, text="")
            else:
                split.prop(d.fcurve.id_data, d.data_path, slider=True, text="")

        split.label(text="")
        #split.prop(bpy.context.scene.driver_gui.edit_drivers[0], 'value', slider=True, text="")


    def __init__(self, driver, collection_name,
                 object_name, data_path, array_index):
        scene_name = None
        self.collection_name = collection_name
        sp = object_name.split("__#__")
        if len(sp) == 2:
            scene_name = sp[0]
            object_name = sp[0]

        self.object_name = object_name
        self.data_path = data_path
        self.array_index = array_index

        self.is_seq = data_path.startswith("sequence_editor.sequences_all")

        self.is_node = (data_path.startswith("node")
                        or self.collection_name == "node_groups")

        rna_type = driver.id_data.rna_type
        self.is_material = data_path.startswith("materials")\
            or rna_type.identifier.startswith("Material")
        self.is_texture = data_path.startswith("textures")
        #driver_fcurve = self.fcurve
        driver_fcurve = driver
        # todo make axis "RGB" and use d.array_index
        is_vector = False
        axis = ""
        text = ""
        if scene_name is not None:
            #do = eval(scene_name)
            do = getattr(bpy.data, collection_name).get(scene_name)
            #do = bpy.data.scenes.get(scene_name)
        else:
            do = driver_fcurve.id_data
        mo = None
        sp = driver_fcurve.data_path.split("][")

        if len(sp) == 2:
            prop = "[%s" % sp[1]

        else:
            sp = driver_fcurve.data_path.split(".")
            prop = sp[-1]

        path = driver_fcurve.data_path.replace("%s" % prop, "")
        array_index = driver_fcurve.array_index
        xx = repr(do)
        if scene_name is not None:
            # quick node fix hack
            bpy_data_path = "bpy.data.%s['%s']" % (collection_name, scene_name)
        else:
            bpy_data_path = "%s.%s" % (xx, path)
        # quick fix for nodes
        # check for custom properties hack
        is_idprop = False
        if bpy_data_path[-1] == '.':
            bpy_data_path = bpy_data_path[:-1]

        try:
            do = eval(bpy_data_path)
        except:
            pass
            # check for nodes
        finally:
            do = None
        # bone custom props of form bone["xx"]["prop"]

        # find the "]["

        if prop.startswith("["):
            do = driver.id_data
            is_idprop = True
        else:
            try:
                do = eval(bpy_data_path)
            except:
                do = None
            try:
                mo = do.path_resolve(prop)
            except:
                mo = None

        if do is None:
            is_vector = False
            text = "BAD_PATH"
            can_edit = False

        elif is_idprop:
            text = prop.strip('["]')

        elif isinstance(mo, Vector):
            is_vector = True
            axis = "XYZ"[array_index]
            text = "%s %s" % (axis, do.bl_rna.properties[prop].name)
            mo = mo[array_index]

        elif isinstance(mo, Euler):
            is_vector = True
            axis = mo.order[array_index]
            text = "%s %s" % (axis, do.bl_rna.properties[prop].name)
            mo = mo[array_index]

        elif isinstance(mo, Quaternion):
            is_vector = True
            axis = "WXYZ"[array_index]
            text = "%s %s" % (axis, do.bl_rna.properties[prop].name)
            mo = mo[array_index]

        elif isinstance(mo, Color):
            is_vector = True
            '''
            driver.color = (0,0,0)
            driver.color[array_index] = 1
            '''
            self.is_color = True
            axis = "RGB"[array_index]
            text = "%s %s" % (axis, do.bl_rna.properties[prop].name)
            mo = mo[array_index]

        elif type(mo).__name__ == "bpy_prop_array":
            is_vector = True
            if prop == "color":
                self.is_rgba_color = True
                axis = "RGBA"[array_index]
                text = "%s %s" % (axis, do.bl_rna.properties[prop].name)
            else:
                text = "%s[%d]" % (do.bl_rna.properties[prop].name,
                                   array_index)
            mo = mo[array_index]

        elif not self.is_node:
            is_vector = False
            if prop in do.bl_rna.properties.keys():
                text = do.bl_rna.properties[prop].name
            else:
                text = "PROBLEM"

        self.driven_object = do
        self.icon_value = icon_value(do) if do else 0
        self.default_value = repr(mo)
        self.is_vector = is_vector
        self.is_idprop = is_idprop
        self.prop = prop
        self.text = text
        self.axis = axis

    @property
    def propname(self):
        return self.driven_object.bl_rna.properties[self.prop].name

    def edit(self, layout, context):

        scene = context.scene
        gui = self.driver_gui(scene)

        if gui is None:
            return None
        if self.fcurve is None:
            layout.label(text="Driver Problems")
            return None
        if self.is_baked:
            row = layout.row()
            row.label("BAKED")
            row.label(self.fcurve.id_data.animation_data.action.name, icon='ACTION')
            #return None
        driver = self.fcurve.driver
        row = layout.row(align=True)
        if self.is_baked:
            row.label("Keyframe", icon='ACTION')
        else:
            row.label("Driver Path", icon='DRIVER')
        sub = row.row()
        sub.enabled = False
        sub.prop(self.fcurve, "data_path", text="", icon="RNA")

        if self.is_vector:
            sub.alignment = 'RIGHT'
            sub.prop(self.fcurve, "array_index", text="")

        box = layout.box()
        box.enabled = not self.is_baked
        row = box.row(align=True)
        row.prop(driver, "type", text="")
        #row = box.row()
        if driver.type == 'SCRIPTED':
            #row.prop(driver, "expression", text="")
            row = box.column(align=True)
            #row.operator("drivermanager.input_text", text=driver.expression, icon="SCRIPT")
            box.alignment  = 'LEFT'
            #row.label(driver.expression)
            op = row.operator("drivermanager.input_text", text=driver.expression, icon="SCRIPT", emboss=False)
            op.dindex = self.index
            row.scale_x = row.scale_y = 0.5
        else:
            row.label(" ")
        '''
        row = box.row()
        row.label("min:%.2f max:%.2f" % (self.min,self.max))
        '''

        if 'SOUNDDRIVER' in gui.gui_types:
            self.edit_draw(box, context)

        varbox = box.column()


        row = varbox.row()
        row.label("Driver Variables")
        op = row.operator("driver.new_var", icon="ZOOMIN", text="")
        op.dindex = self.index
        edit_box = varbox.column()

        for tn, varlist in self.vd.items():
            if tn == "None":
                continue

            target = varlist[0].targets[0]
            row = varbox.row()
            row.alignment = 'LEFT'
            row.label("", icon='BLANK1')
            row.label(target.id.name, icon_value=row.icon(target.id))
            #row.prop(target.id, "name", text="")
            #row.label(target.id.name)
            if target.data_path.startswith("node_tree"):
                row.label("(node_tree)", icon='NODETREE')

            for var in varlist:
                target = var.targets[0]
                row = varbox.row(align=True)
                row.scale_y = 0.5
                col2 = row
                # FIX THIS
                #sub = row.split(percentage=0, align=True)
                sub = row.row()
                sub.alignment = 'LEFT'
                sub.label("", icon='BLANK1')
                sub.scale_y = 0.5
                op = sub.operator("dm.edit_driver_var", text="%s" % var.name.ljust(6), emboss=True)
                op.varname = var.name
                op.dindex = self.index


                if var.type == 'SINGLE_PROP':
                    dp = target.data_path
                    if len(dp) == 0:
                        col2.label("No data_path")
                        continue

                    p = dp
                    suffixes = ["rgba", "xyz", "wxyz"]
                    found = False
                    for suffix in suffixes:
                        if found:
                            break
                        for i, ch in enumerate(suffix):
                            if p.endswith(".%c" % ch):
                                dp = "%s[%d]" % (p[:-2], i)
                                found = True
                                break

                    p = dp.strip(']')
                    i = -1

                    idx = -1
                    while p[-1].isnumeric():
                        i += 1
                        idx += 10 ** i + int(p[-1])
                        p = p[:-1]
                        p = p.strip('[')

                    try:
                        if i > -1:
                            path = p
                            col2.prop(target.id, path, index=idx, slider=True)
                        elif target.data_path.startswith("node_tree"):
                            ntree = target.id.node_tree
                            p = target.data_path.replace("node_tree.", "")
                            p = p.replace(".default_value", "")
                            i = p.find(".inputs")
                            sp = p[:i]
                            i = i + 1
                            ps = p[i:]

                            node = ntree.path_resolve(sp)
                            input = node.path_resolve(ps)
                            name = "%s:%s" % (node.name, input.name)
                            col2.prop(input, "default_value", text=name,
                                      icon='NODE')

                            #col2.template_node_view(ntree, node, input)
                        else:
                            try:
                                # need a nicer path splitting routine
                                path =  split_path(target.data_path)
                                mo = target.id.path_resolve(target.data_path)
                                if len(path) > 1:
                                    mo = target.id.path_resolve(".".join(path[:-1]))

                                    col2.prop(mo,
                                          path[-1],
                                          slider=True)
                                else:
                                    col2.prop(target.id, target.data_path)
                            except:
                                col2.label("XX%s = %.2f" % (dp, mo))
                    except:
                        col2.label("ERROR")
                elif var.type == 'TRANSFORMS':
                    target = var.targets[0]
                    x = self.locs.get(var.name, None) if hasattr(self, "locs") else None
                    if target is None:
                        continue
                    tt = target.transform_type.replace("LOC_",
                                                       "Location ")
                    tt = tt.replace("ROT_", "Rotation ")
                    tt = tt.replace("SCALE_", "Scale ")
                    ts = target.transform_space.replace("_SPACE", "")
                    if x is not None:
                        desc = "%s (%s) %f" % (tt, ts, x)
                        col2.label(desc)
                    else:
                        op = row.operator("driver.edit",
                                          text="Update Dependencies",
                                          icon='FILE_REFRESH')
                        op.dindex = self.index
                        op.update = True
                else:
                    x = self.locs.get(var.name, None) if hasattr(self, "locs") else None
                    if x is not None:
                        a_code = ""
                        if var.type.startswith("ROT"):
                            x = degrees(x)
                            a_code = "\u00b0"
                        col2.label("%.2f%s from %s" % (x, a_code, var.targets[1].id.name))
                    else:
                        col2.label("%s TYPE.." % var.type)
                op = row.operator("dm.remove_driver_var", text="", icon="X")
                op.varname = var.name
                op.dindex = self.index

        invalid_targets = self.vd.get("None")
        if invalid_targets:
            row = box.row()
            row.label("Rubbish Variables")
            ivarbox = box.column()
            for v in invalid_targets:
                row = ivarbox.row()
                row.scale_y = 0.5
                row.label("", icon='BLANK1')
                row.alert = True
                op = row.operator("dm.edit_driver_var", text=v.name, icon='ERROR')
                op.varname = v.name
                op.dindex = self.index
                #row.label("%s has no valid target" % v.name, icon='ERROR')
                op = row.operator("dm.remove_driver_var", text="", icon="X")
                op.varname = v.name
                op.dindex = self.index

        row = layout.row()
        if not self.check_driver(scene):
            row.scale_y = 0.5
            op = row.operator("driver.edit",
                              text="Update Dependencies",
                              icon='FILE_REFRESH')
            op.update = True
            op.dindex = self.index
            row = layout.row()

        d = self.fcurve
        self.draw_outputs(box)
        layout = layout.box()
        if gui.var_index < 0 or gui.var_index >= len(d.driver.variables):
            return
        var_edit_box = edit_box.box()
        row = var_edit_box.row(align=True)
        '''
        row.prop_search(gui,
                        "varname",
                        d.driver,
                        "variables",
                        icon='VIEWZOOM',
                        text="EDIT")
        '''
        if gui.var_index < 0 or gui.var_index >= len(d.driver.variables):
            return

        var = d.driver.variables[gui.var_index]
        self.draw_edit_driver_var(var_edit_box, var)

    def draw_edit_driver_var(self, layout, var):
        #layout.label("%3f" % d.evaluate(0))
        row = layout.row(align=True)
        row.prop(var, "name", text="")
        op = row.operator("dm.edit_driver_var", text="Cancel")
        op.varname = ""
        op.dindex = self.index
        op = row.operator("dm.remove_driver_var", text="", icon='X')
        op.dindex = self.index
        op.varname = var.name
        row = layout.row()
        row.prop(var, 'type', text="")

        for i, target in enumerate(var.targets):
            row = layout.row(align=True)
            row.label("Target %d" % i)
            #row.template_ID(target, "id_type")
            row.prop(target, "id_type", text="")
            row.prop(target, "id", text="")
            if var.type in ['TRANSFORMS', 'LOC_DIFF', 'ROTATION_DIFF']:
                if target.id and getattr(target.id, "type", None) == 'ARMATURE':
                    layout.prop_search(target,
                                       "bone_target",
                                       target.id.data,
                                       "bones",
                                       text="Bone")

            if var.type in ['TRANSFORMS']:
                layout.prop(target, "transform_type")
                layout.prop(target, "transform_space")
            if var.type in ['LOC_DIFF']:
                layout.prop(target, "transform_space")
            if var.type == 'SINGLE_PROP':
                layout.prop(var.targets[0], "data_path", icon='RNA')

    def inputs(self, layout):
        box = layout.box()
        # inputs
        for var in self.fcurve.driver.variables:
            row = box.row()
            # row.label(var.name)
            target = var.targets[0]
            if target.id:
                row.label(var.name)
                row.prop(target.id, target.data_path, slider=True)


class DriverManager():
    _edit_driver = None
    _filterdic = {}
    ticker = 10000
    _all_drivers_list = []

    def index(self, driver):
        try:
            index = self._all_drivers_list.index(driver)
        except:
            index = -1
        return index

    def find(self, index):
        ''' return a driver from the index '''
        if index not in range(len(self._all_drivers_list)):
            return None
        return self._all_drivers_list[index]

    def copy_driver(self, from_driver, target_fcurve):
        ''' copy driver '''
        copy_driver(from_driver, target_fcurve)

    def check_deleted_drivers(self):
        self.ticker += 1
        fcurves = [d.fcurve for d in self.all_drivers_list]
        if None in fcurves:
            self.get_all_drivers_list()

    def check_added_drivers(self, obj, context=bpy.context):
        prefs = context.user_preferences.addons[__package__].preferences
        dmprefs = prefs.addons["driver_manager"].preferences
        us = dmprefs.driver_manager_update_speed
        self.ticker += 1
        if self.ticker <= us: # REFACTO FOR UPDATE SPEED
            return False
        self.ticker = 0
        if obj is None:
            return False
        fcurves = [d.fcurve for d in self.all_drivers_list]
        obj_fcurves = []
        if hasattr(obj, "animation_data") and obj.animation_data is not None:
            obj_fcurves = [d for d in obj.animation_data.drivers]
            # check the object fcurves are in the fcurves coll
            for fc in obj_fcurves:
                if fc not in fcurves:
                    self.get_all_drivers_list()
                    return True
        return False

    def _get_adl(self):
        for i, d in enumerate(self._all_drivers_list):
            d.index = i
        return self._all_drivers_list

    all_drivers_list = property(_get_adl)
    _dels = []
    _dummies = []
    updates = 0

    def get_all_drivers_list(self):
        '''
        Searches for all drivers in a blend
        '''
        self._dummies.clear()
        for sd in self._all_drivers_list:
            if (not sd.validate()
                    or (sd.driven_object is None)
                    or sd.fcurve
                    is None):
                self.updates += 1
                self._all_drivers_list.remove(sd)

        self._dels = [n.fcurve for n in self._all_drivers_list]
        for collname in bpy_collections:
            # hack for nodes
            if collname in ["lamps", "materials", "textures"]:
                coll = getattr(bpy.data, collname)
                collection = [l for l in coll]
                collection.extend([(l, l.node_tree)
                                   for l in coll
                                   if l.use_nodes])
            elif collname == "scenes":
                collection = [s for s in bpy.data.scenes]
                collection.extend([(s, s.node_tree)
                                   for s in bpy.data.scenes
                                   if s.use_nodes])
                collection.extend([(s, s.sequence_editor.sequences_all)
                                   for s in bpy.data.scenes
                                   if s.sequence_editor is not None])
            else:
                collection = getattr(bpy.data, collname, None)
            if collection is None:
                continue

            # make a new entry for collection

            if not len(collection):
                continue

            scene = None
            for ob in collection:
                if isinstance(ob, tuple):
                    # it's a freaken node.. why not in bpy.data... grumble.
                    colln = "%s.%s" % (repr(ob[0]), repr(ob[1]))
                    scene = ob[0]
                    ob = ob[1]
                if (hasattr(ob, 'animation_data')
                        and ob.animation_data is not None):
                    drivers = [d for d in ob.animation_data.drivers]
                    if not len(drivers):
                        continue

                    for d in drivers:
                        if d not in self._dels:
                                
                            self.updates += 1
                            dp = d.data_path
                            ix = d.array_index
                            # quick hack try and enable dead drivers
                            #d.driver.is_valid = True
                            debug.print("Driver",
                                  collname,
                                  ob.name,
                                  dp, ix, "valid:%s" % str(d.driver.is_valid)
                                  )
                            if scene is not None:
                                obname = "%s__#__%s" % (scene.name, ob.name)
                            else:
                                obname = ob.name
                            if  d.data_path.startswith("driver_"): # REFACTO driver_gui to driver_objects:
                                self._dummies.append(SoundDriver(d, collname, obname, dp, ix))

                            else:
                                self._all_drivers_list.append(
                                    SoundDriver(d, collname, obname, dp, ix))

        # index them
        for i, d in enumerate(self._all_drivers_list):
            d.index = i


        return self._all_drivers_list
        '''
        return sorted(self._all_drivers_list,
                      key=attrgetter("collection_name",
                                     "object_name",
                                     "data_path",
                                     "array_index"))
        '''

    def get_context_object_dic(self, object):
        '''
        Get Dictionary for all drivers of object
        object: Blender Object
        return: dictionary of drivers
        '''
        return {}

    def get_object_drivers(self, obj):
        '''
        Get List of all drivers of object obj.
        '''
        return [d for d in self._all_drivers_list if d.fcurve.id_data == obj.id_data]

    def get_driven_object_driver_dic(self, drivers):
        '''
        returns a dictionary using rna_type.base.names
        '''

        #drivers = dm.get_object_drivers(obj)

        dic = {}
        icon_dic = {}
        for d in drivers:
            if d.driven_object.rna_type.base is None:
                base_name = d.driven_object.rna_type.name
            else:
                base_name = d.driven_object.rna_type.base.name
            '''
            if base_name == 'ID':
                # it's an ID object 
                base_name = obj.type
            '''
            base = dic.setdefault(base_name, {})
            objects = base.setdefault(d.driven_object.name, {})
            icon_dic[d.driven_object.name] = icon_value(d.driven_object)
            dp = objects.setdefault(d.propname, {})
            ai = dp.setdefault(str(d.array_index), d.index)
        print("ICON DIC", icon_dic)
        return dic, icon_dic

    def draw_pie_menu(self, obj, pie):
        drivers = self.get_object_drivers(obj)
        dic, icon_dic = self.get_driven_object_driver_dic(drivers)
        for type, driven_objects in dic.items():
            print(type, driven_objects)
            #box = pie.box()
            for name, datapaths in driven_objects.items():
                box = pie.box()
                box = box.row()
                print(name, datapaths)
                box.label(name, icon_value=icon_dic.get(name))
                col = box
                for dp, drivs in datapaths.items():

                    row = box.row(align=True)
                    col = row.column()
                    col.label(dp)
                    row = col.row(align=True)

                    #col.label(dp)
                    for axis, dindex in drivs.items():
                        print(axis, dindex)
                        #row = col.column(align=True)
                        #row.scale_y = 0.6
                        #row = col
                        d = self.find(dindex)
                        #d.draw_slider(row)
                        #op = row.operator("driver.popup_driver", text=d.text, emboss=False)
                        text = d.axis if d.axis else d.prop
                        op = row.operator("driver.popup_driver", text=text, emboss=True)
                        op.dindex = dindex

        return
        for dp, dr in dic.items():
            #p = pie.menu_pie()
            col = pie.column()
            box = col.box()
            box.label(dp, icon='DRIVER')
            for index, dindex in dr.items():
                driver = dm.find(dindex)
                if driver.driven_object != obj:
                    box.label(driver.driven_object.name)
                #driver.edit(box, context)
                row = box.row()
                row.scale_y = row.scale_x = 0.5
                driver.draw_slider(row)
                #driver.draw_default(box)
                #driver.driver_edit_draw(box, context)
                #dm.driver_draw(driver, box)
                op = row.operator("driver.popup_driver", text="EDIT")
                op.dindex = dindex
                # op.toggle = True

    def get_filter_dic(self):
        self._filterdic.clear()
        # for d in self._all_drivers_list:
        for d in self._all_drivers_list:
            coll = self._filterdic.setdefault(d.collection_name, {})
            obj = coll.setdefault(d.object_name, {})
            dp = obj.setdefault(d.data_path, {})
            #FIXME FIXME with a string index can pump into ID props
            ai = dp.setdefault(str(d.array_index), self._all_drivers_list.index(d))
            #ai = dp.setdefault(d.array_index, self._all_drivers_list.index(d))
        return self._filterdic

    filter_dic = property(get_filter_dic)

    def clear(self):
        self._PanelInvader(remove_only=True)
        # mute all drivers
        for d in self._all_drivers_list:
            if d is None:
                continue
            if (d.fcurve.driver.expression.startswith("SoundDrive")
                    or d.fcurve.driver.expression.startswith("GetLocals")):
                d.fcurve.driver.is_valid = False
        # clear the drivers list
        self._all_drivers_list.clear()
        for d in self._dummies:
            if d.fcurve:
                #XXXX
                #print(d.driven_object, d.prop)
                if not d.driven_object.driver_remove(d.prop):
                    #try  # possibly going to need try / catch here.
                    d.fcurve.driver_remove(d.data_path)
                # and the collection too

        return None

    def __init__(self):
        self.get_all_drivers_list()
        self.updates = 0
        self.updated = False
        self.updating = False
        self._PanelInvader()
        # quick fix
        for d in self._all_drivers_list:
            if d.fcurve is None:
                continue
            if (d.fcurve.driver.expression.startswith("SoundDrive")
                    or d.fcurve.driver.expression.startswith("GetLocals")):
                d.fcurve.driver.is_valid = True

    def is_sound_driver(self, driver):
        if driver.driver.expression.startswith("SoundDrive"):
            return True
        return False

    def query_driver_list(self, collection="*", object="*", data_path="*", array_index="*"):
        '''
        Returns a list of drivers matching a path *=all
        '''
        try:
            return(self.filter_dic[collection][object][data_path][array_index])
        except:
            return(None)

    # gui settings

    def draw_menus(self, layout, context):
        layout = layout.layout
        layout.alignment = 'LEFT'

        # layout.template_header(menus=True)
        layout.menu("drivermanager.tools_menu", text="", icon="MENU_PANEL")
        #layout.operator("driver_manager.settings", emboss=False)
        #row.menu("OBJECT_MT_custom_menu", text="Tools")


    def set_edit_driver_gui(self, context, create=False):
        '''Return the edit_driver_gui'''
        debug.print("WRONG SET EDIT DRIVER !!!!")
        return None


    def edit_draw(self, layout, context):
        ''' DRAWS THE SPEAKER TOOLS GUI'''
        # REFACTOR OUT
        debug.print("OLD EDIT_DRAW.... FIX FIX")
        return None

    def draw_spitter(self, context, panel):
        return None
        self.check_deleted_drivers()


        ob = context.object
        mesh = context.mesh
        space = context.space_data

        if ob:
            layout.template_ID(ob, "data")
        elif mesh:
            layout.template_ID(space, "pin_id")



        collection = 'None'
        object = 'None'
        # return collection panel
        area = context.area
        space = context.space_data

        obj = None
        ctxt = 'NONE'
        if hasattr(space, "context"):
            ctxt = space.context

        if area.type.startswith('PROPERTIES'):
            if space.pin_id:
                obj = space.pin_id
            else:
                obj = context.object

        self.check_added_drivers(obj)

        return collection, object, obj

    # The menu can also be called from scripts
    def get_driven_scene_objects(self, scene):
        dic = self.get_collection_dic("objects")
        for k in set(dic.keys()) - set(scene.objects.keys()):
            dic.pop(k)
        return dic

    def get_scene_drivers(self, scene):
        pass

    def get_collection_dic(self, collection):
        return self.filter_dic.get(collection, {})

    def get_object_dic(self, collection, object):
        dm = self
        if dm is None:
            return
        dic = dm.filter_dic
        if collection not in dic.keys():
            return {}
        dic = dic[collection]
        if object not in dic.keys():
            return {}
        dic = dic[object]

        return dic

    def draw_layout(self, layout, context, drivers_dic):

        for dp, array in drivers_dic.items():
            row = layout.row()
            row.label(text=dp)
            row = layout.row()
            col = row.column(align=True)
            for array_index in sorted(array.keys()):

                d = self.find(array[array_index])
                if d is None:
                    continue
                row = col.row()
                edop = row.operator("driver.edit",
                                      emboss=False,
                                      icon='TRIA_RIGHT',
                                      text="")

                edop.toggle = True
                edop.dindex = d.index
                sub = row.split(percentage=100)
                sub.scale_y = 0.6
                #sub = sub.column_flow(columns=1)

                self.driver_draw(d, sub)
                #dm.draw_layout(col, context, [d])
                if getattr(d, "is_open", False):
                    #col.label("OPEN")
                    #dm.draw_layout(col, context, [d])
                    d.driver_edit_draw(col.row(), context)

        return None
    
    def panel_draw_menu(self, panel, context, title="Menu"):
        layout = panel.layout
        row = layout.row()
        sub = row.row()
        sub.alignment = 'LEFT'
        wm = context.window_manager
        sub.prop(wm, "update_dm", text="", icon='FILE_REFRESH')

        row.menu('drivermanager.menu', text=title, icon='DRIVER')

    def panel_posebone_constraint_draw(self, panel, context):
        
        self.check_deleted_drivers()
        active_pose_bone = context.active_pose_bone
        space = context.space_data
        if space.pin_id:
            active_pose_bone = space.pin_id

        constraints = context.pose_bone.constraints.values()

        #get all the drivers that have a do in constaints
        drivers = [d for d in self.all_drivers_list if d.driven_object in constraints]

        dic = {}
        x = {}
        for i, o in enumerate(drivers):

            if o is None or o.driven_object is None:
                continue
            obj = o.fcurve.id_data
            m = dic.setdefault('%s["%s"]' % ("constraints", getattr(o.driven_object, "name", "NoName")), {}) 
            m[i] = o.index

        #debug.print("PD", collection, ob, obj, search, dic)
        if len(dic):
            self.panel_draw_menu(panel, context, title="pose_bone_constraint")
            self.draw_layout(panel.layout, context, dic)
        #self.check_added_drivers(obj)
        #self.check_added_drivers(context.object)

    def panel_draw(self, panel, context):
        if getattr(panel, "search", "") == "pose_bone_constraint":
            self.panel_posebone_constraint_draw(panel, context)
            return None
        def node_name(str):
            name = str.replace('nodes["', '')
            name = name[:name.find(']') - 1]
            return name

        self.check_deleted_drivers()
        collection = getattr(panel, "collection", "NONE")
        panel_context = getattr(panel, "context", "object")
        search = getattr(panel,"search", "")

        obj = getattr(context, panel_context, None)
        if collection == "particles":
            obj = getattr(obj, "settings", None)

        '''
        elif panel_context == "bone":
            print("BONE", obj)
        elif panel_context == "pose_bone":
            print("BONE", obj)

        '''
        space = context.space_data

        if space.pin_id:
            obj = space.pin_id
            #print("PINID BONE", obj)

        if collection == "shape_keys":
            if hasattr(obj, "shape_keys"):
                obj = obj.shape_keys
            if hasattr(obj, "data"):
                obj = obj.data.shape_keys
            else:
                obj = getattr(context.object.data, "shape_keys", None)

        if obj is None:
            return

        dm = self
        
        layout = panel.layout
        #collection, ob, obj = self.draw_spitter(context)
        ob = obj.name
        dic = self.get_object_dic(collection, ob)
        search_string = '%s["%s"]' % (collection, ob)
        if search != "":
            search_string = '%s["%s"]' % (collection, ob)
            if search == "texture_slots":
                obs = [d for d in self.all_drivers_list if getattr(d.driven_object, "name", "") == ob]
            else:
                obs = [self.find(i) for k,v in dic.items()  if k.startswith(search)  for i in v.values()]
            dic = {}
            x = {}
            for i, o in enumerate(obs):

                if o is None or o.driven_object is None:
                    continue
                obj = o.fcurve.id_data
                if search == "texture_slots":
                    m = dic.setdefault(o.prop, {}) 
                    m[o.array_index] = o.index
                else:
                    m = dic.setdefault('%s["%s"]' % (search, getattr(o.driven_object, "name", "NoName")), {}) 
                    m[i] = o.index

        #debug.print("PD", collection, ob, obj, search, dic)
        if len(dic):
            self.panel_draw_menu(panel, context, title=search_string)
            self.draw_layout(layout, context, dic)
        self.check_added_drivers(obj)
        #self.check_added_drivers(context.object)

    def _PanelInvader(self, remove_only=False):
        def SD__draw(panel, context):
            #panel.layout.label("TEST")
            self.panel_draw(panel, context)

        default_dic = {"panels": [],
                       "context": "object",
                       "collection": "objects",
                       "draw": "append",
                       "search": "",
                       }
        panel_dic = {
                     "worlds": {
                                "collection": "worlds",
                                "panels":["WORLD_PT_world"],
                                "context": "world",
                                "draw": "prepend", # will prepend
                               },
                
                     "scenes": {
                                "collection": "scenes",
                                "panels":["SCENE_PT_scene"],
                                "context": "scene",
                                "draw": "prepend", # will prepend
                               },
                     "objects":{
                                "collection": "objects",
                                "panels":["OBJECT_PT_context_object"],
                                "context": "object",
                               },
                     "meshes": {
                                "collection": "meshes",
                                "panels":["DATA_PT_context_mesh"],
                                "context": "mesh",
                               },
                     "shape_keys": {
                                "collection": "shape_keys",
                                "panels":["DATA_PT_shape_keys"],
                                "context": "mesh",
                                "draw": "prepend", # will prepend
                               },
                     "armatures": {
                                "collection": "armatures",
                                "panels":["DATA_PT_context_arm"],
                                "context": "armature",
                               },
                     "bone_constaints": {
                                "collection": "objects",
                                "panels":["BONE_PT_context_bone"],
                                "context": "object",
                                "search": "pose.bones",
                                },
                     "pose_bones": {
                                "collection": "objects",
                                "panels":["BONE_PT_constraints"],
                                "context": "pose_bone",
                                "search": "pose_bone_constraint",
                                "draw": "prepend", # will prepend
                               },
                     "metaballs": {
                                "collection": "metaballs",
                                "panels":["DATA_PT_context_metaball"],
                                "context": "meta_ball",
                               },
                     "lattices": {
                                "collection": "lattices",
                                "panels":["DATA_PT_context_lattice"],
                                "context": "lattice",
                               },
                     "lamps": {
                                "collection": "lamps",
                                "panels":["DATA_PT_context_lamp"],
                                "context": "lamp",
                               },
                     "cameras": {
                                "collection": "cameras",
                                "panels":["DATA_PT_context_camera"],
                                "context": "camera",
                               },
                     "materials": {
                                "collection": "materials",
                                "panels":["MATERIAL_PT_context_material", "Cycles_PT_context_material"],
                                "context": "material",
                                "draw": "prepend", # will prepend
                               },
                     "textures": {
                                "collection": "textures",
                                "panels":["TEXTURE_PT_context_texture"],
                                "context":"texture",
                                "draw": "prepend",
                                "search": "texture_slots",
                                },

                     "constraints": {
                                "collection": "objects",
                                "panels":["OBJECT_PT_constraints"],
                                "search": "constraint",
                                "draw": "prepend",
                                },

                     "modifiers": {
                                "collection": "objects",
                                "panels":["DATA_PT_modifiers"],
                                "search": "modifiers",
                                "draw": "prepend",
                                },
                     "particles": {
                                "collection": "particles",
                                "panels":["PARTICLE_PT_context_particles"],
                                "context": "particle_system",
                                #"search": "modifiers",
                                "draw": "prepend",
                                },

                      }
        '''
                  
                  "",
                  "NODE_PT_active_node_generic",
        '''

        for k in panel_dic.keys():
            pdic = panel_dic[k]
            panels = pdic.setdefault("panels", default_dic["panels"])
            collection = pdic.setdefault("collection", default_dic["collection"])
            panel_context = pdic.setdefault("context", default_dic["context"])
            draw = pdic.setdefault("draw", default_dic["draw"])
            search = pdic.setdefault("search", default_dic["search"])
            for p in panels:
                pt = getattr(bpy.types, p, None)
                if pt is None:
                    debug.print(p, "PANEL is not registered")
                    continue
                remove_draw_pend(pt, "SD_")
                if not remove_only:
                    f = getattr(pt, draw)
                    setattr(pt, "collection", collection)
                    setattr(pt, "context", panel_context)
                    setattr(pt, "search", search)
                    f(SD__draw)

    def panel_shutter(self):
        import bl_ui
        prop_mods = [mod for mod in dir(bl_ui) if mod.startswith('properties')]
        for k in prop_mods:
            prop_mod = getattr(bl_ui, k)
            panels = [p for p in dir(prop_mod) if p.find("_PT_") > 1]

        # panel_shutter()

    def draw_filters(self, layout, context):
        layout = layout.layout
        scene = context.scene
        wm = context.window_manager
        filterrow = layout.row(align=True)
        sub = filterrow.row()
        sub.alignment = 'LEFT'
        wm = context.window_manager
        sub.prop(wm, "update_dm", text="", icon='FILE_REFRESH')

        driven_objects = scene.driver_objects
        filters = driven_objects.filters
        filterrow.prop(driven_objects, "use_filters", text="", icon='FILTER', toggle=True)

        # for key in self.get_driver_dict().keys():
        row = filterrow.row(align=True)

        row.enabled = driven_objects.use_filters
        for key in self.filter_dic:
            row.prop(filters, key, text="", icon=get_icon(key), toggle=True)

    def driver_draw(self, sounddriver, layout):
        # move to isMonkey
        def driver_icon(fcurve):
            driver = fcurve.driver
            if len(driver.variables) == 1 \
                    and driver.variables[0].name == "var" \
                    and driver.variables[0].targets[0].id is None:
                return 'MONKEY'
            return 'DRIVER'

        i = 0

        driver = sounddriver.fcurve
        if not driver:
            return None
        icon = driver_icon(driver)
        can_edit = True
        row = layout
        if self.updating:
            row.label("UPDATING")
            row.alert = True
            return
        row.enabled = can_edit
        row.alignment = 'LEFT'
        #colrow.prop(driver, "color", text="", icon=icon)
        if sounddriver.is_node:
            # quick hack need to pass context or refactor
            sounddriver.draw_node_slider(row, bpy.context)
        else:
            # sounddriver.
            if False and getattr(sounddriver, "edit_driver_baking", False):
                row.scale_y = 0.5
                sounddriver.baking_draw(row)
            else:
                sounddriver.draw_slider(row)

        sub = row.row()
        sub.alignment = 'RIGHT'
        format_data_path(sub, driver.data_path, True, padding=1)

