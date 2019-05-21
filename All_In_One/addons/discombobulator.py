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
    "name": "Discombobulator",
    "description": "Its job is to easily add scifi details to a surface to create nice-looking space-ships or futuristic cities.",
    "author": "Chichiri",
    "version": (0,1),
    "blender": (2, 5, 9),
    "api": 39631,
    "location": "Spacebar > Discombobulate",
    "warning": 'Beta',
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"\
        "Scripts/My_Script",
    "tracker_url": "http://projects.blender.org/tracker/index.php?"\
        "func=detail&aid=<number>",
    "category": "Learnbgame"
}
 
import bpy
import bmesh
import random
import mathutils
import math
 
doprots = True
 
# Datas in which we will build the new discombobulated mesh
nFaces = []
nVerts = []
Verts = []
Faces = []
dVerts = []
dFaces = []
i_prots = [] # index of the top faces on whow we will generate the doodads
i_dood_type = [] # type of doodad (given by index of the doodad obj)
 
bpy.types.Scene.DISC_doodads = []

def randnum(a, b):
    return random.random()*(b-a)+a
 
def randVertex(a, b, c, d, Verts):
    ''' return a vector of a random vertex on a quad-face'''
    i = random.randint(1,2)
    A, B, C, D = 0, 0, 0, 0
    if(a==1):
        A, B, C, D = a, b, c, d
    else:
        A, B, C, D = a, d, c, b
   
    i = randnum(0.1, 0.9)
   
    vecAB = [Verts[B][0]-Verts[A][0], Verts[B][1]-Verts[A][1], Verts[B][2]-Verts[A][2]]
    E = [Verts[A][0]+vecAB[0]*i, Verts[A][1]+vecAB[1]*i, Verts[A][2]+vecAB[2]*i]
   
    vecDC = [Verts[C][0]-Verts[D][0], Verts[C][1]-Verts[D][1], Verts[C][2]-Verts[D][2]]
    F = [Verts[D][0]+vecDC[0]*i, Verts[D][1]+vecDC[1]*i, Verts[D][2]+vecDC[2]*i]
   
    i = randnum(0.1, 0.9)
    vecEF = [F[0]-E[0], F[1]-E[1], F[2]-E[2]]
    O = [E[0]+vecEF[0]*i, E[1]+vecEF[1]*i, E[2]+vecEF[2]*i]
    return O
 
################################ Protusions ###################################
 
def fill_older_datas(verts, face):
    ''' Specifically coded to be called by the function addProtusionToFace, its sets up a tuple which contains the vertices from the base and the top of the protusions. '''
    temp_vertices = []  
    temp_vertices.append(list(verts[face[0]]))
    temp_vertices.append(list(verts[face[1]]))
    temp_vertices.append(list(verts[face[2]]))
    temp_vertices.append(list(verts[face[3]]))
    temp_vertices.append(list(verts[face[0]]))
    temp_vertices.append(list(verts[face[1]]))
    temp_vertices.append(list(verts[face[2]]))
    temp_vertices.append(list(verts[face[3]]))
    return temp_vertices
   
def extrude_top(temp_vertices, normal, height):
    ''' This function extrude the face composed of the four first members of the tuple temp_vertices along the normal multiplied by the height of the extrusion.'''
    j = 0
    while j < 3:  
        temp_vertices[0][j]+=list(normal)[j]*height
        temp_vertices[1][j]+=list(normal)[j]*height
        temp_vertices[2][j]+=list(normal)[j]*height
        temp_vertices[3][j]+=list(normal)[j]*height
        j+=1
 
