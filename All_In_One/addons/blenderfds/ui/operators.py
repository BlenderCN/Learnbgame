"""BlenderFDS, Blender operators"""

import bpy, time
from blenderfds.types import *
from blenderfds.lib import fds_mesh, fds_surf
from blenderfds import geometry

### Dialog box

class WM_OT_bf_dialog(bpy.types.Operator):
    bl_label = "BlenderFDS"
    bl_idname = "wm.bf_dialog"
    bl_description = "BlenderFDS Dialog"

    type = bpy.props.EnumProperty(
        name = "Type",
        items = (("INFO", "Information", "Information",), ("ERROR", "Error", "Error")),
        description = "Dialog type",
        default="INFO",
    )

    msg = bpy.props.StringProperty(
        name="Message",
        description="Dialog message",
        default="No message",
    )

    description = bpy.props.StringProperty(
        name="Description",
        description="Dialog description",
    )

    def execute(self, context):
        return {'FINISHED'}
 
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text=self.msg, icon=self.type)
        if self.description:
            col.separator()
            descriptions = self.description.splitlines()
            for description in descriptions:
                row = col.row()
                row.label(description)

### Set default homefile

import sys

class WM_OT_bf_set_environment(bpy.types.Operator):
    bl_label = "Set Default BlenderFDS Environment"
    bl_idname = "wm.bf_set_environment"
    bl_description = "Set default BlenderFDS environment"

    def execute(self, context):
        # Save user preferences
        bpy.ops.wm.save_userpref()
        # Set default startup.blend        
        filepath = sys.path[0] + "/blenderfds/default/bf_startup.blend"
        bpy.ops.wm.open_mainfile(filepath=filepath, load_ui=True, use_scripts=True)
        bpy.ops.wm.save_homefile()
        self.report({"INFO"}, "Default BlenderFDS environment loaded")
        return {'FINISHED'}

### MESH and IJK

class OBJECT_OT_bf_set_cell_size(bpy.types.Operator):
    bl_label = "Set Cell Sizes"
    bl_idname = "object.bf_set_cell_sizes"
    bl_description = "Set MESH cell sizes"

    bf_cell_sizes = bpy.props.FloatVectorProperty(
        name="Desired Cell Sizes [m]", description="Desired MESH cell sizes",
        default=(.2, .2, .2), min=.001, step=1000, precision=3, size=3
    )
    bf_snap_to_origin = bpy.props.BoolProperty(
        name="Snap To Global Origin",
        description="Snap this MESH to global origin",
        default=True,
    )
    bf_poisson_restriction = bpy.props.BoolProperty(
        name="Poisson Restriction",
        description="Respect FDS Poisson solver restriction on IJK values by adjusting object dimensions",
        default=True,
    )
    
    def draw(self, context):
        layout = self.layout
        ob = context.active_object
        row = layout.row()
        row.prop(self, "bf_cell_sizes")
        row = layout.row()
        row.prop(self, "bf_snap_to_origin")
        row = layout.row()
        row.prop(self, "bf_poisson_restriction")
        
    def execute(self, context):
        ob = context.active_object
        fds_mesh.set_cell_sizes(context, ob, self.bf_cell_sizes, self.bf_snap_to_origin, self.bf_poisson_restriction)
        self.report({"INFO"}, "MESH cell size set")
        return {'FINISHED'}

    def invoke(self, context, event):
        ob = context.active_object
        # Set default
        self.bf_cell_sizes = fds_mesh.get_cell_sizes(context, ob)
        # Call dialog
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OBJECT_OT_bf_correct_ijk(bpy.types.Operator):
    bl_label = "Correct IJK"
    bl_idname = "object.bf_correct_ijk"
    bl_description = "Correct IJK for FDS Poisson solver"

    def execute(self, context):
        ob = context.active_object
        ob.bf_mesh_ijk = fds_mesh.get_good_ijk(ob.bf_mesh_ijk)
        self.report({"INFO"}, "IJK corrected")
        return {'FINISHED'}

