 # -*- coding: utf-8 -*-
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
    "name": "Nikitron tools",
    "version": (2, 1, 5),
    "blender": (2, 7, 9),  
    "category": "Learnbgame",
    "author": "Nikita Gorodetskiy",
    "location": "object",
    "description": "Nikitron tools - vertices and object names, curves to 3d, material to object mode, spread objects, bounding boxes",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Object/Nikitron_tools",          
    "tracker_url": "http://www.blenderartists.org/forum/showthread.php?272679-Addon-WIP-Sverchok-parametric-tool-for-architects",  
}

# 2.1.5 - комплименты добавляю слово

import bpy
from mathutils.geometry import intersect_line_plane
import mathutils
from mathutils import Vector
import math
from math import radians
import re
import os
import random
import bmesh
from bpy_extras.object_utils import object_data_add
from bpy.props import IntProperty, BoolProperty, EnumProperty, FloatProperty
import operator

my_str_classes = [
                'CurvesTo3D', 'CurvesTo2D', 'NikitronPanel', 'ObjectNames',
                'VerticesNumbers3D', 'Connect2Meshes', 'MaterialToObjectAll',
                'MaterialToDataAll', 'BoundingBox', 'SpreadObjects',
                'DeleteOrientation', 'SeparatorM', 'BooleratorRandom',
                'BooleratorTranslation', 'BooleratorIntersection',
                'ComplimentWoman', 'AreaOfLenin', 'EdgeLength',
                'CliffordAttractors', 'NT_ClearNodesLayouts',
                'NT_language', 'ComplimMan', 'Title_section', 'CleanLayoutUsed',
                'Curves_section', 'verticesNum_separator', 'shift_vers',
                'hook', 'maxvers', 'Mesh_section', 'toolsetNT',
                'NTTextMeshWeld', 'areaseps', 'areacoma',
                'volume', 'NTManifestGenerator', 'NTbezierOrdering',
                'NTduplicat', 'NTScaleFit', 'Volums'
                ]
                
my_var_names = [] # extend with veriables names
sv_lang = {}
handle_lang = True

ru_dict = [
                'Кривые_3М', 'Кривые_2М', 'ИНСТРУМЕНТЫ НТ', 'Имена Об',
                'Верш 3М', 'Соединить 2', 'Мат в Об',
                'Мат в Дан', 'Габарит', 'Разложить',
                'Уд ориентацию', 'Разделить', 'Бул С',
                'Бул П', 'Бул Х',
                'Копмлимент', 'Площ гра', 'Длин рёб',
                'Супер кривые', 'Уд раскладки',
                'english', 'Мужской', 'ГЛАВНЫЕ', 'и активные',
                'КРИВЫЕ', 'Верш', 'Сдвиг',
                'Крюк', 'МаксВер', 'СЕТКА', 'ИНСТРУМЕНТЫ НТ',
                'ТЕКСТ+СЕТКА', 'Разделитель', 'Точка',
                'Объём', 'МаниФест', 'Безье выпрямить', 
                'Дубликаты', 'МасшВОбъём', 'Единицы'
                ]
                
en_dict = [
                'Curves_3D', 'Curves_2D', 'NT toolset', 'Obj Names',
                'Verts ind', 'Connect 2', 'Mat 2 obj',
                'Mat 2 data', 'Boundbox', 'Spread to ground',
                'Del Orient', 'Separate', 'Bool R',
                'Bool T', 'Bool X',
                'Compliment(rus)', 'Area pols', 'Length edgs',
                'Clifford attractors curves', 'Del node layouts',
                'Русский', 'For men', 'MAIN', 'And active',
                'CURVES', 'Vers', 'Shift',
                'Hook', 'MaxVers', 'MESH', 'TOOLSET NT',
                'TEXT+MESH', 'Separator', 'Coma',
                'Volume', 'ManiFest', 'Good bezier', 
                'Duplicats', 'Scale2Vol', 'Units'
                ]

area_seps = [(';',';',';'),('    ','tab','    '),(',',',',','),(' ','space',' ')]
area_coma = [(',',',',','),('.','.','.')]

bpy.types.Scene.nt_areaseps = EnumProperty(
    items=area_seps,
    name='separator',
    description='materials separator',
    default=';')

bpy.types.Scene.nt_areacoma = EnumProperty(
    items=area_coma,
    name='coma',
    description='materials coma',
    default=',')

bpy.types.Scene.nt_shift_verts = IntProperty(
    name="shift_verts",
    description="shift vertices of smaller object. смещает вершины для соединения",
    min=0, max=1000,
    default = 0,
    options={'ANIMATABLE', 'LIBRARY_EDITABLE'})
    
bpy.types.Scene.NS_vertices_separator = IntProperty(
    name="separate",
    description="how many vertices in one object",
    min=3, max=1000,
    default = 8)
    
bpy.types.Scene.nt_clean_layout_used = BoolProperty(
    name="clean_layout_used",
    description="remove even if layout has one user (not fake user)",
    default = False)

bpy.types.Scene.nt_main_panel = BoolProperty(
    name="show main panel",
    description="",
    default = False)
    
bpy.types.Scene.nt_additional_panel = BoolProperty(
    name="show additional panel",
    description="",
    default = False)
    
bpy.types.Scene.nt_hook_or_not = BoolProperty(
    name="hook_or_not",
    description="зацепить вершины к изначальным объектам.",
    default = True)
    
def nt_make_lang(classes, names):
    dict = {}
    for i, c in enumerate(classes):
        dict[str(c)] = names[i]
    return dict

def get_lang(lang_dict):
    lang = lang_dict
    return lang
        
def nt_lang_panel():
    global handle_lang
    global sv_lang
    if handle_lang:
        sv_lang = get_lang(lang_dict_ru)
        handle_lang = False
    else:
        sv_lang = get_lang(lang_dict_en)
        handle_lang = True

def maxim():
    """this def for connect2objects maximum shift (it cannot update scene's veriable somehow)"""
    if len(bpy.context.selected_objects) >= 2:   
        if bpy.context.selected_objects[0].type == 'MESH':
            len1 = len(bpy.context.selected_objects[0].data.vertices)
            len2 = len(bpy.context.selected_objects[1].data.vertices)
            maxim = min(len1, len2)
            return maxim

def NTmaketext(name):
    texts = bpy.data.texts.items()
    exists = False
    for t in texts:
        if bpy.data.texts[t[0]].name == name:
            exists = True
            break
    if not exists:
        bpy.data.texts.new(name)

lang_dict_ru = nt_make_lang(my_str_classes, ru_dict)
lang_dict_en = nt_make_lang(my_str_classes, en_dict)
vert_max = 0
nt_lang_panel()





class NTScaleFit(bpy.types.Operator):
    """Масштабирует в указаный объём"""
    bl_idname = "object.nt_scalefit"
    bl_label = 'МАСШТвОБЪ'
    bl_options = {'REGISTER', 'UNDO'}

    Объём = bpy.props.FloatProperty(name='Объём', default=1.0)
    volums = [('m3','m3','m3'),('l','l','l'),('sm3','sm3','sm3')]
    scaleunit = EnumProperty(
        items=volums,
        name="scale2vol_units",
        description="Масштабирует в указанный объём. Scale to defined volume.",
        default = 'm3')

    def execute(self, context):
        objs = bpy.context.selected_objects
        
        volinit = 0
        if self.scaleunit == 'l':
            volend = self.Объём/1000
        elif self.scaleunit == 'sm3':
            volend = self.Объём/1000000
        elif self.scaleunit == 'm3':
            volend = self.Объём


        for o in objs:
            bo = bmesh.new()
            bo.from_mesh(o.data)
            vo = bo.calc_volume()
            su = 1
            for s in o.scale[:]:
                su *= s
            vol = su*vo
            volinit += vol
        coef = volend / volinit
        coep = math.pow(coef,1/3)
        for o in objs:
            o.scale *= coep
        return {'FINISHED'}




