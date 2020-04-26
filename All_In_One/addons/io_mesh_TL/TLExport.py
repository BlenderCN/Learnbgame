#!BPY

"""
Name: 'OGRE for Torchlight (*.MESH)'
Blender: 2.59, 2.62, 2.63a
Group: 'Import/Export'
Tooltip: 'Import/Export Torchlight OGRE mesh files'
    
Author: Dusho

Thanks goes to 'goatman' for his port of Ogre export script from 2.49b to 2.5x,
and 'CCCenturion' for trying to refactor the code to be nicer (to be included)

"""

__author__ = "Dusho"
__version__ = "0.6.2 09-Mar-2013"

__bpydoc__ = """\
This script imports/exports Torchlight Ogre models into/from Blender.

Supported:<br>
    * import/export of basic meshes
    * import of skeleton
    * import/export of vertex weights (ability to import characters and adjust rigs)

Missing:<br>   
    * skeletons (export)
    * animations
    * vertex color export

Known issues:<br>
    * imported materials will loose certain informations not applicable to Blender when exported
     
History:<br>
    * v0.6.2   (09-Mar-2013) - bug fixes (working with materials+textures), added 'Apply modifiers' and 'Copy textures'
    * v0.6.1   (27-Sep-2012) - updated to work with Blender 2.63a
    * v0.6     (01-Sep-2012) - added skeleton import + vertex weights import/export
    * v0.5     (06-Mar-2012) - added material import/export
    * v0.4.1   (29-Feb-2012) - flag for applying transformation, default=true
    * v0.4     (28-Feb-2012) - fixing export when no UV data are present
    * v0.3     (22-Feb-2012) - WIP - started cleaning + using OgreXMLConverter
    * v0.2     (19-Feb-2012) - WIP - working export of geometry and faces
    * v0.1     (18-Feb-2012) - initial 2.59 import code (from .xml)
    * v0.0     (12-Feb-2012) - file created
"""

#from Blender import *
from xml.dom import minidom
import bpy
from mathutils import Vector, Matrix
#import math
import os
import shutil

SHOW_EXPORT_DUMPS = False
SHOW_EXPORT_TRACE = False
SHOW_EXPORT_TRACE_VX = False
DEFAULT_KEEP_XML = True

# default blender version of script
blender_version = 259

class VertexInfo(object):
    def __init__(self, px,py,pz, nx,ny,nz, u,v,boneWeights):        
        self.px = px
        self.py = py
        self.pz = pz
        self.nx = nx
        self.ny = ny
        self.nz = nz        
        self.u = u
        self.v = v
        self.boneWeights = boneWeights        
        

    '''does not compare ogre_vidx (and position at the moment) [ no need to compare position ]'''
    def __eq__(self, o): 
        if self.nx != o.nx or self.ny != o.ny or self.nz != o.nz: return False 
        elif self.px != o.px or self.py != o.py or self.pz != o.pz: return False
        elif self.u != o.u or self.v != o.v: return False
        return True
    
#    def __hash__(self):
#        return hash(self.px) ^ hash(self.py) ^ hash(self.pz) ^ hash(self.nx) ^ hash(self.ny) ^ hash(self.nz)
#        
########################################

class Bone(object):
    ''' EditBone
    ['__doc__', '__module__', '__slots__', 'align_orientation', 'align_roll', 'bbone_in', 'bbone_out', 'bbone_segments', 'bl_rna', 'envelope_distance', 'envelope_weight', 'head', 'head_radius', 'hide', 'hide_select', 'layers', 'lock', 'matrix', 'name', 'parent', 'rna_type', 'roll', 'select', 'select_head', 'select_tail', 'show_wire', 'tail', 'tail_radius', 'transform', 'use_connect', 'use_cyclic_offset', 'use_deform', 'use_envelope_multiply', 'use_inherit_rotation', 'use_inherit_scale', 'use_local_location']
    '''

    def __init__(self, matrix, pbone, id, skeleton):
        self.fixUpAxis = True
        self.flipMat = Matrix(((1,0,0,0),(0,0,1,0),(0,1,0,0),(0,0,0,1)))
