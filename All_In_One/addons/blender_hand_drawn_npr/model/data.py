import logging
from collections import namedtuple

import imageio
from skimage import io, exposure

logger = logging.getLogger(__name__)

Settings = namedtuple("Settings", ["cull_factor",
                                   "optimise_factor",
                                   "curve_fit_error",
                                   "harris_min_distance",
                                   "subpix_window_size",
                                   "curve_sampling_interval",
                                   "stroke_colour",
                                   "streamline_segments",
                                   "silhouette_thickness_parameters",
                                   "internal_edge_thickness_parameters",
                                   "streamline_thickness_parameters",
                                   "uv_primary_trim_size",
                                   "uv_secondary_trim_size",
                                   "lighting_parameters",
                                   "stipple_parameters",
                                   "optimise_clip_paths",
                                   "enable_internal_edges",
                                   "enable_streamlines",
                                   "enable_stipples",
                                   "in_path",
                                   "out_filepath"])

ThicknessParameters = namedtuple("ThicknessParameters", ["const",
                                                         "z",
                                                         "diffdir",
                                                         "stroke_curvature"])

LightingParameters = namedtuple("LightingParameters", ["diffdir",
                                                       "shadow",
                                                       "ao",
                                                       "threshold"])

StippleParameters = namedtuple("StippleParameters", ["head_radius",
                                                     "tail_radius",
                                                     "length",
                                                     "density_fn_min",
                                                     "density_fn_factor",
                                                     "density_fn_exponent"])


class Surface:

    def __init__(self, obj_image=None, z_image=None, diffdir_image=None,
                 norm_x_image=None, norm_y_image=None, norm_z_image=None,
                 u_image=None, v_image=None, shadow_image=None, ao_image=None):
        self.obj_image = obj_image
        self.z_image = z_image
        self.diffdir_image = diffdir_image
        self.norm_image = None
        self.norm_x_image = norm_x_image
        self.norm_y_image = norm_y_image
        self.norm_z_image = norm_z_image
        self.u_image = u_image
        self.v_image = v_image
        self.shadow_image = shadow_image
        self.ao_image = ao_image

        self.SurfaceData = namedtuple("SurfaceData", "obj z diffdir norm_x norm_y norm_z u v")

    def init_obj_image(self, file_path):
        self.obj_image = io.imread(file_path, as_gray=True)
        logger.info("Object image loaded: %s", file_path)

    def init_z_image(self, file_path):
        self.z_image = io.imread(file_path, as_gray=True)
        logger.info("Z image loaded: %s", file_path)

    def init_diffdir_image(self, file_path):
        self.diffdir_image = io.imread(file_path, as_gray=True)
        logger.info("Diffdir image loaded: %s", file_path)

    def init_norm_image(self, file_path):
        norm_image = imageio.imread(file_path)
        logger.info("Normal image loaded: %s", file_path)
        # Original image will be mapped to non-linear colourspace. Correct the normals by adjusting this.
        norm_image = exposure.adjust_gamma(norm_image, 2.2)
        self.norm_image = norm_image

        # Normal x values are encoded in red channel.
        self.norm_x_image = norm_image[:, :, 0]
        # Normal y values are encoded in green channel.
        self.norm_y_image = norm_image[:, :, 1]
        # Normal z values are encoded in blue channel.
        self.norm_z_image = norm_image[:, :, 2]

    def init_uv_image(self, file_path):
        # 16-bit colour-depth, use imageio.
        uv_image = imageio.imread(file_path)
        # Original image will be mapped to non-linear colourspace. Correct the uv coordinates by adjusting this.
        uv_image = exposure.adjust_gamma(uv_image, 2.2)

        # u coordinates are encoded in red channel.
        self.u_image = uv_image[:, :, 0]
        # v coordinates are encoded in green channel.
        self.v_image = uv_image[:, :, 1]

        logger.info("UV image loaded: %s", file_path)

    def init_shadow_image(self, file_path):
        self.shadow_image = io.imread(file_path, as_gray=True)
        logger.info("Shadow image loaded: %s", file_path)

    def init_ao_image(self, file_path):
        self.ao_image = io.imread(file_path, as_gray=True)
        logger.info("AO image loaded: %s", file_path)

    def at_point(self, x, y):
        assert x >= 0
        assert y >= 0
        assert 0 <= x <= self.obj_image.shape[1]
        assert 0 <= y <= self.obj_image.shape[0]

        x = int(x)
        y = int(y)

        surface_data = self.SurfaceData(obj=self.obj_image[y, x],
                                        z=self.z_image[y, x],
                                        diffdir=self.diffdir_image[y, x],
                                        norm_x=self.norm_x_image[y, x],
                                        norm_y=self.norm_y_image[y, x],
                                        norm_z=self.norm_z_image[y, x],
                                        u=self.u_image[y, x],
                                        v=self.v_image[y, x])
        return surface_data

    def is_valid(self, point):
        surface_data = self.at_point(point[0], point[1])
        return surface_data.obj != 0

    def compute_curvature(self, path, target_image):
        for i in range(0, len(path.points) - 1):
            cur_norm = self.at_point(path.points[i][0], path.points[i][1]).norm
            next_norm = self.at_point(path.points[i + 1][0], path.points[i + 1][1]).norm

            delta = abs(cur_norm - next_norm)

            if target_image is self.u_image:
                self.u_curvature_image[path.points[i][1], path.points[i][0]] = delta
            elif target_image is self.v_image:
                self.v_curvature_image[path.points[i][1], path.points[i][0]] = delta
            else:
                logger.warning("UV image mismatch!")
