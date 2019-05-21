import bpy
import math
import struct

### The new operator ###
class Operator(bpy.types.Operator):
    bl_idname = "import_scene.ja_ase"
    bl_label = "Import JA ASE (.ase)"
    
    #gets set by the file select window - internal Blender Magic or whatever.
    filepath = bpy.props.StringProperty(name="File Path", description="File path used for importing the ASE file", maxlen= 1024, default="")
    
    def execute(self, context):
        self.ImportStart()
        return {'FINISHED'}

    def invoke(self, context, event):
        windowMan = context.window_manager
        #sets self.properties.filename and runs self.execute()
        windowMan.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def ImportStart(self):
        whitespace = set( " \t\n" )
        
        def error( msg ):
            self.report( { 'ERROR' }, msg )
        
        def skipWhitespace( file ):
            prevPos = file.tell()
            c = file.read( 1 )
            while c in whitespace:
                prevPos = file.tell()
                c = file.read( 1 )
            if c != "":
                file.seek( prevPos )
        
        # reads everything up to (and excluding) the next whitespace or {, } or *, returns that, cursor is before the whitespace
        # or, if the next token starts with {, } or * returns just that
        def readToken(file ):
            skipWhitespace( file )
            token = ""
            isString = False
            while True:
                prevPos = file.tell()
                c = file.read( 1 )
                if c == "\"":
                    if isString:
                        return token
                    else:
                        if token == "":
                            isString = True
                            continue
                        else: # treat " in mid-token as token's end
                            file.seek( prevPos )
                            return token
                if c in whitespace and not isString:
                    file.seek( prevPos )
                    return token
                if c in [ "{", "}", "*" ] and not isString:
                    if token == "":
                        return c
                    else:
                        file.seek( prevPos )
                        return token
                elif c == "":
                    if isString:
                        print( "Warning: Unterminated String!" )
                    return token
                else:
                    token = token + c
        
        class Block:
            def __init__( self ):
                self.name = ""
                self.parameters = []
                self.children = []
        
        class ASESyntaxError( RuntimeError ):
            def __init__( self, msg ):
                self.message = msg
            
            def __str__( self ):
                return repr( self.message )
        
        # Gets blocks - or should the be called Nodes? Basically stuff like this:
        # *MATERIAL_REF 0
        # and this:
        # *GEOMOBJECT { ... }
        # returns all of them on the same level, and recursively fills the "children" part of those
        def getBlocks( file ):
            blocks = []
            while True:
                prevPos = file.tell()
                token = readToken( file )
                if token == "":
                    return blocks
                elif token == "}":
                    file.seek( prevPos )
                    return blocks
                elif token != "*":
                    raise ASESyntaxError( "Invalid File: * expected, got {}".format( token ) )
                # else: Token == *
                # read block name
                block = Block()
                blocks.append( block )
                block.name = readToken( file )
                if block.name == "":
                    raise ASESyntaxError( "Invalid File: Unexpected end of file!" )
                elif block.name in [ "{", "}", "*" ]:
                    raise ASESyntaxError( "Invalid File: Unexpected {}!".format( block.name ) )
                # read block parameters, i.e. stuff that follows, and children, if any
                parametersOver = False
                while not parametersOver:
                    prevPos = file.tell()
                    nextToken = readToken( file )
                    if nextToken == "": #EOF
                        return blocks
                    elif nextToken in [ "}", "*"]: #end of block
                        file.seek( prevPos )
                        parametersOver = True
                    elif nextToken == "{": #children follow
                        block.children = getBlocks( file )
                        nextToken = readToken( file )
                        if nextToken != "}":
                            raise ASESyntaxError( "Invalid File: Block not properly closed!" )
                    else:
                        block.parameters.append( nextToken )
        
        # open file
        filename = self.properties.filepath
        file = open(filename)
        
        # read file
        try:
            blocks = getBlocks( file )
        except ASESyntaxError as err:
            error( err.message )
            return
        
        #     interpret read blocks:
        
        #   check filetype/version:
        if len( blocks ) == 0:
            error( "No valid ASE file, should start with *3DSMAX_ASCIIEXPORT!" )
            return
        if blocks[0].name.lower() != "3dsmax_asciiexport":
            error( "No valid ASE file, should start with *3DSMAX_ASCIIEXPORT, starts with {}!".format( blocks[0].name ) )
            return
        if len( blocks[0].parameters ) == 0 or blocks[0].parameters[0] != "200":
            error( "Invalid ASE file, wrong version number, must be 200!" )
            return
        
        # remove filetype block
        blocks = blocks[ 1: ]
        
        #   find material list
        material_lists = [ block for block in blocks if block.name.lower() == "material_list" ]
        if len( material_lists ) == 0:
            error( "No *MATERIAL_LIST!" )
            return
        elif len( material_lists ) > 1:
            error( "More than one *MATERIAL_LIST!" )
            return
        # else len == 1
        material_list = material_lists[0]
        material_blocks = [ block for block in material_list.children if block.name.lower() == "material" ]
        try:
            if not all( [ ( len( block.parameters ) > 0 and block.parameters[0] == str( index ) ) for index, block in enumerate( material_blocks ) ] ):
                error( "Materials out of order" )
                return
        except IndexError:
            error( "Invalid file: *MATERIAL with too few arguments!" )
        #   create materials based on material list
        material_names = []
        try:
            for material_block in material_blocks:
                names = [ child.parameters[0] for child in material_block.children if child.name.lower() == "material_name" ]
                if len(names) == 0:
                    error( "*MATERIAL without *MATERIAL_NAME!" )
                    return
                elif len(names) > 1:
                    print( "Warning: *MATERIAL with multiple *MATERIAL_NAMEs!" )
                material_names.append( names[0] )
        except IndexError:
            error( "Invalid file: *MATERIAL_NAME with too few arguments!" )
        
        #   find objects with meshes
        class Object:
            def __init__( self, index ):
                self.mat_ref = -1
                self.vertices = [] #flat list of coordinates
                self.faces = []    #flat list of indices
                self.tvertices = []#list of uv pairs
                self.tfaces = []   #list of tvertex index triples
                self.index = index #index of this object's GEOMOBJECT entry
            
            def toBlender( self, materials ):
                # create mesh
                
                mesh = bpy.data.meshes.new( "ASEMesh" )
                
                # add material
                
                mat  = materials[ self.mat_ref ]
                mesh.materials.append( mat )
                
                # add vertices
                
                numVerts = len( self.vertices ) // 3
                mesh.vertices.add( numVerts )
                mesh.vertices.foreach_set( "co", self.vertices )
                
                # add faces
                                
                numTris = len( self.faces ) // 3
                mesh.polygons.add( numTris )
                # loops are the per-face-vertex-settings in one long flat list
                mesh.loops.add( numTris * 3 )
                # so we need to set where in that list a face's settings start...
                mesh.polygons.foreach_set( "loop_start", range( 0, numTris * 3, 3 ) )
                # ... and how many there are.
                mesh.polygons.foreach_set( "loop_total", (3,) * numTris )
                mesh.loops.foreach_set( "vertex_index", self.faces )
                
                mesh.uv_textures.new() #creates a new uv_layer
                uv_loops = mesh.uv_layers.active.data[:]
                for poly, tface in zip(mesh.polygons, self.tfaces):
                    for ofs, tvertIndex in enumerate( tface ):
                        tvert = None
                        try:
                            tvert = self.tvertices[ tvertIndex ]
                        except IndexError:
                            error( "Invalid file: TFACELIST references non-existing TVERT {} in GEOMOBJECT {}".format( tvertIndex, self.index ) )
                            return
                        try:
                            uv_loops[ poly.loop_start + ofs ].uv = tvert
                        except IndexError:
                            error( "Invalid file: TFACELIST of GEOMOBJECT {} too long.".format( self.index) )
                            return
                
                mesh.update()
                mesh.validate()
                
                # add object
                
                obj = bpy.data.objects.new( "ASEObject", mesh )
                bpy.context.scene.objects.link( obj ) # remember scene.update() later!
        
        objects = []
        
        # if the last index is 0, blender assumes that to be the end...
        # or does it? Maybe it does, but changing the order screws UV up and that
        def fixOrder( face ):
            if face[ -1 ] == 0:
                print( "There might be a missing face on this model. If that's the case, tell me to fix the importer, it's my fault." )
                return face #do nothing for now...
                face.insert( 0, face[ -1 ] )
                del face[ -1 ]
            return face
        
        objIndex = -1
        for block in blocks:
            if block.name.lower() == "geomobject":
                objIndex = objIndex + 1
                try:
                    meshes = [ child for child in block.children if child.name.lower() == "mesh"]
                    mat_refs = [ child for child in block.children if child.name.lower() == "material_ref" ]
                    if len( meshes ) != 1 or len( mat_refs ) != 1:
                        error( "*GEOMOBJECT with no/multiple *MESH and/or *MAT_REF" )
                        return
                    mesh = meshes[ 0 ]
                    vertex_lists = [ child for child in mesh.children if child.name.lower() == "mesh_vertex_list" ]
                    face_lists = [ child for child in mesh.children if child.name.lower() == "mesh_face_list" ]
                    tvert_lists = [ child for child in mesh.children if child.name.lower() == "mesh_tvertlist" ]
                    tface_lists = [ child for child in mesh.children if child.name.lower() == "mesh_tfacelist" ]
                    if len( vertex_lists ) != 1 or len( face_lists ) != 1 or len( tvert_lists ) != 1 or len( tface_lists ) != 1:
                        error( "Invalid *MESH with no/multiple *MESH_VERTEX_LIST/*MESH_FACE_LIST/*MESH_TVERTLIST/*MESH_TFACELIST" )
                        return
                    
                    print( "TVerts:", len( tvert_lists[0].children ) )
                    
                    object = Object( objIndex )
                    object.mat_ref = int( mat_refs[ 0 ].parameters[ 0 ] )
                    # list comprehension yay!
                    
                    # get vertices
                    # basically: [ float(vertex_lists[0].children[n].parameters[1]), float(vertex_lists[0].children[n].parameters[2]), float(vertex_lists[0].children[n].parameters[3]), float(vertex_lists[0].children[n+1].parameters[1]), ... ] for those n... where children[n].name == "MESH_VERTEX"
                    object.vertices = [ float( vert.parameters[ i ] ) for vert in vertex_lists[0].children if vert.name.lower() == "mesh_vertex" for i in [ 1, 2, 3 ] ]
                    
                    # get faces (one flat list of indices)
                    faces = [ fixOrder( [ int( face.parameters[ 2 ] ), int( face.parameters[ 4 ] ), int( face.parameters[ 6 ] ) ] ) for face in face_lists[0].children if face.name.lower() == "mesh_face" ]
                    # flatten
                    object.faces = [ face[ i ] for face in faces for i in range( 3 ) ]
                    
                    # get tvertices (list of uv-pairs)
                    #object.tvertices = [ float( vert.parameters[ i ] ) for vert in tvert_lists[0].children if vert.name.lower() == "mesh_tvert" for i in [ 1, 2 ] ]
                    object.tvertices = [ [ float( vert.parameters[ i ] ) for i in [1, 2] ] for vert in tvert_lists[0].children if vert.name.lower() == "mesh_tvert" ]
                    
                    # get tfaces (list of index-triples)
                    #object.tfaces = [ fixOrder( [ int( face.parameters[ 1 ] ), int( face.parameters[ 2 ] ), int( face.parameters[ 3 ] ) ] ) for face in tface_lists[0].children if face.name.lower() == "mesh_tface" ]
                    object.tfaces = [ [ int( face.parameters[ 1 ] ), int( face.parameters[ 2 ] ), int( face.parameters[ 3 ] ) ] for face in tface_lists[0].children if face.name.lower() == "mesh_tface" ]
                    objects.append( object )
                except IndexError as err:
                    print( err )
                    error( "Invalid file: Node with too few arguments!" )
        
        materials = [ bpy.data.materials.new( material_name ) for material_name in material_names ]
        
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')
        for object in objects:
            object.toBlender( materials )
        bpy.context.scene.update() # since new objects have been linked

def menu_func(self, context):
    self.layout.operator(Operator.bl_idname, text="JA ASE (.ase)")
