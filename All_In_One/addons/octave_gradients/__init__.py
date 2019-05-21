import bpy
import random
from mathutils import Vector
import struct
from bpy.props import PointerProperty

bl_info = {
    "name": "octave gradients",
    "author": "zeffii (aka Dealga McArdle)",
    "version": (0, 0, 4),
    "blender": (2, 7, 6),
    "category": "Node",
    "wiki_url": "",
    "tracker_url": ""
}


hexviz = {
    0: ['lines', '0072bd d95319 edb120 7e2f8e 77ac30 4dbeee a2142f 0072bd d95319 edb120 7e2f8e 77ac30 4dbeee a2142f 0072bd d95319'],
    1: ['pink', '3c0000 653636 814c4c 985d5d ac6c6c be7878 c69184 cda68e d4b898 dac9a1 e1d9aa e7e7b2 ededc8 f3f3dc f9f9ee ffffff'],
    2: ['copper', '000000 150d08 2b1b11 402819 553522 6a422a 805033 955d3b aa6a44 bf784c d48555 ea925d ff9f65 ffad6e ffba76 ffc77f'],
    3: ['bone', '000005 0f0f1a 1e1e2e 2d2d42 3c3c56 4a4a6a 595f79 687388 778797 869ba6 95afb5 a4c3c3 bad2d2 d1e1e1 e8f0f0 ffffff'],
    4: ['gray', '000000 111111 222222 333333 444444 555555 666666 777777 888888 999999 aaaaaa bbbbbb cccccc dddddd eeeeee ffffff'],
    5: ['winter', '0000ff 0011f7 0022ee 0033e6 0044dd 0055d5 0066cc 0077c3 0088bb 0099b3 00aaaa 00bba2 00cc99 00dd91 00ee88 00ff80'],
    6: ['autumn', 'ff0000 ff1100 ff2200 ff3300 ff4400 ff5500 ff6600 ff7700 ff8800 ff9900 ffaa00 ffbb00 ffcc00 ffdd00 ffee00 ffff00'],
    7: ['summer', '008066 118866 229166 339966 44a266 55aa66 66b366 77bb66 88c366 99cc66 aad466 bbdd66 cce666 ddee66 eef766 ffff66'],
    8: ['spring', 'ff00ff ff11ee ff22dd ff33cc ff44bb ff55aa ff6699 ff7788 ff8877 ff9966 ffaa55 ffbb44 ffcc33 ffdd22 ffee11 ffff00'],
    9: ['cool', '00ffff 11eeff 22ddff 33ccff 44bbff 55aaff 6699ff 7788ff 8877ff 9966ff aa55ff bb44ff bf40ff dd22ff ee11ff ff00ff'],
    10: ['hot', '2b0000 550000 800000 aa0000 d50000 ff0000 ff0000 ff5500 ff8000 ffaa00 ffd500 ffff00 ffff40 ffff80 ffffbf ffffff'],
    11: ['hsv', 'ff0000 ff6000 ffbf00 dfff00 80ff00 20ff00 00ff40 00ff9f 00ffff 009fff 0040ff 2000ff 8000ff df00ff ff00bf ff0060'],
    12: ['jet', '0000bf 0000ff 0040ff 0080ff 00bfff 00ffff 40ffbf 80ff80 bfff40 ffff00 ffbf00 ff8000 ff4000 ff0000 bf0000 800000'],
    13: ['parula', '352a87 3145bc 0265e1 0f77db 1388d3 079ccf 07aac1 20b4ad 49bc94 7abf7c a5be6b cabb5c ecb94c fec634 f6dd22 f9fb0e']
}


def hex_to_rgb(rgb_str):
    int_tuple = struct.unpack('BBB', bytes.fromhex(rgb_str))
    return tuple([val / 255 for val in int_tuple])


def generate_pie_nodes(context, nodes, origin):
    node_tree = context.space_data.node_tree
    x, y = context.space_data.cursor_location

    ColorRamp = nodes.new(type="ShaderNodeValToRGB")
    location = (353.9348 + x, 2.7287 + y) if origin == 'search' else (0, 0)
    ColorRamp.location = Vector(location)


