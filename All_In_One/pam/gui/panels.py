"""PAM panels module"""

import bpy

from .. import mapping as map


class PAMLayerToolsPanel(bpy.types.Panel):
    """A tools panel inheriting all mapping functionality"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Layer"
    bl_category = "PAM Mapping"

    def draw(self, context):
        active_obj = context.active_object
        m = context.scene.pam_mapping
        layout = self.layout

        col = layout.column()
        col.prop(m, "num_neurons", text="Neurons")
        col.operator("pam.add_neuron_set", text="Add neuronset")


class PAMMappingToolsPanel(bpy.types.Panel):
    """A tools panel inheriting all mapping functionality"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Mapping"
    bl_category = "PAM Mapping"


    def draw(self, context):
        active_obj = context.active_object
        m = context.scene.pam_mapping
        layout = self.layout

        row = layout.row()
        row.template_list(
            listtype_name="MapSetList",
            list_id="mappings",
            dataptr=m,
            propname="sets",
            active_dataptr=m,
            active_propname="active_set",
            type="DEFAULT",
            rows=6,
        )

        col = row.column()
        sub = col.column(align = True)
        sub.operator("pam.model_load_sync_json", icon = "COPYDOWN", text = "")
        sub.operator("pam.model_sync_save_json", icon = "PASTEDOWN", text = "")
        sub = col.column(align = True)
        sub.operator("pam.mapping_add_set", icon="ZOOMIN", text="")
        sub.operator("pam.mapping_delete_set", icon="ZOOMOUT", text="")
        sub.operator("pam.mapping_up", icon="TRIA_UP", text="")
        sub.operator("pam.mapping_down", icon="TRIA_DOWN", text="")
        sub = col.column(align = True)
        sub.operator("pam.mapping_visibility", icon="RESTRICT_VIEW_OFF", text="")
        sub.operator("pam.mapping_visibility_part", icon="PARTICLES", text="")
        sub = col.column(align = True)
        sub.operator("pam.mapping_visibility_all", icon="RESTRICT_RENDER_OFF", text="")

        active_set = None

        try:
            active_set = m.sets[m.active_set]
        except IndexError:
            pass

        if not active_set:
            return

        layout.label("Layers:")

        for i, layer in enumerate(active_set.layers):
            # layer
            icon_collapsed = "TRIA_RIGHT"
            if not layer.collapsed:
                icon_collapsed = "TRIA_DOWN"

            box = layout.box()

            err = map.validate_layer(context, layer)
            if err:
                row = box.row(align=True)
                row.label(text="Error: %s" % err, icon="ERROR")

            row = box.row(align=True)
            col = row.column()
            col.prop(layer, "collapsed", icon=icon_collapsed, emboss=False, text="")

            row.prop(layer, "type", text="")
            row.operator("pam.mapping_layer_up", icon="TRIA_UP", text="").index = i
            row.operator("pam.mapping_layer_down", icon="TRIA_DOWN", text="").index = i

            col = row.column()
            col.operator("pam.mapping_layer_remove", icon="X", emboss=False, text="").index = i

            if not layer.collapsed:
                row = box.row(align=True)
                row.prop_search(layer, "object", bpy.data, 'objects', text="Object")
                row.operator("pam.mapping_layer_set_object", icon="SNAP_ON", text="").index = i

                if layer.type in ['presynapse', 'postsynapse']:
                    row = box.row(align=True)
                    row.prop(layer.kernel, "particles", text="", icon="PARTICLES")
                    row.prop(layer.kernel, 'particle_count')
                    op_prop = row.operator('pam.add_neuron_set_layer', icon='ZOOMIN', text = "")
                    op_prop.layer_index = i

                    row = box.row()
                    row.prop(layer.kernel, "function", text="", icon="SMOOTHCURVE")

                    row = box.row()
                    row.template_list(
                        listtype_name="CustomPropList",
                        dataptr=layer.kernel,
                        propname="parameters",
                        active_dataptr=layer.kernel,
                        active_propname="active_parameter",
                        type="DEFAULT",
                        rows=3
                    )

                if layer.type in ['synapse']:
                    row = box.row(align=True)
                    row.prop(layer, "synapse_count", text="Synapses")

            if i < len(active_set.mappings):
                mapping = active_set.mappings[i]
                split = layout.split(0.8)
                box = split.box()
                col = box.column()
                col.prop(mapping, "function", text="", icon="MOD_UVPROJECT")
                if mapping.function == "uv":
                    col.prop(mapping, "uv_source", text="Source", icon="FORWARD")
                    col.prop(mapping, "uv_target", text="Target", icon="BACK")
                col = box.column()
                col.prop(mapping, "distance", text="", icon="ALIGN")

        col = layout.column(align=True)
        col.prop(m, "neuron_multiplier")
        col.prop(m, "synapse_multiplier")
        
        col = layout.column(align=True)
        col.operator("pam.mapping_layer_add", icon="ZOOMIN", text="Add layer")
        col.operator("pam.mapping_compute", icon="SCRIPTWIN", text="Compute mapping")
        col.operator("pam.mapping_compute_sel", icon="SCRIPTWIN", text="Compute selected mapping")
        col.operator("pam.mapping_update", icon="SCRIPTWIN", text="Update mapping")
        col.operator("pam.mapping_debug", icon="SCRIPTWIN", text="Debug selected mapping")
        col.prop(m, "seed")

