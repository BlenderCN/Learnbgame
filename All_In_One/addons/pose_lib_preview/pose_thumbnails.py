'''This module does the actual work for the pose thumbnails addon.'''

import os
import logging
import re
import difflib
import copy
import time
if 'bpy' in locals():
    import importlib
    if 'prefs' in locals():
        importlib.reload(prefs)
else:
    from . import prefs
import bpy
import bpy.utils.previews
from bpy_extras.io_utils import ImportHelper


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
preview_collections = {}
enum_items_cache = {}

IMAGE_EXTENSIONS = (
    '.jpeg', '.jpg', '.jpe',
    '.png',
    '.tga', '.tpic',
    '.tiff', '.tif',
    '.bmp', '.dib',
    '.cin',
    '.dpx',
    '.psd',
    '.exr',
    '.hdr', '.pic',
    )


def get_pose_suffix_from_prefs():
    '''Get the pose suffix from the addon preferences.'''
    user_prefs = bpy.context.user_preferences
    addon_prefs = user_prefs.addons[__package__].preferences
    if addon_prefs:
        return ''.join((' ', addon_prefs.pose_suffix))
    else:
        return ''.join((' ', prefs.DEFAULT_POSE_SUFFIX))


def clean_pose_name(pose_name):
    '''Return the clean pose name, that is without thumbnail suffix.'''
    pose_suffix = get_pose_suffix_from_prefs()
    if pose_name.endswith(pose_suffix):
        return pose_name[:-len(pose_suffix)]
    else:
        return pose_name


def suffix_pose_name(pose_name):
    '''Return the pose name with the thumbnail suffix.'''
    pose_suffix = get_pose_suffix_from_prefs()
    if pose_name.endswith(pose_suffix) or not pose_suffix.strip():
        return pose_name
    else:
        return ''.join((pose_name, pose_suffix))


def get_images_from_dir(directory, sort=True):
    '''Get all image files in the directory.'''
    valid_images = []
    image_extensions = ['.png', '.jpg', '.jpeg']
    for filename in os.listdir(directory):
        if os.path.splitext(filename)[-1].lower() in image_extensions:
            valid_images.append(filename)
    return sorted(valid_images)


def is_image_file(filepath):
    '''Check if the file is an image file.'''
    file_extension = os.path.splitext(filepath)[-1]
    return file_extension.lower() in IMAGE_EXTENSIONS


def get_thumbnail_from_pose(pose):
    '''Get the thumbnail that belongs to the pose.

    Args:
        pose (pose_marker): a pose in the pose library

    Returns:
        thumbnail PropertyGroup
    '''
    if pose is None:
        return
    poselib = pose.id_data
    for thumbnail in poselib.pose_thumbnails:
        if thumbnail.frame == pose.frame:
            return thumbnail


def get_pose_from_thumbnail(thumbnail):
    '''Get the pose that belongs to the thumbnail.

    Args:
        thumbnail (PropertyGroup): thumbnail info of a pose

    Returns:
        pose_marker
    '''
    if thumbnail is None:
        return
    poselib = bpy.context.object.pose_library
    for pose in poselib.pose_markers:
        if pose.frame == thumbnail.frame:
            return pose


def get_pose_index_from_frame(poselib, frame):
    '''Get the pose index of the pose with the specified frame.'''
    for i, pose in enumerate(poselib.pose_markers):
        if pose.frame == frame:
            return i


def get_no_thumbnail_path():
    '''Get the path to the 'no thumbnail' image.'''
    no_thumbnail_path = os.path.join(
        os.path.dirname(__file__),
        'thumbnails',
        'no_thumbnail.png',
        )
    return no_thumbnail_path


def get_no_thumbnail_image(pcoll):
    '''Return the 'no thumbnail' preview icon.'''
    no_thumbnail_path = get_no_thumbnail_path()
    no_thumbnail = pcoll.get('No Thumbnail') or pcoll.load(
        'No Thumbnail',
        no_thumbnail_path,
        'IMAGE',
        )
    return no_thumbnail


