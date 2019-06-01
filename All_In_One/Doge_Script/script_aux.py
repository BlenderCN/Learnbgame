import bpy
import json
from . import script_main
from . import util_funcs
from pprint import pprint
# lista_modelos = []


class ImportJsonFileOperator(bpy.types.Operator):
    """ HELP DESCRIPTION """
    bl_idname = "import.jason_file"
    bl_label = "Import Json Files"
    bl_description = "Importador de arquivos Json para o Blender"

    filter_glob = bpy.props.StringProperty(default="*.json", options={'HIDDEN'})            # Filtro para seleção de arquivos, permitir apenas arquivos '.json'
    # filter_glob = bpy.props.StringProperty(default="*.json;*.txt", options={'HIDDEN'})    # Exemplo multiplo arquivos permitidos
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        file = open(self.filepath, 'r')
        if(file is not None):
             print()
            # script_main.lista_modelos = jsonImport(arq)
            # script_main.modelarObjetos(lista_modelos)
            # pprint(script_main.lista_modelos)
        else:
            raise RuntimeError("[ERROR]: Um arquivo inválido foi selecionado.")
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)                                  # abrir a janela para selecionar arquivos
        return {'RUNNING_MODAL'}

def jsonImport(arquivo):
    modelos = []
    dados = json.load(arquivo)
    for item in dados['objects']:
        vertices = util_funcs.listToTuple(item['vertices'])
        arestas = util_funcs.listToTuple(item['edges'])
        faces = item['faces']
        modelos.append({'vertice': vertices, 'edges': arestas, 'faces': faces})
    return modelos

def modelos():

    return

def register():
    bpy.utils.register_class(ImportJsonFileOperator)

def unregister():
    bpy.utils.unregister_class(ImportJsonFileOperator)