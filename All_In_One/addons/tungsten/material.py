import bpy
from bl_ui import properties_material
from .complex_ior_data import data as ior_data
from . import base
from .node import TungstenNodeTree, TungstenNode, NodeTreeProperty

base.compatify_class(properties_material.MATERIAL_PT_preview)
base.compatify_class(properties_material.MATERIAL_PT_custom_props)

@base.register_root_panel
class W_PT_material(properties_material.MaterialButtonsPanel, base.RootPanel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}
    prop_class = bpy.types.Material

    @classmethod
    def get_object(cls, context):
        return context.material
    
    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (context.material or context.object) and (engine in cls.COMPAT_ENGINES)

    PROPERTIES = {
        'material': NodeTreeProperty(
            name='Material',
            description='Material',
        ),
        
        'albedo': bpy.props.FloatVectorProperty(
            name='Albedo',
            description='Albedo',
            subtype='COLOR',
            min=0.0,
            max=1.0,
            default=(0.8, 0.8, 0.8),
        ),

        'emission': bpy.props.FloatVectorProperty(
            name='Emission',
            description='Emission',
            subtype='COLOR',
            min=0.0,
            soft_max=1.0,
            default=(0.0, 0.0, 0.0),
        ),
    }

    @classmethod
    def to_scene_data(self, scene, m):
        w = m.tungsten
        obj = {}
        mat = {}

        ret = w.material.to_scene_data(scene, w)
        if ret:
            obj, mat = ret
        else:
            mat = {
                'type': 'lambert',
                'albedo': list(w.albedo),
            }
            obj = {
                'emission': list(w.emission),
            }
            
        if obj.get('emission') == [0.0, 0.0, 0.0]:
            del obj['emission']

        mat['name'] = m.name
        obj['bsdf'] = m.name

        return obj, mat

    def draw(self, context):
        layout = self.layout

        mat = context.material
        ob = context.object
        slot = context.material_slot
        space = context.space_data

        if ob:
            row = layout.row()
            row.template_list('MATERIAL_UL_matslots', '', ob, 'material_slots', ob, 'active_material_index', rows=1)

            col = row.column(align=True)
            col.operator('object.material_slot_add', icon='ZOOMIN', text='')
            col.operator('object.material_slot_remove', icon='ZOOMOUT', text='')
            col.menu('MATERIAL_MT_specials', icon='DOWNARROW_HLT', text='')

            if ob.mode == 'EDIT':
                row = layout.row(align=True)
                row.operator('object.material_slot_assign', text='Assign')
                row.operator('object.material_slot_select', text='Select')
                row.operator('object.material_slot_deselect', text='Deselect')

        split = layout.split(percentage=0.65)

        if ob:
            split.template_ID(ob, 'active_material', new='material.new')
            row = split.row()
            if slot:
                row.prop(slot, 'link', text='')
            else:
                row.label()
        elif mat:
            split.template_ID(space, 'pin_id')
            split.separator()

        if mat:
            layout.separator()
            w = mat.tungsten

            if not w.material.draw(layout, w):
                layout.prop(w, 'albedo')
                layout.prop(w, 'emission')

@TungstenNodeTree.register_node('Output')
class TungstenMaterialOutputNode(TungstenNode):
    bl_label = 'Material Output'
    w_output = True

    bump_strength = bpy.props.FloatProperty(
        name='Bump Strength',
        description='Bump Strength',
        min=0.0,
        soft_max=10.0,
        default=1.0,
    )

    def init(self, context):
        self.inputs.new('TungstenShaderSocket', 'Material')
        self.inputs.new('TungstenTextureSocket', 'Emission')
        self.inputs['Emission'].default_color = (0.0, 0.0, 0.0)
        self.inputs.new('TungstenTextureSocket', 'Bump')
        self.inputs['Bump'].tex_type = 'PURE'
        self.inputs.new('TungstenMediumSocket', 'Interior')
        self.inputs.new('TungstenMediumSocket', 'Exterior')

    def to_scene_data(self, scene):
        mat = self.inputs['Material'].to_scene_data(scene)
        obj = {
            'emission': self.inputs['Emission'].to_scene_data(scene),
        }

        if self.inputs['Bump'].is_linked:
            obj['bump'] = self.inputs['Bump'].to_scene_data(scene)
            obj['bump_strength'] = self.bump_strength

        i = self.inputs['Interior'].to_scene_data(scene)
        e = self.inputs['Exterior'].to_scene_data(scene)
        if i:
            mat['int_medium'] = i
        if e:
            mat['ext_medium'] = e

        return obj, mat

    def draw_buttons(self, context, layout):
        if self.inputs['Bump'].is_linked:
            layout.prop(self, 'bump_strength')

# base for all material nodes, with albedo and type
class TungstenBSDFNode(TungstenNode):
    w_type = None
    w_has_albedo = True

    def _init(self, context):
        self.outputs.new('TungstenShaderSocket', 'Material')
        if self.w_has_albedo:
            self.inputs.new('TungstenTextureSocket', 'Albedo')

    def _to_scene_data(self, scene):
        d = {'type': self.w_type}
        if self.w_has_albedo:
            d['albedo'] = self.inputs['Albedo'].to_scene_data(scene)
        return d

