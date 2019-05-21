var _transform = undefined;

define([
  "util", "vectormath", "mesh", "simple_toolsys"
], function(util, vectormath, mesh, toolsys) {
  'use strict';
 
  var exports = _transform = {};
  
  var Vector3 = vectormath.Vector3,
      Vector2 = vectormath.Vector2;
      
  var TransformOp = exports.TransformOp = class TransformOp extends toolsys.ToolOp {
    constructor(mpos, selmode) {
      super();
      
      this.selectmode = selmode;
      
      this.start_mpos = new Vector2(mpos);
      this.last_mpos = new Vector2(mpos);
      this.mpos = new Vector2(mpos);
      this.center = new Vector2();

      this.transdata = undefined;
      this.first = false;
    }
    
    canRun(ctx) {
      return ctx.mesh.verts.selected.length > 0;
    }
    
    undoPre(ctx) {
      this._undo = [];
      
      for (var v of ctx.mesh.verts.selected) {
        this._undo.push(v.eid);
        
        this._undo.push(v[0]);
        this._undo.push(v[1]);
        this._undo.push(v[2]);
      }
    }
    
    undo(ctx) {
      var ud = this._undo;
      var mesh = ctx.mesh;
      
      for (var i=0; i<ud.length; i += 4) {
        var eid = ud[i];
        
        if (!(eid in mesh.eidmap)) {
          console.warn("Warning, unknown eid " + eid + " in TransformOp.prototype.undo()!");
          continue;
        }
        
        var v = mesh.eidmap[eid];
        
        v[0] = ud[i+1];
        v[1] = ud[i+2];
        v[2] = ud[i+3];
      }
      
      mesh.regen_render();
    }
    
    genTransData(ctx) {
      this.transdata = [];
      this.center.zero();
      
      for (var v of ctx.mesh.verts.selected) {
        this.transdata.push([v, new Vector3(v)]);
      }
      
      var min = new Vector2(), max = new Vector2();
      min[0] = 1e17, min[1] = 1e17;
      max[0] = -1e17, max[1] = -1e17;
      
      for (var v of ctx.mesh.verts.selected) {
          //min.min(v);
          //max.max(v);
          for (var i=0; i<2; i++) {
              min[i] = Math.min(min[i], v[i]);
              max[i] = Math.max(max[i], v[i]);
          }
      }
      
      this.center.load(min).add(max).mulScalar(0.5);
      
      /*
      var tot = 0;
      for (var v of ctx.mesh.verts.selected) {
        this.center.add(v);
        tot++;
      }
      
      if (tot > 0)
        this.center.mulScalar(1.0 / tot);
      */
    }
    
    modalStart(ctx) {
      this.first = this.mpos === undefined;
      this.genTransData(ctx);
      
      return super.modalStart(ctx);
    }
    
    cancel() {
      var ctx = this.modal_ctx;
      
      for (var td of this.transdata) {
        td[0].load(td[1]);
      }
      
      this.finish(true);
    }
    
    finish(was_cancelled) {
      var ctx = this.modal_ctx;
      
      this.transdata = undefined;
      this.modalEnd(was_cancelled);
      
      window.redraw_all();
    }
    
    on_keydown(e) {
      if (e.keyCode == 27) { //escape key
        this.cancel();
      } else if (e.keyCode == 13) { //enter key
        this.finish();
      }
    }
    
    on_mousedown(e) {
      var ctx = this.modal_ctx;
      
      if (e.button != 0) {
        this.cancel();
      } else {
        this.finish();
      }
    }
    
    on_mousemove(e) {
      if (this.first) {
        this.mpos = new Vector2([e.clientX, e.clientY]);
        this.start_mpos.load(this.mpos);
        this.last_mpos.load(this.mpos);
        
        this.first = false;
      } else {
        this.last_mpos.load(this.mpos);
        this.mpos[0] = e.clientX;
        this.mpos[1] = e.clientY;
      }
    }
    
    on_mouseup(e) {
      if (e.button != 0) {
        this.cancel();
      } else {
        this.finish();
      }
    }
  };
  
  var TranslateOp = exports.TranslateOp = class TranslateOp extends TransformOp {
    static tooldef() {return {
      uiname   : "Translate",
      is_modal : true 
    }}
    
    constructor(mpos, selmode) {
      super(mpos, selmode);
      
      this.offset = new Vector3();
    }
    
    on_mousemove(e) {
      super.on_mousemove(e);
      
      this.offset.load(this.mpos).sub(this.start_mpos);
      this.exec(this.modal_ctx);
    }
    
    exec(ctx) {
      if (!this.modal_running) {
        this.genTransData(ctx);
      }
      
      for (var td of this.transdata) {
        td[0].load(td[1]).add(this.offset);
      }
      
      ctx.mesh.regen_render();
      
      super.exec(ctx);
    }
  };

  var RotateOp = exports.RotateOp = class RotateOp extends TransformOp {
    static tooldef() {return {
      uiname   : "Rotate",
      is_modal : true 
    }}
    
    constructor(mpos, selmode) {
      super(mpos, selmode);
      
      this.offset = 0;
    }
    
    on_mousemove(e) {
      super.on_mousemove(e);

      var th = Math.atan2(this.mpos[1]-this.center[1], this.mpos[0]-this.center[0]);
      th -= Math.atan2(this.last_mpos[1]-this.center[1], this.last_mpos[0]-this.center[0]);
      
      this.resetDrawLines();
      this.addDrawLine(this.mpos, this.center);

      this.offset += th;
      this.exec(this.modal_ctx);
    }
    
    exec(ctx) {
      if (!this.modal_running) {
        this.genTransData(ctx);
      }
      
      console.log(this.offset);
      
      for (var td of this.transdata) {
        td[0].load(td[1]).sub(this.center).rot2d(this.offset).add(this.center);
      }
      
      ctx.mesh.regen_render();
      super.exec(ctx);
    }
  };
  
  var ScaleOp = exports.ScaleOp = class ScaleOp extends TransformOp {
    static tooldef() {return {
      uiname   : "Scale",
      is_modal : true 
    }}
    
    constructor(mpos, selmode) {
      super(mpos, selmode);
      
      this.offset = 0;
    }
    
    on_mousemove(e) {
      super.on_mousemove(e);

      var ratio = this.mpos.vectorDistance(this.center);
      ratio = ratio / this.start_mpos.vectorDistance(this.center);
      
      if (isNaN(ratio)) {
        console.warn("ratio was NaN!");
        return;
      }
      
      this.offset = ratio;

      this.resetDrawLines();
      this.addDrawLine(this.mpos, this.center);
      
      this.exec(this.modal_ctx);
    }
    
    exec(ctx) {
      if (!this.modal_running) {
        this.genTransData(ctx);
      }
      
      for (var td of this.transdata) {
        td[0].load(td[1]).sub(this.center).mulScalar(this.offset).add(this.center);
      }
      
      ctx.mesh.regen_render();
      super.exec(ctx);
    }
  };
  
  return exports;
});
