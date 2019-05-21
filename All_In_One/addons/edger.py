import bpy
import bmesh
import mathutils
import bgl
from bpy_extras.view3d_utils import location_3d_to_region_2d

bl_info = {
    "name": "Edger",
    "author": "Reslav Hollos",
    "version": (0, 3, 6),
    "blender": (2, 72, 0),
    "description": "Lock vertices on \"edge\" they lay, make unselectable edge loops for subdivision",
    "warning": "",
#    "wiki_url": "",
    "category": "Mesh"
}

#TODO noncyclics get drawed when Edger is unregistered
#TODO when groups are added/deleted ReInit
#TODO reinit on history change
#TODO try alt rmb shortcut to deactivate so verts dont deselect
#TODO moving and canceling with RMB spawns shadows
#TODO detect group from selected and remove via button

def walk_edgeloop(l):
    
    e_first = l.edge
    e = None
    while True:
        e = l.edge
        yield e

        if e.is_manifold is False:
            print("not manifold")
            break
        
        l = l.link_loop_next
        
        l = l.link_loop_radial_next
        if len(l.face.verts) is not 4:
            break
        
        l = l.link_loop_next
        if l.edge is e_first:
            break
        
def RefineGroups(obj, bm, groupVerts):
    allGroups = set()
    for g in groupVerts:
        for v in groupVerts[g]:
            for l in v.link_loops:
                validEdges = []
                for e in walk_edgeloop(l):
                    ve1, ve2 = e.verts[0], e.verts[1]
                    gr = groupVerts[g]
                    
                    if ve1 not in gr or ve2 not in gr or \
                       len(ve1.link_edges) is 3 or \
                       len(ve2.link_edges) is 3:
                        validEdges = []
                        break
                    validEdges.append(e)
                 
                if len(validEdges) >2:
                    e1 = validEdges[0]
                    e2 = validEdges[len(validEdges)-1]
                    
                    #if loop is cyclic
                    if e1.verts[0] in e2.verts or \
                       e1.verts[1] in e2.verts:
                        forSet = []
                        for e in validEdges:
                            for v in e.verts:
                                forSet.append(v)
                                #v.select = True
                                
                        allGroups.add(frozenset(forSet))
    
    allVertsOld, allVertsNew = set(), set()
    for g in groupVerts: allVertsOld.update(groupVerts[g])
    for verts in allGroups: allVertsNew.update(verts)
    nonCyclicVerts = list(allVertsOld -allVertsNew)

    deletion = []
    for g in groupVerts:
        deletion.append(g)
    DeleteGroups(obj, deletion)
    
    for verts in allGroups:
        ng = AddNewVertexGroup("_edger_")
        AddVertsToGroup(bm, verts, ng)
    
    #ncName = "_noncyclics_edger_"
    #nc = GetGroupByName(ncName)
    #if nc: 
    #    nonCyclicVerts += GetSpecificGroupVerts(obj, bm, nc)
    #    DeleteGroup(obj, nc)
    
    #nc = AddNewVertexGroup(ncName)
    #AddVertsToGroup(bm, nonCyclicVerts, nc)
    #noncyclics = nonCyclicVerts

def GetSpecificGroupVerts(obj, bm, g):
    verts = []
    deform_layer = GetDeformLayer(bm)
    for v in bm.verts:
        if g.index in v[deform_layer]:
            verts.append(v)
    return verts

def GetGroupVerts(obj, bm):
    groupVerts = {}
    if obj and bm:
        for g in obj.vertex_groups:
            if g.name.startswith("_edger_"):
                groupVerts[g] = []
        
        deform_layer = GetDeformLayer(bm)
        
        deletion = []
        
        for v in bm.verts:
            for g in groupVerts:
                if g.index in v[deform_layer]:
                    #if v not in groupVerts[g]:
                    groupVerts[g].append(v)
        
        for g in groupVerts:
            if len(groupVerts[g]) is 0:
                deletion.append(g)
        
        #delete empty
        groupVerts = {k: v for k, v in groupVerts.items() if len(v) is not 0}
        DeleteGroups(obj, deletion)
        nc = GetGroupByName("_noncyclics_edger_")
        if nc:
            ncv = GetSpecificGroupVerts(obj, bm, nc)
            if len(ncv) is 0:
                DeleteGroup(obj, nc)
            
    return groupVerts    

