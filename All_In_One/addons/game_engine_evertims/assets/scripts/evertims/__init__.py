# ------------------------------------
BLENDER_MODE=None
try:
    from bge import logic as gl
    BLENDER_MODE = 'BGE'
except ImportError:
    # second because bpy can be imported in
    # blender bge (not in blenderplayer bge though)
    import bpy
    BLENDER_MODE = 'BPY'
# ------------------------------------

from .evertClass import *
from . import OSC
from . import evertUtils
import socket
import json

class Evertims():
    """
    Main EVERTims python module. Send scene information
    (room geometry, materials, listener and source position, etc.)
    to EVERTims client. Eventually trace rays received from EVERTims
    client (for debug purpose).
    """

    def __init__(self):
        """
        EVERTims class constructor
        """

        # define dict to store EVERTims elements in the scene,
        # involved in the simulation
        self.rooms = dict()     # store scene's rooms
        self.sources = dict()   # store scene's sources
        self.listeners = dict() # store scene's listeners
        self.materials = dict() # store evertims materials
        self.rt60Values = [] # ugly wrapper for access of these values in BGE

        # define parameters related to raytracing visual feedback
        self.traceRays = False      # enable/disable visual feedback
        self.rayManager = None   # raytracing handler

        # define debug flag
        self.dbg = True # print info in console if set to True

        # define network related parameters
        self.connect = {
        'raw_msg': '',              # To be filled in threading, contains raw socket datas awaiting to be processed (faster to forbid Evertims msg jamming the socket)
        'ip_raytracing': 'localhost',   # IP of EVERTims' computer
        'ip_auralization': 'localhost', # IP of Auralization engine computer
        'ip_local': 'localhost',    # IP of Blender's computer
        'port_w_raytracing': 0,     # Port to write in EVERTims
        'port_w_auralization': 0,   # Port to write in Auralization Engine
        'port_r': 0,                # Port to read from EVERTims
        'socket': None,             # socket to receive msg from EVERTims
        'socket_size': 2*1024,      # Size of reader socket (a_min = 124, v_min = ..?)
        'socket_timeout': 1e-5,     # Timeout of reader socket
        'buffer_size': 0,           # Buffer size (socket buffer) process will discard packets to receive new ones - no packet discarded if 0 (RealTime / NoError mode)
        }

        # define bpy handles
        self.bpy_handle_callback = None

        self.limit_update_room_update_timer = 0

    def __del__(self):
        """
        EVERTims class destructor
        """
        self._del_common()

        if BLENDER_MODE == 'BPY':
            self.handle_remove()

    def _del_common(self):
        """
        Destructor common to BGE and BPY modes
        """
        # close socket used for raytracing feedback if option was enabled
        if self.traceRays:
            if self.dbg: print('closing read socket (the one used for raytracing feedback)')
            self.connect['socket'].close()

    def handle_remove(self):
        """
        Destructor specific to BPY mode
        """
        self._del_common()

        # remove callback from stack in bpy mode
        if self.bpy_handle_callback is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self.bpy_handle_callback, 'WINDOW')
            self.bpy_handle_callback = None
            if self.dbg: print('removed evertims module callback from draw_handler')
        if self.rayManager is not None:
            self.rayManager.handle_remove()
        # clear room callback
        bpy.app.handlers.scene_update_pre.clear()

    def setDebugMode(self, setDebug):
        """
        Enable / disable debug mode (print info in console).

        :param setDebug: enable/disable debug mode
        :type setDebug: Bool
        """
        self.dbg = setDebug

    def setBufferSize(self, buffer_size):
        self.connect['buffer_size'] = buffer_size

    def addRoom(self, obj):
        """
        Add KX_GameObject as EVERTims room in local dictionnary.

        :param obj: room to add in local dict
        :type obj: KX_GameObject
        """
        self.rooms[obj.name] = Room(obj)

    def getRoom(self):
        # TODO: EVERTIms client accepts only one room for now, code may as well
        # reflect that feature
        for k in self.rooms:
            return self.rooms[k].obj

    def addSource(self, obj):
        """
        Add KX_GameObject as EVERTims source in local dictionnary.

        :param obj: source to add in local dict
        :type obj: KX_GameObject
        """
        self.sources[obj.name] = SourceListener(obj, 'source')

    def addListener(self, obj):
        """
        Add KX_GameObject as EVERTims listener in local dictionnary.

        :param obj: listener to add in local dict
        :type obj: KX_GameObject
        """
        self.listeners[obj.name] = SourceListener(obj, 'listener')

    def setMaterials(self, matDict):
        """
        replace material dictionnary.

        :param matDict: evertims materials dict
        :type obj: dict
        """
        self.materials = matDict

    def setRt60Values(self, valuesStr):
        """
        """
        self.rt60Values = json.loads(valuesStr)

    def resetObjDict(self):
        """
        Clear EVERTims listener, Source and Room dictionnaries.
        """        
        self.rooms.clear()
        self.sources.clear()
        self.listeners.clear()

    def initConnection_read(self, ip, port):
        """
        Init EVERTims to Blender connection, used to receive raytracing information.

        :param ip: IP adress of local host running the BGE
        :param port: PORT where to read information sent by EVERTims client
        :type ip: String
        :type port: Integer
        """
        self.connect['port_r'] = port
        self.connect['ip_local'] = ip

    def initConnection_writeRaytracing(self, ip, port):
        """
        Init Blender to EVERTims connection, used to send room, source, listener, etc. information

        :param ip: IP adress of client host running EVERTims
        :param port: PORT where to write information sent to EVERTims client
        :type ip: String
        :type port: Integer
        """
        self.connect['port_w_raytracing'] = port
        self.connect['ip_raytracing'] = ip

    def initConnection_writeAuralization(self, ip, port):
        """
        Init Blender to Auralization engine connection, used to send rt60

        :param ip: IP adress of client host running Auralization Engine
        :param port: PORT where to write information sent to Auralization Engine
        :type ip: String
        :type port: Integer
        """
        self.connect['port_w_auralization'] = port
        self.connect['ip_auralization'] = ip

    def isReady(self):
        """
        Check EVERTims minimum requirements to enable simulation start:
        at least 1 room, 1 listener, 1 source, and initConnection_write
        parameters must have been defined.
        """
        if self.rooms and self.sources and self.listeners \
            and self.connect['port_w_raytracing'] and self.connect['ip_raytracing'] \
            and self.connect['port_w_auralization'] and self.connect['ip_auralization']:
            return True
        else:
            print('rooms:', self.rooms)
            print('sources:', self.sources)
            print('listeners:', self.listeners)
            print('materials:', self.materials)
            print('port_w_raytracing:', self.connect['port_w_raytracing'])
            print('ip_raytracing:', self.connect['ip_raytracing'])
            return False

    def updateClient(self, objType = ''):
        """
        Upload Room, Source, and Listener information to EVERTims client.

        :param objType: which type of object to update: either 'room', 'source', 'listener', or 'mobile' (i.e. 'source' and 'listener')
        :type objType: String
        """
        somethingToUpdate = False

        if (objType == 'room') or not objType:
            for roomName, room in self.rooms.items():
                if room.hasChanged():
                    somethingToUpdate = True
                    msgList = room.getPropsListAsOSCMsgs()
                    for msg in msgList:
                        self._sendOscMsg(self.connect['ip_raytracing'],self.connect['port_w_raytracing'],msg)
                    # update rt60
                    if BLENDER_MODE == 'BGE':
                        msg = self.rt60Values
                    elif BLENDER_MODE == 'BPY':                    
                        msg = evertUtils.getRt60Values(self.materials, room.obj)
                    self._sendOscMsg(self.connect['ip_auralization'],self.connect['port_w_auralization'], '/rt60', msg)

        if (objType == 'source') or (objType == 'mobile') or not objType:
            for sourceName, source in self.sources.items():
                if source.hasMoved():
                    somethingToUpdate = True
                    msg = source.getPropsAsOSCMsg()
                    self._sendOscMsg(self.connect['ip_raytracing'],self.connect['port_w_raytracing'],msg)

        if (objType == 'listener') or (objType == 'mobile') or not objType:
            for listenerName, listener in self.listeners.items():
                if listener.hasMoved():
                    somethingToUpdate = True
                    msg = listener.getPropsAsOSCMsg()
                    self._sendOscMsg(self.connect['ip_raytracing'],self.connect['port_w_raytracing'],msg)

        return somethingToUpdate

    def setMovementUpdateThreshold(self, thresholdLoc, thresholdRot):
        """
        Define a threshold value to limit listener / source update to EVERTims client.

        :param thresholdLoc: value (m) above which an EVERTims object as to move to be updated to the client
        :param thresholdRot: value (deg) above which an EVERTims object as to rotate to be updated to the client
        :type thresholdLoc: Float
        :type thresholdRot: Float
        """
        for sourceName, source in self.sources.items():
            source.setMoveThreshold(thresholdLoc, thresholdRot)
        for listenerName, listener in self.listeners.items():
            listener.setMoveThreshold(thresholdLoc, thresholdRot)

    def startClientSimulation(self):
        """
        Start EVERTims simulation: sent '/facefinished' message to EVERTims client
        to start acoustic calculation, add local pre_draw method to BGE scene stack.
        """
        # send room, listener, source info to EVERTims client
        self.updateClient()
        # send '/facefinished' to EVERTims client (start calculations)
        self._sendOscMsg(self.connect['ip_raytracing'],self.connect['port_w_raytracing'],'/facefinished')
        # add local pre_draw method to to scene callback
        if BLENDER_MODE == 'BGE':
            gl.getCurrentScene().pre_draw.append(self._pre_draw_bge)
        elif BLENDER_MODE == 'BPY':
            self.bpy_handle_callback = bpy.types.SpaceView3D.draw_handler_add(self._pre_draw_bpy, (None,None), 'WINDOW', 'PRE_VIEW')
            if self.dbg: print('added evertims module callback to draw_handler')

    def activateRayTracingFeedback(self, shouldTraceRays):
        """
        Enable / disable visual feedback on EVERTims raytracing.
        Will init read socket to receive raytracing messages if set to True.

        :param shouldTraceRays: activate / deactivate option
        :type shouldTraceRays: Bool
        """
        # check if connection parameters have been defined
        if not shouldTraceRays:
            self.traceRays = False
            # TODO: disable self.rayManager

        else:
            managedToConnect = False
            if self.connect['ip_local'] and self.connect['port_r']:

                # close eventual old socket (e.g. undo that badly resets the on the fly auralization)
                if self.connect['socket'] is not None: self.connect['socket'].close()
                
                # init receive socket
                (self.connect['socket'], isConnected) = self._getOscSocket(self.connect['ip_local'], self.connect['port_r'])
                if isConnected:

                    # RayManager will handle receiving of raytracing messages,
                    # drawing of rays in BGE
                    self.rayManager = RayManager(self.connect['socket'], self.connect['socket_size'], self.dbg)
                    managedToConnect = True

            if managedToConnect:
                self.traceRays = True
            else:
                print('### Cannot establish downlink connection to EVERTims server, Raytracing feedback deactivated')

    def _pre_draw_bge(self):
        """
        Callback method.
        pre draw callback adapted to bge context (accepts no arguments)
        """
        self._pre_draw_common()

    def _pre_draw_bpy(self, bpy_dummy_self, bpy_dummy_context):
        """
        Callback method.
        pre draw callback adapted to bpy context (expects self and context arguments)
        """
        self._pre_draw_common()

    def _pre_draw_common(self):
        """
        Callback method.
        pre draw callback
        """
        self.updateClient('mobile')

    def bpy_modal(self):
        """
        Callback method.
        called from add-on modal loop (Always).
        (note: despite the lack of _ in front of method name, this method should not be
        included in the end-user API)
        """
        # update ray tracing manager
        if self.rayManager is not None:
            self.rayManager.bpy_modal();

        # update room (limited to every N frame not to overload EVERTims client)
        self.limit_update_room_update_timer += 1
        if self.limit_update_room_update_timer > 0: # disabled for now
            self.limit_update_room_update_timer = 0

            roomHasChanged = self.updateClient('room')
            if roomHasChanged:
                if self.dbg: print('# reload room geometry')
                self._sendOscMsg(self.connect['ip_raytracing'],self.connect['port_w_raytracing'],'/facefinished')

    def _getOscSocket(self, ip,host):
        """
        Initialise a socket at host@ip.

        :param ip: IP adress to connect socket
        :param port: PORT to connect socket
        :type ip: String
        :type port: Integer
        :return: (socket, isconnected)
        :rtype: Socket, Bool
        """
        # create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # eventually set socket buffer size (up speed for real-time)
        if self.connect['buffer_size']:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.connect['buffer_size'])
            print ('!!! socket.SO_RCVBUF size set to', self.connect['buffer_size'], '-> expect droped (unprocessed) packets')

        # bind socket
        isConnected = False
        try:
            sock.bind((ip, host))
            sock.setblocking(0)
            sock.settimeout(self.connect['socket_timeout'])
            isConnected = True
        except OSError as e:
            print ('###', e)
        return (sock, isConnected)

    def _sendOscMsg(self, ip, host, header, msg = ''):
        """
        Send OSC 'header msg' at host@ip.

        :param ip: IP adress where to send OSC message
        :param port: PORT where to send OSC message
        :param header: OSC message header
        :param msg: OSC message content
        :type ip: String
        :type port: Integer
        :type header: String
        :type msg: String
        """
        # create OSC client
        client = OSC.OSCClient()
        # create OSC message, set address, fill message
        osc_msg = OSC.OSCMessage()
        osc_msg.setAddress(header)
        osc_msg.append(msg)

        # send OSC message
        try:
            client.sendto(osc_msg,(ip,host))
            if self.dbg: print ('-> sent to ' + str(host) + '@' + ip + ': ' + header + ' ', msg, '\n')
        except TypeError:
            print ('!!! no route to', host, ip, 'to send OSC message:', header.split(' ')[0]) # may occur in OSC.py if no route to host
