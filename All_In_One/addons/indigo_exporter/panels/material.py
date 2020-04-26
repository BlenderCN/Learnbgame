import bpy
import bl_ui

from .. core import BL_IDNAME
from .. properties.material import PROPERTY_GROUP_USAGE

class material_subpanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    
    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == BL_IDNAME and (context.material or context.object) and (context.object.active_material)

class indigo_ui_material(material_subpanel, bpy.types.Panel):
    """    Material Type First     """

    bl_label = 'Material Type'
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        row = self.layout.row(align=True)
        indigo_material = context.object.active_material.indigo_material
        row.prop(indigo_material, 'type', text="Type")

class indigo_ui_material_colour(material_subpanel, bpy.types.Panel):
    bl_label = 'Material Colour'
    
    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.object.active_material.indigo_material.type in PROPERTY_GROUP_USAGE['colour']

    def draw(self, context):
        layout = self.layout
        col = self.layout.column()
        indigo_material = context.object.active_material.indigo_material
        indigo_material_colour = indigo_material.indigo_material_colour
         
        '''
        for opt in indigo_material.indigo_material_colour.properties:
            #print(opt)
            col = self.layout.column()
            col.prop(indigo_material.indigo_material_colour, opt['attr'])
        '''

        col = self.layout.column()
        col.prop(indigo_material_colour, 'colour_type', text="Colour Type")
        
        if indigo_material_colour.colour_type == 'spectrum':
            col = self.layout.column()
            col.prop(indigo_material_colour, 'colour_SP_rgb')


        elif indigo_material_colour.colour_type == 'texture':
            col = self.layout.column()
            col.prop_search(indigo_material_colour, 'colour_TX_texture', context.object.active_material, 'texture_slots')
            
            col = self.layout.column()
            col.prop(indigo_material_colour, 'colour_TX_A')
            col.enabled = indigo_material_colour.colour_TX_abc_from_tex == False

            col = self.layout.column()
            col.prop(indigo_material_colour, 'colour_TX_B')
            col.enabled = indigo_material_colour.colour_TX_abc_from_tex == False

            col = self.layout.column()
            col.prop(indigo_material_colour, 'colour_TX_C')
            col.enabled = indigo_material_colour.colour_TX_abc_from_tex == False

            col = self.layout.column()
            col.prop_search(indigo_material_colour, 'colour_TX_uvset', context.object.data, 'uv_textures')

            row = self.layout.row()
            row.prop(indigo_material_colour, 'colour_TX_abc_from_tex')
            row.prop(indigo_material_colour, 'colour_TX_smooth')

            
        elif indigo_material_colour.colour_type == 'shader':
            col = self.layout.column()
            col.prop(indigo_material_colour, 'colour_SH_text', text="Shader Text")
            
class indigo_ui_material_specular(material_subpanel, bpy.types.Panel):
    bl_label = 'Material Specular Settings'
    
    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.object.active_material.indigo_material.type in PROPERTY_GROUP_USAGE['specular']

    def draw(self, context):
        layout = self.layout
        col = self.layout.column()
        indigo_material = context.object.active_material.indigo_material
        indigo_material_specular = indigo_material.indigo_material_specular
         
        row = col.row()
        row.prop(indigo_material_specular, 'type', expand=True)
        
        if indigo_material_specular.type == 'specular':
            row = col.row()
            row.prop(indigo_material_specular, 'transparent')
            row.prop(indigo_material_specular, 'arch_glass')
            row = row.row()
            row.prop(indigo_material_specular, 'single_face')
            if not indigo_material_specular.arch_glass:
                row.active = False
        elif indigo_material_specular.type == 'glossy_transparent':
            #col.prop(indigo_material_specular, 'exponent')
            col.prop(indigo_material_specular, 'roughness')
        
        col.prop_search(indigo_material_specular, 'medium_chooser', context.scene.indigo_material_medium, 'medium')
        
class indigo_ui_material_fastsss(material_subpanel, bpy.types.Panel):
    bl_label = 'Material Fast SSS Settings'
    
    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.object.active_material.indigo_material.type in PROPERTY_GROUP_USAGE['fastsss']

    def draw(self, context):
        layout = self.layout
        col = self.layout.column()
        indigo_material = context.object.active_material.indigo_material
        indigo_material_fastsss = indigo_material.indigo_material_fastsss
         
        row = col.row()
        
        col.prop_search(indigo_material_fastsss, 'medium_chooser', context.scene.indigo_material_medium, 'medium')
        col.prop(indigo_material_fastsss, 'roughness')
        col.prop(indigo_material_fastsss, 'fresnel_scale')
                
