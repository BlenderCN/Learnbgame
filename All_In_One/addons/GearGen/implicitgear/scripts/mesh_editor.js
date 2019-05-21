var _mesh_editor = undefined;

define([
  "util", "mesh", "mesh_tools", "controller", "screen", "vectormath",
  "transform", "simple_toolsys"
], function(util, mesh, mesh_tools, controller, screen, vectormath,
            transform, toolsys)
{
  'use strict';
  
  var exports = _mesh_editor = {};
  var Vector3 = vectormath.Vector3;
  var Vector2 = vectormath.Vector2;
  var MeshFlags = mesh.MeshFlags;
  var MeshTypes = mesh.MeshTypes;
  
  var SELECT = 1, ACTIVE = 2, HIGHLIGHT = 4;
  
  var MeshColors = exports.MeshColors = {
    0 : [0.23, 0.23, 0.23, 1.0],
    1 : [0.3, 0.5, 1.0, 1.0],  // SELECT
    2 : [1.0, 0.25, 0.1, 1.0], // ACTIVE
    3 : [1.0, 0.5, 0.75, 1.0], // ACTIVE+SELECT
    4 : [1.0, 1.0, 0.3, 1.0],  // HIGHLIGHT
    5 : [1.0, 1.0, 0.6, 1.0],  // SELECT+HIGHLIGHT
    6 : [1.0, 1.0, 0.8, 1.0],  // ACTIVE+HIGHLIGHT
    7 : [1.0, 1.0, 0.8, 1.0]   // ACTIVE+SELECT+HIGHLIGHT
  };
  for (var k in MeshColors) {
    MeshColors[k] = util.color2css(MeshColors[k]);
  }
  
  var getElemColor = exports.getElemColor = function ElemColor(e, list) {
    var flag = 0;
    
    if (e.flag & MeshFlags.SELECT)
      flag |= SELECT;
    if (e === list.highlight)
      flag |= HIGHLIGHT;
    if (e === list.active)
      flag |= ACTIVE;
    
    return MeshColors[flag];
  }
  
  var DrawLine = exports.DrawLine = class DrawLine {
    constructor(v1, v2, style) {
      this.v1 = new Vector3(v1);
      this.v2 = new Vector3(v2);
      
      this.style = style;
    }
  };
  
  var MeshEditor = exports.MeshEditor = class MeshEditor extends screen.Screen {
    constructor(ctx) {
      super();
      
      this.selectmode = MeshTypes.VERTEX;
      this.ctx = ctx;
      this.drawlines = [];
    }
    
    toJSON() {
      return {
        selectmode : this.selectmode
      };
    }
    
    fromJSON(obj) {
      this.selectmode = obj.selectmode;
    }
    
    draw_mesh(mesh, canvas, g) {
      var w = 2;
      
      for (var e of mesh.edges) {
        g.beginPath();
        g.strokeStyle = getElemColor(e, mesh.edges);
        g.moveTo(e.v1[0], e.v1[1]);
        g.lineTo(e.v2[0], e.v2[1]);
        g.stroke();
      }
      
      for (var v of mesh.verts) {
        g.beginPath();
        g.fillStyle = getElemColor(v, mesh.verts);
        g.rect(v[0]-w*0.5, v[1]-w*0.5, w, w);
        g.fill();
      }
    }
    
    draw(ctx, canvas, g) {
      g.clearRect(0, 0, canvas.width, canvas.height);
      this.ctx = ctx;
      
      this.draw_mesh(ctx.mesh, canvas, g);
      
      for (var dl of this.drawlines) {
        g.beginPath();
        g.moveTo(dl.v1[0], dl.v1[1]);
        g.lineTo(dl.v2[0], dl.v2[1]);
        g.strokeStyle = dl.style;
        g.stroke();
      }
    }
    
    on_mousedown(e) {
      super.on_mousedown(e);
      
      var mesh = this.ctx.mesh;
      
      function do_select(list) {
        list.active = list.highlight;
        
        if (!e.shiftKey) {
          var tool = new mesh_tools.SelectOneOp(list.highlight.eid, true);
          _appstate.toolstack.execTool(tool);
          
          window.redraw_all();
        } else {
          var state = list.highlight.flag & MeshFlags.SELECT;
          var tool = new mesh_tools.SelectOneOp(list.highlight.eid, false, !state);
          _appstate.toolstack.execTool(tool);
          
          window.redraw_all();
        }
      }
      
      if (this.selectmode & MeshTypes.VERTEX && mesh.verts.highlight !== undefined) {
        do_select(mesh.verts);
      } else if (this.selectmode & MeshTypes.EDGE && mesh.edges.highlight !== undefined) {
        do_select(mesh.edges);
      } else if (mesh.verts.highlight === undefined && mesh.edges.highlight === undefined) {
        var tool = new mesh_tools.CreateVertexOp(this.mpos);
        
        if (mesh.verts.active !== undefined) {
          var tool2 = new mesh_tools.CreateEdgeOp(mesh.verts.active.eid);
          var macro = new toolsys.ToolMacro();
          
          macro.add(tool).add(tool2).connect(tool, tool2, function(tool, tool2) {
            tool2.v2 = tool.eid;
          });
          
          _appstate.toolstack.execTool(macro);
        } else {
          _appstate.toolstack.execTool(tool);
        }
      }
      
    }
    
    on_drag(e) {
      super.on_drag(e);
      
      console.log("drag!");

      var tool = new transform.TranslateOp(this.start_mpos);
      _appstate.toolstack.execTool(tool);
      
      //tool will consume mouseup event
      this.mdown = false;

      window.redraw_all();
    }
    
    on_mousemove(e) {
      super.on_mousemove(e);
      
      if (this.mdown)
        return;
      
      var mesh = this.ctx.mesh;
      var mpos = new Vector3([e.clientX, e.clientY, 0]);
      var e = mesh_tools.findnearest(this.ctx.mesh, mpos, this.selectmode);
      var redraw;
      
      if (e === undefined) {
        redraw = mesh.verts.highlight !== undefined || mesh.edges.highlight != undefined;
        mesh.verts.highlight = mesh.edges.highlight = undefined;
      } else {
        e = e[0];
        
        mesh.verts.highlight = mesh.edges.highlight = undefined;
        
        var list = mesh.getList(e.type);
        redraw = list.highlight !== e;
        
        list.highlight = e;
      }
      
      if (redraw) {
        window.redraw_all();
      }
    }
    
    addDrawLine(v1, v2, style) {
      var dl = new DrawLine(v1, v2, style);
      this.drawlines.push(dl);
      return dl;
    }
    
    removeDrawLine(dl) {
      this.drawlines.remove(dl, true);
    }
    
    on_keydown(e) {
      console.log(e.keyCode);
      
      switch (e.keyCode) {
        case 70: //fkey
          var mesh = this.ctx.mesh;

          if (mesh.verts.selected.length == 2) {
            var active = mesh.verts.active;
            var v1 = undefined, v2 = undefined;

            v1 = active !== undefined && (active.flag & MeshFlags.SELECT) ? active : undefined;

            for (var v of mesh.verts.selected) {
              if (!v1)
                v1 = v;
              else
                v2 = v;
            }

            if (v1 === undefined || v2 === undefined) {
              console.log("could not make edge; failed to find vertices (mesh integrity error?)");
              break;
            }

            var tool = new mesh_tools.CreateEdgeOp(v1.eid, v2.eid);
            _appstate.toolstack.execTool(tool);

            window.redraw_all();
          }
          break;
        case 71: //gkey
          var tool = new transform.TranslateOp(this.mpos);
          _appstate.toolstack.execTool(tool);
          break;
        case 82: //rkey
          if (!e.ctrlKey && !e.shiftKey && !e.altKey) {
            var tool = new transform.RotateOp(this.mpos);
            _appstate.toolstack.execTool(tool);
          }
          break;
        case 83: //skey
          var tool = new transform.ScaleOp(this.mpos);
          _appstate.toolstack.execTool(tool);
          break;
        case 65: //akey
          var tool = new mesh_tools.ToggleSelectAll();
          _appstate.toolstack.execTool(tool);
          
          window.redraw_all();
          break;
          
        case 88: //xkey
        case 46: //delete
        case  8: //backspace
          if (this.selectmode & MeshTypes.VERTEX) {
            var tool = new mesh_tools.DeleteVertexOp();
            _appstate.toolstack.execTool(tool);
          } else if (this.selectmode & MeshTypes.EDGE) {
            var tool = new mesh_tools.DeleteEdgeOp();
            _appstate.toolstack.execTool(tool);
          }
          
          window.redraw_all();
          break;
        case 76: //lkey
          console.log("select linked");
          
          var mesh = this.ctx.mesh;
          var heid = mesh.verts.highlight !== undefined ? mesh.verts.highlight.eid : undefined;
          var tool = new mesh_tools.SelectLinkedOp(heid, !e.shiftKey);
          
          _appstate.toolstack.execTool(tool);
          
          break;
        case 68: //dkey
          if (e.shiftKey) {
            var tool = new toolsys.ToolMacro();
            
            tool.add(new mesh_tools.DuplicateOp());
            tool.add(new transform.TranslateOp(this.mpos));
            
            _appstate.toolstack.execTool(tool);
          } else {
            var tool = new mesh_tools.DissolveVertexOp();
            _appstate.toolstack.execTool(tool);
          }          
          window.redraw_all();          
          break;
        case 69: //ekey
          var tool = new mesh_tools.SplitEdgeOp();
          _appstate.toolstack.execTool(tool);
        
          window.redraw_all();
          break;
      }
    }
  };
  
  return exports;
});
