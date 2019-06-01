import bpy

class PaletteShaderNode(bpy.types.NodeCustomGroup):
    bl_name = 'PaletteShaderNode' 
    bl_label = 'Palette Tool'
    bl_icon = 'GROUP_VCOL'
    bl_options = {'REGISTER', 'UNDO'}
    
    #palette_list=bpy.props.EnumProperty(name='Palette List', items=PaletteListCallback)
    #CustomBool=bpy.props.BoolProperty(name="MyCustomBool", default=False)
    
    @classmethod
    def poll(cls, context):
        return len(bpy.data.window_managers['WinMan'].palette)!=0
    
    def init(self, context):
        self.node_tree = bpy.data.node_groups.get('___palette_group___')
        # or
        #self.node_tree = bpy.data.node_groups.new('name of the new nodegroup', 'ShaderNodeTree')
    
#    def draw_buttons(self, context, layout):
#        prop=bpy.data.window_managers['WinMan'].palette[0]
#        if len(prop.palettes)!=0:
#            for p in prop.palettes:
#                
#            row=layout.row(align=True)
#            for c in prop.palettes[prop.palette_list].colors:
#                row.prop(c, 'color_value', text='')
#        else:
#            layout.label('No Color Palettes')
    def draw_buttons(self, context, layout):
        palette_prop=bpy.data.window_managers['WinMan'].palette[0]
        idx=palette_prop.index
        col_per_row=palette_prop.color_per_row
        box=layout.box()
        col=box.column()
        col.label('Node Output', icon='GROUP_VCOL')
        if len(palette_prop.palettes)!=0:
            col.prop(palette_prop, 'palette_list', text='')
            row=col.row(align=True)
            for c in palette_prop.palettes[palette_prop.palette_list].colors:
                row.prop(c, 'color_value', text='')
        else:
            col.label("No Existing Palette", icon='INFO')
        bbox=layout.box()
        row=bbox.row(align=True)
        if palette_prop.node_palette_manager_hide==False:
            row.prop(palette_prop, 'node_palette_manager_hide', text='', icon='TRIA_DOWN', emboss=False)
        else:
            row.prop(palette_prop, 'node_palette_manager_hide', text='', icon='TRIA_RIGHT', emboss=False)
        row.label('Palette Manager', icon='MODIFIER')
        if palette_prop.node_palette_manager_hide==False:
            # palette management
            if palette_prop.manage_menu==True:
                row=bbox.row(align=True)
                row.prop(palette_prop, 'manage_menu', text='', icon='LOOP_BACK', emboss=False)
                row.separator()
                row.prop(palette_prop.palettes[palette_prop.index], 'name', text='')
                row.operator('palette.remove_palette', text='', icon='X').index=idx
                row.separator()
                row.operator('palette.add_color', text='', icon='DISCLOSURE_TRI_RIGHT').index=palette_prop.index

                if len(palette_prop.palettes[idx].colors)==0:
                    row=bbox.row(align=True)
                    row.label('No Colors', icon='INFO')
                else:
                    col_per_row=1
                    col=bbox.column(align=True)
                    row=col.row(align=True)
                    ct=-1
                    ctl=0
                    for c in palette_prop.palettes[idx].colors:
                        ct+=1
                        ctl+=1
                        if (ct/col_per_row).is_integer()==True:
                            row=col.row(align=True)
                            ctl=0
                        row.prop(c, 'temp_name', text='')
                        row.operator("palette.rename_color", text='', icon='FILE_TICK').index=ct
                        row.separator()
                        row.prop(c, 'color_value', text='')
                        row.separator()
                        row.operator("palette.remove_color", text='', icon='X').index=ct
                    if ((ct+1)/col_per_row).is_integer()==False:
                        diff=col_per_row-(ctl+1)
                        if palette_prop.display_color_names==True:
                            diff=diff*2
                        for i in range(0, diff):
                            row.label()
                    
            # palette menu
            else:
                row=bbox.row(align=True)
                row.operator('palette.create_palette', text='Create Palette', icon='DISCLOSURE_TRI_RIGHT')
                row.separator()
                row.operator("palette.refresh_from_files", text='', icon='FILE_REFRESH')
                row.separator()
                row.prop(palette_prop, 'display_color_names', text='', icon='VISIBLE_IPO_ON')
                row.separator()
                row.operator('palette.zoom_actions', text='', icon='ZOOM_IN').action = 'PLUS'
                row.operator('palette.zoom_actions', text='', icon='ZOOM_OUT').action = 'MINUS'
                
                #pantone
                box=bbox.box()
                row=box.row(align=True)
                if palette_prop.pantone_hide==True:
                    row.prop(palette_prop, 'pantone_hide', icon_only=True, icon='TRIA_RIGHT', emboss=False)
                else:
                    row.prop(palette_prop, 'pantone_hide', icon_only=True, icon='TRIA_DOWN', emboss=False)
                row.label("Pantone Creation", icon='COLORSET_04_VEC')
                if palette_prop.pantone_hide==False:
                    split=box.split()
                    col=split.column(align=False)
                    col.label('Name')
                    col.label('Base')
                    col.label('Type')
                    col.label('Offset')
                    col.label('Precision')
                    col=split.column(align=False)
                    col.prop(palette_prop, 'pantone_name',text='')
                    col.prop(palette_prop, 'pantone_base_color', text='')
                    col.prop(palette_prop, 'pantone_type',text='')
                    col.prop(palette_prop, 'pantone_offset',text='', slider=True)
                    col.prop(palette_prop, 'pantone_precision',text='', slider=True)
                    row=box.row(align=False)
                    row.operator("palette.create_pantone", text='Generate', icon='GROUP_VCOL')
                if len(palette_prop.palettes)!=0:
                    pt=-1
                    for p in palette_prop.palettes:
                        pt+=1
                        box=bbox.box()
                        col=box.column(align=True)
                        row=col.row(align=True)
                        if p.name==palette_prop.palette_list:
                            row.label(icon='SPACE2')
                        else:
                            row.operator("palette.switch_node_palette", text='', icon='LAYER_USED', emboss=False).index=pt
                        if p.hide==True:
                            row.prop(p, 'hide', icon_only=True, icon='TRIA_RIGHT', emboss=False)
                        else:
                            row.prop(p, 'hide', icon_only=True, icon='TRIA_DOWN', emboss=False)
                        row.label(p.name, icon='GROUP_VCOL')
                        row.operator("palette.switch_to_management", text='', icon='SETTINGS', emboss=False).index=pt
                        row.operator('palette.remove_palette', text='', icon='X', emboss=False).index=pt
                        row.operator("palette.add_color", text='', icon='DISCLOSURE_TRI_RIGHT', emboss=False).index=pt
                        row.operator("palette.get_shader_node_group", text='', icon='NODE_SEL', emboss=False).index=pt
                        if p.hide==False:
                            col.separator()
                            row=col.row(align=True)
                            ct=-1
                            ctl=0
                            if len(p.colors)==0:
                                row=col.row(align=True)
                                row.label('No Colors', icon='INFO')
                            else:
                                for c in p.colors:
                                    ct+=1
                                    ctl+=1
                                    if (ct/col_per_row).is_integer()==True:
                                        row=col.row(align=True)
                                        ctl=0
                                    if palette_prop.display_color_names==True:
                                        row.label(c.name)
                                    row.prop(c, 'color_value', text='')
                                if ((ct+1)/col_per_row).is_integer()==False:
                                    diff=col_per_row-(ctl+1)
                                    if palette_prop.display_color_names==True:
                                        diff=diff*2
                                    for i in range(0, diff):
                                        row.label()
                else:
                    row=bbox.row()
                    row.label("No Existing Palette", icon='INFO')