def get_placeholder_path():
    '''Get the path to the placeholder image.'''
    placeholder_path = os.path.join(
        os.path.dirname(__file__),
        'thumbnails',
        'placeholder.png',
        )
    return placeholder_path


def get_placeholder_image(pcoll):
    '''Return the placeholder preview icon.'''
    placeholder_path = get_placeholder_path()
    placeholder = pcoll.get('Placeholder') or pcoll.load(
        'Placeholder',
        placeholder_path,
        'IMAGE',
        )
    return placeholder


def get_enum_items(poselib, pcoll):
    '''Return the enum items for the thumbnail previews.'''
    logger = logging.getLogger("{}.get_enum_items".format(__name__))
    global enum_items_cache
    enum_items = []
    wm = bpy.context.window_manager
    pose_thumbnail_options = wm.pose_thumbnails.options
    show_all_poses = pose_thumbnail_options.show_all_poses
    for i, pose in enumerate(poselib.pose_markers):
        thumbnail = get_thumbnail_from_pose(pose)
        if thumbnail:
            image = pcoll.get(thumbnail.filepath)
            # TODO: find a better way to compensate for the filepath mangling
            #       if the poselib is linked.
            if image is None and poselib.library:
                image = pcoll.get(
                    bpy.path.abspath(
                        thumbnail.filepath,
                        library=poselib.library,
                        ))
            if not image:
                if poselib.library:
                    logger.debug("Thumbnail path: %s", thumbnail.filepath)
                    thumbnail_path = bpy.path.abspath(
                        thumbnail.filepath,
                        library=poselib.library,
                        )
                    logger.debug("Absolute thumbnail path: %s", thumbnail_path)
                else:
                    thumbnail_path = thumbnail.filepath
                image_path = os.path.normpath(
                    bpy.path.abspath(thumbnail_path))
                if not os.path.isfile(image_path):
                    image = get_no_thumbnail_image(pcoll)
                else:
                    image = pcoll.load(
                        thumbnail_path,
                        image_path,
                        'IMAGE',
                        )
        elif show_all_poses:
            image = get_placeholder_image(pcoll)
        else:
            image = None
        if image is not None:
            # Warning: There is a known bug with using a callback, Python must
            # keep a reference to the strings returned or Blender will crash.
            # That's why we have to 'cache' the items in a dict.
            pose_frame = enum_items_cache.setdefault(
                str(pose.frame),
                str(pose.frame),
                )
            pose_name = enum_items_cache.setdefault(
                clean_pose_name(pose.name),
                clean_pose_name(pose.name),
                )
            enum_items.append((
                pose_frame,
                pose_name,
                '',
                image.icon_id,
                i,
                ))
    return enum_items


def get_pose_thumbnails(self, context):
    '''Get the pose thumbnails and add them to the preview collection.'''
    poselib = context.object.pose_library
    if (context is None or
        not poselib.pose_markers or
        not poselib.pose_thumbnails):
            return []
    pcoll = preview_collections['pose_library']
    enum_items = get_enum_items(
        poselib,
        pcoll,
        )
    pcoll.pose_thumbnails = enum_items
    return pcoll.pose_thumbnails


def get_current_pose():
    '''Copies all pose bone matrices (matrix_basis) and custom props.'''
    armature = bpy.context.object
    pose_bones = bpy.context.selected_pose_bones or armature.pose.bones
    pose = {}
    for pose_bone in pose_bones:
        pose[pose_bone] = {}
        pose[pose_bone]['matrix_basis'] = pose_bone.matrix_basis.copy()
        for key, value in pose_bone.items():
            if key != '_RNA_UI':
                pose[pose_bone][key] = value
    return pose


