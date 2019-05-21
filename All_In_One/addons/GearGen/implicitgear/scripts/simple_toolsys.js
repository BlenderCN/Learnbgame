var _simple_toolsys = undefined;
define([
  "util", "events"
], function(util, events) {
  'use strict';
  
  var exports = _simple_toolsys = {};
  
  var Context = exports.Context = class Context {
    constructor() {
    }
    
    get mesh() {
      return _appstate.mesh;
    }
    
    get editor() {
      return _appstate.editor;
    }
  }
  
  var ToolFlags = exports.ToolFlags = {
    PRIVATE : 1
  };
  
  var UndoFlags = exports.UndoFlags = {
    NO_UNDO      : 1,
    IS_UNDO_ROOT : 2
  };
  
  var ToolOp = exports.ToolOp = class ToolOp extends events.EventHandler {
    static tooldef() {return {
      uiname   : "!untitled tool",
      is_modal : false,
      undoflag : 0,
      flag     : 0
    }}
    
    constructor() {
      super();
      var def = this.constructor.tooldef();
      this._accept = this._reject = undefined;
      this._promise = undefined;
      
      for (var k in def) {
        this[k] = def[k];
      }
      
      this.drawlines = [];
    }
    
    canRun(ctx) {
      return true;
    }
    
    undoPre(ctx) {
      this._undo = _appstate.save();
      window.redraw_all();
    }
    
    undo(ctx) {
      _appstate.load(this._undo);
      
      window.redraw_all();
    }
    
    exec(ctx) {
    }
    
    //for use in modal mode only
    resetDrawLines() {
      var ctx = this.modal_ctx;
      
      for (var dl of this.drawlines) {
        ctx.editor.removeDrawLine(dl);
      }
      
      this.drawlines.length = 0;
    }
    
    error(msg) {
      console.warn(msg);
    }
    
    //for use in modal mode only
    addDrawLine(v1, v2, style) {
      style = style === undefined ? "grey" : style;
      
      var dl = this.modal_ctx.editor.addDrawLine(v1, v2, style);
      this.drawlines.push(dl);
      return dl;
    }
    
    //returns promise to be executed on modalEnd
    modalStart(ctx) {
      if (this.modal_running) {
        console.warn("Warning, tool is already in modal mode consuming events");
        return this._promise;
      }
      
      console.trace("tool modal start");
      
      this.modal_ctx = ctx;
      this.modal_running = true
      
      this.pushModal(document.getElementById("canvas2d"));
      
      this._promise = new Promise((function(accept, reject) {
        this._accept = accept;
        this._reject = reject;
      }).bind(this));
      
      return this._promise;
    }
    
    toolCancel() {
    }
    
    modalEnd(was_cancelled) {
      console.log("tool modal end");
      
      if (was_cancelled && this._on_cancel !== undefined) {
        this._on_cancel(this);
      }
      
      this.resetDrawLines();
      
      var ctx = this.modal_ctx;
      
      this.modal_ctx = undefined;
      this.modal_running = false;
      this.is_modal = false;
      
      this.popModal(document.getElementById("canvas2d"));
      
      this._promise = undefined;
      this._accept(ctx);
      this._accept = this._reject = undefined;
    }
  }
  
  var ToolMacro = exports.ToolMacro = class ToolMacro extends ToolOp {
    static tooldef() {return {
      uiname : "Tool Macro"
    }}
    
    constructor() {
      super();
      
      this.tools = [];
      this.curtool = 0;
      this.has_modal = false;
      this.connects = [];
    }
    
    connect(srctool, dsttool, callback, thisvar) {
      this.connects.push({
        srctool  : srctool,
        dsttool  : dsttool,
        callback : callback,
        thisvar  : thisvar
      });
      
      return this;
    }
    
    add(tool) {
      if (tool.is_modal) {
        this.is_modal = true;
      }
      
      this.tools.push(tool);
      
      return this;
    }
    
    _do_connections(tool) {
      for (var c of this.connects) {
        if (c.srctool === tool) {
          c.callback.call(c.thisvar, c.srctool, c.dsttool);
        }
      }
    }
    
    canRun(ctx) {
      if (this.tools.length == 0)
        return false;
      
      //poll first tool only in list
      return this.tools[0].canRun(ctx);
    }
    
    modalStart(ctx) {
      this._promise = new Promise((function(accept, reject) {
        this._accept = accept;
        this._reject = reject;
      }).bind(this));
      
      this.curtool = 0;
      
      for (var i=0; i<this.tools.length; i++) {
        if (this.tools[i].is_modal)
          break;
        
        this.tools[i].undoPre(ctx);
        this.tools[i].exec(ctx);
        this._do_connections(this.tools[i]);
      }
      
      var on_modal_end = (function on_modal_end() {
          this._do_connections(this.tools[this.curtool]);
          this.curtool++;
          
          while (this.curtool < this.tools.length && 
                 !this.tools[this.curtool].is_modal) 
          {
              this.tools[this.curtool].undoPre(ctx);
              this.tools[this.curtool].exec(ctx);
              this._do_connections(this.tools[this.curtool]);
              
              this.curtool++;
          }
          
          if (this.curtool < this.tools.length) {
            this.tools[this.curtool].undoPre(ctx);
            this.tools[this.curtool].modalStart(ctx).then(on_modal_end);
          } else {
            this._accept(this);
          }
      }).bind(this);
      
      if (i < this.tools.length) {
        this.curtool = i;
        this.tools[this.curtool].undoPre(ctx);
        this.tools[this.curtool].modalStart(ctx).then(on_modal_end);
      }
      
      return this._promise;
    }
    
    exec(ctx) {
      for (var i=0; i<this.tools.length; i++) {
        this.tools[i].undoPre(ctx);
        this.tools[i].exec(ctx);
        this._do_connections(this.tools[i]);
      }
    }
    
    undoPre() {
      return; //undoPre is handled in exec() or modalStart()
    }
    
    undo(ctx) {
      for (var i=this.tools.length-1; i >= 0; i--) {
        this.tools[i].undo(ctx);
      }
    }
  }
  
  var ToolStack = exports.ToolStack = class ToolStack extends Array {
    constructor() {
      super();
      
      this.cur = -1;
      this.ctx = new Context();
      this.modal_running = 0;
    }
    
    execTool(toolop) {
      var ctx = this.ctx;
      
      if (!toolop.canRun(ctx)) {
        console.log("toolop.canRun returned false");
        return;
      }
      
      if (!(toolop.undoflag & UndoFlags.NO_UNDO)) {
        this.cur++;

        //truncate
        this.length = this.cur+1;
        
        this[this.cur] = toolop;
        toolop.undoPre(ctx);
      }
      
      if (toolop.is_modal) {
        this.modal_running = true;
        
        toolop._on_cancel = (function(toolop) {
          this.pop_i(this.cur);
          this.cur--;
        }).bind(this);
        
        //will handle calling .exec itself
        toolop.modalStart(ctx).then((function() {
          this.modal_running = false;
        }).bind(this));
      } else {
        toolop.exec(ctx);
      }
    }
    
    undo() {
      if (this.cur > 0 && !(this[this.cur].undoflag & UndoFlags.IS_UNDO_ROOT)) {
        console.log("undo!", this.cur, this.length);
        
        this[this.cur].undo(this.ctx);
        this.cur--;
      }
    }
    
    redo() {
      if (this.cur >= 0 && this.cur+1 < this.length) {
        console.log("redo!", this.cur, this.length);
        
        this.cur++;
        
        this[this.cur].undoPre(this.ctx);
        this[this.cur].exec(this.ctx);
      }
    }
  }
  
  return exports;
});