class NTduplicat(bpy.types.Operator):
    """дубликатирует"""
    bl_idname = "object.nt_duplicat"
    bl_label = 'ДУБЛИКАТИТ'
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = bpy.context.selected_objects

        o = bpy.context.active_object
        locata = o.matrix_local.copy()
        data = o.data
        name = o.name
        for o in obj:
            if o.name != name:
                ob = bpy.data.objects.new(name+'_duplicatio', data)
                ob.matrix_local = locata
                bpy.context.scene.objects.link(ob)
                ob.parent = o
        return {'FINISHED'}


class NTbezierOrdering(bpy.types.Operator):
    """Делает прямые безье прямыми для перевода в сетку"""
    bl_idname = "object.nt_bezier_making_good"
    bl_label = 'ДЕЛАТЬ_БЕЗЬЕ_ХОРОШО'
    bl_options = {'REGISTER', 'UNDO'}
    
    допуск = bpy.props.FloatProperty(name='допуск', default=0.001)
    
    def bezier_make_good(self, curve):
        for spline in curve.splines:
            spline.type == 'BEZIER'
            for i in range(len(spline.bezier_points)):
                if i != 0:
                    poileft = spline.bezier_points[i-1]
                    poiright = spline.bezier_points[i]
                    if poileft.handle_right_type != 'VECTOR' and poiright.handle_left_type != 'VECTOR':
                        pl,pr,hl,hr = poileft.co, poiright.co, poileft.handle_right, poiright.handle_left
                        n1 = (pl-pr)
                        n1.normalize()
                        n2 = (pl-hl)
                        n2.normalize()
                        n3 = (pl-hr)
                        n3.normalize()
                        #ugly solution
                        if (n1-n2).length <= self.допуск:
                            poileft.handle_right_type = 'VECTOR'
                        if (n1-n3).length <= self.допуск:
                            poiright.handle_left_type = 'VECTOR'
    
    def execute(self, context):
        obj = bpy.context.selected_objects
        for o in obj:
            curve = o.data
            self.bezier_make_good(curve)
        return {'FINISHED'}



class NTTextMeshWeld(bpy.types.Operator):
    """Соединение текстов и сеток если матрицы совпадают"""
    bl_idname = "object.nt_text_mesh_weld"
    bl_label = 'ТЕКСТ_И_СЕТКА_ДРУЗЬЯ'
    bl_options = {'REGISTER', 'UNDO'}
    
    length = bpy.props.StringProperty(name='длина', default='')
    
    def execute(self, context):
        objs = bpy.context.selected_objects
        bpy.ops.object.select_all(action='TOGGLE')
        for i in objs:
            if i.type == 'FONT':
                i.select = True
                bpy.context.scene.objects.active = bpy.data.objects[i.name]
                bpy.ops.object.convert(target='MESH')
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.remove_doubles(threshold=0.005)
                bpy.ops.object.editmode_toggle()
                for o in objs:
                    if i != o and o.matrix_world.translation == i.matrix_world.translation:
                        # objmesh = bpy.data.objects['Sv_'+re.match(r'(\d+)', i.name)[0]]
                        o.select = True
                        bpy.ops.object.join()
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.remove_doubles(threshold=0.0005)
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.select_all(action='TOGGLE')
        return {'FINISHED'}


class NTcsvCalc(bpy.types.Operator):
        
    def calcareasum(self):
        pols = bpy.context.active_object.data.polygons
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        summa = sum([ p.area for p in pols if p.select ])
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        return str(round(summa, 4))

    def take_digit(self, coma, digit, roro):
        if coma == ',':
            return str(round(digit,roro)).replace('.',',')
        else:
            return str(round(digit,roro))

    def do_area(self, area, materials):
        roro = 4
        sep = bpy.context.scene.nt_areaseps
        if sep == '    ':
            tab = ''
        else:
            tab = '    '
        coma = bpy.context.scene.nt_areacoma
        NTmaketext('Materials.csv')


        for_file = 'Объект'+ sep + 'Материал' + sep + 'Площадь м2'+sep + 'Примечание\n\n'
        for_file += 'По материалам:'+sep + sep + '\n'
        a = self.take_digit(coma, materials.pop('Total'), roro)
        for_file += 'Всего:' + sep + sep + a + sep + 'Материалов' + '\n'*2
        for mat, val in materials.items():
            a = self.take_digit(coma, val, roro)
            for_file += sep + mat + sep + a + sep + '\n'
        for_file += '\n\n'
        for_file += 'По объектам:'+sep + sep + sep + '\n'
        a = self.take_digit(coma, area.pop('Total'), roro)
        for_file += 'Всего:' + sep + sep + a + sep + 'Из выделения' + '\n'*2
        sorted_a = sorted(area.items(), key=operator.itemgetter(0))
        for ob, mats in sorted_a:
            a = self.take_digit(coma, area[ob].pop('Total'), roro)
            if len(mats):
                for_file += ob + sep + sep + a + sep + '\n'
                for ma, ar in mats.items():
                    a = self.take_digit(coma, ar, roro)
                    for_file += ob + sep + ma + sep + tab + a + sep + '\n'
            else:
                for_file += ob + sep + sep + a + sep + 'Нет материалов' + '\n'

        bpy.data.texts['Materials.csv'].clear()
        bpy.data.texts['Materials.csv'].write(for_file)

    def do_volume(self, volumes, volume):
        'volumes = object name = mesh name + volume; volume = total volume'
        roro = 4
        sep = bpy.context.scene.nt_areaseps
        if sep == '    ':
            tab = ''
        else:
            tab = '    '
        coma = bpy.context.scene.nt_areacoma
        NTmaketext('Volumes.csv')


        for_file = 'Объект' + sep + 'Сетка' + sep + 'Объём м3' + sep + 'Примечание' + '\n'*2
        a = self.take_digit(coma, volume, roro)
        for_file += 'Всего:' + sep + sep + a + sep + 'Из выделения' + '\n'*2
        sorted_v = sorted(volumes.items())
        for nam, val in sorted_v:
            a = self.take_digit(coma, val[1], roro)
            for_file += nam + sep + val[0] + sep + a + sep + '\n'
        for_file += '\n\n'

        bpy.data.texts['Volumes.csv'].clear()
        bpy.data.texts['Volumes.csv'].write(for_file)

    def calc_materials(self):
        if bpy.context.mode == 'OBJECT':
            obj = bpy.context.selected_objects
            objects = [[o.name, o] for o in obj]
            objects.sort()
            area = {}
            materials = {}
            area['Total'] = 0.0
            materials['Total'] = 0.0
            for name, o in objects:
                if o.type == 'MESH':
                    area[name] = {}
                    area[name]['Total'] = 0.0
                    if len(o.material_slots):
                        for m in o.material_slots:
                            area[name][m.name] = 0.0
                            if not m.name in materials:
                                materials[m.name] = 0.0
                        for p in o.data.polygons:
                            parea = p.area
                            i = p.material_index
                            area[name][o.material_slots[i].name] += parea
                            area[name]['Total'] += parea
                            area['Total'] += parea
                            materials[o.material_slots[i].name] += parea
                            materials['Total'] += parea
                    else:
                        for p in o.data.polygons:
                            parea = p.area
                            area[name]['Total'] += parea
                            area['Total'] += parea
        return area, materials


class NTVolumeCalculate(NTcsvCalc):
    """Подсчёт объёма выбранной сетки"""
    bl_idname = "object.nt_calc_volume"
    bl_label = 'Объём считает'
    bl_options = {'REGISTER', 'UNDO'}
    
    volume = bpy.props.StringProperty(name='объём', default='')

    def execute(self, context):
        self.volume = str(self.calcVolume()[0])
        return {'FINISHED'}
    
    def calcVolume(self):
        objs = bpy.context.selected_objects
        volumes = {}
        volume = 0
        for o in objs:
            on = o.name
            od = o.data
            dn = od.name
            if o.type == 'MESH':
                bo = bmesh.new()
                bo.from_mesh(od)
                vo = bo.calc_volume()
                su = 1
                for s in o.scale[:]:
                    su *= s
                vol = su*vo
                volumes[on] = [dn,vol]
                volume += vol
        bpy.data.objects[on].select = True
        self.do_volume(volumes,volume)
        return volume, volumes
    