#        if OPTIONS['SWAP_AXIS'] == 'xyz':
#            self.fixUpAxis = False
#
#        else:
#            self.fixUpAxis = True
#            if OPTIONS['SWAP_AXIS'] == '-xzy':      # Tundra1
#                self.flipMat = mathutils.Matrix(((-1,0,0,0),(0,0,1,0),(0,1,0,0),(0,0,0,1)))
#            elif OPTIONS['SWAP_AXIS'] == 'xz-y':    # Tundra2
#                self.flipMat = mathutils.Matrix(((1,0,0,0),(0,0,1,0),(0,1,0,0),(0,0,0,1)))
#            else:
#                print( 'ERROR: axis swap mode not supported with armature animation' )
#                assert 0

        self.skeleton = skeleton
        self.name = pbone.name
        self.id = id
        #self.matrix = self.flipMat * matrix
        self.matrix = matrix
        self.bone = pbone        # safe to hold pointer to pose bone, not edit bone!
        if not pbone.bone.use_deform: print('warning: bone <%s> is non-deformabled, this is inefficient!' %self.name)
        #TODO test#if pbone.bone.use_inherit_scale: print('warning: bone <%s> is using inherit scaling, Ogre has no support for this' %self.name)
        self.parent = pbone.parent
        self.children = []

    def update(self):        # called on frame update
        pose =  self.bone.matrix.copy()
        #pose = self.bone.matrix * self.skeleton.object_space_transformation
        #pose =  self.skeleton.object_space_transformation * self.bone.matrix
        self._inverse_total_trans_pose = pose.inverted()

        # calculate difference to parent bone
        if self.parent:
            pose = self.parent._inverse_total_trans_pose* pose
        elif self.fixUpAxis:
            #pose = mathutils.Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1))) * pose   # Requiered for Blender SVN > 2.56
            pose = self.flipMat * pose
        else:
            pass

        # get transformation values
        # translation relative to parent coordinate system orientation
        # and as difference to rest pose translation
        #blender2.49#translation -= self.ogreRestPose.translationPart()
        self.pose_location =  pose.to_translation()  -  self.ogre_rest_matrix.to_translation()

        # rotation (and scale) relative to local coordiante system
        # calculate difference to rest pose
        #blender2.49#poseTransformation *= self.inverseOgreRestPose
        #pose = pose * self.inverse_ogre_rest_matrix        # this was wrong, fixed Dec3rd
        pose = self.inverse_ogre_rest_matrix * pose
        self.pose_rotation = pose.to_quaternion()
        self.pose_scale = pose.to_scale()

        #self.pose_location = self.bone.location.copy()
        #self.pose_rotation = self.bone.rotation_quaternion.copy()
        for child in self.children: child.update()


    def rebuild_tree( self ):        # called first on all bones
        if self.parent:
            self.parent = self.skeleton.get_bone( self.parent.name )
            self.parent.children.append( self )

    def compute_rest( self ):    # called after rebuild_tree, recursive roots to leaves
        if self.parent:
            inverseParentMatrix = self.parent.inverse_total_trans
        elif self.fixUpAxis:
            inverseParentMatrix = self.flipMat
        else:
            inverseParentMatrix = Matrix(((1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)))

        # bone matrix relative to armature object
        self.ogre_rest_matrix = self.matrix.copy()
        # relative to mesh object origin
        #self.ogre_rest_matrix *= self.skeleton.object_space_transformation        # 2.49 style

        ##not correct - june18##self.ogre_rest_matrix = self.skeleton.object_space_transformation * self.ogre_rest_matrix
        #self.ogre_rest_matrix -= self.skeleton.object_space_transformation


        # store total inverse transformation
        self.inverse_total_trans = self.ogre_rest_matrix.inverted()

        # relative to OGRE parent bone origin
        #self.ogre_rest_matrix *= inverseParentMatrix        # 2.49 style
        self.ogre_rest_matrix = inverseParentMatrix * self.ogre_rest_matrix
        self.inverse_ogre_rest_matrix = self.ogre_rest_matrix.inverted()

        ## recursion ##
        for child in self.children:
            child.compute_rest()

class Skeleton(object):
    def get_bone( self, name ):
        for b in self.bones:
            if b.name == name: return b

    def __init__(self, ob ):
        self.object = ob
        self.bones = []
        mats = {}
        self.arm = arm = ob.find_armature()
        arm.hide = False
        self._restore_layers = list(arm.layers)
        #arm.layers = [True]*20      # can not have anything hidden - REQUIRED?
        prev = bpy.context.scene.objects.active
        bpy.context.scene.objects.active = arm        # arm needs to be in edit mode to get to .edit_bones
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        for bone in arm.data.edit_bones: mats[ bone.name ] = bone.matrix.copy()
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        #bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bpy.context.scene.objects.active = prev
        
        # sorting the bones here according to name
        sortedBoneNames = []
        for pbone in arm.pose.bones:
            sortedBoneNames.append(pbone.name)
        
        sortedBoneNames.sort(key=None, reverse=False)
        
        for i, sbone in enumerate(sortedBoneNames):
            mybone = Bone( mats[sbone] ,arm.pose.bones[sbone], i, self )
            self.bones.append( mybone )

#        for pbone in arm.pose.bones:
#            mybone = Bone( mats[pbone.name] ,pbone, self )
#            self.bones.append( mybone )

