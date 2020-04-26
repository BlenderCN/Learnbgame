import bpy
from bpy_extras.io_utils import ExportHelper
import bmesh
import mathutils
import colorsys

import numpy as np
import os
import re
import random
import sys

from . import msh

class bake_operator(bpy.types.Operator):
    """One click texture baking"""
    bl_idname = "mesh.bake"
    bl_label  = "Bakes a HR mesh (AO, textures and normals) to a LR one"

    imgRes  = bpy.props.IntProperty(name="texture resolution", description="target resolution", default=1024, min=128, max=8192)
    bakeTEX = bpy.props.BoolProperty(name="bakeTEX", description="bake the texture", default=True)
    bakeNOR = bpy.props.BoolProperty(name="bakeNOR", description="bake the normals", default=True)
    bakeAO  = bpy.props.BoolProperty(name="bakeAO",  description="bake the ambient occlusion", default=False)
    bakeVC  = bpy.props.BoolProperty(name="bakeVC",  description="bake the vertex colors", default=False)
    bakeSHD = bpy.props.BoolProperty(name="bakeSHD", description="bake shadows", default=False)
    saveIm  = bpy.props.BoolProperty(name="saveIm",  description="save the images", default=False)

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and len(context.selected_objects)==2
            and context.mode=="OBJECT"
        )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        #Identify the different objects
        sourceObject,targetObject = None, None
        sourceVerts, targetVerts = None, None
        for obj in context.selected_objects:
            if context.active_object == obj:
                targetObject = obj
            else:
                sourceObject = obj
        #Prepare the target object
        if not targetObject.data.uv_layers:
            bpy.ops.uv.smart_project()
        for i in range(len(targetObject.material_slots)):
            bpy.ops.object.material_slot_remove({'object': targetObject})
        #Add an empty material
        mat = bpy.data.materials.new('default')
        targetObject.data.materials.append(mat)

        #For blender render:
        render = bpy.context.scene.render.engine
        names = ['TEXTURE', 'NORMALS', 'AO', 'VERTEX_COLORS', 'SHADOWS']
        bake  = [self.bakeTEX, self.bakeNOR, self.bakeAO, self.bakeVC, self.bakeSHD]
        if render == "CYCLES":
            names = ['DIFFUSE', 'NORMAL', 'AO', 'VERTEX_COLORS', 'SHADOWS']
            bake  = [self.bakeTEX, self.bakeNOR, self.bakeAO, self.bakeVC, self.bakeSHD]

        for i,n in enumerate(names):
            if bake[i]:
                tex = bpy.data.textures.new( 'texture_'+n, type = 'IMAGE')
                img = bpy.data.images.new("image_"+n, width=self.imgRes, height=self.imgRes)
                img.file_format='PNG'
                tex.image = img

                if render == "BLENDER_RENDER":
                    mtex = mat.texture_slots.add()
                    mtex.texture = tex
                    mtex.texture_coords = 'UV'

                if render == "BLENDER_RENDER":
                    bpy.context.scene.render.use_bake_selected_to_active = True

                bpy.ops.object.editmode_toggle()
                bpy.data.screens['UV Editing'].areas[1].spaces[0].image = img

                if render == "BLENDER_RENDER":
                    bpy.context.object.active_material.use_textures[i] = False
                if render == "CYCLES":
                    mat.use_nodes = True
                    node = mat.node_tree.nodes.new("ShaderNodeTexImage")
                    node.select = True
                    mat.node_tree.nodes.active = node
                    node.image = img

                #bpy.context.space_data.context = 'RENDER'
                if render == "BLENDER_RENDER":
                    bpy.context.scene.render.bake_type = n
                elif render == "CYCLES":
                    bpy.context.scene.cycles.bake_type = n

                if n == "AO":
                    bpy.context.scene.render.use_bake_normalize = True

                if render == "CYCLES":
                    bpy.ops.object.bake(type=n, pass_filter=set({'COLOR'}), filepath="", margin=32, use_selected_to_active=True, save_mode='INTERNAL')
                else:
                    bpy.ops.object.bake_image()

                img.filepath_raw = "bake_"+n+".png"
                if self.saveIm:
                    img.save()

                bpy.ops.object.editmode_toggle()


        return {'FINISHED'}

    def draw(self, context):
        self.layout.prop(self, "imgRes", text="target resolution")
        self.layout.prop(self, "bakeTEX", text="bake color")
        self.layout.prop(self, "bakeAO", text="bake ambient occlusion")
        self.layout.prop(self, "bakeNOR", text="bake normals")
        self.layout.prop(self, "bakeVC", text="bake vertex colors")
        self.layout.prop(self, "bakeSHD", text="bake shadows")
        self.layout.prop(self, "saveIm", text="save images")
        col = self.layout.column(align=True)
