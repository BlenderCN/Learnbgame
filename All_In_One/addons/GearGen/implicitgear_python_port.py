var _implicitgear = None; #for debugging purposes only.  don't write code with it

define([
  "util", "mesh", "const", "vectormath", "math"
], def(util, mesh, cconst, vectormath, math)
:
  'use strict';
  
    class Profile:  
      __init__(self, numteeth):
          self.pressureth = (20 / 180) * Math.PI;
          self.backlash = 0.1;
          self.modulus = 2.0; #teeth width
          self.depth = (self.modulus * 2 / Math.PI);
          self.numteeth = numteeth;
          self.genRadius();
          self.inner_gear_mode = false;
          
          self._dx = Math.sin(self.pressureth)*self.depth;
          self._dy = Math.cos(self.pressureth)*self.depth;
      }
      
      def genRadius(self):
          self.radius = (self.modulus * 2 * self.numteeth) / Math.PI / 2;
      }
      
      def hash(self):
          self.genRadius();
          
          return "%.5f,%.5f,%.5f,%i,%.5f,%i" % (self.depth, self.pressureth, self.modulus, self.numteeth, self.backlash, self.inner_gear_mode)
          
          #return self.depth.toFixed(5) + "," + self.pressureth.toFixed(5) + "," + self.modulus.toFixed(5) + "," + self.numteeth +
          #       "," + self.backlash.toFixed(5) + "," + self.inner_gear_mode;
      }
  };
  
  class ImplicitGear:
      #g is a Canvas2DContext
      __init__(self, g, profile):
          self.size = 128;
          self.image = new ImageData(new Uint8ClampedArray(self.size*self.size*4), self.size, self.size);
          
          self.profile = profile;
          
          profile.backlash *= 0.25;
          profile.backlash -= 0.0125; #magic number! have to do this for some reason
          
          ilen = self.size*self.size*4;
          data = self.image.data;
          
          for (var i=3; i<ilen; i += 4):
              data[i] = 255;
          }
          
          self.fdata = new Float32Array(self.size*self.size);
          self.fdata.fill(1.0, 0, self.fdata.length);
          
          self.projscale = self.profile.modulus*2.0;
          self._unprojxy_tmp = cachering.fromConstructor(Vector2, 64);
          self._projxy_tmp = cachering.fromConstructor(Vector2, 64);
      }
      
      unproject(ix, iy):
          ret = self._unprojxy_tmp.next().zero();
          
          size = self.size
          radius = self.radius
          projscale = self.projscale
          
          ret[0] = ix / size - 0.5;
          ret[1] = (size - iy) / size - 0.5;
          
          ret[0] *= projscale;
          ret[1] *= projscale;

          ret[1] += radius;
          
          return ret;
      }
      
      project(x, y):
          p = self._projxy_tmp.next();
          size = self.size, radius = self.radius, projscale = self.projscale;

          p[0] = x, p[1] = y;
          
          p[1] -= radius;
          p[0] /= projscale;
          p[1] /= projscale;
          
          p[0] = (p[0] + 0.5) * size;
          p[1] = size * (0.5 - p[1]);
          
          return p;
      }
      
      makeField():
          traps = [];
          
          backlash = self.profile.backlash
          width = self.profile.modulus; #teeth width
          depth = self.profile.depth
          
          numteeth = self.profile.numteeth;
          pressureth = self.profile.pressureth;
          
          radius = self.radius = self.profile.radius;
          inner_gear = self.profile.inner_gear_mode;
          
          def trap() { #trap is short for trapezoid
              width2 = width*0.5;
              
              tanfac = Math.tan(pressureth)*depth;
              
              a = 0.5
              b = 1.0 - a;
              y = 0;
              
              t = [
                new Vector2([-width2+a*tanfac, y]),
                new Vector2([-width2-b*tanfac, y+depth]),
                new Vector2([width2+b*tanfac, y+depth]),
                new Vector2([width2-a*tanfac, y])
              ];
              
              traps.push(t);
              
              return t;
          }
          
          def rot(t, th):
              for (v of t):
                  v.rot2d(th);
              }
          }
          
          def trans(t, offx, offy):
              for (v of t):
                  v[0] += offx;
                  v[1] += offy;
              }
          }
          
          dvel = width*2 #* numteeth*2;
          dth = dvel / radius;
          
          rackx = -dvel;
          
          steps = 32;
          dth2 = dth / steps;
          dvel2 = dvel / steps;
          th = (width) / radius;
          
          if (window.GRAPHICAL_TEST_MODE):
              console.log("pitch:", radius);
          }
          
          for i in range(steps):
            dx = rackx
            dy = radius
            
            dx = (rackx) % (width*2) + width
            t = trap()
           
            trans(t, -dx, dy - depth*0.5);
            rot(t, th);
            
            rackx += dvel2;
            th -= dth2;
          }
          
          '''
          on factor;
          off period;
          '''
          itmp1 = new Vector2();
          itmp2 = new Vector2();
          itmp3 = new Vector2();
          
          def cutout(x, y):
              cutradius = width*0.35
              
              rx = 0
              ry = radius - depth*0.35;
              
              x -= rx
              y -= ry
              
              d = x*x + y*y;
              
              if (d == 0):
                  return 0;
              }
              
              d = Math.sqrt(d);
              
              return cutradius-d;
          }
          
          itmp = new Vector2();
          def inside(x, y):
              minret = None;
              
              if (inner_gear):
                  r2 = Math.sqrt(x*x + y*y);
                  
                  r2 -= radius;# - depth*0.5;
                  #r2 = depth - r2;
                  r2 = -r2;
                  r2 += radius;# - depth*0.5;
                  
                  itmp[0] = x, itmp[1] = y;
                  itmp.normalize().mulScalar(r2);
                  
                  x = itmp[0], y = itmp[1];
              }
              
              r = radius + depth*0.5;
              if (x*x + y*y > r*r):
                  return 1;
              }
              
              for (t of traps):
                    sum = None;
                    
                    ok = true;
                    
                    for i in range(4):
                        a = t[i]
                        b = t[(i+1)%t.length];
                            
                        v1 = itmp1.zero();
                        v2 = itmp2.zero();
                        
                        v1.load(b).sub(a).normalize();
                        
                        v2[0] = x;
                        v2[1] = y;
                        
                        v2.sub(a);
                        
                        c = v1[1]*v2[0] - v1[0]*v2[1];
                        
                        if (c < 0):
                            #ok = false;
                            #break;
                        }
                        
                        if (sum === None or c < sum):
                            sum = c;
                        }
                    }
                    
                    #sum += 0.5*backlash
                    
                    if (ok and sum !== None):
                        minret = minret === None ? sum: Math.max(sum, minret);
                    }
              }
              
              #*
              f = cutout(x, y);
              if (minret === None or f > minret):
                  minret = f;
              }
              #'''
              
              return minret === None ? 1.0: (3 * minret / width) + 0*backlash;
          }
          
          size = self.size;
          data = self.image.data
          fdata = self.fdata;
          xscale = width*4;
          yscale = width*4;
          
          for i in range(size):
              for j in range(size):
                  p = self.unproject(i, j);
                  
                  df = 0.05;
                  
                  c = inside(p[0], p[1]);
                  fdata[j*size + i] = c;
                  
                  c = Math.abs(c);
                  
                  c = ~~(c*255);
                  idx = (j*size + i)*4;
                  
                  data[idx] = c;
                  data[idx+1] = c;
                  data[idx+2] = c;
                  data[idx+3] = 255;
              }
          }
      }
      
      #factor is optional, 1.0
      smooth(mesh, factor):
          factor = factor === None ? 1.0: factor;
          
          cos = []
          i = 0;
          
          for (v of mesh.verts):
              cos.push(new Vector3(v));
              v.index = i;
              
              i++;
          }
          
          let tmp = new Vector3();
          
          for (v of mesh.verts):
              if (v.edges.length != 2):
                  continue;
              }
              
              tot = 0;
              v.zero();
              
              for (e of v.edges):
                  v2 = e.otherVertex(v);
                  
                  tot++;
                  v.add(cos[v2.index]);
              }
              
              v.divScalar(tot);
              
              tmp.load(cos[v.index]).interp(v, factor);
              v.load(tmp);
          }
      }
      
      run():
          newmesh = new mesh.Mesh()
          self.mesh = newmesh
          _appstate.mesh = newmesh
          
          self.profile.genRadius();
          
          width = self.profile.modulus; #teeth width
          depth = self.profile.depth
          
          numteeth = self.profile.numteeth;
          pressureth = self.profile.pressureth;
          size = self.size;
          
          self.radius = self.profile.radius;
          radius = self.radius
          
          self.makeField();
          self.implicit2lines();
          
          for i in range(5):
            self.smooth(newmesh);
          }
          
          def collapse():
              vec1 = new Vector2();
              vec2 = new Vector2();
              tmp = new Vector2();
              dellist = []
              
              for (v of newmesh.verts):
                  if (v.edges.length != 2):
                      continue;
                  }
                  
                  v1 = v.edges[0].otherVertex(v);
                  v2 = v;
                  v3 = v.edges[1].otherVertex(v);
                  
                  #find distance of v2 to edge between v1 and v3
                  v4 = tmp.load(v1).add(v2).mulScalar(0.5);
                  
                  vec1.load(v1).sub(v2).normalize();
                  vec2.load(v3).sub(v2).normalize();
                  
                  err = v2.vectorDistance(v4); #vec1.dot(vec2);
                  dot = vec1.dot(vec2);
                  
                  #take angle into account too
                  #err *= (1.0-Math.abs(dot))*0.3+0.7;
                  
                  #collapse, if small enough
                  if (Math.abs(err) < 0.05):
                      dellist.push(v);
                      newmesh.makeEdge(v1, v3);
                  }
              }
              
              for (v of dellist):
                  newmesh.killVertex(v);
              }
          }
          
          for i in range(10):
            collapse();
          }
          
          var self2 = self;
          def mirror():
              #tag original geometry
              for (v of newmesh.verts):
                  v.tag = 1;
              }
              
              #*
              #mirror
              vmap = {}
              connectv = None;
              for (v of newmesh.verts):
                  if (v.edges.length == 1):
                    if (connectv === None or Math.abs(v[0]) < Math.abs(connectv[0])):
                        connectv = v;
                    }
                }
              }
              
              for (v of newmesh.verts):
                if (v.tag != 1):
                    continue;
                }
                
                v2 = newmesh.makeVertex(v);
                vmap[v.eid] = v2;
                
                v2[0] = -v2[0];
                v2.tag = 2;
                
                if (v === connectv):
                    newmesh.makeEdge(v, v2);
                }
              }
              
              #mirror over edges
              for (e of newmesh.edges):
                  e.tag = 1;
                  
                  v1 = vmap[e.v1.eid];
                  v2 = vmap[e.v2.eid];
                  
                  if (v1 === None or v2 === None):
                      #this should only happen once, because of the "if (v === connectv)" block above to bridge the two sides
                      continue;
                  }
                  
                  newmesh.makeEdge(v1, v2);
              }
              #'''
              
              #now, sort profile
              
              #find the end that's an original vertex
              startv = None;

              for (v of newmesh.verts):
                  if (v.tag == 1 and v.edges.length == 1):
                      startv = v;
                      break;
                  }
              }
              
              #walk
              v = startv, e = v.edges[0];
              _i = 0; #infinite loop guard
              sortlist = self2.sortlist = [];
              
              while (1):
                  sortlist.push(v);
                  
                  v = e.otherVertex(v);
                  
                  if (v.edges.length == 1):
                    sortlist.push(v);
                    break;  
                  } else {              
                    e = v.otherEdge(e);
                  }
                  
                  if (_i++ > 100000):
                      console.log("Infinite loop detected!");
                      break;
                  }
              }
              
              #re-tag mirrored geometry as original
              for (v of newmesh.verts):
                  v.tag = 1;
              }              
              
              return sortlist;
          }
          
          sortlist = mirror();
          #'''
          
          self.applyBacklash(newmesh, sortlist);
          
          #*
          steps = self.profile.numteeth;
          dth = (Math.PI*2) / (steps)
          th = 0;
          lastv = None;
          firstv = None;
          
          for i in range(steps):
              for (var v of sortlist):
                  v2 = newmesh.makeVertex(v);
                  
                  x = v2[0]
                  y = v2[1];
                  
                  v2[0] = Math.cos(th)*x + Math.sin(th)*y;
                  v2[1] = Math.cos(th)*y - Math.sin(th)*x;
                  v2.tag = 2;
                  
                  if (lastv !== None):
                      newmesh.makeEdge(lastv, v2);
                  } else:
                      firstv = v2;
                  }
                  
                  lastv = v2;
              }
              
              th += dth;
          }
          
          #destroy original template
          for (v of sortlist):
              newmesh.killVertex(v);
          }
          newmesh.makeEdge(firstv, lastv)
          #'''
          
          for (v of newmesh.verts):
              if (window.GRAPHICAL_TEST_MODE):
                v.mulScalar(40).addScalar(350.4);
              }
              v[2] = 0;
          }
          '''
          var x = 0, y = radius-depth/2;
          var p = project(x, y);
          var ix = ~~p[0], iy = ~~p[1];
          
          console.log(ix, iy, x, y);
          
          var circ = util.searchoff(12);
          for (var off of circ):
              var ix2 = off[0] + ix;
              var iy2 = off[1] + iy;
              
              if (ix2 < 0 or iy2 < 0 or ix2 >= size or iy2 >= size):
                  continue;
              }
              
              var idx = (iy2*size + ix2)*4;
              
              data[idx] = 255;
              data[idx+1] = 0;
              data[idx+2] = 0;
              data[idx+3] = 255;
          }
          #'''
          
          self.smooth(newmesh, 0.5);
          
          window.redraw_all();
      }
  
  checkMesh(mesh, sortlist):
    if (sortlist.length == 0):
      return;
    }
    