def scale_top(temp_vertices, obface, normal, height, scale_ratio):
    ''' This function scale the face composed of the four first members of the tuple temp_vertices. '''
    vec1 = [0, 0, 0]
    vec2 = [0, 0, 0]
    vec3 = [0, 0, 0]
    vec4 = [0, 0, 0]
   
    j = 0
    while j < 3:
        obface[j]+=list(normal)[j]*height
        vec1[j] = temp_vertices[0][j] - obface[j]
        vec2[j] = temp_vertices[1][j] - obface[j]
        vec3[j] = temp_vertices[2][j] - obface[j]
        vec4[j] = temp_vertices[3][j] - obface[j]
        temp_vertices[0][j] = obface[j] + vec1[j]*(1-scale_ratio)
        temp_vertices[1][j] = obface[j] + vec2[j]*(1-scale_ratio)
        temp_vertices[2][j] = obface[j] + vec3[j]*(1-scale_ratio)
        temp_vertices[3][j] = obface[j] + vec4[j]*(1-scale_ratio)
        j+=1
 
def add_prot_faces(temp_vertices):
    ''' Specifically coded to be called by addProtusionToFace, this function put the data from the generated protusion at the end the tuples Verts and Faces, which will later used to generate the final mesh. '''
    global Verts
    global Faces
    global i_prots
   
    findex = len(Verts)
    Verts+=temp_vertices
   
    facetop = [findex+0, findex+1, findex+2, findex+3]
    face1 = [findex+0, findex+1, findex+5, findex+4]
    face2 = [findex+1, findex+2, findex+6, findex+5]
    face3 = [findex+2, findex+3, findex+7, findex+6]
    face4 = [findex+3, findex+0, findex+4, findex+7]
   
    Faces.append(facetop)
    i_prots.append(len(Faces)-1)
    Faces.append(face1)
    Faces.append(face2)
    Faces.append(face3)
    Faces.append(face4)
       
def addProtusionToFace(obface, verts, minHeight, maxHeight, minTaper, maxTaper):
    '''Create a protusion from the face "obface" of the original object and use several values sent by the user. It calls in this order the following functions:
       - fill_older_data;
       - extrude_top;
       - scale_top;
       - add_prot_faces;
   '''
    # some useful variables
    face = tuple(obface.vertices)
    facetop = face
    face1 = []
    face2 = []
    face3 = []
    face4 = []
    vertices = []
    tVerts = list(fill_older_datas(verts, face)) # list of temp vertices
    height = randnum(minHeight, maxHeight) # height of generated protusion
    scale_ratio = randnum(minTaper, maxTaper)
   
    # extrude the top face
    extrude_top(tVerts, obface.normal, height)
    # Now, we scale, the top face along its normal
    scale_top(tVerts, obface.vertices, obface.normal, height, scale_ratio)
    # Finally, we add the protusions to the list of faces
    add_prot_faces(tVerts)
 
################################## Divide a face ##################################
 
def divide_one(list_faces, list_vertices, verts, face, findex):
    ''' called by divide_face, to generate a face from one face, maybe I could simplify this process '''
    temp_vertices = []
    temp_vertices.append(list(verts[face[0]]))
    temp_vertices.append(list(verts[face[1]]))
    temp_vertices.append(list(verts[face[2]]))
    temp_vertices.append(list(verts[face[3]]))
   
    list_vertices+=temp_vertices
       
    list_faces.append([findex+0, findex+1, findex+2, findex+3])
   
def divide_two(list_faces, list_vertices, verts, face, findex):
    ''' called by divide_face, to generate two faces from one face and add them to the list of faces and vertices which form the discombobulated mesh'''
    temp_vertices = []
    temp_vertices.append(list(verts[face[0]]))
    temp_vertices.append(list(verts[face[1]]))
    temp_vertices.append(list(verts[face[2]]))
    temp_vertices.append(list(verts[face[3]]))
    temp_vertices.append([(verts[face[0]][0]+verts[face[1]][0])/2, (verts[face[0]][1]+verts[face[1]][1])/2, (verts[face[0]][2]+verts[face[1]][2])/2])
    temp_vertices.append([(verts[face[2]][0]+verts[face[3]][0])/2, (verts[face[2]][1]+verts[face[3]][1])/2, (verts[face[2]][2]+verts[face[3]][2])/2])
       
    list_vertices+=temp_vertices
       
    list_faces.append([findex+0, findex+4, findex+5, findex+3])
    list_faces.append([findex+1, findex+2, findex+5, findex+4])
   