def select_all_pose_bones(armature, deselect=False):
    '''Select all the pose bones of the armature.'''
    for pose_bone in armature.pose.bones:
        pose_bone.bone.select = not(deselect)


def auto_keyframe():
    '''Set automatic keyframes (for the current armature).'''
    auto_insert = bpy.context.scene.tool_settings.use_keyframe_insert_auto
    if not auto_insert:
        return
    selected_pose_bones = bpy.context.selected_pose_bones
    if not selected_pose_bones:
        select_all_pose_bones(bpy.context.object)
    scene = bpy.context.scene
    user_preferences = bpy.context.user_preferences
    use_active_keying_set = scene.tool_settings.use_keyframe_insert_keyingset
    only_insert_available = user_preferences.edit.use_keyframe_insert_available
    active_keying_set = scene.keying_sets_all.active
    if use_active_keying_set and active_keying_set is not None:
        bpy.ops.anim.keyframe_insert_menu(type=active_keying_set.bl_idname)
    elif only_insert_available:
        bpy.ops.anim.keyframe_insert_menu(type='Available')
    else:
        bpy.ops.anim.keyframe_insert_menu(type='WholeCharacterSelected')
    if not selected_pose_bones:
        select_all_pose_bones(bpy.context.object, deselect=True)


def mix_to_pose(pose_a, pose_b, factor):
    '''Mixes pose_b over pose_a with the given factor.'''

    def linear_mix(orig, new, factor):
        return orig * (1 - factor) + new * factor

    for pose_bone, pose_a_props in pose_a.items():
        for prop, pose_a_value in pose_a_props.items():
            pose_b_value = pose_b[pose_bone][prop]
            if prop == 'matrix_basis':
                pose_bone.matrix_basis = linear_mix(
                    pose_a_value,
                    pose_b_value,
                    factor,
                    )
            else:
                if isinstance(pose_a_value, float):
                    pose_bone[prop] = linear_mix(
                        pose_a_value,
                        pose_b_value,
                        factor,
                        )
                elif factor < 0.5:
                    pose_bone[prop] = pose_a_value
                else:
                    pose_bone[prop] = pose_b_value
    auto_keyframe()


def update_pose(self, context):
    '''Callback when the enum property is updated (e.g. the index of the active
       item is changed).

    Args:
        self (pose library)
        context (blender context = bpy.context)

    Returns:
        None
    '''
    pose_frame = int(self.active)
    poselib = context.object.pose_library
    pose_index = get_pose_index_from_frame(poselib, pose_frame)
    bpy.ops.poselib.mix_pose('INVOKE_DEFAULT', pose_index=pose_index)


