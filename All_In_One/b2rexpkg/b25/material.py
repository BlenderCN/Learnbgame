"""
Rex material support for the ogre exporter.
"""
import bpy
import os

layerMappings = {'normalMap':'normal',
             'heightMap':'displacement',
             'reflectionMap':'reflect',
             'opacityMap':'alpha',
             'lightMap':'ambient',
             'specularMap':'specular' }
invLayerMappings = {}
for key, val in layerMappings.items():
    invLayerMappings[val] = key

def PathName(filename):
    print("PathName", filename)
    return filename

def indent(howmuch):
    return "  "*howmuch

def clamp(value):
    return max(0.0, min(1.0, value))

class RexMaterialIO(object):
    """
    Material exporter and parser to export for the rex cg supershader
    """
    def __init__(self, manager, blenderMesh, blenderFace, blenderMaterial):
        self.manager = manager
        self.mesh = blenderMesh
        self.face = blenderFace
        self.colouredAmbient = False
        # check if a Blender material is assigned
        try:
            blenderMaterial = blenderMaterial
        except:
            blenderMaterial = None
        self.TEXFACE = blenderFace and blenderFace.use_twoside
        self.IMAGEUVCOL = blenderFace and blenderFace.use_image
        self.fp_parms = {}
        self.vp_parms = {}
        self.alpha = 1.0
        self.shadows = False # doesnt work with rex for now..
        self.material = blenderMaterial
        self._parseMaterial(blenderMaterial)
        return

    def getAutodetect(self):
        """
        Get the autodetect property for the material.
        """
        mat = self.material
        if not mat:
            return True
        return mat.opensim.autodetect

    def toggleAutodetect(self):
        """
        Toggle the autodetect property.
        """
        mat = self.material
        if mat:
            mat.opensim.autodetect = True
            self._parseShader(mat)

    def setShader(self, shader):
        """
        Set the custom shader to use if autodetect is off
        """
        mat = self.material
        if mat:
            mat.opensim.shader = shader
    def getShader(self):
        """
        Get the custom shader to use if autodetect is off
        """
        mat = self.material
        if not mat:
            return ""
        return mat.opensim.shader

    def _parseMaterial(self, mat):
        """
        Parse the blender material and fill up internal structures.
        """
        if mat:
            self.alpha = mat.alpha
            self.shadows = mat.use_cast_buffer_shadows
            self.colouredAmbient = False

            # mat.use_shadows - receive shadows
            # mat.use_shadeless - insensitive to light and shadow
            #print "shadows", self.shadows #, Blender.Material.Modes.keys()
        if self.mesh.uv_textures:
            self.TEXFACE = True
        self._parseShader(mat)

    def getFPShaderVariables(self):
        """
        Unused for the moment
        """
        shVars = {}
        if 'Spec' in self.shader:
            shVars['specularPower'] = 0.8
        return shVars

    def _parseShader(self, mat):
        """
        Find out what shader and shader properties to use.
        """
        fp_parms = {}
        vp_parms = {}
        textures = self.getTextureLayers(mat)
        spectex = textures['specular']
        nortex = textures['normal']
        reftex = textures['reflect']
        ambtex = textures['ambient']
        disptex = textures['displacement']

        specHardness = 0.8
        if mat:
            specHardness = mat.specular_hardness
        if disptex and spectex and nortex:
            shader = "rex/DiffSpecmapNormalParallax"
            fp_parms['specularPower'] = specHardness
        elif nortex and ambtex:
            shader = "rex/DiffNormalLightmap"
        elif nortex and nortex.texture and nortex.texture.image:
            if spectex:
                shader = "rex/DiffSpecmapNormal"
                fp_parms['specularPower'] = specHardness
            else:
                shader = "rex/DiffNormal"
            if self.shadows:
                shader += "Shadow"
        elif reftex and spectex:
            shader = "rex/DiffSpecmapRefl"
            fp_parms['specularPower'] = specHardness
        elif reftex:
            fp_parms['opacity'] = alpha
            shader = "rex/DiffReflAlpha"
        else:
            shader = "rex/Diff"
            if self.shadows:
                shader += "Shadow"

        if mat and mat.opensim.shader and not mat.opensim.autodetect:
            shader = mat.opensim.shader

        self.shader = shader
        self.fp_parms = fp_parms

    def _writeShaderPrograms(self, f):
        """
        Write the rex specific shader references into the material.
        """
        shader = self.shader
        fp_parms = self.fp_parms
        vp_parms = self.vp_parms
        f.write(indent(3)+"vertex_program_ref " + shader + "VP\n")
        f.write(indent(3)+"{\n")
        for par, value in vp_parms.items():
            par_type = "float"
            f.write(indent(4)+"param_named %s %s %s\n"%(par, par_type, value))
        f.write(indent(3)+"}\n")
        f.write(indent(3)+"fragment_program_ref " + shader + "FP\n")
        f.write(indent(3)+"{\n")
        for par, value in fp_parms.items():
            par_type = "float"
            f.write(indent(4)+"param_named %s %s %s\n"%(par, par_type, value))
        f.write(indent(3)+"}\n")

    def writeTechniques(self, f):
        """
        Write the techniques for the material.
        """
        mat = self.material
        if (not(mat)
            and not len(self.mesh.vertex_colors)
            and not len(self.mesh.uv_textures)):
            # default material
            self.writeDefaultTechniques(self, f)
        else:
            self.writeRexTechniques(f, mat)

    def _writePassContents(self, f, mat):
        """
        Write a full pass information.
        """
        f.write(indent(3)+"iteration once\n")

        # shader programs
        self._writeShaderPrograms(f)

        # material colors
        self._writeMaterialParameters(f, mat)

        # texture units
        self._writeTextureUnits(f, mat)

    def _writeMaterialParameters(self, f, mat):
        """
        Write the material parameters.
        """
        # alpha
        if self.alpha < 1.0:
            f.write(indent(3)+"scene_blend alpha_blend\n")
            f.write(indent(3)+"depth_write off\n")

        # ambient
        # (not used in Blender's game engine)
        if mat:
            if (not(mat.use_face_texture)
                and not(mat.use_vertex_color_paint)
                and (mat.ambient)):
                #ambientRGBList = mat.rgbCol
                ambientRGBList = [1.0, 1.0, 1.0]
            else:
                ambientRGBList = [1.0, 1.0, 1.0]
            # ambient <- amb * ambient RGB
            ambR = clamp(mat.ambient * ambientRGBList[0])
            ambG = clamp(mat.ambient * ambientRGBList[1])
            ambB = clamp(mat.ambient * ambientRGBList[2])
            f.write(indent(3)+"ambient %f %f %f\n" % (ambR, ambG, ambB))
        # diffuse
        # (Blender's game engine uses vertex colours
        #  instead of diffuse colour.
        #
        #  diffuse is defined as
        #  (mat->r, mat->g, mat->b)*(mat->emit + mat->ref)
        #  but it's not used.)
        if self.mesh.vertex_colors and False:
            # we ignore this possibility for now...
            # Blender does not handle "texface" mesh with vertex colours
            f.write(indent(3)+"diffuse vertexcolour\n")
        elif mat:
            if (not(mat.use_face_texture)
                and not(mat.use_vertex_color_paint) and not len(mat.texture_slots)):
                # diffuse <- rgbCol
                diffR = clamp(mat.diffuse_color[0])
                diffG = clamp(mat.diffuse_color[1])
                diffB = clamp(mat.diffuse_color[2])
                f.write(indent(3)+"diffuse %f %f %f\n" % (diffR, diffG, diffB))
            elif (mat.use_vertex_color_paint):
                f.write(indent(3)+"diffuse vertexcolour\n")

            # specular <- spec * specCol, hard/4.0
            specR = clamp(mat.specular_intensity * mat.specular_color[0])
            specG = clamp(mat.specular_intensity * mat.specular_color[1])
            specB = clamp(mat.specular_intensity * mat.specular_color[2])
            specShine = mat.specular_hardness/4.0
            f.write(indent(3)+"specular %f %f %f %f\n" % (specR, specG, specB, specShine))
            # emissive
            # (not used in Blender's game engine)
            if(not(mat.use_face_texture)
                and not(mat.use_vertex_color_paint) and not len(mat.texture_slots)):
                # emissive <-emit * rgbCol
                emR = clamp(mat.emit * mat.rgbCol[0])
                emG = clamp(mat.emit * mat.rgbCol[1])
                emB = clamp(mat.emit * mat.rgbCol[2])
                ##f.write(indent(3)+"emissive %f %f %f\n" % (emR, emG, emB))

    def _writeTextureUnits(self, f, mat):
        """
        Write the texture units for the material.
        """
        textures = self.getTextureLayers(mat)
        spectex = textures['specular']
        nortex = textures['normal']
        reftex = textures['reflect']
        ambtex = textures['ambient']
        disptex = textures['displacement']
        shader = self.shader
        # texture units
        if self.mesh.uv_textures:
            # mesh has texture values, resp. tface data
            # scene_blend <- transp
            if (self.face.blend_type == "ALPHA"):
                    f.write(indent(3)+"scene_blend alpha_blend \n")
            elif (self.face.blend_type == "ADD"):
                    f.write(indent(3)+"scene_blend add\n")
            # cull_hardware/cull_software
            # XXX twoside?
            if (self.face.use_twoside):
                f.write(indent(3) + "cull_hardware none\n")
                f.write(indent(3) + "cull_software none\n")
            # shading
            # (Blender's game engine is initialized with glShadeModel(GL_FLAT))
            ##f.write(indent(3) + "shading flat\n")
            # texture
            if (self.face.use_image) and (self.face.image):
                # 0.0-heightMap
                if disptex:
                    self._exportTextureUnit(f, "heightMap", disptex)

                # 0-diffuse
                f.write(indent(3)+"texture_unit baseMap\n")
                f.write(indent(3)+"{\n")
                f.write(indent(4)+"texture %s\n" % self.manager.registerTextureImage(self.face.image))
                f.write(indent(3)+"}\n") # texture_unit
                # 1-specular
                if spectex:
                    self._exportTextureUnit(f, "specularMap", spectex)
                # 2-normal
                if len(self.mesh.materials):
                    tex = self.findMapToTexture(mat, 'normal')
                    if tex and tex.texture and tex.texture.type == 'IMAGE' and  tex.texture.image:
                        self._exportTextureUnit(f, "normalMap", tex)
                # 3-lightMap
                if ambtex:
                    self._exportTextureUnit(f, "lightMap", ambtex)

                # 4-shadow
                if self.shadows and "Shadow" in self.shader:
                    f.write(indent(3)+"texture_unit shadowMap0\n")
                    f.write(indent(3)+"{\n")
                    f.write(indent(4)+"content_type shadow\n")
                    f.write(indent(4)+"tex_address_mode clamp\n")
                    f.write(indent(3)+"}\n") # texture_unit
                    f.write(indent(3)+"texture_unit shadowMap1\n")
                    f.write(indent(3)+"{\n")
                    f.write(indent(4)+"content_type shadow\n")
                    f.write(indent(4)+"tex_address_mode clamp\n")
                    f.write(indent(3)+"}\n") # texture_unit
                    f.write(indent(3)+"texture_unit shadowMap2\n")
                    f.write(indent(3)+"{\n")
                    f.write(indent(4)+"content_type shadow\n")
                    f.write(indent(4)+"tex_address_mode clamp\n")
                    f.write(indent(3)+"}\n") # texture_unit

                # 5-luminanceMap
                # 6-opacityMap
                if textures['alpha']:
                    self._exportTextureUnit(f, "opacityMap", textures['alpha'])
                # 7-reflectionMap
                if reftex:
                    self._exportTextureUnit(f, "reflectionMap", reftex)



    def writeRexTechniques(self, f, mat):
        """
        Write a rex material technique.
        """
        # default material
        # SOLID, white, no specular
        f.write(indent(1)+"technique\n")
        f.write(indent(1)+"{\n")
        f.write(indent(2)+"pass\n")
        f.write(indent(2)+"{\n")
        self._writePassContents(f, mat)
        f.write(indent(2)+"}\n") # pass
        f.write(indent(1)+"}\n") # technique
        return

    def getTextureLayers(self, mat):
        """
        Get an array with the texture layers.
        """
        textures = {}
        if mat:
            for tex in invLayerMappings:
                textures[tex.lower()] = self.findMapToTexture(mat, tex)
        else:
            for tex in invLayerMappings:
                textures[tex.lower()] = None
        return textures

    def _exportTextureUnit(self, f, name, btex):
        """
        Export a single texture unit based on a blender mapto texture.
        """
        f.write(indent(3)+"texture_unit " + name + "\n")
        f.write(indent(3)+"{\n")
        if btex.texture and btex.texture.type == 'IMAGE' and btex.texture.image:
            f.write(indent(4)+"texture %s\n" % self.manager.registerTextureImage(btex.texture.image))
        f.write(indent(3)+"}\n") # texture_unit

    def findMapToTexture(self, meshmat, mapto):
        """
        Find a mapto texture to apply for a specific mapto.
        """
        bmapto = "use_map_"+mapto
        if not meshmat and len(self.mesh.materials):
            meshmat = self.mesh.materials[0]
        if meshmat:
            image = None
            for tex in meshmat.texture_slots:
                if tex and getattr(tex, bmapto):
                    return tex

    # private, might need to override later..
    def _createName(self):
        """Create unique material name.
        
           The name consists of several parts:
           <OL>
           <LI>rendering material name/</LI>
           <LI>blend mode (ALPHA, ADD, SOLID)</LI>
           <LI>/TEX</LI>
           <LI>/texture file name</LI>
           <LI>/VertCol</LI>
           <LI>/TWOSIDE></LI>
           </OL>
        """
        return self.material.name # for now we need to trick the ogre exporter
        # must be called after _generateKey()
        materialName = self.material.name
        # two sided?
        if self.mesh.uv_textures and (self.face.use_twoside):
            materialName += '/TWOSIDE'
        # use UV/Image Editor texture?
        if self.TEXFACE:
            materialName += '/TEXFACE'
            if self.mesh.uv_textures and self.face.image:
                materialName += '/' + PathName(self.face.image.filepath)
        return materialName

    def getName(self):
        return self._createName()

    def write(self, f):
        f.write("material %s\n" % self.getName())
        f.write("{\n")
        self.writeTechniques(f)
        f.write("}\n")
        return
    
