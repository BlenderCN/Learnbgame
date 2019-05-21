# Author: Gurten






bl_info = {
    "name": "Halo Online Tag Tool phmotest json exporter",
    "author": "Gurten",
    "version": ( 1, 0, 4 ),
    "blender": ( 2, 6, 3 ),
    "location": "File > Export > Halo Online Tag Tool phmotest json exporter (.json)",
    "description": "Halo Online Tag Tool phmotest json exporter (.json)",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

import bpy, json
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty
from mathutils import Vector

dp_epsilon = 6 #decimal point epsilon to distinguish vertices from each other
#regular epsilon for equalities
epsilon = 0.0001

#The minimum magnitude for a vector. Any smaller is considered useless.
min_mag = 0.01

#The smallest area for a triangle used to define a plane
min_area = 0.005

def getAABB(points):
    mins = [1e9, 1e9, 1e9]; maxs = [-1e9, -1e9, -1e9]
    for v in points:
        if v.x > maxs[0]:
            maxs[0] = v.x
        if v.x < mins[0]:
            mins[0] = v.x
        if v.y > maxs[1]:
            maxs[1] = v.y
        if v.y < mins[1]:
            mins[1] = v.y
        if v.z > maxs[2]:
            maxs[2] = v.z
        if v.z < mins[2]:
            mins[2] = v.z
    return mins, maxs

#returns a correct plane definition.
def faceToPlane(p):
    vec1 = p[0]- p[1]
    vec2 = p[2]- p[1]
    vec1.normalize()
    vec2.normalize()
    norm = vec1.cross(vec2)
    norm.normalize()
    dist = (norm * p[0])
    return ([-norm[0], -norm[1], -norm[2], -dist]) 

def keyForCoords(v, dp):
    return tuple([round(c, dp) for c in v]) #numbers around 0 cause problems due to sign

def areaOfTris(p):
    vec1 = p[0]- p[1]
    vec2 = p[2]- p[1]
    vec1.normalize()
    vec2.normalize()
    return 0.5 * (vec1.cross(vec2)).magnitude

def serialisePolyhedron(obj):
    local_verts = [obj.matrix_world * v.co for v in obj.data.vertices]
    verts = {}
    for v in local_verts:
        key = keyForCoords(v, dp_epsilon)
        verts[key] = v
    planes = {}
    #this really should only be for triangles
    for p in obj.data.polygons:
        triples = []
        points = [local_verts[obj.data.loops[idx].vertex_index] for idx in p.loop_indices] 
        for i in range(len(points)-2):
            triples.append((points[0], points[i+1], points[i+2]))
        for trip in triples:
            if areaOfTris(trip) < min_area:
                continue
            plane = faceToPlane(trip)
            key = keyForCoords(plane, 3)
            planes[key] = plane
    
    hs_planes = {} # half-space planes are the planes we want to use to define the polyhedra
    for key,val in planes.items():
        side_counts = [0,0,0]
        dist = val[3]; norm = Vector((val[0], val[1], val[2]))
        for v in verts.values():
            mag = (norm * v) - dist
            side = 1 + (mag > epsilon) - (mag < -epsilon)
            side_counts[side] += 1
        # There are vertices to one side of the plane. keep it.
        if not (side_counts[0] > 0 and side_counts[2] > 0):
            hs_planes[key] = val
    
    # Check each vertex lies on 3 planes or more. 
    # Cone-like shapes can have much more planes for the point.
    extreme_pts = []
    for v in verts.values():
        nplanes = 0
        for p in hs_planes.values():
            norm = Vector((p[0], p[1], p[2]))
            mag = (v * norm)- p[3]
            if -epsilon < mag and epsilon > mag:
                nplanes += 1
        if nplanes >= 3:
            extreme_pts.append(v)
    
    # The object may not have enough extreme points to make a convex hull 
    if len(extreme_pts) < 4:
        raise Exception ("Object: \'%s\' did not have enough extreme points to create a 3D hull." % (obj.name))
    
    # Find a centroid for the polyhedra to determine which
    # way the planes should be facing to be an outward boundary
    # of the convex polyhedron.
    
    centroid = Vector((0,0,0))
    for pt in extreme_pts:
        centroid += pt
    centroid /= (len(extreme_pts))
    for p in hs_planes.values():
        norm = Vector((p[0], p[1], p[2])); dist = p[3]
        mag = (centroid * norm) - dist
        # The plane should be 'in front' of the centroid,
        # i.e the plane should be further away than the center
        # of the convex polyhedron.
        if mag > 0:
            for i in range(len(p)):
                p[i] = -p[i] # flip the plane
    
    # The following is to calculate AABB center and extents.
    # Without axis-aligned center and extents, the engine
    # will not attempt to do any further checks against the
    # geometry inside. 
    
    # Two 3D points to represent an AABB
    mins, maxs = getAABB(verts.values())
    
    # The engine prefers an encoding for AABB with a center-point
    # and half-extents 
    center = [(maxs[i] + mins[i])/2.0 for i in range(3)]
    half_extents = [abs(maxs[i] - center[i]) for i in range(3)]
    
    # A python dict is almost 1-1 with the JSON format.
    return {"Type" : "Polyhedron",
            
            # Flip the 'dist' of the plane. Unusual, but needed for the engine.
            
            "Data" : {"Planes" : [[p[0], p[1], p[2], -p[3]] for p in list(hs_planes.values())], 
            
            # Write the vertices.
            
            "Vertices" : [[c for c in vecs] for vecs in extreme_pts], 
            
            # The center-point of the AABB
            
            "Center" : center,
            
            # The half-extents of the bounding box. 
            
            "Extents" : half_extents,
            
            # A garbage value for 'Mass' 
            
            "Mass" : 100,
            
            # A moderately standard value for 'Friction' according to other tags
            
            "Friction" : 0.85,
            
            # A garbage value for 'Mass'  
            
            "Restitution" : 0.3} }

class ExportJson(bpy.types.Operator, ExportHelper):
    bl_idname = "export.json"
    bl_label = "Export"
    __doc__ = "Halo Online Tag Tool phmotest json exporter (.json)"
    filename_ext = ".json"
    filter_glob = StringProperty( default = "*.json", options = {'HIDDEN'} )
    
    filepath = StringProperty( 
        name = "File Path",
        description = "File path used for exporting the JSON file",
        maxlen = 1024,
        default = "" )
            
    option_selection_only = BoolProperty(
        name = "Selection Only",
        description = "Exports selected mesh objects only",
        default = True )
    
    def draw( self, context ):
        layout = self.layout
        box = layout.box()
        box.prop( self, 'option_selection_only' )

    def execute(self, context):
        n_objs_exported = 0
        if self.option_selection_only:
            objs = [o for o in context.selected_objects]
        else:
            objs = [o for o in context.selectable_objects]
        
        objs = list(filter(lambda x: x.type == "MESH", objs))
        if len(objs) == 0:
            raise Exception("No meshes to export.")
        
        output = []
        for obj in objs:
            output.append(serialisePolyhedron(obj))
        
        f = open(self.filepath, "w")
        f.write(json.dumps(output))
        f.close()
        print("wrote json to \'%s\'." % self.filepath)
        return {'FINISHED'}
        
        

# Blender register plugin 
def register():
    bpy.utils.register_class(ExportJson)

def menu_func( self, context ):
    self.layout.operator( ExportJson.bl_idname, text = "Halo Online Tag Tool phmotest json exporter (.json)" )

def register():
    bpy.utils.register_class( ExportJson )
    bpy.types.INFO_MT_file_export.append( menu_func )

def unregister():
    bpy.utils.unregister_class( ExportJson )
    bpy.types.INFO_MT_file_export.remove( menu_func )

if __name__ == "__main__":
    register()