def pose_thumbnails_draw(self, context):
    '''Draw the thumbnail enum in the Pose Library panel.'''
    user_prefs = context.user_preferences
    addon_prefs = user_prefs.addons[__package__].preferences
    wm = context.window_manager
    obj = context.object
    poselib = obj.pose_library
    if poselib is None or not poselib.pose_markers:
        return
    pose_thumbnail_options = wm.pose_thumbnails.options
    show_labels = pose_thumbnail_options.show_labels
    thumbnail_size = addon_prefs.thumbnail_size * 5
    layout = self.layout
    col = layout.column(align=True)
    if obj.mode != 'POSE':
        col.enabled = False
    col.template_icon_view(
        wm.pose_thumbnails,
        'active',
        show_labels=show_labels,
        scale=thumbnail_size,
        )
    row = col.row(align=True)
    row.prop(pose_thumbnail_options, 'show_labels', toggle=True, text='Labels')
    row.prop(pose_thumbnail_options, 'show_all_poses', toggle=True, text='All Poses')
    if obj.library or obj.data.library or obj.pose_library.library:
        col.operator(
            RefreshThumbnails.bl_idname,
            icon='FILE_REFRESH',
            text='Refresh',
            )
        return
    col.separator()
    box = col.box()
    if pose_thumbnail_options.show_creation_options:
        expand_icon = 'TRIA_DOWN'
    else:
        expand_icon = 'TRIA_RIGHT'
    box.prop(
        pose_thumbnail_options,
        'show_creation_options',
        icon=expand_icon,
        toggle=True,
        )
    if pose_thumbnail_options.show_creation_options:
        sub_col = box.column(align=True)
        if not poselib.pose_markers.active:
            return
        thumbnail = get_thumbnail_from_pose(poselib.pose_markers.active)
        if thumbnail and thumbnail.filepath != get_no_thumbnail_path():
            text = 'Replace'
        else:
            text = 'Add'
        row = sub_col.row(align=True)
        row.operator(AddPoseThumbnail.bl_idname, text=text)
        row.operator(AddPoseThumbnailsFromDir.bl_idname, text='Batch Add/Change')
        row = sub_col.row(align=True)
        row_col = row.column(align=True)
        row_col.operator(RemovePoseThumbnail.bl_idname, text='Remove')
        if get_thumbnail_from_pose(poselib.pose_markers.active):
            row_col.enabled = True
        else:
            row_col.enabled = False
        row_col = row.column(align=True)
        row_col.operator(RemoveAllThumbnails.bl_idname, text='Remove All')
        if poselib.pose_thumbnails:
            row_col.enabled = True
        else:
            row_col.enabled = False
        sub_col.separator()
        sub_col.operator(
            RefreshThumbnails.bl_idname,
            icon='FILE_REFRESH',
            text='Refresh',
            )


class MixPose(bpy.types.Operator):
    '''Mix-apply the selected library pose on to the current pose.'''
    bl_idname = 'poselib.mix_pose'
    bl_label = 'Mix the pose with the current pose.'
    bl_options = {'UNDO', 'BLOCKING', 'GRAB_CURSOR'}

    factor = bpy.props.FloatProperty(
        name='Mix Factor',
        default=100,
        subtype='PERCENTAGE',
        unit='NONE',
        min=0,
        max=100,
        description='Mix Factor'
        )
    pose_index = bpy.props.IntProperty(
        name='Pose Index',
        default=0,
        min=0,
        description='The index of the pose to mix.',
        )

    @classmethod
    def poll(cls, context):
        return (context is not None and
                context.object and
                context.object.type == 'ARMATURE' and
                context.object.mode == 'POSE')

    def execute(self, context):
        if self.just_clicked:
            bpy.ops.poselib.apply_pose(pose_index=self.pose_index)
            return {'FINISHED'}
        mouse_delta = self.mouse_x - self.mouse_prev_x
        self.factor = min(100, max(0, mouse_delta))
        mix_factor = self.factor / 100
        mix_to_pose(self.current_pose, self.target_pose, mix_factor)
        return {'FINISHED'}

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            self.mouse_x = event.mouse_x
            self.execute(context)
        elif event.type == 'LEFTMOUSE':
            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if not event.shift:
            self.just_clicked = True
            return self.execute(context)
        self.just_clicked = False
        self.current_pose = get_current_pose()
        bpy.ops.poselib.apply_pose(pose_index=self.pose_index)
        self.target_pose = get_current_pose()
        self.mouse_x = event.mouse_x
        self.mouse_prev_x = event.mouse_prev_x
        self.execute(context)
        wm = context.window_manager
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'factor', text='Mix Factor')


