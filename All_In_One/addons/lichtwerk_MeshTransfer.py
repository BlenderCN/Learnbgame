# --------------------------------------------------------------------------
# Lichtwerk Scripts (author Philipp Oeser)
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------

'''
# ----------------------------------------
# Addon
# ----------------------------------------
'''
bl_info = {
    "name": "LichtwerkMeshTransfer",
    "author": "Philipp Oeser",
    "version": (0, 3),
    "blender": (2, 6, 0),
    "api": 42672,
    "location": "Object data properties > MeshTransfer (panel)",
    "description": "transfers weights/colors/positions from one mesh to the other (with arbitrary topology)",
    "warning": "beta",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

'''
# ----------------------------------------
# Imports
# ----------------------------------------
'''
import bpy
import mathutils
import functools

import sys, os
from operator import attrgetter, itemgetter

import time

'''
# ----------------------------------------
# Helper functions
# ----------------------------------------
'''

def licNormListSumTo(L, sumTo=1):
    '''
    normalize values of a list to make it sum = sumTo
    '''
    sum = functools.reduce(lambda x,y:x+y, L)
    return [ x/(sum*1.0)*sumTo for x in L]


def licGetClosestVertUV(oObject, iX_uv, iY_uv):
    '''
    returns the closest vert to a point in UV space
    '''
    oClosestVert = min(oObject.data.vertices, key=lambda oVert: (vPoint - oObject.matrix_world*oVert.co).length)
    return oClosestVert


def licGetClosestVert(oObject, vPoint):
    '''
    returns the closest vert to a point in 3D space
    '''
    oClosestVert = min(oObject.data.vertices, key=lambda oVert: (vPoint - oObject.matrix_world*oVert.co).length)
    return oClosestVert


def licGetClosestVerts(oObject, vPoint, iAveraging=1):
    '''
    returns a dictionary {'sVertIndex':iFactor)
    for the number of n clostest vertices to a point in 3D space
    iFactor represents each vertexes relative influence based on proximity
    note: all Factors add up to one
    '''
    if iAveraging == 1:
        # note: IDProperties can only be ints, floats, dicts (not lists unfortunately)
        return {'%s'%licGetClosestVert(oObject, vPoint).index:1}
        
    else:
        lVertDistances = [ (oVert.index, (vPoint-oObject.matrix_world*oVert.co).length) for oVert in oObject.data.vertices ]
        
        #only take nearest n into account
        lVertDistances = sorted(lVertDistances, key=lambda x: x[1])[:iAveraging]
        
        # normalize, inverse distance weight
        lNormalized = licNormListSumTo([iDistance for (iIndex,iDistance) in lVertDistances])
        lNormalizedInverse = [ (2/len(lNormalized))-iValue for iValue in lNormalized ]
        #lNormalizedInverse = licNormListSumTo(lNormalizedInverse)                            
        lVertDistances = [ ('%s'%k, lNormalizedInverse[ lVertDistances.index( (k,i) ) ] ) for (k,i) in lVertDistances ]
        
        return dict(lVertDistances)


def licGetClosestVertTransformed(lGlobalVertexPositions, vPoint):
    '''
    returns the closest vert index to a point in 3D space
    note: this is the same as 'licGetClosestVert' but takes a precalculated list of global vertex positions
    '''
    ltVertDistances = [ (index, (vPoint-pos).length) for (index, pos) in lGlobalVertexPositions ]
    tClosestVert = min(ltVertDistances, key=lambda x: x[1])
    return tClosestVert[0]


def licGetClosestVertsTransformed(lGlobalVertexPositions, vPoint, iAveraging=1):
    '''
    returns a dictionary {'sVertIndex':iFactor)
    for the number of n clostest vertices to a point in 3D space
    iFactor represents each vertexes relative influence based on proximity
    note: all Factors add up to one
    note: this is the same as 'licGetClosestVerts' but takes a precalculated list of global vertex positions
    '''
    if iAveraging == 1:
        # note: IDProperties can only be ints, floats, dicts (not lists unfortunately)
        return {'%s'%licGetClosestVertTransformed(lGlobalVertexPositions, vPoint):1}
        
    else:
        ltVertDistances = [ (index, (vPoint-pos).length) for (index, pos) in lGlobalVertexPositions ]
        
        #only take nearest n into account
        ltVertDistances = sorted(ltVertDistances, key=lambda x: x[1])[:iAveraging]
        
        # normalize, inverse distance weight
        lNormalized = licNormListSumTo([iDistance for (iIndex,iDistance) in ltVertDistances])
        lNormalizedInverse = [ (2/len(lNormalized))-iValue for iValue in lNormalized ]
        #lNormalizedInverse = licNormListSumTo(lNormalizedInverse)            
        ltVertDistances = [ ('%s'%k, lNormalizedInverse[ ltVertDistances.index( (k,i) ) ] ) for (k,i) in ltVertDistances ]
        
        return dict(ltVertDistances)

def licGetClosestPoint(oObject, vPoint):
    '''
    note: not used atm
    returns the closest point to a point in 3D space
    '''
    # TODO: object still has to have applied scale/rot -> get rid of this
    #(hit, hitnormal, faceindex) = oObject.closest_point_on_mesh(vPoint)
    
    # transform Cube data first
    
    # work on a mesh copy (modifiers respected)
    oDefMesh = oObject.to_mesh(bpy.context.scene, True, 'PREVIEW')
    oDefOb = bpy.data.objects.new("test", oDefMesh)
    bpy.context.scene.objects.link(oDefOb)
    (hit, hitnormal, faceindex) = oDefOb.closest_point_on_mesh(vPoint) # errors out? maybe update scene before... if(ob->derivedFinal==NULL) in source/blender/makesrna/rna_object.c
    
    #oNull.location = oCube.matrix_world * hit  #?hm
    
    return hit


def licCheckSaneObjects(oTargetObject, oSourceObject, oOperator=None):
    '''
    both target and source should be mesh objects
    '''
    bGoodToGo = False
    if oTargetObject.data is not None and oSourceObject.data is not None:
        if oSourceObject.data.bl_rna.identifier == "Mesh" and oTargetObject.data.bl_rna.identifier == "Mesh":
            bGoodToGo = True
    if not bGoodToGo:
        if oOperator is not None:
            oOperator.report({'WARNING'}, "both target and source MUST be mesh objects")
        return False
    
    return True


def licBuildVertFaceDict(oObject):
    '''
    to speed up the lookup of a vertex-face relation
    this one builds a dictionary with the vertex index as key
    and a list of tuples (faceIndex, indexInFace) of faces this vert belongs to
    '''    
    d = {}
    
    for oFace in oObject.data.faces:
        lAlreadyInList = d.keys()
        for iVertexIndex in oFace.vertices:
            if not iVertexIndex in lAlreadyInList:
                d[iVertexIndex] = []
            d[iVertexIndex].append( (oFace.index, oFace.vertices[:].index(iVertexIndex)) )
            
    return d

def licFindVertexVertexGroupIndex(oTargetVertex, oTargetVertexGroup):
    '''
    vertex.groups[index] and object.vertexgroups[index] is not the same index
    might be different if vertex is not assigned to ALL objects vertex groups
    '''
    for iGroupIndex_vertex in range(len(oTargetVertex.groups)):
        if oTargetVertex.groups[iGroupIndex_vertex].group == oTargetVertexGroup.index:
            return iGroupIndex_vertex
        
    return None

def licFindShapeKeyIndex(oObj, sShapekeyName):
    '''
    finds a named shapekey's index in the key_blocks
    '''
    if oObj.data.shape_keys is None:
        return None
    lShapeKeyNames = [oShape.name for oShape in oObj.data.shape_keys.key_blocks]
    if sShapekeyName in lShapeKeyNames:
        return lShapeKeyNames.index(sShapekeyName)
    else:
        return None

def licRemoveNamedShapekey(oObj, sShapekeyName):
    '''
    removes a named shapekey from the objects key_blocks
    '''
    found = licFindShapeKeyIndex(oObj, sShapekeyName)
    if found is not None:
        oObj.active_shape_key_index = found
        bpy.ops.object.shape_key_remove()

def licDisableGeneratingModifiers(oObject):
    '''
    go over all modifiers and disable the "generating" ones
    returns their original state in a dict so we can leave tidy afterwards
    (see licEnableGeneratingModifiers)
    '''
    lsGeneratingModifiers = ['ARRAY', 'BEVEL', 'BOOLEAN', 'BUILD', 'DECIMATE', 'EDGE_SPLIT', 
                                    'MASK', 'MIRROR', 'MULTIRES', 'REMESH', 'SCREW', 'SOLIDIFY', 'SUBSURF']
    lGeneratingModifiers = [oModifier for oModifier in oObject.modifiers
                                   if oModifier.type in lsGeneratingModifiers]
    dGeneratingModifiers = {}
    for oModifier in lGeneratingModifiers:
        dGeneratingModifiers[oModifier.name] = oModifier.show_render
        oModifier.show_render = False
        #print("temporarily disabled modifier '%s' on '%s'" % (oModifier.name, oObject.name))    

    return dGeneratingModifiers

def licEnableGeneratingModifiers(oObject, dOriginalState):
    '''
    go over all modifiers and enable the "generating" ones again
    based on the cached state we remembered before
    (see licDisableGeneratingModifiers)
    '''    
    lsGeneratingModifiers = ['ARRAY', 'BEVEL', 'BOOLEAN', 'BUILD', 'DECIMATE', 'EDGE_SPLIT', 
                                    'MASK', 'MIRROR', 'MULTIRES', 'REMESH', 'SCREW', 'SOLIDIFY', 'SUBSURF']
    lGeneratingModifiers = [oModifier for oModifier in oObject.modifiers
                                   if oModifier.type in lsGeneratingModifiers]
    for oModifier in lGeneratingModifiers:
        oModifier.show_render = dOriginalState[oModifier.name]

'''      
# ----------------------------------------
# Property definitions
# ----------------------------------------
'''

def licCallbMethodChanged(self, context):
    print("Sorry, UV proximity not supported yet")
    #context.window_manager.lMeshTransfer_Method = '1'

def licsCallbSourceObjectChanged(self, context):
    oWM = context.window_manager
    if self.sSourceObject in bpy.data.objects:
        oSourceObject = bpy.data.objects[self.sSourceObject]
        if oSourceObject.data is not None and oSourceObject.data.bl_rna.identifier == "Mesh":
            # change the source vertex group/color to the active of the newly selected one
            if oSourceObject.vertex_groups.active is not None:
                self.sSourceVertexGroup = oSourceObject.vertex_groups.active.name
            else:
                self.sSourceVertexGroup = ""
                
            if oSourceObject.data.vertex_colors.active is not None:
                self.sSourceVertexColor = oSourceObject.data.vertex_colors.active.name
            else:
                self.sSourceVertexColor = ""
            if oSourceObject.data.shape_keys is not None:
                self.sSourceShapekey = oSourceObject.active_shape_key.name
            else:
                self.sSourceShapekey = ""    
            # TODO: change max average vertices slider in GUI
            bpy.types.WindowManager.iMeshTransfer_VertAveraging = bpy.props.IntProperty(
                name="iMeshTransfer_VertAveraging",
                description="number of nearby vertices on the source object to take into account for averaging",
                default=1,
                min=1,
                max=int(len(oSourceObject.data.vertices)),
                soft_max=min(50,int(len(oSourceObject.data.vertices))))
            #http://blenderartists.org/forum/showthread.php?208605-Correct-Usage-Of-_RNA_UI-for-setting-Min-Max-of-IDProperties&s=98eae13ae0b2f5a65738a84218d91638

bpy.types.WindowManager.lMeshTransfer_Method = bpy.props.EnumProperty(
    name='',
    description='method to calculate vertex mapping on',
    items=[('0', '3D space proximity', '3D space proximity')],
    update=licCallbMethodChanged
    )#,('1', 'UV space proximity', 'UV space proximity')

bpy.types.WindowManager.bMeshTransfer_RespectTransforms = bpy.props.BoolProperty(
    name="", 
    description="take global transforms into acount (ob.matrix_world)",
    default=True)

bpy.types.WindowManager.bMeshTransfer_RespectModifiers = bpy.props.BoolProperty(
    name="", 
    description="take modifiers into acount (ob.to_mesh)",
    default=True)

bpy.types.WindowManager.iMeshTransfer_VertAveraging = bpy.props.IntProperty(
    name="",
    description="number of nearby vertices on the source object to take into account for averaging",
    default=1,
    min=1,
    max=50,
    soft_max=50)

bpy.types.WindowManager.lMeshTransfer_Operation = bpy.props.EnumProperty(
    name='',
    description='what to transfer',
    items=[('0', 'Vertex Groups', 'Vertex Groups'),
           ('1', 'Shape Keys', 'Shape Keys'),
           ('2', 'UV Maps', 'UV Maps'),
           ('3', 'Vertex Colors', 'Vertex Colors'),
           ('4', 'Vertex Displacement (driven)', 'Vertex Displacement (driven)')]
    )#TODO: can we specify icons here?

bpy.types.WindowManager.bMeshTransfer_KeepNames = bpy.props.BoolProperty(
    name="", 
    description="this will keep the names of transfered data like on the SourceObject (will have a more descriptive name if OFF)",
    default=True)

bpy.types.WindowManager.bMeshTransfer_OverwriteExisting = bpy.props.BoolProperty(
    name="", 
    description="will overwrite equally named data on the target (will leave untouched if OFF)",
    default=True)

class MeshTransfer_Props(bpy.types.PropertyGroup):
    
    @classmethod
    def register(MeshTransfer_Props):

        MeshTransfer_Props.sSourceObject = bpy.props.StringProperty(name="Source object", 
                                                            description="the object from which to transfer mesh data",
                                                            update=licsCallbSourceObjectChanged)
        MeshTransfer_Props.sTargetAffectVertexGroup = bpy.props.StringProperty(name="sTargetAffectVertexGroup", 
                                                            description="multiply effect by this this vertexgroup")
        # TODO make this WM prop? (is genreal tool option, no?)
        MeshTransfer_Props.eTransferCount = bpy.props.EnumProperty(
                                                            name='',
                                                            description='choose to transfer all available or just a single data layer',
                                                            items=[('0', 'all available', 'all available'),
                                                                   ('1', 'single', 'single')])
        MeshTransfer_Props.sSourceVertexGroup = bpy.props.StringProperty(
                                                            name="Source Vertex Group", 
                                                            description="Vertex Group on the Source object to transfer data from")      
        MeshTransfer_Props.sSourceVertexColor = bpy.props.StringProperty(
                                                            name="Source Vertex Color", 
                                                            description="Vertex Color on the Source object to transfer data from")       
        MeshTransfer_Props.sSourceShapekey = bpy.props.StringProperty(
                                                            name="Source Shape Key", 
                                                            description="Shape Key on the Source object to transfer data from")
        MeshTransfer_Props.sTargetVertexGroup = bpy.props.StringProperty(
                                                            name="Target Vertex Group", 
                                                            description="Vertex Group on the Target object to transfer data to " \
                                                                        "(leave empty to work on one with a generated descriptive name)")      
        MeshTransfer_Props.sTargetVertexColor = bpy.props.StringProperty(
                                                            name="Target Vertex Color", 
                                                            description="Vertex Color on the Target object to transfer data to " \
                                                                        "(leave empty to work on one with a generated descriptive name)")       
        MeshTransfer_Props.sTargetShapekey = bpy.props.StringProperty(
                                                            name="Target Shape Key", 
                                                            description="Shape Key on the Target object to transfer data to " \
                                                                        "(leave empty to work on one with a generated descriptive name)")
        MeshTransfer_Props.sTargetUVMap = bpy.props.StringProperty(
                                                            name="Target UV Map", 
                                                            description="UV Map on the Target object to transfer data to " \
                                                                        "(leave empty to work on one with a generated descriptive name)")
        bpy.types.Object.meshtransfer_props = bpy.props.PointerProperty(type=MeshTransfer_Props, 
                                                            name="Lichtwerk MeshTransfer Properties", 
                                                            description="Lichtwerk MeshTransfer Properties")
    @classmethod
    def unregister(cls):
        del bpy.types.Object.meshtransfer_props


'''
# ----------------------------------------
# Panel / UI
# ----------------------------------------
'''
class DATA_PT_lichtwerk_meshtransfer(bpy.types.Panel):
    bl_label = "MeshTransfer"
    bl_idname = "lichtwerk.meshtransfer_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    def draw(self, context):
        
        '''
        TODO: rking> This is a feature request that might take more work, but what about an "All Vertex Groups" option on Transfer Weights?
        
        TODO: put check for mesh type in poll and a mixin class like oscuartools?
        '''
        
        layout = self.layout

        oTargetObject = context.active_object
        oWM = context.window_manager
        oProps = oTargetObject.meshtransfer_props
        
        if oTargetObject.data is not None and oTargetObject.data.bl_rna.identifier == "Mesh":
            
            # ------------------------------------------------------------------------
            # ----- MAPPING ----------------------------------------------------------
            # ------------------------------------------------------------------------
            box = layout.box()
            
            split = box.split(percentage=0.4)
            
            col = split.column()
            col.label(text="Target object:")
            col.label(text="Source object:")
            col.label(text="Method:")
            if oWM.lMeshTransfer_Method == '0':
                col.label(text="")
                col.label(text="")
            col.label(text="Average verts:")
            
            col = split.column()
            col.label(text=oTargetObject.name, icon='OBJECT_DATAMODE')
            # TODO: can we restrict this to show only mesh objects?
            col.prop_search(oProps, 
                            "sSourceObject",  context.scene, "objects", text="")
            col.prop(oWM, "lMeshTransfer_Method", text="")
            if oWM.lMeshTransfer_Method == '0':
                col.prop(oWM, "bMeshTransfer_RespectTransforms", text="transforms")
                col.prop(oWM, "bMeshTransfer_RespectModifiers", text="modifiers")
            col.prop(oWM, "iMeshTransfer_VertAveraging", text="", slider=True)
            
            bActiveOps = False
            
            row = box.row()
            lMappings = [key.replace('MeshTransfer_CloseVerts_','',1) for key in oTargetObject.keys() 
                         if key.startswith('MeshTransfer_CloseVerts_')]
            row.label(' %s is mapped to: %s' % (oTargetObject.name, ', '.join(lMappings)), icon='INFO')
            if len(lMappings) > 0:
                bActiveOps = True
            row = box.row()
    
            if not oProps.sSourceObject in lMappings:
                row.operator("lichtwerk.meshtransfer_bind", text="Create vertex mapping")
            else:
                row.operator("lichtwerk.meshtransfer_unbind", text="Delete vertex mapping")

            row = box.row()
            row.operator("lichtwerk.meshtransfer_select_mapped", text="Select mapped vertices")
    
            sSourceObject = oProps.sSourceObject
            if sSourceObject in bpy.data.objects:
                oSourceObject = bpy.data.objects[sSourceObject]
                bActiveOps = True if (licCheckSaneObjects(oTargetObject, oSourceObject) and bActiveOps) else False
            else:
                oSourceObject = None
                bActiveOps = False
    
            layout.separator()
            
            # ------------------------------------------------------------------------
            # ----- TRANSFER ---------------------------------------------------------
            # ------------------------------------------------------------------------
            box = layout.box()
            split = box.split(percentage=0.4)
            col = split.column()
            col.label(text=" Transfer", icon="FORWARD")
            col = split.column()
            col.prop(oWM, "lMeshTransfer_Operation", text="")
            
            if oWM.lMeshTransfer_Operation == '0':
                split = box.split(percentage=0.4)
                
                col = split.column()
                col.label(text=" Source", icon="GROUP_VERTEX")
                if oProps.eTransferCount == '1':
                    col.label(text="")
                    col.label(text=" Target", icon="GROUP_VERTEX")
                    col.label(text="")
                    col.label(text="")
                else:
                    col.label(text=" Target", icon="GROUP_VERTEX")
                    col.label(text="")
                col.label(text=" Target mask:", icon="GROUP_VERTEX")
                
                col = split.column()
                col.prop(oProps, "eTransferCount", text="")
                if oProps.eTransferCount == '1':
                    if bActiveOps:
                        col.prop_search(oProps, "sSourceVertexGroup", oSourceObject, 
                                        "vertex_groups", text="", icon='NONE')
                    else:
                        col.prop(oProps, "sSourceVertexGroup", text="")
                    col.prop(oWM, "bMeshTransfer_KeepNames", text="Names as on Source")
                    col.prop(oWM, "bMeshTransfer_OverwriteExisting", text="Overwrite Existing")
                    row = col.row()
                    if bActiveOps:
                        row.prop_search(oProps, "sTargetVertexGroup", oTargetObject,
                                        "vertex_groups", text="", icon='NONE')
                    else:
                        row.prop(oProps, "sTargetVertexGroup", text="")
                    if oWM.bMeshTransfer_KeepNames: row.active = False
                else:
                    col.prop(oWM, "bMeshTransfer_KeepNames", text="Names as on Source")
                    col.prop(oWM, "bMeshTransfer_OverwriteExisting", text="Overwrite Existing")
                col.prop_search(oProps, "sTargetAffectVertexGroup",  
                            oTargetObject, "vertex_groups", text="")
                row = box.row()
                row.operator("lichtwerk.meshtransfer_weights", text="Transfer weights")

            elif oWM.lMeshTransfer_Operation == '1':
                split = box.split(percentage=0.4)
                col = split.column()
                col.label(text=" Source", icon="SHAPEKEY_DATA")
                if oProps.eTransferCount == '1':
                    col.label(text="")
                    col.label(text=" Target", icon="SHAPEKEY_DATA")
                    col.label(text="")
                    col.label(text="")
                else:
                    col.label(text=" Target", icon="SHAPEKEY_DATA")
                    col.label(text="")
                col.label(text=" Target mask:", icon="GROUP_VERTEX")
                
                col = split.column()
                col.prop(oProps, "eTransferCount", text="")
                if oProps.eTransferCount == '1':
                    if bActiveOps and oSourceObject.data.shape_keys is not None:
                        col.prop_search(oProps, "sSourceShapekey", oSourceObject.data.shape_keys, 
                                        "key_blocks", text="", icon='NONE')
                    else:
                        col.prop(oProps, "sSourceShapekey", text="")
                    col.prop(oWM, "bMeshTransfer_KeepNames", text="Names as on Source")
                    col.prop(oWM, "bMeshTransfer_OverwriteExisting", text="Overwrite Existing")
                    row = col.row()
                    if bActiveOps and oTargetObject.data.shape_keys is not None:
                        row.prop_search(oProps, "sTargetShapekey", oTargetObject.data.shape_keys,
                                        "key_blocks", text="", icon='NONE')
                    else:
                        row.prop(oProps, "sTargetShapekey", text="")
                    if oWM.bMeshTransfer_KeepNames: row.active = False
                else:
                    col.prop(oWM, "bMeshTransfer_KeepNames", text="Names as on Source")
                    col.prop(oWM, "bMeshTransfer_OverwriteExisting", text="Overwrite Existing")
                    
                col.prop_search(oProps, "sTargetAffectVertexGroup",  
                            oTargetObject, "vertex_groups", text="")
                row = box.row()
                row.operator("lichtwerk.meshtransfer_shapekeys", text="Transfer shapekeys")

            elif oWM.lMeshTransfer_Operation == '2':
                split = box.split(percentage=0.4)
                
                col = split.column()
                col.label(text=" Source", icon="GROUP_UVS")
                if oProps.eTransferCount == '1':
                    col.label(text="")
                    col.label(text=" Target", icon="GROUP_UVS")
                    col.label(text="")
                    col.label(text="")
                else:
                    col.label(text=" Target", icon="GROUP_UVS")
                    col.label(text="")
                col.label(text=" Target mask:", icon="GROUP_VERTEX")
                
                col = split.column()
                col.prop(oProps, "eTransferCount", text="")
                if oProps.eTransferCount == '1':
                    if bActiveOps:
                        col.prop_search(oProps, "sSourceUVMap", oSourceObject.data, 
                                        "uv_textures", text="", icon='NONE')
                    else:
                        col.prop(oProps, "sSourceUVMap", text="")
                    col.prop(oWM, "bMeshTransfer_KeepNames", text="Names as on Source")
                    col.prop(oWM, "bMeshTransfer_OverwriteExisting", text="Overwrite Existing")
                    row = col.row()
                    if bActiveOps:
                        row.prop_search(oProps, "sTargetUVMap", oTargetObject.data,
                                        "uv_textures", text="", icon='NONE')
                    else:
                        row.prop(oProps, "sTargetUVMap", text="")
                    if oWM.bMeshTransfer_KeepNames: row.active = False
                else:
                    col.prop(oWM, "bMeshTransfer_KeepNames", text="Names as on Source")
                    col.prop(oWM, "bMeshTransfer_OverwriteExisting", text="Overwrite Existing")
                
                col.prop_search(oProps, "sTargetAffectVertexGroup",
                            oTargetObject, "vertex_groups", text="")
                row = box.row()
                row.operator("lichtwerk.meshtransfer_uvs", text="Transfer UV Maps")
            
            elif oWM.lMeshTransfer_Operation == '3':
                split = box.split(percentage=0.4)
                
                col = split.column()
                col.label(text=" Source", icon="GROUP_VCOL")
                if oProps.eTransferCount == '1':
                    col.label(text="")
                    col.label(text=" Target", icon="GROUP_VCOL")
                    col.label(text="")
                    col.label(text="")
                else:
                    col.label(text=" Target", icon="GROUP_VCOL")
                    col.label(text="")
                col.label(text=" Target mask:", icon="GROUP_VERTEX")
                
                col = split.column()
                col.prop(oProps, "eTransferCount", text="")
                if oProps.eTransferCount == '1':
                    if bActiveOps:
                        col.prop_search(oProps, "sSourceVertexColor", oSourceObject.data, 
                                        "vertex_colors", text="", icon='NONE')
                    else:
                        col.prop(oProps, "sSourceVertexColor", text="")
                    col.prop(oWM, "bMeshTransfer_KeepNames", text="Names as on Source")
                    col.prop(oWM, "bMeshTransfer_OverwriteExisting", text="Overwrite Existing")
                    row = col.row()
                    if bActiveOps:
                        row.prop_search(oProps, "sTargetVertexColor", oTargetObject.data,
                                        "vertex_colors", text="", icon='NONE')
                    else:
                        row.prop(oProps, "sTargetVertexColor", text="")
                    if oWM.bMeshTransfer_KeepNames: row.active = False
                else:
                    col.prop(oWM, "bMeshTransfer_KeepNames", text="Names as on Source")
                    col.prop(oWM, "bMeshTransfer_OverwriteExisting", text="Overwrite Existing")
                
                col.prop_search(oProps, "sTargetAffectVertexGroup",
                            oTargetObject, "vertex_groups", text="")
                row = box.row()
                row.operator("lichtwerk.meshtransfer_vcols", text="Transfer vertex colors")
                
            elif oWM.lMeshTransfer_Operation == '4':
                row = box.row()
                row.label(' experimental feature', icon='ERROR')
                
                row = box.row()
                split = row.split(percentage=0.4)
                col = split.column()
                col.label(text=" Target mask:", icon="GROUP_VERTEX")
                col = split.column()
                col.prop_search(oProps, "sTargetAffectVertexGroup",  
                            oTargetObject, "vertex_groups", text="")
                
                row = box.row()
                row.operator("lichtwerk.meshtransfer_shape", text="Drive vertex displacement")
                            
            if not bActiveOps: box.active = False    



'''
# ----------------------------------------
# Operators
# ----------------------------------------
'''    

class DATA_OT_lichtwerk_meshtransfer_bind(bpy.types.Operator):
    '''
    for use inside panel
    '''
    
    bl_idname = "lichtwerk.meshtransfer_bind"
    bl_label = "Lichtwerk MeshTransfer Bind"

    @classmethod
    def poll(cls, context):

        return context.active_object is not None

    def execute(self, context):
        
        time_start = time.time()
        
        oTargetObject = context.active_object
        sSourceObject = oTargetObject.meshtransfer_props.sSourceObject
        
        if not sSourceObject in bpy.data.objects:
            self.report({'WARNING'}, "source object not found")
            return {'CANCELLED'}
        
        oSourceObject = bpy.data.objects[sSourceObject]
        
        # both target and source should be mesh objects
        if not licCheckSaneObjects(oTargetObject, oSourceObject, self): 
            return {'CANCELLED'}
        
        
        sDictName="MeshTransfer_CloseVerts_%s" % sSourceObject
        oTargetObject[sDictName] = {}
        
        iVertAveraging = context.window_manager.iMeshTransfer_VertAveraging
        
        # work with modifiers applied?
        if context.window_manager.bMeshTransfer_RespectModifiers:
            # go over all modifiers and disable the "generating" ones
            # remember their original state so we can leave tidy afterwards
            dOriginalState_source = licDisableGeneratingModifiers(oSourceObject)
            dOriginalState_target = licDisableGeneratingModifiers(oTargetObject)
            
            oDefMesh_target = oTargetObject.to_mesh(bpy.context.scene, True, 'RENDER')
            oDefMesh_source = oSourceObject.to_mesh(bpy.context.scene, True, 'RENDER')
            
            licEnableGeneratingModifiers(oSourceObject, dOriginalState_source)
            licEnableGeneratingModifiers(oTargetObject, dOriginalState_target)
        else:
            oDefMesh_target = oTargetObject.data.copy()
            oDefMesh_source = oSourceObject.data.copy()
        
        # we can precalculate the worldpositions for sourcevertices only once and reuse later
        # TODO: does parenting screw up something?
        if context.window_manager.bMeshTransfer_RespectTransforms:
            oDefMesh_target.transform(oTargetObject.matrix_world)
            oDefMesh_source.transform(oSourceObject.matrix_world)
            
        lSourceVerticesGlobalSpace = [(oVertex.index, oVertex.co) for oVertex in oDefMesh_source.vertices]

        # multithreading?
        # http://blenderartists.org/forum/showthread.php?193522-Multi-threading-has-an-effect-but-it-doesn-t-improve-performance&highlight=subprocess
        # http://www.blender.org/documentation/blender_python_api_2_61_0/info_gotcha.html
        for oVertex in oDefMesh_target.vertices:
            # get the closest vert on the other mesh
            #dClosestVerts = licGetClosestVerts(oSourceObject, oTargetObject.matrix_world*oVertex.co, iAveraging=iVertAveraging)
            dClosestVerts = licGetClosestVertsTransformed(lSourceVerticesGlobalSpace, 
                                                          oVertex.co, 
                                                          iAveraging=iVertAveraging)
            
            # store closest vert in the dict (note: can only use string dict-keys in Blender)
            oTargetObject[sDictName]['%s' % oVertex.index] = dClosestVerts

        if context.window_manager.bMeshTransfer_RespectModifiers:
            del oDefMesh_target
            del oDefMesh_source

        print("creating vertex mapping took: %.4f sec" % (time.time() - time_start) )
        self.report({'INFO'}, "mapped vertices from '%s' to '%s'" % (oSourceObject.name, oTargetObject.name))
        return {'FINISHED'}
       


class DATA_OT_lichtwerk_meshtransfer_unbind(bpy.types.Operator):
    '''
    get rid of associated data (IDProps, Drivers, driven Shapekeys)
    '''
    
    bl_idname = "lichtwerk.meshtransfer_unbind"
    bl_label = "Lichtwerk MeshTransfer UnBind"

    @classmethod
    def poll(cls, context):

        return context.active_object is not None

    def execute(self, context):
        
        time_start = time.time()
        
        oTargetObject = context.active_object
        sSourceObject = oTargetObject.meshtransfer_props.sSourceObject
        
        if not sSourceObject in bpy.data.objects:
            self.report({'WARNING'}, "source object was not found")
            return {'CANCELLED'}            
        oSourceObject = bpy.data.objects[sSourceObject]
        
        # delete CustomProp/driver on source (in case shape was also transferred)
        sDummyProp = 'MeshTransfer_ScrDriver_%s' % oTargetObject.name
        if oSourceObject.animation_data is not None:
            if '[\"%s\"]' % sDummyProp in [oDrv.data_path for oDrv in oSourceObject.animation_data.drivers]:
                oSourceObject.driver_remove('[\"%s\"]' % sDummyProp)
        if sDummyProp in oSourceObject.keys():
            del oSourceObject[sDummyProp]

        # remove shapekeys
        licRemoveNamedShapekey(oTargetObject, "MeshTransfer [%s] deform" % sSourceObject)
        licRemoveNamedShapekey(oTargetObject, "MeshTransfer [%s] start" % sSourceObject)
        
        # delete CustomProperties on target
        lMeshTransferProps = [key for key in oTargetObject.keys() 
                              if key.lower().startswith('meshtransfer_')]
        for prop in lMeshTransferProps:
            if (prop.find('_CloseVerts_') != -1 and prop.find(sSourceObject) != -1) \
                or prop == 'meshtransfer_props':
                del oTargetObject[prop]
            # in theory 'dOriginalShape' could be meant for different sources as well, what to DO?
        
        # so we dont loose the source in prop_search     
        oTargetObject.meshtransfer_props.sSourceObject = sSourceObject
        
        self.report({'INFO'}, "deleted mapping data")
        return {'FINISHED'}


class DATA_OT_lichtwerk_meshtransfer_select_mapped(bpy.types.Operator):
    '''
    select associated mapped vertices
    '''
    
    bl_idname = "lichtwerk.meshtransfer_select_mapped"
    bl_label = "Lichtwerk MeshTransfer Select Mapped"

    @classmethod
    def poll(cls, context):

        return context.active_object is not None

    def execute(self, context):
        
        oTargetObject = context.active_object
        oProps = oTargetObject.meshtransfer_props
        sSourceObject = oProps.sSourceObject
        oWM = context.window_manager
        
        sDictName="MeshTransfer_CloseVerts_%s" % sSourceObject

        if not sDictName in oTargetObject.keys():
            # TODO: check if dict len corresponds to nb of vertices
            self.report({'WARNING'}, "object was not mapped to '%s'" % sSourceObject)
            return {'CANCELLED'}
        
        if not sSourceObject in bpy.data.objects:
            self.report({'WARNING'}, "source object was not found")
            return {'CANCELLED'}            
        oSourceObject = bpy.data.objects[sSourceObject]

        # both target and source should be mesh objects
        if not licCheckSaneObjects(oTargetObject, oSourceObject, self): 
            return {'CANCELLED'}
        
        
        for oTargetVertex in [o for o in oTargetObject.data.vertices if o.select]:
                
            dNearVerts = oTargetObject[sDictName]['%s' % oTargetVertex.index]
            for sSourceVertexIndex, iFactor in dNearVerts.items():
                oSourceVertex = oSourceObject.data.vertices[ int(sSourceVertexIndex) ]
                oSourceVertex.select = True

        return {'FINISHED'}


class DATA_OT_lichtwerk_meshtransfer_weights(bpy.types.Operator):
    '''
    transfers the vertex weights from one mesh to another
    it uses a dictionary on the targetobject holding the mapping
    between the sourceobjects's vertices and the targetobjects's vertices
    which has been generated by the DATA_OT_lichtwerk_meshtransfer_bind operator
    '''
    
    bl_idname = "lichtwerk.meshtransfer_weights"
    bl_label = "Lichtwerk MeshTransfer Weights"

    @classmethod
    def poll(cls, context):

        #TODO: check if object is bound yet
        return context.active_object is not None


    def execute(self, context):
        
        oTargetObject = context.active_object
        oProps = oTargetObject.meshtransfer_props
        sSourceObject = oProps.sSourceObject
        oWM = context.window_manager
        
        sDictName="MeshTransfer_CloseVerts_%s" % sSourceObject
        
        if not sDictName in oTargetObject.keys():
            # TODO: check if dict len corresponds to nb of vertices
            self.report({'WARNING'}, "object was not mapped to '%s'" % sSourceObject)
            return {'CANCELLED'}
            
        if not sSourceObject in bpy.data.objects:
            self.report({'WARNING'}, "source object was not found")
            return {'CANCELLED'}            
        oSourceObject = bpy.data.objects[sSourceObject]
    
        # both target and source should be mesh objects
        if not licCheckSaneObjects(oTargetObject, oSourceObject, self): 
            return {'CANCELLED'}
        
        # take weight on Affect target vertexgroup into account
        sTargetAffectVertexGroup = oProps.sTargetAffectVertexGroup
        if sTargetAffectVertexGroup in oTargetObject.vertex_groups:
            oTargetAffectVertexGroup = oTargetObject.vertex_groups[sTargetAffectVertexGroup]
            bAffectVG = True
        else:
            bAffectVG = False
        
        # go over source vertex groups (or just a single one)
        # TODO: if we go over all, we could preprocess some stuff further down only _once_
        lSourceVertexGroupsToTransfer = []
        if oProps.eTransferCount == '1':
            sSourceVertexGroup = oProps.sSourceVertexGroup
            if not sSourceVertexGroup in oSourceObject.vertex_groups:
                self.report({'WARNING'}, "no valid source vertex group specified")
                return {'CANCELLED'}
            lSourceVertexGroupsToTransfer.append(oSourceObject.vertex_groups[sSourceVertexGroup])
        else:
            if len(oSourceObject.vertex_groups) == 0:
                self.report({'WARNING'}, "source has no available vertex groups")
                return {'CANCELLED'}
            lSourceVertexGroupsToTransfer = [oVGroup for oVGroup in oSourceObject.vertex_groups]  

        
        for oSourceVertexGroup in lSourceVertexGroupsToTransfer:
            sSourceVertexGroup = oSourceVertexGroup.name
            # create a vertex group on the target (if not existing already)
            # add all vertices to it (weight zero for now, adding comes later)
            # make it active (so we always see what we're doing)
            if oWM.bMeshTransfer_KeepNames:
                sTargetVertexGroup = sSourceVertexGroup
            else:
                if oProps.sTargetVertexGroup != "":
                    sTargetVertexGroup = oProps.sTargetVertexGroup
                else:
                    sTargetVertexGroup = "MeshTransfer [%s] [%s]" % (sSourceObject,sSourceVertexGroup)
            if len(sTargetVertexGroup) > 62:
                sTargetVertexGroup = sTargetVertexGroup[:62]
            if sTargetVertexGroup in oTargetObject.vertex_groups:
                if oWM.bMeshTransfer_OverwriteExisting:
                    oTargetVertexGroup = oTargetObject.vertex_groups[sTargetVertexGroup]
                    bNeedToCalcOrigWeight = True
                else:
                    # dont do anything on this one
                    continue
            else:
                oTargetVertexGroup = oTargetObject.vertex_groups.new(sTargetVertexGroup)
                oTargetVertexGroup.add([oTargetVertex.index for oTargetVertex in oTargetObject.data.vertices], 0.0, 'REPLACE')
                bNeedToCalcOrigWeight = False
            oTargetObject.vertex_groups.active_index = oTargetVertexGroup.index
            
            # OK, copy weights over now...
            
            # speed this up with 'foreach_set'?
            for oTargetVertex in oTargetObject.data.vertices:
                
                # get index in target vertexgroup
                # if vertex is not part of that group (possible on existing equally named vertexgroups)
                # >> continue OR add that vertex to the group if "overwrite exosting is checked"
                iRealIndex_target = licFindVertexVertexGroupIndex(oTargetVertex, oTargetVertexGroup)
                if iRealIndex_target is None:
                    if oWM.bMeshTransfer_OverwriteExisting:
                        oTargetVertexGroup.add([oTargetVertex.index], 0.0, 'REPLACE')
                        iRealIndex_target = licFindVertexVertexGroupIndex(oTargetVertex, oTargetVertexGroup)
                    else:
                        continue
                
                # take weight on Affect target vertexgroup into account
                if bAffectVG:
                    iRealIndex_target = licFindVertexVertexGroupIndex(oTargetVertex, oTargetAffectVertexGroup)
                    if iRealIndex_target is None:
                        iAffectWeight = 0
                    else:
                        iAffectWeight = oTargetVertex.groups[iRealIndex_target].weight
                else:
                    iAffectWeight = 1
                
                # take original weight on "MeshTransfer_" target vertexgroup into account
                if bNeedToCalcOrigWeight:
                    iOriginalWeight = oTargetVertex.groups[iRealIndex_target].weight
                
                # gather weights from source
                iSourceWeight = 0
                dNearVerts = oTargetObject[sDictName]['%s' % oTargetVertex.index]
                for sSourceVertexIndex, iFactor in dNearVerts.items():
                    oSourceVertex = oSourceObject.data.vertices[ int(sSourceVertexIndex) ]
                    
                    # if vertex not in group --> treat as zero weight
                    iRealIndex_source = licFindVertexVertexGroupIndex(oSourceVertex, oSourceVertexGroup)
                    if iRealIndex_source is not None:
                        iSourceWeight += oSourceVertex.groups[iRealIndex_source].weight * iFactor
                    else:
                        iSourceWeight += 0
                
                # blend according to Affect influence and set the result
                if bNeedToCalcOrigWeight:
                    iResultingWeight = iAffectWeight*iSourceWeight + (1-iAffectWeight)*iOriginalWeight
                else:
                     iResultingWeight = iAffectWeight*iSourceWeight
                oTargetVertex.groups[iRealIndex_target].weight = iResultingWeight

        # switch to weight-paint mode (so we always see what we're doing)
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
            
        self.report({'INFO'}, "transfered weights from '%s' to '%s'" % (oTargetObject.name, sSourceObject))
        return {'FINISHED'}      



class DATA_OT_lichtwerk_meshtransfer_vcols(bpy.types.Operator):
    '''
    for use inside panel
    '''
    
    bl_idname = "lichtwerk.meshtransfer_vcols"
    bl_label = "Lichtwerk MeshTransfer Vertex Colors"

    @classmethod
    def poll(cls, context):

        #TODO: check if object is bound yet
        return context.active_object is not None


    def execute(self, context):
        
        oTargetObject = context.active_object
        oProps = oTargetObject.meshtransfer_props
        sSourceObject = oProps.sSourceObject
        oWM = context.window_manager
        
        sDictName="MeshTransfer_CloseVerts_%s" % sSourceObject
        
        if not sDictName in oTargetObject.keys():
            # TODO: check if dict len corresponds to nb of vertices
            self.report({'WARNING'}, "object was not mapped to '%s'" % sSourceObject)
            return {'CANCELLED'}
            
        if not sSourceObject in bpy.data.objects:
            self.report({'WARNING'}, "source object was not found")
            return {'CANCELLED'}
        
        oSourceObject = bpy.data.objects[sSourceObject]
    
        # both target and source should be mesh objects
        if not licCheckSaneObjects(oTargetObject, oSourceObject, self): 
            return {'CANCELLED'}


        # take weight on Affect target vertexgroup into account
        sTargetAffectVertexGroup = oProps.sTargetAffectVertexGroup
        if sTargetAffectVertexGroup in oTargetObject.vertex_groups:
            oTargetAffectVertexGroup = oTargetObject.vertex_groups[sTargetAffectVertexGroup]
            bAffectVG = True
        else:
            bAffectVG = False

        
        # TODO: if we go over all, we could preprocess some stuff further down only _once_
        lSourceVertexColorsToTransfer = []
        if oProps.eTransferCount == '1':
            sSourceVCol = oProps.sSourceVertexColor
            if not sSourceVCol in oSourceObject.data.vertex_colors:
                self.report({'WARNING'}, "no valid source vertex color specified")
                return {'CANCELLED'}
            lSourceVertexColorsToTransfer.append(oSourceObject.data.vertex_colors[sSourceVCol])
        else: # "all available"
            if len(oSourceObject.data.vertex_colors) == 0:
                self.report({'WARNING'}, "source has no available vertex colors")
                return {'CANCELLED'}
            lSourceVertexColorsToTransfer = [oVCol for oVCol in oSourceObject.data.vertex_colors]

        
        for oSourceVCol in lSourceVertexColorsToTransfer:
            sSourceVCol = oSourceVCol.name

            # create a vertex color layer on the target (if not existing already)
            # make it active (so we always see what we're doing)
            if oWM.bMeshTransfer_KeepNames:
                sTargetVCol = sSourceVCol
            else:
                if oProps.sTargetVertexColor != "":
                    sTargetVCol = oProps.sTargetVertexColor 
                else:
                    sTargetVCol = "MeshTransfer [%s] [%s]" % (sSourceObject, sSourceVCol)
            if len(sTargetVCol) > 62:
                sTargetVCol = sTargetVCol[:62]
            if sTargetVCol in oTargetObject.data.vertex_colors:
                if oWM.bMeshTransfer_OverwriteExisting:
                    oTargetVCol = oTargetObject.data.vertex_colors[sTargetVCol]
                    bNeedToCalcOrigCol = True
                else:
                    # dont do anything on this one
                    continue
            else:
                oTargetVCol = oTargetObject.data.vertex_colors.new(sTargetVCol)
                bNeedToCalcOrigCol = False
            oTargetVCol.active = True
            
    
            # creating a dict to speedup vert-->face lookup
            d_target = licBuildVertFaceDict(oTargetObject)
            d_source = licBuildVertFaceDict(oSourceObject)
            
            
            # OK, copy vertex colors over now...
            # speed this up with 'foreach_set'?
            for oTargetVertex in oTargetObject.data.vertices:
                
                # take weight on Affect target vertexgroup into account
                if bAffectVG:
                    iRealIndex_target = licFindVertexVertexGroupIndex(oTargetVertex, oTargetAffectVertexGroup)
                    if iRealIndex_target is None:
                        iAffectWeight = 0
                    else:
                        iAffectWeight = oTargetVertex.groups[iRealIndex_target].weight
                else:
                    iAffectWeight = 1
    
                
                dNearVerts = oTargetObject[sDictName]['%s' % oTargetVertex.index]
                for (iFaceIndex_target, iIndexInFace_target) in d_target[oTargetVertex.index]:
    
                    # take original weight on "MeshTransfer_" target vertexcolor into account
                    if bNeedToCalcOrigCol:
                        oOriginalColor = getattr(oTargetVCol.data[iFaceIndex_target], 
                                                 "color%s" % (iIndexInFace_target+1))
                    
                    # gather color from source
                    oVCol_source = mathutils.Color((0.0, 0.0, 0.0))
                    for sSourceVertexIndex, iFactor in dNearVerts.items():  
                        oSourceVertex = oSourceObject.data.vertices[ int(sSourceVertexIndex) ]
                        
                        iMultiplier = len(d_source[oSourceVertex.index])
                        oTmpColor = mathutils.Color((0.0, 0.0, 0.0))
                        
                        for (iFaceIndex_source, iIndexInFace_source) in d_source[oSourceVertex.index]:
                            color = getattr(oSourceVCol.data[iFaceIndex_source], 
                                            "color%s" % (iIndexInFace_source+1))
                            oTmpColor += color
                    
                        oVCol_source += oTmpColor/iMultiplier*iFactor
                    
                    # blend according to Affect influence and set the result
                    if bNeedToCalcOrigCol:
                        oResultingColor = iAffectWeight*oVCol_source + (1-iAffectWeight)*oOriginalColor
                    else:
                        oResultingColor = iAffectWeight*oVCol_source
                    setattr(oTargetVCol.data[iFaceIndex_target], 
                            "color%s" % (iIndexInFace_target+1), 
                            oResultingColor)
        
        # change to vertex-paint mode (so we always see what we're doing)
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        
        self.report({'INFO'}, "transfered vertex colors from '%s' to '%s'" % (oTargetObject.name, sSourceObject))
        return {'FINISHED'}


class DATA_OT_lichtwerk_meshtransfer_shapekeys(bpy.types.Operator):
    '''
    transfers the vertex weights from one mesh to another
    it uses a dictionary on the targetobject holding the mapping
    between the sourceobjects's vertices and the targetobjects's vertices
    which has been generated by the DATA_OT_lichtwerk_meshtransfer_bind operator
    '''
    
    bl_idname = "lichtwerk.meshtransfer_shapekeys"
    bl_label = "Lichtwerk MeshTransfer Shapekeys"

    @classmethod
    def poll(cls, context):

        #TODO: check if object is bound yet
        return context.active_object is not None


    def execute(self, context):
        
        oTargetObject = context.active_object
        oProps = oTargetObject.meshtransfer_props
        sSourceObject = oProps.sSourceObject
        oWM = context.window_manager
        
        sDictName="MeshTransfer_CloseVerts_%s" % sSourceObject
        
        if not sDictName in oTargetObject.keys():
            # TODO: check if dict len corresponds to nb of vertices
            self.report({'WARNING'}, "object was not mapped to '%s'" % sSourceObject)
            return {'CANCELLED'}
            
        if not sSourceObject in bpy.data.objects:
            self.report({'WARNING'}, "source object was not found")
            return {'CANCELLED'}            
        oSourceObject = bpy.data.objects[sSourceObject]
    
        # both target and source should be mesh objects
        if not licCheckSaneObjects(oTargetObject, oSourceObject, self): 
            return {'CANCELLED'}

        if oSourceObject.data.shape_keys is None:
            self.report({'WARNING'}, "no valid source shapekey specified")
            return {'CANCELLED'}
        
        # take weight on Affect target vertexgroup into account
        sTargetAffectVertexGroup = oProps.sTargetAffectVertexGroup
        if sTargetAffectVertexGroup in oTargetObject.vertex_groups:
            oTargetAffectVertexGroup = oTargetObject.vertex_groups[sTargetAffectVertexGroup]
            bAffectVG = True
        else:
            bAffectVG = False

        # go over source shapekeys (or just a single one)
        # TODO: if we go over all, we could preprocess some stuff further down only _once_
        lSourceShapekeysToTransfer = []
        if oProps.eTransferCount == '1':
            sSourceShapekey = oProps.sSourceShapekey
            if not sSourceShapekey in [o.name for o in oSourceObject.data.shape_keys.key_blocks]:
                self.report({'WARNING'}, "no valid source shapekey specified")
                return {'CANCELLED'}
            lSourceShapekeysToTransfer.append(oSourceObject.data.shape_keys.key_blocks[sSourceShapekey])
        else:
            if len(oSourceObject.data.shape_keys.key_blocks) == 0:
                self.report({'WARNING'}, "source has no available shapekeys")
                return {'CANCELLED'}
            lSourceShapekeysToTransfer = [oShapekey for oShapekey in oSourceObject.data.shape_keys.key_blocks]  
        oSourceReferenceKey = oSourceObject.data.shape_keys.reference_key
        
        # if there is no shapekeys already, we also need a reference keyshape
        if oTargetObject.data.shape_keys is None:
            oTargetReferenceKey = oTargetObject.shape_key_add("MeshTransfer [Basis]")
            bNeedToCalcOrigDisp = False
        else:
            oTargetReferenceKey = oTargetObject.data.shape_keys.reference_key
            bNeedToCalcOrigDisp = True


        # TODO: compensate for both target and source scaling
        bTransforms = bpy.context.window_manager.bMeshTransfer_RespectTransforms
        if bTransforms:
            vScl_t = oTargetObject.scale
            vScl_s = oSourceObject.scale
            vCompensateScaling = mathutils.Vector((vScl_s.x * (1/vScl_t.x),
                                                   vScl_s.y * (1/vScl_t.y),
                                                   vScl_s.z * (1/vScl_t.z),
                                                   ))
        
        for oSourceShapekey in lSourceShapekeysToTransfer:
            #set all other Target shapekeys to zero
            '''
            for oAnyKey in oTargetObject.data.shape_keys.key_blocks:
                oAnyKey.value = 0.0
            '''
             
            sSourceShapekey = oSourceShapekey.name
            
            # create a shapekey on the target (if not existing already)
            # make it active (so we always see what we're doing)
            if oWM.bMeshTransfer_KeepNames:
                sTargetShapekey = sSourceShapekey
            else:
                if oProps.sTargetShapekey != "":
                    sTargetShapekey = oProps.sTargetShapekey
                else:
                    sTargetShapekey = "MeshTransfer [%s] [%s]" % (sSourceObject,sSourceShapekey)
            if len(sTargetShapekey) > 62:
                sTargetShapekey = sTargetShapekey[:62]
            if sTargetShapekey in [o.name for o in oTargetObject.data.shape_keys.key_blocks]:
                if oWM.bMeshTransfer_OverwriteExisting:
                    oTargetShapekey = oTargetObject.data.shape_keys.key_blocks[sTargetShapekey]
                else:
                    # dont do anything on this one
                    continue
            else:
                oTargetShapekey = oTargetObject.shape_key_add(sTargetShapekey)
                bNeedToCalcOrigDisp = False
            #oTargetShapekey.value = 1.0
            oTargetObject.active_shape_key_index = licFindShapeKeyIndex(oTargetObject, oTargetShapekey.name)
            # OK, copy shape over now...

            # speed this up with 'foreach_set'?
            for oTargetVertex in oTargetObject.data.vertices:
                
                vOriginalTargetVertexPosition = oTargetReferenceKey.data[oTargetVertex.index].co
                # take original displacement on "MeshTransfer_" target shapekey into account
                if bNeedToCalcOrigDisp:
                    vOriginalDisplacement = oTargetShapekey.data[oTargetVertex.index].co - \
                                            oTargetReferenceKey.data[oTargetVertex.index].co
                
                # take weight on Affect target vertexgroup into account
                if bAffectVG:
                    iRealIndex_target = licFindVertexVertexGroupIndex(oTargetVertex, oTargetAffectVertexGroup)
                    if iRealIndex_target is None:
                        iAffectWeight = 0
                    else:
                        iAffectWeight = oTargetVertex.groups[iRealIndex_target].weight
                else:
                    iAffectWeight = 1
                
                
                dNearVerts = oTargetObject[sDictName]['%s' % oTargetVertex.index]
                vSourceDisplacement = mathutils.Vector((0,0,0))
                for sSourceVertexIndex, iFactor in dNearVerts.items():
                    oSourceVertex = oSourceObject.data.vertices[ int(sSourceVertexIndex) ]
                    vSourceDisplacement += oSourceShapekey.data[oSourceVertex.index].co - \
                                            oSourceReferenceKey.data[oSourceVertex.index].co
        
                if bTransforms: 
                    vSourceDisplacement = mathutils.Vector((vSourceDisplacement.x * vCompensateScaling.x,
                                                            vSourceDisplacement.y * vCompensateScaling.y,
                                                            vSourceDisplacement.z * vCompensateScaling.z))

                # blend according to Affect influence and set the result
                if bNeedToCalcOrigDisp:
                    vResultingDisplacement = iAffectWeight*vSourceDisplacement + (1-iAffectWeight)*vOriginalDisplacement
                else:
                    vResultingDisplacement = iAffectWeight*vSourceDisplacement
                oTargetShapekey.data[oTargetVertex.index].co = vOriginalTargetVertexPosition + vResultingDisplacement
            
        self.report({'INFO'}, "transfered shapekeys from '%s' to '%s'" % (oTargetObject.name, sSourceObject))
        return {'FINISHED'}      

class DATA_OT_lichtwerk_meshtransfer_uvs(bpy.types.Operator):
    '''
    for use inside panel
    '''
    
    bl_idname = "lichtwerk.meshtransfer_uvs"
    bl_label = "Lichtwerk MeshTransfer UV Maps"

    @classmethod
    def poll(cls, context):

        #TODO: check if object is bound yet
        return context.active_object is not None


    def execute(self, context):
        
        oTargetObject = context.active_object
        oProps = oTargetObject.meshtransfer_props
        sSourceObject = oProps.sSourceObject
        oWM = context.window_manager
        
        sDictName="MeshTransfer_CloseVerts_%s" % sSourceObject
        
        if not sDictName in oTargetObject.keys():
            # TODO: check if dict len corresponds to nb of vertices
            self.report({'WARNING'}, "object was not mapped to '%s'" % sSourceObject)
            return {'CANCELLED'}
            
        if not sSourceObject in bpy.data.objects:
            self.report({'WARNING'}, "source object was not found")
            return {'CANCELLED'}
        
        oSourceObject = bpy.data.objects[sSourceObject]
    
        # both target and source should be mesh objects
        if not licCheckSaneObjects(oTargetObject, oSourceObject, self): 
            return {'CANCELLED'}


        # take weight on Affect target vertexgroup into account
        sTargetAffectVertexGroup = oProps.sTargetAffectVertexGroup
        if sTargetAffectVertexGroup in oTargetObject.vertex_groups:
            oTargetAffectVertexGroup = oTargetObject.vertex_groups[sTargetAffectVertexGroup]
            bAffectVG = True
        else:
            bAffectVG = False

        
        # TODO: if we go over all, we could preprocess some stuff further down only _once_
        lSourceUVMapsToTransfer = []
        if oProps.eTransferCount == '1':
            sSourceUVMap = oProps.sSourceVertexColor
            if not sSourceUVMap in oSourceObject.data.uv_textures:
                self.report({'WARNING'}, "no valid UV Map specified")
                return {'CANCELLED'}
            lSourceUVMapsToTransfer.append(oSourceObject.data.uv_textures[sSourceUVMap])
        else: # "all available"
            if len(oSourceObject.data.uv_textures) == 0:
                self.report({'WARNING'}, "source has no available UV Maps")
                return {'CANCELLED'}
            lSourceUVMapsToTransfer = [oUV for oUV in oSourceObject.data.uv_textures]

        
        for oSourceUVMap in lSourceUVMapsToTransfer:
            sSourceUVMap = oSourceUVMap.name

            # create a vertex color layer on the target (if not existing already)
            # make it active (so we always see what we're doing)
            if oWM.bMeshTransfer_KeepNames:
                sTargetUVMap = sSourceUVMap
            else:
                if oProps.sTargetUVMap != "":
                    sTargetUVMap = oProps.sTargetUVMap 
                else:
                    sTargetUVMap = "MeshTransfer [%s] [%s]" % (sSourceObject, sSourceUVMap)
            if len(sTargetUVMap) > 62:
                sTargetUVMap = sTargetUVMap[:62]
            if sTargetUVMap in oTargetObject.data.uv_textures:
                if oWM.bMeshTransfer_OverwriteExisting:
                    oTargetUVMap = oTargetObject.data.uv_textures[sTargetUVMap]
                    bNeedToCalcOrigUV = True
                else:
                    # dont do anything on this one
                    continue
            else:
                oTargetUVMap = oTargetObject.data.uv_textures.new(sTargetUVMap)
                bNeedToCalcOrigUV = False
            oTargetUVMap.active = True            
    
            # creating a dict to speedup vert-->face lookup
            d_target = licBuildVertFaceDict(oTargetObject)
            d_source = licBuildVertFaceDict(oSourceObject)
            
            
            # OK, copy vertex colors over now...
            # speed this up with 'foreach_set'?
            for oTargetVertex in oTargetObject.data.vertices:
                
                # take weight on Affect target vertexgroup into account
                if bAffectVG:
                    iRealIndex_target = licFindVertexVertexGroupIndex(oTargetVertex, oTargetAffectVertexGroup)
                    if iRealIndex_target is None:
                        iAffectWeight = 0
                    else:
                        iAffectWeight = oTargetVertex.groups[iRealIndex_target].weight
                else:
                    iAffectWeight = 1
    
                
                dNearVerts = oTargetObject[sDictName]['%s' % oTargetVertex.index]
                for (iFaceIndex_target, iIndexInFace_target) in d_target[oTargetVertex.index]:
    
                    # take original weight on "MeshTransfer_" target uv into account
                    if bNeedToCalcOrigUV:
                        vOriginalUV = getattr(oTargetUVMap.data[iFaceIndex_target], 
                                                 "uv%s" % (iIndexInFace_target+1))
                    
                    # gather color from source
                    vUV_source = mathutils.Vector((0.0, 0.0))
                    
                    for sSourceVertexIndex, iFactor in dNearVerts.items():  
                        oSourceVertex = oSourceObject.data.vertices[ int(sSourceVertexIndex) ]
                        
                        iMultiplier = len(d_source[oSourceVertex.index])
                        vTmpUV = mathutils.Vector((0.0, 0.0))
                        
                        # TODO: does looking for pinned verts help, maybe?
                        # TODO: look out for seams, there we have problems
                        for (iFaceIndex_source, iIndexInFace_source) in d_source[oSourceVertex.index]:
                            uv = getattr(oSourceUVMap.data[iFaceIndex_source], 
                                            "uv%s" % (iIndexInFace_source+1))
                            vTmpUV += uv
                            
                            # also set UVMaps Image! TODO: this is called way too often
                            oTargetUVMap.data[iFaceIndex_target].image = oSourceUVMap.data[iFaceIndex_source].image
                            
                            # try: komplett nur auf den ersten
                            #break
                            
                        vUV_source += vTmpUV/iMultiplier*iFactor
                        #vUV_source += vTmpUV*iFactor
                            
                    # blend according to Affect influence and set the result
                    if bNeedToCalcOrigUV:
                        vResultingUV = iAffectWeight*vUV_source + (1-iAffectWeight)*vOriginalUV
                    else:
                        vResultingUV = iAffectWeight*vUV_source
                    setattr(oTargetUVMap.data[iFaceIndex_target], 
                            "uv%s" % (iIndexInFace_target+1), 
                            vResultingUV)
        
        # TODO: maybe secrectly run a "minimize stretch here?
        self.report({'INFO'}, "transfered UV Maps from '%s' to '%s'" % (oTargetObject.name, sSourceObject))
        return {'FINISHED'}

class DATA_OT_lichtwerk_meshtransfer_shape(bpy.types.Operator):
    '''
    for use inside panel
    '''
    
    bl_idname = "lichtwerk.meshtransfer_shape"
    bl_label = "Lichtwerk MeshTransfer Shape (movement)"

    @classmethod
    def poll(cls, context):

        #TODO: check if object is bound yet
        return True


    def execute(self, context):
        
        oTargetObject = context.active_object
        sSourceObject = oTargetObject.meshtransfer_props.sSourceObject

        sDictName="MeshTransfer_CloseVerts_%s" % sSourceObject
        
        if not sDictName in oTargetObject.keys():
            # TODO: check if dict len corresponds to nb of vertices
            self.report({'WARNING'}, "object was not mapped to '%s'" % sSourceObject)
            return {'CANCELLED'}
            
        if not sSourceObject in bpy.data.objects:
            self.report({'WARNING'}, "source object was not found")
            return {'CANCELLED'}            
        oSourceObject = bpy.data.objects[sSourceObject]
    
        # both target and source should be mesh objects
        if not licCheckSaneObjects(oTargetObject, oSourceObject, self): 
            return {'CANCELLED'}

        # store a shapekeys on the target (one that holds the deformation and one for original shape)
        oKey_start = oTargetObject.shape_key_add("MeshTransfer [%s] start" % sSourceObject)
        oKey_deform = oTargetObject.shape_key_add("MeshTransfer [%s] deform" % sSourceObject)
        oKey_deform.value = 1.0
        
        #specify source object and create a dummy IDProp to make the driver work
        oSourceObject['MeshTransfer_ScrDriver_%s' % oTargetObject.name] = 1.0
        
        # add a text which contains the function
        # the driver calls later
        # ===============================
        if not 'MeshTransfer_DriveVertexPositions.py' in bpy.data.texts:
            oText = bpy.data.texts.new('MeshTransfer_DriveVertexPositions.py')
        else:
            oText = bpy.data.texts['MeshTransfer_DriveVertexPositions.py']
        
        oText.clear()
        oText.write(
"""
import bpy
import mathutils

def licFindVertexVertexGroupIndex(oTargetVertex, oTargetVertexGroup):
    '''
    vertex.groups[index] and object.vertexgroups[index] is not the same index
    might be different if vertex is not assigned to ALL objects vertex groups
    '''
    for iGroupIndex_vertex in range(len(oTargetVertex.groups)):
        if oTargetVertex.groups[iGroupIndex_vertex].group == oTargetVertexGroup.index:
            return iGroupIndex_vertex
        
    return None
    
def licDisableGeneratingModifiers(oObject):
    '''
    go over all modifiers and disable the "generating" ones
    returns their original state in a dict so we can leave tidy afterwards
    (see licEnableGeneratingModifiers)
    '''
    lsGeneratingModifiers = ['ARRAY', 'BEVEL', 'BOOLEAN', 'BUILD', 'DECIMATE', 'EDGE_SPLIT', 
                                    'MASK', 'MIRROR', 'MULTIRES', 'REMESH', 'SCREW', 'SOLIDIFY', 'SUBSURF']
    lGeneratingModifiers = [oModifier for oModifier in oObject.modifiers
                                   if oModifier.type in lsGeneratingModifiers]
    dGeneratingModifiers = {}
    for oModifier in lGeneratingModifiers:
        dGeneratingModifiers[oModifier.name] = oModifier.show_render
        oModifier.show_render = False
        #print("temporarily disabled modifier '%s' on '%s'" % (oModifier.name, oObject.name))    

    return dGeneratingModifiers

def licEnableGeneratingModifiers(oObject, dOriginalState):
    '''
    go over all modifiers and enable the "generating" ones again
    based on the cached state we remembered before
    (see licDisableGeneratingModifiers)
    '''    
    lsGeneratingModifiers = ['ARRAY', 'BEVEL', 'BOOLEAN', 'BUILD', 'DECIMATE', 'EDGE_SPLIT', 
                                    'MASK', 'MIRROR', 'MULTIRES', 'REMESH', 'SCREW', 'SOLIDIFY', 'SUBSURF']
    lGeneratingModifiers = [oModifier for oModifier in oObject.modifiers
                                   if oModifier.type in lsGeneratingModifiers]
    for oModifier in lGeneratingModifiers:
        oModifier.show_render = dOriginalState[oModifier.name]
        
def Do(sTargetObject, sSourceObject):

    oTargetObject = bpy.data.objects[sTargetObject]
    oSourceObject = bpy.data.objects[sSourceObject]
    
    
    # go over all modifiers and disable the "generating" ones
    # remember their original state so we can leave tidy afterwards
    dOriginalState_source = licDisableGeneratingModifiers(oSourceObject)
    oDefMesh_source = oSourceObject.to_mesh(bpy.context.scene, True, 'RENDER')
    licEnableGeneratingModifiers(oSourceObject, dOriginalState_source)
    

    # TODO: compensate for both target and source scaling
    bTransforms = bpy.context.window_manager.bMeshTransfer_RespectTransforms
    if bTransforms:
        vScl_t = oTargetObject.scale
        vScl_s = oSourceObject.scale
        vCompensateScaling = mathutils.Vector((vScl_s.x * (1/vScl_t.x),
                                               vScl_s.y * (1/vScl_t.y),
                                               vScl_s.z * (1/vScl_t.z),
                                               ))
    
    sDictName="MeshTransfer_CloseVerts_%s" % sSourceObject

    # take weight on Affect target vertexgroup into account
    sTargetAffectVertexGroup = oTargetObject.meshtransfer_props.sTargetAffectVertexGroup
    if sTargetAffectVertexGroup in oTargetObject.vertex_groups:
        oTargetAffectVertexGroup = oTargetObject.vertex_groups[sTargetAffectVertexGroup]
        bAffectVG = True
    else:
        bAffectVG = False

    oKey_start = oTargetObject.data.shape_keys.key_blocks["MeshTransfer [%s] start" % sSourceObject]
    oKey_deform = oTargetObject.data.shape_keys.key_blocks["MeshTransfer [%s] deform" % sSourceObject]

    # speed this up with 'foreach_set'?
    for oTargetVertex in oTargetObject.data.vertices:
        
        vOriginalTargetVertexPosition = oKey_start.data[oTargetVertex.index].co
        
        # take weight on Affect target vertexgroup into account
        if bAffectVG:
            iRealIndex_target = licFindVertexVertexGroupIndex(oTargetVertex, oTargetAffectVertexGroup)
            if iRealIndex_target is None:
                iAffectWeight = 0
            else:
                iAffectWeight = oTargetVertex.groups[iRealIndex_target].weight
        else:
            iAffectWeight = 1
        
        dNearVerts = oTargetObject[sDictName]['%s' % oTargetVertex.index]
        vSourceDisplacement = mathutils.Vector((0,0,0))
        for sSourceVertexIndex, iFactor in dNearVerts.items():
            oSourceVertex = oSourceObject.data.vertices[ int(sSourceVertexIndex) ]
            oSourceVertex_deformed = oDefMesh_source.vertices[ int(sSourceVertexIndex) ]
            vSourceDisplacement += (oSourceVertex_deformed.co-oSourceVertex.co)*iFactor

        if bTransforms: 
            vSourceDisplacement = mathutils.Vector((vSourceDisplacement.x * vCompensateScaling.x,
                                                    vSourceDisplacement.y * vCompensateScaling.y,
                                                    vSourceDisplacement.z * vCompensateScaling.z))
        oKey_deform.data[oTargetVertex.index].co = vOriginalTargetVertexPosition + iAffectWeight*vSourceDisplacement
        
def Call(sTargetObject, sSourceObject):
    try:
        # is the addon loaded?
        bTransforms = bpy.context.window_manager.bMeshTransfer_RespectTransforms
        Do(sTargetObject, sSourceObject)
        return 1
    except:
        import traceback
        traceback.print_exc()
        return 10

""")
        
        
        # add the text to be executed on
        # the driver calls later
        # ===============================
        if (oSourceObject.animation_data is None) \
        or (not '[\"MeshTransfer_ScrDriver_%s\"]' % oTargetObject.name \
        in [oDrv.data_path for oDrv in oSourceObject.animation_data.drivers]):
            oDriver = oSourceObject.driver_add('[\"MeshTransfer_ScrDriver_%s\"]' % oTargetObject.name)
            oDriver.driver.type = "SCRIPTED"
            oDriver.driver.expression = "float(__import__(\"MeshTransfer_DriveVertexPositions\").Call('%s','%s') )" \
                                        % (oTargetObject.name, oSourceObject.name)
                                        
            # a default modifier is created which we want to remove
            oDriver.modifiers.remove(oDriver.modifiers[0])


        self.report({'INFO'}, "setup driven ShapeTransfer from '%s' to '%s'" % (sSourceObject, oTargetObject.name))
        return {'FINISHED'}


'''
# ----------------------------------------
# registration
# ----------------------------------------
'''

def register():
    bpy.utils.register_class(DATA_PT_lichtwerk_meshtransfer)
    bpy.utils.register_class(DATA_OT_lichtwerk_meshtransfer_bind)
    bpy.utils.register_class(DATA_OT_lichtwerk_meshtransfer_unbind)
    bpy.utils.register_class(DATA_OT_lichtwerk_meshtransfer_select_mapped)
    bpy.utils.register_class(DATA_OT_lichtwerk_meshtransfer_weights)
    bpy.utils.register_class(DATA_OT_lichtwerk_meshtransfer_vcols)
    bpy.utils.register_class(DATA_OT_lichtwerk_meshtransfer_shapekeys)
    bpy.utils.register_class(DATA_OT_lichtwerk_meshtransfer_uvs)
    bpy.utils.register_class(DATA_OT_lichtwerk_meshtransfer_shape)
    bpy.utils.register_class(MeshTransfer_Props)

def unregister():
    bpy.utils.unregister_class(DATA_PT_lichtwerk_meshtransfer)
    bpy.utils.unregister_class(DATA_OT_lichtwerk_meshtransfer_bind)
    bpy.utils.unregister_class(DATA_OT_lichtwerk_meshtransfer_unbind)
    bpy.utils.unregister_class(DATA_OT_lichtwerk_meshtransfer_select_mapped)
    bpy.utils.unregister_class(DATA_OT_lichtwerk_meshtransfer_weights)
    bpy.utils.unregister_class(DATA_OT_lichtwerk_meshtransfer_vcols)
    bpy.utils.unregister_class(DATA_OT_lichtwerk_meshtransfer_shapekeys)
    bpy.utils.unregister_class(DATA_OT_lichtwerk_meshtransfer_uvs)
    bpy.utils.unregister_class(DATA_OT_lichtwerk_meshtransfer_shape)
    bpy.utils.unregister_class(MeshTransfer_Props)
    


if __name__ == "__main__":
    register()