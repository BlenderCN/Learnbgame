bl_info = {
    "name": "Moco",
    "description": "Import and Export camera motion to Mark Roberts Motion Control Flair format",
    "author": "Nicolas Lemery Nantel / Fabricated Media",
    "version": (1, 1),
    "blender": (2, 76, 0),
    "location": "View3D > Animation > Tools",
    "wiki_url": "",
    "category": "Learnbgame"
}

import bpy
from datetime import datetime
from mathutils import Matrix, Vector
from math import radians, degrees
from os.path import isfile

# Data Storage
class MocoData(bpy.types.PropertyGroup):
    file_import = bpy.props.StringProperty(subtype='FILE_PATH')
    file_export = bpy.props.StringProperty(subtype='FILE_PATH')
    camera = bpy.props.StringProperty()
    target = bpy.props.StringProperty()


# Import Panel
class MoCoImportPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_moco_import'
    bl_label = 'MoCo Import'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Animation'
    bl_context = 'objectmode'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        col = layout.column()
        box = col.box()
        row = box.row()
        row.alignment='CENTER'
        row.label(text='MRMC Cartersians')

        col.separator()
        col.prop(scene.moco, 'file_import', text='')
        col.operator('moco.import', text='Import', icon='FILE_TEXT')

# Import Operator
class MocoImport(bpy.types.Operator):
    bl_idname = 'moco.import'
    bl_label = 'Moco Import'
    bl_options = {'REGISTER'}

    def execute(self, context):
        type, message = import_mrmc_carts()
        self.report(type, message)
        return {'FINISHED'}

def import_mrmc_carts():
    """Import a Flair MRMC Cartesians file in Blender.

    Full documentation is in the manual:
    http://www.mrmoco.com/downloads/MANUAL.pdf
    """
    scene = bpy.context.scene
    moco = bpy.context.scene.moco

    data_format = None
    move_info = None
    points = None
    column_headings = None
    keyframes = []

    # Convert from MRMC to Blender coordinates
    conversion_matrix = Matrix.Rotation(radians(-90), 4, 'Z')

    file_import = bpy.path.abspath(moco.file_import)
    if not isfile(file_import):
        return {'ERROR'}, 'Invalid file'

    with open(file_import, mode='r', encoding='utf-8') as file:
        line_index = 1

        for line in file.readlines():
            if line.startswith('#'):  # Line is a comment, skip
                continue
            if line_index == 1:  # Data format
                line_index += 1
                data_format = line.upper().split()
                continue
            if line_index == 2:  # Move Info
                line_index += 1
                move_info = line.upper().split()
                points = int(move_info[move_info.index('POINTS') + 1])
                continue
            if line_index == 3:  # Columns headings
                line_index += 1
                column_headings = line.upper().split()
                continue
            if line_index <= points + 3:  # Ignore weird chars after keyframes
                line_index += 1
                keyframes.append(line.replace(',', '').split())

    # Checks to make sure we support the format
    if 'CARTS_RAW' not in data_format:
        return {'ERROR'}, 'Wrong data format, only MRMC Cartesians is supported'
    if 'MRMC_COORDS' not in data_format:
        return {'ERROR'}, 'Wrong coordinates system, only MRMC_COORDS is supported'
    if 'IN_METRES' in data_format or 'IN_CENTIMETRES' in data_format:
        if 'IN_CENTIMETRES' in data_format:
            conversion_matrix = conversion_matrix * Matrix.Scale(0.01, 4)   # CM -> M
    else:
        return {'ERROR'}, 'Wrong units, only Meters and Centimeters are supported'

    index_frame = column_headings.index('FRAME')
    index_cam_x = column_headings.index('XV')
    index_cam_y = column_headings.index('YV')
    index_cam_z = column_headings.index('ZV')
    index_target_x = column_headings.index('XT')
    index_target_y = column_headings.index('YT')
    index_target_z = column_headings.index('ZT')

    # Set scene range from imported file
    scene.frame_start = int(keyframes[0][index_frame])
    scene.frame_end = int(keyframes[-1][index_frame])

    # Create camera and target
    bpy.ops.object.add(type='CAMERA', location=(0, 0, 0))
    camera = bpy.context.object
    bpy.context.object.scale = (0.2, 0.2, 0.2)
    bpy.ops.object.add(type='EMPTY', location=(0, 0, 0))
    target = bpy.context.object
    bpy.context.object.scale = (0.2, 0.2, 0.2)
    bpy.ops.object.select_all(action='DESELECT')
    camera.select, target.select = True, True
    bpy.ops.object.track_set(type='TRACKTO')


    # Import keyframes in Blender
    def keyframe_to_vector(data, x, y, z):
        """Convert a MRMC keyframe text line to a mathutils.Vector object
        data : List of strings containing the data, eg:
        ['59', '2.14017', '-0.01980', '0.60557', '3.22006', '0.00250', '0.80861', '-0.05048']
        """
        vector = float(data[x]), float(data[y]), float(data[z])
        vector = Vector(vector)  # Convert to Blender vector type
        return vector

    for keyframe in keyframes:
        scene.frame_set(int(keyframe[index_frame]))
        camera.location = keyframe_to_vector(keyframe, index_cam_x, index_cam_y, index_cam_z) * conversion_matrix
        target.location = keyframe_to_vector(keyframe, index_target_x, index_target_y, index_target_z) * conversion_matrix
        bpy.ops.anim.keyframe_insert(type='Location', confirm_success=False)

    return {'INFO'}, 'Imported {} frames from {}'.format(points, bpy.path.basename(file_import))