class indigo_ui_material_phong(material_subpanel, bpy.types.Panel):
    bl_label = 'Material Phong Settings'
    
    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.object.active_material.indigo_material.type in PROPERTY_GROUP_USAGE['phong']

    def draw(self, context):
        layout = self.layout
        col = self.layout.column()
        indigo_material = context.object.active_material.indigo_material
        indigo_material_phong = indigo_material.indigo_material_phong
         
        col.prop(indigo_material_phong, 'specular_reflectivity')
        col.prop(indigo_material_phong, 'roughness')
        col.prop(indigo_material_phong, 'fresnel_scale')
        col.prop(indigo_material_phong, 'nk_data_type')
        if indigo_material_phong.nk_data_type == 'preset':
            col.prop(indigo_material_phong, 'nk_data_preset')
        elif indigo_material_phong.nk_data_type == 'file':
            col.prop(indigo_material_phong, 'nk_data_file')
        elif indigo_material_phong.nk_data_type == 'none':
            col.prop(indigo_material_phong, 'ior')
        
class indigo_ui_material_coating(material_subpanel, bpy.types.Panel):
    bl_label = 'Material Coating Settings'
    
    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.object.active_material.indigo_material.type in PROPERTY_GROUP_USAGE['coating']

    def draw(self, context):
        layout = self.layout
        col = self.layout.column()
        indigo_material = context.object.active_material.indigo_material
        indigo_material_coating = indigo_material.indigo_material_coating
         
        col.prop(indigo_material_coating, 'interference')
        col.prop(indigo_material_coating, 'thickness')
        col.prop(indigo_material_coating, 'roughness')
        col.prop(indigo_material_coating, 'fresnel_scale')
        col.prop(indigo_material_coating, 'ior')
        col.prop_search(indigo_material_coating, 'substrate_material_index', bpy.data, 'materials')
        
class indigo_ui_material_doublesidedthin(material_subpanel, bpy.types.Panel):
    bl_label = 'Material Double-Sided Thin Settings'
    
    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.object.active_material.indigo_material.type in PROPERTY_GROUP_USAGE['doublesidedthin']

    def draw(self, context):
        layout = self.layout
        col = self.layout.column()
        indigo_material = context.object.active_material.indigo_material
        indigo_material_doublesidedthin = indigo_material.indigo_material_doublesidedthin
         
        col.prop(indigo_material_doublesidedthin, 'front_roughness')
        col.prop(indigo_material_doublesidedthin, 'back_roughness')
        col.prop(indigo_material_doublesidedthin, 'r_f')
        col.prop(indigo_material_doublesidedthin, 'front_fresnel_scale')
        col.prop(indigo_material_doublesidedthin, 'back_fresnel_scale')
        col.prop(indigo_material_doublesidedthin, 'ior')
        col.prop_search(indigo_material_doublesidedthin, 'front_material_index', bpy.data, 'materials', text="Front Material")
        col.prop_search(indigo_material_doublesidedthin, 'back_material_index', bpy.data, 'materials', text="Back Material")
        
class indigo_ui_material_transmittance(material_subpanel, bpy.types.Panel):
    bl_label = 'Material Transmittance'
    
    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.object.active_material.indigo_material.type in PROPERTY_GROUP_USAGE['transmittance']

    def draw(self, context):
        layout = self.layout
        col = self.layout.column()
        indigo_material = context.object.active_material.indigo_material
        indigo_material_transmittance = indigo_material.indigo_material_transmittance
         
        col.prop(indigo_material_transmittance, 'transmittance_type')
        
        if indigo_material_transmittance.transmittance_type == 'texture':
            col = self.layout.column()
            col.prop_search(indigo_material_transmittance, 'transmittance_TX_texture', context.object.active_material, 'texture_slots')
            
            col = self.layout.column()
            col.prop(indigo_material_transmittance, 'transmittance_TX_A')
            col.enabled = indigo_material_transmittance.transmittance_TX_abc_from_tex == False

            col = self.layout.column()
            col.prop(indigo_material_transmittance, 'transmittance_TX_B')
            col.enabled = indigo_material_transmittance.transmittance_TX_abc_from_tex == False

            col = self.layout.column()
            col.prop(indigo_material_transmittance, 'transmittance_TX_C')
            col.enabled = indigo_material_transmittance.transmittance_TX_abc_from_tex == False

            col = self.layout.column()
            col.prop_search(indigo_material_transmittance, 'transmittance_TX_uvset', context.object.data, 'uv_textures')

            row = self.layout.row()
            row.prop(indigo_material_transmittance, 'transmittance_TX_abc_from_tex')
            row.prop(indigo_material_transmittance, 'transmittance_TX_smooth')
        elif indigo_material_transmittance.transmittance_type == 'spectrum':
            col.prop(indigo_material_transmittance, 'transmittance_SP_type')
            if indigo_material_transmittance.transmittance_SP_type == 'rgb':
                col.prop(indigo_material_transmittance, 'transmittance_SP_rgb')
            elif indigo_material_transmittance.transmittance_SP_type == 'uniform':
                row = col.row(align=True)
                row.prop(indigo_material_transmittance, 'transmittance_SP_uniform_val')
                row.prop(indigo_material_transmittance, 'transmittance_SP_uniform_exp')
        elif indigo_material_transmittance.transmittance_type == 'shader':
            col.prop(indigo_material_transmittance, 'transmittance_SH_text', text="Shader Text")
            
