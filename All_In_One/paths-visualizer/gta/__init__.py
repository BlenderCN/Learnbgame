if "init_data" in locals():
    import importlib
    importlib.reload(sapaths)
    importlib.reload(ivpaths)
    print("Reloaded gta multifiles")
else:
    from . import sapaths
    from . import ivpaths
    print("Imported gta multifiles")

init_data = True