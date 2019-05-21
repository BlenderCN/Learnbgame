"""\
simple autocomplete:

1) activate addon and press Enable in Autocomplete tab
2) type code in another empty text
3) try declaring variables, classes, functions
4) during typing, if you retype parts of known identifiers, a popup should open
5) choose option and it will be inserted into text
6) after object variables, enter . and member popup should open
7) its all very alpha, in case of error: try pressing ENTER on an empty line or 
   press Disable and Enable again (in target file) 
   to load existing code and create autocomplete datastructures

TODO: [x] = done, [-] = partially done, [ ] = not done

[x] make addon out of this
[x] integrate nicely: create datastructures automatically (on text open), 
    enable/disable via checkbox (maybe then load datastructures), end modal 
    operator with other operator/gui event ?
[ ] prevent segfault when loading new file and autocompleter running
[x] make menu disappear when i continue typing (change focus)
[x] correctly replace previously typed text by suggestion
[x] handle class member display correctly after pushing "PERIOD"
[ ] categorize items: Class, Function, Variable at least ( by type, M modules, classes C, functions F and "(" )
[x] handle imports, fill datastructure with all imported scopes (classes, 
    functions, modules and vars visible, local vars relevant for own code only -
    need to parse imports AND importable stuff (module handling, parse dir for 
    that ?), importable as new datastructure
    
[-] test unnamed scopes, maybe do not store them (unnecessary, maybe active 
    scope only? for indentation bookkeeping)
[x] make autocomplete info persisent, maybe pickle it, so it can be re-applied 
    to the file (watch versions, if file has been changed (not necessary, will 
    be parsed in dynamically, but maybe for big files ?)
[x] externally, continue using or discard or rebuild(!) by parsing the existing 
    code,  automate this 
[x] fix buffer behavior, must be cleared correctly, some state errors still
[x] substitute operator, or function in autocomplete ? buffer is in op, hmm, 
    shared between ops or via text.buffer stringprop delete buffer content from 
    text(select word, cut selected ?) and buffer itself and replace buffer 
    content and insert into text

[ ] make new lookups on smaller buffers, on each time on initial buffer (unnecessary)
[ ] if any keyword before variable, same line, do not accept declaration with = 
    (would be wrong in python at all) are those keyword scopes ?, no unnamed... 
    and type = scope
[x] parse existing code line by line after loading(all) or backspace (current 
    line) (done, check state machine)
[ ] BIG todo: make usable for any type of text / code   
[x] parseLine benutzen dort wird der indent gemessen! evtl bei parseIdentifier 
    keinen buffer benutzen sondern die Zeile buffer nur fuer den Lookup benutzen !!
    auch nicht indent auf -1 setzen und dann current char ermitteln.
[ ] scope parsing: check for \ as last char in previous lines, if there, prepend
    it to buffer !!! substitution, preserve whitespaces before inserted text 

[ ] scope, special cases: 
    - higher class, function(?) names not usable as lhs! only rhs 
    (usable both!)
    - higher declaration: if isinstance(parent, Class) prepend self in choice ! 
    (or check for it)
    - or if startswith(__) static vars, usable with className only 
    (check both lhs and rhs)

[-] evaluate self, and dotted stuff, or simply create entry for it ?, dot -> 
    if available, find object
[-] exclude those entries from suggestions, which match completely with the 
    buffer entry. watch for comma separated assignments, those are multiple 
    identifiers, which need to be assigned separately !!

[x] if only one matching entry in autocomplete suggestions, then substitute 
    automatically !! (press enter for that)
[x] first restore menu functionality  with self drawn menu!!
[x] lookup with dots, commas: always get the last element in sequence only after
    detecting . or , (when typing) when parsing, evaluate dotted or take last 
    part always (or leave it as is ?) and with comma watch whether ret type 
    count types match and assign one after other

[ ] take special care with lambdas, generators, list comps.? or  eval them

[ ] parenthesis: open parameter sequences in menu, and close sucessively entered
    params (highlight them separately, do similar with brackets ([]), eval 
    indexing or show possible keys (dicts) or range of indexes (list)

[x] caution with re-setting/deleting(!!) variables, exec / eval must re-parse 
    the variables too, and delete identifier list before

[x] manage fully qualified variable names internally, but cut all off whats 
    already before the last dot do not let fully qualified names pop up, prepend 
    dotted types in internal rep, and at lookup check activeScope.type as well, 
    if . occurs

[x] if name xyz is a known class name (or part of), do not look for type, use 
    class name itself.

[x] if compile returns None, this means something went wrong. Maybe the code 
    string isnt correctly assembled.
    
[x] add support for non-accessible module bge (only accessible from game engine,
    need offline raw data for this

[ ] change to static evaluation for all modules for which rst files are detected

[ ] dump rst files from python docstrings, maybe rst exists already ?

[ ] nested parenthesis evaluation (static and dynamic)

[ ] use sphinx to collect info from docstrings for static evaluation raw data (so
    only currently typed code without doc needs to be evaled dynamically
    goal is to create rst for standard python modules (if not existing) in the same
    format the bpy rsts are

[ ] enrich function definitions by type info (per Hand) and use that info for auto
    completion, parse in docstrings in RST format, otherwise parameters cant be auto
    completed, for self assume own class, for context assume bpy.context, but otherwise
    youre on your own...

[ ] handle aliased imports

[ ] ignore docstrings during autocompletion parsing, only parse them where necessary!

"""

import bpy
import bgl
import blf
import builtins
import math
import keyword
import os

running = False

#fallback method for bge module, but when its in the import list/code string, do not compile !
#best thing would be RST files for everything, no need for evaluation at all ! maybe generate for all available python modules
class RSTParser:
    
    token_list = ["class", "function", "method", "type", "module", "attribute", "rtype", "args", "data"]
  
    def parseToken(line, t, opdata):
        #print("line", line, t)
        
        #ignore indents completely here in API
        opdata.indent = 0
        opdata.activeScope.indent = 0
        
        tok = ".. " + t + "::"
        line = line.lstrip()
        if line.startswith(tok):
            line = line.split(tok)[1]
            v = line.strip()
            if t == "module":
                if opdata.activeScope.type == "class":
                    opdata.activeScope = opdata.activeScope.parent
                Module.create(v, [], opdata)
            elif t == "class":
                
                if "(" in v:
                    ind = v.index("(")
                    v = v[:ind]
                    
               
                if opdata.activeScope.type == "class": #and opdata.activeScope.type != "module":
                    opdata.activeScope = opdata.activeScope.parent
          
                Class.create(v, [], opdata)
            elif t in ("function", "method"):
                
                if "(" in v:
                    ind = v.index("(")
                    v = v[:ind]
                Function.create(v, [], opdata)
                opdata.activeScope = opdata.activeScope.parent
                
            elif t in ("data", "attribute"):
                #if t == "data": # assume ints for constants, or strings ? who knows... if no type is given
                
                print("DATA1", v)
                typ = RSTParser.parseToken(v, "type", opdata)
                if typ == None:
                    typ = "int"
                
                print("DATA2", v, typ)                                
                Declaration.create(v, typ, opdata)
                    
            elif t == "type":
                return v         
        return None
    
    def parseLine(line, opdata):
        [RSTParser.parseToken(line, t, opdata) for t in RSTParser.token_list] 
    
    def parse(name, opdata):
        
        try:
            filename = os.path.abspath(os.path.dirname(__file__) + "//static_data//" + name + ".rst")
            file = open(filename, "r")
            for line in file:
                RSTParser.parseLine(line, opdata)
        except Exception as ex:
            print(ex)
        
        
