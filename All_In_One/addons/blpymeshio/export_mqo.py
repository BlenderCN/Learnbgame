#!BPY
# coding: utf-8

"""
Name: 'Metasequoia (.mqo)...'
Blender: 245
Group: 'Export'
Tooltip: 'Save as Metasequoia MQO File'
"""
__author__= 'ousttrue'
__url__ = ["http://gunload.web.fc2.com/blender/"]
__version__= '2.4'
__bpydoc__ = """\
This script is an exporter to MQO file format.

Usage:

Run this script from "File->Export" menu.

20080128:
20100518: refactoring.
20100606: integrate 2.4 and 2.5.
20100626: refactoring.
20100710: add [apply_modifier] option(2.5 only).
20100714: remove shape_key when apply_modifier. fix material.
20100724: update for Blender2.53.
20101005: update for Blender2.54.
20101228: update for Blender2.55.
20110429: update for Blender2.57b.
"""

bl_addon_info = {
        "category": "Learnbgame",
        'name': 'Export: Metasequioa Model Format (.mqo)',
        'author': 'ousttrue',
        'version': (2, 1),
        'blender': (2, 5, 3),
        'location': 'File > Export',
        'description': 'Export to the Metasequioa Model Format (.mqo)',
        'warning': '', # used for warning icon and text in addons panel
        'wiki_url': 'http://sourceforge.jp/projects/meshio/wiki/FrontPage',
        'tracker_url': 'http://sourceforge.jp/ticket/newticket.php?group_id=5081',
        }

import os
import sys
import bpy
import bpy_extras.io_utils # pylint: disable=E0401


class MQOMaterial(object):
    __slots__=[
            'name', 'shader', 'r', 'g', 'b', 'a',
            'dif', 'amb', 'emi',
            ]
    def __init__(self, name, shader=3):
        self.name=name
        self.shader=shader
        self.r=0.5
        self.g=0.5
        self.b=0.5
        self.a=1
        self.dif=1
        self.amb=0
        self.emi=0

    def __str__(self):
        return "\"%s\" shader(%d) col(%f %f %f %f) dif(%f) amb(%f) emi(%f)" % (
                self.name, self.shader, self.r, self.g, self.b, self.a,
                self.dif, self.amb, self.emi
                )


# for 2.5
import bpy

# wrapper
from . import bl

def materialToMqo(m):
    material=MQOMaterial(m.name, 3)
    material.r=m.diffuse_color[0]
    material.g=m.diffuse_color[1]
    material.b=m.diffuse_color[2]
    material.a=m.alpha
    material.amb=m.ambient
    material.emi=m.emit
    return material

def apply_transform(vec, matrix):
    x, y, z = vec
    xloc, yloc, zloc = matrix[3][0], matrix[3][1], matrix[3][2]
    return    x*matrix[0][0] + y*matrix[1][0] + z*matrix[2][0] + xloc,\
            x*matrix[0][1] + y*matrix[1][1] + z*matrix[2][1] + yloc,\
            x*matrix[0][2] + y*matrix[1][2] + z*matrix[2][2] + zloc

def convert_to_mqo(vec):
    return vec.x, vec.z, -vec.y


class OutlineNode(object):
    __slots__=['o', 'children']
    def __init__(self, o):
        self.o=o
        self.children=[]

    def __str__(self):
        return "<Node %s>" % self.o


class ObjectInfo(object):
    __slots__=['object', 'depth', 'material_map']
    def __init__(self, o, depth):
        self.object=o
        self.depth=depth
        self.material_map={}

    def __str__(self):
        return "<ObjectInfo %d %s>" % (self.depth, self.object)


