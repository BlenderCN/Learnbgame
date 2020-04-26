"""
 AssetModule. Allows to download assets and provides a callback.
 Requires the caps functionality, but can download assets both over
 lludp or http using GetTexture cap.
"""

import base64

from .base import SyncModule

import bpy

class AssetModule(SyncModule):
    _requested_llassets = {}
    _exporttasks = {}
    _asset_constructors = {}
    def register(self, parent):
        """
        Register this module with the editor
        """
        parent.registerCommand('AssetArrived', self.processAssetArrived)
        parent.registerCommand('AssetUploadFinished',
                               self.processAssetUploadFinished)


    def unregister(self, parent):
        """
        Unregister this module from the editor
        """
        parent.unregisterCommand('AssetArrived')
        parent.unregisterCommand('AssetUploadFinished')

    def upload(self, assetID, assetType, data, cb=None):
        encoded = base64.urlsafe_b64encode(data).decode('ascii')

        if cb and assetID:
            self._exporttasks[assetID] = cb

        self.simrt.UploadAsset(assetID, assetType, encoded)

    def processAssetUploadFinished(self, newAssetID, assetID, trID):
        print("processAssetUploadFinished")
        if assetID in self._exporttasks:
            self._exporttasks[assetID](assetID, newAssetID, trID)
            del self._exporttasks[assetID]

    def processAssetArrived(self, assetId, b64data):
        """
        The data for an asset has arrived from the sim.
        """
        data = base64.urlsafe_b64decode(b64data.encode('ascii'))
        cb, cb_pars, main = self._requested_llassets['lludp:'+assetId]
        def _cb(request, result):
            if 'lludp:'+assetId in self._requested_llassets:
                cb(result, *cb_pars)
            else:
                print("asset arrived but no callback! "+assetId)
        if main:
            self.workpool.addRequest(main,
                                 [[assetId, cb_pars, data]],
                                 _cb,
                                 self._parent.default_error_db)
        else:
            cb(data, *cb_pars)

    def registerAssetType(self, assetType, assetConstructor):
        self._asset_constructors[assetType] = assetConstructor

    def _assetArrived(self, data, assetId, assetType):
        print("Asset arrived")
        if assetType in self._asset_constructors:
            self._asset_constructors[assetType](assetId, assetType, data)

    def downloadAssetDefault(self, assetId, assetType):
        print("Downloading Asset", assetId, assetType)
        self.downloadAsset(assetId, assetType, self._assetArrived,
                                (assetId, assetType))

    def downloadAsset(self, assetId, assetType, cb, pars=(), main=None):
        """
        Download the given asset by uuid and assetType. Will call the provided
        callback cb with the expanded parameters pars.

        If the function main is provided it will be called on a thread before
        calling the callback.

        Returns False if the asset is already downloading.

        This function uses either GetTexture caps or lludp.
        """
        if "GetTexture" in self._parent.caps:
            asset_url = self._parent.caps["GetTexture"] + "?texture_id=" + assetId
            return self._parent.addDownload(asset_url, cb, pars, extra_main=main)
        else:

            if 'lludp:'+assetId in self._requested_llassets:
                return False
            self._requested_llassets['lludp:'+assetId] = (cb, pars, main)
            self.simrt.AssetRequest(assetId, assetType)
            return True