class indigo_ui_material_absorption(material_subpanel, bpy.types.Panel):
    bl_label = 'Material Absorption'
    
    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.object.active_material.indigo_material.type in PROPERTY_GROUP_USAGE['absorption']

    def draw(self, context):
        layout = self.layout
        col = self.layout.column()
        indigo_material = context.object.active_material.indigo_material
        indigo_material_absorption = indigo_material.indigo_material_absorption
         
        col.prop(indigo_material_absorption, 'absorption_type')
        
        if indigo_material_absorption.absorption_type == 'texture':
            col = self.layout.column()
            col.prop_search(indigo_material_absorption, 'absorption_TX_texture', context.object.active_material, 'texture_slots')
            
            col = self.layout.column()
            col.prop(indigo_material_absorption, 'absorption_TX_A')
            col.enabled = indigo_material_absorption.absorption_TX_abc_from_tex == False

            col = self.layout.column()
            col.prop(indigo_material_absorption, 'absorption_TX_B')
            col.enabled = indigo_material_absorption.absorption_TX_abc_from_tex == False

            col = self.layout.column()
            col.prop(indigo_material_absorption, 'absorption_TX_C')
            col.enabled = indigo_material_absorption.absorption_TX_abc_from_tex == False

            col = self.layout.column()
            col.prop_search(indigo_material_absorption, 'absorption_TX_uvset', context.object.data, 'uv_textures')

            row = self.layout.row()
            row.prop(indigo_material_absorption, 'absorption_TX_abc_from_tex')
            row.prop(indigo_material_absorption, 'absorption_TX_smooth')
        elif indigo_material_absorption.absorption_type == 'spectrum':
            col.prop(indigo_material_absorption, 'absorption_SP_type')
            if indigo_material_absorption.absorption_SP_type == 'rgb':
                row = col.row()
                row.prop(indigo_material_absorption, 'absorption_SP_rgb')
                col.prop(indigo_material_absorption, 'absorption_SP_rgb_gain')
            elif indigo_material_absorption.absorption_SP_type == 'uniform':
                row = col.row(align=True)
                row.prop(indigo_material_absorption, 'absorption_SP_uniform_val')
                row.prop(indigo_material_absorption, 'absorption_SP_uniform_exp')
        elif indigo_material_absorption.absorption_type == 'shader':
            col.prop(indigo_material_absorption, 'absorption_SH_text', text="Shader Text")
            
