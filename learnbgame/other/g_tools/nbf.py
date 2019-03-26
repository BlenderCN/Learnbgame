# -*- coding: utf-8 -*-
#便利？関数集。ぶっちゃけ罪です
import re
from itertools import *
from functools import *
from mathutils import Vector,Euler,Quaternion,Matrix
from math import floor,sqrt,sin,cos,tan,asin,acos,atan,atan2,pi
import time

gentype = type((z for z in ()))

#########################################################decorators
def inverterate(f):
    def inverted(*args,**kwargs):
        return not f(*args,**kwargs)
    return inverted
    

#########################################################functional(?)

def assoc(item, lst, key = None,test = None):
    if key == None:
        key = id_func
    if cndf == None:
        def cndf(x):
            return key(x[0]) == item
    return andmap(cndf,lst)
    
def conjoin(targets,fs):
    pass
    
def disjoin(targets,fs):
    pass
    
def curry(f,a):
    def nf(*args):
        return f(a,*args)
        pass
    return nf

def rcurry(f,a):
    def nf(*args):
        return f(*args,a)
        pass
    return nf
    
def postjoin(i,lst):
    return (*lst,i)
    
def adjoin(i,lst):
    for item in lst:
        if item == i:
            return lst
    return (i,*lst)

def every(f,lsts):
    return all(map(f,zip(lsts)))

def some(f,lsts):
    return any(map(f,zip(lsts)))

def eql(a,b):
    return a == b

def y_combinator(x):
    return x(x)
    
def car(a):
        return a[0]

def cdr(b):
        return b[1]

def cprp(s):
    if s[0] == "c": return s[1:-1]
    else: return s[1:-1]

def cpr_fgen(s):
    return map(lambda x: car if x == 'a' else cdr,(cprp(s)))

def cpr(s,a):
    return reduce(lambda x,y: y(x),((a),*cpr_fgen(s)))
    
def cons(a,b):
    return (a,b)
    
def fcons(a,b,c=0):
    def f():
        c = not c
        return (a,b)[c]
    return f
    
def delay(exp):
    def expret():
        return exp
    return expret
    
def force(exp):
    return exp()    
    
def idx_select(c,idx):
    return tuple(item[idx] for item in tuple(c))
    
def ifilter(c1,c2):
    res = tmap(lambda idx: c2[idx],filter(lambda i:c1[i],rlen(c2)))
    print(len(res),len(c2))
    return res

def f2dict(fpath,mode = "r"):
    """
    Convert a file into a dictionary intepreting lines as repeating key,value pairs
    """
    return {l[0]:l[1] for l in by_x(fsplit(fpath,mode),2)}

def csvdict(fpath,mode = "r",delim = ","):
    """
    Convert a csv file into a dictionary intepreting delimiters as repeating key,value pairs
    """
    return {l[0]:l[1] for l in by_x(fread(fpath,mode).split(delim),2)}
    
def fresult_hash(f,*args,**kwargs):
    return {fdict[f.__name__]:f(*args,**kwargs)}
    
def fresult_dict(fs,arglists,kwarglists):
    fdict = {}
    result_hashes = tmap(lambda i: fresult_hash(fs[i],*arglists[i],**kwarglists[i]),rlen(fs))
    reduce(lambda x,y: fdict.update(y),((),*result_hashes))
    return fdict
    
def truef(*args,**kwargs):
    return True
    
def ws_test(s):
    return re.search(r"[^\s]",s)        
def ws_filter(coll):
    return filter(ws_test,coll)
def tws_filter(coll):
    return tuple(filter(ws_test,coll))
def tfilter(f,c):
    return tuple(filter(f,c))
    
def mem_install(init = None,mem = None):
    if mem == None:
        mem = [init]
    def mem_installer(f):
        def mem_installed(*args,**kwargs):
            return f(mem = mem,*args,**kwargs)
        return mem_installed
    return mem_installer
    
def etime():
    return time.clock() - stime 

@mem_install(init = time.clock())
def dtime(mem = None):
    """Given a global timer, return the time difference between now and the last call to self."""
    mem[0] = time.clock() - mem[0]
    return mem[0]
    
def fpack(f,*args,**kwargs):
    """
    Pack a function and its arguments into the format:
    Tuple#2:
        f
        Tuple#2:
            arguments,keyword arguments
    """
    return (f,args,kwargs)