class MqoExporter(object):
    __slots__=["materials", "objects", 'scale', 'apply_modifier',]
    def __init__(self, scale, apply_modifier):
        self.objects=[]
        self.materials=[]
        self.scale=scale
        self.apply_modifier=apply_modifier

    def setup(self, scene):
        # 木構造を構築する
        object_node_map={}
        for o in scene.objects:
            object_node_map[o]=OutlineNode(o)
        for node in object_node_map.values():
            if node.o.parent:
                object_node_map[node.o.parent].children.append(node)

        # ルートを得る
        root=object_node_map[scene.objects.active]

        # 情報を集める
        if root.o.type.upper()=='EMPTY':
            # depth調整 
            for node in root.children:
                self.__setup(node)
        else:
            self.__setup(root)

    def __setup(self, node, depth=0):
        info=ObjectInfo(node.o, depth)
        self.objects.append(info)
        if node.o.type.upper()=='MESH':
            # set material index
            for i, m in enumerate(node.o.data.materials):
                info.material_map[i]=self.__getOrAddMaterial(m)
        # recursive
        for child in node.children:
            self.__setup(child, depth+1)
            
    def __getOrAddMaterial(self, material):
        for i, m in enumerate(self.materials):
            if m==material:
                return i
        index=len(self.materials)
        self.materials.append(material)
        return index

    def write(self, path):
        bl.message("open: "+path)
        io=bl.Writer(path, 'cp932')
        self.__write_header(io)
        self.__write_scene(io)
        print("Writing MaterialChunk")
        self.__write_materials(io, os.path.dirname(path))
        print("Writing ObjectChunk")
        for info in self.objects:
            self.__write_object(io, info)
        io.write("Eof\r\n")
        io.flush()
        io.close()

    def __write_header(self, io):
        io.write("Metasequoia Document\r\n")
        io.write("Format Text Ver 1.0\r\n")
        io.write("\r\n")

    def __write_scene(self, io):
        print("Writing SceneChunk")
        io.write("Scene {\r\n")
        io.write("}\r\n")

    def __write_materials(self, io, dirname):
        # each material    
        io.write("Material %d {\r\n" % (len(self.materials)))
        for m in self.materials:
            io.write(str(materialToMqo(m)))
            # ToDo separated alpha texture
            for filename in bl.material.eachTexturePath(m):
                if len(dirname)>0 and filename.startswith(dirname):
                    # 相対パスに変換する
                    filename=filename[len(dirname)+1:]
                io.write(" tex(\"%s\")" % filename)
                break
            io.write("\r\n") 
        # end of chunk
        io.write("}\r\n") 

    def __write_object(self, io, info):
        print(info)

        obj=info.object
        if obj.type.upper()=='MESH' or obj.type.upper()=='EMPTY':
            pass
        else:
            print(obj.type)
            return

        io.write("Object \""+obj.name+"\" {\r\n")

        # depth
        io.write("\tdepth %d\r\n" % info.depth)
        io.write("\tvisible %d\r\n" % 15)
        # mirror
        if not self.apply_modifier:
            if bl.modifier.hasType(obj, 'MIRROR'):
                    io.write("\tmirror 1\r\n")
                    io.write("\tmirror_axis 1\r\n")

        if obj.type.upper()=='MESH':
            # duplicate and applyMatrix
            copyMesh, copyObj=bl.object.duplicate(obj)
            # apply transform
            """
            copyObj.scale=obj.scale
            bpy.ops.object.scale_apply()
            copyObj.rotation_euler=obj.rotation_euler
            bpy.ops.object.rotation_apply()
            copyObj.location=obj.location
            bpy.ops.object.location_apply()
            """
            copyMesh.transform(obj.matrix_world)
            # apply modifier
            if self.apply_modifier:
                # remove shape key
                while bl.object.hasShapeKey(copyObj):
                    bpy.ops.object.shape_key_remove()
                for m in [m for m in copyObj.modifiers]:
                    if m.type=='SOLIDFY':
                        continue
                    elif m.type=='ARMATURE':
                        bpy.ops.object.modifier_apply(modifier=m.name)
                    elif m.type=='MIRROR':
                        bpy.ops.object.modifier_apply(modifier=m.name)
                    else:
                        print(m.type)
            # write mesh
            self.__write_mesh(io, copyMesh, info.material_map)
            bl.object.delete(copyObj)

        io.write("}\r\n") # end of object

    def __write_mesh(self, io, mesh, material_map):
        # vertices
        io.write("\tvertex %d {\r\n" % len(mesh.vertices))
        for vert in mesh.vertices:
            x, y, z = convert_to_mqo(vert.co)
            io.write("\t\t%f %f %f\r\n" % 
                    (x*self.scale, y*self.scale, z*self.scale)) # rotate to y-up
        io.write("\t}\r\n")

        # faces
        io.write("\tface %d {\r\n" % len(mesh.polygons))
        for i, face in enumerate(mesh.polygons):
            count=bl.face.getVertexCount(face)
            # V
            io.write("\t\t%d V(" % count)
            for j in reversed(bl.face.getVertices(face)):
                io.write("%d " % j)
            io.write(")")
            # mat
            if len(mesh.materials):
                io.write(" M(%d)" % 
                        material_map[bl.face.getMaterialIndex(face)])
            # UV
            if bl.mesh.hasUV(mesh) and bl.mesh.hasFaceUV(mesh, i, face):
                io.write(" UV(")
                for uv in reversed(bl.mesh.getFaceUV(mesh, i, face, count)):
                    # reverse vertical value
                    io.write("%f %f " % (uv[0], 1.0-uv[1])) 
                io.write(")")
            io.write("\r\n")
        io.write("\t}\r\n") # end of faces


def _execute(filepath='', scale=10, apply_modifier=False):
    if bl.object.getActive():
        exporter=MqoExporter(scale, apply_modifier)
        exporter.setup(bl.scene.get())
        exporter.write(filepath)
    else:
        bl.message('no active object !')


class ExportMqo(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    '''Save a Metasequoia MQO file.'''
    bl_idname = 'export_scene.metasequioa_mqo'
    bl_label = 'Export MQO'

    filename_ext = '.mqo'
    filter_glob = bpy.props.StringProperty(
            default='*.mqo', options={'HIDDEN'})

    use_selection = bpy.props.BoolProperty(
            name='Selection Only', 
            description='Export selected objects only', 
            default=False)

    scale = bpy.props.FloatProperty(
            name='Scale',
            description='Scale the MQO by this value',
            min=0.0001, max=1000000.0,
            soft_min=0.001, soft_max=100.0, default=10.0)

    apply_modifier = bpy.props.BoolProperty(
            name='ApplyModifier',
            description='Would apply modifiers',
            default=False)

    def execute(self, context):
        bl.initialize('mqo_export', context.scene)
        _execute(**self.as_keywords(
            ignore=('check_existing', 'filter_glob', 'use_selection')))
        bl.finalize()
        return {'FINISHED'}

    @classmethod
    def menu_func(klass, self, context):
        default_path=bpy.data.filepath.replace('.blend', '.mqo')
        self.layout.operator(klass.bl_idname,
                text='Metasequoia (.mqo)',
                icon='PLUGIN'
                ).filepath=default_path
