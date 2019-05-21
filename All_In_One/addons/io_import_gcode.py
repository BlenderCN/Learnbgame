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

## blendish python ripped from fro io_import_dxf

import bpy 

bl_info = {
    'name': 'Import GCode from Makerbot or Reprap',
    'author': 'Simon Kirkby',
    'version': (0,0,5),
    'blender': (2, 5, 6),
    'api': 32738,
    'location': 'File > Import-Export > Gcode',
    'description': 'Import and visualize gcode files generated for Makerbot printers (.gcode)',
    "wiki_url": "",
    "tracker_url": "",
    'category': 'Import-Export'}

__version__ = '.'.join([str(s) for s in bl_info['version']])

# gcode parser for blender 2.5 
# Simon Kirkby
# 201102051305
# tigger@interthingy.com 

#modified by David Anderson to handle Skeinforge comments
# Thanks Simon!!!

# modified by Alessandro Ranellucci (2011-10-14)
# to make it compatible with Blender 2.59
# and with modern 5D GCODE

# Modified by Winter Guerra (XtremD) on February 16th, 2012
# to make the script compatable with stock Makerbot GCode files
# and grab all nozzle extrusion information from Skeinforge's machine output
# WARNING: This script no longer works with stock 5D GCode! (Can somebody please integrate the two versions together?)

# A big shout-out goes to my friend Jon Spyreas for helping me block-out the maths needed in the "addArc" subroutine
# Thanks a million dude!
# Github branch link: https://github.com/xtremd/blender-gcode-reader

import string,os
import bpy
import mathutils
import math


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
    def __init__(self,pos):
        self.pos = pos
        p = []
        p.append(self.pos['X'])
        p.append(self.pos['Y'])
        p.append(self.pos['Z'])
        self.point = p

class setLayerHeight:
    def __init__(self,val):
        print('Got layer height: ')
        print(val)
        
        machine.extrusion_height = val
        pass

class setExtrusionWidth:
    def __init__(self,val):
        print('Got extrusion width')
        print(val)
        
        machine.extrusion_width = val
        pass

