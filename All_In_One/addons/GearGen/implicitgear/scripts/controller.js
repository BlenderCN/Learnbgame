//handle to module.  never access in code; for debug console use only.
var _controller = undefined;

define([
  "util", "dat"
], function(util, unused_dat) {
  "use strict";
  
  var exports = _controller = {};

  var Context = exports.Context = class Context {
    constructor(appstate) {
      this.appstate = appstate;
    }
  };

  var DataPathError = exports.DataPathError = class DataPathError extends Error {
  };

  var PathProp = exports.PathProp = class PathProp {
    constructor(value, owner, prop) {
      this.value = value;
      this.owner = owner;
      this.prop = prop;
    }

    set(val) {
      this.owner[this.prop] = val;
      return this;
    }
  }

  var parse_path_rets = new util.cachering(function() {
    return new PathProp();
  }, 128);

  var parsePath = exports.parsePath = function(ctx, str) {
    var cs = str.trim().split(".");

    var obj = ctx;
    var ret = parse_path_rets.next();

    for (var i=0; i<cs.length; i++) {
      if (!(cs[i] in obj)) {
        console.trace(cs[i] + " is not in object", obj);
        throw new DataPathError(cs[i] + " is not in object " + obj);
      }

      ret.owner = obj;
      ret.prop = cs[i];

      obj = obj[cs[i]];
    }

    if (ret.owner !== undefined && ret.owner._toolprops !== undefined && ret.prop in ret.owner._toolprops) {
      var toolprop = ret.owner._toolprops[ret.prop];

      if (toolprop.description != "") {
        ret.description = toolprop.description;
      }

      ret.toolprop = toolprop;
    }
    ret.value = obj;

    return ret;
  };

  var GUI = exports.GUI = class GUI {
    constructor(name, appstate, datelem) {
      this.appstate = appstate;

      if (datelem === undefined) { //make root-level gui
        this.dat = new dat.GUI();
        this.dat.domElement.style["z-index"] = 10;
        this.dat.domElement.style["position"] = "absolute";
      } else {
        this.dat = datelem; //e.g. panels
      }

      this.name = name;
      this.ctx = new Context(appstate);
      this.panels = [];
    }

    panel(name) {
      this.panels[name] = new GUI(name, this.appstate, this.dat.addFolder(name));
      return this.panels[name];
    }

    destroy() {
      this.dat.destroy();
    }

    checkbox(name, path) {
      var wrap = {};
      var this2 = this;

      Object.defineProperty(wrap, name, {
        get : function() {
          var prop = parsePath(this2.ctx, path);
          return !!prop.value;
        },

        set : function(val) {
          var prop = parsePath(this2.ctx, path);
          prop.set(!!val);
        }
      })

      var prop = parsePath(this.ctx, path);
      var ret = this.dat.add(wrap, name); //.listen();

      if (prop.description !== undefined) {
        ret.description(prop.description);
      }

      return ret;
    }

    textbox(name, path) {
      var wrap = {};
      var this2 = this;

      Object.defineProperty(wrap, name, {
        get : function() {
          var prop = parsePath(this2.ctx, path);
          return prop.value;
        },

        set : function(val) {
          var prop = parsePath(this2.ctx, path);
          prop.set(val);
        }
      })

      var prop = parsePath(this.ctx, path);
      var ret = this.dat.add(wrap, name); //.listen();

      if (prop.description !== undefined) {
        ret.description(prop.description);
      }

      return ret;
    }

    slider(name, path, min, max, step) {
      step = step === undefined ? 0.1 : step;

      if (arguments.length < 4)
        throw new Error("not enough arguments to GUI.slider()");

      var wrap = {};
      var this2 = this;

      Object.defineProperty(wrap, name, {
        get : function() {
          var prop = parsePath(this2.ctx, path);
          return prop.value;
        },

        set : function(val) {
          var prop = parsePath(this2.ctx, path);
          prop.set(val);
        }
      })

      var prop = parsePath(this.ctx, path);
      var ret = this.dat.add(wrap, name, min, max); //.listen();

      if (prop.description !== undefined) {
        ret.description(prop.description);
      }

      return ret;
    }

    button(name, func, thisvar) {
      var obj = {};
      
      if (thisvar !== undefined) {
        obj[name] = function() {
          func.call(thisvar);
        }
      } else {
        obj[name] = function() {
          func();
        }
      }

      return this.dat.add(obj, name);
    }
  }
  
  return exports;
});
