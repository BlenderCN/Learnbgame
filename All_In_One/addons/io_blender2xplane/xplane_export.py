

import bpy
from bpy.props import BoolProperty,StringProperty,FloatProperty,EnumProperty,CollectionProperty,PointerProperty
import math
import mathutils
import sys
import os

xpLabel = "X-PlaneNG"
xpProp = "xp"
xpExportDescr = "XPlane Export"
xpDatarefsGroup = "XPlaneNG Datarefs"

fileW = None

projectname = "737_cockpit"
output_directory = "d:\\devel"
output_filename = projectname + ".obj"
objects = []
texture_cockpit = ""
ANI = ""
Vector = mathutils.Vector
Matrix = mathutils.Matrix
rad = math.radians
deg = math.degrees
PI=math.pi
expObj = {}
expOrder = []
efaces = {}
matrixXMinus90    = Matrix().Rotation(math.radians(-90),3,"X")
matrixX90         = Matrix().Rotation(math.radians(90),3,"X")
F = ""
VTindex = 0
VTSIZE = 0
TRISIZE = 0
TRIS = 0
VTi = 0


def setAttr(level, val, attrs):
    global ANI
    if val[0] == val[1]:
        return
    if type(val[0]) == type(True):
        v = 0
        if val[0]:
            v = 1
        ANI += "%s%s\n" % (addtab(level),attrs[v])
    if type(val[0]) == type(""):
        ANI += "%s%s\t%s\n" % (addtab(level), attrs[0], val[0])
    val[1] = val[0]
    return


initAniAttrs = {
    "solid_camera":[setAttr,[None,None],["ATTR_no_solid_camera","ATTR_solid_camera"]],
    "double_sided":[setAttr,[None,None],["ATTR_cull","ATTR_no_cull"]],
    "diffuse"     :[setAttr,[None,None],["ATTR_diffuse"]],
    "shiny"       :[setAttr,[None,None],["ATTR_shiny_rat"]],
    "emission"    :[setAttr,[None,None],["ATTR_emission_rgb"]],
    }


def findFCurveByPath(fcurves,path):
    i = 0
    fcurve = None
    
    # find fcurve
    while i<len(fcurves):
        if fcurves[i].data_path == path:
            fcurve = fcurves[i]
            i = len(fcurves)
        i+=1
    return fcurve

def makeKeyframesLinear(obj,path):
    fcurve = None
    
    if (obj.animation_data != None and obj.animation_data.action != None and len(obj.animation_data.action.fcurves)>0):
        fcurve = findFCurveByPath(obj.animation_data.action.fcurves,path)

        if fcurve:
            # find keyframe
            keyframe = None
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = 'LINEAR'




class XPlaneNG_Dataref(bpy.types.PropertyGroup):
    path = StringProperty(attr="path",
                                    name="Dataref",
                                    description="Dataref Path",
                                    default="")
    value = FloatProperty(attr="value",
                                    name="Value",
                                    description="Value",
                                    default=0.0,
                                    precision=2,
                                    )
    loop = FloatProperty(attr="loop",
                                name="Loop Amount",
                                description="Loop amount of animation, usefull for ever increasing Datarefs. A value of 0 will ignore this setting.",
                                min=0.0,
                                precision=2)
    anim_type = EnumProperty(attr="anim_type",
                                        name="Animation Type",
                                        description="Type of animation this Dataref will use.",
                                        default="show",
                                        items=[
                                            ("transform","LocRot","Location/Rotation"),
                                            ("show","Show","Show"),
                                            ("hide","Hide","Hide")
                                            ])
    show_hide_v1 = FloatProperty(attr="show_hide_v1",
                                            name="Value 1",
                                            description="Show/Hide value 1",
                                            default=0.0)
    show_hide_v2 = FloatProperty(attr="show_hide_v2",
                                            name="Value 2",
                                            description="Show/Hide value 2",
                                            default=0.0)




class   XPlaneNG_Manipulator(bpy.types.PropertyGroup):
    enable = BoolProperty(  attr="enable",
                            name="Manipulator",
                            description="Enables object as manipulator",
                            default=False,
                            )
    type = EnumProperty(attr="type",
                                name="Manipulator type",
                                description="The type of the manipulator.",
                                default='drag_xy',
                                items=[("drag_xy","drag_xy","drag_xy"),
                                ("drag_axis","drag_axis","drag_axis"),
                                ("command","command","command"),
                                ("command_axis","command_axis","command_axis"),
                                ("push","push","push"),
                                ("radio","radio","radio"),
                                ("toggle","toggle","toggle"),
                                ("delta","delta","delta"),
                                ("wrap","wrap","wrap"),
                                ("toggle","toggle","toggle"),
                                ("noop","noop","noop")])
    tooltip = StringProperty(attr="tooltip",
                                    name="Manipulator Tooltip",
                                    description="The tooltip will be displayed when hovering over the object.",
                                    default="")

    cursor = EnumProperty(attr="cursor",
                                name="Manipulator Cursor",
                                description="The mouse cursor type when hovering over the object.",
                                default="hand",
                                items=[("four_arrows","four_arrows","four_arrows"),
                                        ("hand","hand","hand"),
                                        ("button","button","button"),
                                        ("rotate_small","rotate_small","rotate_small"),
                                        ("rotate_small_left","rotate_small_left","rotate_small_left"),
                                        ("rotate_small_right","rotate_small_right","rotate_small_right"),
                                        ("rotate_medium","rotate_medium","rotate_medium"),
                                        ("rotate_medium_left","rotate_medium_left","rotate_medium_left"),
                                        ("rotate_medium_right","rotate_medium_right","rotate_medium_right"),
                                        ("rotate_large","rotate_large","rotate_large"),
                                        ("rotate_large_left","rotate_large_left","rotate_large_left"),
                                        ("rotate_large_right","rotate_large_right","rotate_large_right"),
                                        ("up_down","up_down","up_down"),
                                        ("down","down","down"),
                                        ("up","up","up"),
                                        ("left_right","left_right","left_right"),
                                        ("left","left","left"),
                                        ("right","right","right"),
                                        ("arrow","arrow","arrow")])
    dx = FloatProperty(attr="dx",
                            name="dx",
                            description="X-Drag axis length",
                            default=0.0)
    dy = FloatProperty(attr="dy",
                            name="dy",
                            description="Y-Drag axis length",
                            default=0.0)
    dz = FloatProperty(attr="dz",
                            name="dz",
                            description="Z-Drag axis length",
                            default=0.0)
    v1 = FloatProperty(attr="v1",
                            name="v1",
                            description="Value 1",
                            default=0.0)
    v2 = FloatProperty(attr="v2",
                            name="v2",
                            description="Value 2",
                            default=0.0)
    v1_min = FloatProperty(attr="v1_min",
                            name="v1 min",
                            description="Value 1 min.",
                            default=0.0)
    v1_max = FloatProperty(attr="v1_max",
                            name="v1 min",
                            description="Value 1 max.",
                            default=0.0)
    v2_min = FloatProperty(attr="v2_min",
                            name="v2 min",
                            description="Value 2 min.",
                            default=0.0)
    v2_max = FloatProperty(attr="v2_max",
                            name="v2 min",
                            description="Value 2 max.",
                            default=0.0)
    v_down = FloatProperty(attr="v_down",
                                name="v down",
                                description="Value on mouse down",
                                default=0.0)
    v_up = FloatProperty(attr="v_up",
                                name="v up",
                                description="Value on mouse up",
                                default=0.0)
    v_hold = FloatProperty(attr="v_hold",
                                name="v hold",
                                description="Value on mouse hold",
                                default=0.0)
    v_on = FloatProperty(attr="v_on",
                                name="v on",
                                description="On value",
                                default=0.0)
    v_off = FloatProperty(attr="v_off",
                                name="v off",
                                description="Off value",
                                default=0.0)
    command = StringProperty(attr="command",
                                name="Command",
                                description="Command",
                                default="")
    positive_command = StringProperty(attr="positive_command",
                                name="Positive command",
                                description="Positive command",
                                default="")
    negative_command = StringProperty(attr="negative_command",
                                name="Negative command",
                                description="Negative command",
                                default="")
    dataref1 = StringProperty(attr="dataref1",
                                name="Dataref 1",
                                description="Dataref 1",
                                default="none")
    dataref2 = StringProperty(attr="dataref2",
                                name="Dataref 2",
                                description="Dataref 2",
                                default="none")
 


