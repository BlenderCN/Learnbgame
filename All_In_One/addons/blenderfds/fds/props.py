"""BlenderFDS, FDS props"""

import re, os.path, bpy
from blenderfds.types import *
from blenderfds.types.flags import *
from blenderfds.lib import fds_mesh, fds_tables
from blenderfds import geometry

### Common special BFProp
        
class BFPropString(BFProp):
    def get_value(self, context, element):
        # Check strings
        value = super().get_value(context, element)
        if not value: return
        err_msgs = list()
        if '&' in value or '/' in value:
            err_msgs.append("& and / characters not allowed")
        if "'" in value or '"' in value or "`" in value or "“" in value \
            or "”" in value or "‘" in value or "’‌" in value:
            err_msgs.append("Quote characters not allowed")
        if err_msgs: raise BFException(sender=self, msgs=err_msgs)
        return value    

    def _format_value(self, context, element, value) -> "str or None":
        # Expected output: ID='example'
        if not value: return None
        if not self.fds_label: return str(value)
        return "{}='{}'".format(self.fds_label, value)
        
### General BFProp

BFProp(
    idname = "bf_export",
    label = "Export",
    description = "Export element to FDS",
    bpy_idname = "bf_export", # system property, see extensions.py
)

class BFPropFYI(BFPropString):
    def _draw_body(self, layout, context, element):
        row = layout.row()
        row.prop(element, self.bpy_idname, text="", icon="INFO")

BFPropFYI(
    idname = "bf_fyi",
    label = "FYI",
    description = "Object description",
    fds_label = "FYI",
    bpy_idname = "bf_fyi", # system property, see extensions.py
)

class BFPropFree(BFProp):
    def get_value(self, context, element):
        value = super().get_value(context, element)
        if not value: return
        err_msgs = list()
        if '&' in value or '/' in value:
            err_msgs.append("& and / characters not allowed")
        if "`" in value or "‘" in value or "’‌" in value or '"' in value or "”" in value or value.count("'") % 2 != 0:
            err_msgs.append("Only use matched single quotes as 'string' delimiters")
        if err_msgs: raise BFException(sender=self, msgs=err_msgs)
        return value

    def _draw_body(self, layout, context, element):
        row = layout.row()
        row.prop(element, self.bpy_idname, text="", icon="TEXT")

    def _format_value(self, context, element, value) -> "str or None":
        if value: return str(value)

BFPropFree(
    idname = "bf_free",
    label = "Free Parameters",
    description = "Free parameters, use matched single quotes as string delimiters, eg ABC='example'",
    bpy_idname = "bf_free", # system property, see extensions.py
)

### Scene

class BFPropCHID(BFPropString):
    def _draw_body(self, layout, context, element):
        row = layout.row()
        row.template_ID(context.screen, "scene", new="scene.new", unlink="scene.delete")
        # row.prop(element, "name", text="", icon="COPY_ID") FIXME

    def get_value(self, context, element):
        value = super().get_value(context, element)
        if value and bpy.path.clean_name(value) != value:
            raise BFException(self, msg="Illegal characters in filename")
        return value

BFPropCHID(
    idname = "bf_head_chid",
    label = "CHID",
    description = "Case identificator",
    fds_label = "CHID",
    bpy_idname = "name",
)

BFPropFYI(
    idname = "bf_head_title",
    label = "TITLE",
    description = "Case description",
    fds_label = "TITLE",
    bpy_idname = "bf_head_title",
    bpy_prop = bpy.props.StringProperty,
    maxlen = 64,
)

class BFPropPath(BFProp):
    def get_value(self, context, element):
        value = super().get_value(context, element)
        if value and not os.path.exists(bpy.path.abspath(value)):
            raise BFException(self, msg="Path not existing")
        return value

BFPropPath(
    idname = "bf_head_directory",
    label = "Case Directory",
    description = "Case directory",
    flags = NOEXPORT | ACTIVEUI,
    bpy_idname = "bf_head_directory",
    bpy_prop = bpy.props.StringProperty,
    subtype = "DIR_PATH",
    maxlen = 1024,
)