class indigo_ui_material_absorption_layer(material_subpanel, bpy.types.Panel):
    bl_label = 'Absorption Layer'
    
    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.object.active_material.indigo_material.type in PROPERTY_GROUP_USAGE['absorption_layer']

    def draw_header(self, context):
        self.layout.prop(context.object.active_material.indigo_material.indigo_material_absorption_layer, "absorption_layer_enabled", text="")
    
    def draw(self, context):
        indigo_material = context.object.active_material.indigo_material
        indigo_material_absorption_layer = indigo_material.indigo_material_absorption_layer
        layout = self.layout
        if indigo_material.indigo_material_absorption_layer.absorption_layer_enabled:
            col = self.layout.column()
             
            col.prop(indigo_material_absorption_layer, 'absorption_layer_type')
            
            if indigo_material_absorption_layer.absorption_layer_type == 'texture':
                col = self.layout.column()
                col.prop_search(indigo_material_absorption_layer, 'absorption_layer_TX_texture', context.object.active_material, 'texture_slots')
                
                col = self.layout.column()
                col.prop(indigo_material_absorption_layer, 'absorption_layer_TX_A')
                col.enabled = indigo_material_absorption_layer.absorption_layer_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop(indigo_material_absorption_layer, 'absorption_layer_TX_B')
                col.enabled = indigo_material_absorption_layer.absorption_layer_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop(indigo_material_absorption_layer, 'absorption_layer_TX_C')
                col.enabled = indigo_material_absorption_layer.absorption_layer_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop_search(indigo_material_absorption_layer, 'absorption_layer_TX_uvset', context.object.data, 'uv_textures')

                row = self.layout.row()
                row.prop(indigo_material_absorption_layer, 'absorption_layer_TX_abc_from_tex')
                row.prop(indigo_material_absorption_layer, 'absorption_layer_TX_smooth')
            elif indigo_material_absorption_layer.absorption_layer_type == 'spectrum':
                col.prop(indigo_material_absorption_layer, 'absorption_layer_SP_type')
                if indigo_material_absorption_layer.absorption_layer_SP_type == 'rgb':
                    row = col.row()
                    row.prop(indigo_material_absorption_layer, 'absorption_layer_SP_rgb')
                    col.prop(indigo_material_absorption_layer, 'absorption_layer_SP_rgb_gain')
                elif indigo_material_absorption_layer.absorption_layer_SP_type == 'uniform':
                    row = col.row(align=True)
                    row.prop(indigo_material_absorption_layer, 'absorption_layer_SP_uniform_val')
                    row.prop(indigo_material_absorption_layer, 'absorption_layer_SP_uniform_exp')
                elif indigo_material_absorption_layer.absorption_layer_SP_type == 'blackbody':
                    row = col.row(align=True)
                    row.prop(indigo_material_absorption_layer, 'absorption_layer_SP_blackbody_temp')
                    row.prop(indigo_material_absorption_layer, 'absorption_layer_SP_blackbody_gain')
            elif indigo_material_absorption_layer.absorption_layer_type == 'shader':
                col.prop(indigo_material_absorption_layer, 'absorption_layer_SH_text', text="Shader Text")
                
class indigo_ui_material_diffuse(material_subpanel, bpy.types.Panel):
    bl_label = 'Material Diffuse Settings'
    
    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.object.active_material.indigo_material.type in PROPERTY_GROUP_USAGE['diffuse']

    def draw(self, context):
        indigo_material = context.object.active_material.indigo_material
        indigo_material_diffuse = indigo_material.indigo_material_diffuse
        
        layout = self.layout
        col = self.layout.column()
        col.prop(indigo_material_diffuse, 'transmitter')
        if not indigo_material_diffuse.transmitter:
            col.prop(indigo_material_diffuse, 'sigma')
        col.prop(indigo_material_diffuse, 'shadow_catcher')
        
class indigo_ui_material_blended(material_subpanel, bpy.types.Panel):
    bl_label = 'Material Blend Settings'
    
    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.object.active_material.indigo_material.type in PROPERTY_GROUP_USAGE['blended']

    def draw(self, context):
        indigo_material = context.object.active_material.indigo_material
        indigo_material_blended = indigo_material.indigo_material_blended
        
        layout = self.layout
        col = self.layout.column()
        col.prop(indigo_material_blended, 'step')
        
        split = col.split(0.8)
        m_a = split.row()
        m_a.prop_search(indigo_material_blended, 'a_index', bpy.data, 'materials')
        row = split.row()
        row.prop(indigo_material_blended, 'a_null')
        if indigo_material_blended.a_null:
            m_a.active = False
            
        split = col.split(0.8)
        m_b = split.row()
        m_b.prop_search(indigo_material_blended, 'b_index', bpy.data, 'materials')
        row = split.row()
        row.prop(indigo_material_blended, 'b_null')
        if indigo_material_blended.b_null:
            m_b.active = False
        
        col.prop(indigo_material_blended, 'factor')
        
class indigo_ui_material_external(material_subpanel, bpy.types.Panel):
    bl_label = 'Material External Settings'
    
    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.object.active_material.indigo_material.type in PROPERTY_GROUP_USAGE['external']

    def draw(self, context):
        indigo_material = context.object.active_material.indigo_material
        indigo_material_external = indigo_material.indigo_material_external
        
        layout = self.layout
        col = self.layout.column()
        col.operator('WM_OT_url_open', 'Open materials database', 'URL').url = 'http://www.indigorenderer.com/materials/'
        col.prop(indigo_material_external, 'filename')
        col = col.column()
        col.prop(indigo_material_external, 'material_name')
        col.enabled = False
        