class cork_operator(bpy.types.Operator):
    """Applies existing boolean with the cork suite"""
    bl_idname = "mesh.cork"
    bl_label  = "Cork boolean operations"

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and len(context.selected_objects)==1
            and context.mode=="OBJECT"
        )

    def execute(self, context):
        OBJ = bpy.context.scene.objects.active
        basis_file = "bool_" + OBJ.name + ".off"

        objects = []
        operations = []
        commands = []

        #Export the basis mesh
        #Get boolean information
        for m in OBJ.modifiers:
            if m.type == 'BOOLEAN':
                m.show_viewport = False
        bpy.ops.object.modifier_add(type="TRIANGULATE")
        m = OBJ.modifiers[-1]
        m.quad_method = 'BEAUTY'
        m.ngon_method = 'BEAUTY'
        bpy.ops.export_mesh.off(filepath=basis_file)
        bpy.ops.object.modifier_remove(modifier=m.name)

        #Get boolean information
        for m in OBJ.modifiers:
            if m.type == 'BOOLEAN':

                bool_file = "bool_" + m.object.name + ".off"
                m.show_viewport = True

                OPE = None
                if m.operation == "INTERSECT":
                    OPE = " -isct "
                if m.operation == "UNION":
                    OPE = " -union "
                if m.operation == "DIFFERENCE":
                    OPE = " -diff "
                commands.append("cork" + OPE + basis_file + " " + bool_file + " " + basis_file)
                commands.append("echo 'Finished " + m.operation + " with " + m.object.name + "'")

                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.scene.objects.active = m.object
                m.object.select = True

                m.object.hide=False
                bpy.ops.object.modifier_add(type="TRIANGULATE")
                tri = bpy.context.scene.objects.active.modifiers[-1]
                tri.quad_method = 'BEAUTY'
                tri.ngon_method = 'BEAUTY'
                bpy.ops.export_mesh.off(filepath=bool_file)
                bpy.ops.object.modifier_remove(modifier=tri.name)
                m.object.hide = True


        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = OBJ

        with open("bool_script.sh", "w") as f:
            for c in commands:
                f.write(c + "\n")

        print("The cork files should be available in the current directory\nlaunch sh bool_script.sh to obtain the final .off file")

        return {'FINISHED'}
