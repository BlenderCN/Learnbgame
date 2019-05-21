import bpy


DEFAULT_POSE_SUFFIX = '[T]'


def change_suffix(pose, old_suffix, new_suffix):
    '''Change the old suffix to the new one.'''
    clean_name = pose.name[:-len(old_suffix)]
    pose.name = ' '.join((clean_name, new_suffix))


def update_pose_suffixes(self, context):
    '''Update the pose suffixes when the user pref is changed.'''
    for poselib in bpy.data.actions:
        if poselib.pose_markers:
            if poselib.pose_thumbnails.suffix != self.pose_suffix:
                for pose in poselib.pose_markers:
                    old_suffix = poselib.pose_thumbnails.suffix
                    new_suffix = self.pose_suffix
                    change_suffix(pose, old_suffix, new_suffix)
                poselib.pose_thumbnails.suffix = self.pose_suffix


class PoseThumbnailsPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    add_3dview_prop_panel = bpy.props.BoolProperty(
        name='Add 3D View Properties Panel',
        description=('Also add a panel to the Properties Panel of the 3D View.'),
        default=True,
        )
    pose_suffix = bpy.props.StringProperty(
        name='Pose Suffix',
        description=('Add this suffix to the name of a pose when it has a'
                     ' thumbnail. Leave empty to add nothing.'),
        default=DEFAULT_POSE_SUFFIX,
        update=update_pose_suffixes,
        )
    thumbnail_size = bpy.props.FloatProperty(
        name='Thumbnail Size',
        description='How large to draw the pose thumbnails.',
        default=1.0,
        min=0.1,
        max=5.0,
        )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'thumbnail_size')
        layout.prop(self, 'add_3dview_prop_panel')
        layout.prop(self, 'pose_suffix')
