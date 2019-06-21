"""Pose thumbnail creation."""

import collections
import difflib
import logging
import os
import re

import bpy
from bpy_extras.io_utils import ImportHelper

from . import common

logger = logging.getLogger(__name__)
IMAGE_EXTENSIONS = {
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
}


def is_image_file(filepath):
    """Check if the file is an image file."""
    file_extension = os.path.splitext(filepath)[-1]
    return file_extension.lower() in IMAGE_EXTENSIONS


def get_pose_from_thumbnail(thumbnail):
    """Get the pose that belongs to the thumbnail.

    Args:
        thumbnail (PropertyGroup): thumbnail info of a pose

    Returns:
        pose_marker
    """
    if thumbnail is None:
        return
    poselib = bpy.context.object.pose_library
    for pose in poselib.pose_markers:
        if pose.frame == thumbnail.frame:
            return pose


def draw_creation(layout, pose_thumbnail_options, poselib):
    if poselib.library:
        layout.label('Not showing creation options for linked pose libraries')
        layout.operator(
            POSELIB_OT_refresh_thumbnails.bl_idname,
            icon='FILE_REFRESH',
            text='Refresh',
        )
        return
    layout.separator()
    box = layout.box()
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
            logger.debug('No active pose markers, aborting')
            return
        thumbnail = common.get_thumbnail_from_pose(poselib.pose_markers.active)
        if thumbnail and thumbnail.filepath != common.get_no_thumbnail_path():
            text = 'Replace'
        else:
            text = 'Add'
        row = sub_col.row(align=True)
        row.operator(POSELIB_OT_add_thumbnail.bl_idname, text=text)
        row.operator(POSELIB_OT_add_thumbnails_from_dir.bl_idname, text='Batch Add/Change')
        row = sub_col.row(align=True)
        row_col = row.column(align=True)
        row_col.operator(POSELIB_OT_remove_pose_thumbnail.bl_idname, text='Remove')
        if common.get_thumbnail_from_pose(poselib.pose_markers.active):
            row_col.enabled = True
        else:
            row_col.enabled = False
        row_col = row.column(align=True)
        row_col.operator(POSELIB_OT_remove_all_thumbnails.bl_idname, text='Remove All')
        if poselib.pose_thumbnails:
            row_col.enabled = True
        else:
            row_col.enabled = False
        sub_col.separator()
        sub_col.operator(
            POSELIB_OT_refresh_thumbnails.bl_idname,
            icon='FILE_REFRESH',
            text='Refresh',
        )


class POSELIB_OT_add_thumbnail(bpy.types.Operator, ImportHelper):
    """Add a thumbnail to a pose"""
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
        thumbnail = (common.get_thumbnail_from_pose(pose) or
                     poselib.pose_thumbnails.add())
        thumbnail.frame = pose.frame
        thumbnail.filepath = filepath
        common.clear_cached_pose_thumbnails()
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, 'use_relative_path')


class POSELIB_OT_add_thumbnails_from_dir(bpy.types.Operator, ImportHelper):
    """Add thumbnails from a directory to poses from a pose library"""
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
        ('INDEX', 'Index', 'Map the files to the order of the poses (the files are sorted by name, '
                           'so numbering them makes sense).'),
        ('FRAME', 'Frame', 'Map the files to the order of the frame number of the poses.'),
    )
    mapping_method = bpy.props.EnumProperty(
        name='Match by',
        description='Match the thumbnail images to the poses by using this method',
        items=map_method_items,
    )
    overwrite_existing = bpy.props.BoolProperty(
        name='Overwrite existing',
        description='Overwrite existing thumbnails of the poses',
        default=True,
    )
    match_fuzzyness = bpy.props.FloatProperty(
        name='Fuzzyness',
        description='Fuzzyness of the matching (0 = exact match, 1 = everything)',
        min=0.0,
        max=1.0,
        default=0.4,
    )
    match_by_number = bpy.props.BoolProperty(
        name='Match by number',
        description='If the filenames start with a number, match the number to the pose index/frame',
        default=False,
    )
    start_number = bpy.props.IntProperty(
        name='Start number',
        description='The image number to map to the first pose',
        default=1,
    )
    use_relative_path = bpy.props.BoolProperty(
        name='Relative Path',
        description='Select the file relative to the blend file',
        default=True,
    )

    def get_images_from_dir(self):
        """Get all image files from a directory."""
        directory = self.directory
        logger.debug('reading thumbs from %s', directory)
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
                    logger.warning(
                        ' Skipping file {0} because it\'s not an image.'.format(image_file))
                continue
            if self.use_relative_path:
                image_paths.append(bpy.path.relpath(image_path))
            else:
                image_paths.append(image_path)
        return image_paths

    def create_thumbnail(self, pose, image):
        """Create or update the thumbnail for a pose."""
        if not self.overwrite_existing and common.get_thumbnail_from_pose(pose):
            return
        poselib = self.poselib
        thumbnail = (common.get_thumbnail_from_pose(pose) or
                     poselib.pose_thumbnails.add())
        thumbnail.frame = pose.frame
        thumbnail.filepath = image

    def get_image_by_number(self, number):
        """Return a the image file if it contains the number.

        Check if the filename contains the number. It matches the first number
        found in the filename (starting from the left).
        """
        for image in self.image_files:
            basename = os.path.basename(image)
            match = re.match(r'^.*?([0-9]+)', basename)
            if match:
                image_number = int(match.groups()[0])
                if number == image_number:
                    return image

    def match_thumbnails_by_name(self):
        """Assign the thumbnail by trying to match the pose name with a file name."""
        poselib = self.poselib
        image_files = self.image_files
        match_map = {os.path.splitext(os.path.basename(f))[0]: f for f in image_files}
        for pose in poselib.pose_markers:
            match = difflib.get_close_matches(
                pose.name,
                match_map.keys(),
                n=1,
                cutoff=1.0 - self.match_fuzzyness,
            )
            if match:
                thumbnail_image = match_map[match[0]]
                self.create_thumbnail(pose, thumbnail_image)

    def match_thumbnails_by_index(self):
        """Map the thumbnail images to the index of the poses."""
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
        """Map the thumbnail images to the frame of the poses."""
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
        """Try to match the image files to the poses."""
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
        common.clear_cached_pose_thumbnails()
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


