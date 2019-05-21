import bpy

from .preferences import get_addon_preferences
from .functions.update_functions import get_subdirectories_items

#font list
class FontUIList(bpy.types.UIList):

    show_subdirectory_name : bpy.props.BoolProperty(name = "Show Subdirectories", description = "Show Subdirectories")
    show_favorite_icon : bpy.props.BoolProperty(name = "Show Favorites", description = "Show Favorites")
    show_fake_user : bpy.props.BoolProperty(name = "Show Fake User", description = "Show Fake User")

    subdirectories_filter : bpy.props.EnumProperty(items = get_subdirectories_items, 
                                                name = "Subdirectories",
                                                description = "Display only specific Subdirectories")
    favorite_filter : bpy.props.BoolProperty(name = "Favorites Filter", description = "Show Only Favorites")
    invert_filter : bpy.props.BoolProperty(name = "Invert Filter", description = "Invert Filter")
    fake_user_filter : bpy.props.BoolProperty(name = "Fake User Filter", description = "Fake User Filter")

    subdirectories_sorting : bpy.props.BoolProperty(name = "Sort by Subdirectories", description = "Sort by Subdirectories")
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, flt_flag) :
        layout.use_property_split = True # Active single-column layout
        #self.use_filter_show = True

        #text_index = bpy.context.active_object.data.fontselector_index

        row = layout.row(align = True)

        if item.missingfont :
            row.label(icon = 'ERROR')
        row.label(text = item.name)

        if self.show_subdirectory_name :
            row.label(text = item.subdirectory)

        if self.show_fake_user :
            if item.index == active_data.fontselector_index :
                try :
                    if bpy.data.fonts[item.name].use_fake_user :
                        icon = 'FAKE_USER_ON'
                    else :
                        icon = 'FAKE_USER_OFF'
                    row.prop(bpy.data.fonts[item.name], 'use_fake_user', text = "", icon = icon)
                except KeyError :
                    row.label(icon = 'RADIOBUT_OFF')
            else :
                try :
                    if bpy.data.fonts[item.name].use_fake_user :
                        row.prop(bpy.data.fonts[item.name], 'use_fake_user', text = "", icon = 'FAKE_USER_ON')
                    else :
                        row.label(icon = 'RADIOBUT_OFF')
                except KeyError :
                    row.label(icon = 'RADIOBUT_OFF')
        
        if self.show_favorite_icon :
            icon = 'SOLO_ON' if item.favorite else 'SOLO_OFF'
            row.prop(item, "favorite", text = "", icon = icon, emboss = True)


    def draw_filter(self, context, layout):
        wm = bpy.data.window_managers['WinMan']

        layout.use_property_split = True # Active single-column layout
        flow = layout.grid_flow(row_major=True, columns=0, even_columns=False, even_rows=False, align=True)

        # FILTER p1
        box = flow.box()
        row = box.row(align=True)
        row.label(icon = 'VIEWZOOM')
        # search classic
        row.prop(self, 'filter_name', text = '')

        # FILTER p3
        box = flow.box()
        row = box.row(align=True)
        row.label(icon = 'FILE_FOLDER')
        # filter by subfolder
        row.prop(wm, 'fontselector_subdirectories', text = '')
        row.operator('fontselector.open_subdirectory', text = '', icon = 'FILE_FOLDER')

        # FILTER p2
        box = flow.box()
        row = box.row(align=True)
        row.label(icon = 'FILTER')
        # show only fake user
        row.prop(self, 'fake_user_filter', text = '', icon = 'FAKE_USER_ON')
        # show only favorites
        row.prop(self, 'favorite_filter', text = '', icon = 'SOLO_ON')
        # invert filtering
        row.prop(self, 'invert_filter', text = '', icon = 'ARROW_LEFTRIGHT')

        # SORT
        box = flow.box()
        row = box.row(align=True)
        row.label(icon = 'SORTSIZE')
        # sort by subfolder
        row.prop(self, 'subdirectories_sorting', text = '', icon = 'FILE_FOLDER')
        # sort invert
        row.prop(self, 'use_filter_sort_reverse', text = '', icon = 'ARROW_LEFTRIGHT')

        # VIEW
        box = flow.box()
        row = box.row(align=True)
        row.label(icon = 'HIDE_OFF')
        # show subfolder option
        row.prop(self, 'show_subdirectory_name', text = '', icon = 'FILE_FOLDER')
        # show fake user
        row.prop(self, 'show_fake_user', text = '', icon = 'FAKE_USER_ON')
        # show favorite
        row.prop(self, 'show_favorite_icon', text = '', icon = 'SOLO_OFF')
        

    # Called once to filter/reorder items.
    def filter_items(self, context, data, propname):
        # This function gets the collection property (as the usual tuple (data, propname)), and must return two lists:
        # * The first one is for filtering, it must contain 32bit integers were self.bitflag_filter_item marks the
        #   matching item as filtered (i.e. to be shown), and 31 other bits are free for custom needs. Here we use the
        #   first one to mark VGROUP_EMPTY.
        # * The second one is for reordering, it must return a list containing the new indices of the items (which
        #   gives us a mapping org_idx -> new_idx).
        # Please note that the default UI_UL_list defines helper functions for common tasks (see its doc for more info).
        # If you do not make filtering and/or ordering, return empty list(s) (this will be more efficient than
        # returning full lists doing nothing!).
        
        # Default return values.
        flt_flags = []
        flt_neworder = []

        helper_funcs = bpy.types.UI_UL_list

        col = getattr(data, propname)

        subdirectories_filter = bpy.data.window_managers['WinMan'].fontselector_subdirectories
        wm = bpy.data.window_managers['WinMan']
        
        ### FILTERING ###

        if self.filter_name or subdirectories_filter != "All" or self.favorite_filter or self.invert_filter or self.fake_user_filter :
            flt_flags = [self.bitflag_filter_item] * len(col)

            # name search
            if self.filter_name :
                #flt_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, col, "name", flags=None, reverse=False)
                for idx, font in enumerate(col) :
                    if flt_flags[idx] != 0 :
                        if self.filter_name.lower() not in font.name.lower() :
                            flt_flags[idx] = 0
            # subdir filtering
            if subdirectories_filter != 'All' :
                for idx, font in enumerate(col) :
                    if flt_flags[idx] != 0 :
                        if font.subdirectory != subdirectories_filter :
                            flt_flags[idx] = 0

            # favs filtering

            if self.favorite_filter :
                for idx, font in enumerate(col) :
                    if flt_flags[idx] != 0 :
                        if font.favorite ==False :
                            flt_flags[idx] = 0
            
            # fake user filtering
            if self.fake_user_filter :
                for idx, font in enumerate(col) :
                    if flt_flags[idx] != 0 :
                        try :
                            if not bpy.data.fonts[font.name].use_fake_user :
                               flt_flags[idx] = 0
                        except KeyError : 
                            flt_flags[idx] = 0

            # invert filtering
            if self.invert_filter :
                for idx, font in enumerate(col) :
                    if flt_flags[idx] != 0 :
                        flt_flags[idx] = 0
                    else :
                        flt_flags[idx] = self.bitflag_filter_item

        ### REORDERING ###
        if self.subdirectories_sorting :
            _sort = [(idx, font) for idx, font in enumerate(col)]
            flt_neworder = helper_funcs.sort_items_helper(_sort, key=lambda font: font[1].subdirectory)

        return flt_flags, flt_neworder