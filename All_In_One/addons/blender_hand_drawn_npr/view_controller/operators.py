import logging
import tempfile

import bpy

logger = logging.getLogger(__name__)

try:
    from ..model.data import ThicknessParameters, LightingParameters, StippleParameters, Settings
    from ..model.illustrate import Illustrator
except (ImportError, NameError):
    logger.warning("Model data can not be imported. This is fine if running Blender tests in CI, trouble if otherwise.")


class PrepareNPRSettings(bpy.types.Operator):
    bl_idname = "wm.prepare_npr_settings"
    bl_label = "Prepare settings to suit hand-drawn NPR."

    def execute(self, context):
        bpy.context.scene.render.engine = "CYCLES"

        # Set default resolution.
        bpy.context.scene.render.resolution_x = 3840
        bpy.context.scene.render.resolution_y = 2160
        bpy.context.scene.render.resolution_percentage = 100

        bpy.context.scene.frame_current = 1

        # By default, anti-aliasing is applied which wreaks havoc with images which represent hard data
        # (e.g uv pass image). Most effective way to turn off AA is by using Branched Path Tracing with minimal
        # AA samples.
        bpy.context.scene.cycles.progressive = 'BRANCHED_PATH'
        bpy.context.scene.cycles.aa_samples = 1
        bpy.context.scene.cycles.preview_aa_samples = 0
        # Some sensible defaults.
        bpy.context.scene.cycles.diffuse_samples = 10
        bpy.context.scene.cycles.ao_samples = 10

        layer = bpy.context.scene.render.layers["RenderLayer"]
        logger.debug("Configuring passes for " + layer.name)
        layer.use_pass_normal = True
        layer.use_pass_uv = True
        layer.use_pass_object_index = True
        layer.use_pass_z = True
        layer.use_pass_diffuse_direct = True
        layer.use_pass_shadow = True
        layer.use_pass_ambient_occlusion = True

        # System needs knowledge of the corresponding grey level in the indexOB map, which is based on this index.
        # Apply a known index to all meshes in the scene.
        for object in context.scene.objects:
            if object.type == 'MESH':
                index = 1
                object.pass_index = index
                logger.debug("Assigned pass index %d to object: %s", index, object.name)

        return {'FINISHED'}


class CreateNPRCompositorNodes(bpy.types.Operator):
    bl_idname = "wm.create_npr_compositor_nodes"
    bl_label = "Create compositor nodes to write render passes to disk."

    def execute(self, context):
        logger.debug("Executing CreateCompositorNodeOperator...")

        # Blender command for troubleshooting.
        # file_out_node = bpy.context.scene.node_tree.nodes[2]

        context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree

        # Remove all nodes.
        for node in tree.nodes:
            tree.nodes.remove(node)

        # Create nodes.
        render_layer_node = tree.nodes.new(type="CompositorNodeRLayers")
        render_layer_node.location = 0, 0
        file_out_node = tree.nodes.new(type="CompositorNodeOutputFile")
        file_out_node.location = 440, 0
        normalise_node = tree.nodes.new(type="CompositorNodeNormalize")
        normalise_node.location = 220, 10

        # Configure image path.
        file_out_node.base_path = tempfile.gettempdir()

        # Configure outputs and link nodes.
        file_out_node.file_slots.clear()
        links = tree.links
        pass_names = [
            "Image",
            "Depth",
            "Normal",
            "UV",
            "Shadow",
            "AO",
            "IndexOB",
            "DiffDir"
        ]
        for pass_name in pass_names:
            file_out_node.file_slots.new(name=pass_name)
            if pass_name == "Depth":
                links.new(render_layer_node.outputs[pass_name], normalise_node.inputs[0])
                links.new(normalise_node.outputs[0], file_out_node.inputs[pass_name])
            else:
                links.new(render_layer_node.outputs[pass_name], file_out_node.inputs[pass_name])

        # Configure required image formats.
        file_out_node.format.compression = 0
        file_out_node.format.color_depth = "8"

        # Need to use tiff for 16-bit colour depth.
        file_out_node.file_slots['Normal'].use_node_format = False
        file_out_node.file_slots['Normal'].format.file_format = 'TIFF'
        file_out_node.file_slots['Normal'].format.color_depth = "16"
        file_out_node.file_slots['Normal'].format.tiff_codec = 'NONE'

        file_out_node.file_slots['UV'].use_node_format = False
        file_out_node.file_slots['UV'].format.file_format = 'TIFF'
        file_out_node.file_slots['UV'].format.color_depth = "16"
        file_out_node.file_slots['UV'].format.tiff_codec = 'NONE'

        return {'FINISHED'}


