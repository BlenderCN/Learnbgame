"""
Classes managing the ogre mesh and dotscene exporters.
"""

import ogremeshesexporter as meshexport
import ogredotscene as sceneexport

from ogrepkg.base import Log, View

# hook up some ogre exporter functions.
import b2rexpkg.b24.uuidhooks

# kind of reporter	
class Reporter(View):
	def update(self):
		print self.model.messageList[-1][1].strip()

# export meshes
class OgreExporter(object):
    def __init__(self):
        self.meshapp = meshexport.MeshExporterApplication()
        self._myview = Reporter(Log.getSingleton())

    def exportMeshes(self, path, pack_name):
        """
        Export selected meshes to ogre .mesh format and material file.
        """
        meshexport.OgreXMLConverter.getSingleton().setReorganiseBuffers(True)
        exportPath = path
        exportMaterial = True
        materialScriptName = pack_name + ".material"
        customMaterial = False
        customMaterialTplPath = None
        colouredAmbient = False
        gameEngineMaterials = True
        exportMesh = True
        fixUpAxis = True
        skeletonUseMeshName = False
        applyModifiers = False
        convertXML = True
        copyTextures = True
        requireFaceMats = False
        # export meshes
        self.meshapp.selectedObjectManager.updateSelection()
        self.meshapp.selectedObjectManager.export(exportPath, exportMaterial, materialScriptName,
                          customMaterial, customMaterialTplPath,
                          colouredAmbient, gameEngineMaterials, exportMesh,
                          fixUpAxis, skeletonUseMeshName, applyModifiers,
                          convertXML, copyTextures, requireFaceMats)

    def exportScene(self, path, pack_name, offset=[128.0, 128.0, 20]):
        """
        Export selected meshes to ogre scene format.
        """
        self.sceneapp = sceneexport.DotSceneExporterApplication()
        # export scene
        self.sceneapp.exportSettings.path = path
        self.sceneapp.exportSettings.fileName = pack_name + ".scene"
        self.sceneapp.exportSettings.transX = offset[0]
        self.sceneapp.exportSettings.transY = offset[1]
        self.sceneapp.exportSettings.transZ = offset[2]
        self.sceneapp.sceneExporter.export()

    def export(self, path, pack_name, offset):
        """
        Export whole scene, including scene info and mesh info.
        """
        self.exportMeshes(path, pack_name)
        self.exportScene(path, pack_name, offset)
        print sceneexport.exportLogger.messageList

if __name__ == '__main__':
    global_path = "/tmp/export2"
    pack_name = "cube2"
    exporter = OgreExporter()
    exporter.export(global_path, pack_name, [128.0, 128.0, 128.0])
