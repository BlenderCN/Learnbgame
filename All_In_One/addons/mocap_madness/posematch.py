import bpy
from bpy.props import (CollectionProperty,
                       FloatProperty,
                       StringProperty,
                       PointerProperty,
                       BoolProperty,
                       IntProperty,
                       EnumProperty)

from bpy.types import PropertyGroup
from mathutils import Vector, Matrix


from .utils import (bbox_diagonal,
                    bbox_from_diagonal,
                    bbox_rig,
                    bbox_rig_vector,
                    global_bbox,
                    AddHipLocator)


def cull_matches(self, context):
    scene = context.scene
    matches = [o for o in scene.objects
               if "match_action" in o.keys()
               and o["match"] > scene.pose_match.match
               and o.parent["Matches"] == scene.pose_match.rig]
    for ob in matches:
        ob.parent = None
        ob.animation_data_clear()
        ob.use_fake_user = False
        scene.objects.unlink(ob)
        if ob.users == 0:
            bpy.data.objects.remove(ob)


prop_dic = {"name": StringProperty()}
SceneRigs = type("SceneRigs", (PropertyGroup,), prop_dic)
bpy.utils.register_class(SceneRigs)
bpy.types.Scene.rigs = CollectionProperty(type=SceneRigs)


prop_dic = {"b1": FloatProperty(min=0, max=3.2, unit='ROTATION'),
            "name": StringProperty()
           }

BoneRot = type("BoneRot", (PropertyGroup,), prop_dic)
bpy.utils.register_class(BoneRot)


method = EnumProperty(
        name="Pose Match Method",
        description="Choose Way to Match Poses",
        items=(('BBOX', "Bound Box", "Compare Bounding Boxes (Fastest)"),
               ('BONE_DRIVER',
                "Bone Drivers",
                "Set Up Bone Drivers"),
               ('BONE_DRIVER_VIS',
                "Visual Bone Drivers",
                "Set Up Bone Drivers"),
               ),
        default='BBOX',
        )

func = EnumProperty(
        name="Driver Method",
        description="Calculate Using",
        items=(('SUM', "Sum", "Minimise sum of drivers"),
               ('AVERAGE', "Average", "Minimise average of drivers"),
               ('MAX', "Maximum", "Minimimise Maximum"),
               ),
        default='MAX',
        )

driver_var_type = EnumProperty(
        name="Compare",
        description="Choose Way to Match Poses",
        items=(('ROTATION_DIFF',
                "Rotational Difference",
                "Compare the Rotational Difference of bones"),
               ('LOC_DIFF',
                "Bone Distance",
                "Compare the distance between Bones"),
               ),
        default='LOC_DIFF',
        )

prop_dic = {"match": FloatProperty(min=0.0,
                          max=30.0,
                          default=10.0,
                          description="Match Tolerance, lower = better match",
                          options={'SKIP_SAVE'},
                          update=cull_matches),
            "matches": IntProperty(min=2, max=10, default=10, step=2),
            "use_delta_loc": BoolProperty(default=False),
            "delta_loc": FloatProperty(min=-1.0, default=0.1, unit='LENGTH'),
            "rig": StringProperty(),
            "dupe": StringProperty(),
            "action1": StringProperty(),
            "action2": StringProperty(),
            "method": method,
            "func": func,
            "driver_var_type": driver_var_type,
            "name": StringProperty(),
            "pause": BoolProperty(default=False),
            "percent": IntProperty(default=0, min=0, max=100),
            "timers": IntProperty(min=0, default=0),
           }
PoseMatch = type("PoseMatch", (PropertyGroup,), prop_dic)
bpy.utils.register_class(PoseMatch)

bpy.types.Scene.bones = CollectionProperty(type=BoneRot)
bpy.types.Scene.pose_match = PointerProperty(type=PoseMatch)


class PoseMatchPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Pose Matching"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "BVH"

    @classmethod
    def poll(cls, context):
        if context.object is None:
            return False
        if context.object.type == 'ARMATURE':
            return True

    def draw(self, context):
        context.region.tag_redraw()
        layout = self.layout

        scene = context.scene
        pm = scene.pose_match

        if pm.timers and pm.method.endswith("_VIS"):
            bones = scene.bones
            col = layout.column(align=True)
            col.scale_y = 0.4
            #tot = 0
            for b in bones:
                #row = layout.row()
                #row.scale_y = 0.5
                #tot += b.b1
                col.prop(b, "b1", slider=True, text=b.name)

        # show a percent slider for how far
        if pm.timers:
            row = layout.row()
            row.scale_y = 0.4
            #row.alert = True
            row.prop(scene.pose_match, "percent", slider=True, text="%")
        layout.operator("wm.modal_timer_operator")
        layout.operator("object.simple_operator")
        layout.prop(scene.pose_match, "match")
        layout.prop(scene.pose_match, "rig")
        layout.prop(scene.pose_match, "matches")
        layout.prop(scene.pose_match, "delta_loc")
        layout.prop(scene.pose_match, "action1")

        arm = context.object.data
        #arm = scene.objects.get(scene.pose_match.rig).data
        layout.prop_search(scene.pose_match,
                        "action1",
                        arm,
                        "actions",
                        icon='ACTION',
                        text="Action1")
        layout.prop(scene.pose_match, "action2")
        layout.prop_search(scene.pose_match,
                        "action2",
                        arm,
                        "actions",
                        icon='ACTION',
                        text="Action2")
        layout.prop(scene.pose_match, "timers")
        layout.prop(scene.pose_match, "method")
        layout.prop(scene.pose_match, "func")
        layout.prop(scene.pose_match, "driver_var_type")
        layout.prop(scene.pose_match, "pause", toggle=True)

        if "tot" in scene.keys():
            layout.prop(scene, '["tot"]')
        #layout.label("TOT: %3.1f" % tot)
        #if tot < 10:
            #print("under 10 at frame:", scene.frame_current, " (", tot, ")")


def bone(op, scene):
    if scene.pose_match.pause:
        return False
    bones = scene.bones

    # offer selection of
    # visual drivers all bones
    # same but grouped
    # single all encompassing driver using SUM

    ob = op.rig
    action = ob.animation_data.action
    dupe = op.dupe

    #ob = scene.objects.get("16_01")
    #dupe = scene.objects.get("16_01.001")
    strip = op.strip

    tot = 100000
    if strip.action.name == ob.animation_data.action.name:
        if abs(scene.frame_current - strip.action_frame_end) >= 20:
            if scene.pose_match.method == 'BBOX':
                tot = (bbox_rig_vector(ob) - op.dupe_bbox).length
            if scene.pose_match.method == 'BONE_DRIVER':
                tot = scene["tot"]
            if scene.pose_match.method == 'BONE_DRIVER_VIS':
                tot = sum([b.b1 for b in scene.bones])

    if tot < scene.pose_match.match:
        #print("TOT:", tot)
        #op.wait = True

        # look for matches within small distance

        h = ob.pose.bones['Hips']
        loc = h.location
        sf = ob.scale.x
        if scene.pose_match.delta_loc > 0:
            matches = [m for m in op.mt.children
                       if m.users > 0
                       #and m["action_frame"] in list(range(af-5, af+1))
                       and (m.pose.bones["Hips"].location - loc).length
                            < scene.pose_match.delta_loc / sf]
            if len(matches):
                #print("LEN MATCHES", len(matches))
                #print(matches)
                matches.sort(key=lambda x: x["match"])
                # delete all but the best
                if matches[0]["match"] < tot:
                    return False
                #print(matches)
                for o in matches:
                    #print("del", o.name, o["action_frame"], o["match_frame"])
                    o.parent = None
                    scene.objects.unlink(o)
                    #o["match"] = scene.pose_match.match

        dupe2 = dupe.copy()
        dupe2.hide = False
        dupe2.hide_select = False
        # remove custom props
        for prop in dupe2.keys():
            del dupe2[prop]

        scene.objects.link(dupe2)
        dupe2.name = "[%06.3f]" % tot

        af = int(strip.action_frame_start)
        mf = scene.frame_current
        dupe2["match"] = tot

        dupe2["action_frame"] = af
        dupe2["action"] = strip.action.name
        dupe2["match_action"] = action.name
        dupe2["match_frame"] = mf

        dupe2.parent = op.mt

        hips = dupe2.pose.bones['Hips']

        #loc = AddHipLocator(dupe2, hips)
        #scene.update()
        #print("adding hiploc")

        #print("setting hips on ", dupe2.name)

        for c in hips.constraints:
            hips.constraints.remove(c)
        hips.matrix_basis = h.matrix_basis.copy()
        #hips.matrix = h.matrix.copy()
        dupe2.animation_data_clear()
        '''
        hips.keyframe_insert('location', options={'INSERTKEY_VISUAL'})
        dupe2.rotation_mode = 'QUATERNION'
        hips.keyframe_insert('rotation_quaternion',
                              options={'INSERTKEY_VISUAL'})

        # code to add a hip locator instead of armature copy
        loc = AddHipLocator(ob, h)

        loc.matrix_local = loc.matrix_world
        for c in loc.constraints:
            loc.constraints.remove(c)
        print(scene.frame_current, ":", tot)
        op.wait = False

        # remove matches that are similar to current
        matches = [m for m in op.mt.children
                   if m.users > 0
                   #and m["action_frame"] in list(range(af-5, af+1))
                   and m["match_frame"] in list(range(mf-1, mf+1))
                  ]
        if len(matches) > 1:
            print("LEN MATCHES", len(matches))
            #print(matches)
            matches.sort(key=lambda x: x["match"])
            # delete all but the best
            matches.pop(0)
            #print(matches)
            for o in matches:
                print("del", o.name, o["action_frame"], o["match_frame"])
                o.parent = None
                scene.objects.unlink(o)
                #o["match"] = scene.pose_match.match

        '''

        # keep list to 10 matches
        matches = [m["match"]
                   for m in op.mt.children
                   if m.users > 0
                   ]
        #print("LEN MATCHES", len(matches))
        keep = scene.pose_match.matches
        if len(matches) > keep:
            matches.sort()
            #print("10th", matches[keep - 1])
            scene.pose_match.match = matches[keep - 1]
        #op.mt.name = "Matches (%s)" % len(op.mt.children)

    # if at end frame then click up the NLA
    # QUICK HACK TO CHECK
    if scene.frame_current >= int(action.frame_range[1] / 2):
        #bpy.ops.wm.redraw_timer(type='DRAW_WIN')
        scene.pose_match.percent = 100 * strip.action_frame_start / action.frame_range.length
        strip.action_frame_end += 1
        strip.action_frame_start += 1

        scene.frame_set(action.frame_range[0])
        if scene.pose_match.method == 'BBOX':
            op.dupe_bbox = bbox_rig_vector(dupe)
        if strip.action_frame_start > strip.action.frame_range[1]:
            scene.pose_match.pause = True


