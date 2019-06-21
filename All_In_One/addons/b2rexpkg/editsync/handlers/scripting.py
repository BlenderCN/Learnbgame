"""
 Takes care of attaching scripts to objects.
"""
import uuid

from .base import SyncModule

import bpy

LLSDText = 10

class ScriptingModule(SyncModule):
    def register(self, parent):
        """
        Register this module with the editor
        """
        parent.Asset.registerAssetType(LLSDText, self.create_llsd_script)

    def unregister(self, parent):
        """
        Unregister this module from the editor
        """
        return

    def upload(self, name):
        """
        Upload the text with the given name to the sim.
        """
        editor = self._parent
        text_obj = bpy.data.texts[name]
        self.upload_text(text_obj)

    def find_text(self, text_uuid):
        """
        Find the text object with the given uuid
        """
        editor = self._parent
        return editor.find_with_uuid(text_uuid, bpy.data.texts, 'texts')

    def create_llsd_script(self, assetID, assetType, data):
        """
        Import a sl script arriving from the simulator.
        """
        editor = self._parent
        text = data.decode('ascii')
        name = ''

        for item in editor.Inventory:
            if item['AssetID'] == assetID:
                name = item['Name']
        if not name:
            for object_id, items in editor.Inventory.obj_inventory.items():
                for item_id, item in items.items():
                    if item['asset_id'] == assetID:
                        name = item['name']
                        break
         

        text_obj = bpy.data.texts.new(name)
        text_obj.write(text)
        text_obj.opensim.uuid = assetID
        

    # Upload a text object to the sim
    def upload_text(self, text_obj):
        """
        Upload the given blender text object to the simulator.
        """
        editor = self._parent
        text_data = ""
        # gather text data
        for line in text_obj.lines:
            text_data += line.body + "\n"
        # initialize object sim state
        name = text_obj.name
        desc = "test script"

        # asset uploaded callback
        def upload_finished(old_uuid, new_uuid, tr_uuid):
            print('upload_finished!!!!!', old_uuid, new_uuid, tr_uuid)
            text_obj.opensim.uuid = new_uuid
            text_obj.opensim.state = 'OK'
            self.simrt.CreateInventoryItem(tr_uuid,
                                           LLSDText,
                                           LLSDText,
                                           name,
                                           desc)
        def update_finished(old_uuid, new_uuid, tr_uuid):
            text_obj.opensim.uuid = new_uuid
            text_obj.opensim.state = 'OK'
            for item_id, item in editor.Inventory.items():
                if item['AssetID'] == old_uuid:
                    item['AssetID'] = new_uuid

                    self.simrt.UpdateInventoryItem(item_id,
                                                   tr_uuid,
                                                   LLSDText,
                                                   LLSDText,
                                                   name,
                                                   desc)
            for object_id, items in editor.Inventory.obj_inventory.items():
                for item_id, item in items.items():
                    if item['asset_id'] == old_uuid:
                        item['asset_id'] = new_uuid
                        self.simrt.UpdateTaskInventoryItem(object_id, item_id,
                                                           tr_uuid, item)

        if text_obj.opensim.uuid:
            cb = update_finished
        else:
            text_obj.opensim.uuid = str(uuid.uuid4())
            cb = upload_finished
        text_obj.opensim.state = 'UPLOADING'
        # start uploading
        editor.Asset.upload(text_obj.opensim.uuid, LLSDText,
                            text_data.encode('ascii'),
                            cb)



