import bpy
from bpy.props import FloatProperty, BoolProperty
from . init_base_material import init_base_material
from . steps import WStep
from .. import M3utils as m3
from .. utils.operators import get_selection, hide_meshes, intersect, unlink_render_result


class DecalProject(bpy.types.Operator):
    bl_idname = "machin3.decal_project"
    bl_label = "MACHIN3: Decal Project"
    bl_options = {'REGISTER', 'UNDO'}

    depth = FloatProperty(name="Projection Depth", default=10, min=0.01)
    height = FloatProperty(name="Decal Height", default=0)
    parent = BoolProperty(name="Parent", default=True)
    wstep = BoolProperty(name="Transfer Normals", default=True)
    wstepshow = BoolProperty(name="Show in Viewport", default=True)

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.prop(self, "depth")
        col.prop(self, "height")
        col.prop(self, "parent")

        row = col.row()
        row.prop(self, "wstep")
        row.prop(self, "wstepshow")

    def execute(self, context):
        if m3.DM_prefs().consistantscale:
            self.scene_scale = m3.get_scene_scale()
        else:
            self.scene_scale = 1

        self.midlevel = 1 - (0.0001 / self.scene_scale)  # 0.9999 for scene scale of 1.0
        self.projectiondepth = self.depth / 10 / self.scene_scale

        sel = get_selection()
        if sel is not None:
            target, decals = sel
            self.decal_project(target, decals)
        else:
            self.report({'ERROR'}, "Select two or more objects: the decal(s) and the object to project onto!")

        return {'FINISHED'}

    def decal_project(self, target, decals):
        curved = target

        init_base_material([curved])

        for decal in decals:
            print("Projecting '%s' on '%s'." % (decal.name, curved.name))
            m3.unselect_all("OBJECT")

            # duplicating and timestamping the decalbackup for potential future use. the timestamp will be used to identify the duplicate, independend of the obj names
            decalbackup = decal.copy()
            decalbackup.data = decal.data.copy()
            # prevent it from being removed after scene reload
            decalbackup.use_fake_user = True
            timestamp = m3.set_timestamp(decalbackup)
            decalbackup.name = "backup_" + decal.name

            decal.select = True
            m3.make_active(decal)

            # check for active mirror modes
            # they need to be removed and re-applied to the projected decal
            mirrormods = []
            for mod in decal.modifiers:
                if "mirror" in mod.name.lower():
                    mirror = decal.modifiers.get(mod.name)
                    mirrordict = {mirror.name: {"use_x": mirror.use_x,
                                                "use_y": mirror.use_y,
                                                "use_z": mirror.use_z,
                                                "use_mirror_merge": mirror.use_mirror_merge,
                                                "use_clip": mirror.use_clip,
                                                "use_mirror_vertex_groups": mirror.use_mirror_vertex_groups,
                                                "use_mirror_u": mirror.use_mirror_u,
                                                "use_mirror_v": mirror.use_mirror_v,
                                                "merge_threshold": mirror.merge_threshold,
                                                "mirror_object": mirror.mirror_object}}

                    mirrormods.append(mirrordict)
                    bpy.ops.object.modifier_remove(modifier=mod.name)

            curved.select = True
            m3.make_active(curved)

            try:
                decalmat = decal.material_slots[0].material
            except:
                decalmat = None

            # create empty, used for uv projection later on
            uvempty = bpy.data.objects.new("uvempty", None)
            bpy.context.scene.objects.link(uvempty)

            # align uvempty to decal
            # uvempty.location = decal.location
            # uvempty.rotation_euler = decal.rotation_euler
            # the above doesnt work on decals that are parented to the curved (such as decalbackups brought back and used for re-projection)

            # parent uvempty to decal, this positions and aligns it
            uvempty.parent = decal

            # then immedeately clear the parent again and keep the transforms to "freeze" it in place
            # if this is not done, then the uvempty will loose its parent once you intersect and so change its location and rotation

            uvempty.select = True
            m3.make_active(uvempty)
            curved.select = False
            decal.select = False
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')


            # recreate the previous selection pattern
            uvempty.select = False
            curved.select = True
            decal.select = True
            m3.make_active(curved)

            # duplicate the curved mesh, which will become the projected decal after boolean
            curveddecal = curved.copy()
            curveddecal.data = curved.data.copy()
            bpy.context.scene.objects.link(curveddecal)
            curveddecal.select = True
            m3.make_active(curveddecal)

            # unselecting and hiding the original curved object
            curved.select = False
            curved.hide = True

            # we want the geometry of curveddecal to be hidden
            # but we dont won't this for the decal, that is to be projected
            decal.select = False
            hide_meshes()
            decal.select = True

            # applying all modifiers(including bevel, so you can project on objets where the bevels arent applies yet)
            # but excluding data_tansfers, because we want to also apply custom normals to the curved decal, if the curved mesh has them!
            for mod in curveddecal.modifiers:
                # if mod.type != "DATA_TRANSFER":
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)

            # add thickness to decal
            solidify = decal.modifiers.new(name="Solidify", type="SOLIDIFY")
            solidify.offset = -0.5
            solidify.thickness = self.projectiondepth

            # boolean intersection
            intersect()

            # the decal is now gone, so we can take its name and asign it to the new one
            # interstingly we can assign the name like this directly, perhaps because
            # decal is still in memory?
            # the duplicate of the curved(target), will become the new decal(after boolean)
            curveddecal.select = True
            m3.make_active(curveddecal)

            # the prefix(here and later on the backup) is added, because otherwise there will be a bug (in asset manager)
            # causing the backup to become linked and offset, when importing an asset, the backup needs to be always unlinked however
            curveddecal.name = "projected_" + decal.name + "_" + curved.name

            # also adding the timestamp we have previously added to the decalbackup
            m3.set_timestamp(curveddecal, timestamp=timestamp)

            # remove unwanted parts and leave only the "projected decal"
            curveddecal.select = True
            m3.set_mode("EDIT")
            m3.select_all("MESH")
            bpy.ops.mesh.delete(type='FACE')
            bpy.ops.mesh.reveal()
            m3.set_mode("OBJECT")

            # unhiding the original curved object again
            curved.hide = False

            # adding a slight displace to the decal
            displace = curveddecal.modifiers.new(name="Displace", type="DISPLACE")

            # enough to avoid z-fighting, yet not enough to produce a noticable shadow when rendering
            displace.mid_level = self.midlevel - (self.height / 1000 / self.scene_scale)
            displace.show_in_editmode = True
            displace.show_on_cage = True
            displace.show_expanded = False

            # clear out all existing uv 'channels'
            uvs = curveddecal.data.uv_textures
            while uvs:
                uvs.remove(uvs[0])

            # add a new channel
            uvs.new('UVMap')

            # creating uvs for the curved decal using the uvproject mod and the uvempty
            # this way we are ensuring the uvs are always square/rectangular no matter the new topology
            # furthermore, the uvs will always be perfectly centered so we can scale them up witht the boundary limit to fit the whole uv space
            # plus they are of course aligned/rotated just like the source decal!
            uvproject = curveddecal.modifiers.new(name="UVProject", type="UV_PROJECT")
            uvproject.projectors[0].object = uvempty

            # applying uvproject mod
            for mod in curveddecal.modifiers:
                if "uvproject" in mod.name.lower():
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)

            # scaling the uv's up to fit the entire uv space
            m3.set_mode("EDIT")
            m3.select_all("MESH")
            oldcontext = m3.change_context("IMAGE_EDITOR")

            # Check if it is a result image linked, if there is, then no geometry will show in the image editor and nothing can be scaled or rotated
            # se we need to unlink the render result
            unlink_render_result()

            # this needs to be turned on, otherwise nothing will be selected in uv and so nothing will be scaled up
            bpy.context.scene.tool_settings.use_uv_select_sync = True

            # contrain uvs to uv/image bounds
            bpy.context.space_data.uv_editor.lock_bounds = True

            # uv scaling needs to happen based on the bounding box center(which should also be the uv center)
            bpy.context.space_data.pivot_point = 'CENTER'

            # scaling up a lot to hit those bounds and so fill out the entire uv space
            bpy.ops.transform.resize(value=(1000, 1000, 1000), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

            # turning bounds off again
            bpy.context.space_data.uv_editor.lock_bounds = False

            # changing the context back to what it was
            m3.change_context(oldcontext)

            m3.set_mode("OBJECT")

            # remove the uvempty
            m3.unselect_all("OBJECT")
            uvempty.select = True
            bpy.ops.object.delete(use_global=False)

            # cleaning out all materials of the curveddecal
            curveddecal.select = True
            for slot in curveddecal.material_slots:
                bpy.ops.object.material_slot_remove()

            if decalmat is not None:
                # applying the decal material
                bpy.ops.object.material_slot_add()
                curveddecal.material_slots[0].material = decalmat

            # bring back mirror modifiers
            for m in mirrormods:
                for name in m:
                    mirror = curveddecal.modifiers.new(name=name, type="MIRROR")
                    mirror.use_x = m[name]["use_x"]
                    mirror.use_y = m[name]["use_y"]
                    mirror.use_z = m[name]["use_z"]
                    mirror.use_mirror_merge = m[name]["use_mirror_merge"]
                    mirror.use_clip = m[name]["use_clip"]
                    mirror.use_mirror_vertex_groups = m[name]["use_mirror_vertex_groups"]
                    mirror.use_mirror_u = m[name]["use_mirror_u"]
                    mirror.use_mirror_v = m[name]["use_mirror_v"]
                    mirror.merge_threshold = m[name]["merge_threshold"]
                    mirror.mirror_object = m[name]["mirror_object"]

            if self.wstep:
                # select and make active the curved/target to prepare for wstep
                m3.make_active(curved)
                curved.select = True

                # transfer the normals from the target
                bpy.ops.machin3.wstep()

                # turn off viewport visibiity for performance reasons
                if not self.wstepshow:
                    mod = curveddecal.modifiers.get("M3_copied_normals")
                    mod.show_viewport = False

            # turn off shadow casting
            curveddecal.cycles_visibility.shadow = False

            # enable wire display
            curveddecal.show_wire = True
            curveddecal.show_all_edges = True

            if self.parent:
                # curveddecal.parent = curved
                # curveddecal.matrix_parent_inverse = curved.matrix_world.inverted()

                # decalbackup.parent = target
                # decalbackup.matrix_parent_inverse = curved.matrix_world.inverted()

                curveddecal.select = True
                curved.select = True
                m3.make_active(curved)
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

                curveddecal.select = False
                bpy.context.scene.objects.link(decalbackup)
                decalbackup.select = True
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
                bpy.context.scene.objects.unlink(decalbackup)

                curved.select = False
                curveddecal.select = True
                m3.make_active(curveddecal)

            # add to group pro group
            if m3.GP_check():
                if m3.DM_prefs().groupproconnection:
                    if len(bpy.context.scene.storedGroupSettings) > 0:
                        bpy.ops.object.add_to_grouppro()