class indigo_ui_material_bumpmap(material_subpanel, bpy.types.Panel):
    bl_label = 'Material Bump Map'
    
    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.object.active_material.indigo_material.type in PROPERTY_GROUP_USAGE['bumpmap']

    def draw_header(self, context):
        self.layout.prop(context.object.active_material.indigo_material.indigo_material_bumpmap, "bumpmap_enabled", text="")
    
    def draw(self, context):
        indigo_material = context.object.active_material.indigo_material
        indigo_material_bumpmap = indigo_material.indigo_material_bumpmap
        
        layout = self.layout
        if indigo_material_bumpmap.bumpmap_enabled:
            col = self.layout.column()
            col.prop(indigo_material_bumpmap, 'bumpmap_type')
            if indigo_material_bumpmap.bumpmap_type == 'texture':
                col = self.layout.column()
                col.prop_search(indigo_material_bumpmap, 'bumpmap_TX_texture', context.object.active_material, 'texture_slots')
                
                col = self.layout.column()
                col.prop(indigo_material_bumpmap, 'bumpmap_TX_A')
                col.enabled = indigo_material_bumpmap.bumpmap_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop(indigo_material_bumpmap, 'bumpmap_TX_B')
                col.enabled = indigo_material_bumpmap.bumpmap_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop(indigo_material_bumpmap, 'bumpmap_TX_C')
                col.enabled = indigo_material_bumpmap.bumpmap_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop_search(indigo_material_bumpmap, 'bumpmap_TX_uvset', context.object.data, 'uv_textures')

                row = self.layout.row()
                row.prop(indigo_material_bumpmap, 'bumpmap_TX_abc_from_tex')
                row.prop(indigo_material_bumpmap, 'bumpmap_TX_smooth')
            elif indigo_material_bumpmap.bumpmap_type == 'shader':
                col.prop(indigo_material_bumpmap, 'bumpmap_SH_text', text="Shader Text")
                
class indigo_ui_material_normalmap(material_subpanel, bpy.types.Panel):
    bl_label = 'Material Normal Map'
    
    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.object.active_material.indigo_material.type in PROPERTY_GROUP_USAGE['normalmap']

    def draw_header(self, context):
        self.layout.prop(context.object.active_material.indigo_material.indigo_material_normalmap, "normalmap_enabled", text="")
    
    def draw(self, context):
        indigo_material = context.object.active_material.indigo_material
        indigo_material_normalmap = indigo_material.indigo_material_normalmap
        
        layout = self.layout
        if indigo_material_normalmap.normalmap_enabled:
            col = self.layout.column()
            col.prop(indigo_material_normalmap, 'normalmap_type')
            if indigo_material_normalmap.normalmap_type == 'texture':
                col = self.layout.column()
                col.prop_search(indigo_material_normalmap, 'normalmap_TX_texture', context.object.active_material, 'texture_slots')
                
                col = self.layout.column()
                col.prop(indigo_material_normalmap, 'normalmap_TX_A')
                col.enabled = indigo_material_normalmap.normalmap_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop(indigo_material_normalmap, 'normalmap_TX_B')
                col.enabled = indigo_material_normalmap.normalmap_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop(indigo_material_normalmap, 'normalmap_TX_C')
                col.enabled = indigo_material_normalmap.normalmap_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop_search(indigo_material_normalmap, 'normalmap_TX_uvset', context.object.data, 'uv_textures')

                row = self.layout.row()
                row.prop(indigo_material_normalmap, 'normalmap_TX_abc_from_tex')
                row.prop(indigo_material_normalmap, 'normalmap_TX_smooth')
            elif indigo_material_normalmap.normalmap_type == 'shader':
                col.prop(indigo_material_normalmap, 'normalmap_SH_text', text="Shader Text")
                
class indigo_ui_material_displacement(material_subpanel, bpy.types.Panel):
    bl_label = 'Material Displacement Map'
    
    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.object.active_material.indigo_material.type in PROPERTY_GROUP_USAGE['displacement']

    def draw_header(self, context):
        self.layout.prop(context.object.active_material.indigo_material.indigo_material_displacement, "displacement_enabled", text="")
    
    def draw(self, context):
        indigo_material = context.object.active_material.indigo_material
        indigo_material_displacement = indigo_material.indigo_material_displacement
        
        layout = self.layout
        if indigo_material_displacement.displacement_enabled:
            col = self.layout.column()
            col.prop(indigo_material_displacement, 'displacement_type')
            if indigo_material_displacement.displacement_type == 'texture':
                col = self.layout.column()
                col.prop_search(indigo_material_displacement, 'displacement_TX_texture', context.object.active_material, 'texture_slots')
                
                col = self.layout.column()
                col.prop(indigo_material_displacement, 'displacement_TX_A')
                col.enabled = indigo_material_displacement.displacement_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop(indigo_material_displacement, 'displacement_TX_B')
                col.enabled = indigo_material_displacement.displacement_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop(indigo_material_displacement, 'displacement_TX_C')
                col.enabled = indigo_material_displacement.displacement_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop_search(indigo_material_displacement, 'displacement_TX_uvset', context.object.data, 'uv_textures')

                row = self.layout.row()
                row.prop(indigo_material_displacement, 'displacement_TX_abc_from_tex')
                row.prop(indigo_material_displacement, 'displacement_TX_smooth')
            elif indigo_material_displacement.displacement_type == 'shader':
                col.prop(indigo_material_displacement, 'displacement_SH_text', text="Shader Text")


