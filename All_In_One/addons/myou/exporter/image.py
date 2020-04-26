import bpy
import struct
import shutil
import tempfile
import os
from math import *
from json import dumps, loads
from collections import defaultdict
from .s3tc import *
from .etc import *
from .pvrtc import *
from .astc import *
from . import progress
tempdir  = tempfile.gettempdir()

type_to_ext = {'JPEG': 'jpg', 'TIFF': 'tif', 'TARGA': 'tga'}

astc_binary_checked = False

plugin_dir = os.path.realpath(__file__).rsplit(os.sep,2)[0]
# TODO: detect platform
convert_binary = os.path.join(plugin_dir,'bin','convert.exe')

def previous_POT(x):
    if x<=0: return 0
    return int(pow(2, floor(log(x)/log(2))))

def save_image(image, path, new_format, resize=None):
    name = image.name

    # Store current render settings
    settings = bpy.context.scene.render.image_settings
    format = settings.file_format
    mode = settings.color_mode
    depth = settings.color_depth

    # Change render settings to our target format
    settings.file_format = new_format
    settings.color_mode = 'RGB' if new_format == 'JPEG' else 'RGBA'
    settings.color_depth = '8'

    # Save image, this does NOT render anything!
    # It only means that the save command will use the current scene's render settings.
    has_error = False
    try:
        if image.packed_file:
            # TODO: save stored file instead of this
            # otherwise color profile may be messing things up
            image.save_render(path)
            src = path
        else:
            src = bpy.path.abspath(image.filepath)
        if resize and (resize[0] != image.size[0] or resize[1] != image.size[1]):
            # TODO: Use fast setting to use scale instead of resize
            print('s11')
            if subprocess.Popen([convert_binary, src, '-resize',
                '{}x{}!'.format(*resize), path]).wait():
                raise Exception("Error while resizing "+image.name)
            print('s12')
        else:
            print('s13')
            if subprocess.Popen([convert_binary, src, path]).wait():
                raise Exception("Error while converting "+image.name)
            print('s14')
    except:
        has_error = True

    # Restore previous render settings
    settings.file_format = format or None
    settings.color_mode = mode
    settings.color_depth = depth

    if has_error:
        raise Exception("Couldn't export image: "+image.name+". Please replace it or disable the texture slot.")


