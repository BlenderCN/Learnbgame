
# vertex color
def VertexColor(self, context, layout, owner, datablock):
    '''
        Vertex color buttons.
    '''

    me = owner.data

    row = layout.row()
    column = row.column()

    column.template_list('MESH_UL_uvmaps_vcols', 'vcols', me, 'vertex_colors', me.vertex_colors, 'active_index', rows=1)

    column = row.column(align=True)
    column.operator('mesh.vertex_color_add', icon='ZOOMIN', text='')
    column.operator('mesh.vertex_color_remove', icon='ZOOMOUT', text='')