class indigo_ui_material_roughness(material_subpanel, bpy.types.Panel):
    bl_label = 'Material Roughness Map'
    
    @classmethod
    def poll(cls, context):
        #return super().poll(context) and context.object.active_material.indigo_material.type in PROPERTY_GROUP_USAGE['roughness'] and (False if context.object.active_material.indigo_material.type == 'specular' and context.object.active_material.indigo_material.indigo_material_specular.type != 'glossy_transparent' else True)
        if super().poll(context) and context.object.active_material.indigo_material.type in PROPERTY_GROUP_USAGE['roughness']:
            if context.object.active_material.indigo_material.type == 'specular' and context.object.active_material.indigo_material.indigo_material_specular.type == 'specular':
                return False
            return True
        return False
            
            

    def draw_header(self, context):
        self.layout.prop(context.object.active_material.indigo_material.indigo_material_roughness, "roughness_enabled", text="")
    
    def draw(self, context):
        indigo_material = context.object.active_material.indigo_material
        indigo_material_roughness = indigo_material.indigo_material_roughness
        
        layout = self.layout
        if indigo_material_roughness.roughness_enabled:
            col = self.layout.column()
            col.prop(indigo_material_roughness, 'roughness_type')
            if indigo_material_roughness.roughness_type == 'texture':
                col = self.layout.column()
                col.prop_search(indigo_material_roughness, 'roughness_TX_texture', context.object.active_material, 'texture_slots')
                
                col = self.layout.column()
                col.prop(indigo_material_roughness, 'roughness_TX_A')
                col.enabled = indigo_material_roughness.roughness_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop(indigo_material_roughness, 'roughness_TX_B')
                col.enabled = indigo_material_roughness.roughness_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop(indigo_material_roughness, 'roughness_TX_C')
                col.enabled = indigo_material_roughness.roughness_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop_search(indigo_material_roughness, 'roughness_TX_uvset', context.object.data, 'uv_textures')

                row = self.layout.row()
                row.prop(indigo_material_roughness, 'roughness_TX_abc_from_tex')
                row.prop(indigo_material_roughness, 'roughness_TX_smooth')
            elif indigo_material_roughness.roughness_type == 'shader':
                col.prop(indigo_material_roughness, 'roughness_SH_text', text="Shader Text")
                
class indigo_ui_material_fresnel_scale(material_subpanel, bpy.types.Panel):
    bl_label = 'Material Fresnel Scale Map'
    
    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.object.active_material.indigo_material.type in PROPERTY_GROUP_USAGE['fresnel_scale']

    def draw_header(self, context):
        self.layout.prop(context.object.active_material.indigo_material.indigo_material_fresnel_scale, "fresnel_scale_enabled", text="")
    
    def draw(self, context):
        indigo_material = context.object.active_material.indigo_material
        indigo_material_fresnel_scale = indigo_material.indigo_material_fresnel_scale
        
        layout = self.layout
        if indigo_material_fresnel_scale.fresnel_scale_enabled:
            col = self.layout.column()
            col.prop(indigo_material_fresnel_scale, 'fresnel_scale_type')
            if indigo_material_fresnel_scale.fresnel_scale_type == 'texture':
                col = self.layout.column()
                col.prop_search(indigo_material_fresnel_scale, 'fresnel_scale_TX_texture', context.object.active_material, 'texture_slots')
                
                col = self.layout.column()
                col.prop(indigo_material_fresnel_scale, 'fresnel_scale_TX_A')
                col.enabled = indigo_material_fresnel_scale.fresnel_scale_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop(indigo_material_fresnel_scale, 'fresnel_scale_TX_B')
                col.enabled = indigo_material_fresnel_scale.fresnel_scale_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop(indigo_material_fresnel_scale, 'fresnel_scale_TX_C')
                col.enabled = indigo_material_fresnel_scale.fresnel_scale_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop_search(indigo_material_fresnel_scale, 'fresnel_scale_TX_uvset', context.object.data, 'uv_textures')

                row = self.layout.row()
                row.prop(indigo_material_fresnel_scale, 'fresnel_scale_TX_abc_from_tex')
                row.prop(indigo_material_fresnel_scale, 'fresnel_scale_TX_smooth')
            elif indigo_material_fresnel_scale.fresnel_scale_type == 'shader':
                col.prop(indigo_material_fresnel_scale, 'fresnel_scale_SH_text', text="Shader Text")
                