def export_images(dest_path, used_data):
    '''
    This converts/copies all used images and returns encoded JSON with *textures*
    '''
    json_data = []
    if not os.path.exists(dest_path):
        os.mkdir(dest_path)
    elif not os.path.isdir(dest_path):
        raise Exception("Destination path is not a directory: "+dest_path)

    pack_generated_images(used_data)

    # For compatibility with old .blends you need to add
    # 'skip_texture_conversion' to the active scene
    scene = bpy.context.scene
    skip_conversion = scene.get('skip_texture_conversion')

    for image in used_data['images']:
        progress.add()
        print('Img:', image.name)
        if image.source == 'VIEWER':
            raise ValueError('You are using a render result as texture, please save it as image first.')

        image_hash = get_image_hash(image)
        file_name_base = image_hash

        # Find settings in textures. Since there's no UI in Blender for
        # custom properties of images, we'll look at them in textures.
        # Alternatively we'll find global settings in the scene as "texture_lod_levels"
        tex_with_settings = None
        for tex in used_data['image_texture_slots'][image.name]:
            if 'lod_levels' in tex:
                if not tex_with_settings:
                    tex_with_settings = tex
                else:
                    raise Exception('There are several textures with settings for image '+image.name+':\n'+
                        tex_with_settings.name+' and '+tex.name+'. Please remove settings from one of them')

        def parse_lod_levels(levels):
            if isinstance(levels, str):
                return loads(levels)
            else:
                return list(levels)

        lod_levels = []
        if tex_with_settings:
            lod_levels = parse_lod_levels(tex_with_settings['lod_levels'])
        elif 'texture_lod_levels' in scene:
            lod_levels = parse_lod_levels(scene['texture_lod_levels'])

        real_path = bpy.path.abspath(image.filepath)
        tmp_filepath = None
        path_exists = os.path.isfile(real_path)
        # get_png_or_jpg is a function for format encoders that only understand png, jpg
        # TODO: Priorize packed image?
        def get_png():
            nonlocal tmp_filepath
            if tmp_filepath is None:
                tmp_filepath = tempfile.mktemp('.png')
                save_image(image, tmp_filepath, 'PNG')
            return tmp_filepath
        if path_exists and (image.file_format in ['PNG','JPEG'] or image.source == 'MOVIE'):
            get_png_or_jpg = lambda: real_path
            if image.file_format == 'PNG':
                get_png = get_png_or_jpg
        else:
            get_png_or_jpg = get_png
        uses_alpha = image['has_alpha'] # assigned in get_image_hash()
        # is_sRGB = not used_data['image_is_normal_map'].get(image.name, False)
        # if is_sRGB:
        #     print('Image',image.name,'is sRGB')
        # else:
        #     print('Image',image.name,'is linear')
        is_sRGB = False
        image_info = {
            'type': 'TEXTURE',
            'name': image.name,
            'formats': defaultdict(list),
            # 'formats': {
            #     # The list is ordered from low quality to high quality
            #     'png': [{width, height, file_size, file_name, data_uri}, ...]
            #     'jpeg':
            #     'crunch':
            #     'etc1':
            #     'pvrtc':
            # }
            'wrap': None, # null on purpose = setting taken from material
            'filter': None,
            'use_mipmap': None,
            'use_alpha': bool(uses_alpha),
        }

        num_tex_users = len(used_data['image_texture_slots'][image.name])
        print('Exporting image:', image.name, 'with', num_tex_users, 'texture users')
        if uses_alpha:
            print('image:', image.name, 'is using alpha channel')
        if lod_levels:
            print('image:', image.name, 'has lod_levels', lod_levels)

        base_level = None
        if scene.myou_ensure_pot_textures:
            width, height = image.size
            potw = previous_POT(width)
            poth = previous_POT(height)
            if potw != width or poth != height:
                base_level = [potw, poth]

        if image.source == 'FILE':
            out_format = 'JPEG'
            out_ext = 'jpg'
            if uses_alpha:
                out_format = 'PNG'
                out_ext = 'png'
            for lod_level in lod_levels+[base_level]:
                # Skip higher LoD levels configured in the scene
                width, height = image.size
                if lod_level:
                    if isinstance(lod_level, int):
                        width = height = lod_level
                    else:
                        width, height = lod_level
                    if (width > image.size[0] or
                        height > image.size[1]):
                            continue

                if path_exists or image.packed_file:

                    # TODO: Don't convert and flip images all the time!

                    if scene.myou_export_DXT:
                        # TODO: For some reason SOME non-square textures fail
                        # to display in the engine. Making them square for now
                        if scene.myou_export_square=='SMALLER':
                            width = height = min(width, height)
                        else:
                            width = height = max(width, height)
                        file_name = file_name_base + '-{w}x{h}.dds'.format(w=width, h=height)
                        exported_path = os.path.join(dest_path, file_name)
                        print("S3TC out path:", exported_path)
                        if not exists(exported_path):
                            tmp = tempfile.mktemp()+'.png'
                            save_image(image, tmp, 'PNG', resize=(width, height))
                            encode_s3tc(tmp, exported_path, uses_alpha)
                            os.unlink(tmp)
                        # TODO: detect punchthrough alpha?
                        image_info['formats']['dds'].append({
                            'width': width, 'height': height,
                            'file_name': file_name, 'file_size': fsize(exported_path),
                        })

                    if scene.myou_export_ETC1 and not uses_alpha:
                        fast = ''
                        if scene.myou_export_tex_quality=='FAST':
                            fast = '-fast'
                        file_name = file_name_base + fast + '-{w}x{h}.etc1'.format(w=width, h=height)
                        exported_path = os.path.join(dest_path, file_name)
                        if not exists(exported_path):
                            tmp = tempfile.mktemp()
                            save_image(image, tmp, 'PNG', resize=(width, height))
                            encode_etc2_fast(tmp, exported_path,
                                is_sRGB, False, False)
                            os.unlink(tmp)
                        format_enum = get_etc2_format_enum(is_sRGB, False, False)
                        # TODO: detect punchthrough alpha?
                        image_info['formats']['etc1'].append({
                            'width': width, 'height': height,
                            'file_name': file_name, 'file_size': fsize(exported_path),
                            'sRGB': is_sRGB, 'format_enum': format_enum,
                            'bpp': 4,
                        })

                    if scene.myou_export_ETC2:
                        fast = ''
                        if scene.myou_export_tex_quality=='FAST':
                            fast = '-fast'
                        file_name = file_name_base + fast + '-{w}x{h}.etc2'.format(w=width, h=height)
                        exported_path = os.path.join(dest_path, file_name)
                        if not exists(exported_path):
                            tmp = tempfile.mktemp()
                            save_image(image, tmp, 'PNG', resize=(width, height))
                            encode_etc2_fast(tmp, exported_path,
                                is_sRGB, uses_alpha, True)
                            os.unlink(tmp)
                        format_enum = get_etc2_format_enum(is_sRGB, uses_alpha, True)
                        rg11 = False
                        # TODO: detect punchthrough alpha?
                        image_info['formats']['etc2'].append({
                            'width': width, 'height': height,
                            'file_name': file_name, 'file_size': fsize(exported_path),
                            'sRGB': is_sRGB, 'format_enum': format_enum,
                            'bpp':8 if uses_alpha or rg11 else 4,
                        })

                    if scene.myou_export_PVRTC:
                        fast = square = ''
                        if scene.myou_export_tex_quality=='FAST':
                            fast = '-fast'
                        use_smaller = scene.myou_export_square == 'SMALLER'
                        if use_smaller:
                            w = h = min(width, height)
                        else:
                            w = h = max(width, height)
                        file_name = file_name_base + fast + '-{w}x{h}.pvr'.format(w=w, h=h)
                        exported_path = os.path.join(dest_path, file_name)
                        bpp = int(scene.myou_export_pvr_mode)
                        if not exists(exported_path):
                            tmp = tempfile.mktemp()+'.png'
                            save_image(image, tmp, 'PNG', resize=(width, height))
                            encode_pvrtc(tmp, exported_path,
                                bool(fast), uses_alpha, bpp==2, use_smaller)
                            os.unlink(tmp)
                        format_enum = get_pvrtc_format_enum(is_sRGB, uses_alpha, bpp==2)
                        rg11 = False
                        # TODO: detect punchthrough alpha?
                        image_info['formats']['pvrtc'].append({
                            'width': width, 'height': height,
                            'file_name': file_name, 'file_size': fsize(exported_path),
                            'sRGB': is_sRGB, 'format_enum': format_enum,
                            'bpp': bpp,
                        })

                    if scene.myou_export_ASTC:
                        if not astc_binary_checked:
                            download_astc_tools_if_needed()
                        fast = ''
                        quality = 'exhaustive'
                        if scene.myou_export_tex_quality=='FAST':
                            fast = '-fast'
                            quality = 'veryfast'
                        file_name = file_name_base + fast + '-{w}x{h}.astc'.format(w=width, h=height)
                        exported_path = os.path.join(dest_path, file_name)
                        if not exists(exported_path):
                            encode_astc(get_png_or_jpg(), exported_path,
                                scene.myou_export_astc_mode, quality, is_sRGB)
                        format_enum = get_astc_format_enum(scene.myou_export_astc_mode, is_sRGB)
                        # TODO: query exported size?
                        image_info['formats']['astc'].append({
                            'width': image.size[0], 'height': image.size[1],
                            'file_name': file_name, 'file_size': fsize(exported_path),
                            'sRGB': is_sRGB, 'format_enum': format_enum,
                        })

                    # image['exported_extension'] is only used
                    # for material.uniform['filepath'] which is only used
                    # in old versions of the engine.
                    # Current versions use the exported list of textures instead
                    image['exported_extension'] = out_ext

                    # Cases in which we can or must skip conversion
                    just_copy_file = \
                        path_exists and \
                        (image.file_format == out_format or skip_conversion) and \
                        lod_level is None
                    if just_copy_file:
                        file_name = file_name_base + '.' + out_ext
                        exported_path = os.path.join(dest_path, file_name)
                        # The next 2 lines are only necessary for skip_conversion
                        out_ext = image.filepath_raw.split('.')[-1]
                        image['exported_extension'] = out_ext
                        if not exists(exported_path):
                            shutil.copy(real_path, exported_path)
                        image_info['formats'][out_format.lower()].append({
                            'width': image.size[0], 'height': image.size[1],
                            'file_name': file_name, 'file_size': fsize(exported_path),
                        })
                        print('Copied original image')
                    else:
                        if lod_level is not None:
                            file_name = file_name_base + '-{w}x{h}.{e}'.format(w=width, h=height, e=out_ext)
                            exported_path = os.path.join(dest_path, file_name)
                            if not exists(exported_path):
                                save_image(image, exported_path, out_format, resize=(width, height))
                            image_info['formats'][out_format.lower()].append({
                                'width': width, 'height': height,
                                'file_name': file_name,
                                'file_size': fsize(exported_path),
                            })

                            print('Image resized to '+str(lod_level)+' and exported as '+out_format)
                        else:
                            file_name = file_name_base + '.' + out_ext
                            exported_path = os.path.join(dest_path, file_name)
                            if not exists(exported_path):
                                save_image(image, exported_path, out_format)
                            image_info['formats'][out_format.lower()].append({
                                'width': image.size[0], 'height': image.size[1],
                                'file_name': file_name, 'file_size': fsize(exported_path),
                            })
                            print('Image exported as '+out_format)
                else:
                    raise Exception('\n'.join(['Image not found:',
                        'Name: ' + image.name,
                        'Path: ' + real_path,
                        'Materials: ' + ', '.join(m.name for m in used_data['image_materials'][image.name]),
                    ]))
        elif image.source == 'MOVIE' and path_exists:
            out_ext = image.filepath_raw.split('.')[-1]
            file_name = file_name_base + '.' + out_ext
            exported_path = os.path.join(dest_path, file_name)
            image['exported_extension'] = out_ext
            if path_exists:
                if not exists(exported_path):
                    shutil.copy(real_path, exported_path)
                file_format = image.file_format.lower()
                file_name_extension = file_name.split('.')[-1].lower()

                # unsuported video file_format in blender
                if file_format != file_name_extension:
                    print("WARNING: File format doesn't match file name extension")
                file_format = file_name_extension

                image_info['formats'][file_format].append({
                    'width': image.size[0], 'height': image.size[1],
                    'file_name': file_name, 'file_size': fsize(exported_path),
                })
                print('Copied original video:' + file_name + ' format:' + image.file_format.lower())
        else:
            raise Exception('Image source not supported: ' + image.name + ' source: ' + image.source)

        # Embed all images that are 64x64 or lower.
        # To change the default 64x64, add an 'embed_max_size' property
        # to the scene, set the value (as integer) and a max range >= the value
        # (if you don't change the max range, the final value used gets clamped)
        for fmt, datas in image_info['formats'].items():
            for data in datas:
                if fmt in ['png', 'jpeg'] and \
                        max(data['width'],data['height']) <= scene.get('embed_max_size', 64) and \
                        data.get('file_name', None):
                    exported_path = os.path.join(dest_path, data['file_name'])
                    data['data_uri'] = file_path_to_data_uri(exported_path, fmt)
                    data['file_name'] = None
                    del data['file_name']
        if tmp_filepath:
            os.unlink(tmp_filepath)
        print()
        json_data.append(image_info)
    return json_data

