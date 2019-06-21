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

def writeUnityComponent():

	# Currently select object. (Should be the billboard shape.)
	#ob = bpy.context.object
	scene = bpy.context.scene
	t = scene.gs_template
	ob = bpy.context.scene.objects[t.billboard_object]

	#obj_active = bpy.context.scene.objects.active
	scene = bpy.context.scene
	fName = "BillboardBaker.cs"
	fPath = os.path.join(scene.gs_billboard_path, fName)

	# Build a Unity Component file in C#.
	with open("{tpath}".format(tpath=fPath), "w") as file:
		
		# C# includes
		c_includes = ["System.Collections","System.Collections.Generic","System.IO","UnityEditor","UnityEngine"]
		for ci in range(len(c_includes)):
			file.write("using {inc};\n".format(inc=c_includes[ci]))
		
		# file header and class setup
		file.write("\nnamespace gamesolids\n{\n")
		file.write("\tpublic class BillboardBaker : MonoBehaviour\n\t{\n\t#if UNITY_EDITOR\n")
		file.write("\t\tpublic Material material;\n")
		file.write("\t\tpublic string nameOverride;\n\n")
		file.write("\t\t[ContextMenu(\"Bake Billboard\")]\n")
		file.write("\t\tpublic void BakeBillboard()\n\t\t{\n")
		file.write("\t\t\tBillboardAsset billboard = new BillboardAsset();\n\n")
		file.write("\t\t\tbillboard.material = material;\n")
		file.write("\t\t\tVector4[] texCoords = new Vector4[8];\n")
		file.write("\t\t\tushort[] indices = new ushort[12];\n")
		file.write("\t\t\tVector2[] vertices = new Vector2[6];\n\n")
		
		# Texture Coordinates from the UV map
		file.write("\t\t\t// TexCoords\n".format(ob=ob))
		tileWidth = 0.333
		tileHeight= 0.333
		tileStepX = 3
		tileStepY = 3
		texIndex = 0
		for y in range(0, tileStepY):
			for x in range(0, tileStepX):
				if texIndex < 8:
					print(texIndex)
					file.write("\t\t\ttexCoords[{0}].Set({1}f, {2}f, {3}f, {4}f);\n".format(texIndex, x*tileWidth, y*tileHeight, tileWidth, tileHeight))
					texIndex = texIndex+1
		
		file.write( "\n")
		
		# Order of indices from the UV loops
		file.write("\t\t\t// Indices\n".format(ob=ob))
		for face in ob.data.polygons:
			for loop_index in range(face.loop_start, face.loop_start + face.loop_total):
				file.write("\t\t\tindices[%r] =  %r;\n" % (loop_index, ob.data.loops[loop_index].vertex_index))
			
		file.write( "\n")
		
		# Vertices: unique ordered list
		file.write("\t\t\t// UVVerts \n".format(ob=ob))
		vList = []
		for face in ob.data.polygons:
			for loop in face.loop_indices:
				uv = ob.data.uv_layers.active.data[loop].uv
				vList.append(tuple(uv))
				
		vSet = set(vList)
		vList = list(vSet)
		vList.sort(key=itemgetter(0,1))
		for v in range(len(vList)):
			file.write("\t\t\tvertices[{v}].Set( {uv[0]}f, {uv[1]}f );\n".format(v=v, uv=vList[v]))

		file.write( "\n")
		
		# billboard settings
		billy = ["SetImageTexCoords(texCoords)","SetIndices(indices)","SetVertices(vertices)"]
		for bi in range(len(billy)):
			file.write("\t\t\tbillboard.{setting};\n".format(setting=billy[bi]))
		
		bdims = ob.dimensions
		file.write("\t\t\t//dimmensions of mesh in unscaled form?\n")
		file.write("\t\t\tbillboard.width = {0}f;\n".format(bdims[0]))
		file.write("\t\t\tbillboard.height = {0}f;\n".format(bdims[1]))
		file.write("\t\t\tbillboard.bottom = {0}f;\n\n".format(-0.50))
		
		# component options
		file.write("\t\t\t// build our asset path and name\n")
		file.write("\t\t\tstring path;\n")
		file.write("\t\t\tif (nameOverride != null && nameOverride != \"\")\n\t\t\t{\n")
		file.write("\t\t\t\tpath = Path.GetDirectoryName(AssetDatabase.GetAssetPath(material)) + Path.DirectorySeparatorChar + nameOverride + \".asset\";\n")
		file.write("\t\t\t}\n\t\t\telse\n\t\t\t{\n")
		file.write("\t\t\t\tpath = Path.GetDirectoryName(AssetDatabase.GetAssetPath(material)) + Path.DirectorySeparatorChar + material.name + \".asset\";\n")
		file.write("\t\t\t}\n")
		file.write("\t\t\t//create!\n")
		file.write("\t\t\tAssetDatabase.CreateAsset(billboard, path);\n")
		file.write("\t\t}\n\t\t#endif\n\t}\n}\n")

		# that should do it
		