class AddPoseThumbnail(bpy.types.Operator, ImportHelper):
    '''Add a thumbnail to a pose.'''
    bl_idname = 'poselib.add_thumbnail'
    bl_label = 'Add thumbnail'
    bl_options = {'PRESET', 'UNDO'}

    display_type = bpy.props.EnumProperty(
        items=(('LIST_SHORT', 'Short List', '', 1),
               ('LIST_LONG', 'Long List', '', 2),
               ('THUMBNAIL', 'Thumbnail', '', 3)),
        options={'HIDDEN', 'SKIP_SAVE'},
        default='THUMBNAIL',
        )
    filter_image = bpy.props.BoolProperty(
        default=True,
        options={'HIDDEN', 'SKIP_SAVE'},
        )
    filter_folder = bpy.props.BoolProperty(
        default=True,
        options={'HIDDEN', 'SKIP_SAVE'},
        )
    filter_glob = bpy.props.StringProperty(
        default='',
        options={'HIDDEN', 'SKIP_SAVE'},
        )

    use_relative_path = bpy.props.BoolProperty(
        name='Relative Path',
        description='Select the file relative to the blend file',
        default=True,
        )

    def execute(self, context):
        if not self.use_relative_path:
            filepath = self.filepath
        else:
            filepath = bpy.path.relpath(self.filepath)
        if not is_image_file(filepath):
            self.report({'ERROR_INVALID_INPUT'},
                        'The selected file is not an image.')
            logger.error(' File {0} is not an image.'.format(
                os.path.basename(filepath)))
        poselib = context.object.pose_library
        pose = poselib.pose_markers.active
        pose.name = suffix_pose_name(pose.name)
        thumbnail = (get_thumbnail_from_pose(pose) or
                     poselib.pose_thumbnails.add())
        thumbnail.frame = pose.frame
        thumbnail.filepath = filepath
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, 'use_relative_path')


