import sys, os.path
sys.path.append('/usr/lib/python3.2/site-packages/')

from . import netblend
from .netblend import standard

import bpy

def write_netblend(context, filepath, props):
    print('Exporting NetBlend...')
    
    nb = netblend.NetBlend()
    
    b = bpy.types
    n = standard
    
    agameofmatch = {
        b.Scene: n.Scene,
        b.World: n.World,
        b.WorldMistSettings: n.WorldMist,
        b.Object: n.Object,
        b.Mesh: n.Mesh,
    }
    
    accounted = {}
    
    def a(bl):
        if bl in accounted:
            return accounted[bl]
        t = type(bl)
        if t not in agameofmatch:
            return None
        accounted[bl] = agameofmatch[t]()
        accounted[bl].from_bl(bl, a)
        nb.append(accounted[bl])
        return accounted[bl]
    
    if props.export == 'ALL':
        if len(bpy.data.scenes) < 1:
            print('Cancelling: No scenes.')
            return {'CANCELLED'}
        for scene in bpy.data.scenes:
            a(scene)
    
    elif props.export == 'SCENE' or len(bpy.context.scene.objects) < 1:
        if not bpy.context.scene:
            print('Cancelling: No objects.')
            return {'CANCELLED'}
        
        for o in bpy.context.scene.objects:
            a(o)
    
    elif props.export == 'SELECTION':
        if len(bpy.context.selected_objects) < 1:
            print('Cancelling: No selection.')
            return {'CANCELLED'}
        for object in bpy.context.selected_objects:
            a(object)
    
    elif props.export == 'DATA':
        if not bpy.context.object or not bpy.context.object.data:
            print('Cancelling: No data.')
            return {'CANCELLED'}
        a(bpy.context.object.data)
    
    nb.save(filepath)

    return {'FINISHED'}

# NetBlend Addon #

bl_info = {
    'name': 'NetBlend',
    'author': 'Jacob Ferrero',
    'version': (0, 0, 1),
    'blender': (2, 6, 3),
    'location': 'File > Export > NetBlend',
    'warning': 'Incomplete',
    'description': 'A compact and minimal blend format.',
    'wiki_url': 'http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts',
    'tracker_url': 'http://projects.blender.org/tracker/',
    'category': 'Import-Export'}

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty


class ExportNetBlend(bpy.types.Operator, ExportHelper):
    '''A compact and minimal blender format.'''
    bl_idname = 'export.netblend'  # this is important since its how bpy.ops.export.netblend is constructed
    bl_label = 'Export NetBlend'

    # ExportHelper mixin class uses this
    filename_ext = '.netblend'

    filter_glob = StringProperty(
            default='*.netblend',
            options={'HIDDEN'}
            )

    export = EnumProperty(
        name = 'Export',
        description = 'What to export.',
        items=(
            ('ALL', 'All Scenes', 'Export everything.'),
            ('SCENE', 'Current Scene', 'Export only the active scene.'),
            ('SELECTION', 'Selected Objects', 'Export only the selected objects.'),
            ('DATA', 'Active Data', 'Export only the data from the active object.'),
        ),
        default='ALL',
    )

    use_low_precision = BoolProperty(
            name = 'Low Precision',
            description = 'Use low precision in exchange for a smaller file.',
            default = False,
        )

    use_include_names = BoolProperty(
            name = 'Names',
            description = 'Include object and data names in the export.',
            default = True,
        )

    use_include_uv_textures = BoolProperty(
            name = 'UV Textures',
            description = 'Include uv textures in the export.',
            default = True,
        )

    use_include_vertex_colors = BoolProperty(
            name = 'Vertex Colors',
            description = 'Include vertex colors in the export.',
            default = True,
        )

    use_include_modifiers = BoolProperty(
            name = 'Modifiers',
            description = 'Include modifiers in the export.',
            default = True,
        )

    use_include_constraints = BoolProperty(
            name = 'Constraints',
            description = 'Include constraints in the export.',
            default = True,
        )

    use_include_materials = BoolProperty(
            name = 'Materials',
            description = 'Include materials in the export.',
            default = True,
        )

    use_include_world = BoolProperty(
            name = 'World',
            description = 'Export the world.',
            default = False,
        )

    def execute(self, context):
        return write_netblend(context, self.filepath, self)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportNetBlend.bl_idname, text = 'NetBlend (.netblend)')


def register():
    bpy.utils.register_class(ExportNetBlend)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportNetBlend)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == '__main__':
    register()

    # test call
    bpy.ops.export.netblend('INVOKE_DEFAULT')
