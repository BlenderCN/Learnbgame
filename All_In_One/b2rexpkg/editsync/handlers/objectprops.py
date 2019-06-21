"""
 ObjectPropertiesModule: Processor for ObjectProperties and ObjectUpdates.
"""

from .base import SyncModule

from b2rexpkg.tools.simtypes import PCodeEnum

import bpy

class ObjectPropertiesModule(SyncModule):
    def register(self, parent):
        """
        Register this module with the editor
        """
        parent.registerCommand('props', self.processPropsCommand)
        parent.registerCommand('ObjectProperties', self.processObjectPropertiesCommand)

    def unregister(self, parent):
        """
        Unregister this module from the editor
        """
        parent.unregisterCommand('props')
        parent.unregisterCommand('ObjectProperties')

    def processPropsCommand(self, objId, pars):
        """
        Properties arrived from an ObjectUpdate.
        """
        editor = self._parent
        if "PCode" in pars and pars["PCode"] == PCodeEnum.Avatar:
            agent = editor.Agents[objId] # creates the agent
            if "NameValues" in pars:
                props = pars["NameValues"]
                if "FirstName" in props and "LastName" in props:
                    agent.name = props['FirstName']+" "+props["LastName"]
                    editor._total['objects'][objId] = agent.name
        else:
            parentId = pars["ParentID"]
            obj = editor.findWithUUID(objId)
            if not obj and not objId in editor.RexData.rexobjects and pars["PCode"] == PCodeEnum.Primitive:
                    obj = editor.Prims.create(objId, pars)
            if obj:
                # we have the object
                if parentId:
                    parent = editor.findWithUUID(parentId)
                    if parent:
                        obj.parent = parent
                        editor.Object.finishedLoadingObject(objId, obj)
                    else:
                        editor.add_callback('object.precreate', parentId,
                                          editor.Object.processLink,
                              parentId, objId)
                else:
                    obj.parent = None
                    # apply final callbacks
                    editor.Object.finishedLoadingObject(objId, obj)
            elif parentId:
                # need to wait for object and the parent to appear
                editor.add_callback('object.precreate', objId, editor.Object.processLink, parentId, objId)
            else:
                # need to wait for the object and afterwards
                # trigger the object create
                # need to wait for object and the parent to appear
                #def call_precreate(obj_id):
                #    editor.trigger_callback('object.create', obj_id)
                editor.insert_callback('object.precreate',
                                     objId,
                                     editor.Object.finishedLoadingObject,
                                     objId)
                #print("parent for unexisting object!")
        self.processObjectPropertiesCommand(objId, pars)

    def processObjectPropertiesCommand(self, objId, pars):
        """
        Properties arrived from an ObjectProperties packet. Generally this
        happens when the object is selected.
        """
        editor = self._parent
        obj = editor.find_with_uuid(str(objId), bpy.data.objects, "objects")
        if obj:
            if "Name" in pars:
                obj.name = pars["Name"]
                obj.opensim.name = pars["Name"]
            if 'InventorySerial' in pars and pars['InventorySerial'] > 0:
                editor.simrt.RequestTaskInventory(objId)

            editor.applyObjectProperties(obj, pars)
        else:
            editor.add_callback('object.create', objId, self.processObjectPropertiesCommand, objId, pars)


