from blendergltf.exporters.common import Reference #pylint: disable=import-error,wrong-import-position


class ExtMaterialsLegacy:
    ext_meta = {
        'name': 'BP_materials_legacy',
        'isDraft': True,
    }

    def export_material(self, state, material):
        all_textures = [
            slot for slot in material.texture_slots
            if slot and slot.texture.type == 'IMAGE'
        ]
        diffuse_textures = [
            Reference('textures', t.texture.name, t.texture, None)
            for t in all_textures if t.use_map_color_diffuse
        ]
        emission_textures = [
            Reference('textures', t.texture.name, t.texture, None)
            for t in all_textures
            if (
                (material.use_shadeless and t.use_map_color_diffuse)
                or (not material.use_shadeless and t.use_map_emit)
            )
        ]
        specular_textures = [
            Reference('textures', t.texture.name, t.texture, None)
            for t in all_textures if t.use_map_color_spec
        ]

        diffuse_color = list((material.diffuse_color * material.diffuse_intensity)[:])
        diffuse_color += [material.alpha]
        emission_color = list((material.diffuse_color * material.emit)[:])
        emission_color += [material.alpha]
        specular_color = list((material.specular_color * material.specular_intensity)[:])
        specular_color += [material.specular_alpha]

        gltf = {
            'bpLegacy': {
                'diffuseFactor': diffuse_color,
                'emissionFactor': emission_color,
                'specularFactor': specular_color,
                'ambientFactor': ([material.ambient]*3) + [1.0],
                'shininessFactor': material.specular_hardness,
            }
        }

        def handle_tex(name, tex):
            slotname = '{}Texture'.format(name)
            gltf['bpLegacy'][slotname] = {
                'index': tex,
                'texCoord': 0, # FIXME
            }

            use_srgb = tex.source.image.colorspace_settings.name == 'sRGB'
            gltf['bpLegacy']['{}Srgb'.format(slotname)] = use_srgb

            tex.source = gltf['bpLegacy'][slotname]
            tex.prop = 'index'
            state['references'].append(tex)


        if diffuse_textures:
            handle_tex('diffuse', diffuse_textures[-1])
        if emission_textures:
            handle_tex('emission', emission_textures[-1])
        if specular_textures:
            handle_tex('specular', specular_textures[-1])

        return gltf

    def export(self, state):
        state['extensions_used'].append('BP_materials_legacy')

        # Export materials
        material_pairs = [
            (material, state['output']['materials'][state['refmap'][('materials', material.name)]])
            for material in state['input']['materials']
        ]
        for bl_mat, gl_mat in material_pairs:
            gl_mat['extensions'] = gl_mat.get('extensions', {})
            gl_mat['extensions']['BP_materials_legacy'] = self.export_material(state, bl_mat)
