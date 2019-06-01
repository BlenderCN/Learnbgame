import bpy
import colorsys
import random

#pantone similar
def generate_similar_pantone(decalage, precision, color):
    el1=decalage-precision
    el2=decalage+precision
    hue=[]
    sat=[]
    lum=[]
    new_hsv=[]
    new_colors=[]
    r, v, b=color
    h, s, v = colorsys.rgb_to_hsv(r, v, b)

    #hue
    hp1=(random.uniform(el1, el2))
    hpc1=hp1/100
    var=random.randint(1, 2)
    add=h*hpc1*var
    hue.append(h+(add*2))
    hue.append(h-(add*2))
    hue.append(h+add)
    hue.append(h-add)

    #sat lum
    for i in range(1,5):
        pct=(random.uniform(el1, el2))
        pct2=pct/100
        sn=s+s*pct2
        sat.append(sn)
        vn=v+v*pct2
        lum.append(vn)

    for i in range(0,4):
        new_hsv.append([hue[i], sat[i], lum[i]])
        
    new_hsv.sort(reverse=True)

    for i in range(0, 2):
        nh, ns, nv=new_hsv[i]
        nr, nv, nb=colorsys.hsv_to_rgb(nh,ns,nv)
        new_colors.append([nr, nv, nb])
    new_colors.append(color)
    for i in range(2, 4):
        nh, ns, nv=new_hsv[i]
        nr, nv, nb=colorsys.hsv_to_rgb(nh,ns,nv)
        new_colors.append([nr, nv, nb])
        
    return new_colors

#pantone monochromatic
def generate_monochromatic_pantone(decalage, precision, color):
    el1=decalage-precision
    el2=decalage+precision
    sat=[]
    lum=[]
    new_hsv=[]
    new_colors=[]
    r, v, b=color
    h, s, v = colorsys.rgb_to_hsv(r, v, b)

    for i in range(0,4):
        mult=4
        mult1=2
        p1=random.uniform(el1, el2)
        neg=[-1,1][random.randrange(2)]
        pct1=(p1/100)*neg
        p2=random.uniform(el1, el2)
        neg=[-1,1][random.randrange(2)]
        pct2=(p2/100)*neg
        sat.append(s+((s*pct1)*mult1))
        lum.append(v+((v*pct2)*mult))

    for i in range(0,4):
        new_hsv.append([h, sat[i], lum[i]])
        
    new_hsv.sort(reverse=True)

    for i in range(0, 2):
        nh, ns, nv=new_hsv[i]
        nr, nv, nb=colorsys.hsv_to_rgb(nh,ns,nv)
        new_colors.append([nr, nv, nb])
    new_colors.append(color)
    for i in range(2, 4):
        nh, ns, nv=new_hsv[i]
        nr, nv, nb=colorsys.hsv_to_rgb(nh,ns,nv)
        new_colors.append([nr, nv, nb])
        
    return new_colors

#pantone nuance
def generate_shading_pantone(decalage, precision, color):
    el1=decalage-precision
    el2=decalage+precision
    lum=[]
    new_hsv=[]
    new_colors=[]

    r, v, b=color

    h, s, v = colorsys.rgb_to_hsv(r, v, b)

    p1=(random.uniform(el1, el2))
    neg=[-1,1][random.randrange(2)]
    var=random.randint(-4,4)
    var2=random.randint(-4,4)
    pct1=(p1/100)*neg
    add=v*pct1
    lum.append(v+(add*2))
    lum.append(v-(add*2*var))
    lum.append(v+add)
    lum.append(v-add*var2)

    for i in range(0,4):
        new_hsv.append([h, s, lum[i]])
        
    new_hsv.sort(reverse=True)

    for i in range(0, 2):
        nh, ns, nv=new_hsv[i]
        nr, nv, nb=colorsys.hsv_to_rgb(nh,ns,nv)
        new_colors.append([nr, nv, nb])
    new_colors.append(color)
    for i in range(2, 4):
        nh, ns, nv=new_hsv[i]
        nr, nv, nb=colorsys.hsv_to_rgb(nh,ns,nv)
        new_colors.append([nr, nv, nb])
        
    return new_colors

