import bpy
from bpy.props import StringProperty, BoolProperty
import os
import shutil
from .. utils.registration import get_prefs, get_path, get_addon
from .. utils.append import append_object
from .. utils.material import get_decalmat, deduplicate_material, remove_decalmat
from .. utils.scene import setup_surface_snapping
from .. utils.decal import set_props_and_node_names_of_library_decal, set_decalobj_name, align_decal, apply_decal, set_defaults
from .. utils.registration import reload_decal_libraries, reload_instant_decals, set_new_decal_index
from .. utils.collection import sort_into_collections
from .. utils.addon import gp_add_to_edit_mode_group
from .. utils.object import update_local_view
from .. utils.developer import Benchmark


class Insert(bpy.types.Operator):
    bl_idname = "machin3.insert_decal"
    bl_label = "MACHIN3: Insert Decal"
    bl_description = "Insert Selected Decal"
    bl_options = {'REGISTER'}

    library: StringProperty()
    decal: StringProperty()

    instant: BoolProperty(default=False)
    force_cursor_align: BoolProperty(default=False)

    def execute(self, context):
        T = Benchmark(context.scene.DM.debug)

        assetspath = get_prefs().assetspath

        if self.instant:
            blendpath = os.path.join(get_path(), "assets", "Create", "instant", self.decal, "decal.blend")
        else:
            blendpath = os.path.join(assetspath, self.library, self.decal, "decal.blend")

        decalobj = append_object(blendpath, "LIBRARY_DECAL")

        T.measure("append decal")

        if decalobj:
            scene = context.scene

            # deselect everything
            bpy.ops.object.select_all(action='DESELECT')

            T.measure("deselection")

            # to scale the decal accordingly, it needs to be in a collection, so add it to the mcol, temporarily
            scene.collection.objects.link(decalobj)

            # evaluate depsgraph
            dg = context.evaluated_depsgraph_get()

            # align the decal to the cursor or via raycast and scale it
            align_decal(decalobj, scene, dg, force_cursor_align=self.force_cursor_align)

            T.measure("align")

            # """
            # deduplicate the material
            mat = get_decalmat(decalobj)

            if mat:
                decalmat = deduplicate_material(mat)
                decalobj.active_material = decalmat

                T.measure("de-duplicate material")

            else:
                decalmat = None

            if decalmat:
                # set the props of the decal obj and the as of yet unmatched material
                set_props_and_node_names_of_library_decal(self.library, self.decal, decalobj=decalobj, decalmat=decalmat)

                T.measure("set properties")

                # set the defaults, just like the props above, it's important to do this before the decal is applied and the material is potentially auto matched
                set_defaults(decalobj=decalobj, decalmat=decalmat)

                T.measure("set defaults")

                # apply the decal - do a raycast and then set up the custom normals, the parenting, auto match the material according to the result of the cast
                apply_decal(decalobj, raycast=True)

                T.measure("apply decal")

                # set decalobj name, counting up
                set_decalobj_name(decalobj)

                T.measure("set decal obj name")

                # setup snapping
                setup_surface_snapping(scene)

                T.measure("set surface snapping")

            # sort into optional collections based on decaltype, decal parent or active collectinon
            sort_into_collections(scene, decalobj)

            T.measure("collections")

            # select decal once it's in a collection and make it active
            decalobj.select_set(True)
            context.view_layer.objects.active = decalobj

            T.measure("decal selection")

            # group pro
            gp_add_to_edit_mode_group(context, decalobj)

            T.measure("add to group pro")

            # local view update
            update_local_view(context.space_data, [(decalobj, True)])

            T.measure("add to local view")

            # set props for quick insertion
            scene.DM.quickinsertlibrary = self.library
            scene.DM.quickinsertdecal = self.decal
            scene.DM.quickinsertisinstant = self.instant

            T.measure("set quick insert props")

            T.total()
            # """

        return {"FINISHED"}


class QuickInsert(bpy.types.Operator):
    bl_idname = "machin3.quick_insert_decal"
    bl_label = "MACHIN3: Quick Insert Decal"
    bl_description = "Quickly Insert the same Decal as before, directly under the Mouse"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        scene = context.scene
        dm = scene.DM
        wm = context.window_manager

        library = scene.DM.quickinsertlibrary
        decal = scene.DM.quickinsertdecal
        isinstant = scene.DM.quickinsertisinstant

        if library and decal:
            if dm.align_mode == "RAYCAST":
                wm.decal_mousepos = [event.mouse_region_x, event.mouse_region_y]

            elif dm.align_mode == "CURSOR":
                cursorloc = context.scene.cursor.location.copy()
                context.scene.cursor.rotation_mode = 'QUATERNION'
                cursorrot = context.scene.cursor.rotation_quaternion.copy()

                bpy.ops.view3d.cursor3d('INVOKE_DEFAULT', use_depth=True, orientation='GEOM')

            bpy.ops.machin3.insert_decal(library=library, decal=decal, instant=isinstant)

            if dm.align_mode == "CURSOR":
                scene.cursor.location = cursorloc
                scene.cursor.rotation_quaternion = cursorrot

        return {'FINISHED'}


class Remove(bpy.types.Operator):
    bl_idname = "machin3.remove_decal"
    bl_label = "MACHIN3: Remove Decal"
    bl_description = "Remove Selected Decal"

    library: StringProperty()
    decal: StringProperty()

    instant: BoolProperty(default=False)

    def execute(self, context):
        print(" ! REMOVING Decal:", self.library, self.decal)

        assetspath = get_prefs().assetspath

        if self.instant:
            librarypath = os.path.join(get_path(), "assets", "Create", "instant")
        else:
            librarypath = os.path.join(assetspath, self.library)

        decalpath = os.path.join(librarypath, self.decal)
        uuidpath = os.path.join(decalpath, "uuid")

        # remove the decal from the current blend file
        if os.path.exists(uuidpath):
            with open(uuidpath, "r") as f:
                uuid = f.read()

            if uuid:
                for obj in bpy.data.objects:
                    if obj.DM.isdecal and obj.DM.uuid == uuid:
                        bpy.data.meshes.remove(obj.data, do_unlink=True)

                for mat in bpy.data.materials:
                    if mat.DM.isdecalmat and mat.DM.uuid == uuid:
                        remove_decalmat(mat, debug=False)

                for img in bpy.data.images:
                    if img.DM.isdecaltex and img.DM.uuid == uuid:
                        bpy.data.images.remove(img, do_unlink=True)


        # remove decal from disk
        shutil.rmtree(decalpath)

        folders = [f for f in sorted(os.listdir(librarypath)) if os.path.isdir(os.path.join(librarypath, f))]

        decals = []
        nondecals = []

        # check the folders are actual decals, if not collect them as nondecals(incomplete decals)
        for folder in folders:
            files = os.listdir(os.path.join(librarypath, folder))

            if all([f in files for f in ["decal.blend", "decal.png", "uuid"]]):
                decals.append(folder)
            else:
                nondecals.append(folder)

        # in the case of instant decals, remove the non-decals as well
        for nondecal in nondecals:
            path = os.path.join(librarypath, nondecal)

            print("Found broken instant decal, also removing %s!" % (path))
            shutil.rmtree(path)

        default = decals[-1] if decals else None

        # reload the library
        if self.instant:
            reload_instant_decals(default=default)

        else:
            reload_decal_libraries(library=self.library, default=default)

            set_new_decal_index(self, context)

        return {'FINISHED'}
