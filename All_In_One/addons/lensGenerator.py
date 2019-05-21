## props in bpy.types.Object

bl_info = {
    "name": "Lens",
    "author": "Aaron Buchler",
    "version": (1, 0, 0),
    "blender": (2, 77, 0),
    "location": "View3D > Add > Mesh",
    "description": "Add an lens object with a configurable focal length",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

import bpy

from bpy.props import *
from mathutils import Vector

from math import pi, sin, cos, sqrt
tau = 2 * pi

def lens(res_a, res_b, diameter, thickness, ior, curvature, curvature_b, curvatureRatio):
    #convert
    diameter/= 1000
    thickness/= 1000
    curvature_a = curvature/ 1000
    curvature_b/= 1000
    radius = diameter/2
    
    try:
        R1 = curvature_a * (1/(-curvatureRatio+1))
    except ZeroDivisionError:
        R1 = 1000000
    try:
        R2 = curvature_a * (1/(curvatureRatio+1))
    except ZeroDivisionError:
        R2 = 1000000
    
    if (curvature_b != 0) and (curvatureRatio == 0):
        R1 = curvature_a
        R2 = -curvature_b

    #make lens mesh
    verts = []
    edges = [] #using calc_edges later
    faces = []
    
    side1_idx = 0
    side2_idx = 0
    
    for side in range(2): #make each side of lens with same code
        if side==0:
            v1 = Vector((0, thickness/2, 0))
        elif side==1:
            v1 = Vector((0, -thickness/2, 0))
        verts.append(v1)
        
        if side==0:
            c = R1
        elif side==1:
            c = R2
        
        if side==0:
            ringOfst = 1
        elif side==1:
            ringOfst = len(verts)
        
        for r in range(res_b):
            r = r + 1
            rd = (r /  res_b) * radius

            #calculate height from radius of curvature
            try:
                if c < 0:
                    h = -1 * (sqrt(c**2 - rd**2)) - c
                else:
                    h = sqrt(c**2 - rd**2) - c
            except ValueError: #if radius of curvature is smaller than diameter
                h = -c #set h to radius
            if ((r-0) == int((abs(c) / radius) * res_b)) and (abs(c) < radius): #snap vertex ring to edge of hemisphere
                h = -c #set h to radius
                rd = abs(c)
                

            h = h + thickness/2
            
            if side==1:
                h = -h

            for a in range(res_a):
                angle = (a / res_a) * tau
                x = sin(angle) * rd
                y = cos(angle) * rd

                v = Vector((x, h, y))
                verts.append(v)

                v1 = ringOfst-1
                if r == 1:
                    if a == (res_a-1):
                        c1 = v1
                        c2 = v1+a+1
                        c3 = v1+1
                    else:
                        c1 = v1
                        c2 = v1+a+1
                        c3 = v1+a+2
                    
                    if side==0:
                        faces.append((c1, c2, c3))
                    elif side==1:
                        faces.append((c1, c3, c2))
                else:
                    if a == (res_a-1):
                        c1 = ringOfst+a
                        c2 = ringOfst
                        c3 = ringOfst+res_a
                        c4 = ringOfst+res_a+a
                    else:
                        c1 = ringOfst+a
                        c2 = ringOfst+a+1
                        c3 = ringOfst+res_a+a+1
                        c4 = ringOfst+res_a+a
                    
                    if side==0:
                        faces.append((c1, c4, c3, c2))
                    elif side==1:
                        faces.append((c1, c2, c3, c4))

            ringOfst = len(verts)-res_a
        
        if side==0:
            side1_idx = len(verts)-res_a
        elif side==1:
            side2_idx = len(verts)-res_a

    #connect faces
    for i in range(res_a):
        if i == (res_a-1):
            c1 = side1_idx+i
            c2 = side2_idx+i
            c3 = side2_idx
            c4 = side1_idx
        else:
            c1 = side1_idx+i
            c2 = side2_idx+i
            c3 = side2_idx+i+1
            c4 = side1_idx+i+1
        faces.append((c1, c2, c3, c4))
        

    return verts, edges, faces

def makeMaterial(ior=1.52):
    # Create a new material
    material = bpy.data.materials.new(name="Lens Glass")
    material.use_nodes = True
    
    #remove default
    material.node_tree.nodes.remove(material.node_tree.nodes.get('Diffuse BSDF'))
    #add node
    material_output = material.node_tree.nodes.get('Material Output')
    shader = material.node_tree.nodes.new('ShaderNodeBsdfRefraction')
    shader.inputs['IOR'].default_value = ior
    material.node_tree.links.new(material_output.inputs[0], shader.outputs[0])
    
    return material

def initMesh(self, context):
    #make object
    lensMesh = bpy.data.meshes.new('lensmesh')
    lensObj = bpy.data.objects.new('Lens', lensMesh)
    bpy.context.scene.objects.link(lensObj)
    lensObj.location=bpy.context.scene.cursor_location
    
    #select
    bpy.ops.object.select_all(action='DESELECT')
    lensObj.select = True
    bpy.context.scene.objects.active = lensObj
    
    #set properties
    lensObj["is_lens"] = True
    
    #edge split modifier
    lensObj.modifiers.new('Edge Split', 'EDGE_SPLIT')
    
    return lensObj

def initUpdate(obj, args):
    verts, edges, faces = lens(*args)
    
    oldmesh = obj.data

    mesh = bpy.data.meshes.new(name='lensmesh')
    mesh.from_pydata(verts, edges, faces)
    mesh.update(calc_edges=True)
    
    #smooth
    for p in mesh.polygons:
        p.use_smooth = True
    
    obj.data = mesh
    obj.data.update()
    bpy.data.meshes.remove(oldmesh)
    
def updateMesh(self, context):
    print("update")
    obj = context.object
    
    try:
        isLens = obj["is_lens"]
    except KeyError:
        isLens = False
        
    if isLens:
        verts, edges, faces = lens(obj.res_a, obj.res_b, obj.diameter, obj.thickness, obj.ior, obj.curvature, obj.curvature_b, obj.curvatureRatio)

        oldmesh = obj.data
        
        has_mat = bool(obj.data.materials)
        if has_mat:
            origMat = obj.data.materials[0]

        mesh = bpy.data.meshes.new(name='lensmesh')
        mesh.from_pydata(verts, edges, faces)
        mesh.update(calc_edges=True)
        
        #smooth
        for p in mesh.polygons:
            p.use_smooth = True

        obj.data = mesh
        obj.data.update()
        bpy.data.meshes.remove(oldmesh)
        
        # assign or update existing material or add new one
        if has_mat:
            if obj.make_material:
                # set ior
                origMat.node_tree.nodes.get('Refraction BSDF').inputs['IOR'].default_value = obj.ior
            # re-assign material
            obj.data.materials.append(origMat)
        else:
            if obj.make_material:
                bpy.context.scene.render.engine = 'CYCLES'
                mat = makeMaterial(ior=obj.ior)
                obj.data.materials.append(mat)
    

#properties
bpy.types.Object.res_a = IntProperty(name="Circular Resoultion",
    description="Resoultion around",
    default=32,
    update=updateMesh)
bpy.types.Object.res_b = IntProperty(name="Radius Resoultion",
    description="Resoultion from center",
    default=16,
    update=updateMesh)
bpy.types.Object.diameter = FloatProperty(name="Diameter",
    description="diameter in millimeters",
    default=50,
    update=updateMesh)
bpy.types.Object.thickness = FloatProperty(name="Thickness",
    description="Thickness of lens in millimeters",
    default=15.0,
    update=updateMesh)
bpy.types.Object.ior = FloatProperty(name="Index of Refraction",
    description="Index of Refraction of the lens material",
    default=1.52,
    update=updateMesh)
bpy.types.Object.curvature = FloatProperty(name="Curvature",
    description="Radius of curvature in millimeters",
    default=50,
    update=updateMesh)
bpy.types.Object.curvature_b = FloatProperty(name="Curvature b",
    description="Radius of curvature for back face (ignored if 0 or Ratio is not 0",
    default=0,
    update=updateMesh)
bpy.types.Object.curvatureRatio = FloatProperty(name="Curvature Ratio",
    description="Balance of curvature between each face",
    default=0.0,
    update=updateMesh)
bpy.types.Object.make_material = BoolProperty(name="Make Cycles Material",
    description="set render to cycles and add refraction node",
    default=False,
    update=updateMesh)

def draw_focal_length(layout, context):
    obj = context.object
    
    thickness = obj.thickness
    ior = obj.ior
    curvature = obj.curvature
    curvature_b = obj.curvature_b
    curvatureRatio = obj.curvatureRatio
    
    thickness/= 1000
    curvature_a = curvature/ 1000
    curvature_b/= 1000
    
    try:
        R1 = curvature_a * (1/(-curvatureRatio+1))
    except ZeroDivisionError:
        R1 = 1000000
    try:
        R2 = curvature_a * (1/(curvatureRatio+1))
    except ZeroDivisionError:
        R2 = 1000000
    
    if (curvature_b != 0) and (curvatureRatio == 0):
        R1 = curvature_a
        R2 = -curvature_b
    
    # lensmaker's equation
    R2 = -R2
    ifl = (ior-1) * ((1/R1) - (1/R2) + (((ior-1)*thickness) / (ior * R1 + R2)))
    fl = 1 / ifl
    
    layout.label("Focal Length: " + str(round(fl * 1000, 3)) + " mm")

class Lens(bpy.types.Panel):
    bl_idname = "Lens"
    bl_label = "Lens"
    bl_space_type = "PROPERTIES" # change
    bl_region_type = "WINDOW" # change
    bl_context = "modifier" # change
    
    def draw(self, context):
        props = context.object
        layout = self.layout
        row = layout.row()
        row.prop(props, 'res_a')
        row.prop(props, 'res_b')
        layout.prop(props, 'diameter')
        layout.prop(props, 'thickness')
        layout.prop(props, 'ior')
        layout.prop(props, 'curvature')
        layout.prop(props, 'curvature_b')
        layout.prop(props, 'curvatureRatio')
        layout.prop(props, 'make_material')
        
        draw_focal_length(layout, context)

class LensAdd(bpy.types.Operator):
    bl_idname = "mesh.lens_add"
    bl_label = "Lens"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("ui draw")
        lobj = initMesh(self, context)
        initUpdate(lobj, [32, 16, 50, 15, 1.52, 50, 0, 0])
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(LensAdd.bl_idname, text="Add lens mesh",
                        icon='PLUGIN')

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(menu_func)

def unregister():
    bpy.types.INFO_MT_mesh_add.remove(menu_func)
    bpy.utils.unregister_module(__name__)
