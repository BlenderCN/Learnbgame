
from bl_operators.presets import AddPresetBase, ExecutePreset
from bl_operators.presets import AddPresetBase
from bpy.props import (
    BoolProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import (
    Operator,
    Menu,
    Panel,
)
import bpy
import os

PRESET_SUBDIR = "pbs_helper/bake_type"


def add_presets(self, context):
    space = context.space_data
    if (space.type == 'NODE_EDITOR' and
        space.tree_type == 'ShaderNodeTree' and
        space.shader_type == 'OBJECT' and
            space.node_tree):
        self.layout.menu("PBS_HELPER_MT_preset", text='Bake Presets')


class PBS_HELPER_PT_presets_manager(Panel):
    '''Presets Manager'''
    bl_space_type = 'NODE_EDITOR'
    bl_label = "Preset Manager"
    bl_category = 'PBS Helper'
    preset_subdir = PRESET_SUBDIR
    bl_region_type = 'UI'
    act_idx: IntProperty()
    ext = '.blend'
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == 'NODE_EDITOR' and
                space.tree_type == 'ShaderNodeTree' and
                space.shader_type == 'OBJECT')
    def draw(self, context):
        files = []
        search_paths = bpy.utils.preset_paths(self.preset_subdir)
        for search_path in search_paths:
            files.extend([os.path.splitext(os.path.basename(path))[0]
                          for path in os.listdir(search_path) if path.endswith(self.ext)])
        layout = self.layout
        row = layout.row()
        del_ops = row.operator('pbs_helper.preset_add', text='', icon='ADD')
        box = layout.box()
        row = box.row(align=True)
        for f in files:
            row = box.row(align=True)
            row.label(text=f)
            del_ops = row.operator('pbs_helper.preset_add',
                                   text='',
                                   icon='REMOVE')
            del_ops.remove_active = True
            del_ops.name = f


class PBS_HELPER_MT_preset(Menu):
    """Preset menu by finding all preset files in the preset directory"""
    bl_label = "Material Bake Presets"
    preset_subdir = PRESET_SUBDIR
    draw = Menu.draw_preset
    preset_operator = 'pbs_helper.use_preset'  # run preset
    preset_extensions = {'.blend'}


class UsePreset(ExecutePreset):
    '''Add preset to current node tree'''
    bl_idname = "pbs_helper.use_preset"
    bl_label = "Execute a Python Preset"

    filepath: StringProperty(
        subtype='FILE_PATH',
        options={'SKIP_SAVE'},
    )
    menu_idname: StringProperty(
        name="Menu ID Name",
        description="ID name of the menu this was called from",
        options={'SKIP_SAVE'},
    )

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == 'NODE_EDITOR' and
                space.tree_type == 'ShaderNodeTree' and
                space.shader_type == 'OBJECT' and
                space.node_tree)

    def execute(self, context):
        obj = context.active_object
        mat = obj.active_material
        # append data
        with bpy.data.libraries.load(self.filepath, link=False) as (data_from, data_to):
            data_to.materials = data_from.materials
            data_to.node_groups = data_from.node_groups
        # apply data
        node_group = data_to.node_groups[0]
        bpy.ops.node.add_node('INVOKE_DEFAULT',
                              type="ShaderNodeGroup",
                              )
        mat.node_tree.nodes.active.node_tree = node_group
        bpy.ops.node.group_ungroup()
        bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        return {'FINISHED'}


class AddPreset(Operator):
    """Add/Remove preset to library"""
    bl_label = "Add Preset"
    bl_idname = "pbs_helper.preset_add"
    preset_subdir = PRESET_SUBDIR
    name: StringProperty(
        name="Name",
        description="Name of the preset, used to make the path name",
        maxlen=64,
        options={'SKIP_SAVE'},
    )
    remove_active: BoolProperty(
        default=False,
        options={'HIDDEN', 'SKIP_SAVE'},
    )
    ext = '.blend'
    # TODO use when is possible use PointerProperty
    mat_name: StringProperty(name="Preview Material")
    node_group_name: StringProperty(name="bake node_group")

    def __init__(self):
        if self.node_group_name != '':
            return
        try:
            mat = bpy.context.active_object.active_material
            node = mat.node_tree.nodes.active
            if node.bl_idname == 'ShaderNodeGroup':
                self.node_group_name = node.node_tree.name
        except:
            pass

    def execute(self, context):
        if self.name == '':
            return {'CANCELLED'}
        if not self.remove_active:
            if self.node_group_name == '':
                return {'CANCELLED'}
            node_group = bpy.data.node_groups[self.node_group_name]
            filename = self.name+self.ext
            filepath = os.path.join(bpy.utils.preset_paths(self.preset_subdir)[0],
                                    filename)
            data_blocks = [node_group]
            if not self.mat_name == '':
                mat = bpy.data.materials[self.mat_name]
                data_blocks.append(mat)
            bpy.data.libraries.write(filepath, set(data_blocks))
        else:
            filepath = bpy.utils.preset_find(self.name,
                                             self.preset_subdir,
                                             ext=self.ext)
            if not filepath:
                filepath = bpy.utils.preset_find(self.name,
                                                 self.preset_subdir,
                                                 display_name=True,
                                                 ext=self.ext)
            if not filepath:
                return {'CANCELLED'}
            try:
                if hasattr(self, "remove"):
                    self.remove(context, filepath)
                else:
                    os.remove(filepath)
            except Exception as e:
                self.report({'ERROR'}, "Unable to remove preset: %r" % e)
                import traceback
                traceback.print_exc()
                return {'CANCELLED'}
        print()
        print(f'add preset to {self.name}.blend')
        print(f'node group:{self.node_group_name}')
        print(f'material:{self.mat_name}')
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name")
        row = layout.row()
        row.prop_search(self, "mat_name", bpy.data, "materials")
        row = layout.row()
        row.prop_search(self, "node_group_name", bpy.data, "node_groups")

    def invoke(self, context, event):
        if not self.remove_active:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)
        else:
            return self.execute(context)


classes = [AddPreset,
           PBS_HELPER_MT_preset,
           PBS_HELPER_PT_presets_manager,
           UsePreset]


def register():
    bpy.utils.user_resource('SCRIPTS',
                            path="presets/"+PRESET_SUBDIR,
                            create=True)
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.NODE_MT_add.append(add_presets)


def unregister():
    bpy.types.NODE_MT_add.remove(add_presets)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