class XPlaneNG_ObjectSettings(bpy.types.PropertyGroup):
    datarefs = CollectionProperty(attr="datarefs",
                                        name=xpDatarefsGroup,
                                        description="X-Plane Datarefs",
                                        type=XPlaneNG_Dataref)
    solid_camera = BoolProperty(attr="solid_camera",
                                      name="Camera collision",
                                      description="Camera collision",
                                      default=False)
    manip = PointerProperty(attr="manip",
                                    name="Manipulator",
                                    description="",
                                    type=XPlaneNG_Manipulator)




class XPlaneNG_OBJECT_OT_xp_add_dataref(bpy.types.Operator):
    bl_label = 'Add Dataref'
    bl_idname = 'object.xp_add_dataref'

    def execute(self,context):
        obj = context.object
        obj.xp.datarefs.add()
        dataref = obj.xp.datarefs[len(obj.xp.datarefs)-1]
        if obj.type == "ARMATURE":
            dataref.anim_type = "transform"
        else:
            dataref.anim_type = "hide"
        return {'FINISHED'}

class XPlaneNG_OBJECT_OT_xp_remove_dataref(bpy.types.Operator):
    bl_label = ''
    bl_idname = 'object.xp_remove_dataref'
    bl_description = 'Remove a X-Plane Dataref box'
    
    index = bpy.props.IntProperty()

    def execute(self,context):
        obj = context.object
        path = "xp.datarefs["+str(self.index)+"].value"
        if (obj.animation_data != None and obj.animation_data.action != None and len(obj.animation_data.action.fcurves)>0):
            fcurve = findFCurveByPath(obj.animation_data.action.fcurves,path)
            if fcurve:
                obj.animation_data.action.fcurves.remove(fcurve=fcurve)
        obj.xp.datarefs.remove(self.index)
        return {'FINISHED'}



class XPlaneNG_OBJECT_OT_xp_add_dataref_keyframe(bpy.types.Operator):
    bl_label = ''
    bl_idname = 'object.xp_add_dataref_keyframe'
    index = bpy.props.IntProperty()
    def execute(self,context):
        obj = context.object
        path = "xp.datarefs["+str(self.index)+"].value"
        obj.xp.datarefs[self.index].keyframe_insert(data_path="value",group=xpDatarefsGroup)
        makeKeyframesLinear(obj,path)
        return {'FINISHED'}

class XPlaneNG_OBJECT_OT_xp_remove_dataref_keyframe(bpy.types.Operator):
    bl_label = ''
    bl_idname = 'object.xp_remove_dataref_keyframe'
    index = bpy.props.IntProperty()
    def execute(self,context):
        obj = context.object
        obj.xp.datarefs[self.index].keyframe_delete(data_path="value",group=xpDatarefsGroup)
        return {'FINISHED'}




def manipulator(obj,layout):
    r = layout.row()
    r.prop(obj.xp.manip,"enable")
    if obj.xp.manip.enable:

        box = layout.box()
        c = box.column(align=True)
        r = c.row()
        r.prop(obj.xp.manip,"type")
        type = obj.xp.manip.type
        
        if type not in ("noop"):
            r = c.row()
            r.prop(obj.xp.manip,'cursor',text="Cursor")
            r = c.row()
            r.prop(obj.xp.manip,'tooltip',text="Tooltip")

            c = box.column(align=True)

            if type!='drag_xy':
                r = c.row()
                r.prop(obj.xp.manip,'dataref1',text="Dataref")

        if type in ('drag_axis','command_axis'):
            r = c.row()
            r.prop(obj.xp.manip,'dx',text="dx")
            r.prop(obj.xp.manip,'dy',text="dy")
            r.prop(obj.xp.manip,'dz',text="dz")


        # values
        if type=='drag_xy':
            r = c.row()
            r.prop(obj.xp.manip,'dataref1',text="Dataref X")
            r = c.row()
            r.prop(obj.xp.manip,'dx',text="dx")
            r.prop(obj.xp.manip,'v1_min',text="dx min")
            r.prop(obj.xp.manip,'v1_max',text="dx max")
            r = c.row()
            r.prop(obj.xp.manip,'dataref2',text="Dataref Y")
            r = c.row()
            r.prop(obj.xp.manip,'dy',text="dy")
            r.prop(obj.xp.manip,'v2_min',text="dy min")
            r.prop(obj.xp.manip,'v2_max',text="dy max")

        elif type=='drag_axis':
            r = c.row()
            r.prop(obj.xp.manip,'v1',text="v1")
            r.prop(obj.xp.manip,'v2',text="v2")
        elif type=='command':
            r = c.row()
            r.prop(obj.xp.manip,'command',text="Command")
        elif type=='command_axis':
            r = c.row()
            r.prop(obj.xp.manip,'positive_command',text="Pos. command")
            r = c.row()
            r.prop(obj.xp.manip,'negative_command',text="Neg. command")
        elif type=='push':
            r = c.row()
            r.prop(obj.xp.manip,'v_down',text="v down")
            r.prop(obj.xp.manip,'v_up',text="v up")
        elif type=='radio':
            r = c.row()
            r.prop(obj.xp.manip,'v_down',text="v down")
        elif type=='toggle':
            r = c.row()
            r.prop(obj.xp.manip,'v_on',text="v On")
            r.prop(obj.xp.manip,'v_off',text="v Off")
        elif type in ('delta','wrap'):
            r = c.row()
            r.prop(obj.xp.manip,'v_down',text="v down")
            r.prop(obj.xp.manip,'v_hold',text="v hold")
            r = c.row()
            r.prop(obj.xp.manip,'v1_min',text="v min")
            r.prop(obj.xp.manip,'v1_max',text="v max")