def generate_pcts_from_hexviz(mode):
    key = int(mode)
    hexes = hexviz[key][1].split(' ')
    pcts = []
    for i, j in enumerate(hexes):
        pcts.append([round(1 / 16 * 100, 4), list(hex_to_rgb(j)) + [1.0]])
    return pcts


def slice_mutuals(elements, mode):
    procents_and_colors = generate_pcts_from_hexviz(mode)
    # this sections adds or removes elements if you update your
    # procents_and_colors list with more / fewer elements
    diff = len(elements) - len(procents_and_colors)
    if diff > 0:
        for i in range(abs(diff)):
            elements.remove(elements[-1])
    elif diff < 0:
        for i in range(abs(diff)):
            elements.new(position=0.0)

    position = 0
    for idx, section in enumerate(procents_and_colors):
        elements[idx].color = section[1]
        elements[idx].position = position
        position += (section[0] / 100.0)


def make_slices(ctx, nodes, origin):
    cRamp = nodes.get('ColorRamp')
    if not cRamp:
        generate_pie_nodes(ctx, nodes, origin)
        elements = nodes['ColorRamp'].color_ramp.elements
    else:
        elements = cRamp.color_ramp.elements

    mode = ctx.scene.octave_gradients_props.selected_mode
    slice_mutuals(elements, mode)


def external_make_slices(cRamp, mode=0):
    mode = str(mode)
    elements = cRamp.color_ramp.elements
    slice_mutuals(elements, mode)


class OctaveGradientsOps(bpy.types.Operator):
    bl_label = "Octave Cradient Operator"
    bl_idname = "scene.gradient_pusher"

    origin = bpy.props.StringProperty(default='search')
    scripted = bpy.props.BoolProperty(default=False)

    def execute(self, context):
        try:
            space = context.space_data
            node_tree = space.node_tree
            nodes = node_tree.nodes
            make_slices(context, nodes, self.origin)
        except:
            print('external mode')
            bpy.app.driver_namespace['external_octave'] = external_make_slices
        return {'FINISHED'}


class OctaveGradientsPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Octave Gradient Demo"
    bl_idname = "GRADIENT_PT_loader"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'

    @classmethod
    def poll(self, context):
        try:
            return context.space_data.edit_tree.name == 'Shader Nodetree'
        except:
            return False

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        layout.label(text="Pick a gradient")

        r = layout.row(align=True)
        for i in range(16):
            r.prop(scn.octave_gradients_props, 'color_' + str(i), text='')

        r = layout.row()
        r.prop(scn.octave_gradients_props, 'selected_mode', text='')
        r = layout.row()
        r.operator('scene.gradient_pusher', text='set gradient').origin = 'button'


class OctaveGradientsProperties(bpy.types.PropertyGroup):

    @classmethod
    def register(cls):
        Scn = bpy.types.Scene

        Scn.octave_gradients_props = PointerProperty(
            name="internal global properties",
            description="shared properties between operators",
            type=cls,
        )

        def updateColors(self, context):
            props = context.scene.octave_gradients_props
            key = int(props.selected_mode)
            hexes = hexviz[key][1].split(' ')
            for i, j in enumerate(hexes):
                exec('props.color_' + str(i) + ' = hex_to_rgb(j)')

        for i in range(16):
            k = " = bpy.props.FloatVectorProperty(subtype='COLOR', min=0.0, max=1.0)"
            exec('cls.color_' + str(i) + k)

        mode_options = [(str(i), hexviz[i][0], "", i) for i in range(14)]

        cls.selected_mode = bpy.props.EnumProperty(
            items=mode_options,
            description="offers....",
            default="0",
            update=updateColors)

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.octave_gradients_props


def register():
    bpy.types.Scene.OCTAVE_GRADIENTS_CHOICE = bpy.props.StringProperty()
    bpy.utils.register_class(OctaveGradientsProperties)
    bpy.utils.register_class(OctaveGradientsPanel)
    bpy.utils.register_class(OctaveGradientsOps)


def unregister():
    bpy.utils.unregister_class(OctaveGradientsOps)
    bpy.utils.unregister_class(OctaveGradientsPanel)
    bpy.utils.unregister_class(OctaveGradientsProperties)
    del bpy.types.Scene.OCTAVE_GRADIENTS_CHOICE

if __name__ == "__main__":
    register()