def set_up_simulation(operator, scene):
    #operator = operator.__class__
    # set up the action lists
    # put rna checking in the poll method. (both ops)
    operator.rig = rig = scene.objects.active

    scene.pose_match.rig = rig.name
    #print("RIG", rig)
    if rig is None:
        # ABORT
        pass
    arm = rig.data
    actions = arm.actions
    #print(actions)
    action = rig.animation_data.action

    dupe = rig.copy()
    scene.objects.link(dupe)
    dupe["dupe"] = True
    dupe.hide = True
    dupe.hide_select = True
    scene.pose_match.dupe = dupe.name

    #del dupe.data["bvh_import_settings"]
    #remove the actions list from dupe
    dupe["actions"] = []

    dupe.animation_data.action = None
    dupetrack = dupe.animation_data.nla_tracks.new()
    dupetrack.name = "DupeTrack"
    # QUICK HACK TO CHECK
    if scene.pose_match.action1 == scene.pose_match.action2:
        start = action.frame_range[1] / 2
    else:
        start = action.frame_range[0]
        action = bpy.data.actions.get(scene.pose_match.action2)

    dupestrip = dupetrack.strips.new("DupeStrip", 1, action)
    dupestrip.name = "DupeStrip"

    dupestrip.action_frame_start = dupestrip.action_frame_end = int(start)
    dupestrip.scale = 1.0

    scene.pose_match.rig = rig.name
    scene.pose_match.action1 = rig.animation_data.action.name
    scene.pose_match.action2 = dupestrip.action.name

    operator.dupe = dupe
    operator.strip = dupestrip
    for bg in scene.bones:
        bg.driver_remove('b1')

    for bg in scene.bones:
        scene.bones.remove(0)

    if "tot" in scene.keys():
        scene.driver_remove('["tot"]')

    if scene.pose_match.method.startswith('BONE_DRIVER'):
        # ignore the parent bone and zlb's
        bones = [b for b in rig.pose.bones
                 if b.parent is not None
                 ]
        # remove old drivers
        if scene.pose_match.method == 'BONE_DRIVER_VIS':

            for b in bones:
                #pb = ob.pose.bones.get(b["bvh"])
                bg = scene.bones.add()
                bg.name = b.name
                d = bg.driver_add("b1").driver

                v = d.variables.get("bone1", d.variables.new())
                v.name = b.name
                v.type = scene.pose_match.driver_var_type

                # double boner
                v.targets[0].id = rig
                v.targets[0].bone_target = b.name
                v.targets[1].id = dupe
                v.targets[1].bone_target = b.name
                d.expression = "abs(%s)" % v.name
        elif scene.pose_match.method == 'BONE_DRIVER':
            scene["tot"] = 0.0

            tot_driver = scene.driver_add('["tot"]').driver
            tot_driver.type = scene.pose_match.func
            for b in bones:
                #pb = ob.pose.bones.get(b["bvh"])
                bg = scene.bones.add()
                bg.name = b.name
                d = tot_driver
                v = d.variables.get("bone1", d.variables.new())
                v.name = b.name
                v.type = scene.pose_match.driver_var_type

                # double boner
                v.targets[0].id = rig
                v.targets[0].bone_target = b.name
                v.targets[1].id = dupe
                v.targets[1].bone_target = b.name

        # get the angle between them
        #print(angle)

    # add copy transforms constraint

    con = dupe.pose.bones["Hips"].constraints.new(type='COPY_TRANSFORMS')
    con.target = rig
    con.subtarget = "Hips"
    scene.frame_set(1)
    if scene.pose_match.method == 'BBOX':
        operator.dupe_bbox = bbox_rig_vector(dupe)

    return True


