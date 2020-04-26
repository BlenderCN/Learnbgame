import bpy
import os
from .. utils.material import remove_decalmat, get_decalmat, get_decalgroup_from_decalmat, get_pbrnode_from_mat
from .. utils.registration import get_prefs, get_path
from .. utils.pil import fix_legacy_normals
from .. utils.decal import render_thumbnail, save_blend, set_decalobj_props_from_material, set_decalobj_name
from .. utils.modifier import add_displace
from .. utils.system import splitpath
from .. utils.append import append_nodetree, append_object
from .. utils.ui import get_icon
from .. utils.math import flatten_matrix
from .. utils.object import flatten


class DebugWhatever(bpy.types.Operator):
    bl_idname = "machin3.debug_whatever"
    bl_label = "MACHIN3: Debug Whatever"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        active = context.active_object
        # active = bpy.data.objects['Cube.001']

        dg = context.evaluated_depsgraph_get()

        # oldmesh = obj.data
        # active_eval = active.evaluated_get(dg)
        active_eval = dg.id_eval_get(active)

        # active.data = active_eval.to_mesh()
        # active.data = active_eval.to_mesh_clear()
        # active.data = active_eval.data
        active.data = bpy.data.meshes.new_from_object(active_eval)

        active.modifiers.clear()

        # depsgraph.update()

        # bpy.data.meshes.remove(oldmesh, do_unlink=True)

        return {'FINISHED'}


class DebugToggle(bpy.types.Operator):
    bl_idname = "machin3.decalmachine_debug"
    bl_label = "MACHIN3: Debug DECALmachine"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        dm = context.scene.DM
        dm.debug = not dm.debug
        return {'FINISHED'}


class FixLegacyNormals(bpy.types.Operator):
    bl_idname = "machin3.fix_legacy_normals"
    bl_label = "MACHIN3: "
    bl_description = "Fix Normals in Selected User Decal Library"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        assetspath = get_prefs().assetspath
        librarypath = os.path.join(assetspath, scene.userdecallibs)

        folders = sorted([f for f in os.listdir(librarypath) if os.path.isdir(os.path.join(librarypath, f))])

        for folder in folders:
            nrm_alpha_path = os.path.join(librarypath, folder, "nrm_alpha.png")

            if os.path.exists(nrm_alpha_path):
                fix_legacy_normals(nrm_alpha_path)
                print("Fixed %s" % (nrm_alpha_path))

        return {'FINISHED'}


class ReRenderThumbnails(bpy.types.Operator):
    bl_idname = "machin3.rerender_decal_thumbnails"
    bl_label = "MACHIN3: Re-Render Decal Thumbnails"
    bl_description = "Re-Render Decal Thumbnails of the Selected User Decal Library"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        dm = scene.DM
        assetspath = get_prefs().assetspath
        librarypath = os.path.join(assetspath, scene.userdecallibs)

        folders = sorted([f for f in os.listdir(librarypath) if os.path.isdir(os.path.join(librarypath, f))])

        for folder in folders:
            decalpath = os.path.join(librarypath, folder)
            blendpath = os.path.join(decalpath, "decal.blend")

            if os.path.exists(blendpath):
                decal = append_object(blendpath, "LIBRARY_DECAL")

                if decal:
                    decalmat = get_decalmat(decal)

                    if decalmat:
                        render_thumbnail(context, decalpath, decal, decalmat, tint=dm.create_thumbnail_tint, removeall=True)


        return {'FINISHED'}


class UpdateNodeTree(bpy.types.Operator):
    bl_idname = "machin3.update_decal_node_tree"
    bl_label = "MACHIN3: update_decal_node_tree"
    bl_description = "Updatees Decal Node Tree in selected User Decal Library"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        assetspath = get_prefs().assetspath
        librarypath = os.path.join(assetspath, scene.userdecallibs)

        templatepath = os.path.join(get_path(), "resources", "Templates.blend")


        folders = sorted([f for f in os.listdir(librarypath) if os.path.isdir(os.path.join(librarypath, f))])

        for folder in folders:
            decalpath = os.path.join(librarypath, folder)
            blendpath = os.path.join(decalpath, "decal.blend")

            treetypes = ['subset', 'panel']

            while treetypes:
                treetype = treetypes.pop(0)
                nt = append_nodetree(blendpath, "%s.LIBRARY_DECAL" % (treetype))

                if nt:
                    print("found a %s decal: %s" % (treetype, blendpath))
                    bpy.data.node_groups.remove(nt, do_unlink=True)

                    # append the entire decal and the template node tree
                    decal = append_object(blendpath, "LIBRARY_DECAL")
                    newnt = append_nodetree(templatepath, "%s.TEMPLATE_%s" % (treetype, treetype.upper()))

                    # link decal to decal asset scene
                    decalscene = bpy.data.scenes.new(name="Decal Asset")
                    decalscene.collection.objects.link(decal)

                    # get decal nodegroup
                    decalmat = get_decalmat(decal)
                    dg = get_decalgroup_from_decalmat(decalmat)

                    # get Masks from_node
                    from_node = dg.inputs['Masks'].links[0].from_node

                    # replace the old node tree with the new one
                    oldnt = dg.node_tree
                    dg.node_tree = newnt
                    newnt.name = oldnt.name

                    # remove the old node tree
                    bpy.data.node_groups.remove(oldnt, do_unlink=True)

                    # connect the from_node to the new Masks input
                    decalmat.node_tree.links.new(from_node.outputs[0], dg.inputs['Masks'])

                    # save the new decal asset
                    save_blend(decal, decalpath, decalscene)

                    # remove everything
                    remove_decalmat(decalmat, remove_textures=True)

                    bpy.data.meshes.remove(decal.data, do_unlink=True)

                    break

            # if nt:
                # break

        return {'FINISHED'}