class AddPoseThumbnailsFromDir(bpy.types.Operator, ImportHelper):
    '''Add thumbnails from a directory to poses from a pose library.'''
    bl_idname = 'poselib.add_thumbnails_from_dir'
    bl_label = 'Add Thumbnails from Directory'
    bl_options = {'PRESET', 'UNDO'}
    directory = bpy.props.StringProperty(
        maxlen=1024,
        subtype='DIR_PATH',
        options={'HIDDEN', 'SKIP_SAVE'},
        )
    files = bpy.props.CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'},
        )
    display_type = bpy.props.EnumProperty(
        items=(('LIST_SHORT', 'Short List', '', 1),
               ('LIST_LONG', 'Long List', '', 2),
               ('THUMBNAIL', 'Thumbnail', '', 3)),
        options={'HIDDEN', 'SKIP_SAVE'},
        default='THUMBNAIL',
        )
    filter_image = bpy.props.BoolProperty(
        default=True,
        options={'HIDDEN', 'SKIP_SAVE'},
        )
    filter_folder = bpy.props.BoolProperty(
        default=True,
        options={'HIDDEN', 'SKIP_SAVE'},
        )
    filter_glob = bpy.props.StringProperty(
        default='',
        options={'HIDDEN', 'SKIP_SAVE'},
        )
    map_method_items = (
            ('NAME', 'Name', 'Match the file names with the pose names.'),
            ('INDEX', 'Index', 'Map the files to the order of the poses (the files are sorted by name, so numbering them makes sense).'),
            ('FRAME', 'Frame', 'Map the files to the order of the frame number of the poses.'),
            )
    mapping_method = bpy.props.EnumProperty(
        name='Match by',
        description='Match the thumbnail images to the poses by using this method',
        items=map_method_items,
        )
    overwrite_existing = bpy.props.BoolProperty(
        name='Overwrite existing',
        description='Overwrite existing thumbnails of the poses.',
        default=True,
        )
    match_fuzzyness = bpy.props.FloatProperty(
        name='Fuzzyness',
        description='Fuzzyness of the matching (0 = exact match, 1 = everything).',
        min=0.0,
        max=1.0,
        default=0.4,
        )
    match_by_number = bpy.props.BoolProperty(
        name='Match by number',
        description='If the filenames start with a number, match the number to the pose index/frame.',
        default=False,
        )
    start_number = bpy.props.IntProperty(
        name='Start number',
        description='The image number to map to the first pose.',
        default=1,
        )
    use_relative_path = bpy.props.BoolProperty(
        name='Relative Path',
        description='Select the file relative to the blend file',
        default=True,
        )

    def get_images_from_dir(self):
        '''Get all image files from a directory.'''
        directory = self.directory
        files = [f.name for f in self.files]
        image_paths = []
        if files and not files[0]:
            image_files = os.listdir(directory)
            report = False
        else:
            image_files = files
            report = True
        for image_file in sorted(image_files):
            # ext = os.path.splitext(image_file)[-1].lower()
            # if ext and ext in self.filename_ext:
            image_path = os.path.join(directory, image_file)
            if not is_image_file(image_path):
                if not image_file.startswith('.') and report:
                    logger.warning(' Skipping file {0} because it\'s not an image.'.format(image_file))
                continue
            if self.use_relative_path:
                image_paths.append(bpy.path.relpath(image_path))
            else:
                image_paths.append(image_path)
        return image_paths

    def create_thumbnail(self, pose, image):
        '''Create or update the thumbnail for a pose.'''
        if not self.overwrite_existing and get_thumbnail_from_pose(pose):
            return
        poselib = self.poselib
        pose.name = suffix_pose_name(pose.name)
        thumbnail = (get_thumbnail_from_pose(pose) or
                     poselib.pose_thumbnails.add())
        thumbnail.frame = pose.frame
        thumbnail.filepath = image

    def get_image_by_number(self, number):
        '''Return a the image file if it contains the number.

        Check if the filename contains the number. It matches the first number
        found in the filename (starting from the left).
        '''
        for image in self.image_files:
            basename = os.path.basename(image)
            match = re.match(r'^.*?([0-9]+)', basename)
            if match:
                image_number = int(match.groups()[0])
                if number == image_number:
                    return image

    def match_thumbnails_by_name(self):
        '''Assign the thumbnail by trying to match the pose name with a file name.'''
        poselib = self.poselib
        image_files = self.image_files
        match_map = {os.path.splitext(os.path.basename(f))[0]: f for f in image_files}
        for pose in poselib.pose_markers:
            match = difflib.get_close_matches(
                clean_pose_name(pose.name),
                match_map.keys(),
                n=1,
                cutoff=1.0 - self.match_fuzzyness,
                )
            if match:
                thumbnail_image = match_map[match[0]]
                self.create_thumbnail(pose, thumbnail_image)

    def match_thumbnails_by_index(self):
        '''Map the thumbnail images to the index of the poses.'''
        poselib = self.poselib
        if self.match_by_number:
            start_number = self.start_number
            for i, pose in enumerate(poselib.pose_markers):
                image = self.get_image_by_number(i + start_number)
                if image:
                    self.create_thumbnail(pose, image)
        else:
            image_files = self.image_files
            for pose, image in zip(poselib.pose_markers, image_files):
                self.create_thumbnail(pose, image)

    def match_thumbnails_by_frame(self):
        '''Map the thumbnail images to the frame of the poses.'''
        poselib = self.poselib
        if self.match_by_number:
            for i, pose in enumerate(poselib.pose_markers):
                image = self.get_image_by_number(pose.frame)
                if image:
                    self.create_thumbnail(pose, image)
        else:
            frame_sorted = sorted(poselib.pose_markers, key=lambda p: p.frame)
            image_files = self.image_files
            for pose, image in zip(frame_sorted, image_files):
                self.create_thumbnail(pose, image)

    def match_thumbnails(self):
        '''Try to match the image files to the poses.'''
        mapping_method = self.mapping_method
        if mapping_method == 'NAME':
            self.match_thumbnails_by_name()
        elif mapping_method == 'INDEX':
            self.match_thumbnails_by_index()
        else:
            self.match_thumbnails_by_frame()

    def execute(self, context):
        self.poselib = context.object.pose_library
        self.image_files = self.get_images_from_dir()
        self.match_thumbnails()
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        box = col.box()
        box.label(text='Mapping Method')
        row = box.row()
        row.prop(self, 'mapping_method', expand=True)
        box.prop(self, 'overwrite_existing')
        if self.mapping_method == 'NAME':
            box.prop(self, 'match_fuzzyness')
        if self.mapping_method == 'INDEX':
            box.prop(self, 'match_by_number')
            if self.match_by_number:
                box.prop(self, 'start_number')
        if self.mapping_method == 'FRAME':
            box.prop(self, 'match_by_number')
        col.separator()
        col.prop(self, 'use_relative_path')


