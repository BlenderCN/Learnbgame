"""BlenderFDS, FDS geometric props"""

import bpy
from blenderfds.types import *
from blenderfds.types.flags import *
from blenderfds import geometry
from blenderfds.fds.props import BFPropString

### scale_lenght
# Blender internally uses invariant units for length: Blender units.
# bpy.context.scene.unit_settings.scale_length property is used to display different scales
# When importing or exporting Blender offers its own units,

### Eg: 
# If scale_lenght = 0.10: 1 Bu is displayed as 10 cm, but exported as 1 Bu
# When exporting to FDS, Bus are multiplied by scale_lenght:
#   10cm displayed in Blender -> 1 Bu internally in Blender -> 1 * .10 = 10cm exported to FDS
# When importing to FDS, Bu are divided by scale_lenght:
#   10cm in FDS -> 10cm / .10 = 1 Bu internally in Blender -> 10cm displayed in Blender

### Common drawing routines

class BFPropGeometry(BFProp):
    items = "NONE",

    def _get_layout(self, layout, context, element):
        split = layout.split(.1)
        col1, col2 = split.row(), split.column(align=True)
        col1.label(text="{}:".format(self.label))
        return col2
        
    def _draw_body(self, layout, context, element):
        # Draw enum
        row = layout.row(align=True)
        for item in self.items: row.prop_enum(element, self.bpy_idname, item)
    
### XB

class BFPropXB(BFPropGeometry):
    items = "NONE", "BBOX", "VOXELS", "FACES", "PIXELS", "EDGES",

    # Generate VOXELS, PIXELS props UI
    def _draw_extra(self, layout, context, element):
        if element.bf_xb in ("VOXELS", "PIXELS"):
            row = layout.row()
            layout_export, layout_custom = row.column(), row.column()
            layout_export.prop(element, "bf_xb_custom_voxel", text="")
            row = layout_custom.row(align=True)
            row.prop(element, "bf_xb_voxel_size")
            layout_custom.active = element.bf_xb_custom_voxel
    
    # Format single value
    def _format_value(self, context, element, value):
        return "XB={0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{0[3]:.3f},{0[4]:.3f},{0[5]:.3f}".format(value)

    # Format multi values  
    def _format_idi(self, context, element, value, i):
        return "ID='{1}_{2}' XB={0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{0[3]:.3f},{0[4]:.3f},{0[5]:.3f}".format(value, element.name, i)

    def _format_idx(self, context, element, value, i):
        return "ID='{1}{0[0]:+.3f}' XB={0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{0[3]:.3f},{0[4]:.3f},{0[5]:.3f}".format(value, element.name)

    def _format_idy(self, context, element, value, i):
        return "ID='{1}{0[2]:+.3f}' XB={0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{0[3]:.3f},{0[4]:.3f},{0[5]:.3f}".format(value, element.name)

    def _format_idz(self, context, element, value, i):
        return "ID='{1}{0[4]:+.3f}' XB={0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{0[3]:.3f},{0[4]:.3f},{0[5]:.3f}".format(value, element.name)

    def _format_idxy(self, context, element, value, i):
        return "ID='{1}{0[0]:+.3f}{0[2]:+.3f}' XB={0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{0[3]:.3f},{0[4]:.3f},{0[5]:.3f}".format(value, element.name)

    def _format_idxz(self, context, element, value, i):
        return "ID='{1}{0[0]:+.3f}{0[4]:+.3f}' XB={0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{0[3]:.3f},{0[4]:.3f},{0[5]:.3f}".format(value, element.name)

    def _format_idyz(self, context, element, value, i):
        return "ID='{1}{0[2]:+.3f}{0[4]:+.3f}' XB={0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{0[3]:.3f},{0[4]:.3f},{0[5]:.3f}".format(value, element.name)

    def _format_idxyz(self, context, element, value, i):
        return "ID='{1}{0[0]:+.3f}{0[2]:+.3f}{0[4]:+.3f}' XB={0[0]:.3f},{0[1]:.3f},{0[2]:.3f},{0[3]:.3f},{0[4]:.3f},{0[5]:.3f}".format(value, element.name)
    
    _choose_format_multivalue = {
            "IDI" :   _format_idi,
            "IDX" :   _format_idx,
            "IDY" :   _format_idy,
            "IDZ" :   _format_idz,
            "IDXY" :  _format_idxy,
            "IDXZ" :  _format_idxz,
            "IDYZ" :  _format_idyz,
            "IDXYZ" : _format_idxyz,
        }
    
    def get_res(self, context, element, ui=False):
        # Init and check
        bf_xb = element.bf_xb
        if bf_xb not in self.items or ui: return None
        res = BFResult(sender=self)
        # Get coordinates
        xbs, msg = geometry.to_fds.ob_to_xbs(context, element)
        if msg: res.msgs.append(msg)
        if not xbs: return res
        # Correct for scale_lenght
        scale_length = context.scene.unit_settings.scale_length
        xbs = [[coo * scale_length for coo in xb] for xb in xbs]
        # xbs exists, prepare res.value, return res
        if len(xbs) == 1:
            # Format single value
            res.value = self._format_value(context, element, xbs[0])
        else:
            # Format multi value
            _format_multivalue = self._choose_format_multivalue[element.bf_id_suffix]
            res.value = [_format_multivalue(self, context, element, xb, i) for i, xb in enumerate(xbs)] # It's a class method
        return res

    def from_fds(self, context, element, value):
        # Correct for scale_lenght
        scale_length = context.scene.unit_settings.scale_length
        value = [coo / scale_length for coo in value]
        # Set value
        geometry.from_fds.xbs_to_ob(xbs=(value,), context=context, ob=element, bf_xb=element.bf_xb) # Send existing element.bf_xb for evaluation.
        # FUTURE: EDGE recognition!