def animation(obj,layout):
    '''
    if (obj.animation_data != None and obj.animation_data.action != None and len(obj.animation_data.action.fcurves)>0):
        current_frame = bpy.context.scene.frame_current
        keysinframe = False
        for curve in obj.animation_data.action.fcurves:
            for k in curve.keyframe_points:
                if k.co.x == current_frame:
                    keysinframe = True
            

        keysinframe = True
        if keysinframe:
    '''
    for i,attr in enumerate(obj.xp.datarefs):
        box = layout.box()
        c = box.column(align=False)
        r = c.row()
        r.prop(attr,"path")
        r.operator("object.xp_remove_dataref", icon="X",emboss=True).index=i

        c = box.column(align=True)
        r = c.row()
        r.prop(attr,"anim_type",text="AnimType")

        r = c.row()
        if attr.anim_type in "transform":
            if obj.type == "ARMATURE":
                r.prop(attr,"value")
                r.operator("object.xp_add_dataref_keyframe",icon="KEY_HLT").index=i
                r.operator("object.xp_remove_dataref_keyframe",icon="KEY_DEHLT").index=i
                r = c.row()
                r.prop(attr,"loop")

            else:
                box = box.box()
                c = box.column(align=True)
                r = c.row()
                r.label(icon="ERROR")
                r.label("Currently not allowed")
                r = c.row()
                r.label("Look this in the ARMATURE")
#            else:
#                box = box.box()
#                c = box.column(align=True)
#                r = c.row()
#                r.label("Define parent ARMATURE / BONE", icon="ARMATURE_DATA")
            
        elif attr.anim_type in ("show","hide"):
            r.prop(attr,"show_hide_v1")
            r.prop(attr,"show_hide_v2")

    r = layout.row(align=True)
    r.label()
    r.operator("object.xp_add_dataref")


        
    


class XPlaneNG_OBJECT_PROPS(bpy.types.Panel):
    bl_label = xpLabel
    bl_region_type = "WINDOW"
    bl_space_type = "PROPERTIES"
    bl_context = "object"

    height = bpy.props.IntProperty(attr="height")

    def draw(self, context):
        obj = context.object
        layout = self.layout
        row = layout.row
        col = layout.column

        if obj.type in ("MESH"):
            r = row()
            r.prop(obj.xp, "solid_camera")
#            r = row()
#            r.prop(obj.data,"show_double_sided")
            manipulator(obj,layout)
            animation(obj,layout)
        if obj.type in ("ARMATURE"):
            animation(obj,layout)



    
def writeTris(myObj, scObj, level, aniAttrs):
    
    aniAttrs["double_sided"][1][0] = scObj.data.show_double_sided
    aniAttrs["solid_camera"][1][0] = scObj.xp.solid_camera

    if scObj.material_slots:
        mat = scObj.material_slots[0].material

        diffuse = [mat.diffuse_intensity*mat.diffuse_color[0],
                   mat.diffuse_intensity*mat.diffuse_color[1],
                   mat.diffuse_intensity*mat.diffuse_color[2]]
        aniAttrs["diffuse"][1][0] = ("%.3f\t%.3f\t%.3f" %
                                    (
                                        diffuse[0],
                                        diffuse[1],
                                        diffuse[2]
                                    ))

        emission = [mat.emit*mat.diffuse_color[0],
                    mat.emit*mat.diffuse_color[1],
                    mat.emit*mat.diffuse_color[2]]
        aniAttrs["emission"][1][0] = ("%.3f\t%.3f\t%.3f" %
                                    (
                                        emission[0],
                                        emission[1],
                                        emission[2]
                                    ))



        shiny = mat.specular_intensity
        aniAttrs['shiny'][1][0] = ("%.3f" % shiny)
    
    for attr in aniAttrs:
        proc = aniAttrs[attr][0]
        proc(level, aniAttrs[attr][1], aniAttrs[attr][2])
        
        



    '''
    ani(level, "ATTR_diffuse_rgb	 0.608  0.610  0.574\n")
    ani(level, "ATTR_shade_smooth\n")
    ani(level, "ATTR_emission_rgb	 0.700  0.700  0.700\n")
    ani(level, "ATTR_shiny_rat	 0.5\n")
    ani(level, "ATTR_no_hard\n")
    ani(level, "ATTR_no_cull\n")
    ani(level, "ATTR_depth\n")
    ani(level, "ATTR_draw_enable\n")
    ani(level, "ATTR_solid_camera\n")
    ani(level, "ATTR_no_cockpit\n")
    '''
    ani(level, "TRIS\t%d\t%d\n" % (TRIS,len(myObj["faces"])))

def writef(o, w = 0):
    global F
    if w:
        o += "\n"
        fileW.write(o)
    else:
#        print(o)
        o += "\n"
        F += o
    return

def matrixVectorMul(vin, M, deltaLoc = Vector((0,0,0))):
    v = Vector()
    if type(vin) == mathutils.Vector:
        v = vin
    else:
        if "x" in vin:
            v.x = vin["x"]
        if "y" in vin:
            v.y = vin["y"]
        if "z" in vin:
            v.z = vin["z"]
    
    x =  v.x*M[0][0] + v.y*M[1][0] + v.z*M[2][0]
    y =  v.x*M[0][1] + v.y*M[1][1] + v.z*M[2][1]
    z =  v.x*M[0][2] + v.y*M[1][2] + v.z*M[2][2]
    
    
    return Vector((x,y,z))

def eulerToDegrees(e):
    return Vector((round(deg(e.x),4),round(deg(e.y),4),round(deg(e.z),4)))


def getObjectAnim(obj):
    coords = {0:"x",1:"y",2:"z",3:"w"}
    datapaths = {
                    "location":"loc",
                    "rotation_euler":"rot",
                    "pose.bones[\"Bone\"].location":"locBone",
                    "pose.bones[\"Bone\"].rotation_quaternion":"rotBoneQ",
                    "pose.bones[\"Bone\"].rotation_euler":"rotBone",
                }
    anim = {
            "loc":{},
            "rot":{},
            "datarefs":{},
           }
    adr = anim["datarefs"]
    usedframes = []
