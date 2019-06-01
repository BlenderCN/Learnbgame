import logging
import os
import tempfile

import bpy

from .helpers import toggle_hook

logger = logging.getLogger(__name__)


class NPRSystemSettings(bpy.types.PropertyGroup):
    """ Define add-on system settings. """

    logger.debug("Instantiating SystemSettings...")

    is_hook_enabled = bpy.props.BoolProperty(name="Enable",
                                             description="Automatically perform Render NPR post-Cycles",
                                             default=False,
                                             update=toggle_hook)

    out_filepath = bpy.props.StringProperty(name="",
                                            description="File path for the produced SVG",
                                            default=os.path.join(tempfile.gettempdir(), "out.svg"),
                                            subtype="FILE_PATH")

    corner_factor = bpy.props.IntProperty(name="Corner Factor",
                                          description="Influences sensitivity of corner detection. Specifically, "
                                                      "this value influences the min_distance parameter of skimage "
                                                      "peak_local_max",
                                          default=40,
                                          min=1,
                                          soft_max=1000)

    silhouette_const = bpy.props.FloatProperty(name="Constant",
                                               description="Apply a constant thickness to silhouette lines. Thickness "
                                                           "will be proportional to the specified factor",
                                               precision=1,
                                               default=1,
                                               min=0,
                                               soft_max=10)

    silhouette_depth = bpy.props.FloatProperty(name="Depth",
                                               description="Vary silhouette line weight according to distance from the "
                                                           "camera. Thickness will be proportional to the specified "
                                                           "factor",
                                               precision=1,
                                               default=0,
                                               min=0,
                                               soft_max=10)

    silhouette_diffuse = bpy.props.FloatProperty(name="Diffuse",
                                                 description="Vary silhouette line weight according to direct diffuse "
                                                             "lighting. Thickness will be proportional to the "
                                                             "specified factor",
                                                 precision=1,
                                                 default=0,
                                                 min=0,
                                                 soft_max=10)

    silhouette_curvature = bpy.props.FloatProperty(name="Curvature",
                                                   description="Vary silhouette line weight according to line "
                                                               "curvature. Thickness will be proportional to the "
                                                               "specified factor",
                                                   precision=1,
                                                   default=0,
                                                   min=0,
                                                   soft_max=100)

    is_internal_enabled = bpy.props.BoolProperty(name="Internal Edges",
                                                 description="Enable internal edge lines",
                                                 default=False)

    internal_const = bpy.props.FloatProperty(name="Constant",
                                             description="Apply a constant thickness to internal edge lines. Thickness "
                                                         "will be proportional to the specified factor",
                                             precision=1,
                                             default=1,
                                             min=0,
                                             soft_max=10)

    internal_depth = bpy.props.FloatProperty(name="Depth",
                                             description="Vary internal edge line weight according to distance from the "
                                                         "camera. Thickness will be proportional to the specified "
                                                         "factor",
                                             precision=1,
                                             default=0,
                                             min=0,
                                             soft_max=10)

    internal_diffuse = bpy.props.FloatProperty(name="Diffuse",
                                               description="Vary internal edge line weight according to direct diffuse "
                                                           "lighting. Thickness will be proportional to the "
                                                           "specified factor",
                                               precision=1,
                                               default=0,
                                               min=0,
                                               soft_max=10)

    internal_curvature = bpy.props.FloatProperty(name="Curvature",
                                                 description="Vary internal edge line weight according to line "
                                                             "curvature. Thickness will be proportional to the "
                                                             "specified factor",
                                                 precision=1,
                                                 default=0,
                                                 min=0,
                                                 soft_max=100)

    is_streamlines_enabled = bpy.props.BoolProperty(name="Streamlines",
                                                    description="Enable streamlines (requires UV unwrapped mesh)",
                                                    default=False)

    streamline_const = bpy.props.FloatProperty(name="Constant",
                                               description="Apply a constant thickness to streamlines. Thickness "
                                                           "will be proportional to the specified factor",
                                               precision=1,
                                               default=1,
                                               min=0,
                                               soft_max=10)

    streamline_depth = bpy.props.FloatProperty(name="Depth",
                                               description="Vary streamline weight according to distance from the "
                                                           "camera. Thickness will be proportional to the specified "
                                                           "factor",
                                               precision=1,
                                               default=0,
                                               min=0,
                                               soft_max=10)

    streamline_diffuse = bpy.props.FloatProperty(name="Diffuse",
                                                 description="Vary streamline weight according to direct diffuse "
                                                             "lighting. Thickness will be proportional to the "
                                                             "specified factor",
                                                 precision=1,
                                                 default=0,
                                                 min=0,
                                                 soft_max=10)

    streamline_curvature = bpy.props.FloatProperty(name="Curvature",
                                                   description="Vary streamline weight according to line "
                                                               "curvature. Thickness will be proportional to the "
                                                               "specified factor",
                                                   precision=1,
                                                   default=0,
                                                   min=0,
                                                   soft_max=100)

    streamline_segments = bpy.props.IntProperty(name="Segments",
                                                description="The number of segments into which streamlines should "
                                                            "divide the mesh",
                                                default=16,
                                                min=2,
                                                soft_max=128)

    is_stipples_enabled = bpy.props.BoolProperty(name="Stipples",
                                                 description="Enable stipples (requires UV unwrapped mesh)",
                                                 default=False)

    is_optimisation_enabled = bpy.props.BoolProperty(name="Optimise Clip Path",
                                                     description="When enabled, each stipple is checked for "
                                                                 "intersection with a silhouette line. Only "
                                                                 "intersecting strokes are given a clip path. This "
                                                                 "greatly improves performance when opening the final "
                                                                 "image in an SVG editor, but comes "
                                                                 "with a performance penalty during rendering",
                                                     default=False)

    stipple_threshold = bpy.props.FloatProperty(name="Threshold",
                                                description="Stipples located on faces below this lighting intensity"
                                                            "threshold will be discarded.",
                                                precision=2,
                                                default=0,
                                                min=0,
                                                max=100,
                                                subtype="PERCENTAGE")

    stipple_diffuse = bpy.props.FloatProperty(name="Diffuse",
                                              description="Desired weighting of diffuse light contribution to the "
                                                          "overall lighting",
                                              precision=1,
                                              default=1,
                                              min=0,
                                              soft_max=10)

    stipple_shadow = bpy.props.FloatProperty(name="Shadow",
                                             description="Desired weighting of shadow contribution to the "
                                                         "overall lighting",
                                             precision=1,
                                             default=1,
                                             min=0,
                                             soft_max=10)

    stipple_ao = bpy.props.FloatProperty(name="AO",
                                         description="Desired weighting of ambient occlusion's contribution to the "
                                                     "overall lighting",
                                         precision=1,
                                         default=1,
                                         min=0,
                                         soft_max=10)

    stipple_head_radius = bpy.props.FloatProperty(name="Head Radius",
                                                  description="Head radius of the stipple stroke",
                                                  precision=1,
                                                  default=1,
                                                  min=0,
                                                  soft_max=10,
                                                  subtype="PIXEL")

    stipple_tail_radius = bpy.props.FloatProperty(name="Tail Radius",
                                                  description="Tail radius of the stipple stroke",
                                                  precision=1,
                                                  default=0,
                                                  min=0,
                                                  soft_max=10,
                                                  subtype="PIXEL")

    stipple_length = bpy.props.FloatProperty(name="Length",
                                             description="Length of the stipple stroke, defined as the "
                                                         "distance between the center of the head and tail.",
                                             precision=1,
                                             default=30,
                                             min=0,
                                             soft_max=200,
                                             subtype="PIXEL")

    stipple_density_factor = bpy.props.FloatProperty(name="Density Factor",
                                                     description="The combined light intensity map will be scaled by "
                                                                 "this linear factor prior to computation of stipple placement",
                                                     precision=4,
                                                     default=0.002,
                                                     min=0,
                                                     soft_max=1,
                                                     step=1)

    stipple_min_allowable = bpy.props.FloatProperty(name="Min Intensity",
                                                    description="Floor limit on intensity",
                                                    precision=4,
                                                    default=0.004,
                                                    min=0,
                                                    soft_max=1,
                                                    step=1)

    stipple_density_exponent = bpy.props.FloatProperty(name="Density Exponent",
                                                       description="The combined light intensity map will be scaled by "
                                                                   "this power prior to computation of stipple placement",
                                                       precision=2,
                                                       default=1,
                                                       min=0,
                                                       soft_max=10)


classes = (
    NPRSystemSettings,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.Scene.system_settings = bpy.props.PointerProperty(type=NPRSystemSettings)


def unregister():
    from bpy.utils import unregister_class

    for cls in classes:
        unregister_class(cls)
