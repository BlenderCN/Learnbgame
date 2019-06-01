import bpy, re

def get_keyword(context):
    idx = context.scene.lm_keyword_idx
    keywords = context.scene.lm_keywords

    active = keywords[idx] if keywords else None

    return idx, keywords, active

def add_keyword(context, naming_convention, keyword, optionnal):
    if len(naming_convention):
        return '{}{}{}{}{}{}'.format(naming_convention, context.scene.lm_separator, '<', keyword,('?' if optionnal else '' ),  '>')
    else:
        return '{}{}{}{}{}'.format(naming_convention, '<', keyword, ('?' if optionnal else '' ),  '>')

def slice_keyword(context, convention):
    keyword_pattern = re.compile(r'[{0}]?(<[a-zA-Z0-9^?]+>|[a-zA-Z0-9]+)[{0}]?'.format(context.scene.lm_separator), re.IGNORECASE)
    return keyword_pattern.findall(convention)

def remove_keyword(context, convention):
    scn = context.scene
    keyword = slice_keyword(context, convention)
        
    new_keyword = ''
    
    length = len(keyword)
    for i,k in enumerate(keyword):
        if i < length - 1:
            new_keyword = new_keyword + k
        if i < length - 2:
            new_keyword = new_keyword + scn.lm_separator

    return new_keyword

class LM_UI_AddAssetKeyword(bpy.types.Operator):
    bl_idname = "scene.lm_add_asset_keyword"
    bl_label = "Add Keyword to the current asset naming convention"
    bl_options = {'REGISTER', 'UNDO'}

    keyword: bpy.props.StringProperty(default='')
    optionnal: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        if self.keyword == '':
            _, _, keyword = get_keyword(context)

        context.scene.lm_asset_naming_convention = add_keyword(context, context.scene.lm_asset_naming_convention, keyword.name.upper(), self.optionnal)

        return {'FINISHED'}

class LM_UI_AddMeshKeyword(bpy.types.Operator):
    bl_idname = "scene.lm_add_mesh_keyword"
    bl_label = "Add Keyword to the current mesh naming convention"
    bl_options = {'REGISTER', 'UNDO'}

    keyword: bpy.props.StringProperty(default='')
    optionnal: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        if self.keyword == '':
            _, _, keyword = get_keyword(context)

        context.scene.lm_mesh_naming_convention = add_keyword(context, context.scene.lm_mesh_naming_convention, keyword.name.upper(), self.optionnal)

        return {'FINISHED'}

class LM_UI_AddTextureKeyword(bpy.types.Operator):
    bl_idname = "scene.lm_add_texture_keyword"
    bl_label = "Add Keyword to the current texture naming convention"
    bl_options = {'REGISTER', 'UNDO'}

    keyword: bpy.props.StringProperty(default='')
    optionnal: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        if self.keyword == '':
            _, _, keyword = get_keyword(context)

        context.scene.lm_texture_naming_convention = add_keyword(context, context.scene.lm_texture_naming_convention, keyword.name.upper(), self.optionnal)

        return {'FINISHED'}


class LM_UI_RemoveAssetKeyword(bpy.types.Operator):
    bl_idname = "scene.lm_remove_asset_keyword"
    bl_label = "Remove Keyword to the current asset naming convention"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene

        scn.lm_asset_naming_convention = remove_keyword(context, scn.lm_asset_naming_convention)

        return {'FINISHED'}

class LM_UI_RemoveMeshKeyword(bpy.types.Operator):
    bl_idname = "scene.lm_remove_mesh_keyword"
    bl_label = "Remove Keyword to the current mesh naming convention"
    bl_options = {'REGISTER', 'UNDO'}

    keyword: bpy.props.StringProperty(default='')

    def execute(self, context):
        scn = context.scene

        scn.lm_mesh_naming_convention = remove_keyword(context, scn.lm_mesh_naming_convention)
        return {'FINISHED'}

class LM_UI_RemoveTextureKeyword(bpy.types.Operator):
    bl_idname = "scene.lm_remove_texture_keyword"
    bl_label = "Remove Keyword to the current texture naming convention"
    bl_options = {'REGISTER', 'UNDO'}

    keyword: bpy.props.StringProperty(default='')

    def execute(self, context):
        scn = context.scene

        scn.lm_texture_naming_convention = remove_keyword(context, scn.lm_texture_naming_convention)
        return {'FINISHED'}