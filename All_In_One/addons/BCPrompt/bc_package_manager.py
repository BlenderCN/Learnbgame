import ast

import bpy
from console_python import add_scrollback

from .bc_update_utils import get_gist_as_string

current_pydict = {}


def in_bpm_commands(context, m):
    if m.startswith("bpm "):
        if m.startswith('bpm pydict '):

            if not current_pydict:
                gist_id = 'ba45d7e0ebea646ce0b5'
                dict_str = get_gist_as_string(gist_id)
                current_pydict.update(ast.literal_eval(dict_str))
            else:
                add_scrollback('Using local copy from earlier..', 'INFO')

            if not current_pydict:
                add_scrollback('failed to access remote listing', 'ERROR')
                add_scrollback('No local copy was found either..', 'ERROR')
                return True

            # to debug..example
            if m == 'bpm pydict cat Mesh':
                g = current_pydict['categories']['Mesh']
                for addon, info in g.items():
                    msg = '{0}: {1}'.format(addon, info['rev'])
                    add_scrollback(msg, 'OUTPUT')

        add_scrollback(m, 'INFO')
    else:
        return False

    return True
