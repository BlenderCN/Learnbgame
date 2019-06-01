import bpy
from bpy.props import BoolProperty
from .. import M3utils as m3


class ExtractSource(bpy.types.Operator):
    bl_idname = "machin3.extract_decal_source"
    bl_label = "MACHIN3: Extract Decal Source"
    bl_options = {'REGISTER', 'UNDO'}

    deletedecal = BoolProperty(name="Remove Decal", default=False)

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        column.prop(self, "deletedecal")

    def execute(self, context):
        active = bpy.context.scene.objects.active

        timestamp = m3.get_timestamp(active)

        revealed = False
        for obj in bpy.data.objects:
            if obj != active:
                backupstamp = m3.get_timestamp(obj)
                if backupstamp == timestamp and "backup_" in obj.name:
                    # leaving the original backups allone(unlinked), instead we duplicate them and link these
                    # we are also "removing" the timestamp
                    dupbackup = obj.copy()
                    dupbackup.data = obj.data.copy()
                    del dupbackup["timestamp"]

                    if "panel_decal" in dupbackup.name or "material_decal" in dupbackup.name:
                        dupbackup.name = dupbackup.name + "_cutter"
                    dupbackup.name = dupbackup.name.replace("backup_", "")
                    if "dstep_" in dupbackup.name:
                        dupbackup.name = dupbackup.name + "_unstepped"
                        # dupbackup.name.replace("dstep_", "")  # not working for some reasonn
                        dupbackup.name = dupbackup.name[6:]
                        active.hide = True

                    bpy.context.scene.objects.link(dupbackup)

                    m3.make_active(dupbackup)
                    dupbackup.select = True
                    active.select = False
                    revealed = True

                    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

                    break


        if self.deletedecal:
            bpy.data.objects.remove(active, do_unlink=True)

        if revealed is False:
            self.report({'ERROR'}, "No Source found.")

        return {'FINISHED'}
