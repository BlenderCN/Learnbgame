import bpy


class ImportBVH2SelectedArmaturePanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Import BVH to selected rig"
    
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'BVH'

    @classmethod
    def poll(cls, context):
        return context.object is not None
        return bpy.ops.mocap_madness.rescale.poll()
    
    def draw(self, context):
        layout = self.layout

        arm = context.object.data
        row = layout.row()
        # Create a simple row.
        op = row.operator("import_anim.bvh_mocap_madness")
        #op.global_scale = 0.2
        print(dir(op))
        print(op.bl_rna)
        box = layout.box()
        split = box.split(percentage=0.7)
        col1 = split.column()
        col2 = split.column()
        for kw, val in arm['_RNA_UI']['bvh_import_settings'].to_dict().items():
            row = layout.row()
            type = op.bl_rna.properties[kw].rna_type.identifier
            key = op.bl_rna.properties[kw].name
            v = 'XX'
            if type.startswith('Bool'):
                v = bool(val)
            else:
                v = val
            col1.label("%s" % key)
            col2.label("%s" % str(v))
            setattr(op, kw, val)


def register():
    bpy.utils.register_class(ImportBVH2SelectedArmaturePanel)


def unregister():
    bpy.utils.unregister_class(ImportBVH2SelectedArmaturePanel)


if __name__ == "__main__":
    register()

