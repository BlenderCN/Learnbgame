import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty

#from speckle import SpeckleAddon

def menu_func(self, context):
    self.layout.operator(SpeckleUpdateObject.bl_idname, icon='MESH_CUBE')


def get_available_accounts(self, context):
    return [(a, a, a.name) for a in context.scene.speckle.accounts]


class VIEW3D_UL_SpeckleAccounts(bpy.types.UIList):

    def draw_item(self, context, layout, data, account, active_data, active_propname):
        ob = data
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if account:
                #layout.prop(account, "name", text=account.name, emboss=False, icon_value=0)
                layout.label(text=account.name + ' (' + account.email + ')', translate=False, icon_value=0)
            else:
                layout.label(text="", translate=False, icon_value=0)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="Accounts", icon_value=0)

class VIEW3D_UL_SpeckleStreams(bpy.types.UIList):
    def draw_item(self, context, layout, data, stream, active_data, active_propname):
        ob = data
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if stream:
                #layout.prop(account, "name", text=account.name, emboss=False, icon_value=0)
                layout.label(text=stream.name + ' (' + stream.streamId + ')', translate=False, icon_value=0)
            else:
                layout.label(text="", translate=False, icon_value=0)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="Accounts", icon_value=0)

class VIEW3D_PT_speckle(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Speckle'
    bl_context = "objectmode"
    bl_label = "Speckle.Works"

    def draw(self, context):

        scn = context.scene
        speckle = scn.speckle


        layout = self.layout
        col = layout.column()
        col.operator("scene.speckle_update", text='Update scene')
        col.label("Streams")
        col.operator("scene.speckle_import_stream", text='Import stream')
        col.operator("scene.speckle_delete_stream", text='Delete stream')
        col.operator("scene.speckle_select_stream", text='Select stream')
        col.operator("scene.speckle_select_orphans", text='Select orphans')
        col.operator("scene.speckle_not_implemented", text='Create stream')

        col.label("Accounts")
        if len(speckle.accounts) > 0:
            col.label("Current user: %s" % speckle.accounts[speckle.active_account].name)

        col.operator("scene.speckle_account_add", text="Add Account")
        col.operator("scene.speckle_accounts_load", text="Load Accounts")
        col.template_list("VIEW3D_UL_SpeckleAccounts", "", speckle, "accounts", speckle, "active_account")
        col.label("Streams")
        
        if len(speckle.accounts) > 0:
            speckle.active_account = min(speckle.active_account, len(speckle.accounts) - 1)
            account = speckle.accounts[speckle.active_account]
            col.template_list("VIEW3D_UL_SpeckleStreams", "", account, "streams", account, "active_stream")
            col.operator("scene.speckle_import_stream2", text="Load Stream")
            if len(account.streams) > 0:
                account.active_stream = min(account.active_stream, len(account.streams) - 1)
                col.label("Active stream: %s" % account.streams[account.active_stream].name)
                col.label("Stream ID: %s" % account.streams[account.active_stream].streamId)
                col.label("Units: %s" % account.streams[account.active_stream].units)


        col.label("View")
        col.operator("scene.speckle_view_stream_data_api", text='View stream data (API)')
        col.operator("scene.speckle_view_stream_objects_api", text='View stream objects (API)')