#encapsulate drawing and functionality of a menu
#select callback with parameter tuple
class Menu:
    
    color = (0.2, 0.2, 0.2, 1.0)
    hColor = (0.02, 0.4, 0.7, 1.0)
    textColor = (1.0, 1.0, 1.0, 1.0)
    width = 6 # get that from font object ?
    height = 11
    margin = 10
    pos_x = 0
    pos_y = 0
    max = 0
    highlighted = ""
    shift = int(margin / 2)
    index = -1
    wrapCount = 20
    
    def __init__(self, items):
        self.items = items
        self.itemRects = {}
    
    def highlightItem(self, x, y):
        #self.open(self.pos_x, self.pos_y)
        self.highlighted = ""
        for it in self.itemRects.items():
            ir = it[1] 
            if x >= ir[0] and x <= ir[2] and \
               y >= ir[1] and y <= ir[3]:
                #print(x, y, ir)
                self.highlighted = it[0]
                self.index = self.items.index(it[0])
                break
                    
        
    def pickItem(self):
        
        if self.highlighted != "":
            bpy.ops.text.substitute(choice = self.highlighted)
    
    def nextWrap(self):
        if self.index + self.wrapCount <= len(self.items) - 1:
            self.index += self.wrapCount
        else:
            while self.index - self.wrapCount >= 0:
                self.index -= self.wrapCount
        
        self.highlighted = self.items[self.index]
                
    def previousWrap(self):
        if self.index - self.wrapCount >= 0:
            self.index -= self.wrapCount
        else:
            while self.index + self.wrapCount <= len(self.items) - 1:
                self.index += self.wrapCount
        
        self.highlighted = self.items[self.index]
            
    def previousItem(self):
        if self.index > 0:
            self.index -= 1
        else: 
            self.index = len(self.items) - 1
          
        self.highlighted = self.items[self.index]
    
    def nextItem(self):
        
        if self.index < len(self.items) - 1:
            self.index += 1 
        else:
            self.index = 0
            
        self.highlighted = self.items[self.index]
       
    def draw(self, x, y):
         
        #memorize position once
        if self.pos_x == 0:
            self.pos_x = x
        
        if self.pos_y == 0:
            self.pos_y = y
        
        #store rect of each item    
        if len(self.itemRects) == 0:
            self.max = 0
           
            for it in self.items:
                if len(it) > self.max:
                    self.max = len(it)
            
            width = self.max * self.width
            
            #i = 0
            j = 0
            for it in self.items:
                rx = 0
                j = self.items.index(it) + 1
                while j > self.wrapCount:
                    j -= self.wrapCount
                    rx += (width + self.margin)
                    
                rect_x = self.pos_x + rx - self.margin
                rect_y = self.pos_y - j * (self.height + self.margin) 
                     
                self.itemRects[it] = (rect_x, rect_y, 
                                      rect_x + width + self.margin, 
                                      rect_y + self.height + self.margin)
                #i += 1
        
        #auto highlight if only one entry, to be able to press enter and done
        if len(self.items) == 1:
            self.highlighted = self.items[0]
            self.index = 0
            
        self.open(self.pos_x, self.pos_y)     
    
    def open(self, x, y):
        
        if len(self.items) == 0:
            return
         
        width = self.max * self.width        
        
        #menu background
        bgl.glColor4f(*self.color)
        
        
        items = len(self.items)
        rects = math.ceil(items / self.wrapCount)
        for i in range(0, rects):
            
            d = items/self.wrapCount
            if d > 1:
                d = 1
            h = int(d * self.wrapCount)   
            bgl.glRecti(x + i * (width + self.margin) - self.margin, y - (self.height + self.margin) * h - self.margin , 
                    x + (i+1) *(width + self.margin), y  - self.shift) #+ self.height + self.margin)
            if items > self.wrapCount:
                items -= self.wrapCount
        
        if self.highlighted != "":
            ir = self.itemRects[self.highlighted]    
            bgl.glColor4f(*self.hColor)
            bgl.glRecti(ir[0], ir[1] - self.shift, ir[2], ir[3] - 2 * self.shift)
            #bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
        
        font_id = 0  # XXX, need to find out how best to get this.        
        bgl.glColor4f(*self.textColor)
        
        for it in self.items:
            rect = self.itemRects[it]
            
            #if it == self.highlighted:
            #    bgl.glColor4f(self.color[0], self.color[1], self.color[2], self.color[3])
              
            blf.position(font_id, float(rect[0] + self.margin), float(rect[1]), 0) # check for boundaries ?
            blf.size(font_id, self.height, 72)
            blf.draw(font_id, it)
            
            #if it == self.highlighted:
            #   bgl.glColor4f(self.textColor[0], self.textColor[1], self.textColor[2], self.textColor[3])
            
        # restore opengl defaults
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
        
         
class Declaration:
   
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.indent = 0
        self.parent = None
       
    def __str__(self):
        return self.type
    
    def qualify(self, opdata):
        #cant support classes in unnamed scopes and functions this way (makes this sense?)
        pstr = self.name
        #if self.parent != None and (isinstance(self.parent, Class) or \
       # isinstance(self, Class) and isinstance(self.parent, Module)) and \
        #self.parent.name != opdata.module.name:
        #    pstr = self.parent.name + "." + self.name
            
        if ((isinstance(self, Class) and (isinstance(self.parent, Class) or isinstance(self.parent, Module))) or \
        (isinstance(self, Module) and isinstance(self.parent, Module))):
            #add to globals
            print("PSTR", pstr)
            if "bge" in pstr:
                return 
            
            ret = opdata.compile(False, pstr)
            if ret == None:
                return
            
            p = pstr
            if isinstance(self.parent, Class):# or self.parent.name == opdata.module.name:
                p = opdata.last(pstr)
            if "." in pstr:
                print("Setting", p, pstr)     
                opdata.globals[p] = ret 
#            #print(opdata.activeScope)
#            #store qualified name !
#        #    self.name = ret.__name__
#        else:
#            print("PSTR", pstr)
#            self.name = pstr 
    
    @staticmethod
    def createDecl(name, typename, opdata):
        
        #oldscope = opdata.activeScope
        #print("1", oldscope, opdata.activeScope)
    #    if "." in name:
    #        name = opdata.parseDotted(name)
            #name = name.split(".")[-1].strip()
        #print("2", oldscope, opdata.activeScope)
        
        #opdata.activeScope = oldscope   
        v = Declaration(name, typename)
        #active module -> open file ? (important later, when treating different modules too)
        print("INDENT", opdata.indent, opdata.activeScope.indent, opdata.isValid(name), opdata.activeScope)
        if opdata.indent >= opdata.activeScope.indent and opdata.isValid(name):
            print("SCOPE", opdata.activeScope)
           # self.activeScope = v #variables build no scope
            opdata.activeScope.declare(v)
            v.indent = opdata.indent
            v.qualify(opdata)
            
            opdata.identifiers[v.name] = v
            print("DECL",name, v.name, v)
            opdata.lhs = ""
            #[print(it[0], ":", it[1]) for it in opdata.identifiers.items()]
        
    
    @staticmethod
    def create(name, typename, opdata):
        
        #exec/compile: necessary to "create" live objects from source ?
        #code = bpy.types.Text.as_string(bpy.context.edit_text)
