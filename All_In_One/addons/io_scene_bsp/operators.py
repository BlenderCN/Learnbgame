if 'bpy' in locals():
    import importlib as il
    il.reload(import_bsp)
    il.reload(export_bsp)
    # print('io_scene_bsp.operators: reload ready')

else:
    from . import import_bsp
    from . import export_bsp


import bpy

from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatProperty
)

from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
)


class ImportBSP(bpy.types.Operator, ImportHelper):
    """Load a Quake BSP File"""

    bl_idname = 'import_scene.bsp'
    bl_label = 'Import BSP'
    bl_options = {'UNDO', 'PRESET'}

    filename_ext = '.bsp'
    filter_glob: StringProperty(
        default='*.bsp',
        options={'HIDDEN'},
    )

    global_scale: FloatProperty(
            name='Scale',
            min=0.001, max=1000.0,
            default=1.0 / 32.0,
            )

    use_worldspawn_entity: BoolProperty(
        name='Import Worldspawn Entity',
        description='Import worldspawn entities',
        default=True
    )

    use_brush_entities: BoolProperty(
        name='Import Brush Entities',
        description='Import brush entities',
        default=True
    )

    use_point_entities: BoolProperty(
        name='Import Point Entities',
        description='Import point entities',
        default=True
    )

    load_lightmap: BoolProperty(
        name='Load Lightmap Data',
        description='Load lightmap data',
        default=False
    )

    def execute(self, context):
        keywords = self.as_keywords(ignore=("filter_glob",))
        from . import import_bsp

        return import_bsp.load(self, context, **keywords)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'global_scale')
        layout.prop(self, 'use_worldspawn_entity')
        layout.prop(self, 'use_brush_entities')
        layout.prop(self, 'use_point_entities')
        # layout.prop(self, 'load_lightmap')


class ExportBSP(bpy.types.Operator, ExportHelper):
    """Save a Quake BSP File"""

    bl_idname = 'export_scene.bsp'
    bl_label = 'Export BSP'
    bl_options = {'PRESET'}

    filename_ext = '.bsp'
    filter_glob = StringProperty(
        default='*.bsp',
        options={'HIDDEN'},
    )

    check_extension = True

    def execute(self, context):
        from . import export_bsp

        ignore_attrs = (
            'axis_forward',
            'axis_up',
            'global_scale',
            'check_existing',
            'filter_glob'
        )
        keywords = self.as_keywords(ignore=ignore_attrs)

        return export_bsp.save(self, context, **keywords)


def menu_func_import(self, context):
    self.layout.operator(ImportBSP.bl_idname,
                         text='Quake BSP (.bsp)')


def menu_func_export(self, context):
    self.layout.operator(ExportBSP.bl_idname,
                         text='Quake BSP (.bsp)')


def register():
    bpy.utils.register_class(ImportBSP)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportBSP)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_export)