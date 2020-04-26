#    ASE Export Functionality

if "bpy" not in locals():
    import bpy

class Vertex:
    # co: mathutils.Vector (3d)
    # uv: pair
    def __init__( self, co, uv ):
        self.co = co
        self.uv = uv

class Surface:
    # verts: list of Vertex
    # tris: list of vertexIndex (number)
    def __init__( self, verts, tris, materialIndex ):
        self.verts = verts
        self.tris = tris
        self.materialIndex = materialIndex
    
    def saveToFile( self, file ):
        # if the type of numVertices/numTriangles changes, changes to LevelExporter.readMesh will be required as well (limit check)
        file.write( "*GEOMOBJECT\t{{\n\t*MESH\t{{\n\t\t*TIMEVALUE\t0\n\t\t*MESH_NUMVERTEX\t{}\n\t\t*MESH_NUMFACES\t{}\n\t\t*MESH_VERTEX_LIST\t{{\n".format( len( self.verts ), len( self.tris ) ) )
        for i, vert in enumerate( self.verts ):
            file.write( "\t\t\t*MESH_VERTEX\t{index}\t{co[0]:.8f}\t{co[1]:.8f}\t{co[2]:.8f}\n".format( index=i, co=vert.co ) )
        file.write( "\t\t}\n\t\t*MESH_FACE_LIST\t{\n" )
        for i, tri in enumerate( self.tris ):
            file.write( "\t\t\t*MESH_FACE\t{index}\tA:\t{tri[0]}\tB:\t{tri[1]}\tC:\t{tri[2]}\tAB:\t1\tBC:\t1\tCA:\t1\t*MESH_SMOOTHING\t0\t*MESH_MTLID\t0\n".format( index=i, tri=tri ) )
        file.write( "\t\t}}\n\t\t*MESH_NUMTVERTEX\t{}\n\t\t*MESH_TVERTLIST\t{{\n".format( len( self.verts ) ) )
        for i, vert in enumerate( self.verts ):
            file.write( "\t\t\t*MESH_TVERT\t{index}\t{uv[0]:.7f}\t{uv[1]:.7f}\n".format( index=i, uv=vert.uv ) )
        file.write( "\t\t}}\n\t\t*MESH_NUMTVFACES\t{}\n\t\t*MESH_TFACELIST\t{{\n".format( len( self.tris ) ) )
        for i, tri in enumerate( self.tris ):
            file.write( "\t\t\t*MESH_TFACE\t{index}\t{tri[0]}\t{tri[1]}\t{tri[2]}\n".format( index=i, tri=tri ) )
        file.write( "\t\t}}\n\t}}\n\t*MATERIAL_REF\t{}\n}}\n".format( self.materialIndex ) )
        return True