class PAMColorizePanel(bpy.types.Panel):
    """A panel for colorizing layer distances"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Distances"
    bl_category = "PAM Mapping"

    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("pam.mapping_color_layer", icon = "SCRIPTWIN", text = "Colorize")
        col.operator("pam.mapping_distance_csv", text = "Export CSV")


class PAMModelDataPanel(bpy.types.Panel):
    """A panel for loading and saving model data"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Data"
    bl_category = "PAM Modeling"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("pam.model_load", text="Load")
        col.operator("pam.model_save", text="Save")
        col.operator("pam.model_export_csv", text="Export CSV")


class PAMToolsPanel(bpy.types.Panel):
    """A tools panel inheriting all neuronal modelling operations"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Connections"
    bl_category = "PAM Modeling"

    def draw(self, context):
        layout = self.layout
        row = layout.column()
        row.prop(
            context.scene.pam_visualize,
            "smoothing",
            text="Smoothing"
        )
        row.prop(context.scene.pam_visualize,
            "bevel_depth"
        )
        row.prop_search(context.scene.pam_visualize,
            "connection_material",
            bpy.data, "materials"
        )
        row.operator(
            "pam_vis.visualize_connections_for_neuron",
            "Connections at Cursor"
        )
        
        row.separator()
        row.prop(
            context.scene.pam_visualize,
            "connections",
            text="Connections"
        )
        row.operator(
            "pam_vis.visualize_connections_all",
            "Connections for all mappings"
        )

        row.label("Debugging")

        row = layout.row()
        row.prop(context.scene.pam_visualize, "efferent_afferent", text="Direction of connection", expand=True)
        row = layout.column()
        
        row.operator(
            "pam_vis.visualize_forward_connection",
            "Mapping at Cursor"
        )

        row.operator(
            "pam_vis.visualize_unconnected_neurons",
            "Unconnected neurons"
        )
        
        row.separator()
        row.operator("pam_vis.visualize_clean", "Clear Visualizations")

class PAMTracingPanel(bpy.types.Panel):
    """A tools panel for conducting virtual tracer studies"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Tracing"
    bl_category = "PAM Modeling"
    
    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.scene.pam_visualize, "inj_method", text="Injection method", expand=True)

        row = layout.row()
        row.prop(context.scene.pam_visualize, "radius", text="Injection radius")

        row = layout.row()
        row.prop_search(context.scene.pam_visualize, 'mesh', bpy.data, 'objects')
        
        row = layout.row()
        row.prop(context.scene.pam_visualize, "set_color", text="Fix injection color")

        if context.scene.pam_visualize.set_color:
            row = layout.row()
            row.prop(context.scene.pam_visualize, "inj_color", text="Injection color")
            
        row = layout.row()
        row.prop(context.scene.pam_visualize, "draw_paths", text="Draw connections paths")
        
        if context.scene.pam_visualize.draw_paths:
            row = layout.row()
            row.prop(context.scene.pam_visualize, "smoothing", text="Smoothing")

        row = layout.row()
        op = row.operator("pam_vis.tracing", text="Perform tracing")

