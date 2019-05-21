var _parseutil = undefined;

define([
], function(util) {
  "use strict";
  
  var exports = _parseutil = {};
  
  var token = exports.token = class token {
  constructor(type, val, lexpos, lexlen, lineno, lexer, parser) {
    this.type = type;
    this.value = val;
    this.lexpos = lexpos;
    this.lexlen = lexlen;
    this.lineno = lineno;
    this.lexer = lexer;
    this.parser = parser;
  }
  
  toString() {
    if (this.value != undefined)
      return "token(type=" + this.type + ", value='" + this.value + "')"
    else
      return "token(type=" + this.type + ")"
  }
}
  
//func is optional. it takes a function
//with one parameter, token, and either
//a) returns the token, or b) returns
//undefined, in which case the token
//should be ignored by the lexer
var tokdef = exports.tokdef = class tokdef {
  constructor(name, regexpr, func) {
    this.name = name;
    this.re = regexpr
    this.func = func
  }
}

var PUTLParseError = exports.PUTLParseError
 = class PUTLParseError extends Error 
{
  constructor(msg) {
    super();
  }
}

//errfunc is optional.  it requires
//a function that takes one param, lexer,
//and returns whether or not the lexer
//should propegate an error when an error
//has happened
var lexer = exports.lexer = class lexer {
  constructor(tokdef, errfunc) {
    this.tokdef = tokdef;
    this.tokens = new Array();
    this.lexpos = 0;
    this.lexdata = "";
    this.lineno = 0;
    this.errfunc = errfunc;
    this.tokints = {}
    
    for (var i=0; i<tokdef.length; i++) {
      this.tokints[tokdef[i].name] = i;
    }
    
    this.statestack = [["__main__", 0]];
    this.states = {"__main__" : [tokdef, errfunc]};
    this.statedata = 0; //public variable
  }

//errfunc is optional, defines state-specific error function
  add_state(name, tokdef, errfunc) {
    if (errfunc == undefined) {
      errfunc = function(lexer) { return true; };
    }
    
    this.states[name] = [tokdef, errfunc];
  }

  tok_int(name) {
    
  }

  //statedata is optional.
  //it stores state-specific data in lexer.statedata.
  push_state(state, statedata) {
    this.statestack.push([state, statedata])
    
    state = this.states[state];
    this.statedata = statedata;
    
    this.tokdef = state[0];
    this.errfunc = state[1];
  }

  pop_state() {
    var item = this.statestack[this.statestack.length-1];
    var state = this.states[item[0]];
    
    this.tokdef = state[0];
    this.errfunc = state[1];
    this.statedata = item[1];
  }

  input(str) {
    //go back to main state
    while (this.statestack.length > 1) {
      this.pop_state();
    }
    
    this.lexdata = str;
    this.lexpos = 0;
    this.lineno = 0;
    this.tokens = new Array();
    
    this.peeked_tokens = [];
  }

  error() {
    if (this.errfunc != undefined && !this.errfunc(this))
      return;
      
    console.log("Syntax error near line " + this.lineno);
    var next = Math.min(this.lexpos+8, this.lexdata.length);
    console.log("  " + this.lexdata.slice(this.lexpos, next));
    
    throw new PUTLParseError("Parse error");
  }

  peek() {
    var tok = this.next(true);
    
    if (tok == undefined) 
      return undefined;
    
    this.peeked_tokens.push(tok);
    return tok;
  }


  peek_i(i) {
    while (this.peeked_tokens.length <= i) {
      var t = this.peek();
      if (t == undefined)
        return undefined;
    }
    
    return this.peeked_tokens[i];
  }

  at_end() {
    return this.lexpos >= this.lexdata.length && this.peeked_tokens.length == 0;
  }

  next(ignore_peek) {
    if (ignore_peek != true && this.peeked_tokens.length > 0) {
      var tok = this.peeked_tokens[0];
      this.peeked_tokens.shift();
      
      return tok;
    }
    
    if (this.lexpos >= this.lexdata.length)
      return undefined;
    
    var ts = this.tokdef;
    var tlen = ts.length;
    
    var lexdata = this.lexdata.slice(this.lexpos, this.lexdata.length);
    
    var results = []
    
    for (var i=0; i<tlen; i++) {
      var t = ts[i];
      
      if (t.re == undefined)
        continue;
      
      var res = t.re.exec(lexdata);
      
      if (res != null && res != undefined && res.index == 0) {
        results.push([t, res]);
      }
    }
    
    var max_res = 0;
    var theres = undefined;
    for (var i=0; i<results.length; i++) {
      var res = results[i];
      
      if (res[1][0].length > max_res) {
        theres = res;
        max_res = res[1][0].length;
      }
    }
    
    if (theres == undefined) {
      this.error();
      return;
    }
    
    var def = theres[0];
    
    var lexlen = max_res;
    var tok = new token(def.name, theres[1][0], this.lexpos, lexlen, this.lineno, this, undefined);
    this.lexpos += max_res;
    
    if (def.func) {
      tok = def.func(tok)
      if (tok == undefined) {
        return this.next();
      }
    }
    
    return tok;
  }
}

var parser = exports.parser = class parser {
  constructor(lexer, errfunc) {
    this.lexer = lexer;
    this.errfunc = errfunc;
    this.start = undefined;
  }

  parse(data, err_on_unconsumed) {
    if (err_on_unconsumed == undefined)
      err_on_unconsumed = true;
      
    if (data != undefined)
      this.lexer.input(data);
    
    var ret = this.start(this);
    if (err_on_unconsumed && !this.lexer.at_end() && this.lexer.next() != undefined) {
      //console.log(this.lexer.lexdata.slice(this.lexer.lexpos-1, this.lexer.lexdata.length));
      this.error(undefined, "parser did not consume entire input");
    }
    
    return ret;
  }

  input(data) {
    this.lexer.input(data);
  }

  error(tok, msg) {
    if (msg == undefined)
      msg = ""
    
    if (tok == undefined)
      var estr = "Parse error at end of input: " + msg
    else
      estr = "Parse error at line " + (tok.lineno+1) + ": " + msg;
    
    var buf = "1| "
    var ld = this.lexer.lexdata;
    var l = 1;
    for (var i=0; i<ld.length; i++) {
      var c = ld[i];
      if (c == '\n') {
        l++;
        buf += "\n" + l + "| "
      } else {
        buf += c;
      }
    }
    
    console.log("------------------")
    console.log(buf);
    console.log("==================")
    console.log(estr);
    
    if (this.errfunc && !this.errfunc(tok)) {
      return;
    }
    
    throw new PUTLParseError(estr);
  }

  peek() {
    var tok = this.lexer.peek();
    if (tok != undefined)
      tok.parser = this;
      
    return tok;
  }

  peek_i(i) {
    var tok = this.lexer.peek_i(i);
    if (tok != undefined)
      tok.parser = this;
      
    return tok;
  }

  peeknext() {
    return this.peek_i(0);
  }

  next() {
    var tok = this.lexer.next();
    if (tok != undefined)
      tok.parser = this;
    
    return tok;
  }

  optional(type) {
    var tok = this.peek_i(0);
    
    if (tok == undefined) return false;
    
    if (tok.type == type) {
      this.next();
      return true;
    }
    
    return false;
  } 

  at_end() {
    return this.lexer.at_end();
  }

  expect(type, msg) {
    var tok = this.next();
    
    if (msg == undefined)
      msg = type
    
    if (tok == undefined || tok.type != type) {
      this.error(tok, "Expected " + msg);
    }
    
    return tok.value;
  }
}

function test_parser() {
  var basic_types = new set([
    "int", 
    "float", 
    "double",
    "vec2",
    "vec3",
    "vec4",
    "mat4",
    "string"]);
  
  var reserved_tokens = new set([
    "int", 
    "float", 
    "double", 
    "vec2", 
    "vec3", 
    "vec4", 
    "mat4", 
    "string", 
    "static_string",
    "array"]);

  function tk(name, re, func) {
    return new tokdef(name, re, func);
  }
  var tokens = [
    tk("ID", /[a-zA-Z]+[a-zA-Z0-9_]*/, function(t) {
      if (reserved_tokens.has(t.value)) {
        t.type = t.value.toUpperCase();
      }
      
      return t;
    }),
    tk("OPEN", /\{/),
    tk("CLOSE", /}/),
    tk("COLON", /:/),
    tk("JSCRIPT", /\|/, function(t) {
      var js = ""
      var lexer = t.lexer;
      while (lexer.lexpos < lexer.lexdata.length) {
        var c = lexer.lexdata[lexer.lexpos];
        if (c == "\n") 
          break;
        
        js += c;
        lexer.lexpos++;
      }
      
      if (js.endsWith(";")) {
        js = js.slice(0, js.length-1);
        lexer.lexpos--;
      }
      
      t.value = js;
      return t;
    }),
    
    tk("LPARAM", /\(/),
    tk("RPARAM", /\)/),
    tk("COMMA", /,/),
    tk("NUM", /[0-9]/),
    tk("SEMI", /;/),
    tk("NEWLINE", /\n/, function(t) {
      t.lexer.lineno += 1;
    }),
    tk("SPACE", / |\t/, function(t) {
      //throw out non-newline whitespace tokens
    })
  ];

  for (var rt in reserved_tokens) {
    tokens.push(tk(rt.toUpperCase()));
  }
  
  /*var a = 
  Loop {
    eid : int;
    flag : int;
    index : int;
    type : int;
    
    co : vec3;
    no : vec3;
    loop : int | eid(loop);
    edges : array(e, int) | e.eid;
    
    loops : array(Loop);
  }
  """;
  */
  
  function errfunc(lexer) {
    return true; //throw error
  }
  
  var lex = new lexer(tokens, errfunc)
  console.log("Testing lexical scanner...")
  
  lex.input(a);
  
  var tok;
  while (tok = lex.next()) {
    console.log(tok.toString())
  }
  
  var parser = new parser(lex);
  parser.input(a);
  
  function p_Array(p) {
    p.expect("ARRAY");
    p.expect("LPARAM");
    
    var arraytype = p_Type(p);
    var itername = "";
    
    if (p.optional("COMMA")) {
      itername = arraytype;
      arraytype = p_Type(p);
    }
    
    
    p.expect("RPARAM");
    
    return {type : "array", data : {type : arraytype, iname : itername}};
  }
  
  function p_Type(p) {
    var tok = p.peek()
    
    if (tok.type == "ID") {
      p.next();
      return {type : "struct", data : "\"" + tok.value + "\""};
    } else if (basic_types.has(tok.type.toLowerCase())) {
      p.next();
      return {type : tok.type.toLowerCase()};
    } else if (tok.type == "ARRAY") {
      return p_Array(p);
    } else {
      p.error(tok, "invalid type " + tok.type); //(tok.value == "" ? tok.type : tok.value));
    }
  }
  
  function p_Field(p) {
    var field = {}
    
    console.log("-----", p.peek().type);
    
    field.name = p.expect("ID", "struct field name");
    p.expect("COLON");
    
    field.type = p_Type(p);    
    field.set = undefined;
    field.get = undefined;
    
    var tok = p.peek();
    if (tok.type == "JSCRIPT") {
      field.get =  tok.value;
      p.next()
    }
    
    tok = p.peek();
    if (tok.type == "JSCRIPT") {
      field.set = tok.value;
      p.next();
    }
    
    p.expect("SEMI");
    
    return field;
  }
  
  function p_Struct(p) {
    var st = {}
    st.name = p.expect("ID", "struct name")
    st.fields = [];
    
    p.expect("OPEN");
    
    while (1) {
      if (p.at_end()) {
        p.error(undefined);
      } else if (p.optional("CLOSE")) {
        break;
      } else {
        st.fields.push(p_Field(p));
      }
    } 
    
    return st;
  }
  
  var ret = p_Struct(parser);
  
  console.log(JSON.stringify(ret));
}

return exports;
});
