"use strict";

import * as util from 'util';
import * as math from 'math';

import {
  Vector2, Vector3, Vector4,
  Matrix4, Quat
} from 'vectormath';

import {set, hashtable} from 'util';

var sin=Math.sin, cos=Math.cos, abs=Math.abs, log=Math.log,
asin=Math.asin, exp=Math.exp, acos=Math.acos, fract=Math.fract,
sign=Math.sign, tent=Math.tent, atan2=Math.atan2, atan=Math.atan,
pow=Math.pow, sqrt=Math.sqrt, floor=Math.floor, ceil=Math.ceil,
min=Math.min, max=Math.max, PI=Math.PI, E=2.718281828459045;

var set = util.set, hashtable = util.hashtable;


var toHash2_stack = new Array(4096);
var toHash2_stack_2 = new Float64Array(4096);
var toHash2_stack_3 = new Float64Array(4096);

var _str_prejit = new Array(4096);
var strpre = 8;

var RNDLEN = 1024;
var rndtab = new Float64Array(RNDLEN);

for (var i=0; i<rndtab.length; i++) {
  rndtab[i] = Math.random()*0.99999999;
}

function precheck(key) {
  var s1 = "";
  var seed = key.length % RNDLEN;
  seed = floor(rndtab[seed]*RNDLEN);
  
  var klen = key.length;
  
  for (var i=0; i<strpre; i++) {
      s1 += key[floor(rndtab[seed]*klen)];
      seed = (seed+1) % RNDLEN;
  }
  
  return s1;
}

var _vbuf = new Uint8Array(8);
var _view = new DataView(_vbuf.buffer);
var _fview = new Float32Array(_vbuf.buffer);
var _iview = new Int32Array(_vbuf.buffer);
var _sview = new Int16Array(_vbuf.buffer);

function pack_float(f) {
  var s = "";
  //_view.setFloat32(0, f);
  _fview[0] = f;
  
  for (var i=0; i<4; i++) {
      s += String.fromCharCode(_vbuf[i]);
  }
  
  return s;
}
function pack_int(f) {
  var s = "";
  //_view.setFloat32(0, f);
  _iview[0] = f;
  
  for (var i=0; i<4; i++) {
      s += String.fromCharCode(_vbuf[i]);
  }
  
  return s;
}
function pack_short(f) {
  var s = "";
  //_view.setFloat32(0, f);
  _sview[0] = f;
  
  for (var i=0; i<2; i++) {
      s += String.fromCharCode(_vbuf[i]);
  }
  
  return s;
}
function pack_byte(f) {
  return String.fromCharCode(f);
}

var tiny_strpool = {};
var tiny_strpool_idgen = 1;

function pack_str(f) {
  var ret = "";
  
  if (!(f in tiny_strpool)) {
      tiny_strpool[f] = tiny_strpool_idgen++;
  }
  
  return pack_short(tiny_strpool[f]);
}

var tiny_strpool2 = {};
var tiny_strpool_idgen2 = 1;

function pack_op(f) {
  var ret = "";
  
  if (!(f in tiny_strpool2)) {
      tiny_strpool2[f] = tiny_strpool_idgen2++;
  }
  
  return pack_byte(tiny_strpool2[f]);
}

window.pack_float = pack_float;

window.precheck = precheck;

var _str_prehash = {}
var _str_idhash = window._str_idhash = {};
var _str_idhash_rev = window._str_idhash_rev = {};
var _str_idgen = 0;
function spool(hash) {
  if (hash in _str_idhash) {
      return _str_idhash[hash];
  } else {
      var ret = _str_idgen++;
      
      _str_idhash[hash] = ret;
      _str_idhash_rev[ret] = hash;
      
      return ret;
  }
}

function spool_len(id) {
  return _str_idhash_rev[id].length;
}

window.tot_symcls = 0.0;

var KILL_ZEROS = true;

