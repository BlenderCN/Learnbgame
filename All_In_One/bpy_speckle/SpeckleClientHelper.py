from speckle import SpeckleApiClient

def GetAvailableStreams(client):
    if client is None: return None
    res = client.StreamsGetAllAsync()
    if res is not None:
        streams = {}
        for i in res['resources']:
            streams[i['streamId']] = i['name']
        return streams
    return None

