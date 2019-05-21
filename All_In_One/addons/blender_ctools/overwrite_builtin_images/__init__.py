# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    'name': 'Overwrite Builtin Images',
    'author': 'chromoly',
    'version': (0, 2),
    'blender': (2, 77, 0),
    'location': 'UserPreference > Add-ons > Overwrite Builtin Images',
    'description': 'Overwrite splash and icon images',
    'warning': 'Linux only',
    'wiki_url': 'https://github.com/chromoly/blender-OverwriteBuiltinImages',
    'category': 'User Interface',
}


import ctypes
import importlib
import platform

import bpy
import bpy.props

try:
    importlib.reload(utils)
except NameError:
    from . import utils


def test_platform():
    return (platform.platform().split('-')[0].lower()
            not in {'darwin', 'windows'})


def get_size_ptr(blend_cdll, size_name):
    size_addr = ctypes.addressof(getattr(blend_cdll, attrs[size_name]))
    c_int_p = ctypes.POINTER(ctypes.c_int)
    size_p = c_int_p.from_address(size_addr)
    return size_p


def get_image_ptr(blend_cdll, image_name):
    image_addr = ctypes.addressof(getattr(blend_cdll, attrs[image_name]))
    c_uint8_p = ctypes.POINTER(ctypes.c_uint8)
    uint8_arr = c_uint8_p.from_address(image_addr)
    return uint8_arr


# blenderで利用可能な画像フォーマットは source/blender/imbuf/intern/filetype.c
# IMB_FILE_TYPES を参照。
valid_ext = ('.png', '.jpg', '.jpeg', '.jpe', '.tif', '.tiff', '.jp2',
             '.jpc', '.j2k')

attrs = {
    'splash_size': 'datatoc_splash_png_size',
    'splash2x_size': 'datatoc_splash_2x_png_size',
    'splash': 'datatoc_splash_png',
    'splash2x': 'datatoc_splash_2x_png',
    'icons16_size': 'datatoc_blender_icons16_png_size',
    'icons32_size': 'datatoc_blender_icons32_png_size',
    'icons16': 'datatoc_blender_icons16_png',
    'icons32': 'datatoc_blender_icons32_png',
}
attrs.update({v: k for k, v in attrs.items()})


# builtin images
original = {}


def read_original():
    original.clear()
    if test_platform():
        blend_cdll = ctypes.CDLL('')
    else:
        blend_cdll = None
    for size, image in (('splash_size', 'splash'),
                        ('splash2x_size', 'splash2x'),
                        ('icons16_size', 'icons16'),
                        ('icons32_size', 'icons32')):
        if blend_cdll:
            original[size] = get_size_ptr(blend_cdll, size).contents.value
            arr = get_image_ptr(blend_cdll, image)
            original[image] = [arr[i] for i in range(original[size])]
        else:
            original[size] = 0
            original[image] = []


read_original()


def update_image(context, image_type, image_size,
                 update_icons_cache=True):
    if not test_platform():
        return

    pref = OverwriteSplashImagePreferences.get_instance()
    if image_type == 'splash':
        if image_size == 1:
            image_name = 'splash'
        else:
            image_name = 'splash2x'
    else:
        if image_size == 1:
            image_name = 'icons16'
        else:
            image_name = 'icons32'
    size_name = image_name + '_size'
    prop_alert_name = image_name + '_alert'

    blend_cdll = ctypes.CDLL('')
    # size: int
    size_p = get_size_ptr(blend_cdll, size_name)
    # image: char[]
    uint8_arr = get_image_ptr(blend_cdll, image_name)

    def restore():
        # print('restore', image_name, size_name)
        size_p.contents.value = original[size_name]
        int_list = original[image_name]
        for i in range(original[size_name]):
            uint8_arr[i] = int_list[i]
        if image_type == 'icons' and update_icons_cache:
            blend_cdll.ui_resources_free()
            blend_cdll.ui_resources_init()

    setattr(pref, prop_alert_name, False)

    image_path = getattr(pref, image_name)
    if not image_path:
        restore()
        return
    try:
        fp = open(image_path, 'rb')
    except Exception as err:
        print(err)
        restore()
        setattr(pref, prop_alert_name, True)
        return
    if not image_path.endswith(valid_ext):
        print('image type: ' + ', '.join(valid_ext))
        restore()
        setattr(pref, prop_alert_name, True)
        return

    buf = fp.read()
    fp.close()
    if len(buf) > original[size_name]:
        fmt = 'Image size must be {} bytes or less. got {:,} bytes'
        print(fmt.format(original[size_name], len(buf)))
        restore()
        setattr(pref, prop_alert_name, True)
        return

    for i in range(len(buf)):
        uint8_arr[i] = buf[i]
    size_p.contents.value = len(buf)

    if image_type == 'icons' and update_icons_cache:
        blend_cdll.ui_resources_free()
        blend_cdll.ui_resources_init()


