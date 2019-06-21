"""
Class holding all export modules.
"""

import os
import sys
import base64
import logging
import tempfile
import shutil
import uuid
from collections import defaultdict

from io import StringIO

from b2rexpkg.tools import uuidexport

from .tools.siminfo import GridInfo
from .tools.simconnection import SimConnection
from .tools.uuidexport import reset_uuids
from .tools.simtypes import AssetType

if sys.version_info[0] == 2:
    from .b24.ogre_exporter import OgreExporter
else:
    from .b25.ogre_exporter import OgreExporter
    from .b25.material import RexMaterialIO

import bpy
logger = logging.getLogger('b2rex.exporter')

class Exporter(object):
    def __init__(self, gridinfo=None):
        # rest
        if gridinfo:
            self.gridinfo = gridinfo
        else:
            self.gridinfo = GridInfo()
        self.sim = SimConnection()
        self.ogre = OgreExporter()

    def connect(self, base_url, username="", password=""):
        """
        Connect to an opensim instance
        """
        self.gridinfo.connect(base_url, username, password)
        self.sim.connect(base_url)

    def test(self):
        """
        Api tests
        """
        logger.debug(self.gridinfo.getGridInfo()["gridnick"])
        regions = self.gridinfo.getRegions()
        for id in regions:
            region = regions[id]
            logger.debug((" *", region["name"], region["x"], region["y"], id))

        # xmlrpc
        logger.debug(self.sim.login("caedes", "caedes", "pass"))
        logger.debug(self.sim.sceneClear("d9d1b302-5049-452d-b176-3a9561189ca4",
                                         "cube"))
        logger.debug(self.sim.sceneUpload("d9d1b302-5049-452d-b176-3a9561189ca4",
                              "cube",
                              "/home/caedes/groupmembers.zip"))

    def export(self, path, pack_name, offset, exportSettings):
        """
        Export the scene to a zipfile.
        """
        uuidexport.start()
        if exportSettings.regenMaterials:
                uuidexport.reset_uuids(bpy.data.materials)
        if exportSettings.regenObjects:
                uuidexport.reset_uuids(bpy.data.objects)
        if exportSettings.regenTextures:
                uuidexport.reset_uuids(bpy.data.textures)
        if exportSettings.regenMeshes:
                uuidexport.reset_uuids(bpy.data.meshes)
        self.ogre.export(path, pack_name, offset)
        uuid_path = os.path.join(path, pack_name + ".uuids")
        logger.debug('writing uuids to '+uuid_path)
        f = open(uuid_path, 'w')
        uuidexport.write(f)
        f.close()

    def doAsyncExportMesh(self, context, selected, finish_upload):
        self.doExport(context.scene.b2rex_props, list(selected.location))
        f = open(os.path.join(self.getExportDir(), 'b2rx_export',
                              selected.data.name+'.mesh'), 'rb')
        data = f.read()
        f.close()
        finish_upload(data)

    def ensureDestinationDir(self, export_dir=None, delete=False):
        if not export_dir:
            export_dir = self.getExportDir()
        destfolder = os.path.join(export_dir, 'b2rx_export')
        if not os.path.exists(destfolder):
            os.makedirs(destfolder)
        elif delete:
            shutil.rmtree(destfolder)
            os.makedirs(destfolder)
        return destfolder


    def doExport(self, exportSettings, location, pack=True, delete=True):
        """
        Export Action
        """
        tempfile.gettempdir()
        self.exportSettings = exportSettings
        base_url = self.exportSettings.server_url
        pack_name = self.exportSettings.pack
        export_dir = self.getExportDir()

        self.addStatus("Exporting to " + export_dir, 'IMMEDIATE')

        destfolder = self.ensureDestinationDir(export_dir, delete)

        x, y, z = location

        self.export(destfolder, pack_name, [x, y, z], self.exportSettings)
        if pack:
            dest_file = os.path.join(export_dir, "world_pack.zip")
            self.packTo(destfolder, dest_file)

        self.addStatus("Exported to " + dest_file)

    def getExportDir(self):
        """
        Get export directory.
        """
        export_dir = self.exportSettings.path
        if not export_dir:
            export_dir = tempfile.gettempdir()
        return export_dir

    def packTo(self, from_path, to_zip):
        """
        Pack a directory to a file.
        """
        import zipfile
        zfile = zipfile.ZipFile(to_zip, "w", zipfile.ZIP_DEFLATED)
        for dirpath, dirnames, filenames in os.walk(from_path):
            for name in filenames:
                file_path = os.path.join(dirpath,  name)
                zfile.write(file_path, file_path[len(from_path+"/"):])
        zfile.close()

    def doUpload(self):
        """
        Upload Action
        """
        base_url = self.exportSettings.server_url
        pack_name = self.exportSettings.pack
        if not self.region_uuid:
            self.addStatus("Error: No region selected ", 'ERROR')
            return
        self.addStatus("Uploading to " + base_url, 'IMMEDIATE')
        export_dir = self.getExportDir()
        res = self.sim.sceneUpload(self.region_uuid,
                                                           pack_name,
                                   os.path.join(export_dir, "world_pack.zip"))
        if res.has_key('success') and res['success'] == True:
            self.addStatus("Uploaded to " + base_url)
        else:
            self.addStatus("Error: Something went wrong uploading", 'ERROR')


    def _getFaceRepresentatives(self, mesh):
        seen_images = []
        faces = []
        if mesh.uv_textures:
            for face in mesh.uv_textures[0].data:
                if face.use_image and face.image:
                    if not face.image in seen_images:
                        seen_images.append(face.image)
                        faces.append(face)
        return faces

    def _getFaceMaterial(self, mesh, face):
        for mat in mesh.materials:
            for slot in mat.texture_slots:
                if slot and slot.use_map_color_diffuse and slot.texture:
                    tex = slot.texture
                    if tex.type == 'IMAGE' and tex.image and tex.image == face.image:
                        return mat
        if mesh.materials:
            print("returning default material")
            return mesh.materials[0]
        newmat = bpy.data.materials.new("opensim")
        mesh.materials.append(newmat)
        return newmat

    def uploadImage(self, image, cb):
        imagepath = os.path.realpath(bpy.path.abspath(image.filepath))
        if os.path.exists(imagepath):
            converted_path = self.convert_image_format(imagepath, 'jpc')
            if os.path.exists(converted_path):
                f = open(converted_path, 'rb')
                self.Asset.upload(image.opensim.uuid, 0, f.read(), cb)
                f.close()
                return image.opensim.uuid

    def uploadMaterial(self, material, data, cb):
        self.Asset.upload(material.opensim.uuid, AssetType.OgreMaterial,
                               data, cb)
        return material.opensim.uuid


    def doExportMaterials(self, obj, cb):
        mesh = obj.data
        faces = self._getFaceRepresentatives(mesh)
        materials = []
        materialsdone = []
        changednames = []
        tokens = {}
        def material_finished(token, newAssetID, trID):
            print("material_finished go on", token)
            idx = materials.index(token)
            mat = tokens.pop(token)
            mat.opensim.uuid = newAssetID
            materials[idx] = newAssetID
            materialsdone.append(newAssetID)
            if len(materialsdone) == len(materials):
                cb(materials)

        def process_materials():
            # now process materials
            for face in faces:
                bmat = self._getFaceMaterial(mesh, face)
                if not bmat.opensim.uuid:
                    bmat.opensim.uuid = str(uuid.uuid4())
                    bmat.name = bmat.opensim.uuid
                    matio = RexMaterialIO(self, mesh, face, bmat)
                    f = StringIO()
                    matio.write(f)
                    f.seek(0)
                    data = f.read()
                    print("MATERIAL", data)
                    id = self.uploadMaterial(bmat, data, material_finished)
                    if id:
                        tokens[id] = bmat
                else:
                    materialsdone.append(bmat.opensim.uuid)
                materials.append(bmat.opensim.uuid)
            if len(materialsdone) == len(materials):
                cb(materials)

        def image_finished(token, newAssetID, trID):
            print("image finished go on", token)
            face = tokens.pop(token)
            face.image.opensim.uuid = newAssetID
            if not len(tokens):
                process_materials()

        # ensure images first
        for face in faces:
            if not face.image.opensim.uuid:
                face.image.opensim.uuid = str(uuid.uuid4())
                id = self.uploadImage(face.image, image_finished)
                if id:
                    tokens[id] = face
        if not len(tokens):
            process_materials()