def update_bf_xb_voxel_size(self, context):
    """Update function for bf_xb_voxel_size"""
    geometry.tmp.del_all_tmp_objects(context)

BFProp(
    idname = "bf_xb_custom_voxel",
    label = "Use custom settings",
    description = "Use custom settings for object voxelization/pixelization",
    flags = NOEXPORT | ACTIVEUI,
    bpy_idname = "bf_xb_custom_voxel",
    bpy_prop = bpy.props.BoolProperty,
    default = False,
    update = update_bf_xb_voxel_size,
)

BFProp(
    idname = "bf_xb_voxel_size",
    label = "Resolution",
    description = "Resolution for object voxelization/pixelization",
    flags = NOEXPORT | ACTIVEUI,
    bpy_idname = "bf_xb_voxel_size",
    bpy_prop = bpy.props.FloatProperty,
    # unit = "LENGTH", # correction for scale_length needed before exporting!
    step = 1,
    precision = 3,
    min = .001,
    max = 20.,
    default = .10,
    update = update_bf_xb_voxel_size,
)

class BFPropDefaultVoxelSize(BFProp):
    def _draw_body(self, layout, context, element):
        row = layout.row(align=True)
        row.prop(element, "bf_default_voxel_size")

BFPropDefaultVoxelSize(
    idname = "bf_default_voxel_size",
    label = "Default Resolution",
    description = "Default resolution for object voxelization/pixelization",
    flags = NOEXPORT | ACTIVEUI,
    bpy_idname = "bf_default_voxel_size",
    bpy_prop = bpy.props.FloatProperty,
    # unit = "LENGTH", # correction for scale_length needed before exporting!
    step = 1,
    precision = 3,
    min = .001,
    max = 20.,
    default = .10,
    update = update_bf_xb_voxel_size,
)

def update_bf_xb(self, context):
    """Update function for bf_xb"""
    # Del all tmp_objects, if self has one
    if self.bf_has_tmp: geometry.tmp.del_all_tmp_objects(context)
    # Set other geometries to compatible settings
    if self.bf_xb in ("VOXELS", "FACES", "PIXELS", "EDGES"):
        if self.bf_xyz == "VERTICES": self.bf_xyz = "NONE"
        if self.bf_pb == "PLANES": self.bf_pb = "NONE"

BFPropXB(
    idname = "bf_xb",
    label = "XB",
    description = "XB",
    fds_label = "XB",
    bf_props = ("bf_xb_custom_voxel", "bf_xb_voxel_size", ),
    bpy_idname = "bf_xb",
    bpy_prop = bpy.props.EnumProperty,
    items = (
        ("NONE", "None", "Not exported", 0),
        ("BBOX", "BBox", "Use object bounding box", 100),
        ("VOXELS", "Voxels", "Export voxels from voxelized solid object", 200),
        ("FACES", "Faces", "Faces, one for each face of this object", 300),
        ("PIXELS", "Pixels", "Export pixels from pixelized flat object", 400),
        ("EDGES", "Edges", "Segments, one for each edge of this object", 500),
        ),
    update = update_bf_xb,
)

class BFPropXBBBox(BFPropXB):
    items = "NONE", "BBOX",

BFPropXBBBox(
    idname = "bf_xb_bbox",
    label = "XB",
    description = "XB",
    fds_label = "XB",
    bpy_idname = "bf_xb",
)