def pack_generated_images(used_data):
    for image in used_data['images']:
        if image.source == 'GENERATED': #generated or rendered
            print('Generated image will be packed as png')
            #The image must be saved in a temporal path before packing.
            tmp_filepath = tempfile.mktemp('.png')
            image.file_format = 'PNG'
            image.filepath_raw = tmp_filepath
            image.save()
            image.pack()
            image.filepath = ''
            os.unlink(tmp_filepath)

def image_has_alpha(image):
    # TODO: also check if any use_alpha of textures is enabled
    if not image.use_alpha or image.source == 'MOVIE':
        return False
    elif not bpy.context.scene.get('skip_texture_conversion') \
            and bpy.context.scene.myou_export_JPEG_compress == 'COMPRESS':
        # If it's not a format known to not have alpha channel,
        # make sure it has an alpha channel at all
        # by saving it as PNG and parsing the meta data
        if image.file_format not in ['JPEG', 'TIFF'] and image.frame_duration < 2:
            path = bpy.path.abspath(image.filepath)
            # TODO: swap conditions?
            if image.file_format == 'PNG' and os.path.isfile(path):
                return png_file_has_alpha(path)
            elif image.packed_file or os.path.isfile(path):
                tmp_filepath = tempfile.mktemp('.png')
                save_image(image, tmp_filepath, 'PNG')
                has_alpha = png_file_has_alpha(tmp_filepath)
                os.unlink(tmp_filepath)
                return has_alpha
        else:
            return False
    else:
        return image.file_format != 'JPEG'

