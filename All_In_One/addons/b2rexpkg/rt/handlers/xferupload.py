"""
 UDP xfer upload manager
"""

from array import array
import base64

from pyogp.lib.base.datatypes import UUID
from pyogp.lib.base.message.message import Message, Block

from .base import Handler
try:
    from ..tools import uuid_combine
except:
    from b2rexpkg.rt.tools import uuid_combine

class XferUploader(object):
    def __init__(self, data, cb, tr_uuid):
        self.cb = cb
        self.data = data
        self.tr_uuid = tr_uuid
        self.total = len(data)/1024
        self.first = True
        self.nseq = 1
        self.xferID = None
    def getNextPacket(self):
        if not len(self.data):
            return
        if len(self.data) <= 1024:
            nextdata = self.data
            self.data = b''
            ongoing = 0x80000000 # last packet
        else:
            nextdata = self.data[:1024]
            self.data = self.data[1024:]
            ongoing = 0x00000000
        if self.first:
            nextdata = b'\0\0\0\0' + nextdata
            self.first = False

        packet = Message('SendXferPacket',
                        Block('XferID',
                                ID = self.xferID,
                                Packet = ongoing|self.nseq),
                         # first packet needs 4 bytes padding if we dont
                         # bootstrap some data ???
                        Block('DataPacket', Data=array('c',nextdata)))
        self.nseq += 1
        return packet

class XferUploadManager(Handler):
    def __init__(self, parent):
        Handler.__init__(self, parent)
        self._uploaders = {}

    def onAgentConnected(self, agent):
        self._agent = agent

    def onRegionConnect(self, region):
        res = region.message_handler.register("AssetUploadComplete")
        res.subscribe(self.onAssetUploadComplete)
        res = region.message_handler.register("ConfirmXferPacket")
        res.subscribe(self.onConfirmXferPacket)
        res = region.message_handler.register("RequestXfer")
        res.subscribe(self.onRequestXfer)

    def uploadAsset(self, assetType, data, cb):
        """
        Request an asset upload from the simulator
        """
        tr_uuid = UUID()
        tr_uuid.random()
        init_data = None
        assetID = uuid_combine(tr_uuid, self._agent.secure_session_id)

        #if len(data) < 1024:
        #    init_data = array('c', data)
        #else:
        newuploader = XferUploader(data, cb, tr_uuid)
        self._uploaders[str(assetID)] = newuploader

        self._agent.asset_manager.upload_asset(tr_uuid,
                                               assetType,
                                               False, # tempfile
                                               False, # storelocal
                                               init_data) # asset_data
        return  assetID

    def processUploadAsset(self, assetID, assetType, b64data):
        def finish(newAssetID, trID):
            self.out_queue.put(["AssetUploadFinished", str(newAssetID), assetID,
                               str(trID)])
        data = base64.urlsafe_b64decode(b64data.encode('ascii'))
        self.uploadAsset(assetType, data, finish)

    def onRequestXfer(self, packet):
        """
        Confirmation for our asset upload. Now send data.
        """
        xfer_id = packet["XferID"][0]["ID"]
        vfile_id = packet["XferID"][0]["VFileID"] # key and uuid of new asset
        if str(vfile_id) in self._uploaders:
            uploader = self._uploaders[str(vfile_id)]
            self._uploaders[xfer_id] = uploader
            uploader.xferID = xfer_id
            packet = uploader.getNextPacket()
            self._agent.region.enqueue_message(packet)
        else:
            print("NO UPLOAD FOR TRANSFER REQUEST!!", vfile_id,
                  self._uploaders.keys())

    def onConfirmXferPacket(self, packet):
        """
        Confirmation for one of our upload packets.
        """
        xfer_id = packet["XferID"][0]["ID"]
        if xfer_id in self._uploaders:
            uploader = self._uploaders[xfer_id]
            print("ConfirmXferPacket", packet["XferID"][0]["Packet"],
                  uploader.total)
            packet = uploader.getNextPacket()
            if packet:
                self._agent.region.enqueue_message(packet)

    def onAssetUploadComplete(self, packet):
        """
        Confirmation for completion of the asset upload.
        """
        assetID = packet['AssetBlock'][0]['UUID']
        if str(assetID) in self._uploaders:
            print("AssetUploadComplete Go On", assetID)
            uploader = self._uploaders[str(assetID)]
            xferID = uploader.xferID
            uploader.cb(assetID, uploader.tr_uuid)
            del self._uploaders[xferID]
            del self._uploaders[str(assetID)]
        else:
            print("NO UPLOAD FOR ASSET UPLOAD COMPLETE!!", assetID,
                  self._uploaders.keys())


