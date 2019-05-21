import bpy

class B2RexTextMenu(bpy.types.Header):
    bl_label = 'sim'
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = "MENU"
    def draw(self, context):
        spacedata = context.space_data
        session = bpy.b2rex_session
        if spacedata.text:
            if spacedata.text.opensim.uuid:
                label = 'Update'
            else:
                label = 'Upload'
            self.layout.operator('b2rex.upload_text', text=label).text = spacedata.text.name


