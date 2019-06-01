'''
	*** Begin GPL License Block ***

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>
	or write to the Free Software Foundation,
	Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

	*** End GPL License Block ***
'''
''' (c)2018 GameSolids '''

import bpy, os
#from os import path
from operator import itemgetter


def dict2xml(d, root_node=None):
	''' dict2xml method thanks to: '''
	''' @author Reimund Trost 2013 '''
	''' https://gist.github.com/reimund/5435343/ '''
	wrap          =     False if None == root_node or isinstance(d, list) else True
	root          = 'objects' if None == root_node else root_node
	root_singular = root[:-1] if 's' == root[-1] and None == root_node else root
	xml           = ''
	children      = []

	if isinstance(d, dict):
		for key, value in dict.items(d):
			if isinstance(value, dict):
				children.append(dict2xml(value, key))
			elif isinstance(value, list):
				children.append(dict2xml(value, key))
			else:
				#change this line to textNode from attribute
				xml = xml + ' ' + key + '="' + str(value) + '"'
				#xml = xml + '<' + key + '>' + str(value) + '</' + key +'>'
	else:
		for value in d:
			children.append(dict2xml(value, root_singular))

	end_tag = '>' if 0 < len(children) else '/>'

	if wrap or isinstance(d, dict):
		xml = '<' + root + xml + end_tag

	if 0 < len(children):
		for child in children:
			xml = xml + child

		if wrap or isinstance(d, dict):
			xml = xml + '</' + root + '>'
		
	return xml


def writeXML():

	# Currently select object. (Should be the billboard shape.)
	#ob = bpy.context.object
	scene = bpy.context.scene
	t = scene.gs_template
	ob = bpy.context.scene.objects[t.billboard_object]
	treeDict = {}
	#obj_active = bpy.context.scene.objects.active
	scene = bpy.context.scene
	fName = scene.gs_settings.filename+".xml"
	fPath = os.path.join(scene.gs_billboard_path, fName)

	# Texture Coordinates from the UV map
	treeDict = {'basename':{}, 'texCoords':{'face':[],},'indices':{'index':[],},'vertices':{'vertex':[],},}

	tileWidth = 0.333
	tileHeight= 0.333
	tileStepX = 3
	tileStepY = 3
	for y in range(0, tileStepY):
		for x in range(0, tileStepX):
			treeDict['texCoords']['face'].append(
			{'top':x*tileWidth, 'left':y*tileHeight, 'width':tileWidth, 'height':tileHeight}
			)

	# Order of indices from the UV loops
	for face in ob.data.polygons:
		for loop_index in range(face.loop_start, face.loop_start + face.loop_total):
			#loop_index = loop_index if loop_index > 0 else "_0"
			treeDict['indices']['index'].append(
			{ "_"+str(loop_index) : ob.data.loops[loop_index].vertex_index }
			)
			
	# Vertices: unique ordered list
	vList = []
	for face in ob.data.polygons:
		for loop in face.loop_indices:
			uv = ob.data.uv_layers.active.data[loop].uv
			vList.append(tuple(uv))
			
	vSet = set(vList)
	vList = list(vSet)
	vList.sort(key=itemgetter(0,1))
	for v in range(len(vList)):
		treeDict['vertices']['vertex'].append(
		{ 'v': v, 'uv': vList[v] }
		)


	# Build a Unity Component file in C#.
	#file.write( "<basename>"+scene.gs_settings.filename+"</basename>\n" )
	with open("{tpath}".format( tpath=fPath ), "w" ) as file:
		file.write( "<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
		treeDict['basename'] = (scene.gs_settings.filename)
		file.write( dict2xml( treeDict, "billboard_data" ))

		# that should do it
		