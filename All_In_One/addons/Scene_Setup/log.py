def fake_yaml(i, y):
    vals = str(y)
    indent ="\n  "
    if type(y) is dict:
        vals = ""
        for k,v in y.items():
            vals += fake_yaml(k,v)+'\n'
    out = "{}:\n{}".format(i, vals).rstrip('\n')
    return out.replace('\n',indent)

def fake_att(obj):
    logging = {}
    for k in dir(obj):
        if '__' not in k:
            logging[k] = str(getattr(obj,k,'???'))
    return logging

def yaml(i, y, quiet=False):
    if not quiet:
        print(fake_yaml(i,y)+'\n')

def att(obj):
    obj_n = getattr(obj, 'name', str(obj))
    yaml(obj_n, fake_att(obj))
