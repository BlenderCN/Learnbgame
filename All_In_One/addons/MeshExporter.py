bl_info = {
	"name": "MeshGeometry", 
	"category": "Import-Export",
	"blender": (2, 7, 8),
    "location": "File > Export > NCL MeshGeometry (.msh)",
    "description": "Export mesh MeshGeometry (.msh)"
}

import bpy, struct, math, os, time
from bpy.props import *

def mesh_triangulate(me):
    mesh = me
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()

class vSkinEntry:
  weight = 0.0
  index = 0
	
class vSkinData:
  entries = []

  weights = []
  indices = []
  
  count = 0
  
  def __init__(self):
    self.weights = [0.0, 0.0, 0.0, 0.0]	
    self.indices = [0.0, 0.0, 0.0, 0.0]
    self.entries = []

  def AddData(self, index, weight):
    entry = vSkinEntry()
    entry.weight = weight
    entry.index = index
    self.entries.append(entry)
    #print("Vertex now has %i weights" % (len(self.entries)))

    if(self.count < 4): #we'll premptively fill up the results in case there's < 4 entries
      self.weights[self.count] = weight
      self.indices[self.count] = index
      self.count = self.count + 1
	
  def FinaliseData(self, i):
    if(len(self.entries) > 4): #we have to sort and reweight!
      print("Renormalising vertex %i with %i weights" % (i, len(self.entries)))
      self.entries = sorted(self.entries, key = lambda entry: entry.weight, reverse=True) ##sort into descending order

      weightAmount = 0
      for x in range(0,4):
        self.weights[x] = self.entries[x].weight
        self.indices[x] = self.entries[x].index
        weightAmount += self.entries[x].weight
		#Multiply up the chosen weights so they sum to 1
      weightRecip = 1.0 / weightAmount

      for x in range(0,4):
        self.weights[x] = self.weights[x] / weightAmount

class MeshData:
	start = 0
	end = 0
	
class vColour:
    rgba = []
	
    def __init__(self):
      self.rgba = [1.0, 1.0, 1.0, 1.0]	
	  
    def SetValues(self, r, g, b, a):
      self.rgba[0] = r;	  
      self.rgba[1] = g;
      self.rgba[2] = b;
      self.rgba[3] = a;
	  
class vPosition:
    xyz = []
    def __init__(self):
      self.xyz = [0.0, 0.0, 0.0]
	  
    def SetValues(self, x, y, z):
      self.xyz[0] = x;	  
      self.xyz[1] = y;
      self.xyz[2] = z;

class vTexCoord:
    uv = []
    def __init__(self):
      self.uv = [0.0, 0.0]
	  
    def SetValues(self, x,y):
      self.uv[0] = x;	  
      self.uv[1] = y;	
	
class vNormal:
    xyz = []
	
    def __init__(self):
      self.xyz = [0.0, 0.0, 0.0]
	    
    def SetValues(self, x,y,z):
      self.xyz[0] = x;	  
      self.xyz[1] = y;	
      self.xyz[2] = z;
	  
    def AddValues(self, other):
      self.xyz[0] = self.xyz[0] + other[0];	  
      self.xyz[1] = self.xyz[1] + other[1];	
      self.xyz[2] = self.xyz[2] + other[2];

    def Normalise(self):
      l = math.sqrt( (self.xyz[0]*self.xyz[0]) + (self.xyz[1]*self.xyz[1]) + (self.xyz[2]*self.xyz[2]) )
      if l > 0.0:
        self.xyz[0] = self.xyz[0] / l
        self.xyz[1] = self.xyz[1] / l  
        self.xyz[2] = self.xyz[2] / l  
	  
class ExportSettings:
  def __init__(self, filepath, triangulate):
    self.filepath = filepath
    self.triangulate = triangulate


