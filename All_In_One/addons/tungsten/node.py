import bpy
import nodeitems_utils
from . import base, props

class NodeTreeProperty(props.FakeIDProperty):
    ID_NAME = 'node_tree'
    HUMAN_NAME = 'Node Tree'
    COLLECTION = 'node_groups'

    def to_scene_data(self, scene, mat):
        ntree = self.normalize(mat)
        if ntree and ntree.output:
            return ntree.output.to_scene_data(scene)
        return None

    def draw(self, layout, mat):
        ntree = self.normalize(mat)

        if not ntree:
            layout.operator('tungsten.use_nodes', icon='NODETREE')
            return False
        else:
            node = ntree.output
            if not node:
                layout.label('No output node')
            else:
                layout.template_node_view(ntree, node, node.inputs['Material'])

            return True

@base.register_class
class W_OT_use_nodes(bpy.types.Operator):
    """Enable nodes on a material"""
    bl_label = "Use Tungsten Nodes"
    bl_idname = 'tungsten.use_nodes'

    @classmethod
    def poll(cls, context):
        return getattr(context, 'material', False) and context.scene.render.engine == 'TUNGSTEN'

    def execute(self, context):
        mat = context.material
        w = mat.tungsten
        
        if w.material.normalize(w):
            return {'FINISHED'}
        
        nt = bpy.data.node_groups.new(mat.name, type='TungstenNodeTree')
        nt.use_fake_user = True
        w.material_node_tree = nt.name
        nt.nodes.new('TungstenMaterialOutputNode')
        
        return {'FINISHED'}

@base.register_class
class TungstenNodeTree(bpy.types.NodeTree):
    bl_idname = 'TungstenNodeTree'
    bl_label = 'Tungsten Node Tree'
    bl_icon = 'TEXTURE_SHADED'

    node_categories = {}

    @classmethod
    def register_node(cls, category):
        def registrar(nodecls):
            base.register_class(nodecls)
            d = cls.node_categories.setdefault(category, [])
            d.append(nodecls)
            return nodecls
        return registrar

    @classmethod
    def register(cls):
        cats = []
        for c, l in cls.node_categories.items():
            cid = c.replace(' ', '').upper()
            items = [nodeitems_utils.NodeItem(nc.__name__) for nc in l]
            cats.append(TungstenNodeCategory(cid, c, items=items))

        nodeitems_utils.register_node_categories('TUNGSTEN', cats)

    @classmethod
    def unregister(cls):
        nodeitems_utils.unregister_node_categories('TUNGSTEN')

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'TUNGSTEN'

    @classmethod
    def get_from_context(cls, context):
        ob = context.active_object
        if ob and ob.type not in {'LAMP', 'CAMERA'}:
            ma = ob.active_material
            if ma:
                ntree = ma.tungsten.material.normalize(ma.tungsten)
                if ntree:
                    return (ntree, ma, ma)
        return (None, None, None)

    @property
    def output(self):
        for n in self.nodes:
            if getattr(n, 'w_output', False):
                return n
        return None

class TungstenNodeCategory(nodeitems_utils.NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'TungstenNodeTree'

# base for all nodes, with some magic for mixins
class TungstenNode(bpy.types.Node):
    w_output = False
    PROPERTIES = {}
    
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'TungstenNodeTree'

    @classmethod
    def get_mro(cls, attribname):
        for k in cls.__mro__:
            vs = vars(k)
            if attribname in vs:
                yield vs[attribname]

    def do_mro(self, methname, *args, **kwargs):
        for meth in self.get_mro(methname):
            yield meth(self, *args, **kwargs)

    @classmethod
    def register(cls):
        for props in cls.get_mro('PROPERTIES'):
            for k, v in props.items():
                if 'register_properties' in dir(v):
                    for kp, vp in v.get_properties(k):
                        setattr(cls, kp, vp)
                else:
                    setattr(cls, k, v)

    @classmethod
    def unregister(cls):
        for props in cls.get_mro('PROPERTIES'):
            for k, v in props.items():
                if 'register_properties' in dir(v):
                    for kp, vp in v.get_properties(k):
                        delattr(cls, kp)
                else:
                    delattr(cls, k)
    
    def init(self, context):
        for _ in self.do_mro('_init', context):
            pass

    def to_scene_data(self, scene):
        d = {}
        for x in self.do_mro('_to_scene_data', scene):
            d.update(x)
        return d

    def draw_buttons(self, context, layout):
        for _ in self.do_mro('_draw_buttons', context, layout):
            pass

@base.register_class
class TungstenShaderSocket(bpy.types.NodeSocket):
    bl_idname = 'TungstenShaderSocket'
    bl_label = 'Tungsten Shader Socket'

    default_value = bpy.props.FloatVectorProperty(
        name='Albedo',
        description='Albedo',
        subtype='COLOR',
        min=0.0,
        max=1.0,
        default=(0.8, 0.8, 0.8),
    )

    def to_scene_data(self, scene):
        if not self.is_linked:
            return {
                'type': 'lambert',
                'albedo': list(self.default_value),
            }
        return self.links[0].from_node.to_scene_data(scene)
    
    def draw_value(self, context, layout, node):
        layout.label(self.name)

    def draw_color(self, context, node):
        return (0.1, 1.0, 0.2, 0.8)

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(self.name)
        else:
            layout.prop(self, 'default_value', text=self.name)

@base.register_class
class TungstenTextureSocket(bpy.types.NodeSocket):
    bl_idname = 'TungstenTextureSocket'
    bl_label = 'Tungsten Texture Socket'

    default_color = bpy.props.FloatVectorProperty(
        name='Color',
        description='Color',
        subtype='COLOR',
        min=0.0,
        soft_max=1.0,
        default=(0.8, 0.8, 0.8),
    )

    default_value = bpy.props.FloatProperty(
        name='Value',
        description='Value',
        min=0.0,
        soft_max=1.0,
        default=0.5,
    )

    tex_type = bpy.props.EnumProperty(
        name='Texture Type',
        description='Texture Type',
        items=[
            ('COLOR', 'Color', ''),
            ('VALUE', 'Value', ''),
            ('PURE', 'Pure', ''),
        ],
        default='COLOR',
    )
    
    def to_scene_data(self, scene):
        if self.is_linked:
            d = self.links[0].from_node.to_scene_data(scene)
            if d:
                return d
        if self.tex_type == 'COLOR':
            return list(self.default_color)
        elif self.tex_type == 'VALUE':
            return self.default_value
        else:
            return 0.0
    
    def draw_value(self, context, layout, node):
        layout.label(self.name)

    def draw_color(self, context, node):
        return (1.0, 0.1, 0.2, 0.8)

    def draw(self, context, layout, node, text):
        if self.tex_type == 'PURE' or self.is_output or self.is_linked:
            layout.label(self.name)
        else:
            if self.tex_type == 'COLOR':
                layout.prop(self, 'default_color', text=self.name)
            elif self.tex_type == 'VALUE':
                layout.prop(self, 'default_value', text=self.name)

@base.register_class
class TungstenMediumSocket(bpy.types.NodeSocket):
    bl_idname = 'TungstenMediumSocket'
    bl_label = 'Tungsten Medium Socket'

    def to_scene_data(self, scene):
        if self.is_linked:
            return self.links[0].from_node.to_scene_data(scene)
    
    def draw_value(self, context, layout, node):
        layout.label(self.name)

    def draw_color(self, context, node):
        return (0.1, 0.2, 1.0, 0.8)

    def draw(self, context, layout, node, text):
        layout.label(self.name)