def divide_three(list_faces, list_vertices, verts, face, findex, obface):
    ''' called by divide_face, to generate three faces from one face and add them to the list of faces and vertices which form the discombobulated mesh'''
    temp_vertices = []
    temp_vertices.append(list(verts[face[0]]))
    temp_vertices.append(list(verts[face[1]]))
    temp_vertices.append(list(verts[face[2]]))
    temp_vertices.append(list(verts[face[3]]))
    temp_vertices.append([(verts[face[0]][0]+verts[face[1]][0])/2, (verts[face[0]][1]+verts[face[1]][1])/2, (verts[face[0]][2]+verts[face[1]][2])/2])
    temp_vertices.append([(verts[face[2]][0]+verts[face[3]][0])/2, (verts[face[2]][1]+verts[face[3]][1])/2, (verts[face[2]][2]+verts[face[3]][2])/2])
    temp_vertices.append([(verts[face[1]][0]+verts[face[2]][0])/2, (verts[face[1]][1]+verts[face[2]][1])/2, (verts[face[1]][2]+verts[face[2]][2])/2])
    temp_vertices.append(list(obface.normal))
       
    list_vertices+=temp_vertices
       
    list_faces.append([findex+0, findex+4, findex+5, findex+3])
    list_faces.append([findex+1, findex+6, findex+7, findex+4])
    list_faces.append([findex+6, findex+2, findex+5, findex+7])
 
def divide_four(list_faces, list_vertices, verts, face, findex, center):
    ''' called by divide_face, to generate four faces from one face and add them to the list of faces and vertices which form the discombobulated mesh'''
    temp_vertices = []
    temp_vertices.append(list(verts[face[0]]))
    temp_vertices.append(list(verts[face[1]]))
    temp_vertices.append(list(verts[face[2]]))
    temp_vertices.append(list(verts[face[3]]))
    temp_vertices.append([(verts[face[0]][0]+verts[face[1]][0])/2, (verts[face[0]][1]+verts[face[1]][1])/2, (verts[face[0]][2]+verts[face[1]][2])/2])
    temp_vertices.append([(verts[face[2]][0]+verts[face[3]][0])/2, (verts[face[2]][1]+verts[face[3]][1])/2, (verts[face[2]][2]+verts[face[3]][2])/2])
    temp_vertices.append([(verts[face[1]][0]+verts[face[2]][0])/2, (verts[face[1]][1]+verts[face[2]][1])/2, (verts[face[1]][2]+verts[face[2]][2])/2])
    temp_vertices.append(list(center))
    temp_vertices.append([(verts[face[0]][0]+verts[face[3]][0])/2, (verts[face[0]][1]+verts[face[3]][1])/2, (verts[face[0]][2]+verts[face[3]][2])/2])
    temp_vertices.append(list(center))
   
    list_vertices+=temp_vertices
       
    list_faces.append([findex+0, findex+4, findex+7, findex+8])
    list_faces.append([findex+1, findex+6, findex+7, findex+4])
    list_faces.append([findex+6, findex+2, findex+5, findex+7])
    list_faces.append([findex+8, findex+7, findex+5, findex+3])
   
def divideface(obface, verts, number):
    '''Divide the face into the wanted number of faces'''
    global nFaces
    global nVerts
#    centre = sum((obface.vertices[a].co for a in obface.vertices), obface())
#    centre /= len(obface.vertices)
    face = tuple(obface.vertices)
    tVerts = []
   
    if(number==1):
        divide_one(nFaces, nVerts, verts, face, len(nVerts))
    elif(number==2):
        divide_two(nFaces, nVerts, verts, face, len(nVerts))
    elif(number==3):
        divide_three(nFaces, nVerts, verts, face, len(nVerts), obface.normal)      
    elif(number==4):
        divide_four(nFaces, nVerts, verts, face, len(nVerts), obface.normal)    
   
############################### Discombobulate ################################
 