class ReplaceMaterial(bpy.types.Operator):
    bl_idname = "machin3.replace_material"
    bl_label = "MACHIN3: Replace Material"
    bl_description = "Replace Material"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object in context.selected_objects

    def execute(self, context):
        active = context.active_object
        sel = [obj for obj in context.selected_objects if obj != active]

        activemat = active.active_material

        if sel and activemat:
            for obj in sel:
                obj.data.materials.clear()
                obj.data.materials.append(activemat)

        return {'FINISHED'}


class SetPropsAndNameFromMaterial(bpy.types.Operator):
    bl_idname = "machin3.set_props_and_name_from_material"
    bl_label = "MACHIN3: Set Props and Name from Material"
    bl_description = "Set decal props and name from material"
    bl_options = {'REGISTER', 'UNDO'}

    # @classmethod
    # def poll(cls, context):
        # return context.active_object and context.active_object in context.selected_objects and not context.active_object.DM.isdecal

    def execute(self, context):
        for obj in context.selected_objects:
            context.view_layer.objects.active = obj

            decalmat = get_decalmat(obj)

            if decalmat:
                obj.DM.isdecal = True
                obj.DM.decaltype = decalmat.DM.decaltype

                set_decalobj_props_from_material(obj, decalmat)

                set_decalobj_name(obj)

                obj.hide_viewport = True

                displace = False
                nrmtransfer = False

                for mod in obj.modifiers:
                    if mod.type == "DISPLACE":
                        displace = mod
                        mod.name = "Displace"

                    elif mod.type == "DATA_TRANSFER":
                        nrmtransfer = mod
                        mod.object = obj.parent
                        mod.name = "NormalTransfer"

                if not displace:
                    displace = add_displace(obj)

                while obj.modifiers[0] != displace:
                    bpy.ops.object.modifier_move_up(modifier=displace.name)

                # if not nrmtransfer:
                    # nrmtransfer = obj.modifiers.new("NormalTransfer", "DATA_TRANSFER")
                    # nrmtransfer.object = obj.parent
                    # nrmtransfer.use_loop_data = True
                    # nrmtransfer.data_types_loops = {'CUSTOM_NORMAL'}
                    # nrmtransfer.loop_mapping = 'POLYINTERP_LNORPROJ'
                    # nrmtransfer.show_expanded = False
                    # nrmtransfer.show_render = False
                    # nrmtransfer.show_viewport = False

                obj.data.use_auto_smooth = True


        return {'FINISHED'}


class FixTexturePaths(bpy.types.Operator):
    bl_idname = "machin3.fix_decal_texture_paths"
    bl_label = "MACHIN3: Fix Decal Texture Paths"
    bl_description = "Fix Decal Texture Paths"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return [img for img in bpy.data.images if img.DM.isdecaltex]

    def execute(self, context):
        assetspath = get_prefs().assetspath

        textures = sorted([img for img in bpy.data.images if img.DM.isdecaltex], key=lambda x: x.DM.decallibrary)

        for img in textures:
            print("\nold path:", img.filepath)

            split = splitpath(img.filepath)
            print("split path:", split)

            newpath = os.path.join(assetspath, *split[-3:])
            print("new path:", newpath)

            img.filepath = newpath

        return {'FINISHED'}


class UpdateDecalBackup(bpy.types.Operator):
    bl_idname = "machin3.update_decal_backup"
    bl_label = "MACHIN3: Update Decal Backup"
    bl_description = "Update Decal Backup (Matrix)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        active = context.active_object
        return active and (active.DM.isbackup or active.DM.decalbackup)

    def invoke(self, context, event):
        if event.alt:
            backup = context.active_object
            target = backup.parent

            backup.DM.backupmx = flatten_matrix(target.matrix_world.inverted() @ backup.matrix_world)

            context.scene.collection.objects.unlink(backup)

        else:
            backup = context.active_object.DM.decalbackup
            context.scene.collection.objects.link(backup)

            bpy.ops.object.select_all(action='DESELECT')

            backup.select_set(True)
            context.view_layer.objects.active = backup


        return {'FINISHED'}