#        ret = opdata.compile(True, typename)
#        if ret == None:
#            return 
#             
#        typ = type(ret).__name__
#        builtin = dir(builtins)
#        if typ not in builtin:
#            if "(" in typename:
#                typ = typename.split("(")[0]
#            else:
#                typ = typename
        
        typ = typename
        
        if name not in opdata.identifiers and "." in name and \
        "self" not in name and "context" not in name: 
            tempname = name
            if "(" in tempname:
                ind = tempname.rindex(".") # skip the functions, try evalling the classes first
                tempname = tempname[:ind]
            opdata.parseModule(tempname, False)
            opdata.builtins = opdata.module
            opdata.builtinId = opdata.identifiers
            opdata.activeScope = opdata.module
        
        if typename not in opdata.identifiers and "." in typename and \
        not typename.startswith('"') and "self" not in typename and "context" not in typename:
            tempname = typename
            if "(" in tempname:
                ind = tempname.rindex(".") # skip the functions, try evalling the classes first
                tempname = tempname[:ind]
            opdata.parseModule(tempname, False)
            opdata.builtins = opdata.module
            opdata.builtinId = opdata.identifiers
            opdata.activeScope = opdata.module
        
        if "." in name:
            name = opdata.parseDotted(name, "self" in name or "context" in name)
        
        
        if "." in typename or "(" in typename or typename.startswith('"'):
            typ = opdata.parseDotted(typename, True) 
                
        print("NAME/TYPE", name, typ)
        
        if typ == "tuple" and isinstance(name, list):
            for i in range(0, len(name)): #name list can be shorter, might not be interested in all ret vals
                Declaration.createDecl(name[i].strip(), type(ret[i]).__name__, opdata)
        elif isinstance(name, str): 
            Declaration.createDecl(name, typ, opdata)        
        
    def copy(self):
        d = Declaration(self.name, self.type)
        d.indent = self.indent
        d.parent = self.parent
        return d    
  
class Scope(Declaration):

    
    def __init__(self, name, type): #indentation creates new scope too, name can be empty here
        super().__init__(name, type)
        self.local_funcs = {}
        self.local_vars = {}
        self.local_classes = {}
        self.local_unnamed_scopes = []
        
    def declare(self, declaration):
        #add a new declaration
        # if its a variable, add to localvars
        # if its a scope, add to scopes
        
        declaration.parent = self
        name = bpy.context.edit_text.name
        if "." in name:
            name = name.split(".")[0]
        
        #prepend module names
        if name != self.name and (not isinstance(declaration, Module) or not "." in declaration.name):
            declaration.name = self.name + "." + declaration.name
             
        #declaration.indent = self.indent + 4
        #handle pseudo modules from imports somehow...
       # if "Xnor" in self.name or "Xnor" in declaration.name:
    #        print("DECLARE", self, declaration)
        if isinstance(declaration, Module):
            self.local_vars[declaration.name] = declaration
        elif isinstance(declaration, Class):
            self.local_classes[declaration.name] = declaration
        elif isinstance(declaration, Function):
            self.local_funcs[declaration.name] = declaration
        elif isinstance(declaration, Scope):
            self.local_unnamed_scopes.append(declaration)
        elif isinstance(declaration, Declaration):
            self.local_vars[declaration.name] = declaration
    
    def __str__(self):
        f = ""
        v = ""
        c = ""
        
        if len(self.local_funcs) > 0:
            #f = "".join(it[0] + ":" + str(it[1]) for it in self.local_funcs.items())
            f = "F " + str(len(self.local_funcs))
        if len(self.local_vars) > 0:    
            #v = "".join(it[0] + ":" + str(it[1]) for it in self.local_vars.items())
            v = "V " + str(len(self.local_vars))
        if len(self.local_classes) > 0:
            #print("LEN", len(self.local_classes))
            c = "C " + str(len(self.local_classes))    
            #c = "".join(it[0] + ":" + str(it[1]) for it in self.local_classes.items())
        
        return self.type + " " + f + " " + v + " " + c + self.name
    
    
    @staticmethod
    def create(opdata):
        #Case 4: Anonymous scope declaration: after SPACE/ENTER check for :        
        s = Scope("", "scope")
        if opdata.indent >= opdata.activeScope.indent:
            opdata.activeScope.declare(s)
            s.indent = opdata.indent + 4 
            opdata.activeScope = s
            print("scope created") 
    
    def copyContent(self, target):
        for f in self.local_funcs.values():
            target.local_funcs[f.name] = f.copy()
        for v in self.local_vars.values():
            #print("VAR", v.name)
            #if v.name != self.name:
            target.local_vars[v.name] = v.copy()
        for c in self.local_classes.values():
            target.local_classes[c.name] = c.copy()
        for u in self.local_unnamed_scopes:
            target.local_unnamed_scopes.append(u.copy())    
            
        
    
    def copy(self):
        s = Scope(self.name, self.type)
        s.indent = self.indent
        s.parent = self.parent
        self.copyContent(s)
        return s

class Function(Scope):
    
    def __init__(self, name, paramlist):
        super().__init__(name, "function") #must be evaluated to find out return type...
        self.paramlist = paramlist
        
    def declare(self, declaration):
        super().declare(declaration)
    
    def __str__(self):
        return super().__str__()
    
    @staticmethod
    def create(name, params, opdata):
        f = Function(name, params)
        if opdata.indent >= opdata.activeScope.indent and opdata.isValid(name):
            print("SCOPE", opdata.activeScope.name)
            opdata.activeScope.declare(f)
            f.indent = opdata.indent + 4
            f.qualify(opdata)
            opdata.activeScope = f
            opdata.identifiers[f.name] = f
            print(f.name, f)
            
            print("SCOPE1", opdata.activeScope.name)
            for p in params:
                if p == "self":
                    Declaration.create(f.name + ".self", opdata.activeScope.parent.name, opdata)
                    print("SCOPE2", opdata.activeScope.name)
                if p == "context":
                    Declaration.create(f.name + ".context", "bpy.context", opdata)
                    print("SCOPE3", opdata.activeScope.name)
                    
           # [print(it[0], ":", it[1]) for it in opdata.identifiers.items()]
    
    def copy(self):
        f = Function(self.name, self.paramlist)
        f.indent = self.indent
        f.parent = self.parent
        self.copyContent(f)        
        return f
 
class Class(Scope):
        
    def __init__(self, name, to_parse):
        super().__init__(name, "class")
        self.to_parse = to_parse
    
    def declare(self, declaration):
        super().declare(declaration)
    
    def __str__(self):
        return super().__str__()
    
    @staticmethod
    def create(name, to_parse, opdata):
        c = Class(name, to_parse)
        if opdata.indent >= opdata.activeScope.indent and opdata.isValid(name):
            print("SCOPE", opdata.activeScope)
            opdata.activeScope.declare(c)
            c.indent = opdata.indent + 4
            c.qualify(opdata)
            opdata.activeScope = c
            opdata.identifiers[c.name] = c
            print(c.name, c)
            #[print(it[0], ":", it[1]) for it in opdata.identifiers.items()]
    
    def copy(self):
        c =  Class(self.name, self.to_parse)
        c.indent = self.indent
        c.parent = self.parent
        self.copyContent(c)
        return c

#list of that (imported) modules must be generated, and active module (__module__)
class Module(Scope):
    
    def __init__(self, name, submodules):
        super().__init__(name, "module")
        self.indent = 0
        self.submodules = submodules
       
    def declare(self, declaration):
        super().declare(declaration)
    
    def __str__(self):
        return super().__str__()
    
    @staticmethod
    def create(name, submodules, opdata):
        
        m = Module(name, submodules)
        opdata.activeScope.declare(m)
    
        #if isinstance(opdata.activeScope, Module):
        print("SCOPE", opdata.activeScope.name, m.name)
        opdata.activeScope = m
        m.qualify(opdata)
        opdata.identifiers[m.name] = m
        print(m.name, m)
    
    def copy(self):
        m = Module(self.name, self.submodules)
        m.indent = self.indent
        m.parent = self.parent
        self.copyContent(m)
        return m
            
