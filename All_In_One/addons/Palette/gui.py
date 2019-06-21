import bpy

# 3D view panel
class PalettePanelManager(bpy.types.Panel):
    bl_idname = "palette.panel_manager"
    bl_label = "Palette Manager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    
    @classmethod
    def poll(cls, context):
        return len(bpy.data.window_managers['WinMan'].palette)!=0
    
    def draw(self, context):
        palette_prop=bpy.data.window_managers['WinMan'].palette[0]
        idx=palette_prop.index
        col_per_row=palette_prop.color_per_row
        
        layout = self.layout
        try:
            # palette management
            if palette_prop.manage_menu==True:
                row=layout.row(align=True)
                row.prop(palette_prop, 'manage_menu', text='', icon='LOOP_BACK', emboss=False)
                row.separator()
                row.prop(palette_prop.palettes[palette_prop.index], 'temp_name', text='')
                row.operator("palette.rename_palette", text='', icon='FILE_TICK')
                row.separator()
                row.operator('palette.remove_palette', text='', icon='X').index=idx
                row.separator()
                row.operator('palette.add_color', text='', icon='DISCLOSURE_TRI_RIGHT').index=palette_prop.index

                if len(palette_prop.palettes[idx].colors)==0:
                    row=layout.row(align=True)
                    row.label('No Colors', icon='INFO')
                else:
                    col_per_row=1
                    col=layout.column(align=True)
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
                row=layout.row(align=True)
                row.operator('palette.create_palette', text='', icon='PLUS')
                #row.separator()
                row.operator("palette.refresh_from_files", text='', icon='FILE_REFRESH')
                #row.separator()
                row.operator("palette.remove_all_palette", text='', icon='CANCEL')
                #row.separator()
                row.operator("palette.open_folder", text='', icon='FILESEL')
                #row.separator()
                row.operator("palette.create_pantone", text='', icon='COLORSET_04_VEC')
                #row.separator()
                row.operator('palette.create_image_palette', text='', icon='FILE_IMAGE')
                row.separator()
                row.prop(palette_prop, 'display_color_names', text='', icon='VISIBLE_IPO_ON')
                #row.separator()
                row.operator('palette.zoom_actions', text='', icon='ZOOM_IN').action = 'PLUS'
                row.operator('palette.zoom_actions', text='', icon='ZOOM_OUT').action = 'MINUS'
                bcol=layout.column(align=True)
                pt=-1
                for p in palette_prop.palettes:
                    pt+=1
                    box=bcol.box()
                    col=box.column(align=True)
                    row=col.row(align=True)
                    if p.hide==True:
                        row.prop(p, 'hide', icon_only=True, icon='TRIA_RIGHT', emboss=False)
                    else:
                        row.prop(p, 'hide', icon_only=True, icon='TRIA_DOWN', emboss=False)
                    row.label(p.name)
                    row.operator("palette.switch_to_management", text='', icon='SETTINGS', emboss=False).index=pt
                    row.operator('palette.remove_palette', text='', icon='X', emboss=False).index=pt
                    row.operator("palette.add_color", text='', icon='DISCLOSURE_TRI_RIGHT', emboss=False).index=pt
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
        except IndexError:
            row.label("No Existing Palette", icon='INFO')
            row.operator('palette.actions_palette', text='', icon='DISCLOSURE_TRI_RIGHT').action='ADD'

# float Menu
class PaletteFloatManager(bpy.types.Operator):
    bl_idname = "palette.float_manager"
    bl_label = "Palette Manager"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
#    @classmethod
#    def poll(cls, context):

#        return 

    def execute(self, context):
        return {"FINISHED"}
    
    def invoke(self, context, event):

        wm = context.window_manager

        return wm.invoke_props_dialog(self, width=300, height=100)
    
    def check(self, context):
        return True
    
    def draw(self, context):
        palette_prop=bpy.data.window_managers['WinMan'].palette[0]
        idx=palette_prop.index
        col_per_row=palette_prop.color_per_row
        
        layout = self.layout
        try:
            # palette management
            if palette_prop.manage_menu==True:
                row=layout.row(align=True)
                row.prop(palette_prop, 'manage_menu', text='', icon='LOOP_BACK', emboss=False)
                row.separator()
                row.prop(palette_prop.palettes[palette_prop.index], 'temp_name', text='')
                row.operator("palette.rename_palette", text='', icon='FILE_TICK')
                row.separator()
                row.operator('palette.remove_palette', text='', icon='X').index=idx
                row.separator()
                row.operator('palette.add_color', text='', icon='DISCLOSURE_TRI_RIGHT').index=palette_prop.index

                if len(palette_prop.palettes[idx].colors)==0:
                    row=layout.row(align=True)
                    row.label('No Colors', icon='INFO')
                else:
                    col_per_row=1
                    col=layout.column(align=True)
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
                row=layout.row(align=True)
                row.operator('palette.create_palette', text='', icon='PLUS')
                #row.separator()
                row.operator("palette.refresh_from_files", text='', icon='FILE_REFRESH')
                #row.separator()
                row.operator("palette.remove_all_palette", text='', icon='CANCEL')
                #row.separator()
                row.operator("palette.open_folder", text='', icon='FILESEL')
                #row.separator()
                row.operator("palette.create_pantone", text='', icon='COLORSET_04_VEC')
                #row.separator()
                row.operator('palette.create_image_palette', text='', icon='FILE_IMAGE')
                row.separator()
                row.prop(palette_prop, 'display_color_names', text='', icon='VISIBLE_IPO_ON')
                #row.separator()
                row.operator('palette.zoom_actions', text='', icon='ZOOM_IN').action = 'PLUS'
                row.operator('palette.zoom_actions', text='', icon='ZOOM_OUT').action = 'MINUS'
                bcol=layout.column(align=True)
                pt=-1
                for p in palette_prop.palettes:
                    pt+=1
                    box=bcol.box()
                    col=box.column(align=True)
                    row=col.row(align=True)
                    if p.hide==True:
                        row.prop(p, 'hide', icon_only=True, icon='TRIA_RIGHT', emboss=False)
                    else:
                        row.prop(p, 'hide', icon_only=True, icon='TRIA_DOWN', emboss=False)
                    row.label(p.name)
                    row.operator("palette.switch_to_management", text='', icon='SETTINGS', emboss=False).index=pt
                    row.operator('palette.remove_palette', text='', icon='X', emboss=False).index=pt
                    row.operator("palette.add_color", text='', icon='DISCLOSURE_TRI_RIGHT', emboss=False).index=pt
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
        except IndexError:
            row.label("No Existing Palette", icon='INFO')
            row.operator('palette.actions_palette', text='', icon='DISCLOSURE_TRI_RIGHT').action='ADD'