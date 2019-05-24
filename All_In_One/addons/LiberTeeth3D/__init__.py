bl_info = {
    "name": "LiberTeeth3D",
    "author": "Cicero Moraes e Graziane Olimpio",
    "version": (1, 0, 0),
    "blender": (2, 75, 0),
    "location": "View3D",
    "description": "Ortodontia no Blender",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
    }


import bpy
import fnmatch
import operator
import tempfile
from os.path import expanduser
import platform
import shutil
import subprocess
from math import sqrt

from .CriaSplintWeight import *

# ATUALIACAO DO SCRIPT

def LiberAtualizaScriptDef(self, context):

	if platform.system() == "Windows":

		arquivo = open('atualiza_liber.bat', 'w+')
		arquivo.writelines("""cd C:/OrtogOnBlender/Blender/2.78/scripts/addons && ^
rd /s /q LiberTeeth3D-master && ^
C:/OrtogOnBlender/Python27/python.exe -c "import urllib; urllib.urlretrieve ('https://github.com/cogitas3d/LiberTeeth3D/archive/master.zip', 'master.zip')" && ^
C:/OrtogOnBlender/7-Zip/7z x  master.zip && ^
del master.zip""")

		arquivo.close()

		subprocess.call('atualiza_liber.bat', shell=True)

	if platform.system() == "Linux":

		arquivo = open('Programs/OrtogOnBlender/atualiza_liber.sh', 'w+')
		arquivo.writelines("""cd $HOME/Downloads && rm -Rfv LiberTeeth3D-master* && \
if [ -f "master.zip" ]; then echo "tem arquivo" && rm master.zi*; fi && \
wget https://github.com/cogitas3d/LiberTeeth3D/archive/master.zip && \
rm -Rfv $HOME/.config/blender/2.78/scripts/addons/LiberTeeth3D-master && \
unzip master.zip && \
cp -Rv LiberTeeth3D-master $HOME/.config/blender/2.78/scripts/addons/""")

		arquivo.close()

		subprocess.call('chmod +x Programs/OrtogOnBlender/atualiza_liber.sh && Programs/OrtogOnBlender/atualiza_liber.sh', shell=True)
        

	if platform.system() == "Darwin":

		arquivo = open('atualiza_liber.sh', 'w+')
		arquivo.writelines("""cd $HOME/Downloads && rm -Rfv LiberTeeth3D-master* && \
if [ -f "master.zip" ]; then echo "tem arquivo" && rm master.zi*; fi && \
wget https://github.com/cogitas3d/LiberTeeth3D/archive/master.zip && \
rm -Rfv $HOME/Library/Application\ Support/Blender/2.78/scripts/addons/LiberTeeth3D-master && \
unzip master.zip && \
mv LiberTeeth3D-master $HOME/Library/Application\ Support/Blender/2.78/scripts/addons/""")

		arquivo.close()

		subprocess.call('chmod +x atualiza_liber.sh && ./atualiza_liber.sh', shell=True)

