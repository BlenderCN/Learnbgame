import bpy
import bmesh
import math
import mathutils
import os

rootKeys = {
    "depTexKey": "dependentTextures",
    "matsKey": "materials",
    "meshesKey": "meshes",
    "objectsKey": "objects"
}

objectKeys = {
    "typeKey": "type",
    "dataKey": "data",
    "matWorldKey": "matrixWorld",
    "parentKey": "parent"
}

uvLayersKey = {
    "uvKey": "uv",
    "tanKey": "tan"
}

meshKeys = {
    "facesGroupsKey": "facesGroups",
    "matSlotsKey": "materialSlots",
    "normalsKey": "normals",
    "uvLayersKey": "uvLayers",
    "verticesKey": "vertices"
}

matKeys = {
    "drawableKey": "drawable",
    "shaderPathKey": "shaderPath",
    "shaderUniformsKey": "shaderUniforms",
    "shaderAttributesKey": "shaderAttributes",
    "envprobeTypeKey": "envprobeType",
    "renderPassKey": "renderPass",
    "lightingModelKey": "lightingModel"
}


def normalizeFilePath(path):
    path = os.path.normpath(path)
    path = path.lstrip('/')
    return path


def changeFileExtension(file, ext):
    return (os.path.splitext(file)[0] + '.' + ext)