def get_holder_empty(scene, key):
    obs = [mt for mt in scene.objects
           if mt.data is None
           and "Matches" in mt.keys()
           and mt["Matches"] == key]
    if len(obs):
        return obs[0]

    mt = bpy.data.objects.new("%s (Pose Match)" % key, None)
    mt["Matches"] = key  # number of matches
    return scene.objects.link(mt).object


class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    _timer = None
    wait = False

    def modal(self, context, event):

        scene = context.scene
        if event.type in {'ESC'} or scene.pose_match.pause:
            return self.cancel(context)

        if self.wait:
            return {'PASS_THROUGH'}

        if event.type == 'TIMER':
            scene = context.scene
            bone(self, scene)
            scene.frame_set(scene.frame_current + 1)

        return {'PASS_THROUGH'}

    def execute(self, context):
        scene = context.scene

        if not scene.pose_match.timers:
            set_up_simulation(self, scene)
        else:
            scene.pose_match.timers = 0
            self.rig = scene.objects.get(scene.pose_match.rig)
            self.dupe = scene.objects.get(scene.pose_match.dupe)
            self.dupe_bbox = bbox_rig_vector(self.dupe)
            dad = self.dupe.animation_data
            self.strip = dad.nla_tracks["DupeTrack"].strips["DupeStrip"]

        wm = context.window_manager
        scene.pose_match.timers += 1
        #holder empty

        #mt.location = (0,0,0)

        self.mt = get_holder_empty(scene, self.rig.name)
        self._timer = wm.event_timer_add(0.01, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        scene = context.scene

        scene.pose_match.timers -= 1
        if scene.pose_match.timers == 0:
            scene.pose_match.pause = False
            if scene.objects.get(self.dupe.name):
                scene.objects.unlink(self.dupe)
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

        return {'CANCELLED'}


class PoseMatch(bpy.types.Operator):
    """Operator to do the matching non modal"""
    bl_idname = "object.simple_operator"
    bl_label = "Simple Object Operator"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        scene = context.scene
        scene.pose_match.pause = False
        scene.frame_set(1)
        #holder empty

        set_up_simulation(self, scene)
        self.mt = get_holder_empty(scene, self.rig.name)
        action = self.rig.animation_data.action

        while not scene.pose_match.pause:
            bone(self, scene)

            scene.frame_set(scene.frame_current + 1)

        # clean up
        if scene.objects.get(self.dupe.name):
            scene.objects.unlink(self.dupe)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(PoseMatchPanel)
    bpy.utils.register_class(ModalTimerOperator)
    bpy.utils.register_class(PoseMatch)


def unregister():
    bpy.utils.unregister_class(PoseMatchPanel)
    bpy.utils.unregister_class(ModalTimerOperator)
    bpy.utils.unregister_class(PoseMatch)