class BFPropText(BFProp):
    def _draw_body(self, layout, context, element):
        row = layout.row(align=True)
        row.prop_search(element, self.bpy_idname, bpy.data, "texts")
        row.operator("scene.bf_edit_head_free_text", icon="FILESEL", text="")

BFPropText(
    idname = "bf_head_free_text",
    label = "Free Text File",
    description = "Name of the free text file appended to the HEAD namelist",
    flags = NOEXPORT | ACTIVEUI,
    bpy_idname = "bf_head_free_text",
    bpy_prop = bpy.props.StringProperty,
)

BFProp(
    idname = "bf_time_t_begin",
    label = "T_BEGIN [s]",
    description = "Simulation starting time",
    fds_label = "T_BEGIN",
    bpy_idname = "bf_time_t_begin",
    bpy_prop = bpy.props.FloatProperty,
    unit = "TIME",
    step = 100.,
    precision = 1,
    min = 0.,
    default = 0.,
)

class BFPropTEND(BFProp):
    def get_exported(self, context, element):
        return not element.bf_time_setup_only

BFPropTEND(
    idname = "bf_time_t_end",
    label = "T_END [s]",
    description = "Simulation ending time",
    fds_label = "T_END",
    bpy_idname = "bf_time_t_end",
    bpy_prop = bpy.props.FloatProperty,
    unit = "TIME",
    step = 100.,
    precision = 1,
    min = 0.,
    default= 0.,
)

class BFPropTimeSetupOnly(BFProp):
    def get_my_res(self, context, element, ui=False):
        # if SMV setup only, bf_time_t_end = bf_time_t_begin
        if element.bf_time_setup_only and not ui:
            return BFResult(
                sender = self,
                value = "T_END={}".format(element.bf_time_t_begin),
                msg = "Set" # This message does not appear on ui
            )    

BFPropTimeSetupOnly(
    idname = "bf_time_setup_only",
    label = "Smokeview Setup Only",
    description = "Perform Smokeview setup only",
    bpy_idname = "bf_time_setup_only",
    bpy_prop = bpy.props.BoolProperty,
    default = False,
)

BFPropFree(
    idname = "bf_time_free",
    label = "Free Parameters",
    description = "Free parameters, use matched single quotes as string delimiters, eg ABC='example'",
    bpy_idname = "bf_time_free",
    bpy_prop = bpy.props.StringProperty,
    maxlen = 1024,
)

class BFPropDumpRenderFile(BFProp):
    def get_value(self, context, element):
        if element.bf_dump_render_file: return bpy.path.clean_name(element.name) + ".GE1" # FUTURE: this is hardcoded, improve!

    def set_value(self, context, element, value):
        if value: element.bf_dump_render_file = True

BFPropDumpRenderFile(
    idname = "bf_dump_render_file",
    label = "Export Geometric Description File",
    description = "Export geometric description file GE1",
    fds_label = "RENDER_FILE",
    bpy_idname = "bf_dump_render_file",
    bpy_prop = bpy.props.BoolProperty,
    default = True,
)

class BFPropNFRAMES(BFProp):
    def get_my_res(self, context, element, ui=False):
        if not self.get_exported(context, element): return None
        return BFResult(
            sender = self,
            value = self._format_value(context, element, element.bf_dump_nframes),
            msg = "Output is dumped every {:.2f} s".format(
                (element.bf_time_t_end - element.bf_time_t_begin) / element.bf_dump_nframes # bf_dump_nframes != 0, its min is 1
            ),
        )

BFPropNFRAMES(
    idname = "bf_dump_nframes",
    label = "NFRAMES",
    description = "Number of output dumps per calculation",
    fds_label = "NFRAMES",
    bf_prop_export = "bf_dump_nframes_export",
    bpy_idname = "bf_dump_nframes",
    bpy_prop = bpy.props.IntProperty,
    min = 1,
    default = 1000,
)