class EdgeLength(NTcsvCalc):
    """Длина рёбер объектов"""
    bl_idname = "object.nt_edgelength"
    bl_label = 'ДЛИН_РЁБ'
    bl_options = {'REGISTER', 'UNDO'}
    
    length = bpy.props.StringProperty(name='длина', default='')
    
    def execute(self, context):
        self.length = str(self.calclength())
        return {'FINISHED'}

    def calclength(self):
        if bpy.context.mode == 'OBJECT':
            obj = bpy.context.selected_objects
            allthelength = []
            for o in obj:
                v = o.data.vertices
                for e in o.data.edges:
                    ev = e.vertices
                    diff = v[ev[0]].co-v[ev[1]].co
                    edglength = diff.length
                    allthelength.append(edglength)
            summa = sum(allthelength)
        elif bpy.context.mode == 'EDIT_MESH':
            data = bpy.context.active_object.data
            edgs, vers = data.edges, data.vertices
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            edgs_sel = [ tuple(e.vertices[:]) for e in edgs if e.select ]
            summa = sum([ (vers[e[0]].co-vers[e[1]].co).length for e in edgs_sel ])
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        return round(summa, 4)

class AreaOfLenin(NTcsvCalc):
    """площадь объектов"""
    bl_idname = "object.nt_areaoflenin"
    bl_label = "ПЛОЩ_ОБ"
    bl_options = {'REGISTER', 'UNDO'}
    
    area = bpy.props.StringProperty(name='площадь', default='')

    def execute(self, context):
        #try:
        if bpy.context.selected_objects:
            if bpy.context.mode == 'OBJECT':
                area, materials = self.calc_materials()
                self.area = str(round(area['Total'],4))
                self.do_area(area, materials)
            elif bpy.context.mode == 'EDIT_MESH':
                self.area = self.calcareasum()
        #except:
        #    self.report({'ERROR'}, 'Проверьте материалы и объекты')
        return {'FINISHED'}

class CliffordAttractors(bpy.types.Operator):
    """ клиффорда точки притяжения в кривые """
    bl_idname = "object.nt_cliffordattractors"
    bl_label = "СУПЕР_КРИВЫЕ"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Code adapted by Eduardo Maldonado (Elbrujodelatribu)
    # Most of them from addon add_curve_extra_objects
    #      -> add_curve_spirals.py (see it in your Blender release)
    # Info about the attractor in http://paulbourke.net/fractals/clifford/
    
    # STARTING LOCATION
    position_x = bpy.props.FloatProperty(name='позиция_x', default=0.1)
    position_y = bpy.props.FloatProperty(name='позиция_y', default=0.0)
    position_z = bpy.props.FloatProperty(name='позиция_z', default=0.0)
    
    # SEED / CONSTANTS
    x_1 = bpy.props.FloatProperty(name='x_волна', default=-1.4, description='размер волны')
    x_2 = bpy.props.FloatProperty(name='x_габарит', default=1.0, description='ширина')
    y_1 = bpy.props.FloatProperty(name='y_волна', default=1.6, description='размер волны')
    y_2 = bpy.props.FloatProperty(name='y_габарит', default=0.7, description='глубина')
    z_1 = bpy.props.FloatProperty(name='z_волна', default=0.2, description='размер волны')
    z_2 = bpy.props.FloatProperty(name='z_габарит', default=0.5, description='высота')
    
    iterations = bpy.props.IntProperty(name='iterations', default=500, min=200, max=4000)
    
    #ADD VERTICES TO A SPLINE
    def makeBezier(self, spline, vertList):
        numPoints = (len(vertList) / 3) - 1
        spline.bezier_points.add(numPoints)
        spline.bezier_points.foreach_set("co", vertList)
        for point in spline.bezier_points:
            point.handle_left_type = "AUTO"
            point.handle_right_type = "AUTO"
    
    def execute(self, context):
        # VERTEX LIST FOR THE ATTRACTOR
        vertList = []
        px = self.position_x
        py = self.position_y
        pz = self.position_z

        # SEED / CONSTANTS
        a = self.x_1
        b = self.y_1
        c = self.x_2
        d = self.y_2
        e = self.z_1
        f = self.z_2

        # INIT itr VARIABLE
        itr = 0

        #CREATE AND ADD VERTICES
        while itr < self.iterations:
            #CLIFFORD ATTRACTOR ALGORITHM MODIFIED FOR 3D
            newpx = math.sin(a*py) + c*math.cos(a*px)
            newpy = math.sin(b*px) + d*math.cos(b*py)
            newpz = math.sin(e*px) + f*math.cos(e*pz)
            
            #SAVE CURRENT POINT FOR NEXT ITERATION
            px = newpx
            py = newpy
            pz = newpz

            #SKIP FIRST 100 ITERATIONS AND ADD VERTICES
            if (itr > 100):
                vertList.append( newpx )
                vertList.append( newpy )
                vertList.append( newpz )
            itr += 1

        # BUILD THE ATTRACTOR - A BEZIER CURVE
        crv = bpy.data.curves.new("Attractor", type = "CURVE")
        crv.dimensions = '3D'
        crv.splines.new(type = 'BEZIER')
        spline = crv.splines[0]
        self.makeBezier(spline, vertList)
        
        # CREATE OBJECT
        new_obj = object_data_add(bpy.context, crv)
        return {'FINISHED'}

class NTManifestGenerator(bpy.types.Operator):
    """Генератор манифестов"""
    bl_idname = "object.nt_manifest_generator"
    bl_label = "манифест"
    bl_options = {'REGISTER', 'UNDO'}
    
    manifest = bpy.props.StringProperty(name='манифест', default='')
    
    def execute(self, context):
        #a = context.window_manager
        #a.progress_begin(0,1)
        self.main()
        #a.progress_update(0.5)
        #a.progress_end()
        return {'FINISHED'}
    
    def w(self, a):
        return random.choice(a)
    
    def main(self):
        a1 = ['Дорогие ',]
        a2 = ['друзья! ', 'соратники! ', 'братья! ', 'сёстры! ', 'ляшки! ']
        a3 = ['Мы собрались здесь сегодня чтобы сказать наше решительное ']
        a4 = ['да','нет','геть','вали в Москву','дайте денег']
        a5 = [' продажной власти ']
        a6 = ['Кучмы','Ющенко','Порошенко','Яйценюха','Этого']
        a7 = ['. Мы все, как один, требуем немедленно ']
        a8 = ['вернуть Крым','посадить Тимошенко','освободить Тимошенко','войти в Европу','ещё пива']
        a9 = ['. Предупреждаем! Если власти не пойдут навстречу нашим ']
        a10 = ['справедливым','наглым','невнятным','идиотским','кличкоподобным']
        a11 = [' требованиям, то мы незамедлительно начнём ']
        a12 = ['жечь покрышки!!! ','есть печеньки!!! ','скакать как немоскали!!! ','воровать газ!!! ']
        a13 = [' Москаляку на гиляку!!! ','Судью на мыло!!!  ','Деньги на бочку!!! ','Зубы на полку!!! ']
        a14 = ['Да здравствует небесная ']
        a15 = ['сотня','тысяча','армия Украины']
        a16 = ['. Слава Украини! Героям ']
        a17 = ['сала.','утку.','по лбу.','памятник.','уже всё равно.']
        manifest = (str(self.w(a1))+str(self.w(a2))+ str(self.w(a3))+ \
                        str(self.w(a4))+ str(self.w(a5))+ str(self.w(a6))
                        + str(self.w(a7))+ str(self.w(a8))+ str(self.w(a9)) 
                        + str(self.w(a10)) + str(self.w(a11)) + str(self.w(a12)) 
                        + str(self.w(a13)) + str(self.w(a14)) + str(self.w(a15)) 
                        + str(self.w(a16)) + str(self.w(a17))
                        )
        self.report({'INFO'}, 'Смотри в текстовом окне и терминале.')
        self.manifest = manifest
        NTmaketext(self.bl_label)
        bpy.data.texts[self.bl_label].clear()
        bpy.data.texts[self.bl_label].write(manifest)
        print(manifest)
        return