outer:
    for (let e1 of mesh.edges):
      for (let e2 of mesh.edges):
        let skip = e1 == e2;
        
        skip = skip or e1.v1 === e2.v1 or e1.v2 === e2.v2;
        skip = skip or e1.v1 === e2.v2 or e1.v2 === e2.v1;
        
        if (skip):
          continue;
        }
        
        if (math.line_line_cross(e1.v1, e1.v2, e2.v1, e2.v2)):
          console.log("isect");
          
          #find "ear" loop to cut off
          #note that we'll add a new vertex at the intersection
          let vlist = [], elist = [];
          let prevv = None, nextv = None;
          let ok = false;
          
          #there are two directions to search in, have to try both
          for (let i=0; i<2; i++):
            vlist.length = 0;
            elist.length = 0;
            
            let v = i ? e1.v2: e1.v1, e = e1;
            let _i = 0;
            
            vlist.push(v);
            elist.push(e);
            
            while (1):
              v = e.otherVertex(v);
              vlist.push(v);
              
              if (v === e2.v1 or v === e2.v2):
                ok = true;
                break;
              }
              
              if (v.edges.length != 2):
                break;
              }
              
              e = v.otherEdge(e);
              elist.push(e);
              
              if (_i++ > 100000):
                console.warn("Infinite loop error");
                break;
              }
            }
            
            if (ok):
              break;
            }
          }
          
          if (not k):
            vlist.length = elist.length = 0;
          } else:
            let getadj = (v, e) =>:
              if (v.edges.length != 2):
                return None;
              }
              
              e = v.otherEdge(e);
              return e.otherVertex(v);
            }
            
            prevv = getadj(vlist[0], elist[0]);
            nextv = getadj(vlist[vlist.length-1], elist[elist.length-1]);
          }
          
          if (prevv === None or nextv === None):
            continue;
          }
          
          let isect = math.line_line_isect(e1.v1, e1.v2, e2.v1, e2.v2);
          
          let nv = mesh.makeVertex(isect);
          
          let v1 = e1.v1, v2 = e1.v2, v3 = e2.v1, v4 = e2.v2;
          
          for (let v of vlist):
              mesh.killVertex(v); 
          }
          
          mesh.makeEdge(prevv, nv);
          mesh.makeEdge(nv, nextv);
          continue outer;
        }
      }
    }
    
    self.genSortList(mesh, sortlist[0], sortlist);
  }
  
  #sortlist is optional, array to reuse
  genSortList(mesh, startv1, sortlist):
    sortlist = sortlist === None ? []: sortlist;
    
    let v1 = startv1;
    let e1 = v1.edges[0];
    let _i = 0;
    
    sortlist.length = 0;
    while (1):
      sortlist.push(v1);
      
      v1 = e1.otherVertex(v1);
      
      if (v1.edges.length != 2):
        break;
      }
      
      e1 = v1.otherEdge(e1);
      
      if (_i++ > 100000):
        console.warn("infinite loop detected");
        break;
      }
    }
    
    sortlist.push(v1);
    
    return sortlist;
  }
  
  applyBacklash(mesh, sortlist):
    norm = new Vector2();
    tmp1 = new Vector2()
    tmp2 = new  Vector2();
    
    if (sortlist.length < 2):
        return;
    }
    
    newcos = []
    sign = self.profile.inner_gear_mode ? -1: 1;
    
    let steps = 1;
    let dist = self.profile.backlash / steps;
    
    for (let si=0; si<steps; si++):
      for (let i=0; i<sortlist.length; i++):
          let v = sortlist[i];
          
          if (i == 0):
              norm.load(sortlist[1]).sub(v).normalize();
          } else if (i == sortlist.length - 1 and v.edges.length == 1):
              norm.load(v).sub(sortlist[i-1]).normalize();
          } else:
              v2 = sortlist[(i - 1)];
              v3 = sortlist[(i + 1) % sortlist.length];
              
              tmp1.load(v).sub(v2);
              tmp2.load(v3).sub(v);
              
              norm.load(tmp1).add(tmp2).normalize();
          }
          
          let t = norm[0]; norm[0] = norm[1]; norm[1] = -t;
          
          norm.mulScalar(sign*dist);
          
          newcos.push(new Vector2(v).add(norm));
      }
      
      for (let i=0; i<sortlist.length; i++):
          sortlist[i].load(newcos[i]);
      }
      
      self.smooth(mesh, 0.5);
      self.checkMesh(mesh, sortlist);
      
      newcos.length = 0;
    }
  }
  
  implicit2lines():
      width = self.profile.modulus; #teeth width
      depth = self.profile.depth
      radius = self.radius
      fdata = self.fdata
      size = self.size;
      numteeth = self.profile.numteeth;
      newmesh = self.mesh;
      
      offs = [
        [0, 1],
        [1, 1],
        [1, 0]
      '''
        [-1, -1],
        [0, -1],
        [1, -1], 
        
        [1, 0],
        [1, 1],
        [0, 1],
        
        [-1, 1]
        [-1, 0]
        '''
      ];
      
      mids = [
        [[0, 0.5], [0.5, 1]], #1
        [[0.5, 1], [1, 0.5]], #2
        [[1, 0.5], [0.5, 0]], #4
        [[0.5, 0], [0, 0.5]], #8
        [[0, 0.5], [1, 0.5]], #16
        [[0.5, 0], [0.5, 1]], #32
        [[0, 0], [1, 1]],     #64
        [[0, 0.5], [0.5, 0]]  #128
      ];
      
      masktable = [
        0,
        1,
        2,
        16,
        4,
        64,
        32,
        128
      ];
      
      v1 = new Vector2()
      v2 = new Vector2();
      vhash = {};
      
      def getvert(co):
        hash = co[0] + "," + co[1];

        if (hash in vhash):
            return vhash[hash];
        } else:
            vhash[hash] = newmesh.makeVertex(co);
            return vhash[hash];
        }
      }
      
      for ix in range(2, int(size/2)):
        for iy in range(2, int(size-2)):
              s = fdata[iy*size + ix];
              
              table = []
              mask = 0;
              
              for i in range(len(offs)):
                  ix2 = ix + offs[i][0]
                  iy2 = iy + offs[i][1];
                  s2 = fdata[iy2*size + ix2];
                  
                  if (s == 0 or s2 == 0):
                      continue;
                  }
                   
                  if ((s > 0.0) != (s2 > 0.0)) { #(Math.sign(s) != Math.sign(s2)):
                      mask |= 1<<i;
                  }
              }
              
              lines = masktable[mask];
              
              for i in range(len(mids)):
                  l = mids[i];
                  
                  if (lines & (1<<i)):
                      x1 = ix + l[0][0]
                      y1 = iy + l[0][1];
                      x2 = ix + l[1][0]
                      y2 = iy + l[1][1];
                      
                      v1[0] = x1, v1[1] = y1;
                      v2[0] = x2, v2[1] = y2;
                      
                      v1.load(self.unproject(v1[0], v1[1]));
                      v2.load(self.unproject(v2[0], v2[1]));
                      
                      mv1 = getvert(v1);
                      mv2 = getvert(v2);
                      newmesh.makeEdge(mv1, mv2);
                  }
              }
          }
      }
  }

  };
  
  return exports;
});