BFPropFree(
    idname = "bf_dump_free",
    label = "Free Parameters",
    description = "Free parameters, use matched single quotes as string delimiters, eg ABC='example'",
    bpy_idname = "bf_dump_free",
    bpy_prop = bpy.props.StringProperty,
    maxlen = 1024,
)

BFPropFree(
    idname = "bf_misc_free",
    label = "Free Parameters",
    description = "Free parameters, use matched single quotes as string delimiters, eg ABC='example'",
    bpy_idname = "bf_misc_free",
    bpy_prop = bpy.props.StringProperty,
    maxlen = 1024,
)

BFPropString(
    idname = "bf_reac_fuel",
    label = "FUEL",
    description = "Identificator of fuel species",
    fds_label = "FUEL",
    bpy_idname = "bf_reac_fuel",
    bpy_prop = bpy.props.StringProperty,
    maxlen = 32,
)

BFPropFYI(
    idname = "bf_reac_fyi",
    label = "FYI",
    description = "Namelist description",
    fds_label = "FYI",
    bpy_idname = "bf_reac_fyi",
    bpy_prop = bpy.props.StringProperty,
    maxlen = 128,
)

BFPropString(
    idname = "bf_reac_formula",
    label = "FORMULA",
    description = "Chemical formula of fuel species, it can only contain C, H, O, or N",
    fds_label = "FORMULA",
    bf_prop_export = "bf_reac_formula_export",
    bpy_idname = "bf_reac_formula",
    bpy_prop = bpy.props.StringProperty,
    maxlen = 32,
)

BFProp(
    idname = "bf_reac_co_yield",
    label = "CO_YIELD [kg/kg]",
    description = "Fraction of fuel mass converted into carbon monoxide",
    fds_label = "CO_YIELD",
    bf_prop_export = "bf_reac_co_yield_export",
    bpy_idname = "bf_reac_co_yield",
    bpy_prop = bpy.props.FloatProperty,
    step = 1.,
    precision = 6,
    min = 0.,
    max = 1.,
    default = 0.,
)

BFProp(
    idname = "bf_reac_soot_yield",
    label = "SOOT_YIELD [kg/kg]",
    description = "Fraction of fuel mass converted into smoke particulate",
    fds_label = "SOOT_YIELD",
    bf_prop_export = "bf_reac_soot_yield_export",
    bpy_idname = "bf_reac_soot_yield",
    bpy_prop = bpy.props.FloatProperty,
    step = 1.,
    precision = 6,
    min = 0.,
    max = 1.,
    default = 0.,
)

BFProp(
    idname = "bf_reac_heat_of_combustion",
    label = "HEAT_OF_COMBUSTION [kJ/kg]",
    description = "Fuel heat of combustion",
    fds_label = "HEAT_OF_COMBUSTION",
    bf_prop_export = "bf_reac_heat_of_combustion_export",
    bpy_idname = "bf_reac_heat_of_combustion",
    bpy_prop = bpy.props.FloatProperty,
    step = 100000.,
    precision = 1,
    min = 0.,
    default = 0.,
)

BFProp(
    idname = "bf_reac_ideal",
    label = "IDEAL",
    description = "Set ideal heat of combustion to .TRUE.",
    fds_label = "IDEAL",
    bpy_idname = "bf_reac_ideal",
    bpy_prop = bpy.props.BoolProperty,
    default = False,
)

BFPropFree(
    idname = "bf_reac_free",
    label = "Free Parameters",
    description = "Free parameters, use matched single quotes as string delimiters, eg ABC='example'",
    bpy_idname = "bf_reac_free",
    bpy_prop = bpy.props.StringProperty,
    maxlen = 1024,
)

### Object