def DeleteGroups(obj, groups):
    for g in groups: DeleteGroup(obj, g)

def DeleteGroup(obj, g):
    obj.vertex_groups.remove(g)    
    
def AddNewVertexGroup(name):
    #TODO make check if selected are already part of _edger_ group
    try: bpy.context.object.vertex_groups[groupName]
    except: return bpy.context.object.vertex_groups.new(name)
    return None

#def DeselectGroupsSelectCloser(adjInfos):
def DeselectGroups(adjInfos):
    for i in adjInfos:
        try: 
            if i.target.select is True:            
                i.target.select = False
                
                if i.ratioToEnd1 < 0.5:
                    i.end1.select = True
                else: i.end2.select = True
                    
        except: ReInit()

def AdjacentVerts(v, exclude = []):    
    adjacent = []
    for e in v.link_edges:
        if e.other_vert(v) not in exclude:
            adjacent.append(e.other_vert(v))
    return adjacent
        
def GetAdjInfos(groupVerts):
    adjInfos = []
    for g in groupVerts:
        for v in groupVerts[g]:
            adj = AdjacentVerts(v, groupVerts[g])
            if len(adj) is 2:
                aifv = AdjInfoForVertex(v, adj[0], adj[1])
                adjInfos.append(aifv)
    return adjInfos

class AdjInfoForVertex(object):
    def __init__(self, target, end1, end2):
        self.target = target
        self.end1 = end1
        self.end2 = end2
        self.UpdateRatio()
       
    def UpdateRatio(self):
        end1ToTarget = (self.end1.co -self.target.co).length
        end1ToEnd2 = (self.end1.co -self.end2.co).length
        self.ratioToEnd1 = end1ToTarget/end1ToEnd2; #0 is end1, 1 is end2
       
    def LockTargetOnEdge(self):
        # c = a + r(b -a)
        #TODO try except here!!
        try: self.target.co = self.end1.co +self.ratioToEnd1*(self.end2.co -self.end1.co)
        except: return
        #TODO check this out copy_from_vert_interp(vert_pair, fac)
        
def LockVertsOnEdge(adjInfos):
    for i in adjInfos:
        i.LockTargetOnEdge()
        
def GetDeformLayer(bm):
    deform_layer = bm.verts.layers.deform.active
    if deform_layer is None: 
        return bm.verts.layers.deform.new()
    return deform_layer
     
def RemoveVertsFromGroup(bm, verts, g):
    if g is None: return 
    deform_layer = GetDeformLayer(bm)
    for v in verts:
        del v[deform_layer][g.index]

def AddVertsToGroup(bm, verts, g):
    deform_layer = GetDeformLayer(bm)
    for v in verts:
        v[deform_layer][g.index] = 1     #set weight to 1 as usual default
    
def AddSelectedToGroup(bm, g):
    deform_layer = GetDeformLayer(bm)
    for v in bm.verts:
        if v.select is True:
            v[deform_layer][g.index] = 1     #set weight to 1 as usual default

def GetGroupByName(name):
    try: return bpy.context.object.vertex_groups[name]
    except: return None

def draw_callback_px(self, context):
    #if context.object and context.object.mode is not "EDIT":
    #    return
    if context.scene.isEdgerRunning is False or \
       context.scene.isEdgerDebugActive is False:
        return
    
    obj = context.object
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    context.area.tag_redraw()
    
    #draw noncyclics
    #global noncyclics
    #verts2d = Get2dFrom3dVerts(context, noncyclics)
    #DrawByVertices("points", verts2d, [0.1, 0.1, 0.5, 0.6])
    
    for g in groupVerts:
        verts2d = Get2dFrom3dVerts(context, groupVerts[g])
        DrawByVertices("lines", verts2d, [0.5, 0.1, 0.1, 0.5])

def Get2dFrom3dVerts(context, verts3d):
    verts2d =[]
    for v in verts3d:
        try: 
            v_worldCo = obj.matrix_world*v.co
            new2dCo = location_3d_to_region_2d(context.region, context.space_data.region_3d, v_worldCo)
            verts2d.append([new2dCo.x,new2dCo.y])
        #TODO multiple registered instances when running SCRIPT, qfix:restart blender 
        except: continue

    return verts2d

