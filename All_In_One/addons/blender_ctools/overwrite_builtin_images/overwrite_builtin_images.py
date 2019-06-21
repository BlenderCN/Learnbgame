#!/usr/bin/env python3


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


"""
blender-2.75aのスプラッシュ画像を置換する。(2.75も可？)
linuxとwindowsでのみ使える。動作確認は公式の2.75a-64bit(linux,win)のみ。
バイナリを弄るので自己責任で。
"""


import sys
import os
import hashlib
import platform
from collections import OrderedDict
import struct
import pprint
import copy


log_name = 'overwrite_builtin_images.log'

# blenderで利用可能な画像フォーマットは source/blender/imbuf/intern/filetype.c
# IMB_FILE_TYPES を参照。
valid_ext = ('.png', '.jpg', '.jpeg', '.jpe', '.tif', '.tiff', '.jp2',
             '.jpc', '.j2k')


def find_png(buf, width, height):
    """bytesの中からpngを探してそのアドレスとサイズを返す
    icon画像はコンパイル時にsvgからpngに変換しているので中身は環境依存
    """
    a = 0
    while True:
        addr = buf.find(b'\x89PNG\r\n\x1a\n', a)
        if addr == -1:
            break
        image_addr = addr
        w = h = 0
        chunk_end = False
        addr += 8
        while not chunk_end:
            chunk_length, chunk_type = struct.unpack(
                '>I4s', buf[addr: addr + 8])
            addr += 8
            if chunk_type == b'\x00\x00\x00\x00':  # 不正なpngが存在
                break
            if chunk_type == b'IHDR':
                w, h = struct.unpack('>2I', buf[addr: addr + 8])
            elif chunk_type == b'IEND':
                chunk_end = True
            addr += chunk_length + 4
        image_size = addr - image_addr
        if w == width and h == height:
            return image_addr, image_size
        a = addr

    return -1, 0


def get_defalut_target():
    p = platform.platform().split('-')[0].lower()
    if p == 'linux':
        target = 'blender'
    elif p == 'windows':
        target = 'blender-app.exe'
    else:  # 'darwin'
        target = ''
    return target