class ComplimentWoman(bpy.types.Operator):
    """Делайте дамам приятно"""
    bl_idname = "object.nt_compliment_wom"
    bl_label = "комплимент"
    bl_options = {'REGISTER', 'UNDO'}
    
    compliment = bpy.props.StringProperty(name='compliment', default='')
    
    def execute(self, context):
        #a = context.window_manager
        #a.progress_begin(0,1)
        self.report({'INFO'}, self.main())
        #a.progress_update(0.5)
        #a.progress_end()
        return {'FINISHED'}
    
    def w(self, a):
        return random.choice(a)
    
    def main(self):
        a1 = ['Ты',]
        a2 = ['так', 'офигенски', 'просто', 'невероятно', 'супер', 'безумно', 'нереально','всё равно']
        a3 = ['круто','потрясно','вкусно','улётно','клёво','прелестно','замечательно']
        a4 = ['выглядишь','пахнешь','целуешься','печёшь пирожки','двигаешься','танцуешь','готовишь','поёшь','смеёшься','работаешь']
        a5 = ['пупсик','дорогая','милая','солнце','зайка','как всегда','моя королева','бегемотик','горошинка','луковичка','малинка']
        compliment = (str(self.w(a1))+' '+ str(self.w(a2))+ ' '+ str(self.w(a3))+ \
                        ' '+ str(self.w(a4)) + ','+ ' '+ str(self.w(a5)) + '!'
                        )
        self.compliment = compliment
        return compliment
    
    #def invoke(self, context, event):
        #wm = context.window_manager
        #return wm.invoke_props_dialog(self)
    
class CurvesTo3D (bpy.types.Operator):
    """превращает кривые в 3М кривые скопом"""
    bl_idname = "object.nt_curv_to_3d"
    bl_label = "КРИВ_3М"
    bl_options = {'REGISTER', 'UNDO'} 
    
    thikns = bpy.props.FloatProperty(name='толщина', default=0.0)
    resolution = bpy.props.IntProperty(name='разрешение', default=12)
    smooth = bpy.props.BoolProperty(name='сгладить', default=True)
    bezier = bpy.props.BoolProperty(name='безье', default=False)
    variants_ = ['AUTOMATIC', 'VECTOR', 'ALIGNED', 'FREE_ALIGN', 'TOGGLE_FREE_ALIGN']
    variants = [tuple(3*[x]) for x in variants_]
    handle = bpy.props.EnumProperty(items=variants, name='тип рычажков', default='VECTOR')
    bevel = bpy.props.FloatProperty(name='закругление', default=0.0)
    bev_resolution = bpy.props.IntProperty(name='разрешение', default=0)
    
    def execute(self, context):
        obj = bpy.context.selected_objects
        if obj[0].type == 'CURVE':
            bpy.ops.object.select_all(action='DESELECT')
            for o in obj:
                o.data.extrude = self.thikns
                o.data.dimensions = '3D'
                #o.matrix_world.translation[2] = 0
                nam = o.data.name
                # Я фанат группы "Сплин", ребята.
                for splin in bpy.data.curves[nam].splines:
                    splin.use_smooth = self.smooth
                o.data.resolution_u = self.resolution
                o.data.bevel_depth = self.bevel
                o.data.bevel_resolution = self.bev_resolution
                if self.bezier:
                    bpy.data.objects[nam].select = True
                    bpy.context.scene.objects.active = bpy.data.objects[nam]
                    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                    bpy.ops.curve.select_all(action='SELECT')
                    bpy.ops.curve.spline_type_set(type='BEZIER', use_handles=False)
                    bpy.ops.curve.handle_type_set(type=self.handle)
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_props_dialog(self, 250)
        return {'RUNNING_MODAL'}
    
class CurvesTo2D (bpy.types.Operator):
    """Превращает кривые в 2М кривые скопом (толщина по умолчанию 0.03)"""
    bl_idname = "object.nt_curv_to_2d"
    bl_label = "КРИВ_2М"
    bl_options = {'REGISTER', 'UNDO'} 
    
    thikns = bpy.props.FloatProperty(name='толщина', default=0.0016)
    resolution = bpy.props.IntProperty(name='разрешение', default=12)
    smooth = bpy.props.BoolProperty(name='сгладить', default=False)
    bezier = bpy.props.BoolProperty(name='безье', default=False)
    variants_ = ['AUTOMATIC', 'VECTOR', 'ALIGNED', 'FREE_ALIGN', 'TOGGLE_FREE_ALIGN']
    variants = [tuple(3*[x]) for x in variants_]
    handle = bpy.props.EnumProperty(items=variants, name='тип рычажков', default='VECTOR')
    bevel = bpy.props.FloatProperty(name='закругление', default=0.0)
    bev_resolution = bpy.props.IntProperty(name='разрешение', default=0)
    
    def execute(self, context):
        obj = bpy.context.selected_objects
        if obj[0].type == 'CURVE':
            bpy.ops.object.select_all(action='DESELECT')
            for o in obj:
                o.data.extrude = self.thikns
                o.data.dimensions = '2D'
                nam = o.data.name
                # Я фанат группы "Сплин", ребята.
                for splin in bpy.data.curves[nam].splines:
                    splin.use_smooth = self.smooth
                    for point in splin.bezier_points:
                        point.radius = 1.0
                o.data.resolution_u = self.resolution
                o.data.bevel_depth = self.bevel
                o.data.bevel_resolution = self.bev_resolution

                if self.bezier:
                    bpy.data.objects[nam].select = True
                    bpy.context.scene.objects.active = bpy.data.objects[nam]
                    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                    bpy.ops.curve.select_all(action='SELECT')
                    bpy.ops.curve.spline_type_set(type='BEZIER', use_handles=False)
                    bpy.ops.curve.handle_type_set(type=self.handle)
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_props_dialog(self, 250)
        return {'RUNNING_MODAL'}
    
 #breakpoint
class ObjectNames (bpy.types.Operator):
    """Имена объектов в 3М текст"""      
    bl_idname = "object.nt_name_objects" 
    bl_label = "ИМЕНА_ОБ"        
    bl_options = {'REGISTER', 'UNDO'} 
    
    size = bpy.props.FloatProperty(name='размер', default=1.0)
    
    def execute(self, context):
        obj = bpy.context.selected_objects
        
        for ob in obj:
            mw = ob.matrix_world
            name_all = re.match(r'(\w+)', ob.name)
            name = name_all.group(1)
            len = 1#abs(max(ob.dimensions) * (sum(mw.to_scale()) / 3))
            #print ()
            self.run(mw,name,len)
        return {'FINISHED'}

    def run(self, origin,text,length):
       # Create and name TextCurve object
        bpy.ops.object.text_add(view_align=False,
        enter_editmode=False,location=origin.translation[:], 
        rotation=origin.to_euler()[:])
        ob = bpy.context.object
        ob.name = 'lable_'+str(text)
        tcu = ob.data
        tcu.name = 'lable_'+str(text)
        # TextCurve attributes
        tcu.body = str(text)
        tcu.font = bpy.data.fonts[0]
        tcu.offset_x = 0
        tcu.offset_y = -0.25
        tcu.resolution_u = 2
        tcu.shear = 0
        Tsize = self.size #* length
        tcu.size = Tsize
        tcu.space_character = 1
        tcu.space_word = 1
        tcu.align = 'CENTER'
        # Inherited Curve attributes
        tcu.extrude = 0.0
        tcu.fill_mode = 'NONE'
        
        
class VerticesNumbers3D (bpy.types.Operator):
    """Номера вершин в 3М текст"""      
    bl_idname = "object.nt_vertices_numbers3d"
    bl_label = "НОМ_ВЕР"
    bl_options = {'REGISTER', 'UNDO'}
    
    size = bpy.props.FloatProperty(name='размер', default=0.1)
    
    def execute(self, context):
        obj = bpy.context.selected_objects[0]
        mw = obj.matrix_world
        mesh = obj.data
        size1 = 1#abs(max(obj.dimensions) * (sum(mw.to_scale()) / 3))
        if obj.type == 'MESH':
            mesh.update()
            ver = mesh.vertices
        else:
            ver = mesh.splines[0].bezier_points
        i = 0
        for id in ver:
            coor = mw * ver[i].co
            self.run(coor, i, size1)
            i += 1
        return {'FINISHED'}
    
    def run(self, origin, text, size1):
        # Create and name TextCurve object
        bpy.ops.object.text_add(
        location=origin,
        rotation=(radians(90),radians(0),radians(0)))
        ob = bpy.context.object
        ob.name = 'vert '+ str(text)
        tcu = ob.data
        tcu.name = 'vert '+ str(text)
        # TextCurve attributes
        tcu.body = str(text)
        tcu.font = bpy.data.fonts[0]
        tcu.offset_x = 0
        tcu.offset_y = 0
        tcu.shear = 0
        tcu.size = self.size # * size1 
        tcu.space_character = 1
        tcu.space_word = 1
        # Inherited Curve attributes
        tcu.extrude = 0
        tcu.fill_mode = 'BOTH'



