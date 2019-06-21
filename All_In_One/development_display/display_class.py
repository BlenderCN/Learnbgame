import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix, Euler, Quaternion

from .view import draw_display_view
from .pixel import draw_display_px
from .plot import Plot

__all__ = ['Display']


class Display():
    """
This is intended to help developing scripts by making
it easyer to visualize things directly from scripts.
Look in the 3DView N-Panel for the display options.

usage:

dspl = bpy.types.WindowManager.display

Then in your script you can simply add stuff to visualize it.
For example:

vecs = list of points
dspl.add_points(vecs, 'list with my important points')

when done or starting a new loop do
dspl.clear() to clear all data
or dspl.points.clear() for the subdicts.
[points, edges, edge_chains, matrizies, eulers, quats, plots]

All objects are stored in a dictonary and can thus be overwritten
or reaccessed later. The key is also the display name in the viewport.

The functions for adding all have a k (for key) value for this.
If it is unset the next free integer in the dict keys is used instead.

Use dspl.set_transform(some_matrix) to transform all later added elements
by that matrix (to put them into object-local-space). Alternatively use
dspl.apply_transform(some_matrix, inv=False)
to transform all those already set.

Functions for adding stuff:
add_point(point, k='')
add_points(points) # has no key. Is convinience to add a list of vecs
add_edge(edge, k='') --> edge = [point, point]
add_point_chain(points, k='') --> points = [point, point, ...]
add_matrix(matrix, k='')
add_euler(euler, k='')
add_quat(quat, k='')
add_bm(bm, k='')    --> bm = BMesh
add_plotted_function(function, interval=[start, stop, step], k='')
add_plot(xvalues, yvalues, k='')

With add_plot you can visualize your own precomputed plots.

Plotting of simple functions:
The function takes the interval as input args and plots the
function output on y
(function, interval[start, stop, step]], plot(key/display)name)

Plot sinus:
dspl.add_plotted_function(function=sin, interval=[0, 6, 0.1], k='sinus-plot')
to overwrite the plot use same k value

other example:
dspl.add_plotted_function(lambda x: 1/(exp(x)),[-2 ,2, 0.1],0)
dspl.add_plotted_function(lambda x: np.sin(x),[-np.pi ,np.pi, 0.1], k=1)

"""
    draw_handle = []

    object_transform = Matrix()
    
    points = {}
    edges = {}
    point_chains = {}
    plots = {}
    matrizies = {}
    eulers = {}
    quats = {}
    bmeshs = {}

    display_view = draw_display_view
    display_px = draw_display_px

    def __init__(self):
        self.draw_start()

    def clear(self):
        """Clear all display data."""
        self.points.clear()
        self.edges.clear()
        self.point_chains.clear()
        self.plots.clear()
        self.matrizies.clear()
        self.eulers.clear()
        self.quats.clear()
        self.bmeshs.clear()
        
        self.tag_redraw_all_view3d()

    #SET "ADDING" TRANSFORM
    def set_transform(self, mat):
        """mat: Matrix to transform the input by.
        Only points, edges and pointchains"""
        if type(mat) == Matrix:
            self.object_transform = mat

    #APPLY TRANFORM ON EXISTING ELEMENTS
    def apply_transform(self, mat=None, inv=False):
        """Apply the transform (set in set_transform(matrix))
        to points, edges, point_chains.
        If mat is given apply that instead.
        inv: If True apply the invers"""
        if mat is None:
            mat = self.object_transform.copy()
        if inv:
            mat = mat.inverted()
        if self.points:
            for p in self.points.values():
                p[:] = mat * p
        if self.edges:
            for e in self.edges.values():
                e[:] = [mat * v for v in e]
        if self.point_chains:
            for chain in self.point_chains.values():
                chain[:] = [mat*v for v in chain]

    #ADD POINT
    def add_point(self, point, k=''):
        """point: vector like iterable
        k: key(name) for the point"""
        if not k and type(k) == str:
            k = next_int_key(self.points.keys())
        try: hash(k)
        except: k = str(k)
            
        point = Vector(point).to_3d()
        point = self.object_transform * point
        self.points[k] = point

        self.tag_redraw_all_view3d()

    #ADD POINTS
    def add_points(self, points):
        """Convinience add list of points"""
        for p in points:
            self.add_point(p)

    #ADD EDGE
    def add_edge(self, edge, k=''):
        """edge: iterable thing with two vector like things
        k: key(name) for the edge"""
        if not k and type(k) == str:
            k = next_int_key(self.edges.keys())
        try: hash(k)
        except: k = str(k)
        
        edge = [Vector(v).to_3d() for v in edge]
        edge =[self.object_transform * v for v in edge]
        if (edge[0] - edge[1]).length == 0:
            return
        self.edges[k] = edge

        self.tag_redraw_all_view3d()

    #ADD EDGES
    def add_edges(self, edges):
        """Convinience add list of edges"""
        for e in edges:
            self.add_edge(e)

    #ADD POINT CHAIN
    def add_point_chain(self, points, k=''):
        """points: list of vector like things
        k: key(name) for the point chain"""
        if not k and type(k) == str:
            k = next_int_key(self.point_chains.keys())
        try: hash(k)
        except: k = str(k)
        
        points = [Vector(v).to_3d() for v in points]
        points = [self.object_transform * v for v in points]
        self.point_chains[k] = points

        self.tag_redraw_all_view3d()

    #ADD MATRIX
    def add_matrix(self, mat, k=''):
        """mat: Matrix type
        k: key(name) for the matrix"""
        if not k and type(k) == str:
            k = next_int_key(self.matrizies.keys())
        try: hash(k)
        except: k = str(k)
        
        if type(mat) == Matrix:
            self.matrizies[k] = mat

        self.tag_redraw_all_view3d()

    #ADD EULER
    def add_euler(self, euler, k=''):
        """euler: Euler type
        k: key(name) for the Euler"""
        if not k and type(k) == str:
            k = next_int_key(self.eulers.keys())
        try: hash(k)
        except: k = str(k)
        
        if type(euler) == Euler:
            self.eulers[k] = euler

        self.tag_redraw_all_view3d()

    #ADD QUATERNION
    def add_quat(self, quat, k=''):
        """quat: Quaternion type
        k: key(name) for the Quaternion"""
        if not k and type(k) == str:
            k = next_int_key(self.quats.keys())
        try: hash(k)
        except: k = str(k)
        
        if type(quat) == Quaternion:
            self.quats[k] = quat

        self.tag_redraw_all_view3d()

    #ADD BMESH
    def add_bm(self, bm, k=''):
        """bm: BMesh type
        k: key(name) for the bmesh"""
        if not k and type(k) == str:
            k = next_int_key(self.quats.keys())
        try: hash(k)
        except: k = str(k)
        if not isinstance(bm, bmesh.types.BMesh):
            print('Not a bmesh type', str(bm))
            return
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        self.bmeshs[k] = bm

        self.tag_redraw_all_view3d()

    #ADD PLOTTED FUNCTION
    def add_plotted_function(self, function, interval=[0, 1, 0.1], k=''):
        """function: some function with a single float input/output
        interval: [start, stop, step] for the input to function
        k: key(name) for the plot"""
        if not k and type(k) == str:
            k = next_int_key(self.plots.keys())
        try: hash(k)
        except: k = str(k)
            
        xvalues = np.arange(*interval)
        yvalues = [function(x) for x in xvalues]
        pl = Plot(xvalues, yvalues, name=str(k))
        self.plots[k] = pl
        
        self.tag_redraw_all_view3d()

    #ADD PLOT
    def add_plot(self, xvalues, yvalues=None, k=''):
        """Add some precomputed values to a plot.
        If yvalues are None xvalues is used for y,
        x is then max(y))"""
        if not k and type(k) == str:
            k = next_int_key(self.plots.keys())
        try: hash(k)
        except: k = str(k)

        if yvalues is None:
            yvalues = xvalues
            if type(yvalues) == function: yvalues = yvalues()
            xvalues = np.arange(0, np.max(yvalues), np.max(yvalues)/len(yvalues))

        if not (all(np.isfinite(xvalues)) and all(np.isfinite(yvalues))):
            print('Not all finite numbers in plot. Aborting.')
            return

        pl = Plot(xvalues, yvalues, name=str(k))
        self.plots[k] = pl
        
        self.tag_redraw_all_view3d()

    ### INTERNAL FUNCTIONS
    def create_edge_list(self, points=[]):
        """Returns the edges combining the list of points"""
        points = [list(v) for v in points]
        points = [Vector(v).to_3d() for v in points]
        points = [self.object_transform * v for v in points]
        edge_list = list(zip(points[:-1], points[1:]))
        return edge_list

    @classmethod
    def tag_redraw_all_view3d(self):
        context = bpy.context
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            region.tag_redraw()

    def draw_start(self):
        SpaceView3D = bpy.types.SpaceView3D
        if self.draw_handle:
            return

        print('Starting Development Display Drawing')
        handle_pixel = SpaceView3D.draw_handler_add(self.display_px, (), 'WINDOW', 'POST_PIXEL')
        handle_view = SpaceView3D.draw_handler_add(self.display_view, (), 'WINDOW', 'POST_VIEW')
        self.draw_handle[:] = [handle_pixel, handle_view]

        self.tag_redraw_all_view3d()

    def draw_stop(self):
        SpaceView3D = bpy.types.SpaceView3D
        if not self.draw_handle:
            return

        print('Stopping Development Display Drawing')
        handle_pixel, handle_view = self.draw_handle
        SpaceView3D.draw_handler_remove(handle_pixel, 'WINDOW')
        SpaceView3D.draw_handler_remove(handle_view, 'WINDOW')
        self.draw_handle[:] = []

        self.tag_redraw_all_view3d()

    def __call__(self):
        if self.draw_handle:
            self.draw_stop()
        elif not self.draw_handle:
            self.draw_start()

    def __repr__(self):
        return 'Points: %d, Edges: %d, PointChains: %d,\nMatrizies: %d, Eulers: %d, Quaternions: %d,\nPlots: %d'%(
        len(self.points), len(self.edges), len(self.point_chains), len(self.matrizies),
        len(self.eulers), len(self.quats), len(self.plots))

### UTILS
def next_int_key(keys):
    nums = []
    for k in keys:
        try:
            num = int(k)
            nums.append(num)
        except:
            pass
    if nums:
        return sorted(nums)[-1] + 1
    return 0