class domain_operator(bpy.types.Operator):
    """Creates a computation domain"""
    bl_idname = "mesh.adddomain"
    bl_label  = "Adds a computation domain to the object"

    flowAxis = bpy.props.EnumProperty(items=[ ("xp","xp","minus X to plus X"),  ("xm","xm","plus X to minus X"), ("yp","yp","minus Y to plus Y"), ("ym","ym","plus Y to minus Y"), ("zp","zp","minus Z to plus Z"), ("zm","zm","plus Z to minus Z") ],
    name="flowAxis", description="Axis of the flow for a fluid simulation (side boundaries)", default="yp")
    scaleX = bpy.props.FloatProperty(name="scaleX", description="scale X", default=1.2, min=1.1, max=10)
    scaleY = bpy.props.FloatProperty(name="scaleY", description="scale X", default=2, min=1.1, max=10)
    scaleZ = bpy.props.FloatProperty(name="scaleZ", description="scale X", default=1.2, min=1.1, max=10)
    differentBottom = bpy.props.BoolProperty(name="differentBottom", description="Use a different reference for the bottom boundary", default=False)
    merge = bpy.props.BoolProperty(name="merge", description="Merge with the original object", default=False)

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and len(context.selected_objects)==1
            and context.mode=="OBJECT"
        )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        #Get bounding box info
        active = bpy.context.scene.objects.active
        loca = active.location
        dims = active.dimensions
        bbox = active.bound_box
        matr = active.matrix_world
        corners = [matr*mathutils.Vector(x) for x in bbox]
        min = np.min(corners, axis=0)
        max = np.max(corners, axis=0)
        mean = (max + min)/2.

        #Add a cube around the mesh
        bpy.ops.mesh.primitive_cube_add(location=mean)
        domain = bpy.context.scene.objects.active
        domain.dimensions = max-min
        domain.scale[0] = domain.scale[0]*self.scaleX
        domain.scale[1] = domain.scale[1]*self.scaleY
        domain.scale[2] = domain.scale[2]*self.scaleZ

        #Prepare the references materials
        names = ["inlet", "outlet", "boundaries"]
        colors = [(0,1,0), (1,0,0), (0,0,1)]
        refs = []
        if self.flowAxis == "xp":
            refs = [ [0], [2], [1,3,5] ]
        if self.flowAxis == "xm":
            refs = [ [2], [0], [1,3,5] ]
        if self.flowAxis == "yp":
            refs = [ [3], [1], [0,2,5] ]
        if self.flowAxis == "ym":
            refs = [ [1], [3], [0,2,5] ]
        if self.flowAxis == "zp":
            refs = [ [4], [5], [0,1,2,3] ]
        if self.flowAxis == "zm":
            refs = [ [5], [4], [0,1,2,3] ]
        if self.differentBottom and self.flowAxis!=4 and self.flowAxis!=5:
            names.append("bottom")
            colors.append( (1,1,0) )
            refs.append([4])
        if not self.differentBottom:
            refs[-1].append(4)

        #Get the mesh info and into edit mode
        bpy.ops.object.editmode_toggle()
        mesh = bmesh.from_edit_mesh(domain.data)
        for i,r in enumerate(refs):
            #Create a new material
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.context.object.active_material_index = i
            mat = bpy.data.materials.new(name=names[i])
            domain.data.materials.append(mat)
            mat.diffuse_color = colors[i]
            for j,f in enumerate(mesh.faces):
                if j in r:
                    f.select = True
            bpy.ops.object.material_slot_assign()
        bpy.ops.object.editmode_toggle()

        #Subdivide the cube
        bpy.ops.object.modifier_add(type='SUBSURF')
        domain.modifiers["Subsurf"].subdivision_type = 'SIMPLE'
        domain.modifiers["Subsurf"].levels = 3
        domain.modifiers["Subsurf"].render_levels = 3
        bpy.ops.object.modifier_apply(modifier="Subsurf")

        if self.merge:
            #Join with the mesh
            active.select = True
            domain.select = True
            bpy.context.scene.objects.active = active
            for mod in active.modifiers:
                bpy.ops.object.modifier_apply(modifier = mod.name)
            nbMat = len(active.data.materials)
            bpy.ops.object.join()

        #Print the default.nstokes file
        nstokes = ""
        materials = bpy.context.scene.objects.active.data.materials
        dirichlet, slip = [],[]
        for i,m in enumerate(materials):
            #Inlet material = Dirichlet with non null speed
            if "inlet" in m.name:
                if self.flowAxis == "xp":
                    speed = "1. 0. 0."
                if self.flowAxis == "xm":
                    speed = "-1. 0. 0."
                if self.flowAxis == "yp":
                    speed = "0. 1. 0."
                if self.flowAxis == "ym":
                    speed = "0. -1. 0."
                if self.flowAxis == "zp":
                    speed = "0. 0. 1."
                if self.flowAxis == "zm":
                    speed = "0. 0. -1."
                dirichlet.append([i+1, speed])
            #Outlet material = pass
            elif "outlet" in m.name:
                pass
            #Boundary materials = slip condition
            elif "bounaries" in m.name:
                dirichlet.append([i+1, "0. 0. 0."])
            #Bottom = dirichlet with null value
            elif "bottom" in m.name:
                dirichlet.append([i+1, "0. 0. 0."])
            #Original object = dirichlet with null value
            else:
                dirichlet.append([i+1, "0. 0. 0."])

        #Writing the file
        if len(dirichlet):
            nstokes += "Dirichlet\n"+str(len(dirichlet))+"\n"
            for d in dirichlet:
                nstokes += str(d[0]) + " triangle v " + d[1] + "\n"
            nstokes+="\n"
        if len(slip):
            nstokes += "Slip\n"+str(len(slip))+"\n"
            for s in slip:
                nstokes += str(s[0]) + " triangle v " + s[1] + "\n"
            nstokes+="\n"
        nstokes+="Gravity\n0. 0. -0.1\n\n"
        nstokes+="Domain\n1\n1 1. 1."
        print(nstokes)

        return {'FINISHED'}

    def draw(self, context):
        self.layout.prop(self, "flowAxis", text="Main axis of th fluid flow")
        self.layout.prop(self, "scaleX", text="X scale for the domain")
        self.layout.prop(self, "scaleY", text="Y scale for the domain")
        self.layout.prop(self, "scaleZ", text="Z scale for the domain")
        self.layout.prop(self, "merge", text="Merge the object and the domain")
        self.layout.prop(self, "differentBottom", text="Different ref for the bottom")
        col = self.layout.column(align=True)
class export_mesh_operator(bpy.types.Operator, ExportHelper):
    """Export a Mesh file"""
    bl_idname = "export_mesh.mesh"
    bl_label  = "Export .mesh"

    filter_glob = bpy.props.StringProperty(
        default="*.mesh",
        options={'HIDDEN'},
    )
    check_extension = True
    filename_ext = ".mesh"
    refAtVerts = bpy.props.BoolProperty(name="refAtVerts", description="reference at vertices", default=False)
    triangulate = bpy.props.BoolProperty(name="triangulate", description="triangulate the mesh", default=True)
    miniSol = bpy.props.FloatProperty(name="miniSol", description="Minimum value for the scalar field", default=0, subtype="FACTOR")
    maxiSol = bpy.props.FloatProperty(name="maxiSol", description="Maximum value for the scalar field", default=1, subtype="FACTOR")

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and len(context.selected_objects)==1
            and context.mode=="OBJECT"
        )

    def execute(self, context):
        keywords = self.as_keywords(ignore=('filter_glob','check_existing'))
        err = export(self, context, **keywords)
        if err:
            return {'CANCELLED'}
        else:
            return {'FINISHED'}