#        if arm.name not in Report.armatures: Report.armatures.append( arm.name )

        # additional transformation for root bones:
        # from armature object space into mesh object space, i.e.,
        # (x,y,z,w)*AO*MO^(-1)
        self.object_space_transformation = arm.matrix_local * ob.matrix_local.inverted()

        ## setup bones for Ogre format ##
        for b in self.bones: b.rebuild_tree()
        ## walk bones, convert them ##
        self.roots = []
        for b in self.bones:
            if not b.parent:
                b.compute_rest()
                self.roots.append( b )

    def to_xml( self ):
        from xml.dom.minidom import Document
        
        _fps = float( bpy.context.scene.render.fps )

        doc = Document()
        root = doc.createElement('skeleton'); doc.appendChild( root )
        bones = doc.createElement('bones'); root.appendChild( bones )
        bh = doc.createElement('bonehierarchy'); root.appendChild( bh )
        for i,bone in enumerate(self.bones):
            b = doc.createElement('bone')
            b.setAttribute('name', bone.name)
            b.setAttribute('id', str(bone.id) )
            bones.appendChild( b )
            mat = bone.ogre_rest_matrix.copy()
            if bone.parent:
                bp = doc.createElement('boneparent')
                bp.setAttribute('bone', bone.name)
                bp.setAttribute('parent', bone.parent.name)
                bh.appendChild( bp )

            pos = doc.createElement( 'position' ); b.appendChild( pos )
            x,y,z = mat.to_translation()
            pos.setAttribute('x', '%6f' %x )
            pos.setAttribute('y', '%6f' %y )
            pos.setAttribute('z', '%6f' %z )
            rot =  doc.createElement( 'rotation' )        # note "rotation", not "rotate"
            b.appendChild( rot )

            q = mat.to_quaternion()
            rot.setAttribute('angle', '%6f' %q.angle )
            axis = doc.createElement('axis'); rot.appendChild( axis )
            x,y,z = q.axis
            axis.setAttribute('x', '%6f' %x )
            axis.setAttribute('y', '%6f' %y )
            axis.setAttribute('z', '%6f' %z )

            ## Ogre bones do not have initial scaling? ##
            ## NOTE: Ogre bones by default do not pass down their scaling in animation,
            ## so in blender all bones are like 'do-not-inherit-scaling'
            if 0:
                scale = doc.createElement('scale'); b.appendChild( scale )
                x,y,z = swap( mat.to_scale() )
                scale.setAttribute('x', str(x))
                scale.setAttribute('y', str(y))
                scale.setAttribute('z', str(z))

#        arm = self.arm
#        if not arm.animation_data or (arm.animation_data and not arm.animation_data.nla_tracks):  # assume animated via constraints and use blender timeline.
#            anims = doc.createElement('animations'); root.appendChild( anims )
#            anim = doc.createElement('animation'); anims.appendChild( anim )
#            tracks = doc.createElement('tracks'); anim.appendChild( tracks )
#            anim.setAttribute('name', 'my_animation')
#            start = bpy.context.scene.frame_start; end = bpy.context.scene.frame_end
#            anim.setAttribute('length', str( (end-start)/_fps ) )
#
#            _keyframes = {}
#            _bonenames_ = []
#            for bone in arm.pose.bones:
#                _bonenames_.append( bone.name )
#                track = doc.createElement('track')
#                track.setAttribute('bone', bone.name)
#                tracks.appendChild( track )
#                keyframes = doc.createElement('keyframes')
#                track.appendChild( keyframes )
#                _keyframes[ bone.name ] = keyframes
#
#            for frame in range( int(start), int(end), bpy.context.scene.frame_step):
#                bpy.context.scene.frame_set(frame)
#                for bone in self.roots: bone.update()
#                print('\t\t Frame:', frame)
#                for bonename in _bonenames_:
#                    bone = self.get_bone( bonename )
#                    _loc = bone.pose_location
#                    _rot = bone.pose_rotation
#                    _scl = bone.pose_scale
#
#                    keyframe = doc.createElement('keyframe')
#                    keyframe.setAttribute('time', str((frame-start)/_fps))
#                    _keyframes[ bonename ].appendChild( keyframe )
#                    trans = doc.createElement('translate')
#                    keyframe.appendChild( trans )
#                    x,y,z = _loc
#                    trans.setAttribute('x', '%6f' %x)
#                    trans.setAttribute('y', '%6f' %y)
#                    trans.setAttribute('z', '%6f' %z)
#
#                    rot =  doc.createElement( 'rotate' )
#                    keyframe.appendChild( rot )
#                    q = _rot
#                    rot.setAttribute('angle', '%6f' %q.angle )
#                    axis = doc.createElement('axis'); rot.appendChild( axis )
#                    x,y,z = q.axis
#                    axis.setAttribute('x', '%6f' %x )
#                    axis.setAttribute('y', '%6f' %y )
#                    axis.setAttribute('z', '%6f' %z )
#
#                    scale = doc.createElement('scale')
#                    keyframe.appendChild( scale )
#                    x,y,z = _scl
#                    scale.setAttribute('x', '%6f' %x)
#                    scale.setAttribute('y', '%6f' %y)
#                    scale.setAttribute('z', '%6f' %z)
#
#
#        elif arm.animation_data:
#            anims = doc.createElement('animations'); root.appendChild( anims )
##            if not len( arm.animation_data.nla_tracks ):
##                Report.warnings.append('you must assign an NLA strip to armature (%s) that defines the start and end frames' %arm.name)
#
#            for nla in arm.animation_data.nla_tracks:        # NLA required, lone actions not supported
#                if not len(nla.strips): print( 'skipping empty NLA track: %s' %nla.name ); continue
#                for strip in nla.strips:
#                    anim = doc.createElement('animation'); anims.appendChild( anim )
#                    tracks = doc.createElement('tracks'); anim.appendChild( tracks )
##                    Report.armature_animations.append( '%s : %s [start frame=%s  end frame=%s]' %(arm.name, nla.name, strip.frame_start, strip.frame_end) )
#
#                    #anim.setAttribute('animation_group', nla.name)        # this is extended xml format not useful?
#                    anim.setAttribute('name', strip.name)                       # USE the action's name
#                    anim.setAttribute('length', str( (strip.frame_end-strip.frame_start)/_fps ) )
#                    ## using the fcurves directly is useless, because:
#                    ## we need to support constraints and the interpolation between keys
#                    ## is Ogre smart enough that if a track only has a set of bones, then blend animation with current animation?
#                    ## the exporter will not be smart enough to know which bones are active for a given track...
#                    ## can hijack blender NLA, user sets a single keyframe for only selected bones, and keys last frame
#                    stripbones = []
##                    if OPTIONS['EX_ONLY_ANIMATED_BONES']:
#                    if True:
#                        for group in strip.action.groups:        # check if the user has keyed only some of the bones (for anim blending)
#                            if group.name in arm.pose.bones: stripbones.append( group.name )
#
#                        if not stripbones:                                    # otherwise we use all bones
#                            stripbones = [ bone.name for bone in arm.pose.bones ]
#                    else:
#                        stripbones = [ bone.name for bone in arm.pose.bones ]
#
#                    print('NLA-strip:',  nla.name)
#                    _keyframes = {}
#                    for bonename in stripbones:
#                        track = doc.createElement('track')
#                        track.setAttribute('bone', bonename)
#                        tracks.appendChild( track )
#                        keyframes = doc.createElement('keyframes')
#                        track.appendChild( keyframes )
#                        _keyframes[ bonename ] = keyframes
#                        print('\t Bone:', bonename)
#
#                    for frame in range( int(strip.frame_start), int(strip.frame_end), bpy.context.scene.frame_step):
#                        bpy.context.scene.frame_set(frame)
#                        for bone in self.roots: bone.update()
#                        print('\t\t Frame:', frame)
#                        for bonename in stripbones:
#                            bone = self.get_bone( bonename )
#                            _loc = bone.pose_location
#                            _rot = bone.pose_rotation
#                            _scl = bone.pose_scale
#
#                            keyframe = doc.createElement('keyframe')
#                            keyframe.setAttribute('time', str((frame-strip.frame_start)/_fps))
#                            _keyframes[ bonename ].appendChild( keyframe )
#                            trans = doc.createElement('translate')
#                            keyframe.appendChild( trans )
#                            x,y,z = _loc
#                            trans.setAttribute('x', '%6f' %x)
#                            trans.setAttribute('y', '%6f' %y)
#                            trans.setAttribute('z', '%6f' %z)
#
#                            rot =  doc.createElement( 'rotate' )
#                            keyframe.appendChild( rot )
#                            q = _rot
#                            rot.setAttribute('angle', '%6f' %q.angle )
#                            axis = doc.createElement('axis'); rot.appendChild( axis )
#                            x,y,z = q.axis
#                            axis.setAttribute('x', '%6f' %x )
#                            axis.setAttribute('y', '%6f' %y )
#                            axis.setAttribute('z', '%6f' %z )
#
#                            scale = doc.createElement('scale')
#                            keyframe.appendChild( scale )
#                            x,y,z = _scl
#                            scale.setAttribute('x', '%6f' %x)
#                            scale.setAttribute('y', '%6f' %y)
#                            scale.setAttribute('z', '%6f' %z)

        return doc.toprettyxml(indent="    ")

 

