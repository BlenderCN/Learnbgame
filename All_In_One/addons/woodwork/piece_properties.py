import bpy.utils
from bpy.props import (
    FloatProperty,
    EnumProperty,
    PointerProperty,
    FloatVectorProperty,
    StringProperty,
    BoolProperty,
    IntProperty
)
from bpy.types import (
    PropertyGroup
)


class WorkpieceDescription(PropertyGroup):
    piece_name = StringProperty(
        name="name",
        description="Workpiece name"
    )

    comments = StringProperty()

    cutting_list_type = EnumProperty(
        items=[
            (
                "none",
                "None / Special",
                "Nothing in particular"
            ),
            (
                "rail",
                "Rail",
                "Horizontal member of a frame"
            ),
            (
                "stile",
                "Stile",
                "Vertical member of a frame"
            ),
            # plinthe
            (
                "baseboard",
                "Baseboard",
                "A board functioning as the base of anything"
            ),
            # bordure
            (
                "skirting",
                "Skirting",
                ""
            ),
            (
                "breadboard end",
                "Breadboard end",
                "Narrow piece that is mechanically joined to the end of a larger panel"
            ),
            # latte / lamelle
            (
                "slat",
                "Slat",
                ""
            ),
            # etagere
            (
                "shelf",
                "Shelf plank",
                ""
            ),
            (
                "bead",
                "Bead",
                ""
            ),
            # moulure
            (
                "molding",
                "Molding",
                "Shaped strip"
            )
        ],
        name="cutting_list_type",
        default="none"
    )

    is_in_group = BoolProperty(
        name="Part of",
        description="This piece is in a part of a project",
        default=True
    )

    active_group_index = IntProperty(
        name="Active Group Index",
        description="Active group index",
        default=0
    )

    create_new_group = BoolProperty(
        name="Create a new project part",
        default=False
    )

    group_name = StringProperty(
        name="Part name",
        description="Part of the project this piece belongs to",
        maxlen=64
    )


class WorkpieceSize(PropertyGroup):
    thickness = FloatProperty(
        name="Thickness",
        description="Thickness value",
        min=0.0,
        default=0.02,
        subtype='DISTANCE',
        unit='LENGTH',
        precision=4,
        step=0.01)

    length = FloatProperty(
        name="Length",
        description="Length value",
        min=0.0,
        default=0.2,
        subtype='DISTANCE',
        unit='LENGTH',
        precision=4,
        step=0.01)

    width = FloatProperty(
        name="Width",
        description="Width value",
        min=0.0,
        default=0.05,
        subtype='DISTANCE',
        unit='LENGTH',
        precision=4,
        step=0.01)


