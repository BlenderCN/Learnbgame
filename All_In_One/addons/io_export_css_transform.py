"""
Copyright (C) 2009-2012 James S Urquhart (contact@jamesu.net)

This program is free software; you can redistribute it and/or modify it 
under the terms of the GNU General Public License as published by the 
Free Software Foundation; either version 2 of the License, 
or (at your option) any later version.

This program is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License 
along with this program; if not, write to the 
Free Software Foundation, Inc., 59 Temple Place, 
Suite 330, Boston, MA 02111-1307 USA
"""

bl_info = {
    "name": "CSS Transform Export (.html)",
    "description": "Magically Exports to HTML&CSS Transform",
    "author": "James Urquhart",
    "version": (1, 0),
    "blender": (2, 6, 0),
    "location": "File > Export > CSS Transform (.html)",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "https://github.com/jamesu/csstransformexport",
    "tracker_url": "https://github.com/jamesu/csstransformexport",
    "category": "Learnbgame"
}

import os
import time
import bpy
import mathutils
import random
import operator
import math
import string

from bpy.props import *    

# NOTE: Keyframes only interpolate between individual keys, i.e. values don't
#       interpolate across the entire animation.

# BEGIN TEMPLATES

WEBKIT_TPL = """
<html>
<head>
<title>%(title)s</title>
<style>%(style)s</style>
<link href=\"%(track_path)s.css\" rel=\"stylesheet\" type=\"text/css\"/>
<link href=\"%(track_path)s.overrides.css\" rel=\"stylesheet\" type=\"text/css\"/>
</head>
<body>
<div id=\"root\">%(scene)s</div>
</body>
</html>
"""

TRACKS_TPL = """
/* Animation keyframes */
%(content)s
"""

# END TEMPLATES

def initSceneProperties(scn):
	bpy.types.Scene.cssexportanimtrackonly = BoolProperty(
	    name="Only Export Animation Track",
	    description="Only export CSS tracks",
	    default=False)

	bpy.types.Scene.cssexportanimloop = BoolProperty(
	    name="Loop Animation",
	    description="Loop Animation",
	    default=True)

	bpy.types.Scene.cssexportbakeanim = BoolProperty(
	    name="Bake Animation",
	    description="Sample animation each frame (interpolation will be forced to linear)",
	    default=True)

	bpy.types.Scene.cssexport3d = BoolProperty(
	    name="Export 3D",
	    description="Incorporates Z axis and camera perspective",
	    default=False)

	bpy.types.Scene.cssexportswitchaxis = BoolProperty(
	    name="Switch Axis",
	    description="Switch Z and Y axes (useful if incoporating simulated physics)",
	    default=False)

	bpy.types.Scene.cssexportcollapsetransforms = BoolProperty(
	    name="Collapse Transforms",
	    description="Use world space transforms instead of relying on parent-child transforms. Buggy with anims.",
	    default=False)

	bpy.types.Scene.cssexportanimfps = IntProperty(
	    name="Override FPS",
	    description="Override FPS",
	    default=0)

	bpy.types.Scene.cssexportglobalscale = FloatProperty(
    name="Global Scale",
    description="Global Scale",
    default=1.0)

initSceneProperties(bpy.context.scene)

bpy.context.scene.cssexportcollapsetransforms = False
bpy.context.scene.cssexport3d = False
bpy.context.scene.cssexportswitchaxis = False


# Export action



class ExportCSSData(bpy.types.Operator):
    global exportmessage
    bl_idname = "export_scene.css_html"
    bl_label = "Export CSS Transform"
    __doc__ = """Exports scene to a CSS Transform animation"""

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.

    filepath = StringProperty(
            subtype='FILE_PATH',
            )
    filter_glob = StringProperty(
            default="*.html",
            options={'HIDDEN'},
            )

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        doExport(self.filepath, context)
        
        return {'FINISHED'}
        
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


# Lookups

InterpolationLookup = {
	'CONSTANT' : 'linear',
	'LINEAR': 'linear',
	'BEZIER': 'bezier'
}

# Util

import os.path

 
# Gets base path with trailing /
def basepath(filepath):
	if "\\" in filepath: sep = "\\"
	else: sep = "/"
	words = filepath.split(sep)
	# join drops last word (file name)
	return sep.join(words[:-1])

