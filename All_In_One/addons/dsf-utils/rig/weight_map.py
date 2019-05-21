import types, itertools, array, functools, bisect, math
import operator

class weight_map (object):
  """weight map interface: represents a function that order a weight
     (single value) to any given vertex of the mesh.
  """
  def __init__ (self):
    """initialize a weight map. This baseclass represents an empty map.
    """
    pass
  def get_weight (self, index):
    """return the weight for the vertex at the given index.
    """
    # default implementation: return 0 (represents an empty weightmap).
    return 0
  def get_domain (self):
    """return the index range this weight map is defined on.
       Subclasses should overwrite this function to make it as narrow
       as possible.
    """
    # default: return an empty range
    return (0, 0)

class geometric_map (weight_map):
  """weight map that is based on geometric location of a vertex
     rather than on an index. subclasses must implement get_coord_weight
     which gets called by the implementation of get_weight.
  """
  def __init__ (self, lookup = None):
    """initialize with a lookup function. The lookup function
       transforms a vertex number to its coordinates.
    """
    assert (callable (lookup))
    self.lookup = lookup
  def get_weight (self, index):
    """gets the coordinates of vertex index and calls get_coord_weight.
    """
    return self.get_coord_weight (self.lookup (index))
  def get_coord_weight (self, coord):
    """default implementation of a weight.
    """
    raise NotImplementedError ("get_coord_weight undefined.")

class transform_map (geometric_map):
  """weight map helper for weight maps based on a geometric transformation
     to calculate a weight. implements the get-coord-weight function by calling
     the get_local_weight function to be implemented by subclasses.
  """
  def __init__ (self, transformation = None, lookup = None):
    """initialize with a transformation which transforms
       a point in 3d-space to another coordinate system.
    """
    super (transform_map, self).__init__ (lookup = lookup)
    assert (callable (transformation))
    self.transformation = transformation
  def get_coord_weight (self, coord):
    """transform coord and call the get_local_weight function on self.
    """
    return self.get_local_weight (self.transformation (coord))
  def get_local_weight (self, coords):
    """calculate a weight for a vertex that is given in local coordinates.
       subclasses need to overwrite this method.
    """
    raise NotImplementedError ("calc_vertex undefined.")

class angle_map (transform_map):
  """a weight map that applies a transformation to a vertex,
     projects it into the xy-plane and uses the angle between the
     x-axis and the vector (positive direction) to create a weight-value.
  """
  def __init__ (self, incl = None, excl = None, **kwarg):
    """incl is two angles which get weight 1
       excl is two angles for weight 0
       the rest is interpolated somehow.
    """
    assert (incl)
    assert (excl)
    super (angle_map, self).__init__ (**kwarg)
    incl = (min (incl), max (incl))
    excl = (min (excl), max (excl))
    self.angles = list ()
    self.angles.extend ([(incl[0], 1), (incl[1], 1)])
    self.angles.extend ([(excl[0], 0), (excl[1], 0)])
    self.angles.sort ()
    (min_a, min_w) = self.angles[0]
    (max_a, max_w) = self.angles[-1]
    self.angles.insert (0, (max_a - 360, max_w))
    self.angles.append ((min_a + 360, min_w))
  def get_local_weight (self, coords):
    """calculate the weight for the vertex with the given coordinates.
       coords are a position in local space.
    """
    angle = math.degrees (math.atan2 (coords[1], coords[0])) % 360
    # search for the two angles-weights surrounding the angle.
    pos = 1
    while pos != 5:
      if angle < self.angles[pos][0]:
        break
      else:
        pos += 1;
    # angle[pos-1] is less than angle, angle[pos] is greater than angle.
    (left_a, left_w) = self.angles[pos-1]
    (right_a, right_w) = self.angles[pos]
    # ratio = 0 when near the left angle, 1 when near the right angle
    ratio = (angle - left_a) / (right_a - left_a)
    weight = (1 - ratio) * left_w + ratio * right_w
    return weight