def export(operator, context, filepath, refAtVerts, triangulate, miniSol, maxiSol):
    #Get the selected object
    APPLY_MODIFIERS = True
    scene = context.scene
    bpy.ops.object.duplicate()
    obj = scene.objects.active

    #Convert the big n-gons in triangles if necessary
    bpy.context.tool_settings.mesh_select_mode=(False,False,True)
    bpy.ops.object.convert(target='MESH')

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER')
    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
    if triangulate:
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_face_by_sides(number=3, type='GREATER')
        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
    bpy.ops.object.editmode_toggle()

    mesh = obj.to_mesh(scene, APPLY_MODIFIERS, 'PREVIEW')
    mesh.transform(obj.matrix_world)

    #Get the info
    verts = [[v.co[0], v.co[1], v.co[2], 0] for v in mesh.vertices[:]]
    triangles = [ [v for v in f.vertices] + [f.material_index + 1] for f in mesh.polygons if len(f.vertices) == 3 ]
    quads = [ [v for v in f.vertices] + [f.material_index + 1]  for f in mesh.polygons if len(f.vertices) == 4 ]

    if refAtVerts:
        for i in range(len(obj.data.materials[:])):
            for f in mesh.polygons:
                if f.material_index == i:
                    for v in f.vertices:
                        verts[v][3] = f.material_index + 1

    exportMesh = msh.Mesh()
    exportMesh.verts = msh.np.array(verts)
    exportMesh.tris  = msh.np.array(triangles)
    exportMesh.quads = msh.np.array(quads)
    exportMesh.write(filepath)

    #Solutions according to the weight paint mode (0 to 1 by default)
    vgrp = bpy.context.active_object.vertex_groups.keys()
    if(len(vgrp)>0):
        GROUP = bpy.context.active_object.vertex_groups.active
        cols = [0.0] * len(verts)
        for i,t in enumerate(mesh.polygons):
            for j,v in enumerate(t.vertices):
                try:
                    cols[v] = float(GROUP.weight(v))
                except:
                    continue
        try:
            mini = bpy.context.scene["mmgsMini"]
            maxi = bpy.context.scene["mmgsMaxi"]
            exportMesh.scalars = msh.np.array(cols)*(maxi - mini) + mini
            print("Min and max vallues taken from the scene property")
        except:
            exportMesh.scalars = msh.np.array(cols)*(maxiSol - miniSol) + miniSol
            print("Min and max vallues taken from the operator property")
        exportMesh.writeSol(filepath[:-5] + ".sol")

    bpy.ops.object.delete()
    bpy.data.meshes.remove(mesh)
    del exportMesh

    return {'FINISHED'}
class import_mesh_operator(bpy.types.Operator, ExportHelper):
    """Import a Mesh file"""
    bl_idname = "import_mesh.mesh"
    bl_label  = "Import .mesh"

    filter_glob = bpy.props.StringProperty(
        default="*.mesh",
        options={'HIDDEN'},
    )
    check_extension = True
    filename_ext = ".mesh"
    @classmethod
    def poll(cls, context):
        return (
            context.mode=="OBJECT"
        )
    def execute(self, context):
        keywords = self.as_keywords(ignore=('filter_glob','check_existing'))
        err = meshImport(self, context, **keywords)
        if err:
            return {'CANCELLED'}
        else:
            return {'FINISHED'}
def meshImport(operator, context, filepath):
    MESH = msh.Mesh(filepath)
    MESH.readSol()
    MESH.tets = msh.np.array([])
    MESH.discardUnused()

    meshes = []
    rTris = MESH.tris[:,-1].tolist() if len(MESH.tris)>0 else []
    rQuads = MESH.quads[:,-1].tolist() if len(MESH.quads)>0 else []
    tris = [t.tolist() for t in MESH.tris]
    quads = [q.tolist() for q in MESH.quads]
    verts = [v.tolist()[:-1] for v in MESH.verts]
    REFS = set(rTris + rQuads)

    for i,r in enumerate(REFS):
        refFaces = [t[:-1] for t in tris + quads if t[-1]==r]
        #refFaces = refFaces + [[q[:-1] for q in quads if q[-1] == r]]
        mesh_name = bpy.path.display_name_from_filepath(filepath)
        mesh = bpy.data.meshes.new(name=mesh_name)
        meshes.append(mesh)
        mesh.from_pydata(verts, [], refFaces)
        mesh.validate()
        mesh.update()


    if not meshes:
        return 1

    scene = context.scene

    objects = []
    for i,m in enumerate(meshes):
        obj = bpy.data.objects.new(m.name, m)
        bpy.ops.object.select_all(action='DESELECT')
        scene.objects.link(obj)
        scene.objects.active = obj
        mat = bpy.data.materials.new(m.name+"_material_"+str(i))
        if i==0:
            mat.diffuse_color = colorsys.hsv_to_rgb(0,0,1)
        else:
            mat.diffuse_color = colorsys.hsv_to_rgb(float(i/len(meshes)),1,1)
        obj.data.materials.append(mat)
        objects.append(obj)
    del meshes

    scene.update()
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select=True
    bpy.ops.object.join()
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.editmode_toggle()

    #Solutions according to the weight paint mode (0 to 1 by default)
    if len(MESH.vectors) > 0:
        print("Minimum velocity =", msh.np.min(msh.np.linalg.norm(MESH.vectors,axis=0)))
        print("Maximum velocity =", msh.np.max(msh.np.linalg.norm(MESH.vectors,axis=0)))
        bpy.ops.object.vertex_group_add()
        vgrp = bpy.context.active_object.vertex_groups[0]
        for X in tris+quads:
            for x in X:
                vgrp.add([x],msh.np.linalg.norm(MESH.vectors[x]),"REPLACE")
    elif len(MESH.scalars) > 0:
        print("Minimum .sol scalar =", msh.np.min(MESH.scalars))
        print("Maximum .sol scalar =", msh.np.max(MESH.scalars))
        bpy.ops.object.vertex_group_add()
        vgrp = bpy.context.active_object.vertex_groups[0]
        for X in tris+quads:
            for x in X:
                vgrp.add([x],MESH.scalars[x],"REPLACE")
    del MESH
    del verts, tris, quads

    return 0