class SubstituteTextOperator(bpy.types.Operator):
    bl_idname = "text.substitute"
    bl_label = "Substitute Text"
    
    choice = bpy.props.StringProperty(name = "choice")
   # type = bpy.props.StringProperty(name = "type")
   # indent = bpy.props.IntProperty(name = "indent")
   
    def index(self, buffer):
        ind1 = -1
        ind2 = -1
        
        if "." in buffer:
            ind1 = buffer.index(".")
        if " " in buffer:
            ind2 = buffer.index(" ")
        
        if ind1 != -1 and ind1 < ind2:
            return ind1
        elif ind2 != -1 and ind2 < ind1:
            return ind2
        else:
            return -1
    
    def rindex(self, buffer):
        
        ind1 = -1
        ind2 = -1
        
        if "." in buffer:
            ind1 = buffer.rindex(".")
        if " " in buffer:
            ind2 = buffer.rindex(" ")
        
        if ind1 != -1 and ind1 > ind2:
            return ind1
        elif ind2 != -1 and ind2 > ind1:
            return ind2
        else:
            return -1
            
        
    def execute(self, context):
        #easy(?) way to delete entered word, but watch this for classes and functions (only select back to period), maybe this is done
        #already...
        
        line = context.edit_text.current_line
        buffer = context.edit_text.buffer
        ind = self.rindex(buffer)
        
        bpy.ops.text.select_line()
        if ind != -1:
            ind += 1
            pre = buffer[:ind]
            lbuf = line.body
            lbuf = lbuf.split(pre)[0]
            pre = lbuf + pre
            post = buffer[ind+1:]
            ind = self.index(post)
            if ind == -1:
                post = ""
            else:
                post = post[ind+1:]
            print("PREPOST", pre, post)
            
            text = pre + self.choice + post
        else:
            text = self.choice
        
        context.edit_text.buffer = text
        bpy.ops.text.insert(text = text)
        
        return {'FINISHED'}    
        
        
#class AutoCompletePopup(bpy.types.Menu):
#    bl_idname = "text.popup"
#    bl_label = ""
#       
#    def draw(self, context):
#        layout = self.layout
#        entries = context.edit_text.suggestions
#        
#        for e in entries:
#            layout.operator("text.substitute", text = e.name).choice = e.name
                                   
class AutoCompleteOperator(bpy.types.Operator):
    bl_idname = "text.autocomplete"
    bl_label = "Autocomplete"
    
    def compile(self, all, expr):
        #code = bpy.context.edit_text.as_string()
        #compile only the code BEFORE the editing location
        try:
             
            code = bpy.context.edit_text.as_string()
            
            code = code.replace("import bge", "")
            
            
            if not all:
                lines = code.splitlines()
                code = ""
                line_index = bpy.context.edit_text.lines.values().index(bpy.context.edit_text.current_line)
                for i in range(0, line_index):
                    code += (lines[i] + "\n")
                
            if not "bge" in code and not "bge" in expr:  #TODO watch other names containing bge....                 
                               
               # print("CODE", code)
                exec(compile(code, '<string>', 'exec'))
                ret = eval(expr)
            else:
               # expr = self.identifiers[expr]
                print("EXPR", expr)
                #if not "bge." in expr:
                #    ret = self.compile(all, expr)
                #else:
                e = self.identifiers[expr]
                if e.type == "module":
                    ret = "#" + e.name
                else:
                   ret = "#" + e.type
                    
                    
            return ret
        except Exception as ex:
            print(ex)
            #raise
        
    def draw_popup_callback_px(self, context):
        
        if self.menu != None:
            self.menu.draw(self.caret_x, self.caret_y)
        
    def cleanup(self):
        self.typedChar = []
        self.module = None
        self.activeScope = None
        self.lhs = ""
        self.identifiers = {}
        self.indent = 0
        self.menu = None
        self.caret_x = 0
        self.caret_y = 0
        self.globals = None
        
        try:
            bpy.context.region.callback_remove(self._handle)
        except Exception:
            pass
    
    def trackScope(self):
        print("TRACKSCOPE", self.indent, self.activeScope.indent)
        while self.indent < self.activeScope.indent:
            if self.activeScope.parent != None:
                self.activeScope = self.activeScope.parent
            else:
                self.activeScope = self.module
                break
    
    def list(self):
        try:
            print("ACTIVESCOPE", self.activeScope.name)
            name = bpy.context.edit_text.name
            if "." in name:
                name = name.split(".")[0]
            if self.activeScope.name != name:
                ret = self.compile(False, self.activeScope.name)
                return dir(ret)
            return dir(builtins)
        except Exception as ex:
            print(ex)
            return dir(builtins)
    
    def recurseTest(self, a, b, r):
        
        if not r:
            return b + "." + a 
            
        ret1 = None
        ret2 = None
        try:
            ret1 = type(self.compile(True, b)).__name__
            
        except Exception as ex:
            print(ex)
        
        if ret1 == None:
            return a
        
        try:
            ret2 = type(self.compile(True, b + "." + a)).__name__
                
        except Exception as ex:
            print(ex)
            
        
        if ret2 == None:
            return a
        
        if ret1 == "type" and ret2 == "type":
            if a == b:
                return a
            return b + "." + a
        
        if ret1 == ret2:
            return a
        
        if "." in b:
            ind = b.rindex(".")
            l = b[ind+1:]
            b = b[:ind]
            return self.recurseTest(l + "." + a, b, r)
        
        return b + "." + a     
    
         
    def parseModule(self, e, recursive):
        
        #ignore indents completely here 
        self.indent = 0
        self.activeScope.indent = 0
      #  self.trackScope(
        
        if e.startswith("bge") and e not in self.identifiers:
            RSTParser.parse(e, self)
        
        if e in self.identifiers:
            return
             
        try:
            ret = self.compile(True, e)
        except NameError as ex:
            print(ex)
            #self.indent = 0
            return
            
        except AttributeError as ex:
            print(ex)
            #self.indent = 0
            return
        
        print(e)
        typ = type(ret).__name__
        print("TYPE", typ)
        
        if typ == "str" and "#" in ret:
            return
            
        
       # if typ != "list":
        names = dir(ret)
        act = self.list()
        #else:
        #    names = []
        #    act = []
        #    for r in ret:
        #        names.append(self.last(r))
        #        act.append(self.last(r))
       # print("ACT", act, self.last(e))
        
        if act == None:
            return
        
