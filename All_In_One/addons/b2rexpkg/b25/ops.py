import bpy
from bpy.props import StringProperty, PointerProperty, IntProperty

from bpy.props import StringProperty, PointerProperty, IntProperty
from bpy.props import BoolProperty, FloatProperty, CollectionProperty
from bpy.props import FloatVectorProperty, EnumProperty

import b2rexpkg

import logging

log_levels = ((str(logging.ERROR), 'Standard', 'standard level, show only errors'),
              (str(logging.CRITICAL), 'Critical', 'show only critical errors (least info)'),
              (str(logging.WARNING), 'Warning', 'show warnings or errors'),
              (str(logging.INFO), 'Info', 'show info or errors'),
              (str(logging.DEBUG), 'Debug', 'debug log level'))

def getLogLabel(level):
    level = str(level)
    loglevel = list(filter(lambda s: s[0] == level, log_levels))
    if loglevel:
        return loglevel[0][1]
    else:
        return log_levels[0][1]


class SetLogLevel(bpy.types.Operator):
    bl_idname = "b2rex.loglevel"
    bl_label = "LogLevel"
    level = EnumProperty(items=log_levels,
                         name='level',
                         default=str(logging.ERROR))

    def getLabel(self):
        return getLogLabel(self.level)

    def execute(self, context):
        if not self.level:
            self.level = logging.ERROR
        context.scene.b2rex_props.loglevel = int(self.level)
        logging.getLogger('root').setLevel(int(self.level))
        for logger in logging.getLogger('root').manager.loggerDict.values():
            logger.setLevel(int(self.level))
        return {'FINISHED'}

class AddConnection(bpy.types.Operator):
    bl_idname = "b2rex.addconnection"
    bl_label = "Add"
    bl_description = "Perform an action on a connection"
    action = StringProperty(name="action",default='add')
    def draw(self, context):
        self.bl_description = self.action+" the current connection"
        self.description = self.action+" the current connection"

    def execute(self, context):
        if self.action == 'add':
            bpy.b2rex_session.add_connection(context)
        elif self.action == 'edit':
            bpy.b2rex_session.edit_connection(context)
        elif self.action == 'cancel':
            bpy.b2rex_session.cancel_edit_connection(context)
        elif self.action == 'create':
            bpy.b2rex_session.create_connection(context)
        elif self.action == 'delete':
            bpy.b2rex_session.delete_connection(context)

        return {'FINISHED'}

class B2RexStartGame(bpy.types.Operator):
    bl_idname = "b2rex.game_start"
    bl_label = "Start Game"
    def execute(self, context):
        bpy.b2rex_session.Game.start_game(context)
        return {'FINISHED'}


class UploadText(bpy.types.Operator):
    bl_idname = "b2rex.upload_text"
    bl_label = "Upload to Sim"
    text = StringProperty(name="text",default='')

    def execute(self, context):
        bpy.b2rex_session.Scripting.upload(self.text)
        return {'FINISHED'}

class RequestAsset(bpy.types.Operator):
    bl_idname = "b2rex.requestasset"
    bl_label = "request asset"
    item_id = StringProperty(name="item_id",default='')
    asset_id = StringProperty(name="asset_id",default='')
    object_id = StringProperty(default='')
    asset_type = IntProperty(name="asset_type",default=0)

    def execute(self, context):
        session = bpy.b2rex_session
        if self.item_id:
            if self.object_id:
                ob = session.findWithUUID(self.object_id)
                ob.opensim.inventory[self.item_id]['Downloading'] = True
            else:
                session.Inventory[self.item_id]['Downloading'] = True
        session.Asset.downloadAssetDefault(self.asset_id,
                                                     self.asset_type)
        return {'FINISHED'}


class Connect(bpy.types.Operator):
    bl_idname = "b2rex.connect"
    bl_label = "connect"

    def execute(self, context):
        bpy.b2rex_session.onconnect(context)
        return {'FINISHED'}

class Section(bpy.types.Operator):
    bl_idname = "b2rex.section"
    bl_label = "section"
    section = StringProperty()
    def execute(self, context):
        getattr(bpy.b2rex_session, self.section)._expand ^= 1
        return {'FINISHED'}


