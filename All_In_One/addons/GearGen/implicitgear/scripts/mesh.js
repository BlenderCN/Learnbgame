var _mesh = undefined;

define([
  "util", "vectormath", "math"
], function(util, vectormath, math) {
  'use strict';
  
  var exports = _mesh = {};

  //var patch_canvas2d = canvas_patch.patch_canvas2d;
  var Vector2 = vectormath.Vector2, Vector3 = vectormath.Vector3;
  var Vector4 = vectormath.Vector4, Matrix4 = vectormath.Matrix4;
  
  var MeshTypes = exports.MeshTypes = {
    VERTEX : 1,
    EDGE   : 2
  };
  
  var MeshFlags = exports.MeshFlags = {
    SELECT : 1,
    HIDE   : 2
  };
  
  var Element = exports.Element = class Element {
    constructor(type) {
      this.type = type;
      this.flag = this.index = 0;
      this.tag = 0;
      this.eid = -1;
    }
    
    [Symbol.keystr]() {
      return this.eid;
    }
    
    toJSON() {
      return {
        type  : this.type,
        flag  : this.flag,
        index : this.index,
        eid   : this.eid
      };
    }
    
    loadJSON(obj) {
      this.type = obj.type;
      this.flag = obj.flag;
      this.index = obj.index;
      this.eid = obj.eid;
      
      return this;
    }
  }
  
  //has Vector3 mixin
  var Vertex = exports.Vertex = class Vertex extends Element {
    constructor(co) {
      super(MeshTypes.VERTEX);
      this.initVector3();
      
      if (co !== undefined) {
        this.load(co);
      }
      
      this.edges = [];
    }
    
    toJSON() {
      var edges = [];
      for (var e of this.edges) {
        edges.push(e.eid);
      }
      
      return util.merge(super.toJSON(), {
        0 : this[0],
        1 : this[1],
        2 : this[2],
        edges : edges
      });
    }

    otherEdge(e) {
      if (this.edges.length != 2) {
        throw new Error ("otherEdge only works on 2-valence vertices");
      }

      if (e === this.edges[0])
        return this.edges[1];
      else if (e === this.edges[1])
        return this.edges[0];
    }

    loadJSON(obj) {
      super.loadJSON(obj);
      
      this.edges = obj.edges;
      this[0] = obj[0];
      this[1] = obj[1];
      this[2] = obj[2];
      
      return this;
    }
  }
  
  util.mixin(Vertex, Vector3);
  
  var _evaluate_vs = util.cachering.fromConstructor(Vector3, 64);
  
  var Edge = exports.Edge = class Edge extends Element {
    constructor() {
      super(MeshTypes.EDGE);
      
      this.v1 = this.v2 = undefined;
    }
    
    evaluate(t) {
      return _evaluate_vs.next().load(this.v1).interp(this.v2, t);
    }
    
    derivative(t) {
      var df = 0.0001;
      var a = this.evaluate(t-df);
      var b = this.evaluate(t+df);
      
      return b.sub(a).mulScalar(0.5/df);
    }
    
    derivative2(t) {
      var df = 0.0001;
      var a = this.derivative(t-df);
      var b = this.derivative(t+df);
      
      return b.sub(a).mulScalar(0.5/df);
    }
    
    curvature(t) {
      dv1 = this.derivative(t);
      dv2 = this.derivative2(t);
      
      return (dv1[0]*dv2[1] - dv1[1]*dv2[0]) / Math.sqrt(dv2, 2.0/3.0);
    }
    
    toJSON() {
      return util.merge(super.toJSON(), {
        v1 : this.v1.eid,
        v2 : this.v2.eid
      });
    }
    
    loadJSON(obj) {
      super.loadJSON(obj);
      
      this.v1 = obj.v1;
      this.v2 = obj.v2;
      
      return this;
    }
    
    otherVertex(v) {
      if (v === undefined)
        throw new Error("v cannot be undefined in Edge.prototype.otherVertex()");
      
      if (v === this.v1)
        return this.v2;
      if (v === this.v2)
        return this.v1;
      
      throw new Error("vertex " + v.eid + " not in edge");
    }
  };
  
  var ElementArray = exports.ElementArray = class ElementArray extends Array {
    constructor(type) {
      super();
      
      this.type = type;
      this.selected = new util.set();
      this.on_selected = undefined;
      this.highlight = this.active = undefined;
    }
    
    toJSON() {
      var arr = [];
      for (var i=0; i<this.length; i++) {
        arr.push(this[i]);
      }
      
      var sel = [];
      for (var v of this.selected) {
        sel.push(v.eid);
      }
      
      return {
        type      : this.type,
        array     : arr,
        selected  : sel,
        active    : this.active !== undefined ? this.active.eid : -1,
        highlight : this.highlight !== undefined ? this.highlight.eid : -1
      };
    }
    
    loadJSON(obj) {
      this.length = 0;
      this.selected = new util.set();
      this.active = this.highlight = undefined;
      this.type = obj.type;
      
      for (var e of obj.array) {
        var e2 = undefined;
        
        switch (e.type) {
          case MeshTypes.VERTEX:
            e2 = new Vertex();
            break;
          case MeshTypes.EDGE:
            e2 = new Edge();
            break;
          default:
            console.log(e);
            throw new Error("bad element " + e);
        }
        
        e2.loadJSON(e);
        super.push(e2);
        if (e2.flag & MeshFlags.SELECT) {
          this.selected.add(e2);
        }
        
        if (e2.eid == obj.active) {
          this.active = e2;
        } else if (e2.eid == obj.highlight) {
          this.highlight = e2;
        }
      }
    }
    
    push(v) {
      super.push(v);
      
      if (v.flag & MeshFlags.SELECT) {
        this.selected.add(v);
      }
      
      return this;
    }
    
    remove(v) {
      if (this.selected.has(v)) {
        this.selected.remove(v);
      }
      
      if (this.active === v)
        this.active = undefined;
      if (this.highlight === v)
        this.highlight = undefined;
      
      super.remove(v);
      
      return this;
    }
    
    selectNone() {
      for (var e of this) {
        this.setSelect(e, false);
      }
    }
    
    selectAll() {
      for (var e of this) {
        this.setSelect(e, true);
      }
    }
    
    setSelect(v, state) {
      if (state) {
        v.flag |= MeshFlags.SELECT;
        
        this.selected.add(v);
      } else {
        v.flag &= ~MeshFlags.SELECT;
        
        this.selected.remove(v, true);
      }
      
      return this;
    }
  };
  
  var Mesh = exports.Mesh = class Mesh {
    constructor() {
      this.eidgen = new util.IDGen();
      this.eidmap = {};
      
      this.verts = new ElementArray(MeshTypes.VERTEX);
      this.edges = new ElementArray(MeshTypes.EDGE);
    }
    
    _element_init(e) {
      e.eid = this.eidgen.next();
      this.eidmap[e.eid] = e;
    }
    
    makeVertex(co) {
      var v = new Vertex(co);
      
      this._element_init(v);
      this.verts.push(v);
      
      return v;
    }
    
    getEdge(v1, v2) {
      for (var e of v1.edges) {
        if (e.otherVertex(v1) === v2)
          return e;
      }
      
      return undefined;
    }
    
    makeEdge(v1, v2) {
      var e = new Edge();
      
      e.v1 = v1;
      e.v2 = v2;
      
      v1.edges.push(e);
      v2.edges.push(e);
      
      this._element_init(e);
      this.edges.push(e);
      
      return e;
    }
    
    killVertex(v) {
      if (v.eid === -1) {
        console.trace("Warning: vertex", v.eid, "already freed", v);
        return;
      }
      
      var _i = 0;
      while (v.edges.length > 0 && _i++ < 10000) {
        this.killEdge(v.edges[0]);
      }
      
      if (_i >= 10000) {
        console.trace("mesh integrity warning, infinite loop detected in killVertex");
      }
      
      delete this.eidmap[v.eid];
      this.verts.remove(v);
      v.eid = -1;
    }
    
    killEdge(e) {
      if (e.eid == -1) {
        console.trace("Warning: edge", e.eid, "already freed", e);
        return;
      }
      
      delete this.eidmap[e.eid];
      this.edges.remove(e);
      
      e.eid = -1;
      
      e.v1.edges.remove(e);
      e.v2.edges.remove(e);
    }
    
    selectFlush(selmode) {
      if (selmode & MeshTypes.VERTEX) {
        this.edges.selectNone();
        var set_active = this.edges.active === undefined;
        set_active = set_active || !((this.edges.active.v1.flag|this.edges.active.v2.flag) & MeshFlags.SELECT);
        
        for (var e of this.edges) {
          if ((e.v1.flag & MeshFlags.SELECT) && (e.v2.flag & MeshFlags.SELECT)) {
            this.edges.setSelect(e, true);
            
            if (set_active) {
              this.edges.active = e;
            }
          }
        }
      } else if (selmode & MeshTypes.EDGE) {
        this.verts.selectNone();
        
        for (var v of this.verts) {
          for (var e of v.edges) {
            if (e.flag & MeshFlags.SELECT) {
              this.verts.setSelect(v, true);
              break;
            }
          }
        }
      }
    }
    
    splitEdge(e, t) {
      t = t === undefined ? 0.5 : t;
      
      var nv = this.makeVertex(e.v1).interp(e.v2, t);
      var ne = this.makeEdge(nv, e.v2);
      
      e.v2.edges.remove(e);
      e.v2 = nv;
      nv.edges.push(e);
      
      if (e.flag & MeshFlags.SELECT) {
        this.edges.setSelect(ne, true);
        this.verts.setSelect(nv, true);
      }
      
      return [ne, nv];
    }
    
    dissolveVertex(v) {
      if (v.edges.length != 2) {
        throw new Error("can't dissolve vertex with more than two edges");
      }
      
      var e1 = v.edges[0], e2 = v.edges[1];
      var v1 = e1.otherVertex(v), v2 = e2.otherVertex(v);
      
      var flag = (e1.flag | e2.flag) & ~MeshFlags.HIDE;
      
      this.killVertex(v);
      var e3 = this.makeEdge(v1, v2);
      
      if (flag & MeshFlags.SELECT) {
        this.edges.setSelect(e3, true);
      }
      
      e3.flag |= flag;
    }
    
    getList(type) {
      if (type == MeshTypes.VERTEX)
        return this.verts;
      else if (type == MeshTypes.EDGE)
        return this.edges;
    }
    
    toJSON() {
      return {
        eidgen : this.eidgen,
        verts  : this.verts,
        edges  : this.edges
      };
    }
    
    loadJSON(obj) {
      this.verts = new ElementArray();
      this.edges = new ElementArray();
      this.eidgen.loadJSON(obj.eidgen);
      this.eidmap = {};
      
      this.verts.loadJSON(obj.verts);
      this.edges.loadJSON(obj.edges);
      
      for (var v of this.verts) {
        this.eidmap[v.eid] = v;
      }
      
      for (var e of this.edges) {
        this.eidmap[e.eid] = e;
      }
      
      for (var v of this.verts) {
        for (var i=0; i<v.edges.length; i++) {
          v.edges[i] = this.eidmap[v.edges[i]];
        }
      }
      
      for (var e of this.edges) {
        e.v1 = this.eidmap[e.v1];
        e.v2 = this.eidmap[e.v2];
      }
      
      return this;
    }
    
    setSelect(e, state) {
      if (e.type == MeshTypes.VERTEX)
        this.verts.setSelect(e, state);
      else if (e.type == MeshTypes.EDGE)
        this.edges.setSelect(e, state);
      else
        console.log("bad element", e);
    }
    
    selectNone() {
      this.verts.selectNone();
      this.edges.selectNone();
    }
    
    selectAll() {
      this.verts.selectAll();
      this.edges.selectAll();
    }
    
    get elements() {
      var this2 = this;
      
      return (function*() {
        for (var k in this2.eidmap) {
          yield this2.eidmap[k];
        }
      })()
    }
    
    regen_render() {
      window.redraw_all();
    }
  };
  
  return exports;
});
