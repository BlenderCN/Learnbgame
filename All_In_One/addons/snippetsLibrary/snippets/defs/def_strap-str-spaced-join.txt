def strap(*args):
    '''return a string like the output of print() with multiple args'''
    return(' '.join([str(a) for a in args]))