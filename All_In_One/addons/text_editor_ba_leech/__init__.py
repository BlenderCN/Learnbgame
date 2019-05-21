bl_info = {
    "name": "BlenderArtists.org code leecher",
    "author": "zeffii",
    "version": (0, 2, 0),
    "blender": (2, 6, 4),
    "location": "Text Editor",
    "description": "scrapes code object from data found at post link",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

if "bpy" in locals():
    import imp
    imp.reload(text_editor_bacodeleech)

else:
    import bpy
    from . import text_editor_bacodeleech

def AddBAVariables():
    bpy.types.Scene.ba_post_id = bpy.props.StringProperty(
        name = "Post ID",
        description = "BA post ID containing desired snippet(s)",
        default = ""
    ) 


def register():
    AddBAVariables()
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