def lookup_ior(name):
    _, eta, k = [i for i in ior_data if i[0] == name][0]
    return (eta, k)

def update_conductor_material(self, context):
    if self.material != 'CUSTOM':
        self.eta, self.k = lookup_ior(self.material)

# mixin for eta/k (conductors)
class EtaK(TungstenBSDFNode):
    PROPERTIES = {
        'material': bpy.props.EnumProperty(
            name='Material',
            description='Conductor Material',
            items=[
                ('CUSTOM', 'Custom', ''),
            ] + [(n, n, '') for n, _, _ in ior_data],
            default='W',
            update=update_conductor_material,
        ),
        'eta': bpy.props.FloatVectorProperty(
            name='Eta',
            description='Conductor Eta',
            min=0,
            default=lookup_ior('W')[0],
        ),
        'k': bpy.props.FloatVectorProperty(
            name='K',
            description='Conductor K',
            min=0,
            default=lookup_ior('W')[1],
        ),
    }

    def _to_scene_data(self, scene):
        return {
            'eta': list(self.eta),
            'k': list(self.k),
        }

    def _draw_buttons(self, context, layout):
        layout.prop(self, 'material', text='Metal')
        if self.material == 'CUSTOM':
            col = layout.column()
            col.prop(self, 'eta')
            col.prop(self, 'k')

# mixin for bare ior (dielectric)
class IOR(TungstenBSDFNode):
    PROPERTIES = {
        'ior': bpy.props.FloatProperty(
            name='IOR',
            description='Dielectric IOR',
            min=0,
            default=1.5,
        ),
        'enable_refraction': bpy.props.BoolProperty(
            name='Refraction',
            description='Enable Refraction',
            default=True,
        ),
    }

    def _to_scene_data(self, scene):
        return {
            'ior': self.ior,
            'enable_refraction': self.enable_refraction,
        }

    def _draw_buttons(self, context, layout):
        layout.prop(self, 'enable_refraction')
        if self.enable_refraction:
            layout.prop(self, 'ior')

# mixin for ior/thickness/sigma_a (plastic)
class IORThicknessSigmaA(TungstenBSDFNode):
    PROPERTIES = {
        'ior': bpy.props.FloatProperty(
            name='IOR',
            description='Plastic IOR',
            min=0,
            default=1.5,
        ),
        'thickness': bpy.props.FloatProperty(
            name='Thickness',
            description='Plastic Thickness',
            min=0,
            default=1.0,
        ),
        'sigma_a': bpy.props.FloatVectorProperty(
            # FIXME good bounds?
            name='Sigma A',
            description='Plastic Sigma A',
            min=0,
            default=(0.0, 0.0, 0.0),
        ),
    }

    def _to_scene_data(self, scene):
        return {
            'ior': self.ior,
            'thickness': self.thickness,
            'sigma_a': list(self.sigma_a),
        }

    def _draw_buttons(self, context, layout):
        layout.prop(self, 'ior')
        layout.prop(self, 'thickness')
        col = layout.column()
        col.prop(self, 'sigma_a')

# mixin that has a substrate
class Substrate(TungstenBSDFNode):
    w_has_albedo = False
    w_substrate_name = 'substrate'
    
    def _init(self, context):
        self.inputs.new('TungstenShaderSocket', 'Substrate')

    def _to_scene_data(self, scene):
        return {
            self.w_substrate_name: self.inputs['Substrate'].to_scene_data(scene),
        }

# mixin for roughness/distribution
class RoughnessDistribution(TungstenBSDFNode):
    PROPERTIES = {
        'distribution': bpy.props.EnumProperty(
            name='Distribution',
            description='Microfacet Distribution',
            items=[
                ('beckmann', 'Beckmann', ''),
                ('phong', 'Phong', ''),
                ('ggx', 'GGX', ''),
            ],
            default='ggx',
        ),
    }
    
    def _init(self, context):
        self.inputs.new('TungstenTextureSocket', 'Roughness')
        self.inputs['Roughness'].tex_type = 'VALUE'

    def _to_scene_data(self, scene):
        return {
            'roughness': self.inputs['Roughness'].to_scene_data(scene),
            'distribution': self.distribution,
        }

    def _draw_buttons(self, context, layout):
        layout.prop(self, 'distribution')
        
def lookup_ior(name):
    _, eta, k = [i for i in ior_data if i[0] == name][0]
    return (eta, k)

def update_conductor_material(self, context):
    if self.material != 'CUSTOM':
        self.eta, self.k = lookup_ior(self.material)

@TungstenNodeTree.register_node('Materials')
class TungstenConductorNode(EtaK):
    bl_label = 'Conductor'
    w_type = 'conductor'

@TungstenNodeTree.register_node('Materials')
class TungstenDielectricNode(IOR):
    bl_label = 'Dielectric'
    w_type = 'dielectric'

