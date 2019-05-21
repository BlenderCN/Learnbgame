import bpy, bmesh,os
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty

from bpy_speckle.SpeckleBlenderConverter import SpeckleMesh_to_Lists, Lists_to_Mesh, SpeckleMesh_to_MeshObject, MeshObject_to_SpeckleMesh, UpdateObject, UpdateStream
from speckle import SpeckleApiClient
#from speckle import SpeckleResource

from ..SpeckleClientHelper import GetAvailableStreams
from ..operators import get_available_streams, initialize_speckle_client

class SpeckleUpdateObject(bpy.types.Operator):
    bl_idname = "object.speckle_update"
    bl_label = "Speckle - Update Object"
    bl_options = {'REGISTER', 'UNDO'}

    client = None

    def execute(self, context):
        client = context.scene.speckle_client
        account = context.scene.speckle.accounts[context.scene.speckle.active_account]
        stream =account.streams[account.active_stream]

        client.server = account.server
        client.session.headers.update({'Authorization': account.authToken})   

        '''
        # This is the easy way, but it seems that we need to delete the existing object
        # and create a new one for the GH client to see any changes - it only looks for 
        # new _id values

        UpdateObject(context.scene.speckle_client, context.object)
        UpdateStream(context.scene.speckle_client, context.object.speckle.stream_id)
        
        context.scene.update()

        return {'FINISHED'}
        '''

        # This is the longer way - object updates delete the existing object on the server, upload a new one,
        # and patch the stream with new objectId
        
        active = context.active_object
        if active is not None:
            if active.speckle.enabled:
                if active.speckle.send_or_receive == "send" and active.speckle.stream_id:
                    sm = MeshObject_to_SpeckleMesh(active, 1 / context.scene.speckle.scale)

                    res = client.ObjectCreateAsync([sm])
                    new_id = res['resources'][0]['_id']

                    res = client.StreamGetAsync(active.speckle.stream_id)
                    if res is None:
                        print ("Getting stream failed.")
                        return {'CANCELLED'}

                    stream = res['resource']

                    for o in stream['objects']:
                        if o['_id'] == active.speckle.object_id:
                            o['_id'] = new_id
                            break

                    res = client.StreamUpdateAsync(active.speckle.stream_id, {'objects': stream['objects']})
                    res = client.ObjectDeleteAsync(active.speckle.object_id)
                    active.speckle.object_id = new_id

                    if res == None: return {'CANCELLED'}
            return {'FINISHED'}
        return {'CANCELLED'}            


class SpeckleResetObject(bpy.types.Operator):
    bl_idname = "object.speckle_reset"
    bl_label = "Speckle - Reset Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        context.object.speckle.send_or_receive = "send"
        context.object.speckle.stream_id = ""
        context.object.speckle.object_id = ""
        context.object.speckle.enabled = False
        context.scene.update()

        return {'FINISHED'}

class SpeckleDeleteObject(bpy.types.Operator):
    bl_idname = "object.speckle_delete"
    bl_label = "Speckle - Delete Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active = context.object
        if active.speckle.enabled:
            res = context.scene.speckle_client.StreamGetAsync(active.speckle.stream_id)
            existing = [x for x in res['resource']['objects'] if x['_id'] == active.speckle.object_id]
            if existing == None:
                return {'CANCELLED'}
            #print("Existing: %s" % SpeckleResource.to_json_pretty(existing))
            new_objects = [x for x in res['resource']['objects'] if x['_id'] != active.speckle.object_id]
            #print (SpeckleResource.to_json_pretty(new_objects))

            res = context.scene.speckle_client.GetLayers(active.speckle.stream_id)
            new_layers = res['resource']['layers']
            new_layers[-1]['objectCount'] = new_layers[-1]['objectCount'] - 1
            new_layers[-1]['topology'] = "0-%s" % new_layers[-1]['objectCount']

            res = context.scene.speckle_client.StreamUpdateAsync({"objects":new_objects, "layers":new_layers}, active.speckle.stream_id)
            res = context.scene.speckle_client.ObjectDeleteAsync(active.speckle.object_id)

            active.speckle.send_or_receive = "send"
            active.speckle.stream_id = ""
            active.speckle.object_id = ""
            active.speckle.enabled = False
            context.scene.update()

        return {'FINISHED'}        

