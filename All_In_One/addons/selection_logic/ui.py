import bpy
from math import pi
from bpy.props import *
from . operators import selectVertices

selectionConditionTypes = [
    ("MASK", "Mask", "Use a custom mask", "NONE", 0),
    ("IN_RANGE", "In Range", "Vertices are in the given range", "NONE", 1),
    ("DIRECTION", "Direction", "The angles that vertices normals makes with the given vector are in a the given range", "NONE", 2)
]
rangeTypes = [
    ("MIN_MAX", "Min / Max", "Define range using maximum and minimum.", "NONE", 0),
    ("CENTER_SCALE", "Center / Scale", "Define range using center and scale.", "NONE", 1)
]
angleTypes = [
    ("MIN_MAX", "Min / Max", "Define range using maximum and minimum angles", "NONE", 0),
    ("START_RANGE", "Start / Range", "Define range using start and range angles", "NONE", 1)
]

def autoUpdate(self, context):
    if context.active_object.auto_update:
        selectVertices(context)

class SelectionConditionOptions(bpy.types.PropertyGroup):
    name = StringProperty(update = autoUpdate)
    expanded = BoolProperty(default = True)
    type = EnumProperty(name = "Type", items = selectionConditionTypes, default = "MASK",
                        update = autoUpdate)
    invert = BoolProperty(name = "Invert", default = False, update = autoUpdate)

    # Mask.
    identifier = StringProperty()
    outDated = BoolProperty(default = False)

    # In Range.
    rangeType = EnumProperty(name = "Type", items = rangeTypes, default = "CENTER_SCALE",
                             update = autoUpdate)
    minVector = FloatVectorProperty(name = "Min", subtype = "XYZ", update = autoUpdate)
    maxVector = FloatVectorProperty(name = "Max", subtype = "XYZ", update = autoUpdate)
    centerVector = FloatVectorProperty(name = "Center", subtype = "XYZ", update = autoUpdate)
    scaleVector = FloatVectorProperty(name = "Scale", subtype = "XYZ", update = autoUpdate)

    # Direction.
    angleType = EnumProperty(name = "Type", items = angleTypes, default = "MIN_MAX",
                             update = autoUpdate)
    direction = FloatVectorProperty(subtype = "DIRECTION", default=(0,0,1), update = autoUpdate)
    minAngle = FloatProperty(name = "Min", unit = "ROTATION", soft_min = 0, soft_max = pi,
                             update = autoUpdate)
    maxAngle = FloatProperty(name = "Max", unit = "ROTATION", soft_min = 0, soft_max = pi,
                             update = autoUpdate)
    startAngle = FloatProperty(name = "Start", unit = "ROTATION", soft_min = 0, soft_max = pi,
                                update = autoUpdate)
    angleRange = FloatProperty(name = "Range", unit = "ROTATION", soft_min = 0, soft_max = pi,
                               update = autoUpdate)

class ObjectSelectPanel(bpy.types.Panel):
    bl_idname = "MESH_PT_selection_conditions"
    bl_label = "Selection Conditions"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "mesh_edit"

    def draw(self, context):
        layout = self.layout
        object = context.active_object

        column = layout.column()
        for index, condition in enumerate(object.selection_conditions):
            box = column.box()
            drawHeader(condition, box, index)

            if condition.expanded:
                box.prop(condition, "type", text="")
                if condition.type == "MASK":
                    drawMask(condition, box, index)
                elif condition.type == "IN_RANGE":
                    drawInRange(condition, box)
                elif condition.type == "DIRECTION":
                    drawDirection(condition, box)
                box.prop(condition, "invert", toggle = True)

        column.operator("mesh.add_selection_condition", text="", icon='PLUS')

        layout.separator()
        column = layout.column()
        column.label("Expression:")
        column.prop(object, "selection_expression", text="")
        row = column.row(True)
        row.operator("mesh.select_by_expression", text="Select")
        row.prop(object, "auto_update", text="", icon= "AUTO")
        if object.invalid_expression:
            layout.label("Invalid Expression!")

def drawHeader(condition, box, index):
    row = box.row()
    row.operator("mesh.collapse_selection_condition", text="",
        icon='TRIA_DOWN' if condition.expanded else 'TRIA_RIGHT', emboss = False).index = index
    row.prop(condition, "name", text = "")
    row.operator("mesh.remove_selection_condition", text="", icon='X', emboss = False).index = index

def drawMask(condition, box, index):
    box.operator("mesh.update_selection_mask").index = index
    if condition.outDated:
        box.label("Mask is outdated!")

def drawInRange(condition, box):
    isMinMax = condition.rangeType == "MIN_MAX"
    box.prop(condition, "rangeType", text="")
    row = box.row()
    column = row.column()
    column.prop(condition, "minVector" if isMinMax else "centerVector")
    column = row.column()
    column.prop(condition, "maxVector" if isMinMax else "scaleVector")

def drawDirection(condition, box):
    isMinMax = condition.angleType == "MIN_MAX"
    box.prop(condition, "direction", text="")
    box.prop(condition, "angleType", text="")
    row = box.row(True)
    row.prop(condition, "minAngle" if isMinMax else "startAngle")
    row.prop(condition, "maxAngle" if isMinMax else "angleRange")

classes = [ObjectSelectPanel, SelectionConditionOptions]
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.auto_update = BoolProperty(default = True)
    bpy.types.Object.invalid_expression = BoolProperty(default = False)
    bpy.types.Object.selection_conditions = CollectionProperty(type=SelectionConditionOptions)
    bpy.types.Object.selection_expression = StringProperty(update = autoUpdate,
                                                           options ={"TEXTEDIT_UPDATE"})

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Object.auto_update
    del bpy.types.Object.selection_conditions
    del bpy.types.Object.selection_expression