#        print("MODL", e)
#        if hasattr(ret, "__module__"):
#            print("MODL2", ret.__module__)    
#            if ret.__module__ == "auto_complete":
#                return
               
        #filter = []
         
        if ("function" in typ or "method" in typ and "descriptor" not in typ):
            
            #filter = [self.recurseTest(n,e, recursive) for n in names if not n.startswith("_")]
            
            print("FUNCTION", e)
            if self.last(e) in act:
                Function.create(self.last(e), [], self) #get paramlist length and elems/types ?
            else:
                while (True):     
                    act = self.list()
                   # print("ACT(F)", act, self.activeScope.name, e)
                    if (self.last(e) in act):
                        Function.create(self.last(e), [], self)
                        break 
                    
                    self.activeScope = self.activeScope.parent
                    if self.activeScope == None:
                        self.activeScope = self.module
                        Function.create(e , [], self)
                        break
                 
            filter = []
            #filter = [self.recurseTest(n,e, recursive) for n in names if not n.startswith("_")]
           
            self.activeScope = self.activeScope.parent
            if self.activeScope == None:
                self.activeScope = self.module
                     
        elif "type" == typ and not "bpy" in e:
            
            filter = [self.recurseTest(n,e, recursive) for n in names if not n.startswith("_")]
            
            if self.last(e) in act:
                print("CLASS", e)
                Class.create(e, filter, self) #get superclasses somehow ?  
            else:
                print("CLASS2", e)
                #self.activeScope = self.module
                
                while (True):
                         
                    act = self.list()
                    #print("ACT(C)", act, self.activeScope.name, e)
                    if (self.last(e) in act):
                        Class.create(e, filter, self)
                        break 
                    
                    self.activeScope = self.activeScope.parent
                    if self.activeScope == None:
                        self.activeScope = self.module
                        Class.create(e, filter, self)
                        break
            
            #recursive = True    
            #filter = [self.recurseTest(n,e, recursive) for n in names if not n.startswith("_")]
            
        elif (str(self.activeScope.name + "." + typ) in self.identifiers and "RNA" not in typ and \
        "bpy" not in str(ret) and "bpy" not in typ):#  or "descriptor" in typ:     
            #known types  
            
            if self.last(e) in act:
                print("DECL", e)
                Declaration.create(self.last(e), typ, self) 
            else:
                print("DECL2", e)
                self.activeScope = self.module
                act = self.list()
                if (self.last(e) in act):
                    Declaration.create(self.last(e), [], self) 
                
            filter = []
            
           # self.activeScope = self.activeScope.parent
        #    if self.activeScope == None:
         #       self.activeScope = self.module
            
        else:
            
            #modules and module like classes and all the rest (yuck...)       
            print("MODULE", e,)
            if e != "builtins":
                #if not isinstance(self.activeScope, Module):
                #    filter = []
                #else:
                filter = [self.recurseTest(n, e, recursive) for n in names if not n.startswith("_")]  
            else:  
                filter = [n for n in names if not n.startswith("_")]
            
            if e != "builtins":
                if (self.last(e) in act):
                    print("MODULE", e)
                    Module.create(e, filter, self)
                       
                else:
                    
                    while (True):
                        
                        act = self.list()
                        if (self.last(e) in act):
                            Module.create(e, filter, self)
                            break
                        
                        self.activeScope = self.activeScope.parent
                        if self.activeScope == None:
                            self.activeScope = self.module
                            Module.create(e, filter, self)
                            break
            #else:
            #    for f in filter:
            #        self.parseModule(f, False)
                            
        if recursive:
            for f in filter:
                self.parseModule(f, recursive)  
            
    def parseCode(self, codetxt):
        
        try:
            
            self.identifiers = dict(self.builtinId)
            self.activeScope = self.module
            self.module = self.builtins.copy() 
                            
            for l in codetxt.lines:
                self.parseLine(l.body)
                
            return {'RUNNING_MODAL'}
        except Exception as e:
            print("Exception:", e)
           # self.cleanup() # maybe to finally ?
            #self.report({'ERROR'}, "Autocompleter stopped because of exception: " + str(e))
            #print("... autocompleter stopped")
            #return {'CANCELLED'}
            return {'RUNNING_MODAL'}
            #raise
            
    def parseClass(self, line):
        beforeColon = line.split(":")
        name = beforeColon[0].split(' ')[1]
        return name
    
    def parseFunction(self, line):
        params = []
        openbr = line.split('(')
        name = openbr[0].split(' ')[1]
                
        closedbr = openbr[1].split(')')[0]
        psplit = closedbr.split(',')
        for p in psplit:
            #strip whitespace
            params.append(p.strip())
        
        return name, params
    
    def parseDeclaration(self, line):
           
        index = line.index("=")
        lhs = line[:index-1].strip()
        if "," in lhs:
            lhs = line.split(",")
        
        rhs = line[index+1:].strip()
        return lhs, rhs
     
    def parseLine(self, line):
        # ignore comments, do that at typing too!!
        self.indent = 0 
        
        if len(line) == 0:
            return
        
        l1 = len(line)
        line = line.lstrip()
        l2 = len(line)
        spaces = l1-l2
        self.indent = spaces
        self.trackScope()
        
        if "#" in line:
            line = line.split("#")[0]
        
        if '"""' in line:
            line = line.split('"""')[0]
        
       # print(line, self.activeScope, self.indent, self.activeScope.indent)
          
        if "=" in line:
            found = False
            for k in keyword.kwlist:
                if line.startswith(k):
                    found = True
            #if not found:
                # dont support local vars ??, way too slow when reading code files...
            lhs, rhs = self.parseDeclaration(line)
            Declaration.create(lhs, rhs, self)
        elif line.startswith("def"):
            name, params = self.parseFunction(line)
            Function.create(name, params, self)
        elif line.startswith("class"):
            if "(" not in line:
                name = self.parseClass(line)
                params = []
            else:
                name, params = self.parseFunction(line)
            
            Class.create(name, params, self)
        
        elif line.startswith("import"):# or line.startswith("from"): for alias only, declaring a module variable
            
            #exec(line)
            modname = line.split("import")[1].strip()
            print("MODNAME", modname)
            
            if modname == "bge" and "bge" not in self.identifiers:
                Module.create("bge", ["bge.types", "bge.logic", 
                              "bge.render", "bge.texture", "bge.events", "bge.constraints"], self)
            
            if modname not in self.identifiers:
                self.parseModule(modname, False)
            #print(self.identifiers)    
            self.builtinId = self.identifiers
            self.builtins = self.module
            self.activeScope = self.module
                
        elif line.endswith(":"):
            Scope.create(self)
            
    
    def parseDotted(self, buffer, isRhs = False):
        
        op = buffer.count("(")
        cl = buffer.count(")")
        parenthesis = op > 0 and op == cl
        if parenthesis:
            ri = buffer.rindex("(")
            #dotted = buffer[:ri]
            ind = buffer.rindex(")")
            print("IND )", ind, len(buffer))
            #if ind < len(buffer)-1:
            #    dotted = buffer[:ri]
            #else:
            dotted = buffer[:ind+1]
            post = buffer[ind+2:]
                  
        elif "." in buffer and not buffer.startswith('"'):    
            ri = buffer.rindex(".")
            dotted = buffer[:ri]
            post = buffer[ri+1:]
        else:
            ri = -1
            dotted = buffer
            post = ""
        
        isSelf = False    
        if "self" in dotted and not ".self" in dotted:
            if self.activeScope.type == "function":
                self.activeScope = self.activeScope.parent
            typ = self.identifiers[self.activeScope.name].name
            dotted = dotted.replace("self", typ)
            isSelf = True
            
        #a bpy specific assumption:
        isContext = False
        if "context" in dotted and not ".context" in dotted:
            if self.activeScope.type == "function":
                self.activeScope = self.activeScope.parent
            typ = "bpy.context" # the function name
            dotted = dotted.replace("context", typ)
            isContext = True
        
        #otherwise replace param by its type, if specified by user
        #like .. args :: argname
        #     .. type :: typename, TODO
        
      
        dotted = dotted.strip()        
        print("TOEVAL", dotted)
        ret = self.compile(False, dotted)
        
        if ret == None:
            return buffer 
         
            #print("LOCALS", locals()) 
            #print("GLOBALS", globals())
      
        typename = type(ret).__name__
        
        isStatic = False
        # '#' marks static evaluation result
        if typename == "str" and "#" in ret:
            typename = ret.split("#")[1]
            isStatic = True
        
        if "(" in typename:
            typename = typename.split("(")[0]
            
        print("TYPENAME", typename)
        if not parenthesis and not isSelf and not isContext:
            if ri != -1:
                buffer = buffer[ri+1:]
            else:
                buffer = post
        elif parenthesis or isSelf or isContext:
            if "." in post:
                sp = post.split(".")
                if len(sp) > 1:
                    post = sp[1]
            buffer = post
                     
        if typename in self.identifiers and typename != "type" and \
        typename != "module" and typename != "function" and \
        "bpy" not in str(ret) and "RNA" not in typename:    
            buffer = typename + "." + buffer
            check = typename
        elif typename != "type" and typename != "module" and typename != "function":
            #typename = ret.__name__
            found = False
            for k in self.identifiers:
                if k.endswith(typename):
                    check = k
                    buffer = k + "." + buffer
                    found = True
                    print(found)
                    break
                
            if not found and not parenthesis:
                buffer = dotted + "." + buffer
                check = dotted
            elif not found:
                check = dotted
                
        else:
            #if not parenthesis:
            buffer = dotted + "." + buffer
            #else:
            #    buffer = buffer[:ri]
            check = dotted
            
        print("BUF", buffer)
        
        if isRhs:
            scope = self.activeScope.copy()
        
        equal = False
        for val in self.identifiers.values():
            if isinstance(val, Module) and val.name == check:
                self.activeScope = val
                break
            elif isinstance(val, Scope) and val.name == check:
                print("SKOPE", self.activeScope.name, val.name)
                if self.activeScope.name == val.name:
                    print("Equal.")
                    equal = True   
                self.activeScope = val
                break
            elif isinstance(val, Declaration) and val.name == check:
                #print("BUHF", buffer, self.activeScope.name)
                #if buffer.endswith("self") or buffer.endswith("context"):
                #    self.activeScope = val
                #else:
                self.activeScope = val.parent
                break
            
        if isRhs:
            if not equal:
                if not buffer.startswith(self.activeScope.name): # somehow separate simple from complex assignments
                    buffer = dotted
                else:
                    buffer = self.activeScope.name
                    self.activeScope = scope
            else:
                if buffer.count(".") > 0 and not isStatic:
                    ind = buffer.index(".")
                    buffer = buffer[ind+1:] # cut first name off otherwise its class.class.var instead class.var
                   
            print("RHS", buffer, self.activeScope)
        
        if equal and not isRhs and not isStatic:
            if buffer.count(".") > 1:
                ind = buffer.index(".")
                buffer = buffer[ind+1:] # cut first name off otherwise its class.class.var instead class.var
            
        print("DOTTED", dotted, self.activeScope.name, buffer)
        return buffer.strip()
            
    def handleImport(self):
        #add all types of import to identifiers...
        #print out current module, after declaration change scope.... must parse the currently used code
        pass
    
    def isValid(self, identifier):
        return not identifier in self.identifiers or self.identifiers[identifier] != "keyword" 
    
    def parseIdentifier(self):
        
        self.lhs = ""
        
        #first check if we have a new identifier which mustnt be a keyword...
        bpy.context.edit_text.buffer = bpy.context.edit_text.current_line.body
        print("BUFFER", bpy.context.edit_text.buffer)
        
        #go to parent scope if new indent is smaller, "unindent"
        #indent = bpy.context.edit_text.current_character
        self.parseCode(bpy.context.edit_text) # make sure removed variables are gone, but not very performant
        self.parseLine(bpy.context.edit_text.buffer)
        
        bpy.context.edit_text.buffer = ""
    
    def testScope(self, declaration):
       # print("TESTSCOPE", self.activeScope.name, declaration.name)
        
        if self.activeScope != None:
            if self.indent > self.activeScope.indent:
                return True
            
            elif isinstance(self.activeScope, Module) and self.activeScope.name != self.module.name:
                #print("MKEYS", self.activeScope.submodules)
                name = declaration.name
                return name in self.activeScope.local_funcs or \
                       name in self.activeScope.local_vars or \
                       name in self.activeScope.local_classes or \
                       name in self.activeScope.submodules
            
            elif isinstance(self.activeScope, Class):
                name = declaration.name
                return name in self.activeScope.local_funcs or \
                       name in self.activeScope.local_vars or \
                       name in self.activeScope.local_classes or \
                       name in self.activeScope.to_parse
                                  
            elif isinstance(self.activeScope, Function):
                #print("KEYS", self.activeScope.local_vars.keys(), declaration.name)
                #print(self.module.name)
                name = self.last(declaration.name)
                #name = declaration.name
                return name in self.activeScope.parent.local_funcs or \
                       name in self.activeScope.parent.local_vars or \
                       name in self.activeScope.parent.local_classes
            else:
                #print(self.module.name)
                return True
        else:
            return False    
    
    def testIndent(self, declaration):
  
        if isinstance(declaration, Function) or isinstance(declaration, Class) or \
        isinstance(declaration, Scope):
            print("TESTINDENT", self.indent, declaration.indent)
            t = self.testScope(declaration)
            print(t, declaration.name)
            return self.indent >= (declaration.indent - 4) and t # the "outer" indent
        elif isinstance(declaration, Declaration): 
            print("TESTINDENT", self.indent, declaration.indent)
            t = self.testScope(declaration)
            print(t, declaration.name)   
            return self.indent >= declaration.indent and t
        else:
            return False
        