#    values = {}
    usedkeys = {}
    vkeys = {}
    
    if ( obj.animation_data and obj.animation_data.action and obj.animation_data.action.fcurves) and len(obj.xp.datarefs):


        curves = obj.animation_data.action.fcurves
        for curve in curves:
#            print(curve.data_path)
            sdatapath = curve.data_path.split(".")
            sdatapath = sdatapath[len(sdatapath)-1]
            if curve.data_path in datapaths:
                datapath = datapaths[curve.data_path]
                if curve.array_index in coords:
                    coord = coords[curve.array_index]
                    for keyframe in curve.keyframe_points:
                        co = Vector(keyframe.co)
                        if datapath == "rot":
                            co[1] = co.y
#                        print(datapath, coord, co)
                        if co.x not in usedkeys:
                            usedkeys[co.x] = {}
                        if datapath not in usedkeys[co.x]:
                            usedkeys[co.x][datapath] = {}
                        if coord in usedkeys[co.x][datapath]:
                            usedkeys[co.x][datapath][coord] += co.y
                        else:
                            usedkeys[co.x][datapath][coord] = co.y

                        if datapath == "rot" and "x" in usedkeys[co.x][datapath] and "y" in usedkeys[co.x][datapath] and "z" in usedkeys[co.x][datapath]:
#                            print("FULL ROT")
                            R = Vector((
                            round(deg(usedkeys[co.x][datapath]["x"])),
                            round(deg(usedkeys[co.x][datapath]["y"])),
                            round(deg(usedkeys[co.x][datapath]["z"]))
                            ))
                            R = matrixVectorMul(R,matrixX90)
#                            R[0] *= -1
                            R[1] *= -1
                            R[2] *= -1
                            usedkeys[co.x][datapath] = R
#                            print( R )

                        if datapath == "rotBoneQ"   and "x" in usedkeys[co.x][datapath] \
                                                    and "y" in usedkeys[co.x][datapath] \
                                                    and "z" in usedkeys[co.x][datapath] \
                                                    and "w" in usedkeys[co.x][datapath]:
#                            print("FULL ROTQ")
                            R = mathutils.Quaternion((
                                    usedkeys[co.x][datapath]["x"],
                                    usedkeys[co.x][datapath]["y"],
                                    usedkeys[co.x][datapath]["z"],
                                    usedkeys[co.x][datapath]["w"],
                                    )).to_euler()
                            R = Vector((
                            round(deg(R[0])),
                            round(deg(R[2])),
                            round(deg(R[1]))
                            ))
                            R = matrixVectorMul(R,matrixX90)
#                            R[0] *= -1
                            R[1] *= -1
                            R[2] *= -1
                            usedkeys[co.x][datapath] = R
#                            print(R)

                        if datapath in ("loc","locBone") and "x" in usedkeys[co.x][datapath] and "y" in usedkeys[co.x][datapath] and "z" in usedkeys[co.x][datapath]:
#                            print("FULL LOC")
                            R = Vector((
                            usedkeys[co.x][datapath]["x"],
                            usedkeys[co.x][datapath]["y"],
                            usedkeys[co.x][datapath]["z"]
                            ))
                            R = matrixVectorMul(R,matrixXMinus90)
#                            R[1] *= -1
                            usedkeys[co.x][datapath] = R
#                            print(R)



                    
        
        for dataref_index,dataref in enumerate(obj.xp.datarefs):
            dataref_path = dataref.path_from_id() + ".value"
            animType = dataref.anim_type

            if dataref.anim_type in ("show","hide"):
                if dataref_index not in adr:
                    adr[dataref_index] = {}
                    adr[dataref_index]["path"] = dataref.path
                    adr[dataref_index]["values"] = {}
                    values = adr[dataref_index]["values"]
                    if animType not in values:
                        values[animType] = {}
                    values[animType]["show_hide_v1"] = dataref.show_hide_v1
                    values[animType]["show_hide_v2"] = dataref.show_hide_v2

#            '''
            for curve_index,curve in enumerate(curves):
#                print(curve.group)
                if curve.group and curve.group.name == xpDatarefsGroup:
#                    print(curve.data_path , dataref_path, dataref)
                    if curve.data_path == dataref_path and dataref.path != "":
#                        print(dataref_index)
                        if dataref_index not in adr:
                            adr[dataref_index] = {}
                            adr[dataref_index]["path"] = dataref.path
                            adr[dataref_index]["values"] = {}
                            values = adr[dataref_index]["values"]
                        for keyframe in curve.keyframe_points:
                            if animType in ("transform"):
                                if animType not in values:
                                    values[animType] = {}
                                values[animType][int(keyframe.co.x)] = keyframe.co.y
                                if keyframe.co.x in usedkeys:
                                    for k in usedkeys[keyframe.co.x]:
                                        kk = str(k)
                                        if kk == "locBoneQ":
                                            kk = "loc"
                                        if kk == "rotBoneQ":
                                            kk = "rot"

                                        if kk in ("loc","rot"):
                                            if (kk) not in values:
                                                values[kk] = {}
#                                            if keyframe.co.x not in values[kk]:
#                                                values[kk][keyframe.co.x] = usedkeys[keyframe.co.x][k]
#                                            else:
#                                                values[kk][keyframe.co.x] += usedkeys[keyframe.co.x][k]
                                            if kk == "loc":
#                                                print(co)
                                                if keyframe.co.x not in anim[kk]:
                                                    anim[kk][keyframe.co.x] = usedkeys[keyframe.co.x][k]
                                                else:
                                                    anim[kk][keyframe.co.x] += usedkeys[keyframe.co.x][k]
                                
                                
                            usedframes.append(int(keyframe.co.x))
#                            print(keyframe.co)
#            '''

#    print(usedkeys)

#    '''
#    print(anim)

    if obj.type in ("ARMATURE"):
        oldmatrix = None
        diffe = Vector()
        for keyframe in usedframes:

            bpy.context.scene.frame_set(keyframe)

            mb = Matrix()
            if obj.pose:
                mb = obj.pose.bones[0].matrix_channel
            ma = obj.matrix_local
            matrix = mb * ma
            matrix[3] = (ma*mb)[3]
#            print("frame",keyframe)
#            print(matrix)
            if oldmatrix:


#                print(axisX)
#                print(axisY)
#                print(axisZ)


                
                olde = oldmatrix.to_euler()
                e = matrix.to_euler()
                diffe = Vector((e.x - olde.x, e.y - olde.y, e.z - olde.z))
                print()
                print("DIFFE")
                print(diffe)
#                print(eulerToDegrees(diffe))

                rotates = []
                rotA = eulerToDegrees(diffe)
                print(rotA)
                print(axisX)
                print(axisY)
                print(axisZ)

                print()

                if round(diffe.x,4) != 0:
                    rotates.append([axisX,rotA.x * 1,'x'])
                if round(diffe.y,4) != 0:
                    rotates.append([axisY,rotA.y * -1,'z'])
                if round(diffe.z,4) != 0:
                    rotates.append([axisZ,rotA.z * 1,'y'])
                
                
