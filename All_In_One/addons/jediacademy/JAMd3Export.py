
__author__ = ["Xembie","PhaethonH","Bob Holcomb","Damien McGinnes","Robert (Tr3B) Beckebans"]
__version__ = '1.4'
__url__ = ["www.blender.org","http://xreal.sourceforge.net","http://www.katsbits.com"]

import math, time, os, imp, mathutils
if "JAMd3Encode" in locals():
    import imp
    imp.reload( JAMd3Encode )
else:
    from . import JAMd3Encode

def message( log, msg ):
    if log:
        log.write( msg + "\n" )
    else:
        print( msg )

class md3Settings:
    def __init__( self,
                  savepath,
                  name,
                  logtype,
                  dumpall   = False,
                  ignoreuvs = False,
                  scale     = 1.0,
                  offsetx   = 0.0,
                  offsety   = 0.0,
                  offsetz   = 0.0 ):
        self.savepath  = savepath
        self.name      = name
        self.logtype   = logtype
        self.dumpall   = dumpall
        self.ignoreuvs = ignoreuvs
        self.scale     = scale
        self.offset    = [ offsetx, offsety, offsetz ]

def print_md3(log,md3,dumpall):
    message( log, "Header Information" )
    message( log, "Ident: {}".format( md3.ident ) )
    message( log, "Version: {}".format( md3.version ) )
    message( log, "Name: {}".format( md3.name ) )
    message( log, "Flags: {}".format( md3.flags ) )
    message( log, "Number of Frames: {}".format( md3.numFrames ) )
    message( log, "Number of Tags: {}".format( md3.numTags ) )
    message( log, "Number of Surfaces: {}".format( md3.numSurfaces ) )
    message( log, "Number of Skins: {}".format( md3.numSkins ) )
    message( log, "Offset Frames: {}".format( md3.ofsFrames ) )
    message( log, "Offset Tags: {}".format( md3.ofsTags ) )
    message( log, "Offset Surfaces: {}".format( md3.ofsSurfaces ) )
    message( log, "Offset end: {}".format( md3.ofsEnd ) )
    
    if dumpall:
        message( log, "Frames:" )
        for f in md3.frames:
            message( log," Mins: {f.mins[0]} {f.mins[1]} {f.mins[2]}".format( f = f ) )
            message( log," Maxs: {f.maxs[0]} {f.maxs[1]} {f.maxs[2]}".format( f = f ) )
            message( log," Origin(local): {f.localOrigin[0]} {f.localOrigin[1]} {f.localOrigin[2]}".format( f = f ) )
            message( log," Radius: {}".format( f.radius ) )
            message( log," Name: {}".format( f.name ) )

        message( log, "Tags:" )
        for t in md3.tags:
            message( log, " Name: " + t.name)
            message( log, " Origin: {t.origin[0]} {t.origin[1]} {t.origin[2]}".format( t = t ) )
            message( log, " Axis[0]: {t.axis[0]} {t.axis[1]} {t.axis[2]}".format( t = t ) )
            message( log, " Axis[1]: {t.axis[3]} {t.axis[4]} {t.axis[5]}".format( t = t ) )
            message( log, " Axis[2]: {t.axis[6]} {t.axis[7]} {t.axis[8]}".format( t = t ) )

        message( log, "Surfaces:" )
        for s in md3.surfaces:
            message( log, " Ident: {}".format( s.ident ) )
            message( log, " Name: {}".format( s.name ) )
            message( log, " Flags: {}".format( s.flags ) )
            message( log, " # of Frames: {}".format( s.numFrames ) )
            message( log, " # of Shaders: {}".format( s.numShaders ) )
            message( log, " # of Verts: {}".format( s.numVerts ) )
            message( log, " # of Triangles: {}".format( s.numTriangles ) )
            message( log, " Offset Triangles: {}".format( s.ofsTriangles ) )
            message( log, " Offset UVs: {}".format( s.ofsUV ) )
            message( log, " Offset Verts: {}".format( s.ofsVerts ) )
            message( log, " Offset End: {}".format( s.ofsEnd ) )
            message( log, " Shaders:" )
            for shader in s.shaders:
                message( log, "    Name: {}".format( shader.name ) )
                message( log, "    Index: {}".format( shader.index ) )
            message( log, " Triangles:" )
            for tri in s.triangles:
                message( log,"    Indexes: {tri.indexes[0]} {tri.indexes[1]} {tri.indexes[2]}".format( tri = tri ) )
            message( log, " UVs:")
            for uv in s.uv:
                message( log, "    U: {}".format( uv.u ) )
                message( log, "    V: {}".format( uv.v ) )
            message( log, " Verts:" )
            for vert in s.verts:
                message( log, "    XYZ: {xyz[0]} {xyz[1]} {xyz[2]}".format( xyz = vert.xyz ) )
                message( log, "    Normal: {}".format( vert.normal ) )

    shader_count = 0
    vert_count   = 0
    tri_count    = 0
    for surface in md3.surfaces:
        shader_count += surface.numShaders
        tri_count    += surface.numTriangles
        vert_count   += surface.numVerts
        if surface.numShaders >= JAMd3Encode.MD3_MAX_SHADERS:
            message( log, "!Warning: Shader limit ({}/{}) reached for surface {}".format( surface.numShaders, JAMd3Encode.MD3_MAX_SHADERS, surface.name ) )
        if surface.numVerts >= JAMd3Encode.MD3_MAX_VERTICES:
            message( log, "!Warning: Vertex limit ({}/{}) reached for surface {}".format( surface.numVerts, JAMd3Encode.MD3_MAX_VERTICES, surface.name ) )
        if surface.numTriangles >= JAMd3Encode.MD3_MAX_TRIANGLES:
            message( log, "!Warning: Triangle limit ({}/{}) reached for surface {}".format( surface.numTriangles, JAMd3Encode.MD3_MAX_TRIANGLES, surface.name ) )
    
    if md3.numTags >= JAMd3Encode.MD3_MAX_TAGS:
        message(log,"!Warning: Tag limit ({}/{}) reached for md3!".format( md3.numTags, JAMd3Encode.MD3_MAX_TAGS ) )
    if md3.numSurfaces >= JAMd3Encode.MD3_MAX_SURFACES:
        message(log,"!Warning: Surface limit ({}/{}) reached for md3!".format( md3.numSurfaces, JAMd3Encode.MD3_MAX_SURFACES ) )
    if md3.numFrames >= JAMd3Encode.MD3_MAX_FRAMES:
        message(log,"!Warning: Frame limit ({}/{}) reached for md3!".format( md3.numFrames, JAMd3Encode.MD3_MAX_FRAMES ) )
        
    message( log, "Total Shaders: {}".format( shader_count ) )
    message( log, "Total Triangles: {}".format( tri_count ) )
    message( log, "Total Vertices: {}".format( vert_count ) )

