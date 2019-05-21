bl_info = {
    "name": "Ramp Object",
    "category": "Object"
}

import bpy
import bmesh
import math
import mathutils
from functools import reduce
import pprint
import time

SHOULD_LOG = False
SHOULD_UPDATE_SLOWLY = False
SLOW_UPDATE_DELAY = 0.5 # seconds

class RampObject(bpy.types.Operator):
    """Ramp Object"""
    bl_idname = "object.ramp_object"
    bl_label = "Ramp Object"
    bl_options = {'REGISTER', 'UNDO'}

    platformWidth = bpy.props.FloatProperty(name="Platform Width", default=1, min=0.5, max=100)
    rampHeight = bpy.props.FloatProperty(name="Ramp Height", default=2, min=1, max=100)
    rampWidth = bpy.props.FloatProperty(name="Ramp Width", default=4, min=1, max=100)
    rampLength = bpy.props.FloatProperty(name="Ramp Length", default=4, min=1, max=100)
    rampMaxInclination = bpy.props.FloatProperty(name="Max Inclination", default=60, min=0, max=120)
    # ease = bpy.props.FloatProperty(name="Ease", default=5, min=0, max=10)
    # curveVerticalOffsetScale = bpy.props.FloatProperty(name="Offset Scale", default=0.05, min=0.0, max=0.5)
    curveVerticalOffsetScale = 0.0


    def execute(self, context):
        debugLog('\n------Script Start------\n')

        scene = context.scene
        cursor = scene.cursor_location

        debugLog('create curve...')
        bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=True)
        straightCurveObject = context.object

        debugLog('straighten then lengthen curve...')
        bpy.ops.curve.select_all(action='DESELECT')
        bpy.ops.curve.de_select_first()
        bpy.ops.transform.rotate(value=math.radians(-45), axis=[0, 0, 1])
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.transform.resize(value=[self.rampWidth / 2.0, 1, 1])

        debugLog('create curve...')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=True)
        rampCurveObject = context.object

        debugLog('straighten then lengthen curve...')
        bpy.ops.curve.select_all(action='DESELECT')
        bpy.ops.curve.de_select_first()
        bpy.ops.transform.rotate(value=math.radians(-45), axis=[0, 0, 1])
        bpy.ops.transform.resize(value=[(2.85) * (self.rampHeight) / (self.rampLength), 1, 1])
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.transform.resize(value=[self.rampLength / 2.0, 1, 1])

        debugLog('pull up first segment...')
        bpy.ops.curve.select_all(action='DESELECT')
        bpy.ops.curve.de_select_first()
        bpy.ops.transform.rotate(value=math.radians(self.rampMaxInclination), axis=[0, 1, 0])
        bpy.ops.transform.translate(value=[0, 0, self.rampHeight * (1 + self.curveVerticalOffsetScale) / 2 ])

        debugLog('pull down second segment...')
        bpy.ops.curve.select_all(action='DESELECT')
        bpy.ops.curve.de_select_last()
        bpy.ops.transform.translate(value=[0, 0, -self.rampHeight * (1 + self.curveVerticalOffsetScale) / 2])

        debugLog('set straight curve as bevel object of ramp curve...')
        rampCurveObject.data.bevel_object = straightCurveObject

        debugLog('convert ramp curve to mesh and delete straight curve...')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.shade_flat()
        bpy.ops.object.select_all(action='DESELECT')
        straightCurveObject.select = True
        bpy.ops.object.delete()

        debugLog('perform limited dissolve on ramp mesh...')
        rampCurveObject.select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.dissolve_limited(angle_limit=math.radians(0.05))

        debugLog('enter edge select mode and grab reference to ramp BMesh...')
        bpy.ops.mesh.select_mode(type='EDGE')
        rampBm = bmesh.from_edit_mesh(rampCurveObject.data)

        debugLog('select edge with greatest x value...')
        bpy.ops.mesh.select_all(action='DESELECT')
        edgeTuples = bmEdgeSeqToTupleList(rampBm.edges)
        edgeTuplesSorted = sorted(edgeTuples, key=lambda edge: edge[1].x)
        rampBm.edges.ensure_lookup_table()
        rampBm.edges[edgeTuplesSorted[len(edgeTuplesSorted) - 1][0]].select = True

        debugLog('extrude edge along x by rampLength...')
        bpy.ops.mesh.extrude_edges_move(TRANSFORM_OT_translate={'value':(-(self.rampLength + self.platformWidth), 0, 0)})

        debugLog('extrude edge along z by rampHeight...')
        bpy.ops.mesh.extrude_edges_move(TRANSFORM_OT_translate={'value':(0, 0, self.rampHeight)})

        debugLog('select the two edges with greatest z value...')
        bpy.ops.mesh.select_all(action='DESELECT')
        edgeTuples = bmEdgeSeqToTupleList(rampBm.edges)
        edgeTuplesSorted = sorted(edgeTuples, key=lambda edge: edge[1].z)
        rampBm.edges.ensure_lookup_table()
        rampBm.edges[edgeTuplesSorted[len(edgeTuplesSorted) - 1][0]].select = True
        rampBm.edges[edgeTuplesSorted[len(edgeTuplesSorted) - 2][0]].select = True

        debugLog('add face, joining the two edges...')
        bpy.ops.mesh.edge_face_add()

        debugLog('select loop with greatest y value...')
        bpy.ops.mesh.select_all(action='DESELECT')
        edgeTuples = bmEdgeSeqToTupleList(rampBm.edges)
        edgeTuplesSorted = sorted(edgeTuples, key=lambda edge: edge[1].y)
        rampBm.edges.ensure_lookup_table()
        rampBm.edges[edgeTuplesSorted[len(edgeTuplesSorted) - 1][0]].select = True
        bpy.ops.mesh.loop_multi_select()

        debugLog('add face, joining the edge loop...')
        bpy.ops.mesh.edge_face_add()

        debugLog('select loop with lowest y value...')
        bpy.ops.mesh.select_all(action='DESELECT')
        edgeTuples = bmEdgeSeqToTupleList(rampBm.edges)
        edgeTuplesSorted = sorted(edgeTuples, key=lambda edge: edge[1].y)
        rampBm.edges.ensure_lookup_table()
        rampBm.edges[edgeTuplesSorted[0][0]].select = True
        bpy.ops.mesh.loop_multi_select()

        debugLog('add face, joining the edge loop...')
        bpy.ops.mesh.edge_face_add()

        # debugLog('enter object mode...')
        bpy.ops.object.mode_set(mode='OBJECT')

        debugLog('\n------Script End------')

        # TODO: set shading to flat
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(something)

        return {'FINISHED'}

