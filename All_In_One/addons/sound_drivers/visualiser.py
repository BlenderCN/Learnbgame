import bpy

from bpy.props import *
from bpy.types import PropertyGroup, Operator, Panel
from bpy.utils import unregister_class, register_class
from mathutils import Vector
from sound_drivers.utils import bbdim, hasparent, selected_bbox,\
                                get_driver_settings, getAction,\
                                driver_expr
from math import sqrt
####################################################
'''
Create a Sound Visualiser.
--------------------------

Create a visualiser from a "unit" object or collections.
All drivers referring to channel 0 of the sound action
will be assigned to channel i for i in 1 to len channels

'''
#########################################################


def FCurve2Curve(holder, fcurve, index, frame_scale, d, use_radius):
    f_i = index
    c = fcurve
    sam = c.sampled_points
    ch = c.data_path.strip('[""]')
    mt = bpy.data.objects.new(ch, None)
    cu = bpy.data.curves.new('path', 'CURVE')
    cu.dimensions = '3D'
    if use_radius:
        cu.fill_mode = 'FULL'
        cu.bevel_resolution = 10
        cu.bevel_depth = 1
    spline = cu.splines.new('BEZIER')
    spline.bezier_points.add(len(sam) - 1)
    curva = bpy.data.objects.new('curve', cu)
    bpy.context.scene.objects.link(curva)
    bpy.context.scene.objects.link(mt)
    curva.parent = mt
    mt.parent = holder
    mt.location.x += f_i * d
    for i in range(len(sam)):
        '''
        if i > 20:
            continue
        '''
        w = spline.bezier_points[i]
        y = c.evaluate(sam[i].co[0])
        if use_radius:
            w.radius = y
            y = 0
        coords = (0, frame_scale * sam[i].co[0], y)
        w.co = w.handle_left = w.handle_right = coords


def CurveVis(context, action, use_radius=False, frame_scale=1.0, d=1):
    holder = bpy.data.objects.new("VIS:%s" % action.name, None)
    holder["VIS"] = 'CURVESURFACE'
    holder['_RNA_UI'] = {}
    rna = {"d": d, "frame_scale": frame_scale, "description": "Curves from %s" %
       action.name}
    holder['_RNA_UI']["VIS"] = rna
    context.scene.objects.link(holder)

    for f_i, fcurve in enumerate(action.fcurves):
        FCurve2Curve(holder, fcurve, f_i, frame_scale, d, use_radius)

    bpy.ops.object.select_all(action='DESELECT')
    context.scene.objects.active = holder
    holder.select = True


def rechannel_visualiser(handle, context, from_channel, to_channel):
    # select all the underlings
    # print("RECHANNEL TEST", from_channel, to_channel)
    select_visualiser(handle, context)

    dns = bpy.app.driver_namespace
    dm = dns.get("DriverManager")
    drivers_list = [d for d in dm.all_drivers_list if d.driven_object.id_data in context.selected_objects]

    for d in drivers_list:
        expr = d.fcurve.driver.expression
        d.fcurve.driver.expression = expr.replace(from_channel, to_channel)

    var_list = [v for d in drivers_list for v in d.fcurve.driver.variables if v.name.startswith(from_channel)]
    '''
    need to change var name
    targets.datapath
    driver.expression
    '''
    for v in var_list:
        v.name = v.name.replace(from_channel, to_channel)
        for t in v.targets:
            t.data_path = t.data_path.replace(from_channel, to_channel)


def retarget_visualiser(handle, context, from_target, to_target):
    # select all the underlings
    select_visualiser(handle, context)
    for obj in context.selected_objects:

        if hasattr(obj, "animation_data") and obj.animation_data is not None:
            targets = [t for d in obj.animation_data.drivers
                       for v in d.driver.variables
                       for t in v.targets
                       if t.id == from_target]
            if len(targets):
                print(obj.name, len(targets), "... reTargetting")
            for t in targets:
                t.id = to_target


