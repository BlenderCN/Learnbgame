import bpy
import textureUtil
import install
import pbrt
import sceneParser
import generalUtil
import materialTree
import lightEnv

import os
import math
import subprocess

# =============================================================================
# Utils

def dump(obj):
   for attr in dir(obj):
       if hasattr( obj, attr ):
           print( "obj.%s = %s" % (attr, getattr(obj, attr)))

def wline(f, t):
    f.write("{}\n".format(t))

def runCmd(cmd, stdout=None, cwd=None, env=None):
    stdoutInfo = ""
    if stdout is not None:
        stdoutInfo = " > {}".format(stdout.name)
    print(">>> {}{}".format(cmd, stdoutInfo))
    subprocess.call(cmd, shell=False, stdout=stdout, cwd=cwd, env=env)

def appendFile(sourcePath, destFile):
    sourceFile = open(sourcePath, 'r')
    for line in sourceFile:
        destFile.write(line)
    sourceFile.close()

def warningMessage(renderContext, message):
    renderContext.report({"WARNING"}, message)

def errorMessage(renderContext, message):
    renderContext.report({"ERROR"}, message)
    raise Exception(message)

# =============================================================================
# Materials generation

def createEmptyMaterialObject():
    m = generalUtil.emptyObject()
    m.iileMaterial = "MATTE"
    m.iileMatteColorTexture = ""
    m.iileMatteColor = [1.0, 0.0, 1.0] # Bright purple
    return m

def processMatteMaterial(matName, outDir, block, matObj):
    block.appendLine(2, '"string type" "matte"')
    if matObj.iileMatteColorTexture == "":
        # Diffuse color
        block.appendLine(2, '"rgb Kd" [ {} {} {} ]' \
            .format(matObj.iileMatteColor[0],
                matObj.iileMatteColor[1],
                matObj.iileMatteColor[2]))
    else:
        # Diffuse texture
        # Get the absolute path of the texture
        print("Texture detected for material {}".format(matName))
        texSource = matObj.iileMatteColorTexture
        destName = textureUtil.addTexture(texSource, outDir, block)
        # Set Kd to the texture
        materialLine = '"texture Kd" "{}"'.format(destName)
        block.appendLine(2, materialLine)

def processPlasticMaterial(matName, outDir, block, matObj):
    block.appendLine(2, '"string type" "plastic"')

    # Diffuse
    if matObj.iilePlasticDiffuseTexture == "":
        # Diffuse color
        block.appendLine(2, '"rgb Kd" [ {} {} {} ]' \
            .format(matObj.iilePlasticDiffuseColor[0],
                matObj.iilePlasticDiffuseColor[1],
                matObj.iilePlasticDiffuseColor[2]))
    else:
        # Diffuse texture
        texSource = matObj.iilePlasticDiffuseTexture
        destName = textureUtil.addTexture(texSource, outDir, block)
        # Set Kd
        materialLine = '"texture Kd" "{}"'.format(destName)
        block.appendLine(2, materialLine)

    # Specular
    if matObj.iilePlasticSpecularTexture == "":
        # Specular color
        block.appendLine(2, '"rgb Ks" [ {} {} {} ]'\
            .format(matObj.iilePlasticSpecularColor[0],
                matObj.iilePlasticSpecularColor[1],
                matObj.iilePlasticSpecularColor[2])
        )
    else:
        # Specular texture
        texSource = matObj.iilePlasticSpecularTexture
        destName = textureUtil.addTexture(texSource, outDir, block)
        # Set Kd
        materialLine = '"texture Ks" "{}"'.format(destName)
        block.appendLine(2, materialLine)

    # Roughness
    if matObj.iilePlasticRoughnessTexture == "":
        roughnessLine = '"float roughness" [{}]'.format(matObj.iilePlasticRoughnessValue)
        block.appendLine(2, roughnessLine)
    else:
        texSource = matObj.iilePlasticRoughnessTexture
        destName = textureUtil.addTexture(texSource, outDir, block, "float")
        roughnessLine = '"texture roughness" "{}"'.format(destName)
        block.appendLine(2, roughnessLine)

    # remaproughness
    remapLine = '"bool remaproughness" "true"'
    block.appendLine(2, remapLine)