def update_splash(self, context):
    update_image(context, 'splash', 1)


def update_splash2x(self, context):
    update_image(context, 'splash', 2)


def update_icons16(self, context):
    update_image(context, 'icons', 1)


def update_icons32(self, context):
    update_image(context, 'icons', 2)


class OverwriteSplashImagePreferences(
        utils.AddonPreferences,
        bpy.types.PropertyGroup if '.' in __name__ else
        bpy.types.AddonPreferences):
    bl_idname = __name__
    splash = bpy.props.StringProperty(
        name='Splash Image',
        description='size: 501x282, max: {:,} bytes ({})'.format(
            original['splash_size'], '/'.join(valid_ext)),
        subtype='FILE_PATH',
        update=update_splash,
    )
    splash2x = bpy.props.StringProperty(
        name='Splash Image 2x',
        description='size: 1002x564, max: {:,} bytes ({})'.format(
            original['splash2x_size'], '/'.join(valid_ext)),
        subtype='FILE_PATH',
        update=update_splash2x,
    )
    splash_alert = bpy.props.BoolProperty(options={'HIDDEN'})
    splash2x_alert = bpy.props.BoolProperty(options={'HIDDEN'})

    icons16 = bpy.props.StringProperty(
        name='Icons 16',
        description='size: 602x640, max: {:,} bytes ({})'.format(
            original['icons16_size'], '/'.join(valid_ext)),
        subtype='FILE_PATH',
        update=update_icons16,
    )
    icons32 = bpy.props.StringProperty(
        name='Icons 32',
        description='size: 1204x1280, max: {:,} bytes ({})'.format(
            original['icons32_size'], '/'.join(valid_ext)),
        subtype='FILE_PATH',
        update=update_icons32,
    )
    icons16_alert = bpy.props.BoolProperty(options={'HIDDEN'})
    icons32_alert = bpy.props.BoolProperty(options={'HIDDEN'})

    def draw(self, context):
        col = self.layout.column()
        row = col.row()
        icon = 'ERROR' if self.splash_alert else 'NONE'
        row.prop(self, 'splash', icon=icon)
        row = col.row()
        icon = 'ERROR' if self.splash2x_alert else 'NONE'
        row.prop(self, 'splash2x', icon=icon)

        row = col.row()
        icon = 'ERROR' if self.icons16_alert else 'NONE'
        row.prop(self, 'icons16', icon=icon)
        row = col.row()
        icon = 'ERROR' if self.icons32_alert else 'NONE'
        row.prop(self, 'icons32', icon=icon)


def restore_all():
    if not test_platform():
        return

    blend_cdll = ctypes.CDLL('')
    for size_name, image_name in (('splash_size', 'splash'),
                                  ('splash2x_size', 'splash2x'),
                                  ('icons16_size', 'icons16'),
                                  ('icons32_size', 'icons32')):
        size_p = get_size_ptr(blend_cdll, size_name)
        size_p.contents.value = original[size_name]
        uint8_arr = get_image_ptr(blend_cdll, image_name)
        int_list = original[image_name]
        for i in range(original[size_name]):
            uint8_arr[i] = int_list[i]
    blend_cdll.ui_resources_free()
    blend_cdll.ui_resources_init()


def register():
    bpy.utils.register_class(OverwriteSplashImagePreferences)
    update_image(bpy.context, 'splash', 1)
    update_image(bpy.context, 'splash', 2)
    update_image(bpy.context, 'icons', 1, False)
    update_image(bpy.context, 'icons', 2)


def unregister():
    bpy.utils.unregister_class(OverwriteSplashImagePreferences)
    restore_all()


if __name__ == '__main__':
    register()
