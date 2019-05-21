var _implicitgear = undefined; //for debugging purposes only.  don't write code with it

define([
  "util", "mesh", "const", "vectormath", "math"
], function(util, mesh, cconst, vectormath, math)
{
  'use strict';
  
  var Vector2 = vectormath.Vector2;
  var Vector3 = vectormath.Vector3;
  var Matrix4 = vectormath.Matrix4;
  
  var exports = _implicitgear = {};
    
  var Profile = exports.Profile = class Profile {
      constructor(numteeth) {
          this.pressureth = (20 / 180) * Math.PI;
          this.backlash = 0.1;
          this.modulus = 2.0; //teeth width
          this.depth = (this.modulus * 2 / Math.PI);
          this.numteeth = numteeth;
          this.genRadius();
          this.inner_gear_mode = false;
          
          this._dx = Math.sin(this.pressureth)*this.depth;
          this._dy = Math.cos(this.pressureth)*this.depth;
      }
      
      genRadius() {
          this.radius = (this.modulus * 2 * this.numteeth) / Math.PI / 2;
          this.pitch_radius = this.radius //+this.depth*0.5;
      }
      
      hash() {
          this.genRadius();
          
          return this.depth.toFixed(5) + "," + this.pressureth.toFixed(5) + "," + this.modulus.toFixed(5) + "," + this.numteeth +
                 "," + this.backlash.toFixed(5) + "," + this.inner_gear_mode;
      }
  };
  
  var ImplicitGear = exports.ImplicitGear = class ImplicitGear {
      //g is a Canvas2DContext
      constructor(g, profile) {
          this.size = 128;
          this.image = new ImageData(new Uint8ClampedArray(this.size*this.size*4), this.size, this.size);
          
          this.profile = profile;
          
          profile.backlash *= 0.25;
          profile.backlash -= 0.0125; //magic number! have to do this for some reason
          
          var ilen = this.size*this.size*4;
          var data = this.image.data;
          for (var i=3; i<ilen; i += 4) {
              data[i] = 255;
          }
          
          this.fdata = new Float32Array(this.size*this.size);
          this.fdata.fill(1.0, 0, this.fdata.length);
          
          this.projscale = this.profile.modulus*2.0;
          this._unprojxy_tmp = util.cachering.fromConstructor(Vector2, 64);
          this._projxy_tmp = util.cachering.fromConstructor(Vector2, 64);
      }
      
      unproject(ix, iy) {
          var ret = this._unprojxy_tmp.next().zero();
          
          var size = this.size, radius = this.radius, projscale = this.projscale;
          
          ret[0] = ix / size - 0.5;
          ret[1] = (size - iy) / size - 0.5;
          
          ret.mulScalar(projscale);
          ret[1] += radius;
          
          return ret;
      }
      
      project(x, y) {
          var p = this._projxy_tmp.next();
          var size = this.size, radius = this.radius, projscale = this.projscale;

          p[0] = x, p[1] = y;
          
          p[1] -= radius;
          p.divScalar(projscale);
          
          p[0] = (p[0] + 0.5) * size;
          p[1] = size * (0.5 - p[1]);
          
          return p;
      }
      draw(canvas, g) {
          g.putImageData(this.image, 0, 0);
      }
      
      makeField() {
          var traps = [];
          
          var backlash = this.profile.backlash
          var width = this.profile.modulus; //teeth width
          var depth = this.profile.depth
          
          var numteeth = this.profile.numteeth;
          var pressureth = this.profile.pressureth;
          
          var radius = this.radius = this.profile.radius;
          var inner_gear = this.profile.inner_gear_mode;
          
          function trap() { //trap is short for trapezoid
              var width2 = width*0.5;
              
              var tanfac = Math.tan(pressureth)*depth;
              
              var a = 0.5, b = 1.0 - a;
              var y = 0;
              
              var t = [
                new Vector2([-width2+a*tanfac, y-depth*0.5]),
                new Vector2([-width2-b*tanfac, y+depth*0.5]),
                new Vector2([width2+b*tanfac, y+depth*0.5]),
                new Vector2([width2-a*tanfac, y-depth*0.5])
              ];
              
              traps.push(t);
              
              return t;
          }
          
          function rot(t, th) {
              for (var v of t) {
                  v.rot2d(th);
              }
          }
          
          function trans(t, offx, offy) {
              for (var v of t) {
                  v[0] += offx;
                  v[1] += offy;
              }
          }
          
          function scale(t, sx, sy) {
              sy = sy === undefined ? sx : sy;
              
              for (var v of t) {
                  v[0] *= sx;
                  v[1] *= sy;
              }
          }
          
          var dvel = width*2 //* numteeth*2;
          var dth = dvel / radius;
          
          var rackx = -dvel;
          
          var steps = 32;
          var dth2 = dth / steps;
          var dvel2 = dvel / steps;
          var th = (width) / radius;
          
          if (window.GRAPHICAL_TEST_MODE) {
              console.log("pitch:", radius);
          }
          
          for (var i=0; i<steps; i++) {
            var dx = rackx, dy = radius;
            
            var dx = (rackx) % (width*2) + width;
            var t = trap();
           
            //scale(t, 1.0, 0.9);
            trans(t, -dx, dy);
            rot(t, th);
            
            rackx += dvel2;
            th -= dth2;
          }
          
          /*
          on factor;
          off period;
          */
          var itmp1 = new Vector2(), itmp2 = new Vector2(), itmp3 = new Vector2();
          
          function cutout(x, y) {
              var cutradius = width*0.35
              var rx = 0, ry = radius - depth*0.35;
              
              x -= rx, y -= ry;
              var d = x*x + y*y;
              
              if (d == 0) {
                  return 0;
              }
              
              d = Math.sqrt(d);
              
              return cutradius-d;
          }
          
          var itmp = new Vector2();
          function inside(x, y) {
              var minret = undefined;
              
              if (inner_gear) {
                  var r2 = Math.sqrt(x*x + y*y);
                  
                  r2 -= radius;// - depth*0.5;
                  //r2 = depth - r2;
                  r2 = -r2;
                  r2 += radius;// - depth*0.5;
                  
                  itmp[0] = x, itmp[1] = y;
                  itmp.normalize().mulScalar(r2);
                  
                  x = itmp[0], y = itmp[1];
              }
              
              var r = radius + depth*0.5;
              if (x*x + y*y > r*r) {
                  return 1;
              }
              
              for (var t of traps) {
                    var sum = undefined;
                    
                    var ok = true;
                    
                    for (var i=0; i<4; i++) {
                        var a = t[i], b = t[(i+1)%t.length];
                            
                        var v1 = itmp1.zero();
                        var v2 = itmp2.zero();
                        
                        v1.load(b).sub(a).normalize();
                        
                        v2[0] = x;
                        v2[1] = y;
                        
                        v2.sub(a);
                        
                        var c = v1[1]*v2[0] - v1[0]*v2[1];
                        
                        if (c < 0) {
                            //ok = false;
                            //break;
                        }
                        
                        if (sum === undefined || c < sum) {
                            sum = c;
                        }
                    }
                    
                    //sum += 0.5*backlash
                    
                    if (ok && sum !== undefined) {
                        minret = minret === undefined ? sum : Math.max(sum, minret);
                    }
              }
              
              //*
              var f = cutout(x, y);
              if (minret === undefined || f > minret) {
                  minret = f;
              }
              //*/
              
              return minret === undefined ? 1.0 : (3 * minret / width) + 0*backlash;
          }
          
          var size = this.size;
          var data = this.image.data, fdata = this.fdata;
          var xscale = width*4;
          var yscale = width*4;
          
          for (var i=0; i<size; i++) {
              for (var j=0; j<size; j++) {
                  var p = this.unproject(i, j);
                  
                  var df = 0.05;
                  
                  var c = inside(p[0], p[1]);
                  fdata[j*size + i] = c;
                  
                  c = Math.abs(c);
                  
                  c = ~~(c*255);
                  var idx = (j*size + i)*4;
                  
                  data[idx] = c;
                  data[idx+1] = c;
                  data[idx+2] = c;
                  data[idx+3] = 255;
              }
          }
      }
      
      //factor is optional, 1.0
      smooth(mesh, factor) {
          factor = factor === undefined ? 1.0 : factor;
          
          var cos = []
          var i = 0;
          
          for (var v of mesh.verts) {
              cos.push(new Vector3(v));
              v.index = i;
              
              i++;
          }
          
          let tmp = new Vector3();
          
          for (var v of mesh.verts) {
              if (v.edges.length != 2) {
                  continue;
              }
              
              var tot = 0;
              v.zero();
              
              for (var e of v.edges) {
                  var v2 = e.otherVertex(v);
                  
                  tot++;
                  v.add(cos[v2.index]);
              }
              
              v.divScalar(tot);
              
              tmp.load(cos[v.index]).interp(v, factor);
              v.load(tmp);
          }
      }
      
      run() {
          var newmesh = _appstate.mesh = this.mesh = new mesh.Mesh();
          this.profile.genRadius();
          
          var width = this.profile.modulus; //teeth width
          var depth = this.profile.depth
          
          var numteeth = this.profile.numteeth;
          var pressureth = this.profile.pressureth;
          var size = this.size;
          
          var radius = this.radius = this.profile.radius;
          
          this.makeField();
          this.implicit2lines();
          
          for (var i=0; i<5; i++) {
            this.smooth(newmesh);
          }
          
          function collapse() {
              var vec1 = new Vector2();
              var vec2 = new Vector2();
              var tmp = new Vector2();
              var dellist = []
              
              for (var v of newmesh.verts) {
                  if (v.edges.length != 2) {
                      continue;
                  }
                  
                  var v1 = v.edges[0].otherVertex(v);
                  var v2 = v;
                  var v3 = v.edges[1].otherVertex(v);
                  
                  //find distance of v2 to edge between v1 and v3
                  var v4 = tmp.load(v1).add(v2).mulScalar(0.5);
                  
                  vec1.load(v1).sub(v2).normalize();
                  vec2.load(v3).sub(v2).normalize();
                  
                  var err = v2.vectorDistance(v4); //vec1.dot(vec2);
                  var dot = vec1.dot(vec2);
                  
                  //take angle into account too
                  //err *= (1.0-Math.abs(dot))*0.3+0.7;
                  
                  //collapse, if small enough
                  if (Math.abs(err) < 0.05) {
                      dellist.push(v);
                      newmesh.makeEdge(v1, v3);
                  }
              }
              
              for (var v of dellist) {
                  newmesh.killVertex(v);
              }
          }
          
          for (var i=0; i<10; i++) {
            collapse();
          }
          
          var this2 = this;
          function mirror() {
              //tag original geometry
              for (var v of newmesh.verts) {
                  v.tag = 1;
              }
              
              //*
              //mirror
              var vmap = {}
              var connectv = undefined;
              for (var v of newmesh.verts) {
                  if (v.edges.length == 1) {
                    if (connectv === undefined || Math.abs(v[0]) < Math.abs(connectv[0])) {
                        connectv = v;
                    }
                }
              }
              
              for (var v of newmesh.verts) {
                if (v.tag != 1) {
                    continue;
                }
                
                var v2 = newmesh.makeVertex(v);
                vmap[v.eid] = v2;
                
                v2[0] = -v2[0];
                v2.tag = 2;
                
                if (v === connectv) {
                    newmesh.makeEdge(v, v2);
                }
              }
              
              //mirror over edges
              for (var e of newmesh.edges) {
                  e.tag = 1;
                  
                  var v1 = vmap[e.v1.eid];
                  var v2 = vmap[e.v2.eid];
                  
                  if (v1 === undefined || v2 === undefined) {
                      //this should only happen once, because of the "if (v === connectv)" block above to bridge the two sides
                      continue;
                  }
                  
                  newmesh.makeEdge(v1, v2);
              }
              //*/
              
              //now, sort profile
              
              //find the end that's an original vertex
              var startv = undefined;

              for (var v of newmesh.verts) {
                  if (v.tag == 1 && v.edges.length == 1) {
                      startv = v;
                      break;
                  }
              }
              
              //walk
              var v = startv, e = v.edges[0];
              var _i = 0; //infinite loop guard
              var sortlist = this2.sortlist = [];
              
              while (1) {
                  sortlist.push(v);
                  
                  v = e.otherVertex(v);
                  
                  if (v.edges.length == 1) {
                    sortlist.push(v);
                    break;  
                  } else {              
                    e = v.otherEdge(e);
                  }
                  
                  if (_i++ > 100000) {
                      console.log("Infinite loop detected!");
                      break;
                  }
              }
              
              //re-tag mirrored geometry as original
              for (var v of newmesh.verts) {
                  v.tag = 1;
              }              
              
              return sortlist;
          }
          
          var sortlist = mirror();
          //*/
          
          this.applyBacklash(newmesh, sortlist);
          
          //*
          var steps = this.profile.numteeth;
          var dth = (Math.PI*2) / (steps), th = 0;
          var lastv = undefined;
          var firstv = undefined;
          
          for (var i=0; i<steps; i++) {              
              for (var v of sortlist) {
                  var v2 = newmesh.makeVertex(v);
                  
                  var x = v2[0], y = v2[1];
                  
                  v2[0] = Math.cos(th)*x + Math.sin(th)*y;
                  v2[1] = Math.cos(th)*y - Math.sin(th)*x;
                  v2.tag = 2;
                  
                  if (lastv !== undefined) {
                      newmesh.makeEdge(lastv, v2);
                  } else {
                      firstv = v2;
                  }
                  
                  lastv = v2;
              }
              
              th += dth;
          }
          
          //destroy original template
          for (var v of sortlist) {
              newmesh.killVertex(v);
          }
          newmesh.makeEdge(firstv, lastv)
          //*/
          
          for (var v of newmesh.verts) {
              if (window.GRAPHICAL_TEST_MODE) {
                v.mulScalar(40).addScalar(350.4);
              }
              v[2] = 0;
          }
          /*
          var x = 0, y = radius-depth/2;
          var p = project(x, y);
          var ix = ~~p[0], iy = ~~p[1];
          
          console.log(ix, iy, x, y);
          
          var circ = util.searchoff(12);
          for (var off of circ) {
              var ix2 = off[0] + ix;
              var iy2 = off[1] + iy;
              
              if (ix2 < 0 || iy2 < 0 || ix2 >= size || iy2 >= size) {
                  continue;
              }
              
              var idx = (iy2*size + ix2)*4;
              
              data[idx] = 255;
              data[idx+1] = 0;
              data[idx+2] = 0;
              data[idx+3] = 255;
          }
          //*/
          
          this.smooth(newmesh, 0.5);
          
          window.redraw_all();
      }
  
  checkMesh(mesh, sortlist) {
    if (sortlist.length == 0) {
      return;
    }
    
outer:
    for (let e1 of mesh.edges) {
      for (let e2 of mesh.edges) {
        let skip = e1 == e2;
        
        skip = skip || e1.v1 === e2.v1 || e1.v2 === e2.v2;
        skip = skip || e1.v1 === e2.v2 || e1.v2 === e2.v1;
        
        if (skip) {
          continue;
        }
        
        if (math.line_line_cross(e1.v1, e1.v2, e2.v1, e2.v2)) {
          console.log("isect");
          
          //find "ear" loop to cut off
          //note that we'll add a new vertex at the intersection
          let vlist = [], elist = [];
          let prevv = undefined, nextv = undefined;
          let ok = false;
          
          //there are two directions to search in, have to try both
          for (let i=0; i<2; i++) {
            vlist.length = 0;
            elist.length = 0;
            
            let v = i ? e1.v2 : e1.v1, e = e1;
            let _i = 0;
            
            vlist.push(v);
            elist.push(e);
            
            while (1) {
              v = e.otherVertex(v);
              vlist.push(v);
              
              if (v === e2.v1 || v === e2.v2) {
                ok = true;
                break;
              }
              
              if (v.edges.length != 2) {
                break;
              }
              
              e = v.otherEdge(e);
              elist.push(e);
              
              if (_i++ > 100000) {
                console.warn("Infinite loop error");
                break;
              }
            }
            
            if (ok) {
              break;
            }
          }
          
          if (!ok) {
            vlist.length = elist.length = 0;
          } else {
            let getadj = (v, e) => {
              if (v.edges.length != 2) {
                return undefined;
              }
              
              e = v.otherEdge(e);
              return e.otherVertex(v);
            }
            
            prevv = getadj(vlist[0], elist[0]);
            nextv = getadj(vlist[vlist.length-1], elist[elist.length-1]);
          }
          
          if (prevv === undefined || nextv === undefined) {
            continue;
          }
          
          let isect = math.line_line_isect(e1.v1, e1.v2, e2.v1, e2.v2);
          
          let nv = mesh.makeVertex(isect);
          
          let v1 = e1.v1, v2 = e1.v2, v3 = e2.v1, v4 = e2.v2;
          
          for (let v of vlist) {
              mesh.killVertex(v); 
          }
          
          mesh.makeEdge(prevv, nv);
          mesh.makeEdge(nv, nextv);
          continue outer;
        }
      }
    }
    
    this.genSortList(mesh, sortlist[0], sortlist);
  }
  
  //sortlist is optional, array to reuse
  genSortList(mesh, startv1, sortlist) {
    sortlist = sortlist === undefined ? [] : sortlist;
    
    let v1 = startv1;
    let e1 = v1.edges[0];
    let _i = 0;
    
    sortlist.length = 0;
    while (1) {
      sortlist.push(v1);
      
      v1 = e1.otherVertex(v1);
      
      if (v1.edges.length != 2) {
        break;
      }
      
      e1 = v1.otherEdge(e1);
      
      if (_i++ > 100000) {
        console.warn("infinite loop detected");
        break;
      }
    }
    
    sortlist.push(v1);
    
    return sortlist;
  }
  
  applyBacklash(mesh, sortlist) {
    var norm = new Vector2();
    var tmp1 = new Vector2(), tmp2 = new  Vector2();
    
    if (sortlist.length < 2) {
        return;
    }
    
    var newcos = []
    var sign = this.profile.inner_gear_mode ? -1 : 1;
    
    let steps = 1;
    let dist = this.profile.backlash / steps;
    
    for (let si=0; si<steps; si++) {
      for (let i=0; i<sortlist.length; i++) {
          let v = sortlist[i];
          
          if (i == 0) {
              norm.load(sortlist[1]).sub(v).normalize();
          } else if (i == sortlist.length - 1 && v.edges.length == 1) {
              norm.load(v).sub(sortlist[i-1]).normalize();
          } else {
              var v2 = sortlist[(i - 1)];
              var v3 = sortlist[(i + 1) % sortlist.length];
              
              tmp1.load(v).sub(v2);
              tmp2.load(v3).sub(v);
              
              norm.load(tmp1).add(tmp2).normalize();
          }
          
          let t = norm[0]; norm[0] = norm[1]; norm[1] = -t;
          
          norm.mulScalar(sign*dist);
          
          newcos.push(new Vector2(v).add(norm));
      }
      
      for (let i=0; i<sortlist.length; i++) {
          sortlist[i].load(newcos[i]);
      }
      
      this.smooth(mesh, 0.5);
      this.checkMesh(mesh, sortlist);
      
      newcos.length = 0;
    }
  }
  
  implicit2lines() {
      var width = this.profile.modulus; //teeth width
      var depth = this.profile.depth
      var radius = this.radius, fdata = this.fdata, size = this.size;
      var numteeth = this.profile.numteeth;
      var newmesh = this.mesh;
      
      var offs = [
        [0, 1],
        [1, 1],
        [1, 0]
      /*
        [-1, -1],
        [0, -1],
        [1, -1], 
        
        [1, 0],
        [1, 1],
        [0, 1],
        
        [-1, 1]
        [-1, 0]
        */
      ];
      
      var mids = [
        [[0, 0.5], [0.5, 1]], //1
        [[0.5, 1], [1, 0.5]], //2
        [[1, 0.5], [0.5, 0]], //4
        [[0.5, 0], [0, 0.5]], //8
        [[0, 0.5], [1, 0.5]], //16
        [[0.5, 0], [0.5, 1]], //32
        [[0, 0], [1, 1]],     //64
        [[0, 0.5], [0.5, 0]]  //128
      ];
      
      var masktable = [
        0,
        1,
        2,
        16,
        4,
        64,
        32,
        128
      ];
      
      var v1 = new Vector2(), v2 = new Vector2();
      var vhash = {};
      
      function getvert(co) {
        var hash = co[0] + "," + co[1];

        if (hash in vhash) {
            return vhash[hash];
        } else {
            vhash[hash] = newmesh.makeVertex(co);
            return vhash[hash];
        }
      }
      
      for (var ix=2; ix<size/2; ix++) {
          for (var iy=2; iy<size-2; iy++) {
              var s = fdata[iy*size + ix];
              
              var table = []
              var mask = 0;
              
              for (var i=0; i<offs.length; i++) {
                  var ix2 = ix + offs[i][0], iy2 = iy + offs[i][1];
                  var s2 = fdata[iy2*size + ix2];
                  
                  if (s == 0 || s2 == 0) {
                      continue;
                  }
                   
                  if ((s > 0.0) != (s2 > 0.0)) { //(Math.sign(s) != Math.sign(s2)) {
                      mask |= 1<<i;
                  }
              }
              
              var lines = masktable[mask];
              
              for (var i=0; i<mids.length; i++) {
                  var l = mids[i];
                  
                  if (lines & (1<<i)) {
                      var x1 = ix + l[0][0], y1 = iy + l[0][1];
                      var x2 = ix + l[1][0], y2 = iy + l[1][1];
                      
                      v1[0] = x1, v1[1] = y1;
                      v2[0] = x2, v2[1] = y2;
                      
                      v1.load(this.unproject(v1[0], v1[1]));
                      v2.load(this.unproject(v2[0], v2[1]));
                      
                      var mv1 = getvert(v1);
                      var mv2 = getvert(v2);
                      newmesh.makeEdge(mv1, mv2);
                  }
              }
          }
      }
  }

  };
  
  return exports;
});
