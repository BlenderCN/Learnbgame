"""
 TerrainModule: Manages LayerData and editor terrain objects.
"""

import sys
import base64
from .base import SyncModule

from b2rexpkg.terrainsync import TerrainSync
from b2rexpkg.tools.terraindecoder import TerrainDecoder, TerrainEncoder

import bpy

class TerrainModule(SyncModule):
    # Terrain
    terrain = None
    def register(self, parent):
        """
        Register this module with the editor
        """
        parent.registerCommand('LayerData', self.processLayerData)
        parent.registerCommand('LayerDataDecoded', self.processLayerDataDecoded)

    def unregister(self, parent):
        """
        Unregister this module from the editor
        """
        parent.unregisterCommand('LayerData')
        parent.unregisterCommand('LayerDataDecoded')

    def onToggleRt(self, enabled):
        """
        Real time agent has been enabled. the first time we need to create the
        TerrainSync object for the region and get a few pointers.
        """
        if not self.terrain:
            self._props = self._parent.exportSettings
            self.terrain = TerrainSync(self._parent, self._props.terrainLOD)
            self.workpool = self._parent.workpool
        if enabled:
            self.simrt = self._parent.simrt
        else:
            self.simrt = None

    def check(self, starttime, timebudget):
        """
        Callback for the check stage of command processing. We need to see if
        the terrain came back from edit mode and scan for changes to send.
        """
        if not sys.version_info[0] == 3:
            return
        updated_blocks = []

        if bpy.context.mode == 'EDIT_MESH' or bpy.context.mode == 'SCULPT':
            if bpy.context.scene.objects.active:
                if bpy.context.scene.objects.active.name == 'terrain':
                    self.terrain.set_dirty()
        elif self.terrain.is_dirty():
            while self.terrain.is_dirty() and time.time() - starttime < timebudget:
                updated_blocks.extend(self.terrain.check())

        if updated_blocks:
            self.sendTerrainBlocks(updated_blocks)

        if self.terrain.is_dirty() or updated_blocks:
            self._parent.queueRedraw()

    def sendTerrainBlocks(self, updated_blocks):
        self.workpool.addRequest(self.encodeTerrainBlock, updated_blocks,
                             self.terrainEncoded, self._parent.default_error_db)

    def encodeTerrainBlock(self, args):
        """
        Function for the encoding thread, encodes and sends a block of terrain
        data.
        """
        datablock, x, y = args
        bindata = TerrainEncoder.encode([[datablock, x, y]])
        b64data = base64.urlsafe_b64encode(bindata).decode('ascii')
        # send directly from the thread
        self.simrt.LayerData(x, y, b64data)
        return True

    def terrainEncoded(self, request, result):
        """
        Callback for a terrain encoder thread. we do nothing.
        """
        pass

    def processLayerData(self, layerType, b64data):
        """
        LayerData arrived from the simulator.
        """
        self.workpool.addRequest(self.decodeTerrainBlock, [b64data],
                             self.terrainDecoded, self._parent.default_error_db)

    def processLayerDataDecoded(self, header, layer):
        """
        LayerData ready from the transcoding thread.
        """
        self.terrain.apply_patch(layer, header.x, header.y)

    def decodeTerrainBlock(self, b64data):
        """
        Decode a block of terrain data from the transcoding thread. Converts from base64
        into a python array.
        """
        data = base64.urlsafe_b64decode(b64data.encode('ascii'))
        terrpackets = TerrainDecoder.decode(data)
        return terrpackets
 
    def terrainDecoded(self, request, terrpackets):
        """
        Terrain data is ready, push it into the command processor queue.
        """
        for header, layer in terrpackets:
            self._parent.command_queue.append(['LayerDataDecoded', header, layer])
