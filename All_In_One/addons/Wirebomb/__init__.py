import bpy
from . import w_b_scene
from . import b_tools
from . import w_operators
from . import w_var
from . import constants

if 'bpy' in locals():
    import importlib

    if 'w_b_scene' in locals():
        importlib.reload(w_b_scene)

    if 'b_tools' in locals():
        importlib.reload(b_tools)

    if 'w_operators' in locals():
        importlib.reload(w_operators)

    if 'w_var' in locals():
        importlib.reload(w_var)

    if 'constants' in locals():
        importlib.reload(constants)

bl_info = {
    "name": "Wirebomb",
    "author": "Gustaf Blomqvist",
    "version": (1, 1, 3),
    "blender": (2, 79, 0),
    "location": "Properties > Render settings > Wirebomb",
    "description": "Setting up wireframe renders has never been easier!",
    "warning": "",
    "wiki_url": "https://blendermarket.com/products/wirebomb",
    "tracker_url": "https://blendermarket.com/products/wirebomb",
    "category": "Render"
}


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.wirebomb = bpy.props.PointerProperty(type=Wirebomb)


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.wirebomb


if __name__ == '__main__':
    register()


def update_color_wire(self, context):
    """Updates the wireframe material's color."""
    wireframe_method = context.scene.wirebomb.wireframe_method

    if wireframe_method == 'WIREFRAME_FREESTYLE':
        if context.scene.wirebomb.data_freestyle_linestyle in bpy.data.linestyles:
            linestyle = bpy.data.linestyles[context.scene.wirebomb.data_freestyle_linestyle]
            linestyle.color = context.scene.wirebomb.color_wire[0:3]
            linestyle.alpha = context.scene.wirebomb.color_wire[-1]

    elif wireframe_method == 'WIREFRAME_MODIFIER':
        material_name = context.scene.wirebomb.data_material_wire

        if material_name in bpy.data.materials:
            material = bpy.data.materials[material_name]
            new_color = context.scene.wirebomb.color_wire
            renderengine = context.scene.wirebomb.data_renderengine

            if renderengine == 'CYCLES':
                node_color = material.node_tree.nodes['addon_wireframe_color']
                node_color.inputs[0].default_value = new_color[0:3] + (1.0,)

                node_mix = material.node_tree.nodes['addon_wireframe_alpha']
                node_mix.inputs[0].default_value = new_color[-1]

                # updating viewport color
                material.diffuse_color = new_color[0:3]

            elif renderengine == 'BLENDER_RENDER':
                material.diffuse_color = new_color[0:3]
                material.alpha = new_color[-1]


def update_color_clay(self, context):
    """Updates the clay material's color."""
    material_name = context.scene.wirebomb.data_material_clay

    if material_name in bpy.data.materials:
        material = bpy.data.materials[material_name]
        new_color = context.scene.wirebomb.color_clay
        renderengine = context.scene.wirebomb.data_renderengine

        if renderengine == 'CYCLES':
            node_color = material.node_tree.nodes['addon_clay_color']
            node_color.inputs[0].default_value = new_color[0:3] + (1.0, )

            node_mix = material.node_tree.nodes['addon_clay_alpha']
            node_mix.inputs[0].default_value = new_color[-1]

            # updating viewport color
            material.diffuse_color = new_color[0:3]

        elif renderengine == 'BLENDER_RENDER':
            material.diffuse_color = new_color[0:3]
            material.alpha = new_color[-1]


def update_wire_thickness(self, context):
    """Updates the wireframe's thickness."""
    if context.scene.wirebomb.wireframe_method == 'WIREFRAME_FREESTYLE':
        if context.scene.wirebomb.data_freestyle_linestyle in bpy.data.linestyles:
            linestyle = bpy.data.linestyles[context.scene.wirebomb.data_freestyle_linestyle]
            linestyle.thickness = context.scene.wirebomb.slider_wt_freestyle

    elif context.scene.wirebomb.wireframe_method == 'WIREFRAME_MODIFIER':
        for col_obj in context.scene.wirebomb.data_objects_affected:
            if col_obj.name in bpy.data.objects:
                obj = bpy.data.objects[col_obj.name]
                if obj.type == 'MESH':
                    if 'addon_wireframe' in obj.modifiers:
                        obj.modifiers['addon_wireframe'].thickness = context.scene.wirebomb.slider_wt_modifier