#                print(rotates)
                if rotates:
                    anim["rot"][str(oldkeyframe) + "-" + str(keyframe)] = rotates




                
                
#                print("matrix",matrix)
#                print("euler",eulerToDegrees(matrix.to_euler()))
#                print("diffmatrix",diffmatrix)
#                print("euler",eulerToDegrees(diffmatrix.to_euler()))
#                print(eulerToDegrees(matrix.to_euler()), eulerToDegrees(rotates))
#                print()
                
                
            else:
                anim["matrix"] = matrix
                axisX = Vector(obj.pose.bones[0].x_axis)
                axisY = Vector(obj.pose.bones[0].z_axis)
                axisZ = Vector(obj.pose.bones[0].y_axis)

                axisZ = matrixVectorMul(axisZ, matrix)
                axisY = matrixVectorMul(axisY, matrix)
                axisX = matrixVectorMul(axisX, matrix)

                axisX = matrixVectorMul(axisX,matrixXMinus90)
                axisY = matrixVectorMul(axisY,matrixXMinus90)
                axisZ = matrixVectorMul(axisZ,matrixXMinus90)
                
                
#            anim["loc"][keyframe] = matrix[3]
#            anim["rot"][keyframe] = matrix.to_euler()

            if keyframe in anim["loc"]:
                matco = Vector((matrix[3]))
                matco = matrixVectorMul(matco,matrixXMinus90)
                anim["loc"][keyframe] = matco
            print("MATCO")
            print(matrix)

            oldmatrix = Matrix(matrix)
            oldkeyframe = keyframe
    else:
        anim = {}

#    print(anim)

#    '''            
#    if anim["values"]["rot"]:
#        for i in anim["values"]["rot"]:
#            anim["values"]["rot"][i] = matrixVectorMul(anim["rot"][i],matrixX90)
#            anim["values"]["rot"][i].x *= -1
#            anim["values"]["rot"][i].y *= -1
#            anim["values"]["rot"][i].z *= -1
#    if anim["values"]["loc"]:
#        for i in anim["values"]["loc"]:
#            anim["values"]["loc"][i] = matrixVectorMul(anim["loc"][i],matrixXMinus90)
#            anim["values"]["loc"][i].y *= -1
#    if len(anim["values"]["rot"]) < 2 and len(anim["values"]["loc"]) < 2:
#        anim = {}

#    print(obj)
#    print()
#    print("ANIM")

#    print(obj.name)
#    print(anim)

    return anim


def getObjectFaces(objin, VTindex = 0):
    global texture_cockpit
    
    me_da = objin.data.copy() #copy data
    me_ob = objin.copy() #copy object
#    print(me_da)
#    print(me_ob)
    
    
    print("created",me_da,me_ob)
    obj = me_ob
    #note two copy two types else it will use the current data or mesh
    me_ob.data = me_da
    bpy.context.scene.objects.link(me_ob)#link the object to the scene #current object location
    for i in bpy.context.scene.objects: i.select = False #deselect all objects
    me_ob.select = True
    bpy.context.scene.objects.active = me_ob #set the mesh object to current
    bpy.ops.object.mode_set(mode='EDIT') #Operators
    bpy.ops.mesh.select_all(action='SELECT')#select all the face/vertex/edge
    bpy.ops.mesh.quads_convert_to_tris() #Operators
    bpy.context.scene.update()
    bpy.ops.object.mode_set(mode='OBJECT') # set it in object
    mesh = me_ob.to_mesh(bpy.context.scene, True, "PREVIEW")
    
    oldmesh = obj.data
    obj.data = mesh


    fd = []
    vd = []
    vdx = 0
    notexture = ""
#    print(obj.data.faces)
    for face in obj.data.faces:
        vertnum = 0
#        print(list(face.vertices))
        for vertice in face.vertices:
#            print(vertice)
            uvx = 0
            uvy = 0
            if len(obj.data.uv_textures) and len(obj.data.uv_textures[0].data):
                uf = obj.data.uv_textures[0].data[face.index]
                if uf.image:
                    image = uf.image.name
                    if texture_cockpit != "" and texture_cockpit != image:
                        print("Multiple cockpit images!")
                    texture_cockpit = image
                else:
                    notexture = "No texture for %s" % objin.name
                uvx = uf.uv[vertnum][0]
                uvy = uf.uv[vertnum][1]
            x = obj.data.vertices[vertice].co.x
            y = obj.data.vertices[vertice].co.y
            z = obj.data.vertices[vertice].co.z
            nx = obj.data.vertices[vertice].normal.x
            ny = obj.data.vertices[vertice].normal.y
            nz = obj.data.vertices[vertice].normal.z
            v = [x,y,z,nx,ny,nz,uvx,uvy]
#            print(x,y,z)
            vertnum+=1
            
            vindex = 0
            for vfind in vd:
                if vfind == v:
                    vertice = vindex
                    break
                vindex+=1
            else:
                vd.append(v)
                vertice = len(vd)-1
#            vd.append(v)
            fd.insert(0,vertice)
            vdx += 1

#    print(me_da)
#    print(me_ob)
#    print(mesh)


    print("deleting",me_da)

    bpy.context.scene.objects.active = me_ob
    
    bpy.ops.object.mode_set(mode='EDIT') #Operators
    bpy.ops.mesh.select_all(action='SELECT')#select all the face/vertex/edge
#    print(bpy.context.object.data)
    bpy.context.scene.update()
    bpy.ops.mesh.delete()
    
    me_ob.data = oldmesh
    bpy.context.scene.update()
    bpy.ops.mesh.select_all(action='SELECT')#select all the face/vertex/edge
#    print(bpy.context.object.data)
    bpy.ops.mesh.delete()
    

    bpy.ops.object.mode_set(mode='OBJECT') # set it in object

    print("deleting",me_ob)

    bpy.ops.object.delete()
#    bpy.context.scene.objects.unlink(me_ob)


    if notexture != "":
        print(notexture)
    return [vd,fd]

    
def verticesRotate(verts, M = None):
    global matrixXMinus90

    for i in range(0,len(verts)):
        vert = list(verts[i])
        xyz = Vector((vert[0],vert[1],vert[2]))
        nxyz = Vector((vert[3],vert[4],vert[5]))

        xyz = matrixVectorMul(xyz, M)
        xyz += Vector(M[3]).to_3d()
        xyz = matrixVectorMul(xyz, matrixXMinus90)

#        nxyz = matrixVectorMul(nxyz, M)
        nxyz = matrixVectorMul(nxyz, matrixXMinus90)

        vert[0] = xyz.x
        vert[1] = xyz.y
        vert[2] = xyz.z
        vert[3] = nxyz.x
        vert[4] = nxyz.y
        vert[5] = nxyz.z
        verts[i] = vert
    return