BFProp( # Useful for bpy_props_copy operator
    idname = "bf_show_transparent",
    label = "Show Object Transparency",
    description = "Show Object Transparency",
    flags = NOUI | NOEXPORT,
    bpy_idname = "show_transparent",
)

BFProp( # Useful for bpy_props_copy operator
    idname = "bf_draw_type",
    label = "Draw Type",
    description = "Draw type",
    flags = NOUI | NOEXPORT,
    bpy_idname = "draw_type",
)

BFProp( # Useful for bpy_props_copy operator
    idname = "bf_hide",
    label = "Hide",
    description = "Hide object",
    flags = NOUI | NOEXPORT,
    bpy_idname = "hide",
)

BFProp( # Useful for bpy_props_copy operator
    idname = "bf_hide_select",
    label = "Hide From Selection",
    description = "Hide from selection",
    flags = NOUI | NOEXPORT,
    bpy_idname = "hide_select",
)

BFProp(
    idname = "bf_id_suffix",
    label = "ID Suffix",
    description = "Append suffix to multiple ID values",
    flags = NOUI,
    bpy_idname = "bf_id_suffix",
    bpy_prop = bpy.props.EnumProperty,
    items = (
        ("IDI",   "Index", "Append index number to multiple ID values", 100),
        ("IDX",   "x",     "Append x coordinate to multiple ID values", 200),
        ("IDY",   "y",     "Append y coordinate to multiple ID values", 300),
        ("IDZ",   "z",     "Append z coordinate to multiple ID values", 400),
        ("IDXY",  "xy",    "Append x,y coordinates to multiple ID values", 500),
        ("IDXZ",  "xz",    "Append x,z coordinates to multiple ID values", 600),
        ("IDYZ",  "yz",    "Append y,z coordinates to multiple ID values", 700),
        ("IDXYZ", "xyz",   "Append x,y,z coordinates to multiple ID values", 800),
    ),
    default = "IDI"
)

class BFPropID(BFPropString):
    def _draw_body(self, layout, context, element):
        row = layout.split(.8, align=True)
        row.template_ID(context.scene.objects, "active")
        row.prop(element, "bf_id_suffix", text="")

BFPropID(
    idname = "bf_id",
    label = "ID",
    description = "Identificator",
    fds_label = "ID",
    bf_props = ("bf_id_suffix", "bf_draw_type", "bf_hide", "bf_hide_select"), # The last three are automatically draw in Object panel
    bpy_idname = "name",
)

class BFPropSURFID(BFProp):
    def get_exported(self, context, element):
        return element.active_material and element.active_material.bf_export

    def get_value(self, context, element):
        if element.active_material: return element.active_material.name

    def set_value(self, context, element, value):
        element.active_material = geometry.utilities.get_material(context, str(value))
        
BFPropSURFID(
    idname = "bf_surf_id",
    label = "SURF_ID",
    description = "Reference to SURF",
    fds_label = "SURF_ID",
    bpy_idname = "active_material",
)

BFProp(
    idname = "bf_obst_thicken",
    label = "THICKEN",
    description = "Prevent FDS from allowing thin sheet obstructions",
    fds_label = "THICKEN",
    bpy_idname = "bf_obst_thicken",
    bpy_prop = bpy.props.BoolProperty,
    default = True,
)

BFPropString(
    idname = "bf_quantity",
    label = "QUANTITY",
    description = "Output quantity",
    fds_label = "QUANTITY",
    bpy_idname = "bf_quantity",
    bpy_prop = bpy.props.StringProperty,
    maxlen = 32,
)

BFProp(
    idname = "bf_devc_setpoint",
    label = "SETPOINT [~]",
    description = "Value of the device at which its state changes",
    fds_label = "SETPOINT",
    bf_prop_export = "bf_devc_setpoint_export",
    bpy_idname = "bf_devc_setpoint",
    bpy_prop = bpy.props.FloatProperty,
    step = 10,
    precision = 3,
    default = 100.,
)