def SortGroupVertsByAdjacent(groupVerts):
    for g in groupVerts:
        ordered = []
        #GetGroupVerts removes empty so len(groupVerts[g]) always >0
        ordered.append(groupVerts[g].pop(0))
        while len(groupVerts[g]) > 0:
            a = NextAdjacentInLoop(ordered[len(ordered)-1], groupVerts[g])
            if a is not None:
                ordered.append(a)
                groupVerts[g].remove(a)
                continue
            #TODO that means loop group isn't a loop and contains disconnected verts, debug this to user!
            break
        if len(groupVerts[g]) is 0:
            groupVerts[g] = ordered            
        else:
            #TODO debug to user, maybe remove verts from group so it gets deleted from GetGroupVerts (?)
            groupVerts[g] = ordered + groupVerts[g]
        
def NextAdjacentInLoop(v, loopVerts):
    for e in v.link_edges:
        if e.other_vert(v) in loopVerts:
            return e.other_vert(v)
    return None

def DrawByVertices(mode, verts2d, color):
    bgl.glColor4f(*color)
    
    bgl.glEnable(bgl.GL_BLEND)
    
    if mode is "points":
        bgl.glPointSize(5)
        bgl.glBegin(bgl.GL_POINTS)
            
    elif mode is "lines":
        bgl.glLineWidth(2)
        bgl.glBegin(bgl.GL_LINE_LOOP)
    
    for x, y in verts2d:
        bgl.glVertex2f(x, y)

    bgl.glEnd()
    bgl.glDisable(bgl.GL_BLEND)
    #restore defaults
    bgl.glLineWidth(1)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

    return

#INIT
def ReInit(context = None):
    global obj, me, bm
    global groupVerts, adjInfos
    obj = bpy.context.object
    if context is not None:
        obj = context.object
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    
    groupVerts = GetGroupVerts(obj, bm)
    RefineGroups(obj, bm, groupVerts)
    groupVerts = GetGroupVerts(obj, bm)
    SortGroupVertsByAdjacent(groupVerts)
    adjInfos = GetAdjInfos(groupVerts)
    
#has to be global to sustain adjInfos between modal calls :'( sorry global haters )':
isEditMode = False
obj, me, bm = None, None, None
groupVerts = {}     #dict[g] = [list, of, vertices]
adjInfos = []
#noncyclics = []

bpy.types.Scene.isEdgerRunning = False
bpy.types.Scene.deselectGroups = True
bpy.types.Scene.isSelectFlush = bpy.props.BoolProperty(name="Flush", description="If vertex is not selected deselect parent face", default=False)
bpy.types.Scene.isEdgerActive = True
bpy.types.Scene.isEdgerDebugActive = bpy.props.BoolProperty(name="Draw", description="Toggle if edge loops should be drawn", default=True)

#bpy.props.BoolProperty(name="Deselect", description="Deselect all verts from _edger_groups, and select edge end", default=True)
#bpy.props.BoolProperty(name="Active", description="Toggle if Edger is active", default=False)

class UnlockEdgeLoop(bpy.types.Operator):
    """Unlock SINGLE selected edge loop"""
    bl_idname = "wm.unlock_edge_loop_idname"
    bl_label = "UnlockEdgeLoop_label"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def execute(self, context):
        obj = context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        
        global groupVerts
        
        selected = []
        for v in bm.verts:
            if v.select is True:
                selected.append(v)
        
        for g in groupVerts:
            if DoesListContainsList(groupVerts[g], selected):
                DeleteGroup(obj, g)
                break
       
        ReInit()
        
        return {'FINISHED'}

class LockEdgeLoop(bpy.types.Operator):
    """Lock selected edgeloop(s) as if it was on flat surface"""
    bl_idname = "wm.lock_edge_loop_idname"
    bl_label = "LockEdgeLoop_label"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def execute(self, context):
        obj = context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        
        name = "_edger_"
        counter = 0
        
        while GetGroupByName(name + "." + str(counter)) is not None:
            counter += 1
        g = AddNewVertexGroup(name + "." + str(counter))
        AddSelectedToGroup(bm, g)
        
       
        ReInit()
        
        return {'FINISHED'}

def DoesListContainsList(big, small):
    for s in small:
        if s not in big: return False
    return True