class zdist_map (transform_map):
  """weight map implementation that applies a transformation to a vertex,
     measures its value along the z-axis and uses that value to check
     if a predefined interval is met.
  """
  def __init__ (self, zmin = None, zmax = None, **kwarg):
    """initialize a zdist map with the zrange [zmin, zmax]. z-values
       below zmin get a weight of 0, z-values above zmax get a weight of 1,
       intermediate values are interpolated linearly.
    """
    super (zdist_map, self).__init__ (**kwarg)
    assert (zmin is not None)
    assert (zmax is not None)
    self.zmin = zmin
    self.zmax = zmax
  def get_local_weight (self, coords):
    """calculate the weight for the vertex with the given coordinates.
       coords are the vertex position in local space.
    """
    zdist = coords[2]
    if zdist < self.zmin:
      return 0
    elif self.zmax < zdist:
      return 1
    else:
      return (zdist - self.zmin) / (self.zmax - self.zmin)

class sphere_dist_map (transform_map):
  """weight map that uses the inclusion of a vertex within a ellipsoid
     to return a weight between 0 (in the center of the ellipsoid) and
     infinity (somewhere outside the ellipsoid). The exact border of
     the ellipsoid gets weight 1. This is basically the relative distance
     to the center.
  """
  def __init__ (self, sphere_mat, **kwarg):
    """initialize a sphere_dist_map with a given matrix sphere_mat which
       transforms the unit sphere into an ellipsoid in global space.
    """
    sphere_inv_func = sphere_mat.inverted ().__mul__
    super (sphere_dist_map, self).__init__\
        (transformation = sphere_mat.inverted ().__mul__, **kwarg)
  def get_local_weight (self, coord):
    """return how near coord is to the center of the ellipsoid.
    """
    return coord.length

class sphere_map (geometric_map):
  """weight map implementation that uses an inclusion/exclusion-sphere
     to calculate a weight.
  """
  def __init__ (self, inner = None, outer = None, **kwarg):
    """initialize a sphere map with two ellipsoids inner and outer.
       inner and outer are given as matrices transforming the unit-sphere
       into the respective ellipsoids.
    """
    super (sphere_map, self).__init__ (**kwarg)
    assert (inner)
    assert (outer)
    self.inner_map = sphere_dist_map (inner, **kwarg)
    self.outer_map = sphere_dist_map (outer, **kwarg)
  def get_weight (self, index):
    """calculate a weight for vertex at the given index.
    """
    global_coord = self.lookup (index)
    # greedily calculate the inner and outer weight; it would be more
    # performant to calculate the inner first and the outer only when
    # needed. something todo when it is too slow.
    inner_weight = self.inner_map.get_coord_weight (global_coord)
    outer_weight = self.outer_map.get_coord_weight (global_coord)
    if inner_weight <= 1:
      return 1.0
    elif outer_weight > 1:
      return 0
    else:
      # todo: do some interpolation here, perhaps use the relation
      # between inner and outer scaled to [0, 1]
      return 0.5

class group_map (weight_map):
  """weight map implementation where each vertex only has a weight
     of 1 or 0 (i.e. contained or not).
  """
  def __init__ (self, idxs, **kwarg):
    """initialize with a list of vertex numbers idxs.
    """
    super (group_map, self).__init__ (**kwarg)
    idxs_list = list (idxs)
    idxs_list.sort ()
    self.idxs = array.array ('i', idxs_list)
    self.min = self.idxs[0]
    self.max = self.idxs[-1] + 1
  def get_weight (self, index):
    """check for containment in the group.
    """
    if self.min <= index < self.max:
      idxidx = bisect.bisect_left (self.idxs, index)
      if self.idxs[idxidx] == index:
        return 1
      else:
        return 0
    else:
      return 0
  def get_domain (self):
    """return the minimum and maximum vertex number of the group.
    """
    return (self.min, self.max)
    
class sparse_table (object):
  """class to implement index lookup based on a dictionary.
  """
  def __init__ (self, indices, values):
    """initialize this object with an iterable of indices
       and an iterable of values.
    """
    assert (len (indices) == len (values))
    self.data = {
      idx: val for (idx, val) in itertools.zip_longest (indices, values)
    }
  def get_value (self, index):
    """return the value for the given index.
    """
    if index in self.data:
      return self.data[index]
    else:
      return 0

