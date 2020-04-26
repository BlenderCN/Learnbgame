import bpy
from os import path

class LM_PT_main(bpy.types.Panel):          
    bl_label = "Make Lineup"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Lineup Maker'

    
    def draw(self, context):
        scn = context.scene
        assetPath = bpy.path.abspath(scn.lm_asset_path)
        layout = self.layout

        row = layout.row(align=True)
        if path.exists(assetPath):
            icon = "DOWNARROW_HLT"
        else:
            icon = "BLANK1"
        row.prop(scn, 'lm_asset_path', text = 'Asset Path', icon=icon)
        layout.operator("scene.lm_importfiles", icon='IMPORT', text="Import all assets")

class LM_PT_NamingConvention(bpy.types.Panel):
    bl_label = "Naming Convention"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Lineup Maker"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        scn = context.scene
        layout = self.layout

        # NAMING CONVENTION SETUP
        col = layout.column(align=True)

        col.prop(scn, 'lm_separator', text = 'Separator')

        b = col.box()
        b.label(text='Asset Naming Convention')
        br = b.box()
        bbr = br.split(align=True)
        
        bbr.operator("scene.lm_add_asset_keyword", text='Add', icon='ADD').optionnal = False
        bbr.operator("scene.lm_add_asset_keyword", text='Optionnal', icon='ADD').optionnal = True
        bbr.operator("scene.lm_remove_asset_keyword", text='Remove', icon='REMOVE')
        
        b.prop(scn, 'lm_asset_naming_convention', text='')
        col.separator()

        b = col.box()
        b.label(text='Mesh Naming Convention')
        br = b.box()
        bbr = br.split(align=True)
        bbr.operator("scene.lm_add_mesh_keyword", text='Add', icon='ADD').optionnal = False
        bbr.operator("scene.lm_add_mesh_keyword", text='Optionnal', icon='ADD').optionnal = True
        bbr.operator("scene.lm_remove_mesh_keyword", text='Remove', icon='REMOVE')

        b.prop(scn, 'lm_mesh_naming_convention', text='')
        col.separator()

        b = col.box()
        b.label(text='Texture Naming Convention')
        br = b.box()
        bbr = br.split(align=True)
        bbr.operator("scene.lm_add_texture_keyword", text='Add', icon='ADD').optionnal = False
        bbr.operator("scene.lm_add_texture_keyword", text='Optionnal', icon='ADD').optionnal = True
        bbr.operator("scene.lm_remove_texture_keyword", text='Remove', icon='REMOVE')

        b.prop(scn, 'lm_texture_naming_convention', text='')
        col.separator()

        # Keywords Setup

        col = layout.column(align=True)
        b = col.box()
        b.label(text='Keywords')
        
        row = b.row()
        
        rows = len(scn.lm_keywords) if len(scn.lm_keywords) > 2 else 2
        row.template_list('LM_UL_keywords', '', scn, 'lm_keywords', scn, 'lm_keyword_idx', rows=rows)
        c = row.column(align=True)
        c.operator("scene.lm_move_keyword", text="", icon='TRIA_UP').direction = "UP"
        c.operator("scene.lm_move_keyword", text="", icon='TRIA_DOWN').direction = "DOWN"

        c.separator()
        c.operator("scene.lm_clear_keywords", text="", icon='LOOP_BACK')
        c.operator("scene.lm_remove_keyword", text="", icon='X')
        c.separator()
        c.operator("scene.lm_rename_keyword", text="", icon='OUTLINER_DATA_FONT')

        b.prop(scn, 'lm_keyword_name')

        c.separator()

        col = layout.column(align=True)
        b = col.box()
        b.label(text='Keyword Value')
        row = b.row()
        
        rows = len(scn.lm_keyword_values) if len(scn.lm_keyword_values) > 4 else 4
        row.template_list('LM_UL_keyword_values', '', scn, 'lm_keyword_values', scn, 'lm_keyword_value_idx', rows=rows)
        c = row.column(align=True)
        c.operator("scene.lm_move_keyword_value", text="", icon='TRIA_UP').direction = "UP"
        c.operator("scene.lm_move_keyword_value", text="", icon='TRIA_DOWN').direction = "DOWN"

        c.separator()
        c.operator("scene.lm_clear_keyword_values", text="", icon='LOOP_BACK')
        c.operator("scene.lm_remove_keyword_value", text="", icon='X')
        c.separator()
        c.operator("scene.lm_rename_keyword_value", text="", icon='OUTLINER_DATA_FONT')

        b.prop(scn, 'lm_keyword_value')

        c.separator()
        

class LM_PT_TextureSetSettings(bpy.types.Panel):
    bl_label = "TextureSet Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Lineup Maker"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        scn = context.scene
        assetPath = bpy.path.abspath(scn.lm_asset_path)
        layout = self.layout

        col = layout.column(align=True)
        col.label(text='Shader Name')
        row = col.row()
        
        rows = len(scn.lm_shaders) if len(scn.lm_shaders) > 2 else 2
        row.template_list('LM_UL_shaders', '', scn, 'lm_shaders', scn, 'lm_shader_idx', rows=rows)
        c = row.column(align=True)
        c.operator("scene.lm_move_shader", text="", icon='TRIA_UP').direction = "UP"
        c.operator("scene.lm_move_shader", text="", icon='TRIA_DOWN').direction = "DOWN"

        c.separator()
        c.operator("scene.lm_clear_shaders", text="", icon='LOOP_BACK')
        c.operator("scene.lm_remove_shader", text="", icon='X')
        c.separator()
        c.operator("scene.lm_rename_shader", text="", icon='OUTLINER_DATA_FONT')

        col.prop(scn, 'lm_shader_name')

        c.separator()

        col = layout.column(align=True)
        col.label(text='Channel Name')
        row = col.row()
        
        rows = len(scn.lm_channels) if len(scn.lm_channels) > 4 else 4
        row.template_list('LM_UL_channels', '', scn, 'lm_channels', scn, 'lm_channel_idx', rows=rows)
        c = row.column(align=True)
        c.operator("scene.lm_move_channel", text="", icon='TRIA_UP').direction = "UP"
        c.operator("scene.lm_move_channel", text="", icon='TRIA_DOWN').direction = "DOWN"

        c.separator()
        c.operator("scene.lm_clear_channels", text="", icon='LOOP_BACK')
        c.operator("scene.lm_remove_channel", text="", icon='X')
        c.separator()
        c.operator("scene.lm_rename_channel", text="", icon='OUTLINER_DATA_FONT')

        col.prop(scn, 'lm_channel_name')

        c.separator()
        col.label(text='Texture Name')
        row = col.row()
        
        rows = len(scn.lm_texture_channels) if len(scn.lm_texture_channels) > 4 else 4
        row.template_list('LM_UL_texturesets', '', scn, 'lm_texture_channels', scn, 'lm_texture_channel_idx', rows=rows)
        c = row.column(align=True)
        c.operator("scene.lm_move_texture_channel", text="", icon='TRIA_UP').direction = "UP"
        c.operator("scene.lm_move_texture_channel", text="", icon='TRIA_DOWN').direction = "DOWN"

        c.separator()
        c.operator("scene.lm_clear_texture_channels", text="", icon='LOOP_BACK')
        c.operator("scene.lm_remove_texture_channel", text="", icon='X')
        c.separator()
        c.operator("scene.lm_rename_texture_channel", text="", icon='OUTLINER_DATA_FONT')

        col.prop(scn, 'lm_texture_channel_name')