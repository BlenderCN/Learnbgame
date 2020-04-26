import imp, os, glob, sys
from arnold import *
from bpy.props import (CollectionProperty,StringProperty, BoolProperty,
IntProperty, FloatProperty, FloatVectorProperty, EnumProperty, PointerProperty)
from bl_ui import properties_material
pm = properties_material

if "bpy" in locals():
    pass
else:
    import bpy

for member in dir(properties_material):
    subclass = getattr(properties_material, member)

    try:
        # this is a horrible hack. Must figure out how to get this to work better
        subclass.COMPAT_ENGINES.add('BtoA')
        if subclass.bl_label in ["Material Specials",
"SSS Presets",
"Custom Properties",
"Diffuse",
"Flare",
"Halo",
"Mirror",
"Options",
"Physics",
"Render Pipeline Options",
"Shading",
"Shadow",
"Specular",
"Subsurface Scattering",
"Strand",
"Density",
"Integration",
"Transparency",
"Lighting"]:
            subclass.COMPAT_ENGINES.remove('BtoA')

    except:
        pass
########################
#
# custom material properties
#
########################
def rnaPropUpdate(self, context):
    self.update_tag()

class BtoA_material_shader_gui(pm.MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Arnold Shader"
    COMPAT_ENGINES = {'BtoA'}

    @classmethod
    def poll(cls, context):
        mat = context.material
        engine = context.scene.render.engine
        return pm.check_material(mat) and (mat.type in {'SURFACE', 'WIRE'}) and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        mat = pm.active_node_mat(context.material)
        split = layout.split()
        split.prop(mat.BtoA,"shaderType")

class BtoAMaterialSettings(bpy.types.PropertyGroup):
    name="BtoAMaterialSettings"
    #################   
    # Import Modules from default folder
    #################
    defaultMatDir = os.path.join(os.path.dirname(__file__),"materials")
    defaultMats = glob.glob(os.path.join(defaultMatDir,"*.py"))
    # if the dir is not a "module", lets turn it into one
    if not os.path.exists(os.path.join(defaultMatDir,"__init__py")):
        fin = open(os.path.join(defaultMatDir,"__init__.py"),'w')
        fin.close()

    # load all materials from the materials folder
    materials = []
    loadedMaterials = {}
    for modulePath in defaultMats:
        module = os.path.basename(modulePath)
        moduleName = module[:-3]
        if module == '__init__.py' or module[-3:] != '.py':
            continue
        print("BtoA:: Loading %s"%module) 
        foo = __import__("BtoA.materials."+moduleName, locals(), globals())
        module = eval("foo.materials."+moduleName)
        materials.append(module.enumValue)
        vars()[moduleName] = PointerProperty(type=module.className)
        loadedMaterials[module.enumValue[0]] = module

    #################   
    # Import Modules from the Material Module search path
    # THIS DOES NOT WORK. The GUI WILL NOT REDRAW PROPERLY
    #################
    #rawMatPath = os.environ["BTOA_MATERIAL_PATHS"]
    #searchPaths = []
    #searchPaths = rawMatPath.split(":")
    # separate /// for windows paths
    #for i in searchPaths:
    #    if "///" in i:
    #        i = i.replace(":")

    #for i in searchPaths:
    #    localMats = glob.glob(os.path.join(i,"*.py"))
    #    if len(localMats) == 0:
    #        break

        # if the dir is not a "module", lets turn it into one
    #    if not os.path.exists(os.path.join(i,"__init__py")):
    #        fin = open(os.path.join(i,"__init__.py"),'w')
    #        fin.close()

    #    for modulePath in localMats:
    #        module = os.path.basename(modulePath)
    #        moduleDir = os.path.dirname(modulePath)
    #        sys.path.append(os.path.dirname(moduleDir))
    #        print(sys.path)
    #        moduleDir = os.path.basename(moduleDir)
    #        moduleName = module[:-3]
    #        if module == '__init__.py' or module[-3:] != '.py':
    #            continue
    #        print("Loading ",module) 
            
    #        foobar = __import__(moduleDir+"."+moduleName, locals(), globals())
    #        loadedModule = eval("foobar."+moduleName)
    #        materials.append(loadedModule.enumValue)
    #        vars()[moduleName] = PointerProperty(type=loadedModule.className,name=moduleName)
    #        loadedMaterials[loadedModule.enumValue[0]] = loadedModule

    shaderType = EnumProperty(items=materials,
                             name="Shader", description="Surface Shader", 
                             default="STANDARD")

bpy.utils.register_class(BtoAMaterialSettings)
bpy.types.Material.BtoA = PointerProperty(type=BtoAMaterialSettings,name='BtoA')

class Materials:
    def __init__(self, scene,textures=None):
        self.scene = scene
        self.textures = None
        if textures:
            self.textures = textures.texturesDict
        self.materialDict = {}

    def writeMaterials(self):
        for mat in bpy.data.materials:
            self.writeMaterial(mat)

    def writeMaterial(self,mat):
        outmat = None
        currentMaterial = mat.BtoA.loadedMaterials[mat.BtoA.shaderType]
        outmat = currentMaterial.write(mat,self.textures)

        AiNodeSetStr(outmat,b"name",mat.name.encode('utf-8'))
        self.materialDict[mat.as_pointer()] = outmat
        return outmat