class POSELIB_OT_remove_pose_thumbnail(bpy.types.Operator):
    """Remove a thumbnail from a pose"""
    bl_idname = 'poselib.remove_thumbnail'
    bl_label = 'Remove Thumbnail'
    bl_options = {'PRESET', 'UNDO'}

    def execute(self, context):
        poselib = context.object.pose_library
        pose = poselib.pose_markers.active
        common.clear_cached_pose_thumbnails()
        for i, thumbnail in enumerate(poselib.pose_thumbnails):
            if pose.frame == thumbnail.frame:
                poselib.pose_thumbnails.remove(i)
                break
        return {'FINISHED'}


class POSELIB_OT_remove_all_thumbnails(bpy.types.Operator):
    """Remove all thumbnails"""
    bl_idname = 'poselib.remove_all_thumbnails'
    bl_label = 'Remove All Thumbnails'
    bl_options = {'PRESET', 'UNDO'}

    def execute(self, context):
        poselib = context.object.pose_library
        poselib.pose_thumbnails.clear()
        common.clear_cached_pose_thumbnails()
        return {'FINISHED'}


class POSELIB_OT_refresh_thumbnails(bpy.types.Operator):
    """Reloads and cleans the thumbnails and poses"""
    bl_idname = 'poselib.refresh_thumbnails'
    bl_label = 'Refresh Thumbnails'
    bl_options = {'PRESET', 'UNDO'}

    def remove_thumbnail(self, thumbnail):
        """Remove the thumbnail from the poselib thumbnail info."""
        pose_thumbnails = self.poselib.pose_thumbnails
        for i, existing_thumbnail in enumerate(pose_thumbnails):
            if thumbnail == existing_thumbnail:
                logger.debug('removing thumbnail %r at index %d', thumbnail, i)
                pose_thumbnails.remove(i)

    def remove_unused_thumbnails(self):
        """Remove unused thumbnails."""

        thumbs = self.poselib.pose_thumbnails
        count = len(thumbs)
        for i, thumbnail in enumerate(reversed(thumbs)):
            if not get_pose_from_thumbnail(thumbnail):
                thumbs.remove(count - i - 1)

    def remove_double_thumbnails(self):
        """Remove extraneous thumbnails from a pose."""
        thumbnail_map = collections.defaultdict(list)
        for thumbnail in self.poselib.pose_thumbnails:
            thumbnail_map[str(thumbnail.frame)].append(thumbnail)

        for thumbnail_list in thumbnail_map.values():
            for thumbnail in thumbnail_list[:-1]:
                self.remove_thumbnail(thumbnail)

    def execute(self, context):
        self.poselib = context.object.pose_library
        self.remove_unused_thumbnails()
        self.remove_double_thumbnails()
        common.clear_cached_pose_thumbnails(full_clear=True)
        return {'FINISHED'}


classes = [
    POSELIB_OT_refresh_thumbnails,
    POSELIB_OT_remove_all_thumbnails,
    POSELIB_OT_remove_pose_thumbnail,
    POSELIB_OT_add_thumbnails_from_dir,
    POSELIB_OT_add_thumbnail,
]


def register():
    """Register all pose thumbnail creation related things."""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister all pose thumbnails creation related things."""
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as ex:
            logger.exception('Unable to unregister %s', cls)