def save_msh(settings):
  print("Saving as Mesh Geometry...")
  
  VPositions		= 1
  VNormals			= 2
  VTangents			= 4
  VColors			= 8
  VTex0				= 16
  VTex1				= 32
  VWeightValues		= 64
  VWeightIndices	= 128
  Indices			= 256
  BindPose			= 512
  Material			= 1024
  
  if len(bpy.data.scenes) == 0:
    print("No scenes?!")
	
  sce = bpy.data.scenes[0]
  
  meshDatas = []
  allMeshes = []
  armature = []
	
  if len(sce.objects) == 0:
    print("No objects?!")
	
  for obj in sce.objects:
    if obj.type == 'MESH':
      allMeshes.append(obj)
    if obj.type == 'ARMATURE':
      armature = obj
	  
  if len(allMeshes) == 0:
    print("No submeshes to export?!")
    return
  
  allVerts = []
  allIndices = []
  allUVs = []
  allNormals = []
  allColours = []
  allTangents = []
  
  allSkinData = []
    
  indexOffset = 0
  numMeshes = 0
  numChunks = 0
  
  doColours = False
  doUVs = False
  doNormals = False
  doSkins = False
  
  if armature != None:
    doSkins = True
  
  numChunks = 3 ##We always get positions,normals, and indices
  
  for mesh in allMeshes:
    if len(mesh.data.vertices) == 0:
      print("Submesh has no vertices!")
      continue
	  
    meshData = MeshData()
    meshDatas.append(meshData)
	  
    numMeshes+=1
    mesh_triangulate(mesh.data)
    
	
    for v in mesh.data.vertices:
      vert = vPosition()
      vert.SetValues(v.co.x, v.co.y, v.co.z)
      allVerts.append(vert)
      newNormal = vNormal()
      allNormals.append(newNormal)
	  
    for poly in mesh.data.polygons: 
      for vert in poly.vertices:
        allNormals[vert].AddValues(poly.normal)
        
    if(len(mesh.data.vertex_colors) > 0):
      doColours = True
	  
    if(len(mesh.data.uv_layers) > 0):
      doUVs = True
      mesh.data.calc_tangents()
	  
    for poly in mesh.data.polygons: 
      for vert in poly.vertices:
        allIndices.append(indexOffset + vert)
		
    indexOffset += len(mesh.data.vertices)
#Fill the colours/UVs arrays if necessary
  if doUVs == True:
    numChunks+=2 #UVs and tangents - can't have tangents without em!
    for i in allVerts:
      newUV = vTexCoord()
      allUVs.append(newUV)
      newTangent = vNormal()
      allTangents.append(newTangent)

  if doColours == True:
    numChunks+=1
    for i in allVerts:
      newColour = vColour()
      allColours.append(newColour)	
		
#Now that the arrays are set up	we can fill them up...
#Try the UVs first
  startVertex = 0
  for mesh in allMeshes:
    if len(mesh.data.vertices) == 0:
      continue
	  
    uv_layer = mesh.data.uv_layers[0].data
	
    for poly in mesh.data.polygons: 
      for loop_index in poly.loop_indices:
        vIndex = mesh.data.loops[loop_index].vertex_index
        allUVs[startVertex + vIndex].SetValues(uv_layer[loop_index].uv[0],uv_layer[loop_index].uv[1])
        allTangents[startVertex + vIndex].AddValues(mesh.data.loops[loop_index].tangent )

    startVertex += len(mesh.data.vertices)

#now try the Colours
  startVertex = 0
  for mesh in allMeshes:
    if len(mesh.data.vertices) == 0:
      continue
	  
    if(len(mesh.data.vertex_colors) > 0):
      i = 0
      for col in mesh.data.vertex_colors:
        allColours[startVertex +i].SetValues(col.color[0], col.color[1], col.color[2], col.color[3])
        i+=1
    startVertex += len(mesh.data.vertices)	
	
##The normals have to be normalised
  for normal in allNormals:
   normal.Normalise()

  for tangent in allTangents:
   tangent.Normalise()  
##If there's any weights etc to do, fill the arrays up 
  if doSkins:
    numChunks+=2 #indices and weights
    for i in allVerts:
      skinning = vSkinData()
      allSkinData.append(skinning)
	  
  skinVert = 0
  for mesh in allMeshes:
    if len(mesh.data.vertices) == 0:
      continue
    obj_group_names = [g.name for g in mesh.vertex_groups]
		
    boneID = 0	

    for v in mesh.data.vertices:
      for vg in v.groups:
        jointName = obj_group_names[vg.group]

        joint = []
        jointID = 0
        for bone in armature.pose.bones:
          if bone.name == jointName:
            joint = bone
            break
          jointID += 1

        if joint == [None]:
          print("Cant find joint %i" % jointName)
        else:
          if(skinVert + v.index > len(allSkinData)):
            print("Skin vertex %i is greater than skinData size %i" %(skinVert + v.index, len(allSkinData)))
          allSkinData[skinVert + v.index].AddData(jointID,vg.weight)
          #print("Adding weight to vertex %i" %(skinVert + v.index))
    skinVert += len(mesh.data.vertices)
        #print("jointName for this vert/index is %s" %jointName)
		
