import sys
debug = 0


def print(*args, sep=' ', end='\n'):
    if debug:
        dprint("ST_DB: ", *args)

dprint = print