#    def testModule(self, buffer, item):
#        if isinstance(item, Scope) and self.module.name != item.name:
#            print("SC", item.name, buffer)
#            return item.name in buffer
#        #return item.name.startswith(buffer)
#        return True
                    
    def lookupIdentifier(self, lastWords = None):
        
        #self.lhs = ""
           
        if len(self.typedChar) > 0:
            char = self.typedChar[0]
        else:
            char = ""
        
        bpy.context.edit_text.buffer = bpy.context.edit_text.current_line.body
        if self.lhs == "":# and "." not in bpy.context.edit_text.buffer and "." != char:    
            bpy.context.edit_text.buffer = bpy.context.edit_text.current_line.body
            l1 = len(bpy.context.edit_text.buffer)
            bpy.context.edit_text.buffer = bpy.context.edit_text.buffer.lstrip()
            l2 = len(bpy.context.edit_text.buffer)
            self.indent = l1-l2
            print("INDENT SET", self.indent, self.activeScope.indent, self.activeScope.name, self.lhs, bpy.context.edit_text.buffer)
            self.trackScope()
            print("ACTIVE SCOPE", self.activeScope.name)
            
        #add char later...
        #if char != ".":
        bpy.context.edit_text.buffer += char
        
        if bpy.context.edit_text.buffer == "" and lastWords == None:
            return
        
        #if period/members: first show all members, then limit selection to members and so on
        #must pass/store lastWords selection, together with lastBuffer ?
        
        #dynamically get the last of . and , lists on lhs of =
        buffer = bpy.context.edit_text.buffer
        buffer = buffer.lstrip()
        print("lookupbuf", buffer)
        
        if char == " ":
            return
        
     #   l1 = len(bpy.context.edit_text.buffer)
    #    l2 = len(buffer)
    
        words = []
        if lastWords == None or lastWords == []:
        
            if "," in buffer and self.lhs == "":
                sp = buffer.split(",")
                buffer = sp[-1]
            
            if "=" in buffer:
                i = buffer.index("=")
                buffer = buffer[i+1:].strip()
            
            op = buffer.count("(")
            cl = buffer.count(")") 
            
            if op == cl and op > 0:
                do_parse = op == cl and op > 0 and ( "." == char and buffer.rindex(")") == len(buffer)-2) or char != "."
            else:
                do_parse = True
                   
            if "." in buffer and do_parse:#and self.lhs == "":
                buffer = self.parseDotted(buffer)
                print("BUFR", buffer)     
                #if char == ".":
                #    bpy.context.edit_text.buffer += char
                    #buffer += char
            
        #only the NEW string compared to the last buffer is relevant
        #to look it up inside a subset/subdict of items
        #words = []
        #if lastWords == None or lastWords == []:
            #if self.oldbuffer in self.lastLookups:
            #    lastWords = self.lastLookups[self.oldbuffer] #its a list only
            #    words = [it for it in lastWords if it.startswith(bpy.context.edit_text.buffer)]
            #else:
            lastWords = self.identifiers
            
            found1 = False
            for k in self.identifiers.keys():
                if k.startswith(buffer):
                    found1 = True
                    break 
                
            found2 = False
            for k in self.builtinId.keys():
                if k.startswith(buffer):
                    found2 = True
                    break     
                   
            print("LOOKUP", found1, found2)
            words = [self.last(it[0], buffer) for it in lastWords.items() if it[0].startswith(buffer) and \
                    (it[1] == 'keyword' or self.testIndent(it[1])) and it[0] != buffer and self.last(it[0], buffer) != None]
        else:
            #print("OKKK")
            #words = [it for it in lastWords if it.startswith(bpy.context.edit_text.buffer)]
            words = lastWords
            
        print("WORDS", words)
        
        #display all looked up words
        self.displayPopup(words) # close after some time or selection/keypress
