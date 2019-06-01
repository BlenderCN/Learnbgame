import logging
import math

import numpy as np
import svgpathtools as svgp
import svgwrite
from scipy import stats, ndimage
from skimage import measure, util, feature, morphology, graph

from blender_hand_drawn_npr.model.primitives import Path, Curve1D, CurvedStroke, DirectionalStippleStroke
from blender_hand_drawn_npr.model.third_party.variable_density import moving_front_nodes

logger = logging.getLogger(__name__)


def create_curved_stroke(construction_curve, hifi_path, thickness_parameters, surface, settings):
    upper_path = construction_curve.offset(interval=settings.curve_sampling_interval,
                                           hifi_path=hifi_path,
                                           thickness_parameters=thickness_parameters,
                                           surface=surface,
                                           positive_direction=True)

    upper_curve = Curve1D(fit_path=upper_path, settings=settings)

    lower_path = construction_curve.offset(interval=settings.curve_sampling_interval,
                                           hifi_path=hifi_path,
                                           thickness_parameters=thickness_parameters,
                                           surface=surface,
                                           positive_direction=False)
    lower_curve = Curve1D(fit_path=lower_path, settings=settings)

    return CurvedStroke(upper_curve=upper_curve, lower_curve=lower_curve)


class Silhouette:
    """
    A Silhouette is a collection of Strokes which capture the silhouette of the render subject.
    """

    def __init__(self, surface, settings):
        self.surface = surface
        self.settings = settings
        self.paths = []
        self.boundary_curves = []
        self.clip_path_d = None
        self.svg_strokes = []

    def __generate_clip_path(self):

        # Combine curves into a single path.
        combined = svgp.path.concatpaths([svgp.parse_path(curve) for curve in self.boundary_curves])
        self.clip_path_d = combined.d()

    def generate(self):
        """
        Make all such classes which produce paths implement this method to allow for polymorphic calls?
        :return: A collection of Paths which encompass the silhouette of the render subject.
        """

        contours = measure.find_contours(self.surface.obj_image, 0.99)

        # find_contours may return more than one contour set. Assume the "correct" contour is the longest path in
        # the set.
        contour = max(contours, key=len)

        # Create the initial Path.
        path = Path([[coord[1], coord[0]] for coord in contour])

        # Initial Path must be split into multiple Paths if corners are present.
        corners = path.find_corners(self.surface.obj_image, self.settings.harris_min_distance,
                                    self.settings.subpix_window_size)
        logger.info("Silhouette corners found: %d", len(corners))

        if corners:
            self.paths += path.split_corners(corners)
        else:
            self.paths.append(path)

        logger.info("Silhouette Paths found: %d", len(self.paths))

        for path in self.paths:
            hifi_path = path.round().bump(self.surface).remove_dupes().simple_cull(self.settings.cull_factor)
            fit_path = hifi_path.optimise(self.settings.optimise_factor)

            if len(fit_path.points) < 2:
                logger.debug("Silhouette path of length %d ignored.", len(path.points))
                continue

            logger.debug("Creating Silhouette stroke...")
            construction_curve = Curve1D(fit_path=fit_path, settings=self.settings)
            self.boundary_curves.append(construction_curve.d)
            stroke = create_curved_stroke(construction_curve=construction_curve,
                                          hifi_path=hifi_path,
                                          thickness_parameters=self.settings.silhouette_thickness_parameters,
                                          surface=self.surface,
                                          settings=self.settings)
            svg_stroke = svgwrite.path.Path(fill=self.settings.stroke_colour, stroke_width=0)
            svg_stroke.push(stroke.d)
            self.svg_strokes.append(svg_stroke)

            logger.info("Silhouette Strokes prepared: %d", len(self.svg_strokes))

        self.__generate_clip_path()


