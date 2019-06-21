import functools
import re

import bpy


def clear_charnamere_cache(self: 'PoseThumbnailsPreferences', context):
    self.character_name_re.cache_clear()


def for_addon(context=None) -> 'PoseThumbnailsPreferences':
    """Return preferences for this add-on.

    If the context is given it is used, defaulting to bpy.context.
    """
    context = context or bpy.context
    return context.user_preferences.addons[__package__].preferences


class PoseThumbnailsPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    add_3dview_prop_panel = bpy.props.BoolProperty(
        name='Add 3D View Properties Panel',
        description='Also add a panel to the Properties Panel of the 3D View',
        default=True,
    )
    thumbnail_size = bpy.props.FloatProperty(
        name='Thumbnail Size',
        description='How large to draw the pose thumbnails',
        default=1.0,
        min=0.1,
        max=5.0,
    )
    character_name_regexp = bpy.props.StringProperty(
        name='Character Name Regexp',
        description='Obtains the character name from the object name',
        default='[A-Za-z0-9_]+',
        update=clear_charnamere_cache,
    )
    optional_name_prefix = bpy.props.StringProperty(
        name='Optional Object Prefix',
        description='Strip this off the object name before determining the Character Name. '
                    'Ignored if the object name does not start with this',
        default='RIG-',
    )
    pose_lib_name_prefix = bpy.props.StringProperty(
        name='Pose Library Name Prefix',
        description='Only Actions whose name start with this prefix are considered Pose Libraries',
        default='PLB-',
    )

    @functools.lru_cache(maxsize=1)
    def character_name_re(self):
        """Compile the character name regexp.

        Cached for fast reuse.
        """
        return re.compile(self.character_name_regexp)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'thumbnail_size')
        layout.prop(self, 'add_3dview_prop_panel')

        layout.separator()
        col = layout.box()
        col.label('Character Name and Pose Library recognition:', icon='TRIA_RIGHT')
        row = col.row(align=True)
        row.prop(self, 'character_name_regexp')
        row.operator('poselib.help_regexp', icon='HELP', text='')

        col = col.column(align=True)
        col.prop(self, 'optional_name_prefix')
        col.prop(self, 'pose_lib_name_prefix')
        try:
            re.compile(self.character_name_regexp)
        except re.error as ex:
            col.label('Error in regular expression: %s at position %s' % (ex.msg, ex.pos),
                      icon='ERROR')
        else:
            from . import core
            char = self.optional_name_prefix + 'Alpha_monster-blenrig.001'
            pl = core.pose_library_name_prefix(char, context)
            col.label('Object %r will use Pose Libraries %r' % (char, pl + '…'))
