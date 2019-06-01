def decrement_name(ob):
    if not re.match(r'(.*)(.\d{3})$', ob.name):
        return
    old = ob.name
    if not D.objects.get(ob.name[:-4]):
        #rename
        ob.name = ob.name[:-4]
        print(old, '>>', ob.name)
        return(ob.name)
    else:
        num = int(ob.name[-3:])
        #maybe start at 0 to take case '.000' (but supposely covered previously)
        for i in range(1, num):
            new = ob.name[:-3] + str(i).zfill(3)
            if not bpy.data.objects.get(new):
                ob.name = new
                print(old, '>>', new, ' - from num', num, 'to', i)
                return(ob.name)
    print(ob.name, 'impossible to decrement')
    return