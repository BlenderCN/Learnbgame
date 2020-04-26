'''Geometry Utilities (mathutils.geometry)
   The Blender geometry module
   
'''


def area_tri(v1, v2, v3):
   '''Returns the area size of the 2D or 3D triangle defined.
      
      Arguments:
      @v1 (mathutils.Vector): Point1
      @v2 (mathutils.Vector): Point2
      @v3 (mathutils.Vector): Point3

   '''

   return float

def barycentric_transform(point, tri_a1, tri_a2, tri_a3, tri_b1, tri_b2, tri_b3):
   '''Return a transformed point, the transformation is defined by 2 triangles.
      
      Arguments:
      @point (mathutils.Vector): The point to transform.
      @tri_a1 (mathutils.Vector): source triangle vertex.
      @tri_a2 (mathutils.Vector): source triangle vertex.
      @tri_a3 (mathutils.Vector): source triangle vertex.

      @returns (mathutils.Vector): The transformed point
   '''

   return mathutils.Vector

def box_fit_2d(points):
   '''Returns an angle that best fits the points to an axis aligned rectangle
      
      Arguments:
      @points (list): list of 2d points.

      @returns (float): angle
   '''

   return float

def box_pack_2d(boxes):
   '''Returns the normal of the 3D tri or quad.
      
      Arguments:
      @boxes (list): list of boxes, each box is a list where the first 4 items are [x, y, width, height, ...] other items are ignored.

      @returns ((float, float)): the width and height of the packed bounding box
   '''

   return (float, float)

def convex_hull_2d(points):
   '''Returns a list of indices into the list given
      
      Arguments:
      @points (list): list of 2d points.

      @returns (list of ints): a list of indices
   '''

   return list of ints

def distance_point_to_plane(pt, plane_co, plane_no):
   '''Returns the signed distance between a point and a plane    (negative when below the normal).
      
      Arguments:
      @pt (mathutils.Vector): Point
      @plane_co (mathutils.Vector): A point on the plane
      @plane_no (mathutils.Vector): The direction the plane is facing

   '''

   return float

def interpolate_bezier(knot1, handle1, handle2, knot2, resolution):
   '''Interpolate a bezier spline segment.
      
      Arguments:
      @knot1 (mathutils.Vector): First bezier spline point.
      @handle1 (mathutils.Vector): First bezier spline handle.
      @handle2 (mathutils.Vector): Second bezier spline handle.
      @knot2 (mathutils.Vector): Second bezier spline point.
      @resolution (int): Number of points to return.

      @returns ([mathutils.Vector]): The interpolated points
   '''

   return [mathutils.Vector]

def intersect_line_line(v1, v2, v3, v4):
   '''Returns a tuple with the points on each line respectively closest to the other.
      
      Arguments:
      @v1 (mathutils.Vector): First point of the first line
      @v2 (mathutils.Vector): Second point of the first line
      @v3 (mathutils.Vector): First point of the second line
      @v4 (mathutils.Vector): Second point of the second line

   '''

   return (mathutils.Vector, mathutils.Vector)

def intersect_line_line_2d(lineA_p1, lineA_p2, lineB_p1, lineB_p2):
   '''Takes 2 segments (defined by 4 vectors) and returns a vector for their point of intersection or None.
      .. warning:: Despite its name, this function works on segments, and not on lines.
      
      Arguments:
      @lineA_p1 (mathutils.Vector): First point of the first line
      @lineA_p2 (mathutils.Vector): Second point of the first line
      @lineB_p1 (mathutils.Vector): First point of the second line
      @lineB_p2 (mathutils.Vector): Second point of the second line

      @returns (mathutils.Vector): The point of intersection or None when not found
   '''

   return mathutils.Vector

def intersect_line_plane(line_a, line_b, plane_co, plane_no, no_flip=False):
   '''Calculate the intersection between a line (as 2 vectors) and a plane.
      Returns a vector for the intersection or None.
      
      Arguments:
      @line_a (mathutils.Vector): First point of the first line
      @line_b (mathutils.Vector): Second point of the first line
      @plane_co (mathutils.Vector): A point on the plane
      @plane_no (mathutils.Vector): The direction the plane is facing

      @returns (mathutils.Vector): The point of intersection or None when not found
   '''

   return mathutils.Vector

def intersect_line_sphere(line_a, line_b, sphere_co, sphere_radius, clip=True):
   '''Takes a line (as 2 points) and a sphere (as a point and a radius) and
      returns the intersection
      
      Arguments:
      @line_a (mathutils.Vector): First point of the line
      @line_b (mathutils.Vector): Second point of the line
      @sphere_co (mathutils.Vector): The center of the sphere
      @sphere_radius (sphere_radius): Radius of the sphere

      @returns (A tuple pair containing mathutils.Vector or None): The intersection points as a pair of vectors or None when there is no intersection
   '''

   return A tuple pair containing mathutils.Vector or None

def intersect_line_sphere_2d(line_a, line_b, sphere_co, sphere_radius, clip=True):
   '''Takes a line (as 2 points) and a sphere (as a point and a radius) and
      returns the intersection
      
      Arguments:
      @line_a (mathutils.Vector): First point of the line
      @line_b (mathutils.Vector): Second point of the line
      @sphere_co (mathutils.Vector): The center of the sphere
      @sphere_radius (sphere_radius): Radius of the sphere

      @returns (A tuple pair containing mathutils.Vector or None): The intersection points as a pair of vectors or None when there is no intersection
   '''

   return A tuple pair containing mathutils.Vector or None

