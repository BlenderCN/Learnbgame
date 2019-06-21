"""Temporary Helper Module"""

import logging
import math
import numpy

import bpy
import mathutils

from . import constants
from . import helper

#import constants
#import helper

logger = logging.getLogger(__package__)


def uv_bounds(obj):
    """Returns uv bounds of an object

    :param bpy.types.Object obj: blender object
    :return: uv coordinates
    :rtype: tuple (float, float, float, float)

    :raises TypeError: if obj has no uv data attached

    """
    active_uv = obj.data.uv_layers.active

    if not hasattr(active_uv, "data"):
        logger.error("%s has no uv data", obj)
        raise TypeError("object has no uv data")

    u_max = max([mesh.uv[0] for mesh in active_uv.data])
    v_max = max([mesh.uv[1] for mesh in active_uv.data])
    u_min = min([mesh.uv[0] for mesh in active_uv.data])
    v_min = min([mesh.uv[1] for mesh in active_uv.data])

    logger.debug("%s uv bounds (%f, %f, %f, %f)", obj, u_min, u_max, v_min, v_max)

    return u_min, u_max, v_min, v_max


def grid_dimension(u, v, res):
    """Calculates grid dimension from uv bounds size

    :param float u: u size
    :param float v: v size
    :param float res: needed resolution
    :return: row, column count
    :rtype: tuple (int, int)

    :raises ValueError: if uv coordinates exceed 0.0-1.0 range

    """
    if u < 0.0 or u > 1.0 or v < 0.0 or v > 1.0:
        logger.error("uv coordinate out of bounds (%f, %f)", u, v)
        raise ValueError("uv coordinate out of bounds")

    minor = min(u, v)
    col = math.ceil(1.0 / res)
    row = math.ceil(minor / res)

    if minor is u:
        row, col = col, row

    logger.debug(
        "uv bounds (%f, %f) to grid dimension [%d][%d]",
        u, v, row, col
    )

    return int(col), int(row)