def update_cb_composited(self, context):
    if context.scene.wirebomb.wireframe_method != 'WIREFRAME_FREESTYLE':
        context.scene.wirebomb.cb_composited = False


class Wirebomb(bpy.types.PropertyGroup):
    """Stores data for the add-on."""
    
    # render engine used
    data_renderengine = bpy.props.StringProperty()
    
    # names of the materials used
    data_material_wire = bpy.props.StringProperty()
    data_material_clay = bpy.props.StringProperty()

    # freestyle linstyle used in freestyle wireframe method
    data_freestyle_linestyle = bpy.props.StringProperty()

    # objects affected, other and all are saved in these collections
    data_objects_affected = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    data_objects_other = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    data_objects_all = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    # drop-down list with different wireframe methods
    wireframe_method = bpy.props.EnumProperty(
        items=[('WIREFRAME_MODIFIER', 'Modifier', 'Create wireframe using cycles and the wireframe modifier'),
               ('WIREFRAME_FREESTYLE', 'Freestyle', 'Create wireframe using cycles freestyle renderer')],
        name='Method',
        description='Wireframe method',
        default='WIREFRAME_FREESTYLE',
        update=update_cb_composited)

    # checkboxes
    cb_backup = bpy.props.BoolProperty(name='Backup scene', default=True, description="Create a backup scene")
    cb_clear_rlayers = bpy.props.BoolProperty(name='Clear render layers', default=True, description="Remove all previous render layers")
    cb_clear_materials = bpy.props.BoolProperty(name='Clear materials', default=True, description="Remove all previous materials from objects")
    cb_composited = bpy.props.BoolProperty(name='Composited wires', default=False, description="Add the wireframe through composition "
                                                                      "(only available when there is a posibility "
                                                                      "that it is needed)")
    cb_only_selected = bpy.props.BoolProperty(name='Only selected', default=False, description="Only affect the selected meshes")
    cb_ao = bpy.props.BoolProperty(name='AO as light', default=False, description="Use ambient occlusion lighting setup")
    cb_clay = bpy.props.BoolProperty(name='Use clay', default=True, description="Activate the use of clay")
    cb_clay_only = bpy.props.BoolProperty(name='Only clay', default=False, description="Only use clay, don't set up wireframe")
    cb_mat_wire = bpy.props.BoolProperty(name='Use material', default=False, description="Use material from scene as wireframe material")
    cb_mat_clay = bpy.props.BoolProperty(name='Use material', default=False, description="Use material from scene as clay material")

    # color pickers
    color_wire = bpy.props.FloatVectorProperty(name='Wireframe color',
                                               subtype='COLOR',
                                               min=0,
                                               max=1,
                                               size=4,
                                               default=(0.257273, 0.791067, 0.039042, 0.8),
                                               update=update_color_wire,
                                               description="Wireframe color (changes real-time)")
    color_clay = bpy.props.FloatVectorProperty(name='Clay color',
                                               subtype='COLOR',
                                               min=0, max=1,
                                               size=4,
                                               default=(0.019607, 0.019607, 0.019607, 1.0),
                                               update=update_color_clay,
                                               description="Clay color (changes real-time)")

    # materials from prop searches
    material_wire = bpy.props.StringProperty()
    material_clay = bpy.props.StringProperty()

    # layer tables
    layers_affected = bpy.props.BoolVectorProperty(subtype='LAYER',
                                                   size=20,
                                                   default=(True,) + (False,) * 19,
                                                   description="Layers whose meshes will be affected")
    layers_other = bpy.props.BoolVectorProperty(subtype='LAYER',
                                                size=20,
                                                default=(False,) * 20,
                                                description="Layers whose objects will be "
                                                            "included as is, e.g. lights")

    # sliders for the wireframe thickness
    slider_wt_freestyle = bpy.props.FloatProperty(name='Wireframe thickness',
                                                  subtype='NONE',
                                                  precision=3,
                                                  step=10,
                                                  min=0,
                                                  max=10000,
                                                  default=3,
                                                  update=update_wire_thickness,
                                                  description="Wireframe thickness "
                                                              "(changes real-time)")
    slider_wt_modifier = bpy.props.FloatProperty(name='Wireframe thickness',
                                                 subtype='NONE',
                                                 precision=4,
                                                 step=0.01,
                                                 soft_min=0,
                                                 soft_max=1,
                                                 default=0.02,
                                                 update=update_wire_thickness,
                                                 description="Wireframe thickness "
                                                             "(changes real-time)")

    # scene naming text fields
    scene_name_1 = bpy.props.StringProperty(name='Scene name',
                                            default='wireframe',
                                            maxlen=47,
                                            description="The wireframe/clay scene's name")


