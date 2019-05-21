# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/blender-color-matching


import bpy
import os
import json
import copy
from mathutils import Vector
from .b3d_lib_int.rgb import RGB


class ColorMatching:

    __matches = []  # search results -> first element - rgb color
    __match_textures = []   # [[image1, texutre1], [image2, texture2], ...]

    @staticmethod
    def search_by_rgb(context, db, rgb, limit):
        __class__.clear(context)
        if db == 'NCS':
            __class__.__matches = NCS_DB.search(rgb, limit)
        elif db == 'RAL_C':
            __class__.__matches = RAL_C_DB.search(rgb, limit)
        elif db == 'RAL_D':
            __class__.__matches = RAL_D_DB.search(rgb, limit)
        elif db == 'RAL_E':
            __class__.__matches = RAL_E_DB.search(rgb, limit)

    @staticmethod
    def matches():
        return __class__.__matches

    @staticmethod
    def matches_str(context, db):
        matches_str = ''
        if __class__.__matches:
            matches_str += '%\t\tRGB\t\t\t'+db+'\t\t\tHEX\t\tCMYK\n'
            for line in __class__.__matches:
                matches_str += '{:<7.2%}\t{:03d}-{:03d}-{:03d}\t{:<15}\t'.format(line[2], int(line[0][0]), int(line[0][1]), int(line[0][2]), line[1][0])
                matches_str += '{}\t{}'.format(line[1][3], '-'.join([a.zfill(3) for a in line[1][1].split('-')]))
                matches_str += '\n'
        return matches_str

    @staticmethod
    def match_textures():
        return __class__.__match_textures

    @staticmethod
    def create_match_textures():
        if __class__.__matches:
            for i, item in enumerate(__class__.__matches):
                img = bpy.data.images.new('colormatch_image' + str(i), 255, 255)
                matchcolor = RGB.fromlist(item[0]).as_linear()
                img.generated_color[0] = matchcolor[0]
                img.generated_color[1] = matchcolor[1]
                img.generated_color[2] = matchcolor[2]
                texture = bpy.data.textures.new('colormatch_texture' + str(i), type='IMAGE')
                texture.image = img
                __class__.__match_textures.append([img, texture])

    @staticmethod
    def clear_match_textures():
        if __class__.__match_textures:
            for item in __class__.__match_textures:
                bpy.data.images.remove(item[0], do_unlink=True)
                bpy.data.textures.remove(item[1], do_unlink=True)
        __class__.__match_textures = []

    @staticmethod
    def clear(context):
        __class__.__matches = []
        __class__.clear_match_textures()


class ColorDB:

    #DB format: [[[RGB], [NCS/RAL, CMYK (C), CMYK (U), HTML]], [...], ...]
    __database = None
    _database_file = None

    @classmethod
    def db(cls):
        if not cls.__database:
            with open(cls._database_file) as data:
                cls.__database = json.load(data)
        return cls.__database

    @classmethod
    def search(cls, rgb, limit):
        rgb_vector = rgb.as_vector()
        db = cls.db()
        rez = copy.deepcopy(sorted(db, key=lambda x: (rgb_vector - Vector((x[0][0], x[0][1], x[0][2]))).length)[:limit])
        for result in rez:
            result.append(RGB.relevance(rgb, RGB.fromlist(result[0])))
        return rez


class NCS_DB(ColorDB):

    _database_file = os.path.join(os.path.dirname(__file__), 'ncs.json')


class RAL_C_DB(ColorDB):

    _database_file = os.path.join(os.path.dirname(__file__), 'ral_c.json')


class RAL_D_DB(ColorDB):

    _database_file = os.path.join(os.path.dirname(__file__), 'ral_d.json')


class RAL_E_DB(ColorDB):

    _database_file = os.path.join(os.path.dirname(__file__), 'ral_e.json')


class ColorMatchingVars(bpy.types.PropertyGroup):
    source_color = bpy.props.FloatVectorProperty(
        name='Color',
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(0.8, 0.8, 0.8, 1.0)
    )


class ColorMatchingStatic:
    matching_count = 5


class DestColorItem(bpy.types.PropertyGroup):
    dest_color = bpy.props.FloatVectorProperty(
         name='Color',
         subtype='COLOR',
         size=4,
         min=0.0,
         max=1.0,
         default=(0.8, 0.8, 0.8, 1.0)
     )


def register():
    bpy.utils.register_class(ColorMatchingVars)
    bpy.utils.register_class(DestColorItem)
    bpy.types.WindowManager.colormatching_vars = bpy.props.PointerProperty(type=ColorMatchingVars)
    bpy.types.WindowManager.colormatching_colors = bpy.props.CollectionProperty(type=DestColorItem)


def unregister():
    del bpy.types.WindowManager.colormatching_colors
    del bpy.types.WindowManager.colormatching_vars
    bpy.utils.unregister_class(DestColorItem)
    bpy.utils.unregister_class(ColorMatchingVars)