class Connect2Meshes (bpy.types.Operator):
    """Соединить два объекта"""      
    bl_idname = "object.nt_connect2objects"
    bl_label = "СОЕДИНИТЬ_2_ОБ"
    bl_options = {'REGISTER', 'UNDO'}
    
    nt_shift_verts = bpy.props.IntProperty(name="смещение вершин", description="shift vertices of smaller object, it can reach     maximum (look right), to make patterns", default=0, min=0, max=1000)
    
    def dis(self, x,y):
        vec = mathutils.Vector((x[0]-y[0], x[1]-y[1], x[2]-y[2]))
        return vec.length
    
    def maxObj(self, ver1, ver2, mw1, mw2):
        if len(ver1) > len(ver2):
            inverc = 0
            vert1 = ver1
            mworld1 = mw1
            vert2 = ver2
            mworld2 = mw2
        else:
            inverc = 1
            vert1 = ver2
            mworld1 = mw2
            vert2 = ver1
            mworld2 = mw1
        cache_max = [vert1, mworld1]
        cache_min = [vert2, mworld2]
        return cache_max, cache_min, inverc
    
    def points(self, ver1, ver2, mw1, mw2, shift):
        vert_new = []
        # choosing maximum vertex count in ver1/2, esteblish vert2 - mincount of vertex
        cache = self.maxObj(ver1, ver2, mw1, mw2)
        vert1 = cache[0][0]
        vert2 = cache[1][0]
        mworld1 = cache[0][1]
        mworld2 = cache[1][1]
        inverc = cache[2]
        # append new verts in new obj
        for v in vert2:
            v2 = mworld2 * v.co
            if len(vert2) > v.index + shift:
                v1 = mworld1 * vert1[v.index + shift].co
            else:
                v1 = mworld1 * vert1[v.index + shift - len(vert2)].co
            if inverc == True:
                m1 = mworld2.translation
                m2 = mworld2.translation
            else:
                m1 = mworld1.translation
                m2 = mworld1.translation
            vert_new.append(v2 - m2)
            vert_new.append(v1 - m1)
        return vert_new
    
    def edges(self, vert_new):
        edges_new = []
        i = -2
        for v in vert_new:
            # dis(vert_new[i],vert_new[i+1]) < 10 and 
            if i > -1 and i < (len(vert_new)):
                edges_new.append((i,i + 1))
            i += 2
        return edges_new
    
    def mk_me(self, name):
        me = bpy.data.meshes.new(name+'Mesh')
        return me
    
    def mk_ob(self, mesh, name, mw):
        loc = mw.translation.to_tuple()
        ob = bpy.data.objects.new(name, mesh)
        ob.location = loc
        ob.show_name = True
        bpy.context.scene.objects.link(ob)
        return ob
    
    def def_me(self, mesh, ver1, ver2, mw1, mw2, obj1, obj2, nam):
        ver = self.points(ver1, ver2, mw1, mw2, bpy.context.scene.nt_shift_verts)
        edg = self.edges(ver)
        mesh.from_pydata(ver, edg, [])
        mesh.update(calc_edges=True)
        if bpy.context.scene.nt_hook_or_not:
            self.hook_verts(ver, obj1, obj2, nam, ver1, ver2, mw1, mw2)
        return
    
    # preparations for hooking
    def hook_verts(self, ver, obj1, obj2, nam, ver1, ver2, mw1, mw2):
        # pull cache from maxObj
        cache = self.maxObj(ver1, ver2, mw1, mw2)
        vert1 = cache[0][0]
        vert2 = cache[1][0]
        mworld1 = cache[0][1]
        mworld2 = cache[1][1]
        inverc = cache[2]
        points_ev = []
        points_od = []
        # devide even/odd verts
        for v in ver:
            if (ver.index(v) % 2) == 0:
                points_ev.append(ver.index(v))
                # print ('чёт ' + str(ver.index(v)))
            else:
                points_od.append(ver.index(v))
                # print ('нечет ' + str(ver.index(v)))
        if bpy.context.selected_objects:
            bpy.ops.object.select_all(action='TOGGLE')
        # depend on bigger (more verts) object it hooks even or odd verts
        if inverc == False:
            # ob1 = obj1 ob2 = obj2, 1 - bigger
            self.hooking_action(obj2, nam, points_ev, ver)
            self.hooking_action(obj1, nam, points_od, ver)
        else:
            # ob1 = obj2 ob2 = obj1, 2 - bigger
            self.hooking_action(obj2, nam, points_od, ver)
            self.hooking_action(obj1, nam, points_ev, ver)
        
    # free hooks :-)
    def hooking_action(self, ob, nam, points, verts_of_object):
        # select 1st obj, second connection
        bpy.data.scenes[bpy.context.scene.name].objects[ob.name].select = True
        bpy.data.scenes[bpy.context.scene.name].objects[nam].select = True
        bpy.data.scenes[bpy.context.scene.name].objects.active = bpy.data.objects[nam]
        # deselect vertices
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='TOGGLE')
        bpy.ops.object.editmode_toggle()
        # select nearby vertices
        for vert in points:
            bpy.context.object.data.vertices[vert].select = True
        # hook itself
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.hook_add_selob(use_bone=False)
        #bpy.ops.mesh.select_all(action='TOGGLE')
        bpy.ops.object.editmode_toggle()
        # deselect all
        bpy.ops.object.select_all(action='TOGGLE')

    def maxim(self):
        if bpy.context.selected_objects[0].type == 'MESH':
            if len(bpy.context.selected_objects) >= 2:     
                len1 = len(bpy.context.selected_objects[0].data.vertices)
                len2 = len(bpy.context.selected_objects[1].data.vertices)
                maxim = min(len1, len2)
                #print (maxim)
        return maxim
    
    def execute(self, context):
        
        bpy.types.Scene.nt_shift_verts = self.nt_shift_verts
        context.scene.update()
        obj1 = context.selected_objects[0]
        obj2 = context.selected_objects[1]
        mw1 = obj1.matrix_world
        mw2 = obj2.matrix_world
        mesh1 = obj1.data
        mesh1.update()
        mesh2 = obj2.data
        mesh2.update()
        ver1 = mesh1.vertices
        ver2 = mesh2.vertices
        nam = 'linked_' + str(obj1.name) + str(obj2.name)
        me = self.mk_me(nam)
        ob = self.mk_ob(me, nam, mw1)
        self.def_me(me, ver1, ver2, mw1, mw2, obj1, obj2, nam)
        print ('---- NIKITRON_connect2objects MADE CONNECTION BETWEEN: ' + str(obj1.name) + ' AND ' + str(obj2.name) + ' AND GOT ' + str(ob.name) + ' ----')
        return {'FINISHED'}


class MaterialToObjectAll (bpy.types.Operator):
    """Материалы в объект"""      
    bl_idname = "object.nt_materials_to_object"
    bl_label = "МАТ_ОБ"
    bl_options = {'REGISTER', 'UNDO'} 
    
    def execute(self, context):
        obj = bpy.context.selected_objects
        mode = 'OBJECT'
        for o in obj:
            materials = bpy.data.objects[o.name].material_slots
            for m in materials:
                m.link = mode
                print('материал "'+str(m.name)+'", объект "'+o.name+'", режим материала: '+mode)
        return {'FINISHED'}
    