class UVGrid(object):
    """Convenience class to raster and project on uv mesh"""

    def __init__(self, obj, resolution=constants.DEFAULT_RESOLUTION):
        self._obj = obj
        self._scaling = obj['uv_scaling']
        self._resolution = resolution

        self._u_min, self._u_max, self._v_min, self._v_max = uv_bounds(obj)
        self._size_u = self._u_max - self._u_min
        self._size_v = self._v_max - self._v_min
        self._col, self._row = grid_dimension(
            self._size_u,
            self._size_v,
            self._resolution
        )

        self.reset_weights()
        self._uvcoords = [[[] for j in range(self._row)] for i in range(self._col)]
        self._gridmask = [[True for j in range(self._row)] for i in range(self._col)]

        self._masks = {
            "pre": [[[] for j in range(self._row)] for i in range(self._col)],
            "post": [[[] for j in range(self._row)] for i in range(self._col)]
            }

        self._converted = False

        self._grid = {}

        self._compute_uvcoords()

    def __del__(self):
        del self._weights
        self._obj = None

    def __repr__(self):
        return "<UVRaster uv: %s resolution: %f dimension: %s items: %d>" % \
               (self.uv_bounds, self.resolution, self.dimension, len(self))

    def __getitem__(self, index):
        return self._weights[index]

    def __setitem__(self, index):
        pass

    def __len__(self):
        return any([len(c) for r in self._weights for c in r if any(c)])
        
    def reset_weights(self):
        self._weights = [[[] for j in range(self._row)] for i in range(self._col)]

    # TODO(SK): Missing docstring
    @property
    def dimension(self):
        return (self._row, self._col)

    # TODO(SK): Missing docstring
    @property
    def resolution(self):
        return self._resolution

    # TODO(SK): Missing docstring
    @property
    def uv_bounds(self):
        return self._u_min, self._u_max, self._v_min, self._v_max

    # TODO(SK): Missing docstring
    def compute_pre_mask(self, kernel):
        self.compute_grid("pre", kernel)

    # TODO(SK): Missing docstring
    def compute_post_mask(self, kernel):
        self.compute_grid("post", kernel)
        self._grid['post'] = [item for sublist in self._grid['post'][:,:] for item in sublist]

    def compute_grid(self, mask, kernel):
        grid = numpy.zeros((self._col, self._row, self._col, self._row))
        # Padding for uv coordinates is half the size of a cell to center the coordinate
        padding_horizontal = self._size_u / self._col / 2.
        padding_vertical = self._size_v / self._row / 2.
        left, bottom = self._cell_index_to_uv(0, 0)
        right, top = self._cell_index_to_uv(self._col - 1, self._row - 1)
        x = numpy.linspace(left, right, self._col)
        y = numpy.linspace(bottom, top, self._row)
        guvs = numpy.dstack(numpy.meshgrid(x, y))[...,::-1]
        guvs = numpy.zeros((self._col, self._row, 2))
        for i in range(self._col):
            for j in range(self._row):
                guvs[i][j] = self._cell_index_to_uv(i, j)
        for i in range(self._col):
            for j in range(self._row):
                uvs = numpy.array([self._cell_index_to_uv(i, j)])
                # Create array with uv-coords
                grid[i][j] = kernel.apply(uvs, guvs)
        self._grid[mask] = grid

    def insert_postNeuron(self, index, uv, p_3d, d):
        if not self._in_bounds(uv[0], uv[1]):
            uv = self.adjustUV2(uv)
        col, row = self._uv_to_cell_index(uv[0], uv[1])
        if col == -1:
            return

        if self._gridmask[col][row]:
            self._masks['post'][col][row].append((index, self._cell_index_to_uv(col, row), p_3d, d))
        
    def convert_data_structures(self):
        """ Needs to be called after all neurons have been inserted (usually, this is
        done in select_random """
        self.convert_postNeuronStructure()
        self.convert_pre_neuron_structure()
        self._converted = True

    def convert_postNeuronStructure(self):
        """Converts post neuron structure to a flattened numpy array"""
        self._masks['post'] = numpy.array([item for sublist in self._masks['post'] for item in sublist])

    def convert_pre_neuron_structure(self):
        """Converts all cells in the grid to a flattened array, deletes weights that are outside 
        of the grid and normalizes the weights"""
        weights = numpy.array([len(cell) for cell in self._masks['post']])
        numpy.clip(weights, 0, 1, weights)
        
        grid = [[None] * self._row for _ in range(self._col)]
        for row in range(self._row):
            for col in range(self._col):
                g = self._grid['pre'][col][row].flatten() * weights
                weight_sum = numpy.sum(g)
                if weight_sum == 0:
                    continue
                g /= weight_sum
                grid[col][row] = numpy.array(g)
        self._grid['pre'] = grid

    def cell(self, u, v):
        """Returns cell for uv coordinate

        :param float u: u coordinate
        :param float v: v coordinate
        :return: cell
        :rtype: list

        """
        col, row = self._uv_to_cell_index(u, v)
        if row == -1:
            return []

        c = self._weights[col][row]

        logger.debug("cell at index [%d][%d]", col, row)

        return c

    def select_random(self, uv, quantity):
        """Returns a set of randomly selected items from uv coordinate
        corresponding cell

        :param uv: uv coordinates
        :type: tuple (float, float)
        :param int quantity: size of set
        :return: randomly selected items
        :rtype: list

        """
        if not self._in_bounds(uv[0], uv[1]):
            uv = self.adjustUV2(uv)

        col, row = self._uv_to_cell_index(uv[0], uv[1])
        if row == -1:
            return []
        
        # check, whether data structures have already been converted. If not, convert them
        if not self._converted:
            self.convert_data_structures()

        weights = self._grid['pre'][col][row]
        if weights is None:
            return []

        indices = numpy.random.choice(len(weights), size = quantity, p = weights)
        # select post-synaptic cell-array for synapse locations
        selected_cells = numpy.take(self._grid['post'], indices, axis = 0)

        synapse_coords = []
        # Get uv coordinate for selected indices
        for index in indices:
            row = index % self._row
            col = index // self._row
            synapse_coords.append(self._uvcoords[col][row])

        selected = []
        cell_indices = []

        for i, c in enumerate(selected_cells):
            # compute weights for cell
            weights = c.flatten()
            # Multiply by number of cells available
            weights *= [len(cells) for cells in self._masks['post']]
            # select with weighted probabilites one cell-index per cell
            cell_indices.append( numpy.random.choice(len(weights), size = 1, p = weights / numpy.sum(weights))[0] )

        post_cells = numpy.take(self._masks['post'], cell_indices, axis = 0)
        
        # select randomly post-neurons
        for p_index, p_cell in enumerate(post_cells):
            post_neuron = numpy.random.choice(len(p_cell))
            selected.append((p_cell[post_neuron], synapse_coords[p_index]))

        return selected

    def adjustUV(self, uv):
        """Return adjustd uv coordinates

        :param uv: uv coordinates
        :type uv: tuple (float, float)
        :return: adjusted uv coordinates
        :rtype: tuple (float, float)

        """
        if uv[0] >= self._u or vv[1] >= self._v or uv[0] < 0.0 or vv[0] < 0.0:
            uv[0] = min(self._u, max(0., uv[0]))
            uv[1] = min(self._v, max(0., vv[0]))
        return uv
        
    def adjustUV2(self, uv):
        """Return adjustd uv coordinates, corrected version with threshold

        :param uv: uv coordinates
        :type uv: tuple (float, float)
        :return: adjusted uv coordinates
        :rtype: tuple (float, float)

        """
        uv_new = [uv[0],uv[1]]
        uv_new[0] = min(self._u_max, max(self._u_min, uv[0]))
        uv_new[1] = min(self._v_max, max(self._v_min, uv[1]))
        
        #test if deviation is below threshold
        if (constants.UV_GRID_THRESHOLD*self._size_u > abs(uv_new[0]-uv[0])) and (constants.UV_GRID_THRESHOLD*self._size_v > abs(uv_new[1]-uv[1])):
            return uv_new
        else:
            return uv

    def _uv_to_cell_index(self, u, v):
        """Returns cell index for a uv coordinate"""
        if not self._in_bounds(u, v):
            # logger.error("uv coordinate out of bounds (%f, %f)", u, v)
            return -1, -1
            # u = min(self._u, max(0., u))
            # v = min(self._v, max(0., v))

        col = int(math.floor((u - self._u_min) / self._size_u * self._col))
        row = int(math.floor((v - self._v_min) / self._size_v * self._row))
        
        if u == self._u_max:      #if uv was adjusted, uv may be exactly on the upper border, which calculates to an invalid col,row value
            col = self._col-1     #but is, in fact, a valid coordinate.
        if v == self._v_max:
            row = self._row-1

        logger.debug("uv (%f, %f) to cell index [%d][%d]", u, v, col, row)

        return col, row

    def _cell_index_to_uv(self, col, row):
        """Returns uv coordinate from the center of a cell"""
        center_u = self._size_u / self._col / 2.
        center_v = self._size_v / self._row / 2.
        center = self.resolution / 2.
        u = col / self._col * self._size_u + center + self._u_min
        v = row / self._row * self._size_v + center + self._v_min

        logger.debug(
            "cell index [%d][%d] to center uv (%f, %f)",
            col, row, u, v
        )
        return u, v

    def _compute_uvcoords(self):
        """Computes corresponding uv coordinate across grid"""
        for col in range(self._col):
            for row in range(self._row):
                u, v = self._cell_index_to_uv(col, row)
                self._uvcoords[col][row] = numpy.array((u, v))
                if self._onGrid(numpy.array((u, v))) == 0:
                    self._gridmask[col][row] = False

    def _in_bounds(self, u, v):
        """Checks if a uv coordinate is inside uv bounds"""
        return u <= self._u_max and v <= self._v_max and u >= self._u_min and v >= self._v_min

    def _reset_weights(self):
        """Resets weights across the grid"""
        self._weights = [[[] for j in range(self._row)]
                         for i in range(self._col)]

    def _onGrid(self, uv):
        """Converts a given UV-coordinate into a 3d point,
        object for the 3d point and object_uv must have the same topology
        if normal is not None, the normal is used to detect the point on object, otherwise
        the closest_point_on_mesh operation is used
        """

        result = 0
        for p in self._obj.data.polygons:
            uvs = [self._obj.data.uv_layers.active.data[li] for li in p.loop_indices]
            result = mathutils.geometry.intersect_point_tri_2d(
                uv,
                uvs[0].uv,
                uvs[1].uv,
                uvs[2].uv
            )

            if (result == 1) | (result == -1):
                result = 1
                break
            else:
                result = mathutils.geometry.intersect_point_tri_2d(
                    uv,
                    uvs[0].uv,
                    uvs[2].uv,
                    uvs[3].uv
                )

                if (result == 1) | (result == -1):
                    result = 1
                    break

        return result