class InternalEdges:

    def __init__(self, surface, settings):
        self.settings = settings
        self.surface = surface

        self.paths = []
        self.boundary_curves = []

        self.svg_strokes = []

    def __find_paths(self):

        logger.debug("Generating Internal Edges...")

        # By using the object image as a mask we find only internal edges and disregard silhouette edges.
        edge_image = feature.canny(self.surface.z_image, sigma=1, mask=self.surface.obj_image.astype(bool))

        # Identify all continuous lines.
        labels = measure.label(edge_image, connectivity=2)

        for region in measure.regionprops(labels):
            image = region.image

            if image.shape < (3, 3):
                continue

            # Condition the line to ensure each cell has only one or two neighbours (remove "L"s).
            image = morphology.skeletonize(image)

            # A cell with only one neighbour can be considered as the end of a continuous line, i.e
            # the sum of a cell's 8 surrounding neighbours will equal 1.
            kernel = [[1, 1, 1],
                      [1, 0, 1],
                      [1, 1, 1]]
            convolved = ndimage.convolve(image.astype(float), kernel, mode="constant")
            # Refine the convolution to only contain cells which were present in the original image.
            convolved[util.invert(image)] = 0

            # Extract the region coordinates of cells which meet the condition for being a start/end position.
            terminator_pair = np.argwhere(convolved == 1)

            if len(terminator_pair) < 2:
                # Unable to extract two meaningful points.
                continue

            # Make edges have a value of 0 ("cheap").
            image = util.invert(image)

            # An ordered list of coordinates for each line is now found by computing the cheapest route between each
            # terminator_pair.
            route, cost = graph.route_through_array(image, terminator_pair[0], terminator_pair[1])

            # Convert regional route coords back to global coords.
            region_offset = [region.bbox[0], region.bbox[1]]
            coords = np.array(route) + region_offset
            self.paths.append(Path(coords, is_rc=True))

    def generate(self):
        self.__find_paths()

        for path in self.paths:
            hifi_path = path.round().bump_z(self.surface).remove_dupes().simple_cull(self.settings.cull_factor)
            fit_path = hifi_path.optimise(self.settings.optimise_factor)

            if len(fit_path.points) < 2:
                logger.debug("Internal Edge path of length %d ignored.", len(path.points))
                continue

            logger.debug("Creating Internal Edge stroke...")
            construction_curve = Curve1D(fit_path=fit_path, settings=self.settings)
            self.boundary_curves.append(construction_curve.d)
            stroke = create_curved_stroke(construction_curve=construction_curve,
                                          hifi_path=hifi_path,
                                          thickness_parameters=self.settings.internal_edge_thickness_parameters,
                                          surface=self.surface,
                                          settings=self.settings)
            svg_stroke = svgwrite.path.Path(fill=self.settings.stroke_colour, stroke_width=0)
            svg_stroke.push(stroke.d)
            self.svg_strokes.append(svg_stroke)


class Streamlines:
    """
    Streamlines are a collection of SVG Streamline strokes.
    """

    def __init__(self, surface, settings):
        self.settings = settings
        self.surface = surface
        self.svg_strokes = []

    def generate(self):
        u_image = self.surface.u_image
        v_image = self.surface.v_image
        n = self.settings.streamline_segments

        u_separation, v_separation = (u_image.max() - u_image.min()) / n, \
                                     (v_image.max() - v_image.min()) / n
        logger.debug("Streamline separation (u, v): %s, %s", u_separation, v_separation)

        u_intensities = []
        for streamline_pos in range(1, n):
            u_intensities.append(streamline_pos * u_separation)
        logger.debug("Intensities (u): %s", u_intensities)

        v_intensities = []
        for streamline_pos in range(1, n):
            v_intensities.append(streamline_pos * v_separation)
        logger.debug("Intensities (v): %s", v_intensities)

        strokes = []
        for intensity in u_intensities:
            norm_image_component = self.surface.norm_x_image
            logger.debug("Creating (u) streamline at intensity %d...", intensity)
            u_streamline = Streamline(primary_uv_image_component=u_image,
                                      secondary_uv_image_component=v_image,
                                      norm_image_component=norm_image_component,
                                      surface=self.surface,
                                      intensity=intensity,
                                      settings=self.settings)
            u_streamline.generate()
            strokes += u_streamline.strokes

        for intensity in v_intensities:
            norm_image_component = self.surface.norm_y_image
            logger.debug("Creating (v) streamline at intensity %d...", intensity)
            v_streamline = Streamline(primary_uv_image_component=v_image,
                                      secondary_uv_image_component=u_image,
                                      norm_image_component=norm_image_component,
                                      surface=self.surface,
                                      intensity=intensity,
                                      settings=self.settings)
            v_streamline.generate()
            strokes += v_streamline.strokes

        for stroke in strokes:
            svg_stroke = svgwrite.path.Path(fill=self.settings.stroke_colour, stroke_width=0)
            svg_stroke.push(stroke.d)
            self.svg_strokes.append(svg_stroke)

        logger.info("Streamline Strokes prepared: %d", len(self.svg_strokes))


