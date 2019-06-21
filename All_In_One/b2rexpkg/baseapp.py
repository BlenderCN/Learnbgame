import os
import sys
import time
import uuid
import traceback
import threading
from hashlib import md5
from collections import defaultdict

import b2rexpkg
from b2rexpkg.tools.siminfo import GridInfo
from b2rexpkg import IMMEDIATE, ERROR, OK
from b2rexpkg import editor

from .editsync.handlers.map import MapModule
from .editsync.handlers.game import GameModule
from .editsync.handlers.caps import CapsModule
from .editsync.handlers.stats import StatsModule
from .editsync.handlers.asset import AssetModule
from .editsync.handlers.prims import PrimsModule
from .editsync.handlers.online import OnlineModule
from .editsync.handlers.rexlogic import RexLogicModule
from .editsync.handlers.rexexport import RexExportModule
from .editsync.handlers.fsmeditor import FsmEditorModule
from .editsync.handlers.scripting import ScriptingModule
from .editsync.handlers.agents import AgentsModule
from .editsync.handlers.object import ObjectModule
from .editsync.handlers.terrain import TerrainModule
from .editsync.handlers.rexdata import RexDataModule
from .editsync.handlers.objectprops import ObjectPropertiesModule
from .editsync.handlers.regionhandshake import RegionHandshakeModule

from .tools.threadpool import ThreadPool, NoResultsPending

from .importer import Importer
from .exporter import Exporter
from .tools.simconnection import SimConnection

from .tools.simtypes import AssetType

import bpy

priority_commands = ['pos', 'LayerData', 'LayerDataDecoded', 'scale',
                     'RexPrimData', 'capabilities']

if sys.version_info[0] == 3:
    import urllib.request as urllib2
else:
    import Blender
    import urllib2


eventlet_present = False
try:
    import eventlet
    try:
        from b2rexpkg import simrt
        eventlet_present = True
    except:
        traceback.print_exc()
except:
    from b2rexpkg import threadrt as simrt
    eventlet_present = True

import logging
logger = logging.getLogger('b2rex.baseapp')

class ObjectState(object):
    def __init__(self, bobj):
        self.update(bobj)

    def update(self, bobj):
        self.pointer = bobj.as_pointer()
        if hasattr(bobj, 'parent') and bobj.parent and bobj.parent.opensim.uuid:
            self.parent = bobj.parent.as_pointer()
            self.parent_uuid = bobj.parent.opensim.uuid
        else:
            self.parent = None

class DefaultMap(defaultdict):
    def __init__(self):
        defaultdict.__init__(self, list)