#########################################
def fileExist(filepath):
    try:
        filein = open(filepath)
        filein.close()
        return True
    except:
        print ("No file: ", filepath)
        return False
        
def toFmtStr(number):
    #return str("%0.7f" % number)
    return str(round(number, 7))

def indent(indent):
    """Indentation.
    
       @param indent Level of indentation.
       @return String.
    """
    return "        "*indent 

def xSaveGeometry(geometry, xDoc, xMesh, isShared):
    # I guess positions (vertices) must be there always
    vertices = geometry['positions']
    
    if isShared:
        geometryType = "sharedgeometry"
    else:
        geometryType = "geometry"
    
    isNormals = False
    if 'normals' in geometry:    
        isNormals = True
        normals = geometry['normals']
        
    isTexCoordsSets = False
    texCoordSets = geometry['texcoordsets']
    if texCoordSets>0 and 'uvsets' in geometry:
        isTexCoordsSets = True
        uvSets = geometry['uvsets']
    
    xGeometry = xDoc.createElement(geometryType)
    xGeometry.setAttribute("vertexcount", str(len(vertices)))
    xMesh.appendChild(xGeometry)
    
    xVertexBuffer = xDoc.createElement("vertexbuffer")
    xVertexBuffer.setAttribute("positions", "true")
    if isNormals:
        xVertexBuffer.setAttribute("normals", "true")
    if isTexCoordsSets:
        xVertexBuffer.setAttribute("texture_coord_dimensions_0", "2")
        xVertexBuffer.setAttribute("texture_coords", str(texCoordSets))
    xGeometry.appendChild(xVertexBuffer)
    
    for i, vx in enumerate(vertices):
        xVertex = xDoc.createElement("vertex")
        xVertexBuffer.appendChild(xVertex)
        xPosition = xDoc.createElement("position")
        xPosition.setAttribute("x", toFmtStr(vx[0]))
        xPosition.setAttribute("y", toFmtStr(vx[2]))
        xPosition.setAttribute("z", toFmtStr(-vx[1]))
        xVertex.appendChild(xPosition)
        if isNormals:
            xNormal = xDoc.createElement("normal")
            xNormal.setAttribute("x", toFmtStr(normals[i][0]))
            xNormal.setAttribute("y", toFmtStr(normals[i][2]))
            xNormal.setAttribute("z", toFmtStr(-normals[i][1]))
            xVertex.appendChild(xNormal)
        if isTexCoordsSets:
            xUVSet = xDoc.createElement("texcoord")
            xUVSet.setAttribute("u", toFmtStr(uvSets[i][0][0])) # take only 1st set for now
            xUVSet.setAttribute("v", toFmtStr(1.0 - uvSets[i][0][1]))            
            xVertex.appendChild(xUVSet)
            