class Streamline:
    """
    A Streamline is a collection of Strokes which follow a specified UV intensity value.
    """

    def __init__(self, primary_uv_image_component, secondary_uv_image_component, norm_image_component,
                 surface, intensity, settings):
        self.primary_uv_image_component = primary_uv_image_component
        self.secondary_uv_image_component = secondary_uv_image_component
        self.norm_image_component = norm_image_component
        self.surface = surface
        self.intensity = intensity
        self.settings = settings

        self.paths = []
        self.strokes = []

    def generate(self):
        contours = measure.find_contours(self.primary_uv_image_component, self.intensity)
        logger.debug("Streamline contours found: %d", len(contours))

        for contour in contours:
            # Create the rough path.
            path = Path([[coord[1], coord[0]] for coord in contour])
            # Condition and create final paths.
            paths = path.round().bump(self.surface).remove_dupes() \
                .trim_uv(target_intensity=self.intensity,
                         primary_image=self.primary_uv_image_component,
                         secondary_image=self.secondary_uv_image_component,
                         primary_trim_size=self.settings.uv_primary_trim_size,
                         secondary_trim_size=self.settings.uv_secondary_trim_size)

            for path in paths:
                logger.debug("UV contour split into %d paths.", len(paths))

                hifi_path = path.simple_cull(self.settings.cull_factor)
                fit_path = hifi_path.optimise(self.settings.optimise_factor)

                num_points = len(fit_path.points)
                if num_points > 1:

                    # Store to allow plotting of construction points for debugging.
                    self.paths.append(fit_path)

                    construction_curve = Curve1D(fit_path=fit_path, settings=self.settings)
                    stroke = create_curved_stroke(construction_curve=construction_curve,
                                                  hifi_path=hifi_path,
                                                  thickness_parameters=self.settings.streamline_thickness_parameters,
                                                  surface=self.surface,
                                                  settings=self.settings)

                    self.strokes.append(stroke)
                else:
                    logger.debug("Streamline of length %d rejected", num_points)