class RemovePoseThumbnail(bpy.types.Operator):
    '''Remove a thumbnail from a pose.'''
    bl_idname = 'poselib.remove_thumbnail'
    bl_label = 'Remove Thumbnail'
    bl_options = {'PRESET', 'UNDO'}

    def execute(self, context):
        poselib = context.object.pose_library
        pose = poselib.pose_markers.active
        pose.name = clean_pose_name(pose.name)
        for i, thumbnail in enumerate(poselib.pose_thumbnails):
            if pose.frame == thumbnail.frame:
                poselib.pose_thumbnails.remove(i)
                break
        return {'FINISHED'}


class RemoveAllThumbnails(bpy.types.Operator):
    '''Remove all thumbnails.'''
    bl_idname = 'poselib.remove_all_thumbnails'
    bl_label = 'Remove All Thumbnails'
    bl_options = {'PRESET', 'UNDO'}

    def execute(self, context):
        poselib = context.object.pose_library
        poselib.pose_thumbnails.clear()
        for pose in poselib.pose_markers:
            pose.name = clean_pose_name(pose.name)
        return {'FINISHED'}


class RefreshThumbnails(bpy.types.Operator):
    '''Reloads and cleans the thumbnails and poses.'''
    bl_idname = 'poselib.refresh_thumbnails'
    bl_label = 'Refresh Thumbnails'
    bl_options = {'PRESET', 'UNDO'}

    def remove_thumbnail(self, thumbnail):
        '''Remove the thumbnail from the poselib thumbnail info.'''
        pose_thumbnails = self.poselib.pose_thumbnails
        for i, existing_thumbnail in enumerate(pose_thumbnails):
            if thumbnail == existing_thumbnail:
                pose_thumbnails.remove(i)

    def remove_unused_thumbnails(self):
        '''Remove unused thumbnails.'''

        def get_unused_thumbnails():
            for thumbnail in self.poselib.pose_thumbnails:
                if not get_pose_from_thumbnail(thumbnail):
                    yield thumbnail

        unused_thumbnails = get_unused_thumbnails()
        for thumbnail in unused_thumbnails:
            self.remove_thumbnail(thumbnail)

    def remove_double_thumbnails(self):
        '''Remove extraneous thumbnails from a pose.'''
        thumbnail_map = {}
        for thumbnail in self.poselib.pose_thumbnails:
            if str(thumbnail.frame) not in thumbnail_map:
                thumbnail_map[str(thumbnail.frame)] = [thumbnail]
            else:
                thumbnail_map[str(thumbnail.frame)].append(thumbnail)
        for frame, thumbnail_list in thumbnail_map.items():
            for thumbnail in thumbnail_list[:-1]:
                self.remove_thumbnail(thumbnail)

    def clean_pose_names(self):
        '''Remove suffixes from poses without a thumbnail.'''
        for pose in self.poselib.pose_markers:
            if not get_thumbnail_from_pose(pose):
                pose.name = clean_pose_name(pose.name)
            else:
                pose.name = suffix_pose_name(pose.name)

    def execute(self, context):
        self.poselib = context.object.pose_library
        self.clean_pose_names()
        self.remove_unused_thumbnails()
        self.remove_double_thumbnails()
        pcoll = preview_collections['pose_library']
        pcoll.clear()
        return {'FINISHED'}