class BFPropXBSolid(BFPropXB):
    items = "NONE", "BBOX", "VOXELS"

BFPropXBSolid(
    idname = "bf_xb_solid",
    label = "XB",
    description = "XB",
    fds_label = "XB",
    bpy_idname = "bf_xb",
)

class BFPropXBFaces(BFPropXB):
    items = "NONE", "FACES", "PIXELS"

BFPropXBFaces(
    idname = "bf_xb_faces",
    label = "XB",
    description = "XB",
    fds_label = "XB",
    bpy_idname = "bf_xb",
)

### XYZ

class BFPropXYZ(BFPropGeometry):
    items = "NONE", "CENTER", "VERTICES"

    # Format single value    
    def _format_value(self, context, element, value):
        return "XYZ={0[0]:.3f},{0[1]:.3f},{0[2]:.3f}".format(value)

    # Format multi values
    def _format_idi(self, context, element, value, i):
        return "ID='{1}_{2}' XYZ={0[0]:.3f},{0[1]:.3f},{0[2]:.3f}".format(value, element.name, i)

    def _format_idx(self, context, element, value, i):
        return "ID='{1}{0[0]:+.3f}' XYZ={0[0]:.3f},{0[1]:.3f},{0[2]:.3f}".format(value, element.name)

    def _format_idy(self, context, element, value, i):
        return "ID='{1}{0[1]:+.3f}' XYZ={0[0]:.3f},{0[1]:.3f},{0[2]:.3f}".format(value, element.name)

    def _format_idz(self, context, element, value, i):
        return "ID='{1}{0[2]:+.3f}' XYZ={0[0]:.3f},{0[1]:.3f},{0[2]:.3f}".format(value, element.name)

    def _format_idxy(self, context, element, value, i):
        return "ID='{1}{0[0]:+.3f}{0[1]:+.3f}' XYZ={0[0]:.3f},{0[1]:.3f},{0[2]:.3f}".format(value, element.name)

    def _format_idxz(self, context, element, value, i):
        return "ID='{1}{0[0]:+.3f}{0[2]:+.3f}' XYZ={0[0]:.3f},{0[1]:.3f},{0[2]:.3f}".format(value, element.name)

    def _format_idyz(self, context, element, value, i):
        return "ID='{1}{0[1]:+.3f}{0[2]:+.3f}' XYZ={0[0]:.3f},{0[1]:.3f},{0[2]:.3f}".format(value, element.name)

    def _format_idxyz(self, context, element, value, i):
        return "ID='{1}{0[0]:+.3f}{0[1]:+.3f}{0[2]:+.3f}' XYZ={0[0]:.3f},{0[1]:.3f},{0[2]:.3f}".format(value, element.name)
    
    _choose_format_multivalue = {
        "IDI" :   _format_idi,
        "IDX" :   _format_idx,
        "IDY" :   _format_idy,
        "IDZ" :   _format_idz,
        "IDXY" :  _format_idxy,
        "IDXZ" :  _format_idxz,
        "IDYZ" :  _format_idyz,
        "IDXYZ" : _format_idxyz,
    }
    
    def get_res(self, context, element, ui=False):
        # Init and check
        bf_xyz = element.bf_xyz
        if bf_xyz not in self.items or ui: return None
        res = BFResult(sender=self)
        # Get coordinates
        xyzs, msg = geometry.to_fds.ob_to_xyzs(context, element)
        if msg: res.msgs.append(msg)
        if not xyzs: return res
        # Correct for scale_lenght
        scale_length = context.scene.unit_settings.scale_length
        xyzs = [[coo * scale_length for coo in xyz] for xyz in xyzs]
        # xyzs exists, prepare res.value, return res
        if len(xyzs) == 1:
            # Format single value
            res.value = self._format_value(context, element, xyzs[0])
        else:
            # Format multi value
            _format_multivalue = self._choose_format_multivalue[element.bf_id_suffix]
            res.value = [_format_multivalue(self, context, element, xyz, i) for i, xyz in enumerate(xyzs)]
        return res

    def from_fds(self, context, element, value):
        # Correct for scale_lenght
        scale_length = context.scene.unit_settings.scale_length
        value = [coo / scale_length for coo in value]
        # Set value
        geometry.from_fds.xyzs_to_ob(xyzs=(value,), context=context, ob=element, bf_xyz=element.bf_xyz) # Send existing element.bf_xyz for evaluation