class Redraw(bpy.types.Operator):
    bl_idname = "b2rex.redraw"
    bl_label = "redraw"

    def invoke(self, context, event):
        for area in context.screen.areas:
            if area.type == 'INFO':
                area.tag_redraw()
        return {'RUNNING_MODAL'}
    def check(self, context):
        return True
    def execute(self, context):
        if not context.screen:
            print("not redrawing")
            return {'FINISHED'}
        for scene in bpy.data.scenes:
            # what is the best way to trigger a redraw?
            # only the stuff below the return doesnt seem
            # to always work.
            scene.name = scene.name
            return {'FINISHED'}
        return
        if context and context.screen:
            for area in context.screen.areas:
                if area.type in ['INFO', 'VIEW_3D']:
                    area.tag_redraw()
            return {'FINISHED'}
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type == 'INFO':
                    area.tag_redraw()
        return {'FINISHED'}



class ToggleRt(bpy.types.Operator):
    bl_idname = "b2rex.toggle_rt"
    bl_label = "RT"

    def execute(self, context):
        bpy.b2rex_session.onToggleRt(context)
        return {'FINISHED'}

class Export(bpy.types.Operator):
    bl_idname = "b2rex.export"
    bl_label = "export"

    def execute(self, context):
        bpy.b2rex_session.onExport(context)
        return {'FINISHED'}

class RexExport(bpy.types.Operator):
    bl_idname = "b2rex.rexexport"
    bl_label = "rexexport"

    action = bpy.props.StringProperty()
    def execute(self, context):
        getattr(bpy.b2rex_session.RexExport, self.action)(context)
        return {'FINISHED'}

class RexExport(bpy.types.Operator):
    bl_idname = "b2rex.reload_components"
    bl_label = "Reload Components"

    def execute(self, context):
        bpy.b2rex_session.RexLogic.reload_components(context)
        return {'FINISHED'}



class ProcessQueue(bpy.types.Operator):
    bl_idname = "b2rex.processqueue"
    bl_label = "processqueue"

    def execute(self, context):
        bpy.b2rex_session.onProcessQueue(context)
        return {'FINISHED'}

class GenPrim(bpy.types.Operator):
    bl_idname = "b2rex.genprim"
    bl_label = "Generate Prim"

    def execute(self, context):
        bpy.b2rex_session.Prims.generate(context)
        return {'FINISHED'}


class Delete(bpy.types.Operator):
    bl_idname = "b2rex.delete"
    bl_label = "delete"

    def execute(self, context):
        bpy.b2rex_session.onDelete(context)
        return {'FINISHED'}


class Upload(bpy.types.Operator):
    bl_idname = "b2rex.upload"
    bl_label = "upload"

    def execute(self, context):
        bpy.b2rex_session.onUpload(context)
        return {'FINISHED'}

class ExportUpload(bpy.types.Operator):
    bl_idname = "b2rex.exportupload"
    bl_label = "export+upload"

    def execute(self, context):
        bpy.b2rex_session.onExportUpload(context)
        return {'FINISHED'}

class Import(bpy.types.Operator):
    bl_idname = "b2rex.import"
    bl_label = "import"

    def execute(self, context):
        print('exec import')
        bpy.b2rex_session.onImport(context)
        return {'FINISHED'}

class Check(bpy.types.Operator):
    bl_idname = "b2rex.check"
    bl_label = "Check"

    def execute(self, context):
        bpy.b2rex_session.onCheck(context)
        return {'FINISHED'}

class Sync(bpy.types.Operator):
    bl_idname = "b2rex.sync"
    bl_label = "Sync"

    def execute(self, context):
        bpy.b2rex_session.onSync(context)
        return {'FINISHED'}

class Settings(bpy.types.Operator):
    bl_idname = "b2rex.settings"
    bl_label = "Settings"

    def execute(self, context):
        bpy.b2rex_session.onSettings(context)
        return {'FINISHED'}
        
class SetMaskOn(bpy.types.Operator):
    bl_idname = "b2rex.setmaskon"
    bl_label = "SetMaskOn"
    mask = bpy.props.IntProperty(name="Mask")
    def execute(self, context):
        simrt = bpy.b2rex_session.simrt
        for obj in context.selected_objects:
            simrt.UpdatePermissions(obj.opensim.uuid, self.mask, 1)
        
        return {'FINISHED'}
        
class SetMaskOff(bpy.types.Operator):
    bl_idname = "b2rex.setmaskoff"
    bl_label = "SetMaskOff"
    mask = bpy.props.IntProperty(name="Mask")

    def execute(self, context):
        simrt = bpy.b2rex_session.simrt
        for obj in context.selected_objects:
            simrt.UpdatePermissions(obj.opensim.uuid, self.mask, 0)
 
        return {'FINISHED'}
   

class FolderStatus(bpy.types.Operator):
    bl_idname = "b2rex.folder"
    bl_label = "Folder"
    expand = bpy.props.BoolProperty(name="Expand")
    folder_id = bpy.props.StringProperty(name="Folder ID")

    def execute(self, context):
        setattr(context.scene.b2rex_props, "e_" + self.folder_id.split('-')[0], self.expand)
        if self.expand == True:
            bpy.b2rex_session.simrt.FetchInventoryDescendents(self.folder_id)

        return {'FINISHED'}

