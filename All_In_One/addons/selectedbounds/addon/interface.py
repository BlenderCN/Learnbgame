def draw(self, context):

    layout = self.layout

    addon = context.user_preferences.addons[__name__.partition('.')[0]]

    option = context.scene.selected_bounds if addon.preferences.scene_independent else addon.preferences

    column = layout.column()

    if not context.window_manager.is_selected_bounds_drawn:

        column.operator('view3d.selected_bounds')

    else:

        column.prop(context.window_manager, 'selected_bounds')

        if context.window_manager.selected_bounds:

            if addon.preferences.scene_independent or addon.preferences.display_preferences:

                column = layout.column(align=True)

                if not addon.preferences.scene_independent and addon.preferences.display_preferences and addon.preferences.mode_only:

                    column.prop(option, 'mode', text='')

                else:

                    column.prop(option, 'mode', text='')

                    row = column.row(align=True)

                    if context.object and option.use_object_color:

                        row.prop(context.object, 'color', text='')

                    else:

                        row.prop(option, 'color', text='')

                    row.prop(option, 'use_object_color', text='', icon='OBJECT_DATA')

                    column.prop(option, 'width')

                    column.prop(option, 'length', slider=True)
