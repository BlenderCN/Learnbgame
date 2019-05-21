var _screen = undefined;

define([
  "util", "mesh", "mesh_tools", "controller", "vectormath"
], function(util, mesh, mesh_tools, controller, vectormath) {
  'use strict';
  
  var exports = _screen = {};
  var Vector3 = vectormath.Vector3;
  var Vector2 = vectormath.Vector2;
  
  var Screen = exports.Screen = class Screen {
    constructor() {
      this.size = new Vector2();
      this.mdown = 0;
      
      this.start_mpos = new Vector2();
      this.last_mpos = new Vector2();
      this.mpos = new Vector2();
    }
    
    on_resize(newsize) {
      this.size.load(newsize);
    }
    
    on_mousedown(e) {
      this.mdown = true;
      this.start_mpos.load([e.clientX, e.clientY]);
    }
    
    on_mouseup(e) {
      this.mdown = false;
    }
    
    on_mousemove(e) {
      this.last_mpos.load(this.mpos);
      
      this.mpos[0] = e.clientX;
      this.mpos[1] = e.clientY;
      
      if (this.mdown) {
        this.on_drag(this.mdown);
      }
    }
    
    on_keydown(e) {
      console.log(e.keyCode);
    }
    
    on_tick() {
    }
    
    on_resize(newsize) {
    }
    
    //internally generated
    on_drag(button) {
    }
    
    draw(ctx, canvas, g) {
    }
    
    destroy(ctx) {
    }
  }
  
  return exports;
});
