import traceback
import math
import uuid
from io import StringIO

from ..tools.siminfo import GridInfo
from ..compatibility import BaseApplication
from ..tools.logger import logger

# modules for b25
from ..editsync.handlers.chat import ChatModule
from ..editsync.handlers.inventory import InventoryModule
#from .properties import B2RexObjectProps
#from .properties import B2RexProps

from .material import RexMaterialIO

from bpy.props import StringProperty, PointerProperty, IntProperty
from bpy.props import BoolProperty, FloatProperty, CollectionProperty
from bpy.props import FloatVectorProperty

from b2rexpkg.tools.passmanager import PasswordManager

from b2rexpkg import IMMEDIATE, ERROR, OK

import bpy

b_version = 256
if hasattr(bpy.utils, 'register_class'):
    b_version = 257


class B2Rex(BaseApplication):
    def __init__(self, context):
        self.credentials = PasswordManager('b2rex')
        self.region_report = ''
        self.cb_pixel = []
        BaseApplication.__init__(self)
        self.registerModule(ChatModule(self))
        self.registerModule(InventoryModule(self))

    def onConnect(self, context):
        props = context.scene.b2rex_props
        #self.connect(props.server_url, props.username, props.password)
        self.exportSettings = props
        self.onConnectAction()
        if not self.connected:
            return False
        while(len(props.regions) > 0):
                props.regions.remove(0)
        for key, region in self.regions.items():
            props.regions.add()
            regionss = props.regions[-1]
            regionss.name = region['name']
