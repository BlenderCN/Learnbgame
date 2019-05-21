import bpy, bmesh,os
import webbrowser
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty

from bpy_speckle.SpeckleBlenderConverter import Speckle_to_Blender, SpeckleMesh_to_Lists, Lists_to_Mesh, SpeckleMesh_to_MeshObject, MeshObject_to_SpeckleMesh, UpdateObject
from speckle import SpeckleApiClient

from bpy_speckle.SpeckleClientHelper import GetAvailableStreams
from bpy_speckle.operators import get_available_streams, initialize_speckle_client

class SpeckleViewStreamDataApi(bpy.types.Operator):
    bl_idname = "scene.speckle_view_stream_data_api"
    bl_label = "Speckle - View Stream Data (API)"
    bl_options = {'REGISTER', 'UNDO'}
    '''
    available_streams = EnumProperty(
        name="Available streams",
        description="Available streams associated with account.",
        items=get_available_streams,
        )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "available_streams")
        
    def invoke(self, context, event):
        wm = context.window_manager

        profiles = context.scene.speckle_client.load_local_profiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')
        context.scene.speckle_client.use_existing_profile(sorted(profiles.keys())[0])
        context.scene.speckle.user = sorted(profiles.keys())[0]

        stream_ids = GetAvailableStreams(context.scene.speckle_client)
        context.scene['speckle_streams'] = stream_ids

        return wm.invoke_props_dialog(self)    
    '''
    def execute(self, context):

        if len(context.scene.speckle.accounts) > 0:
            account = context.scene.speckle.accounts[context.scene.speckle.active_account]
            if len(account.streams) > 0:
                stream =account.streams[account.active_stream]         

                webbrowser.open('%s/streams/%s' % (account.server, stream.streamId), new=2)
                return {'FINISHED'}
        return {'CANCELLED'}

class SpeckleViewStreamObjectsApi(bpy.types.Operator):
    bl_idname = "scene.speckle_view_stream_objects_api"
    bl_label = "Speckle - View Stream Objects (API)"
    bl_options = {'REGISTER', 'UNDO'}

    '''
    available_streams = EnumProperty(
        name="Available streams",
        description="Available streams associated with account.",
        items=get_available_streams,
        )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "available_streams")
        
    def invoke(self, context, event):
        wm = context.window_manager

        profiles = context.scene.speckle_client.load_local_profiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')
        context.scene.speckle_client.use_existing_profile(sorted(profiles.keys())[0])
        context.scene.speckle.user = sorted(profiles.keys())[0]

        stream_ids = GetAvailableStreams(context.scene.speckle_client)
        context.scene['speckle_streams'] = stream_ids

        return wm.invoke_props_dialog(self)    
    '''
    def execute(self, context):
        if len(context.scene.speckle.accounts) > 0:
            account = context.scene.speckle.accounts[context.scene.speckle.active_account]
            if len(account.streams) > 0:
                stream =account.streams[account.active_stream]         

                webbrowser.open('%s/streams/%s/objects?omit=displayValue,base64' % (account.server, stream.streamId), new=2)
                return {'FINISHED'}
        return {'CANCELLED'}

class SpeckleDeleteStream(bpy.types.Operator):
    bl_idname = "scene.speckle_delete_stream"
    bl_label = "Speckle - Delete Stream"
    bl_options = {'REGISTER', 'UNDO'}

    available_streams = EnumProperty(
        name="Available streams",
        description="Available streams associated with account.",
        items=get_available_streams,
        )

    are_you_sure = BoolProperty(
        name="Confirm",
        default=False,
        )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "available_streams")
        col.prop(self, "are_you_sure")
        
    def invoke(self, context, event):
        wm = context.window_manager

        profiles = context.scene.speckle_client.load_local_profiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')
        context.scene.speckle_client.use_existing_profile(sorted(profiles.keys())[0])
        context.scene.speckle.user = sorted(profiles.keys())[0]

        stream_ids = GetAvailableStreams(context.scene.speckle_client)
        context.scene['speckle_streams'] = stream_ids

        return wm.invoke_props_dialog(self)    

    def execute(self, context):
        if not self.are_you_sure:
            print ("Deleting stream %s cancelled." % self.available_streams)
            return {'CANCELLED'}
        self.are_you_sure = False

        if self.available_streams == "":
            print ("Speckle: Specify stream ID.")
            return {'FINISHED'}

        if context.scene.speckle_client is None: 
            print ("SpeckleClient was not initialized...")
            return {'CANCELLED'}

        print ("Deleting %s..." % self.available_streams)
        res = context.scene.speckle_client.StreamDeleteAsync(self.available_streams)
        if res is None: return {'CANCELLED'}
        return {'FINISHED'}

class SpeckleSelectStream(bpy.types.Operator):
    bl_idname = "scene.speckle_select_stream"
    bl_label = "Speckle - Select Stream"
    bl_options = {'REGISTER', 'UNDO'}

    '''
    streamId = StringProperty(
        name="Stream ID",
        description="ID of stream to select.",
        default="",
        )
    '''

    available_streams = EnumProperty(
        name="Available streams",
        description="Available streams associated with account.",
        items=get_available_streams,
        )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "available_streams")    

    def invoke(self, context, event):
        wm = context.window_manager

        profiles = context.scene.speckle_client.load_local_profiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')

        context.scene.speckle_client.use_existing_profile(sorted(profiles.keys())[0])

        context.scene['speckle_streams'] = GetAvailableStreams(context.scene.speckle_client)

        return wm.invoke_props_dialog(self)   

    def execute(self, context):

        for o in context.scene.objects:
            if o.speckle.stream_id == self.available_streams:
                o.select = True
            else:
                o.select = False

        return {'FINISHED'}      