export class symcls {
  constructor(name_or_value, op) {
    this._id = tot_symcls++;
    
    this._last_h = undefined;
    this.value = undefined;
    this.name = ""; //"(error)";
    this.a = this.b = undefined;
    this.use_parens = false;
    this.op = undefined;
    this.parent = undefined;
    this._toString = undefined;
    this.is_func = false;
    
    this._hash = this._toString = undefined;
    
    this.key = this.tag = undefined;
    this._done = this._visit = false;
    this.id = undefined;
    this.ins = this.ins_ids = undefined;
    this.is_tag = this.is_root = undefined;
    
    /*Object.defineProperty(this, "hash", {
        get : function() {
            if (this._hash == undefined) {
                this._hash = spool(""+this);
            }
            return this._hash;
        }   
    });*/
    
    if (typeof name_or_value == "number" || typeof name_or_value == "boolean") {
        this.value = name_or_value;
    } else if (typeof name_or_value == "string" || name_or_value instanceof String) {
        this.name = name_or_value;
    }
  }

  unop(op) {
    return this.func(op);
  }
  
  binop(b, op) {
      if (typeof b == "string" || typeof b == "number" || typeof b == "boolean") {
          b = new symcls(b);
      }
          
      var ret = new symcls();
      var a = this;
      
      if (a.value != undefined && b.value != undefined && a.a == undefined && b.a == undefined) {
          ret.value = eval(a.value + " " + op + " " + b.value);
          return ret;
      }
      
      ret.use_parens = true;
      ret.op = op;
      
      if (KILL_ZEROS && a.value != undefined && a.value == 0.0 && (op == "*" || op == "/")) {
          return sym(0);
      } else if (KILL_ZEROS && b.value != undefined && b.value == 0.0 && (op == "*")) {
          return sym(0);
      } else if (KILL_ZEROS && this.a == undefined && this.value == 0.0 && op == "+") {
          return b.copy();
      } else if (KILL_ZEROS && b.a == undefined && b.value == 0.0 && (op == "+" || op == "-")) {
          return this.copy();
      } else if (this.value == 1.0 && op == "*" && this.a == undefined) {
          return b.copy();
      } else if (b.value == 1.0 && (op == "*" || op == "/") && b.a == undefined) {
          return this.copy();
      }
      
      if (this.b != undefined && this.b.value != undefined && 
          b.value != undefined && op == "+") {
          
          ret = this.copy();
          ret.b.value = this.b.value + b.value;
          return ret;
      }
      
      ret.a = a.copy();
      ret.b = b.copy();
      
      ret.a.parent = ret;
      ret.b.parent = ret;
      
      return ret;
  }
  
  hash() {
      if (this._hash == undefined) {
          this._hash = spool(this.toHash());
      }
      return this._hash;
  }
  
  index(arg1) {
      if (typeof arg1 == "string" || arg1 instanceof String || typeof arg1
              == "number" || typeof arg1 == "boolean") 
      {
          arg1 = sym(arg1);
      } else {
          arg1 = arg1.copy();
      }
      
      var ret = sym();
      
      ret.op = "i";
      ret.a = this.copy();
      ret.b = arg1;
      
      return ret;
  }
  
  func(fname, arg1) {
      if (typeof fname == "string" || fname instanceof String) {
          fname = sym(fname);
      }
      
      var ret = sym();
      
      if (arg1 == undefined) {
          ret.a = fname.copy();
          ret.b = this.copy();
          ret.op = "c";
      } else {
          if (typeof arg1 == "string" || arg1 instanceof String || typeof arg1
              == "number" || typeof arg1 == "boolean") 
          {
              arg1 = sym(arg1);
          }
          
          ret.a = this.copy();
          ret.b = arg1.copy();
          ret.op = fname;
      }
      
      ret.is_func = true;
      
      return ret;
  }
  
  copy(copy_strcache) {
      var ret = new symcls();
      ret.name = this.name;
      ret.value = this.value;
      ret.use_parens = this.use_parens;
      ret.op = this.op;
      ret.is_func = this.is_func;
      
      if (copy_strcache) {
          ret._toString = this._toString; //risky!
          ret._hash = this._hash; //this too!
      } else {
          ret._hash = ret._toString = undefined;
      }
      
      if (this.a != undefined) {
          ret.a = this.a.copy(copy_strcache);
          ret.b = this.b.copy(copy_strcache);
      
          ret.a.parent = ret;
          ret.b.parent = ret;
      }
      
      return ret;
  }
  
  negate() {
      return this.binop(-1.0, "*");
  }
  
  add(b) {
      return this.binop(b, "+");
  }
  
