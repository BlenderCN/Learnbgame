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

# Thanks to Simon Kirkby and David Anderson for their previous
# versions of this script!

import string,os
import mathutils

import bpy

extrusion_diameter = 0.4

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
    self.extrusion_amount = pos['E']

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
    '92': tool_off, # not sure what this is
    '90': setting
  },
  'M':{
    '01' : undef,
    '6' : undef,
    '101' : tool_on,
    '103' : undef,
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

    print('createing poly lines')
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
        if i.extrusion_amount > 0:
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

    self.data=f.readlines()
    f.close()
    self.remove_comments()

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

      if len(tmp) == 0:
        continue

      command = tmp[0][0]
      com_type = tmp[0][1:]

      if command == ';':
        continue

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

def load_gcode(file_name):
  m = machine(['X','Y','Z','F','E'])
  m.import_file(file_name)
  m.process()
  d = blender_driver()
  d.load_data(m.commands)
  d.drive()
  print('finished parsing... done')

def load(operator, context, filter_glob, filepath=""):
  load_gcode(filepath)

  return {'FINISHED'}