def division(obfaces, verts, sf1, sf2, sf3, sf4):
    '''Function to divide each of the selected faces'''
    divide = []
    if(sf1): divide.append(1)
    if(sf2): divide.append(2)
    if(sf3): divide.append(3)
    if(sf4): divide.append(4)
    for face in obfaces:
        if(face.select == True):
            a = random.randint(0, len(divide)-1)
            divideface(face, verts, divide[a])
 
def protusion(obverts, obfaces, minHeight, maxHeight, minTaper, maxTaper):
    '''function to generate the protusions'''
    verts = []
    for vertex in obverts:
        verts.append(tuple(vertex.co))
           
    for face in obfaces:
        if(face.select == True):
            if(len(face.vertices) == 4):
                addProtusionToFace(face, verts, minHeight, maxHeight, minTaper, maxTaper)
 
def test_v2_near_v1(v1, v2):
    if(v1.x - 0.1 <= v2.x <= v1.x + 0.1
        and v1.y - 0.1 <= v2.y <= v1.y + 0.1
        and v1.z - 0.1 <= v2.z <= v1.z + 0.1):
        return True
   
    return False
 
def angle_between_nor(nor_orig, nor_result):
    angle = math.acos(nor_orig.dot(nor_result))
    axis = nor_orig.cross(nor_result).normalized()
   
    q = mathutils.Quaternion()
    q.x = axis.x*math.sin(angle/2)
    q.y = axis.y*math.sin(angle/2)
    q.z = axis.z*math.sin(angle/2)
    q.w = math.cos(angle/2)
   
    return q
 
def doodads(object1, mesh1, dmin, dmax):
    '''function to generate the doodads'''
    global dVerts
    global dFaces
    i = 0
    # on parcoure cette boucle pour ajouter des doodads a toutes les faces
    while(i<len(object1.data.polygons)):
        doods_nbr = random.randint(dmin, dmax)
        j = 0
        while(j<=doods_nbr):
            origin_dood = mathutils.Vector(randVertex(object1.data.polygons[i].vertices[0], object1.data.polygons[i].vertices[1], object1.data.polygons[i].vertices[2], object1.data.polygons[i].vertices[3], Verts))
            type_dood = random.randint(0, len(bpy.types.Scene.DISC_doodads)-1)
            faces_add = []
            verts_add = []
           
            # First we have to apply scaling and rotation to the mesh
            bpy.ops.object.select_pattern(pattern=bpy.types.Scene.DISC_doodads[type_dood],extend=False)
            bpy.context.scene.objects.active=bpy.data.objects[bpy.types.Scene.DISC_doodads[type_dood]]
            bpy.ops.object.transform_apply(rotation=True, scale=True)
           
            for face in bpy.data.objects[bpy.types.Scene.DISC_doodads[type_dood]].data.polygons:
                faces_add.append(tuple(face.vertices))
            for vertex in bpy.data.objects[bpy.types.Scene.DISC_doodads[type_dood]].data.vertices:
                verts_add.append(vertex.co.copy())
            normal_original_face = object1.data.polygons[i].normal
           
            nor_def = mathutils.Vector((0.0, 0.0, 1.0))
            qr = nor_def.rotation_difference(normal_original_face.normalized())
           
            case_z = False
            if(test_v2_near_v1(nor_def, -normal_original_face)):
                case_z = True
                qr = mathutils.Quaternion((0.0, 0.0, 0.0, 0.0))
            #qr = angle_between_nor(nor_def, normal_original_face)
            for vertex in verts_add:
                vertex.rotate(qr)
                vertex+=origin_dood
            findex = len(dVerts)
            for face in faces_add:
                dFaces.append([face[0]+findex, face[1]+findex, face[2]+findex, face[3]+findex])
                i_dood_type.append(bpy.data.objects[bpy.types.Scene.DISC_doodads[type_dood]].name)
            for vertex in verts_add:
                dVerts.append(tuple(vertex))
            j+=1
        i+=5
       