class icp_operator(bpy.types.Operator):
    """Export a Mesh file"""
    bl_idname = "mesh.icp"
    bl_label  = "Runs an ICP between two meshes"

    maxIt = bpy.props.IntProperty(name="maxIt", description="Maximum number of iterations", default=50, min=1, max=200)
    numPtSource = bpy.props.IntProperty(name="numPtSource", description="Approximate number of points for the source", default=5000, min=100, max=20000)
    numPtTarget = bpy.props.IntProperty(name="numPtTarget", description="Approximate number of points for the target", default=5000, min=100, max=20000)
    toler = bpy.props.FloatProperty(name="toler", description="Tolerance threshold", default=0.001, min=0.00001, max=0.1)
    weigh = bpy.props.BoolProperty(name="weigh", description="Use the target weight as a segmentation region on source", default=True)

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and len(context.selected_objects)==2
            and context.mode=="OBJECT"
        )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        from . import icp
        #Identify the different objects
        sourceObject,targetObject = None, None
        sourceVerts, targetVerts = None, None
        for obj in context.selected_objects:
            if context.active_object == obj:
                targetObject = obj
            else:
                sourceObject = obj

        bpy.context.scene.objects.active=sourceObject
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
        source = sourceObject.to_mesh(context.scene, True, 'PREVIEW')
        sourceMat = sourceObject.matrix_world
        sourceVerts = [[x for x in sourceMat*v.co] for v in source.vertices[:]]
        step1 = int(len(sourceVerts)/self.numPtSource) + 1

        vgrp = sourceObject.vertex_groups.keys()
        if(len(vgrp)>0 and self.weigh):
            GROUP = sourceObject.vertex_groups.active
            cols = [0.0] * len(sourceVerts)
            for i,t in enumerate(source.polygons):
                for j,v in enumerate(t.vertices):
                    try:
                        cols[v] = float(GROUP.weight(v))
                    except:
                        continue
            sourceVerts = [v for v,c in zip(sourceVerts,cols) if c>0.5]

        sourceVerts = sourceVerts[::step1]


        bpy.context.scene.objects.active=targetObject
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
        target = targetObject.to_mesh(context.scene, True, 'PREVIEW')
        targetMat = targetObject.matrix_world
        targetVerts = np.array([[x for x in targetMat*v.co] for v in target.vertices])
        step2 = int(len(targetVerts)/self.numPtTarget) + 1
        targetVerts = targetVerts[::step2]

        T = icp.icp(sourceVerts, targetVerts, max_iterations=self.maxIt, tolerance=self.toler)
        sourceObject.matrix_world = mathutils.Matrix(T)

        return {'FINISHED'}

    def draw(self, context):
        self.layout.prop(self, "numPtSource", text="Approx pts for source")
        self.layout.prop(self, "numPtTarget", text="Approx pts for target")
        self.layout.prop(self, "maxIt", text="Max iterations")
        self.layout.prop(self, "toler", text="Tolerance")
        self.layout.prop(self, "weigh", text="Use weight paint")
        col = self.layout.column(align=True)
def tryint(s):
    try:
        return int(s)
    except:
        return s
def alphanum_key(s):
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]
def sort_nicely(l):
    l.sort(key=alphanum_key)
class import_sequence_operator(bpy.types.Operator, ExportHelper):
    """Imports a morphing sequence"""
    bl_idname = "import_mesh.sequence"
    bl_label  = "Morphing sequence"

    filter_glob = bpy.props.StringProperty(
        default="*.mesh",
        options={'HIDDEN'},
    )
    check_extension = True
    filename_ext = ".mesh"

    @classmethod
    def poll(cls, context):
        return (
            context.mode=="OBJECT"
        )

    def execute(self, context):
        keywords = self.as_keywords(ignore=('filter_glob','check_existing'))
        err = importSequence(self, context, **keywords)
        if err:
            return {'CANCELLED'}
        else:
            return {'FINISHED'}