def funpack(fpack):
    """
    Execute a function, packed arguments pair.
    """
    return fpack[0](*fpack[1],**fpack[2])

def nullf():
    pass

def cforce(y):
    if type(y) == type(nullf):
        return y()
    return y

def cforce_rec(y):
    if type(y) == type(nullf):
        return cforce_rec(y())
    return y

def wrapmap(x,y):
    def wrapped(*args,**kwargs):
        return y(cforce(x))
    return wrapped
def wrapmap2(x,y):
    def wrapped(*args,**kwargs):
        return y(x)
    return wrapped
    
def wreduce(f,c):
    """
    Wrap the first element of a generator or collection in functional form and reduce it.
    For when you want to apply one function of two arguments that unconditionally calls the first... I guess.
    """
    #if the collection is a stream
    if type(c) not in (list,tuple,set):
        for x in c:
            y = lambda *args,**kwargs:c[0]
            break
        c2 = (y,c)
    #if it's an immediate collection
    else:
        c2 = (lambda *args,**kwargs: c[0],*c[1::])
    return reduce(f,c2)
    

def lstfill(required,args):
    arglen = len(args)
    diff = (required-arglen)
    return (*args,*(None for x in range(diff*int(diff>0))))
    
    '''
    arglen = len(args)
    if arglen == 1:
        args == args[0]
        arglen = len(args)
    diff = (expected-arglen)
    return (*args,*(None for x in range(diff*int(diff>0))))
    '''
    
def setidx(i,idx,val):
    i[idx] = val
    return None
    
def setvec(i,idx,val):
    i[idx] = val[idx]
    return None

def getidx(i,idx):
    return i[idx]
    
def none_test(x):
    """
    xはNoneであるかを試す
    Test for None
    """
    return x == None
    
def inone_test(x):
    """
    xはNoneであるかを試して、結果の真偽を反転する
    Test for None, inverting truth.
    """
    return not (x == None)
    
def getattr2(i,prop):
    """
    getattr, but if passed an integer get the value fo the index i.
    may have unintended effects if there's an occasion where integers are actually used as a property.
    """
    if type(prop == int):
        return getidx(i,prop)
    
def setattr2(i,prop,val):
    """
    setattr, but if passed an integer set the value of the index i.
    will fail on immutable data.
    """
    if type(prop == int):
        setidx(i,prop,val)

#########################################################arg analysis
def argfill(expected,*args):
    diff = (expected-len(args))
    return (*args,*(None for x in range(diff*int(diff>0))))

def default_fill(args,defaults):
    args = argfill(len(defaults),*args)
    return tuple(args[a] if not none_test(args[a]) else defaults[a] for a in range(3))
    
#########################################################numerical analysis
def even(n):
    return n%2 == 0
    
def odd(n):
    return n%2 != 0

def is_prime(n):
    if n == 2:
        return n
    elif n < 2:
        return False
    elif even(n):
        return False

    sqrt_n = int(floor(sqrt(n)))
    for i in range(3, sqrt_n + 1, 2):
        if n % i == 0:
            return False
    return True

def prime_range(target_count):
    l = ()
    c = 1
    while len(l) < target_count:
        if is_prime(c):
            l = postjoin(c,l)
        c+=1
    return l
    
def pi_range(res):
    return (0,*tuple((pi/res)*r for r in range(1,res)))
def tau_range(res):
    tau = pi*2
    return (0,*tuple((tau/res)*r for r in range(1,res)))
    
#########################################################set analysis
def even_length(res):
    return even(len(res))

def odd_length(res):
    return odd(len(res))
    
#########################################################set creation
def expand(f,v,*args,**kwargs):
    return map(id_func,f(v,*args,**kwargs))
    
#########################################################hash related
    
def bidict(d):
    keys = tuple(d.keys())
    for i in keys:
        d[d[i]] = i 
    return d
    
    
#########################################################iterable related
def lst_shift(lst,count = 1):
    """
    単にcount回リストの最初のアイテムを最後の位置に入れ替えるだけ
    元のリストが変更されるので注意
    """
    for x in range(count):
        lst.append(lst.pop(0))
    return lst
    
def lst_shift_ex(lst,count = 1):
    """
    range二つとってcountで始まるようにリストのアイテムを入れ替える
    元のリストが変更されるので注意
    """
    lst_new = lst[count:len(lst)]+lst[0:count]
    lst.clear()
    lst += lst_new
    return lst
    
