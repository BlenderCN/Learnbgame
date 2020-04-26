import bpy
import bmesh
from mathutils import Vector, Matrix
import gpu
from gpu_extras.batch import batch_for_shader
import bgl
from .. utils.decal import apply_decal, set_defaults, get_target
from .. utils.modifier import add_displace, add_nrmtransfer, get_displace, add_subd, add_shrinkwrap, get_subd, get_shrinkwrap, get_mods_as_dict, add_mods_from_dict
from .. utils.raycast import get_origin_from_object_boundingbox
from .. utils.mesh import hide, unhide, blast, smooth
from .. utils.object import intersect, flatten, parent, update_local_view, lock, unshrinkwrap
from .. utils.math import remap, create_bbox, flatten_matrix
from .. utils.raycast import get_bvh_ray_distance_from_verts
from .. utils.ui import popup_message, wrap_mouse
from .. utils.collection import unlink_object
from .. utils.addon import gp_add_to_edit_mode_group


class Project(bpy.types.Operator):
    bl_idname = "machin3.project_decal"
    bl_label = "MACHIN3: Project Decal"
    bl_description = "Project Selected Decals on Surface\nALT: Manually Adjust Projection Depth\nCTRL: Use UV Project instead of UV Transfer\nSHIFT: Shrinkwrap"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return any(obj.DM.isdecal and not obj.DM.isprojected and not obj.DM.issliced for obj in context.selected_objects)

    def draw(self, context):
        layout = self.layout
        col = layout.column()

    def draw_VIEW3D(self, args):
        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        shader.bind()

        bgl.glEnable(bgl.GL_BLEND)
        # bgl.glDepthFunc(bgl.GL_ALWAYS)

        for decal, target, projected, (front, back), bbox in self.projections:
            coords, edge_indices, tri_indices = bbox

            mxcoords = []
            for idx, co in enumerate(coords):
                if idx > 3:
                    mxt = Matrix.Translation((0, 0, (back + abs(self.offset)) / decal.scale.z))
                    mxco = decal.matrix_world @ mxt @ Vector(co)
                else:
                    mxt = Matrix.Translation((0, 0, (-front - abs(self.offset)) / decal.scale.z))
                    mxco = decal.matrix_world @ mxt @ Vector(co)

                mxcoords.append(mxco)

            # bottom and top face lines
            bgl.glLineWidth(4)
            shader.uniform_float("color", (1, 1, 1, 0.4))
            batch = batch_for_shader(shader, 'LINES', {"pos": mxcoords}, indices=edge_indices[:8])
            batch.draw(shader)

            # side lines
            bgl.glLineWidth(2)
            shader.uniform_float("color", (1, 1, 1, 0.2))
            batch = batch_for_shader(shader, 'LINES', {"pos": mxcoords}, indices=edge_indices[8:])
            batch.draw(shader)

            # bottom and top faces
            shader.uniform_float("color", (1, 1, 1, 0.1))
            batch = batch_for_shader(shader, 'TRIS', {"pos": mxcoords}, indices=tri_indices[:4])
            batch.draw(shader)


        bgl.glDisable(bgl.GL_BLEND)

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x


        events = ['MOUSEMOVE']

        if event.type in events:

            if event.type == 'MOUSEMOVE':
                wrap_mouse(self, context, event, x=True)

                divisor = 10000 if event.shift else 100 if event.ctrl else 1000
                self.offset += (self.mouse_x - self.last_mouse_x) / divisor

        # VIEWPORT control

        elif event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        # FINISH

        elif event.type in {'LEFTMOUSE', 'SPACE'}:
            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')

            for decal, target, projected, (front, back), bbox in self.projections:
                projected = self.project(context, event, decal, target, projected=projected, depth=(front + abs(self.offset), back + abs(self.offset)))

                if not projected:
                    self.failed.append(decal)

            if self.failed:
                self.report_errors(self.failed)

            return {'FINISHED'}

        # CANCEL

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel_modal()
            return {'CANCELLED'}

        self.last_mouse_x = self.mouse_x

        return {'RUNNING_MODAL'}

    def cancel_modal(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')

        for decal, target, projected, (front, back), bbox in self.projections:
            bpy.data.meshes.remove(projected.data, do_unlink=True)

    def invoke(self, context, event):
        self.dg = context.evaluated_depsgraph_get()
        sel = context.selected_objects

        decals = [obj for obj in context.selected_objects if obj.DM.isdecal and not obj.DM.isprojected and not obj.DM.issliced]

        # unselect what won't be projected, not necessary but useful if you want to follow with the Adjust tool
        for obj in sel:
            if obj not in decals:
                obj.select_set(False)

        # alternative modal mode
        if event.alt:
            if self.invoke_modal(context, event, decals):
                return {'RUNNING_MODAL'}

            elif self.failed:
                self.report_errors(self.failed)

        # simple mode
        else:
            self.invoke_simple(context, event, decals)

        return {'FINISHED'}

    def invoke_modal(self, context, event, decals):
        self.projections = []
        self.failed = []

        for decal in decals:
            target = get_target(context, decal)

            if target:
                if target != decal.parent:
                    apply_decal(decal, target=target)

                projected = target.copy()
                projected.data = bpy.data.meshes.new_from_object(target.evaluated_get(self.dg))
                projected.modifiers.clear()
                projected.name = decal.name + "_projected"

                # determine  base projection depth
                front, back = get_bvh_ray_distance_from_verts(projected, decal, (0, 0, -1), 0.1)

                # take care of flat decals on a flat face, where both distances are close to 0
                if front + back < 0.001 * decal.scale.z:
                    front = back = 0.001 * decal.scale.z

                bbox = create_bbox(decal)

                self.projections.append((decal, target, projected, (front, back), bbox))

            else:
                self.failed.append(decal)


        # start the modal
        if self.projections:
            self.mouse_x = self.last_mouse_x = event.mouse_region_x
            self.offset = 0

            args = (self, context)
            self.VIEW3D = bpy.types.SpaceView3D.draw_handler_add(self.draw_VIEW3D, (args, ), 'WINDOW', 'POST_VIEW')

            context.window_manager.modal_handler_add(self)

            return True

    def invoke_simple(self, context, event, decals):
        failed = []

        for decal in decals:
            target = get_target(context, decal)

            if target:

                # if the parent is None or different than the "forced" target or raycasted target, re-aply the decal, before projecting to ensure the material matches and the backup is parented
                # this is useful if you move a decal from an object that was currently parented or applied to another object, and means you don't have to run reapply manually before projecting
                if target != decal.parent:

                    apply_decal(decal, target=target)
                    # apply_decal(decal)

                # shrinkwrap
                if event.shift:
                    self.shrinkwrap(context, decal, target)

                # project
                else:
                    projected = self.project(context, event, decal, target)

                    if not projected:
                        failed.append(decal)

            else:
                failed.append(decal)

        if failed:
            self.report_errors(failed)

    def report_errors(self, failed):
        msg = ["Projecting the following decals failed:"]

        for obj in failed:
            msg.append(" » " + obj.name)

        msg.append("Try Re-Applying the decal first!")
        msg.append("You can also force-project on a non-decal object by selecting it last.")

        popup_message(msg)

    def project(self, context, event, decal, target, projected=None, depth=None):
        # check  mirror mods, they need to be disabled, added to the projected decal and re-enabled again
        mirrors = [mod for mod in decal.modifiers if mod.type == "MIRROR" and mod.show_render and mod.show_viewport]

        for mod in mirrors:
            mod.show_viewport = False

        # remove subd and shrinkwrap mods, if present
        unshrinkwrap(decal)

        # create and align empty, used for uv projection
        if event.ctrl:
            uvempty = bpy.data.objects.new("uvempty", None)
            context.collection.objects.link(uvempty)

            self.align_uvempty(uvempty, decal)

        # duplicate target mesh, which will become the projected decal after boolean, the projected is passed in when run as a modal, because we need to do the raycast in advance
        if not projected:
            projected = target.copy()
            projected.data = bpy.data.meshes.new_from_object(target.evaluated_get(self.dg))
            projected.modifiers.clear()
            projected.name = decal.name + "_projected"

        for col in decal.users_collection:
            col.objects.link(projected)

        # hide decal geo, unhide projected geo, this will allow us to easily select the projected decal faces after the boolean
        unhide(projected.data)
        hide(decal.data)

        # determine projection depth, use passed in depth, if available
        if not depth:
            front, back = get_bvh_ray_distance_from_verts(projected, decal, (0, 0, -1), 0.1)

            # take care of flat d)ecals on a flat face, where both distances are close to 0
            if front + back < 0.001 * decal.scale.z:
                front = back = 0.001 * decal.scale.z

            # add 20% additional depth
            factor = 1.2

        else:
            front, back = depth

            # add a tiny amount, to counter cases where no modal depth is added a and a decal is perfectly on a surface
            factor = 1.01


        # add thickness to decal, based on front and backside distances, with proper offset. compensate for decal scaling and add 20% extra for good measure
        thickness = (front + back) / decal.scale.z

        solidify = decal.modifiers.new(name="Solidify", type="SOLIDIFY")
        solidify.thickness = thickness * factor
        solidify.offset = remap(0, -back, front, -1 / factor, 1 / factor)

        # temporarily turn of the displace mod, otherwise its offset may negatively affeect the intersection. the raycast distance is calculated without it after all
        displace = get_displace(decal)
        if displace:
            displace.show_viewport = False

        # """
        # boolean intersection
        intersect(projected, decal)
        flatten(projected)

        # remove everything but the projectd decal faces
        blast(projected.data, "hidden", "FACES")

        # parent projected decal
        parent(projected, target)

        # set decal obj props
        projected.DM.isdecal = True
        projected.DM.isprojected = True
        projected.DM.projectedon = target
        projected.DM.decalbackup = decal
        projected.DM.uuid = decal.DM.uuid
        projected.DM.decaltype = decal.DM.decaltype
        projected.DM.decallibrary = decal.DM.decallibrary
        projected.DM.decalname = decal.DM.decalname
        projected.DM.decalmatname = decal.DM.decalmatname
        projected.DM.creator = decal.DM.creator

        # turn off shadow casting and diffuse rays
        projected.cycles_visibility.shadow = False
        projected.cycles_visibility.diffuse = False


        # remove solidiy mod from decal and unhide its geo again, this needs to happen before the uv transfer!
        decal.modifiers.remove(solidify)
        unhide(decal.data)

        # also enable the displace mod again
        if displace:
            displace.show_viewport=True

        # check if the intersection resulted in any geometry, if not abort. also remove polygons facing the wrong direction
        if not self.validate_projected(projected, decal):
            bpy.data.meshes.remove(projected.data, do_unlink=True)
            for mod in mirrors:
                mod.show_viewport = True

            return False

        # with ctrl pressed, do an uv projection instead of a transfer
        # uv project
        if event.ctrl:
            uvproject = projected.modifiers.new(name="UVProject", type="UV_PROJECT")
            uvproject.projectors[0].object = uvempty
            flatten(projected)
            bpy.data.objects.remove(uvempty, do_unlink=True)

        # uv transfer
        else:
            uvtransfer = projected.modifiers.new(name="UVTransfer", type="DATA_TRANSFER")
            uvtransfer.object = decal
            uvtransfer.use_loop_data = True
            uvtransfer.loop_mapping = 'POLYINTERP_NEAREST'
            uvtransfer.data_types_loops = {'UV'}
            flatten(projected)

        # apply the decalmat
        projected.data.materials.clear()  # actually no longer necessary, materials are cleared and obj is flattened
        if decal.active_material:
            projected.data.materials.append(decal.active_material)

        # displace
        add_displace(projected)

        # mirror
        for mod in mirrors:
            mirror = projected.modifiers.new(name=mod.name, type="MIRROR")
            mirror.use_axis = mod.use_axis
            mirror.use_mirror_u = mod.use_mirror_u
            mirror.use_mirror_v = mod.use_mirror_v
            mirror.mirror_object = mod.mirror_object

        # normal tranfer
        add_nrmtransfer(projected, target)

        # set object defaults
        set_defaults(decalobj=projected)

        # lock transforms
        lock(projected)

        # select and make active
        projected.select_set(True)

        if context.active_object == decal:
            context.view_layer.objects.active = projected

        # turn the decal into a decal backup
        decal.use_fake_user = True
        decal.DM.isbackup = True

        unlink_object(decal)

        # store the backup's matrix in target's local space
        decal.DM.backupmx = flatten_matrix(target.matrix_world.inverted() @ decal.matrix_world)

        # add edit mode group
        gp_add_to_edit_mode_group(context, projected)

        # local view update
        update_local_view(context.space_data, [(projected, True)])

        return True

    def align_uvempty(self, uvempty, decal):
        # find true location by creating 4 corner boundary locations from decal mesh and calcuate the center from them
        loc = get_origin_from_object_boundingbox(decal)

        # get rotation
        _, rot, _ = decal.matrix_world.decompose()

        # construct scale matrix from decal dimensions, divided by two, because like a default cube the empty is actually 2 units wide, even though is doesnt have dimenisions
        sca = Matrix()
        sca[0][0] = decal.dimensions.x / 2
        sca[1][1] = decal.dimensions.y / 2
        sca[2][2] = 1

        # align empty for perfect uv projection
        uvempty.matrix_world = Matrix.Translation(loc) @ rot.to_matrix().to_4x4() @ sca

    def validate_projected(self, projected, decal):
        # check if there is any geometry at all, if not abort projection
        if not projected.data.polygons:
            return False

        # if there is geometry, check for faces pointing in the same directino as the decals -Z, these need to go
        dmxw = decal.matrix_world
        origin, _, _ = dmxw.decompose()
        direction = dmxw @ Vector((0, 0, -1)) - origin

        pmxw = projected.matrix_world
        pmxi = pmxw.inverted()
        direction_local = pmxi.to_3x3() @ direction

        bm = bmesh.new()
        bm.from_mesh(projected.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        backfaces = [f for f in bm.faces if f.normal.dot(direction_local) > 0]

        bmesh.ops.delete(bm, geom=backfaces, context="FACES")

        # again check if any polygons are left
        if bm.faces:
            bm.to_mesh(projected.data)
            bm.clear()
            return True

        # otherwise abort
        else:
            return False

    def shrinkwrap(self, context, decal, target):
        # smooth mesh
        smooth(decal.data)

        # get mirror mods
        mirrors = get_mods_as_dict(decal, types=['MIRROR'])

        # clear existing mods, to guarantee proper order, fetch the current displace mid-level first however
        displace = get_displace(decal)
        midlevel = displace.mid_level if displace else None

        decal.modifiers.clear()

        # add shrinkwrap mods
        add_subd(decal)
        add_shrinkwrap(decal, target)

        # add original displace
        displace = add_displace(decal)
        if midlevel:
            displace.mid_level = midlevel

        # add original mirrors
        add_mods_from_dict(decal, mirrors)

        # add new normal transfer
        add_nrmtransfer(decal, target)

        # set object defaults
        set_defaults(decalobj=decal)


class UnShrinkwrap(bpy.types.Operator):
    bl_idname = "machin3.unshrinkwrap_decal"
    bl_label = "MACHIN3: Unshrinkwrap"
    bl_description = "Un-Shrinkwrap, turn shrinkwrapped decal back into flat one."
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        decals = [obj for obj in context.selected_objects if obj.DM.isdecal]
        return decals and any(get_shrinkwrap(obj) or get_subd(obj) for obj in decals)

    def execute(self, context):
        decals = [obj for obj in context.selected_objects if obj.DM.isdecal]

        for obj in decals:
            # remove shrinkwrap and subd mods
            unshrinkwrap(obj)

            # unsmooth
            smooth(obj.data, smooth=False)

        return {'FINISHED'}