def xSaveSubMeshes(meshData, xDoc, xMesh, hasSharedGeometry):
            
    xSubMeshes = xDoc.createElement("submeshes")
    xMesh.appendChild(xSubMeshes)
    
    for submesh in meshData['submeshes']:
                
        numVerts = len(submesh['geometry']['positions'])
        
        xSubMesh = xDoc.createElement("submesh")
        xSubMesh.setAttribute("material", submesh['material'])
        if hasSharedGeometry:
            xSubMesh.setAttribute("usesharedvertices", "true")
        else:
            xSubMesh.setAttribute("usesharedvertices", "false")
        xSubMesh.setAttribute("use32bitindexes", str(bool(numVerts > 65535)))   
        xSubMesh.setAttribute("operationtype", "triangle_list")  
        xSubMeshes.appendChild(xSubMesh)
        # write all faces
        if 'faces' in submesh:
            faces = submesh['faces']
            xFaces = xDoc.createElement("faces")
            xFaces.setAttribute("count", str(len(faces)))
            xSubMesh.appendChild(xFaces)
            for face in faces:
                xFace = xDoc.createElement("face")
                xFace.setAttribute("v1", str(face[0]))
                xFace.setAttribute("v2", str(face[1]))
                xFace.setAttribute("v3", str(face[2]))
                xFaces.appendChild(xFace)
        # if there is geometry per sub mesh
        if 'geometry' in submesh:
            geometry = submesh['geometry']
            xSaveGeometry(geometry, xDoc, xSubMesh, hasSharedGeometry)
        # boneassignments
        if 'skeleton' in meshData:
            skelMeshData = meshData['skeleton']
            xBoneAssignments = xDoc.createElement("boneassignments")
            #print(submesh['geometry']['boneassignments'][0])
            for vxIdx, vxBoneAsg in enumerate(submesh['geometry']['boneassignments']):
                #print(submesh['geometry']['boneassignments'][vxIdx])
                #print(vxBoneAsg)
                for boneAndWeight in vxBoneAsg:
                    #print(boneAndWeight)
                    boneName = boneAndWeight[0]
                    boneWeight = boneAndWeight[1]
                    xVxBoneassignment = xDoc.createElement("vertexboneassignment")
                    xVxBoneassignment.setAttribute("vertexindex", str(vxIdx))
                    #print(boneName)
                    boneNameToId = skelMeshData['boneIDs']
                    #print(skelMeshData['boneIDs'])
                    #print(boneNameToId[boneName])
                    xVxBoneassignment.setAttribute("boneindex", str(skelMeshData['boneIDs'][boneName]))
                    xVxBoneassignment.setAttribute("weight", '%6f' % boneWeight)
                    xBoneAssignments.appendChild(xVxBoneassignment)
            xSubMesh.appendChild(xBoneAssignments)
            
def xSaveSkeletonData(blenderMeshData, filepath):
    if 'skeleton' in blenderMeshData:
        skelData = blenderMeshData['skeleton']
        skel = skelData['instance']
        data = skel.to_xml()
        name = skelData['name']
        #xmlfile = os.path.join(filepath, '%s.skeleton.xml' %name )
        nameOnly = os.path.splitext(filepath)[0] # removing .mesh
        xmlfile = nameOnly + ".skeleton.xml"
        f = open( xmlfile, 'wb' )
        f.write( bytes(data,'utf-8') )
        f.close() 
    
    
def xSaveMeshData(meshData, filepath, export_and_link_skeleton):    
    from xml.dom.minidom import Document
    
    hasSharedGeometry = False
    if 'sharedgeometry' in meshData:
        hasSharedGeometry = True
        
    # Create the minidom document
    xDoc = Document()
    
    xMesh = xDoc.createElement("mesh")
    xDoc.appendChild(xMesh)
    
    if hasSharedGeometry:
        geometry = meshData['sharedgeometry']
        xSaveGeometry(geometry, xDoc, xMesh, hasSharedGeometry)
    
    xSaveSubMeshes(meshData, xDoc, xMesh, hasSharedGeometry)
    
    #skeleton link only
    if 'skeleton' in meshData:
        xSkeletonlink = xDoc.createElement("skeletonlink")
        # default skeleton
        linkSkeletonName = meshData['skeleton']['name']
        if(export_and_link_skeleton):    
            nameDotMeshDotXml = os.path.split(filepath)[1].lower()
            nameDotMesh = os.path.splitext(nameDotMeshDotXml)[0]
            linkSkeletonName = os.path.splitext(nameDotMesh)[0] 
        #xSkeletonlink.setAttribute("name", meshData['skeleton']['name']+".skeleton")
        xSkeletonlink.setAttribute("name", linkSkeletonName+".skeleton")
        xMesh.appendChild(xSkeletonlink)
   
    # Print our newly created XML    
    fileWr = open(filepath + ".xml", 'w') 
    fileWr.write(xDoc.toprettyxml(indent="    ")) # 4 spaces
    #doc.writexml(fileWr, "  ")
    fileWr.close() 
    
