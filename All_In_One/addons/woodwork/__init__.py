# add-on info
bl_info = {
    "name": "wood work",
    "description": "Help joining timber for woodworkers",
    "author": "Christophe Chabanois",
    "version": (1, 0),
    "blender": (2, 71, 0),
    "location": "View3D > Tool Shelf > Woodworking",
    "warning": "",
    "wiki_url": "https://github.com/Khrisbie/blender-woodworking",
    "category": "Learnbgame"
}


# import files in package
if "bpy" in locals():
    print("Reloading WoodWorking v %d.%d" % bl_info["version"])
    import imp

    imp.reload(mortise_properties)
    imp.reload(mortise)
    imp.reload(tenon_properties)
    imp.reload(tenon)
    imp.reload(joints_panel)

    imp.reload(piece_properties)
    imp.reload(piece)
    imp.reload(components_panel)

    imp.reload(scene_woodwork)
    imp.reload(object_woodwork)

    imp.reload(translations)

else:
    print("Loading WoodWorking v %d.%d" % bl_info["version"])

    from . import mortise_properties
    from . import mortise
    from . import tenon_properties
    from . import tenon
    from . import joints_panel

    from . import piece_properties
    from . import piece
    from . import components_panel

    from . import scene_woodwork
    from . import object_woodwork

    from . import translations


# registration
def register():
    tenon_properties.register()
    tenon.register()
    mortise_properties.register()
    mortise.register()
    joints_panel.register()

    piece_properties.register()
    piece.register()
    components_panel.register()

    scene_woodwork.register()
    object_woodwork.register()

    translations.register(__name__)


def unregister():
    translations.unregister(__name__)

    object_woodwork.unregister()
    scene_woodwork.unregister()

    components_panel.unregister()
    piece.unregister()
    piece_properties.unregister()

    joints_panel.unregister()
    mortise.unregister()
    mortise_properties.unregister()
    tenon.unregister()
    tenon_properties.unregister()

if __name__ == '__main__':
    register()
