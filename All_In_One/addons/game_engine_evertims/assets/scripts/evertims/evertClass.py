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


from . import ( evertUtils, OSC )
import mathutils
import math
import socket
import bgl

class Ray():
    """
    Ray object, used for raytracing visual feedback. Basically a start point, an
    end point and a drawing method based on bgl (GLSL)
    """

    def __init__(self, ID, p1, p2):
        """
        Ray class constructor.

        :param ID: ray ID
        :param p1: ray start point coordinates
        :param p2: ray end point coordinates
        :type ID: Integer
        :type p1: 3-elements tuple
        :type p2: 3-elements tuple
        """

        self.ID = ID
        self.p1 = p1
        self.p2 = p2

    def setCoord(self, p1, p2):
        """
        Define ray coordinates.

        :param p1: ray start point coordinates
        :param p2: ray end point coordinates
        :type p1: 3-elements tuple
        :type p2: 3-elements tuple
        """

        self.p1 = p1
        self.p2 = p2

    def drawPath(self):
        """
        Draw ray on screen.
        """
        bgl.glColor4f(0.8,0.8,0.9,0.01)
        bgl.glLineWidth(0.01)

        bgl.glBegin(bgl.GL_LINES)
        bgl.glVertex3f(self.p1[0],self.p1[1],self.p1[2])
        bgl.glVertex3f(self.p2[0],self.p2[1],self.p2[2])
        bgl.glEnd()

        bgl.glNormal3f(0.0,0.0,1.0)
        bgl.glShadeModel(bgl.GL_SMOOTH);

def test(scene):
    print('true update')

