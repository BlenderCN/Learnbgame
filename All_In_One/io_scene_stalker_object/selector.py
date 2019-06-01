
import bpy
from . import parse_xr


def create_operator_classes(shaderList, rootShaders, shaderType, prefix):
    operatorsCode = ''
    for shaderName in shaderList:
        classesList = []
        shaderNameSplit = shaderName.split('\\')
        shaderNameReplace = shaderName.replace('\\', '_')
        shaderNameReplace = shaderNameReplace.replace('-', '_')
        if len(shaderNameSplit) == 1:
            rootShader = ('stalker.{0}_{1}'.format(prefix, shaderNameReplace), shaderName.replace('\\', '\\\\'))
            if rootShader not in rootShaders:
                rootShaders.append(rootShader)
        operatorsCode += '''
class Op_{5}_{0}(bpy.types.Operator):
    bl_idname = 'stalker.{5}_{0}'
    bl_label = ''
    operatorsList.append(('stalker.{5}_{0}', '{1}', 'Op_{5}_{0}'))

    def execute(self, context):
        context.material.stalker.{4} = '{1}'
        return {2}'FINISHED'{3}

bpy.utils.register_class(Op_{5}_{0})
classesOperator.append(Op_{5}_{0})
'''.format(shaderNameReplace, shaderName.replace('\\', '\\\\'), '{', '}', shaderType, prefix)
    return operatorsCode


def create_menu_classes(shaderList, shaderType, prefix):
    menuClassCode = ''
    uniqDirs = []
    for shaderName in shaderList:
        shaderNameSplit = shaderName.split('\\')
        dirName = shaderNameSplit[0]
        if len(shaderNameSplit) >= 2 and dirName not in uniqDirs:
            uniqDirs.append(dirName)
            menuClassCode += '''
class Menu_{3}_{0}(bpy.types.Menu):
    bl_label = '{0}'
    menusList.append('Menu_{3}_{0}')

    def draw(self, context):
        layout = self.layout
        for operator, shader, className in operatorsList:
            if operator.startswith('stalker.{4}_{0}'):
                layout.operator(operator, text=shader.split('\\\\')[-1])

bpy.utils.register_class(Menu_{3}_{0})
classesMenu.append(Menu_{3}_{0})
'''.format(dirName, '{', '}', shaderType, prefix)
    return menuClassCode


def create_selector(parse_function, shader_type, prefix, menu_prefix):
    shaderList = parse_function()
    if shaderList:
        operatorsCode = create_operator_classes(shaderList, rootShaders, shader_type, prefix)
        menuClassCode = create_menu_classes(shaderList, shader_type, prefix)
        exec(operatorsCode)
        exec(menuClassCode)

        menuCode = '''
class {0}_Menu(bpy.types.Menu):
    bl_label = ''

    def draw(self, context):
        layout = self.layout
        for menu in menusList:
            if menu.startswith('Menu_{1}_'):
                layout.menu(menu)

        for operator, shader in rootShaders:
            if operator.startswith('stalker.{2}'):
                layout.operator(operator, text=shader.split('\\\\')[-1])
        '''.format(menu_prefix, shader_type, prefix)

    else:
        menuCode = '''
class {0}_Menu(bpy.types.Menu):
    bl_label = ''

    def draw(self, context):
        layout = self.layout
        '''.format(menu_prefix)
    exec(menuCode)

    bpy.utils.register_class(eval('{0}_Menu'.format(menu_prefix)))
    classesMenuRoot.append(eval('{0}_Menu'.format(menu_prefix)))


def remove_shader_selector():
    bpy.utils.unregister_class(Shader_Menu)


def update_create_shader_selector(self, context):
    global operatorsList
    global menusList
    operatorsList = []
    menusList = []
    create_selector(parse_xr.parse_shaders, 'engine_shader', 'es', 'Shader')


def update_create_compiler_selector(self, context):
    global operatorsList
    global menusList
    operatorsList = []
    menusList = []
    create_selector(parse_xr.parse_shaders_xrlc, 'compiler_shader', 'cs', 'Compiler')


def update_create_game_material_selector(self, context):
    global operatorsList
    global menusList
    operatorsList = []
    menusList = []
    create_selector(parse_xr.parse_game_materials, 'game_material', 'gm', 'Game_Material')


def unregister_selector():
    for class_ in classesOperator:
        try:
            bpy.utils.unregister_class(class_)
        except:
            pass
    for class_ in classesMenu:
        try:
            bpy.utils.unregister_class(class_)
        except:
            pass
    for class_ in classesMenuRoot:
        try:
            bpy.utils.unregister_class(class_)
        except:
            pass


operatorsList = []
menusList = []
classesMenuRoot = []
classesOperator = []
classesMenu = []
rootShaders = []