### Copy properties between elements

def bpy_props_copy(context, source_element, destination_elements):
    """Copy all bpy_props from source_element to destination_elements"""
    # Copy bf_namelist, if present (Scene does not have it)
    try: bf_namelist_idname = source_element.bf_namelist_idname
    except AttributeError: pass
    else:
        for destination_element in destination_elements:
            destination_element.bf_namelist_idname = bf_namelist_idname
    # Copy all other bf_props
    for bf_prop in bf_props:
        if bf_prop.bpy_idname == "name": continue # Do not copy ID and CHID
        try: bpy_value = getattr(source_element, bf_prop.bpy_idname)
        except: continue
        for destination_element in destination_elements:
            setattr(destination_element, bf_prop.bpy_idname, bpy_value)
            print("BFDS: Copy: {} -> {}: {}='{}'".format(source_element.name, destination_element.name, bf_prop.bpy_idname, bpy_value)) 

class SCENE_OT_bf_copy_props_to_scene(bpy.types.Operator):
    bl_label = "Copy Properties To Scene"
    bl_idname = "scene.bf_props_to_scene"
    bl_description = "Copy these properties to another scene"

    bf_destination_element = bpy.props.StringProperty(name="To scene")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop_search(self, "bf_destination_element", bpy.data, "scenes")        

    def execute(self, context):
        # Get source and destination scenes
        source_element = context.scene
        destination_elements = (bpy.data.scenes.get(self.bf_destination_element, None),) # a tuple!
        if not destination_elements[0]:
            self.report({"WARNING"}, "No destination scene")
            return{'CANCELLED'}
        if not source_element:
            self.report({"WARNING"}, "No source scene")
            return{'CANCELLED'}
        # Copy
        bpy_props_copy(context, source_element, destination_elements)
        self.report({"INFO"}, "Copied to destination scene")
        return {'FINISHED'}

    def invoke(self, context, event):
        # Call dialog
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OBJECT_OT_bf_copy_FDS_properties_to_sel_obs(bpy.types.Operator):
    bl_label = "Copy To Selected Objects"
    bl_idname = "object.bf_props_to_sel_obs"
    bl_description = "Copy these properties to other selected objects"

    def execute(self,context):
        if context.mode != 'OBJECT': bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        # Get source and destination objects
        source_element = context.active_object
        destination_elements = set(ob for ob in context.selected_objects if ob.type == "MESH" and ob != source_element)
        if not destination_elements:
            self.report({"WARNING"}, "No destination objects")
            return{'CANCELLED'}
        if not source_element:
            self.report({"WARNING"}, "No source object")
            return{'CANCELLED'}
        # Copy
        bpy_props_copy(context, source_element, destination_elements)
        self.report({"INFO"}, "Copied to selected objects")
        return {'FINISHED'}
        
class MATERIAL_OT_bf_assign_BC_to_sel_obs(bpy.types.Operator):
    bl_label = "Assign To Selected Objects"
    bl_idname = "material.bf_surf_to_sel_obs"
    bl_description = "Assign this boundary condition to selected objects"

    def execute(self,context):
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        # Get source and destination materials
        source_element = context.active_object
        active_material = source_element.active_material
        destination_elements = set(ob for ob in context.selected_objects if ob.type == "MESH" and ob != source_element)
        if not destination_elements:
            self.report({"WARNING"}, "No destination objects")
            return{'CANCELLED'}
        if not source_element:
            self.report({"WARNING"}, "No source object")
            return{'CANCELLED'}
        if not active_material:
            self.report({"WARNING"}, "No boundary condition to assign")
            return{'CANCELLED'}
        # Loop on objects
        for ob in destination_elements:
            ob.active_material = active_material
            print("BlenderFDS: Assign material '{}' -> {}".format(active_material.name, ob.name))
        # Set myself as exported
        active_material.bf_export = True
        # Return
        self.report({"INFO"}, "Assigned to selected objects")
        return {'FINISHED'}

