import os

# TODO: move this is
def explode_path(p):
    p = os.path.normpath(p)
    p = p.split(os.sep)
    return p


def implode_path(p):
    return os.sep.join(p)


def rtrim_path_until(p, dir):
    parts = explode_path(p)
    try:
        i = list(reversed(parts)).index(dir)
        if i == 0:
            return p
    except ValueError:
        return ''
    return implode_path(parts[0:-i])


def get_data_path(p):
    data_path = rtrim_path_until(p, 'data')
    if data_path == '':
        return os.path.dirname(p)
    return data_path