def protusions_repeat(object1, mesh1, r_prot):
    i = 2
    while(i<r_prot):
        # Here we select the top faces stored in i_prots
        bpy.ops.object.select_pattern(pattern = object1.name,extend=False)
        bpy.context.scene.objects.active=bpy.data.objects[object1.name]
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.wm.context_set_value(data_path="tool_settings.mesh_select_mode", value="(False, False, True)")
        for j in i_prots:
            object1.data.faces[j].select = True
        bpy.ops.object.mode_set(mode='OBJECT')
        i+=1
 
# add material to discombobulated mesh
def setMatProt(discObj, origObj, sideProtMat, topProtMat):
    # First we put the materials in their slots
    bpy.ops.object.select_pattern(pattern = discObj.name,extend=False)
    bpy.context.scene.objects.active=bpy.data.objects[discObj.name]
    try:
        origObj.material_slots[topProtMat]
        origObj.material_slots[sideProtMat]
    except:
        return
        
    bpy.ops.object.material_slot_add()
    bpy.ops.object.material_slot_add()
    discObj.material_slots[0].material = origObj.material_slots[topProtMat].material
    discObj.material_slots[1].material = origObj.material_slots[sideProtMat].material
   
    # Then we assign materials to protusions
    for face in discObj.data.faces:
        if face.index in i_prots:
            face.material_index = 0
        else:
            face.material_index = 1
 
def setMatDood(doodObj):
    # First we add the materials slots
    bpy.ops.object.select_pattern(pattern = doodObj.name,extend=False)
    bpy.context.scene.objects.active=bpy.data.objects[doodObj.name]
    for name in bpy.types.Scene.DISC_doodads:
        try:
            bpy.ops.object.material_slot_add()
            doodObj.material_slots[-1].material = bpy.data.objects[name].material_slots[0].material
            for face in doodObj.data.faces:
                if i_dood_type[face.index] == name:
                    face.material_index = len(doodObj.material_slots)-1
                    print(len(doodObj.material_slots)-1)
        except:
            print()
           
           
 
def discombobulate(minHeight, maxHeight, minTaper, maxTaper, sf1, sf2, sf3, sf4, dmin, dmax, r_prot, sideProtMat, topProtMat):
    global doprots
    global nVerts
    global nFaces
    global Verts
    global Faces
    global dVerts
    global dFaces
    global i_prots
   
    bpy.ops.object.mode_set(mode="OBJECT")
    # Create the discombobulated mesh
    mesh = bpy.data.meshes.new("tmp")
    object = bpy.data.objects.new("tmp", mesh)
    bpy.context.scene.objects.link(object)
   
    # init final verts and faces tuple
    nFaces = []
    nVerts = []
    Faces = []
    Verts = []
    dFaces = []
    dVerts = []
   
    origObj = bpy.context.active_object
   
    # There we collect the rotation, translation and scaling datas from the original mesh
    to_translate = bpy.context.active_object.location
    to_scale     = bpy.context.active_object.scale
    to_rotate    = bpy.context.active_object.rotation_euler
   
    # First, we collect all the informations we will need from the previous mesh        
    obverts = bpy.context.active_object.data.vertices
    obfaces = bpy.context.active_object.data.polygons
    verts = []
    for vertex in obverts:
        verts.append(tuple(vertex.co))
   
    division(obfaces, verts, sf1, sf2, sf3, sf4)
       
    # Fill in the discombobulated mesh with the new faces
    mesh.from_pydata(nVerts, [], nFaces)
    mesh.update(calc_edges = True)
   
   
    # Reload the datas
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.object.select_pattern(pattern = object.name,extend=False)
    bpy.context.scene.objects.active=bpy.data.objects[object.name]
    obverts = bpy.context.active_object.data.vertices
    obfaces = bpy.context.active_object.data.polygons
   
    protusion(obverts, obfaces, minHeight, maxHeight, minTaper, maxTaper)
   
    # Fill in the discombobulated mesh with the new faces
    mesh1 = bpy.data.meshes.new("discombobulated_object")
    object1 = bpy.data.objects.new("discombobulated_mesh", mesh1)
    bpy.context.scene.objects.link(object1)
    mesh1.from_pydata(Verts, [], Faces)
    mesh1.update(calc_edges = True)
   
    # Set the material's of discombobulated object
    setMatProt(object1, origObj, sideProtMat, topProtMat)
   
    bpy.ops.object.select_pattern(pattern = object1.name,extend=False)
    bpy.context.scene.objects.active=bpy.data.objects[object1.name]
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
   
    if(bpy.types.Scene.repeatprot):
        protusions_repeat(object1, mesh1, r_prot)
   
    if(len(bpy.types.Scene.DISC_doodads) != 0):
        doodads(object1, mesh1, dmin, dmax)
        mesh2 = bpy.data.meshes.new("dood_mesh")
        object2 = bpy.data.objects.new("dood_obj", mesh2)
        bpy.context.scene.objects.link(object2)
        mesh2.from_pydata(dVerts, [], dFaces)
        mesh2.update(calc_edges = True)
        setMatDood(object2)
        object2.location        = to_translate
        object2.rotation_euler  = to_rotate
        object2.scale           = to_scale
 
    bpy.ops.object.select_pattern(pattern = object.name,extend=False)
    bpy.context.scene.objects.active=bpy.data.objects[object.name]
    bpy.ops.object.delete()
   
    # translate, scale and rotate discombobulated results
    object1.location        = to_translate
    object1.rotation_euler  = to_rotate
    object1.scale           = to_scale
 
