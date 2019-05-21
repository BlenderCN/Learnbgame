//a zebra-like type system api

//handle to module.  never access in code; for debug console use only.
var _typesystem = undefined;

define([
  "polyfill"
], function(unused) {
  "use strict";
  
  var exports = _typesystem = {};

  function ClassGetter(func) {
    this.func = func;
  }
  function ClassSetter(func) {
    this.func = func;
  }

  var prototype_idgen = 1;
  var defined_classes = exports.defined_classes = [];

  var StaticMethod = function StaticMethod(func) {
    this.func = func;
  }
    
  var handle_statics = function(cls, parent) {
    for (var k in cls.prototype) {
      if (cls.prototype[k] instanceof StaticMethod) {
        var func = cls.prototype[k];
        
        delete cls.prototype[k];
        cls[k] = func.func;
      }
    }
    
    if (parent != undefined) {
      for (var k in parent) {
        var v = parent[k];
        
        //only inherit static methods added to parent with this module
        if ((v == undefined || "_is_static_method" in v) && !(k in cls)) {
          cls[k] = v;
        }
      }
    }
  }

  var Class = exports.Class = function Class(methods) {
    var construct = undefined;
    var parent = undefined;
    
    if (arguments.length > 1) {
      //a parent was passed in
      
      parent = methods;
      methods = arguments[1];
    }
    
    for (var i=0; i<methods.length; i++) {
      var f = methods[i];
      
      if (f.name == "constructor") {
        construct = f;
        break;
      }
    }
    
    if (construct == undefined) {
      console.log("Warning, constructor was not defined", methods);
      
      if (parent != undefined) {
        construct = function() {
          parent.apply(this, arguments);
        }
      } else {
        construct = function() {
        }
      }
    }
    
    if (parent != undefined) {
      construct.prototype = Object.create(parent.prototype);
    }
    
    construct.prototype.__prototypeid__ = prototype_idgen++;
    construct[Symbol.keystr] = function() {
      return this.prototype.__prototypeid__;
    }
    
    construct.__parent__ = parent;
    construct.__statics__ = [];
    
    var getters = {};
    var setters = {};
    var getset = {};
    
    var statics = {}
    
    //handle getters/setters
    for (var i=0; i<methods.length; i++) {
      var f = methods[i];
      
      if (f instanceof ClassSetter) {
        setters[f.func.name] = f.func;
        getset[f.func.name] = 1;
      } else if (f instanceof ClassGetter) {
        getters[f.func.name] = f.func;
        getset[f.func.name] = 1;
      } else if (f instanceof StaticMethod) {
        statics[f.func.name] = f.func;
      }
    }
    
    for (var k in statics) {
      construct[k] = statics[k];
    }
    
    for (var k in getset) {
      var def = {
        enumerable   : false,
        configurable : true,
        get : getters[k],
        set : setters[k]
      }
      
      Object.defineProperty(construct.prototype, k, def);
    }
    
    handle_statics(construct, parent);
    
    if (parent != undefined)
      construct.__parent__ = parent;
    
    for (var i=0; i<methods.length; i++) {
      var f = methods[i];
      
      if (f instanceof ClassGetter || f instanceof ClassSetter)
        continue;

      construct.prototype[f.name] = f;
    }
    
    return construct;
  }

  Class.getter = Class.get = function(func) {
    return new ClassGetter(func);
  }
  Class.setter = Class.set = function(func) {
    return new ClassSetter(func);
  }

  Class.static = Class.static_method = function(func) {
    func._is_static_method = true;
    return new StaticMethod(func);
  }

  var mixin = exports.mixin = function mixin(cls, parent) {
    var keys = Object.getOwnPropertyNames(parent.prototype);
    
    for (var k of keys) {
      if (k == "constructor") {
        continue;
      }
      
      if (!(k in cls.prototype)) {
        cls.prototype[k] = parent.prototype[k];
      }
    }
    
    for (var sym of Object.getOwnPropertySymbols(parent.prototype)) {
      if (!(sym in cls.prototype)) {
        cls.prototype[sym] = parent.prototype[sym];
      }
    }
  }
  
  return exports;
});