# make a sliding visualiser
# sp_copy = copy speaker
# vis_copy = copy visualiser
# retarget all drivers in copy vis to from speaker to copy_speaker
# drop the animation into NLA
# slide the starting point accordingly
# recursively find all the children in the visualiser


def select_visualiser(handle, context):
    scene = context.scene
    # deselect all
    bpy.ops.object.select_all(action='DESELECT')
    scene.objects.active = handle
    bpy.ops.object.select_grouped(extend=False, type='CHILDREN_RECURSIVE')
    handle.select = True
    # ok this is all the objects in the visualiser


def revert_visualiser(handle, context):
    for child in handle.children:
        if child["ST_Vis"] == 0:
            first_child = child
            break
    scene = context.scene
    scene.objects.active = child
    # TODO fix for when vis is in a diffent layer
    bpy.ops.object.select_grouped(extend=False, type='CHILDREN_RECURSIVE')
    sel_objs = [o for o in context.selected_objects]
    select_visualiser(handle, context)
    for o in sel_objs:
        o.select = False
    bpy.ops.object.delete()
    for o in sel_objs:
        o.select = True
    scene.objects.active = sel_objs[0]
    # scene update and tag_redraw no good..
    # hence this silly code.
    for o in sel_objs:
        o.location = o.location


def delete_visualiser(handle, context):
    scene = context.scene

    select_visualiser(handle, context)
    bpy.ops.object.delete()


def copy_visualiser(handle, context):
    # dupe the handle
    select_visualiser(handle, context)
    bpy.ops.object.duplicate()
    for ob in context.selected_objects:
        if ob != context.active_object:
            ob.select = False


class Visualiser:

    def __init__(self):
        pass

class CreateSoundVisualiserPanel(Panel):
    """Create a sound visualiser from baked sound"""
    bl_category = "SoundDrive"
    bl_label = "Visualisers"
    bl_idname = "SPEAKER_PT_createvisualiserpanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    @classmethod
    def poll(cls, context):
        sp = context.scene.speaker
        # need an action to generate this kind from
        return sp is not None\
                and getAction(sp) is not None\
                and context.object is not None\


    def retarget_draw(self, ob, context):
        handle = ob
        rna = handle["_RNA_UI"]["VIS"].to_dict()
        layout = self.layout

        visualiser = context.scene.visualisers.grids.get(rna["name"])
        if visualiser is None:
            return
        row = layout.row()
        row.prop(visualiser, "from_channel")
        row.prop(visualiser, "to_channel")
        row = layout.row()
        row.prop(visualiser, "from_target")
        row.prop(visualiser, "to_target")
        op = layout.operator("visualiser.edit", text="ReChannel")
        op.func = "rechannel"
        op.from_channel = visualiser.from_channel
        op.to_channel = visualiser.to_channel

    def curvesurface_draw(self, layout, context):
        handle = context.object
        layout.prop(handle, '["VIS"]', text="", icon='OUTLINER_OB_CURVE')
        layout.enabled = False

    def grid_draw(self, layout, context):
        handle = context.object
        rna = handle["_RNA_UI"]["VIS"].to_dict()
        rows = rna["rows"]
        cols = rna["cols"]
        # look for a grid
        grid = context.scene.visualisers.grids.get(rna["name"])
        if grid is None:
            layout.row().label("XXX")
            return
        row = layout.row(align=True)
        wm = context.window_manager
        split = row.split(percentage=0.3, align=True)
        split.prop(wm, "visualiser_type", text="")
        split.prop(grid, "name", text="")
        if grid is None:
            layout.label("ERROR", icon='ERROR')
            return None
        layout.label("Rows x Cols")
        layout.menu("visualiser.rows_columns", text="%d x %d" % (rows, cols))
        row = layout.row()
        col = row.column()
        col.prop(grid, "offset")
        col = row.column()
        col.prop(handle, "scale")

    def edit_draw(self, ob, context):
        layout = self.layout
        # funcs = ["select", "copy", "delete", "retarget"]
        # going to make this a menu for better labelling
        funcs = ["select", "copy", "delete", "revert"]
        row = layout.row(align=True)
        split = row.split(percentage=0.2)
        func_col = split.column()
        func_col.alignment = 'LEFT'
        func_col.menu("visualiser.functions")
        vis_col = split.column()

        vis_type = ob["VIS"]
        if vis_type == 'GRID':
            self.grid_draw(vis_col, context)
        elif vis_type == 'CURVESURFACE':
            self.curvesurface_draw(vis_col, context)

    def draw(self, context):
        wm = context.window_manager
        scene = context.scene
        a = getAction(context.scene.speaker)
        channels = a["Channels"]
        ob = context.object
        VisualiserRowsColumns.channels = channels
        if "VIS" in ob.keys():
            self.edit_draw(ob, context)
            self.retarget_draw(ob, context)
            row = self.layout.row()
            row.operator("sounddriver.create_visualiser")
            return

        n = channels
        # rcs = [(x, n/x) for x in range(1, int(sqrt(n))+1) if n % x == 0]
        rcs = [(x, n / x) for x in range(1, n+1) if n % x == 0]

        layout = self.layout
        row = layout.row()
        row.prop(wm, "visualiser_type")
        row = layout.row()
        col = row.column()
        '''
        col.label("TEST")

        for obj in context.selected_objects:
            orow = col.row()
            orow.label(obj.name)
        '''
        col = row.column()
        row = col.row()

        scene = context.scene
        if wm.visualiser_type == "GRID":
            col.menu("visualiser.rows_columns", text="Rows x Cols")

        elif wm.visualiser_type == "SOUNDSURFACE":
            row = layout.row()
            row.label("NIY: Not Implemented Yet")

        if wm.visualiser_type == "CURVESURFACE":
            actions = [a for a in bpy.data.actions if 'wavfile' in a.keys()]
            for a in actions:
                row = layout.row()
                txt = "%s %s channels:%d" % (a.name,
                                             a["channel_name"],
                                             a["Channels"])

                op = row.operator("soundaction.create_visualiser", text=txt)
                op.type = 'CURVESURFACE'
                op.action = a.name
