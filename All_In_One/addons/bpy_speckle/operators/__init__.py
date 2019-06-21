import bpy
from speckle import SpeckleApiClient

def initialize_speckle_client(scene):
    if 'speckle_client' not in scene:
        #scene['speckle_client'] = SpeckleClient()
        profiles = context.scene.speckle_client.LoadProfiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')
        context.scene.speckle_client.UseExistingProfile(sorted(profiles.keys())[0])

def get_available_streams(self, context):
    if 'speckle_streams' in context.scene.keys():
        streams = context.scene['speckle_streams']
        if streams is not None:
            return [(x, "%s (%s)" % (streams[x], x), "") for x in streams.keys()]