class DataPacker:
    exporter = None
    toOpenGLSpaceMat = mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')

    def packMaterials(self, packedData, context):
        packedMaterials = packedData[rootKeys["matsKey"]] = {}

        for mat in bpy.data.materials:
            packedMaterial = packedMaterials[mat.name] = {}
            self.packMaterial(packedMaterial, mat)

        return True

    def packMaterial(self, packedMaterial, mat):
        nodes = mat.node_tree.nodes

        """
        EN: Search frames called "zimeshShader", "uniforms", "attributes"
        PL: Szuka ramek "zimeshShader", "uniforms", "attributes"
        """
        shdFrame = nodes.get('zimeshShader')
        if (shdFrame is None) or (type(shdFrame) is not bpy.types.NodeFrame):
            return False

        shdUniformsFrame = nodes.get('uniforms')
        if (shdUniformsFrame is None) or (type(shdUniformsFrame) is not bpy.types.NodeFrame):
            return False

        shdAttribsFrame = nodes.get('attributes')
        if (shdAttribsFrame is None) or (type(shdAttribsFrame) is not bpy.types.NodeFrame):
            return False

        """
        EN: Get name Label from frame "zimeshShader", which is
            path to shader descriptor file.
        PL: Z ramki "zimeshShader" pobiera jej nazwę Label, która jest
            ścieżką do deskryptora shadera.
        """
        packedMaterial[matKeys["shaderPathKey"]] = normalizeFilePath(shdFrame.label)

        """
        EN: Search nodes belong to frame "uniforms" or "attributes".
        PL: Szuka nodes należących do ramki "uniforms" lub "attributes".
        """
        uniformNodes = []
        attribNodes = []
        for node in nodes:
            if node.parent == shdUniformsFrame:
                uniformNodes.append(node)
            if node.parent == shdAttribsFrame:
                attribNodes.append(node)

        packedShdUniforms = packedMaterial[matKeys["shaderUniformsKey"]] = {}
        packedShdAttribs = packedMaterial[matKeys["shaderAttributesKey"]] = {}

        """
        EN: Pack attribute and uniform nodes to dictionary
        PL: Pakuje nodes atrybutów lub uniformów do słownika
        """
        for node in uniformNodes:
            uniform = self.packShaderUniform(node)
            if uniform is not None:
                packedShdUniform = packedShdUniforms[node.name] = uniform
        for node in attribNodes:
            attrib = self.packShaderAttrib(node)
            if attrib is not None:
                packedShdAttrib = packedShdAttribs[node.name] = attrib

        packedMaterial[matKeys["drawableKey"]] = True
        packedMaterial[matKeys["envprobeTypeKey"]] = "None"
        packedMaterial[matKeys["renderPassKey"]] = "Deferred"
        packedMaterial[matKeys["lightingModelKey"]] = "PBR"

        return True

    def packShaderUniform(self, node):
        if type(node) is bpy.types.ShaderNodeValue:
            val = node.outputs[0].default_value
            return str(val)
        if type(node) is bpy.types.ShaderNodeTexImage:
            img_fp = normalizeFilePath(node.image.filepath)
            return changeFileExtension(img_fp, "zitex")
        return None

    def packShaderAttrib(self, node):
        if type(node) is bpy.types.ShaderNodeUVMap:
            return node.uv_map
        if type(node) is bpy.types.ShaderNodeTangent:
            if node.direction_type == "UV_MAP":
                return node.uv_map
            else:
                return None
        return None

    def packMeshObject(self, packedData, obj, context):
        # Triangulate and transform to OpenGL Space
        meshTemp = obj.to_mesh(context.scene, True, "PREVIEW")
        bm = bmesh.new()
        bm.from_mesh(meshTemp)
        bm.transform(self.toOpenGLSpaceMat)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.to_mesh(meshTemp)
        bm.free()

        packedObjects = packedData[rootKeys["objectsKey"]]
        packedMeshes = packedData[rootKeys["meshesKey"]]

        packedObject = packedObjects[obj.name] = {}
        packedMesh = packedMeshes[obj.data.name] = {}

        meshTemp.calc_normals_split()

        packedVertices = packedMesh[meshKeys["verticesKey"]] = []
        packedNormals = packedMesh[meshKeys["normalsKey"]] = []
        for loop in meshTemp.loops:
            norm = loop.normal
            vertIdx = loop.vertex_index
            vert = meshTemp.vertices[vertIdx]

            packedVertices.extend([vert.co[0], vert.co[1], vert.co[2]])
            packedNormals.extend([norm[0], norm[1], norm[2]])

        packedUvLayers = packedMesh[meshKeys["uvLayersKey"]] = {}
        for uvLayer in meshTemp.uv_layers:
            uvLayerData = packedUvLayers[uvLayer.name] = {}
            uvComponents = uvLayerData[uvLayersKey["uvKey"]] = []
            tanComponents = uvLayerData[uvLayersKey["tanKey"]] = []

            for uvLoop in uvLayer.data:
                uvComponents.extend([uvLoop.uv[0], uvLoop.uv[1]])

            meshTemp.calc_tangents(uvLayer.name)
            for loop in meshTemp.loops:
                tan = loop.tangent
                bitanSign = loop.bitangent_sign
                tanComponents.extend([tan[0], tan[1], tan[2], bitanSign])

        packedMatSlots = packedMesh[meshKeys["matSlotsKey"]] = []
        for slot in obj.material_slots:
            packedMatSlots.append(slot.material.name)

        packedFaces = packedMesh[meshKeys["facesGroupsKey"]] = {}
        for matSlotIndex in range(0, len(obj.material_slots)):
            packedFaces[matSlotIndex] = []

        for polygon in meshTemp.polygons:
            if polygon.loop_total >= 3:
                fg = packedFaces[polygon.material_index]
                fg.extend([polygon.loop_indices[0], polygon.loop_indices[1], polygon.loop_indices[2]])

        packedObject[objectKeys["typeKey"]] = "Mesh"
        packedObject[objectKeys["dataKey"]] = obj.data.name
        if obj.parent is not None:
            packedObject[objectKeys["parentKey"]] = obj.parent.name
        else:
            packedObject[objectKeys["parentKey"]] = None

        matWorld = obj.matrix_world
        packedObject[objectKeys["matWorldKey"]] = [
            matWorld.col[0][0], matWorld.col[0][1], matWorld.col[0][2], matWorld.col[0][3],
            matWorld.col[1][0], matWorld.col[1][1], matWorld.col[1][2], matWorld.col[1][3],
            matWorld.col[2][0], matWorld.col[2][1], matWorld.col[2][2], matWorld.col[2][3],
            matWorld.col[3][0], matWorld.col[3][1], matWorld.col[3][2], matWorld.col[3][3]
        ]

        # Free temporary mesh (with applied modifiers of obj)
        bpy.data.meshes.remove(meshTemp)
        return True

    def packLightObject(self, packedData, light, context):
        return True

    def packObjects(self, packedData, context):
        objectsToExport = None
        if self.exporter.selectedOnly:
            objectsToExport = context.selected_objects
        else:
            objectsToExport = context.scene.objects

        packedData[rootKeys["objectsKey"]] = {}
        packedData[rootKeys["meshesKey"]] = {}

        for obj in objectsToExport:
            if obj.type == "MESH":
                self.packMeshObject(packedData, obj, context)
            if obj.type == "LIGHT":
                self.packLightObject(packedData, obj, context)
        return True

    def packData(self, exporter, context):
        self.exporter = exporter
        packedData = {}
        self.packMaterials(packedData, context)
        self.packObjects(packedData, context)
        return packedData
