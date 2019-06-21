# <pep8 compliant>

bl_info = {
    "name": "Display Area Spaces in Header",
    "author": "Satish Goda (iluvblender on BA, satishgoda@gmail.com)",
    "version": (0, 1),
    "blender": (2, 7, 0),
    "location": "Most Editors -> Header",
    "description": "Displays spaces that were activated in all the areas so that you can \
                    conviniently switch between then",
    "warning": "",
    "category": "Learnbgame",
}

"""Display Area Spaces in Header"""

import bpy


def draw(self, context):
    spaces = tuple(filter(lambda space: space.type != context.area.type, context.area.spaces))
    if spaces:
        row = self.layout.row(align=True)
        row.alert = True
        for space in spaces:
            kwargs = {}
            space_rna = space.rna_type.properties['type'].enum_items[space.type]
            kwargs['text'] = '' #space_rna.name
            kwargs['icon'] = space_rna.icon
            op_props = row.operator('wm.context_set_enum', **kwargs)
            op_props.data_path = "area.type"
            op_props.value = space.type
        row.operator('screen.spacedata_cleanup', text='', emboss=not False, icon='CANCEL')


def _doIt(process):
    only_headers = lambda typestr: typestr.find('HT_header') != -1
    processstr = ('remove', 'prepend')
    for headerstr in filter(only_headers, dir(bpy.types)):
        headertype = eval('bpy.types.' + headerstr)
        getattr(headertype, processstr[process])(draw)


def register():
    _doIt(1)


def unregister():
    _doIt(0)


if __name__ == '__main__':
    register()