# Export Panel
class MoCoExportPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_moco_export'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Animation'
    bl_label = 'MoCo Export'
    bl_context = 'objectmode'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        col = layout.column()

        box = col.box()
        row = box.row()
        row.alignment = 'CENTER'
        row.label(text='MRMC Cartesians')

        col.separator()
        col.prop_search(scene.moco, 'camera', scene, 'objects', text='Camera', icon='OUTLINER_OB_CAMERA')
        col.prop_search(scene.moco, 'target', scene, 'objects', text='Target', icon='OUTLINER_OB_EMPTY')
        col.separator()
        col.prop(scene.moco, 'file_export', text='')
        col.operator('moco.export', text='Export', icon='FILE_TEXT')

# Export Operator
class MocoExport(bpy.types.Operator):
    bl_idname = 'moco.export'
    bl_label = 'Moco Export'

    def execute(self, context):
        type, message = export_mrmc_carts()
        self.report(type, message)
        return {'FINISHED'}

def export_mrmc_carts():
    """Export a camera and target to Flair MRMC Cartesians format.

    Full documentation is in the manual:
    http://www.mrmoco.com/downloads/MANUAL.pdf
    """
    scene = bpy.context.scene
    moco = bpy.context.scene.moco

    # Make sure we have a camera, target and file
    try:
        camera = scene.objects[moco.camera]
        target = scene.objects[moco.target]
    except:
        return {'ERROR'}, 'Missing camera or target objects'
    file_export = bpy.path.abspath(moco.file_export)
    if file_export == '':
        return {'ERROR'}, 'Missing export filename'

    frame_start = scene.frame_start
    frame_end = scene.frame_end
    frame_current = scene.frame_current

    # Exporting at frame boundaries, so there's always +1 frame
    # -> Might need to revisit this in the future as it's not exactly correct
    # since shutter open would be in-between the two frames, not at boundaries
    # for a motion move. For stop motion, only the left boundary is shot by default,
    # so the last keyframe is not shot at all, which is why we have an extra frame.
    frames = frame_end - frame_start + 1

    # Convert coordinates from Blender to MRMC
    conversion_matrix = (
        Matrix.Rotation(radians(90), 4, 'Z') *  # Rotate world 90
        Matrix.Scale(100, 4))  # Convert from Meters to Centimeters

    with open(file_export, mode='w', encoding='utf-8') as file:
        file.write('# CGI Export from Blender/MoCo on {}\n'.format(
            datetime.now().strftime("%Y-%m-%d %H:%M")))
        file.write('# Exported from: {}\n'.format(bpy.data.filepath))
        file.write('# Exported objects: {}, {}\n'.format(
            scene.moco.camera, scene.moco.target))
        file.write('DATA_TYPE  CARTS_RAW  MRMC_COORDS  IN_CENTIMETRES\n')
        file.write('POINTS {}  SPEED {}\n'.format(frames, scene.render.fps))
        file.write('FRAME     XV         YV         ZV         XT         YT         ZT         ROLL')

        for frame in range(frame_start, frame_end+1):
            scene.frame_set(frame)
            v = camera.matrix_world.to_translation() * conversion_matrix
            t = target.matrix_world.to_translation() * conversion_matrix
            r = degrees(camera.rotation_euler.y + camera.delta_rotation_euler.y) * -1
            file.write('\n' +
                '{:4}'.format(frame) +
                '{:11.5f}'.format(v.x) +
                '{:11.5f}'.format(v.y) +
                '{:11.5f}'.format(v.z) +
                '{:11.5f}'.format(t.x) +
                '{:11.5f}'.format(t.y) +
                '{:11.5f}'.format(t.z) +
                '{:11.5f}'.format(r))

    scene.frame_set(frame_current)
    return {'INFO'}, 'Exported {} frames to {}'.format(frames, bpy.path.basename(file_export))


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.moco = bpy.props.PointerProperty(type=MocoData)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.moco

if __name__ == '__main__':
    register()