def png_file_has_alpha(file_path):
    # TODO: Read from packed file?
    try:
        file = open(file_path, 'rb')
        file.seek(8, 0)
        has_alpha_channel = False
        has_transparency_chunk = False
        end = False
        max_bytes = 12
        while not end:
            data_bytes, tag = struct.unpack('!I4s', file.read(8))
            data = file.read(min(data_bytes, max_bytes))
            file.seek(max(0, data_bytes-max_bytes) + 4, 1)
            if tag == b'IHDR':
                if data[9] in [4,6]:
                    has_alpha_channel = True
            if tag == b'tRNS':
                has_transparency_chunk = True
            end = tag == b'IEND'
    except:
        raise Exception("Couldn't read PNG file "+file_path)
    if has_alpha_channel or has_transparency_chunk:
        # if the answer is affirmative, let's check the individual pixels
        # to see if any is not opaque
        img = bpy.data.images.new('tmp', 1, 1)
        img.filepath = file_path
        img.source = 'FILE'
        img.reload()
        opaque = sum(list(img.pixels)[3::4]) == len(img.pixels) / 4
        bpy.data.images.remove(img)
        return not opaque
    return False

def fsize(path):
    return os.stat(path).st_size

import base64
def file_path_to_data_uri(path, type):
    data = base64.b64encode(open(path, 'rb').read()).decode().replace('\n', '')
    return 'data:image/'+type.lower()+';base64,'+data