class Room():
    """
    Room object, bridge between the notions of BGE KX_GameObject and EVERTims room.
    """

    def __init__(self, kx_obj):
        """
        Room constructor.

        :param kx_obj: Blender Object representing EVERTims room
        :type kx_obj: KX_GameObject
        """
        self.obj = kx_obj
        # self.objName = kx_obj.name # UNDO related
        self.rt60Values = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        # TODO: ADD GLOBAL NUMBERING ON '...' PROPERTY (TO AVOID 2 OBJECTS HAVING THE SAME)
        if not 'room' in self.obj:
            self.obj['room'] = 0

        self.is_updated = True # name is ill chosen: understand "needs to be updated?", chosen for compliance with blender's internal ".is_updated"

        if BLENDER_MODE == 'BPY':
            self.oldMaterialCollection = self.obj.data.materials
            # print('added room callback to scene_update_pre stack')
            bpy.app.handlers.scene_update_pre.append(self._check_for_updates_callback)

    def hasChanged(self):
        """
        Check if room has changed since last check.

        :return: a boolean saying whether or not the room changed since last check
        :rtype: Boolean
        """
        if self.is_updated:
            self.is_updated = False
            return True
        else:
            return False

        # if not self.hasBeenUpdatedOnce:
        #     self.hasBeenUpdatedOnce = True
        #     return True
        # else:
        #     if BLENDER_MODE == 'BPY':
        #         # for e in dir(self.obj): print(e)
        #         # print(self.obj, self.obj.name, self.obj.is_updated, self.obj.is_updated_data)
        #         # return self.obj.is_updated # DOESN't UPDATE A THING!
        #         # return True
        #         return self.is_updated

        # return False # no update in BGE mode

    def _check_for_updates_callback(self, scene):
        if not self.is_updated: # do not set to false here
            # check for mesh update based on blender is_updated internal routine
            self.is_updated = self.obj.is_updated

            # check for material update
            # DOESN'T WORK IF ONLY CHANGE MATERIAL NAME
            # for e in self.obj.data.materials: print(e, dir(e))
            if (BLENDER_MODE == 'BPY') and (self.obj.data is not None) and (self.oldMaterialCollection != self.obj.data.materials):
                self.is_updated = True
                self.oldMaterialCollection = self.obj.data.materials
            # print('check for room update', self.is_updated)


    def getPropsListAsOSCMsgs(self):
        """
        Return a list of OSC formatted messages holding room properties
        (faces geometry and associated materials).

        :return: list of strings, formatted as OSC messages ready to be sent to EVERTims Client
        :rtype: List
        """
        formatedMsg = []

        if BLENDER_MODE == 'BGE':
            polygonDict = self._getFacesAndMaterials()
        elif BLENDER_MODE == 'BPY':
            polygonDict = self._getFacesAndMaterials_bpy()

        for key in polygonDict.keys():
            faceID = str(key)
            matID = polygonDict[key]['material']
            p0123 = polygonDict[key]['vertices']
            msg = self._shapeFaceMsg(faceID,matID,p0123)
            formatedMsg.append(msg)
        return formatedMsg

    def _getFacesAndMaterials(self):
        """
        Return a dictionary which elements represent the vertices and material of a face.

        :return: dict of dict, each dict holds items representing a face: keys are 'material' (String naming the material) and 'vertices' (N-element list of the vertices that compose the face, each element of said list is a list of the vertice's coordinates).
        :rtype: Dictionary
        """
        room = self.obj
        polygonDict = {}          # a dict that holds faces (dict), their vertices (dict: positions and materials)
        mesh = room.meshes[0]     # WARNING: supposed to work with a single mesh material
        poly = mesh.getPolygon(0) # get polygon list

        for n in range(0,mesh.numPolygons):
            polygonDict[n+1] = {}

            # get face (poly) materials
            poly = mesh.getPolygon(n)
            polygonDict[n+1]['material'] = poly.material_name.replace('MA','') # since blender add 'MA' to each material name

            # get face (poly) vertices positions
            v1_xyz = room.worldTransform * mesh.getVertex(poly.material_id, poly.v1).XYZ
            v2_xyz = room.worldTransform * mesh.getVertex(poly.material_id, poly.v2).XYZ
            v3_xyz = room.worldTransform * mesh.getVertex(poly.material_id, poly.v3).XYZ
            v4_xyz = room.worldTransform * mesh.getVertex(poly.material_id, poly.v4).XYZ
            polygonDict[n+1]['vertices'] = [v1_xyz, v2_xyz, v3_xyz, v4_xyz]
            # if gl.dbg: print ('  ' + 'face ' + str(n) + ' - materials '+ poly.material_name.replace('MA',''))
        return polygonDict

    def _getFacesAndMaterials_bpy(self):
        """
        Return a dictionary which elements represent the vertices and material of a face.

        :return: dict of dict, each dict holds items representing a face: keys are 'material' (String naming the material) and 'vertices' (N-element list of the vertices that compose the face, each element of said list is a list of the vertice's coordinates).
        :rtype: Dictionary
        """
        obj = self.obj
        mesh = obj.data
        polygonDict = {}          # a dict that holds faces (dict), their vertices (dict: positions and materials)
        # self._checkForUndoMess()

        for n in range (0, len(mesh.polygons)):
            f = mesh.polygons[n] # current face

            # create local dict
            d = {}

            # get face material
            slot = obj.material_slots[f.material_index]
            mat = slot.material
            d['material'] = mat.name

            # get face vertices
            v_list = []
            for v in f.vertices: # browse through vertice index
                vect = obj.matrix_world * mesh.vertices[v].co
                v_list.append(vect)
            
            # add third twice for triangle face (expected by evertims raytracing client)
            if( len(f.vertices) == 3 ): 
                vect = obj.matrix_world * mesh.vertices[ f.vertices[2] ].co
                v_list.append(vect)

            d['vertices'] = v_list

            # store local dict
            polygonDict[n] = d
        return polygonDict

    def _shapeFaceMsg(self, faceID,matID,pListVect):
        """
        String shapping (particularly for pListVect)
        """
        pList_string = ''
        for vect in pListVect:
            vectRound = [round(elmt,2) for elmt in vect[:]]
            p_string = str(vectRound[:])
            p_string = p_string.replace('[','').replace(']','').replace(',','')
            pList_string = pList_string + ' ' + p_string
        osc_msg = '/face ' + str(faceID) + ' ' + matID +  ' ' + pList_string
        return osc_msg

    # def _checkForUndoMess(self):
    #     """
    #     Undo (Ctrl + Z, BPY mode only) will cause unpredicted things, e.g. self.obj not being the orignal one 
    #     as defined in __init__. This method handles this mess. 

    #     :return: boolean, True if mess detected
    #     """
    #     try:
    #         if self.objName != self.obj.name:
    #             self.obj = bpy.context.scene.objects.get(self.objName)
    #             return True
    #     except UnicodeDecodeError:
    #         self.obj = bpy.context.scene.objects.get(self.objName)
    #         return True
    #     return False

