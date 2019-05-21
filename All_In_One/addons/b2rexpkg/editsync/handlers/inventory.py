"""
 InventoryModule: Manages inventoy inside the editor and provides operations
 for putting items in and out of inventory.
"""
import uuid
import logging

import bpy
from bpy.props import BoolProperty
from collections import defaultdict
from .base import SyncModule


logger = logging.getLogger('b2rex.InventoryModule')


class InventoryModule(SyncModule):

    def register(self, parent):
        """
        Register this module with the editor
        """
        self.obj_inventory = defaultdict(dict)
        self.ui_inventory_expand = defaultdict(bool)
        bpy.types.B2RexObjectProps.inventory = property(self.get_inventory, self.set_inventory)
        bpy.types.B2RexObjectProps.inventory_expand = property(self.get_inventory_expand)
        bpy.types.B2RexObjectProps.toggle_inventory_expand = property(self.toggle_inventory_expand)

        parent.registerCommand('ObjectInventory', self.processObjectInventory)
        parent.registerCommand('InventorySkeleton', self.processInventorySkeleton)
        parent.registerCommand('InventoryDescendents', self.processInventoryDescendents)
        parent.registerCommand('ScriptRunningReply', self.processScriptRunningReply)

    def unregister(self, parent):
        """
        Unregister this module from the editor
        """
        parent.unregisterCommand('InventorySkeleton')
        parent.unregisterCommand('InventoryDescendents')

    def update_folders(self, folders):
        """
        Update the available folders with the given folder dict.
        """
        props = bpy.context.scene.b2rex_props
        cached_folders = getattr(props, 'folders')
        cached_folders.clear()
        
        for folder in folders:
            expand_prop = "e_" + str(folder['FolderID']).split('-')[0]
            if not hasattr(bpy.types.B2RexProps, expand_prop):
                prop = BoolProperty(name="expand", default=False)
                setattr(bpy.types.B2RexProps, expand_prop, prop)

            if folder['Descendents'] < 1:
                setattr(props, expand_prop, False)

            cached_folders[folder['FolderID']] = folder

    def update_items(self, items):
        """
        Update the available items from the fiven item dict.
        """
        props = bpy.context.scene.b2rex_props
        cached_items = props._items
        cached_items.clear()
        for item in items:
            cached_items[item['ItemID']] = item

    def processInventoryDescendents(self, folder_id, folders, items):
        """
        Inventory descendents arrived from the sim.
        """
        logger.debug("processInventoryDescendents")
        self.update_folders(folders)
        self.update_items(items)

    def get_inventory(self, obj):
        return self.obj_inventory[obj.uuid]

    def set_inventory(self, obj, items):
        old_ob_items = self.obj_inventory[obj.uuid]
        ob_items = {}
        self.obj_inventory[obj.uuid] = ob_items
        if isinstance(items, dict):
            items = list(items.values())
        for item in items:
            print(item)
            item_id = item['item_id']
            if item_id in old_ob_items:
                ob_items[item_id] = old_ob_items[item_id]
                ob_items[item_id].update(item)
            else:
                ob_items[item_id] = item
            self.simrt.GetScriptRunning(obj.uuid, item_id)

    def get_inventory_expand(self, obj):
        if not obj.uuid in self.ui_inventory_expand:
            self.ui_inventory_expand[obj.uuid] = False

        return self.ui_inventory_expand[obj.uuid]

    def processScriptRunningReply(self, obj_id, item_id, running, mono):
        editor = self._parent
        obj = editor.findWithUUID(obj_id)
        if item_id in obj.opensim.inventory:
            obj.opensim.inventory[item_id]['running'] = running

    def processObjectInventory(self, obj_inv):

        obj_uuid = obj_inv['object'][0]['obj_id']
        items = obj_inv['item']

        editor = self._parent
        foundobject = editor.find_with_uuid(obj_uuid, bpy.data.objects, "objects")

        if foundobject:
            foundobject.opensim.inventory = items

    def toggle_inventory_expand(self, obj):
        self.ui_inventory_expand[obj.uuid] ^= True
        return self.ui_inventory_expand[obj.uuid]

    def __iter__(self):
        props = bpy.context.scene.b2rex_props
        return iter(props._items.values())

    def values(self):
        props = bpy.context.scene.b2rex_props
        return iter(props._items.values())

    def keys(self):
        props = bpy.context.scene.b2rex_props
        return iter(props._items.keys())

    def items(self):
        props = bpy.context.scene.b2rex_props
        return iter(props._items.items())

    def __contains__(self, itemID):
        props = bpy.context.scene.b2rex_props
        return itemID in props._items

    def __getitem__(self, itemID):
        props = bpy.context.scene.b2rex_props
        return props._items[itemID]

    def processInventorySkeleton(self, inventory):
        """
        Inventory skeleton arrived from the sim.
        """
        logger.debug("processInventorySkeleton")

        props = bpy.context.scene.b2rex_props
        session = bpy.b2rex_session
        B2RexProps = bpy.types.B2RexProps

        if not hasattr(B2RexProps, 'folders'):
            setattr(B2RexProps, 'folders',  dict())
        if not hasattr(B2RexProps, '_items'):
            setattr(B2RexProps, '_items', dict())

        for inv in inventory:
            session.simrt.FetchInventoryDescendents(inv['folder_id'])
            if uuid.UUID(inv['parent_id']).int == 0:
                if not hasattr(B2RexProps, "root_folder"):
                    setattr(B2RexProps, "root_folder", inv['folder_id'])
                setattr(props, "root_folder", inv['folder_id'])


        session.inventory = inventory

    def draw(self, layout, session, props):
        """
        Draw the inventory panel into the given layout.
        """
        row = layout.column()
        row.alignment = 'CENTER'
        if not hasattr(session, 'inventory'):
            return
        if props.inventory_expand:
            row.prop(props, 'inventory_expand', icon="TRIA_DOWN", text="Inventory")
        else:
            row.prop(props, 'inventory_expand', icon="TRIA_RIGHT", text="Inventory")
            return
            
        try:
            inventory = session.inventory
        except:
            row = layout.column()
            row.label(text='Inventory not loaded')
            return

        
        if hasattr(bpy.types.B2RexProps, "root_folder"): 
            root_folder = getattr(props, "root_folder")
            self.draw_folder(layout, root_folder, 0)

    def draw_folder(self, layout, folder_id, indent):
        """
        Draw an inventory folder into the given layout.
        """
 
        props = bpy.context.scene.b2rex_props
    
        folders = dict()
        items = dict()
        if hasattr(bpy.types.B2RexProps, 'folders'):
            folders = getattr(props, 'folders')

        if hasattr(bpy.types.B2RexProps, '_items'):
            items = getattr(props, '_items')

        if not folder_id in folders:
            return

        folder = folders[folder_id]

        session = bpy.b2rex_session
        row = layout.row()

        for i in range(indent):
            row.separator()

        if folder['Descendents'] > -1:
            name = folder['Name'] + " (" + str(folder['Descendents']) + " children)"
        elif folder['Descendents'] == 0:
            name = folder['Name'] + " (empty)"
        elif folder['Descendents'] == -1:
            name = folder['Name'] + " (? children)"

        folder_expand = "e_" +  str(folder_id).split('-')[0]
        if hasattr(bpy.types.B2RexProps, folder_expand):
            if folder['Descendents'] == 0: 
                oper = row.operator('b2rex.folder', text=name, icon='RIGHTARROW_THIN', emboss=False)
                oper.expand = False
                return
            if not getattr(props, folder_expand):
                oper = row.operator('b2rex.folder', text=name, icon='TRIA_RIGHT', emboss=False)
                oper.expand = True
            else:
                oper = row.operator('b2rex.folder', text=name, icon='TRIA_DOWN', emboss=False)
                count = 0
                for _id,_folder in folders.items():
                    if _folder['ParentID'] == folder_id:
                        count += 1
                        self.draw_folder(layout, _id, indent + 1) 
                for i_if,item in items.items():
                    if item['FolderID'] == folder_id:
                        count += 1
                        row = layout.row()
                        for i in range(indent + 1):
                            row.separator()
                        if item['InvType'] == 6:
                            row.label(text=item['Name'], icon='OBJECT_DATA')
                            row.operator('b2rex.localview', text="", icon='MUTE_IPO_OFF', emboss=False).item_id=str(item['ItemID']) 
                            row.operator('b2rex.rezobject', text="", icon='PARTICLE_DATA', emboss=False).item_id=str(item['ItemID']) 
                            row.operator('b2rex.removeinventoryitem', text="", icon='ZOOMOUT', emboss=False).item_id=str(item['ItemID']) 
                        elif item['InvType'] == 10:
                            row.label(text=item['Name'], icon='WORDWRAP_ON')
                            if not session.Scripting.find_text(item['AssetID']):
                                if "Downloading" in item:
                                    row.label(icon='FORCE_DRAG', text='')
                                else:
                                    op = row.operator('b2rex.requestasset', text="",
                                                 icon='MUTE_IPO_OFF',
                                                 emboss=False)
                                    op.item_id=str(item['ItemID'])
                                    op.asset_id=str(item['AssetID'])
                                    op.asset_type = 10 # LLSD Script
                            row.operator('b2rex.rezscript',
                                         icon='PARTICLE_DATA', text="", emboss=False).item_id = str(item['ItemID'])
                            row.operator('b2rex.removeinventoryitem', text="", icon='ZOOMOUT', emboss=False).item_id=str(item['ItemID']) 
                           
                            #row.label(text=item['Name'], icon='SCRIPT')
                        else:
                            row.label(text=item['Name'] + str(item['InvType']))
      
                
                if count < folder['Descendents'] or folder['Descendents'] == -1:
                    row = layout.row()
                    for i in range(indent + 1):
                        row.separator()
                    row.label(text="Loading...")
  
                oper.expand = False

            oper.folder_id = folder_id
        else:
            row.label(text="Loading.......")

    def _get_item(self, obj_uuid, item_uuid):
        obj = self._parent.findWithUUID(obj_uuid)
        inv = self.get_inventory(obj.opensim)
        return inv.get(item_uuid, False)

    def _reset_script(self, obj_uuid, item_uuid):
        self.simrt.ScriptReset(obj_uuid, item_uuid)

    def _delete_script(self, obj_uuid, item_uuid):
        self.simrt.RemoveTaskInventoryItem(obj_uuid, item_uuid)

    def _toggle_script_active(self, obj_uuid, item_uuid):
        founditem = self._get_item(obj_uuid, item_uuid)
        if not founditem:
            return
        newrunning = not founditem['running']
        #inv[item_uuid]['running'] = newrunning
        self.simrt.SetScriptRunning(obj_uuid, founditem['item_id'], newrunning)
        self.simrt.GetScriptRunning(obj_uuid, founditem['item_id'])

    def draw_object(self, box, editor, obj):
       if not editor.simrt:
           return
       if obj.opensim.inventory_expand:
           box.operator("b2rex.objectitems", text="object inventory", icon='TRIA_DOWN', emboss=True).obj_uuid = obj.opensim.uuid
           for _item_id, _item in obj.opensim.inventory.items():
               if not _item:
                   continue
               row = box.row()
               icon = 'WORDWRAP_ON'
               if 'running' in _item and _item['running']:
                   icon = 'SCRIPT'
               row.label(_item['name'], icon=icon)
               row = row.row()
               row.alignment = 'RIGHT'

               # delete button
               op = row.operator('b2rex.objectinventory', icon='ZOOMOUT',
                                 text='')
               op.action = '_delete_script'
               op.obj_uuid = obj.opensim.uuid
               op.item_uuid = _item_id

               if 'running' in _item:
                   enable_text = 'enable'
                   enable_icon = 'PLAY'
                   if _item['running']:
                       enable_text = 'disable'
                       enable_icon = 'PAUSE'
                       # reset button
                       op = row.operator('b2rex.objectinventory', icon='REW',
                                         text='')
                       op.action = '_reset_script'
                       op.obj_uuid = obj.opensim.uuid
                       op.item_uuid = _item_id

                   # enable / disable button
                   op = row.operator('b2rex.objectinventory', icon=enable_icon,
                                     text='')
                   op.action = '_toggle_script_active'
                   op.obj_uuid = obj.opensim.uuid
                   op.item_uuid = _item_id

                   if not editor.find_with_uuid(_item['asset_id'],
                                                bpy.data.texts, 'texts'):
                        if "Downloading" in _item:
                            row.label(icon='FORCE_DRAG', text='')
                        else:
                            op = row.operator('b2rex.requestasset', text="",
                                         icon='MUTE_IPO_OFF',
                                         emboss=False)
                            op.item_id = str(_item['item_id'])
                            op.asset_id = str(_item['asset_id'])
                            op.object_id = str(obj.opensim.uuid)
                            op.asset_type = 10 # LLSD Script

       else:
           box.operator("b2rex.objectitems", text="object inventory", icon='TRIA_RIGHT', emboss=True).obj_uuid = obj.opensim.uuid
 

