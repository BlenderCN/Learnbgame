var _app = undefined; //for debugging purposes only.  don't write code with it

define([
  "util", "mesh", "mesh_tools", "mesh_editor", "const", "simple_toolsys",
  "transform", "events", "implicitgear"
], function(util, mesh, mesh_tools, mesh_editor, cconst, toolsys,
            transform, events, implicitgear)
{
  'use strict';
  
  var exports = _app = {};
  
  window.STARTUP_FILE_NAME = "startup_file_implicitgear";
  window.GRAPHICAL_TEST_MODE = true
  
  var AppState = exports.AppState = class AppState extends events.EventHandler {
    constructor() {
      super();
      
      this.last_save = 0;
      this.canvas = document.getElementById("canvas2d");
      this.g = this.canvas.getContext("2d");
      this.mesh = new mesh.Mesh();
      this.numteeth = 13;
      
      this.ctx = new toolsys.Context();
      this.toolstack = new toolsys.ToolStack();
      this.editor = new mesh_editor.MeshEditor();
      
      this.depthmul = 2.0;
      
      var profile = this.profile = new implicitgear.Profile(this.numteeth);
      
      //profile.inner_gear_mode = 1;
      profile.modulus = 2.0
      profile.backlash = -0.1*4
      profile.depth *= this.depthmul
      
      this.igear = new implicitgear.ImplicitGear(this.g, profile);
    }
    
    setsize() {
      var w = window.innerWidth, h = window.innerHeight;
      
      var eventfire = this.canvas.width != w || this.canvas.height != h;
      
      if (this.canvas.width != w)
        this.canvas.width = w;
      if (this.canvas.height != h)
        this.canvas.height = h;
      
      if (eventfire)
        this.on_resize([w, h]);
    }
    
    draw() {
      this.setsize();
      this.g.clearRect(0, 0, this.canvas.width, this.canvas.height);
      this.editor.draw(this.ctx, this.canvas, this.g);

      this.igear.draw(this.canvas, this.g);
    }
    
    save() {
      return JSON.stringify(this);
    }
    
    load(str) {
      this.loadJSON(JSON.parse(str));
      return this;
    }
    
    toJSON() {
      return {
        version : cconst.APP_VERSION,
        mesh    : this.mesh
      };
    }
    
    loadJSON(obj) {
      this.mesh = new mesh.Mesh();
      this.mesh.loadJSON(obj.mesh);
      
      window.redraw_all();
      return this;
    }
    
    on_resize(newsize) {
      console.log("resize event");
      this.editor.on_resize(newsize);
    }
    
    on_mousedown(e) {
      this.editor.on_mousedown(e);
    }
    
    on_mousemove(e) {
      this.editor.on_mousemove(e);
    }
    
    on_mouseup(e) {
      this.editor.on_mouseup(e);
    }
    
    on_tick() {
      this.editor.on_tick();
      
      if (util.time_ms() - this.last_save > 900) {
        console.log("autosaving");
        localStorage[STARTUP_FILE_NAME] = this.save();
        
        this.last_save = util.time_ms();
      }
    }
    
    on_keydown(e) {
      switch (e.keyCode) {
        case 75: //kkey
            this.igear.run();
            break;
        case 90: //zkey
          if (e.ctrlKey && e.shiftKey && !e.altKey) {
            this.toolstack.redo();
            window.redraw_all();
          } else if (e.ctrlKey && !e.altKey) {
            this.toolstack.undo();
            window.redraw_all();
          }
          break;
        case 187: //pluskey
        case 189: //minuskey
            this.depthmul += e.keyCode == 187 ? 1 : -1;
            this.depthmul = Math.max(this.depthmul, 1);
            this.profile.depth = (this.profile.modulus * 2 / Math.PI) * this.depthmul;
            
            /*
            this.numteeth += e.keyCode == 187 ? 1 : -1;
            
            console.log(this.numteeth)
            this.profile.numteeth = this.numteeth;
            this.igear = new implicitgear.ImplicitGear(this.g, this.profile); //new implicitgear.Profile(this.numteeth));
            //*/
            
            this.igear.run();
            break;
        case 89: //ykey
          if (e.ctrlKey && !e.shiftKey && !e.altKey) {
            this.toolstack.redo();
            window.redraw_all();
          }
          break;
          
        default:
          return this.editor.on_keydown(e);
      }
    }
  }
  
  function start() {
    window._appstate = new AppState();
    
    var canvas = document.getElementById("canvas2d");
    _appstate.pushModal(canvas, true);
    
    var animreq = undefined;
    function dodraw() {
      animreq = undefined;
      _appstate.draw();
    }
    
    window.redraw_all = function redraw_all() {
      if (animreq !== undefined) {
        return;
      }
      
      animreq = requestAnimationFrame(dodraw);
    }
    
    if (STARTUP_FILE_NAME in localStorage) {
      try {
        _appstate.load(localStorage[STARTUP_FILE_NAME]);
      } catch(error) {
        util.print_stack(error);
        console.log("failed to load startup file");
        
        window._appstate = new AppState();
        _appstate.pushModal(canvas, true);
        
        //make base file
        _appstate.toolstack.execTool(new mesh_tools.CreateDefaultFile());
        
        console.log("started!");
        window.redraw_all();
      }
    } else {
      //make base file
      _appstate.toolstack.execTool(new mesh_tools.CreateDefaultFile());
      console.log("started!");
      window.redraw_all();
    }
    
    window.setInterval(function() {
      _appstate.on_tick();
    }, 250);
  }

  start();
  _appstate.igear.run();
  
  return exports;
});