class Bitfield:
	INT_WIDTH=32
	
	def __init__(self, size):
		self.size = int(size)
		self.field = [0] * int(math.ceil(float(self.size) / Bitfield.INT_WIDTH))
	
	def __setitem__(self, position, value):
		if value:
			self.field[int(position) // Bitfield.INT_WIDTH] |= 1 << (int(position) % Bitfield.INT_WIDTH)
		elif self.field[int(position) // Bitfield.INT_WIDTH] & 1 << (int(position) % Bitfield.INT_WIDTH) > 0:
			self.field[int(position) // Bitfield.INT_WIDTH] ^= 1 << (int(position) % Bitfield.INT_WIDTH)
	
	def __getitem__(self, position):
		try:
			if self.field[int(position) // Bitfield.INT_WIDTH] & 1 << (int(position) % Bitfield.INT_WIDTH) > 0:
				return 1
			else:
				return 0
		except:
			return 0
	
	def dump(self):
		out = []
		for item in self.field:
			st = map(lambda y:str((item>>y)&1), range(Bitfield.INT_WIDTH-1, -1, -1))
			st.reverse()
			out.append("".join(st))
		return (''.join(out))
		
	# e.g. [0,0,1,1,0,0].setFrom([1,1,1,1,1,1], -6) == [1,1,1,1,1,1,0,0,1,1,0,0]
	def setFrom(self, other, offset):
		pos = other.size + offset
		new_size = self.size
		start_pos = 0
		if pos > new_size:
			# Expand
			new_size = pos
		if offset < 0:
			new_size += -offset
			start_pos = -offset
		
		new_field = Bitfield(new_size)
		# Copy existing
		for i in range(start_pos, start_pos+self.size):
			new_field[i] = self[i-start_pos]
		# Copy new
		for i in range(offset, offset+other.size):
			if not new_field[i]:
				new_field[i] = other[i-offset]
		return new_field

# Helper class for CSS transforms
class SimpleTransform:
	MATTERS_LOCX=1<<0
	MATTERS_LOCY=1<<1
	MATTERS_LOCZ=1<<2
	
	MATTERS_LOC2D = MATTERS_LOCX | MATTERS_LOCY
	MATTERS_LOC3D = MATTERS_LOCX | MATTERS_LOCY | MATTERS_LOCZ
	
	MATTERS_ROTX=1<<3
	MATTERS_ROTY=1<<4
	MATTERS_ROTZ=1<<5
	
	MATTERS_ROT3D = MATTERS_ROTX | MATTERS_ROTY | MATTERS_ROTZ
	
	MATTERS_SCLX=1<<6
	MATTERS_SCLY=1<<7
	MATTERS_SCLZ=1<<8
	
	MATTERS_SCL2D = MATTERS_SCLX | MATTERS_SCLY
	MATTERS_SCL3D = MATTERS_SCLX | MATTERS_SCLY | MATTERS_SCLZ
	
	# Global scaling
	GLOBAL_SCALE = 10.0
	
	def __init__(self):
		self.matters = 0
		self.loc = [0,0,0]
		self.rot = [0,0,0]
		self.scl = [0,0,0]
		
		self.is3D = False
	
	def setLocation(self, x, y, z):
		if x != None and x != self.loc[0]:
			self.matters |= SimpleTransform.MATTERS_LOCX
			self.loc[0] = x
		if y != None and y != self.loc[1]:
			self.matters |= SimpleTransform.MATTERS_LOCY
			self.loc[1] = y
		if z != None and z != self.loc[2]:
			self.matters |= SimpleTransform.MATTERS_LOCZ
			self.loc[2] = z
	
	def setRotation(self, x, y, z):
		if x != None and x != self.rot[0]:
			self.matters |= SimpleTransform.MATTERS_ROTX
			self.rot[0] = x
		if y != None and y != self.rot[1]:
			self.matters |= SimpleTransform.MATTERS_ROTY
			self.rot[1] = y
		if z != None and z != self.rot[2]:
			self.matters |= SimpleTransform.MATTERS_ROTZ
			self.rot[2] = z
	
	def setScale(self, x, y, z):
		if x != None and x != self.scl[0]:
			self.matters |= SimpleTransform.MATTERS_SCLX
			self.scl[0] = x
		if y != None and y != self.scl[1]:
			self.matters |= SimpleTransform.MATTERS_SCLY
			self.scl[1] = y
		if z != None and z != self.scl[2]:
			self.matters |= SimpleTransform.MATTERS_SCLZ
			self.scl[2] = z
	
	def transformValue(self, threedee=False):
		string = ""
		list = []
		
		# Location
		if threedee and self.matters & SimpleTransform.MATTERS_LOC3D == SimpleTransform.MATTERS_LOC3D:
			list.append("translate3d(%fpx, %fpx, %fpx)" % (self.loc[0], self.loc[1], self.loc[2]))
		elif self.matters & SimpleTransform.MATTERS_LOC2D == SimpleTransform.MATTERS_LOC2D:
			list.append("translate(%fpx, %fpx)" % (self.loc[0], self.loc[1]))
		else:
			if self.matters & SimpleTransform.MATTERS_LOCX:
				list.append("translateX(%fpx)" % self.loc[0])
			if self.matters & SimpleTransform.MATTERS_LOCY:
				list.append("translateY(%fpx)" % self.loc[1])
			if threedee and self.matters & SimpleTransform.MATTERS_LOCZ:
				list.append("translateZ(%fpx)" % self.loc[2])
		
		# Rotation
		# TODO: rotate3d()
		if threedee:
			if self.matters & SimpleTransform.MATTERS_ROTX:
				list.append("rotateX(%frad)" % -self.rot[0])
			if self.matters & SimpleTransform.MATTERS_ROTY:
				list.append("rotateY(%frad)" % -self.rot[1])
			if self.matters & SimpleTransform.MATTERS_ROTZ:
				list.append("rotateZ(%frad)" % -self.rot[2])
		else:
			if self.matters & SimpleTransform.MATTERS_ROTZ:
				list.append("rotate(%frad)" % -self.rot[2])
		
		# Scale
		if threedee and self.matters & SimpleTransform.MATTERS_SCL3D == SimpleTransform.MATTERS_SCL3D:
			list.append("scale3d(%f, %f, %f)" % (self.scl[0], self.scl[1], self.scl[2]))
		elif self.matters & SimpleTransform.MATTERS_SCL2D == SimpleTransform.MATTERS_SCL2D:
			list.append("scale(%f, %f)" % (self.scl[0], self.scl[1]))
		else:
			if self.matters & SimpleTransform.MATTERS_SCLX:
				list.append("scaleX(%f)" % self.scl[0])
			if self.matters & SimpleTransform.MATTERS_SCLY:
				list.append("scaleY(%f)" % self.scl[1])
			if threedee and self.matters & SimpleTransform.MATTERS_SCLZ:
				list.append("scaleZ(%f)" % self.scl[2])
		
		return " ".join(list)

def scaleVA(arr, scale):
	return [x*scale for x in arr]
	
class SimpleObject:
	def __init__(self, obj, scene):
		self.name = obj.name.replace(".", "__")
		self.obj = obj
		self.parent = None
		self.children = []
		self.anim = None
		self.material = None
		self.transformOrigin = None
		self.scene = scene
		
		if obj.type == 'MESH':
			self.mesh = obj.data
		else:
			self.mesh = None

		if self.mesh != None:
			mat_list = obj.material_slots
			if len(mat_list) > 0:
				self.material = mat_list[0].material
		
	def importIpo(self, ipo):
		anim = SimpleAnim(self)
		anim.grabAllFrameTimes(ipo)
		self.anim = anim
		return anim
	
	def blenderChildren(self):
		return [obj for obj in self.scene.objects if obj.parent == self.obj ]
	
	def getTransform(self):
		mat = self.obj.matrix_local
		# Handle collapsed transforms
		if self.scene.cssexportcollapsetransforms:
			mat = self.obj.matrix_world
			#mat = parentMat * mat
		
		loc = scaleVA(mat.to_translation(), SimpleTransform.GLOBAL_SCALE)
		rot = mat.to_euler()
		scl = mat.to_scale()
		
		trans = SimpleTransform()

		#print("[%i] %s getLocation: %f %f %f" % (bpy.context.scene.frame_current, self.obj.name, loc[0], -loc[1], loc[2]))
		#print("[%i] %s getRotation: %f %f %f" % (bpy.context.scene.frame_current, self.obj.name, rot[0], rot[1], rot[2]))

		if self.scene.cssexportswitchaxis:
			trans.setLocation(loc[0], -loc[2], loc[1])
			trans.setRotation(rot[0], rot[2], rot[1])
			trans.setScale(scl[0], scl[2], scl[1])
		else:
			trans.setLocation(loc[0], -loc[1], loc[2])
			trans.setRotation(rot[0], rot[1], rot[2])
			trans.setScale(scl[0], scl[1], scl[2])
		
		return trans
	
	def getUVBounds(self):
		msh = self.mesh

		mshuv = None
		for uv in msh.uv_textures:
			if uv.active:
				mshuv = uv.data
				break

		if msh != None and mshuv:
			minp = [10e30,10e30]
			maxp = [-10e30,-10e30]
			
			uvcoords = []
			for f in mshuv:
				for uv in f.uv:
					uvcoords.append(tuple(uv))
			for pos in uvcoords:
				for i in range(0,2):
					if pos[i] < minp[i]:
						minp[i] = pos[i]
					if pos[i] > maxp[i]:
						maxp[i] = pos[i]
			return minp, maxp

		return [0.0, 0.0], [1.0, 1.0]
	
	def getBounds(self):
		msh = self.mesh
		if msh != None:
			minp = [10e30,10e30,10e30]
			maxp = [-10e30,-10e30,-10e30]
			
			for v in msh.vertices:
				pos = v.co
				for i in range(0,3):
					if pos[i] < minp[i]:
						minp[i] = pos[i]
					if pos[i] > maxp[i]:
						maxp[i] = pos[i]
			return scaleVA(minp, SimpleTransform.GLOBAL_SCALE), scaleVA(maxp, SimpleTransform.GLOBAL_SCALE)

		box = obj.bound_box
		return scaleVA(min(box), SimpleTransform.GLOBAL_SCALE), scaleVA(max(box), SimpleTransform.GLOBAL_SCALE)
	
	def getWorldCenter(self):
		if self.parent != None:
			center = self.parent.getWorldCenter()
		else:
			center = [0,0,0]
		center[0] += self.center[0]
		center[1] += self.center[1]
		center[2] += self.center[2]
		return center

class SimpleAnim:
	def __init__(self, obj):
		self.object = obj
		self.identifier = obj.name + '-anim'
		self.matters = None
		self.interpolation = None
		self.animates_layer = False
		self.frames = None # generated frames
		self.propertyInterpolation = {}
		self.start = 0
		self.len = 0
	
	def encompassesFrame(self, fid):
		if fid >= self.start and fid < self.start+self.len:
			return True
		return False
	
	def setPropertyInterpolationTypes(self):
		for interpolation in self.interpolation:
			if interpolation != None:
				self.propertyInterpolation["TRANSFORM"] = interpolation
				break
	
	def combineFrom(self, other):
		#print "COMBINING %s with %s" % (self.identifier, other.identifier)
		self.matters = self.matters.setFrom(other.matters, 0)
		
		# Fit start,len
		if other.start < self.start:
			self.len += self.start - other.start
			self.start = other.start
		sEnd = self.start + self.len
		oEnd = other.start + other.len
		if oEnd > sEnd:
			self.len += oEnd - sEnd
		
		for key in other.propertyInterpolation.keys():
			if not key in self.propertyInterpolation.keys():
				self.propertyInterpolation[key] = other.propertyInterpolation[key]
	
	def grabAllFrameTimes(self, ipo):
		frames = {}
		
		checkList = ['location', 'scale', 'rotation_euler', 'layer']

		#print("ANIM: %s" % ipo.name)
		curveFrameList = []
		for fcurve in ipo.fcurves:
			# Determine frame times for this curve
			curveFrames = self.getFrameTimes(fcurve)
			if curveFrames != None:
				print("CURVEFRAMELIST: %i, start=%i, end=%i" % (len(curveFrames['frames']), curveFrames['start'], curveFrames['end']))
				curveFrameList.append(curveFrames)
		
		# Combine all
		earliest, latest = tuple(ipo.frame_range)  # e.g. 1, 2
		numFrames = int(((latest+1) - earliest)) # e.g. 1, 2 == 2

		#print("NUMBER OF FRAMES = %i, START == %i" % (numFrames, earliest))
		
		for frameList in curveFrameList:
			self.combineFrameTimes(frameList, earliest, latest, frames)
		
		framesList = list(frames.values())
		framesList = sorted(framesList, key=lambda a:a[0])
		
		self.matters = Bitfield(latest+1)
		self.interpolation = list(map(lambda x:None, range(int(latest)+1)))
		for frame in framesList:
			self.matters[frame[0]] = 1 # NOTE: frame 0 will be ignored
			self.interpolation[frame[0]] = frame[1]
		
		#print "\tSTART=%i,END=%d,LEN=%d" % (earliest, latest, numFrames)
		self.start = earliest    # e.g. 1
		self.len = numFrames     # e.g. 2 [1,2]
		self.setPropertyInterpolationTypes()
	
	def combineFrameTimes(self, frames, startFrame, endFrame, outList):
		fl = endFrame - startFrame
		for frame in frames["frames"]:
			percent = float(frame[0]-startFrame) / fl  # e.g. 1-1 / 2-1 == 0; 2-1 / 2-1 == 1.0
			key = ("%2.2f" % (percent*100)) + "%"
			if not key in outList:
				outList[key] = [int(frame[0]), frame[2]]
	
	def getFrameTimes(self, curve):
		if curve == None:
			return None
		
		# time, value
		fr = list(map(lambda f: [f.co[0], f.co[1], f.interpolation], curve.keyframe_points))
		return {"frames":fr, 
				"start": fr[0][0],
				"end": fr[-1][0]}
	
	# Calculates overall start & stop time
	def getFrameTimeBounds(self, list):
		earliest = 99999999
		latest = -1
		
		for f in list:
			if f["start"] < earliest:
				earliest = f["start"]
			if f["end"] > latest:
				latest = f["end"]
			
		return earliest, latest

def importObjects(olist, out_list, anims_list, scene, parent=None):
	for obj in olist:
		#print("IMPORTING OBJECT: %s %s" % (obj.name, obj.type))
		obj_parent = obj.parent
		if (parent == None and obj_parent != None) or (parent != None and obj_parent != parent.obj):
			continue
		
		if obj.type != "MESH" and obj.type != "EMPTY":
			continue
		
		ipo = obj.animation_data
		built_object = SimpleObject(obj, scene)
		
		if ipo != None and ipo.action != None and len(ipo.action.fcurves) != 0:
			#print("Importing curve for %s" % obj.name)
			anims_list.append(built_object.importIpo(ipo.action))
		
		# Insert into correct list
		if parent != None:
			built_object.parent = parent
			parent.children.append(built_object)
		else:
			out_list.append(built_object)
		
		# Recurse
		importObjects(built_object.blenderChildren(), out_list, anims_list, scene, built_object)

def halfOf(p1, p2):
	x = (p2[0] - p1[0]) * 0.5
	y = (p2[1] - p1[1]) * 0.5
	z = (p2[2] - p1[2]) * 0.5
	return [x, y, z]
	
def exportObjects(olist, doc, style, scene):
	threedee = scene.cssexport3d
	fps = None
	if scene.cssexportanimfps == 0.0:
		fps = scene.render.fps
	else:
		fps = scene.cssexportanimfps

	for obj in olist:
		#print("EXPORTING OBJECT %s" % obj.obj.name)
		# Actual div
		doc.append("<div id=\"%s\">" % obj.name)
		
		# CSS
		style.append("#%s {\n" % obj.name)
		
		if obj.mesh != None:
			minb, maxb = obj.getBounds()
			
			# Problem: we need to fix the origin of the HTML element. 
			#          -webkit-transform-origin only works for rotation and scaling.
			# Solution:
			#          use left and top to offset element center instead,
			#          taking into account the origin is by default at the center
			# e.g. bound size = 64,64
			#      bound origin = 0,0
			#      webkit origin = 32,32
			#      left, top = -32, -32  (i.e. bound origin - webkit origin)
			halfSize = halfOf(minb, maxb)
			
			boundOrigin = [
			halfSize[0] + minb[0],
			halfSize[1] + minb[1],
			halfSize[2] + minb[2]]
			
			boundOrigin[1] = -boundOrigin[1] # scene is -y
			
			obj.center = [
			boundOrigin[0] - halfSize[0],
			boundOrigin[1] - halfSize[1],
			boundOrigin[2] - halfSize[2]]
			
			# transformOrigin to correct rotation and scaling
			obj.transformOrigin = [-obj.center[0], -obj.center[1]]
		else:
			obj.center = [0,0,0]
		
		#print "%s actual center=%s" % (obj.obj.getName(), str(obj.center))
		
		if not scene.cssexportcollapsetransforms and obj.parent != None:
			wc = obj.getWorldCenter()
			wc[0] -= obj.center[0]
			wc[1] -= obj.center[1]
			
			# Center needs to be expressed in parents coordinate system
			obj.center[0] = obj.center[0] - wc[0]
			obj.center[1] = obj.center[1] - wc[1]
		#
		#print "%s center=%s" % (obj.obj.getName(), str(obj.center))
		
		style.append("-webkit-transform: %s;\n" % obj.getTransform().transformValue(threedee))
		style.append("-moz-transform: %s;\n" % obj.getTransform().transformValue(threedee))
		
		if obj.mesh != None:
			style.append("width: %dpx;\n" % (maxb[0] - minb[0]))
			style.append("height: %dpx;\n" % (maxb[1] - minb[1]))
		style.append("left: %dpx;\n" % (obj.center[0]))
		style.append("top: %dpx;\n" % (obj.center[1]))
		if obj.transformOrigin != None:
			style.append("-webkit-transform-origin: %dpx %dpx;\n" % (obj.transformOrigin[0], obj.transformOrigin[1]))
			style.append("-moz-transform-origin: %dpx %dpx;\n" % (obj.transformOrigin[0], obj.transformOrigin[1]))
		
		if scene.cssexport3d:
			style.append("-webkit-transform-style: preserve-3d;\n")
		
		# color, texture, etc
		if obj.material != None:
			# 
			mat = obj.material
			if not obj.material.transparency_method == 'Z_TRANSPARENCY':
				# color
				style.append("background-color: rgb(%d,%d,%d);\n" % (mat.diffuse_color[0] * 255, mat.diffuse_color[1] * 255, mat.diffuse_color[2] * 255))
				
			if mat.alpha < 1.0:
				style.append("opacity: %f;\n" % mat.alpha)
			
			# Use first texture slot to determine image background
			texSlot = mat.texture_slots[0]
			if texSlot != None:
				tex = texSlot.texture
				if tex != None and tex.type == 'IMAGE':
					# Dump & save
					img = tex.image
					if img != None:
						# Image file
						name = img.filepath
						style.append("background-image: url(\"%s.png\");\n" % bpy.path.ensure_ext(bpy.path.basename(name), ''))
						
						# Background position
						uv_min, uv_max = obj.getUVBounds()
						style.append("background-position: %i%% %i%%;\n" % (uv_min[0] * 100, uv_min[1] * 100))
						
						# Background scaling
						scale = [uv_max[0] - uv_min[0], 
						         uv_max[1] - uv_min[1]]
						
						# Calculate difference in image scale
						sz = img.size
						oWidth = sz[0] / (maxb[0] - minb[0])
						oHeight = sz[1] / (maxb[1] - minb[1])
						
						scale[0] = round(scale[0] * 100, 2)
						scale[1] = round(scale[1] * 100, 2)
						
						if oWidth != 1.0 or oHeight != 1.0:
							style.append("-webkit-background-size: %.2f%% %.2f%%;\n" % (scale[0], scale[1]))
							style.append("-moz-background-size: %.2f%% %.2f%%;\n" % (scale[0], scale[1]))
		
		# animation
		if obj.anim != None:
			anim = obj.anim
			
			duration = anim.len / fps
			delay = (anim.start-1) / fps
			
			style.append("-webkit-animation-name: %s;\n" % anim.identifier)
			style.append("-webkit-animation-duration: %fs;\n" % duration)
			style.append("-webkit-animation-delay: %fs;\n" % delay)
			
			if scene.cssexportanimloop:
				style.append("-webkit-animation-iteration-count: infinite;\n")
			if scene.cssexportbakeanim:
				style.append("-webkit-animation-timing-function: linear;\n")
			
		style.append("}\n")
		
		# Children are part of element
		if not scene.cssexportcollapsetransforms:
			exportObjects(obj.children, doc, style, scene)
		
		doc.append("</div>\n")
		
		# Children are part of root
		if scene.cssexportcollapsetransforms:
			exportObjects(obj.children, doc, style, scene)

def exportWebkit(objects, anims, scene, filename):
	# Second step: output webkit stuff
	doc = []
	style = ["#root div {position: absolute;}\n",
	         "#root {background-color: #eeeeee; position: absolute; width:640px; height: 480px;"]
	
	# 3D Needs to have a perspective and origin
	# TODO: some form of logical calculation using a camera
	if scene.cssexport3d:
		style.append("-webkit-perspective: %i; " % (70))
		style.append("-webkit-perspective-origin: center 240px;")
	style.append("}\n")
	
	exportObjects(objects, doc, style, scene)
	
	className = bpy.path.ensure_ext(bpy.path.basename(filename), '')
	classPath = basepath(str(filename))
	animName = "%s-%s" % (className, scene.name) 
	doBake = scene.cssexportbakeanim
	
	tracks = []
	# Animation keyframes
	for anim in anims:
		tracks.append("@-webkit-keyframes %s {\n" % anim.identifier)
		
		earliest = anim.start
		fl = anim.len-1
		frames = anim.frames
		for frame in frames:
			# e.g. two frames 1 2
			# (1 - 1) / 2 = 0%
			# (2 - 1) / 2 = 100%
			percent = float(frame[0] - earliest) / fl
			fid = ("%2.2f" % (percent*100)) + "%"
			
			tracks.append("%s {\n" % fid)
			tracks.append("-webkit-transform: %s;\n" % frame[1].transformValue(scene.cssexport3d))
			if anim.animates_layer:
				if frame[3]:
					tracks.append("visibility: hidden;\n")
				else:
					tracks.append("visibility: visible;\n")	
			if not doBake:
				tracks.append("-webkit-animation-timing-function: %s;\n" % InterpolationLookup[frame[2]])
			tracks.append("}\n")
		
		tracks.append("}\n")
	
	substitutions = {'title': className, 'style': "".join(style), 'track_path':animName, 'scene': "".join(doc)}
	css_substitutions = {'content': "".join(tracks)}
	
	# Dump tracks
	fs = open("%s/%s.css" % (classPath, animName), "w")
	fs.write(TRACKS_TPL % css_substitutions)
	fs.close()
	
	# Dump to document
	if not scene.cssexportanimtrackonly:
		fs = open("%s/%s.html" % (classPath, className), "w")
		fs.write(WEBKIT_TPL % substitutions)
		fs.close()

# Recursively makes sure child elements have anim tracks (for collapsed transforms)
def recursiveAnimClone(obj, new_anims):
	parent = obj.parent
	if parent != None and parent.anim != None:
		if obj.anim == None:
			obj.anim = SimpleAnim(obj)
			obj.anim.matters = Bitfield(parent.anim.matters.size)
			new_anims.append(obj.anim)
		obj.anim.combineFrom(parent.anim)
	
	for child in obj.children:
		recursiveAnimClone(child, new_anims)

def doExport(filePath, context):
	scene = context.scene
	
	ctx = scene.render
	
	objects = []
	anims = []

	SimpleTransform.GLOBAL_SCALE = scene.cssexportglobalscale
	
	scene.frame_set(1)
	
	# Import objects and frame times
	importObjects(scene.objects, objects, anims, scene)
	
	# Collapse transforms if neccesary
	if scene.cssexportcollapsetransforms:
		new_anims = []
		for anim in anims:
			recursiveAnimClone(anim.object, new_anims)
		anims += new_anims
	
	# Clear anim frames
	for anim in anims:
		anim.frames = []
	
	doBake = scene.cssexportbakeanim
	
	# Grab frames for all anims
	for fid in range(scene.frame_start, scene.frame_end):
		scene.frame_set(fid)
		scene.update()
		
		for anim in anims:
			if anim.matters[fid] or (doBake and anim.encompassesFrame(fid)):
				# TODO: grab material color, etc
				interpolation = None
				try:
					interpolation = anim.propertyInterpolation["TRANSFORM"]
				except:
					interpolation = "linear"
				
				if doBake:
					interpolation = "linear"
				layer_20 = 20 in anim.object.obj.layers
				anim.frames.append([fid, anim.object.getTransform(), interpolation, layer_20])
	
	exportWebkit(objects, anims, scene, filePath)

def menu_func(self, context):
    default_path = os.path.splitext(bpy.data.filepath)[0] + ".html"
    self.layout.operator(ExportCSSData.bl_idname, text="Export CSS Transform (.html)").filepath = default_path

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()