class dense_table (object):
  """class to implement index lookup based on a single array
     of values.
  """
  def __init__ (self, indices, values):
    """initialize this object with a list of indices
       and an iterable of values.
    """
    assert (len (indices) == len (values))
    self.low = min (indices)
    self.high = max (indices) + 1
    self.data = array.array ('f', [0.0] * (self.high - self.low))
    for index, value in itertools.zip_longest (indices, values):
      self.data[index - self.low] = value
  def get_value (self, index):
    """return the value for the given index.
    """
    if self.low <= index and index <= self.high:
      return self.data[index - self.low]
    else:
      return 0.0

class linear_table (object):
  """class to implement index lookup based on two arrays.
  """
  def __init__ (self, indices, values):
    """initialize this object with a list of indices
       and an iterable of values. indices must be sorted.
    """
    assert (len (indices) == len (values))
    self.value = array.array ('f', values)
    self.index = array.array ('i', indices)
  def get_value (self, index):
    """return the value for the given index.
    """
    idx_pos = bisect.bisect_left (self.index, index)
    if idx_pos == len (self.index):
      return 0.0
    elif self.index[idx_pos] == index:
      return self.value[idx_pos]
    else:
      return 0.0
  
class table_map (weight_map):
  """weight map that simply uses a stored array of values to deliver these
     as weight values.
  """
  def __init__ (self, indices, values, **kwarg):
    """initialize a weight map given by a table.
       @param indices is a list of indexes for the weightmap.
       @param values is an iterable return weights.
    """
    super (table_map, self).__init__ (**kwarg)
    (low, high) = (min (indices), max (indices) + 1)
    assert (len (indices) < high - low)
    density = len (indices) / (high - low)
    if density < 0.1:
      self.data = sparse_table (indices, values)
    elif density < 0.7:
      self.data = linear_table (indices, values)
    else:
      self.data = dense_table (indices, values)
    self.domain = (low, high)
  def get_domain (self):
    """overwritten domain function returns an actually usable range.
    """
    return self.domain
  def get_weight (self, index):
    """return the value for the given index.
    """
    return self.data.get_value (index)

def multiply_map (weight_map):
  """define a weight map by multiplying multiple maps.
  """
  def __init__ (self, *arg, **kwarg):
    """takes a variable number of arguments, each is a weight-map.
    """
    super (multiply_map, self).__init__ (**kwarg)
    self.submaps = list (arg)
    (self.min, self.max) = super (multiply_map, self).get_domain ()
    for submap in self.submaps:
      (submin, submax) = submap.get_domain ()
      self.min = max (self.min, submin)
      self.max = min (self.max, submax)
  def get_weight (self, index):
    """return the product of all weights.
    """
    if self.min <= index < self.max:
      return functools.reduce\
          (operator.mul, map (lambda sub: sub.get_weight (index)))
    else:
      return 0
  def get_domain (self):
    """return the intersection of all subdomains.
    """
    return (self.min, self.max)

class scale_map (weight_map):
  """a map that is the same as another map scaled by a constant.
  """
  def __init__ (self, factor, other, **kwarg):
    """initialize with another map other and a constant scaling factor.
    """
    super (scale_map, self).__init__ (**kwarg)
    self.factor = factor
    self.other = other
  def get_weight (self, index):
    """return the scaled weight of index.
    """
    other_weight = self.other.get_weight (index)
    return self.factor * other_weight
  def get_domain (self):
    return self.other.get_domain ()

class average_map (weight_map):
  """define a weight map by averaging multiple maps.
  """
  def __init__ (self, *arg, **kwarg):
    """takes a variable number of arguments, each is a weight-map.
    """
    super (average_map, self).__init__ (**kwarg)
    self.submaps = list (*arg)
    (self.min, self.max) = super (average_map, self).get_domain ()
    for submap in self.submaps:
      (submin, submax) = submap.get_domain ()
      self.min = min (self.min, submin)
      self.max = max (self.max, submax)
  def get_weight (self, index):
    """return the average of all weights.
    """
    added = functools.reduce\
        (operator.add, map (lambda sub: sub.get_weight (index), self.submaps))
    return added / len (self.submaps)
  def get_domain (self):
    """return the union of all subdomains.
    """
    return (self.min, self.max)