from struct import unpack
def get_crcs_from_png_data(data):
    pos = 8
    length = data[pos:pos+4]
    crcs = b''
    while len(length) == 4:
        l = unpack('>I', length)[0]
        crcs += data[pos+8+l:pos+12+l]
        pos += 12+l
        length = data[pos:pos+4]
    return crcs

from os.path import exists, getmtime
import time
from bpy.path import abspath
import hashlib, codecs
hash_version = 3 # increment when there's any change on texture conversion
# TODO: It doesn't invalidate cache?

def get_image_hash(image):
    recompute_hash = True
    filename = abspath(image.filepath)
    if 'image_hash' in image:
        # get date (from file or packed crc)
        # if packed
        #    if png, get crc date
        #    else, get file date or blend date
        # else, get file date
        date = 0
        if image.packed_file:
            if image.file_format == 'PNG':
                crc = get_crcs_from_png_data(image.packed_file.data)
                if crc == image.get('packed_crc', b''):
                    date = image['packed_crc_date']
                else:
                    image['packed_crc'] = crc
                    image['packed_crc_date'] = date = time.time()
            elif not exists(filename) and exists(bpy.data.filepath):
                filename = bpy.data.filepath
        if date == 0 and exists(filename):
            date = getmtime(filename)
        recompute_hash = date > image['hash_date'] \
            or image.get('hash_version') != hash_version \
            or image.get('hash_file_name') != image.filepath
    if recompute_hash:
        # for our use case,
        # MD5 is good enough, fast enough and available natively
        if image.packed_file:
            digest = hashlib.md5(image.packed_file.data).digest()
        elif exists(filename):
            md5 = hashlib.md5()
            file = open(filename, 'rb')
            chunk = file.read(1048576)
            while chunk:
                md5.update(chunk)
                chunk = file.read(1048576)
            digest = md5.digest()
        else:
            # file not found, always reset hash next time
            image['image_hash'] = ''
            image['hash_date'] = 0
            image['hash_file_name'] = ''
            image['has_alpha'] = True
            return
        # convert digest to unpadded base64url
        hash = codecs.encode(digest, 'base64').strip(b'=\n') \
            .replace(b'+',b'-').replace(b'/',b'_').decode()
        image['image_hash'] = hash
        image['hash_date'] = time.time()
        image['has_alpha'] = image_has_alpha(image)
        image['hash_file_name'] = image.filepath
        image['hash_version'] = hash_version
    return image['image_hash']
