"""BlenderFDS, FDS namelists"""

import bpy
from blenderfds.types import *
from blenderfds.types.flags import *

# FUTURE: evacuation namelists

### Scene namelists

class BFNamelistHead(BFNamelist):
    def get_my_res(self, context, element, ui=False):
        # Export free text file
        """

        :type element: object
        """
        if element.bf_head_free_text:
            if not element.bf_head_free_text in bpy.data.texts:
                raise BFException(sender=self, msg="Free text file not existing")
            else:
                value = bpy.data.texts[element.bf_head_free_text].as_string() + "\n! End of free text\n"
                msg = "Free text '{}' appended".format(element.bf_head_free_text)
        else: value, msg = None, None
        # No need for msg or value
        if ui: return None
        return BFResult(sender=self, value=value, msg=msg)

BFNamelistHead(
    idname = "bf_head",
    label = "HEAD",
    description = "FDS case header",
    fds_label = "HEAD",
    enum_id = 1001,
    bpy_type = bpy.types.Scene,
    bf_props = ("bf_head_chid", "bf_head_title", "bf_head_directory", "bf_head_free_text", "bf_default_voxel_size"),
)

BFNamelist(
    idname = "bf_time",
    label = "TIME",
    description = "Simulation time settings",
    fds_label = "TIME",
    enum_id = 1002,
    bpy_type = bpy.types.Scene,
    bf_prop_export = "bf_time_export",
    bf_props = ("bf_time_t_begin", "bf_time_t_end", "bf_time_setup_only", ),
    bf_prop_free = "bf_time_free",
)

BFNamelist(
    idname = "bf_misc",
    label = "MISC",
    description = "Miscellaneous parameters",
    fds_label = "MISC",
    enum_id = 1003,
    bpy_type = bpy.types.Scene,
    bf_prop_export = "bf_misc_export",
    bf_props = None,
    bf_prop_free = "bf_misc_free",
)

BFNamelist(
    idname = "bf_reac",
    label = "REAC",
    description = "Reaction",
    fds_label = "REAC",
    enum_id = 1004,
    bpy_type = bpy.types.Scene,
    bf_prop_export = "bf_reac_export",
    bf_props = ("bf_reac_fuel", "bf_reac_fyi", "bf_reac_formula", "bf_reac_co_yield", "bf_reac_soot_yield", "bf_reac_heat_of_combustion", "bf_reac_ideal", ),
    bf_prop_free = "bf_reac_free",
)

BFNamelist(
    idname = "bf_dump",
    label = "DUMP",
    description = "Output parameters",
    fds_label = "DUMP",
    enum_id = 1005,
    bpy_type = bpy.types.Scene,
    bf_prop_export = "bf_dump_export",
    bf_props = ("bf_dump_render_file", "bf_dump_nframes", ),
    bf_prop_free = "bf_dump_free",
)

BFNamelist(
    idname = "bf_tail",
    fds_label = "TAIL",
    flags = IMPORTONLY, # used to trap TAIL namelist
    bpy_type = bpy.types.Scene,
)

### Object namelists

BFNamelist(
    idname = "bf_obst",
    label = "OBST",
    description = "Obstruction",
    fds_label = "OBST",
    enum_id = 1000,
    bpy_type = bpy.types.Object,
    bf_prop_export = "bf_export",
    bf_props = ("bf_id", "bf_fyi", "bf_surf_id", "bf_obst_thicken", "bf_xb_solid",),
    bf_prop_free = "bf_free",
    bf_other = {"show_transparent": True},
)

BFNamelist(
    idname = "bf_hole",
    label = "HOLE",
    description = "Obstruction Cutout",
    fds_label = "HOLE",
    enum_id = 1009,
    bpy_type = bpy.types.Object,
    bf_prop_export = "bf_export",
    bf_props = ("bf_id", "bf_fyi", "bf_xb_solid",),
    bf_prop_free = "bf_free",
    bf_other = {"draw_type": "WIRE", "show_transparent": True},
)

BFNamelist(
    idname = "bf_vent",
    label = "VENT",
    description = "Boundary Condition Patch",
    fds_label = "VENT",
    enum_id = 1010,
    bpy_type = bpy.types.Object,
    bf_prop_export = "bf_export",
    bf_props = ("bf_id", "bf_fyi", "bf_surf_id", "bf_xb_faces", "bf_xyz", "bf_pb",),
	bf_prop_free = "bf_free",
    bf_other = {"show_transparent": True},
)

BFNamelist(
    idname = "bf_devc",
    label = "DEVC",
    description = "Device",
    fds_label = "DEVC",
    enum_id = 1011,
    bpy_type = bpy.types.Object,
    bf_prop_export = "bf_export",
    bf_props = ("bf_id", "bf_fyi", "bf_quantity", "bf_devc_setpoint", "bf_devc_initial_state", "bf_devc_latch", "bf_devc_prop_id", "bf_xb", "bf_xyz",),
    bf_prop_free = "bf_free",
    bf_other = {"show_transparent": True},
)

