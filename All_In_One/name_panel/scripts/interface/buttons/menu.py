
def menu(self, context):

    # layout
    layout = self.layout

    # option
    option = context.scene.NamePanel

    # label
    layout.label(text='Operators')

    # seperate
    layout.separator()

    # batch auto name
    layout.operator('view3d.auto_name', icon='AUTO')

    # bath name
    op = layout.operator('wm.batch_name', icon='SORTALPHA')
    op.simple = False
    op.quickBatch = False

    # batch copy
    layout.operator('view3d.transfer_name', icon='COPYDOWN')

    # is option.regex
    if option.regex or context.window_manager.BatchName.regex:

        # separate
        layout.separator()

        # operator; regular expression cheatsheet
        layout.operator('wm.regular_expression_cheatsheet', icon='NEW')

    # separate
    layout.separator()

    # label
    layout.label(text='Panel Options')

    # seperate
    layout.separator()

    # is display names
    if option.displayNames:

            # pin active object
            layout.prop(option, 'pinActiveObject')

    # is display bone names
    if option.displayBones:

            # pin active bone
            layout.prop(option, 'pinActiveBone')

    # hide find
    layout.prop(option, 'hideFind')

    # isnt hide find
    if not option.hideFind:

        # hide replace
        layout.prop(option, 'hideReplace')

    # isnt hide replace
    if not option.hideFind and not option.hideReplace:

        # clear search
        layout.prop(option, 'clearSearch')

    # separate
    layout.separator()

    # reset panel
    op = layout.operator('wm.reset_name_panel_settings', text='Reset Panel', icon='LOAD_FACTORY')
    op.panel = True
    op.auto = False
    op.names = False
    op.name = False
    op.copy = False