def bmEdgeSeqToTupleList(edgeSeq):
    return list(map(lambda edge: (edge.index, reduce(lambda acc,vert: acc + vert.co, edge.verts, mathutils.Vector((0.0,0.0,0.0))) / len(edge.verts)), edgeSeq))

def menu_func(self, context):
    self.layout.operator(RampObject.bl_idname)

def debugLog(message):
    if(SHOULD_LOG):
        print(message)
    if(SHOULD_UPDATE_SLOWLY):
        time.sleep(SLOW_UPDATE_DELAY)
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

# store keymaps here to access after registration
addon_keymaps = []

def register():
    bpy.utils.register_class(RampObject)
    bpy.types.INFO_MT_add.append(menu_func)

    # handle the keymap
    wm = bpy.context.window_manager
    # Note that in background mode (no GUI available), keyconfigs are not available either, so we have to check this
    # to avoid nasty errors in background case.
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(RampObject.bl_idname, 'SPACE', 'PRESS', ctrl=True, shift=True)
        # kmi.properties.total = 4
        addon_keymaps.append((km, kmi))

def unregister():
    # Note: when unregistering, it's usually good practice to do it in reverse order you registered.
    # Can avoid strange issues like keymap still referring to operators already unregistered...
    # handle the keymap 
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(RampObject)
    bpy.types.INFO_MT_add.remove(menu_func)

if __name__ == "__main__":
    register()