def importSequence(operator, context, filepath):
    print(filepath)
    [verts, tris, quads] = msh.readMesh(filepath)

    tris = [t.tolist()[:-1] for t in tris]
    verts = [t.tolist()[:-1] for t in verts]

    mesh_name = "basis"
    mesh = bpy.data.meshes.new(name=mesh_name)
    mesh.from_pydata(verts, [], tris)
    mesh.validate()
    mesh.update()
    del verts, tris
    scene = context.scene
    obj = bpy.data.objects.new(mesh.name, mesh)
    bpy.ops.object.select_all(action='DESELECT')
    scene.objects.link(obj)
    scene.objects.active = obj
    scene.update()

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.editmode_toggle()

    path = "/".join(filepath.split("/")[:-1])
    root = (filepath.split("/")[-1]).split(".")[0]

    files = [f for f in os.listdir(path) if ".mesh" in f and root in f]
    sort_nicely(files)

    for f in files[1:]:
        print(f)
        [verts, tris, quads] = msh.readMesh(path + "/" + f)
        tris = [t.tolist()[:-1] for t in tris]
        verts = [t.tolist()[:-1] for t in verts]
        for basis in bpy.context.scene.objects:
            basis.select=True
            if basis.type == "MESH":
                shapeKey = basis.shape_key_add(from_mix=False)
                shapeKey.name = "1"
                for vert, newV in zip(basis.data.vertices, verts):
                    shapeKey.data[vert.index].co = newV
            basis.select=False

    for basis in bpy.context.scene.objects:
        if basis.type == "MESH":
            nb = len(files)
            scene = bpy.context.scene
            scene.frame_start = 1
            scene.frame_end   = 1 + nb * 3

            for i in range(nb):
                for j,key in enumerate(basis.data.shape_keys.key_blocks):
                    if i == j:
                        key.value = 1
                    else:
                        key.value = 0
                    key.keyframe_insert("value", frame=1 + 3*i)

    return 0
class medit_operator(bpy.types.Operator):
    """Previews a .mesh file in medit"""
    bl_idname = "preview.medit"
    bl_label  = "Preview in medit"
    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and len(context.selected_objects)==1
            and context.mode=="OBJECT"
        )
    def execute(self, context):
        bpy.ops.export_mesh.mesh(filepath="tmp.mesh")
        os.system("medit tmp.mesh")
        os.system("rm tmp.mesh")
        return {'FINISHED'}
class metis_partition_operator(bpy.types.Operator):
    """Partition a mesh with metis"""
    bl_idname = "mesh.metis_partition"
    bl_label  = "Metis partition"

    nPar = bpy.props.IntProperty(name="n partitions",  description="Number of partitions", default=5, min=2, max=50)
    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and len(context.selected_objects)==1
            and context.mode=="OBJECT"
        )
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    def execute(self, context):
        root="tmp"
        obj = bpy.context.scene.objects.active
        partition(obj,self.nPar)
    def draw(self, context):
        self.layout.prop(self, "nPar", text="n partitions")
def partition(object, nb):
    #Metis file writing
    mesh = object.to_mesh(bpy.context.scene, apply_modifiers=True, settings='PREVIEW')
    triangles = mesh.polygons
    with open(os.path.join("tmp.txt"),"w") as f:
        f.write( str(len(triangles)) + " 1\n")
        for t in triangles:
            for v in t.vertices:
                f.write(str(v+1))
                f.write(" ")
            f.write('\n')
    #Partitionning
    os.system("mpmetis " + "tmp.txt" + " " + str(nb))
    #Reading the results
    with open("tmp.txt.epart." + str(nb)) as f:
        partition = [int(line) for line in f]
        #Write the .mesh file
        with open("tmp.mesh","w") as f:
            f.write("MeshVersionFormatted 2\nDimension 3\n")
            f.write("Vertices\n" + str(len(mesh.vertices)) + "\n")
            for v in mesh.vertices:
                f.write(str(v.co[0]) + " " + str(v.co[1]) + " " + str(v.co[2]) + " " + str(0) + "\n")
            f.write("Triangles\n" + str(len(triangles)) + "\n")
            for i,t in enumerate(triangles):
                for v in t.vertices:
                    f.write(str(v+1))
                    f.write(" ")
                f.write(str(partition[i]))
                f.write('\n')
    #Import the new mesh
    #bpy.ops.object.select_all(action='DESELECT')
    #object.select = True
    #bpy.ops.object.delete()
    bpy.ops.import_mesh.mesh(filepath="tmp.mesh")