#All the arrays are filled up now, we can write them all out
  print("Exporting %i submeshes" % numMeshes)
  out = open(settings.filepath, 'w')
  out.write('MeshGeometry\n');
  out.write('%i\n' % 1)	#version
  out.write('%i\n' % numMeshes) #num meshes 
  out.write('%i\n' % len(allVerts))#this will be num vertices
  out.write('%i\n' % len(allIndices)) #this will be num indices
  out.write('%i\n' % numChunks)  #this will be the num chunks
   
  out.write('%i\n' % VPositions)
  for vert in allVerts:
    out.write( '%f %f %f\n' % (vert.xyz[0], vert.xyz[1], vert.xyz[2]) )
	  
  out.write('%i\n' % Indices)
  i = 0
  while i < len(allIndices):
    out.write( '%i %i %i' % (allIndices[i], allIndices[i+1], allIndices[i+2] ) )
    i += 3
    out.write('\n') 
	  
  out.write('%i\n' % VNormals)
  for normal in allNormals:
    out.write( '%f %f %f\n' % (normal.xyz[0], normal.xyz[1], normal.xyz[2]) )


		  
  if doUVs == True: 
    out.write('%i\n' % VTex0)
    for tex in allUVs:
      out.write( '%f %f\n' % (tex.uv[0], tex.uv[1]) )

    out.write('%i\n' % VTangents)
    for tangent in allTangents:
      out.write( '%f %f %f\n' % (tangent.xyz[0], tangent.xyz[1], tangent.xyz[2]) )

  if doColours == True:
    out.write('%i\n' % VColors)  
    for colour in allColours:
      out.write( '%f %f %f %f\n' % (colour.rgba[0], colour.rgba[1], colour.rgba[2], colour.rgba[3]) )
	  
  if doSkins == True:
    out.write('%i\n' % VWeightValues)
    i = 0
    for skinData in allSkinData:
      skinData.FinaliseData(i)
      i+=1
    for skinData in allSkinData:
      out.write( '%f %f %f %f\n' % (skinData.weights[0], skinData.weights[1], skinData.weights[2], skinData.weights[3]) )
    out.write('%i\n' % VWeightIndices)
    for skinData in allSkinData:
      out.write( '%i %i %i %i\n' % (skinData.indices[0], skinData.indices[1], skinData.indices[2], skinData.indices[3]) )
	  
  out.close()
	
  print("Finished saving mesh geometry!")

class ExportMsh(bpy.types.Operator):
  '''Export to .msh'''
  bl_idname = "export.msh"
  bl_label = 'Export MeshGeometry'
  filename_ext = ".msh"
    
  filepath    = StringProperty(name="File Path", description="Filepath for exporting", maxlen= 1024, default="")
  triangulate = BoolProperty(name="Triangulate", description="Transform all geometry to triangles",default=True)
  
  triangulate_property = True
  
  def execute(self, context):
    settings = ExportSettings(self.properties.filepath, self.properties.triangulate)
    save_msh(settings)
    return {'FINISHED'}
		
  def invoke(self, context, event):
    self.filepath = ""
    wm = context.window_manager
    wm.fileselect_add(self)
    return {'RUNNING_MODAL'}
		
  @classmethod
  def poll(cls, context):
    return context.active_object != None
		
def menu_func(self, context):
	self.layout.operator(ExportMsh.bl_idname, text="NCL MeshGeometry", icon='EXPORT')
	
def register():
    print("Registering MeshGeometry addon")
    bpy.utils.register_class(ExportMsh)
    bpy.types.INFO_MT_file_export.append(menu_func)
	
def unregister():
    print("Unregistering MeshGeometry addon")
    bpy.utils.unregister_class(ExportMsh)
    bpy.types.INFO_MT_file_export.remove(menu_func)
	
if __name__ == "__main__":
    register()