import bpy

#####################################################################
# Globals.
#####################################################################
lista_modelos = []
lista_modelos_modificar = []
ajustar = False     # Flag para ajustar um modelo

class AutoModelerOperator(bpy.types.Operator) :
    bl_idname = "object.auto_modeler_avatar"
    bl_label = "Modelador Automatico"
    bl_description = "Operador do Modelador Automatico de Avatares"

    def execute(self, context):
        if(len(lista_modelos) != 0):
            modelar(lista_modelos)
        else:
            raise RuntimeError("[ERROR]: A Lista de Modelos está vazia")
            #print("[ERROR]: A Lista de Modelos está vazia")
        return {'FINISHED'}

def modelar(modelos):
    # Magic
    lista_objetos = bpy.data.objects.items()
    for indice in range(len(lista_objetos)):
        for modelo in modelos:
            if (lista_objetos[indice][0] == modelo):
                print("Modificando: ", lista_objetos[indice][0], "\nParametros: ", modelos[modelo])
                # check_model()
                # compare os parametros do objeto
                # se equivalentes, nada muda
                # se diferentes, iniciar o processo de ajustes
                if(ajustar):
                    print("ajustando")
                else:
                    print("sem ajustes")
            print("")

    '''
    objects = bpy.data.objects
    for object in objects:
        name = object.name
        name.lower()
        print(name)
        if(name == 'empty.001'):
            print("Empty.001 econtrado. Modificando")
        elif(name == 'empty.002'):
            print("Empty.002 econtrado. Modificando")
        elif(name == 'empty.003'):
            print("Empty.003 econtrado. Modificando")
        elif(name == 'empty.004'):
            print("Empty.004 econtrado. Modificando")
    '''
    return None

def check_model(model, new_model):
    global ajustar
    if(model == new_model):
        ajustar = False
    else:
        ajustar = True

def ajust_model(model, new_model):
    # modificar parametros globais
    # modificar parametros unitarios (vertices, edges e faces)
    # iterar entre os parametros unitarios
    return

def model_translate():
    print("Operacao de translação")
    # transladar
    return None

def model_rotate():
    print("Operação de rotação")
    # rotacionar
    return None

def model_scale():
    print("Operação de escala")
    # escalar
    return None

def register():
    bpy.utils.register_class(AutoModelerOperator)

def unregister():
    bpy.utils.unregister_class(AutoModelerOperator)