class MaterialToDataAll (bpy.types.Operator):
    """Материалы в данные"""      
    bl_idname = "object.nt_materials_to_data"
    bl_label = "МАТ_ДАТ"
    bl_options = {'REGISTER', 'UNDO'} 
    
    def execute(self, context):
        obj = bpy.context.selected_objects
        mode = 'DATA'
        for o in obj:
            materials = bpy.data.objects[o.name].material_slots
            for m in materials:
                m.link = mode
                print('материал "'+str(m.name)+'", объект "'+o.name+'", режим материала: '+mode)
        return {'FINISHED'}


class NT_ClearNodesLayouts (bpy.types.Operator):
    """Очистить раскладки узлов (Сверчок, Блендграф) работает когда рядом нет редактора узлов \
    Clear node layouts, when no nodes editor opened"""      
    bl_idname = "object.nt_delete_nodelayouts"
    bl_label = "УД_РАСКЛ"
    bl_options = {'REGISTER', 'UNDO'} 
    
    
    @classmethod
    def poll(cls, self):
        for area in bpy.context.window.screen.areas:
            if area.type == 'NODE_EDITOR':
                return False
        return True
    
    do_clear = bpy.props.BoolProperty(default=False, name='even used', description='remove even if layout has one user (not fake user)')
    
    def execute(self, context):
        self.do_clear = context.scene.nt_clean_layout_used
        trees = bpy.data.node_groups
        for T in trees:
            if T.bl_rna.name in ['Shader Node Tree']:
                continue
            if trees[T.name].users > 1 and T.use_fake_user == True:
                print ('Layout '+str(T.name)+' protected by fake user.')
            if trees[T.name].users == 1 and self.do_clear and T.use_fake_user == False:
                print ('cleaning user: '+str(T.name))
                trees[T.name].user_clear()
            if trees[T.name].users == 0:
                print ('removing layout: '+str(T.name)+' | '+str(T.bl_rna.name))
                bpy.data.node_groups.remove(T)
                
        return {'FINISHED'}


class DeleteOrientation (bpy.types.Operator):
    """Удалить ориентации (alt+space) \
    delete orientations"""      
    bl_idname = "object.nt_delete_orientation"
    bl_label = "УД_ОРИЕНТ"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D'
        
    def execute(self, context):
        orients = bpy.data.scenes[bpy.context.scene.name].orientations
        for o in orients:
            if o.name != 'Global' or o.name != 'Local' or o.name != 'Normal' or o.name != 'Gimbal' or o.name != 'View':
                bpy.ops.transform.select_orientation(orientation=o.name)
                try:
                    bpy.ops.transform.delete_orientation()
                    print (str(o.name)+' orientation deleted')
                except:
                    print ('cannot delete orientation' + str(o.name))
        return {'FINISHED'}

class BooleratorRandom (bpy.types.Operator):
    """Булен объединение nt_hook_or_not, Случайном порядке если нет - Обычном порядке поимённо"""      
    bl_idname = "object.nt_boolerator_random"
    bl_label = "Bool_СЛ"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        objects = bpy.context.selected_objects
        if bpy.context.scene.nt_hook_or_not:
            random.shuffle(objects)
        lenth = len(objects) - 1
        while lenth:
            bpy.ops.object.select_all(action='DESELECT')
            obj2 = objects[lenth]
            obj1 = objects[lenth - 1]
            name1 = obj1.name
            name2 = obj2.name
            bpy.data.objects[name2].select = True
            bpy.data.objects[name1].select = True
            bpy.context.scene.objects.active = bpy.data.objects[name1]
            md = obj1.modifiers.new('booleanunion', 'BOOLEAN')
            md.operation = 'UNION'
            md.object = obj2
            # apply the modifier
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="booleanunion")
            lenth -= 1
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[name2].select = True
            bpy.ops.object.delete()
            bpy.data.objects[name1].select = True
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        return {'FINISHED'}


class BooleratorIntersection (bpy.types.Operator):
    """ Булен единство Пересечения"""      
    bl_idname = "object.nt_boolerator_intersection"
    bl_label = "Bool_ПЕР"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        objects = bpy.context.selected_objects
        lenth = len(objects) - 1
        while lenth:
            bpy.ops.object.select_all(action='DESELECT')
            obj2 = objects[lenth]
            obj1 = objects[lenth - 1]
            self.check_bool(objects, lenth, obj1, obj2)
            lenth -= 1
        return {'FINISHED'}
    def interinsects(self, ob1, ob0):
        name1 = ob1.name
        name0 = ob0.name
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[name1].select = True
        bpy.data.objects[name0].select = True
        bpy.context.scene.objects.active = bpy.data.objects[name1]
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        bpy.ops.object.join()
        obj = bpy.context.selected_objects[0]
        faces_intersect = self.bmesh_check_self_intersect_object(obj)
        bpy.ops.object.delete()
        if faces_intersect:
            bpy.data.objects[name1].select = True
            bpy.data.objects[name0].select = True
            return True
        else:
            return False
    
    def bmesh_check_self_intersect_object(self, obj):
        """
        Check if any faces self intersect
    
        returns an array of edge index values.
        """
        # Heres what we do!
        #
        # * Take original Mesh.
        # * Copy it and triangulate it (keeping list of original edge index values)
        # * Move the BMesh into a temp Mesh.
        # * Make a temp Object in the scene and assign the temp Mesh.
        # * For every original edge - ray-cast on the object to find which intersect.
        # * Report all edge intersections.
        # Triangulate
        bm = self.bmesh_copy_from_object(obj, transform=False, triangulate=False)
        face_map_index_org = {f: i for i, f in enumerate(bm.faces)}
        ret = bmesh.ops.triangulate(bm, faces=bm.faces, use_beauty=False)
        face_map = ret["face_map"]
        # map new index to original index
        face_map_index = {i: face_map_index_org[face_map.get(f, f)] for i, f in enumerate(bm.faces)}
        del face_map_index_org
        del ret
        # Create a real mesh (lame!)
        scene = bpy.context.scene
        me_tmp = bpy.data.meshes.new(name="~temp~")
        bm.to_mesh(me_tmp)
        bm.free()
        obj_tmp = bpy.data.objects.new(name=me_tmp.name, object_data=me_tmp)
        scene.objects.link(obj_tmp)
        scene.update()
        ray_cast = obj_tmp.ray_cast
        faces_error = False
        EPS_NORMAL = 0.000001
        EPS_CENTER = 0.01  # should always be bigger
        for ed in me_tmp.edges:
            v1i, v2i = ed.vertices
            v1 = me_tmp.vertices[v1i]
            v2 = me_tmp.vertices[v2i]
            # setup the edge with an offset
            co_1 = v1.co.copy()
            co_2 = v2.co.copy()
            co_mid = (co_1 + co_2) * 0.5
            no_mid = (v1.normal + v2.normal).normalized() * EPS_NORMAL
            co_1 = co_1.lerp(co_mid, EPS_CENTER) + no_mid
            co_2 = co_2.lerp(co_mid, EPS_CENTER) + no_mid
            co, no, index = ray_cast(co_1, co_2)
            if index != -1:
                faces_error = True
        scene.objects.unlink(obj_tmp)
        bpy.data.objects.remove(obj_tmp)
        bpy.data.meshes.remove(me_tmp)
        scene.update()
        return faces_error
    
    def bmesh_copy_from_object(self, obj, transform=True, triangulate=True, apply_modifiers=False):
        """
        Returns a transformed, triangulated copy of the mesh
        """
        #assert(obj.type == 'MESH')
        if apply_modifiers and obj.modifiers:
            import bpy
            me = obj.to_mesh(bpy.context.scene, True, 'PREVIEW', calc_tessface=False)
            bm = bmesh.new()
            bm.from_mesh(me)
            bpy.data.meshes.remove(me)
            del bpy
        else:
            me = obj.data
            if obj.mode == 'EDIT':
                bm_orig = bmesh.from_edit_mesh(me)
                bm = bm_orig.copy()
            else:
                bm = bmesh.new()
                bm.from_mesh(me)
        # TODO. remove all customdata layers.
        # would save ram
        if transform:
            bm.transform(obj.matrix_world)
        if triangulate:
            bmesh.ops.triangulate(bm, faces=bm.faces, use_beauty=True)
        return bm
    
    def check_bool(self, objects, lenth, obj1, obj2):
        inters = self.interinsects(obj1, obj2)
        if inters:
            self.boolerator(obj1, obj2)
        elif lenth > 2:
            obj1 = objects[lenth - 2]
            self.check_bool(objects, lenth - 1, obj1, obj2)
    
    def boolerator(self, obj1, obj2):
        name1 = obj1.name
        name2 = obj2.name
        bpy.data.objects[name2].select = True
        bpy.data.objects[name1].select = True
        bpy.context.scene.objects.active = bpy.data.objects[name1]
        md = obj1.modifiers.new('booleanunion', 'BOOLEAN')
        md.operation = 'UNION'
        md.object = obj2
        # apply the modifier
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="booleanunion")
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[name2].select = True
        bpy.ops.object.delete()
        bpy.data.objects[name1].select = True
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