  sub(b) {
      return this.binop(b, "-");
  }
  
  mul(b) {
      return this.binop(b, "*");
  }
  
  div(b) {
      return this.binop(b, "/");
  }
  
  pow(b) {
      return this.binop(b, "p");
  }
  
  clear_toString() {
      this._toString = undefined;
      this._hash = undefined;
      this._last_h = undefined;
      
      if (this.a != undefined) {
       //   this.a.clear_toString();
        //  this.b.clear_toString();
      }
  }
   
  toHash2() {
      var stack = toHash2_stack, stack2 = toHash2_stack_2, top=0;
      var stack3 = toHash2_stack_3;
      
      //stack is main stack
      //stack2 stores "stages" (states)
      //stack3 store beginning string indexing for caching
      
      stack[top] = this;
      stack2[top] = 0;
      stack3[top] = 0;
      
      var ret = "";
      
      var _i = 0;
      while (top >= 0) {
          if (_i > 100000) { 
              console.log("infinite loop!");
              break;
          }
          
          var item = stack[top];
          var stage = stack2[top];
          var start = stack3[top];
          top--;
          
          /*
          if (item._last_h != undefined) {
              ret += item._last_h;
              continue;
          }*/
          
          //console.log(item, stage);
          
          if (stage == 0) {
              ret += item.name+"|";
              ret += (item.value != undefined ? item.value : "") + "|";
              ret += item.is_func + "|";
          }
          
          if (item.a != undefined && stage == 0) {
              ret += item.op + "$";
              
              top++;
              stack[top] = item;
              stack2[top] = 1;
              stack3[top] = start;
              
              top++;
              stack[top] = item.a;
              stack2[top] = 0;
              stack3[top] = ret.length;
          } else if (item.b != undefined && stage == 1) {
              ret += "$";
              /*
              top++;
              stack[top] = item;
              stack2[top] = 2;
              stack3[top] = start;
              //*/
              
              top++;
              stack[top] = item.b;
              stack2[top] = 0;
              stack3[top] = ret.length;
          } /*else { 
              if (stage == 2) {
                  ret += "$";
              }
              
              item._last_h = ret.slice(start, ret.length);
          }*/
      }
      
      return ret;
  }
  
  toHash3() {
      var ret = "";
      
      if (this._last_h != undefined) {
          return this._last_h;
      }
      
      ret += pack_str(this.name);
      
      ret += this.value != undefined ? pack_short(this.value*15000) : "" //pack_short(0.0);
      ret += pack_byte(this.is_func);
      
      if (this.a != undefined) {
          ret += pack_op(this.op)
          ret += this.a.toHash3();// + pack_byte(-1);
          ret += this.b.toHash3();// + pack_byte(-1);
      }
      
      this._last_h = ret;
      
      return ret;
  }
  
  toHash() {
      //return ""+this;
      return this.toHash3();
      
      var ret = "";
      
      if (this._last_h != undefined) {
          //return this._last_h;
      }
      
      ret += this.name+"|";
      ret += (this.value != undefined ? this.value : "") + "|";
      ret += this.is_func + "|";
      
      if (this.a != undefined) {
          ret += this.op + "$";
          ret += this.a.toHash() + "$";
          ret += this.b.toHash() + "$";
      }
      
      this._last_h = ret;
      
      return ret;
  }
  
  toString() {
      if (this._toString != undefined) {
          return this._toString;
      }
      
      var use_parens = this.use_parens;
      var use_parens = use_parens && !(this.parent != undefined && (this.parent.op == "i" ||
                                       this.parent.op == "c" || this.parent.op.length > 2));
      
      use_parens = use_parens && !(this.value != undefined && this.a == undefined);
      use_parens = use_parens && !(this.name != undefined && this.name != "" && this.a == undefined);
      
      var s = use_parens ? "(" : "";
      
      if (this.a != undefined && this.op == "i") {
          return ""+this.a+"["+this.b+"]";
      } else if (this.a != undefined && this.is_func && this.op != "c") {
          s += ""+this.op + "(" + this.a + ", " + this.b + ")";
      } else if (this.a != undefined && this.is_func && this.op == "c") {
          s += ""+this.a+"("+this.b+")";
      } else if (this.a != undefined && this.op != "p") {
          s += ""+this.a + " " + this.op + " " + this.b;
      } else if (this.a != undefined && this.op == "p") {
          return "pow("+this.a+", "+this.b+")";
      } else if (this.value != undefined && this.a == undefined) {
          s += ""+this.value;
      } else if (this.name != undefined && this.name != "") {
          s += this.name;
      } else {
          s += "{ERROR!}";
      }
      
      s += use_parens ? ")" : "";
      
      this._toString = s;
      
      return s;
  }
}