### Predefined materials

class MATERIAL_OT_bf_set_predefined(bpy.types.Operator):
    bl_label = "Set Predefined"
    bl_idname = "material.bf_set_predefined"
    bl_description = "Set predefined SURFs: INERT, OPEN, MIRROR..."

    def execute(self, context):
        fds_surf.set_predefined(context)
        self.report({"INFO"}, "Predefined SURFs ok")
        return {'FINISHED'}

### Show exported geometry

class OBJECT_OT_bf_show_fds_geometries(bpy.types.Operator):
    bl_label = "Show FDS Geometries"
    bl_idname = "object.bf_show_fds_geometries"
    bl_description = "Show geometries as exported to FDS"

    def execute(self, context):
        # Init
        w = context.window_manager.windows[0]
        w.cursor_modal_set("WAIT")
        if context.mode != 'OBJECT': bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        ob = context.object
        msgs = list()
        err_msgs = list()
        # Manage XB: get coordinates, show them in a tmp object, prepare msg
        xbs = None
        msg = None
        try:  xbs, msg  = geometry.to_fds.ob_to_xbs(context, ob)
        except BFException as err: err_msgs.extend(err.labels)
        if msg: msgs.append(msg)
        if xbs:
            ob_tmp = geometry.from_fds.xbs_to_ob(xbs, context, bf_xb=ob.bf_xb, name="Shown {} XBs".format(ob.name))
            geometry.tmp.set_tmp_object(context, ob, ob_tmp)
        # Manage XYZ: get coordinates, show them in a tmp object, prepare msg
        xyzs = None
        msg = None
        try: xyzs, msg = geometry.to_fds.ob_to_xyzs(context, ob)
        except BFException as err: err_msgs.extend(err.labels)
        if msg: msgs.append(msg)
        if xyzs:
            ob_tmp = geometry.from_fds.xyzs_to_ob(xyzs, context, bf_xyz=ob.bf_xyz, name="Shown {} XYZs".format(ob.name))
            geometry.tmp.set_tmp_object(context, ob, ob_tmp)
        # Manage PB*: get coordinates, show them in a tmp object, prepare msg
        pbs  = None
        msg = None        
        try: pbs, msg  = geometry.to_fds.ob_to_pbs(context, ob)
        except BFException as err: err_msgs.extend(err.labels)
        if msg: msgs.append(msg)
        if pbs:
            ob_tmp = geometry.from_fds.pbs_to_ob(pbs, context, bf_pb=ob.bf_pb, name="Shown {} PBs".format(ob.name))
            geometry.tmp.set_tmp_object(context, ob, ob_tmp)
        # Set report
        if err_msgs: report = {"ERROR"}, "; ".join(err_msgs)
        elif msgs: report = {"INFO"}, "; ".join(msgs)
        elif xbs or xyzs or pbs: report = {"INFO"}, "FDS geometries shown"
        else: report = {"WARNING"}, "No geometry to show"
        # Return
        w.cursor_modal_restore()
        self.report(*report)
        return{'FINISHED'}

class SCENE_OT_bf_del_all_tmp_objects(bpy.types.Operator):
    bl_label = "Hide Temporary Objects"
    bl_idname = "scene.bf_del_all_tmp_objects"
    bl_description = "Delete all temporary objects"

    def execute(self, context):
        geometry.tmp.del_all_tmp_objects(context)
        self.report({"INFO"}, "All temporary objects deleted")
        return {'FINISHED'}

### Open text editor with right text displayed

def _open_text_in_editor(context, text_name):
    # Text Editor already displayed?
    area_te = None
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if 'TEXT_EDITOR' == area.type:
                area_te = area
                break
    # If Text Editor is displayed, show requested text
    if area_te:
        if text_name in bpy.data.texts:
            area_te.spaces[0].text = bpy.data.texts[text_name]
    