def addtab(level = 0):
    s = ""
    while level > 0:
        s += "\t"
        level-=1
    return s

def ani(level,s):
    global ANI
    ANI += addtab(level) + str(s)


def exportVertices(
        owner = None,
        xVTi = 0,
        allowparent = 0,
        level = 0,
        aniAttrs = initAniAttrs,
        parentObj = {   "have_anim":False,
                        "matrix":Matrix()
                    }
        ):
    global TRIS,TRISIZE,VTSIZE
    global expObj
    global efaces
    global VTi


    
    if owner == None:
        owner = expObj

    oldpObj = dict(parentObj)

    objects = bpy.context.scene.objects


    for objName in owner:

        pObj = dict(oldpObj)

        scObj = objects[objName]
        obj = objects[objName]
        scene = bpy.context.scene

#       if objName in expObj:  
#        myObj = expObj[objName]
        print("in",scObj.name)
        print(VTi)

        bpy.context.scene.frame_set(1)
        matrix = Matrix(scObj.matrix_local)# * pObj["matrix"]
        
#        print("OBJMATRIX")
#        print(matrix)
        m = Matrix(pObj["matrix"])
#        print("POBJMATRIX")
#        print(m)
        pscale = pObj["matrix"].to_scale()
#        print("PSCALE")
#        print(pscale)
        
        msc = matrix.to_scale()
#        print("SCALE")
#        print(msc)
        sc = Vector()
        sc.x = msc.x * pscale.x
        sc.y = msc.y * pscale.y
        sc.z = msc.z * pscale.z
#        print("GSCALE")
#        print(sc)
    


#        matrix[3].x *= sc.x
#        matrix[3].y *= sc.y
#        matrix[3].z *= sc.z
        
        m[3] = Vector().to_4d()
        matrix = m * matrix
#        matrix[3].x *= pscale.x
#        matrix[3].y *= pscale.y
#        matrix[3].z *= pscale.z


        sc = Vector((1,1,1))
        
#        print("ANIMATRIX")
#        print(matrix)
#        print(matrix.to_scale())
#        print(anim)
    
#        print("XXX")
#        print(pObj["matrix"])
#        print(scObj.matrix_local)
#        print(matrix)
    
#        parentObj["matrix"] = matrix


        anim = getObjectAnim(scObj)
        have_anim = len(anim)>0


        if have_anim:
            print(anim["loc"])

            ani(level, "# %s\n" % scObj.name)
            ani(level, "ANIM_begin\n")
            if ("datarefs") in anim:
#                for co in ('z','y','x'):
                if 1:
                    for dataref_key in anim["datarefs"]:
                        dataref = anim["datarefs"][dataref_key]
                        path = dataref["path"]
    
    
    
                        for value_key in dataref["values"]:
                            value = dataref["values"][value_key]
                            keyframes = list(value)
                            if value_key in ("show","hide"):
                                ani(level+1, "ANIM_%s\t%.2f\t%.2f\t%s\n" % (value_key, value["show_hide_v1"], value["show_hide_v2"], path))
    
    
                            if value_key == "transform":
                                loc = {}
                                rot = {}
                                if ("loc") in anim:
                                    loc = anim["loc"]
                                if ("rot") in anim:
                                    rot = anim["rot"]
                                    
                                '''
                                if len(value) > 2:
                                    if anim["loc"]:
                                        ani(level+1, "ANIM_trans_begin\t%s\n" % path)
                                        for k in keyframes:
                                            v = value[k]
                                            d = anim["loc"][k]
                                            ani(level+2, "ANIM_trans_key\t%.2f\t%.4f\t%.4f\t%.4f\n" % (v, d.x, d.y, d.z))
                                        ani(level+1, "ANIM_trans_end\n")
                                    
                                    if anim["rot"]:
    
                                        ani(level+1, "ANIM_rotate_begin\t0\t0\t1\t%s\n" % path)
                                        for k in keyframes:
                                            v = value[k]
                                            d = anim["rot"][k]
                                            ani(level+2, "ANIM_trans_key\t%.2f\t%.2f\n" % (v, deg(d.z)))
                                        ani(level+1, "ANIM_rotate_end\n")
    
                                        ani(level+1, "ANIM_rotate_begin\t0\t1\t0\t%s\n" % path)
                                        for k in keyframes:
                                            v = value[k]
                                            d = anim["rot"][k]
                                            ani(level+2, "ANIM_trans_key\t%.2f\t%.2f\n" % (v, deg(d.y)))
                                        ani(level+1, "ANIM_rotate_end\n")
    
                                        ani(level+1, "ANIM_rotate_begin\t1\t0\t0\t%s\n" % path)
                                        for k in keyframes:
                                            v = value[k]
                                            d = anim["rot"][k]
                                            ani(level+2, "ANIM_trans_key\t%.2f\t%.2f\n" % (v, deg(d.x)))
                                        ani(level+1, "ANIM_rotate_end\n")
                                '''


                                if len(value) > 2:
                                    pass
#                                    print(value)
#                                    print(rot)
#                                    print(loc)
#                                    print(path)

                                    '''
                                    print("VVVVVVVVVV")
                                    if rot:
                                        kf1 = keyframes[0]
                                        kf2 = keyframes[1]
                                        kf = str(kf1) + "-" + str(kf2)
                                        r = rot[kf]
                                        ani(level+1,
                                            "ANIM_rotate_begin\t%.4f\t%.4f\t%.4f\t%s\n" %
                                            (r[0][0].x, r[0][0].y, r[0][0].z, path)
                                            )
                                        ani(level+2,
                                            "ANIM_rotate_key\t%.2f\t%.2f\n" %
                                            (value[kf1],0)
                                            )
                                        oldrot = 0
                                        for i in range(1,len(keyframes)):
                                            kf2 = keyframes[i]
                                            kf = str(kf1) + "-" + str(kf2)
                                            val = value[kf2]
                                            
                                            if kf in rot:
                                                oldrot = rot[kf][0][1]
                                            print(kf, kf2, val, oldrot)
                                            ani(level+2,
                                                "ANIM_rotate_key\t%.2f\t%.2f\n" %
                                                (val, oldrot)
                                                )
                                            kf1 = kf2


                                        ani(level+1,
                                            "ANIM_rotate_end\n"
                                            )
                                    '''



#                                    print(co, "ROTI")
                                if len(rot) > 0:
                                    for co in ('z','y','x'):
                                        for k in range(0,len(keyframes)-1):
                                            kf1 = keyframes[k]
                                            kf2 = keyframes[k+1]
                                            kf = str(kf1) + "-" + str(kf2)
                                            if kf in rot:
                                                for kr in rot[kf]:
                                                    if kr[2] == co:
                                                        
                                                        
                                                        print(round(value[kf2],5),kr)
                                            
                                    
                                    
                                    