def xSaveMaterialData(filepath, meshData, overwriteMaterialFlag, copyTextures):
    
    #print("filepath: %s" % filepath)
    matFile = os.path.splitext(filepath)[0] # removing .mesh
    #print("matFile: %s" % matFile)
    #matFile = os.path.splitext(matFile)[0] + ".material"
    matFile = matFile + ".material"
    print("material file: %s" % matFile)
    
    isMaterial = True
    try:
        filein = open(matFile)
        filein.close()
    except:
        #print ("Material: File", matFile, "not found!")
        isMaterial = False
    
    allMatData = meshData['materials']
    # if is no material file, or we are forced to overwrite it, write the material file
    if isMaterial==False or overwriteMaterialFlag==True:
        if 'materials' not in meshData:
            return
        if len(meshData['materials'])<=0:
            return
        # write material        
        fileWr = open(matFile, 'w')        
        for matName, matInfo in allMatData.items():
            fileWr.write("material %s\n" % matName)
            fileWr.write("{\n")
            fileWr.write(indent(1) + "technique\n" + indent(1) + "{\n")
            fileWr.write(indent(2) + "pass\n" + indent(2) + "{\n")
            
            # write material content here
            fileWr.write(indent(3) + "ambient %f %f %f\n" % (matInfo['ambient'][0], matInfo['ambient'][1], matInfo['ambient'][2]))
            fileWr.write(indent(3) + "diffuse %f %f %f\n" % (matInfo['diffuse'][0], matInfo['diffuse'][1], matInfo['diffuse'][2]))
            fileWr.write(indent(3) + "specular %f %f %f 0\n" % (matInfo['specular'][0], matInfo['specular'][1], matInfo['specular'][2]))
            fileWr.write(indent(3) + "emissive %f %f %f\n" % (matInfo['emissive'][0], matInfo['emissive'][1], matInfo['emissive'][2]))
            
            if 'texture' in matInfo:
                fileWr.write(indent(3) + "texture_unit\n" + indent(3) + "{\n")
                fileWr.write(indent(4) + "texture %s\n" % matInfo['texture'])
                fileWr.write(indent(3) + "}\n") # texture unit
            
            fileWr.write(indent(2) + "}\n") # pass
            fileWr.write(indent(1) + "}\n") # technique
            fileWr.write("}\n")
        
        fileWr.close()
    
    #print("CopyTextures: %s" % copyTextures)
    if copyTextures:
        #print("CopyTextures: true")
        #try to copy material textures to destination
        for matName, matInfo in allMatData.items():
            if 'texture' in matInfo:
                if 'texture_path' in matInfo:
                    srcTextureFile = matInfo['texture_path']
                    #print("Source\"%s\"" % srcTextureFile)
                    #print("Path exists \"%s\"" % os.path.exists(srcTextureFile))
                    baseDirName = os.path.dirname(bpy.data.filepath)
                    if (srcTextureFile[0:2] == "//"):
                        print("Converting relative image name \"%s\"" % srcTextureFile)
                        srcTextureFile = os.path.join(baseDirName, srcTextureFile[2:])
                    if fileExist(srcTextureFile):
                        # copy texture to dir
                        print("Copying texture \"%s\"" % srcTextureFile)
                        try:
                            print(" to \"%s\"" % os.path.dirname(matFile))
                            shutil.copy(srcTextureFile, os.path.dirname(matFile))
                        except:
                            print("Error copying \"%s\"" % srcTextureFile)
                    else:
                        print("Can't copy texture \"%s\" because file does not exists!" % srcTextureFile)

    

def getVertexIndex(vertexInfo, vertexList):
    
    for vIdx, vert in enumerate(vertexList):
        if vertexInfo == vert:
            return vIdx
    
    #not present in list:
    vertexList.append(vertexInfo)
    return len(vertexList)-1