class WireframePanel(bpy.types.Panel):
    """The panel in the GUI."""

    bl_label = 'Wirebomb'
    bl_idname = 'RENDER_PT_wireframe'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon='WIRE')

    # draws the GUI
    def draw(self, context):
        scene_inst = w_b_scene.BlenderSceneW(context.scene, False)
        scene = scene_inst.get_scene()
        layout = self.layout

        # config file
        row = layout.row(align=True)
        row.label("Config file:")
        row.operator(operator='scene.wirebomb_config_save', icon='SAVE_PREFS')
        row.operator(operator='scene.wirebomb_config_load', icon='FILESEL')

        # box line
        layout.box()

        # method
        layout.separator()
        layout.prop(context.scene.wirebomb, property='wireframe_method')

        # box start
        layout.separator()
        box = layout.box()

        # backup scene
        split = box.split()
        col = split.column()
        row = col.row()
        row.prop(context.scene.wirebomb, property='cb_backup')

        # clear render layers
        row = col.row()
        row.prop(context.scene.wirebomb, property='cb_clear_rlayers')

        # clear materials
        row = col.row()
        row.prop(context.scene.wirebomb, property='cb_clear_materials')

        # composited wires
        row = col.row()

        if scene.wirebomb.wireframe_method == 'WIREFRAME_FREESTYLE':
            if scene.wirebomb.cb_clay_only is True:
                row.active = False
                w_var.cb_composited_active = False

            else:
                w_var.cb_composited_active = True

            row.prop(context.scene.wirebomb, property='cb_composited')

        # only selected
        col = split.column()
        row = col.row()

        if (w_var.error_101 and scene.wirebomb.cb_only_selected and not scene_inst.check_any_selected('MESH')
                and not any(scene.wirebomb.layers_other)):
            row.alert = True

        else:
            w_var.error_101 = False

        row.prop(context.scene.wirebomb, property='cb_only_selected')

        # ao as light
        row = col.row()
        row.prop(context.scene.wirebomb, property='cb_ao')

        # use clay
        row = col.row()
        row.prop(context.scene.wirebomb, property='cb_clay')

        # only clay
        row = col.row()
        row.separator()

        if scene.wirebomb.cb_clay is not True:
            row.active = False
            w_var.cb_clay_only_active = False

        else:
            w_var.cb_clay_only_active = True

        row.prop(context.scene.wirebomb, property='cb_clay_only')
        # box end

        # wire color
        layout.separator()
        row = layout.row()

        if ((scene.wirebomb.cb_mat_wire and
             scene.wirebomb.wireframe_method != 'WIREFRAME_FREESTYLE') or
                (scene.wirebomb.cb_clay_only and w_var.cb_clay_only_active)):
            row.active = False

        row.prop(context.scene.wirebomb, property='color_wire')

        if scene.wirebomb.wireframe_method != 'WIREFRAME_FREESTYLE':

            # use material (wire)
            split = layout.split()
            col = split.column()
            row = col.row()

            if (scene.wirebomb.wireframe_method == 'WIREFRAME_FREESTYLE' or
                    (scene.wirebomb.cb_clay_only and w_var.cb_clay_only_active)):
                row.active = False
                w_var.cb_mat_wire_active = False

            else:
                w_var.cb_mat_wire_active = True

            if scene.wirebomb.cb_mat_wire and scene.wirebomb.material_wire == '':
                row.alert = True

            row.prop(context.scene.wirebomb, property='cb_mat_wire')

            # wire material
            col = split.column()
            row = col.row()

            if (not scene.wirebomb.cb_mat_wire or
                    (scene.wirebomb.cb_clay_only and scene.wirebomb.cb_clay)):
                row.active = False

            row.prop_search(context.scene.wirebomb, 'material_wire', bpy.data, 'materials', text='')

        # clay color
        layout.separator()
        row = layout.row()

        if scene.wirebomb.cb_mat_clay or not scene.wirebomb.cb_clay:
            row.active = False

        row.prop(context.scene.wirebomb, property='color_clay')

        # use material (clay)
        split = layout.split()
        col = split.column()
        row = col.row()

        if not scene.wirebomb.cb_clay:
            row.active = False
            w_var.cb_mat_clay_active = False

        else:
            w_var.cb_mat_clay_active = True

        if scene.wirebomb.cb_mat_clay and scene.wirebomb.material_clay == '':
            row.alert = True

        row.prop(context.scene.wirebomb, property='cb_mat_clay')

        # clay material
        col = split.column()
        row = col.row()

        if not (scene.wirebomb.cb_mat_clay and w_var.cb_mat_clay_active):
            row.active = False

        row.prop_search(context.scene.wirebomb, 'material_clay', bpy.data, 'materials', text='')

        # wire thickness
        layout.separator()
        row = layout.row()

        if scene.wirebomb.wireframe_method == 'WIREFRAME_FREESTYLE':
            row.prop(context.scene.wirebomb, property='slider_wt_freestyle')

        elif scene.wirebomb.wireframe_method == 'WIREFRAME_MODIFIER':
            row.prop(context.scene.wirebomb, property='slider_wt_modifier')

        # 'affected layers' buttons
        layout.separator()
        split = layout.split()
        col = split.column()
        col.label(text='Affected layers:')
        row = col.row(align=True)

        if scene.wirebomb.cb_only_selected:
            col.active = False
            row.active = False

        row.operator(operator='scene.wirebomb_select_layers_affected')
        row.operator(operator='scene.wirebomb_deselect_layers_affected')
        col.prop(context.scene.wirebomb, property='layers_affected', text='')

        # 'other layers' buttons
        col = split.column()
        col.label(text='Other included layers:')
        row = col.row(align=True)
        row.operator(operator='scene.wirebomb_select_layers_other')
        row.operator(operator='scene.wirebomb_deselect_layers_other')
        col.prop(context.scene.wirebomb, property='layers_other', text='')

        # scene name 1
        layout.separator()
        row = layout.row()

        if (w_var.error_301 and len(scene.wirebomb.scene_name_1) == 0 and
                scene.wirebomb.cb_backup):
            row.alert = True

        else:
            w_var.error_301 = False

        row.prop(context.scene.wirebomb, property='scene_name_1')

        # 'set up new' button
        layout.separator()
        row = layout.row()
        row.scale_y = 1.3
        row.operator(operator='scene.wirebomb_set_up_new', icon='WIRE')
        
        # developer info
        layout.separator()
        info = layout.row()
        info.label(text='Developed by Gustaf Blomqvist | v1.1.3')
