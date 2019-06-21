# Plugin for loading SWC format neuron structures into Blender

bl_info = {
    'name': 'Load SWC neuron',
    'author': 'Christopher M. Bruns',
    'version': (1, 0, 0),
    'blender': (2, 76, 0),
    'location': 'File > Import > SWC Neuron',
    'description': 'Import SWC Neuron Structures',
    'license': 'MIT',
    "category": "Learnbgame",
}

__author__ = bl_info['author']
__license__ = bl_info['license']
__version__ = ".".join([str(s) for s in bl_info['version']])


import os
import math

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
import numpy


class SwcNeuronImporter(bpy.types.Operator, ImportHelper):
    "Loads SWC format neuron structures"

    bl_label = 'Import SWC Neuron structures'
    bl_idname = 'import_mesh.swcneuron'
    filename_ext = '.swc'
    filter_glob = StringProperty(
            default="*.swc",
            options={'HIDDEN'})
    
    def _neuron_name(self):
        return os.path.splitext(os.path.basename(self.filepath))[0]
    
    def execute(self, context):
        "Load the SWC file the user already specified, and display the geometry in the current scene"
        self.load_swc_file(self.filepath)
        swc_name = self._neuron_name()
        # print (swc_name)
        # Create a top level container to hold the neuron representation(s)
        bpy.ops.object.empty_add()
        root = bpy.context.object
        root.name = swc_name
        root.location = (0,0,0)
        # Create a neuron skeleton mesh using only vertices and edges (ignoring vertex radii)
        skeleton = self.create_skeleton()
        skeleton.parent = root
        # Create a sphere at each neuron vertex
        spheres = self.create_node_spheres()
        spheres.parent = root
        # TODO: Create a cylinder at each pair of adjacent nodes with identical radii
        cylinders = self.create_edge_cylinders()
        cylinders.parent = root
        # TODO: Create a truncated cone at each edge
        # TODO: Cylinders for cases where adjacent radii are the same
        return {'FINISHED'}
        
    def load_swc_file(self, filename):
        self.nodes = dict()
        self.first_node = None
        self.index_from_id = dict()
        self.vertices = list()
        with open(self.filepath, 'r') as fh:
            node_count = 0
            for line in fh:
                if line.startswith('#'):
                    continue # skip comments
                fields = line.split() # split on all runs of whitespace, including tabs
                if len(fields) < 7:
                    continue # not enough fields
                id = int(fields[0])
                type_ = int(fields[1])
                xyz = [float(x) for x in fields[2:5]]
                radius = float(fields[5])
                parent_id = int(fields[6])
                self.nodes[id] = {
                        'id': id,
                        'type': type_, 
                        'xyz': numpy.array(xyz, 'f'), 
                        'radius': radius,
                        'parent_id': parent_id
                }
                if self.first_node is None:
                    self.first_node = self.nodes[id]
                self.vertices.append(xyz)
                self.index_from_id[id] = node_count
                node_count += 1
            print( "%s SWC nodes read" % node_count )
        self.edges = list()
        for id, data in self.nodes.items():
            if data['parent_id'] not in self.index_from_id:
                continue # no parent
            v1 = self.index_from_id[id]
            v2 = self.index_from_id[data['parent_id']]
            self.edges.append( (v1, v2) )
        return self.nodes
    
    def create_edge_cylinders(self):
        # Create top level empty container for edge cylinders
        bpy.ops.object.empty_add()
        cylinders = bpy.context.object
        cylinders.name = 'Cylinders_' + self._neuron_name()
        # Create single prototype for edge cylinders
        material = bpy.data.materials.new('Mat_cylinders_' + self._neuron_name())
        bpy.ops.surface.primitive_nurbs_surface_cylinder_add(
                    view_align=False, enter_editmode=False,
                    location=(0,0,0), rotation=(0.0, 0.0, 0.0),
                    radius=1.0)
        cylinder = bpy.context.scene.objects.active
        cylinder_data = cylinder.data
        bpy.context.scene.objects.unlink(cylinder)
        # 
        edge_count = 0
        cylinder_count = 0
        cone_count = 0
        for id, data in self.nodes.items():
            parent_id = data['parent_id']
            if parent_id not in self.nodes:
                continue # we need two nodes to make an edge...
            parent = self.nodes[parent_id]
            edge_count += 1
            r1 = data['radius']
            r2 = parent['radius']
            r = min(r1, r2)
            dr = r2 - r1
            dxyz = parent['xyz'] - data['xyz']
            # Rotation
            dx, dy, dz = dxyz
            phi = math.atan2(pow(dx*dx + dy*dy, 0.5), dz)
            theta = math.atan2(dy, dx)
            xyz = 0.5 * (data['xyz'] + parent['xyz'])
            d = numpy.linalg.norm(dxyz)
            if abs(dr)/r <= 0.001: # cylinder
                # center on center of mass of two spheres
                cylinder_count += 1
                cylinder = bpy.data.objects.new('cylinder_%s'%cylinder_count, cylinder_data)
                cylinder.location = xyz
                cylinder.scale = [r,r,0.5*d]
                cylinder.rotation_euler = (0, phi, theta)
                cylinder.active_material = material
                cylinder.parent = cylinders
                bpy.context.scene.objects.link(cylinder)
            else: # Cone
                # TODO:
                sinangle = -dr / d
                cosangle = pow(1.0 - sinangle*sinangle, 0.5)
                # print("cosangle = %s" % str(cosangle))
                # print("sinangle = %s" % str(sinangle))
                # Compute locations of cone ends
                axisdir = dxyz / d
                # one = numpy.linalg.norm(axisdir)
                # print("one = %d" % one)
                p1 = data['xyz'] + sinangle * r1 * axisdir
                p2 = parent['xyz'] + sinangle * r2 * axisdir
                center = (p1 + p2)/2.0
                # 
                cr1 = r1 * cosangle
                cr2 = r2 * cosangle
                # print('r1 = %f, r2 = %f, xyz1 = %s, xyz2 = %s' % (r1, r2, data['xyz'], parent['xyz']))
                # print('cr1 = %f, cr2 = %f, center = %s' % (cr1, cr2, center))
                # print('p1 = %s, p2 = %s' % (p1, p2))
                bpy.ops.mesh.primitive_cone_add(
                    radius1=cr1,
                    radius2=cr2,
                    depth=numpy.linalg.norm(p2-p1),
                    end_fill_type='NOTHING',
                    enter_editmode=True)
                cone = bpy.context.object
                cone.name = 'Truncated_Cone_%s' % cone_count
                bpy.ops.mesh.faces_shade_smooth()
                cone.location = center
                cone.rotation_euler = (0, phi, theta)
                cone.active_material = material
                cone.parent = cylinders
                cone_count += 1
                bpy.ops.object.mode_set(mode = 'OBJECT')
        print("%s edges found; %s cylinders created; %s cones created" % (edge_count, cylinder_count, cone_count))
        cylinders.location = (0,0,0)
        return cylinders
    
    def create_node_spheres(self):
        "Place one sphere at each vertex of the neuron structure"
        # Create a single shared material for the neuron
        material = bpy.data.materials.new('Mat_spheres_' + self._neuron_name())
        swc_mesh = bpy.data.meshes.new('Mesh_spheres_' + self._neuron_name())
        # Create a face of the appropriate size at each node, so we can use dupli-faces
        verts = []
        faces = []
        for id, data in self.nodes.items():
            i = len(verts)
            x,y,z = data['xyz']
            r = 0.5 * data['radius']
            # Four corners of square face
            verts.append([x-r, y-r, z])
            verts.append([x-r, y+r, z])
            verts.append([x+r, y+r, z])
            verts.append([x+r, y-r, z])
            faces.append([i, i+1, i+2, i+3])
        swc_mesh.from_pydata(verts, [], faces)
        swc_mesh.update()
        swc_obj = bpy.data.objects.new('Spheres_' + self._neuron_name(), swc_mesh)
        bpy.context.scene.objects.link(swc_obj)
        # One nurbs sphere as a prototype
        bpy.ops.surface.primitive_nurbs_surface_sphere_add(
                    view_align=False, enter_editmode=False,
                    location=(0,0,0), rotation=(0.0, 0.0, 0.0),
                    radius=1.0)
        ball = bpy.context.scene.objects.active
        ball.active_material = material
        ball.parent = swc_obj
        # bpy.context.scene.objects.unlink(ball)
        swc_obj.dupli_type = 'FACES'
        swc_obj.use_dupli_faces_scale = True
        return swc_obj
    
    def create_skeleton(self):
        "Skeletal model of neuron, using only mesh vertices and edges"
        if len(self.nodes) <= 0:
            return
        # skeleton made of line segments
        skeleton_name = 'Skeleton_' + self._neuron_name()
        mesh = bpy.data.meshes.new(skeleton_name + ' mesh')
        mesh.from_pydata(self.vertices, self.edges, [])
        mesh.update()
        skeleton = bpy.data.objects.new(skeleton_name, mesh)
        bpy.context.scene.objects.link(skeleton)
        return skeleton


def register():
    bpy.utils.register_class(SwcNeuronImporter)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(SwcNeuronImporter)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

def menu_func_import(self, context):
    self.layout.operator(SwcNeuronImporter.bl_idname, text="SWC Neuron (.swc)")

if __name__ == "__main__":
    register()
