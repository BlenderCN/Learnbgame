var _mesh;

define([
  "util", "vectormath", "math", "mesh", "simple_toolsys"
], function(util, vectormath, math, mesh, toolsys) {
  'use strict';
  
  var exports = _mesh = {};
  var Vector2 = vectormath.Vector2;
  var Vector3 = vectormath.Vector3;
  var MeshFlags = mesh.MeshFlags;
  var MeshTypes = mesh.MeshTypes;
  
  var DEFAULT_LIMIT = 55;
  
  var findnearest_vertex = exports.findnearest_vertex = function findnearest_vertex(mesh, mpos, limit) {
    limit = limit === undefined ? DEFAULT_LIMIT : limit;
    
    mpos = new Vector3(mpos);
    mpos[2] = 0.0;
    
    var mindis = 1e17;
    var minret = undefined;
    
    for (var v of mesh.verts) {
      var dis = v.vectorDistance(mpos);
      
      if (dis < mindis && dis < limit) {
        mindis = dis;
        minret = v;
      }
    }
    
    if (minret !== undefined) {
      return [minret, mindis];
    }
    
    return undefined;
  }
  
  var findnearest_edge = exports.findnearest_edge = function findnearest_edge(mesh, mpos, limit) {
    limit = limit === undefined ? DEFAULT_LIMIT : limit;
  }
  
  var findnearest = exports.findnearest = function findnearest(mesh, mpos, typemask, limit) {
    limit = limit === undefined ? DEFAULT_LIMIT : limit;
    
    var ret = undefined;
    
    function domin(ret2) {
      if (ret2 === undefined)
        return;
      if (ret === undefined || ret2[1] < ret[1]) {
        ret = ret2;
      }
    }
    
    if (typemask == 0) {
      throw new Error("typemask cannot be zero");
    }
    
    if (typemask & MeshTypes.VERTEX) {
      domin(exports.findnearest_vertex(mesh, mpos));
    }
    
    if (typemask & MeshTypes.EDGE) {
      domin(exports.findnearest_edge(mesh, mpos));
    }
    
    return ret;
  }
  
  var SelectOpBase = exports.SelectOpBase = class SelectOpBase extends toolsys.ToolOp {
    static tooldef() {return {
      uiname : "Selection Tool"
    }}
    
    constructor() {
      super();
    }
    
    undoPre(ctx) {
      var mesh = ctx.mesh;
      this._undo = [];
      
      for (var k in mesh.eidmap) {
        var e = mesh.eidmap[k];
        
        this._undo.push(e.eid);
        this._undo.push(e.flag & MeshFlags.SELECT);
      }
    }
    
    undo(ctx) {
      var mesh = ctx.mesh;
      
      for (var i=0; i<this._undo.length; i += 2) {
        var eid = this._undo[i], state = this._undo[i+1];
        var e = mesh.eidmap[eid];
        
        if (e === undefined) {
          console.log("Failed to lookup eid in SelectOpBase.prototype.undo()", mesh, ctx, this);
          continue;
        }
        
        mesh.setSelect(e, state);
      }
      
      window.redraw_all();
    }
  }
  
  var SelectOneOp = exports.SelectOneOp = class SelectOneOp extends SelectOpBase {
    static tooldef() {return {
      uiname : "Select One Element"
    }}
    
    constructor(eid, preclear, state) {
      super();
      
      this.preclear = preclear !== undefined ? preclear : false;
      this.eid = eid;
      this.state = state === undefined ? true : !!state;
    }
    
    exec(ctx) {
      if (this.preclear) {
        for (var e of ctx.mesh.elements) {
          ctx.mesh.setSelect(e, false);
        }
      }
      
      ctx.mesh.setSelect(ctx.mesh.eidmap[this.eid], this.state);
      ctx.mesh.selectFlush(ctx.editor.selectmode);
    }
  }
  
  var ToggleSelectAll = exports.ToggleSelectAll = class ToggleSelectAll extends SelectOpBase {
    static tooldef() {return {
      uiname : "Toggle Select All"
    }}
    
    constructor() {
      super();
      
      this.clearActive = true;
    }
    
    exec(ctx) {
      var selstate = true;
      
      for (var e of ctx.mesh.elements) {
        if (e.flag & MeshFlags.HIDE)
          continue;
        
        if (e.flag & MeshFlags.SELECT)
          selstate = false;
      }
      
      if (!selstate && this.clearActive) {
        ctx.mesh.verts.active = ctx.mesh.edges.active = undefined;
      }
      
      for (var e of ctx.mesh.elements) {
        if (e.flag & MeshFlags.HIDE)
          continue;
        
        ctx.mesh.setSelect(e, selstate);
      }
    }
  }
  
  exports.CreateDefaultFile = class CreateDefaultFile extends toolsys.ToolOp {
    static tooldef() {return {
      uiname   : "Create Default File",
      undoflag : toolsys.UndoFlags.IS_UNDO_ROOT
    }}
    
    exec(ctx) {
      var mesh = ctx.mesh;
      
      var v1 = mesh.makeVertex([50, 49, 0]);
      var v2 = mesh.makeVertex([250, 49, 0]);
      var v3 = mesh.makeVertex([250, 249, 0]);
      var v4 = mesh.makeVertex([50, 249, 0]);
      
      mesh.makeEdge(v1, v2);
      mesh.makeEdge(v2, v3);
      mesh.makeEdge(v3, v4);
      mesh.makeEdge(v4, v1);
      
      mesh.regen_render();
    }
  }
  
  var CreateVertexOp = exports.CreateVertexOp = class CreateVertexOp extends toolsys.ToolOp {
    static tooldef() {return {
      uiname : "Create Vertex"
    }}
    
    constructor(co) {
      super();
      
      this.setActive = true; //set new vert as active vertex
      this.clearSelection = true;
      this.selectNew = true;
      
      this.co = new Vector3(co);
      this.eid = undefined; //will be set to new vertex's eid
      
      //sanitize
      for (var i=0; i<this.co.length; i++) {
        if (this.co[i] === undefined)
          this.co[i] = 0;
      }
    }
    
    exec(ctx) {
      var v = ctx.mesh.makeVertex(this.co);
      this.eid = v.eid;
      
      if (this.setActive)
        ctx.mesh.verts.active = v;
      
      if (this.clearSelection) {
        ctx.mesh.selectNone();
      }
      
      if (this.selectNew) {
        ctx.mesh.setSelect(v, true);
      }
      
      ctx.mesh.regen_render();
    }
  }
  
  var DeleteVertexOp = exports.DeleteVertexOp = class DeleteVertexOp extends toolsys.ToolOp {
    static tooldef() {return {
      uiname : "Delete Vertices",
      description : "Delete Selected Vertices"
    }}
    
    constructor() {
      super();
    }
    
    exec(ctx) {
      for (var v of ctx.mesh.verts.selected) {
        ctx.mesh.killVertex(v);
      }
    }
  };
  
  var CreateEdgeOp = exports.CreateEdgeOp = class CreateEdgeOp extends toolsys.ToolOp {
    constructor(v1, v2) {
      super();
      
      this.doSelectFlush = true;
      
      if (v1 !== undefined && typeof v1 == "object")
        v1 = v1.eid;
      if (v2 !== undefined && typeof v2 == "object")
        v2 = v2.eid;
      
      this.v1 = v1;
      this.v2 = v2;
      
      this.eid = undefined; //will be set to eid of new edge
    }
    
    canRun(ctx) {
      var ok = this.v1 !== undefined && this.v2 !== undefined;
      
      ok = ok && this.v1 in ctx.mesh.eidmap && this.v2 in ctx.mesh.eidmap;
      ok = ok && ctx.mesh.eidmap[this.v1].type == MeshTypes.VERTEX;
      ok = ok && ctx.mesh.eidmap[this.v2].type == MeshTypes.VERTEX;
      ok = ok && !ctx.mesh.getEdge(ctx.mesh.eidmap[this.v1], ctx.mesh.eidmap[this.v2]);
      
      return ok;
    }
    
    exec(ctx) {
      this.eid = ctx.mesh.makeEdge(ctx.mesh.eidmap[this.v1], ctx.mesh.eidmap[this.v2]).eid;

      if (this.doSelectFlush) {
        ctx.mesh.selectFlush(ctx.editor.selectmode);
      }
    }
  };
  
  var DeleteEdgeOp = exports.DeleteEdgeOp = class DeleteEdgeOp extends toolsys.ToolOp {
    static tooldef() {return {
      uiname : "Delete Edges",
      description : "Delete Selected Edges"
    }}
    
    constructor() {
      super();
    }
    
    exec(ctx) {
      for (var e of ctx.mesh.edges.selected) {
        ctx.mesh.killEdge(e);
      }
    }
  };
  
  var DissolveVertexOp = exports.DissolveVertexOp = class DissolveVertexOp extends toolsys.ToolOp {
    static tooldef() {return {
      uiname : "Dissolve Vertices",
      description : "Dissolve Selected Vertices"
    }}
    
    constructor() {
      super();
    }
    
    exec(ctx) {
      for (var v of ctx.mesh.verts.selected) {
        if (v.edges.length < 2)
          continue; //ignore verts with valence less than 2
        
        if (v.edges.length > 2) {
          //verts with valence greater than 2 are in error
          this.error("Can't dissolve vertex with more than two edges");
          continue;
        }
        
        ctx.mesh.dissolveVertex(v);
      }
    }
  };
  
  var SplitEdgeOp = exports.SplitEdgeOp = class SplitEdgeOp extends toolsys.ToolOp {
    static tooldef() {return {
      uiname : "Split Edges",
      description : "Split selected edges"
    }}
    
    constructor() {
      super();
    }
    
    exec(ctx) {
      var list = [];
      
      for (var e of ctx.mesh.edges.selected) {
        list.push(e);
      }
      
      for (var e of list) {
        ctx.mesh.splitEdge(e);
      }
    }
  };
  
  var DuplicateOp = exports.DuplicateOp = class DuplicateOp extends toolsys.ToolOp {
    static tooldef() {return {
      uiname : "Duplicate Geomtry"
    }}
    
    constructor() {
      super();
    }
    
    exec(ctx) {
      var vs = new util.set(), es = new util.set();
      
      var eidmap = {};
      
      for (var e of ctx.mesh.edges.selected) {
        vs.add(e.v1);
        vs.add(e.v2);
        
        es.add(e);
      }
      
      for (var v of ctx.mesh.verts.selected) {
        vs.add(v);
      }
      
      for (var v of vs) {
        var nv = ctx.mesh.makeVertex(v);
        
        eidmap[v.eid] = nv;
        ctx.mesh.setSelect(v, false);
        ctx.mesh.setSelect(nv, true);
      }
      
      for (var e of es) {
        var ne = ctx.mesh.makeEdge(eidmap[e.v1.eid], eidmap[e.v2.eid]);
        eidmap[e.eid] = ne;
        
        ctx.mesh.setSelect(e, false);
        ctx.mesh.setSelect(ne, true);
      }
      
      ctx.mesh.regen_render();
    }
  }
  
  var SelectLinkedOp = exports.SelectLinkedOp = class SelectLinkedOp extends SelectOpBase {
    constructor(highlightVertexEid, selState) {
      super();
      
      this.highlightVertexEid = highlightVertexEid;
      this.selState = selState;
    }
    
    exec(ctx) {
      var mesh = ctx.mesh;
      
      var vs = new util.set();
      
      //include selected vertices if selState is true
      if (this.selState) {
        for (var v of mesh.verts.selected) {
          vs.add(v);
        }
      }
      
      if (this.highlightVertexEid !== undefined && this.highlightVertexEid in mesh.eidmap) {
        vs.add(mesh.eidmap[this.highlightVertexEid]);
      }
      
      for (var v of vs) {
        var stack = [v];
        var visit = new util.set();
        visit.add(v);
        
        while (stack.length > 0) {
          var v = stack.pop();
          
          mesh.setSelect(v, this.selState);
          
          for (var e of v.edges) {
            var v2 = e.otherVertex(v);
            
            if (!visit.has(v2)) {
              visit.add(v2);
              stack.push(v2);
            }
          }
        }
      }
      
      mesh.selectFlush(ctx.editor.selectmode);
      mesh.regen_render();
    }
  }
  
  return exports;
});