class mmgs_operator(bpy.types.Operator):
    """Remeshes a mesh with mmgs"""
    bl_idname = "mesh.mmgs"
    bl_label  = "MMGS remesh"

    hmin = bpy.props.FloatProperty(name="hmin",  description="Minimal edge length ratio", default=0.001, min=0.00001, max=0.1)
    hmax = bpy.props.FloatProperty(name="hmax",  description="Maximal edge length ratio", default=0.1, min=0.01, max=1)
    haus = bpy.props.FloatProperty(name="hausd", description="Haussdorf distance ratio", default=0.01, min=0.00001, max=0.1)
    hgra = bpy.props.FloatProperty(name="hgrad", description="Gradation", default=1.08, min=1, max=5)
    nr   = bpy.props.BoolProperty(name="nr", description="normal regulation", default=True)
    ar   = bpy.props.BoolProperty(name="ar", description="angle regulation", default=False)
    prev = bpy.props.BoolProperty(name="preview", description="preview only", default=True)
    sol  = bpy.props.BoolProperty(name="solution", description="use weight paint for metrics", default=False)

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and len(context.selected_objects)==1
            and context.mode=="OBJECT"
        )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        hasTriangulate = False
        obj = bpy.context.scene.objects.active
        maxDim = max(obj.dimensions)
        for m in bpy.context.scene.objects.active.modifiers:
            if m.type == 'TRIANGULATE':
                hasTriangulate = True
        if not hasTriangulate:
            bpy.ops.object.modifier_add(type='TRIANGULATE')

        bpy.context.scene["mmgsMini"] = self.hmin*maxDim
        bpy.context.scene["mmgsMaxi"] = self.hmax*maxDim
        bpy.ops.export_mesh.mesh(filepath="tmp.mesh")
        bpy.context.scene.objects.active = obj

        if not hasTriangulate:
            bpy.ops.object.modifier_remove(modifier="Triangulate")

        if not self.sol:
            os.system("rm tmp.sol")
        cmd = "mmgs_O3 tmp.mesh -o tmp.o.mesh"
        cmd+= " -hmin " + str(self.hmin*maxDim)
        cmd+= " -hmax " + str(self.hmax*maxDim)
        cmd+= " -hausd " + str(self.haus*maxDim)
        cmd+= " -hgrad " + str(self.hgra)
        if self.nr:
            cmd+=" -nr"
        if self.ar:
            cmd+=" -ar 1"

        os.system(cmd)

        os.system("medit tmp.o.mesh")

        if not self.prev:
            bpy.ops.import_mesh.mesh(filepath="tmp.o.mesh")

        os.system("rm tmp.o.mesh tmp.o.sol")

        return {'FINISHED'}

    def draw(self, context):
        self.layout.prop(self, "hmin", text="hmin")
        self.layout.prop(self, "hmax", text="hmax")
        self.layout.prop(self, "haus", text="hausd")
        self.layout.prop(self, "hgra", text="hgrad")
        self.layout.prop(self, "nr", text="nr")
        self.layout.prop(self, "ar", text="ar")
        self.layout.prop(self, "sol", text="Use solution")
        self.layout.prop(self, "prev", text="Preview only")
class superPCS_operator(bpy.types.Operator):
    """runs a super4PCS"""
    bl_idname = "mesh.superpcs"
    bl_label  = "Runs a super4PCS alignement between two meshes"

    #maxIt = bpy.props.IntProperty(name="maxIt", description="Maximum number of iterations", default=50, min=1, max=200)
    #numPtSource = bpy.props.IntProperty(name="numPtSource", description="Approximate number of points for the source", default=5000, min=100, max=20000)
    #numPtTarget = bpy.props.IntProperty(name="numPtTarget", description="Approximate number of points for the target", default=5000, min=100, max=20000)
    #toler = bpy.props.FloatProperty(name="toler", description="Tolerance threshold", default=0.001, min=0.00001, max=0.1)
    #weigh = bpy.props.BoolProperty(name="weigh", description="Use the target weight as a segmentation region on source", default=True)

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and len(context.selected_objects)==2
            and context.mode=="OBJECT"
        )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        #Identify the different objects
        sourceObject,targetObject = None, None
        sourceVerts, targetVerts = None, None
        for obj in context.selected_objects:
            if context.active_object == obj:
                targetObject = obj
            else:
                sourceObject = obj

        bpy.ops.object.select_all(action='DESELECT')
        sourceObject.select = True
        bpy.context.scene.objects.active=sourceObject
        bpy.ops.export_scene.obj(filepath="source.obj",use_selection=True, use_materials=False)

        bpy.ops.object.select_all(action='DESELECT')
        targetObject.select = True
        bpy.context.scene.objects.active=targetObject
        bpy.ops.export_scene.obj(filepath="target.obj",use_selection=True, use_materials=False)

        os.system("super4PCS -i source.obj target.obj -d 0.2 -r output.obj")

        """
        T = icp.icp(sourceVerts, targetVerts, max_iterations=self.maxIt, tolerance=self.toler)
        sourceObject.matrix_world = mathutils.Matrix(T)
        """

        return {'FINISHED'}

    def draw(self, context):
        """
        self.layout.prop(self, "numPtSource", text="Approx pts for source")
        self.layout.prop(self, "numPtTarget", text="Approx pts for target")
        self.layout.prop(self, "maxIt", text="Max iterations")
        self.layout.prop(self, "toler", text="Tolerance")
        self.layout.prop(self, "weigh", text="Use weight paint")
        """
        col = self.layout.column(align=True)