def save_md3(settings):
    starttime = time.clock() #start timer
    newlogpath = os.path.splitext( settings.savepath )[ 0 ] + ".log"
    if settings.logtype == "append":
        log = open(newlogpath,"a")
    elif settings.logtype == "overwrite":
        log = open(newlogpath,"w")
    else:
        log = False
    message( log, "######################BEGIN######################" )
    message( log, "Exporting selected objects..." )
    ##bpy.ops.object.mode_set(mode='OBJECT')
    md3           = JAMd3Encode.md3Object()
    md3.ident     = JAMd3Encode.MD3_IDENT
    md3.version   = JAMd3Encode.MD3_VERSION
    md3.name      = settings.name
    md3.numFrames = ( bpy.context.scene.frame_end + 1 ) - bpy.context.scene.frame_start

    # matrix to apply offset & scale - just calculate once and cache
    offset_scale_mat = mathutils.Matrix.Translation( settings.offset ) * mathutils.Matrix.Scale( settings.scale, 4 )
    
    # export all selected meshes, remember empties for later...
    empties = []
    for obj in bpy.context.selected_objects:
        # ...of type mesh
        if obj.type == 'MESH':
            bpy.context.scene.frame_set( bpy.context.scene.frame_start )
            mesh = obj.to_mesh( bpy.context.scene, True, 'PREVIEW' )
            
            nsurface       = JAMd3Encode.md3Surface()
            nsurface.name  = obj.name
            nsurface.ident = JAMd3Encode.MD3_IDENT
            
            ignoreuvs = False
            nshader   = JAMd3Encode.md3Shader()
            #Add only 1 shader per surface/object
            try:
                #Using custom properties allows a longer string
                nshader.name = obj[ "md3shader" ]
            except: #we should add a blank as a placeholder
                ignoreuvs    = True
                nshader.name = "NULL"
                message( log, "{} has no md3shader property, defaulting to NULL".format( obj.name ) )
            nsurface.shaders.append( nshader )
            nsurface.numShaders = 1
 
            vertlist = []
            
            if len( mesh.uv_layers ) == 0:
                message( log, "{} has no UV map".format( obj.name ) )
                ignoreuvs = True
            else:
                uvLoops = mesh.uv_layers[0].data

            for polyIndex, polygon in enumerate( mesh.polygons ):
                ntri = JAMd3Encode.md3Triangle()
                if len( polygon.vertices ) != 3:
                    message( log, "Found a nontriangle face in object " + obj.name )
                    continue

                for indexIndex, (vertIndex, uvLoopIndex) in enumerate( zip( polygon.vertices, polygon.loop_indices) ):
                    if settings.ignoreuvs or ignoreuvs:
                        uv = [ 0, 0 ]
                    else:
                        uv = uvLoops[ uvLoopIndex ].uv.to_tuple()
                        uv = [ round( x, 5 ) for x in uv ]

                    match = False
                    match_index = 0
                    # find duplicate UV coordinates, don't add those vertices twice.
                    for i, vi in enumerate( vertlist ):
                        if vi == vertIndex:
                            if settings.ignoreuvs or ignoreuvs:
                                match = True
                                match_index = i
                                break
                            else:
                                if nsurface.uv[ i ].u == uv[ 0 ] and nsurface.uv[ i ].v == uv[ 1 ]:
                                    match = True
                                    match_index = i
                                    break
                    
                    if not match:
                        # this UV coordinate is not yet used - add it
                        vertlist.append( vertIndex )
                        ntri.indexes[ indexIndex ] = nsurface.numVerts
                        ntex = JAMd3Encode.md3TexCoord()
                        ntex.u = uv[ 0 ]
                        ntex.v = uv[ 1 ]
                        nsurface.uv.append( ntex )
                        nsurface.numVerts += 1
                    else:
                        # this UV coordinate has been previously encountered, use that one.
                        ntri.indexes[ indexIndex ] = match_index
                nsurface.triangles.append( ntri )
                nsurface.numTriangles += 1

            for frame in range( bpy.context.scene.frame_start,bpy.context.scene.frame_end + 1 ):
                bpy.context.scene.frame_set( frame )
                frame_mesh = obj.to_mesh( bpy.context.scene, True, 'PREVIEW' )
                #fobj.calc_normals()
                # only add new frames once
                if len( md3.frames ) <= frame - bpy.context.scene.frame_start:
                        nframe = JAMd3Encode.md3Frame()
                        nframe.name = str( frame )
                else:
                        nframe = md3.frames[ frame - bpy.context.scene.frame_start ]
                for vi in vertlist:
                    vert = frame_mesh.vertices[ vi ]
                    nvert = JAMd3Encode.md3Vert()
                    nvert.normal = nvert.Encode( vert.normal )
                    nvert.xyz = offset_scale_mat * obj.matrix_world * vert.co
                    nvert.xyz = [ round( x, 5 ) for x in nvert.xyz ]
                    for i in range(0,3):
                        nframe.mins[i] = min( nframe.mins[ i ], nvert.xyz[i] )
                        nframe.maxs[i] = max( nframe.maxs[ i ], nvert.xyz[i] )
                    minlength = math.sqrt( sum( [ x * x for x in nframe.mins ] ) )
                    maxlength = math.sqrt( sum( [ x * x for x in nframe.maxs ] ) )
                    nframe.radius = round( max( minlength, maxlength), 5)
                    nsurface.verts.append( nvert ) 
                # only add if not already there
                if len( md3.frames ) <= frame - bpy.context.scene.frame_start:
                        md3.frames.append( nframe )
                nsurface.numFrames += 1
                bpy.data.meshes.remove( frame_mesh )
            assert( len( md3.frames ) == md3.numFrames )
            md3.surfaces.append( nsurface )
            md3.numSurfaces += 1
            
            # to_mesh creates a copy with modifiers applied - we got to delete that
            bpy.data.meshes.remove( mesh )

        elif obj.type == 'EMPTY':
            empties.append( obj )
    
    #write empties(=tags) in correct order - tag1frame1, tag2frame1, ..., tag1frame2, tag2frame2, ...
    md3.numTags = len(empties)
    for frame in range(bpy.context.scene.frame_start,bpy.context.scene.frame_end + 1):
        bpy.context.scene.frame_set(frame)
        for obj in empties:
            ntag = JAMd3Encode.md3Tag()
            ntag.name = obj.name
            ntag.origin = [ round( ( obj.matrix_world[ i ][ 3 ] * settings.scale ) + settings.offset[ i ], 5 ) for i in range( 3 ) ]
            ntag.axis = [ obj.matrix_world[ x ] [ y ] for y in range( 3 ) for x in range ( 3 ) ]
            md3.tags.append( ntag )
    
    if bpy.context.selected_objects:
        file = open( settings.savepath, "wb" )
        md3.Save( file )
        print_md3( log, md3, settings.dumpall )
        file.close()
        message( log, "MD3 saved to " + settings.savepath )
        elapsedtime = round(time.clock() - starttime, 5 )
        message( log, "Elapsed {} seconds".format( elapsedtime ) )
    else:
        message( log, "Select an object to export!" )
        
    if log:
        print( "Logged to {}".format( newlogpath ) )
        log.close()