def continuate(lst):
    """
    i1からのリストか、
    長さ=1の場合空のチュープルを戻す
    長さは最低2でなければエラーが発生する為必要…と思われる
    return either lst from i1 or nil
    necessary? because [1::] on list causes error
    """
    if len(lst) == 1:
        return ()
    else:
        return lst[1::]
        
def ungroup(lst):
    """
    lstの中身のまた中身にの数でlstを分ける
    例：
        ungroup( ( (1,2),(3,4),(5,6) ) ) = ((1,3,5),(2,4,6))
    args:
        lst:
            中身に中身があるやつ
            とりあえず中身の中身は全部同じ長さでなきゃならん
    """
    l = len(lst)
    l2 = len(lst[0])
    r = range(l)
    r2 = range(l2)
    return tmap(lambda x: tmap(lambda y: lst[y][x],r),r2)
    
def by_x(lst,step):
    """
    lstの中身をstep個チュープルに放り込む
    例：
        by_x((1,2,3,4,5,6),2) = ((1,2),(3,4),(5,6))
    """
    return (lst[n:step+n] for n in range(0,int(len(lst)),step))
    
def reorder(new_order,lst):
    """
    new_orderの中身をインデックスと捉えて、lstの中身をnew_orderの順に再構築する
    """
    return tmap(lambda x: lst[x],type(new_order)(new_order))
    
def lstwrap(lst,offset_start,offset_end,match_type = True,rev = False):
    if rev:
        lst = lst[::1]
    res = tuple((*lst[offset_start:offset_end],*lst[offset_end::],*lst[0:offset_start]))
    if match_type:
        res = type_match(lst,res)
    return res
    
#########################################################string related
    
    
#########################################################mathutils related
def dotmu(x,y):
    return x.dot(y)    
    
def crossmu(x,y):
    return x.cross(y)
    
def normalizemu(x):
    return x.normalized()
    
#########################################################misc

def passmap(*args,**kwargs):
    for x in map(*args,**kwargs): pass

def tmap(f,c):
    return tuple(map(f,c))
    
def tfil(f,c):
    return tuple(filter(f,c))
    
def argize(*args):
    return args
    
def kwargize(**kwargs):
    """
    関数呼び出し時のキーワードシンタックスでdictを生成する
    例：
        kwargize(a = 2,b = 3) = {"a":2,"b":3}
    """
    return kwargs
kwargdict = kwargize

def setattrate(___itarget1,dbg = False,**kwargs):
    if dbg:
        print(___itarget1)
        for kw in kwargs:
            print("Key:",kw)
            print("Value:",kwargs[kw])
    if ___itarget1 == None:
        return kwargs
    anymap(lambda kw: setattr(___itarget1,kw,kwargs[kw]),kwargs)
    return kwargs

def get_other(pair,current_item,*args,**kwargs):
    return tuple(i for i in pair if i != current_item)[0]
    
def get_sel(coll,prop = "select"):
    return tuple(filter(lambda x:(getattr(coll[x],prop)),range(len(coll))))
    
def setvec(i,idx,val):
    i[idx] = val[idx]
    return None
    
def getidx(i,idx):
    return i[idx]
    
def setidx(i,idx,val):
    i[idx] = val
    return None
    
def setattr2(i,prop,val):
    """
    setattr, but if passed an integer set the value of the index i.
    Will fail on immutable data.
    """
    if type(prop == int):
        setidx(i,prop,val)
    else:
        setattr(i,prop,val)
        
def try_setattr(i,prop,val):
    try:
        return setattr2(i,prop,val)
    except:
        return 0
        
def dict2attr(obj,attrdict):
    return any(map(lambda attr: try_setattr(obj,attr,attrdict[attr]),attrdict.keys()))
    
def prop_dict(obj,filter_func = truef,result_filter = truef,targets = None):
    cdir = tuple(filter(filter_func,dir(obj)))
    def gattrate(obj,i):
        try:
            return getattr(obj,i)
        except:
            return "#_GET_ERR"
    if targets != None:
        cdir = targets
    proplist = ((i,gattrate(obj,cdir[i])) for i in range(len(cdir)))
    proplist = filter(lambda i: result_filter(i[1]),proplist)
    return {cdir[i[0]]:i[1] for i in proplist}