export function sym(name_or_value) {
  return new symcls(name_or_value);
}

function recurse2_a(n, root, map, haskeys, map2, subpart_i, symtags) {
  function recurse2(n, root) {
      var key = n.hash();
      
      if (map.has(key)) {
          n.tag = symtags.get(map2.get(key));
          n.tag.key = key;
          n.tag.is_tag = true;
          n.key = key;
          
          if (root != undefined && n !== root) {
              if (!haskeys.has(root.key)) {
                  haskeys.set(root.key, new hashtable());
              }
              
              haskeys.get(root.key).set(key, 1);
          }
      }
      
      if (n.a != undefined) {
          recurse2(n.a, root);
          recurse2(n.b, root);
      }
      
      return n;
  }
  
  return recurse2(n, root);
}

var optimize = exports.optimize = function optimize(tree) {
  tot_symcls = 0;

  var start_tree = tree.copy(true);

  function output() {
    console.log.apply(console, arguments);
  }

  function optimize_pass(tree, subpart_start_i) {
    if (subpart_start_i == undefined)
        subpart_start_i = 0;
    var subpart_i = subpart_start_i;
    
    var totstep = 8;
    var curstage = 1;
    
    output("begin optimization stage "+(curstage++)+" of " + totstep + ". . .");
    
    
    var symtags = new hashtable();
    var map = new hashtable()
    var mapcount = new hashtable();
    function recurse(n, depth) {
        if (depth == undefined)
            depth = 0;
        
        if (n.a == undefined) // || n.a.a == undefined)
            return;
            
        var hash;
        if (n.a != undefined) {
            var str = n.toHash();
                
            if (str.length < 25) { //n.a == undefined || n.a.a == undefined) {//str.length < 30) {
                return;
            }
        }
        
        if (depth > 3) {
            hash = hash == undefined ? n.hash() : hash;
            
            map.set(hash, n.copy());
            
            if (!mapcount.has(hash)) {
                mapcount.set(hash, 0);
            }
            
            mapcount.set(hash, mapcount.get(hash)+1);
        }
        
        if (n.a != undefined) {
            recurse(n.a, depth+1);
        }
        if (n.b != undefined) {
            recurse(n.b, depth+1);
        }
    }
    
    recurse(tree);
    
    var keys = map.keys();
    keys.sort(function(a, b) {
        return -spool_len(a)*mapcount.get(a) + spool_len(b)*mapcount.get(b);
    });

    var map2 = new hashtable();

    output("begin optimization stage "+(curstage++)+" of " + totstep + ". . .");
    
    //supposedly, putting this bit in a closure will optimize better.
    var keys3 = [];
    var i2 = 0;
    var max_si = 0;
    function next() {
        for (var i=0; i<keys.length; i++) {
            if (mapcount.get(keys[i]) < 3) {
                map.remove(keys[i]);
                continue;
            }
            
            map2.set(keys[i], i2++);
            max_si = max(map2.get(keys[i]), max_si);
            
            symtags.set(i2-1, sym("SUBPART"+((i2-1)+subpart_i)));
        }
    }
    next();
    output("begin optimization stage "+(curstage++)+" of " + totstep + ". . .");
    
    keys = undefined;
    var haskeys = new hashtable();

    tree = recurse2_a(tree, undefined, map, haskeys, map2, subpart_i, symtags);
    
    var keys3 = map2.keys();
    keys3.sort(function(a, b) {
        return -spool_len(a)*mapcount.get(a) + spool_len(b)*mapcount.get(b);
    });
    
    function recurse3(n, key) {
        if (n.a != undefined) {
            if (n.a.tag != undefined && !n.a.is_tag && n.a.key == key) {
                n.a.parent = undefined;
                n.a = n.a.tag;
                n.clear_toString();
            } else {
                recurse3(n.a, key);
            }
            
            if (n.b.tag != undefined && !n.b.is_tag && n.b.key == key) {
                n.b.parent = undefined;
                n.b = n.b.tag;
                n.clear_toString();
            } else {
                recurse3(n.b, key);
            }                
        }
        
        return n;
    }
    output("begin optimization stage "+(curstage++)+" of " + totstep + ". . .");
    
    for (var i=0; i<keys3.length; i++) {
        tree = recurse3(tree, keys3[i]);
    }
    
    var exists = new hashtable();
    function recurse4(n, key) {
        if (n.is_tag) {
            exists.set(n.key, true);
        }
        
        if (n.is_tag && n.key != undefined && n.key == key)
            return true;
        
        if (n.a != undefined) {
            if (recurse4(n.a, key))
                return true;
            if (recurse4(n.b, key))
                return true;
        }
        
        return false;
    }
    
    recurse4(tree);
    output("begin optimization stage "+(curstage++)+" of " + totstep + ". . .");
    
    keys3.sort(function(a, b) {
        return -map2.get(a) + map2.get(b);
    });
    
    //apply substitutions to substitutions, too
    output("begin optimization stage "+(curstage++)+" of " + totstep + ". . .");
    output(keys3.length);
    var last_time2 = util.time_ms();
     
    var haskeys = new hashtable();
    window.haskeys = haskeys;

    /*
    function find_keys(n, root) {
        if (n !== root && n.is_tag) {
            
        }
        
        if (n.a != undefined) {
            find_keys(n.a, root);
            find_keys(n.b, root);
        }
    }
    
    for (var i=0; i<keys3.length; i++) {
        var n = map.get(keys3[i])
        n.key = keys3[i];
        
        find_keys(n, n);
    }*/
    
    for (var i=0; i<keys3.length; i++) {
    //for (var i=keys3.length-1; i>= 0; i--) {
        if (util.time_ms() - last_time2 > 500) {
            output("optimizing key", i+1, "of", keys3.length);
            last_time2 = util.time_ms();
        }
        
        var n = map.get(keys3[i]);
        
        var last_time = util.time_ms();
        
       for (var j=0; j<keys3.length; j++) {
       //for (var j=keys3.length-1; j>= 0; j--) {
            if (i == j)
                continue;
                
            if (util.time_ms() - last_time > 500) {
                output("  subkey part 1:", j+1, "of", keys3.length+", for", i+1);
                last_time = util.time_ms();
            }
            
            recurse2_a(n, n, map, haskeys, map2, subpart_i, symtags); 
       //*
       }
       
       for (var j=0; j<keys3.length; j++) {
       //for (var j=keys3.length-1; j>= 0; j--) {
            var key = keys3[j];
            
            if (i == j)
                continue;
                
            if (util.time_ms() - last_time > 500) {
                output("  subkey part 2", j+1, "of", keys3.length+", for", i+1);
                last_time = util.time_ms();
            }//*/
            
            if (haskeys.get(n.key) == undefined || !(haskeys.get(n.key).has(key)))
                continue;
                
            recurse3(n, keys3[j]);
            recurse4(n, keys3[j]);
            
            n.clear_toString();
        }
    }
    
    output("begin optimization stage "+(curstage++)+" of " + totstep + ". . .");
    
    function tag(n, root) {
        if (n != root && n.is_tag) {
            var k = n.key;
            
            if (k == root.key) {
                output("Cycle!", k, root.key);
                throw RuntimeError("Cycle! " + k + ", " + root.key);
                return;
            }
            
            root.ins.set(n.key, 1);
            
            var id = map2.get(n.key);
            root.ins_ids.set(id, id);
        }   
        
        if (n.a != undefined) {
            tag(n.a, root);
            tag(n.b, root);
        }
    }
    
    output("begin optimization stage "+(curstage++)+" of " + totstep + ". . .");
    
    var dag = [];
    window.dag = dag;
    
    function visit_n(k) {
        var n2 = map.get(k);
        
        if (!n2._done) {
            dagsort(n2);
        }
    }
    
    function dagsort(n) {
        if (n._done) {
            return;
        }
        
        if (n._visit) {
            throw new Error("CYCLE!", n, n._visit);
        }
        
        if (n.is_root) {
            n._visit = true;
            
            /*for (var k in n.ins) {
            n.ins.forEach(function(k) {
                var n2 = map.get(k);
                
                if (!n2._done) {
                    dagsort(n2);
                }
            }//, this);//*/
            n.ins.forEach(visit_n, this);
            
            n._visit = false;
            dag.push(n);
            
            n._done = true;
        }
        
        if (n.a != undefined) {
            dagsort(n.a);
            dagsort(n.b);
        }
    }
    
    for (var i=0; i<keys3.length; i++) {
        var n = map.get(keys3[i]);
        
        n.is_root = true;
        n.ins = new hashtable();
        n.ins_ids = new hashtable();
        //n.outs = new hashtable();
        n.id = map2.get(keys3[i]);
    }
    
    for (var i=0; i<keys3.length; i++) {
        var n = map.get(keys3[i]);
        
        n._visit = n._done = false;
        n.key = keys3[i];
        tag(n, n);
    }
    
    for (var i=0; i<keys3.length; i++) {
        var n = map.get(keys3[i]);
        if (!n._done) {
            dagsort(n);
        }
    }
    
    var i1 = 0;
    var header = "";
    for (var i=0; i<dag.length; i++) {
        var n = dag[i];
        var key = n.key;
        
        if (subpart_i > 0 || i > 0) header += ", "
        
        n.clear_toString();
        
        header += "\n    "
        header += "SUBPART"+map2.get(key)+" = " + ""+n;
    }
    header += "\n";
    
    var finals = header+""+tree;
    
    output("finished!");
    
    return [tree, finals, header, max_si];
  }

  var si = 0;
  var header2 = "";
  //for (var i=0; i<4; i++) {
    var r = optimize_pass(tree, si);
    
    if (i > 0 && header2.trim() != "" && header2.trim()[header2.length-1] != ",")
        header2 += ", ";
        
    header2 += r[2];
    
    tree = r[0].copy();
    si += r[3]+1;
    //console.log("\n\n\n\n");
  //}
  header2 = header2.trim();
  if (header2.trim() != "")
    header2 = "var " + header2 + ";\n";
    
  var final2 = header2+"\n  return "+tree+";\n";

  var ret=undefined, func;
  var code1 = final2;
  code1 = splitline(code1);
  //eval(code1)
  func = ret;

  var func2=undefined;
  var code2 = ""+start_tree;
  code2 = splitline(code2);
  func = ret;
  //eval(code2)

  return [code1, code2, tree]; //func, func2, code1, code2, tree];
  }
  var get_cache = exports.get_cache = function get_cache(k, v) {
    var ret;
    try {
        ret =  JSON.parse(localStorage["_store_"+k]);
    } catch (error) {
        util.print_stack(error);
        return undefined;
    }
    
    if (ret == "undefined") {
        return undefined;
    }
  }

  var optimize = exports.optimize = function optimize(tree) {
  var start_tree = tree.copy();

  function optimize_pass(tree, subpart_start_i) {
    if (subpart_start_i == undefined)
        subpart_start_i = 0;
    var subpart_i = subpart_start_i;
    
    var totstep = 8;
    var curstage = 1;
    
    console.log("begin optimization stage "+(curstage++)+" of " + totstep + ". . .");
    
    var map = new hashtable()
    var mapcount = new hashtable();
    function recurse(n, depth) {
        if (depth == undefined)
            depth = 0;
            
        var str = ""+n;
        if (str.length < 30)
            return;
        
        if (depth > 3) {
            var hash = n.hash();
            map.set(hash, n.copy());
            
            if (!mapcount.has(hash)) {
                mapcount.set(hash, 0);
            }
            
            mapcount.set(mapcount.get(hash)+1);
        }
        
        if (n.a != undefined) {
            recurse(n.a, depth+1);
        }
        if (n.b != undefined) {
            recurse(n.b, depth+1);
        }
    }
    
    recurse(tree);
    
    var keys = map.keys();
    keys.sort(function(a, b) {
        return spool_len(a)*mapcount[a] - spool_len(b)*mapcount[b];
    });

    var map2 = new hashtable();

    console.log("begin optimization stage "+(curstage++)+" of " + totstep + ". . .");
    
    //supposedly, putting this bit in a closure will optimize better.
    var keys3 = [];
    var i2 = 0;
    var max_si = 0;
    function next() {
        for (var i=0; i<keys.length; i++) {
            if (mapcount[keys[i]] < 3) {
                map.remove(keys[i]);
                continue;
            }
            
            //console.log(mapcount[keys[i]]*keys[i].length, mapcount[keys[i]]);
            
            map2.set(keys[i], i2++);
            max_si = max(map2[keys[i]], max_si);
        }
    }
    next();
    console.log("begin optimization stage "+(curstage++)+" of " + totstep + ". . .");
    
    keys = undefined;
    var haskeys = new hashtable();
    
    function recurse2(n, root) {
        var key = n.hash();
        
        if (map.has(key)) {
            n.tag = sym("SUBPART"+(map2.get(key)+subpart_i));
            n.tag.key = key;
            n.tag.is_tag = true;
            n.key = key;
            
            if (root != undefined && n !== root) {
                if (!haskeys.has(root.key)) {
                    haskeys.set(root.key, new hashtable());
                }
                
                haskeys.get(root.key).set(key, 1);
            }
        }
        
        if (n.a != undefined) {
            recurse2(n.a, root);
            recurse2(n.b, root);
        }
        
        return n;
    }
    tree = recurse2(tree);
    
    var keys3 = map2.keys();
    keys3.sort(function(a, b) {
        return spool_len(a)*mapcount[a] - spool_len(b)*mapcount[b];
    });
    
    function recurse3(n, key) {
        if (n.a != undefined) {
            if (n.a.tag != undefined && !n.a.is_tag && n.a.key == key) {
                n.a.parent = undefined;
                n.a = n.a.tag;
                n.clear_toString();
            } else {
                recurse3(n.a, key);
            }
            
            if (n.b.tag != undefined && !n.b.is_tag && n.b.key == key) {
                n.b.parent = undefined;
                n.b = n.b.tag;
                n.clear_toString();
            } else {
                recurse3(n.b, key);
            }                
        }
        
        return n;
    }
    console.log("begin optimization stage "+(curstage++)+" of " + totstep + ". . .");
    
    for (var i=0; i<keys3.length; i++) {
        tree = recurse3(tree, keys3[i]);
    }
    
    var exists = new hashtable();
    function recurse4(n, key) {
        if (n.is_tag) {
            exists.set(n.key, true);
        }
        
        if (n.is_tag && n.key != undefined && n.key == key)
            return true;
        
        if (n.a != undefined) {
            if (recurse4(n.a, key))
                return true;
            if (recurse4(n.b, key))
                return true;
        }
        
        return false;
    }
    
    recurse4(tree);
    console.log("begin optimization stage "+(curstage++)+" of " + totstep + ". . .");
    
    keys3.sort(function(a, b) {
        return map2.get(a) - map2.get(b);
    });
    
    //apply substitutions to substitutions, too
    console.log("begin optimization stage "+(curstage++)+" of " + totstep + ". . .");
    console.log(keys3.length);
    var last_time2 = util.time_ms();
    
    /*
    function find_keys(n, root) {
        if (n !== root && n.is_tag) {
            
        }
        
        if (n.a != undefined) {
            find_keys(n.a, root);
            find_keys(n.b, root);
        }
    }
    
    for (var i=0; i<keys3.length; i++) {
        var n = map[keys3[i]];
        n.key = keys3[i];
        
        find_keys(n, n);
    }*/
    
    for (var i=0; i<keys3.length; i++) {
        if (util.time_ms() - last_time2 > 500) {
            console.log("optimizing key", i+1, "of", keys3.length);
            last_time2 = util.time_ms();
        }
        
        var n = map.get(keys3[i]);
        
        var last_time = util.time_ms();
        
        for (var j=0; j<keys3.length; j++) {
            if (i == j)
                continue;
                
            if (util.time_ms() - last_time > 500) {
                console.log("  subkey part 1:", j+1, "of", keys3.length+", for", i+1);
                last_time = util.time_ms();
            }
            
            recurse2(n, n);
       }
       
       for (var j=0; j<keys3.length; j++) {
            var key = keys3[j];
            
            if (i == j)
                continue;
                
            if (util.time_ms() - last_time > 500) {
                console.log("  subkey part 2", j+1, "of", keys3.length+", for", i+1);
                last_time = util.time_ms();
            }
            
            if (haskeys[n.key] == undefined || !(haskeys.has(n.key)))
                continue;
                
            recurse3(n, keys3[j]);
            recurse4(n, keys3[j]);
            
            n.clear_toString();
        }
    }
    
    console.log("begin optimization stage "+(curstage++)+" of " + totstep + ". . .");
    
    function tag(n, root) {
        if (n != root && n.is_tag) {
            var k = n.key;
            
            if (k == root.key) {
                console.log("Cycle!", k, root.key);
                throw RuntimeError("Cycle! " + k + ", " + root.key);
                return;
            }
            
            root.ins.set(n.key, 1);
            
            var id = map2.get(n.key);
            root.ins_ids.set(id, id);
        }   
        
        if (n.a != undefined) {
            tag(n.a, root);
            tag(n.b, root);
        }
    }
    
    console.log("begin optimization stage "+(curstage++)+" of " + totstep + ". . .");
    
    var dag = [];
    window.dag = dag;
    
    function dagsort(n) {
        if (n._done) {
            return;
        }
        
        if (n._visit) {
            throw new Error("CYCLE!", n, n._visit);
        }
        
        if (n.is_root) {
            n._visit = true;
            
            n.ins.forEach(function(k) {
                var n2 = map.get(k);
                
                if (!n2._done) {
                    dagsort(n2);
                }
            }, this);
            
            n._visit = false;
            dag.push(n);
            
            n._done = true;
        }
        
        if (n.a != undefined) {
            dagsort(n.a);
            dagsort(n.b);
        }
    }
    
    for (var i=0; i<keys3.length; i++) {
        var n = map.get(keys3[i]);
        
        n.is_root = true;
        n.ins = new hashtable();
        n.ins_ids = new hashtable();
        n.outs = new hashtable();
        n.id = map2.get(keys3[i]);
    }
    
    for (var i=0; i<keys3.length; i++) {
        var n = map.get(keys3[i]);
        
        n._visit = n._done = false;
        n.key = keys3[i];
        tag(n, n);
    }
    
    for (var i=0; i<keys3.length; i++) {
        //console.log("inlen", Object.keys(n.ins).length);
        
        var n = map.get(keys3[i]);
        if (!n._done) {
            dagsort(n);
        }
    }
    
    var i1 = 0;
    var header = "";
    for (var i=0; i<dag.length; i++) {
        var n = dag[i];
        var key = n.key;
        
        //if (!(exists.has(key)))
        //    continue;
        
        if (subpart_i > 0 || i > 0) header += ", "
        
        n.clear_toString();
        
        header += "\n    "
        header += "SUBPART"+map2.get(key)+" = " + ""+n;
    }
    header += "\n";
    
    var finals = header+""+tree;
    
    console.log("finished!");
    
    return [tree, finals, header, max_si];
  }

  var si = 0;
  var header2 = "";
  //for (var i=0; i<4; i++) {
    var r = optimize_pass(tree, si);
    
    if (i > 0 && header2.trim() != "" && header2.trim()[header2.length-1] != ",")
        header2 += ", ";
        
    header2 += r[2];
    
    tree = r[0].copy();
    si += r[3]+1;
    //console.log("\n\n\n\n");
  //}
  header2 = header2.trim();
  if (header2.trim() != "")
    header2 = "var " + header2 + ";\n";
    
  var final2 = header2+"\n  return "+tree+";\n";

  var func;
  var code1 = "func = function(s, j, n, ks, dvn) {"+final2+"};";
  code1 = splitline(code1);
  eval(code1)

  var func2=undefined;
  var code2 = "func2 = function(s, j, n, ks, dvn) {return "+(""+start_tree)+";};";
  code2 = splitline(code2);
  eval(code2)

  return [func, func2, code1, code2, tree];
}

export function get_cache(k, v) {
    var ret;
    try {
        ret =  JSON.parse(localStorage["_store_"+k]);
    } catch (error) {
      util.print_stack(error);
      return undefined;
  }
  
  if (ret == "undefined") {
      return undefined;
  }
}
window.get_cache = get_cache;

export function store_cache(k, v) {
  localStorage["_store_"+k] = JSON.stringify(v);
}