class SCENE_OT_bf_edit_head_free_text(bpy.types.Operator):
    bl_label = "Edit"
    bl_idname = "scene.bf_edit_head_free_text"
    bl_description = "Edit free text file in separate editor"

    def execute(self, context):
        sc = context.scene
        # Check
        if not sc.bf_head_free_text: # Empty field?
            sc.bf_head_free_text = "HEAD free text"
        if sc.bf_head_free_text not in bpy.data.texts: # No linked file?
            bpy.data.texts.new(sc.bf_head_free_text)
        # Open
        _open_text_in_editor(context, sc.bf_head_free_text)
        # Return
        self.report({"INFO"}, "See '{}' in the text editor".format(sc.bf_head_free_text))
        return {'FINISHED'}

### Set TAU_Q ramp according to norms

class MATERIAL_OT_bf_set_tau_q(bpy.types.Operator):
    bl_label = "Set t² Ramp"
    bl_idname = "material.set_tau_q"
    bl_description = "Set t² ramp and HRRPUA"

    bf_burner_area = bpy.props.FloatProperty(name="Est.d Burner Area [m²]", min=0., precision=3, step=1000) # unit="AREA" this would need correction
    bf_hrr_max = bpy.props.FloatProperty(name="HRR Max [kW]", min=0., precision = 1, step=1000)
    bf_growth_rate = bpy.props.EnumProperty(
        name = "Growth Rate",
        items = (
            ("SLOW", "Slow (600 s)", "Slow growth rate (600 s)"),
            ("MEDIUM", "Medium (300 s)", "Medium growth rate (300 s)"),
            ("FAST", "Fast (150 s)", "Fast growth rate (150 s)"),
            ("ULTRA-FAST", "Ultra fast (75 s)", "Ultra fast growth rate (75 s)"),
        ),
    )
    bf_reference_hrr = bpy.props.EnumProperty(
        name = "Reference HRR",
        items = (
            ("US", "US, 1000 BTU/s (1055 kW)", "US, 1000 BTU/s (1055 kw)"),
            ("EN", "Eurocode, 1000 kW", "Eurocode, 1000 kW"),
        ),
    )
    bf_set_fyi = bpy.props.BoolProperty(name = "Set FYI")

    def execute(self, context):
        ma = context.object.active_material
        reference_hrr = {"US":1055., "EN":1000.}[self.bf_reference_hrr]
        time = {"SLOW":600., "MEDIUM":300., "FAST":150., "ULTRA-FAST":75.}[self.bf_growth_rate]
        ma.bf_tau_q = -time * (self.bf_hrr_max / reference_hrr) ** .5
        ma.bf_hrrpua = self.bf_hrr_max / self.bf_burner_area
        if self.bf_set_fyi:
            ma.bf_fyi = "Est.d area {:.2f} m², HRR max {:.0f} kW, {} t² ramp ({})".format(
                self.bf_burner_area,
                self.bf_hrr_max,
                self.bf_growth_rate.lower(),
                self.bf_reference_hrr
            )
        self.report({'INFO'}, "TAU_Q and HRRPUA set")
        return {'FINISHED'}

    def invoke(self, context, event):
        ma = context.object.active_material
        # Calc burner area
        burner_area = 0.
        obs = (ob for ob in context.scene.objects \
            if ob.type == "MESH" and ob.bf_export \
            and ob.active_material == ma and "bf_surf_id" in ob.descendants)
        for ob in obs: burner_area += geometry.utilities.get_global_area(context, ob)
        # Set defaults to estimated values
        self.bf_burner_area = burner_area
        self.bf_hrr_max = ma.bf_hrrpua * burner_area
        self.bf_growth_rate = "FAST"
        self.bf_reference_hrr = "US"
        self.bf_set_fyi = False # The user shall choose and understand implications
        # Call dialog
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