class indigo_ui_material_blendmap(material_subpanel, bpy.types.Panel):
    bl_label = 'Material Blend Map'
    
    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.object.active_material.indigo_material.type in PROPERTY_GROUP_USAGE['blendmap']

    def draw_header(self, context):
        self.layout.prop(context.object.active_material.indigo_material.indigo_material_blendmap, "blendmap_enabled", text="")
    
    def draw(self, context):
        indigo_material = context.object.active_material.indigo_material
        indigo_material_blendmap = indigo_material.indigo_material_blendmap
        
        layout = self.layout
        if indigo_material_blendmap.blendmap_enabled:
            col = self.layout.column()
            col.prop(indigo_material_blendmap, 'blendmap_type')
            if indigo_material_blendmap.blendmap_type == 'texture':
                col = self.layout.column()
                col.prop_search(indigo_material_blendmap, 'blendmap_TX_texture', context.object.active_material, 'texture_slots')
                
                col = self.layout.column()
                col.prop(indigo_material_blendmap, 'blendmap_TX_A')
                col.enabled = indigo_material_blendmap.blendmap_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop(indigo_material_blendmap, 'blendmap_TX_B')
                col.enabled = indigo_material_blendmap.blendmap_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop(indigo_material_blendmap, 'blendmap_TX_C')
                col.enabled = indigo_material_blendmap.blendmap_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop_search(indigo_material_blendmap, 'blendmap_TX_uvset', context.object.data, 'uv_textures')

                row = self.layout.row()
                row.prop(indigo_material_blendmap, 'blendmap_TX_abc_from_tex')
                row.prop(indigo_material_blendmap, 'blendmap_TX_smooth')
            elif indigo_material_blendmap.blendmap_type == 'shader':
                col.prop(indigo_material_blendmap, 'blendmap_SH_text', text="Shader Text")
                
class indigo_ui_material_emission(material_subpanel, bpy.types.Panel):
    bl_label = 'Material Emission'
    
    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.object.active_material.indigo_material.type in PROPERTY_GROUP_USAGE['emission']

    def draw_header(self, context):
        self.layout.prop(context.object.active_material.indigo_material.indigo_material_emission, "emission_enabled", text="")
    
    def draw(self, context):
        indigo_material = context.object.active_material.indigo_material
        indigo_material_emission = indigo_material.indigo_material_emission
        
        layout = self.layout
        if indigo_material_emission.emission_enabled:
            col = self.layout.column()
            #
            col.prop(indigo_material_emission, 'emission_type')
            
            if indigo_material_emission.emission_type == 'texture':
                col = self.layout.column()
                col.prop_search(indigo_material_emission, 'emission_TX_texture', context.object.active_material, 'texture_slots')
                
                col = self.layout.column()
                col.prop(indigo_material_emission, 'emission_TX_A')
                col.enabled = indigo_material_emission.emission_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop(indigo_material_emission, 'emission_TX_B')
                col.enabled = indigo_material_emission.emission_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop(indigo_material_emission, 'emission_TX_C')
                col.enabled = indigo_material_emission.emission_TX_abc_from_tex == False

                col = self.layout.column()
                col.prop_search(indigo_material_emission, 'emission_TX_uvset', context.object.data, 'uv_textures')

                row = col.row()
                row.prop(indigo_material_emission, 'emission_TX_abc_from_tex')
                row.prop(indigo_material_emission, 'emission_TX_smooth')
            elif indigo_material_emission.emission_type == 'spectrum':
                col.prop(indigo_material_emission, 'emission_SP_type')
                if indigo_material_emission.emission_SP_type == 'rgb':
                    row = col.row()
                    row.prop(indigo_material_emission, 'emission_SP_rgb')
                    #col.prop(indigo_material_emission, 'emission_SP_rgb_gain')
                elif indigo_material_emission.emission_SP_type == 'uniform':
                    row = col.row(align=True)
                    row.prop(indigo_material_emission, 'emission_SP_uniform_val')
                    row.prop(indigo_material_emission, 'emission_SP_uniform_exp')
                elif indigo_material_emission.emission_SP_type == 'blackbody':
                    row = col.row(align=True)
                    row.prop(indigo_material_emission, 'emission_SP_blackbody_temp')
                    row.prop(indigo_material_emission, 'emission_SP_blackbody_gain')
            #
            
            col.separator()
            col.prop_search(indigo_material_emission, 'emit_layer', context.scene.indigo_lightlayers, 'lightlayers')
            
            col.separator()
            col.prop(indigo_material_emission, 'emission_scale')
            if indigo_material_emission.emission_scale:
                row = col.row(align=True)
                row.prop(indigo_material_emission, 'emission_scale_value')
                row.prop(indigo_material_emission, 'emission_scale_exp')
                col.prop(indigo_material_emission, 'emission_scale_measure')
            else:
                col.prop(indigo_material_emission, 'emit_power')
                row = col.row(align=True)
                row.prop(indigo_material_emission, 'emit_gain_val')
                row.prop(indigo_material_emission, 'emit_gain_exp')
            
            col.separator()    
            col.prop(indigo_material_emission, 'em_sampling_mult')
            col.prop(indigo_material_emission, 'emit_ies')
            if indigo_material_emission.emit_ies:
                col.prop(indigo_material_emission, 'emit_ies_path')
            
            col.prop(indigo_material_emission, 'backface_emit')
            