class PoselibThumbnail(bpy.types.PropertyGroup):
    '''A property to hold the thumbnail info for a pose.'''
    frame = bpy.props.IntProperty(
        name='Pose frame',
        description='The frame of the pose marker.',
        default=-1,
        )
    filepath = bpy.props.StringProperty(
        name='Thumbnail path',
        description='The file path of the thumbnail image.',
        default='',
        subtype='FILE_PATH',
        )


class PoselibThumbnailsOptions(bpy.types.PropertyGroup):
    '''A property to hold the option info for the thumbnail UI.'''
    show_creation_options = bpy.props.BoolProperty(
        name='Thumbnail Creation',
        description='Show or hide the thumbnail creation options.',
        default=False,
        )
    show_labels = bpy.props.BoolProperty(
        name='Show Labels',
        description='Show the labels (pose names) underneath the thumbnails.',
        default=True,
        )
    show_all_poses = bpy.props.BoolProperty(
        name='Show All Poses',
        description='Also show poses that don\'t have a thumbnail.',
        default=False,
        )


class PoselibUiSettings(bpy.types.PropertyGroup):
    '''A collection property for all the UI related settings.'''
    active = bpy.props.EnumProperty(
        items=get_pose_thumbnails,
        update=update_pose,
        )
    options = bpy.props.PointerProperty(
        type=PoselibThumbnailsOptions,
        )
    suffix = bpy.props.StringProperty(
        name='Pose Suffix',
        description=('Add this suffix to the name of a pose when it has a'
                     ' thumbnail. Leave empty to add nothing.'),
        default=get_pose_suffix_from_prefs(),
        )


class PoselibThumbnailsPropertiesPanel(bpy.types.Panel):
    '''Creates a pose thumbnail panel in the 3D View Properties panel'''
    bl_label = "Pose Library"
    bl_idname = "VIEW3D_PT_pose_previews"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        user_prefs = context.user_preferences
        addon_prefs = user_prefs.addons[__package__].preferences
        obj = context.object
        return (obj and obj.type == 'ARMATURE' and
                addon_prefs.add_3dview_prop_panel)

    def draw(self, context):
        user_prefs = context.user_preferences
        addon_prefs = user_prefs.addons[__package__].preferences
        wm = context.window_manager
        obj = context.object
        poselib = obj.pose_library
        layout = self.layout
        col = layout.column(align=True)
        col.template_ID(obj, "pose_library", unlink="poselib.unlink")
        if poselib is not None:
            pose_thumbnail_options = wm.pose_thumbnails.options
            show_labels = pose_thumbnail_options.show_labels
            thumbnail_size = addon_prefs.thumbnail_size * 5
            col.template_icon_view(
                wm.pose_thumbnails,
                'active',
                show_labels=show_labels,
                scale=thumbnail_size,
                )
            row = col.row(align=True)
            row.prop(
                pose_thumbnail_options,
                'show_labels',
                toggle=True,
                text='Labels',
                )
            row.prop(
                pose_thumbnail_options,
                'show_all_poses',
                toggle=True,
                text='All Poses',
                )


def register():
    '''Register all pose thumbnail related things.'''
    bpy.types.Action.pose_thumbnails = bpy.props.CollectionProperty(
        type=PoselibThumbnail)
    bpy.types.WindowManager.pose_thumbnails = bpy.props.PointerProperty(
        type=PoselibUiSettings)
    bpy.types.DATA_PT_pose_library.prepend(pose_thumbnails_draw)
    pcoll = bpy.utils.previews.new()
    pcoll.pose_thumbnails = ()
    preview_collections['pose_library'] = pcoll


def unregister():
    '''Unregister all pose thumbnails related things.'''
    bpy.types.DATA_PT_pose_library.remove(pose_thumbnails_draw)
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    del bpy.types.Action.pose_thumbnails
    del bpy.types.WindowManager.pose_thumbnails
