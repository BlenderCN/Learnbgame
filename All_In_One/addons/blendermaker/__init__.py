# *** Notes ***
#
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
###### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    'name': 'Blender maker',
    'author': 'Miguel Jimenez <miguel.jgz@gmail.com>',
    'version': (0, 1),
    "blender": (2, 5, 8),
    "api": 35622,
    'location': '',
    'description': 'Extension of blender for Open hardware 3D printing.',
    'warning': '',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'CNC'}

'''
-------------------------------------------------------------------------
Rev 0.1 Blender 2.5 support.
Is integrates addons from:
- Import/Export STL addon.
-------------------------------------------------------------------------
'''

import bpy
from bpy import* 
import os,sys
import struct
import mmap
import contextlib
import itertools
import mathutils
from bpy.props import StringProperty, BoolProperty, CollectionProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bpy.props import IntProperty, BoolProperty, FloatVectorProperty
import random
import math
import cmath
import webbrowser
import subprocess as sub

extrusion_diameter = 0.4 

######
# UI #
######

#panel blender maker GCODE.
class BMUI_GCODE(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Blender Maker: Object implementation"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        col = layout.column(align=True)
        col.label(text="Skeinforge:")
        row = col.row()
        row.operator("export.gcode", text="Export to GCODE")


#panel blender maker
class BMUI(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Blender Maker: Object model"
    bl_context = "objectmode"

    scaleXval=0
    scaleYval=0
    scaleZval=0
    randomMag=0
    dialogRF=0
    randomFact=0
    artisanActv=0
    def draw(self, context):
        global scaleXval
        global scaleYval
        global scaleZval
        global randomMag
        global dialogRF
        global randomFact
        global artisanActv

        #capture
        layout = self.layout
        obj = context.object
        scene = context.scene

        #save file.
        col = layout.column(align=True)
        row = col.row()
        row = layout.row()
        
        col.label(text="STL file", icon='FILE')
        col = layout.column()
        col = layout.column_flow(columns=5,align=True)
        row.operator("export_mesh.stl", text="Save")
        row.operator("import_mesh.stl", text="Load")

        box = layout.separator()        
        
        #select view from.
        col = layout.column()
        col.label(text="View from:", icon='MANIPUL')
        col = layout.column_flow(columns=5,align=True)
        col.operator("view3d.viewnumpad",text="X").type='LEFT'
        col.operator("view3d.viewnumpad",text="Y").type='FRONT'
        col.operator("view3d.viewnumpad",text="Z").type='TOP'
                
        #Scale
        col = layout.column(align=True)
        col.label(text="Scale object:", icon='MAN_SCALE')

        row = col.row()
        row.prop( scene, "scaleX" )
        row = col.row()
        row.prop( scene, "scaleY" )
        row = col.row()
        row.prop( scene, "scaleZ" )
        
        box = layout.separator()        
        
        col = layout.column(align=True)
        row = col.row()
        row.label(text="Randomize:", icon='FORCE_TURBULENCE')
        row = col.row()
        row.prop( scene, "randomMagnitude" )
        row = col.row()
        row.prop( scene, "randomFactor" )
        row = col.row()
        row.operator("object.randomize", text="Randomize")

        box = layout.separator()        

        col = layout.column(align=True)
        row = col.row()
        row.label(text="Artisan mode:", icon='SCULPTMODE_HLT')
        row.prop( scene, "artisanActive" )
        
        artisanActv = bpy.context.scene.artisanActive
        scaleXval = bpy.context.scene.scaleX
        scaleYval = bpy.context.scene.scaleY
        scaleZval = bpy.context.scene.scaleZ

        randomMag = bpy.context.scene.randomMagnitude
        randomFact = bpy.context.scene.randomFactor
        dialogRF = bpy.context.scene.dialog
        artisanActv = bpy.context.scene.artisanActive

#panel metadata
class BMUI_META(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Blender Maker: Object Metadata"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        
        col = layout.column(align=True)
        row = col.row()
        row = layout.row()
        
        col.label(text="RFID metadata", icon='RNA_ADD')
        col = layout.column()
        col = layout.column_flow(columns=5,align=True)
        
        row.operator("object.readrfid", text="Read")
        row.operator("object.writerfid", text="Write")        
        
        col = layout.column(align=True)
        row = col.row()
        row = layout.row()
        row = col.row()
        row.prop(scene,"dialog")
        

        row = col.row()
        row.operator("object.openurl",text="Open Web object")



class DialogOperator(bpy.types.Operator):
    bl_idname = "object.dialog_operator"
    bl_label = "RFID data:"

    my_string = bpy.props.StringProperty(name="",default="#$%")
    
    def execute(self, context):
        print("Dialog Runs")
        
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

        



        

#############
# Operators #
#############

# class ExportGcode(bpy.types.Operator):
#     ''''''
#     bl_idname = "export.gcode"
#     bl_label = "Align Selected To Active"

#     @classmethod
#     def poll(cls, context):
#         return context.active_object != None

#     def execute(self, context):
#         print("In export GCODE")
#         print("executing.")
#         import_gcode("/home/miguel/objects/test2.gcode")
#         return {'FINISHED'}


class ExportGcode(bpy.types.Operator):
    ''''''
    bl_idname = "export.gcode"
    bl_label = "Align Selected To Active"


    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        skpath="/home/miguel/tecroom/replicatorg-0025/skein_engines/skeinforge-0006/"
        objpath="/home/miguel/objects"
        print("****In export GCODE")
        print("**Exporting...")
        skein_launcher(skpath,objpath)
        print("**Finished")
        return {'FINISHED'}


class AlignOperator(bpy.types.Operator):
    ''''''
    bl_idname = "object.align"
    bl_label = "Align Selected To Active"

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        print("in Align Operator")
        return {'FINISHED'}


class randomizeObject(bpy.types.Operator):
    ''''''
    bl_idname = "object.randomize"
    bl_label = "Randomize selected object"


    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        print("in randomize operator")
        randomize2()
        return {'FINISHED'}

class readRFID(bpy.types.Operator):
    ''''''
    bl_idname = "object.readrfid"
    bl_label = "Read the rfid metadata"


    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        print("** In read metadata.")
        read_rfid()
        return {'FINISHED'}

class writeRFID(bpy.types.Operator):
    ''''''
    bl_idname = "object.writerfid"
    bl_label = "Write the rfid metadata"


    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        print("** In write metadata.")
        #webbrowser.open('http://hackaday.com')

        write_rfid()
        return {'FINISHED'}

class openURL(bpy.types.Operator):
    ''''''
    bl_idname = "object.openurl"
    bl_label = "Open the URL"


    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        print("in open url operator")
        webbrowser.open(dialogRF)
        return {'FINISHED'}



class ExportSTL(bpy.types.Operator, ExportHelper):
    '''
    Save STL triangle mesh data from the active object
    '''
    bl_idname = "export_mesh.stl"
    bl_label = "Export STL"

    filename_ext = ".stl"

    ascii = BoolProperty(name="Ascii",
                         description="Save the file in ASCII file format",
                         default=False)
    apply_modifiers = BoolProperty(name="Apply Modifiers",
                                   description="Apply the modifiers "
                                               "before saving",
                                   default=True)

    def execute(self, context):
        from . import stl_utils
        from . import blender_utils
        import itertools
        
        print("in export")
        faces = itertools.chain.from_iterable(
            blender_utils.faces_from_mesh(ob, self.apply_modifiers)
            for ob in context.selected_objects)
        
        stl_utils.write_stl(self.filepath, faces, self.ascii)

        return {'FINISHED'}




##########
# Events #
##########
def scale_x(self, context):
    print("** in scale x")
    obj = context.object
    obj.scale[0] = scaleXval
    
def scale_y(self, context):
    print("** in scale y")
    obj = context.object
    obj.scale[1] = scaleYval

def scale_z(self, context):
    print("** in scale z")
    obj = context.object
    obj.scale[2] = scaleZval

def artisan_actv(self,context):
    print("** In artisan mode event")
    print(artisanActv)

def ASCIICheck(self, context):
    print("** in scale ASCII check")
    #ASCIIcheckstate = true



##############
# Registring #
##############

def register():
    bpy.utils.register_class(AlignOperator)
    bpy.utils.register_class(randomizeObject)
    bpy.utils.register_class(readRFID)
    bpy.utils.register_class(writeRFID)
    bpy.utils.register_class(openURL)
    bpy.utils.register_class(BMUI_GCODE)
    bpy.utils.register_class(BMUI)
    bpy.utils.register_class(BMUI_META)
    bpy.utils.register_class(ExportSTL)
    bpy.utils.register_class(ExportGcode)
    bpy.utils.register_class(DialogOperator) 
    #bpy.types.INFO_MT_file_import.append(menu_func)


    scnType = bpy.types.Scene
    scnType.scaleX = bpy.props.FloatProperty( name = "X", 
                                                     default = 10, min = -20, max = 20, 
                                                     description = "Scale object in X axys" ,update=scale_x)
    
    scnType = bpy.types.Scene
    scnType.scaleY = bpy.props.FloatProperty( name = "Y", 
                                                     default = 1, min = -20, max = 20, 
                                                     description = "Scale object in Y axys",update=scale_y)
    
    scnType = bpy.types.Scene
    scnType.scaleZ = bpy.props.FloatProperty( name = "Z", 
                                                     default = 1, min = -20, max = 20, 
                                                     description = "Scale object in Z axys",update=scale_z)
    
    scnType = bpy.types.Scene
    scnType.randomMagnitude = bpy.props.IntProperty( name = "Jump Vertices", 
                                                     default = 0, min = -20, max = 20, 
                                                     description = "Randomize object")
    
    
    scnType = bpy.types.Scene
    scnType.randomFactor = bpy.props.FloatProperty( name = "Randomfactor", 
                                                     default = 0, min = 0, max = 5, 
                                                     description = "Randomize factor")


    scnType = bpy.types.Scene
    scnType.dialog = bpy.props.StringProperty( name = "Tag memory:")


    
    scnType = bpy.types.Scene
    scnType.artisanActive = bpy.props.BoolProperty( name = "Active", 
                                                     default = 1, 
                                                     description = "Artisan mode checkbox",update=artisan_actv)
    
    

    scale = FloatVectorProperty(name="Scale",
        description="Maximum scale randomization over each axis",
        default=(0.0, 0.0, 0.0), min=-100.0, max=100.0, subtype='TRANSLATION')
    
    pass


def unregister():
    bpy.utils.register_class(AlignOperator)
    bpy.utils.register_class(randomizeObject)
    bpy.utils.register_class(BMUI_GCODE)
    bpy.utils.register_class(BMUI)
    bpy.utils.register_class(BMUI_META)
    bpy.utils.register_class(ExportSTL)
    bpy.utils.register_class(ExportGcode)
    #bpy.types.INFO_MT_file_import.append(menu_func)

    pass


if __name__ == "__main__":
    register()

    
#############
# Functions #
#############

# Writing stl#
def write_stl(filename, faces, ascii=False):
    '''
    Write a stl file from faces,

    filename
       output filename

    faces
       iterable of tuple of 3 vertex, vertex is tuple of 3 coordinates as float

    ascii
       save the file in ascii format (very huge)
    '''
    print("** In write_stl")
    (_ascii_write if ascii else _binary_write)(filename, faces)


def _ascii_write(filename, faces):
    with open(filename, 'w') as data:
        data.write('solid Exported from blender\n')

        for face in faces:
            data.write('''facet normal 0 0 0\nouter loop\n''')
            for vert in face:
                data.write('vertex %f %f %f\n' % vert)
            data.write('endloop\nendfacet\n')

        data.write('endsolid Exported from blender\n')


def _binary_write(filename, faces):
    with open(filename, 'wb') as data:
        # header
        # we write padding at header begginning to avoid to
        # call len(list(faces)) which may be expensive
        data.write(struct.calcsize('<80sI') * b'\0')

        # 3 vertex == 9f
        pack = struct.Struct('<9f').pack
        # pad is to remove normal, we do use them
        pad = b'\0' * struct.calcsize('<3f')

        nb = 0
        for verts in faces:
            # write pad as normal + vertexes + pad as attributes
            data.write(pad + pack(*itertools.chain.from_iterable(verts)))
            data.write(b'\0\0')
            nb += 1

        # header, with correct value now
        data.seek(0)
        data.write(struct.pack('<80sI', b"Exported from blender", nb))


def randomize():
    obj = context.object
    
    mesh = obj.data

    copyverts=mesh.vertices[:]
    covertices=[]

    topz=copyverts[0].co[2]
    bottomz=copyverts[0].co[2]
        
    #find topz and bottomz
    for vertice in copyverts:
            if(vertice.co[2]>topz):
                topz=vertice.co[2]
            elif(vertice.co[2]<bottomz):
                bottomz=vertice.co[2]
                
    print("** The vertices:")
    print("top="+str(topz)+",bottom="+str(bottomz))

    #pass to all the vertices.
    for vertice in copyverts:
        #top and bottom layers.
        if(vertice.co[2]>bottomz and vertice.co[2]<topz):
            verticeact=vertice
            if not(verticeact in covertices):
                covertices.append(vertice)
                randx=random.uniform(-0.1,0.1)
                randy=random.uniform(-0.1,0.1)
                index=0
                step=randomMag-1
                for index,verticeref in enumerate(copyverts):
                    if(step == 0):
                        if verticeref.co[0]==verticeact.co[0]:
                            mesh.vertices[index].co[0]= verticeref.co[0]+randx
                            mesh.vertices[index].co[1]= verticeref.co[1]+randy
                        else:
                            print("was already")
                        step=randomMag
                    else:
                        print("step salta")
                    step=step-1


def randomize2():

    obj = context.object
    
    mesh = obj.data

    copyverts=mesh.vertices[:]
    covertices=[]

    topz=copyverts[0].co[2]
    bottomz=copyverts[0].co[2]
   
    
    #find topz and bottomz
    for vertice in copyverts:
        if(vertice.co[2]>topz):
            topz=vertice.co[2]
        elif(vertice.co[2]<bottomz):
            bottomz=vertice.co[2]
                
    print("** The vertices:")
    print("top="+str(topz)+",bottom="+str(bottomz))

    step=randomMag

    #pass to all the vertices.
    for index,verticeref in enumerate(copyverts):
        if(step==0):
            r,phi=cmath.polar(complex(verticeref.co[0],verticeref.co[1]))
            r=random.uniform(-randomFact,randomFact)+r
            x=cmath.rect(r,phi)
            mesh.vertices[index].co[0]= x.real
            mesh.vertices[index].co[1]= x.imag
            step=randomMag
        else:
            step=step-1


def read_rfid():
    rfidpath="./2.60/scripts/addons/bm/lib-touchatag-1.0/"
    print("********")
    print("* Reading RFID...")
    #bpy.ops.object.dialog_operator('INVOKE_DEFAULT') 
    p = sub.Popen(rfidpath+"rfidreader",stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    print(output[len(output)-12:])

def write_rfid():
    rfidpath="./2.60/scripts/addons/bm/lib-touchatag-1.0/"
    print("\n************")
    print("\n* Writing RFID:"+str(dialogRF))

    os.system(rfidpath+"rfidwriter "+dialogRF)
    print("\n done.")
    print("\n************")

    




##################
#CLASes and GCODE#
##################
class tool:
    def __init__(self,name='null tool'):
        self.name = name

class move():
    def __init__(self,pos):
        self.pos = pos
        p = []
        p.append(self.pos['X'])
        p.append(self.pos['Y'])
        p.append(self.pos['Z'])
        self.point = p
    
class fast_move(move):
    def __init__(self,pos):
        move.__init__(self,pos)
        
class tool_on:
    def __init__(self,val):
        pass

class tool_off:
    def __init__(self,val):
        pass

class layer:
    def __init__(self):
        print('layer')
        pass

class setting:
    def __init__(self,val):
        pass

class set_temp(setting):
    def __init__(self,val):
        setting.__init__(self,val)
 
class tool_change():
    def __init__(self,val):
        self.val = val

class undef:
    def __init__(self,val):
        pass


codes = {
    '(':{
        '</surroundingLoop>)' : undef,
        '<surroundingLoop>)' : undef,
        '<boundaryPoint>' : undef,
        '<loop>)' : undef,
        '</loop>)' : undef,
        '<layer>)' : undef,
        '</layer>)' : undef,
        '<layer>' : undef,
        '<perimeter>)' : undef,
        '</perimeter>)' : undef, 
        '<bridgelayer>)' : undef,
        '</bridgelayer>)' : undef,
        '</extrusion>)' :undef                     
    },
    'G':{
        '0': fast_move,
        '1': move,
        '01' : move,
        '04': undef,
        '21': setting,
        '28': setting, # go home
        '92': setting, # not sure what this is 
        '90': setting
    },
    'M':{
        '01' : undef,
        '6' : undef,
        '101' : tool_on,
        '103' : tool_off,
        '104' : set_temp,
        '105' : undef,
        '106' : undef,
        '107' : undef,
        '108' : undef,
        '109' : undef, # what is this ? 
        '113' : undef, # what is this ? 
        '115' : undef, # what is this ? 
        '116' : undef, # what is this ? 
        '117' : undef # what is this ? 
    },
    'T':{
        '0;' : tool_change
    }
}

class driver:
    # takes action object list and runs through it 
    def __init__(self):
        pass
    
    def drive(self):
        pass 
    
    def load_data(self,data):
        self.data = data

    
def vertsToPoints(Verts):
    # main vars
    vertArray = []
    for v in Verts:
        vertArray += v
        vertArray.append(0)
    return vertArray

def create_poly(verts,counter):
    splineType = 'POLY'
    name = 'skein'+str(counter) 
    pv = vertsToPoints(verts)
    # create curve
    scene = bpy.context.scene
    newCurve = bpy.data.curves.new(name, type = 'CURVE')
    newSpline = newCurve.splines.new(type = splineType)
    newSpline.points.add(int(len(pv)*0.25 - 1))
    newSpline.points.foreach_set('co',pv)
    newSpline.use_endpoint_u = True
    
    # create object with newCurve
    newCurve.bevel_object = bpy.data.objects['profile']
    newCurve.dimensions = '3D'
    new_obj = bpy.data.objects.new(name, newCurve) # object
    scene.objects.link(new_obj) # place in active scene
    return new_obj
    
class blender_driver(driver):
     def __init__(self):
         driver.__init__(self)
         
     def drive(self):        
        print('building curves')
        # info 
        count = 0 
        for i in self.data:
            if isinstance(i,layer):
                count += 1
        print('has '+str(count)+' layers')
        
        print('creating poly lines')
        if 'profile' in bpy.data.objects:
            print('profile exisits')
        else:
            bpy.ops.curve.primitive_bezier_circle_add()
            curve = bpy.context.selected_objects[0]
            d = extrusion_diameter
            curve.scale = [d,d,d]
            curve.name = 'profile'
            curve.data.resolution_u = 2
            curve.data.render_resolution_u = 2
            
        poly = []
        layers = []
        this_layer = []
        counter = 1
        global thing
        for i in self.data:
            if isinstance(i,move):
                #print(i.point)
                poly.append(i.point)
            if isinstance(i,tool_off):
                if len(poly) > 0:
                    counter += 1
                    pobj = create_poly(poly,counter)
                    this_layer.append(pobj)
                poly = []
            if isinstance(i,layer):
                print('layer '+str(len(layers)))
                layers.append(this_layer)
                this_layer = []
        layers.append(this_layer)
        
        print('animating build')
        
        s = bpy.context.scene
        # make the material 
        if 'Extrusion' in bpy.data.materials:
            mt = bpy.data.materials['Extrusion']
        else:
            # make new material
            bpy.ops.material.new()
            mt = bpy.data.materials[-1]
            mt.name = 'Extrusion'
        
        s.frame_end = len(layers)
        # hide everything at frame 0
        s.frame_set(0)
        
        for i in range(len(layers)):
            for j in layers[i]:
                j.hide = True
                j.hide_render = True
                j.keyframe_insert("hide")
                j.keyframe_insert("hide_render")
                # assign the material 
                j.active_material = mt
        
        # go through the layers and make them reappear
        for i in range(len(layers)):
            s.frame_set(i)
            print('frame '+str(i))
            for j in layers[i]:
                j.hide = False
                j.hide_render = False
                j.keyframe_insert("hide")
                j.keyframe_insert("hide_render")



class machine:

    def __init__(self,axes):
        self.axes = axes
        self.axes_num = len(axes)
        self.data = []
        self.cur = {} 
        self.tools = []
        self.commands = []
        self.driver = driver()

    def add_tool(self,the_tool):
        self.tools.append(the_tool)
        
    def remove_comments(self):
        tempd=[]
        for st in self.data:
            startcommentidx= st.find('(')
            if startcommentidx == 0 :  #line begins with a comment 
                split1=st.partition(')')
                st = ''
            if startcommentidx > 0:   # line has an embedded comment to remove
                split1=st.partition('(')
                split2=split1[2].partition(')')
                st = split1[0]+split2[2]
            if st != '':    
                tempd.append(st)
            #print("...>",st)
        self.data=tempd
        
    

    def import_file(self,file_name):
        print('opening '+file_name)
        f = open(file_name)
        #for line in f:
        #    self.data.append(self.remove_comments(line))
        self.data=f.readlines()
        f.close()
        self.remove_comments()
        
        # uncomment to see the striped file
        #k = open('c:/davelandia/blender/out1.txt','w')
        #k.writelines(self.data)
        #k.close()
        
        print(str(len(self.data))+' lines')
        
                
    def process(self):
        # zero up the machine
        pos = {}
        for i in self.axes:
            pos[i] = 0
            self.cur[i] = 0
        for i in self.data:
            i=i.strip()
            print( "Parsing Gcode line ", i)   
            #print(pos)
            tmp = i.split()
            if(len(tmp)==0):
                tmp=['E','0','0']
                print("No processable")
            #print(type.tmp)
            command = tmp[0][0]
            com_type = tmp[0][1:]
            if command in codes:
                if com_type in codes[command]:
                    #print('good =>'+command+com_type)
                    for j in tmp[1:]:
                        axis = j[0]
                        if axis == ';':
                            # ignore comments
                            break
                        if axis in self.axes:
                            val = float(j[1:])
                            pos[axis] = val
                            if self.cur['Z'] != pos['Z']:
                                self.commands.append(layer())
                            self.cur[axis] = val
                    # create action object
                    #print(pos)
                    act = codes[command][com_type](pos)
                    #print(act)
                    self.commands.append(act)
                    #if isinstance(act,move):
                        #print(act.coord())
                else:
                    print(i)
                    print(' G/M/T Code for this line is unknowm ' + com_type)
                    #break
            else:
                
                print(' line does not have a G/M/T Command '+ str(command))
                #break

def import_gcode(file_name):
    print('hola')
    m = machine(['X','Y','Z','F','S'])
    m.import_file(file_name)
    m.process()
    d = blender_driver()
    d.load_data(m.commands)
    d.drive()
    print('finished parsing... done')


DEBUG= False
from bpy.props import *

def tripleList(list1):
    list3 = []
    for elt in list1:
        list3.append((elt,elt,elt))
    return list3

theMergeLimit = 4
theCodec = 1 
theCircleRes = 1

def skein_launcher(skpath,objpath):
    print("In skein launcher")
    obj = context.object
    print(obj.name)
    
    print(str(skpath)+"skeinforge.py  -p "+str(skpath)+"prefs/skeinforge/export.csv "+objpath+"/"+str(obj.name)+".stl")
    os.system(str(skpath)+"skeinforge.py  -p "+str(skpath)+"prefs/skeinforge/ "+objpath+"/vaas4.stl")

    # if(os.system(path+"skeinforge.py  -p "+path+"prefs/skeinforge/export.csv /home/miguel/objects/" +obj.name+".stl")):
    #     print("sucess")
    # else:
    #     print("Error: Wrong path ")
        