#        self.lastLookups[bpy.context.edit_text.buffer] = words #make copy of string for key ?
#        self.oldbuffer = str(bpy.context.edit_text.buffer)
#        self.activeScope = self.module
#        self.indent = l1-l2
#        self.trackScope()
        lastWords = None
    #    self.activeScope = self.module
    
    def last(self, item, buffer = None): 
        if "." in item:
            index = item.rindex(".")
            item = item[index+1:]
            if buffer != None:
                if buffer.startswith(self.activeScope.name):
                    return item #invalid choice e.g. b -> bpy.app.background instead of bpy only
                return None
        return item
        
    def lookupMembers(self):
        words = []
       # self.tempBuffer = "".join(str(i) for i in self.buflist).lstrip()
        #print("TEMP", self.tempBuffer)
        
        buffer = bpy.context.edit_text.buffer
        
        if "=" in buffer:
            i = buffer.index("=")
            buffer = buffer[i+1:].strip()
        
        if "." in buffer or "self" in buffer or "context" in buffer:
            buffer = self.parseDotted(buffer)
            if buffer.endswith("."):
                ind = buffer.rindex(".")
                buffer = buffer[:ind]
            print("BUFR2", buffer)
        
#        if self.activeScope.name not in self.identifiers and self.activeScope != self.module:
#            self.parseModule(self.activeScope.name, False)
        
        scope = self.activeScope.copy()
        print("BUFFR2", buffer)
        if buffer in self.identifiers:  
            cl = self.identifiers[buffer]
            if isinstance(cl, Module):
                [words.append(self.last(v)) for v in cl.submodules if self.last(v) != None and not v in cl.local_vars and \
                not v in cl.local_funcs and not v in cl.local_classes] 
                
                #parse on demand, recursive is too long
                [self.parseModule(v, False) for v in cl.submodules if not v in self.identifiers]
                self.builtins = self.module
                self.builtinId = self.identifiers
                self.activeScope = scope
                
                [words.append(self.last(v)) for v in cl.local_vars if self.last(v) != None]
                [words.append(self.last(v)) for v in cl.local_funcs if self.last(v) != None]
                [words.append(self.last(v)) for v in cl.local_classes if self.last(v) != None]
            elif isinstance(cl, Class):
                #print("TO_PARSE", cl.name, cl.to_parse)
               # [words.append(self.last(v)) for v in cl.to_parse if self.last(v) != None and not v in cl.local_vars and \
                #not v in cl.local_funcs and not v in cl.local_classes]
                
                [self.parseModule(v, False) for v in cl.to_parse if not v in self.identifiers]
                self.builtins = self.module
                self.builtinId = self.identifiers
                self.activeScope = scope
                
                [words.append(self.last(v)) for v in cl.local_vars if self.last(v) != None]
                [words.append(self.last(v)) for v in cl.local_funcs if self.last(v) != None]
                [words.append(self.last(v)) for v in cl.local_classes if self.last(v) != None]
                
            elif isinstance(cl, Declaration):
                typ = cl.type
                if typ not in self.identifiers:
                    self.parseModule(typ, False)
                    self.builtins = self.module
                    self.builtinId = self.identifiers
                    self.activeScope = scope
                    
                cl = self.identifiers[typ]
                [words.append(self.last(v)) for v in cl.local_vars if self.last(v) != None] #pseudo modules appear here
                [words.append(self.last(v)) for v in cl.local_funcs if self.last(v) != None]
                [words.append(self.last(v)) for v in cl.local_classes if self.last(v) != None]
                
                if isinstance(cl, Class):
                    [words.append(self.last(v)) for v in cl.to_parse if self.last(v) != None and not v in cl.local_vars and
                    not v in cl.local_funcs and not v in cl.local_classes] 
            
          
        print("MEMBERZ", words)           
        return words   
                    
    def displayPopup(self, words):
        #sort it by category (class, function, var, constant, keyword....) first, then alpabetically
        #s = sorted(words, key=itemgetter(1))     # sort on value first
        #disp = sorted(s, key=itemgetter(0))      # now sort that on key
        if len(words) > 0:
            self.menu = Menu(sorted(words))
            #toPopup(disp)
            print("POPUP", self.menu.items)
            
            
            
            #items = []
            #bpy.context.edit_text.suggestions.clear()
            #for d in disp:
            #    prop = bpy.context.edit_text.suggestions.add()
            #    prop.name = d
                
           # bpy.ops.wm.call_menu(name = "text.popup")
    
    def caretPosition(self, event):
        area = None
        for a in bpy.context.screen.areas:
            if a.type == 'TEXT_EDITOR':
                area = a
                