#pantone triad
def generate_triad_pantone(decalage, precision, color):
    el1=decalage-precision
    el2=decalage+precision
    sat=[]
    lum=[]
    new_hsv=[]
    new_colors=[]
    r, v, b=color
    h, s, v = colorsys.rgb_to_hsv(r, v, b)

    nb1=h+0.333
    nh1=float(str(nb1-int(nb1))[1:])
    nb2=h+0.666
    nh2=float(str(nb2-int(nb2))[1:])

    for i in range(0,4):
        mult=3
        mult1=2
        p1=random.uniform(el1, el2)
        neg=[-1,1][random.randrange(2)]
        pct1=(p1/100)*neg
        p2=random.uniform(el1, el2)
        neg=[-1,1][random.randrange(2)]
        pct2=(p2/100)*neg
        sat.append(s+((s*pct1)*mult1))
        lum.append(v+((v*pct2)*mult))

    rd=random.choice([-1,0,1])
    if rd==0:
        for i in range(0,2):
            new_hsv.append([nh1, sat[i], lum[i]])
        for i in range(2,4):
            new_hsv.append([nh2, sat[i], lum[i]])
    elif rd==-1:
        for i in range(0,2):
            new_hsv.append([nh1, sat[i], lum[i]])
        new_hsv.append([h, sat[2], lum[2]])
        new_hsv.append([nh2, sat[3], lum[3]])
    elif rd==1:
        new_hsv.append([nh1, sat[0], lum[0]])
        new_hsv.append([h, sat[1], lum[1]])
        for i in range(2,4):
            new_hsv.append([nh2, sat[i], lum[i]])

    for i in range(0, 2):
        nh, ns, nv=new_hsv[i]
        nr, nv, nb=colorsys.hsv_to_rgb(nh,ns,nv)
        new_colors.append([nr, nv, nb])
    new_colors.append(color)
    for i in range(2, 4):
        nh, ns, nv=new_hsv[i]
        nr, nv, nb=colorsys.hsv_to_rgb(nh,ns,nv)
        new_colors.append([nr, nv, nb])
        
    return new_colors

#find complementary from rgb to hsv
def get_complementary(color):
    r, v, b = color
    h, s, v = colorsys.rgb_to_hsv(r, v, b)
    nb=h+0.5
    nh=float(str(nb-int(nb))[1:])
    comp_hsv=[nh,s,v]
    # return the result
    return comp_hsv

#pantone complementary
def generate_complementary_pantone(decalage, precision, color):
    el1=decalage-precision
    el2=decalage+precision
    sat=[]
    lum=[]
    new_hsv=[]
    new_colors=[]
    r, v, b=color
    h, s, v = colorsys.rgb_to_hsv(r, v, b)

    nh=get_complementary(color)[0]
    comp=[nh,s,v]

    for i in range(0,4):
        mult=3
        mult1=2
        p1=random.uniform(el1, el2)
        neg=[-1,1][random.randrange(2)]
        pct1=(p1/100)*neg
        p2=random.uniform(el1, el2)
        neg=[-1,1][random.randrange(2)]
        pct2=(p2/100)*neg
        sat.append(s+((s*pct1)*mult1))
        lum.append(v+((v*pct2)*mult))

    for i in range(0,2):
        new_hsv.append([h, sat[i], lum[i]])
    new_hsv.append([nh, sat[2], lum[2]])
    new_hsv.append(comp)

    for i in range(0, 2):
        nh, ns, nv=new_hsv[i]
        nr, nv, nb=colorsys.hsv_to_rgb(nh,ns,nv)
        new_colors.append([nr, nv, nb])
    new_colors.append(color)
    for i in range(2, 4):
        nh, ns, nv=new_hsv[i]
        nr, nv, nb=colorsys.hsv_to_rgb(nh,ns,nv)
        new_colors.append([nr, nv, nb])
        
    return new_colors