class LiberAtualizaScript(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.liber_atualiza_script"
    bl_label = "Atualiza Script"

    def execute(self, context):
        LiberAtualizaScriptDef(self, context)
        return {'FINISHED'}


def LiberArrumaCenaDef(self, context):

    context = bpy.context

    bpy.context.tool_settings.gpencil_stroke_placement_view3d = 'SURFACE'

    bpy.data.screens['Default'].areas[4].spaces[0].fx_settings.use_ssao = True
    bpy.data.screens['Default'].areas[4].spaces[0].fx_settings.ssao.factor = 7

    bpy.context.scene.frame_end = 100

    bpy.context.space_data.show_floor = False
    bpy.context.space_data.show_axis_x = False
    bpy.context.space_data.show_axis_y = False


class LiberArrumaCena(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.liber_arruma_cena"
    bl_label = "Arruma Cena"
    
    def execute(self, context):
        LiberArrumaCenaDef(self, context)
        return {'FINISHED'}


# IMPORTA CORTE

def ImportaCorteDef(self, context):

    context = bpy.context
    obj = context.active_object
    scn = context.scene

    if platform.system() == "Linux" or platform.system() == "Darwin":
        dirScript = bpy.utils.user_resource('SCRIPTS')
        
        blendfile = dirScript+"addons/LiberTeeth3D-master/objetos.blend"
        section   = "\\Group\\"
        object    = "ArcadaCorta"
        
    if platform.system() == "Windows":
        dirScript = 'C:/OrtogOnBlender/Blender/2.78/scripts/' 

        blendfile = dirScript+"addons/LiberTeeth3D-master/objetos.blend"
        section   = "\\Group\\"
        object    = "Group"

    filepath  = blendfile + section + object
    directory = blendfile + section
    filename  = object

    bpy.ops.wm.append(
        filepath=filepath, 
        filename=filename,
        directory=directory)

    bpy.context.space_data.show_relationship_lines = False


class ImportaCorte(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.importa_arcada_corte"
    bl_label = "Importa Arcada Corte"
    
    def execute(self, context):
        ImportaCorteDef(self, context)
        return {'FINISHED'}

# IMPORTA CORTE

def ImportaAlinhaArcadaDef(self, context):

    context = bpy.context
    obj = context.active_object
    scn = context.scene

    if platform.system() == "Linux" or platform.system() == "Darwin":
        dirScript = bpy.utils.user_resource('SCRIPTS')
        
        blendfile = dirScript+"addons/LiberTeeth3D-master/objetos.blend"
        section   = "\\Group\\"
        object    = "ArcadaReferencia"
        
    if platform.system() == "Windows":
        dirScript = 'C:/OrtogOnBlender/Blender/2.78/scripts/' 

        blendfile = dirScript+"addons/LiberTeeth3D-master/objetos.blend"
        section   = "\\Group\\"
        object    = "Group"

    filepath  = blendfile + section + object
    directory = blendfile + section
    filename  = object

    bpy.ops.wm.append(
        filepath=filepath, 
        filename=filename,
        directory=directory)

    bpy.context.space_data.show_relationship_lines = False


class ImportaAlinhaArcada(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.importa_alinha_arcada"
    bl_label = "Importa Arcada Corte"
    
    def execute(self, context):
        ImportaAlinhaArcadaDef(self, context)
        return {'FINISHED'}

# ALINHA ARCADA 2

def liberPosicionaEmpties():

    context = bpy.context    
    obj = context.active_object
    v0 = obj.data.vertices[0]
    v1 = obj.data.vertices[1]
    v2 = obj.data.vertices[2]

    co_final0 = obj.matrix_world * v0.co
    co_final1 = obj.matrix_world * v1.co
    co_final2 = obj.matrix_world * v2.co

    # now we can view the location by applying it to an object
    obj_empty0 = bpy.data.objects.new("Dist0", None)
    context.scene.objects.link(obj_empty0)
    obj_empty0.location = co_final0

    obj_empty1 = bpy.data.objects.new("Dist1", None)
    context.scene.objects.link(obj_empty1)
    obj_empty1.location = co_final1

    obj_empty2 = bpy.data.objects.new("Dist2", None)
    context.scene.objects.link(obj_empty2)
    obj_empty2.location = co_final2

def liberMedidaAtual():

    liberPosicionaEmpties()
    
    """ Retorna Média de Três Pontos """
    bpy.ops.object.select_all(action='DESELECT')
    a = bpy.data.objects['Dist0']
    b = bpy.data.objects['Dist1']
    c = bpy.data.objects['Dist2']
    a.select = True
    b.select = True
    c.select = True
    l = []
    for item in bpy.context.selected_objects:
        l.append(item.location)

    distancia1 = sqrt( (l[0][0] - l[2][0])**2 + (l[0][1] - l[2][1])**2 + (l[0][2] - l[2][2])**2)
    distancia2 = sqrt( (l[1][0] - l[2][0])**2 + (l[1][1] - l[2][1])**2 + (l[1][2] - l[2][2])**2)
    distancia3 = sqrt( (l[1][0] - l[0][0])**2 + (l[1][1] - l[0][1])**2 + (l[1][2] - l[0][2])**2)

    print(distancia1)
    print(distancia2)
    print(distancia3)
    
    medidaAtual = max(distancia1, distancia2, distancia3)
#    medidaAtual = min(distancia1, distancia2, distancia3)
    print("A distância menor é:")
    print(medidaAtual)

    medidaReal = float(bpy.context.scene.medida_real)
    print(medidaReal)

    global fatorEscala 
    fatorEscala = medidaReal / medidaAtual
    print(fatorEscala)


# Alinha 2

def AlinhaArcada2Def(self, context):

    liberMedidaAtual()
    
    bpy.ops.object.select_all(action='DESELECT')
    c = bpy.data.objects['Rosto.001']
    bpy.context.scene.objects.active = c
    
    context = bpy.context
    obj = context.active_object
    scn = context.scene

    bpy.ops.object.editmode_toggle() #entra edit mode 
    bpy.ops.view3d.snap_cursor_to_selected() # posiciona o cursor ao centro da seleção
#    bpy.ops.mesh.delete(type='EDGE_FACE') # deleta apenas a face e edges selecionadas
    bpy.ops.object.editmode_toggle() #sai edit mode
    
    bpy.ops.object.select_all(action='DESELECT') # desseleciona todos os objetos
    bpy.ops.object.add(radius=1.0, type='EMPTY', view_align=True)
#    bpy.ops.object.empty_add(type='SINGLE_ARROW', view_align=True) # cria um empty single arrow apontando para o view
    bpy.context.object.name = "Alinhador" #renomeia de alinhador

#    bpy.context.object.rotation_euler[0] = 1.5708

# Parenteia objetos
    a = bpy.data.objects['Rosto']
    b = bpy.data.objects['Alinhador']
    c = bpy.data.objects['Rosto.001']


    bpy.ops.object.select_all(action='DESELECT')
    a.select = True
    b.select = True 
    bpy.context.scene.objects.active = b
    bpy.ops.object.parent_set()
    
    bpy.ops.object.select_all(action='DESELECT')
    c.select = True
    b.select = True 
    bpy.context.scene.objects.active = b
    bpy.ops.object.parent_set() 

# Reseta rotações
    bpy.ops.object.rotation_clear(clear_delta=False)
    
    bpy.ops.object.select_all(action='DESELECT')
    a.select = True
    bpy.context.scene.objects.active = a        
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

    bpy.ops.object.select_all(action='DESELECT')
    b.select = True
    bpy.context.scene.objects.active = b
    bpy.ops.object.delete(use_global=False)

    bpy.ops.object.select_all(action='DESELECT')
    c.select = True
    bpy.context.scene.objects.active = c
    bpy.ops.object.delete(use_global=False)

    bpy.ops.object.select_all(action='DESELECT')
    a.select = True 
    bpy.context.scene.objects.active = a
    bpy.ops.transform.rotate(value=1.5708, axis=(0, 0, 1), constraint_axis=(False, False, True), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
#    bpy.ops.transform.rotate(value=1.5708, axis=(1, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)


    objRedimensionado = bpy.data.objects['Rosto']
    objRedimensionado.scale = ( fatorEscala, fatorEscala, fatorEscala )

   
    bpy.ops.view3d.viewnumpad(type='FRONT')
    bpy.ops.view3d.view_selected(use_all_regions=False)
    
    
    bpy.context.object.name = "Rosto_OK"
    
    bpy.ops.object.select_all(action='DESELECT')
    a = bpy.data.objects['Dist0']
    b = bpy.data.objects['Dist1']
    c = bpy.data.objects['Dist2']
    a.select = True
    b.select = True
    c.select = True

    bpy.ops.object.delete(use_global=False)


class AlinhaArcada2(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.alinha_arcada2"
    bl_label = "Prepara Impressao"
    
    def execute(self, context):
        AlinhaArcada2Def(self, context)
        return {'FINISHED'}  

# ROTACIONA/FLIP Z

#def liberRotacionaYDef(self, context):
    
#    context = bpy.context
#    obj = context.active_object
#    scn = context.scene

#    bpy.ops.transform.rotate(value=1.5708, axis=(1, 0, 0))

#class liberRotacionaY(bpy.types.Operator):
#    """Tooltip"""
#    bl_idname = "object.liber_rotaciona_y"
#    bl_label = "Rotaciona Z"
    
#    def execute(self, context):
#        liberRotacionaYDef(self, context)
#        return {'FINISHED'}
    
def liberFlipYDef(self, context):
    
    context = bpy.context
    obj = context.active_object
    scn = context.scene

    bpy.ops.transform.rotate(value=3.14159, axis=(0, 1, 0))

class liberFlipY(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.liber_flip_y"
    bl_label = "Flip Y"
    
    def execute(self, context):
        liberFlipYDef(self, context)
        return {'FINISHED'}

# FOTOGRAMETRIA

def liberGeraModeloFotoDef(self, context):
    
    scn = context.scene
    tmpdir = tempfile.gettempdir()
    homeall = expanduser("~")

    try:

        OpenMVGtmpDir = tmpdir+'/OpenMVG'
        tmpPLYface = tmpdir+'/MVS/meshlabDec.ply'
#        tmpOBJface = tmpdir+'/MVS/scene_dense_mesh_texture2.obj'

        
        if platform.system() == "Linux":
            OpenMVGPath = homeall+'/Programs/OrtogOnBlender/openMVG/software/SfM/SfM_SequentialPipeline.py'
            OpenMVSPath = homeall+'/Programs/OrtogOnBlender/openMVS/OpenMVSarcada.sh'
            
        if platform.system() == "Windows":
            OpenMVGPath = 'C:/OrtogOnBlender/openMVGWin/software/SfM/SfM_SequentialPipeline.py' 
            OpenMVSPath = 'C:/OrtogOnBlender/openMVSWin/OpenMVSarcada.bat' 

        if platform.system() == "Darwin":
            OpenMVGPath = homeall+'/OrtogOnBlender/openMVGMAC/SfM_SequentialPipeline.py' 
            OpenMVSPath = homeall+'/OrtogOnBlender/openMVSMAC/openMVSarcadaMAC.sh'


        shutil.rmtree(tmpdir+'/OpenMVG', ignore_errors=True)
        shutil.rmtree(tmpdir+'/MVS', ignore_errors=True)


        if platform.system() == "Linux":
            subprocess.call(['python', OpenMVGPath , scn.my_tool.path ,  OpenMVGtmpDir])
            
        if platform.system() == "Windows":
            subprocess.call(['C:/OrtogOnBlender/Python27/python', OpenMVGPath , scn.my_tool.path ,  OpenMVGtmpDir])

        if platform.system() == "Darwin":
            subprocess.call(['python', OpenMVGPath , scn.my_tool.path ,  OpenMVGtmpDir])

        subprocess.call(OpenMVSPath ,  shell=True)

    #    subprocess.call([ 'meshlabserver', '-i', tmpdir+'scene_dense_mesh_texture.ply', '-o', tmpdir+'scene_dense_mesh_texture2.obj', '-om', 'vn', 'wt' ])


        bpy.ops.import_mesh.ply(filepath=tmpPLYface, filter_glob="*.ply")
        meshlabDec = bpy.data.objects['meshlabDec']
        
#        bpy.ops.import_scene.obj(filepath=tmpOBJface, filter_glob="*.obj;*.mtl")

#        scene_dense_mesh_texture2 = bpy.data.objects['scene_dense_mesh_texture2']

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = meshlabDec
        bpy.data.objects['meshlabDec'].select = True


#        bpy.context.object.data.use_auto_smooth = False
#        bpy.context.object.active_material.specular_hardness = 60
#        bpy.context.object.active_material.diffuse_intensity = 0.6
#        bpy.context.object.active_material.specular_intensity = 0.3
#        bpy.context.object.active_material.specular_color = (0.233015, 0.233015, 0.233015)
    #    bpy.ops.object.modifier_add(type='SMOOTH')
    #    bpy.context.object.modifiers["Smooth"].factor = 2
    #    bpy.context.object.modifiers["Smooth"].iterations = 3
    #    bpy.ops.object.convert(target='MESH')
        bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
        bpy.ops.view3d.view_all(center=False)
        bpy.ops.file.pack_all()
        
    except RuntimeError:
        bpy.context.window_manager.popup_menu(ERROruntimeFotosDef, title="Atenção!", icon='INFO')


class liberGeraModeloFoto(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.liber_gera_modelo_foto"
    bl_label = "Liber Gera Modelos Foto"

    def execute(self, context):
        liberGeraModeloFotoDef(self, context)
        return {'FINISHED'}
        
# SEPARA DENTES E NOMEIA

def arcadaCortaSupDef(self, context):
    
    #Arcada Superior

    a1 = bpy.data.objects['BaseCorteArcada']
    a2 = bpy.data.objects['BaseCorteDentes']
    b = bpy.data.objects['FaceMalha.001']

    # Faz cópia da arcada cortada

    bpy.ops.object.select_all(action='DESELECT')
    b.select = True
    bpy.context.scene.objects.active = b

    bpy.ops.object.duplicate_move()
    
    # Corta arcada geral

    bpy.ops.object.select_all(action='DESELECT')

    a1.select = True
    b.select = True

    bpy.context.scene.objects.active = b

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action = 'DESELECT')

    bpy.ops.mesh.knife_project(cut_through=True)
    bpy.ops.mesh.separate(type='SELECTED')

    bpy.ops.object.editmode_toggle()

    bpy.ops.object.select_all(action='DESELECT')

    # Apaga resto

    b.select = True
    bpy.context.scene.objects.active = b

    bpy.ops.object.delete(use_global=False)

    # Corta dentes

    bpy.ops.object.select_all(action='DESELECT')
    d = bpy.data.objects['FaceMalha.002']
    a2.select = True
    d.select = True
    bpy.context.scene.objects.active = d

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.mesh.knife_project(cut_through=True)
    bpy.ops.mesh.separate(type='SELECTED')
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.select_all(action='DESELECT')

    # Separa dentes

    e = bpy.data.objects['FaceMalha.001']
    e.select = True
    bpy.ops.mesh.separate(type='LOOSE')

    bpy.ops.object.select_all(action='DESELECT')

    d.select = True
    bpy.ops.mesh.separate(type='LOOSE')


        # Muda nome de FaceMalha.000

    bpy.ops.object.select_all(action='DESELECT')
    c = bpy.data.objects['FaceMalha.000']
    c.select = True
    bpy.context.scene.objects.active = c
    bpy.context.object.name = "ArcadaCortada"
    bpy.ops.object.hide_view_set(unselected=False)
    
# Joga o centro nos dentes

    scene = bpy.context.scene
    foo_objs = [obj for obj in scene.objects if fnmatch.fnmatchcase(obj.name, "FaceMalh*")]
    foo_objs

    elemento = len(foo_objs)
    numero = 0

    while numero < elemento:
        objNome = foo_objs[numero].name
        objeto = bpy.data.objects[objNome]
        objeto.select = True
        bpy.context.scene.objects.active = objeto
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        numero += 1

# Nomeia dentes

    scene = bpy.context.scene
    foo_objs = [obj for obj in scene.objects if fnmatch.fnmatchcase(obj.name, "FaceMalh*")]
    foo_objs

    elemento = len(foo_objs)
    numero = 0

    menosX ={}
    maisX = {}
    menosXordenada = {}
    maisXordenada = {}


    while numero < elemento:
        coordenadaX = foo_objs[numero].location[0]
        if coordenadaX < 0:
            menosX[foo_objs[numero].name] = foo_objs[numero].location[0]
            menosXordenada = sorted(menosX.items(), key=operator.itemgetter(1), reverse=True)


        if coordenadaX > 0:
            maisX[foo_objs[numero].name] = foo_objs[numero].location[0]
            maisXordenada = sorted(maisX.items(), key=operator.itemgetter(1))

        numero += 1

    print(menosXordenada)
    print("------------")
    print(maisXordenada)

    print(type(menosXordenada))
    print(type(maisXordenada))

    numMenos = 0
    lenMenos = len(menosXordenada)
    nomeMenos = 11

    while numMenos < lenMenos:
        objDenteMenos = menosXordenada[numMenos][0]
        bpy.ops.object.select_all(action='DESELECT')
        a = bpy.data.objects[objDenteMenos]
        bpy.context.scene.objects.active = a
        bpy.context.object.name = str(nomeMenos)

        
        numMenos += 1
        nomeMenos += 1
        
    numMais = 0
    lenMais = len(maisXordenada)
    nomeMais = 21

    while numMais < lenMais:
        objDenteMais = maisXordenada[numMais][0]
        bpy.ops.object.select_all(action='DESELECT')
        a = bpy.data.objects[objDenteMais]
        bpy.context.scene.objects.active = a
        bpy.context.object.name = str(nomeMais)
        
        numMais += 1
        nomeMais += 1
    

class arcadaCortaSup(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.arcada_corta_sup"
    bl_label = "Arcada Corta"
    
    def execute(self, context):
        arcadaCortaSupDef(self, context)
        return {'FINISHED'}

def arcadaCortaInfDef(self, context):
    
    #Arcada Superior

    a1 = bpy.data.objects['BaseCorteArcada']
    a2 = bpy.data.objects['BaseCorteDentes']
    b = bpy.data.objects['FaceMalha.001']

    # Faz cópia da arcada cortada

    bpy.ops.object.select_all(action='DESELECT')
    b.select = True
    bpy.context.scene.objects.active = b

    bpy.ops.object.duplicate_move()
    
    # Corta arcada geral

    bpy.ops.object.select_all(action='DESELECT')

    a1.select = True
    b.select = True

    bpy.context.scene.objects.active = b

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action = 'DESELECT')

    bpy.ops.mesh.knife_project(cut_through=True)
    bpy.ops.mesh.separate(type='SELECTED')

    bpy.ops.object.editmode_toggle()

    bpy.ops.object.select_all(action='DESELECT')

    # Apaga resto

    b.select = True
    bpy.context.scene.objects.active = b

    bpy.ops.object.delete(use_global=False)

    # Corta dentes

    bpy.ops.object.select_all(action='DESELECT')
    d = bpy.data.objects['FaceMalha.002']
    a2.select = True
    d.select = True
    bpy.context.scene.objects.active = d

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.mesh.knife_project(cut_through=True)
    bpy.ops.mesh.separate(type='SELECTED')
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.select_all(action='DESELECT')

    # Separa dentes

    e = bpy.data.objects['FaceMalha.001']
    e.select = True
    bpy.ops.mesh.separate(type='LOOSE')

    bpy.ops.object.select_all(action='DESELECT')

    d.select = True
    bpy.ops.mesh.separate(type='LOOSE')


        # Muda nome de FaceMalha.000

    bpy.ops.object.select_all(action='DESELECT')
    c = bpy.data.objects['FaceMalha.000']
    c.select = True
    bpy.context.scene.objects.active = c
    bpy.context.object.name = "ArcadaCortada"
    bpy.ops.object.hide_view_set(unselected=False)
    
# Joga o centro nos dentes

    scene = bpy.context.scene
    foo_objs = [obj for obj in scene.objects if fnmatch.fnmatchcase(obj.name, "FaceMalh*")]
    foo_objs

    elemento = len(foo_objs)
    numero = 0

    while numero < elemento:
        objNome = foo_objs[numero].name
        objeto = bpy.data.objects[objNome]
        objeto.select = True
        bpy.context.scene.objects.active = objeto
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        numero += 1

# Nomeia dentes

    scene = bpy.context.scene
    foo_objs = [obj for obj in scene.objects if fnmatch.fnmatchcase(obj.name, "FaceMalh*")]
    foo_objs

    elemento = len(foo_objs)
    numero = 0

    menosX ={}
    maisX = {}
    menosXordenada = {}
    maisXordenada = {}


    while numero < elemento:
        coordenadaX = foo_objs[numero].location[0]
        if coordenadaX < 0:
            menosX[foo_objs[numero].name] = foo_objs[numero].location[0]
            menosXordenada = sorted(menosX.items(), key=operator.itemgetter(1), reverse=True)


        if coordenadaX > 0:
            maisX[foo_objs[numero].name] = foo_objs[numero].location[0]
            maisXordenada = sorted(maisX.items(), key=operator.itemgetter(1))

        numero += 1

    print(menosXordenada)
    print("------------")
    print(maisXordenada)

    print(type(menosXordenada))
    print(type(maisXordenada))

    numMenos = 0
    lenMenos = len(menosXordenada)
    nomeMenos = 41

    while numMenos < lenMenos:
        objDenteMenos = menosXordenada[numMenos][0]
        bpy.ops.object.select_all(action='DESELECT')
        a = bpy.data.objects[objDenteMenos]
        bpy.context.scene.objects.active = a
        bpy.context.object.name = str(nomeMenos)

        
        numMenos += 1
        nomeMenos += 1
        
    numMais = 0
    lenMais = len(maisXordenada)
    nomeMais = 31

    while numMais < lenMais:
        objDenteMais = maisXordenada[numMais][0]
        bpy.ops.object.select_all(action='DESELECT')
        a = bpy.data.objects[objDenteMais]
        bpy.context.scene.objects.active = a
        bpy.context.object.name = str(nomeMais)
        
        numMais += 1
        nomeMais += 1
    

class arcadaCortaInf(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.arcada_corta_inf"
    bl_label = "Arcada Corta"
    
    def execute(self, context):
        arcadaCortaInfDef(self, context)
        return {'FINISHED'}


# FOTOGRAMETRIA

class liberCriaFotogrametria(bpy.types.Panel):
    """Planejamento de cirurgia ortognática no Blender"""
    bl_label = "Generate/Import Archs"
    bl_idname = "liber_cria_fotogrametria"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Liber"


    def draw(self, context):
        layout = self.layout
        scn = context.scene
        obj = context.object 

        row = layout.row()
        row.label(text="Scene Setup:")

        row = layout.row()
        knife=row.operator("object.liber_arruma_cena", text="Fix scene!", icon="PARTICLES") 

        row = layout.row()
        row.label(text="3D Scanning:")

        row = layout.row()
        row.operator("import_mesh.stl", text="Import STL", icon="IMPORT")

        row = layout.row()
        row.label(text="Scanning by Photogrammetry:")

        col = layout.column(align=True)
        col.prop(scn.my_tool, "path", text="")
 
        row = layout.row()
        row.operator("object.liber_gera_modelo_foto", text="Start Photogrammetry!", icon="IMAGE_DATA")


        row = layout.row()        
        row.label(text="Align and Resize:")
 
        row = layout.row()
        row.operator("object.cria_tres_pontos", text="3 Points Click", icon="OUTLINER_OB_MESH")

        col = self.layout.column(align = True)
        col.prop(context.scene, "medida_real2")  

        row = layout.row()
        row.operator("object.alinha_forca", text="Align and Resize!", icon="LAMP_POINT")

        row = layout.row()
        row.label(text="CT-Scan Reconstruction:")

        col = layout.column(align=True)
        col.prop(scn.my_tool, "path", text="")
 
        row = layout.row()
        row.operator("object.gera_modelos_tomo_arc", text="Arch Generator", icon="SNAP_FACE")

#        col = layout.column(align=True)
#        col.prop(scn.my_tool, "path", text="")


# CORTA DESENHO


def LiberCortaDesenhoDef(self, context):

    bpy.ops.gpencil.convert(type='POLY')
    bpy.ops.gpencil.layer_remove()
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.knife_project()
    bpy.ops.mesh.delete(type='FACE')
    bpy.ops.object.editmode_toggle()


    bpy.ops.object.select_all(action='DESELECT')
    a = bpy.data.objects['GP_Layer']
    a.select = True
    bpy.context.scene.objects.active = a
    bpy.ops.object.delete(use_global=False)

class LiberCortaDesenho(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.liber_corta_desenho"
    bl_label = "Desenha Corte"
    
    def execute(self, context):
        LiberCortaDesenhoDef(self, context)
        return {'FINISHED'}

# PREPARA DENTES MANUAL SUPERIOR

def LiberPreparaDenteManSupDef(self, context):
    
    context = bpy.context
    obj = context.active_object
    scn = context.scene

    posicao_1 = bpy.context.scene.cursor_location[2]

    bpy.ops.object.join()

    bpy.ops.object.editmode_toggle()

    bpy.ops.object.mode_set(mode = 'EDIT') 

    bpy.ops.mesh.select_all(action = 'DESELECT')

    bpy.ops.mesh.select_non_manifold()

    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})

    bpy.ops.transform.resize(value=(1, 1, 0), constraint_axis=(False, False, True), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

#    bpy.ops.mesh.fill()

    bpy.ops.view3d.snap_cursor_to_selected()

    posicao_2 = bpy.context.scene.cursor_location[2]
    
    posicao_inicial = posicao_1 - posicao_2
    
#   posicao_final = posicao_inicial + 7

    bpy.ops.transform.translate(value=(0, 0, posicao_inicial), constraint_axis=(False, False, True), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)

    bpy.context.space_data.pivot_point = 'INDIVIDUAL_ORIGINS'


    bpy.ops.transform.resize(value=(0.4, 0.4, 0.4), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})

    bpy.ops.transform.resize(value=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

    bpy.context.space_data.pivot_point = 'MEDIAN_POINT'


    bpy.ops.view3d.snap_cursor_to_selected()
    
    
    bpy.ops.object.mode_set(mode = 'OBJECT')

    bpy.context.object.name = "CorteManualSup"


    bpy.ops.mesh.separate(type='LOOSE')
    
# Joga o centro nos dentes

    scene = bpy.context.scene
    foo_objs = [obj for obj in scene.objects if fnmatch.fnmatchcase(obj.name, "CorteManualSup*")]
    foo_objs

    elemento = len(foo_objs)
    numero = 0

    while numero < elemento:
        objNome = foo_objs[numero].name
        objeto = bpy.data.objects[objNome]
        objeto.select = True
        bpy.context.scene.objects.active = objeto
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        numero += 1

# Nomeia dentes

    scene = bpy.context.scene
    foo_objs = [obj for obj in scene.objects if fnmatch.fnmatchcase(obj.name, "CorteManualSup*")]
    foo_objs

    elemento = len(foo_objs)
    numero = 0

    menosX ={}
    maisX = {}
    menosXordenada = {}
    maisXordenada = {}


    while numero < elemento:
        coordenadaX = foo_objs[numero].location[0]
        if coordenadaX < 0:
            menosX[foo_objs[numero].name] = foo_objs[numero].location[0]
            menosXordenada = sorted(menosX.items(), key=operator.itemgetter(1), reverse=True)


        if coordenadaX > 0:
            maisX[foo_objs[numero].name] = foo_objs[numero].location[0]
            maisXordenada = sorted(maisX.items(), key=operator.itemgetter(1))

        numero += 1


    numMenos = 0
    lenMenos = len(menosXordenada)
    nomeMenos = 11

    while numMenos < lenMenos:
        objDenteMenos = menosXordenada[numMenos][0]
        bpy.ops.object.select_all(action='DESELECT')
        a = bpy.data.objects[objDenteMenos]
        bpy.context.scene.objects.active = a
        bpy.context.object.name = str(nomeMenos)

        
        numMenos += 1
        nomeMenos += 1
        
    numMais = 0
    lenMais = len(maisXordenada)
    nomeMais = 21

    while numMais < lenMais:
        objDenteMais = maisXordenada[numMais][0]
        bpy.ops.object.select_all(action='DESELECT')
        a = bpy.data.objects[objDenteMais]
        bpy.context.scene.objects.active = a
        bpy.context.object.name = str(nomeMais)
        
        numMais += 1
        nomeMais += 1    

class LiberPreparaDenteManSup(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.liber_manual_superior"
    bl_label = "Prepara Dentes Manuais Superiores"
    
    def execute(self, context):
        LiberPreparaDenteManSupDef(self, context)
        return {'FINISHED'}

# PREPARA DENTES MANUAL INFERIOR

def LiberPreparaDenteManInfDef(self, context):
    
    context = bpy.context
    obj = context.active_object
    scn = context.scene

    posicao_1 = bpy.context.scene.cursor_location[2]

    bpy.ops.object.join()

    bpy.ops.object.editmode_toggle()

    bpy.ops.object.mode_set(mode = 'EDIT') 

    bpy.ops.mesh.select_all(action = 'DESELECT')

    bpy.ops.mesh.select_non_manifold()

    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})

    bpy.ops.transform.resize(value=(1, 1, 0), constraint_axis=(False, False, True), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

#    bpy.ops.mesh.fill()

    bpy.ops.view3d.snap_cursor_to_selected()

    posicao_2 = bpy.context.scene.cursor_location[2]
    
    posicao_inicial = posicao_1 - posicao_2
    
#   posicao_final = posicao_inicial + 7

    bpy.ops.transform.translate(value=(0, 0, posicao_inicial), constraint_axis=(False, False, True), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)

    bpy.context.space_data.pivot_point = 'INDIVIDUAL_ORIGINS'


    bpy.ops.transform.resize(value=(0.4, 0.4, 0.4), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})

    bpy.ops.transform.resize(value=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

    bpy.context.space_data.pivot_point = 'MEDIAN_POINT'


    bpy.ops.view3d.snap_cursor_to_selected()
    
    
    bpy.ops.object.mode_set(mode = 'OBJECT')

    bpy.context.object.name = "CorteManualInf"


    bpy.ops.mesh.separate(type='LOOSE')
    
# Joga o centro nos dentes

    scene = bpy.context.scene
    foo_objs = [obj for obj in scene.objects if fnmatch.fnmatchcase(obj.name, "CorteManualInf*")]
    foo_objs

    elemento = len(foo_objs)
    numero = 0

    while numero < elemento:
        objNome = foo_objs[numero].name
        objeto = bpy.data.objects[objNome]
        objeto.select = True
        bpy.context.scene.objects.active = objeto
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        numero += 1

# Nomeia dentes

    scene = bpy.context.scene
    foo_objs = [obj for obj in scene.objects if fnmatch.fnmatchcase(obj.name, "CorteManualInf*")]
    foo_objs

    elemento = len(foo_objs)
    numero = 0

    menosX ={}
    maisX = {}
    menosXordenada = {}
    maisXordenada = {}


    while numero < elemento:
        coordenadaX = foo_objs[numero].location[0]
        if coordenadaX < 0:
            menosX[foo_objs[numero].name] = foo_objs[numero].location[0]
            menosXordenada = sorted(menosX.items(), key=operator.itemgetter(1), reverse=True)


        if coordenadaX > 0:
            maisX[foo_objs[numero].name] = foo_objs[numero].location[0]
            maisXordenada = sorted(maisX.items(), key=operator.itemgetter(1))

        numero += 1

    print(menosXordenada)
    print("------------")
    print(maisXordenada)

    print(type(menosXordenada))
    print(type(maisXordenada))

    numMenos = 0
    lenMenos = len(menosXordenada)
    nomeMenos = 41

    while numMenos < lenMenos:
        objDenteMenos = menosXordenada[numMenos][0]
        bpy.ops.object.select_all(action='DESELECT')
        a = bpy.data.objects[objDenteMenos]
        bpy.context.scene.objects.active = a
        bpy.context.object.name = str(nomeMenos)

        
        numMenos += 1
        nomeMenos += 1
        
    numMais = 0
    lenMais = len(maisXordenada)
    nomeMais = 31

    while numMais < lenMais:
        objDenteMais = maisXordenada[numMais][0]
        bpy.ops.object.select_all(action='DESELECT')
        a = bpy.data.objects[objDenteMais]
        bpy.context.scene.objects.active = a
        bpy.context.object.name = str(nomeMais)
        
        numMais += 1
        nomeMais += 1

class LiberPreparaDenteManInf(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.liber_manual_inferior"
    bl_label = "Prepara Dentes Manuais Inferiores"
    
    def execute(self, context):
        LiberPreparaDenteManInfDef(self, context)
        return {'FINISHED'}

# Desenha Pad

def LiberPadExtDef(self, context):

    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})


    bpy.ops.gpencil.convert(type='POLY')
    bpy.ops.gpencil.layer_remove()
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.knife_project()
    bpy.ops.mesh.select_mode(type="FACE")
    bpy.ops.mesh.select_all(action='INVERT')
    bpy.ops.mesh.delete(type='FACE')
    bpy.ops.object.editmode_toggle()
    
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    bpy.context.object.modifiers["Solidify"].thickness = -0.5
    
    bpy.ops.object.modifier_add(type='REMESH')
    bpy.context.object.modifiers["Remesh"].mode = 'SMOOTH'
    bpy.context.object.modifiers["Remesh"].octree_depth = 6
    bpy.context.object.modifiers["Remesh"].scale = 0.99
    bpy.ops.object.modifier_add(type='SMOOTH')
    bpy.context.object.modifiers["Smooth"].factor = 2
    bpy.context.object.modifiers["Smooth"].iterations = 6

    scene = bpy.context.scene 

    try:
        mat = bpy.data.materials['Pad']
        print("Material existe")
        activeObject = bpy.context.active_object 
        bpy.ops.object.material_slot_remove()
        me = activeObject.data
        me.materials.append(mat)
        
    except KeyError:
        print("Não existe")
        activeObject = bpy.context.active_object 
        bpy.ops.object.material_slot_remove()
        mat = bpy.data.materials.new(name="Pad")
        activeObject.data.materials.append(mat) 
        bpy.context.object.active_material.diffuse_color = (0.8, 0.49, 0.025)

    bpy.ops.object.select_all(action='DESELECT')
    a = bpy.data.objects['GP_Layer']
    a.select = True
    bpy.context.scene.objects.active = a
    bpy.ops.object.delete(use_global=False)

class LiberPadExt(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.liber_extruda_desenho"
    bl_label = "Desenha Corte"
    
    def execute(self, context):
        LiberPadExtDef(self, context)
        return {'FINISHED'}

#ATUALIZA VERSAO
class LiberPainelAtualiza(bpy.types.Panel):
    """Planejamento de Ortodontia no Blender"""
    bl_label = "Upgrade LiberTeeth3D"
    bl_idname = "liber_atualiza"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Liber"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        obj = context.object 
		
        row = layout.row()
        row.label(text="VERSION: 20190219a")

        row = layout.row()
        row.operator("object.liber_atualiza_script", text="UPGRADE LIBER!", icon="RECOVER_LAST")
		
        if platform.system() == "Windows":
            row = layout.row()
            row.operator("wm.console_toggle", text="Open Terminal?", icon="CONSOLE")

class liberBotoesArcada(bpy.types.Panel):
    """LiberTeeth 3D"""
    bl_label = "Archs Setup"
    bl_idname = "liber_configura_arcada"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Liber"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="Interest Area Segmentation:")

        row = layout.row()
        row.operator("cut_mesh.polytrim", text="Draw Line Cut", icon="OUTLINER_DATA_MESH")

        row = layout.row()
        row.operator("object.cria_circulo_corte", text="Cutting circle", icon="MESH_CIRCLE")


        row = layout.row()
        knife=row.operator("object.corta_face", text="Cut!", icon="META_PLANE")


        row = layout.row()
        row.operator("object.importa_arcada_corte", text="Cut Plane Add", icon="BORDER_LASSO")

        row = layout.row()
        row.label(text="Arch Setup:")

        row = layout.row()
        row.operator("object.arcada_corta_sup", text="Setup Upper Arch", icon="TRIA_UP")

        row = layout.row()
        row.operator("object.arcada_corta_inf", text="Setup Lower Arch", icon="TRIA_DOWN")

        row = layout.row()
        row.label(text="Manual Setup:")

        row = layout.row()
        row.operator("gpencil.draw", icon='LINE_DATA', text="Draw Cut").mode = 'DRAW_POLY'

        row = layout.row()
        linha=row.operator("object.segmenta_desenho", text="Cut All!", icon="FCURVE")

        row = layout.row()
        row.operator("object.acabamento", icon='MOD_MULTIRES', text="Cut IN!")

        row = layout.row()
        row.operator("object.liber_corta_desenho", text="Cut Front!", icon="MOD_BOOLEAN")

        row = layout.row()
        row.operator("object.fecha_buraco", icon='FACESEL', text="Fill Hole")

        row = layout.row()
        row.operator("mesh.fill_grid", text="Grid Fill", icon="MESH_GRID")#.span=1
        #mesh.fill_grid(span=1)

        row = layout.row()
        circle=row.operator("view3d.cork_mesh_slicer", text="Boolean Union", icon="MOD_ARRAY")
        circle.method='UNION'

        row = layout.row()
        row.operator("object.prepara_impressao", text="Prepares 3D Printing", icon="MOD_REMESH")

        row = layout.row()
        row.label(text="Sculpting:")

        row = layout.row()
        row.operator("object.mode_set", text="Object Mode", icon="OBJECT_DATA").mode = 'OBJECT'
        
        row = layout.row()
        row.operator("sculpt.sculptmode_toggle", text="Sculpt Mode", icon="SCULPTMODE_HLT")
        
        row = layout.row()
        row.operator("object.escultura_grab", text="Grab", icon="BRUSH_GRAB")
 
        row = layout.row()
        row.operator("paint.brush_select", text="Nudge", icon="BRUSH_NUDGE").sculpt_tool='NUDGE'
        
        row = layout.row()
        row.operator("paint.brush_select", text="Draw", icon="BRUSH_SCULPT_DRAW").sculpt_tool='DRAW'
        
        row = layout.row()
        row.operator("paint.brush_select", text="Smooth", icon="BRUSH_SMOOTH").sculpt_tool='SMOOTH'

        row = layout.row()
        row.label(text="Teeth Setup:")

#        row = layout.row()
#        row.operator("cut_mesh.polytrim", text="Desenha Cortes", icon="OUTLINER_DATA_MESH")

        row = layout.row()
        row.operator("object.liber_manual_superior", text="Setup Upper Teeth", icon="TRIA_UP")
        
        row = layout.row()
        row.operator("object.liber_manual_inferior", text="Setup Lower Teeth", icon="TRIA_DOWN")

        row = layout.row()
        row.operator("object.importa_alinha_arcada", text="Align References", icon="CURVE_PATH")


        row = layout.row()
        row.label(text="Kynematic:")

        row = layout.row()
        row.operator("screen.frame_jump", text="Start", icon="REW").end=False
        row.operator("screen.animation_play", text="", icon="PLAY_REVERSE").reverse=True
        row.operator("anim.animalocrot", text="", icon="CLIP")
        row.operator("screen.animation_play", text="", icon="PLAY")
        row.operator("screen.frame_jump", text="End", icon="FF").end=True  

# Draw Pad

        row = layout.row()
        row.label(text="Create Pad:")

        if context.space_data.type == 'VIEW_3D':
                propname = "gpencil_stroke_placement_view3d"
        elif context.space_data.type == 'SEQUENCE_EDITOR':
                propname = "gpencil_stroke_placement_sequencer_preview"
        elif context.space_data.type == 'IMAGE_EDITOR':
                propname = "gpencil_stroke_placement_image_editor"
        else:
                propname = "gpencil_stroke_placement_view2d"

        ts = context.tool_settings

        col = layout.column(align=True)

        col.label(text="Stroke Placement:")

        row = col.row(align=True)
        row.prop_enum(ts, propname, 'VIEW')
        row.prop_enum(ts, propname, 'CURSOR')

        if context.space_data.type == 'VIEW_3D':
            row = col.row(align=True)
            row.prop_enum(ts, propname, 'SURFACE')
            row.prop_enum(ts, propname, 'STROKE')

            row = col.row(align=False)
            row.active = getattr(ts, propname) in {'SURFACE', 'STROKE'}
            row.prop(ts, "use_gpencil_stroke_endpoints")        

        row = layout.row()
        row.operator("gpencil.draw", icon='LINE_DATA', text="Draw Pad").mode = 'DRAW_POLY'

        row = layout.row()
        row.operator("object.liber_extruda_desenho", text="Extrude", icon="CURSOR")

        row = layout.row()
        row.label(text="Splint:")

        row = layout.row()
        row.operator("object.liber_weight_1", text="Weight Paint 1", icon="COLOR_RED") 

        row = layout.row()
        row.operator("object.liber_weight_0", text="Weight Paint 0", icon="COLOR_BLUE")     

        row = layout.row()
        row.operator("object.liber_splint_weight", text="Create Splint!", icon="FILE_TICK")        
    
def register():
    bpy.utils.register_class(LiberSplintWeight)
    bpy.utils.register_class(LiberWeight1)
    bpy.utils.register_class(LiberWeight0)
    bpy.utils.register_class(LiberAtualizaScript)
    bpy.utils.register_class(LiberArrumaCena)
    bpy.utils.register_class(ImportaCorte)
    bpy.utils.register_class(AlinhaArcada2)
    bpy.utils.register_class(ImportaAlinhaArcada)
#    bpy.utils.register_class(liberRotacionaY)
    bpy.utils.register_class(liberFlipY)    
    bpy.utils.register_class(liberGeraModeloFoto)
    bpy.utils.register_class(arcadaCortaSup)
    bpy.utils.register_class(arcadaCortaInf)
    bpy.utils.register_class(LiberPainelAtualiza)
    bpy.utils.register_class(liberCriaFotogrametria)
    bpy.utils.register_class(LiberCortaDesenho)
    bpy.utils.register_class(LiberPreparaDenteManSup)
    bpy.utils.register_class(LiberPreparaDenteManInf)
    bpy.utils.register_class(liberBotoesArcada)
    bpy.utils.register_class(LiberPadExt)
#    bpy.utils.register_class(LiberPreparaImpreBotoes)

    
def unregister():
    bpy.utils.unregister_class(LiberSplintWeight)
    bpy.utils.unregister_class(LiberWeight1)
    bpy.utils.unregister_class(LiberWeight0)
    bpy.utils.unregister_class(LiberAtualizaScript)
    bpy.utils.unregister_class(LiberArrumaCena)
    bpy.utils.unregister_class(ImportaCorteSup)
    bpy.utils.register_class(arcadaCortaInf)
    bpy.utils.unregister_class(AlinhaArcada2)
    bpy.utils.unregister_class(ImportaAlinhaArcada)
#    bpy.utils.unregister_class(liberRotacionaY)
    bpy.utils.unregister_class(liberFlipY)    
    bpy.utils.unregister_class(liberGeraModeloFoto)
    bpy.utils.unregister_class(arcadaCorta)
    bpy.utils.unregister_class(LiberPainelAtualiza)
    bpy.utils.unregister_class(liberCriaFotogrametria)
    bpy.utils.unregister_class(LiberCortaDesenho)
    bpy.utils.unregister_class(LiberPreparaDenteManSup)
    bpy.utils.unregister_class(LiberPreparaDenteManInf)
    bpy.utils.unregister_class(liberBotoesArcada)
    bpy.utils.unregister_class(LiberPadExt)
#    bpy.utils.unregister_class(LiberPreparaImpreBotoes)

        
if __name__ == "__main__":
    register()