def update_bf_xyz(self, context):
    """On bf_prop["XYZ"] update"""
    # Del all tmp_objects, if self has one
    if self.bf_has_tmp: geometry.tmp.del_all_tmp_objects(context)
    # Set other geometries to compatible settings
    if self.bf_xyz == "VERTICES":
        if self.bf_xb in ("VOXELS", "FACES", "PIXELS", "EDGES"): self.bf_xb = "NONE"
        if self.bf_pb == "PLANES": self.bf_pb = "NONE"

BFPropXYZ(
    idname = "bf_xyz",
    label = "XYZ",
    description = "Set points",
    fds_label = "XYZ",
    bpy_idname = "bf_xyz",
    bpy_prop = bpy.props.EnumProperty,
    items = [
        ("NONE", "None", "Not exported", 0),
        ("CENTER", "Center", "Point, corresponding to the center point of this object", 100),
        ("VERTICES", "Vertices", "Points, one for each vertex of this object", 200),
        ],
    update = update_bf_xyz,
)

### PB

class BFPropPB(BFPropGeometry):
    items = "NONE", "PLANES"

    # Format single value
    def _format_value(self, context, element, value):
        return "PB{0[0]}={0[1]:.3f}".format(value)

    # Format multi values
    def _format_idi(self, context, element, value, i):
        return "ID='{1}_{2}' PB{0[0]}={0[1]:.3f}".format(value, element.name, i)

    def _format_idxyz(self, context, element, value, i):
        return "ID='{1}_{0[0]}{0[1]:+.3f}' PB{0[0]}={0[1]:.3f}".format(value, element.name)

    _choose_format_multivalue = {
        "IDI" :   _format_idi,
        "IDX" :   _format_idxyz,
        "IDY" :   _format_idxyz,
        "IDZ" :   _format_idxyz,
        "IDXY" :  _format_idxyz,
        "IDXZ" :  _format_idxyz,
        "IDYZ" :  _format_idxyz,
        "IDXYZ" : _format_idxyz,
    }

    def get_res(self, context, element, ui=False):
        # Init and check
        bf_pb = element.bf_pb
        if bf_pb not in self.items or ui: return None
        res = BFResult(sender=self)
        # Get coordinates
        pbs, msg = geometry.to_fds.ob_to_pbs(context, element)
        if msg: res.msgs.append(msg)
        if not pbs: return res
        # Correct for scale_lenght
        scale_length = context.scene.unit_settings.scale_length
        pbs = [[pb[0], pb[1] * scale_length] for pb in pbs]
        # pbs exists, prepare res.value, return res
        if len(pbs) == 1:
            # Format single value
            res.value = self._format_value(context, element, pbs[0])
        else:
            # Format multi value
            _format_multivalue = self._choose_format_multivalue[element.bf_id_suffix]
            res.value = [_format_multivalue(self, context, element, pb, i) for i, pb in enumerate(pbs)]
        return res

    def from_fds(self, context, element, value):
        # Correct for scale_lenght
        value = value / context.scene.unit_settings.scale_length
        # Set value
        pbs = ((self.fds_label[2], value),) # eg: (("X", 3.4),)
        geometry.from_fds.pbs_to_ob(pbs=pbs, context=context, ob=element, bf_pb=element.bf_pb) # Send existing element.bf_pb for evaluation
        
def update_bf_pb(self, context):
    """Update function for bf_pb"""
    # Del all tmp_objects
    if self.bf_has_tmp: geometry.tmp.del_all_tmp_objects(context)
    # Set other geometries to compatible settings
    if self.bf_pb == "PLANES":
        if self.bf_xb in ("VOXELS", "FACES", "PIXELS", "EDGES"): self.bf_xb = "NONE"
        if self.bf_xyz == "VERTICES": self.bf_xyz = "NONE"

# used for PBX, PBY, PBZ import trapping
BFPropPB(idname = "bf_pbx", fds_label = "PBX", flags = IMPORTONLY)
BFPropPB(idname = "bf_pby", fds_label = "PBY", flags = IMPORTONLY)
BFPropPB(idname = "bf_pbz", fds_label = "PBZ", flags = IMPORTONLY)

BFPropPB(
    idname = "bf_pb",
    label = "PB*",
    description = "Set planes",
    # fds_label = "PB",
    bf_props = ("bf_pbx", "bf_pby", "bf_pbz"),
    bpy_idname = "bf_pb",
    bpy_prop = bpy.props.EnumProperty,
    items = (
        ("NONE", "None", "Not exported", 0),
        ("PLANES", "Planes", "Planes, one for each face of this object", 100),
        ),
    update = update_bf_pb,
)