def bCollectMeshData(meshData, selectedObjects, applyModifiers):
    
    subMeshesData = []
    for ob in selectedObjects:             
        subMeshData = {}        
        #ob = bpy.types.Object ##
        materialName = ob.name
        if len(ob.data.materials)>0:
            materialName = ob.data.materials[0].name       
        #mesh = bpy.types.Mesh ##
        if applyModifiers:        
            mesh = ob.to_mesh(bpy.context.scene, True, 'PREVIEW')
        else:
            mesh = ob.data     
        
        # blender 2.62 <-> 2.63 compatibility
        if(blender_version<=262):
            meshFaces = mesh.faces
            meshUV_textures = mesh.uv_textures
            meshVertex_colors = mesh.vertex_colors
        elif(blender_version>262): 
            mesh.update(calc_tessface=True)            
            meshFaces = mesh.tessfaces 
            meshUV_textures = mesh.tessface_uv_textures 
            meshVertex_colors = mesh.tessface_vertex_colors
        
        # first try to collect UV data
        uvData = []
        hasUVData = False
        if meshUV_textures.active:
            hasUVData = True
            #uvLayerTofaceUVdata = {}
            for layer in meshUV_textures:
                faceIdxToUVdata = {}
                for fidx, uvface in enumerate(layer.data):               
                    faceIdxToUVdata[fidx] = uvface.uv
                #uvData[layer]=faceIdxToUVdata
                uvData.append(faceIdxToUVdata)
                      
        vertexList = []        
        newFaces = []
                
        for fidx, face in enumerate(meshFaces):
            tris = []
            tris.append( (face.vertices[0], face.vertices[1], face.vertices[2]) )
            if(len(face.vertices)>=4):
                tris.append( (face.vertices[0], face.vertices[2], face.vertices[3]) ) 
            if SHOW_EXPORT_TRACE_VX:
                    print("_face: "+ str(fidx) + " indices [" + str(list(face.vertices))+ "]")
            for tri in tris:
                newFaceVx = []                        
                for vertex in tri:
                    vxOb = mesh.vertices[vertex]
                    u = 0
                    v = 0
                    if hasUVData:
                        uv = uvData[0][fidx][ list(tri).index(vertex) ] #take 1st layer only
                        u = uv[0]
                        v = uv[1]
                    px = vxOb.co[0]
                    py = vxOb.co[1]
                    pz = vxOb.co[2]
                    nx = vxOb.normal[0] 
                    ny = vxOb.normal[1]
                    nz = vxOb.normal[2]
                    #vertex groups
                    boneWeights = {}
                    for vxGroup in vxOb.groups:
                        if vxGroup.weight > 0.01:
                            vg = ob.vertex_groups[ vxGroup.group ]
                            boneWeights[vg.name]=vxGroup.weight
                        
                    if SHOW_EXPORT_TRACE_VX:
                        print("_vx: "+ str(vertex)+ " co: "+ str([px,py,pz]) +
                              " no: " + str([nx,ny,nz]) +
                              " uv: " + str([u,v]))
                    vert = VertexInfo(px,py,pz,nx,ny,nz,u,v,boneWeights)
                    newVxIdx = getVertexIndex(vert, vertexList)
                    newFaceVx.append(newVxIdx)
                    if SHOW_EXPORT_TRACE_VX:
                        print("Nvx: "+ str(newVxIdx)+ " co: "+ str([px,py,pz]) +
                              " no: " + str([nx,ny,nz]) +
                              " uv: " + str([u,v]))
                newFaces.append(newFaceVx)
                if SHOW_EXPORT_TRACE_VX:
                    print("Nface: "+ str(fidx) + " indices [" + str(list(newFaceVx))+ "]")
                  
        # geometry
        geometry = {}
        #vertices = bpy.types.MeshVertices
        #vertices = mesh.vertices
        faces = [] 
        normals = []
        positions = []
        uvTex = []
        #vertex groups of object
        boneAssignments = []
        
        faces = newFaces
        
        for vxInfo in vertexList:
            positions.append([vxInfo.px, vxInfo.py, vxInfo.pz])
            normals.append([vxInfo.nx, vxInfo.ny, vxInfo.nz])
            uvTex.append([[vxInfo.u, vxInfo.v]])
            
            boneWeights = []
            for boneW in vxInfo.boneWeights.keys():
                boneWeights.append([boneW, vxInfo.boneWeights[boneW]])
            boneAssignments.append(boneWeights)            
            #print(boneWeights)
        
        if SHOW_EXPORT_TRACE_VX:
            print("uvTex:")
            print(uvTex)
            print("boneAssignments:")
            print(boneAssignments)
        
        geometry['positions'] = positions
        geometry['normals'] = normals
        geometry['texcoordsets'] = len(mesh.uv_textures)
        if SHOW_EXPORT_TRACE:
            print("texcoordsets: " + str(len(mesh.uv_textures)))
        if hasUVData:
            geometry['uvsets'] = uvTex
                
        #need bone name to bone ID dict
        geometry['boneassignments'] = boneAssignments
        
        subMeshData['material'] = materialName
        subMeshData['faces'] = faces
        subMeshData['geometry'] = geometry
        subMeshesData.append(subMeshData)
        
        # if mesh was newly created with modifiers, remove the mesh
        if applyModifiers:
            bpy.data.meshes.remove(mesh)
        
    meshData['submeshes']=subMeshesData
    
    return meshData

def bCollectSkeletonData(blenderMeshData, selectedObjects):
    
    #need to collect bones 
    if SHOW_EXPORT_TRACE:       
        print("bpy.data.armatures = %s" % bpy.data.armatures)
        
    # TODO, for now just take armature of first selected object
    #if (len(bpy.data.armatures)>=0):
    if selectedObjects[0].find_armature():
        # creates and parses blender skeleton
        skelInstance = Skeleton( selectedObjects[0] )
        
        #amt = bpy.data.armatures[bpy.data.armatures.keys()[0]]
        amt = selectedObjects[0].find_armature()
        if SHOW_EXPORT_TRACE:
            print("amt = %s" % amt)
        armatureName = amt.name 
        skeleton = {}
        skeletonNameToID = {}
        blenderMeshData['skeleton'] = skeleton
        skeleton['instance'] = skelInstance
        skeleton['name'] = armatureName
        skeleton['boneIDs'] = skeletonNameToID
        
        #skeleton name to ID:        
        for skBone in skelInstance.bones:
            skeletonNameToID[skBone.name] = str(skBone.id)
            if SHOW_EXPORT_TRACE:           
                print("bone=%s, id=%s" % (skBone.name,skBone.id))
        
    