BFNamelist(
    idname = "bf_slcf",
    label = "SLCF",
    description = "Slice File",
    fds_label = "SLCF",
    enum_id = 1012,
    bpy_type = bpy.types.Object,
    bf_prop_export = "bf_export",
    bf_props = ("bf_id", "bf_fyi", "bf_quantity", "bf_slcf_vector", "bf_xb_faces", "bf_pb",),
    bf_prop_free = "bf_free",
    bf_other = {"hide": True, "show_transparent": True},
)

BFNamelist(
    idname = "bf_prof",
    label = "PROF",
    description = "Wall Profile Output",
    fds_label = "PROF",
    enum_id = 1013,
    bpy_type = bpy.types.Object,
    bf_prop_export = "bf_export",
    bf_props = ("bf_id", "bf_fyi", "bf_quantity", "bf_xyz",),
    bf_prop_free = "bf_free",
)

BFNamelist(
    idname = "bf_mesh",
    label = "MESH",
    description = "Domain of simulation",
    fds_label = "MESH",
    enum_id = 1014,
    bpy_type = bpy.types.Object,
    bf_prop_export = "bf_export",
    bf_props = ("bf_id", "bf_fyi", "bf_ijk", "bf_xb_bbox",),
    bf_prop_free = "bf_free",
    bf_other = {"draw_type": "WIRE"},
)

BFNamelist(
    idname = "bf_init",
    label = "INIT",
    description = "Initial condition",
    fds_label = "INIT",
    enum_id = 1015,
    bpy_type = bpy.types.Object,
    bf_prop_export = "bf_export",
    bf_props = ("bf_id", "bf_fyi", "bf_xb_solid", "bf_xyz",),
    bf_prop_free = "bf_free",
    bf_other = {"draw_type": "WIRE", "hide": True},
)

BFNamelist(
    idname = "bf_zone",
    label = "ZONE",
    description = "Pressure zone",
    fds_label = "ZONE",
    enum_id = 1016,
    bpy_type = bpy.types.Object,
    bf_prop_export = "bf_export",
    bf_props = ("bf_id", "bf_fyi", "bf_xb_bbox",),
    bf_prop_free = "bf_free",
    bf_other = {"draw_type": "WIRE", "hide": True},
)

class BFNamelistFree(BFNamelist):
    def _draw_body(self, layout, context, element):
        # Invert drawing order
        if self.bf_prop_free: self.bf_prop_free.draw(layout, context, element)
        for bf_prop in self.bf_props or tuple(): bf_prop.draw(layout, context, element)

BFNamelistFree(
    idname = "bf_free",
    label = "Free Namelist",
    description = None,
    fds_label = None,
    enum_id = 1007,
    bpy_type = bpy.types.Object,
    bf_prop_export = "bf_export",
    bf_props = ("bf_id", "bf_fyi", "bf_surf_id", "bf_xb", "bf_xyz", "bf_pb",),
    bf_prop_free = "bf_free_namelist",
    bf_other = {"show_transparent": True},
)

### Material namelists

class BFNamelistSurf(BFNamelist):
    def get_my_res(self, context, element, ui=False) -> "BFResult or None":
        if not self.get_exported(context, element): return None
        if ui and len(context.active_object.material_slots) > 1: msg = "Several material slots available, using active material only. "
        else: msg = None
        return BFResult(
            sender = self,
            value = None, 
            msg = msg, 
        )

BFNamelistSurf(
    idname = "bf_surf",
    label = "SURF",
    description = "Generic Boundary Condition",
    fds_label = "SURF",
    enum_id = 2000,
    bpy_type = bpy.types.Material,
    bf_prop_export = "bf_export",
    bf_props = ("bf_id_ma", "bf_fyi", "bf_rgb", "bf_transparency", "bf_matl_id", ),
    bf_prop_free = "bf_free",
)

BFNamelistSurf(
    idname = "bf_surf_burner",
    label = "SURF",
    description = "Spec'd rate burner",
    fds_label = "SURF",
    enum_id = 2001,
    bpy_type = bpy.types.Material,
    bf_prop_export = "bf_export",
    bf_props = ("bf_id_ma", "bf_fyi", "bf_rgb", "bf_transparency", "bf_hrrpua", "bf_tau_q", ),
    bf_prop_free = "bf_free",
)

BFNamelistSurf(
    idname = "bf_surf_solid",
    label = "SURF",
    description = "Spec'd rate burning solid",
    fds_label = "SURF",
    enum_id = 2002,
    bpy_type = bpy.types.Material,
    bf_prop_export = "bf_export",
    bf_props = ("bf_id_ma", "bf_fyi", "bf_rgb", "bf_transparency", "bf_hrrpua", "bf_tau_q", "bf_matl_id", "bf_ignition_temperature", "bf_thickness", ),
    bf_prop_free = "bf_free",
)
