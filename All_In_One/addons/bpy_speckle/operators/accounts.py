import bpy, bmesh,os
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty
from bpy_speckle.properties.scene import SpeckleUserAccountObject

from bpy_speckle.SpeckleBlenderConverter import Speckle_to_Blender, SpeckleMesh_to_Lists, Lists_to_Mesh, SpeckleMesh_to_MeshObject, MeshObject_to_SpeckleMesh, UpdateObject

from speckle import SpeckleApiClient
#from speckle import SpeckleResource

class SpeckleLoadAccounts(bpy.types.Operator):
    bl_idname = "scene.speckle_accounts_load"
    bl_label = "Speckle - Load Accounts"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        client = SpeckleApiClient()
 
        profiles = client.load_local_profiles_from_database(None)

        for p in profiles:
            #print(p)
            ua = context.scene.speckle.accounts.add()
            ua.name = p['server_name']
            ua.server=p['server'] 
            ua.email=p['email']
            ua.authToken = p['apitoken']

            client.server = ua.server
            client.session.headers.update({'Authorization': ua.authToken})

            res = client.StreamsGetAllAsync()
            streams = sorted(res['resources'], key=lambda x: x['name'], reverse=False)

            for s in streams:
                stream = ua.streams.add()
                stream.name = s['name']
                stream.streamId = s['streamId']
                if 'baseProperties' in s.keys() and s['baseProperties'] is not None:
                    #print (s['baseProperties'])
                    if 'units' in s['baseProperties'].keys():
                        stream.units = s['baseProperties']['units']

        return {'FINISHED'}


class SpeckleAddAccount(bpy.types.Operator):
    bl_idname = "scene.speckle_account_add"
    bl_label = "Speckle - Add Account"
    bl_options = {'REGISTER', 'UNDO'}

    email = StringProperty(name="Email", description="User email.", default="")
    pwd = StringProperty(name="Password", description="User password.", default="")
    server = StringProperty(name="Server", description="Server address.", default="https://hestia.speckle.works/api/v1")

    def execute(self, context):

        client = SpeckleApiClient()
        client.server = self.server

        if self.server is "":
            return {'FINISHED'}

        res = client.UserLoginAsync({"email":self.email,"password":self.pwd})
        if res is None:
            print("Failed to login to server '%s' with email '%s'" % (self.server, self.email))
            return {'CANCELLED'}

        user = res['resource']

        #print(user)

        user['server'] = self.server
        user['server_name'] = "SpeckleServer" #TODO: Find way to get official server name

        client.write_profile_to_database(user)

        bpy.ops.scene.speckle_accounts_load()

        '''
        context.scene.speckle.accounts.add(SpeckleUserAccountObject(
            name="Namerino", 
            server=self.server, 
            email=self.email, 
            authToken = res['resource']['authToken']))
        '''
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self) 

# TERMPORARY

def get_scale_length(text):
    if text is 'Meters':
        return 1.0
    elif text is 'Centimeters':
        return 0.01
    elif text is 'Millimeters':
        return 0.001
    elif text is 'Inches':
        return 0.0254
    elif text is 'Feet':
        return 0.3048
    elif text is 'Kilometers':
        return 1000.0
    else:
        return 1.0


class SpeckleImportStream2(bpy.types.Operator):
    bl_idname = "scene.speckle_import_stream2"
    bl_label = "Speckle - Import Stream"
    bl_options = {'REGISTER', 'UNDO'}   

    def execute(self, context):
        context.scene.objects.active = None

        if context.scene.speckle_client is None: 
            print ("SpeckleClient was not initialized...")
            return {'CANCELLED'}

        client = context.scene.speckle_client
        account = context.scene.speckle.accounts[context.scene.speckle.active_account]
        stream = account.streams[account.active_stream]

        # TODO: Implement scaling properly
        scale = context.scene.unit_settings.scale_length / get_scale_length(stream.units)
        
        client.server = account.server
        client.session.headers.update({'Authorization': account.authToken})

        res = context.scene.speckle_client.StreamGetObjectsAsync(stream.streamId)
        if res is None: return {'CANCELLED'}

        if 'resources' in res.keys():
            for resource in res['resources']:
                o = Speckle_to_Blender(resource, scale)

                if o is None:
                    continue

                o.speckle.stream_id = stream.streamId
                o.speckle.send_or_receive = 'receive'
                o.select = True
                bpy.context.scene.objects.link(o)

        else:
            #print(SpeckleResource.to_json_pretty(res))
            pass

        context.scene.update()
        #print ("Received %i objects." % len(res.resources))
        return {'FINISHED'}