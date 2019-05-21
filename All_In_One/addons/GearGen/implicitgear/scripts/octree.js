"use strict";

//note to self: I think this might be an older version
//todo: update to newer (read: less buggy) one.

var LEAF_LIMIT = 8

class OcNode {
  constructor(Array<float> min, Array<float> max) {
    this.children = new GArray();
    this.data = undefined;
    this.idata = undefined;
    
    this.leaf = false;
    this._ret = [0, [0, 0, 0]]; //cached return for .isect_ray
    
    this.min = new Vector3(min);
    this.max = new Vector3(max);

    this.cent = new Vector3(max).add(min).mulScalar(0.5);
    this.halfsize = new Vector3(max).sub(min).mulScalar(0.5);
    
    this.id = undefined;
  }
  
  isect_ray(Array<float> co, Array<float> dir) {
    if (this.children.length == 0) {
      var data = this.data;
      var idata = this.idata;
      var ilen = Math.floor(data.length/3);
      
      var ret = undefined;
      var t = 0;
      var reti = 0;
      
      for (var i=0; i<ilen; i++) {
        var ret2 = ray_tri_isect(co, dir, data[i*3], data[i*3+1], data[i*3+2]);
        if (ret2 != undefined && (ret==undefined || (ret[0]>0 && ret[0]<t))) {
          //console.log("yay, tri ray isect");
          
          ret = ret2;
          reti = i;
          t = ret[0];
        }
      }
      
      if (ret == undefined) return undefined;
      
      var ret2 = this._ret;
      ret2[0] = idata[reti];
      ret2[1][0] = ret[0];
      ret2[1][1] = ret[1];
      ret2[1][2] = ret[2];
      
      return ret2;
    } else {
      var ret = undefined;
      var t;
      
      for (var c of this.children) {
        if (aabb_ray_isect(co, dir, c.min, c.max)) {
          var ret2 = c.isect_ray(co, dir);
          if (ret2 == undefined) continue;
          
          //console.log("t:", ret2[1][0]);
          if (ret == undefined || (ret2[1][0] > 0 && ret2[1][0] < t)) {
            ret = ret2;
            t = ret[1][0];
          }
        }
      }
      
      return ret;
    }
  }
  
  split() {
    if (this.children.length > 0)
      return;
    
    this.leaf = false;
    
    static csize = new Vector3();
    static min = new Vector3();
    static max = new Vector3();
    var omin = this.min;
    
    csize.load(this.halfsize);
    
    for (var x=0; x<2; x++) {
      min[0] = omin[0]+csize[0]*x;
      for (var y=0; y<2; y++) {
        min[1] = omin[1]+csize[1]*y;
        for (var z=0; z<2; z++) {
          min[2] = omin[2]+csize[2]*z;
          
          max.load(min).add(csize);
          
          var c = new OcNode(min, max);
          
          c.leaf = true;
          c.data = new GArray();
          c.idata = new GArray();
          
          this.children.push(c);
        }
      }
    }
    
    var data = this.data;
    var idata =  this.idata
    this.data = undefined;
    this.idata = undefined;
    
    var v1 = new Vector3(), v2 = new Vector3(), v3 = new Vector3();
    var ilen = Math.floor(data.length/3);
    
    for (var i=0; i<ilen; i++) {
      v1.load(data[i*3]); v2.load(data[i*3+1]); v3.load(data[i*3+2]);
      this.add_tri(v1, v2, v3, idata[i]);
    }
  }
  
  add_tri(Array<float> v1, Array<float> v2, Array<float> v3, int idx) {
    static tris = [0, 0, 0];
    
    tris[0] = v1, tris[1] = v2, tris[2] = v3;
    for (var c of this.children) {
      if (triBoxOverlap(c.cent, c.halfsize, tris)) {
        c.add_tri(v1, v2, v3, idx);
        return;
      }
    }
    
    if (this.data == undefined) {
      console.log("evil in octree!");
      return;
    }
    
    this.data.push(new Vector3(v1));
    this.data.push(new Vector3(v2));
    this.data.push(new Vector3(v3));
    this.idata.push(idx);
    
    if (this.data.length*0.33 > LEAF_LIMIT) {
      this.split();
    }
  }
}

class OcTree {
  constructor(Array<float> min, Array<float> max) {
    this.min = new Vector3(min);
    this.max = new Vector3(max);
    
    this.root = new OcNode(min, max);
    this.root.leaf = true;
    this.root.data = new GArray();
    this.root.idata = new GArray();
  }
    
  add_tri(Array<float> v1, Array<float> v2, Array<float> v3, int idx) {
    this.root.add_tri(v1, v2, v3, idx);
  }
  
  isect_ray(Array<float> co, Array<float> dir) : Array<Array<float>> {
    return this.root.isect_ray(co, dir);
  }
}

function build_octree(Mesh mesh) : Octree {
  if (mesh.looptris == undefined) {
    gen_tris(mesh);
  }
  
  if (mesh.looptris == undefined) {
    console.trace();
    console.log("could not build octree");
    
    return new Octree([-1, -1, -1], [1, 1, 1]);
  }
  
  var mm = new MinMax(3);
  var use_mapco = mesh.flag & MeshFlags.USE_MAP_CO;
  
  for (var v of mesh.verts) {
    if (use_mapco)
      mm.minmax(v.mapco);
    else
      mm.minmax(v.co);
  }
  
  var min = new Vector3(mm.min);
  var max = new Vector3(mm.max);
  
  var cent = new Vector3(mm.max).add(mm.min).mulScalar(0.5);
  
  min.sub(cent);
  min.mulScalar(1.25);
  min.add(cent);
  
  max.sub(cent);
  max.mulScalar(1.25);
  max.add(cent);
  
  var octree = new OcTree(min, max);
  var ilen = Math.floor(mesh.looptris.length/3);
  var ls = mesh.looptris;
  
  if (mesh.flag & MeshFlags.USE_MAP_CO) {
    for (var i=0; i<ilen; i++) {
      octree.add_tri(ls[i*3].v.mapco, ls[i*3+1].v.mapco, ls[i*3+2].v.mapco, ls[i*3].f.eid);
    }
  } else {
    for (var i=0; i<ilen; i++) {
      octree.add_tri(ls[i*3].v.co, ls[i*3+1].v.co, ls[i*3+2].v.co, ls[i*3].f.eid);
    }
  }
  
  return octree;
}


function build_octree_ss(Mesh mesh) : Octree {
  var mm = new MinMax(3);

  for (var v of mesh.verts) {
    mm.minmax(v.co);
  }
  
  var min = new Vector3(mm.min);
  var max = new Vector3(mm.max);
  
  var cent = new Vector3(mm.max).add(mm.min).mulScalar(0.5);
  
  min.sub(cent);
  min.mulScalar(1.25);
  min.add(cent);
  
  max.sub(cent);
  max.mulScalar(1.25);
  max.add(cent);
  
  var octree = new OcTree(min, max);
  for (var f of mesh.faces) {
    if (f.old_face == undefined) continue;
    var idx = f.old_face.eid;
    
    var l = f.looplists[0].loop;
    
    octree.add_tri(l.v.co, l.next.v.co, l.next.next.v.co, idx);
    octree.add_tri(l.v.co, l.next.next.v.co, l.next.next.next.v.co, idx);
  }
  
  return octree;
}
