import bpy
import math
from bl_ui import properties_texture

from . import props, base, node

base.compatify_class(properties_texture.TEXTURE_PT_preview)

class TextureProperty(props.FakeIDProperty):
    ID_NAME = 'texture'
    HUMAN_NAME = 'Texture'
    COLLECTION = 'textures'
    
    def to_scene_data(self, scene, mat):
        tex = self.normalize(mat)
        if tex:
            return W_PT_texture.to_scene_data(scene, tex)
        return None

class FloatTextureProperty(TextureProperty):
    def __init__(self, name, description, default):
        super().__init__(name, description)
        self.properties['value'] = bpy.props.FloatProperty(
            name=name,
            description=description,
            min=0,
            max=1,
            default=default,
        )

    def draw(self, lay, mat):
        row = lay.row(align=True)
        row.prop(mat, self.prefix + 'value')
        super().draw(row, mat, text='')

    def to_scene_data(self, scene, mat):
        tex = super().to_scene_data(scene, mat)
        if tex is None:
            return getattr(mat, self.prefix + 'value')
        return tex

class ColorTextureProperty(TextureProperty):
    def __init__(self, name, description, default):
        super().__init__(name, description)
        self.properties['color'] = bpy.props.FloatVectorProperty(
            name=name,
            description=description,
            subtype='COLOR',
            min=0,
            soft_max=1,
            default=default,
        )

    def draw(self, lay, mat):
        row = lay.row(align=True)
        row.prop(mat, self.prefix + 'color')
        super().draw(row, mat, text='')

    def to_scene_data(self, scene, mat):
        tex = super().to_scene_data(scene, mat)
        if tex is None:
            return list(getattr(mat, self.prefix + 'color'))
        return tex

@node.TungstenNodeTree.register_node('Input')
@props.meta_propertize
class TungstenTextureNode(node.TungstenNode):
    bl_label = 'Texture'

    texture = TextureProperty('Texture', 'Texture')
    
    def init(self, context):
        self.outputs.new('TungstenTextureSocket', 'Texture')

    def to_scene_data(self, scene):
        return self.texture.to_scene_data(scene, self)

    def draw_buttons(self, context, layout):
        self.texture.draw(layout, self, text='')

# try to keep blender in-the-know about the texture type
def update_tex_type(self, context):
    TEX_TYPES = {
        'image': 'IMAGE',
    }
    try:
        tex = context.texture
        if tex is not None:
            tex.type = TEX_TYPES.get(tex.tungsten.type, 'NONE')
    except Exception:
        pass

@base.register_root_panel
class W_PT_texture(properties_texture.TextureButtonsPanel, base.RootPanel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}
    prop_class = bpy.types.Texture

    @classmethod
    def get_object(cls, context):
        return context.texture

    PROPERTIES = {
        'type': bpy.props.EnumProperty(
            name='Texture Type',
            description='Texture Type',
            items=[
                ('image', 'Image', ''),
                ('checker', 'Checker', ''),
                ('disk', 'Disk', ''),
                ('blade', 'Blade', ''),
            ],
            default='checker',
            update=update_tex_type,
        ),
    }

    @classmethod
    def to_scene_data(cls, scene, tex):
        w = tex.tungsten
        d = {'type': w.type}

        if w.type == 'image':
            # this one's very special
            return W_PT_image.to_scene_data(scene, tex)

        d.update(super().to_scene_data(scene, tex))
        return d

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        if not hasattr(context, 'texture_slot'):
            return False

        if engine not in cls.COMPAT_ENGINES:
            return False

        return any([context.material, context.world, context.texture])

    def draw(self, context):
        lay = self.layout
        slot = getattr(context, 'texture_slot', None)
        tex = context.texture
        idblock = properties_texture.context_tex_datablock(context)

        tex_collection = True # aaaah
        if tex_collection:
            row = lay.row()
            row.template_list('TEXTURE_UL_texslots', '', idblock, 'texture_slots', idblock, 'active_texture_index', rows=2)

            col = row.column(align=True)
            col.operator('texture.slot_move', text='', icon='TRIA_UP').type = 'UP'
            col.operator('texture.slot_move', text='', icon='TRIA_DOWN').type = 'DOWN'
            col.menu('TEXTURE_MT_specials', icon='DOWNARROW_HLT', text='')

        if tex_collection:
            lay.template_ID(idblock, 'active_texture', new='texture.new')
        elif idblock:
            lay.template_ID(idblock, 'texture', new='texture.new')

        if tex:
            w = tex.tungsten
            lay.prop(w, 'type')

@base.register_sub_panel
class W_PT_image(W_PT_texture.SubPanel):
    bl_label = 'Image'
    w_type = 'image'

    @classmethod
    def to_scene_data(cls, scene, tex):
        return scene.add_image(tex.image)

    def draw_for_object(self, tex):
        layout = self.layout
        w = tex.tungsten

        layout.template_image(tex, 'image', tex.image_user)

@base.register_sub_panel
class W_PT_checker(W_PT_texture.SubPanel):
    bl_label = 'Checker'
    w_type = 'checker'

    PROPERTIES = {
        'checker_on': bpy.props.FloatVectorProperty(
            name='On Color',
            description='Checker On Color',
            subtype='COLOR',
            min=0.0,
            soft_max=1.0,
            default=(0.8, 0.8, 0.8),
        ),
        
        'checker_off': bpy.props.FloatVectorProperty(
            name='Off Color',
            description='Checker Off Color',
            subtype='COLOR',
            min=0.0,
            soft_max=1.0,
            default=(0.2, 0.2, 0.2),
        ),
        
        'checker_resu': bpy.props.IntProperty(
            name='U',
            description='Checker U Resolution',
            subtype='UNSIGNED',
            min=0,
            default=20,
        ),
        
        'checker_resv': bpy.props.IntProperty(
            name='V',
            description='Checker V Resolution',
            subtype='UNSIGNED',
            min=0,
            default=20,
        ),
    }

    @classmethod
    def to_scene_data(cls, scene, tex):
        w = tex.tungsten
        return {
            'on_color': list(w.checker_on),
            'off_color': list(w.checker_off),
            'res_u': w.checker_resu,
            'res_v': w.checker_resv,
        }

    def draw_for_object(self, tex):
        layout = self.layout
        w = tex.tungsten
        
        layout.prop(w, 'checker_on')
        layout.prop(w, 'checker_off')
        row = layout.row()
        row.label('Resolution:')
        sub = row.row(align=True)
        sub.prop(w, 'checker_resu')
        sub.prop(w, 'checker_resv')

@base.register_sub_panel
class W_PT_blade(W_PT_texture.SubPanel):
    bl_label = 'Blade'
    w_type = 'blade'

    PROPERTIES = {
        'blades': bpy.props.IntProperty(
            name='Blades',
            description='Number of Blades',
            subtype='UNSIGNED',
            min=3,
            soft_max=20,
            default=6,
        ),
        
        'blade_angle': bpy.props.FloatProperty(
            name='Blade Angle',
            description='Blade Angle',
            subtype='ANGLE',
            min=0,
            max=2 * math.pi,
            default=0.5 * math.pi / 6,
        ),
    }

    @classmethod
    def to_scene_data(cls, scene, tex):
        w = tex.tungsten
        return {
            'blades': w.blades,
            'angle': w.blade_angle,
        }

    def draw_for_object(self, tex):
        layout = self.layout
        w = tex.tungsten
        
        layout.prop(w, 'blades')
        layout.prop(w, 'blade_angle')
