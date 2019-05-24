
bl_info = {
    'name': 'OOPS Schematic',
    'author': 'Pavel_Blend, Bibo',
    'version': (0, 0, 0),
    'blender': (2, 79, 0),
    "category": "Learnbgame",
    'location': 'Node Editor > OOPS Schematic',
    'description': 'Object-Oriented Programming System Schematic View'
}


from .plugin import register, unregister
