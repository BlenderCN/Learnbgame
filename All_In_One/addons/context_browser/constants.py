import bpy

LIST_ROW_SCALE_Y = 0.95
TOOLTIP_LEN = 40

ICON_UNKNOWN = 'LAYER_USED'
ICON_FUNC = 'OUTLINER_OB_FONT'
ICON_FOLDER = 'FILE_FOLDER'
ICON_PROP = 'OUTLINER_OB_GROUP_INSTANCE'
ICON_NONE = 'FILE_FOLDER'
ICON_ON = 'CHECKBOX_HLT'
ICON_OFF = 'CHECKBOX_DEHLT'
ICON_COL = 'GROUP'

ICONS = (
    ("FOLDER", "Struct", ICON_FOLDER),
    ("builtin_function_or_method", "Function", ICON_FUNC),
    ("bpy_func", "Function or Method", ICON_FUNC),
    ("method", "Function", ICON_FUNC),
    ("NoneType", "None", ICON_NONE),
    ("bool", "Boolean", 'MESH_PLANE'),
    ("int", "Int", 'MESH_CUBE'),
    ("float", "Float", 'MATSPHERE'),
    ("enum", "Enum", 'MESH_GRID'),
    ("str", "String", 'SORTALPHA'),
    ("string", "String", 'MESH_MONKEY'),
    ("Vector", "Vector", 'MAN_TRANS'),
    ("list", "List", ICON_FOLDER),
    ("tuple", "Tuple", ICON_FOLDER),
)

ICONS_MAP = {id: (label, icon) for id, label, icon in ICONS}

VPROPERTIES = (
    bpy.types.BoolProperty,
    bpy.types.IntProperty,
    bpy.types.FloatProperty,
    bpy.types.EnumProperty,
    bpy.types.StringProperty,
)


def get_icon(id):
    return ICONS_MAP[id][1] if id in ICONS_MAP else ICON_UNKNOWN


def get_bool_icon(value):
    return ICON_ON if value else ICON_OFF