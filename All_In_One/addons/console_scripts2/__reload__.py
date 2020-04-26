
if "bpy" in locals():
    print("reloaded")
    # Reloaded multifiles
    import importlib

    importlib.reload(context_data)
    importlib.reload(console_writer)

else:
    print("imported")
    # Imported multifiles
    from .models import context_data
    from .utils import console_writer