def bCollectMaterialData(blenderMeshData, selectedObjects):
    
    allMaterials = {}
    blenderMeshData['materials'] = allMaterials
    
    for ob in selectedObjects:   
        if ob.type == 'MESH' and len(ob.data.materials)>0:
            for mat in ob.data.materials:
                #mat = bpy.types.Material ##
                if mat.name not in allMaterials:
                    matInfo = {}
                    allMaterials[mat.name]=matInfo                    
                    # ambient
                    matInfo['ambient']=[ mat.ambient, mat.ambient, mat.ambient]
                    # diffuse
                    matInfo['diffuse']=[mat.diffuse_color[0],mat.diffuse_color[1],mat.diffuse_color[2]]
                    # specular
                    matInfo['specular']=[mat.specular_color[0],mat.specular_color[1],mat.specular_color[2]]
                    # emissive
                    matInfo['emissive']=[mat.emit,mat.emit,mat.emit]                    
                    # texture
                    if len(mat.texture_slots)>0:
                        if mat.texture_slots[0].texture:
                            if mat.texture_slots[0].texture.type == 'IMAGE':
                                #print('\t\t XXXX:', mat.texture_slots[0].texture.type)
                                matInfo['texture'] = mat.texture_slots[0].texture.image.name
                                matInfo['texture_path'] = mat.texture_slots[0].texture.image.filepath
    
    
def SaveMesh(filepath, selectedObjects, ogreXMLconverter, applyModifiers,
              overrideMaterialFlag, copyTextures, export_and_link_skeleton, keep_xml):
    
    blenderMeshData = {}
    
    #skeleton
    bCollectSkeletonData(blenderMeshData, selectedObjects) 
    #mesh
    bCollectMeshData(blenderMeshData, selectedObjects, applyModifiers)
    #materials
    bCollectMaterialData(blenderMeshData, selectedObjects)
    
    if SHOW_EXPORT_TRACE:
        print(blenderMeshData['materials'])
    
    if SHOW_EXPORT_DUMPS:
        dumpFile = filepath + ".EDump"    
        fileWr = open(dumpFile, 'w')
        fileWr.write(str(blenderMeshData))    
        fileWr.close() 
    
    #selObj = selectedObjects[0]
    
    if export_and_link_skeleton:
        xSaveSkeletonData(blenderMeshData, filepath)  
    
    xSaveMeshData(blenderMeshData, filepath, export_and_link_skeleton)
    
    xSaveMaterialData(filepath, blenderMeshData, overrideMaterialFlag, copyTextures)
    
    XMLtoOGREConvert(blenderMeshData, filepath, ogreXMLconverter,
                      export_and_link_skeleton, keep_xml)
    
def XMLtoOGREConvert(blenderMeshData, filepath, ogreXMLconverter,
                     export_and_link_skeleton, keep_xml):
        
    if(ogreXMLconverter is not None):
        # for mesh
        # use Ogre XML converter  xml -> binary mesh
        xmlFilepath = filepath + ".xml"
        os.system('%s "%s"' % (ogreXMLconverter, xmlFilepath))        
        # remove XML file
        if keep_xml is False:
            os.unlink("%s" % xmlFilepath)  
        if 'skeleton' in blenderMeshData and export_and_link_skeleton:
            # for skeleton
            skelFile = os.path.splitext(filepath)[0] # removing .mesh
            xmlFilepath = skelFile + ".skeleton.xml"
            print(xmlFilepath)
            os.system('%s "%s"' % (ogreXMLconverter, xmlFilepath))        
            # remove XML file
            if keep_xml is False:
                os.unlink("%s" % xmlFilepath) 

def save(operator, context, filepath,       
         ogreXMLconverter=None,
         keep_xml=DEFAULT_KEEP_XML,
         apply_transform=True,
         apply_modifiers=True,
         overwrite_material=False,
         copy_textures=False,
         export_and_link_skeleton=False,):
            
    global blender_version
    
    blender_version = bpy.app.version[0]*100 + bpy.app.version[1]
    
    # just check if there is extension - .mesh
    if '.mesh' not in filepath.lower():
        filepath = filepath + ".mesh"
    
    print("saving...")
    print(str(filepath))
    
    # go to the object mode
    for ob in bpy.data.objects: 
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # apply transform   
    if apply_transform:        
        bpy.ops.object.transform_apply(rotation=True, scale=True)
        
    # get mesh data from selected objects
    selectedObjects = []
    scn = bpy.context.scene
    for ob in scn.objects:
        if ob.select==True and ob.type!='ARMATURE':            
            selectedObjects.append(ob)
                
    if len(selectedObjects)==0:
        print("No objects selected for export.")
        return ('CANCELLED')
        
    SaveMesh(filepath, selectedObjects, ogreXMLconverter, apply_modifiers,
              overwrite_material, copy_textures, export_and_link_skeleton, keep_xml)
    
    
    print("done.")
    
    return {'FINISHED'}