def processMirrorMaterial(matName, outDir, block, matObj):
    block.appendLine(2, '"string type" "mirror"')

    # Reflectivity
    if matObj.iileMirrorKrTex == "":
        krLine = '"rgb Kr" [ {} {} {} ]' \
            .format(matObj.iileMirrorKr[0], matObj.iileMirrorKr[1], matObj.iileMirrorKr[2])
        block.appendLine(2, krLine)
    else:
        texSource = matObj.iileMirrorKrTex
        destName = textureUtil.addTexture(texSource, outDir, block)
        krTexLine = '"texture Kr" "{}"'.format(destName)
        block.appendLine(2, krTexLine)

def processMixMaterial(matName, outDir, block, matObj):
    block.appendLine(2, '"string type" "mix"')

    # Amount
    if matObj.iileMatMixAmountTex == "":
        amountLine = '"rgb amount" [ {} {} {} ]' \
            .format(
                matObj.iileMatMixAmount[0],
                matObj.iileMatMixAmount[1],
                matObj.iileMatMixAmount[2]
            )
        block.appendLine(2, amountLine)
    else:
        texSource = matObj.iileMatMixAmountTex
        destName = textureUtil.addTexture(texSource, outDir, block)
        amountTexLine = '"texture amount" "{}"'.format(destName)
        block.appendLine(2, amountTexLine)
    
    # Material 1
    mat1Line = '"string namedmaterial1" "{}"'.format(
        matObj.iileMatMixSlot1Val
    )
    block.appendLine(2, mat1Line)

    # Material 2
    mat2Line = '"string namedmaterial2" "{}"'.format(
        matObj.iileMatMixSlot2Val
    )
    block.appendLine(2, mat2Line)

def processGlassMaterial(matName, outDir, matBlock, matObj):
    matBlock.appendLine(2, '"string type" "glass"')

    # Kr
    if matObj.iileMatGlassKrTex == "":
        krLine = '"rgb Kr" [ {} {} {} ]'.format(matObj.iileMatGlassKr[0], matObj.iileMatGlassKr[1], matObj.iileMatGlassKr[2])
        matBlock.appendLine(2, krLine)
    else:
        texSource = matObj.iileMatGlassKrTex
        destName = textureUtil.addTexture(texSource, outDir, matBlock)
        line = '"texture Kr" "{}"'.format(destName)
        matBlock.appendLine(2, line)

    # Kt
    if matObj.iileMatGlassKtTex == "":
        line = '"rgb Kt" [ {} {} {} ]'.format(matObj.iileMatGlassKt[0], matObj.iileMatGlassKt[1], matObj.iileMatGlassKt[2])
        matBlock.appendLine(2, line)
    else:
        texSource = matObj.iileMatGlassKtTex
        destName = textureUtil.addTexture(texSource, outDir, matBlock)
        line = '"texture Kr" "{}"'.format(destName)
        matBlock.appendLine(2, line)

    # Ior
    if matObj.iileMatGlassIorTex == "":
        line = '"float eta" [ {} ]'.format(matObj.iileMatGlassIor)
        matBlock.appendLine(2, line)
    else:
        texSource = matObj.iileMatGlassIorTex
        destName = textureUtil.addTexture(texSource, outDir, matBlock, texType="float")
        line = '"texture eta" "{}"'.format(destName)
        matBlock.appendLine(2, line)

    # URough
    if matObj.iileMatGlassURoughTex == "":
        line = '"float uroughness" [ {} ]'.format(matObj.iileMatGlassURough)
        matBlock.appendLine(2, line)
    else:
        texSource = matObj.iileMatGlassURoughTex
        destName = textureUtil.addTexture(texSource, outDir, matBlock, texType="float")
        line = '"texture uroughness" "{}"'.format(destName)
        matBlock.appendLine(2, line)

    # VRough
    if matObj.iileMatGlassVRoughTex == "":
        line = '"float vroughness" [ {} ]'.format(matObj.iileMatGlassVRough)
        matBlock.appendLine(2, line)
    else:
        texSource = matObj.iileMatGlassVRoughTex
        destName = textureUtil.addTexture(texSource, outDir, matBlock, texType="float")
        line = '"texture vroughness" "{}"'.format(destName)
        matBlock.appendLine(2, line)

    # Remap roughness
    matBlock.appendLine(2, '"bool remaproughness" "true"')