class SpeckleSelectOrphanObjects(bpy.types.Operator):
    bl_idname = "scene.speckle_select_orphans"
    bl_label = "Speckle - Select Orphaned Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout 

    def execute(self, context):

        profiles = context.scene.speckle_client.load_local_profiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')

        context.scene.speckle_client.use_existing_profile(sorted(profiles.keys())[0])
        context.scene['speckle_streams'] = GetAvailableStreams(context.scene.speckle_client)

        for o in context.scene.objects:
            if o.speckle.stream_id and o.speckle.stream_id not in context.scene['speckle_streams']:
                o.select = True
            else:
                o.select = False

        return {'FINISHED'}                  

class SpeckleImportStream(bpy.types.Operator):
    bl_idname = "scene.speckle_import_stream"
    bl_label = "Speckle - Import Stream"
    bl_options = {'REGISTER', 'UNDO'}

    available_streams = EnumProperty(
        name="Available streams",
        description="Available streams associated with account.",
        items=get_available_streams,
        )

    clear_stream = BoolProperty(
        name="Clear stream",
        description="Delete existing objects that identify with this stream.",
        default=True,
        )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "available_streams")
        col.prop(self, "clear_stream")
        
    def invoke(self, context, event):
        wm = context.window_manager

        profiles = context.scene.speckle_client.load_local_profiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')
        context.scene.speckle_client.use_existing_profile(sorted(profiles.keys())[0])
        context.scene.speckle.user = sorted(profiles.keys())[0]

        stream_ids = GetAvailableStreams(context.scene.speckle_client)
        context.scene['speckle_streams'] = stream_ids

        return wm.invoke_props_dialog(self)    

    def execute(self, context):

        if self.available_streams == "":
            print ("Speckle: Specify stream ID.")
            return {'FINISHED'}

        # Not too elegant. Should compare individual objectIds and update object
        # data instead of deleting every object that has the streamId.
        if self.clear_stream:
            for o in context.scene.objects:
                if o.speckle.stream_id == self.available_streams:
                    context.scene.objects.unlink(o)

        context.scene.objects.active = None

        if context.scene.speckle_client is None: 
            print ("SpeckleClient was not initialized...")
            return {'CANCELLED'}

        print (self.available_streams)
        res = context.scene.speckle_client.StreamGetObjectsAsync(self.available_streams)
        if res is None: return {'CANCELLED'}

        if 'resources' in res.keys():
            stream = res['resources']

            for resource in res['resources']:
                o = Speckle_to_Blender(resource, context.scene.speckle.scale)

                if o is None:
                    continue

                o.speckle.stream_id = self.available_streams
                o.speckle.send_or_receive = 'receive'
                o.select = True
                bpy.context.scene.objects.link(o)

        else:
            #print(SpeckleResource.to_json_pretty(res))
            pass

        context.scene.update()
        #print ("Received %i objects." % len(res.resources))
        return {'FINISHED'}

class SpeckleImportStreamRaw(bpy.types.Operator):
    bl_idname = "scene.speckle_import_stream_raw"
    bl_label = "Speckle - Import Stream Raw"
    bl_options = {'REGISTER', 'UNDO'}

    stream_id = StringProperty(
        name="Stream ID",
        description="Manually input stream ID.",
        )

    clear_stream = BoolProperty(
        name="Clear stream",
        description="Delete existing objects that identify with this stream.",
        default=True,
        )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "stream_id")
        col.prop(self, "clear_stream")
        
    def execute(self, context):

        if self.stream_id == "":
            print ("Speckle: Specify stream ID.")
            return {'FINISHED'}

        # Not too elegant. Should compare individual objectIds and update object
        # data instead of deleting every object that has the streamId.
        if self.clear_stream:
            for o in context.scene.objects:
                if o.speckle.stream_id == self.stream_id:
                    context.scene.objects.unlink(o)

        context.scene.objects.active = None

        if context.scene.speckle_client is None: 
            print ("SpeckleClient was not initialized...")
            return {'CANCELLED'}

        print (self.stream_id)
        res = context.scene.speckle_client.StreamGetObjectsAsync(self.stream_id)
        if res is None: return {'CANCELLED'}

        if 'resources' in res.keys():
            stream = res['resources']

            for resource in res['resources']:
                o = Speckle_to_Blender(resource, context.scene.speckle.scale)

                if o is None:
                    continue

                o.speckle.stream_id = self.stream_id
                o.speckle.send_or_receive = 'receive'
                o.select = True
                bpy.context.scene.objects.link(o)

        else:
            #print(SpeckleResource.to_json_pretty(res))
            pass

        context.scene.update()
        #print ("Received %i objects." % len(res.resources))
        return {'FINISHED'}

class SpeckleUpdateGlobal(bpy.types.Operator):
    bl_idname = "scene.speckle_update"
    bl_label = "Speckle - Update All"
    bl_options = {'REGISTER', 'UNDO'}

    client = None

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        label = row.label(text="Update everything.")

    def execute(self, context):

        profiles = context.scene.speckle_client.load_local_profiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')
        context.scene.speckle_client.use_existing_profile(sorted(profiles.keys())[0])
        context.scene.speckle.user = sorted(profiles.keys())[0]

        for obj in context.scene.objects:
            if obj.speckle.enabled:
                UpdateObject(context.scene.speckle_client, obj)

        context.scene.update()
        return {'FINISHED'}


class NotImplementedOperator(bpy.types.Operator):
    bl_idname = "scene.speckle_not_implemented"
    bl_label = "Speckle - Dummy"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        label = row.label(text="Not implemented.")

    def execute(self, context):

        print ("Speckle :: Not implemented.")

        context.scene.update()
        return {'FINISHED'}