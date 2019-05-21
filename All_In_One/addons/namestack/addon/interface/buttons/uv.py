
# uv
def UV(self, context, layout, owner, datablock):
    '''
        UV buttons.
    '''

    mesh = owner.data
    # group = ob.vertex_groups.active

    row = layout.row()
    row.template_list('MESH_UL_uvmaps_vcols', 'uvmaps', mesh, 'uv_textures', mesh.uv_textures, 'active_index', rows=1)

    column = row.column(align=True)
    column.operator('mesh.uv_texture_add', icon='ZOOMIN', text='')
    column.operator('mesh.uv_texture_remove', icon='ZOOMOUT', text='')