def prop_copy(pyobj,prop_source,excludes = None):
    if type(prop_source) == dict:
        property_dictionary = prop_source
    else:
        property_dictionary = prop_dict(prop_source)
    
    errs = [property_dictionary[i] for i in property_dictionary]
    
    if excludes != None:
        for i in excludes:
            property_dictionary.pop(i)
    for idx,x in enumerate(property_dictionary):
        try:
            item = property_dictionary[x]
            if item == "#_GET_ERR":
                continue
            setattr(pyobj,x,item)
        except Exception as e:
            errs[idx] = e
    return errs
   
   
def acc(o,instrs,):
    """
    Parse an accessor string into a series of getattr statements.
    """

    instrs = acc_instparse(instrs)
    #For the case in which the instructions contain no accessors; skip the loop and return o.
    if instrs == ():
        return o
    
    return accrate(o,instrs,0)

def accrate(o,instrs,parse_index):
    if parse_index == len(instrs):
        return o
    ftype,i = instrs[parse_index]
    #Loop over the instructions.
    if ftype:
        g = lambda x,y: x.__getitem__(y)
        if "\"" in i:
            i = i.replace("\"","")
        else:
            i = int(i)
    else:
        g = getattr
    return accrate(g(o,i),instrs,parse_index + 1)

def accset(o,instrs,val):
    """
    Parse an accessor string into a series of getattr statements.
    """

    instrs = acc_instparse(instrs)
    #For the case in which the instructions contain no accessors; skip the loop and return o.
    if instrs == ():
        return o
    
    return accsetrate(o,instrs,val,0)

def accsetrate(o,instrs,val,parse_index):
    if parse_index == len(instrs)-1:
        return setattr(o,instrs[-1][-1],val)
    ftype,i = instrs[parse_index]
    #Loop over the instructions.
    if ftype:
        g = lambda x,y: x.__getitem__(y)
        if "\"" in i:
            i = i.replace("\"","")
        else:
            i = int(i)
    else:
        g = getattr
    return accsetrate(g(o,i),instrs,val,parse_index + 1)
    
def acc_instparse(i,accdict = {'.':'0','[':'1','(':'2'}):
    def clip_initial(inst,accdict = {'.':'0','[':'1','(':'2'}):
        for i in range(len(inst)):
            if inst[i] in "([.":
                return accdict[inst[i]] + inst[(i+1)::]
    rgxer = r'[.[(]'
    parse_res = clip_initial(i)
    if parse_res == None:
        return ()
    elif len(parse_res) == 1:
        raise ValueError("Malformed accessor string")
    inst = parse_res.replace(".",".0").replace("[","[1").replace("(","(2").replace(")","").replace("]","")
    return tuple(map(lambda x: (bool(int(x[0])),x[1::]),re.split(rgxer,inst)))

def prop_switch(o,prop,new_val = True):
    init_val = acc(o,prop)
    c = 0
    while True:
        is_even = even(c)
        if is_even:
            accset(o,prop,new_val)
        else:
            accset(o,prop,init_val)
        yield is_even
        c+=1
    

#vector map return retrieve example
#q = map(lambda x: (lambda v: ((v).rotate(Euler((30,90,20))),v))(Vector(x))[1],cos)
def sreduce(f,c,*init_args,init_func = None,**init_kwargs):
    if init_func == None:
        def init_func(*args,**kwargs):
            return ()
    return reduce(f,(init_func(*init_args,**init_kwargs),*c))
    
def sreduce_offset(start_indices,strings,offset_end = 1,offset_start = 0):
    return reduce(lambda x,y: (*x,start_indices[x+1]-x[-1]) ,((start_indices[offset_start:offset]),*start_indices[offset::]))
    
def sreduce_wrap(start_indices,strings,offset_end = 1,offset_start = 0):
    return reduce(lambda x,y: (*x,start_indices[x+1]-x[-1]) ,(*(start_indices[offset_start:offset]),*start_indices[offset::]))
    
def reduce_wrap(f,lst,offset_end = 1,offset_start = 0):
    return reduce(f,lstwrap(lst,offset_start,offset_end))
    
def format_squeeze(start_indices,strings):
    space = reduce(lambda x,y: (*x,start_indices[x+1]-x[-1]) ,((start_indices[0]),*start_indices[1::]))
    