import os
import bpy
import mathutils

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )

bl_info = {
    "name": "MMG",
    "description": "Remeshes with MMG tool and vertex paint",
    "author": "Loïc NORGEOT",
    "version": (0, 0),
    "blender": (2, 76, 0),
    "warning": "",
    "category": "Learnbgame"
}

def command(program, args, flags, values):
    commandString = [program]
    for a in args:
        commandString.append(str(a))
    for f,v in zip(flags, values):
        st = "-"
        st += str(f)
        if v != None:
            st += " " + str(v)
        commandString.append(st)
    st = ""
    for c in commandString:
        st += c + " "
    print(st)
    os.system(st)

def MMG(TOOL):
    mesh = TOOL.file#[:-5]+".tmp.mesh"
    sol = mesh[:-5] + ".sol"
    out = mesh
    args = [mesh, out]
    flags =  ["hgrad",    "hausd",    "hmin",    "hmax"]
    hmin = TOOL.hmin/100.0 * max(bpy.context.object.dimensions)  
    hmax = TOOL.hmax/100.0 * max(bpy.context.object.dimensions)
    hausd = TOOL.hausd/100.0 * max(bpy.context.object.dimensions)
    values = [TOOL.hgrad, hausd, hmin, hmax]
    if not TOOL.nr:
        flags.append("nr")
        values.append(None)
    flags.append("sol")
    values.append(sol)
    command("mmgs_O3", args, flags, values)
    return out

def MEDIT(files):
    st = "medit "
    for f in files:
        st += str(f) + " " + "-fs"
    os.system(st)


class Settings(PropertyGroup):
    medit = BoolProperty(name="medit",
                         description="Display in MEDIT",
                         default = True)
    #sol = BoolProperty(name="sol",
    #                     description="Use .sol file if available",
    #                     default = True)
    nr = BoolProperty(name="angle",
                      description="Angle Detection",
                      default = True)
    reload = BoolProperty(name="reload",
                          description="Load remeshed file",
                          default = False)

    hmin = FloatProperty(name = "hmin (%)",
                         description="Minimal edge length (%)",
                         default = 0.5,
                         min = 0.01,
                         max = 20
    )
    hmax = FloatProperty(name = "hmax (%)",
                         description="Maximal edge length (%)",
                         default = 5,
                         min = 0.1,
                         max = 100
    )
    hausd = FloatProperty(name = "hausd (%)",
                         description="Haussdorf distance (%)",
                         default = 2,
                         min = 0.001,
                         max = 20
    )
    hgrad = FloatProperty(name = "hgrad",
                         description="Gradation",
                         default = 1.08,
                         min = 1,
                         max = 10
    )
    file = StringProperty(name = "file",
                          default = "",
                          description = "File to be exported to",
                          subtype = 'FILE_PATH'
    )

class MMGPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "weightpaint"
    bl_category = "Tools"
    bl_label = "Export and remesh"
    
    def draw(self, context):
        mytool = context.scene.my_tool

        # display the properties
        self.layout.prop(mytool, "hausd", text="haus_d")
        self.layout.prop(mytool, "hgrad", text="h_grad")
        self.layout.prop(mytool, "hmin", text="h_min")
        self.layout.prop(mytool, "hmax", text="h_max")
        self.layout.prop(mytool, "nr", text = "Angle detection")
        self.layout.prop(mytool, "file", text="Output mesh")
        #self.layout.prop(mytool, "sol", text="Use .sol file")
        self.layout.prop(mytool, "medit", text="View in medit")
        self.layout.prop(mytool, "reload", text="Load remeshed model")
        TheCol = self.layout.column(align=True)
        TheCol.operator("mesh.mmg", text="Launch MMG")

class runMMG(bpy.types.Operator):
    bl_idname = "mesh.mmg"
    bl_label = "Export and remesh"

    def invoke(self, context, event):
        T = context.scene.my_tool
        try:
            inFile = T.file
            bpy.ops.export_mesh.mesh(filepath = inFile)
            mmgFile = MMG(T)
            if(T.medit):
                MEDIT([mmgFile])
            if(T.reload):
                scene = bpy.context.scene
                for ob in scene.objects:
                    if ob.type == 'MESH':
                        ob.select=True
                        scene.objects.active = ob
                        bpy.ops.object.mode_set(mode='OBJECT')
                        scene.objects.unlink(ob)
                        bpy.data.objects.remove(ob)
                for m in bpy.data.meshes:
                    bpy.data.meshes.remove(m)
                bpy.ops.import_mesh.mesh(filepath = mmgFile)
                bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        except AttributeError:
            print("MESH_IO NOT INSTALLED!")
        return {"FINISHED"}

bpy.utils.register_class(runMMG)
bpy.utils.register_class(MMGPanel)

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.my_tool = PointerProperty(type=Settings)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.my_tool

if __name__ == "__main__":
    register()