BFProp(
    idname = "bf_devc_initial_state",
    label = "INITIAL_STATE",
    description = "Set device initial state to .TRUE.",
    fds_label = "INITIAL_STATE",
    bpy_idname = "bf_devc_initial_state",
    bpy_prop = bpy.props.BoolProperty,
    default = False,
)

BFProp(
    idname = "bf_devc_latch",
    label = "LATCH",
    description = "Device only changes state once",
    fds_label = "LATCH",
    bpy_idname = "bf_devc_latch",
    bpy_prop = bpy.props.BoolProperty,
    default = True,
)

BFPropString(
    idname = "bf_devc_prop_id",
    label = "PROP_ID",
    description = "Reference to a PROP (Property) line for self properties",
    fds_label = "PROP_ID",
    bpy_idname = "bf_devc_prop_id",
    bpy_prop = bpy.props.StringProperty,
    maxlen = 32,
)

BFProp(
    idname = "bf_slcf_vector",
    label = "VECTOR",
    description = "Create animated vectors",
    fds_label = "VECTOR",
    bpy_idname = "bf_slcf_vector",
    bpy_prop = bpy.props.BoolProperty,
    default = False,
)

class BFPropIJK(BFProp):
    def get_my_res(self, context, element, ui=False):
        if not self.get_exported(context, element): return None
        # Init
        has_good_ijk, cell_sizes, cell_number, cell_aspect_ratio  = fds_mesh.get_cell_infos(context, element)
        res = BFResult(sender=self)
        # Get and compare good IJK
        if not has_good_ijk:
            res.msgs.append("J and K not optimal for Poisson solver")
            res.operators.append("object.bf_correct_ijk")
        # Info on cells
        res.msgs.append("{0} mesh cells of size {1[0]:.3f}x{1[1]:.3f}x{1[2]:.3f} m".format(cell_number, cell_sizes))
        res.operators.append("object.bf_set_cell_sizes")
        # Info on aspect ratio
        if cell_aspect_ratio > 2.:
            res.msgs.append("Max cell aspect ratio is {:.1f}".format(cell_aspect_ratio))
            res.operators.append(None)
        # Set value and return
        if not ui: res.value = self._format_value(context, element, element.bf_mesh_ijk)
        return res

BFPropIJK(
    idname = "bf_ijk",
    label = "IJK",
    description = "Cell number in x, y, and z direction",
    fds_label = "IJK",
    bf_prop_export = "bf_ijk_export",
    bpy_idname = "bf_mesh_ijk",
    bpy_prop = bpy.props.IntVectorProperty,
    default = (10,10,10),
    size = 3,
    min = 1,
)

class BFPropFreeNamelist(BFPropFree):    
    def get_value(self, context, element):
        value = super().get_value(context, element)
        if not value: return
        err_msgs = list()
        if '&' in value or '/' in value:
            err_msgs.append("& and / characters not allowed")
        if "`" in value or "‘" in value or "’‌" in value or '"' in value or "”" in value or value.count("'") % 2 != 0:
            err_msgs.append("Only use matched single quotes as 'string' delimiters")
        if value and not re.match("[A-Z0-9_]{4}", value):
            err_msgs.append("Malformed namelist")
        if err_msgs: raise BFException(sender=self, msgs=err_msgs)
        return value
    
BFPropFreeNamelist(
    idname = "bf_free_namelist",
    label = "Free Namelist",
    description = "Free namelist and parameters, & and / not needed, use matched single quotes as string delimiters, eg ABCD PROP1='example'",
    bpy_idname = "bf_free", # system property
)

### Material

class BFPropIDMaterial(BFPropString):
    def _draw_body(self, layout, context, element):
        row = layout.row()
        row.template_ID(context.object, "active_material", new="material.new")

BFPropIDMaterial(
    idname = "bf_id_ma",
    label = "ID",
    description = "Identificator",
    fds_label = "ID",
    bpy_idname = "name",
)