class PAMVisualizeKernelToolsPanel(bpy.types.Panel):
    """A tools panel for visualization of kernel function """

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Kernel"
    bl_category = "PAM Modeling"

    def draw(self, context):
        active_obj = context.active_object

        name = mesh_object_name(active_obj)
        customs = context.scene.pam_visualize.customs
        layout = self.layout

        row = layout.row()
        row.prop(context.scene.pam_visualize, "view", text="")

        row = layout.row()
        row.label("Active: %s" % name)

        row = layout.row()
        row.prop(context.scene.pam_visualize, "resolution", text="Resolution")

        row = layout.row()
        row.prop(context.scene.pam_visualize, "kernel", text="")

        row = layout.row()
        row.label("Parameter:")

        if context.scene.pam_visualize.mode == "COORDINATES":
            row = layout.row()
            col = row.column(align=True)
            col.prop(context.scene.pam_visualize, "u", text="u")
            col.prop(context.scene.pam_visualize, "v", text="v")

        row = layout.row()
        row.template_list(
            listtype_name="CustomPropList",
            dataptr=context.scene.pam_visualize,
            propname="customs",
            active_dataptr=context.scene.pam_visualize,
            active_propname="active_index",
            type="DEFAULT",
            rows=6,
        )

        # row = layout.row(align=True)
        # row.template_preview(context.blend_data.textures.get("pam.temp_texture"))

        row = layout.row(align=True)
        op = row.operator("pam.reset_params", text="Reset parameters")

        layout.separator()

        row = layout.row()
        row.prop(context.scene.pam_visualize, "mode", expand=True)

        row = layout.row()
        op = row.operator("pam.visualize", text="Generate texture")


class PAMModelingPanel(bpy.types.Panel):
    """A panel for loading and saving model data"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Modeling"
    bl_category = "PAM Modeling"

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("pam.map_via_uv", text="Deform mesh via UV")


class PAMMeasureToolsPanel(bpy.types.Panel):
    """A tools panel inheriting all measurment operations"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Measure"
    bl_category = "PAM Modeling"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        active_obj = context.active_object

        name = mesh_object_name(active_obj)

        layout = self.layout
        layout.label("Active: %s" % name)

        row = layout.row()
        col = row.column(align=True)
        col.prop(context.scene.pam_measure, "quantity", text="Neurons")
        col.prop(context.scene.pam_measure, "area", text="Area")

        row = layout.row()
        col = row.column()
        op = col.operator("pam.measure_layer", "Calculate")
        col.label("Total neurons: %d" % context.scene.pam_measure.neurons)
        col.label("Total area: %d" % context.scene.pam_measure.total_area)


class CustomPropList(bpy.types.UIList):
    """A custom cell for property display"""
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        layout.prop(item, "name", text="", emboss=False)
        layout.prop(item, "value", text="", emboss=False, slider=False)


class IntermediateLayerList(bpy.types.UIList):
    """A custom cell for intermediate layer objects"""
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        layout.prop(item, "object", text="", emboss=False)


class MapSetList(bpy.types.UIList):
    """A custom cell for mapping names"""
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        layout.prop(item, "name", text="", emboss=False)


def mesh_object_name(obj):
    """Get name of an object

    :param bpy.types.Object obj: an object
    :return: name of object
    :rtype: str

    """
    name = ""
    if obj is not None:
        if obj.type == "MESH":
            name = obj.name

    return name