class tetgen_fill_operator(bpy.types.Operator):
    """Fills a closed surface with tetgen"""
    bl_idname = "mesh.tetgen_fill"
    bl_label = "Tetgen fill"

    opt_p = bpy.props.BoolProperty(name="opt_p", description="Piecewise Complex Linear", default=True)
    opt_q = bpy.props.BoolProperty(name="opt_q", description="Refines mesh to improve quality", default=True)
    opt_a = bpy.props.BoolProperty(name="opt_a", description="Maximum volume Constraint", default=True)
    opt_A = bpy.props.BoolProperty(name="opt_A", description="Attributes in different regions", default=True)
    opt_Y = bpy.props.BoolProperty(name="opt_Y", description="Preserves the surface", default=True)
    opt_Q = bpy.props.BoolProperty(name="opt_Q", description="Quiet", default=True)
    prev = bpy.props.BoolProperty(name="preview", description="preview only", default=True)

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and len(context.selected_objects)==1
            and context.mode=="OBJECT"
        )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        hasTriangulate = False
        obj = bpy.context.scene.objects.active
        maxDim = max(obj.dimensions)
        for m in bpy.context.scene.objects.active.modifiers:
            if m.type == 'TRIANGULATE':
                hasTriangulate = True
        if not hasTriangulate:
            bpy.ops.object.modifier_add(type='TRIANGULATE')

        bpy.ops.export_mesh.mesh(filepath="tmp.mesh")
        bpy.context.scene.objects.active = obj

        if not hasTriangulate:
            bpy.ops.object.modifier_remove(modifier="Triangulate")

        cmd = "tetgen"
        if self.opt_p:
            cmd+= " -p"
        if self.opt_q:
            cmd+= " -q"
        if self.opt_a:
            cmd+= " -a"
        if self.opt_A:
            cmd+= " -A"
        if self.opt_Y:
            cmd+= " -Y"
        if self.opt_Q:
            cmd+= " -Q"
        cmd+= " -g"
        cmd+= " tmp.mesh"

        os.system(cmd)

        os.system("medit tmp.1.mesh")

        if self.prev:
            os.system("rm tmp.mesh tmp.1.*")
        else:
            os.system("mv tmp.1.mesh fill.mesh")
            os.system("rm tmp.mesh tmp.1.*")

        return {'FINISHED'}

    def draw(self, context):
        self.layout.prop(self, "opt_p", text="PCL")
        self.layout.prop(self, "opt_q", text="mesh refinement")
        self.layout.prop(self, "opt_a", text="maximum volume")
        self.layout.prop(self, "opt_A", text="attributes in regions")
        self.layout.prop(self, "opt_Y", text="keep surface")
        self.layout.prop(self, "opt_Q", text="quiet")
        self.layout.prop(self, "prev", text="Preview only")
        col = self.layout.column(align=True)
class Weight2VertexCol(bpy.types.Operator):
    """Tooltip"""
    # from Kursad Karatas
    bl_idname = "object.weight2vertexcol"
    bl_label = "Weight2VertexCol"
    bl_space_type = "VIEW_3D"
    bl_options = {'REGISTER', 'UNDO'}

    method=bpy.props.BoolProperty(name="Color", description="Choose the coloring method", default=False)

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and len(context.selected_objects)==1
        )

    def execute(self, context):
        transferWeight2VertexCol(context, self.method)
        context.active_object.data.update()
        return {'FINISHED'}
def transferWeight2VertexCol(context, method):
    me=context.active_object
    verts=me.data.vertices

    col=mathutils.Color()
    col.h=0
    col.s=1
    col.v=1

    #vcolgrp=bpy.context.active_object.data.vertex_colors.keys()

    try:
        assert bpy.context.active_object.vertex_groups
        if not bpy.context.active_object.data.vertex_colors:
            bpy.context.active_object.data.vertex_colors.new()
        assert bpy.context.active_object.data.vertex_colors

    except AssertionError:
        print('you need at least one vertex group and one color group')
        return

    vgrp=bpy.context.active_object.vertex_groups.keys()

    vcolgrp=bpy.context.active_object.data.vertex_colors


    #Check to see if we have at least one vertex group and one vertex color group
    if len(vgrp) > 0 and len(vcolgrp) > 0:
        print ("enough parameters")
        if not method:
            for poly in me.data.polygons:
                for loop in poly.loop_indices:
                    vertindex=me.data.loops[loop].vertex_index
                    #weight=me.vertex_groups['Group'].weight(vertindex)
                    #Check to see if the vertex has any geoup association
                    try:
                        weight=me.vertex_groups.active.weight(vertindex)
                    except:
                        continue

                    col.r= (weight*-1.0)+1.0
                    col.g=col.r
                    col.b=col.r
                    me.data.vertex_colors.active.data[loop].color = (col.b, col.g, col.r)