class BooleratorTranslation (bpy.types.Operator):
    """ Булен единство от Перемещения"""      
    bl_idname = "object.nt_boolerator_translation"
    bl_label = "Bool_ПОЛОЖ"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        objects_init = bpy.context.selected_objects
        lenth = len(objects_init)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        objects_dic = {}
        trans_init = objects_init[0].matrix_world.translation
        for obj in objects_init:
            trans_obj = obj.matrix_world.translation
            trans = Vector(((trans_obj[0]-trans_init[0]),
                            (trans_obj[1]-trans_init[1]),
                            (trans_obj[2]-trans_init[2])
                            ))
            lenth_obj = trans.length
            objects_dic[obj] = lenth_obj
        objects = sorted(objects_dic.items(), key=lambda x: x[1], reverse=True)
        for l in range(lenth):
            bpy.ops.object.select_all(action='DESELECT')
            #print ('l is:'+ str(l))
            if l == 0:
                continue
            elif l == lenth:
                break
            obj2 = objects[lenth-1][0]
            obj1 = objects[l - 1][0]
            name1 = obj1.name
            name2 = obj2.name
            #print (name1, name2)
            bpy.data.objects[name1].select = True
            bpy.data.objects[name2].select = True
            bpy.context.scene.objects.active = bpy.data.objects[name2]
            md = obj2.modifiers.new('booleanunion', 'BOOLEAN')
            md.operation = 'UNION'
            md.object = obj1
            # apply the modifier
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="booleanunion")
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[name1].select = True
            bpy.ops.object.delete()
        return {'FINISHED'}

class SeparatorM (bpy.types.Operator):
    """Разделитель объектов по количеству вершин"""      
    bl_idname = "object.nt_separator_multi"
    bl_label = "РАЗДЕЛИТЬ"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        self.separate()
        return {'FINISHED'}
    
    def separate(self):
        objects = bpy.context.selected_objects
        goon = False
        vert_limit1 = bpy.context.scene.NS_vertices_separator
        vert_limit2 = vert_limit1*2
        vert_limit3 = vert_limit2-1
        vert_limit4 = vert_limit1*75
        for obj in objects:
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            name = obj.name
            lenth = len(bpy.data.objects[name].data.vertices)
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[name].select = True
            bpy.context.scene.objects.active = bpy.data.objects[name]
            #bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            #bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.data.objects[name].data.vertices[0].select = True
            bpy.ops.mesh.select_linked(limit=True)
            if lenth == vert_limit1:
                print ('объект ' + str(name) + ' готов')
            elif lenth == 0:
                print ('объект ' + str(name) + ' удаляется')
                bpy.ops.object.delete()
            else:
                print ('объект ' + str(name) + ' пока ещё НЕ разделан :-( ' + str(lenth))
            if lenth > vert_limit4:
                i = 3
                goon = True
                while i:
                    division = round(lenth / 3)
                    for v in bpy.data.objects[name].data.vertices[0:division]:
                        v.select = True
                    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                    bpy.ops.mesh.select_linked(limit=True)
                    bpy.ops.mesh.separate(type='SELECTED')
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                    lenth = len(bpy.data.objects[name].data.vertices)
                    i -= 1
            
            elif lenth > vert_limit2:
                goon = True
                while lenth:
                    #bpy.ops.object.select_all(action='DESELECT')
                    #bpy.data.objects[name].select = True
                    if lenth <= vert_limit3:
                        lenth = 0
                        break
                    bpy.data.objects[name].data.vertices[0].select = True
                    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                    bpy.ops.mesh.select_linked(limit=True)
                    bpy.ops.mesh.remove_doubles()
                    bpy.ops.mesh.separate(type='SELECTED')
                    lenth = len(bpy.data.objects[name].data.vertices)
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            else:
                pass
        if goon:
            self.separate()
        print ('---- Разделка объектов окончена. ----  \n')


class BoundingBox (bpy.types.Operator):
    """Делает габаритный куб"""      
    bl_idname = "object.nt_bounding_boxers"
    bl_label = "ГАБАРИТ"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        objects = bpy.context.selected_objects
        i = 0
        #for ob in bpy.context.selected_objects:
            #if ob.type == 'MESH':
            #z = ob.dimensions
            #ob.name = "_".join(list(map(lambda x: str(int(round(x,1)*100)),z)))
        for a in objects:
            self.make_it(i, a)
            i += 1
        return {'FINISHED'}
    
    def make_it(self, i, obj):
        box = bpy.context.selected_objects[i].bound_box
        mw = bpy.context.selected_objects[i].matrix_world
        WDH = str([round(i,3) for i in bpy.context.selected_objects[i].dimensions[:]])
        name = (bpy.context.selected_objects[i].name + '_bbox|WDH' + WDH)
        me = bpy.data.meshes.new(name+'Mesh')
        ob = bpy.data.objects.new(name, me)
        ob.location = mw.translation
        ob.scale = mw.to_scale()
        ob.rotation_euler = mw.to_euler()
        ob.show_name = True
        bpy.context.scene.objects.link(ob)
        loc = []
        for ver in box:
            loc.append(mathutils.Vector((ver[0],ver[1],ver[2])))
        me.from_pydata((loc), [], ((0,1,2,3),(0,1,5,4),(4,5,6,7), (6,7,3,2),(0,3,7,4),(1,2,6,5)))
        me.update(calc_edges=True)
        return

class SpreadObjects (bpy.types.Operator):
    """Раскладывает объекты по полу."""
    bl_idname = "object.nt_spread_objects"
    bl_label = "РАЗЛОЖИТЬ"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = bpy.context.selected_objects
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        count = len(obj) - 1                # items number
        row = math.modf(math.sqrt(count))[1] or 1 #optimal number of rows and columns !!! temporery solution
        locata = mathutils.Vector()    # while veriable 
        dx, dy, ddy = 0, 0, 0                       # distance
        while count > -1:   # iterations X
            locata[2] = 0               # Z = 0
            row1 = row
            x_curr = []                     # X bounds collection
            locata[1] = 0              # Y = 0
            while row1:         # iteratiorns Y
                # counting bounds
                bb = obj[count].bound_box
                mwscale = obj[count].matrix_world.to_scale()
                mwscalex = mwscale[0]
                mwscaley = mwscale[1]
                x0 = bb[0][0]
                x1 = bb[4][0]
                y0 = bb[0][1]
                y1 = bb[2][1]
                ddy = dy            # secondary distance to calculate avverage
                dx = mwscalex*(max(x0,x1)-min(x0,x1)) + 0.03        # seek for distance !!! temporery solution
                dy = mwscaley*(max(y0,y1)-min(y0,y1)) + 0.03        # seek for distance !!! temporery solution
                # shift y
                locata[1] += ((dy + ddy) / 2)
                # append x bounds
                x_curr.append(dx)
                bpy.ops.object.rotation_clear()
                bpy.context.selected_objects[count].location = locata
                row1 -= 1
                count -= 1
            locata[0] += max(x_curr)        # X += 1
            dx, dy, ddy = 0, 0, 0
            del(x_curr)
        return {'FINISHED'}



class NT_language (bpy.types.Operator):
    """Меняет язык"""      
    bl_idname = "object.nt_language" 
    bl_label = "English"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        nt_lang_panel()
        return {'FINISHED'}