class RenderNPR(bpy.types.Operator):
    bl_idname = "wm.render_npr"
    bl_label = "Render NPR"

    def execute(self, context):

        logger.debug("Executing RenderNPR...")

        context = bpy.context
        system_settings = context.scene.system_settings

        logger.debug("Building settings...")

        silhouette_thickness_parameters = ThicknessParameters(const=system_settings.silhouette_const,
                                                              z=system_settings.silhouette_depth,
                                                              diffdir=system_settings.silhouette_diffuse,
                                                              stroke_curvature=system_settings.silhouette_curvature)
        internal_edge_thickness_parameters = ThicknessParameters(const=system_settings.internal_const,
                                                                 z=system_settings.internal_depth,
                                                                 diffdir=system_settings.internal_diffuse,
                                                                 stroke_curvature=system_settings.internal_curvature)
        streamline_thickness_parameters = ThicknessParameters(const=system_settings.streamline_const,
                                                              z=system_settings.streamline_depth,
                                                              diffdir=system_settings.streamline_diffuse,
                                                              stroke_curvature=system_settings.streamline_curvature)
        lighting_parameters = LightingParameters(diffdir=system_settings.stipple_diffuse,
                                                 shadow=system_settings.stipple_shadow,
                                                 ao=system_settings.stipple_ao,
                                                 threshold=system_settings.stipple_threshold / 100)
        stipple_parameters = StippleParameters(head_radius=system_settings.stipple_head_radius,
                                               tail_radius=system_settings.stipple_tail_radius,
                                               length=system_settings.stipple_length,
                                               density_fn_min=system_settings.stipple_min_allowable,
                                               density_fn_factor=system_settings.stipple_density_factor,
                                               density_fn_exponent=system_settings.stipple_density_exponent)

        settings = Settings(in_path=tempfile.gettempdir(),
                            out_filepath=system_settings.out_filepath,
                            harris_min_distance=system_settings.corner_factor,
                            silhouette_thickness_parameters=silhouette_thickness_parameters,
                            enable_internal_edges=system_settings.is_internal_enabled,
                            internal_edge_thickness_parameters=internal_edge_thickness_parameters,
                            enable_streamlines=system_settings.is_streamlines_enabled,
                            streamline_segments=system_settings.streamline_segments,
                            streamline_thickness_parameters=streamline_thickness_parameters,
                            enable_stipples=system_settings.is_stipples_enabled,
                            lighting_parameters=lighting_parameters,
                            stipple_parameters=stipple_parameters,
                            optimise_clip_paths=system_settings.is_optimisation_enabled,
                            # Note: Remaining values hard-coded to sensible defaults. Minimal benefit to exposing
                            # these in UI.
                            cull_factor=20,
                            optimise_factor=5,
                            curve_fit_error=0.01,
                            subpix_window_size=20,
                            curve_sampling_interval=20,
                            stroke_colour="black",
                            uv_primary_trim_size=200,
                            uv_secondary_trim_size=20)

        logger.debug("Starting illustrator...")
        try:
            illustrator = Illustrator(settings)
            illustrator.illustrate()
            illustrator.save()
        except FileNotFoundError:
            self.report({"ERROR"}, "First render the scene with Cycles and try again.")
            logger.info("Source image(s) not found.")
            return {'FINISHED'}

        self.report({"INFO"}, "Render NPR complete!")
        return {'FINISHED'}


classes = (
    PrepareNPRSettings,
    CreateNPRCompositorNodes,
    RenderNPR
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in classes:
        unregister_class(cls)