class SourceListener():
    """
    Source / Listener object, bridge between the notions of BGE KX_GameObject and EVERTims Listeners / Sources.
    """

    def __init__(self, kx_obj, typeOfInstance):
        """
        Source / Listener constructor.

        :param kx_obj: Blender Object representing EVERTims listener / source
        :param typeOfInstance: precision on the nature of the created object, either 'source' or 'listener'
        :type kx_obj: KX_GameObject
        :type typeOfInstance: String
        """
        self.obj = kx_obj
        # self.objName = kx_obj.name
        self.type = typeOfInstance # either 'source' or 'listener'
        self.old_worldTransform = None
        self.moveThresholdLoc = 0.0
        self.moveThresholdRot = 0.0
        # TODO: ADD GLOBAL NUMBERING ON '...' PROPERTY (TO AVOID 2 OBJECTS HAVING THE SAME)
        if not self.type in self.obj:
            self.obj[self.type] = 0

    def setMoveThreshold(self, thresholdLoc, thresholdRot):
        """
        Define a threshold value to limit listener / source update to EVERTims client.

        :param threshold: value above which an EVERTims object as to move to be updated (in position) to the client
        :type threshold: Float
        """
        self.moveThresholdLoc = thresholdLoc
        self.moveThresholdRot = thresholdRot

    def hasMoved(self):
        """
        Check if source/client has moved since last check.

        :return: a boolean saying whether or not the source / listener moved since last check
        :rtype: Boolean
        """
        if BLENDER_MODE == 'BGE':
            world_tranform = self.obj.worldTransform.copy()
        elif BLENDER_MODE == 'BPY':
            world_tranform = self.obj.matrix_world.copy()

        # if objed has not yet been checked
        if not self.old_worldTransform:
            self.old_worldTransform = world_tranform
            return True

        elif self._areDifferent_Mat44(world_tranform, self.old_worldTransform, self.moveThresholdLoc, self.moveThresholdRot):
            # moved since last check
            self.old_worldTransform = world_tranform
            return True
        else:
            # did not move since last check
            return False

    def getPropsAsOSCMsg(self):
        """
        Return a OSC formated string holding source / lister type, name, and current world transform.

        :return: typically: '/listener listener_1 -0.76 -0.65 0.0 0.0 -0.13 0.15 0.98 0.0 -0.63 0.75 -0.19 0.0 4.62 -5.45 3.08 1.0'
        :rtype: String
        """
        if BLENDER_MODE == 'BGE':
            world_tranform = self.obj.worldTransform
            # obj_type_id = self.obj[self.type] # based on game property
            obj_type_id = 1 # hardcoded for now (limited to a unique self.type then)
        elif BLENDER_MODE == 'BPY':
            # self._checkForUndoMess()
            world_tranform = self.obj.matrix_world
            # obj_type_id = self.obj.game.properties[self.type].value
            obj_type_id = 1 # hardcoded for now (limited to a unique self.type then)

        msg = self._shapeOSCMsg('/' + self.type, self.type + '_' + str(obj_type_id), world_tranform)
        return msg

    # def _checkForUndoMess(self):
    #     """
    #     Undo (Ctrl + Z, BPY mode only) will cause unpredicted things, e.g. self.obj not being the orignal one 
    #     as defined in __init__. This method handles this mess. 

    #     :return: boolean, True if mess detected
    #     """
    #     try:
    #         if self.objName != self.obj.name:
    #             self.obj = bpy.context.scene.objects.get(self.objName)
    #             return True
    #     except UnicodeDecodeError:
    #         self.obj = bpy.context.scene.objects.get(self.objName)
    #         return True
    #     return False

    def _shapeOSCMsg(self, header, ID, mat44):
        """
        String shapping (particularly for mat44).
        """
        mat44_str = ''
        for elmt in mat44.col: mat44_str = mat44_str + str(elmt.to_tuple(2)[:]) # to tuple allows to round the Vector
        mat44_str = mat44_str.replace('(','').replace(')',' ').replace(',','')
        osc_msg = header + ' ' + ID + ' ' + mat44_str
        return osc_msg

    def _areDifferent_Mat44(self, mat1, mat2, thresholdLoc = 1.0, thresholdRot = 1.0):
        """
        Check if 2 input matrices are different above a certain threshold.

        :param mat1: input Matrix
        :param mat2: input Matrix
        :param thresholdLoc: threshold above which delta translation between the 2 matrix has to be for them to be qualified as different
        :param thresholdRot: threshold above which delta rotation between the 2 matrix has to be for them to be qualified as different
        :type mat1: mathutils.Matrix
        :type mat2: mathutils.Matrix
        :type thresholdLoc: Float
        :type thresholdRot: Float
        :return: a boolean stating wheter the two matrices are different
        :rtype: Boolean
        """
        areDifferent = False
        jnd_vect = mathutils.Vector((thresholdLoc,thresholdLoc,thresholdRot))
        t1, t2 = mat1.to_translation(), mat2.to_translation()
        r1, r2 = mat1.to_euler(), mat2.to_euler()
        for n in range(3):
            if (abs(t1[n]-t2[n]) > thresholdLoc) or (abs(math.degrees(r1[n]-r2[n])) > thresholdRot): areDifferent = True
        return areDifferent