############ Operator to select and deslect an object as a doodad ###############
 
class chooseDoodad(bpy.types.Operator):
    bl_idname = "object.discombobulate_set_doodad"
    bl_label = "Discombobulate set doodad object"
   
    def execute(self, context):
        bpy.context.scene.DISC_doodads.append(bpy.context.active_object.name)
       
    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}
 
class unchooseDoodad(bpy.types.Operator):
    bl_idname = "object.discombobulate_unset_doodad"
    bl_label = "Discombobulate unset doodad object"
   
    def execute(self, context):
        for name in bpy.context.scene.DISC_doodads:
            if name == bpy.context.active_object.name:
                bpy.context.scene.DISC_doodads.remove(name)
               
    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}
 
################################## Interface ####################################
 
class discombobulator(bpy.types.Operator):
    bl_idname = "object.discombobulate"
    bl_label = "Discombobulate"
    bl_options = {'REGISTER', 'UNDO'}    
   
    def execute(self, context):
        scn = context.scene
        discombobulate(scn.minHeight, scn.maxHeight, scn.minTaper, scn.maxTaper, scn.subface1, scn.subface2, scn.subface3, scn.subface4, scn.mindoodads, scn.maxdoodads, scn.repeatprot, scn.sideProtMat, scn.topProtMat)
        return {'FINISHED'}
 