class BaseApplication(Importer, Exporter):
    def __init__(self, title="RealXtend"):
        self.command_queue = []
        self.wanted_workers = 1
        self._callbacks = defaultdict(DefaultMap)
        self.second_start = time.time()
        self.second_budget = 0
        self._lastthrottle = 0
        self._last_time = time.time()
        self.pool = ThreadPool(1)
        self.workpool = ThreadPool(5)
        self.rawselected = set()
        self.caps = {}
        self.agent_id = ""
        self.loglevel = "standard"
        self.agent_access = ""
        self.rt_support = eventlet_present
        self.stats = [0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.status = "b2rex started"
        self.status_level = OK
        self.selected = {}
        self.sim_selection = set()
        self.connected = False
        self.positions = {}
        self.rotations = {}
        self.scales = {}
        self.rt_on = False
        self.simrt = None
        self.screen = self
        self.gridinfo = GridInfo()
        self.buttons = {}
        self.settings_visible = False
        self._requested_urls = []
        self._modules = {}
        self._module_cb = defaultdict(list)
        self.initializeCommands()
        self.initializeModules()
        Importer.__init__(self, self.gridinfo)
        Exporter.__init__(self, self.gridinfo)

    # Modules
    def registerModule(self, module):
        """
        Register a module with the editor.

        The module will be registrered as an attribute in the
        editor, generally taking the name and removing "Module", so
        for example AssetModule becomes self.Asset.

        Also, some special callbacks will be looked for and registered
        for calling, at the moment we have the following:
            * check: check during the command processing stage
            * draw: gets drawn into the scene panel
        """
        self._modules[module.getName()] = module
        module.register(self)
        setattr(self, module.getName(), module)
        for section in ["check", "draw", "draw_object"]:
            if hasattr(module, section):
                self._module_cb[section].append(getattr(module, section))

    def drawModules(self, layout, props):
        """
        Calls to draw all modules registered in the system.
        """
        for draw_cb in self._module_cb["draw"]:
            draw_cb(layout, self, props)

    def drawObjectModules(self, layout, obj):
        """
        Calls to draw all modules registered in the system.
        """
        for draw_cb in self._module_cb["draw_object"]:
            draw_cb(layout, self, obj)


    # Generic callback functionality
    def add_callback(self, section, signal, callback, *parameters):
        """
        Add a callback into a given section, waiting for a specific signal.
        The callback will be called with the specified parameters in expanded
        form.
        """
        self._callbacks[str(section)][str(signal)].append((callback, parameters))

    def insert_callback(self, section, signal, callback, *parameters):
        """
        Like ass_callback but inserts the callback at the beginning of the
        queue.
        """
        self._callbacks[str(section)][str(signal)].insert(0, (callback, parameters))

    def trigger_callback(self, section, signal):
        """
        Trigger the callback for the given section and signal.
        """
        for callback, parameters in self._callbacks[str(section)][str(signal)]:
            callback(*parameters)
        del self._callbacks[str(section)][str(signal)]

    # Initialization
    def initializeModules(self):
        """
        Initialize editor modules.
        """
        self.registerModule(AssetModule(self))
        self.registerModule(PrimsModule(self))
        self.registerModule(MapModule(self))
        self.registerModule(GameModule(self))
        self.registerModule(CapsModule(self))
        self.registerModule(ObjectModule(self))
        self.registerModule(RexDataModule(self))
        self.registerModule(ObjectPropertiesModule(self))
        self.registerModule(RegionHandshakeModule(self))
        self.registerModule(TerrainModule(self))
        self.registerModule(StatsModule(self))
        self.registerModule(OnlineModule(self))
        self.registerModule(RexLogicModule(self))
        self.registerModule(RexExportModule(self))
        self.registerModule(AgentsModule(self))
        self.registerModule(ScriptingModule(self))
        self.registerModule(FsmEditorModule(self))

    def initializeCommands(self):
        """
        Initialize internal editor commands.
        """
        self._cmd_matrix = {}
        self.registerCommand('pos', self.processPosCommand)
        self.registerCommand('rot', self.processRotCommand)
        self.registerCommand('scale', self.processScaleCommand)
        self.registerCommand('msg', self.processMsgCommand)
        self.registerCommand('connected', self.processConnectedCommand)

        # internal
        self.registerCommand('error', self.processError)
        self.registerCommand('agentquit', self.processAgentQuit)
        self.registerCommand('materialarrived', self.processMaterialArrived)
        self.registerCommand('texturearrived', self.processTextureArrived)

    # Threaded Downloader
    def addDownload(self, http_url, cb, cb_pars=(), error_cb=None, extra_main=None):
        """
        Add a download into the internal threaded downloader. If the url is
        already downloaded False will be returned, otherwise the url will be
        downloaded, then the callback cb will be called with cb_pars.

        If extra_main is supplied it will be run in a thread before returning
        the final callback.

        If error_cb is supplied it will be called on errors.
        """
        if http_url in self._requested_urls:
            return False
        self._requested_urls.append(http_url)

        if not error_cb:
            _error_cb = self.default_error_db
        else:
            def _error_cb(request, result):
                error_cb(result)

        def _cb(request, result):
            cb(result, *cb_pars)

        def _extra_cb(request, result):
             self.workpool.addRequest(extra_main,
                                     [[http_url, cb_pars, result]],
                                      _cb,
                                      _error_cb)
        if extra_main:
            _main_cb = _extra_cb
        else:
            _main_cb = _cb
        self.pool.addRequest(self.doDownload, [[http_url, cb_pars]], _main_cb, _error_cb)
        return True

    def default_error_db(self, request, error):
        """
        Default error function for thread pool jobs.
        """
        if hasattr(error[1], "code") and error[1].code in [404]:
            pass
        else:
            logger.warning("error downloading "+str(request)+": "+str(error))
            if hasattr(error[1], "code"):
                print("error downloading "+str(request)+": "+str(error[1].code))
            traceback.print_tb(error[2])

    def doDownload(self, pars):
        """
        Internal downloading function to be run in a thread.
        """
        http_url, pars = pars
        req = urllib2.urlopen(http_url)
        return req.read()

    # Connection
    def processConnectedCommand(self, agent_id, agent_access):
        """
        Connected messaage received from agent.
        """
        self.agent_id = agent_id
        self.agent_access = agent_access
        self.addStatus("Connected to region")

    def connect(self, base_url, username="", password=""):
        """
        Connect to an opensim instance
        """
        self.sim.connect(base_url+'/xml-rpc.php')
        firstname, lastname = username.split()
        coninfo = self.sim.login(firstname, lastname, password)
        self._sim_port = coninfo['sim_port']
        self._sim_ip = coninfo['sim_ip']
        self._sim_url = 'http://'+str(self._sim_ip)+':'+str(self._sim_port)
        logger.info("reconnect to " + self._sim_url)
        self.gridinfo.connect('http://'+str(self._sim_ip)+':'+str(9000), username, password)
        self.sim.connect(self._sim_url)

    def onConnectAction(self):
        """
        Connect Action
        """
        base_url = self.exportSettings.server_url
        self.addStatus("Connecting to " + base_url, IMMEDIATE)
        self.region_uuid = ''
        self.regionLayout = None
        self.connect(base_url, self.exportSettings.username,
                         self.exportSettings.password)


        try:
            self.regions = self.gridinfo.getRegions()
            self.griddata = self.gridinfo.getGridInfo()
        except:
            self.addStatus("Error: couldnt connect to " + base_url, ERROR)
            traceback.print_exc()
            return
        # create the regions panel
        self.addRegionsPanel(self.regions, self.griddata)
        if eventlet_present:
            self.addRtCheckBox()
        else:
            logger.warning("no support for real time communications")

        self.connected = True
        self.addStatus("Connected to " + self.griddata['gridnick'])

    # Rt enable/disable
    def onToggleRt(self, context=None):
        """
        Toggle the real time agent.
        """
        if context:
            if context.scene:
                # scene will not be defined when exiting the program
                self.exportSettings = context.scene.b2rex_props
        if self.rt_on:
            self.simrt.quit()
            self.rt_on = False
            self.simrt = None
        else:
            self.enableRt(context)
            self.rt_on = True

        for mod in self._modules.values():
            mod.onToggleRt(self.rt_on)

    def enableRt(self, context):
        """
        Enable the real time agent.
        """
        # for the moment we fet some parameters in a different way depending
        # on the editor version.
        if sys.version_info[0] == 3:
            pars = self.exportSettings.getCurrentConnection()
            server_url = pars.url
            credentials = self.credentials
        else:
            pars = self.exportSettings
            server_url = pars.server_url
            credentials = self.exportSettings.credentials

        props = self.exportSettings

        # no functionality yet to change region.
        region_name = 'last'

        # we will send the editor version as our entrance punchline.
        firstline = editor.getVersion()

        # get the password from the credential manager since we dont store
        # it with other blender data.
        username, password = credentials.get_credentials(server_url,
                                                              pars.username)

        # if defined we insert the agent library path into the environment.
        if props.agent_libs_path:
            os.environ['SIMRT_LIBS_PATH'] = props.agent_libs_path
        elif 'SIMRT_LIBS_PATH' in os.environ:
            del os.environ['SIMRT_LIBS_PATH']

        # tools path, where python may be located
        if props.tools_path:
            os.environ['SIMRT_TOOLS_PATH'] = props.tools_path
        elif 'SIMRT_TOOLS_PATH' in os.environ:
            del os.environ['SIMRT_TOOLS_PATH']

        # now setup the login parameters to be forwarded to the agent.
        login_params = { 'region': region_name, 
                        'firstline': firstline }
       
        # depending on the usename form we will use a different kind of login.
        if '@' in pars.username:
            # federated login
            auth_uri = pars.username.split('@')[1]
            con = SimConnection()
            con.connect('http://'+auth_uri)
            account = pars.username
            passwd_hash = '$1$'+md5(password.encode('ascii')).hexdigest()

            res = con._con.ClientAuthentication({'account':account,
                                           'passwd':passwd_hash,
                                           'loginuri':server_url})

            avatarStorageUrl = res['avatarStorageUrl']
            sessionHash = res['sessionHash']
            gridUrl = res['gridUrl']

            login_params['first'] = 'NotReallyNeeded'
            login_params['last'] = 'NotReallyNeeded'
            login_params['AuthenticationAddress'] = auth_uri
            login_params['account'] = pars.username
            login_params['passwd'] = passwd_hash
            login_params['sessionhash'] = sessionHash

        else:
            # normal opensim login
            login_params['first'] = pars.username.split()[0]
            login_params['last'] = pars.username.split()[1]
            login_params['passwd'] = password

        # start the agent.
        self.simrt = simrt.run_thread(self, server_url,
                                      login_params)
        self.connected = True

        # send our preferred throttle.
        self._lastthrottle = self.exportSettings.kbytesPerSecond*1024
        self.simrt.Throttle(self._lastthrottle)

        if not context:
            Blender.Window.QAdd(Blender.Window.GetAreaID(),Blender.Draw.REDRAW,0,1)

    # Redraw from thread
    def redraw(self):
        """
        Queue a redraw of the application. This function is designed to be run
        from a thread, and for the moment is dangerous so can be controlled with
        a global toggle at b2rexpkg.safe_mode.
        """
        if b2rexpkg.safe_mode:
            return
        if not self.stats[5] and self._last_time + 1 < time.time():
            # we're using the commands left stats to keep our counter
            self.stats[5] += 1
            self._last_time = time.time()
            self.queueRedraw(True)

    # Commands
    def registerCommand(self, cmd, callback):
        """
        Register a command with the command processing subsystem.
        """
        self._cmd_matrix[cmd] = callback

    def unregisterCommand(self, cmd):
        """
        Unregister a command from the command processing subsystem.
        """
        del self._cmd_matrix[cmd]

    def processCommand(self, cmd, *args):
        """
        Process the given command with the given arguments.
        """
        self.stats[0] += 1
        cmdHandler = self._cmd_matrix.get(cmd, None)
        if cmdHandler:
            try:
                cmdHandler(*args)
            except Exception as e:
                print("Error executing", cmd, e)
                traceback.print_exc()

    # Material related callbacks
    def materialArrived(self, data, objId, meshId, matId, assetType, matIdx):
        """
        A material has arrived from downloading.
        """
        self.command_queue.append(["materialarrived", data, objId, meshId,
                                      matId, assetType, matIdx])

    def materialTextureArrived(self, data, objId, meshId, matId, assetType, matIdx):
        """
        A material texture has arrived (a material with AssetType 0 which means
        there is no formal material declaration and we will use the texture
        directly).
        """
        self.create_material_fromimage(matId, data, meshId, matIdx)

    def processMaterialArrived(self, data, objId, meshId, matId, assetType, matIdx):
        """
        A material has arrived and has to be processed in the queue.
        """
        if assetType == AssetType.OgreMaterial:
            self.parse_material(matId, {"name":matId, "data":data}, meshId,
                                matIdx)



    # Object actions
    def doRtUpload(self, context):
        """
        Upload the active object using the real time connection.
        """
        selected = bpy.context.selected_objects
        if selected:
            # just the first for now
            selected = selected[0]
            if not selected.opensim.uuid:
                self.Object.doRtObjectUpload(context, selected)
                return

    def doDelete(self):
        """
        Delete all selected objects from the simulator.
        """
        selected = editor.getSelected()
        if selected:
            for obj in selected:
                if obj.opensim.uuid:
                    self.simrt.Delete(obj.opensim.uuid)

    def doDeRezObject(self):
        """
        DeRez all active objects into inventory.
        """
        selected = editor.getSelected()
        if selected:
            for obj in selected:
                if obj.opensim.uuid:
                    editor.set_loading_state(obj, 'TAKING')
                    self.simrt.DeRezObject(obj.opensim.uuid)

    # Misc common functionality
    def registerTextureImage(self, image):
        """
        Register an image with the system.
        """
        # register a texture with the sim
        if not image.opensim.uuid:
            image.opensim.uuid = str(uuid.uuid4())
        return image.opensim.uuid

    def processError(self, error):
        """
        Error received from the agent.
        """
        self.addStatus(error, ERROR)
        self.queueRedraw(immediate=True)

    def processAgentQuit(self, msg):
        """
        Quit received from the agent.
        """
        if self.rt_on:
            self.onToggleRt()
            self.queueRedraw()

    def processMsgCommand(self, username, message):
        """
        Process a chat message, can be overloaded by additional modules ;)
        """
        self.addStatus("message from "+username+": "+message)

    def findWithUUID(self, objId):
        """
        Find the editor object with the given uuid.
        """
        obj = self.find_with_uuid(str(objId), bpy.data.objects, "objects")
        return obj

    def setMeshMaterials(self, mesh, materials):
        """
        Set the materials for a mesh from an idx, matId, asset_type list.
        """
        presentIds = list(map(lambda s: s.opensim.uuid, mesh.materials))
        for idx, matId, asset_type in materials:
            mat = self.find_with_uuid(matId, bpy.data.materials, 'materials')
            if mat and not matId in presentIds:
                mesh.materials.append(mat)

    # Position commands
    def processPosCommand(self, objId, pos, rot=None):
        """
        Position for an object arrived from the agent.
        """
        obj = self.findWithUUID(objId)
        if obj and editor.get_loading_state(obj) == 'OK':
            self._processPosCommand(obj, objId, pos)
            if rot:
                self._processRotCommand(obj, objId, rot)
        else:
            self.add_callback('object.create', objId, self.processPosCommand, objId, pos, rot)

    def processScaleCommand(self, objId, scale):
        """
        Scale for an object arrived from the agent.
        """
        obj = self.findWithUUID(objId)
        if obj and editor.get_loading_state(obj) == 'OK':
            self._processScaleCommand(obj, objId, scale)
        else:
            self.add_callback('object.create', objId, self.processScaleCommand,
                              objId, scale)

    def processRotCommand(self, objId, rot):
        """
        Rotation for an object arrived from the agent.
        """
        obj = self.findWithUUID(objId)
        if obj and editor.get_loading_state(obj) == 'OK':
            self._processRotCommand(obj, objId, rot)
        else:
            self.add_callback('object.create', objId, self.processRotCommand,
                              objId, rot)
            
    # Checks
    def processUpdate(self, obj):
        """
        Process all object updates not requiring modification of the object
        (executed from the view).
        """
        obj_uuid = self.get_uuid(obj)
        if obj_uuid:
            pos, rot, scale = self.getObjectProperties(obj)
            pos = list(pos)
            rot = list(rot)
            scale = list(scale)
            # check parent
            if obj_uuid in self.selected:
                parent_pointer = None
                prevstate = self.selected[obj_uuid]
                if obj.parent and obj.parent.opensim.uuid:
                    parent_pointer = obj.parent.as_pointer()
                if prevstate.parent != parent_pointer:
                    if parent_pointer:
                        parent_uuid = obj.parent.opensim.uuid
                        self.simrt.Link(parent_uuid, obj_uuid)
                    else:
                        parent_uuid = prevstate.parent_uuid
                        self.simrt.Unlink(parent_uuid, obj_uuid)
                    # save properties and dont process position updates
                    prevstate.update(obj)
                    self.positions[obj_uuid] = pos
                    self.rotations[obj_uuid] = rot
                    self.scales[obj_uuid] = scale
                    return obj_uuid

            if not obj_uuid in self.rotations or not rot == self.rotations[obj_uuid]:
                self.stats[1] += 1
                if obj.parent:
                    self.simrt.apply_position(obj_uuid,
                                              self.unapply_position(obj, pos,0,0,0), self.unapply_rotation(rot))
                else:
                    self.simrt.apply_position(obj_uuid,
                                              self.unapply_position(obj, pos), self.unapply_rotation(rot))
                self.positions[obj_uuid] = pos
                self.rotations[obj_uuid] = rot
            elif not obj_uuid in self.positions or not pos == self.positions[obj_uuid]:
                self.stats[1] += 1
                if obj.parent:
                    self.simrt.apply_position(obj_uuid,
                                              self.unapply_position(obj, pos,0,0,0))
                else:
                    self.simrt.apply_position(obj_uuid, self.unapply_position(obj, pos))
                self.positions[obj_uuid] = pos
            if not obj_uuid in self.scales or not scale == self.scales[obj_uuid]:
                self.stats[1] += 1
                self.simrt.apply_scale(obj_uuid, self.unapply_scale(obj, scale))
                self.scales[obj_uuid] = scale

            return obj_uuid


    def checkPool(self):
        """
        Check the pool size and apply any needed adjustments.
        """
        # check thread pool size
        if self.wanted_workers != self.exportSettings.pool_workers:
            current_workers = self.wanted_workers
            wanted_workers = self.exportSettings.pool_workers
            if current_workers < wanted_workers:
                self.pool.createWorkers(wanted_workers-current_workers)
            else:
                self.pool.dismissWorkers(current_workers-wanted_workers)
            self.wanted_workers = self.exportSettings.pool_workers

    def processUpdates(self):
        """
        Process all pending updates up to the configured time budget.
        """
        starttime = time.time()
        self._last_time = time.time()
        framebudget = float(self.exportSettings.rt_budget)/1000.0
        try:
            self.pool.poll()
        except NoResultsPending:
            pass
        try:
            self.workpool.poll()
        except NoResultsPending:
            pass

        props = self.exportSettings
        if props.kbytesPerSecond*1024 != self._lastthrottle:
            self.simrt.Throttle(props.kbytesPerSecond*1024)

        # check consistency
        self.checkUuidConsistency(set(editor.getSelected()))

        # per second checks
        if time.time() - self.second_start > 1:
            self.checkPool()
            self.second_budget = 0
            self.second_start = time.time()

        for check_cb in self._module_cb["check"]:
            check_cb(starttime, framebudget)
        self.checkObjects()

        # process command queue
        if time.time() - starttime < framebudget:
            self.processCommandQueue(starttime, framebudget)

        # redraw if we have commands left
        if len(self.command_queue):
            self.queueRedraw()

    def checkObjects(self):
        """
        Check objects during operator process. This is the main place to perform
        checks on objects to see if we have to send any updates. Note at the
        moment also processUpdate performs some checks.
        """
        selected = set(editor.getSelected())
        all_selected = set()
        # look for changes in objects
        for obj in selected:
            obj_id = self.get_uuid(obj)
            if obj_id in self.selected and obj.as_pointer() == self.selected[obj_id].pointer:
                if obj.name != obj.opensim.name:
                    if not obj.name.startswith('opensim') and not obj.name.startswith(obj.opensim.name):
                        print("Sending New Name", obj.name, obj.opensim.name)
                        self.simrt.SetName(obj_id, obj.name)
                        obj.opensim.name = obj.name
                        print(obj.opensim.name)

    def processCommandQueue(self, starttime, budget):
        """
        Process the command queue up to the given budget, considering start
        of budget consumption at starttime.
        """
        # the command queue can change while we execute here, but it should
        # be ok as long as things are just added at the end.
        # note if they are added at the beginning we would have problems
        # when deleting things after processing.
        self.command_queue += self.simrt.getQueue()
        cmds = self.command_queue
        second_budget = float(self.exportSettings.rt_sec_budget)/1000.0
        currbudget = 0
        self.stats[8] += 1
        if cmds:
            self.stats[2] += 1
            # first check the priority commands
            processed = []
            for idx, cmd in enumerate(cmds):
                currbudget = time.time()-starttime
                if currbudget < budget and self.second_budget+currbudget < second_budget:
                    if cmd[0] in priority_commands:
                        processed.append(idx)
                        self.processCommand(*cmd)
                else:
                    break
            # delete all processed elements. in reversed order
            # to avoid problems because of index changing
            for idx in reversed(processed):
                cmds.pop(idx)
            # now all other commands, note there should be no priority
            # commands so we just ignore they exist and process all commands.
            if time.time()-starttime < budget:
                processed = []
                for idx, cmd in enumerate(cmds):
                    currbudget = time.time()-starttime
                    if currbudget < budget and self.second_budget+currbudget < second_budget:
                        processed.append(idx)
                        self.processCommand(*cmd)
                    else:
                        break
                for idx in reversed(processed):
                    cmds.pop(idx)
        self.second_budget += currbudget
        self.stats[5] = len(self.command_queue)
        self.stats[6] = (currbudget)*1000 # processed
        self.stats[7] = threading.activeCount()-1

    def checkUuidConsistency(self, selected):
        """
        Check the selection for uuid inconsistencies derived from object cloning
        or copying.
        """
        # look for duplicates
        if self.rawselected == selected:
            return
        oldselected = self.selected
        newselected = {}
        isobjcopy = True
        for obj in selected:
            obj_uuid = obj.opensim.uuid
            if obj.type == 'MESH' and obj_uuid:
                mesh_uuid = obj.data.opensim.uuid
                if obj.opensim.uuid in oldselected:
                    prevstate = oldselected[obj_uuid]
                    if prevstate.pointer == obj.as_pointer():
                        newselected[obj_uuid] = oldselected[obj_uuid]
                        if mesh_uuid:
                            newselected[mesh_uuid] = oldselected[mesh_uuid]
                    else:
                        # check for copy or clone
                        # copy or clone
                        if mesh_uuid in oldselected and not oldselected[mesh_uuid].pointer == obj.data.as_pointer():
                            # copy
                            ismeshcopy = True
                            obj.data.opensim.uuid = ""
                        else:
                            # clone
                            if mesh_uuid in oldselected:
                                newselected[mesh_uuid] = oldselected[mesh_uuid]
                        obj.opensim.uuid = ""
                        obj.opensim.state = "OFFLINE"
                else:
                    newselected[obj_uuid] = ObjectState(obj)
                    newselected[mesh_uuid] = ObjectState(obj.data)
        self.selected = newselected
        self.rawselected = selected

    def processView(self):
        """
        Process any needed updates from the view.
        """
        self.stats[9] += 1

        selected = set(editor.getSelected())
        all_selected = set()
        # changes in our own avatar
        agent = self.findWithUUID(self.agent_id)
        if agent:
            self.processUpdate(agent)
        # look for changes in objects
        for obj in selected:
            obj_id = self.get_uuid(obj)
            if obj_id in self.selected and obj.as_pointer() == self.selected[obj_id].pointer:
                self.processUpdate(obj)
                all_selected.add(obj_id)
        # update selection
        if not all_selected == self.sim_selection:
            self.simrt.Select(*all_selected)
            self.sim_selection = all_selected

    def getSelected(self):
        """
        Get the selected objects, possibly proxyed into editor objects.
        """
        return editor.getSelected()

    # Callbacks to override in specific applications
    def addStatus(self, text, priority=0):
        """
        Add a status line to the editor.
        """
        pass

    def initGui(self, title):
        """
        Init the gui.
        """
        pass

    def go(self):
        """
        Start the ogre interface system
        """
        self.screen.activate()

    def addRegionsPanel(self, regions, griddata):
        """
        Add the regions panel after getting the region list from /admin/regions
        """
        pass

    def queueRedraw(self, pars=None, immediate=False):
        """
        queue a redraw for the application.
        """
        pass

    def applyObjectProperties(self, obj, pars):
        """
        Apply object properties into the editor backend.
        """
        pass

    def addRtCheckBox(self):
        """
        Add a checkbox to enable or disable the real time agent.
        """
        pass