class RayManager():
    """
    Ray manager class: handle Ray objects for raytracing visual feedback.
    """

    def __init__(self, sock, sock_size, dbg = False):
        """
        Ray manager constructor.

        :param sock: socket with which the ray manager communicates with the EVERTims client.
        :param sock_size: size of packet read every pass (sock.recv(sock_size))
        :param dbg: enable debug (print log in console)
        :type sock: Socket
        :type sock_size: Integer
        :type dbg: Boolean
        """
        self.sock = sock
        self.sock_size = sock_size
        self.dbg = dbg
        self.rayDict = {}
        self.missedRayCounter = 0

        # define bpy handle
        self._draw_handler_handle = None

        # add local pre_draw method to to scene callback
        if BLENDER_MODE == 'BGE':
            gl.getCurrentScene().pre_draw.append(self._pre_draw_bge)
        elif BLENDER_MODE == 'BPY':
            self._draw_handler_handle = bpy.types.SpaceView3D.draw_handler_add(self._draw_handler, (None,None), 'WINDOW', 'PRE_VIEW')
            if self.dbg: print('added evertims module raytracing callback to draw_handler')

    def __del__(self):
        """
        Main Destructor
        """
        self.del_common()


    def handle_remove(self):
        """
        Destructor related method, called when EVERTims bpy module disabled from addon
        """
        self.del_common()

    def del_common(self):
        """
        Destructor actions
        """
        if BLENDER_MODE == 'BPY':
            if self._draw_handler_handle is not None:
                bpy.types.SpaceView3D.draw_handler_remove(self._draw_handler_handle, 'WINDOW')
                self._draw_handler_handle = None
                if self.dbg: print('removed evertims module raytracing callback from draw_handler')

    def _pre_draw_common(self):
        """
        Callback method.
        Common to BPY and BGE mode
        """
        # read socket content...
        msg = self._readSocket()
        # ... until socket is empty
        while msg:
            self._syncRayDict(msg)
            msg = self._readSocket()

    def _pre_draw_bge(self):
        """
        Callback method.
        invoked in BGE mode every frame
        """
        self._pre_draw_common()
        # draw rays
        self._drawRays()

    # NOTE FOR SELF:
    # I had to split the raytracing drawing on screen in two methods:
    # bpy_modal, run always, that receives packets from EVERTims client
    # and _draw_handler called as a draw_handler, i.e. every
    # time something changes on the screen.
    # the reason is that rays are not traced if the _drawRays() method is called
    # in the modal loop (go wonder why though). Best solution would be to find a draw_handler equivalent
    # called every N frame (and not only when something moves on the screen)

    def bpy_modal(self):
        """
        Callback method.
        invoked from main evertims module bpy_modal (always)
        """
        self._pre_draw_common()

    def _draw_handler(self, bpy_dummy_self, bpy_dummy_context):
        """
        Callback method.
        invoked in bpy.types.SpaceView3D draw_handler (every time something moves on Blender 3D view)
        """
        self._drawRays()

    def _syncRayDict(self, msg):
        """
        Synchronize (add, update, or remove) rays from the
        local dict based on OSC messages received from EVERTims client.

        :param msg: OSC message received from EVERTims client
        :type msg: String
        """
        # check if 'on' or 'off' line
        if msg[0] == 'on':
            # check if full message received
            if len(msg) == 4 and len(msg[-1]) == 3:
                # if on, check if new line or update line
                if not msg[1] in self.rayDict:
                    # new line
                    self.rayDict[msg[1]] = Ray(msg[1],msg[2], msg[3])
                    if self.dbg: print('+ added in ray dict: ', msg, '\n')
                else:
                    # update line
                    self.rayDict[msg[1]].setCoord(msg[2], msg[3])
                    if self.dbg: print('updated line in ray dict: ', msg, '\n')
            else:
                # account for missed ray
                self.missedRayCounter += 1
                if self.dbg:
                    print('\r!!! ray(s) missed: {0}'.format(self.missedRayCounter), '\n')

        elif msg[0] == 'off':
            # remove ray from local dict
            try:
                del(self.rayDict[msg[1]])
                if self.dbg: print ('removed line in ray dict:', self.rayDict[msg[1]].ID, '\n')
            except KeyError:
                if self.dbg: print ('cannot remove ray (not in local dict):', msg, '\n')


    def _drawRays(self):
        """
        Invoke draw methods from rays in local dict
        """
        for rayID, ray in self.rayDict.items():
            ray.drawPath()


    def _readSocket(self):
        """
        Read input from socket.

        :return: OSC message as a decoded string
        :rtype: String
        """
        try:
            raw_msg = self.sock.recv(self.sock_size)

            if raw_msg:
                osc_msg = raw_msg.decode("utf-8")
                out_msg = self._shapeOscInMsg(osc_msg)
                if self.dbg: print ('<- received from', self.sock.getsockname()[0] + ':' + str(self.sock.getsockname()[1]), ':', out_msg)
                # gl.logs['in'].append(out_msg) # record OSC logs
                return out_msg
            # ''.join(total_data)
            else: return ()

        except socket.timeout: # nothing received
            return ()
        except OSError: # socket closed
            return ()

    def _shapeOscInMsg(self, msg_str):
        """
        OSC input message shapping.

        Format OUT (state, ID, (coodStart), (coordEnd))
                   ('on', 45, (2.06, 0.0, 1.67), (28.2, 0.0))

        :param msg_str: OSC input message
        :type msg_str: String
        """

        msg_list = msg_str.split(' ')

        onOff = msg_list[0][6:9].replace(' ', '')
        ID = int(msg_list[1])

        if len(msg_list) == 8 and len(msg_list[-1]) >= 4:
            coord1, coord2 = tuple([round(float(elmt),2) for elmt in msg_list[2:5]]), tuple([round(float(elmt),2) for elmt in msg_list[5::]])
        else:
            coord1, coord2 = (), ()

        return (onOff,ID,coord1,coord2)