@TungstenNodeTree.register_node('Materials')
class TungstenForwardNode(TungstenBSDFNode):
    bl_label = 'Forward'
    w_type = 'forward'
    w_has_albedo = False

@TungstenNodeTree.register_node('Materials')
class TungstenLambertNode(TungstenBSDFNode):
    bl_label = 'Lambert'
    w_type = 'lambert'

@TungstenNodeTree.register_node('Materials')
class TungsteMirrorNode(TungstenBSDFNode):
    bl_label = 'Mirror'
    w_type = 'mirror'

@TungstenNodeTree.register_node('Materials')
class TungstenMixedNode(TungstenBSDFNode):
    bl_label = 'Mixed'
    w_type = 'mixed'
    w_has_albedo = False
    
    def _init(self, context):
        self.inputs.new('TungstenShaderSocket', 'A')
        self.inputs.new('TungstenShaderSocket', 'B')
        self.inputs.new('TungstenTextureSocket', 'Ratio')
        self.inputs['Ratio'].tex_type = 'VALUE'

    def _to_scene_data(self, scene):
        return {
            'bsdf0': self.inputs['A'].to_scene_data(scene),
            'bsdf1': self.inputs['B'].to_scene_data(scene),
            'ratio': self.inputs['Ratio'].to_scene_data(scene),
        }

@TungstenNodeTree.register_node('Materials')
class TungstenNullNode(TungstenBSDFNode):
    bl_label = 'Null'
    w_type = 'null'
    w_has_albedo = False

@TungstenNodeTree.register_node('Materials')
class TungstenOrenNayarNode(TungstenBSDFNode):
    bl_label = 'Oren Nayar'
    w_type = 'oren_nayar'

    def _init(self, context):
        self.inputs.new('TungstenTextureSocket', 'Roughness')
        self.inputs['Roughness'].tex_type = 'VALUE'

    def _to_scene_data(self, scene):
        return {
            'roughness': self.inputs['Roughness'].to_scene_data(scene),
        }

@TungstenNodeTree.register_node('Materials')
class TungstenPhongNode(TungstenBSDFNode):
    bl_label = 'Phong'
    w_type = 'phong'

    PROPERTIES = {
        'exponent': bpy.props.FloatProperty(
            name='Exponent',
            description='Phong Exponent',
            min=0,
            default=100,
        ),
        'diffuse_ratio': bpy.props.FloatProperty(
            name='Ratio',
            description='Diffuse Ratio',
            min=0,
            max=1,
            default=0.5,
        ),
    }

    def _to_scene_data(self, scene):
        return {
            'exponent': self.exponent,
            'diffuse_ratio': self.diffuse_ratio,
        }

    def _draw_buttons(self, context, layout):
        layout.prop(self, 'exponent')
        layout.prop(self, 'diffuse_ratio')

@TungstenNodeTree.register_node('Materials')
class TungstenPlasticNode(IORThicknessSigmaA):
    bl_label = 'Plastic'
    w_type = 'plastic'

@TungstenNodeTree.register_node('Materials')
class TungstenRoughCoatNode(IORThicknessSigmaA, RoughnessDistribution, Substrate):
    bl_label = 'Rough Coat'
    w_type = 'rough_coat'

@TungstenNodeTree.register_node('Materials')
class TungstenRoughConductorNode(EtaK, RoughnessDistribution):
    bl_label = 'Rough Conductor'
    w_type = 'rough_conductor'

@TungstenNodeTree.register_node('Materials')
class TungstenRoughDielectricNode(IOR, RoughnessDistribution):
    bl_label = 'Rough Dielectric'
    w_type = 'rough_dielectric'

@TungstenNodeTree.register_node('Materials')
class TungstenRoughPlasticNode(IORThicknessSigmaA, RoughnessDistribution):
    bl_label = 'Rough Plastic'
    w_type = 'rough_plastic'

@TungstenNodeTree.register_node('Materials')
class TungstenSmoothCoatNode(IORThicknessSigmaA, Substrate):
    bl_label = 'Smooth Coat'
    w_type = 'smooth_coat'

# FIXME this supports a texture thickness but NOTHING ELSE DOES
@TungstenNodeTree.register_node('Materials')
class TungstenThinSheetNode(IORThicknessSigmaA):
    bl_label = 'Thin Sheet'
    w_type = 'thinsheet'

    PROPERTIES = {
        'enable_interference': bpy.props.BoolProperty(
            name='Interference',
            description='Enable Interference',
            default=False,
        ),
    }

    def _to_scene_data(self, scene):
        return {
            'enable_interference': self.enable_interference,
        }

    def _draw_buttons(self, context, layout):
        layout.prop(self, 'enable_interference')

@TungstenNodeTree.register_node('Materials')
class TungstenTransparencyNode(Substrate):
    bl_label = 'Transparency'
    w_type = 'transparency'
    w_substrate_name = 'base'

    def _init(self, context):
        self.inputs.new('TungstenTextureSocket', 'Alpha')
        self.inputs['Alpha'].tex_type = 'VALUE'

    def _to_scene_data(self, scene):
        return {
            'alpha': self.inputs['Alpha'].to_scene_data(scene),
        }
