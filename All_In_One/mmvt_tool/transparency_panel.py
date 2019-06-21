import bpy
import mmvt_utils as mu


def _addon():
    return TransparencyPanel.addon


def set_layer_weight(val):
    for obj in mu.get_hemis_objs():
        obj.active_material.node_tree.nodes['Layer Weight'].inputs['Blend'].default_value = val


def layer_weight_update(self, context):
    set_layer_weight(bpy.context.scene.appearance_layer_weight)


def appearance_update(self=None, context=None):
    _addon().make_brain_solid_or_transparent()
    _addon().set_layers_depth_trans()
    if bpy.data.objects.get('seghead', None) is not None:
        try:
            bpy.data.materials['seghead_mat'].node_tree.nodes["Mix Shader.002"].inputs[0].default_value = \
                1 - bpy.context.scene.appearance_seghead_trans
        except:
            print('No seghead_mat mix shader')


def set_brain_transparency(val):
    if 0 <= val <= 1:
        bpy.context.scene.appearance_solid_slider = 1 - val
        appearance_update()
    else:
        print('transparency value must be between 0 (not transparent) and 1')


def set_head_transparency(val):
    if 0 <= val <= 1:
        bpy.context.scene.appearance_seghead_trans = val
        appearance_update()
    else:
        print('transparency value must be between 0 (not transparent) and 1')


def set_light_layers_depth(val):
    if 0 <= val <= 10:
        bpy.context.scene.appearance_depth_slider = val
        appearance_update()
    else:
        print('light layers depth must be between 0 and 10')


def transparency_draw(self, context):
    layout = self.layout
    if context.scene.filter_view_type == 'rendered' and bpy.context.scene.appearance_show_rois_activity == 'activity':
    # if context.scene.filter_view_type == 'RENDERED' and bpy.context.scene.appearance_show_activity_layer is True:
        layout.prop(context.scene, 'appearance_solid_slider', text="Show solid brain")
        layout.prop(context.scene, 'appearance_depth_slider', text="Depth")
        if bpy.data.objects.get('seghead', None) is not None:
            layout.prop(context.scene, 'appearance_seghead_trans', text="Transparent head")
        layout.prop(context.scene, 'appearance_layer_weight', text='Light weight')
    else:
        layout.label(text='This panel works only in rendered brain and activity map mode')


class UpdateAppearance(bpy.types.Operator):
    bl_idname = "mmvt.appearance_update"
    bl_label = "filter clear"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        _addon().make_brain_solid_or_transparent()
        _addon().set_layers_depth_trans()
        return {"FINISHED"}


class TransparencyPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Transparency"
    addon = None
    init = False

    def draw(self, context):
        transparency_draw(self, context)


bpy.types.Scene.appearance_solid_slider = bpy.props.FloatProperty(default=1.0, min=0, max=1, update=appearance_update,
    description='Sets the transparency value from 0 to 1 (mostly transparent to mostly opaque)')
bpy.types.Scene.appearance_depth_slider = bpy.props.IntProperty(default=0, min=0, max=10, update=appearance_update,
    description='Sets the amount of surface layers that will be seen')
bpy.types.Scene.appearance_seghead_trans = bpy.props.FloatProperty(default=0, min=0, max=1, update=appearance_update,
    description='Sets the transparency value of the head from 0 to 1 ')
bpy.types.Scene.appearance_layer_weight = bpy.props.FloatProperty(default=0.3, update=layer_weight_update)


def init(addon):
    TransparencyPanel.addon = addon
    bpy.context.scene.appearance_solid_slider = 0.0
    bpy.context.scene.appearance_depth_slider = 0
    TransparencyPanel.init = True
    register()


def register():
    try:
        unregister()
        bpy.utils.register_class(TransparencyPanel)
        bpy.utils.register_class(UpdateAppearance)
        # print('Transparency Panel was registered!')
    except:
        print("Can't register Transparency Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(TransparencyPanel)
        bpy.utils.unregister_class(UpdateAppearance)
    except:
        pass
        # print("Can't unregister Freeview Panel!")