class UnselectableVertices(bpy.types.Operator):
    """Make selected vertices unselectable"""
    bl_idname = "wm.unselectable_vertices_idname"
    bl_label = "unselectable_vertices_label"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def execute(self, context):
        global obj, me, bm
        '''
        name = "_unselectable_"
        g = GetGroupByName(name)
        if g is not None:
            g = AddNewVertexGroup(name)
        AddSelectedToGroup(bm, g)
        '''
        ReInit()
        return {'FINISHED'}

def MakeSelectedOnlyVertsInGroup(bm, g):
    deform_layer = GetDeformLayer(bm)
    for f in bm.faces:
        f.select = False
        for v in f.verts:
            if g.index in v[deform_layer]:
                v.select = True

def DuplicateObject():
    bpy.ops.object.mode_set(mode = 'OBJECT') 
    bpy.ops.object.duplicate_move()
    bpy.ops.object.mode_set(mode = 'EDIT') 
    
class ClearEdgerLoops(bpy.types.Operator):
    """Create duplicate of object and remove _edger_ vertexGroups and delete their Edge Loops"""
    bl_idname = "wm.clear_edger_oops_idname"
    bl_label = "clear_edger_oops__label"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def execute(self, context):
        DuplicateObject()
        ReInit()
        global obj, me, bm
        global groupVerts
        
        bpy.types.Scene.isEdgerActive = False

        groups = []
        for g in obj.vertex_groups:
            if g.name.startswith("_edger_"):
                groups.append(g)
        for g in groups:
            MakeSelectedOnlyVertsInGroup(bm, g)
            bpy.ops.object.mode_set(mode = 'OBJECT') 
            bpy.ops.object.mode_set(mode = 'EDIT') 
            bpy.ops.mesh.delete_edgeloop()
            ReInit(context)                    
        
        #once empty groups will be automatically deleted
        return {'FINISHED'}
    
'''
class EdgerFunc1(bpy.types.Operator):
    """EdgerFunc1"""
    bl_idname = "wm.edger_func1_idname"
    bl_label = "EdgerFunc1_label"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def execute(self, context):
      
        return {'FINISHED'}
'''

def RunEdger():
    try: bpy.utils.register_class(Edger)
    except: pass
    bpy.ops.wm.edger()
    bpy.types.Scene.isEdgerRunning = True
   
def StopEdger():
    try: bpy.types.SpaceView3D.draw_handler_remove(_handle, 'WINDOW')
    except: pass
    try: bpy.utils.unregister_class(Edger)
    except: pass
    bpy.types.Scene.isEdgerRunning = False
    
class ToggleEdger(bpy.types.Operator):
    """Start or stop running Edger modal operator"""
    bl_idname = "uv.toggle_edger"
    bl_label = "Toggle Edger"

    def execute(self, context):
        if bpy.types.Scene.isEdgerRunning:
            StopEdger()
        else: RunEdger()
        
        return {'FINISHED'}
    
class ToggleLocking(bpy.types.Operator):
    """Toggle Locking of vertices on a line"""
    bl_idname = "uv.toggle_edger_locking"
    bl_label = "Toggle Edger Locking"

    def execute(self, context):
        bpy.types.Scene.isEdgerActive = not bpy.types.Scene.isEdgerActive
        return {'FINISHED'}
    
class ToggleDeselecting(bpy.types.Operator):
    """Toggle Deselecting of locked vertices"""
    bl_idname = "uv.toggle_edger_deselecting"
    bl_label = "Toggle Edger Deselecting"

    def execute(self, context):
        bpy.types.Scene.deselectGroups = not bpy.types.Scene.deselectGroups
        return {'FINISHED'}

bpy.props.StringProperty()
class Edger(bpy.types.Operator):
    """Lock vertices on edge"""
    bl_idname = "wm.edger"
    bl_label = "Edger"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    _timer = None
    
    def modal(self, context, event):
        if bpy.types.Scene.isEdgerRunning is False:
            return self.cancel(context)
        
        if event.type == 'TIMER':
            if context.object is None:
                return {'PASS_THROUGH'}
            
            if context.object.mode == "EDIT":
                global isEditMode
                obj = context.object
                me = obj.data
                bm = bmesh.from_edit_mesh(me)
                global groupVerts, adjInfos
                
                if isEditMode is False:
                    isEditMode = True
                    ReInit()
                
                me.update()
                    
                if context.scene.isEdgerActive is False:
                    return {'PASS_THROUGH'}
                
                if context.scene.deselectGroups:
                    DeselectGroups(adjInfos)
                if context.scene.isSelectFlush is False:
                    bm.select_flush(False)
                LockVertsOnEdge(adjInfos)
               
            else:
                isEditMode = False

        return {'PASS_THROUGH'}

    def execute(self, context):
        self._timer = context.window_manager.event_timer_add(0.03, context.window)
        
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

        return {'CANCELLED'}
        