class WorkpiecePosition(PropertyGroup):
    visible_surface = EnumProperty(
        items=[('edge grain',
                "Edge grain",
                "Set side of the board as front face"),
               ('end grain',
                "End grain",
                "Set end of the board as front face"),
               ('face grain',
                "Face grain",
                "Set the outside of the board as front face")
               ],
        name="Visible surface",
        default='edge grain')

    orientation = EnumProperty(
        items=[
            (
                'horizontal',
                "Horizontal",
                "Put visible surface horizontally",
                "RIGHT_ARROW",
                0
            ),
            (
                'vertical',
                "Vertical",
                "Put visible surface vertically",
                "DOWN_ARROW_HLT",
                1
            )
        ],
        name="Orientation",
        default='horizontal')

    view = EnumProperty(
        items=[('top',
                "Top",
                "Put visible surface in top view",
                "AXIS_TOP",
                0),
               ('front',
                "Front",
                "Put visible surface in front view",
                "AXIS_FRONT",
                1),
               ('right',
                "Right",
                "Put visible surface in right view",
                "AXIS_SIDE",
                2),
               ('align',
                "Align to view",
                "Align visible surface to active view",
                "VIEW3D",
                3)
               ],
        name="View",
        default='front')

    origin_type = EnumProperty(
        items=[
            (
                'center',
                "Object center",
                "Set object origin to it's center",
                "ROTATE",
                0
            ),
            (
                'corner',
                "Face corner",
                "Set object origin to a face's corner",
                "VERTEXSEL",
                1
            ),
            (
                'edge-centered',
                "Edge center",
                "Set object origin to an edge center",
                "EDGESEL",
                2
            ),
            (
                'face-centered',
                "Face center",
                "Set object origin to a face's center",
                "FACESEL",
                3
            )
        ],
        name="Origin type",
        default='center'
    )

    origin_corner = EnumProperty(
        items=[
            (
                'xminyminzmin',
                "Xmin-Ymin-Zmin",
                "Choose this corner's coordinates as origin",
                "",
                0
            ),
            (
                'xmaxyminzmin',
                "Xmax-Ymin-Zmin",
                "Choose this corner's coordinates as origin",
                "",
                1
            ),
            (
                'xminymaxzmin',
                "Xmin-Ymax-Zmin",
                "Choose this corner's coordinates as origin",
                "",
                2
            ),
            (
                'xmaxymaxzmin',
                "Xmax-Ymax-Zmin",
                "Choose this corner's coordinates as origin",
                "",
                3
            ),
            (
                'xminyminzmax',
                "Xmin-Ymin-Zmax",
                "Choose this corner's coordinates as origin",
                "",
                4
            ),
            (
                'xmaxyminzmax',
                "Xmax-Ymin-Zmax",
                "Choose this corner's coordinates as origin",
                "",
                5
            ),
            (
                'xminymaxzmax',
                "Xmin-Ymax-Zmax",
                "Choose this corner's coordinates as origin",
                "",
                6
            ),
            (
                'xmaxymaxzmax',
                "Xmax-Ymax-Zmax",
                "Choose this corner's coordinates as origin",
                "",
                7
            )
        ],
        name="Origin corner",
        default="xminyminzmin"
    )

    origin_edge = EnumProperty(
        items=[
            (
                "top-face-xmin",
                "Top Face grain - xmin",
                "Choose this edge's center coordinates as origin",
                "",
                0
            ),
            (
                "top-face-xmax",
                "Top Face grain - xmax",
                "Choose this edge's center coordinates as origin",
                "",
                1
            ),
            (
                "top-face-ymin",
                "Top Face grain - ymin",
                "Choose this edge's center coordinates as origin",
                "",
                2
            ),
            (
                "top-face-ymax",
                "Top Face grain - ymax",
                "Choose this edge's center coordinates as origin",
                "",
                3
            ),

            (
                "bottom-face-xmin",
                "Bottom Face grain - xmin",
                "Choose this edge's center coordinates as origin",
                "",
                4
            ),
            (
                "bottom-face-xmax",
                "Bottom Face grain - xmax",
                "Choose this edge's center coordinates as origin",
                "",
                5
            ),
            (
                "bottom-face-ymin",
                "Bottom Face grain - ymin",
                "Choose this edge's center coordinates as origin",
                "",
                6
            ),
            (
                "bottom-face-ymax",
                "Bottom Face grain - ymax",
                "Choose this edge's center coordinates as origin",
                "",
                7
            ),

            (
                "front-edge-xmin",
                "Front edge grain - xmin",
                "Choose this edge's center coordinates as origin",
                "",
                8
            ),
            (
                "front-edge-xmax",
                "Front edge grain - xmax",
                "Choose this edge's center coordinates as origin",
                "",
                9
            ),
            (
                "front-edge-zmin",
                "Front edge grain - zmin",
                "Choose this edge's center coordinates as origin",
                "",
                10
            ),
            (
                "front-edge-zmax",
                "Front edge grain - zmax",
                "Choose this edge's center coordinates as origin",
                "",
                11
            ),

            (
                "back-edge-xmin",
                "Back edge grain - xmin",
                "Choose this edge's center coordinates as origin",
                "",
                12
            ),
            (
                "back-edge-xmax",
                "Back edge grain - xmax",
                "Choose this edge's center coordinates as origin",
                "",
                13
            ),
            (
                "back-edge-zmin",
                "Back edge grain - zmin",
                "Choose this edge's center coordinates as origin",
                "",
                14
            ),
            (
                "back-edge-zmax",
                "Back edge grain - zmax",
                "Choose this edge's center coordinates as origin",
                "",
                15
            ),

            (
                "left-end-ymin",
                "Left end grain - ymin",
                "Choose this edge's center coordinates as origin",
                "",
                16
            ),
            (
                "left-end-ymax",
                "Left end grain - ymax",
                "Choose this edge's center coordinates as origin",
                "",
                17
            ),
            (
                "left-end-zmin",
                "Left end grain - zmin",
                "Choose this edge's center coordinates as origin",
                "",
                18
            ),
            (
                "left-end-zmax",
                "Left end grain - zmax",
                "Choose this edge's center coordinates as origin",
                "",
                19
            ),

            (
                "right-end-ymin",
                "Right end grain - ymin",
                "Choose this edge's center coordinates as origin",
                "",
                20
            ),
            (
                "right-end-ymax",
                "Right end grain - ymax",
                "Choose this edge's center coordinates as origin",
                "",
                21
            ),
            (
                "right-end-zmin",
                "Right end grain - zmin",
                "Choose this edge's center coordinates as origin",
                "",
                22
            ),
            (
                "right-end-zmax",
                "Right end grain - zmax",
                "Choose this edge's center coordinates as origin",
                "",
                23
            )
        ],
        name="Origin edge",
        default="top-face-xmin"
    )
    origin_face = EnumProperty(
        items=[
            (
                "face-top",
                "Face grain - top face",
                "Choose this face's center coordinates as origin",
                "",
                0
            ),
            (
                "face-bottom",
                "Face grain - bottom face",
                "Choose this face's center coordinates as origin",
                "",
                1
            ),
            (
                "edge-front",
                "Edge grain - Front face",
                "Choose this face's center coordinates as origin",
                "",
                2
            ),
            (
                "edge-back",
                "Edge grain - Back face",
                "Choose this face's center coordinates as origin",
                "",
                3
            ),
            (
                "end-left",
                "End grain - Left face",
                "Choose this face's center coordinates as origin",
                "",
                4
            ),
            (
                "end-right",
                "End grain - Right face",
                "Choose this face's center coordinates as origin",
                "",
                5
            )
        ],
        name="Origin face",
        default="end-left"
    )

    origin_location = EnumProperty(
        items=[
            (
                '3D cursor',
                "3D Cursor",
                "Set location to 3D cursor",
                "CURSOR",
                0
            ),
            (
                'center',
                "Center",
                "Set location to scene center",
                "EMPTY_DATA",
                1
            ),
            (
                'position',
                "Position",
                "Enter location coordinates",
                "MANIPUL",
                2
            ),
            (
                'selected',
                "Near selected",
                "Put piece near selected object",
                "BORDER_RECT",
                3
            )
        ],
        name="Origin location",
        default='3D cursor'
    )

    location_coordinates = FloatVectorProperty(
        name="Location",
        subtype="XYZ"
    )

    distance = FloatVectorProperty(
        name="Distance",
        description="Distance between the elements in BUs",
        subtype="XYZ",
        unit="LENGTH",
        default=(0.1, 0.0, 0.0))