class DeRezObject(bpy.types.Operator):
    bl_idname = "b2rex.derezobject"
    bl_label = "Take item to inventory"

    def execute(self, context):
        bpy.b2rex_session.onDeRezObject()
        return {'FINISHED'}

class RezObject(bpy.types.Operator):
    bl_idname = "b2rex.rezobject"
    bl_label = "Take item from inventory"

    item_id = StringProperty(name="item_id")

    def execute(self, context):
        bpy.b2rex_session.onRezObject(self.item_id)
        return {'FINISHED'}

class RemoveInventoryItem(bpy.types.Operator):
    bl_idname = "b2rex.removeinventoryitem"
    bl_label = "Remove item from inventory"

    item_id = StringProperty(name="item_id")

    def execute(self, context):
        props = context.scene.b2rex_props

        items = getattr(props, "_items")
        folders = getattr(props, "folders")

        item =  items[self.item_id] 
        folder_id = item['FolderID']

        if folder_id in folders:
            folders[folder_id]['Descendents'] -= 1

        if self.item_id in items:
            del items[self.item_id]
        else:
            return {'FINISHED'}
        
        bpy.b2rex_session.onRemoveInventoryItem(self.item_id)
        return {'FINISHED'}

class LocalView(bpy.types.Operator):
    bl_idname = "b2rex.localview"
    bl_label = "Item local view"

    item_id = StringProperty(name="item_id")

    def execute(self, context):
        obj = bpy.b2rex_session.findWithUUID(self.item_id)
        if obj:
            bpy.ops.object.select_all(action="DESELECT")
            bpy.ops.object.select_name(name=obj.name, extend=False)
        
        #bpy.ops.view3d.localview()
    
        return {'FINISHED'}

class ToggleImportTerrain(bpy.types.Operator):
    bl_idname = "b2rex.toggleimportterrain"
    bl_label = "Toggle import terrain"

    def execute(self, context):
        
        session = bpy.b2rex_session
        context.scene.b2rex_props.importTerrain ^=  True
        if context.scene.b2rex_props.importTerrain:
            session.registerCommand('LayerData', session.processLayerData)
            session.registerCommand('LayerDataDecoded', session.processLayerDataDecoded)
        else:
            session.unregisterCommand('LayerData')
            session.unregisterCommand('LayerDataDecoded')
    
        return {'FINISHED'}

class ToggleImportTextures(bpy.types.Operator):
    bl_idname = "b2rex.toggleimporttextures"
    bl_label = "Toggle import textures"

    def execute(self, context):
        
        session = bpy.b2rex_session
        context.scene.b2rex_props.importTextures ^=  True
        if context.scene.b2rex_props.importTerrain:
            session.registerCommand('texturearrived', session.processTextureArrived)
        else:
            session.unregisterCommand('texturearrived')
    
        return {'FINISHED'}

class ToggleSafeMode(bpy.types.Operator):
    bl_idname = "b2rex.toggle_safe_mode"
    bl_label = "Toggle safe mode"

    def execute(self, context):
        b2rexpkg.safe_mode ^= True
        return {'FINISHED'}

class ObjectInventoryOperator(bpy.types.Operator):
    bl_idname = "b2rex.objectinventory"
    bl_label = "Open object inventory"
    obj_uuid = StringProperty()
    item_uuid = StringProperty()
    action = StringProperty(name="")
    def execute(self, context):
        getattr(bpy.b2rex_session.Inventory, self.action)(self.obj_uuid,
                                                          self.item_uuid)
        return {'FINISHED'}


class ObjectItems(bpy.types.Operator):
    bl_idname = "b2rex.objectitems"
    bl_label = "Open object inventory"
    obj_uuid = StringProperty(name="obj_uuid")
    def execute(self, context):
        for obj in context.selected_objects:
            obj.opensim.toggle_inventory_expand 
            if obj.opensim.inventory_expand:
                bpy.b2rex_session.simrt.RequestTaskInventory(obj.opensim.uuid)

        return {'FINISHED'}

class RezScript(bpy.types.Operator):
    bl_idname = "b2rex.rezscript"
    bl_label = "Add script to object"
    item_id = StringProperty(name="item_id")

    def execute(self, context):
        simrt = bpy.b2rex_session.simrt
        for obj in context.selected_objects:
            simrt.RezScript(obj.opensim.uuid, self.item_id)
        
        return {'FINISHED'}