def main(target, extract=False):
    if target:
        target = os.path.abspath(target)
    else:
        target = get_defalut_target()
        if not target:
            return

    with open(target, 'rb') as fp:
        bl_bytes = fp.read()
        bl = bytearray(bl_bytes)

    if not bl:
        print('Not found {}'.format(target))
        sys.exit()

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    splash = splash2x = icons16 = icons32 = log = None
    splash_name = splash2x_name = icons16_name = icons32_name = ''
    for name in os.listdir('.'):
        base, ext = os.path.splitext(name)
        if base == 'splash' and ext in valid_ext:
            with open(name, 'rb') as fp:
                splash = bytearray(fp.read())
                splash_name = name
        elif base == 'splash_2x' and ext in valid_ext:
            with open(name, 'rb') as fp:
                splash2x = bytearray(fp.read())
                splash2x_name = name
        elif base == 'icons16' and ext in valid_ext:
            with open(name, 'rb') as fp:
                icons16 = bytearray(fp.read())
                icons16_name = name
        elif base == 'icons32' and ext in valid_ext:
            with open(name, 'rb') as fp:
                icons32 = bytearray(fp.read())
                icons32_name = name
        elif name == log_name:
            with open(name, 'r') as fp:
                log = fp.read()

    if log:
        image_addresses = OrderedDict(eval(log))
    else:
        image_addresses = OrderedDict()
    m = hashlib.md5()
    m.update(bl)
    h = m.hexdigest()
    if h in image_addresses:
        d = image_addresses[h]
        splash_addr, splash_capacity, splash_size = d['splash']
        splash2x_addr, splash2x_capacity, splash2x_size = d['splash2x']
        icons16_addr, icons16_capacity, icons16_size = d['icons16']
        icons32_addr, icons32_capacity, icons32_size = d['icons32']
    else:
        splash_addr, splash_size = find_png(bl_bytes, 501, 282)
        splash2x_addr, splash2x_size = find_png(bl_bytes, 1002, 564)
        icons16_addr, icons16_size = find_png(bl_bytes, 602, 640)
        icons32_addr, icons32_size = find_png(bl_bytes, 1204, 1280)
        splash_capacity = splash_size
        splash2x_capacity = splash2x_size
        icons16_capacity = icons16_size
        icons32_capacity = icons32_size
        assert (splash_addr != -1 and splash2x_addr != -1 and
                icons16_addr != -1 and icons16_addr != -1)
        d = {'splash': [splash_addr, splash_capacity, splash_size],
             'splash2x': [splash2x_addr, splash2x_capacity, splash2x_size],
             'icons16': [icons16_addr, icons16_capacity, icons16_size],
             'icons32': [icons32_addr, icons32_capacity, icons32_size],
             }
        image_addresses[h] = d

    if extract:
        with open('splash.builtin', 'wb') as fp:
            fp.write(bl[splash_addr: splash_addr + splash_size])
        with open('splash_2x.builtin', 'wb') as fp:
            fp.write(bl[splash2x_addr: splash2x_addr + splash2x_size])
        with open('icons16.builtin', 'wb') as fp:
            fp.write(bl[icons16_addr: icons16_addr + icons16_size])
        with open('icons32.builtin', 'wb') as fp:
            fp.write(bl[icons32_addr: icons32_addr + icons32_size])
        print('Extracted. splash.builtin, splash_2x.builtin, icons16.builtin, '
              'icons32.builtin')
        sys.exit()

    def write_image(image_addr, image_capacity, image, file_name):
        image_size = len(image)
        if image_size > image_capacity:
            print('{} is {} bytes. Max: {} bytes'.format(
                file_name, image_size, image_capacity))
        bl[image_addr: image_addr + image_size] = image
        n = image_capacity - image_size
        bl[image_addr + image_size: image_addr + image_size + n] = bytearray(n)

    if splash:
        write_image(splash_addr, splash_capacity, splash, splash_name)
        splash_size = len(splash)
    if splash2x:
        write_image(splash2x_addr, splash2x_capacity, splash2x, splash2x_name)
        splash2x_size = len(splash2x)
    if icons16:
        write_image(icons16_addr, icons16_capacity, icons16, icons16_name)
        icons16_size = len(icons16)
    if icons32:
        write_image(icons32_addr, icons32_capacity, icons32, icons32_name)
        icons32_size = len(icons32)

    # overwrite
    with open(target, 'wb') as fp:
        fp.write(bl)
    names = ', '.join([name for name in [splash_name, splash2x_name,
                                         icons16_name, icons32_name]
                       if name])
    if names:
        print('Overwrite with ' + names)

    # write log file
    m = hashlib.md5()
    m.update(bl)
    d_cp = copy.deepcopy(d)
    d_cp['splash'][2] = splash_size
    d_cp['splash2x'][2] = splash2x_size
    d_cp['icons16'][2] = icons16_size
    d_cp['icons32'][2] = icons32_size
    image_addresses[m.hexdigest()] = d_cp
    with open(log_name, 'w') as fp:
        fp.write(pprint.pformat(list(image_addresses.items())))


script_usage = """
1. Copy images and script to blender directory:
  blender --- blender-app.exe (or blender (linux))
           |- splash.png (png / jpeg / tiff /jpeg2000)
           |    (size: 501x282, max: 187546 bytes))
           |- splash_2x.png (png / jpeg / tiff /jpeg2000)
           |    (size: 1002x564, max: 632582 bytes)
           |- icons16.png (png / jpeg / tiff /jpeg2000)
           |    (size: 602x640, max: about 200kB)
           |- icons32.png (png / jpeg / tiff /jpeg2000)
           |    (size: 1204x1280, max: about 550kB)
           `- overwrite_builtin_images.py (this script)
2. Run this script:
  python3 overwrite_builtin_images.py
"""

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description='Overwrite blender-2.75(a) splash/icons image',
        usage=script_usage
    )
    parser.add_argument(
        '-t', '--target',
        default=get_defalut_target(),
        type=str,
        required=False,
        help='overwrite target. (default: {})'.format(get_defalut_target()),
    )
    parser.add_argument(
        '--extract',
        action='store_const',
        const=True,
        default=False,
        required=False,
        help='Extract splash and icon images in the target',
    )

    args = parser.parse_args()
    main(args.target, args.extract)
