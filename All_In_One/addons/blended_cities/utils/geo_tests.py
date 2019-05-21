import random
from random import randint as Prandint, uniform as Puniform

import bpy
from blended_cities.core.common import *

def plant(tlenght,lenght,minmaxint,choose='') :

    tlenght -=lenght
    if tlenght < 0 : return 0,0
    elif tlenght <= lenght : return 1,tlenght/2
    elif tlenght < lenght+minmaxint[0] : return 1,tlenght/2

    maxnbit=tlenght/(lenght+minmaxint[0])
    minnbit=tlenght/(lenght+minmaxint[1])
    if minnbit-int(minnbit)>0 : minnbit += 1
    #print 'between',minnbit,'and',maxnbit
    if maxnbit > minnbit :
        if choose=='min' :nbit=int(minnbit)
        elif choose=='max' :nbit=int(maxnbit)
        else : nbit=Prandint(int(minnbit),int(maxnbit))
    else : nbit=int(minnbit)
    #print 'choose',nbit
    inter = (tlenght-(nbit*lenght)) / nbit
    return nbit+1,inter

## cut a width into several widths
# @param width the total available space
# @param ob_width a min-max interval for objects
# @param ob_width a min-max interval for interval between objects
# @param sticked probability to stick two object side by side with a nul interval ( 1 = always sticked)
# @minl nul interval value (dafault 1 centimeter)
# @return list of widths like [ ob0_width, inteval0_width, ob1_width, interval1_width .... obn_width]
def cutB(width,ob_width,int_width,sticked,minl=0.01,pdeb=False) :
    #pdeb=False
    dprint('cutB :',level=2)

    min_A,max_A = int_width
    min_B,max_B = ob_width
    widths=[]
    lint=[]
    if min_A + min_B > width : return [width]
    owidth=width
    
    # check the max number of cut to avoid loop
    wt = min_B
    cutnb = 1
    nbminl = 0
    while wt < width :
        if Puniform(0.0001,1) <= sticked :
            l = minl
            nbminl += 1
        else :
            l = Puniform(min_A, max_A)
        lint.append(l)
        wt += l + min_B
        cutnb += 2
    if cutnb%2 == 0 : cutnb += 1
    dprint('max cut : %s %s'%(cutnb,cutnb%2),level=2)
    
    # cut it xixixix
    i=0
    while width>=0 and i<cutnb :
        if i%2 :
            #if Puniform(0.0001,1) <= sticked :
            #    l=minl
            #else :
            #    l=Puniform(min_A,max_A)
            l = lint[int(i/2)]
        else :l=Puniform(min_B,max_B)
        widths.append(l)
        width -=l
        i +=1
    
    # remove the last interval if exists
    if len(widths)%2 == 0 :
        width +=widths.pop(-1)
        dprint('odd removed',level=2)
    dprint('width list input\n%s'%widths,level=2)
    # should we add or substract  meters ?
    sign = -1 if width > 0 else 1

    dprint(' input %s'%(widths),level=2)
    dprint(' depart %s %s (%s cut(s))'%(width,sign,len(widths)),level=2)
    
    # rigid widths cases :
    if min_B == max_B and min_A == max_A :
        dprint(' rigid %s'%widths,level=0)
        width=abs(width)
        if sign == 1 :
            # compact
            if width < min_B*0.5 :
                if pdeb : print("reduce")
                # reduce intervals
                wm=width/len(widths)
                for wi in range(1,len(widths),2) :
                    if widths[wi]-wm >= minl :
                        width -=wm
                        widths[wi] -=wm
                    elif widths[wi] > minl :
                        width -= widths[wi]-minl
                        widths[wi] = minl
                # reduce building fronts
                wm=width/int((len(widths)*0.5)+1)
                for wi in range(0,len(widths),2) :
                    width -=wm
                    widths[wi] -=wm
            else :
                # enlarge 
                if pdeb : print("enlarge")
                width=widths[-2]+widths[-1]-width
                widths=widths[:-2]
                wm=width/len(widths)
                for wi in range(len(widths)) :
                        width -=wm
                        widths[wi] +=wm
            
        else : widths[-1] += width

    # normal case :        
    else :
        i=0
        t=0
        while width != 0 and t < 50 :
            j=Prandint(0,len(widths)-1)
            if widths[j]==minl : j -=1
            if j%2 : [min,max] = int_width
            else : [min,max] = ob_width
            # substract
            if sign==1 :
                max=widths[j]
                dprint(' id %s : min %s max %s'%(j,min,max),level=2)
                if abs(width)<=max-min :
                    widths[j] -= abs(width)
                    offset=abs(width)
                else :
                    widths[j]=Puniform(min,max)
                    offset=max-widths[j]
            # add
            else :
                min=widths[j]
                dprint(' id %s : min %s max %s'%(j,min,max),level=2)
                if width<=max-min :
                    widths[j] += width
                    offset=width                
                else :
                    widths[j]=Puniform(min,max)
                    offset=widths[j]-min
            width=width+(offset)*sign
            if pdeb : dprint(' width %s'%width)
            t+=1
        # too much iterations
        if t == 50 :
            dprint(' worst case',level=2)
            if width > 0 : widths[-1] +=width
            else :
                while width<0 :
                    if widths[-1] > abs(width) :
                        widths[-1] += width
                        width=0
                    else :
                        width +=widths[-1]
                        del(widths[-1])
    if pdeb : print(' width list final\n%s'%widths)
    return widths
'''
tlength = 40
oblength = 5
sticked = 0
cuts=[[0,0],[5,5]]
print()


nb_ob, i = plant(tlength,oblength,[0,5])
print('%s %s %s'%(nb_ob,i,oblength*nb_ob + i*(nb_ob-1)))


lengths = cutB(tlength,cuts,sticked,minl=0.001,pdeb=False)
c = 0
for l in lengths : c += l
print('%s\n%s'%(lengths,c))
'''