#                region = None
#                for r in area.regions:
#                    if r.type == 'WINDOW':
#                        region = r
                
                try:
                    #raise Exception
                    space = None
                    for s in area.spaces:
                        if s.type == 'TEXT_EDITOR':
                            space = s
                            loc = space.cursor_location
                            x = int(loc[0] + 20)
                            y = int(loc[1] - 40)
                            # print("XY", x, y)
                            return x, y
                except Exception:
                    return event.mouse_region_x, event.mouse_region_y
            
    def cancel(self, context):
        self.cleanup()
        print("... autocompleter cancelled")
        return {'CANCELLED'}
                 
    def modal(self, context, event):
        
        try:
            
           
            if not context.edit_text:
                self.cleanup()
                print("... autocompleter stopped")
                return {'CANCELLED'}
            
            global running
            if not running:
                self.cleanup()
                context.edit_text.buffer = ""
                print("... autocompleter stopped(modal)")
                return {'CANCELLED'}
                
            context.area.tag_redraw()
            
            #works with caretxy.patch applied ONLY.
            self.caret_x, self.caret_y = self.caretPosition(event)
            
            mouse_x = event.mouse_region_x
            mouse_y = event.mouse_region_y
               
            if event.type == 'MOUSEMOVE':
                if self.menu != None:
                    self.menu.highlightItem(mouse_x, mouse_y)
            
            if (event.type == 'RIGHTMOUSE' or event.type =='ESC') and event.value == 'PRESS':
                self.menu = None
                return {'RUNNING_MODAL'}
                
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                if self.menu != None:
                    self.menu.pickItem()
                    self.menu = None
                    return {'RUNNING_MODAL'} #do not pass the event ?
            
            if event.type == 'DOWN_ARROW' and event.value == 'PRESS':
                if self.menu != None:
                    self.menu.nextItem()
                    return {'RUNNING_MODAL'}
                    
            
            if event.type == 'UP_ARROW' and event.value == 'PRESS':
                if self.menu != None:
                    self.menu.previousItem()
                    return {'RUNNING_MODAL'}   
                
            if event.type == 'RIGHT_ARROW' and event.value == 'PRESS':
                if self.menu != None:
                    self.menu.nextWrap()
                    return {'RUNNING_MODAL'}
                    
            
            if event.type == 'LEFT_ARROW' and event.value == 'PRESS':
                if self.menu != None:
                    self.menu.previousWrap()
                    return {'RUNNING_MODAL'}       
                
            #add new entry to identifier list
            if 'MOUSE' not in event.type and event.value == 'PRESS':
                print(event.type, event.value)
            
           
            if event.shift:
                print("SHIFT")
            
            #hack, trigger parse manually, must be done with bpy.app. handler somehow (on change of text block)
            #if event.shift and event.ctrl:
                #parse existing code to buildup data structure, what to do when code has syntax errors (it is execed to get types)
                #maybe avoid unnecessary compile steps
            #    print("Reading file...")
            #    self.parseCode(context.edit_text)
            #    print("... file read")
            
            if event.type == 'RET' and event.value == 'PRESS':
                if self.menu != None:
                    self.menu.pickItem()
                    self.menu = None
                    return {'RUNNING_MODAL'}
                
                self.parseIdentifier()
                self.indent = 0
                self.lhs = ""     
            
            elif event.unicode == "=" and self.lhs == "" and event.value == 'PRESS':
                
                print("ASSIGN")
                context.edit_text.buffer += event.unicode 
                self.lookupIdentifier(self.lookupMembers())
                lhs, rhs = self.parseDeclaration(context.edit_text.buffer)
                self.lhs = lhs
               # context.edit_text.buffer = ""
                    
            #do lookups here
            elif event.type == 'PERIOD' and event.value == 'PRESS' and not event.shift:
                #look up all members of class/module of variable, depending on chars
                self.typedChar.append(event.unicode) # . is part of name
                context.edit_text.buffer = context.edit_text.current_line.body
                if event.unicode == ".":
                    self.indent += 4
                
                #eval the line
                #self.compile(True, context.edit_text.buffer)
                    
                self.lookupIdentifier(self.lookupMembers())
                
                if len(self.typedChar) > 0:
                    self.typedChar.pop()
    #            
            #elif event.type == '(':
                #look up parameters of function
                #self.lookupParameters()
             #   pass
    #        
    #        elif event.type == '[':
    #            #look up keys in dictionary /indexable class ???            
    #            #self.lookupDictKeys()
    #            pass
    #        
            elif event.type in ('BACK_SPACE', 'LEFT_ARROW', 'RIGHT_ARROW', 'UP_ARROW', 'DOWN_ARROW') and event.value == 'PRESS':
                #delete last lookup structure (sample, ...)
                #remove last char from buffer, do lookup again
                if len(self.typedChar) > 0:
                    self.typedChar.pop()
                    
                #self.lookupIdentifier()
                #if event.type in ('BACK_SPACE', 'LEFT_ARROW', 'RIGHT_ARROW'): 
                self.indent = 0
                self.menu = None
                
                #refill the buffer, IF ARROW UP take prev line, ARROW DOWN next (because this event is caught before)
                context.edit_text.buffer = context.edit_text.current_line.body
                       
            elif (((event.type in ('A', 'B', 'C', 'D', 'E',
                                'F', 'G', 'H', 'I', 'J',
                                'K', 'L', 'M', 'N', 'O',
                                'P', 'Q', 'R', 'S', 'T',
                                'U', 'V', 'W', 'X', 'Y',
                                'Z', 'ZERO','ONE', 'TWO',
                                'THREE', 'FOUR', 'FIVE',
                                'SIX', 'SEVEN','EIGHT', 
                                'NINE', 'MINUS', 'PLUS',
                                'SPACE', 'COMMA')) or \
                                (event.type == 'PERIOD' and \
                                 event.shift)) or (event.unicode in ["'", "#", "?", "+" ,"*"])) and event.value == 'PRESS': 
                #catch all KEYBOARD events here...
                #maybe check whether we are run inside text editor
                
                #obviously this is called BEFORE the text editor receives the event. so we need to store the typed char too.
                #self.indent = 0
                self.menu = None
                print(event.unicode)
                self.typedChar.append(event.unicode)
            
                #watch copy and paste ! must add all pasted chars to buffer and separate by space TODO
                #via MOUSE events and is_dirty/is_modified
                
             #   if context.edit_text.bufferReset:
                    #self.typedChar.pop()
              #      self.tempBuffer += context.edit_text.buffer
               #     context.edit_text.bufferReset = False
                #self.buflist.append(char)
                
                #also do word lookup, maybe triggered by a special key for now... 
                #start a timer, re-init it always, and accumulate a buffer
                #if timer expires, pass oldbuffer and buffer to lookup function, oldbuffer = buffer
                
                self.lookupIdentifier()
                
                if len(self.typedChar) > 0:
                    self.typedChar.pop()
                
                #how to end the op ?
            return {'PASS_THROUGH'}
        
        except Exception as e:
            # clean up after error
            print("Exception:", e)
            #self.cleanup() # maybe to finally ?
            #self.report({'ERROR'}, "Autocompleter stopped because of exception: " + str(e))
            #print("... autocompleter stopped")
            #return {'CANCELLED'}
            #raise
            return {'PASS_THROUGH'}
            
    
    def invoke(self, context, event):
        
        global running
        if running:
           running = False
          #    self.cleanup()
           print("Requesting Autocompleter stop....")
           return {'RUNNING_MODAL'}
        
        try:
            text = context.edit_text
        except Exception:
            return {'CANCELLED'}
        
        if not text:
            return {'CANCELLED'}
        
        self.module = Module(text.name.split(".")[0], []) #better: filepath, if external
        print(self.module.name, self.module.indent)
        self.activeScope = self.module
        self.globals = globals()
         
        self.typedChar = []
        
        self.lhs = ""   
        self.tempBuffer = ""
        self.indent = 0
        self.menu = None
        self.caret_x = 0
        self.caret_y = 0
        
        self.identifiers = {}
        
        for k in keyword.kwlist:
            self.identifiers[k] = 'keyword'
                             
        
        try:
            self.parseModule("builtins", True)
            self.builtins = self.module
            self.builtinId = self.identifiers
           
        except Exception as e:
            print("Exception(parseModule)", e)
            #raise
            
        #do not automatically parse own code (throws registration errors)
        print("autocompleter started...")
             
        context.window_manager.modal_handler_add(self)
        self._handle = context.region.callback_add(self.draw_popup_callback_px, (context,), 'POST_PIXEL')
   
        running = True
        if text.name != "auto_complete.py": 
            return self.parseCode(text) 
        return {'RUNNING_MODAL'}

class AutoCompletePanel(bpy.types.Panel):
    bl_idname = 'auto_complete'
    bl_label = 'Autocomplete'
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    
    def register():
        bpy.types.Text.buffer = bpy.props.StringProperty(name = "buffer")
    
    def unregister():
        del bpy.types.Text.buffer
        
    def draw(self, context):
        layout = self.layout
       # layout.prop(context.edit_text, "autocomplete_enabled", text = "Enabled",  event = True)
        text = "Enable"
        label = "Autocompleter stopped"
        
        global running
        if context.edit_text and running:
            text = "Disable"
            label = "Autocompleter running"
        layout.operator("text.autocomplete", text = text)
        layout.label(label)
        #layout.label("disable with ESC")
