import materials_mgr.material_mgr


def reload():
    from importlib import reload
    modules = [materials_mgr.material_mgr]
    for module in modules:
        reload(module)


def register():
    pass


def unregister():
    pass
