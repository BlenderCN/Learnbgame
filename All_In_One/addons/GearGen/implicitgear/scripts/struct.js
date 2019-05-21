(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    //Allow using this built library as an AMD module
    //in another project. That other project will only
    //see this AMD call, not the internal modules in
    //the closure below.
    define([], factory);
  } else {
    //Browser globals case. Just assign the
    //result to a property on the global.
    root.nstructjs = factory();
  }
}(this, function () {
  //almond, and your modules will be inlined here
  /**
   * @license almond 0.3.1 Copyright (c) 2011-2014, The Dojo Foundation All Rights Reserved.
   * Available via the MIT or new BSD license.
   * see: http://github.com/jrburke/almond for details
   */
//Going sloppy to avoid 'use strict' string cost, but strict practices should
//be followed.
  /*jslint sloppy: true */
  /*global setTimeout: false */

  var requirejs, require, define;
  (function (undef) {
    var main, req, makeMap, handlers,
      defined = {},
      waiting = {},
      config = {},
      defining = {},
      hasOwn = Object.prototype.hasOwnProperty,
      aps = [].slice,
      jsSuffixRegExp = /\.js$/;

    function hasProp(obj, prop) {
      return hasOwn.call(obj, prop);
    }

    /**
     * Given a relative module name, like ./something, normalize it to
     * a real name that can be mapped to a path.
     * @param {String} name the relative name
     * @param {String} baseName a real name that the name arg is relative
     * to.
     * @returns {String} normalized name
     */
    function normalize(name, baseName) {
      var nameParts, nameSegment, mapValue, foundMap, lastIndex,
        foundI, foundStarMap, starI, i, j, part,
        baseParts = baseName && baseName.split("/"),
        map = config.map,
        starMap = (map && map['*']) || {};

      //Adjust any relative paths.
      if (name && name.charAt(0) === ".") {
        //If have a base name, try to normalize against it,
        //otherwise, assume it is a top-level require that will
        //be relative to baseUrl in the end.
        if (baseName) {
          name = name.split('/');
          lastIndex = name.length - 1;

          // Node .js allowance:
          if (config.nodeIdCompat && jsSuffixRegExp.test(name[lastIndex])) {
            name[lastIndex] = name[lastIndex].replace(jsSuffixRegExp, '');
          }

          //Lop off the last part of baseParts, so that . matches the
          //"directory" and not name of the baseName's module. For instance,
          //baseName of "one/two/three", maps to "one/two/three.js", but we
          //want the directory, "one/two" for this normalization.
          name = baseParts.slice(0, baseParts.length - 1).concat(name);

          //start trimDots
          for (i = 0; i < name.length; i += 1) {
            part = name[i];
            if (part === ".") {
              name.splice(i, 1);
              i -= 1;
            } else if (part === "..") {
              if (i === 1 && (name[2] === '..' || name[0] === '..')) {
                //End of the line. Keep at least one non-dot
                //path segment at the front so it can be mapped
                //correctly to disk. Otherwise, there is likely
                //no path mapping for a path starting with '..'.
                //This can still fail, but catches the most reasonable
                //uses of ..
                break;
              } else if (i > 0) {
                name.splice(i - 1, 2);
                i -= 2;
              }
            }
          }
          //end trimDots

          name = name.join("/");
        } else if (name.indexOf('./') === 0) {
          // No baseName, so this is ID is resolved relative
          // to baseUrl, pull off the leading dot.
          name = name.substring(2);
        }
      }

      //Apply map config if available.
      if ((baseParts || starMap) && map) {
        nameParts = name.split('/');

        for (i = nameParts.length; i > 0; i -= 1) {
          nameSegment = nameParts.slice(0, i).join("/");

          if (baseParts) {
            //Find the longest baseName segment match in the config.
            //So, do joins on the biggest to smallest lengths of baseParts.
            for (j = baseParts.length; j > 0; j -= 1) {
              mapValue = map[baseParts.slice(0, j).join('/')];

              //baseName segment has  config, find if it has one for
              //this name.
              if (mapValue) {
                mapValue = mapValue[nameSegment];
                if (mapValue) {
                  //Match, update name to the new value.
                  foundMap = mapValue;
                  foundI = i;
                  break;
                }
              }
            }
          }

          if (foundMap) {
            break;
          }

          //Check for a star map match, but just hold on to it,
          //if there is a shorter segment match later in a matching
          //config, then favor over this star map.
          if (!foundStarMap && starMap && starMap[nameSegment]) {
            foundStarMap = starMap[nameSegment];
            starI = i;
          }
        }

        if (!foundMap && foundStarMap) {
          foundMap = foundStarMap;
          foundI = starI;
        }

        if (foundMap) {
          nameParts.splice(0, foundI, foundMap);
          name = nameParts.join('/');
        }
      }

      return name;
    }

    function makeRequire(relName, forceSync) {
      return function () {
        //A version of a require function that passes a moduleName
        //value for items that may need to
        //look up paths relative to the moduleName
        var args = aps.call(arguments, 0);

        //If first arg is not require('string'), and there is only
        //one arg, it is the array form without a callback. Insert
        //a null so that the following concat is correct.
        if (typeof args[0] !== 'string' && args.length === 1) {
          args.push(null);
        }
        return req.apply(undef, args.concat([relName, forceSync]));
      };
    }

    function makeNormalize(relName) {
      return function (name) {
        return normalize(name, relName);
      };
    }

    function makeLoad(depName) {
      return function (value) {
        defined[depName] = value;
      };
    }

    function callDep(name) {
      if (hasProp(waiting, name)) {
        var args = waiting[name];
        delete waiting[name];
        defining[name] = true;
        main.apply(undef, args);
      }

      if (!hasProp(defined, name) && !hasProp(defining, name)) {
        throw new Error('No ' + name);
      }
      return defined[name];
    }

    //Turns a plugin!resource to [plugin, resource]
    //with the plugin being undefined if the name
    //did not have a plugin prefix.
    function splitPrefix(name) {
      var prefix,
        index = name ? name.indexOf('!') : -1;
      if (index > -1) {
        prefix = name.substring(0, index);
        name = name.substring(index + 1, name.length);
      }
      return [prefix, name];
    }

    /**
     * Makes a name map, normalizing the name, and using a plugin
     * for normalization if necessary. Grabs a ref to plugin
     * too, as an optimization.
     */
    makeMap = function (name, relName) {
      var plugin,
        parts = splitPrefix(name),
        prefix = parts[0];

      name = parts[1];

      if (prefix) {
        prefix = normalize(prefix, relName);
        plugin = callDep(prefix);
      }

      //Normalize according
      if (prefix) {
        if (plugin && plugin.normalize) {
          name = plugin.normalize(name, makeNormalize(relName));
        } else {
          name = normalize(name, relName);
        }
      } else {
        name = normalize(name, relName);
        parts = splitPrefix(name);
        prefix = parts[0];
        name = parts[1];
        if (prefix) {
          plugin = callDep(prefix);
        }
      }

      //Using ridiculous property names for space reasons
      return {
        f: prefix ? prefix + '!' + name : name, //fullName
        n: name,
        pr: prefix,
        p: plugin
      };
    };

    function makeConfig(name) {
      return function () {
        return (config && config.config && config.config[name]) || {};
      };
    }

    handlers = {
      require: function (name) {
        return makeRequire(name);
      },
      exports: function (name) {
        var e = defined[name];
        if (typeof e !== 'undefined') {
          return e;
        } else {
          return (defined[name] = {});
        }
      },
      module: function (name) {
        return {
          id: name,
          uri: '',
          exports: defined[name],
          config: makeConfig(name)
        };
      }
    };

    main = function (name, deps, callback, relName) {
      var cjsModule, depName, ret, map, i,
        args = [],
        callbackType = typeof callback,
        usingExports;

      //Use name if no relName
      relName = relName || name;

      //Call the callback to define the module, if necessary.
      if (callbackType === 'undefined' || callbackType === 'function') {
        //Pull out the defined dependencies and pass the ordered
        //values to the callback.
        //Default to [require, exports, module] if no deps
        deps = !deps.length && callback.length ? ['require', 'exports', 'module'] : deps;
        for (i = 0; i < deps.length; i += 1) {
          map = makeMap(deps[i], relName);
          depName = map.f;

          //Fast path CommonJS standard dependencies.
          if (depName === "require") {
            args[i] = handlers.require(name);
          } else if (depName === "exports") {
            //CommonJS module spec 1.1
            args[i] = handlers.exports(name);
            usingExports = true;
          } else if (depName === "module") {
            //CommonJS module spec 1.1
            cjsModule = args[i] = handlers.module(name);
          } else if (hasProp(defined, depName) ||
            hasProp(waiting, depName) ||
            hasProp(defining, depName)) {
            args[i] = callDep(depName);
          } else if (map.p) {
            map.p.load(map.n, makeRequire(relName, true), makeLoad(depName), {});
            args[i] = defined[depName];
          } else {
            throw new Error(name + ' missing ' + depName);
          }
        }

        ret = callback ? callback.apply(defined[name], args) : undefined;

        if (name) {
          //If setting exports via "module" is in play,
          //favor that over return value and exports. After that,
          //favor a non-undefined return value over exports use.
          if (cjsModule && cjsModule.exports !== undef &&
            cjsModule.exports !== defined[name]) {
            defined[name] = cjsModule.exports;
          } else if (ret !== undef || !usingExports) {
            //Use the return value from the function.
            defined[name] = ret;
          }
        }
      } else if (name) {
        //May just be an object definition for the module. Only
        //worry about defining if have a module name.
        defined[name] = callback;
      }
    };

    requirejs = require = req = function (deps, callback, relName, forceSync, alt) {
      if (typeof deps === "string") {
        if (handlers[deps]) {
          //callback in this case is really relName
          return handlers[deps](callback);
        }
        //Just return the module wanted. In this scenario, the
        //deps arg is the module name, and second arg (if passed)
        //is just the relName.
        //Normalize module name, if it contains . or ..
        return callDep(makeMap(deps, callback).f);
      } else if (!deps.splice) {
        //deps is a config object, not an array.
        config = deps;
        if (config.deps) {
          req(config.deps, config.callback);
        }
        if (!callback) {
          return;
        }

        if (callback.splice) {
          //callback is an array, which means it is a dependency list.
          //Adjust args if there are dependencies
          deps = callback;
          callback = relName;
          relName = null;
        } else {
          deps = undef;
        }
      }

      //Support require(['a'])
      callback = callback || function () {};

      //If relName is a function, it is an errback handler,
      //so remove it.
      if (typeof relName === 'function') {
        relName = forceSync;
        forceSync = alt;
      }

      //Simulate async callback;
      if (forceSync) {
        main(undef, deps, callback, relName);
      } else {
        //Using a non-zero value because of concern for what old browsers
        //do, and latest browsers "upgrade" to 4 if lower value is used:
        //http://www.whatwg.org/specs/web-apps/current-work/multipage/timers.html#dom-windowtimers-settimeout:
        //If want a value immediately, use require('id') instead -- something
        //that works in almond on the global level, but not guaranteed and
        //unlikely to work in other AMD implementations.
        setTimeout(function () {
          main(undef, deps, callback, relName);
        }, 4);
      }

      return req;
    };

    /**
     * Just drops the config on the floor, but returns req in case
     * the config return value is used.
     */
    req.config = function (cfg) {
      return req(cfg);
    };

    /**
     * Expose module registry for debugging and tooling
     */
    requirejs._defined = defined;

    define = function (name, deps, callback) {
      if (typeof name !== 'string') {
        throw new Error('See almond README: incorrect module build, no module name');
      }

      //This module may not have dependencies
      if (!deps.splice) {
        //deps is not an array, so probably means
        //an object literal or factory function for
        //the value. Adjust args.
        callback = deps;
        deps = [];
      }

      if (!hasProp(defined, name) && !hasProp(waiting, name)) {
        waiting[name] = [name, deps, callback];
      }
    };

    define.amd = {
      jQuery: true
    };
  }());

  define("../node_modules/almond/almond", function(){});

//zebra-style class system, see zebkit.org
  define('struct_typesystem',[],function() {
    "use strict";

    var exports = {};

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
    };

    //parent is optional
    var handle_statics = function(cls, methods, parent) {
      for (var i=0; i<methods.length; i++) {
        var m = methods[i];

        if (m instanceof StaticMethod) {
          cls[m.func.name] = m.func;
        }
      }

      //inherit from parent too.
      //only inherit static methods added to parent with this module, though
      if (parent != undefined) {
        for (var k in parent) {
          var v = parent[k];

          if ((typeof v == "object"|| typeof v == "function")
            && "_is_static_method" in v && !(k in cls))
          {
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
        console.trace("Warning, constructor was not defined", methods);

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
      construct.__keystr__ = function() {
        return this.prototype.__prototypeid__;
      }

      construct.__parent__ = parent;
      construct.__statics__ = [];

      var getters = {};
      var setters = {};
      var getset = {};

      //handle getters/setters
      for (var i=0; i<methods.length; i++) {
        var f = methods[i];
        if (f instanceof ClassSetter) {
          setters[f.func.name] = f.func;
          getset[f.func.name] = 1;
        } else if (f instanceof ClassGetter) {
          getters[f.func.name] = f.func;
          getset[f.func.name] = 1;
        }
      }

      for (var k in getset) {
        var def = {
          enumerable   : true,
          configurable : true,
          get : getters[k],
          set : setters[k]
        }

        Object.defineProperty(construct.prototype, k, def);
      }

      handle_statics(construct, methods, parent);

      if (parent != undefined)
        construct.__parent__ = parent;

      for (var i=0; i<methods.length; i++) {
        var f = methods[i];

        if (f instanceof StaticMethod || f instanceof ClassGetter || f instanceof ClassSetter)
          continue;

        construct.prototype[f.name] = f;
      }

      return construct;
    }

    Class.getter = function(func) {
      return new ClassGetter(func);
    }
    Class.setter = function(func) {
      return new ClassSetter(func);
    }

    Class.static_method = function(func) {
      func._is_static_method = true;

      return new StaticMethod(func);
    }

    var EmptySlot = {};

    var set = exports.set = Class([
      function constructor(input) {
        this.items = [];
        this.keys = {};
        this.freelist = [];

        this.length = 0;

        if (input != undefined) {
          input.forEach(function(item) {
            this.add(item);
          }, this);
        }
      },

      function add(item) {
        var key = item.__keystr__();

        if (key in this.keys) return;

        if (this.freelist.length > 0) {
          var i = this.freelist.pop();

          this.keys[key] = i;
          items[i] = i;
        } else {
          var i = this.items.length;

          this.keys[key] = i;
          this.items.push(item);
        }

        this.length++;
      },

      function remove(item) {
        var key = item.__keystr__();

        if (!(key in this.keys)) {
          console.trace("Warning, item", item, "is not in set");
          return;
        }

        var i = this.keys[key];
        this.freelist.push(i);
        this.items[i] = EmptySlot;

        delete this.items[i];
        this.length--;
      },

      function has(item) {
        return item.__keystr__() in this.keys;
      },

      function forEach(func, thisvar) {
        for (var i=0; i<this.items.length; i++) {
          var item = this.items[i];

          if (item === EmptySlot)
            continue;

          thisvar != undefined ? func.call(thisvar, time) : func(item);
        }
      }
    ]);

    return exports;
  });

  define('struct_util',[
    "struct_typesystem"
  ], function(struct_typesystem) {
    "use strict";

    var Class = struct_typesystem.Class;

    var exports = {};
    var _o_basic_types = {"String" : 0, "Number" : 0, "Array" : 0, "Function" : 0};

    function is_obj_lit(obj) {
      if (obj.constructor.name in _o_basic_types)
        return false;

      if (obj.constructor.name == "Object")
        return true;
      if (obj.prototype == undefined)
        return true;

      return false;
    }

    function set_getkey(obj) {
      if (typeof obj == "number" || typeof obj == "boolean")
        return ""+obj;
      else if (typeof obj == "string")
        return obj;
      else
        return obj.__keystr__();
    }

    var set = exports.set = Class([
      function constructor(input) {
        this.items = [];
        this.keys = {};
        this.freelist = [];

        this.length = 0;

        if (input != undefined && input instanceof Array) {
          for (var i=0; i<input.length; i++) {
            this.add(input[i]);
          }
        } else if (input != undefined && input.forEach != undefined) {
          input.forEach(function(item) {
            this.add(input[i]);
          }, this);
        }
      },
      function add(obj) {
        var key = set_getkey(obj);
        if (key in this.keys) return;

        if (this.freelist.length > 0) {
          var i = this.freelist.pop();
          this.keys[key] = i;
          this.items[i] = obj;
        } else {
          this.keys[key] = this.items.length;
          this.items.push(obj);
        }

        this.length++;
      },
      function remove(obj, raise_error) {
        var key = set_getkey(obj);

        if (!(keystr in this.keys)) {
          if (raise_error)
            throw new Error("Object not in set");
          else
            console.trace("Object not in set", obj);
          return;
        }

        var i = this.keys[keystr];

        this.freelist.push(i);
        this.items[i] = undefined;

        delete this.keys[keystr];
        this.length--;
      },

      function has(obj) {
        return set_getkey(obj) in this.keys;
      },

      function forEach(func, thisvar) {
        for (var i=0; i<this.items.length; i++) {
          var item = this.items[i];

          if (item == undefined) continue;

          if (thisvar != undefined)
            func.call(thisvar, item);
          else
            func(item);
        }
      }
    ]);

    var IDGen = exports.IDGen = Class([
      function constructor() {
        this.cur_id = 1;
      },

      function gen_id() {
        return this.cur_id++;
      },

      Class.static_method(function fromSTRUCT(reader) {
        var ret = new IDGen();
        reader(ret);
        return ret;
      })
    ]);

    IDGen.STRUCT = [
      "struct_util.IDGen {",
      "  cur_id : int;",
      "}"
    ].join("\n");

    return exports;
  });

  define('struct_binpack',[
    "struct_typesystem", "struct_util"
  ], function(struct_typesystem, struct_util) {
    var exports = {};

    var Class = struct_typesystem.Class;

    var temp_dataview = new DataView(new ArrayBuffer(16));
    var uint8_view = new Uint8Array(temp_dataview.buffer);

    var unpack_context = exports.unpack_context = Class([
      function constructor() {
        this.i = 0;
      }
    ]);

    var pack_byte = exports.pack_byte = function(array, val) {
      array.push(val);
    }

    var pack_int = exports.pack_int = function(array, val) {
      temp_dataview.setInt32(array, val);

      for (var i=0; i<4; i++) {
        array.push(uint8_view[i]);
      }
    }

    exports.pack_float = function(array, val) {
      temp_dataview.setFloat32(array, val);

      for (var i=0; i<4; i++) {
        array.push(uint8_view[i]);
      }
    }

    exports.pack_double = function(array, val) {
      temp_dataview.setFloat64(array, val);

      for (var i=0; i<8; i++) {
        array.push(uint8_view[i]);
      }
    }

    exports.pack_short = function(array, val) {
      temp_dataview.setInt16(array, val);

      for (var i=0; i<2; i++) {
        array.push(uint8_view[i]);
      }
    }

    var encode_utf8 = exports.encode_utf8 = function encode_utf8(arr, str) {
      for (var i=0; i<str.length; i++) {
        var c = str.charCodeAt(i);

        while (c != 0) {
          var uc = c & 127;
          c = c>>7;

          if (c != 0)
            uc |= 128;

          arr.push(uc);
        }
      }
    }

    var decode_utf8 = exports.decode_utf8 = function decode_utf8(arr) {
      var str = ""
      var i = 0;

      while (i < arr.length) {
        var c = arr[i];
        var sum = c & 127;
        var j = 0;
        var lasti = i;

        while (i < arr.length && (c & 128)) {
          j += 7;
          i++;
          c = arr[i];

          c = (c&127)<<j;
          sum |= c;
        }

        if (sum == 0) break;

        str += String.fromCharCode(sum);
        i++;
      }

      return str;
    }

    var test_utf8 = exports.test_utf8 = function test_utf8()
    {
      var s = "a" + String.fromCharCode(8800) + "b";
      var arr = [];

      encode_utf8(arr, s);
      var s2 = decode_utf8(arr);

      if (s != s2) {
        throw new Error("UTF-8 encoding/decoding test failed");
      }

      return true;
    }

    function truncate_utf8(arr, maxlen)
    {
      var len = Math.min(arr.length, maxlen);

      var last_codepoint = 0;
      var last2 = 0;

      var incode = false;
      var i = 0;
      var code = 0;
      while (i < len) {
        incode = arr[i] & 128;

        if (!incode) {
          last2 = last_codepoint+1;
          last_codepoint = i+1;
        }

        i++;
      }

      if (last_codepoint < maxlen)
        arr.length = last_codepoint;
      else
        arr.length = last2;

      return arr;
    }

    var _static_sbuf_ss = new Array(2048);
    var pack_static_string = exports.pack_static_string = function pack_static_string(data, str, length)
    {
      if (length == undefined)
        throw new Error("'length' paremter is not optional for pack_static_string()");

      var arr = length < 2048 ? _static_sbuf_ss : new Array();
      arr.length = 0;

      encode_utf8(arr, str);
      truncate_utf8(arr, length);

      for (var i=0; i<length; i++) {
        if (i >= arr.length) {
          data.push(0);
        } else {
          data.push(arr[i]);
        }
      }
    }

    var _static_sbuf = new Array(32);

    /*strings are packed as 32-bit unicode codepoints*/
    var pack_string = exports.pack_string = function pack_string(data, str)
    {
      _static_sbuf.length = 0;
      encode_utf8(_static_sbuf, str);

      pack_int(data, _static_sbuf.length);

      for (var i=0; i<_static_sbuf.length; i++) {
        data.push(_static_sbuf[i]);
      }
    }

    var unpack_bytes = exports.unpack_bytes = function unpack_bytes(dview, uctx, len)
    {
      var ret = new DataView(dview.buffer.slice(uctx.i, uctx.i+len));
      uctx.i += len;

      return ret;
    }

    var unpack_byte = exports.unpack_byte = function(dview, uctx) {
      return dview.getUint8(uctx.i++);
    }

    var unpack_int = exports.unpack_int = function(dview, uctx) {
      uctx.i += 4;
      return dview.getInt32(uctx.i-4);
    }

    exports.unpack_float = function(dview, uctx) {
      uctx.i += 4;
      return dview.getFloat32(uctx.i-4);
    }

    exports.unpack_double = function(dview, uctx) {
      uctx.i += 8;
      return dview.getFloat64(uctx.i-8);
    }

    exports.unpack_short = function(dview, uctx) {
      uctx.i += 2;
      return dview.getInt16(uctx.i-2);
    }

    var _static_arr_us = new Array(32);
    exports.unpack_string = function(data, uctx) {
      var str = ""

      var slen = unpack_int(data, uctx);
      var arr = slen < 2048 ? _static_arr_us : new Array(slen);

      arr.length = slen;
      for (var i=0; i<slen; i++) {
        arr[i] = unpack_byte(data, uctx);
      }

      return decode_utf8(arr);
    }

    var _static_arr_uss = new Array(2048);
    exports.unpack_static_string = function unpack_static_string(data, uctx, length) {
      var str = "";

      if (length == undefined)
        throw new Error("'length' cannot be undefined in unpack_static_string()");

      var arr = length < 2048 ? _static_arr_uss : new Array(length);
      arr.length = 0;

      var done = false;
      for (var i=0; i<length; i++) {
        var c = unpack_byte(data, uctx);

        if (c == 0) {
          done = true;
        }

        if (!done && c != 0) {
          arr.push(c);
          //arr.length++;
        }
      }

      truncate_utf8(arr, length);
      return decode_utf8(arr);
    }

    return exports;
  });

  /*
   The lexical scanner in this module was inspired by PyPLY

   http://www.dabeaz.com/ply/ply.html
   */

  define('struct_parseutil',[
    "struct_typesystem", "struct_util"
  ], function(struct_typesystem, struct_util) {
    "use strict";
    var t;

    var Class = struct_typesystem.Class;

    var exports = {};
    exports.token = Class([
      function constructor(type, val, lexpos, lineno, lexer, parser) {
        this.type = type;
        this.value = val;
        this.lexpos = lexpos;
        this.lineno = lineno;
        this.lexer = lexer;
        this.parser = parser;
      },
      function toString() {
        if (this.value!=undefined)
          return "token(type="+this.type+", value='"+this.value+"')";
        else
          return "token(type="+this.type+")";
      }
    ]);

    exports.tokdef = Class([
      function constructor(name, regexpr, func) {
        this.name = name;
        this.re = regexpr;
        this.func = func;
      }
    ]);

    var PUTIL_ParseError = exports.PUTIL_ParseError = Class(Error, [
      function constructor(msg) {
        Error.call(this);
      }
    ]);

    exports.lexer = Class([
      function constructor(tokdef, errfunc) {
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
        this.states = {"__main__": [tokdef, errfunc]}
        this.statedata = 0;
      },
      function add_state(name, tokdef, errfunc) {
        if (errfunc==undefined) {
          errfunc = function(lexer) {
            return true;
          };
        }
        this.states[name] = [tokdef, errfunc];
      },
      function tok_int(name) {
      },
      function push_state(state, statedata) {
        this.statestack.push([state, statedata]);
        state = this.states[state];
        this.statedata = statedata;
        this.tokdef = state[0];
        this.errfunc = state[1];
      },
      function pop_state() {
        var item=this.statestack[this.statestack.length-1];
        var state=this.states[item[0]];
        this.tokdef = state[0];
        this.errfunc = state[1];
        this.statedata = item[1];
      },
      function input(str) {
        while (this.statestack.length>1) {
          this.pop_state();
        }
        this.lexdata = str;
        this.lexpos = 0;
        this.lineno = 0;
        this.tokens = new Array();
        this.peeked_tokens = [];
      },
      function error() {
        if (this.errfunc != undefined && !this.errfunc(this))
          return;

        console.log("Syntax error near line "+this.lineno);

        var next=Math.min(this.lexpos+8, this.lexdata.length);
        console.log("  "+this.lexdata.slice(this.lexpos, next));

        throw new PUTIL_ParseError("Parse error");
      },
      function peek() {
        var tok=this.next(true);
        if (tok==undefined)
          return undefined;
        this.peeked_tokens.push(tok);
        return tok;
      },
      function at_end() {
        return this.lexpos>=this.lexdata.length&&this.peeked_tokens.length==0;
      },

      //ignore_peek is optional, false
      function next(ignore_peek) {
        if (!ignore_peek && this.peeked_tokens.length>0) {
          var tok=this.peeked_tokens[0];
          this.peeked_tokens.shift();
          return tok;
        }

        if (this.lexpos>=this.lexdata.length)
          return undefined;

        var ts=this.tokdef;
        var tlen=ts.length;
        var lexdata=this.lexdata.slice(this.lexpos, this.lexdata.length);
        var results=[];

        for (var i=0; i<tlen; i++) {
          var t=ts[i];
          if (t.re==undefined)
            continue;
          var res=t.re.exec(lexdata);
          if (res!=null&&res!=undefined&&res.index==0) {
            results.push([t, res]);
          }
        }

        var max_res=0;
        var theres=undefined;
        for (var i=0; i<results.length; i++) {
          var res=results[i];
          if (res[1][0].length>max_res) {
            theres = res;
            max_res = res[1][0].length;
          }
        }

        if (theres==undefined) {
          this.error();
          return ;
        }

        var def=theres[0];
        var token=new exports.token(def.name, theres[1][0], this.lexpos, this.lineno, this, undefined);
        this.lexpos+=token.value.length;

        if (def.func) {
          token = def.func(token);
          if (token==undefined) {
            return this.next();
          }
        }

        return token;
      }
    ]);

    exports.parser = Class([
      function constructor(lexer, errfunc) {
        this.lexer = lexer;
        this.errfunc = errfunc;
        this.start = undefined;
      },
      function parse(data, err_on_unconsumed) {
        if (err_on_unconsumed==undefined)
          err_on_unconsumed = true;

        if (data!=undefined)
          this.lexer.input(data);

        var ret=this.start(this);

        if (err_on_unconsumed && !this.lexer.at_end() && this.lexer.next() != undefined) {
          this.error(undefined, "parser did not consume entire input");
        }
        return ret;
      },

      function input(data) {
        this.lexer.input(data);
      },

      function error(token, msg) {
        if (msg==undefined)
          msg = "";
        if (token==undefined)
          var estr="Parse error at end of input: "+msg;
        else
          estr = "Parse error at line "+(token.lineno+1)+": "+msg;
        var buf="1| ";
        var ld=this.lexer.lexdata;
        var l=1;
        for (var i=0; i<ld.length; i++) {
          var c=ld[i];
          if (c=='\n') {
            l++;
            buf+="\n"+l+"| ";
          }
          else {
            buf+=c;
          }
        }
        console.log("------------------");
        console.log(buf);
        console.log("==================");
        console.log(estr);
        if (this.errfunc&&!this.errfunc(token)) {
          return ;
        }
        throw new PUTIL_ParseError(estr);
      },
      function peek() {
        var tok=this.lexer.peek();
        if (tok!=undefined)
          tok.parser = this;
        return tok;
      },
      function next() {
        var tok=this.lexer.next();
        if (tok!=undefined)
          tok.parser = this;
        return tok;
      },
      function optional(type) {
        var tok=this.peek();
        if (tok==undefined)
          return false;
        if (tok.type==type) {
          this.next();
          return true;
        }
        return false;
      },
      function at_end() {
        return this.lexer.at_end();
      },
      function expect(type, msg) {
        var tok=this.next();
        if (msg==undefined)
          msg = type;
        if (tok==undefined||tok.type!=type) {
          this.error(tok, "Expected "+msg);
        }
        return tok.value;
      }
    ]);
    function test_parser() {
      var basic_types=new set(["int", "float", "double", "vec2", "vec3", "vec4", "mat4", "string"]);
      var reserved_tokens=new set(["int", "float", "double", "vec2", "vec3", "vec4", "mat4", "string", "static_string", "array"]);
      function tk(name, re, func) {
        return new exports.tokdef(name, re, func);
      }
      var tokens=[tk("ID", /[a-zA-Z]+[a-zA-Z0-9_]*/, function(t) {
        if (reserved_tokens.has(t.value)) {
          t.type = t.value.toUpperCase();
        }
        return t;
      }), tk("OPEN", /\{/), tk("CLOSE", /}/), tk("COLON", /:/), tk("JSCRIPT", /\|/, function(t) {
        var js="";
        var lexer=t.lexer;
        while (lexer.lexpos<lexer.lexdata.length) {
          var c=lexer.lexdata[lexer.lexpos];
          if (c=="\n")
            break;
          js+=c;
          lexer.lexpos++;
        }
        if (js.endsWith(";")) {
          js = js.slice(0, js.length-1);
          lexer.lexpos--;
        }
        t.value = js;
        return t;
      }), tk("LPARAM", /\(/), tk("RPARAM", /\)/), tk("COMMA", /,/), tk("NUM", /[0-9]/), tk("SEMI", /;/), tk("NEWLINE", /\n/, function(t) {
        t.lexer.lineno+=1;
      }), tk("SPACE", / |\t/, function(t) {
      })];
      var __iter_rt=__get_iter(reserved_tokens);
      var rt;
      while (1) {
        var __ival_rt=__iter_rt.next();
        if (__ival_rt.done) {
          break;
        }
        rt = __ival_rt.value;
        tokens.push(tk(rt.toUpperCase()));
      }
      var a="\n  Loop {\n    eid : int;\n    flag : int;\n    index : int;\n    type : int;\n\n    co : vec3;\n    no : vec3;\n    loop : int | eid(loop);\n    edges : array(e, int) | e.eid;\n\n    loops : array(Loop);\n  }\n  ";
      function errfunc(lexer) {
        return true;
      }
      var lex=new exports.lexer(tokens, errfunc);
      console.log("Testing lexical scanner...");
      lex.input(a);
      var token;
      while (token = lex.next()) {
        console.log(token.toString());
      }
      var parser=new exports.parser(lex);
      parser.input(a);
      function p_Array(p) {
        p.expect("ARRAY");
        p.expect("LPARAM");
        var arraytype=p_Type(p);
        var itername="";
        if (p.optional("COMMA")) {
          itername = arraytype;
          arraytype = p_Type(p);
        }
        p.expect("RPARAM");
        return {type: "array", data: {type: arraytype, iname: itername}}
      }
      function p_Type(p) {
        var tok=p.peek();
        if (tok.type=="ID") {
          p.next();
          return {type: "struct", data: "\""+tok.value+"\""}
        }
        else
        if (basic_types.has(tok.type.toLowerCase())) {
          p.next();
          return {type: tok.type.toLowerCase()}
        }
        else
        if (tok.type=="ARRAY") {
          return p_Array(p);
        }
        else {
          p.error(tok, "invalid type "+tok.type);
        }
      }
      function p_Field(p) {
        var field={}
        console.log("-----", p.peek().type);
        field.name = p.expect("ID", "struct field name");
        p.expect("COLON");
        field.type = p_Type(p);
        field.set = undefined;
        field.get = undefined;
        var tok=p.peek();
        if (tok.type=="JSCRIPT") {
          field.get = tok.value;
          p.next();
        }
        tok = p.peek();
        if (tok.type=="JSCRIPT") {
          field.set = tok.value;
          p.next();
        }
        p.expect("SEMI");
        return field;
      }
      function p_Struct(p) {
        var st={}
        st.name = p.expect("ID", "struct name");
        st.fields = [];
        p.expect("OPEN");
        while (1) {
          if (p.at_end()) {
            p.error(undefined);
          }
          else
          if (p.optional("CLOSE")) {
            break;
          }
          else {
            st.fields.push(p_Field(p));
          }
        }
        return st;
      }
      var ret=p_Struct(parser);
      console.log(JSON.stringify(ret));
    }

    return exports;
  });
  define('struct_parser',[
    "struct_parseutil", "struct_util"
  ], function(struct_parseutil, struct_util) {
    "use strict";

    var exports = {};

    //the discontinuous id's are to make sure
    //the version I originally wrote (which had a few application-specific types)
    //and this one do not become totally incompatible.
    var StructEnum = exports.StructEnum = {
      T_INT    : 0,
      T_FLOAT  : 1,
      T_DOUBLE : 2,
      T_STRING : 7,
      T_STATIC_STRING : 8,
      T_STRUCT : 9,
      T_TSTRUCT : 10,
      T_ARRAY   : 11,
      T_ITER    : 12,
      T_SHORT   : 13
    };

    var StructTypes = exports.StructTypes = {
      "int": StructEnum.T_INT,
      "float": StructEnum.T_FLOAT,
      "double": StructEnum.T_DOUBLE,
      "string": StructEnum.T_STRING,
      "static_string": StructEnum.T_STATIC_STRING,
      "struct": StructEnum.T_STRUCT,
      "abstract": StructEnum.T_TSTRUCT,
      "array": StructEnum.T_ARRAY,
      "iter": StructEnum.T_ITER,
      "short": StructEnum.T_SHORT
    };

    var StructTypeMap = exports.StructTypeMap = {};

    for (var k in StructTypes) {
      StructTypeMap[StructTypes[k]] = k;
    }

    function gen_tabstr(t) {
      var s="";
      for (var i=0; i<t; i++) {
        s+="  ";
      }
      return s;
    }

    function StructParser() {
      var basic_types=new struct_util.set([
        "int", "float", "double", "string", "short"
      ]);

      var reserved_tokens=new struct_util.set([
        "int", "float", "double", "string", "static_string", "array",
        "iter", "abstract", "short"
      ]);

      function tk(name, re, func) {
        return new struct_parseutil.tokdef(name, re, func);
      }

      var tokens=[tk("ID", /[a-zA-Z_]+[a-zA-Z0-9_\.]*/, function(t) {
        if (reserved_tokens.has(t.value)) {
          t.type = t.value.toUpperCase();
        }
        return t;
      }), tk("OPEN", /\{/), tk("EQUALS", /=/), tk("CLOSE", /}/), tk("COLON", /:/), tk("SOPEN", /\[/), tk("SCLOSE", /\]/), tk("JSCRIPT", /\|/, function(t) {
        var js="";
        var lexer=t.lexer;
        while (lexer.lexpos<lexer.lexdata.length) {
          var c=lexer.lexdata[lexer.lexpos];
          if (c=="\n")
            break;
          js+=c;
          lexer.lexpos++;
        }
        if (js.endsWith(";")) {
          js = js.slice(0, js.length-1);
          lexer.lexpos--;
        }
        t.value = js;
        return t;
      }), tk("LPARAM", /\(/), tk("RPARAM", /\)/), tk("COMMA", /,/), tk("NUM", /[0-9]+/), tk("SEMI", /;/), tk("NEWLINE", /\n/, function(t) {
        t.lexer.lineno+=1;
      }), tk("SPACE", / |\t/, function(t) {
      })
      ];

      reserved_tokens.forEach(function(rt) {
        tokens.push(tk(rt.toUpperCase()));
      });

      function errfunc(lexer) {
        return true;
      }

      var lex=new struct_parseutil.lexer(tokens, errfunc);
      var parser=new struct_parseutil.parser(lex);

      function p_Static_String(p) {
        p.expect("STATIC_STRING");
        p.expect("SOPEN");
        var num=p.expect("NUM");
        p.expect("SCLOSE");
        return {type: StructEnum.T_STATIC_STRING, data: {maxlength: num}}
      }

      function p_DataRef(p) {
        p.expect("DATAREF");
        p.expect("LPARAM");
        var tname=p.expect("ID");
        p.expect("RPARAM");
        return {type: StructEnum.T_DATAREF, data: tname}
      }

      function p_Array(p) {
        p.expect("ARRAY");
        p.expect("LPARAM");
        var arraytype=p_Type(p);

        var itername="";
        if (p.optional("COMMA")) {
          itername = arraytype.data.replace(/"/g, "");
          arraytype = p_Type(p);
        }

        p.expect("RPARAM");
        return {type: StructEnum.T_ARRAY, data: {type: arraytype, iname: itername}}
      }

      function p_Iter(p) {
        p.expect("ITER");
        p.expect("LPARAM");
        var arraytype=p_Type(p);
        var itername="";

        if (p.optional("COMMA")) {
          itername = arraytype.data.replace(/"/g, "");
          arraytype = p_Type(p);
        }

        p.expect("RPARAM");
        return {type: StructEnum.T_ITER, data: {type: arraytype, iname: itername}}
      }

      function p_Abstract(p) {
        p.expect("ABSTRACT");
        p.expect("LPARAM");
        var type=p.expect("ID");
        p.expect("RPARAM");
        return {type: StructEnum.T_TSTRUCT, data: type}
      }

      function p_Type(p) {
        var tok=p.peek();

        if (tok.type=="ID") {
          p.next();
          return {type: StructEnum.T_STRUCT, data: tok.value}
        } else if (basic_types.has(tok.type.toLowerCase())) {
          p.next();
          return {type: StructTypes[tok.type.toLowerCase()]}
        } else if (tok.type=="ARRAY") {
          return p_Array(p);
        } else if (tok.type=="ITER") {
          return p_Iter(p);
        } else if (tok.type=="STATIC_STRING") {
          return p_Static_String(p);
        } else if (tok.type=="ABSTRACT") {
          return p_Abstract(p);
        } else if (tok.type=="DATAREF") {
          return p_DataRef(p);
        } else {
          p.error(tok, "invalid type "+tok.type);
        }
      }

      function p_Field(p) {
        var field={}

        field.name = p.expect("ID", "struct field name");
        p.expect("COLON");

        field.type = p_Type(p);
        field.set = undefined;
        field.get = undefined;

        var tok=p.peek();
        if (tok.type=="JSCRIPT") {
          field.get = tok.value;
          p.next();
        }

        tok = p.peek();
        if (tok.type=="JSCRIPT") {
          field.set = tok.value;
          p.next();
        }

        p.expect("SEMI");
        return field;
      }

      function p_Struct(p) {
        var st={}

        st.name = p.expect("ID", "struct name");

        st.fields = [];
        st.id = -1;
        var tok=p.peek();
        var id=-1;
        if (tok.type=="ID"&&tok.value=="id") {
          p.next();
          p.expect("EQUALS");
          st.id = p.expect("NUM");
        }

        p.expect("OPEN");
        while (1) {
          if (p.at_end()) {
            p.error(undefined);
          }
          else
          if (p.optional("CLOSE")) {
            break;
          }
          else {
            st.fields.push(p_Field(p));
          }
        }
        return st;
      }
      parser.start = p_Struct;
      return parser;
    }

    exports.struct_parse = StructParser();

    return exports;
  });

  define('nstructjs',[
    "struct_util", "struct_binpack", "struct_parseutil", "struct_typesystem", "struct_parser"
  ], function(struct_util, struct_binpack, struct_parseutil, struct_typesystem, struct_parser) {
    "use strict";

    var exports = {};

    var StructTypeMap = struct_parser.StructTypeMap;
    var StructTypes = struct_parser.StructTypes;
    var Class = struct_typesystem.Class;

    exports.binpack = struct_binpack;
    exports.util = struct_util;
    exports.typesystem = struct_typesystem;
    exports.parseutil = struct_parseutil;
    exports.parser = struct_parser;

    var struct_parse = struct_parser.struct_parse;
    var StructEnum = struct_parser.StructEnum;

    var _static_envcode_null="";
    window.debug_struct=0;
    var packdebug_tablevel=0;

    function gen_tabstr(tot) {
      var ret = "";

      for (var i=0; i<tot; i++) {
        ret += " ";
      }

      return ret;
    }

    if (1||debug_struct) {
      var packer_debug=function(msg) {
        if (!debug_struct) {
          return;
        }

        if (msg!=undefined) {
          var t=gen_tabstr(packdebug_tablevel);
          console.log(t+msg);
        } else {
          console.log("Warning: undefined msg");
        }
      };
      var packer_debug_start=function(funcname) {
        if (!debug_struct) {
          return;
        }

        packer_debug("Start "+funcname);
        packdebug_tablevel++;
      };

      var packer_debug_end=function(funcname) {
        packdebug_tablevel--;
        packer_debug("Leave "+funcname);
      };
    }
    else {
      var packer_debug=function() {};
      var packer_debug_start=function() {};
      var packer_debug_end=function() {};
    }

    var _ws_env=[[undefined, undefined]];

    var pack_callbacks=[
      function pack_int(data, val) {
        packer_debug("int "+val);

        struct_binpack.pack_int(data, val);
      }, function pack_float(data, val) {
        packer_debug("float "+val);

        struct_binpack.pack_float(data, val);
      }, function pack_double(data, val) {
        packer_debug("double "+val);

        struct_binpack.pack_double(data, val);
      }, 0, 0, 0, 0,
      function pack_string(data, val) {
        if (val==undefined)
          val = "";
        packer_debug("string: "+val);
        packer_debug("int "+val.length);

        struct_binpack.pack_string(data, val);
      }, function pack_static_string(data, val, obj, thestruct, field, type) {
        if (val==undefined)
          val = "";
        packer_debug("static_string: '"+val+"' length="+type.data.maxlength);

        struct_binpack.pack_static_string(data, val, type.data.maxlength);
      }, function pack_struct(data, val, obj, thestruct, field, type) {
        packer_debug_start("struct "+type.data);

        thestruct.write_struct(data, val, thestruct.get_struct(type.data));

        packer_debug_end("struct");
      }, function pack_tstruct(data, val, obj, thestruct, field, type) {
        var cls=thestruct.get_struct_cls(type.data);
        var stt=thestruct.get_struct(type.data);

        //make sure inheritance is correct
        if (val.constructor.structName!=type.data && (val instanceof cls)) {
          if (DEBUG.Struct) {
            console.log(val.constructor.structName+" inherits from "+cls.structName);
          }
          stt = thestruct.get_struct(val.constructor.structName);
        } else if (val.constructor.structName==type.data) {
          stt = thestruct.get_struct(type.data);
        } else {
          console.trace();
          throw new Error("Bad struct "+val.constructor.structName+" passed to write_struct");
        }

        if (stt.id==0) {
        }

        packer_debug_start("tstruct '"+stt.name+"'");
        packer_debug("int "+stt.id);

        struct_binpack.pack_int(data, stt.id);
        thestruct.write_struct(data, val, stt);

        packer_debug_end("tstruct");
      }, function pack_array(data, val, obj, thestruct, field, type) {
        packer_debug_start("array");

        if (val==undefined) {
          console.trace();
          console.log("Undefined array fed to struct struct packer!");
          console.log("Field: ", field);
          console.log("Type: ", type);
          console.log("");
          packer_debug("int 0");
          struct_binpack.pack_int(data, 0);
          return ;
        }

        packer_debug("int "+val.length);
        struct_binpack.pack_int(data, val.length);

        var d=type.data;

        var itername = d.iname;
        var type2 = d.type;

        var env=_ws_env;
        for (var i=0; i<val.length; i++) {
          var val2=val[i];
          if (itername!=""&&itername!=undefined&&field.get) {
            env[0][0] = itername;
            env[0][1] = val2;
            val2 = thestruct._env_call(field.get, obj, env);
          }
          var f2={type: type2, get: undefined, set: undefined};
          do_pack(data, val2, obj, thestruct, f2, type2);
        }
        packer_debug_end("array");
      }, function pack_iter(data, val, obj, thestruct, field, type) {
        //this was originally implemented to use ES6 iterators.

        packer_debug_start("iter");

        if (val==undefined || val.forEach == undefined) {
          console.trace();
          console.log("Undefined iterable list fed to struct struct packer!", val);
          console.log("Field: ", field);
          console.log("Type: ", type);
          console.log("");
          packer_debug("int 0");
          struct_binpack.pack_int(data, 0);
          return ;
        }

        var len  = 0.0;
        val.forEach(function(val2) {
          len++;
        }, this);

        packer_debug("int "+len);
        struct_binpack.pack_int(data, len);

        var d=type.data, itername=d.iname, type2=d.type;
        var env=_ws_env;

        var i = 0;
        val.forEach(function(val2) {
          if (i >= len) {
            console.trace("Warning: iterator returned different length of list!", val, i);
            return;
          }

          if (itername!=""&&itername!=undefined&&field.get) {
            env[0][0] = itername;
            env[0][1] = val2;
            val2 = thestruct._env_call(field.get, obj, env);
          }

          var f2={type: type2, get: undefined, set: undefined};
          do_pack(data, val2, obj, thestruct, f2, type2);

          i++;
        }, this);

        packer_debug_end("iter");
      }, function pack_short(data, val) {
        packer_debug("short "+val);

        struct_binpack.pack_short(data, Math.floor(val));
      }];

    function do_pack(data, val, obj, thestruct, field, type) {
      pack_callbacks[field.type.type](data, val, obj, thestruct, field, type);
    }

    /**
     Main STRUCT management class.  Defines nstructjs.manger.

     @constructor
     */
    var STRUCT=exports.STRUCT = Class([
      function constructor() {
        this.idgen = new struct_util.IDGen();

        this.structs = {}
        this.struct_cls = {}
        this.struct_ids = {}

        this.compiled_code = {}
        this.null_natives = {}

        function define_null_native(name, cls) {
          var obj={name: name, prototype: Object.create(Object.prototype)}
          obj.constructor = obj;
          obj.STRUCT = name+" {\n  }\n";
          obj.fromSTRUCT = function(reader) {
            var ob={}
            reader(ob);
            return ob;
          }

          var stt=struct_parse.parse(obj.STRUCT);

          stt.id = this.idgen.gen_id();

          this.structs[name] = stt;
          this.struct_cls[name] = cls;
          this.struct_ids[stt.id] = stt;

          this.null_natives[name] = 1;
        }

        define_null_native.call(this, "Object", Object);
      },

      function forEach(func, thisvar) {
        for (var k in this.structs) {
          var stt = this.structs[k];

          if (thisvar != undefined)
            func.call(thisvar, stt);
          else
            func(stt);
        }
      },

      //defined_classes is an array of class constructors
      //with STRUCT scripts
      function parse_structs(buf, defined_classes) {
        console.log(buf);

        if (defined_classes == undefined) {
          defined_classes = [];
          for (var k in exports.manager.struct_cls) {
            defined_classes.push(exports.manager.struct_cls[k]);
          }
        }

        var clsmap={}

        for (var i=0; i<defined_classes.length; i++) {
          var cls = defined_classes[i];

          if (cls.structName == undefined && cls.STRUCT != undefined) {
            var stt=struct_parse.parse(cls.STRUCT.trim());
            cls.structName = stt.name;
          } else if (cls.structName == undefined && cls.name != "Object") {
            console.log("Warning, bad class in registered class list", cls.name, cls);
            continue;
          }

          clsmap[cls.structName] = defined_classes[i];
        }

        struct_parse.input(buf);

        while (!struct_parse.at_end()) {
          var stt=struct_parse.parse(undefined, false);

          if (!(stt.name in clsmap)) {
            if (!(stt.name in this.null_natives))
              console.log("WARNING: struct "+stt.name+" is missing from class list.");

            var dummy=Object.create(Object.prototype);
            dummy.prototype = Object.create(Object.prototype);

            dummy.STRUCT = STRUCT.fmt_struct(stt);
            dummy.fromSTRUCT = function(reader) {
              var obj={}
              reader(obj);
              return obj;
            };

            dummy.structName = stt.name;
            dummy.prototype.structName = dummy.name;
            dummy.prototype.constructor = dummy;

            this.struct_cls[dummy.structName] = dummy;
            this.struct_cls[dummy.structName] = stt;

            if (stt.id!=-1)
              this.struct_ids[stt.id] = stt;
          } else {
            this.struct_cls[stt.name] = clsmap[stt.name];
            this.structs[stt.name] = stt;

            if (stt.id!=-1)
              this.struct_ids[stt.id] = stt;
          }

          var tok=struct_parse.peek();
          while (tok!=undefined&&(tok.value=="\n" || tok.value=="\r" || tok.value=="\t" || tok.value==" ")) {
            tok = struct_parse.peek();
          }
        }
      },

      function add_class(cls) {
        var stt=struct_parse.parse(cls.STRUCT);

        cls.structName = stt.name;

        if (stt.id==-1)
          stt.id = this.idgen.gen_id();

        this.structs[cls.structName] = stt;
        this.struct_cls[cls.structName] = cls;
        this.struct_ids[stt.id] = stt;
      },

      function get_struct_id(id) {
        return this.struct_ids[id];
      },

      function get_struct(name) {
        if (!(name in this.structs)) {
          console.trace();
          throw new Error("Unknown struct "+name);
        }
        return this.structs[name];
      },

      function get_struct_cls(name) {
        if (!(name in this.struct_cls)) {
          console.trace();
          throw new Error("Unknown struct "+name);
        }
        return this.struct_cls[name];
      },

      Class.static_method(function inherit(child, parent) {
        var stt=struct_parse.parse(parent.STRUCT);
        var code=child.structName+"{\n";
        code+=STRUCT.fmt_struct(stt, true);
        return code;
      }),

      Class.static_method(function chain_fromSTRUCT(cls, reader) {
        var proto=cls.prototype;
        var parent=cls.prototype.prototype.constructor;

        var obj=parent.fromSTRUCT(reader);
        var keys=Object.keys(proto);

        for (var i=0; i<keys.length; i++) {
          var k=keys[i];
          if (k=="__proto__")
            continue;
          obj[k] = proto[k];
        }

        if (proto.toString!=Object.prototype.toString)
          obj.toString = proto.toString;

        return obj;
      }),

      Class.static_method(function fmt_struct(stt, internal_only, no_helper_js) {
        if (internal_only==undefined)
          internal_only = false;
        if (no_helper_js==undefined)
          no_helper_js = false;

        var s="";
        if (!internal_only) {
          s+=stt.name;
          if (stt.id!=-1)
            s+=" id="+stt.id;
          s+=" {\n";
        }
        var tab="  ";
        function fmt_type(type) {
          if (type.type==StructEnum.T_ARRAY||type.type==StructEnum.T_ITER) {
            if (type.data.iname!=""&&type.data.iname!=undefined) {
              return "array("+type.data.iname+", "+fmt_type(type.data.type)+")";
            }
            else {
              return "array("+fmt_type(type.data.type)+")";
            }
          } else  if (type.type==StructEnum.T_STATIC_STRING) {
            return "static_string["+type.data.maxlength+"]";
          } else if (type.type==StructEnum.T_STRUCT) {
            return type.data;
          } else if (type.type==StructEnum.T_TSTRUCT) {
            return "abstract("+type.data+")";
          } else {
            return StructTypeMap[type.type];
          }
        }

        var fields=stt.fields;
        for (var i=0; i<fields.length; i++) {
          var f=fields[i];
          s += tab + f.name+" : "+fmt_type(f.type);
          if (!no_helper_js&&f.get!=undefined) {
            s += " | "+f.get.trim();
          }
          s+=";\n";
        }
        if (!internal_only)
          s+="}";
        return s;
      }),

      function _env_call(code, obj, env) {
        var envcode=_static_envcode_null;
        if (env!=undefined) {
          envcode = "";
          for (var i=0; i<env.length; i++) {
            envcode = "var "+env[i][0]+" = env["+i.toString()+"][1];\n"+envcode;
          }
        }
        var fullcode="";
        if (envcode!==_static_envcode_null)
          fullcode = envcode+code;
        else
          fullcode = code;
        var func;
        if (!(fullcode in this.compiled_code)) {
          var code2="func = function(obj, env) { "+envcode+"return "+code+"}";
          try {
            eval(code2);
          }
          catch (err) {
            console.log(code2);
            console.log(" ");
            print_stack(err);
            throw err;
          }
          this.compiled_code[fullcode] = func;
        }
        else {
          func = this.compiled_code[fullcode];
        }
        try {
          return func(obj, env);
        }
        catch (err) {
          var code2="func = function(obj, env) { "+envcode+"return "+code+"}";
          console.log(code2);
          console.log(" ");
          print_stack(err);
          throw err;
        }
      },

      function write_struct(data, obj, stt) {
        function use_helper_js(field) {
          if (field.type.type==StructEnum.T_ARRAY||field.type.type==StructEnum.T_ITER) {
            return field.type.data.iname==undefined||field.type.data.iname=="";
          }
          return true;
        }

        var fields=stt.fields;
        var thestruct=this;
        for (var i=0; i<fields.length; i++) {
          var f=fields[i];
          var t1=f.type;
          var t2=t1.type;

          if (use_helper_js(f)) {
            var val;
            var type=t2;
            if (f.get!=undefined) {
              val = thestruct._env_call(f.get, obj);
            }
            else {
              val = obj[f.name];
            }
            do_pack(data, val, obj, thestruct, f, t1);
          }
          else {
            var val=obj[f.name];
            do_pack(data, val, obj, thestruct, f, t1);
          }
        }
      },

      function write_object(data, obj) {
        var cls=obj.constructor.structName;
        var stt=this.get_struct(cls);

        this.write_struct(data, obj, stt);
      },

      function read_object(data, cls, uctx) {
        var stt=this.structs[cls.structName];

        if (uctx==undefined) {
          uctx = new struct_binpack.unpack_context();
          packer_debug("\n\n=Begin reading=");
        }
        var thestruct=this;

        var unpack_funcs=[
          function t_int(type) { //int
            var ret=struct_binpack.unpack_int(data, uctx);

            packer_debug("-int "+ret);

            return ret;
          }, function t_float(type) {
            var ret=struct_binpack.unpack_float(data, uctx);

            packer_debug("-float "+ret);

            return ret;
          }, function t_double(type) {
            var ret=struct_binpack.unpack_double(data, uctx);

            packer_debug("-double "+ret);

            return ret;
          }, 0, 0, 0, 0,
          function t_string(type) {
            packer_debug_start("string");

            var s=struct_binpack.unpack_string(data, uctx);

            packer_debug("data: '"+s+"'");
            packer_debug_end("string");
            return s;
          }, function t_static_string(type) {
            packer_debug_start("static_string");

            var s=struct_binpack.unpack_static_string(data, uctx, type.data.maxlength);

            packer_debug("data: '"+s+"'");
            packer_debug_end("static_string");

            return s;
          }, function t_struct(type) {
            packer_debug_start("struct "+type.data);

            var cls2=thestruct.get_struct_cls(type.data);
            var ret=thestruct.read_object(data, cls2, uctx);

            packer_debug_end("struct");
            return ret;
          }, function t_tstruct(type) {
            packer_debug_start("tstruct");

            var id=struct_binpack.unpack_int(data, uctx);

            packer_debug("-int "+id);
            if (!(id in thestruct.struct_ids)) {
              packer_debug("struct id: "+id);
              console.trace();
              console.log(id);
              console.log(thestruct.struct_ids);
              packer_debug_end("tstruct");
              throw new Error("Unknown struct type "+id+".");
            }

            var cls2=thestruct.get_struct_id(id);

            packer_debug("struct name: "+cls2.name);
            var sname = cls2.name;

            var cls2a = cls2;
            cls2 = thestruct.struct_cls[cls2.name];

            if (cls2 === undefined) {
              console.log("failed to find class constructor for", sname, cls2a);
              throw new Error("bad class");
            }

            var ret=thestruct.read_object(data, cls2, uctx);

            packer_debug_end("tstruct");
            return ret;
          }, function t_array(type) {
            packer_debug_start("array");

            var len=struct_binpack.unpack_int(data, uctx);
            packer_debug("-int "+len);

            var arr=new Array(len);
            for (var i=0; i<len; i++) {
              arr[i] = unpack_field(type.data.type);
            }

            packer_debug_end("array");
            return arr;
          }, function t_iter(type) {
            packer_debug_start("iter");

            var len=struct_binpack.unpack_int(data, uctx);
            packer_debug("-int "+len);

            var arr=new Array(len);
            for (var i=0; i<len; i++) {
              arr[i] = unpack_field(type.data.type);
            }

            packer_debug_end("iter");
            return arr;
          }, function t_short(type) { //int
            var ret=struct_binpack.unpack_short(data, uctx);

            packer_debug("-short "+ret);

            return ret;
          }
        ];

        function unpack_field(type) {
          return unpack_funcs[type.type](type);
        }

        var load_called = 0;
        function load(obj) {
          load_called++;

          var fields=stt.fields;
          var flen=fields.length;

          for (var i=0; i<flen; i++) {
            var f=fields[i];
            var val=unpack_field(f.type);
            obj[f.name] = val;
          }
        }

        if (cls.fromSTRUCT === undefined) {
          console.log(cls.structName, cls);
          throw new Error ("no fromSTRUCT for " + cls.structName + ":" + cls);
        }

        var ret = cls.fromSTRUCT(load);
        if (load_called != 1) {
          throw new Error("fromSTRUCT called reader() " + load_called + " times; should be 1");
        }
        return ret;
      }
    ]);

    //main struct script manager
    var manager = exports.manager = new STRUCT();

    var write_scripts = exports.write_scripts = function write_scripts() {
      var buf="";

      manager.forEach(function(stt) {
        buf+=STRUCT.fmt_struct(stt, false, true)+"\n";
      });

      var buf2=buf;
      buf = "";

      for (var i=0; i<buf2.length; i++) {
        var c=buf2[i];
        if (c=="\n") {
          buf+="\n";
          var i2=i;
          while (i<buf2.length&&(buf2[i]==" "||buf2[i]=="\t"||buf2[i]=="\n")) {
            i++;
          }
          if (i!=i2)
            i--;
        }
        else {
          buf+=c;
        }
      }

      return buf;
    }

    return exports;
  });


  require(["nstructjs"]);
  //The modules for your project will be inlined above
  //this snippet. Ask almond to synchronously require the
  //module value for 'main' here and return it as the
  //value to use for the public API for the built file.
  return require('nstructjs');
}));