def processNoneMaterial(matName, outDir, matBlock, matObj):
    matBlock.appendLine(2, '"string type" "none"')

# Render engine ================================================================================

class IILERenderEngine(bpy.types.RenderEngine):
    bl_idname = "iile_renderer" # internal name
    bl_label = "PBRTv3" # Visible name
    bl_use_preview = False # capabilities

    def render(self, scene):

        # Check first-run installation
        install.install()

        # Compute film dimensions
        scale = scene.render.resolution_percentage / 100.0
        sx = int(scene.render.resolution_x * scale)
        sy = int(scene.render.resolution_y * scale)

        print("Starting render, resolution {} {}".format(sx, sy))
        textureUtil.resetTextureCounter()

        # Compute pbrt executable path
        pbrtExecPath = install.getExecutablePath(
            scene.iilePath,
            pbrt.DEFAULT_IILE_PROJECT_PATH,
            "pbrt"
        )
        obj2pbrtExecPath = install.getExecutablePath(
            scene.iilePath,
            pbrt.DEFAULT_IILE_PROJECT_PATH,
            "obj2pbrt"
        )

        if pbrtExecPath is None:
            errorMessage(self, "PBRT executable not found. The exporter can use the pbrt executable if it's in the system PATH, or you can specify the directory of the PBRT executable from the Render properties tab")
        if obj2pbrtExecPath is None:
            errorMessage(self, "obj2pbrt executable not found. The exporter can use the obj2pbrt executable if it's in the system PATH, or you can specify the directory of the PBRT and OBJ2PBRT executables from the Render properties tab")

        print("PBRT: {}".format(pbrtExecPath))
        print("OBJ2PBRT: {}".format(obj2pbrtExecPath))

        # Determine PBRT project directory
        if not os.path.exists(scene.iilePath):
            # Check fallback
            if not os.path.exists(pbrt.DEFAULT_IILE_PROJECT_PATH):
                warningMessage(self, "WARNING no project directory found. Are you using vanilla PBRTv3? Some features might not work, such as IILE integrator and GUI renderer")
            else:
                scene.iilePath = pbrt.DEFAULT_IILE_PROJECT_PATH

        rootDir = os.path.abspath(os.path.join(scene.iilePath, ".."))

        # Get the output path
        outDir = bpy.data.scenes["Scene"].render.filepath
        outDir = bpy.path.abspath(outDir)
        print("Out dir is {}".format(outDir))
        outObjPath = os.path.join(outDir, "exp.obj")
        outExpPbrtPath = os.path.join(outDir, "exp.pbrt")
        outExp2PbrtPath = os.path.join(outDir, "exp2.pbrt")
        outScenePath = os.path.join(outDir, "scene.pbrt")

        # Create exporting script
        expScriptPath = os.path.join(outDir, "exp.py")
        expScriptFile = open(expScriptPath, "w")
        wline(expScriptFile, 'import bpy')
        wline(expScriptFile, 'outobj = "{}"'.format(outObjPath))
        wline(expScriptFile, 'bpy.ops.export_scene.obj(filepath=outobj, axis_forward="Y", axis_up="-Z", use_materials=True)')
        expScriptFile.close()

        blenderPath = bpy.app.binary_path
        projectPath = bpy.data.filepath
        if not os.path.isfile(projectPath):
            errorMessage(self, "Please Save before Render")

        cmd = [
            blenderPath,
            projectPath,
            "--background",
            "--python",
            expScriptPath
        ]
        runCmd(cmd)

        print("OBJ export completed")

        # Run obj2pbrt
        cmd = [
            obj2pbrtExecPath,
            outObjPath,
            outExpPbrtPath
        ]
        runCmd(cmd, cwd=outDir)

        # Run pbrt --toply
        cmd = [
            pbrtExecPath,
            "--toply",
            outExpPbrtPath
        ]
        outExp2PbrtFile = open(outExp2PbrtPath, "w")
        runCmd(cmd, stdout=outExp2PbrtFile, cwd=outDir)
        outExp2PbrtFile.close()

        # -----------------------------------------------------------
        # Scene transformation
        doc = sceneParser.SceneDocument()
        doc.parse(outExp2PbrtPath)

        # Write initial things
        headerBlocks = []

        # Film, Camera, transformations
        b = sceneParser.SceneBlock([])
        headerBlocks.append(b)
        b.appendLine(0, 'Film "image" "integer xresolution" {} "integer yresolution" {}'.format(sx, sy))

        # Integrator name
        integratorName = "path"
        if bpy.context.scene.iileIntegrator == "PATH":
            integratorName = "path"
        elif bpy.context.scene.iileIntegrator == "IILE":
            integratorName = "iispt"
        elif bpy.context.scene.iileIntegrator == "BDPT":
            integratorName = "bdpt"
        else:
            errorMessage(self, "Unrecognized iileIntegrator {}".format(
                bpy.context.scene.iileIntegrator))
        b.appendLine(0, 'Integrator "{}"'.format(integratorName))

        # Integrator specifics
        if bpy.context.scene.iileIntegrator == "PATH":
            pass
        elif bpy.context.scene.iileIntegrator == "BDPT":
            b.appendLine(1, '"integer maxdepth" [{}]'.format(bpy.context.scene.iileIntegratorBdptMaxdepth))
            b.appendLine(1, '"string lightsamplestrategy" "{}"'.format(bpy.context.scene.iileIntegratorBdptLightsamplestrategy.lower()))
            b.appendLine(1, '"bool visualizestrategies" "{}"'.format("true" if bpy.context.scene.iileIntegratorBdptVisualizestrategies else "false"))
            b.appendLine(1, '"bool visualizeweights" "{}"'.format("true" if bpy.context.scene.iileIntegratorBdptVisualizeweights else "false"))

        samplerName = "random"
        if bpy.context.scene.iileIntegratorPathSampler == "RANDOM":
            samplerName = "random"
        elif bpy.context.scene.iileIntegratorPathSampler == "SOBOL":
            samplerName = "sobol"
        elif bpy.context.scene.iileIntegratorPathSampler == "HALTON":
            samplerName = "halton"
        else:
            errorMessage(self, "Unrecognized sampler {}".format(bpy.context.scene.iileIntegratorPathSampler))

        b.appendLine(0, 'Sampler "{}" "integer pixelsamples" {}'.format(samplerName, bpy.context.scene.iileIntegratorPathSamples))

        b.appendLine(0, 'Scale -1 1 1')

        # Get camera
        theCameraName = bpy.context.scene.camera.name
        theCamera = bpy.data.cameras[theCameraName]

        bpy.context.scene.camera.rotation_mode = "AXIS_ANGLE"
        print("Camera rotation axis angle is {} {} {} {}".format(bpy.context.scene.camera.rotation_axis_angle[0], bpy.context.scene.camera.rotation_axis_angle[1], bpy.context.scene.camera.rotation_axis_angle[2], bpy.context.scene.camera.rotation_axis_angle[3]))

        # Write camera rotation
        cameraRotationAmount = bpy.context.scene.camera.rotation_axis_angle[0]
        cameraRotationAmount = math.degrees(cameraRotationAmount)
        cameraRotationX, cameraRotationY, cameraRotationZ = \
            bpy.context.scene.camera.rotation_axis_angle[1:]
        # Flip Y
        cameraRotationY = -cameraRotationY
        b.appendLine(0, 'Rotate {} {} {} {}'.format(
            cameraRotationAmount, cameraRotationX,
            cameraRotationY, cameraRotationZ))

        # Write camera translation
        cameraLocX, cameraLocY, cameraLocZ = bpy.context.scene.camera.location
        # Flip Y
        cameraLocY = -cameraLocY
        b.appendLine(0, 'Translate {} {} {}'.format(
            cameraLocX, cameraLocY, cameraLocZ))

        # Write camera fov
        b.appendLine(0, 'Camera "perspective" "float fov" [{}]'.format(math.degrees(theCamera.angle / 2.0)))

        # Write world begin
        b.appendLine(0, 'WorldBegin')

        # Set environment lighting
        envBlock = lightEnv.createEnvironmentBlock(scene.world, outDir)
        if envBlock is not None:
            headerBlocks.append(envBlock)

        # Do materials
        materialsResolutionOrder = materialTree.buildMaterialsDependencies()

        for i in range(len(materialsResolutionOrder)):
            matName = materialsResolutionOrder[i]
            matBlock = sceneParser.SceneBlock([])
            headerBlocks.append(matBlock)

            matBlock.appendLine(0, 'MakeNamedMaterial "{}"'.format(matName))
            print("Processing material {}".format(matName))
            if matName not in bpy.data.materials:
                matObj = createEmptyMaterialObject()
            else:
                matObj = bpy.data.materials[matName]
            # Write material type
            if matObj.iileMaterial == "MATTE":
                processMatteMaterial(matName, outDir, matBlock, matObj)
            elif matObj.iileMaterial == "PLASTIC":
                processPlasticMaterial(matName, outDir, matBlock, matObj)
            elif matObj.iileMaterial == "MIRROR":
                processMirrorMaterial(matName, outDir, matBlock, matObj)
            elif matObj.iileMaterial == "MIX":
                processMixMaterial(matName, outDir, matBlock, matObj)
            elif matObj.iileMaterial == "GLASS":
                processGlassMaterial(matName, outDir, matBlock, matObj)
            elif matObj.iileMaterial == "NONE":
                processNoneMaterial(matName, outDir, matBlock, matObj)

            else:
                errorMessage(self, "Unrecognized material {}".format(
                    matObj.iileMaterial))

        blocks = doc.getBlocks()
        for block in blocks:

            # Set area light emission color
            if block.isAreaLightSource():
                print("Processing an area light source")
                matName = block.getAssignedMaterial()
                print(matName)
                if matName not in bpy.data.materials:
                    continue
                matObj = bpy.data.materials[matName]
                emitIntensity = matObj.emit
                emitColor = [0.0, 0.0, 0.0]
                emitColor[0] = emitIntensity * matObj.iileEmission[0]
                emitColor[1] = emitIntensity * matObj.iileEmission[1]
                emitColor[2] = emitIntensity * matObj.iileEmission[2]
                block.replaceLine(3, '"rgb L"',
                    '"rgb L" [ {} {} {} ]'.format(
                        emitColor[0], emitColor[1], emitColor[2]))

            # Set material properties
            if block.isMakeNamedMaterial():
                block.clearAll()

        doc.addBlocksBeginning(headerBlocks)

        # WorldEnd block
        weBlock = sceneParser.SceneBlock([])
        weBlock.appendLine(0, "WorldEnd")
        doc.addBlocksEnd([weBlock])

        doc.write(outScenePath)

        print("Rendering finished.")

        if (bpy.context.scene.iileIntegrator == "IILE") and bpy.context.scene.iileStartRenderer:
            print("Starting IILE GUI...")

            # Setup PATH for nodejs executable
            nodeBinDir = install.findNodeDir(scene.iilePath)
            newEnv = os.environ.copy()
            if nodeBinDir is not None:
                oldPath = newEnv["PATH"]
                addition = ':{}'.format(nodeBinDir)
                if not oldPath.endswith(addition):
                    oldPath = oldPath + addition
                newEnv["PATH"] = oldPath
                print("Updated PATH to {}".format(oldPath))

            guiDir = os.path.join(rootDir, "gui")
            electronPath = os.path.join(guiDir,
                "node_modules",
                "electron",
                "dist",
                "electron")
            jsPbrtPath = os.path.join(rootDir,
                "bin",
                "pbrt")
            cmd = []
            cmd.append(electronPath)
            cmd.append("main.js")
            cmd.append(jsPbrtPath)
            cmd.append(outScenePath)
            cmd.append("{}".format(bpy.context.scene.iileIntegratorIileIndirect))
            cmd.append("{}".format(bpy.context.scene.iileIntegratorIileDirect))
            runCmd(cmd, cwd=guiDir, env=newEnv)

        result = self.begin_result(0, 0, sx, sy)
        self.end_result(result)