#                                    for roti in rot:
#                                        kf = str(keyframes[0]) + "-" + str(keyframes[1])
#                                        if roti == kf and co == rot[kf][0][2]:
#                                            v = rot[kf][0][0]
#                                            r = rot[kf][0][1]
#                                            v1 = value[keyframes[0]]
#                                            v2 = value[keyframes[1]]
#                                            ani(level+1, "ANIM_rotate\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.2f\t%.2f\t%s\n" %
#                                                        ( v.x,v.y,v.z,0,r,v1,v2,path ) )
    
                                if len(value) == 2:
                                    if len(loc) == 2 and keyframes[1] in loc and keyframes[0] in loc:
                                        v1 = value[keyframes[0]]
                                        v2 = value[keyframes[1]]
                                        k1 = loc[keyframes[0]]
                                        k2 = loc[keyframes[1]]
    #                                        matrixVectorMul(parentLocation, matrixX90) -= k1
                                        ani(level+1, "ANIM_trans\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.2f\t%.2f\t%s\n" %
                                                    (
                                                    k1.x*sc.x,k1.y*sc.y,k1.z*sc.z,
                                                    k2.x*sc.x,k2.y*sc.y,k2.z*sc.z,v1,v2,path ) )
                                        
                                            
                                            
                                            
#                                    if keyframes[1] in rot:
#                                        if co in rot[keyframes[1]][0][2]:
#                                            v1 = value[keyframes[0]]
#                                            v2 = value[keyframes[1]]
#                                            v = rot[keyframes[1]][0][0]
#                                            r = rot[keyframes[1]][0][1]
#                                            ani(level+1, "ANIM_rotate\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.2f\t%.2f\t%s\n" %
#                                                        ( v.x,v.y,v.z,0,r,v1,v2,path ) )
    
    
    #                            if len(rot) == 1:
    #                                v1 = value[keyframes[0]]
    #                                v2 = value[keyframes[1]]
    #                                k1 = rot[keyframes[0]]
    #                                k2 = rot[keyframes[1]]
    #                                v = rot[keyframes[1]][0][0]
    #                                r = rot[keyframes[1]][0][1]
    #                                ani(level+1, "ANIM_rotate\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.2f\t%.2f\t%s\n" %
    #                                            ( v.x,v.y,v.z,0,r,v1,v2,path ) )
    #                                ani(level+1, "ANIM_rotate\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.2f\t%.2f\t%s\n" %
    #                                            ( 1,0,0,k1.x,k2.x,v1,v2,path ) )
    #                                ani(level+1, "ANIM_rotate\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.2f\t%.2f\t%s\n" %
    #                                            ( 0,1,0,k1.y,k2.y,v1,v2,path ) )
    
    
                                    '''
                                    if keyframes[0] in anim["rot"] and keyframes[1] in anim["rot"]:
                                        k1 = anim["rot"][keyframes[0]]
                                        k2 = anim["rot"][keyframes[1]]
    #                                        if round(k1.z,6) != round(k2.z,6):
                                        ani(level+1, "ANIM_rotate\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.2f\t%.2f\t%s\n" %
                                                            ( 0,0,1,deg(k1.z),deg(k2.z),v1,v2,path ) )
    #                                        if round(k1.y,6) != round(k2.y,6):
                                        ani(level+1, "ANIM_rotate\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.2f\t%.2f\t%s\n" %
                                                            ( 0,1,0,deg(k1.y),deg(k2.y),v1,v2,path ) )
    #                                        if round(k1.x,6) != round(k2.x,6):
                                        ani(level+1, "ANIM_rotate\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.2f\t%.2f\t%s\n" %
                                                            ( 1,0,0,deg(k1.x),deg(k2.x),v1,v2,path ) )
                                    '''
    
    
                        dr = scObj.xp.datarefs[dataref_key]
                        if dr.loop != 0:
                            ani(level+1, "ANIM_keyframe_loop\t%.2f\n" % dr.loop)
        
            
#            if not have_anim and parent:
#                ani(level,"ANIM_begin\n")
#                level += 1
#                ani(level,"ANIM_trans\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.2f\t%.2f\t%s\n" %
#                         ( 1,0,0,1,0,0,0,0,"none" ) )


















        if scObj.type=="MESH" and obj.layers[0] and obj.is_visible(scene):
#            print("PARENT",scObj.parent)

        

            efaces[objName] = {}
            e = efaces[objName]
            vertsfaces = getObjectFaces(obj)
            e["verts"] = vertsfaces[0]
            e["faces"] = vertsfaces[1]
            e["verts_len"] = len(e["verts"])

            verts = list(e["verts"])
            faces = list(e["faces"])
            
            verticesRotate(verts,matrix)


            attr_manip = None
            m = scObj.xp.manip
            if m.enable:
                if m.type == "noop":
                    attr_manip = ""
                elif m.type == "drag_xy":
                    attr_manip = ( "%s\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%s\t%s\t%s" % (m.cursor, m.dx, m.dy, m.v1_min, m.v1_max, m.v2_min, m.v2_max, m.dataref1, m.dataref2, m.tooltip) )
                elif m.type == "drag_axis":
                    attr_manip = ( "%s\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%s\t%s" % (m.cursor, m.dx, m.dy, m.dz, m.v1, m.v2, m.dataref1, m.tooltip) )
                elif m.type == "command":
                    attr_manip = ( "%s\t%s\t%s" % (m.cursor, m.command, m.tooltip) )
                elif m.type == "command_axis":
                    attr_manip = ( "%s\t%.2f\t%.2f\t%.2f\t%s\t%s\t%s" % (m.cursor, m.dx, m.dy, m.dz, m.positive_command, m.negative_command, m.tooltip) )
                elif m.type == "push":
                    attr_manip = ( "%s\t%.2f\t%.2f\t%s\t%s" % (m.cursor, m.v_down, m.v_up, m.dataref1, m.tooltip) )
                elif m.type == "radio":
                    attr_manip = ( "%s\t%.2f\t%s\t%s" % (m.cursor, m.v_down, m.dataref1, m.tooltip) )
                elif m.type == "toggle":
                    attr_manip = ( "%s\t%.2f\t%.2f\t%s\t%s" % (m.cursor, m.v_on, m.v_off, m.dataref1, m.tooltip) )
                elif m.type == "delta":
                    attr_manip = ( "%s\t%.2f\t%.2f\t%.2f\t%.2f\t%s\t%s" % (m.cursor, m.v_down, m.v_hold, m.v1_min, m.v1_max, m.dataref1, m.tooltip) )
                elif m.type == "wrap":
                    attr_manip = ( "%s\t%.2f\t%.2f\t%.2f\t%.2f\t%s\t%s" % (m.cursor, m.v_down, m.v_hold, m.v1_min, m.v1_max, m.dataref1, m.tooltip) )
            if m.enable:
                ani(level + (have_anim>0), "ATTR_manip_" + m.type + "\t" + attr_manip + "\n")
            else:
                ani(level + (have_anim>0), "ATTR_manip_noop\n")



            writef("# %s %i" % (scObj.name,VTi))
            for v in verts:
                s =   ("VT\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f" %
                      (v[0],v[1],v[2],v[3],v[4],v[5],v[6],v[7]))
                writef(s)
                VTSIZE += 1
            e["verts_start"] = VTi
            VTi += len(verts)
            e["verts_exported"] = 1
            expOrder.append(scObj.name)