class BFPropCOLOR(BFProp):
    def set_value(self, context, element, value):
        try: value = fds_tables.colors[value]
        except KeyError: raise BFException(sender=self, msg="Unknown color name '{}'".format(value))
        element.diffuse_color = value[0]/255, value[1]/255, value[2]/255

BFPropCOLOR(
    idname = "bf_color",
    fds_label = "COLOR",
    flags = IMPORTONLY, # only for import purpose
    bpy_idname = "diffuse_color",
)

class BFPropRGB(BFProp):
    def get_value(self, context, element):
        color = element.diffuse_color
        return int(color[0]*255), int(color[1]*255), int(color[2]*255)
        
    def set_value(self, context, element, value):
        element.diffuse_color = value[0]/255, value[1]/255, value[2]/255    

BFPropRGB(
    idname = "bf_rgb",
    label = "RGB",
    description = "A triplet of integer color values (red, green, blue)",
    flags = NOUI, # ui is statically added in the material panel
    fds_label = "RGB",
    bf_props = ("bf_color",), # call bf_color for registration
    bpy_idname = "diffuse_color",
)

class BFPropTRANSPARENCY(BFProp):
    def get_exported(self, context, element):        
        # Export me only if transparency is set
        return element.alpha < 1.

BFPropTRANSPARENCY(
    idname = "bf_transparency",
    label = "TRANSPARENCY",
    description = "Transparency",
    flags = NOUI, # ui is statically added in the material panel
    fds_label = "TRANSPARENCY",
    bpy_idname = "alpha",
)

BFPropString(
    idname = "bf_matl_id",
    label = "MATL_ID",
    description = "Reference to a MATL (Material) line for self properties",
    fds_label = "MATL_ID",
    bf_prop_export = "bf_matl_id_export",
    bpy_idname = "bf_matl_id",
    bpy_prop = bpy.props.StringProperty,
    maxlen = 32,
)

BFProp(
    idname = "bf_thickness",
    label = "THICKNESS [m]",
    description = "Surface thickness for heat transfer calculation",
    fds_label = "THICKNESS",
    bf_prop_export = "bf_thickness_export",
    bpy_idname = "bf_thickness",
    bpy_prop = bpy.props.FloatProperty,
    # unit = "LENGTH", # correction for scale_length needed before exporting!
    step = 1,
    precision = 3,
    min = .001,
    default = .01,
)

BFProp(
    idname = "bf_hrrpua",
    label = "HRRPUA [kW/m²]",
    description = "Heat release rate per unit area",
    fds_label = "HRRPUA",
    bpy_idname = "bf_hrrpua",
    bpy_prop = bpy.props.FloatProperty,
    step = 1000,
    precision = 3,
    min = 0.,
    default = 1000.,
)

class BFPropTAUQ(BFProp):
    def get_my_res(self, context, element, ui=False):
        if not self.get_exported(context, element): return None
        return BFResult(
            sender = self,
            value = self._format_value(context, element, element.bf_tau_q),
            msg = element.bf_tau_q <= 0 and "HRR(t) has a t² ramp" or "HRR(t) has a tanh(t/τ) ramp",
            operators = ("material.set_tau_q",),
            )

BFPropTAUQ(
    idname = "bf_tau_q",
    label = "TAU_Q [s]",
    description = "Ramp time for heat release rate",
    fds_label = "TAU_Q",
    bpy_idname = "bf_tau_q",
    bpy_prop = bpy.props.FloatProperty,
    unit = "TIME",
    step = 10,
    precision = 1,
    default = 100.,
)

BFProp(
    idname = "bf_ignition_temperature",
    label = "IGNITION_TEMPERATURE [°C]",
    description = "Ignition temperature",
    fds_label = "IGNITION_TEMPERATURE",
    bf_prop_export = "bf_ignition_temperature_export",
    bpy_idname = "bf_ignition_temperature",
    bpy_prop = bpy.props.FloatProperty,
    step = 100,
    precision = 1,
    min = -273.,
    default = 300.,
)