#            regionss.description = region['id']

    def onCheck(self, context):
        props = context.scene.b2rex_props
        self.exportSettings = props
        self.region_uuid = list(self.regions.keys())[props.selected_region]
        self.do_check()

    def onTest(self, context):
        print("export materials")
        props = context.scene.b2rex_props
        current = context.active_object
        if current:
            session = bpy.b2rex_session.doExportMaterials(current, cb=print)
            return
            for mat in current.data.materials:
                face = None
                if current.data.uv_textures:
                    face = current.data.uv_textures[0].data[0]
                matio = RexMaterialIO(self, current.data, face,
                                     False)
                f = StringIO()
                matio.write(f)
                f.seek(0)
                print("MATERIAL", mat.opensim.uuid)
                print(f.read())

    def onProcessQueue(self, context):
        self.processUpdates()

    def onDelete(self, context):
        self.doDelete()

    def onDeRezObject(self):
        self.doDeRezObject()

    def onRezObject(self, item_id):
        location_to_rez_x = bpy.context.scene.cursor_location[0]
        location_to_rez_y = bpy.context.scene.cursor_location[1]
        location_to_rez_z = bpy.context.scene.cursor_location[2]
        location_to_rez = (location_to_rez_x, location_to_rez_y, location_to_rez_z)
        location_to_rez = self._unapply_position(location_to_rez)

        print("onRezObject", item_id, location_to_rez)
        self.simrt.RezObject(item_id, location_to_rez, location_to_rez)

    def onRemoveInventoryItem(self, item_id):
        self.simrt.RemoveInventoryItem(item_id)
 

    def onExport(self, context, delete=True):
        props = context.scene.b2rex_props
        self.doExport(props, props.loc, delete=delete)

    def delete_connection(self, context):
        props = context.scene.b2rex_props
        print("no workie")

    def cancel_edit_connection(self, context):
        props = context.scene.b2rex_props
        props.connection.search = props.connection.list[0].name
        form = props.connection.form
        form.username = ""
        form.password = ""
        form.url = ""
        form.name = ""

    def create_connection(self, context):
        props = context.scene.b2rex_props
        form = props.connection.form
        con = props.connection.list[props.connection.search]
        form.url = ""
        form.name = ""
        form.username = ""
        props.connection.search = 'add'

    def edit_connection(self, context):
        props = context.scene.b2rex_props
        if "add" in props.connection.list:
            props.connection.list.remove(1)
        form = props.connection.form
        con = props.connection.list[props.connection.search]
        form.url = con.url
        form.name = con.name
        form.username = con.username
        props.connection.search = 'edit'

    def add_connection(self, context):
        props = context.scene.b2rex_props
        form = props.connection.form
        if form.name in props.connection.list:
            con = props.connection.list[form.name]
        else:
            props.connection.list.add()
            con = props.connection.list[-1]
        con.name = form.name
        con.username = form.username
        con.url = form.url
        form.name = ""
        form.url = ""
        form.username = ""
        props.connection.search = con.name
        self.credentials.set_credentials(con.url, con.username, form.password)
        form.password = ""

    def draw_callback_view(self, context):
        self.processView()
        bpy.ops.b2rex.processqueue()
        pass

    def register_draw_callbacks(self, context):
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    #if region.type == 'WINDOW': # gets updated every frame
                    if region.type == 'TOOL_PROPS': # gets updated when finishing and operation
                        self.cb_pixel.append(region.callback_add(self.draw_callback_view, 
                                        (context, ),
                                        'POST_PIXEL'))
    def unregister_draw_callbacks(self, context):
        for cb in self.cb_pixel:
            if context.region:
                context.region.callback_remove(cb)
        self.cb_pixel = []

    def onToggleRt(self, context=None):
        if not context:
            context = bpy.context
        if self.rt_on:
            self.addStatus("Agent disconnected.")
        else:
            self.addStatus("Starting agent...")
            self.queueRedraw(immediate=True)
        BaseApplication.onToggleRt(self, context)
        if self.simrt:
            self.register_draw_callbacks(context)
        else:
            self.unregister_draw_callbacks(context)

    def onExportUpload(self, context):
        if self.simrt:
            self.doRtUpload(context)
        else:
            self.onExport(context)
            self.onUpload(context)

    def onUpload(self, context):
        self.doUpload()

    def onImport(self, context):
        props = context.scene.b2rex_props
        self.region_uuid = list(self.regions.keys())[props.selected_region]
        self._import()

    def onSettings(self, context):
        self.settings()

    def _import(self):
        print('importing..')
        text = self.import_region(self.region_uuid)
        self.addStatus("Scene imported " + self.region_uuid)

    def settings(self):
        print("conecttt")

    def do_check(self):
        print("do_check regionuuid" + self.region_uuid)
        self.region_report = self.check_region(self.region_uuid)

    def addStatus(self, status, level=OK):
        self.status = status
        self.status_level = level

    def get_uuid(self, obj):
        """
        Get the uuid from the given object.
        """
        obj_uuid = obj.opensim.uuid
        if obj_uuid:
            return obj_uuid

    def set_uuid(self, obj, obj_uuid):
        """
        Set the uuid for the given blender object.
        """
        obj.opensim.uuid = obj_uuid

    def _processScaleCommand(self, obj, objId, scale):
        self.apply_scale(obj, scale)
        #prev_scale = list(obj.scale)
        #if not prev_scale == scale:
            #    obj.scale = scale
        self.scales[objId] = list(obj.scale)
        self.positions[objId] = list(obj.location)

    def _processPosCommand(self, obj, objId, pos):
        self.apply_position(obj, pos)
        self.positions[objId] = list(obj.location)

    def getObjectProperties(self, obj):
        rot = obj.rotation_euler
        #if obj.opensim.uuid in self.Agents:
            #    rot = [rot[0]-math.pi/2.0, rot[1], rot[2]+math.pi/2.0]
        return (obj.location, rot, obj.scale)

    def _processRotCommand(self, obj, objId, rot):
        """
        if objId in self.Agents:
            rot = self._apply_rotation(rot)
            obj.rotation_euler = (rot[0]+math.pi/2.0, rot[1], rot[2]-math.pi/2.0)
        else:
            self.apply_rotation(obj, rot)
        """
        self.apply_rotation(obj, rot)
        self.rotations[objId] = list(obj.rotation_euler)

    def applyObjectProperties(self, obj, pars):
        for key, value in pars.items():
            if hasattr(obj.opensim, key):
                try:
                    setattr(obj.opensim, key, value)
                except:
                    print("cant set %s to %s"%(key, value))
                    pass # too bad :P
            else:
                prop = None
                if isinstance(value, str):
                    prop = StringProperty(name=key)
                elif isinstance(value, bool):
                    prop = BoolProperty(name=key)
                elif isinstance(value, dict):
                    self.applyObjectProperties(obj, value)
                elif isinstance(value, int):
                    prop = IntProperty(name=key)
                elif isinstance(value, float):
                    prop = FloatProperty(name=key)
                if prop:
                    setattr(bpy.types.B2RexObjectProps, key, prop)
                    setattr(obj.opensim, key, value)
        self.queueRedraw()

    def draw_callback(self, referer, context):
        bpy.ops.b2rex.redraw()
        

    def queueRedraw(self, immediate=False):
        screen = bpy.context.screen
        context = bpy.context
        if screen and not immediate:
            if b_version == 256:
                bpy.ops.b2rex.redraw()
            # b2.57 does it directly on menu panel with
            # draw callbacks
        else:
            # no context means we call a redraw for every
            # screen. this may be happening from a thread
            # and seems to be problematic.
            for screen in bpy.data.screens:
                self.queueRedrawScreen(screen)

    def queueRedrawScreen(self, screen):
        for area in screen.areas:
                area.tag_redraw()


