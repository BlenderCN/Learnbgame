import logging
import os

import svgwrite

from blender_hand_drawn_npr.model.elements import Silhouette, InternalEdges, Streamlines, Stipples
from blender_hand_drawn_npr.model.data import Surface

logger = logging.getLogger(__name__)


class Illustrator:

    def __init__(self, settings):
        self.settings = settings

        # Load render pass images from disk.
        self.surface = Surface()
        self.surface.init_obj_image(os.path.join(self.settings.in_path, "IndexOB0001.png"))
        self.surface.init_z_image(os.path.join(self.settings.in_path, "Depth0001.png"))
        self.surface.init_diffdir_image(os.path.join(self.settings.in_path, "DiffDir0001.png"))
        self.surface.init_norm_image(os.path.join(self.settings.in_path, "Normal0001.tif"))
        self.surface.init_uv_image(os.path.join(self.settings.in_path, "UV0001.tif"))
        self.surface.init_shadow_image(os.path.join(self.settings.in_path, "Shadow0001.png"))
        self.surface.init_ao_image(os.path.join(self.settings.in_path, "AO0001.png"))

        illustration_dimensions = (self.surface.obj_image.shape[1],
                                   self.surface.obj_image.shape[0])
        self.illustration = svgwrite.Drawing(self.settings.out_filepath, illustration_dimensions)

        self.intersect_boundaries = []

    def illustrate(self):
        # Silhouettes are essential to generate as they are used for clipping paths.
        silhouette = Silhouette(surface=self.surface, settings=self.settings)
        silhouette.generate()
        [self.illustration.add(svg_stroke) for svg_stroke in silhouette.svg_strokes]
        [self.intersect_boundaries.append(boundary_curve) for boundary_curve in silhouette.boundary_curves]
        clip_path = self.illustration.defs.add(self.illustration.clipPath(id='silhouette_clip_path'))
        clip_path.add(svgwrite.path.Path(silhouette.clip_path_d))

        if self.settings.enable_internal_edges:
            internal_edges = InternalEdges(surface=self.surface, settings=self.settings)
            internal_edges.generate()
            [self.illustration.add(svg_stroke) for svg_stroke in internal_edges.svg_strokes]

        if self.settings.enable_streamlines:
            streamlines = Streamlines(surface=self.surface, settings=self.settings)
            streamlines.generate()
            [self.illustration.add(svg_stroke) for svg_stroke in streamlines.svg_strokes]

        if self.settings.enable_stipples:
            stipples = Stipples(clip_path=clip_path, intersect_boundaries=self.intersect_boundaries,
                                surface=self.surface, settings=self.settings)
            stipples.generate()
            [self.illustration.add(svg_stroke) for svg_stroke in stipples.svg_strokes]

    def save(self):
        self.illustration.save()

        logger.info("Illustration saved to: %s", self.settings.out_filepath)


if __name__ == "__main__":

    # Example of stand-alone operation.

    from blender_hand_drawn_npr.model.data import Settings, LightingParameters, StippleParameters, ThicknessParameters

    settings = Settings(out_filepath="/tmp/out.svg",
                        cull_factor=50,
                        optimise_factor=5,
                        curve_fit_error=0.01,
                        harris_min_distance=40,
                        subpix_window_size=20,
                        curve_sampling_interval=20,
                        stroke_colour="black",
                        streamline_segments=64,
                        silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                            stroke_curvature=0),
                        internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=3, diffdir=0,
                                                                               stroke_curvature=0),
                        streamline_thickness_parameters=ThicknessParameters(const=0, z=0.5, diffdir=1,
                                                                            stroke_curvature=0),
                        uv_primary_trim_size=200,
                        uv_secondary_trim_size=20,
                        lighting_parameters=LightingParameters(diffdir=1.5, shadow=1, ao=2,
                                                               threshold=0.25),
                        stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=40,
                                                             density_fn_min=0.005,
                                                             density_fn_factor=0.0025,
                                                             density_fn_exponent=2),
                        optimise_clip_paths=True,
                        enable_internal_edges=True,
                        enable_streamlines=True,
                        enable_stipples=True,
                        in_path="/tmp/")

    illustrator = Illustrator(settings)
    illustrator.illustrate()
    illustrator.save()