class ModelExporter:
    def __init__(self, errorFunc):
        self.reportError = errorFunc
        self.materialIndices = {}
        
    def export( self, filename ):
        # We work on layer 0
        prevLayer0State = bpy.context.scene.layers[0]
        
        # read objects
        if not self.readObjects():
            bpy.context.scene.layers[0] = prevLayer0State
            return
        
        bpy.context.scene.layers[0] = prevLayer0State
        
        # save to file
        with open(filename, "w") as file:
            self.saveToFile(file)
            file.close()
            return
        
        self.reportError("Could not open \"{}\" for writing!".format(filename))
        
    def readObjects( self ):
        self.surfaces = []
        # go through all objects in the scene
        for obj in bpy.context.scene.objects:
            # mesh entities are geometry
            if obj.type == 'MESH':
                if not self.readGeometry(obj):
                    return False
        return True
        
    def readGeometry( self, obj ):
        if bpy.context.mode != 'OBJECT':
            self.reportError("Must be in Object Mode to export!")
            return False
        
        print( "Processing geometry object \"{}\"...".format( obj.name ) )
            
        bpy.ops.object.select_all( action='DESELECT' )
        
        success = True
        mesh = obj.to_mesh( bpy.context.scene, True, 'PREVIEW' )
        # only export meshes with faces
        if len( mesh.polygons ) > 0:
            # let's just use the first material, it's the user's job to separate by material.
            material = obj.material_slots[0]
            if not self.readMesh( obj, mesh, material ):
                success = False
        bpy.data.meshes.remove(mesh)
        
        print( "Done." )
        
        return success
    
    def readMesh( self, obj, mesh, material ):
        # make sure there's a uv map
        if len( mesh.uv_layers ) == 0:
            self.reportError( "Mesh of object \"{}\" has no UV map!".format( obj.name ) )
            return False
        uv_layer = mesh.uv_layers[0]
        uv_loops = uv_layer.data
        if len( uv_loops ) == 0:
            self.reportError( "Mesh of object \"{}\" has no UV map!".format( obj.name ) )
            return False
        
        # a single vertex may have multiple uv coordinates (since they're per face)
        # I need to export that as multiple vertices, so I use this:
        # { blender vertex index : [ blender uv loop index ] }
        exportIndexLookup = {}
        verts = []
        # also adds the vertex to verts, if necessary
        def getExportIndex( vertexIndex, loopIndex ):
            uv = uv_loops[ loopIndex ].uv.to_tuple()
            indices = exportIndexLookup.get( vertexIndex )
            if not indices:
                exportIndexLookup[vertexIndex] = indices = {}
            index = indices.get(uv)
            if not index:
                verts.append( Vertex( obj.matrix_world * mesh.vertices[ vertexIndex ].co, uv ) )
                index = len( verts ) - 1
                indices[ uv ] = index
            return index
        
        # the polys may get new vertex indices due to vertex splitting due to different UVs - this is all done by this beautiful list comprehension.
        tris = [ [ getExportIndex( vertIndex, loopIndex ) for vertIndex, loopIndex in zip( poly.vertices, poly.loop_indices ) ] for poly in mesh.polygons ]
        
        materialIndex = None
        if material in self.materialIndices:
            materialIndex = self.materialIndices[ material ]
        else:
            materialIndex = len( self.materialIndices )
            self.materialIndices[ material ] = materialIndex
        print("surface makin'")
        # append surface to list of surfaces
        self.surfaces.append( Surface( verts, tris, materialIndex ) )
        
        return True
    
    def saveToFile( self, file ):
        # save header
        file.write( "*3DSMAX_ASCIIEXPORT\t200\n" )
        
        # save materials
        file.write( "*MATERIAL_LIST\t{\n" )
        file.write( "\t*MATERIAL_COUNT\t{}\n".format( len( self.materialIndices ) ) )
        for material, materialIndex in self.materialIndices.items():
            file.write( "\t*MATERIAL\t{}\t{{\n\t\t*MATERIAL_NAME\t\"{}\"\n\t}}\n".format( materialIndex, material.name ) )
        file.write( "}\n" )
        
        # save surfaces
        for surface in self.surfaces:
            if not surface.saveToFile( file ):
                return False
        return True

class Operator( bpy.types.Operator ):
    """Operator for ASE export"""

    bl_idname = "export_scene.ja_ase"
    bl_label = "Export JA ASE (.ase)"

    filepath = bpy.props.StringProperty( subtype='FILE_PATH' )

    def execute( self, context ):
        filepath = bpy.path.ensure_ext( self.filepath, ".ase" )
        
        def report_error(msg):
            self.report( { 'ERROR' }, msg )
        
        exporter = ModelExporter(report_error)
        exporter.export(filepath)
        return { "FINISHED" }

    def invoke( self, context, event ):
        if not self.filepath:
            self.filepath = bpy.path.ensure_ext( bpy.data.filepath, ".ase" )
        WindowManager = context.window_manager
        WindowManager.fileselect_add( self )
        return { "RUNNING_MODAL" }

def menu_func(self, context):
    self.layout.operator(Operator.bl_idname, text="JA ASE (.ase)")