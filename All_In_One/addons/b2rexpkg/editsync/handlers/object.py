"""
 ObjectModule: Manages the synchronization of editor objects.
"""
import logging

from .base import SyncModule
import base64

import b2rexpkg

import bpy

logger = logging.getLogger('b2rex.Object')

class ObjectModule(SyncModule):
    def register(self, parent):
        """
        Register this module with the editor
        """
        parent.registerCommand('delete', self.processDeleteCommand)
        parent.registerCommand('meshcreated', self.processMeshCreated)

    def unregister(self, parent):
        """
        Unregister this module from the editor
        """
        parent.unregisterCommand('delete')
        parent.unregisterCommand('meshcreated')

    def finishedLoadingObject(self, objId, obj=None):
        """
        To be called when an object has finished loading. This happens when we
        gathered enough information to place the object, which includes parent,
        scale and position.
        """
        editor = self._parent
        if not obj:
            obj = editor.findWithUUID(objId)
        if obj.opensim.state == 'OK':
            # already loaded so just updating
            return
        b2rexpkg.editor.set_loading_state(obj, 'OK')
        editor.trigger_callback('object.create', str(objId))


    def createObjectWithMesh(self, new_mesh, objId, meshId, materials=[]):
        """
        Create an object for the given mesh, with an optional list of materials.
        """
        editor = self._parent
        obj = editor.getcreate_object(objId, "opensim", new_mesh)
        editor.setMeshMaterials(new_mesh, materials)
        if objId in editor.positions:
            pos = editor.positions[objId]
            editor.apply_position(obj, pos, raw=True)
        if objId in editor.rotations:
            rot = editor.rotations[objId]
            editor.apply_rotation(obj, rot, raw=True)
        if objId in editor.scales:
            scale = editor.scales[objId]
            editor.apply_scale(obj, scale)
        editor.set_uuid(obj, objId)
        editor.set_uuid(new_mesh, meshId)
        scene = editor.get_current_scene()
        if not obj.name in scene.objects:
            if hasattr(obj, '_obj'):
                try:
                    scene.objects.link(obj._obj)
                except:
                    pass # XXX :-P
            else:
                scene.objects.link(obj)
            new_mesh.update()
        editor.trigger_callback('object.precreate', str(objId))
        return obj

    def processMeshCreated(self, obj_uuid, mesh_uuid, new_obj_uuid, asset_id):
        """
        The agent informed of a mesh object that finished creation. It provides
        new uuids for the object, since we set random uuids when creating but
        the sim provides its own.
        """
        foundobject = False
        foundmesh = False
        editor = self._parent
        for obj in editor.getSelected():
            if obj.type == 'MESH' and obj.opensim.uuid == obj_uuid:
                foundobject = obj
            if obj.type == 'MESH' and obj.data.opensim.uuid == mesh_uuid:
                foundmesh = obj.data

        if not foundmesh:
            foundmesh = editor.find_with_uuid(mesh_uuid,
                                              bpy.data.meshes, "meshes")
        if not foundobject:
            foundobject = editor.find_with_uuid(obj_uuid,
                                              bpy.data.objects, "objects")
        if foundobject:
            editor.set_uuid(foundobject, new_obj_uuid)
            b2rexpkg.editor.set_loading_state(foundobject, 'OK')
        else:
            logger.warning("Could not find object for meshcreated")
        if foundmesh:
            editor.set_uuid(foundmesh, asset_id)
        else:
            logger.warning("Could not find mesh for meshcreated")

    def processDeleteCommand(self, objId):
        """
        An object kill arrived from the simulator.
        """
        editor = self._parent
        obj = editor.findWithUUID(objId)
        if obj:
            print("DELETE FOR",objId)
            # delete from object cache
            if objId in editor._total['objects']:
                del editor._total['objects'][objId]
            # clear uuid
            obj.opensim.uuid = ""
            scene = editor.get_current_scene()
            # unlink
            scene.objects.unlink(obj)
            editor.queueRedraw()

    def processLink(self, parentId, *childrenIds):
        """
        Link the given parent to the specified children.
        """
        editor = self._parent
        parent = editor.findWithUUID(parentId)
        if parent:
            for childId in childrenIds:
                child = editor.findWithUUID(childId)
                if child:
                    child.parent = parent
                    # apply final callbacks
                    self.finishedLoadingObject(childId, child)
                else:
                    # shouldnt happen :)
                    print("b2rex.processLink: cant find child to link!")
        else:
            for childId in childrenIds:
                editor.add_callback('object.precreate', parentId, self.processLink,
                              parentId, childId)

    def sendObjectClone(self, obj, materials):
        """
        Send a Clone command to the agent.
        """
        editor = self._parent
        obj_name = obj.name
        mesh = obj.data
        if not obj.opensim.uuid:
            obj.opensim.uuid = str(uuid.uuid4())
        obj_uuid = obj.opensim.uuid
        mesh_name = mesh.name
        mesh_uuid = mesh.opensim.uuid
        pos, rot, scale = editor.getObjectProperties(obj)
        
        self.simrt.Clone(obj_name, obj_uuid, mesh_name, mesh_uuid,
                           editor.unapply_position(obj, pos),
                           editor.unapply_rotation(rot),
                           editor.unapply_scale(obj, scale), materials)
        
    def sendObjectUpload(self, obj, mesh, data, materials):
        """
        Send a Create command tot he agent.
        """
        editor = self._parent
        data = data.replace(b'MeshSerializer_v1.41', b'MeshSerializer_v1.40')

        b64data = base64.urlsafe_b64encode(data).decode('ascii')
        obj_name = obj.name
        obj_uuid = obj.opensim.uuid
        mesh_name = mesh.name
        mesh_uuid = mesh.opensim.uuid
        pos, rot, scale = editor.getObjectProperties(obj)
        
        self.simrt.Create(obj_name, obj_uuid, mesh_name, mesh_uuid,
                           editor.unapply_position(obj, pos),
                           editor.unapply_rotation(rot),
                           editor.unapply_scale(obj, scale), b64data,
                           materials)

    def doRtObjectUpload(self, context, obj):
        """
        Perform an object upload using the real time connection. If the given
        mesh has the uuid set we will clone the object, otherwise we create
        which means we have to upload the new mesh object.
        """
        editor = self._parent
        mesh = obj.data
        has_mesh_uuid = mesh.opensim.uuid
        b2rexpkg.editor.set_loading_state(obj, 'UPLOADING')
        if has_mesh_uuid:
            def finish_clone(materials):
                self.sendObjectClone(obj, materials)
            editor.doExportMaterials(obj, cb=finish_clone)
            return
        def finish_upload(materials):
            def send_upload(data):
                self.sendObjectUpload(obj, mesh, data, materials)
            editor.doAsyncExportMesh(context, obj, send_upload)
        editor.doExportMaterials(obj, cb=finish_upload)
        # export mesh
        # upload prim
        # self.sendObjectUpload(selected, mesh, data)
        # send new prim