#addon_keymaps = []
#def menu_func_edger(self, context): self.layout.operator(Edger.bl_idname)

class EdgerPanel(bpy.types.Panel):
    """Edger Panel"""
    bl_label = "Edger"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'   #TODO
    def draw(self, context):
        layout = self.layout
        row = layout.row()          
 
        if(bpy.types.Scene.isEdgerRunning):
            #row.prop(context.scene, 'isEdgerActive')
            
            ic = "UNLOCKED"
            if bpy.types.Scene.isEdgerActive:
                ic = "LOCKED"
            row.operator(ToggleLocking.bl_idname, text="Lock", icon=ic)
            
            ic = "RESTRICT_SELECT_OFF"
            if bpy.types.Scene.deselectGroups:
                ic = "RESTRICT_SELECT_ON"
            row.operator(ToggleDeselecting.bl_idname, text="Deselect", icon=ic)
            
            row = layout.row()
            row.prop(context.scene, 'isEdgerDebugActive')
            row.prop(context.scene, 'isSelectFlush')
        
            #row = layout.row()
            #row.label(text="")
            split = layout.split()
            col = split.column(align=True)
            #col.operator(UnselectableVertices.bl_idname, text="Unselectable", icon = "RESTRICT_SELECT_ON")
            #row.label(text="Edgeloops")
            row = layout.row()
            sub = row.row(align=True)
            sub.operator(LockEdgeLoop.bl_idname, text="Add", icon = "ZOOMIN")
            sub.operator(UnlockEdgeLoop.bl_idname, text="Remove", icon = "ZOOMOUT")
            
            row = layout.row()
            row.operator(ClearEdgerLoops.bl_idname, text="Clear Loops", icon = "MOD_SOLIDIFY")
            row = layout.row()
            row.label(text="")
            row.operator(ToggleEdger.bl_idname, text="stop", icon = "X_VEC")
        else:
            row = layout.row();row.label(text="")
            row = layout.row();row.label(text="")
            row = layout.row();row.label(text="")
            row = layout.row();row.label(text="")
            row = layout.row()
            row.operator(ToggleEdger.bl_idname, text="Run", icon = "POSE_HLT")    
            row.label(text="")            
          
        
            
        
#handle the keymap
#wm = bpy.context.window_manager
#km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
#kmi = km.keymap_items.new(UvSquaresByShape.bl_idname, 'E', 'PRESS', alt=True)
#addon_keymaps.append((km, kmi))

def register():
    bpy.utils.register_class(Edger)
    bpy.utils.register_class(ToggleEdger)
    #bpy.utils.register_class(EdgerFunc1)
    bpy.utils.register_class(LockEdgeLoop)
    bpy.utils.register_class(ToggleDeselecting)
    bpy.utils.register_class(ToggleLocking)
    bpy.utils.register_class(UnlockEdgeLoop)
    bpy.utils.register_class(ClearEdgerLoops)
    bpy.utils.register_class(UnselectableVertices)
    bpy.utils.register_class(EdgerPanel)

def unregister():
    try: bpy.utils.unregister_class(Edger)
    except RuntimeError: pass
    bpy.utils.unregister_class(ToggleEdger)
    #bpy.utils.unregister_class(EdgerFunc1)
    bpy.utils.unregister_class(LockEdgeLoop)
    bpy.utils.unregister_class(ToggleDeselecting)
    bpy.utils.unregister_class(ToggleLocking)
    bpy.utils.unregister_class(UnlockEdgeLoop)
    bpy.utils.unregister_class(ClearEdgerLoops)
    bpy.utils.unregister_class(UnselectableVertices)
    bpy.utils.unregister_class(EdgerPanel)

if __name__ == "__main__":
    register()