from bpy.props import *
import bpy

class Operator( bpy.types.Operator ):
    bl_idname = "export.ja_md3"
    bl_label = "Export MD3"

    logenum = [ ( "console",   "Console",   "log to console"     ),
                ( "append",    "Append",    "append to log file" ),
                ( "overwrite", "Overwrite", "overwrite log file" ) ]

    filepath = StringProperty( subtype = 'FILE_PATH', name = "File Path", description = "Filepath for exporting", maxlen = 1024, default = "" )
    md3name = StringProperty( name = "MD3 Name", description = "MD3 header name / skin path (64 bytes)", maxlen = 64, default = "" )
    md3logtype = EnumProperty( name = "Save log", items = logenum, description = "File logging options",default = 'console')
    md3dumpall = BoolProperty( name = "Dump all", description = "Dump all data for md3 to log", default = False )
    md3ignoreuvs = BoolProperty( name = "Ignore UVs", description = "Ignores uv influence on mesh generation", default = False )
    md3scale = FloatProperty( name = "Scale", description = "Scale all objects from world origin (0,0,0)", default = 1.0,precision = 5 )
    md3offsetx = FloatProperty( name = "Offset X", description = "Transition scene along x axis", default = 0.0, precision = 5 )
    md3offsety = FloatProperty( name = "Offset Y", description = "Transition scene along y axis", default = 0.0, precision = 5 )
    md3offsetz = FloatProperty( name = "Offset Z", description = "Transition scene along z axis", default = 0.0, precision = 5 )

    def execute( self, context ):
        settings = md3Settings( savepath = self.properties.filepath,
                                name = self.properties.md3name,
                                logtype = self.properties.md3logtype,
                                dumpall = self.properties.md3dumpall,
                                ignoreuvs = self.properties.md3ignoreuvs,
                                scale = self.properties.md3scale,
                                offsetx = self.properties.md3offsetx,
                                offsety = self.properties.md3offsety,
                                offsetz = self.properties.md3offsetz )
        save_md3( settings )
        return { 'FINISHED' }

    def invoke( self, context, event ):
        wm = context.window_manager
        wm.fileselect_add( self )
        return { 'RUNNING_MODAL' }

def menu_func( self, context ):
    self.layout.operator(Operator.bl_idname, text="JA MD3 (.md3)")