#            print("%%%%%%%%%%%")
#            print(VTi)
#            print(TRIS)

            writeTris(e, scObj, level+(have_anim>0), aniAttrs)
            TRIS += len(e["faces"])
            TRISIZE += len(e["faces"])/3



        if scObj.type == "ARMATURE":



            bones = {}
            for bone in scObj.children:
                if bone.name in objects:
                    o = objects[bone.name]
                    if o.layers[0] and o.is_visible(scene):
                        bones[bone.name] = {}
#            print("call", bones)

            pObj["matrix"] = matrix
            print("VTi", VTi)
            exportVertices(bones, VTi, 1, level + 1, aniAttrs, pObj)
            print("VTi", VTi)


    
#            if myObj["children"]:
#                childs = []
#                for child in myObj["children"]:
#                    childs.append(child.name)
#                exportVertices(childs, VTi, 1, level + (have_anim>0), aniAttrs, parentObj)
        if have_anim:
            ani(level, "ANIM_end\n")
#            if not have_anim and parent:
#                level -= 1
#                ani(level,"ANIM_end\n")


    return

    


def exportFaces():
    idx = []
    for objName in expOrder:
        myObj = efaces[objName]
        scObj = objects[objName]
        if myObj["verts_exported"]:
            vtindex = myObj["verts_start"]
            faces = myObj["faces"]
            for f in faces:
                idx.append(f + vtindex)
                if len(idx)>=10:
                    s = "IDX10"
                    for ix in idx:
                        s += "\t%i" % ix
                    writef(s)
                    idx = []
    if len(idx)>0:
        for i in idx:
            writef("IDX\t%i" % i)
    return






def GoExport():

    global efaces
    efaces = {}
    global objects
    global output_directory
    global output_filename
    global projectname 
    global texture_cockpit
    texture_cockpit = ""
    global ANI
    ANI = ""
    global F
    F = ""
    global VTindex
    VTindex = 0
    global VTSIZE
    VTSIZE = 0
    global TRISIZE
    TRISIZE = 0
    global TRIS
    TRIS = 0
    global VTi
    VTi = 0

    global expObj
    expObj = {}
    global expOrder
    expOrder = []

    if output_directory=="" or output_filename == "":
        print("Output file not defined!")
        return

    scene = bpy.context.scene
    objects = scene.objects
    activeObject = bpy.context.scene.objects.active
    currentFrame = bpy.context.scene.frame_current
#    bpy.context.scene.frame_set(1)

    print("Starting XPlaneNG Exporter")

    try:
        bpy.ops.object.mode_set(mode="OBJECT")
    except:
        pass

    global fileW
    fullpath = "%s%s%s" % (output_directory,os.path.sep,output_filename)
    fileW = open(fullpath , "w")

    for obj in objects:
        if obj.type=="MESH" and not obj.parent and obj.layers[0] and obj.is_visible(scene):
            expObj[obj.name] = {}
            e = expObj[obj.name]
    for obj in objects:
        if obj.type == "ARMATURE" and not obj.parent:
            expObj[obj.name] = {}


#            e["name"] = obj.name
#            e["children"] = obj.children
#            e["anim"] = {}
#            e["verts_exported"] = 0
#            e["rot"] = obj.rotation_euler
#            e["loc"] = obj.location
#            e["dloc"] = obj.delta_location


    for e in expObj:
        print(e)
    
    print("Exporting VT...")
    exportVertices()
    print("Exporting FACES...")
    exportFaces()
    print("Exporting ANIMATION DATA")
    writef(ANI)
    writef("I\n800\nOBJ\n",1)
    writef("TEXTURE\t%s" % texture_cockpit,1)
    writef("POINT_COUNTS\t%d\t%d\t%d\t%d" % (VTSIZE,0,0,TRISIZE*3) ,1)
    writef(F,1)
    fileW.close()
    
    
    if activeObject:
    #    print(activeObject.name)
        bpy.context.scene.objects[activeObject.name].select = True
        bpy.context.scene.objects.active = activeObject
    
    bpy.context.scene.frame_set(currentFrame)
    print("Exporting ended.")



def Register():
    global xpProp
    global xpExportDescr
#    print("Registering BLENDER2XPLANE CLASSES")
    bpy.utils.register_class(XPlaneNG_Manipulator)
    bpy.utils.register_class(XPlaneNG_Dataref)
    bpy.utils.register_class(XPlaneNG_ObjectSettings)
    bpy.utils.register_class(XPlaneNG_OBJECT_OT_xp_add_dataref)
    bpy.utils.register_class(XPlaneNG_OBJECT_OT_xp_remove_dataref)
    bpy.utils.register_class(XPlaneNG_OBJECT_OT_xp_add_dataref_keyframe)
    bpy.utils.register_class(XPlaneNG_OBJECT_OT_xp_remove_dataref_keyframe)
    bpy.utils.register_class(XPlaneNG_OBJECT_PROPS)
    bpy.types.Object.xp = bpy.props.PointerProperty(attr=xpProp, type=XPlaneNG_ObjectSettings, name=xpProp.upper(), description=xpExportDescr)


def Unregister():    
#    print("Unregistering BLENDER2XPLANE CLASSES")
    bpy.utils.unregister_class(XPlaneNG_OBJECT_PROPS)
    bpy.utils.unregister_class(XPlaneNG_OBJECT_OT_xp_add_dataref)
    bpy.utils.unregister_class(XPlaneNG_OBJECT_OT_xp_remove_dataref)
    bpy.utils.unregister_class(XPlaneNG_OBJECT_OT_xp_add_dataref_keyframe)
    bpy.utils.unregister_class(XPlaneNG_OBJECT_OT_xp_remove_dataref_keyframe)
    bpy.utils.unregister_class(XPlaneNG_ObjectSettings)
    bpy.utils.unregister_class(XPlaneNG_Dataref)
    bpy.utils.unregister_class(XPlaneNG_Manipulator)




if __name__ == "__main__":
#    Unregister()
    Register()
    GoExport()
#else:
#    print("IMPORTING MODULE [%s]" % (__name__))
#    Register()
#