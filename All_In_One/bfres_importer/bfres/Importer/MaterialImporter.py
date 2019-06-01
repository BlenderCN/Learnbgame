import logging; log = logging.getLogger(__name__)
import bmesh
import bpy
import bpy_extras
import struct

class MaterialImporter:
    """Imports material from FMDL."""

    def __init__(self, parent, fmdl):
        self.fmdl     = fmdl
        self.operator = parent.operator
        self.context  = parent.context


    def importMaterial(self, fmat):
        """Import specified material."""
        mat = bpy.data.materials.new(fmat.name)
        mat.use_transparency = True
        mat.alpha = 1
        mat.specular_alpha = 1
        mat.specular_intensity = 0  # Do not make materials without specular map shine exaggeratedly.
        self._addCustomProperties(fmat, mat)

        for i, tex in enumerate(fmat.textures):
            log.info("Importing Texture %3d / %3d '%s'...",
                i+1, len(fmat.textures), tex['name'])
            texObj = self._importTexture(fmat, tex)

            # Add texture slot
            # XXX use tex['slot'] if it's ever not -1
            name = tex['name'].split('.')
            if len(name) > 1:
                name, idx = name
            else:
                name = name[0]
                idx  = 0

            mtex                       = mat.texture_slots.add()
            mtex.texture               = texObj
            mtex.texture_coords        = 'UV'
            mtex.emission_color_factor = 0.5
            #mtex.use_map_density       = True
            mtex.mapping               = 'FLAT'
            mtex.use_map_color_diffuse = False

            if name.endswith('_Nrm'): # normal map
                mtex.use_map_normal = True

            elif name.endswith('_Spm'): # specular map
                mtex.use_map_specular = True

            elif name.endswith('_Alb'): # albedo (regular texture)
                mtex.use_map_color_diffuse  = True
                mtex.use_map_color_emission = True
                mtex.use_map_alpha          = True

            elif name.endswith('_AO'): # ambient occlusion
                mtex.use_map_ambient = True

            # also seen:
            # `_Blur_%02d` (in Animal_Bee)
            # `_Damage_Alb`, `_Red_Alb` (in Link)

            else:
                log.warning("Don't know what to do with texture: %s", name)

            param = "uking_texture%d_texcoord" % i
            param = fmat.materialParams.get(param, None)
            if param:
                mat.texture_slots[0].uv_layer = "_u"+param
                #log.debug("Using UV layer %s for texture %s",
                #    param, name)
            else:
                log.warning("No texcoord attribute for texture %d", i)

        return mat


    def _importTexture(self, fmat, tex):
        """Import specified texture to specified material."""
        # do we use the texid anymore?
        texid   = tex['name'].replace('.', '_') # XXX ensure unique
        texture = bpy.data.textures.new(texid, 'IMAGE')
        try:
            texture.image = bpy.data.images[tex['name']]
        except KeyError:
            log.error("Texture not found: '%s'", tex['name'])
        return texture


    def _addCustomProperties(self, fmat, mat):
        """Add render/shader/material parameters and sampler list
        as custom properties on the Blender material object.
        """
        for name, param in fmat.renderParams.items():
            val = param['vals']
            if param['count'] == 1: val = val[0]
            mat['renderParam_'+name] = val

        for name, param in fmat.shaderParams.items():
            mat['shaderParam_'+name] = {
                'type':   param['type']['name'],
                'size':   param['size'],
                'offset': param['offset'],
                'idxs':   param['idxs'],
                'unk00':  param['unk00'],
                'unk14':  param['unk14'],
                'data':   param['data'],
            }

        for name, val in fmat.materialParams.items():
            mat['matParam_'+name] = val

        mat['samplers']    = fmat.samplers
        mat['mat_flags']   = fmat.header['mat_flags']
        mat['section_idx'] = fmat.header['section_idx']
        mat['unkB2']       = fmat.header['unkB2']
        mat['unkB4']       = fmat.header['unkB4']