class VIEW3D_PT_tools_discombobulate(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
 
    bl_label = "Discombobulator"
    bl_context = "objectmode"
 
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("object.discombobulate", text = "Discombobulate")
        box = layout.box()
        box.label("Protusions settings")
        row = box.row()
        row.prop(context.scene, 'doprots')
        row = box.row()
        row.prop(context.scene, 'minHeight')
        row = box.row()
        row.prop(context.scene, 'maxHeight')
        row = box.row()
        row.prop(context.scene, 'minTaper')
        row = box.row()
        row.prop(context.scene, 'maxTaper')
        row = box.row()
        col1 = row.column(align = True)
        col1.prop(context.scene, "subface1")
        col2 = row.column(align = True)
        col2.prop(context.scene, "subface2")
        col3 = row.column(align = True)
        col3.prop(context.scene, "subface3")
        col4 = row.column(align = True)
        col4.prop(context.scene, "subface4")
        row = box.row()
        row.prop(context.scene, "repeatprot")
        box = layout.box()
        box.label("Doodads settings")
        row = box.row()
        row.prop(context.scene, 'dodoodads')
        row = box.row()
        row.prop(context.scene, "mindoodads")
        row = box.row()
        row.prop(context.scene, "maxdoodads")
        row = box.row()
        row.operator("object.discombobulate_set_doodad", text = "Pick doodad")
        row = box.row()
        row.operator("object.discombobulate_unset_doodad", text = "Remove doodad")
        col = box.column(align = True)
        for name in bpy.context.scene.DISC_doodads:
            col.label(text = name)
        box = layout.box()
        box.label("Materials settings")
        row = box.row()
        row.prop(context.scene, 'topProtMat')
        row = box.row()
        row.prop(context.scene, "sideProtMat")
        row = box.row()
           
# registering and menu integration
def register():
    # Protusions Buttons:
    bpy.types.Scene.repeatprot = bpy.props.IntProperty(name="Repeat protusions", description="make several layers of protusion", default = 1, min = 1, max = 10)
    bpy.types.Scene.doprots = bpy.props.BoolProperty(name="Make protusions", description = "Check if we want to add protusions to the mesh", default = True)
    bpy.types.Scene.faceschangedpercent = bpy.props.FloatProperty(name="Face %", description = "Percentage of changed faces", default = 1.0)
    bpy.types.Scene.minHeight = bpy.props.FloatProperty(name="Min height", description="Minimal height of the protusions", default=0.2)
    bpy.types.Scene.maxHeight = bpy.props.FloatProperty(name="Max height", description="Maximal height of the protusions", default = 0.4)
    bpy.types.Scene.minTaper = bpy.props.FloatProperty(name="Min taper", description="Minimal height of the protusions", default=0.15, min = 0.0, max = 1.0, subtype = 'PERCENTAGE')
    bpy.types.Scene.maxTaper = bpy.props.FloatProperty(name="Max taper", description="Maximal height of the protusions", default = 0.35, min = 0.0, max = 1.0, subtype = 'PERCENTAGE')
    bpy.types.Scene.subface1 = bpy.props.BoolProperty(name="1", default = True)
    bpy.types.Scene.subface2 = bpy.props.BoolProperty(name="2", default = True)
    bpy.types.Scene.subface3 = bpy.props.BoolProperty(name="3", default = True)
    bpy.types.Scene.subface4 = bpy.props.BoolProperty(name="4", default = True)
   
    # Doodads buttons:
    bpy.types.Scene.dodoodads = bpy.props.BoolProperty(name="Make doodads", description = "Check if we want to generate doodads", default = True)
    bpy.types.Scene.mindoodads = bpy.props.IntProperty(name="Minimum doodads number", description = "Ask for the minimum number of doodads to generate per face", default = 1, min = 0, max = 50)
    bpy.types.Scene.maxdoodads = bpy.props.IntProperty(name="Maximum doodads number", description = "Ask for the maximum number of doodads to generate per face", default = 6, min = 1, max = 50)
    bpy.types.Scene.doodMinScale = bpy.props.FloatProperty(name="Scale min", description="Minimum scaling of doodad", default = 0.5, min = 0.0, max = 1.0, subtype = 'PERCENTAGE')
    bpy.types.Scene.doodMaxScale = bpy.props.FloatProperty(name="Scale max", description="Maximum scaling of doodad", default = 1.0, min = 0.0, max = 1.0, subtype = 'PERCENTAGE')
   
    # Materials buttons:
    bpy.types.Scene.sideProtMat = bpy.props.IntProperty(name="Side's prot mat", description = "Material of protusion's sides", default = 0, min = 0)
    bpy.types.Scene.topProtMat = bpy.props.IntProperty(name = "Prot's top mat", description = "Material of protusion's top", default = 0, min = 0)
   
    bpy.utils.register_class(discombobulator)
    bpy.utils.register_class(chooseDoodad)
    bpy.utils.register_class(unchooseDoodad)
    bpy.utils.register_class(VIEW3D_PT_tools_discombobulate)
 
# unregistering and removing menus
def unregister():
    bpy.utils.unregister_class(discombobulator)
    bpy.utils.unregister_class(chooseDoodad)
    bpy.utils.unregister_class(unchooseDoodad)
    bpy.utils.unregister_class(VIEW3D_PT_tools_discombobulate)
 
if __name__ == "__main__":
    register()