def intersect_plane_plane(plane_a_co, plane_a_no, plane_b_co, plane_b_no):
   '''Return the intersection between two planes
      
      Arguments:
      @plane_a_co (mathutils.Vector): Point on the first plane
      @plane_a_no (mathutils.Vector): Normal of the first plane
      @plane_b_co (mathutils.Vector): Point on the second plane
      @plane_b_no (mathutils.Vector): Normal of the second plane

      @returns (tuple pair of mathutils.Vector or None if the intersection can't be calculated): The line of the intersection represented as a point and a vector
   '''

   return tuple pair of mathutils.Vector or None if the intersection can't be calculated

def intersect_point_line(pt, line_p1, line_p2):
   '''Takes a point and a line and returns a tuple with the closest point on the line and its distance from the first point of the line as a percentage of the length of the line.
      
      Arguments:
      @pt (mathutils.Vector): Point
      @line_p1 (mathutils.Vector): First point of the line

   '''

   return (mathutils.Vector, float)

def intersect_point_quad_2d(pt, quad_p1, quad_p2, quad_p3, quad_p4):
   '''Takes 5 vectors (using only the x and y coordinates): one is the point and the next 4 define the quad, 
      only the x and y are used from the vectors. Returns 1 if the point is within the quad, otherwise 0.
      Works only with convex quads without singular edges.
      
      Arguments:
      @pt (mathutils.Vector): Point
      @quad_p1 (mathutils.Vector): First point of the quad
      @quad_p2 (mathutils.Vector): Second point of the quad
      @quad_p3 (mathutils.Vector): Third point of the quad
      @quad_p4 (mathutils.Vector): Fourth point of the quad

   '''

   return int

def intersect_point_tri(pt, tri_p1, tri_p2, tri_p3):
   '''Takes 4 vectors: one is the point and the next 3 define the triangle.
      
      Arguments:
      @pt (mathutils.Vector): Point
      @tri_p1 (mathutils.Vector): First point of the triangle
      @tri_p2 (mathutils.Vector): Second point of the triangle
      @tri_p3 (mathutils.Vector): Third point of the triangle

      @returns (mathutils.Vector): Point on the triangles plane or None if its outside the triangle
   '''

   return mathutils.Vector

def intersect_point_tri_2d(pt, tri_p1, tri_p2, tri_p3):
   '''Takes 4 vectors (using only the x and y coordinates): one is the point and the next 3 define the triangle. Returns 1 if the point is within the triangle, otherwise 0.
      
      Arguments:
      @pt (mathutils.Vector): Point
      @tri_p1 (mathutils.Vector): First point of the triangle
      @tri_p2 (mathutils.Vector): Second point of the triangle
      @tri_p3 (mathutils.Vector): Third point of the triangle

   '''

   return int

def intersect_ray_tri(v1, v2, v3, ray, orig, clip=True):
   '''Returns the intersection between a ray and a triangle, if possible, returns None otherwise.
      
      Arguments:
      @v1 (mathutils.Vector): Point1
      @v2 (mathutils.Vector): Point2
      @v3 (mathutils.Vector): Point3
      @ray (mathutils.Vector): Direction of the projection
      @orig (mathutils.Vector): Origin
      @clip (boolean): When False, don't restrict the intersection to the area of the triangle, use the infinite plane defined by the triangle.

      @returns (mathutils.Vector): The point of intersection or None if no intersection is found
   '''

   return mathutils.Vector

def intersect_sphere_sphere_2d(p_a, radius_a, p_b, radius_b):
   '''Returns 2 points on between intersecting circles.
      
      Arguments:
      @p_a (mathutils.Vector): Center of the first circle
      @radius_a (float): Radius of the first circle
      @p_b (mathutils.Vector): Center of the second circle
      @radius_b (float): Radius of the second circle

   '''

   return tuple of mathutils.Vector's or None when there is no intersection

def normal(vectors):
   '''Returns the normal of a 3D polygon.
      
      Arguments:
      @vectors (sequence of 3 or more 3d vector): Vectors to calculate normals with

   '''

   return mathutils.Vector

def points_in_planes(planes):
   '''Returns a list of points inside all planes given and a list of index values for the planes used.
      
      Arguments:
      @planes (list of mathutils.Vector): List of planes (4D vectors).

      @returns (pair of lists): two lists, once containing the vertices inside the planes, another containing the plane indices used
   '''

   return pair of lists

def tessellate_polygon(veclist_list):
   '''Takes a list of polylines (each point a vector) and returns the point indices for a polyline filled with triangles.
      
      Arguments:
      @veclist_list: list of polylines

   '''

   return list

def volume_tetrahedron(v1, v2, v3, v4):
   '''Return the volume formed by a tetrahedron (points can be in any order).
      
      Arguments:
      @v1 (mathutils.Vector): Point1
      @v2 (mathutils.Vector): Point2
      @v3 (mathutils.Vector): Point3
      @v4 (mathutils.Vector): Point4

   '''

   return float

