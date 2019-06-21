
if "bpy" in locals():
    # Reloaded multifiles
    import importlib

    importlib.reload(space_region)

else:
    print("imported")
    # Imported multifiles
    from .src import space_region

