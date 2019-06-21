def menu_menu(cls, method):
    if isinstance(cls, str):
        menu = lambda menu, context: menu.layout.menu(cls)
    elif hasattr(cls, 'bl_icon') and cls.bl_icon:
        menu = lambda menu, context: menu.layout.menu(cls.bl_idname, icon=cls.bl_icon)
    else:
        menu = lambda menu, context: menu.layout.menu(cls.bl_idname)
    method(menu)
    return cls

def menu_operator(cls, method):
    if cls.bl_icon:
        operator = lambda menu, context: menu.layout.operator(cls.bl_idname, text="something something", icon=cls.bl_icon)
    else:
        operator = lambda menu, context: menu.layout.operator(cls.bl_idname, text="something something")
    method(operator)
    return cls