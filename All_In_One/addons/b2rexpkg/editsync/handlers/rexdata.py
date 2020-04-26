"""
 RexDataModule: Manages RexData and mesh creation.
"""

import logging
from .base import SyncModule

import bpy

from b2rexpkg.tools.simtypes import AssetType, ZERO_UUID_STR, RexDrawType

logger = logging.getLogger('b2rex.RexDataModule')

class RexDataModule(SyncModule):
    rexobjects = []
    def register(self, parent):
        """
        Register this module with the editor
        """
        parent.registerCommand('RexPrimData', self.processRexPrimDataCommand)
        parent.registerCommand('mesharrived', self.processMeshArrived)

    def unregister(self, parent):
        """
        Unregister this module from the editor
        """
        parent.unregisterCommand('RexPrimData')
        parent.unregisterCommand('mesharrived')

    def processRexPrimDataCommand(self, objId, pars):
        """
        RexPrimData arrived from the simulator.
        """
        editor = self._parent
        editor.stats[3] += 1
        meshId = pars["RexMeshUUID"]
        obj = editor.findWithUUID(objId)
        if pars["drawType"] == RexDrawType.Mesh:
            self.rexobjects.append(objId)
        if obj or not meshId:
            if obj:
                logger.warning(("Object already created", obj, meshId, objId))
            # XXX we dont update mesh for the moment
            return
        mesh = editor.find_with_uuid(meshId, bpy.data.meshes, "meshes")
        urls = []
        # 4 is sound and more are materials
        if 'urls' in pars and len(pars['urls']) > 3:
            urls = pars['urls']
        if mesh:
            editor.Object.createObjectWithMesh(mesh, objId, meshId)
            editor.queueRedraw()
        else:
            materials = []
            if "Materials" in pars:
                materials = pars["Materials"]
                for index, matId, asset_type in materials:
                    if not matId == ZERO_UUID_STR:
                        if asset_type == AssetType.OgreMaterial:
                            if urls:
                                asset_url = urls[5+index]
                                self.addDownload(asset_url, cb, pars, extra_main=main)
                            else:
                                editor.Asset.downloadAsset(matId, asset_type,
                                               editor.materialArrived, (objId,
                                                                         meshId,
                                                                         matId,
                                                                         asset_type,
                                                                         index))
                        elif asset_type == 0:
                            if urls:
                                asset_url = urls[5+index]
                                self.addDownload(asset_url, cb, pars, extra_main=main)
                            else:
                                editor.Asset.downloadAsset(matId, asset_type,
                                               editor.materialTextureArrived, (objId,
                                                                         meshId,
                                                                         matId,
                                                                         asset_type,
                                                                         index))
                        else:
                            logger.warning("unhandled material of type " + str(asset_type))
            if meshId and not meshId == ZERO_UUID_STR:
                asset_type = pars["drawType"]
                if asset_type == RexDrawType.Mesh:
                    if urls:
                        asset_url = urls[0]
                        todownload = self.addDownload(asset_url, cb, pars, extra_main=main)
                    else:
                        todownload = editor.Asset.downloadAsset(meshId, AssetType.OgreMesh,
                                    self.meshArrived, 
                                     (objId, meshId, materials),
                                            main=self.doMeshDownloadTranscode)
                    if not todownload:
                            editor.add_mesh_callback(meshId,
                                               editor.Object.createObjectWithMesh,
                                               objId,
                                               meshId, materials)
                else:
                    logger.warning("unhandled rexdata of type " + str(asset_type))

    def doMeshDownloadTranscode(self, pars):
        """
        Function for the transcoding thread to convert and parse assets.
        """
        http_url, pars, data = pars
        assetName = pars[1] # we dont get the name here
        assetId = pars[1]
        return self._parent.create_mesh_frombinary(assetId, assetName, data)

    def meshArrived(self, mesh, objId, meshId, materials):
        """
        A mesh arrived from a thread. We queue it into the command processor.
        """
        self._parent.command_queue.append(["mesharrived", mesh, objId, meshId, materials])

    def processMeshArrived(self, mesh, objId, meshId, materials):
        """
        A mesh arrived and is fully decoded and parsed. Now we need to create
        the editor mesh object and finish object creation.
        """
        editor = self._parent
        editor.stats[4] += 1
        obj = editor.findWithUUID(objId)
        if obj:
            return
        new_mesh = editor.create_mesh_fromomesh(meshId, "opensim", mesh, materials)
        if new_mesh:
            editor.Object.createObjectWithMesh(new_mesh, str(objId), meshId, materials)
            editor.trigger_mesh_callbacks(meshId, new_mesh)
        else:
            print("No new mesh with processMeshArrived")