class SpeckleUploadObject(bpy.types.Operator):
    bl_idname = "object.speckle_upload_object"
    bl_label = "Speckle - Upload Object"
    bl_options = {'REGISTER', 'UNDO'}

    '''
    available_streams = EnumProperty(
        name="Available streams",
        description="Available streams associated with account.",
        items=get_available_streams,
        )
    '''

    '''
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "available_streams")

    def invoke(self, context, event):
        wm = context.window_manager

        profiles = context.scene.speckle_client.load_local_profiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')
        context.scene.speckle_client.use_existing_profile(sorted(profiles.keys())[0])

        stream_ids = GetAvailableStreams(context.scene.speckle_client)
        context.scene['speckle_streams'] = stream_ids

        return wm.invoke_props_dialog(self)
    '''

    def execute(self, context):
        '''
        if self.available_streams == "":
            print ("Speckle: Specify stream ID.")
            return {'FINISHED'} 
        '''        

        active = context.active_object
        if active is not None:
            # If active object is mesh
            sm = MeshObject_to_SpeckleMesh(active, 1 / context.scene.speckle.scale)

            del sm['transform']
            del sm['properties']

            client = context.scene.speckle_client
            account = context.scene.speckle.accounts[context.scene.speckle.active_account]
            stream =account.streams[account.active_stream]

            client.server = account.server
            client.session.headers.update({'Authorization': account.authToken})   

            print(stream.name + "    " + stream.streamId)         

            print("Creating object...")
            res = client.ObjectCreateAsync([sm])
            if res == None: return {'CANCELLED'}

            sm['_id'] = res['resources'][0]['_id']
            pl = {'type':'Placeholder', '_id':res['resources'][0]['_id']}

            # Get list of existing objects in stream and append new object to list
            print("Fetching stream...")            
            res = client.StreamGetAsync(stream.streamId)
            if res is None: return {'CANCELLED'}

            objects = [x for x in res['resource']['objects']]
            N_current = len(objects)
            objects.append(pl)

            '''
            res = client.StreamGetAsync(stream.streamId, "fields=layers")
            if res is None: return {'CANCELLED'}
            '''

            layers = res['resource']['layers']
            new_layers = []
            
            if layers is None or len(layers) < 1:
                layer = {}
                layer['name'] = "Blender"
                layer['guid'] = ""
                layer['orderIndex'] = 0
                layer['startIndex'] = 0
                layer['objectCount'] = len(objects)
                layer['topology'] = "0-%s" % len(objects)
                new_layers.append(layer)
            else:
                new_layers = [x for x in layers]
                N = new_layers[-1]['objectCount']
                new_layers[-1]['objectCount'] = N + 1
                new_layers[-1]['topology'] = "0-%s" % (N + 1)

            streamUpdate = {}
            streamUpdate['objects'] = objects
            streamUpdate['layers'] = new_layers

            print("Updating: %s" % stream.streamId)
            #print(speckle.jdumps(streamUpdate))

            print("Updating stream...")
            res = client.StreamUpdateAsync(stream.streamId, streamUpdate)

            active.speckle.enabled = True
            active.speckle.object_id = sm['_id']
            active.speckle.stream_id = stream.streamId
            active.speckle.send_or_receive = 'receive'

            context.scene.update()
            print("Done.")

        return {'FINISHED'}    

class SpeckleUploadObjectRaw(bpy.types.Operator):
    bl_idname = "object.speckle_upload_object_raw"
    bl_label = "Speckle - Upload Object Raw"
    bl_options = {'REGISTER', 'UNDO'}

    stream_id = StringProperty(
        name="Stream ID",
        description="Manually input stream ID.",
        )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "stream_id")

    def invoke(self, context, event):
        wm = context.window_manager

        profiles = context.scene.speckle_client.load_local_profiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')
        context.scene.speckle_client.use_existing_profiles(sorted(profiles.keys())[0])

        return wm.invoke_props_dialog(self)         


    def execute(self, context):

        if self.stream_id == "":
            print ("Speckle: Specify stream ID.")
            return {'FINISHED'}         

        active = context.active_object
        if active is not None:
            # If active object is mesh
            sm = MeshObject_to_SpeckleMesh(active, 1 / context.scene.speckle.scale)

            context.scene.speckle_client.verbose = True
            res = context.scene.speckle_client.ObjectCreateAsync([sm])
            if res == None: return {'CANCELLED'}

            sm._id = res['resources'][0]['_id']
            pl = {'type':'Placeholder', '_id':res['resources'][0]['_id']}



            # Get list of existing objects in stream and append new object to list
            res = context.scene.speckle_client.StreamGetAsync(self.stream_id)
            if res is None: return {'CANCELLED'}

            #print(SpeckleResource.to_json_pretty(res))

            stream_name = self.stream_id
            objects = [x for x in res['resource']['objects']]
            N_current = len(objects)
            objects.append(pl)

            #res = context.scene.speckle_client.GetStreamAsync(self.stream_id, "fields=layers")
            #if res is None: return {'CANCELLED'}
            #print (res)

            #print(SpeckleResource.to_json_pretty(res))

            layers = res['resource']['layers']
            new_layers = []
            
            if layers is None or len(layers) < 1:
                layer = {}
                layer['name'] = "Blender"
                layer['guid'] = ""
                layer['orderIndex'] = 0
                layer['startIndex'] = 0
                layer['objectCount'] = len(objects)
                layer['topology'] = "0-%s" % len(objects)
                new_layers.append(layer)
            else:
                new_layers = [x for x in layers]
                N = new_layers[-1]['objectCount']
                new_layers[-1]['objectCount'] = N + 1
                new_layers[-1]['topology'] = "0-%s" % (N + 1)

            stream = {}
            stream['objects'] = objects
            stream['layers'] = new_layers

            print("Updating: %s" % self.stream_id)
            #print(SpeckleResource.to_json_pretty(stream))
            res = context.scene.speckle_client.StreamUpdateAsync(stream, self.stream_id)

            active.speckle.enabled = True
            active.speckle.object_id = sm._id
            active.speckle.stream_id = self.stream_id
            active.speckle.send_or_receive = 'receive'

            context.scene.update()

        return {'FINISHED'}        