# Operators
'''
----------------------------------------------
CreateSoundVisualiser
----------------------------------------------
'''


class ActionVisualiser(Operator):
    ''' Create Visualiser From Action '''
    bl_idname = "soundaction.create_visualiser"
    bl_label = "Action Visualiser"
    action = StringProperty(default="", options={'SKIP_SAVE'})
    type = StringProperty(default="", options={'SKIP_SAVE'})

    @classmethod
    def poll(self, context):
        return len(context.scene.soundspeakers)

    # Will refactor to modal timer op to show progress.
    def execute(self, context):
        action = bpy.data.actions.get(self.action)
        if self.type == 'CURVESURFACE':
            CurveVis(context, action, use_radius=False, frame_scale=1.0, d=1)
            return {'FINISHED'}
        return {'CANCELLED'}


class VisualiserEdit(Operator):
    ''' Edit Visualiser '''
    bl_idname = "visualiser.edit"
    bl_label = "Edit Visualiser"
    # Make ENUM [copy, select, retarget, delete]
    func = StringProperty(default="", options={'SKIP_SAVE'})
    from_target = StringProperty(default="", options={'SKIP_SAVE'})
    to_target = StringProperty(default="", options={'SKIP_SAVE'})
    from_channel = StringProperty(default="", options={'SKIP_SAVE'})
    to_channel = StringProperty(default="", options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        ob = context.object
        # no selected objects if in different layer.
        return context.selected_objects and "VIS" in ob.keys()

    def execute(self, context):
        handle = context.object
        if self.func == "select":
            select_visualiser(handle, context)

        elif self.func == "copy":
            copy_visualiser(handle, context)
        elif self.func == "delete":
            visobjs = [ob for ob in context.selected_objects
                       if "VIS" in ob.keys()]
            for vo in visobjs:
                delete_visualiser(vo, context)
        elif self.func == "retarget":
            retarget_visualiser(handle, context, self.from_target,
                                self.to_target)
        elif self.func == "rechannel":
            rechannel_visualiser(handle, context, self.from_channel,
                                self.to_channel)
        elif self.func == "revert":
            revert_visualiser(handle, context)
        else:
            print("op did nothing")
        return {'FINISHED'}

# update methods for grid vis


def re_offset(self, context):
    # self is the grid ui
    # the visualise will be context.object
    # the grids children will have index in ["ST_Vis"]

    # move all the kiddies to local(0,0,0)
    # this will be the location of the original unit.(good)

    handle = context.object
    rna = handle["_RNA_UI"]["VIS"]
    rows = self.rows
    cols = self.cols
    channels = rows * cols
    dimensions = Vector([rna["dimensions"][axis] for axis in "xyz"])
    print("REOFFSET", rna["dimensions"].items(), dimensions, self.offset)
    offset = Vector(self.offset)

    delta = Vector((rows * (dimensions.x + offset.x) / 2,
                   cols * (dimensions.y + offset.y) / 2, 0))
    loc = Vector()
    for h in handle.children:

        h.location = Vector((0, 0, 0))
        i = h["ST_Vis"]
        row = i // cols
        col = i % cols
        v = Vector((row, col, 0))

        h.location.x += col * offset.x * dimensions.x
        h.location.y += row * offset.y * dimensions.y
        h.location.z += offset.z * dimensions.z
        loc += h.location

    for h in handle.children:
        h.location -= loc/channels
    return None

class CreateSoundVisualiser(Operator):
    """Create Visualiser from Unit"""
    bl_idname = "sounddriver.create_visualiser"
    bl_label = "Create Visualiser"
    # registered ops give me grief.
    # bl_options = {'REGISTER', 'UNDO'}
    rows = IntProperty(default=1, options={'SKIP_SAVE'})
    cols = IntProperty(default=1, options={'SKIP_SAVE'})
    offset = FloatVectorProperty(default=(1.0, 1.0, 0.0), size=3,
                                 options={'SKIP_SAVE'})
    translate = FloatVectorProperty(size=3, options={'SKIP_SAVE'})
    scale = FloatProperty(default=1.0, name="Visualiser Scale",
                          options={'SKIP_SAVE'},
                          description="Scale the Visualiser")

    handle = False
    handle_name = ""

    @classmethod
    def poll(cls, context):
        sp = context.scene.speaker
        # need an action to generate this kind from
        return sp is not None\
               and getAction(sp) is not None

    def draw(self, context):
        a = getAction(context.scene.speaker)

        layout = self.layout
        row = layout.row()
        row.label(a["channel_name"])
        row.label("%d" % a["Channels"])
        col = layout.column()
        col.prop(self, "offset")
        row = layout.row()
        if self.handle:
            handle = bpy.data.objects.get(self.handle_name)
            row.prop(handle, "name")
            row = layout.row()
            col = row.column()
            box = col.box()
            box.label("Scale")
            box.prop(self, "scale", text="")
            col = row.column()
            box = col.box()
            box.label("Translate")
            box.prop(self, "translate", text="")

    def invoke(self, context, event):
        ob = context.object
        if "VIS" in context.object.keys():
            rna = ob['_RNA_UI']["VIS"].to_dict()
            grid = context.scene.visualisers.grids[rna["name"]]
            rna['rows'] = grid.rows = self.rows
            rna['cols'] = grid.cols = self.cols
            ob['_RNA_UI']["VIS"] = rna
            # call the update function
            re_offset(grid, context)
            return {'FINISHED'}

        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        sp = scene.speaker

        scene_objects_set = set(scene.objects)
        obj = context.active_object
        # copy cursor location

        cursor_loc = scene.cursor_location.copy()
        # snap the cursor to the selected

        bpy.ops.view3d.snap_cursor_to_selected()
        channels = self.rows * self.cols

        # bpy.context for testing. Use context from Op, Panel method.

        originals = context.selected_objects.copy()
        # has the selected objects in it.
        c = {}

        c["scene"] = scene
        c["screen"] = context.screen
        c["area"] = context.area
        c["region"] = context.region
        c["active_object"] = None
        c["edit_object"] = None
        c["window"] = context.window
        # c["selected_bases"] = context.selected_bases.copy()
        # c["selected_editable_objects"] = context.selected_editable_objects.copy()
        # c["selected_bases"] = []
        c["selected_objects"] = originals
        dimensions = bbdim(selected_bbox(context))
        # Location of original unit
        location = scene.cursor_location.copy()

        st_handle = bpy.data.objects.new("ST_handle", None)
        st_handle["channels"] = channels
        scene.objects.link(st_handle)

        st_handle.matrix_world.translation = location
        st_handle["ST_Vis"] = 0
        handles = []
        new_objects = set(originals)
        vis = []
        # make duplicates
        for i in range(channels):
            scene.update()
            handle = bpy.data.objects.new("ch[%04d]" % i, None)
            scene.objects.link(handle)

            handle["ST_Vis"] = i  # the channel to drive with.
            handle.parent = st_handle
            handles.append(handle)
            # make the handle the objects parent if no parent else

            if i:
                scene_objects_set = set(scene.objects)
                bpy.ops.object.duplicate(c, 'INVOKE_DEFAULT', linked=False)
                scene.update()
                new_objects = set(scene.objects) - scene_objects_set
            vis.append((i, handle, new_objects))
        for i, handle, new_objects in vis:
            for o in new_objects:
                print(o, o.parent)
                if not o.parent or o.parent in handles:
                    o.parent = handle
                if not i or not o.animation_data:
                    continue  # drivers ok for ch0

                # get the drivers of o
                # have speaker as a var target
                # have CH0 as a variable
                drivers = o.animation_data.drivers
                drivers = [d for d in drivers for v in d.driver.variables for t in v.targets if t.id == sp]
                for d in drivers:
                    all_channels, args = get_driver_settings(d)
                    driver = d.driver
                    expr = driver.expression
                    for ch in all_channels:
                        if len(ch) == 3 and ch.endswith("0"):
                            all_channels.remove(ch)
                            newch = ch.replace("0", str(i))
                            expr = expr.replace(ch, newch)
                            all_channels.append(newch)
                            var = driver.variables.get(ch)
                            var.name = newch
                            var.targets[0].data_path = var.targets[0].data_path.replace(ch, newch)
                    driver.expression = driver_expr(expr,
                                               all_channels,
                                               args)

        # distribute

        # Properties
        rows = self.rows
        cols = self.cols

        offset = Vector(self.offset)
        offset.x = dimensions.x * offset.x
        offset.y = dimensions.y * offset.y
        offset.z = dimensions.z * offset.z

        # deselect all
        bpy.ops.object.select_all(action='DESELECT')
        self.handle = st_handle is not None
        self.handle_name = st_handle.name
        context.scene.objects.active = st_handle
        st_handle.select = True
        st_handle["VIS"] = 'GRID'

        # make an rna and make a grid
        vis_RNA = {
                   "name": self.handle_name,
                   "rows": self.rows,
                   "cols": self.cols,
                   "channels": channels,
                   "offset": {
                              "x": self.offset[0],
                              "y": self.offset[1],
                              "z": self.offset[2]
                              },
                   "dimensions": {
                              "x": dimensions[0],
                              "y": dimensions[1],
                              "z": dimensions[2],
                                }

                  }
        st_handle['_RNA_UI'] = {}
        st_handle['_RNA_UI']["VIS"] = vis_RNA

        # make a new edit item in the grids collection

        grid = context.scene.visualisers.grids.add()
        grid.name = st_handle.name
        grid.rows = self.rows
        grid.cols = self.cols
        grid.offset = self.offset

        return {'FINISHED'}

'''
Menus
'''
class VisualiserFuncMenu(bpy.types.Menu):
    bl_label = "Visualiser Menu"
    bl_idname = "visualiser.functions"

    def draw(self, context):
        handle = context.object
        vis = handle.get('VIS', 'NONE')
        layout = self.layout
        op = layout.operator("visualiser.edit", text="Select Items")
        op.func = "select"
        op = layout.operator("visualiser.edit", text="Copy")
        op.func = "copy"
        op = layout.operator("visualiser.edit", text="Delete")
        op.func = "delete"
        if vis in {'GRID'}:
            op = layout.operator("visualiser.edit", text="Revert to Unit")
            op.func = "revert"


class VisualiserRowsColumns(bpy.types.Menu):
    ''' Set Rows and Columns for Visualiser '''
    bl_label = "Set Visualiser Rows Columns"
    bl_idname = "visualiser.rows_columns"

    def draw(self, context):
        layout = self.layout
        n = self.__class__.channels
        rcs = [(x, n/x) for x in range(1, n+1) if n % x == 0]
        for r, c in rcs:
            row = layout.row()
            op = row.operator("sounddriver.create_visualiser", text="%d x %d" % (r, c))
            op.rows = r
            op.cols = c

def register_visualiser_groups():

    vis = EnumProperty(items=(
            ("GRID", "Grid", "Create Grid Visualiser from Multi Selection"),
            ("SPIRAL", "Spiral", "Spirals, (flat, fibonacci)"),
            ("SOUNDSURFACE", "SoundSurface", "Create Sound Surface Disp Map"),
            ("CURVESURFACE", "Curve Surface", "Create Curves from Action"),
            ),
            name="Visualiser Type",
            default="GRID",
            description="Create Sound Visualisers",
            )

    bpy.types.WindowManager.visualiser_type = vis
    # Visualiser Groups

    # Grid Visualiser

    vis_prop_dic = {}

    from_channel = StringProperty(default="AA")
    to_channel = StringProperty(default="AA")
    from_target = StringProperty(default="None")
    to_target = StringProperty(default="None")
    name = StringProperty(default="Visualiser")

    vis_prop_dic["name"] = name
    vis_prop_dic["from_channel"] = from_channel
    vis_prop_dic["to_channel"] = to_channel
    vis_prop_dic["from_target"] = from_target
    vis_prop_dic["to_target"] = to_target

    scale = FloatProperty(default=1.0, name="Visualiser Scale",
                          options={'SKIP_SAVE'},
                          description="Scale the Visualiser")
    vis_prop_dic["type"] = vis
    vis_prop_dic["scale"] = scale

    rows = IntProperty(default=1, options={'SKIP_SAVE'})
    cols = IntProperty(default=1, options={'SKIP_SAVE'})
    offset = FloatVectorProperty(default=(1.0, 1.0, 0.0), size=3,
                                 options={'SKIP_SAVE'},
                                 update=re_offset)
    translate = FloatVectorProperty(size=3, options={'SKIP_SAVE'})

    prop_dic = vis_prop_dic
    prop_dic["rows"] = rows
    prop_dic["cols"] = cols
    prop_dic["offset"] = offset

    GridVis = type("GridVis", (PropertyGroup,), prop_dic)
    register_class(GridVis)

    prop_dic = {}
    prop_dic["grids"] = CollectionProperty(type=GridVis)

    Visualisers = type("Visualisers", (PropertyGroup,), prop_dic)
    register_class(Visualisers)

    bpy.types.Scene.visualisers = PointerProperty(type=Visualisers)

def register():
    register_visualiser_groups()
    # Operators
    register_class(CreateSoundVisualiser)
    register_class(ActionVisualiser)
    register_class(VisualiserEdit)
    # Panels
    register_class(CreateSoundVisualiserPanel)
    # Menus
    register_class(VisualiserFuncMenu)
    register_class(VisualiserRowsColumns)

def unregister():
    # Operators
    unregister_class(CreateSoundVisualiser)
    unregister_class(ActionVisualiser)
    unregister_class(VisualiserEdit)
    # Panels
    unregister_class(CreateSoundVisualiserPanel)
    # Menus
    unregister_class(VisualiserFuncMenu)
    unregister_class(VisualiserRowsColumns)

if __name__ == "__main__":
    register()
