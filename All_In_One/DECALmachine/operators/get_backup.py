import bpy
from mathutils import Matrix
from .. utils.object import parent, update_local_view
from .. utils.math import flatten_matrix

# TODO: add reconstruct panel cutter as alternative mode


class GetBackup(bpy.types.Operator):
    bl_idname = "machin3.get_backup_decal"
    bl_label = "MACHIN3: Get Backup Decal"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Default: Retrieve Decal Backup\nAlt: Delete Projected/Sliced Decal"


    def draw(self, context):
        layout = self.layout
        col = layout.column()

    @classmethod
    def poll(cls, context):
        return any(obj for obj in context.selected_objects if obj.DM.isdecal and obj.DM.decalbackup)

    def invoke(self, context, event):
        decals = [obj for obj in context.selected_objects if obj.DM.isdecal and obj.DM.decalbackup]
        active = context.active_object

        for decal in decals:

            # if you delete the original, fetch the original backup too
            if event.alt:
                backup = decal.DM.decalbackup

            # otherwise, copy the backup and keep the original backup in store
            else:
                backup = decal.DM.decalbackup.copy()
                backup.data = decal.DM.decalbackup.data.copy()

            # if the backup is a decal, sort it into the same collections as the decal is in
            if backup.DM.isdecal:
                cols = [col for col in decal.users_collection]

                for col in cols:
                    col.objects.link(backup)

            # otherwise put it into the master collection
            else:
                context.scene.collection.objects.link(backup)


            # restore backup location (even when objects were duplicated and when groupro kills the relationship)
            if decal.parent:
                backup.matrix_world = decal.parent.matrix_world @ backup.DM.backupmx

                # restore parenting, in case of object duplicaton
                if decal.parent != backup.parent:
                    parent(backup, decal.parent)

            # clear the backupparentmx
            backup.DM.backupparentmx = flatten_matrix(Matrix())

            # clear props
            backup.DM.isbackup = False
            backup.use_fake_user = False

            backup.select_set(True)

            if decal == active:
                context.view_layer.objects.active = backup

            if event.alt:
                bpy.data.meshes.remove(decal.data, do_unlink=True)

            else:
                decal.select_set(False)

            # local view update
            update_local_view(context.space_data, [(backup, True)])

        return {'FINISHED'}