### medium ###
            
class Indigo_Medium_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, 'name', text='', emboss=False, translate=False)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("")
            
class indigo_ui_material_medium(material_subpanel, bpy.types.Panel):
    bl_label = 'Indigo Medium'
    
    def draw(self, context):
        indigo_material = context.object.active_material.indigo_material
        #indigo_material_emission = indigo_material.indigo_material_emission
        
        layout = self.layout
        col = self.layout.column()
        #
        indigo_medium = context.scene.indigo_material_medium
        col.template_list("Indigo_Medium_UL_List", "Profile_List", indigo_medium, "medium", indigo_medium, "medium_index", rows=5)
        row = col.row(align=True)
        row.operator('indigo.medium_add', icon='ZOOMIN')
        row.operator('indigo.medium_remove', icon='ZOOMOUT')
        
        if len(context.scene.indigo_material_medium.medium) > 0:
            current_med_ind = context.scene.indigo_material_medium.medium_index
            current_med = context.scene.indigo_material_medium.medium[current_med_ind]

            col.prop(current_med, 'name')
            col.prop(current_med, 'medium_type')
            if current_med.medium_type == 'basic':
                col.prop(current_med, 'precedence')
                row = col.row(align=True)
                row.prop(current_med, 'medium_ior', slider=True)
                row.prop(current_med, 'medium_cauchy_b', slider=True)
                
                col.prop(current_med, 'medium_type_SP_type')
                if current_med.medium_type_SP_type == 'rgb':
                    row = col.row()
                    row.prop(current_med, 'medium_type_SP_rgb')
                    col.prop(current_med, 'medium_type_SP_rgb_gain')
                elif current_med.medium_type_SP_type == 'uniform':
                    row = col.row(align=True)
                    row.prop(current_med, 'medium_type_SP_uniform_val')
                    row.prop(current_med, 'medium_type_SP_uniform_exp')
                
                col.prop(current_med, 'sss')
                if current_med.sss:
                    col.prop(current_med, 'fast_sss')
                    col.prop(current_med, 'sss_scatter_SP_type')
                    if current_med.sss_scatter_SP_type == 'rgb':
                        row = col.row()
                        row.prop(current_med, 'sss_scatter_SP_rgb')
                        col.prop(current_med, 'sss_scatter_SP_rgb_gain')
                    elif current_med.sss_scatter_SP_type == 'uniform':
                        row = col.row(align=True)
                        row.prop(current_med, 'sss_scatter_SP_uniform_val')
                        row.prop(current_med, 'sss_scatter_SP_uniform_exp')
                    col.separator()
                        
                    col.prop(current_med, 'sss_phase_function')
                    if current_med.sss_phase_function == 'hg':
                        col.prop(current_med, 'sss_phase_hg_SP_type')
                        if current_med.sss_phase_hg_SP_type == 'rgb':
                            row = col.row()
                            row.prop(current_med, 'sss_phase_hg_SP_rgb')
                            col.prop(current_med, 'sss_phase_hg_SP_rgb_gain')
                        elif current_med.sss_phase_hg_SP_type == 'uniform':
                            row = col.row(align=True)
                            row.prop(current_med, 'sss_phase_hg_SP_uniform_val')
                            row.prop(current_med, 'sss_phase_hg_SP_uniform_exp')
                        
            elif current_med.medium_type == 'dermis':
                col.prop(current_med, 'precedence')
                col.prop(current_med, 'medium_haemoglobin', slider=True)
            if current_med.medium_type == 'epidermis':
                col.prop(current_med, 'precedence')
                row = col.row(align=True)
                row.prop(current_med, 'medium_melanin', slider=True)
                row.prop(current_med, 'medium_eumelanin', slider=True)