class WorkpieceCount(PropertyGroup):
    count = IntProperty(
        name="Count",
        description="Number of pieces with same characteristics to use",
        min=1
    )

    use_same_mesh = BoolProperty(
        name="Use same mesh",
        description="Use the same mesh for each piece (modifying one will modify the others)",
        default=False
    )

    distance = FloatVectorProperty(
        name="Distance",
        description="Distance between the elements",
        subtype="XYZ",
        unit="LENGTH",
        default=(0.0, 0.0, 0.0))


class WorkpiecePropertyGroup(PropertyGroup):
    description_properties = PointerProperty(type=WorkpieceDescription)
    size_properties = PointerProperty(type=WorkpieceSize)
    position_properties = PointerProperty(type=WorkpiecePosition)
    count_properties = PointerProperty(type=WorkpieceCount)


def register():
    bpy.utils.register_class(WorkpieceCount)
    bpy.utils.register_class(WorkpieceDescription)
    bpy.utils.register_class(WorkpieceSize)
    bpy.utils.register_class(WorkpiecePosition)
    bpy.utils.register_class(WorkpiecePropertyGroup)


def unregister():
    bpy.utils.unregister_class(WorkpiecePropertyGroup)
    bpy.utils.unregister_class(WorkpiecePosition)
    bpy.utils.unregister_class(WorkpieceSize)
    bpy.utils.unregister_class(WorkpieceDescription)
    bpy.utils.unregister_class(WorkpieceCount)
