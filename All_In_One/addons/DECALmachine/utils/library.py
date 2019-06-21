from . registration import get_prefs


def get_lib():
    idx = get_prefs().decallibsIDX
    libs = get_prefs().decallibsCOL
    active = libs[idx] if libs else None

    return idx, libs, active