class NikitronPanel(bpy.types.Panel):
    """ Инструменты для работы """
    bl_idname = "panel.nikitron"
    bl_label = 'ИНСТРУМЕНТЫ НТ'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'SV'
    bl_options = {'DEFAULT_CLOSED'}
    #bl_context = 'objectmode'
    #bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        #global cache_obj
        #global cache_add
        #global shift
        global maxim
        global sv_lang
        
        layout = self.layout
        
        # it is all about maximum shift, it cannot update scene's veriable 'shift_verts' with 'maxim' veriable somehow
        #if context.selected_objects[0] != cache_obj[0]:
        #    bpy.data.scenes[0].update_tag()
        #    cache_obj = []
        #    cache_add()
        #    shift()

        
        box = layout.box()
        row = box.row(align=True)
        
        split = row.split(percentage=0.34)
        main = bpy.context.scene
        if main.nt_main_panel:
            split.prop(main, 'nt_main_panel', text=" ", icon='DOWNARROW_HLT')
        else:
            split.prop(main, 'nt_main_panel', text=" ", icon='RIGHTARROW')
        row.label(text=sv_lang['Title_section'])
        row.operator('object.nt_language', text=sv_lang['NT_language'])
            
            
        
        if main.nt_main_panel:
            row = box.row(align=True)
            row.operator("object.nt_compliment_wom", text=sv_lang['ComplimentWoman'])
            row.operator("object.nt_manifest_generator", text=sv_lang['NTManifestGenerator'])
            ##row.operator('wm.url_open', text=sv_lang['ComplimMan']).url = 'http://w-o-s.ru/article/2469'
            
            
            col = box.column(align=True)
            col.scale_y=1.1
            col.operator("object.nt_spread_objects",icon="GRID", text=sv_lang['SpreadObjects'])
            row = col.row(align=True)
            row.operator("object.nt_cliffordattractors",icon="OUTLINER_OB_CURVE", text=sv_lang['CliffordAttractors'])
            row = col.row(align=True)
            row.operator("object.nt_materials_to_object",icon="MATERIAL_DATA", text=sv_lang['MaterialToObjectAll'])
            row.operator("object.nt_materials_to_data",icon="MATERIAL_DATA", text=sv_lang['MaterialToDataAll'])
                
            row = col.row(align=True)
            row.operator("object.nt_name_objects",icon="OUTLINER_OB_FONT", text=sv_lang['ObjectNames'])
            row.operator("object.nt_vertices_numbers3d",icon="FONT_DATA", text=sv_lang['VerticesNumbers3D'])
            
            row = col.row(align=True)
            row.operator("object.nt_bounding_boxers",icon="SNAP_VOLUME", text=sv_lang['BoundingBox'])
            row.operator("object.nt_delete_orientation",icon="MANIPUL", text=sv_lang['DeleteOrientation'])
            
            row = col.row(align=True)
            row.scale_y=1.1
            row.operator("object.nt_delete_nodelayouts",icon="NODE", text=sv_lang['NT_ClearNodesLayouts'])
            row.prop(bpy.context.scene, "nt_clean_layout_used", text=sv_lang['CleanLayoutUsed'])
            row = col.row(align=True)
            row.operator("object.nt_duplicat",icon="GROUP_VERTEX", text=sv_lang['NTduplicat'])
        
        if bpy.context.selected_objects:
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)
            row.scale_y=1.1
            split = row.split(percentage=0.22)
            if main.nt_additional_panel:
                split.prop(main, "nt_additional_panel", text=" ", icon='DOWNARROW_HLT')
                if context.selected_objects[0].type == 'CURVE':
                    row.label(text=sv_lang['Curves_section'])
                else:
                    row.label(text=sv_lang['Mesh_section'])
            else:
                split.prop(main, "nt_additional_panel", text=" ", icon='RIGHTARROW')
                if context.selected_objects[0].type == 'CURVE':
                    row.label(text=sv_lang['Curves_section'])
                else:
                    row.label(text=sv_lang['Mesh_section'])
            
            
            if main.nt_additional_panel:
                if context.selected_objects:
                    if context.selected_objects[0].type == 'CURVE':
                        row = col.row(align=True)
                        row.operator("object.nt_curv_to_3d",icon="CURVE_DATA", text=sv_lang['CurvesTo3D'])
                        row.operator("object.nt_curv_to_2d",icon="CURVE_DATA", text=sv_lang['CurvesTo2D'])
                        row.operator("object.nt_bezier_making_good",icon="CURVE_DATA", text=sv_lang['NTbezierOrdering'])
                
                    if context.selected_objects[0].type == 'MESH':
                        box0 = col.box()
                        box1 = box0.column(align=True)
                        row = box1.row(align=True)
                        row.prop(bpy.context.scene, "nt_areacoma", text=' ', expand=True) # sv_lang['areacoma'])
                        row = box1.row(align=True)
                        row.prop(bpy.context.scene, "nt_areaseps", text=' ', expand=True) # sv_lang['areaseps'])
                        row = box1.row(align=True)
                        # row.scale_y=1.5
                        row.operator("object.nt_areaoflenin",icon="FONT_DATA", text=sv_lang['AreaOfLenin'])
                        row = box1.row(align=True)
                        row.operator("object.nt_calc_volume",icon="FONT_DATA", text=sv_lang['volume'])
                        row = box1.row(align=True)
                        row.operator("object.nt_edgelength",icon="FONT_DATA", text=sv_lang['EdgeLength'])
                        
                        
                        #row = col.row(align=True)
                        #row.operator("object.nt_separator_multi",icon="MOD_BUILD", text=sv_lang['SeparatorM'])
                        #row.prop(bpy.context.scene, "NS_vertices_separator", text=sv_lang['verticesNum_separator'])
                        #row = col.row(align=True)
                        #row.operator("object.nt_boolerator_random",icon="MOD_BOOLEAN", text=sv_lang['BooleratorRandom'])
                        #row.operator("object.nt_boolerator_intersection",icon="MOD_BOOLEAN", text=sv_lang['BooleratorIntersection'])
                        #row.operator("object.nt_boolerator_translation",icon="MOD_BOOLEAN", text=sv_lang['BooleratorTranslation'])

                        row = col.row(align=True)
                        #row.prop(bpy.context.scene, "nt_scale2vol", text=sv_lang['Volums'])
                        row.operator("object.nt_scalefit",icon="VIEW3D", text=sv_lang['NTScaleFit'])                        
                        row = col.row(align=True)
                        row.operator("object.nt_text_mesh_weld",icon="FULLSCREEN_EXIT", text=sv_lang['NTTextMeshWeld'])
                        row = col.row(align=True)
                        row.operator("object.nt_connect2objects",icon="LINKED", text=sv_lang['Connect2Meshes'])
                        row = col.row(align=True)
                        row.scale_y=1.1
                        row.prop(bpy.context.scene, "nt_shift_verts", text=sv_lang['shift_vers'])
                        row.prop(bpy.context.scene, "nt_hook_or_not", text=sv_lang['hook'])
                        row.label(text=sv_lang['maxvers'] + ' ' + str(maxim()))

my_classes = [
                CurvesTo3D, CurvesTo2D, NikitronPanel, ObjectNames,
                VerticesNumbers3D, Connect2Meshes, MaterialToObjectAll,
                MaterialToDataAll, BoundingBox, SpreadObjects,
                DeleteOrientation, SeparatorM, BooleratorRandom,
                BooleratorTranslation, BooleratorIntersection,
                ComplimentWoman, AreaOfLenin, EdgeLength,
                CliffordAttractors, NT_ClearNodesLayouts,
                NT_language, NTTextMeshWeld, NTVolumeCalculate,
                NTManifestGenerator, NTbezierOrdering, NTduplicat,
                NTScaleFit
                ]


    

    
def register():
    global handle_lang
    for clas in my_classes:
        bpy.utils.register_class(clas)
    #path = os.path.join(os.path.dirname(__file__),'nikitron_locale')
    #file=open(path, 'r+', encoding='utf-8')
    #text=file.read()
    #file.close()
    #if 'ru' in text:
        #handle_lang = False
    #elif 'en' in text:
        #handle_lang = True
    bpy
        

def unregister():
    a = reversed(my_classes)
    for clas in a:
        bpy.utils.unregister_class(clas)
    del a
            
if __name__ == "__main__":
    register()