class layer:
    def __init__(self):
        print('New layer')
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
        '<layer>)' : undef, #Just changed
        '</layer>)' : undef,
        '<layer>' : undef,
        '<layerThickness>' : setLayerHeight,
        '</layerThickness>)' : undef,
        '<perimeter>)' : undef,
        '</perimeter>)' : undef, 
        '<bridgelayer>)' : undef,
        '</bridgelayer>)' : undef,
        '</extrusion>)' : undef,
        '<perimeterWidth>' : setExtrusionWidth,
        '</perimeterWidth>)' : undef
    
    },    
    'G':{
        '0': move,
        '1': move,
        '01' : move
        
    },
    'M':{
        '101' : tool_on,
        '103' : tool_off
        
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
        #vertArray.append(1) #If using NURBS, must be 1
    return vertArray

def create_poly(verts,counter):
    name = 'skein'+str(counter) 
    pv = vertsToPoints(verts)
    # create curve
    scene = bpy.context.scene
    newCurve = bpy.data.curves.new(name, type = 'CURVE')
    
    newSpline = newCurve.splines.new(type='POLY')
    newSpline.points.add((len(pv)*0.25) - 1)
    newSpline.points.foreach_set('co',pv)
    #newSpline.use_endpoint_u = True #Too CPU intensive!
    
    #newspline.order_u = 4
    
    # create object with newCurve
    newCurve.dimensions = '3D'
    newCurve.bevel_object = bpy.data.objects['profile']
    new_obj = bpy.data.objects.new(name, newCurve) # object
    scene.objects.link(new_obj) # place in active scene
    return new_obj

def addArc(Verts):
    #Takes the verts for a polyline and then adds verts on either side of the original verts to create a sort of 'arc'
    #Should help prevent the polyline from doing stupid things like kinking or twisting
    
    # A big shout-out goes to my friend Jon Spyreas for helping me block-out the maths needed in this subroutine
    # Thanks a million dude!
    
    vertArray = []
    
    #Take the list of verts to process
    for index, vert in enumerate(Verts):
        #Place first vert into list
        vertArray.append(vert)
        
        if (index < len(Verts)-1): #Is this not the last vert in the polyline?
            #Do arc stuff
            
            #Peek at the next vert
            peekVert = Verts[index+1]
            
            #Add arcpoints this far apart (in mm) on either side of the polyline point grabbed from the GCode file 
            distance = 0.02
            doubleDistance = distance*2
            
            #SANITY CHECK!
            #Check that the next vert is AT LEAST more than 2 x the "distance" away.
            if (math.pow((peekVert[1]-vert[1]),2) + math.pow((peekVert[0]-vert[0]),2) <= math.pow(doubleDistance,2)):
                #The verts are too close together! Argh!
                #Let's not mess with these verts, they look pretty scary.
                print('Discarding arcpoints; verts too close together.')
                continue
            
            if((peekVert[0]-vert[0]) == 0):
                #interpolated verts will be straight along the y axis
                #Assume that the yOffset will be the distance, xOffset will be 0
                xOffset = 0
                yOffset = distance
            
            else:
                #Calculate slope (Rise over run)
                slope = (peekVert[1]-vert[1])/(peekVert[0]-vert[0])
                #Get angle relative to X axis
                radians = math.atan(slope) #Outputs radians
                
                #Calculate the x and y offsets
                xOffset = math.cos(radians)*distance
                yOffset = math.sin(radians)*distance
        
            #Make sure that the offsets are positive (this makes for easier arithmetic logic)
            xOffset = math.fabs(xOffset)
            yOffset = math.fabs(yOffset)
            
            #Init arcpoints
            arcPoint1 = []
            arcPoint2 = []
            
            #if the starting loc is smaller than the ending loc
            #We want the points to gradually increase
            if (vert[0] < peekVert[0]):
                arcPoint1.append(vert[0]+xOffset)
                arcPoint2.append(peekVert[0]-xOffset)
            else:
                #gradually decrease
                arcPoint1.append(vert[0]-xOffset)
                arcPoint2.append(peekVert[0]+xOffset)
                    
            if (vert[1] < peekVert[1]):
                #gradually increase
                arcPoint1.append(vert[1]+yOffset)
                arcPoint2.append(peekVert[1]-yOffset)
            else:
                #gradually decrease
                arcPoint1.append(vert[1]-yOffset)
                arcPoint2.append(peekVert[1]+yOffset)
                    
            #Add the current Z position to the new arcpoints
            #Use the starting point's Z pos as it should be on the same plane as the rest of the verts added
            #This looks wierd but actualy fixes the bug that happens where the last segment of the poly is a
            #move on the Z axis.
        
            arcPoint1.append(vert[2])
            arcPoint2.append(vert[2]) 
    
#            ######DEBUG OUTPUT CODE######
#            print('#######Interpolating points########')
#    
#            print('Point1 X'+str(vert[0])+' Y'+str(vert[1])+' Z'+str(vert[2]))
#            
#            print('Point2 X'+str(arcPoint1[0])+' Y'+str(arcPoint1[1])+' Z'+str(arcPoint1[2]))
#            
#            print('Point3 X'+str(arcPoint2[0])+' Y'+str(arcPoint2[1])+' Z'+str(arcPoint2[2]))
#                
#            print('Point4 X'+str(peekVert[0])+' Y'+str(peekVert[1])+' Z'+str(peekVert[2]))
#            
#            print('xOffset'+str(xOffset)+' yOffset'+str(yOffset))
#            
#            print('#######Done interpolating points########')
            
            #Add the arcpoints to the vert list
            vertArray.append(arcPoint1)
            vertArray.append(arcPoint2)
    
    return vertArray

    
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
            print('profile exists')
        else:
            bpy.ops.curve.primitive_bezier_circle_add()
            curve = bpy.context.selected_objects[0]
            #Get the extrusion width and height from our cached values (taken from skeinforge comments in our GCode file)
            curve.dimensions = [float(machine.extrusion_width),float(machine.extrusion_height),0]
            curve.name = 'profile'
            curve.data.resolution_u = 2
            curve.data.render_resolution_u = 2
            
        poly = []
        endingPoint = []
        startingPoint = []
        layers = []
        this_layer = []
        counter = 1
        global thing
        for i in self.data:
            if isinstance(i,move):
                poly.append(i.point)
                endingPoint = i.point
            
            if isinstance(i,tool_off):
                
                if len(poly) > 0:#A poly is only a poly if it has more than one point!
                    
                    #poly.append(endingPoint) #make two starting and ending points to try and straighten out some of polyline's wierdness
                    
                    poly.insert(0,startingPoint) #Prepend the poly with the last point before the extruder was turned on
                    
                    print('Adding arc points to poly')
                    polyArc = addArc(poly)
                    
                    counter += 1
                    print('Creating poly ' + str(counter))
                    pobj = create_poly(polyArc,counter)
                    #pobj = create_poly(poly,counter)
                        
                    this_layer.append(pobj)
                else:                       #This is not a poly! Discard!
                    print('Discarding bad poly')
                poly = []
                startingPoint = i.point         #Save this point, it might become the start of the next poly
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
            #mt.diffuse_shader = 'MINNAERT'
            #mat.diffuse_color = (0.0, 0.0, 0.200)
            #mat.darkness = 0.8
        
        s.frame_end = len(layers)
        # hide everything at frame 0
                
        for i in range(len(layers)):
            print('setting material/visibility for layer '+str(i)+' of '+str(len(layers)))
            for j in layers[i]:
                j.hide = True
                j.hide_render = True
                j.keyframe_insert(data_path="hide",frame=0)
                j.keyframe_insert(data_path="hide_render",frame=0)
                # assign the material 
                j.active_material = mt
                
        
        # go through the layers and make them reappear
        for i in range(len(layers)):
            #s.frame_set(i)
            print('frame '+str(i)+' of '+str(len(layers)))
            for j in layers[i]:
                j.hide = False
                j.hide_render = False
                j.keyframe_insert(data_path="hide",frame=i)
                j.keyframe_insert(data_path="hide_render",frame=i)


class machine:
    
    extruder = False
    extrusion_height = 5
    extrusion_width = 5
    
    printStarted = False

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
                st = split1[0]
            if startcommentidx > 0:   # line has an embedded comment to remove
                split1=st.partition('(')
                split2=split1[2].partition(')')
                st = split1[0]+split2[2]
            #Do nothing if startcommentidx is -1 (not found)
            if st != '':    
                tempd.append(st)
            #print("Cleaned out comment and left: ",st)
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
        self.commands.append(layer()) #Make a new first layer
        
        for i in self.axes:
            pos[i] = 0
            self.cur[i] = 0 #init
        for i in self.data: #get data
            i = i.strip() #clean (Is there a better way?)
            print( "Parsing Gcode line ", i)
            #print('pos: ' + pos)
            if i == '':
                continue
            tmp = i.split()
            command = tmp[0][0]
            com_type = tmp[0][1:]
            
            if command in codes:
                if com_type in codes[command]:
                    if (command != '('):
                        #We have a GCode (Not a skeinforge command)
                        #Run the usual checks
                        print('good com =>'+command+com_type)
                    
                        for j in tmp[1:]:
                            axis = j[0]
                            if axis == ';':
                                # ignore comments
                                break
                            if axis in self.axes:
                                val = float(j[1:])
                                pos[axis] = val
#                                if machine.buildStarted == True: #HACK! If we're in a build...
#                                    
#                                    if self.cur['Z'] < pos['Z']:
#                                        #This should never happen. The GCode just told us to move to a lower position!
#                                        #GCode generator FAIL!
#                                        #Throw a tantrum in the log but don't add a ghost layer
#                                        
#                                        #NOTE: This may be due to wipe or other commands. Might I suggest some sort of layer reset command?
#                                        #This line might make the visualizer 'ratchet' up unless a reset command is implemented.
#                                        print('!!Just recieved a move with a Z height LESS than a previous move! You trying to make the printer DIG man??')
#                                        print('Discarding idiotic layer command')
#                                    
#                                    elif self.cur['Z'] != pos['Z']:
#                                        self.commands.append(layer())
#                                        self.commands.append(tool_off(pos))
#                                        self.cur[axis] = val
                                            
                        # create action object
                        #print(pos)
                        if com_type == '101':
                            machine.extruder = True
                            print('Extruder ON')
                    
                        elif com_type == '103':
                            machine.extruder = False
                            print('Extruder OFF')
                                
                        elif (machine.extruder == False):
                            act = tool_off(pos)
                            print('made move with extruder OFF')
                            self.commands.append(act)
                        else:
                            #We got an extruded move command!
                            
                            #Check if this extrusion is the start of a new layer
                            if self.cur['Z'] > pos['Z']:
                                #This should never happen. The GCode just told us to move to a lower position!
                                #GCode generator FAIL!
                                #Throw a tantrum in the log but don't add a ghost layer
                                #                                        
                                #NOTE: This may be due to wipe or other commands. Might I suggest some sort of layer reset command?
                                #This line might make the visualizer 'ratchet' up unless a reset command is implemented.
                                print('!!Just recieved a extrusion move with a Z height LESS than a previous move! You trying to make the printer DIG man??')
                                print('Discarding idiotic layer command')
                                                                    
                            elif self.cur['Z'] != pos['Z']:
                                self.commands.append(layer())
                                #self.commands.append(tool_off(pos))
                                for index in self.axes:
                                    self.cur[index] = pos[index]
                            
                            act = codes[command][com_type](pos)
                            print('made move with extruder ON')
                            self.commands.append(act)
                    else:
                        #We have a skeinforge command
                        #Run the skeinforge command
                        print('Good Skeinforge com => '+command+com_type)
                        codes [command] [com_type] (tmp[1])
                else:
                    print(i)
                    print(' G/M/T Code for this line is unknowm ' + com_type)
            
            else:
                print(' line does not have a G/M/T Command '+ str(command))


def import_gcode(file_name):
    print('hola')
    m = machine(['X','Y','Z'])
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

class IMPORT_OT_gcode(bpy.types.Operator):
    '''Imports Reprap FDM gcode'''
    bl_idname = "import_scene.gocde"
    bl_description = 'Gcode reader, reads tool moves and animates layer build'
    bl_label = "Import gcode" +' v.'+ __version__
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    filepath = StringProperty(name="File Path", description="Filepath used for importing the GCode file", maxlen= 1024, default= "")

    #new_scene = BoolProperty(name="Replace scene", description="Replace scene", default=toggle&T_NewScene)
    #new_scene = BoolProperty(name="New scene", description="Create new scene", default=toggle&T_NewScene)
    #curves = BoolProperty(name="Draw curves", description="Draw entities as curves", default=toggle&T_Curves)
    #thic_on = BoolProperty(name="Thic ON", description="Support THICKNESS", default=toggle&T_ThicON)
#
 #   merge = BoolProperty(name="Remove doubles", description="Merge coincident vertices", default=toggle&T_Merge)
 #   mergeLimit = FloatProperty(name="Limit", description="Merge limit", default = theMergeLimit*1e4,min=1.0, soft_min=1.0, max=100.0, soft_max=100.0)

 #   draw_one = BoolProperty(name="Merge all", description="Draw all into one mesh-object", default=toggle&T_DrawOne)
 #   circleResolution = IntProperty(name="Circle resolution", description="Circle/Arc are aproximated will this factor", default = theCircleRes,
 #               min=4, soft_min=4, max=360, soft_max=360)
 #   codecs = tripleList(['iso-8859-15', 'utf-8', 'ascii'])
 #   codec = EnumProperty(name="Codec", description="Codec",  items=codecs, default = 'ascii')

 #   debug = BoolProperty(name="Debug", description="Unknown DXF-codes generate errors", default=toggle&T_Debug)
 #   verbose = BoolProperty(name="Verbose", description="Print debug info", default=toggle&T_Verbose)

    ##### DRAW #####
    def draw(self, context):
        layout0 = self.layout
        #layout0.enabled = False

        #col = layout0.column_flow(2,align=True)
#        layout = layout0.box()
#        col = layout.column()
#        #col.prop(self, 'KnotType') waits for more knottypes
#        #col.label(text="import Parameters")
#        #col.prop(self, 'replace')
#        col.prop(self, 'new_scene')
#        
#        row = layout.row(align=True)
#        row.prop(self, 'curves')
#        row.prop(self, 'circleResolution')
#
#        row = layout.row(align=True)
#        row.prop(self, 'merge')
#        if self.merge:
#            row.prop(self, 'mergeLimit')
 
#        row = layout.row(align=True)
        #row.label('na')
#        row.prop(self, 'draw_one')
#        row.prop(self, 'thic_on')
#
#        col = layout.column()
#        col.prop(self, 'codec')
# 
#        row = layout.row(align=True)
#        row.prop(self, 'debug')
#        if self.debug:
#            row.prop(self, 'verbose')
#         
    def execute(self, context):
        global toggle, theMergeLimit, theCodec, theCircleRes
        #O_Merge = T_Merge if self.properties.merge else 0
        #O_Replace = T_Replace if self.properties.replace else 0
        #O_NewScene = T_NewScene if self.properties.new_scene else 0
        #O_Curves = T_Curves if self.properties.curves else 0
        #O_ThicON = T_ThicON if self.properties.thic_on else 0
        #O_DrawOne = T_DrawOne if self.properties.draw_one else 0
        #O_Debug = T_Debug if self.properties.debug else 0
        #O_Verbose = T_Verbose if self.properties.verbose else 0

        #toggle =  O_Merge | O_DrawOne | O_NewScene | O_Curves | O_ThicON | O_Debug | O_Verbose
        #theMergeLimit = self.properties.mergeLimit*1e-4
        #theCircleRes = self.properties.circleResolution
        #theCodec = self.properties.codec

        import_gcode(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func(self, context):
    self.layout.operator(IMPORT_OT_gcode.bl_idname, text="Reprap GCode (.gcode)", icon='PLUGIN')

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func)
 
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()