class Stipples:
    """
    Stipples are a collection of SVG Stipple strokes.
    """

    def __init__(self, clip_path, intersect_boundaries, surface, settings):
        self.clip_path = clip_path
        self.intersect_boundaries = intersect_boundaries
        self.settings = settings
        self.surface = surface

        self.reference_image = None
        self.reference_stats = None
        self.svg_strokes = []

    def density_function(self, x, y):
        min = self.settings.stipple_parameters.density_fn_min
        factor = self.settings.stipple_parameters.density_fn_factor
        exponent = self.settings.stipple_parameters.density_fn_exponent

        density = np.maximum(min, (self.reference_image[int(round(y)), int(round(x))] ** exponent) * factor)

        return density

    def __prepare_reference(self):
        # Prepare component images, where areas of high intensity will correspond to areas of dense stroke placement.
        shadow = util.invert(self.surface.shadow_image)
        ao = util.invert(self.surface.ao_image)
        diff = util.invert(self.surface.diffdir_image)

        # Combine the images according to desired weights.
        combined = (self.settings.lighting_parameters.shadow * shadow) + \
                   (self.settings.lighting_parameters.ao * ao) + \
                   (self.settings.lighting_parameters.diffdir * diff)

        # Make areas outside the object boundary zero intensity to avoid unnecessary stroke placement here. These
        # strokes will later be discarded, but generating them in the first place leads to reduced performance.
        mask = self.surface.obj_image == 0
        combined[mask] = 0

        self.reference_image = combined

        # Compute the mean of intensities which lie within the object boundary.
        self.reference_stats = stats.describe(combined[util.invert(mask)])

    def generate(self):
        self.__prepare_reference()

        logger.debug("Computing Stipple nodes...")
        y_res, x_res = self.reference_image.shape
        nodes = moving_front_nodes(self.density_function, (0, 0, x_res - 1, y_res - 1))

        # Nodes coords will be used as image index coords, so must be rounded.
        nodes = np.round(nodes)

        threshold = self.settings.lighting_parameters.threshold * (self.reference_stats.minmax[1] -
                                                                   self.reference_stats.minmax[0])
        # Place a marker at each node location in image-space.
        image = np.zeros_like(self.reference_image)
        for node in nodes:
            coordinate = (int(node[1]), int(node[0]))
            if self.reference_image[coordinate] > threshold:
                image[coordinate] = 1

        # Clip all stipples placed outside of the object boundary.
        mask = self.surface.obj_image == 1
        image[util.invert(mask)] = 0

        # Extract the list of node coordinates from the image.
        nodes = np.argwhere(image)

        u_image = self.surface.u_image
        v_image = self.surface.v_image

        # Parse intersect boundaries for use in the main loop.
        intersect_boundaries = [svgp.parse_path(d) for d in self.intersect_boundaries]

        # Remember node coordinates remain in row, column format here.
        for node in nodes:
            target = u_image[node[0], node[1]]
            from skimage import draw
            # Search radius for suitable uv coordinate. The radius value limits the available stroke orientations, so
            # consider making this proportional to the stroke length - longer strokes will require more accurate
            # orientations, but this comes with a performance penalty.
            rr, cc = draw.circle_perimeter(r=node[0], c=node[1], radius=10)
            errors = {}
            for i in range(0, len(rr)):
                try:
                    candidate_v = v_image[rr[i], cc[i]]
                    # Select only for secondary coordinate values above the current value.
                    if candidate_v > v_image[node[0], node[1]]:
                        candidate_u = u_image[rr[i], cc[i]]
                        # Compute error, cast to Python int required to avoid issues with numpy uint16 overflow.
                        error = abs(target.item() - candidate_u.item())
                        errors[rr[i], cc[i]] = error
                except IndexError:
                    # Candidate index was off the image, ignore.
                    logger.warning("Candidate index was off the image.")
                    pass

            # There may be multiple minimums, but it's good enough to settle for the first that's encountered.
            try:
                tail = min(errors, key=errors.get)
            except ValueError:
                # Occurs if the node is off the image surface, just ignore this point if so.
                continue

            # Compute x and y deltas between node and tail.
            x_delta = tail[1] - node[1]
            y_delta = tail[0] - node[0]

            # Angle between these points.
            heading = math.degrees(math.atan2(y_delta, x_delta))

            stipple = DirectionalStippleStroke(length=self.settings.stipple_parameters.length,
                                               r0=self.settings.stipple_parameters.head_radius,
                                               r1=self.settings.stipple_parameters.tail_radius,
                                               p0=(node[1], node[0]),
                                               heading=heading)

            clip_path_url = "url(" + self.clip_path.get_iri() + ")"
            if self.settings.optimise_clip_paths:
                svgp_stipple = svgp.parse_path(stipple.d)
                found = []
                for intersect_boundary in intersect_boundaries:
                    found += intersect_boundary.intersect(svgp_stipple)

                if found:
                    svg_stroke = svgwrite.path.Path(fill=self.settings.stroke_colour, stroke_width=0,
                                                    clip_path=clip_path_url)
                else:
                    svg_stroke = svgwrite.path.Path(fill=self.settings.stroke_colour, stroke_width=0)

            else:
                svg_stroke = svgwrite.path.Path(fill=self.settings.stroke_colour, stroke_width=0,
                                                clip_path=clip_path_url)

            svg_stroke.push(stipple.d)
            self.svg_strokes.append(svg_stroke)


if __name__ == "__main__":
    pass
