//handle to module.  never access in code; for debug console use only.
var _math = undefined;

define([
  "util", "vectormath"
], function(util, vectormath) {
  "use strict";
  
  //XXX refactor to use es6 classes,
  //    or at last the class system in typesystem.js
  function init_prototype(cls, proto) {
    for (var k in proto) {
      cls.prototype[k] = proto[k];
    }
    
    return cls.prototype;
  }
  
  function inherit(cls, parent, proto) {
    cls.prototype = Object.create(parent.prototype);
    
    for (var k in proto) {
      cls.prototype[k] = proto[k];
    }
    
    return cls.prototype;
  }
  
  var exports = _math = {};
  
  var Vector2 = vectormath.Vector2, Vector3 = vectormath.Vector3;
  var Vector4 = vectormath.Vector4, Matrix4 = vectormath.Matrix4;

  var set = util.set;

  //everything below here was compiled from es6 code  
  //variables starting with $ are function static local vars,
  //like in C.  don't use them outside their owning functions.
  //
  //except for $_mh and $_swapt.  they were used with a C macro
  //preprocessor.
  var $_mh, $_swapt;

  var feps=exports.feps = feps = 2.22e-16;

  var COLINEAR=exports.COLINEAR = COLINEAR = 1;
  var LINECROSS=exports.LINECROSS = LINECROSS = 2;
  var COLINEAR_ISECT=exports.COLINEAR_ISECT = COLINEAR_ISECT = 3;

  var _cross_vec1=new Vector3();
  var _cross_vec2=new Vector3();

  var SQRT2 = exports.SQRT2 = Math.sqrt(2);
  var FEPS_DATA = exports.FEPS_DATA = exports.FEPS_DATA = {
    F16 : 1.11e-16,
    F32 : 5.96e-08,
    F64 : 4.88e-04
  };

  /*use 32 bit epsilon by default, since we're often working from
    32-bit float data.  note that javascript uses 64-bit doubles 
    internally.*/
  var FEPS = exports.FEPS = FEPS_DATA.F32;
  var FLOAT_MIN=exports.FLOAT_MIN = FLOAT_MIN = -1e+21;
  var FLOAT_MAX=exports.FLOAT_MAX = FLOAT_MAX = 1e+22;
  var Matrix4UI=exports.Matrix4UI = Matrix4UI = Matrix4;

  /*
  var Matrix4UI=exports.Matrix4UI = function(loc, rot, size) {
    if (rot==undefined) {
        rot = undefined;
    }
    
    if (size==undefined) {
        size = undefined;
    }
    
    Object.defineProperty(this, "loc", {get: function() {
      var t=new Vector3();
      this.decompose(t);
      return t;
    }, set: function(loc) {
      var l=new Vector3(), r=new Vector3(), s=new Vector3();
      this.decompose(l, r, s);
      this.calc(loc, r, s);
    }});
    
    Object.defineProperty(this, "size", {get: function() {
      var t=new Vector3();
      this.decompose(undefined, undefined, t);
      return t;
    }, set: function(size) {
      var l=new Vector3(), r=new Vector3(), s=new Vector3();
      this.decompose(l, r, s);
      this.calc(l, r, size);
    }});
    
    Object.defineProperty(this, "rot", {get: function() {
      var t=new Vector3();
      this.decompose(undefined, t);
      return t;
    }, set: function(rot) {
      var l=new Vector3(), r=new Vector3(), s=new Vector3();
      this.decompose(l, r, s);
      this.calc(l, rot, s);
    }});
    
    if (loc instanceof Matrix4) {
        this.load(loc);
        return ;
    }
    
    if (rot==undefined)
      rot = [0, 0, 0];
    if (size==undefined)
      size = [1.0, 1.0, 1.0];
    this.makeIdentity();
    this.calc(loc, rot, size);
  };
  
  Matrix4UI.prototype = inherit(Matrix4UI, Matrix4, {
    calc : function(loc, rot, size) {
      this.rotate(rot[0], rot[1], rot[2]);
      this.scale(size[0], size[1], size[2]);
      this.translate(loc[0], loc[1], loc[2]);
    }

  });
  */
  
  if (FLOAT_MIN!=FLOAT_MIN||FLOAT_MAX!=FLOAT_MAX) {
      FLOAT_MIN = 1e-05;
      FLOAT_MAX = 1000000.0;
      console.log("Floating-point 16-bit system detected!");
  }

  var _static_grp_points4=new Array(4);
  var _static_grp_points8=new Array(8);
  var get_rect_points=exports.get_rect_points = function get_rect_points(p, size) {
    var cs;
    if (p.length==2) {
        cs = _static_grp_points4;
        cs[0] = p;
        cs[1] = [p[0]+size[0], p[1]];
        cs[2] = [p[0]+size[0], p[1]+size[1]];
        cs[3] = [p[0], p[1]+size[1]];
    }
    else 
      if (p.length==3) {
        cs = _static_grp_points8;
        cs[0] = p;
        cs[1] = [p[0]+size[0], p[1], p[2]];
        cs[2] = [p[0]+size[0], p[1]+size[1], p[2]];
        cs[3] = [p[0], p[1]+size[0], p[2]];
        cs[4] = [p[0], p[1], p[2]+size[2]];
        cs[5] = [p[0]+size[0], p[1], p[2]+size[2]];
        cs[6] = [p[0]+size[0], p[1]+size[1], p[2]+size[2]];
        cs[7] = [p[0], p[1]+size[0], p[2]+size[2]];
    }
    else {
      throw "get_rect_points has no implementation for "+p.length+"-dimensional data";
    }
    return cs;
  };

  var get_rect_lines=exports.get_rect_lines = function get_rect_lines(p, size) {
    var ps=get_rect_points(p, size);
    if (p.length==2) {
        return [[ps[0], ps[1]], [ps[1], ps[2]], [ps[2], ps[3]], [ps[3], ps[0]]];
    }
    else 
      if (p.length==3) {
        var l1=[[ps[0], ps[1]], [ps[1], ps[2]], [ps[2], ps[3]], [ps[3], ps[0]]];
        var l2=[[ps[4], ps[5]], [ps[5], ps[6]], [ps[6], ps[7]], [ps[7], ps[4]]];
        l1.concat(l2);
        l1.push([ps[0], ps[4]]);
        l1.push([ps[1], ps[5]]);
        l1.push([ps[2], ps[6]]);
        l1.push([ps[3], ps[7]]);
        return l1;
    }
    else {
      throw "get_rect_points has no implementation for "+p.length+"-dimensional data";
    }
  };

  var $vs_simple_tri_aabb_isect=[0, 0, 0];
  var simple_tri_aabb_isect=exports.simple_tri_aabb_isect = function simple_tri_aabb_isect(v1, v2, v3, min, max) {
    $vs_simple_tri_aabb_isect[0] = v1;
    $vs_simple_tri_aabb_isect[1] = v2;
    $vs_simple_tri_aabb_isect[2] = v3;
    for (var i=0; i<3; i++) {
        var isect=true;
        for (var j=0; j<3; j++) {
            if ($vs_simple_tri_aabb_isect[j][i]<min[i]||$vs_simple_tri_aabb_isect[j][i]>=max[i])
              isect = false;
        }
        if (isect)
          return true;
    }
    return false;
  };

  var MinMax = exports.MinMax = class MinMax {
    constructor(totaxis) {
      if (totaxis==undefined) {
          totaxis = 1;
      }
      this.totaxis = totaxis;
      if (totaxis!=1) {
          this._min = new Array(totaxis);
          this._max = new Array(totaxis);
          this.min = new Array(totaxis);
          this.max = new Array(totaxis);
      }
      else {
        this.min = this.max = 0;
        this._min = FLOAT_MAX;
        this._max = FLOAT_MIN;
      }
      this.reset();
      this._static_mr_co = new Array(this.totaxis);
      this._static_mr_cs = new Array(this.totaxis*this.totaxis);
    }
    
    load(mm) {
      if (this.totaxis==1) {
          this.min = mm.min;
          this.max = mm.max;
          this._min = mm.min;
          this._max = mm.max;
      }
      else {
        this.min = new Vector3(mm.min);
        this.max = new Vector3(mm.max);
        this._min = new Vector3(mm._min);
        this._max = new Vector3(mm._max);
      }
    }
    
    reset() {
      var totaxis=this.totaxis;
      if (totaxis==1) {
          this.min = this.max = 0;
          this._min = FLOAT_MAX;
          this._max = FLOAT_MIN;
      }
      else {
        for (var i=0; i<totaxis; i++) {
            this._min[i] = FLOAT_MAX;
            this._max[i] = FLOAT_MIN;
            this.min[i] = 0;
            this.max[i] = 0;
        }
      }
    }

    minmax_rect(p, size) {
      var totaxis=this.totaxis;
      var cs=this._static_mr_cs;
      if (totaxis==2) {
          cs[0] = p;
          cs[1] = [p[0]+size[0], p[1]];
          cs[2] = [p[0]+size[0], p[1]+size[1]];
          cs[3] = [p[0], p[1]+size[1]];
      }
      else 
        if (totaxis = 3) {
          cs[0] = p;
          cs[1] = [p[0]+size[0], p[1], p[2]];
          cs[2] = [p[0]+size[0], p[1]+size[1], p[2]];
          cs[3] = [p[0], p[1]+size[0], p[2]];
          cs[4] = [p[0], p[1], p[2]+size[2]];
          cs[5] = [p[0]+size[0], p[1], p[2]+size[2]];
          cs[6] = [p[0]+size[0], p[1]+size[1], p[2]+size[2]];
          cs[7] = [p[0], p[1]+size[0], p[2]+size[2]];
      }
      else {
        throw "Minmax.minmax_rect has no implementation for "+totaxis+"-dimensional data";
      }
      for (var i=0; i<cs.length; i++) {
          this.minmax(cs[i]);
      }
    }

    minmax(p) {
      var totaxis=this.totaxis;
      
      if (totaxis==1) {
          this._min = this.min = Math.min(this._min, p);
          this._max = this.max = Math.max(this._max, p);
      } else if (totaxis == 2) {
        this._min[0] = this.min[0] = Math.min(this._min[0], p[0]);
        this._min[1] = this.min[1] = Math.min(this._min[1], p[1]);
        this._max[0] = this.max[0] = Math.max(this._max[0], p[0]);
        this._max[1] = this.max[1] = Math.max(this._max[1], p[1]);
      } else if (totaxis == 3) {
        this._min[0] = this.min[0] = Math.min(this._min[0], p[0]);
        this._min[1] = this.min[1] = Math.min(this._min[1], p[1]);
        this._min[2] = this.min[2] = Math.min(this._min[2], p[2]);
        this._max[0] = this.max[0] = Math.max(this._max[0], p[0]);
        this._max[1] = this.max[1] = Math.max(this._max[1], p[1]);
        this._max[2] = this.max[2] = Math.max(this._max[2], p[2]);
      } else {
        for (var i=0; i<totaxis; i++) {
            this._min[i] = this.min[i] = Math.min(this._min[i], p[i]);
            this._max[i] = this.max[i] = Math.max(this._max[i], p[i]);
        }
      }
    }

    static fromSTRUCT(reader) {
      var ret=new MinMax();
      reader(ret);
      return ret;
    }
  };

  var winding_yup=exports.winding_yup = function winding(a, b, c) {
    for (var i=0; i<a.length; i++) {
        _cross_vec1[i] = b[i]-a[i];
        _cross_vec2[i] = c[i]-a[i];
    }
    if (a.length==2) {
        _cross_vec1[2] = 0.0;
        _cross_vec2[2] = 0.0;
    }
    _cross_vec1.cross(_cross_vec2);
    return _cross_vec1[1]>0.0;
  };

  MinMax.STRUCT = "\n  math.MinMax {\n    min     : vec3;\n    max     : vec3;\n    _min    : vec3;\n    _max    : vec3;\n    totaxis : int;\n  }\n";
  var winding=exports.winding = function winding(a, b, c, zero_z, tol) {
    if (tol == undefined) tol = 0.0;
    
    for (var i=0; i<a.length; i++) {
        _cross_vec1[i] = b[i]-a[i];
        _cross_vec2[i] = c[i]-a[i];
    }
    if (a.length==2 || zero_z) {
        _cross_vec1[2] = 0.0;
        _cross_vec2[2] = 0.0;
    }
    _cross_vec1.cross(_cross_vec2);
    return _cross_vec1[2]>tol;
  };
  var inrect_2d=exports.inrect_2d = function inrect_2d(p, pos, size) {
    if (p==undefined||pos==undefined||size==undefined) {
        console.trace();
        console.log("Bad paramters to inrect_2d()");
        console.log("p: ", p, ", pos: ", pos, ", size: ", size);
        return false;
    }
    return p[0]>=pos[0]&&p[0]<=pos[0]+size[0]&&p[1]>=pos[1]&&p[1]<=pos[1]+size[1];
  };
  var $smin_aabb_isect_line_2d=new Vector2();
  var $ssize_aabb_isect_line_2d=new Vector2();
  var $sv1_aabb_isect_line_2d=new Vector2();
  var $ps_aabb_isect_line_2d=[new Vector2(), new Vector2(), new Vector2()];
  var $l1_aabb_isect_line_2d=[0, 0];
  var $smax_aabb_isect_line_2d=new Vector2();
  var $sv2_aabb_isect_line_2d=new Vector2();
  var $l2_aabb_isect_line_2d=[0, 0];
  var aabb_isect_line_2d=exports.aabb_isect_line_2d = function aabb_isect_line_2d(v1, v2, min, max) {
    for (var i=0; i<2; i++) {
        $smin_aabb_isect_line_2d[i] = Math.min(min[i], v1[i]);
        $smax_aabb_isect_line_2d[i] = Math.max(max[i], v2[i]);
    }
    $smax_aabb_isect_line_2d.sub($smin_aabb_isect_line_2d);
    $ssize_aabb_isect_line_2d.load(max).sub(min);
    if (!aabb_isect_2d($smin_aabb_isect_line_2d, $smax_aabb_isect_line_2d, min, $ssize_aabb_isect_line_2d))
      return false;
    for (var i=0; i<4; i++) {
        if (inrect_2d(v1, min, $ssize_aabb_isect_line_2d))
          return true;
        if (inrect_2d(v2, min, $ssize_aabb_isect_line_2d))
          return true;
    }
    $ps_aabb_isect_line_2d[0] = min;
    $ps_aabb_isect_line_2d[1][0] = min[0];
    $ps_aabb_isect_line_2d[1][1] = max[1];
    $ps_aabb_isect_line_2d[2] = max;
    $ps_aabb_isect_line_2d[3][0] = max[0];
    $ps_aabb_isect_line_2d[3][1] = min[1];
    $l1_aabb_isect_line_2d[0] = v1;
    $l1_aabb_isect_line_2d[1] = v2;
    for (var i=0; i<4; i++) {
        var a=$ps_aabb_isect_line_2d[i], b=$ps_aabb_isect_line_2d[(i+1)%4];
        $l2_aabb_isect_line_2d[0] = a;
        $l2_aabb_isect_line_2d[1] = b;
        if (line_line_cross($l1_aabb_isect_line_2d, $l2_aabb_isect_line_2d))
          return true;
    }
    return false;
  };

  var aabb_isect_2d=exports.aabb_isect_2d = function aabb_isect_2d(pos1, size1, pos2, size2) {
    var ret=0;
    for (var i=0; i<2; i++) {
        var a=pos1[i];
        var b=pos1[i]+size1[i];
        var c=pos2[i];
        var d=pos2[i]+size2[i];
        if (b>=c&&a<=d)
          ret+=1;
    }
    return ret==2;
  };

  var expand_rect2d=exports.expand_rect2d = function expand_rect2d(pos, size, margin) {
    pos[0]-=Math.floor(margin[0]);
    pos[1]-=Math.floor(margin[1]);
    size[0]+=Math.floor(margin[0]*2.0);
    size[1]+=Math.floor(margin[1]*2.0);
  };

  var expand_line=exports.expand_line = function expand_line(l, margin) {
    var c=new Vector3();
    c.add(l[0]);
    c.add(l[1]);
    c.mulScalar(0.5);
    l[0].sub(c);
    l[1].sub(c);
    var l1=l[0].vectorLength();
    var l2=l[1].vectorLength();
    l[0].normalize();
    l[1].normalize();
    l[0].mulScalar(margin+l1);
    l[1].mulScalar(margin+l2);
    l[0].add(c);
    l[1].add(c);
    return l;
  };

  var colinear=exports.colinear = function colinear(a, b, c) {
    for (var i=0; i<3; i++) {
        _cross_vec1[i] = b[i]-a[i];
        _cross_vec2[i] = c[i]-a[i];
    }
    var limit=2.2e-16;
    if (a.vectorDistance(b)<feps*100&&a.vectorDistance(c)<feps*100) {
        return true;
    }
    if (_cross_vec1.dot(_cross_vec1)<limit||_cross_vec2.dot(_cross_vec2)<limit)
      return true;
    _cross_vec1.cross(_cross_vec2);
    return _cross_vec1.dot(_cross_vec1)<limit;
  };

  var _llc_l1=[new Vector3(), new Vector3()];
  var _llc_l2=[new Vector3(), new Vector3()];
  var _llc_l3=[new Vector3(), new Vector3()];
  var _llc_l4=[new Vector3(), new Vector3()];
  
  var lli_v1 = new Vector3(), lli_v2 = new Vector3(), lli_v3 = new Vector3(), lli_v4 = new Vector3();

  var _zero_cn = new Vector3();
  var _tmps_cn = util.cachering.fromConstructor(Vector3, 64);
  var _rets_cn = util.cachering.fromConstructor(Vector3, 64);

  //vec1, vec2 should both be normalized
  var corner_normal = exports.corner_normal = function corner_normal(vec1, vec2, width) {
    var ret = _rets_cn.next().zero();

    var vec = _tmps_cn.next().zero();
    vec.load(vec1).add(vec2).normalize();

    /*
    ret.load(vec).mulScalar(width);
    return ret;
    */

    //handle colinear case
    if (Math.abs(vec1.normalizedDot(vec2)) > 0.9999) {
      if (vec1.dot(vec2) > 0.0001) {
        ret.load(vec1).add(vec2).normalize();
      } else {
        ret.load(vec1).normalize();
      }

      ret.mulScalar(width);

      return ret;
    } else { //XXX
      //ret.load(vec).mulScalar(width);
      //return ret;
    }

    vec1 = _tmps_cn.next().load(vec1).mulScalar(width);
    vec2 = _tmps_cn.next().load(vec2).mulScalar(width);

    var p1 = _tmps_cn.next().load(vec1);
    var p2 = _tmps_cn.next().load(vec2);

    vec1.addFac(vec1, 0.01);
    vec2.addFac(vec2, 0.01);

    var sc = 1.0;

    p1[0] += vec1[1]*sc;
    p1[1] += -vec1[0]*sc;

    p2[0] += -vec2[1]*sc;
    p2[1] += vec2[0]*sc;

    var p = exports.line_line_isect(vec1, p1, vec2, p2, false);

    if (p == undefined || p === exports.COLINEAR_ISECT || p.dot(p) < 0.000001) {
      ret.load(vec1).add(vec2).normalize().mulScalar(width);
    } else {
      ret.load(p);

      if (vec.dot(vec) > 0 && vec.dot(ret) < 0) {
        ret.load(vec).mulScalar(width);
      }
    }

    return ret;
  }

  //test_segment is optional, true
  var line_line_isect = exports.line_line_isect = function line_line_isect(v1, v2, v3, v4, test_segment) {
    test_segment = test_segment === undefined ? true : test_segment;

    if (!line_line_cross(v1, v2, v3, v4)) {
      return undefined;
    }
    
    /*
    on factor;
    off period;
    
    xa := xa1 + (xa2 - xa1)*t1;
    xb := xb1 + (xb2 - xb1)*t2;
    ya := ya1 + (ya2 - ya1)*t1;
    yb := yb1 + (yb2 - yb1)*t2;
    
    f1 := xa - xb;
    f2 := ya - yb;
    
    f := solve({f1, f2}, {t1, t2});
    ft1 := part(f, 1, 1, 2);
    ft2 := part(f, 1, 2, 2);
    
    */
    
    var xa1 = v1[0], xa2 = v2[0], ya1 = v1[1], ya2 = v2[1];
    var xb1 = v3[0], xb2 = v4[0], yb1 = v3[1], yb2 = v4[1];
    
    var div = ((xa1-xa2)*(yb1-yb2)-(xb1-xb2)*(ya1-ya2));
    if (div < 0.00000001) { //parallel but intersecting lines.
      return exports.COLINEAR_ISECT;
    } else { //intersection exists
      var t1 = (-((ya1-yb2)*xb1-(yb1-yb2)*xa1-(ya1-yb1)*xb2))/div;
      
      return lli_v1.load(v1).interp(v2, t1);
    }
  }
  
  var line_line_cross=exports.line_line_cross = function line_line_cross(v1, v2, v3, v4, tol) {
    tol = tol === undefined ? 0.0000001 : tol;
    
    let l1 = _llc_l3, l2 = _llc_l4;
    l1[0].load(v1), l1[1].load(v2), l2[0].load(v3), l2[1].load(v4);
    
    //l1[0][2] = l1[1][2] = l2[0][2] = l2[1][2] = 0;
    
    /*
    var limit=feps*1000;
    if (Math.abs(l1[0].vectorDistance(l2[0])+l1[1].vectorDistance(l2[0])-l1[0].vectorDistance(l1[1]))<limit) {
        return true;
    }
    if (Math.abs(l1[0].vectorDistance(l2[1])+l1[1].vectorDistance(l2[1])-l1[0].vectorDistance(l1[1]))<limit) {
        return true;
    }
    if (Math.abs(l2[0].vectorDistance(l1[0])+l2[1].vectorDistance(l1[0])-l2[0].vectorDistance(l2[1]))<limit) {
        return true;
    }
    if (Math.abs(l2[0].vectorDistance(l1[1])+l2[1].vectorDistance(l1[1])-l2[0].vectorDistance(l2[1]))<limit) {
        return true;
    }
    //*/
    
    var a=l1[0];
    var b=l1[1];
    var c=l2[0];
    var d=l2[1];
    
    var w1=winding(a, b, c, undefined, tol);
    var w2=winding(c, a, d, undefined, tol);
    var w3=winding(a, b, d, undefined, tol);
    var w4=winding(c, b, d, undefined, tol);
    
    return (w1==w2)&&(w3==w4)&&(w1!=w3);
  };

  var _asi_v1 = new Vector3();
  var _asi_v2 = new Vector3();
  var _asi_v3 = new Vector3();
  var _asi_v4 = new Vector3();
  var _asi_v5 = new Vector3();
  var _asi_v6 = new Vector3();

  var point_in_aabb_2d = exports.point_in_aabb_2d = function(p, min, max) {
    return p[0] >= min[0] && p[0] <= max[0] && p[1] >= min[1] && p[1] <= max[1];
  }

  var _asi2d_v1 = new Vector2();
  var _asi2d_v2 = new Vector2();
  var _asi2d_v3 = new Vector2();
  var _asi2d_v4 = new Vector2();
  var _asi2d_v5 = new Vector2();
  var _asi2d_v6 = new Vector2();
  var aabb_sphere_isect_2d = exports.aabb_sphere_isect_2d = function(p, r, min, max) {
    var v1 = _asi2d_v1, v2 = _asi2d_v2, v3 = _asi2d_v3, mvec = _asi2d_v4;
    var v4 = _asi2d_v5;
    
    p = _asi2d_v6.load(p);
    v1.load(p);
    v2.load(p);
    
    min = _asi_v5.load(min);
    max = _asi_v6.load(max);
    
    mvec.load(max).sub(min).normalize().mulScalar(r+0.0001);
    
    v1.sub(mvec);
    v2.add(mvec);
    v3.load(p);
    
    var ret = point_in_aabb_2d(v1, min, max) || point_in_aabb_2d(v2, min, max)
           || point_in_aabb_2d(v3, min, max);
    
    if (ret)
        return ret;
    
    /*
    v1.load(min).add(max).mulScalar(0.5);
    ret = ret || v1.vectorDistance(p) < r;
    
    v1.load(min);
    ret = ret || v1.vectorDistance(p) < r;
    
    v1.load(max);
    ret = ret || v1.vectorDistance(p) < r;
    
    v1[0] = min[0], v1[1] = max[1];
    ret = ret || v1.vectorDistance(p) < r;
    
    v1[0] = max[0], v1[1] = min[1];
    ret = ret || v1.vectorDistance(p) < r;
    */
    //*
    v1.load(min);
    v2[0] = min[0]; v2[1] = max[1];
    ret = ret || dist_to_line_2d(p, v1, v2) < r;
    
    v1.load(max);
    v2[0] = max[0]; v2[1] = max[1];
    ret = ret || dist_to_line_2d(p, v1, v2) < r;

    v1.load(max);
    v2[0] = max[0]; v2[1] = min[1];
    ret = ret || dist_to_line_2d(p, v1, v2) < r;

    v1.load(max);
    v2[0] = min[0]; v2[1] = min[1];
    ret = ret || dist_to_line_2d(p, v1, v2) < r;
    //*/
    return ret;
  };

  var point_in_aabb = exports.point_in_aabb = function(p, min, max) {
    return p[0] >= min[0] && p[0] <= max[0] && p[1] >= min[1] && p[1] <= max[1]
           && p[2] >= min[2] && p[2] <= max[2];
  }
  var aabb_sphere_isect = exports.aabb_sphere_isect = function(p, r, min, max) {
    var v1 = _asi_v1, v2 = _asi_v2, v3 = _asi_v3, mvec = _asi_v4;
    min = _asi_v5.load(min);
    max = _asi_v6.load(max);
    
    if (min.length == 2) {
      min[2] = max[2] = 0.0;
    }
    
    mvec.load(max).sub(min).normalize().mulScalar(r+0.0001);
    v1.sub(mvec);
    v2.add(mvec);
    v3.load(p);
    
    //prevent NaN on 2d vecs
    if (p.length == 2) {
        mvec[2] = v1[2] = v2[2] = v3[2] = 0.0;
    }
    
    return point_in_aabb(v1, min, max) || point_in_aabb(v2, min, max) ||
           point_in_aabb(v3, min, max);
  };

  var point_in_tri=exports.point_in_tri = function point_in_tri(p, v1, v2, v3) {
    var w1=winding(p, v1, v2);
    var w2=winding(p, v2, v3);
    var w3=winding(p, v3, v1);
    return w1==w2&&w2==w3;
  };

  var convex_quad=exports.convex_quad = function convex_quad(v1, v2, v3, v4) {
    return line_line_cross([v1, v3], [v2, v4]);
  };

  var $e1_normal_tri=new Vector3();
  var $e3_normal_tri=new Vector3();
  var $e2_normal_tri=new Vector3();
  var normal_tri=exports.normal_tri = function normal_tri(v1, v2, v3) {
    $e1_normal_tri[0] = v2[0]-v1[0];
    $e1_normal_tri[1] = v2[1]-v1[1];
    $e1_normal_tri[2] = v2[2]-v1[2];
    $e2_normal_tri[0] = v3[0]-v1[0];
    $e2_normal_tri[1] = v3[1]-v1[1];
    $e2_normal_tri[2] = v3[2]-v1[2];
    $e3_normal_tri[0] = $e1_normal_tri[1]*$e2_normal_tri[2]-$e1_normal_tri[2]*$e2_normal_tri[1];
    $e3_normal_tri[1] = $e1_normal_tri[2]*$e2_normal_tri[0]-$e1_normal_tri[0]*$e2_normal_tri[2];
    $e3_normal_tri[2] = $e1_normal_tri[0]*$e2_normal_tri[1]-$e1_normal_tri[1]*$e2_normal_tri[0];
    
    var _len=Math.sqrt(($e3_normal_tri[0]*$e3_normal_tri[0]+$e3_normal_tri[1]*$e3_normal_tri[1]+$e3_normal_tri[2]*$e3_normal_tri[2]));
    if (_len>1e-05)
      _len = 1.0/_len;
    $e3_normal_tri[0]*=_len;
    $e3_normal_tri[1]*=_len;
    $e3_normal_tri[2]*=_len;
    return $e3_normal_tri;
  };

  var $n2_normal_quad=new Vector3();
  var normal_quad=exports.normal_quad = function normal_quad(v1, v2, v3, v4) {
    var n=normal_tri(v1, v2, v3);
    $n2_normal_quad[0] = n[0];
    $n2_normal_quad[1] = n[1];
    $n2_normal_quad[2] = n[2];
    n = normal_tri(v1, v3, v4);
    $n2_normal_quad[0] = $n2_normal_quad[0]+n[0];
    $n2_normal_quad[1] = $n2_normal_quad[1]+n[1];
    $n2_normal_quad[2] = $n2_normal_quad[2]+n[2];
    var _len=Math.sqrt(($n2_normal_quad[0]*$n2_normal_quad[0]+$n2_normal_quad[1]*$n2_normal_quad[1]+$n2_normal_quad[2]*$n2_normal_quad[2]));
    if (_len>1e-05)
      _len = 1.0/_len;
    $n2_normal_quad[0]*=_len;
    $n2_normal_quad[1]*=_len;
    $n2_normal_quad[2]*=_len;
    return $n2_normal_quad;
  };

  var _li_vi=new Vector3();

  //calc_t is optional, false
  var line_isect=exports.line_isect = function line_isect(v1, v2, v3, v4, calc_t) {
    if (calc_t==undefined) {
        calc_t = false;
    }
    var div=(v2[0]-v1[0])*(v4[1]-v3[1])-(v2[1]-v1[1])*(v4[0]-v3[0]);
    if (div==0.0)
      return [new Vector3(), COLINEAR, 0.0];
    var vi=_li_vi;
    vi[0] = 0;
    vi[1] = 0;
    vi[2] = 0;
    vi[0] = ((v3[0]-v4[0])*(v1[0]*v2[1]-v1[1]*v2[0])-(v1[0]-v2[0])*(v3[0]*v4[1]-v3[1]*v4[0]))/div;
    vi[1] = ((v3[1]-v4[1])*(v1[0]*v2[1]-v1[1]*v2[0])-(v1[1]-v2[1])*(v3[0]*v4[1]-v3[1]*v4[0]))/div;
    if (calc_t||v1.length==3) {
        var n1=new Vector2(v2).sub(v1);
        var n2=new Vector2(vi).sub(v1);
        var t=n2.vectorLength()/n1.vectorLength();
        n1.normalize();
        n2.normalize();
        if (n1.dot(n2)<0.0) {
            t = -t;
        }
        if (v1.length==3) {
            vi[2] = v1[2]+(v2[2]-v1[2])*t;
        }
        return [vi, LINECROSS, t];
    }
    return [vi, LINECROSS];
  };

  var dt2l_v1 = new Vector2();
  var dt2l_v2 = new Vector2();
  var dt2l_v3 = new Vector2();
  var dt2l_v4 = new Vector2();
  var dt2l_v5 = new Vector2();

       var dist_to_line_2d = exports.dist_to_line_2d = 
  function dist_to_line_2d(p, v1, v2, clip) {
    if (clip == undefined) {
        clip = true;
    }
    
    v1 = dt2l_v4.load(v1);
    v2 = dt2l_v5.load(v2);
    
    var n = dt2l_v1;
    var vec = dt2l_v3;
    
    n.load(v2).sub(v1).normalize();
    vec.load(p).sub(v1);
    
    var t = vec.dot(n);
    if (clip) {
      t = Math.min(Math.max(t, 0.0), v1.vectorDistance(v2));
    }
    
    n.mulScalar(t).add(v1);
    
    return n.vectorDistance(p);
  }

  var dt3l_v1 = new Vector3();
  var dt3l_v2 = new Vector3();
  var dt3l_v3 = new Vector3();
  var dt3l_v4 = new Vector3();
  var dt3l_v5 = new Vector3();

       var dist_to_line = exports.dist_to_line = 
  function dist_to_line(p, v1, v2, clip) {
    if (clip == undefined) {
        clip = true;
    }
    
    v1 = dt3l_v4.load(v1);
    v2 = dt3l_v5.load(v2);
    
    var n = dt3l_v1;
    var vec = dt3l_v3;
    
    n.load(v2).sub(v1).normalize();
    vec.load(p).sub(v1);
    
    var t = vec.dot(n);
    if (clip) {
      t = Math.min(Math.max(t, 0.0), v1.vectorDistance(v2));
    }
    
    n.mulScalar(t).add(v1);
    
    return n.vectorDistance(p);
  }

  //p cam be 2d, 3d, or 4d point, v1/v2 however must be full homogenous coordinates
  var _cplw_vs4 = util.cachering.fromConstructor(Vector4, 64);
  var _cplw_vs3 = util.cachering.fromConstructor(Vector3, 64);
  var _cplw_vs2 = util.cachering.fromConstructor(Vector2, 64);

  function wclip(x1, x2, w1, w2, near) {
    var r1 = near*w1 - x1;
    var r2 = (w1-w2)*near - (x1-x2);

    if (r2 == 0.0) return 0.0;

    return r1 / r2;
  }

  function clip(a, b, znear) {
    if (a-b == 0.0) return 0.0;

    return (a - znear) / (a - b);
  }

  /*clips v1 and v2 to lie within homogenous projection range
    v1 and v2 are assumed to be projected, pre-division Vector4's
    returns a positive number (how much the line was scaled) if either _v1 or _v2 are
    in front of the near clipping plane otherwise, returns 0
   */
  var clip_line_w = exports.clip_line_w = function(_v1, _v2, znear, zfar) {
    var v1 = _cplw_vs4.next().load(_v1);
    var v2 = _cplw_vs4.next().load(_v2);

    //are we fully behind the view plane?
    if ((v1[2] < 1.0 && v2[2] < 1.0))
      return false;

    function doclip1(v1, v2, axis) {
      if (v1[axis]/v1[3] < -1) {
        var t = wclip(v1[axis], v2[axis], v1[3], v2[3], -1);
        v1.interp(v2, t);
      } else if (v1[axis]/v1[3] > 1) {
        var t = wclip(v1[axis], v2[axis], v1[3], v2[3], 1);
        v1.interp(v2, t);
      }
    }

    function doclip(v1, v2, axis) {
      doclip1(v1, v2, axis);
      doclip1(v2, v1, axis);
    }

    function dozclip(v1, v2) {
      if (v1[2] < 1) {
        var t = clip(v1[2], v2[2], 1);
        v1.interp(v2, t);
      } else if (v2[2] < 1) {
        var t = clip(v2[2], v1[2], 1);
        v2.interp(v1, t);
      }
    }

    dozclip(v1, v2, 1);
    doclip(v1, v2, 0);
    doclip(v1, v2, 1);

    for (var i=0; i<4; i++) {
      _v1[i] = v1[i];
      _v2[i] = v2[i];
    }

    return !(v1[0]/v1[3] == v2[0]/v2[3] || v1[1]/v2[3] == v2[1]/v2[3]);
  };

  //clip is optional, true.  clip point to lie within line segment v1->v2
  var _closest_point_on_line_cache = util.cachering.fromConstructor(Vector3, 64);
  var _closest_point_rets = new util.cachering(function() {
    return [0, 0];
  }, 64);

  var _closest_tmps = [new Vector3(), new Vector3(), new Vector3()];
  var closest_point_on_line=exports.closest_point_on_line = function closest_point_on_line(p, v1, v2, clip) {
    if (clip == undefined)
      clip = true;
    var l1 = _closest_tmps[0], l2 = _closest_tmps[1];
    
    l1.load(v2).sub(v1).normalize();
    l2.load(p).sub(v1);
    
    var t = l2.dot(l1);
    if (clip) {
      t = t*(t<0.0) + t*(t>1.0) + (t>1.0);
    }
    
    var p = _closest_point_on_line_cache.next();
    p.load(l1).mulScalar(t).add(v1);
    var ret = _closest_point_rets.next();
    
    ret[0] = p;
    ret[1] = t;
    
    return ret;
  };

  /*given input line (a,d) and tangent t,
    returns a circle that goes through both
    a and d, whose normalized tangent at a is the same
    as normalized t.
    
    note that t need not be normalized, this function
    does that itself*/
  var _circ_from_line_tan_vs = util.cachering.fromConstructor(Vector3, 32);
  var _circ_from_line_tan_ret = new util.cachering(function() {
    return [new Vector3(), 0];
  });
  var circ_from_line_tan = exports.circ_from_line_tan = function(a, b, t) {
    var p1 = _circ_from_line_tan_vs.next();
    var t2 = _circ_from_line_tan_vs.next();
    var n1 = _circ_from_line_tan_vs.next();
    
    p1.load(a).sub(b);
    t2.load(t).normalize();
    n1.load(p1).normalize().cross(t2).cross(t2).normalize();
    
    var ax = p1[0], ay = p1[1], az=p1[2], nx = n1[0], ny=n1[1], nz=n1[2];
    var r = -(ax*ax + ay*ay + az*az) / (2*(ax*nx + ay*ny +az*nz));
    
    var ret = _circ_from_line_tan_ret.next();
    ret[0].load(n1).mulScalar(r).add(a)
    ret[1] = r;
    
    return ret;
  }

  var _gtc_e1=new Vector3();
  var _gtc_e2=new Vector3();
  var _gtc_e3=new Vector3();
  var _gtc_p1=new Vector3();
  var _gtc_p2=new Vector3();
  var _gtc_v1=new Vector3();
  var _gtc_v2=new Vector3();
  var _gtc_p12=new Vector3();
  var _gtc_p22=new Vector3();
  var _get_tri_circ_ret = new util.cachering(function() { return [0, 0]});

  var get_tri_circ=exports.get_tri_circ = function get_tri_circ(a, b, c) {
    var v1=_gtc_v1;
    var v2=_gtc_v2;
    var e1=_gtc_e1;
    var e2=_gtc_e2;
    var e3=_gtc_e3;
    var p1=_gtc_p1;
    var p2=_gtc_p2;
    
    for (var i=0; i<3; i++) {
        e1[i] = b[i]-a[i];
        e2[i] = c[i]-b[i];
        e3[i] = a[i]-c[i];
    }
    
    for (var i=0; i<3; i++) {
        p1[i] = (a[i]+b[i])*0.5;
        p2[i] = (c[i]+b[i])*0.5;
    }
    
    e1.normalize();
    
    v1[0] = -e1[1];
    v1[1] = e1[0];
    v1[2] = e1[2];

    v2[0] = -e2[1];
    v2[1] = e2[0];
    v2[2] = e2[2];

    v1.normalize();
    v2.normalize();

    var cent;
    var type;
    for (var i=0; i<3; i++) {
        _gtc_p12[i] = p1[i]+v1[i];
        _gtc_p22[i] = p2[i]+v2[i];
    }

    var ret=line_isect(p1, _gtc_p12, p2, _gtc_p22);
    cent = ret[0];
    type = ret[1];

    e1.load(a);
    e2.load(b);
    e3.load(c);

    var r=e1.sub(cent).vectorLength();
    if (r<feps)
      r = e2.sub(cent).vectorLength();
    if (r<feps)
      r = e3.sub(cent).vectorLength();
    
    var ret = _get_tri_circ_ret.next();
    ret[0] = cent;
    ret[1] = r;
    
    return ret;
  };

  var gen_circle=exports.gen_circle = function gen_circle(m, origin, r, stfeps) {
    var pi=Math.PI;
    var f=-pi/2;
    var df=(pi*2)/stfeps;
    var verts=new Array();
    for (var i=0; i<stfeps; i++) {
        var x=origin[0]+r*Math.sin(f);
        var y=origin[1]+r*Math.cos(f);
        var v=m.make_vert(new Vector3([x, y, origin[2]]));
        verts.push(v);
        f+=df;
    }
    for (var i=0; i<verts.length; i++) {
        var v1=verts[i];
        var v2=verts[(i+1)%verts.length];
        m.make_edge(v1, v2);
    }
    return verts;
  };

  var cos = Math.cos;
  var sin = Math.sin;
  //axis is optional, 0
  var rot2d = exports.rot2d = function(v1, A, axis) {
    var x = v1[0];
    var y = v1[1];
    
    if (axis == 1) {
      v1[0] = x * cos(A) + y*sin(A);
      v1[2] = y * cos(A) - x*sin(A);
    } else {
      v1[0] = x * cos(A) - y*sin(A);
      v1[1] = y * cos(A) + x*sin(A);
    }
  }

  var makeCircleMesh=exports.makeCircleMesh = function makeCircleMesh(gl, radius, stfeps) {
    var mesh=new Mesh();
    var verts1=gen_circle(mesh, new Vector3(), radius, stfeps);
    var verts2=gen_circle(mesh, new Vector3(), radius/1.75, stfeps);
    mesh.make_face_complex([verts1, verts2]);
    return mesh;
  };
  var minmax_verts=exports.minmax_verts = function minmax_verts(verts) {
    var min=new Vector3([1000000000000.0, 1000000000000.0, 1000000000000.0]);
    var max=new Vector3([-1000000000000.0, -1000000000000.0, -1000000000000.0]);
    var __iter_v=__get_iter(verts);
    var v;
    while (1) {
      var __ival_v=__iter_v.next();
      if (__ival_v.done) {
          break;
      }
      v = __ival_v.value;
      for (var i=0; i<3; i++) {
          min[i] = Math.min(min[i], v.co[i]);
          max[i] = Math.max(max[i], v.co[i]);
      }
    }
    return [min, max];
  };

  var unproject=exports.unproject = function unproject(vec, ipers, iview) {
    var newvec=new Vector3(vec);
    newvec.multVecMatrix(ipers);
    newvec.multVecMatrix(iview);
    return newvec;
  };

  var project=exports.project = function project(vec, pers, view) {
    var newvec=new Vector3(vec);
    newvec.multVecMatrix(pers);
    newvec.multVecMatrix(view);
    return newvec;
  };

  var _sh_minv=new Vector3();
  var _sh_maxv=new Vector3();
  var _sh_start=[];
  var _sh_end=[];
  var spatialhash=exports.spatialhash = function spatialhash(init, cellsize) {
    if (cellsize==undefined)
      cellsize = 0.25;
    this.cellsize = cellsize;
    this.shash = {}
    this.items = {}
    this.length = 0;
    this.hashlookup = function(x, y, z, create) {
      if (create==undefined)
        create = false;
      var h=this.hash(x, y, z);
      var b=this.shash[h];
      if (b==undefined) {
          if (!create)
            return null;
          var ret={};
          this.shash[h] = ret;
          return ret;
      }
      else {
        return b;
      }
    }
    this.hash = function(x, y, z) {
      return z*125000000+y*250000+x;
    }
    this._op = function(item, mode) {
      var csize=this.cellsize;
      var minv=_sh_minv;
      minv.zero();
      var maxv=_sh_maxv;
      maxv.zero();
      if (item.type==MeshTypes.EDGE) {
          for (var i=0; i<3; i++) {
              minv[i] = Math.min(item.v1.co[i], item.v2.co[i]);
              maxv[i] = Math.max(item.v1.co[i], item.v2.co[i]);
          }
      }
      else 
        if (item.type==MeshTypes.FACE) {
          var firstl=item.looplists[0].loop;
          var l=firstl;
          do {
            for (var i=0; i<3; i++) {
                minv[i] = Math.min(minv[i], l.v.co[i]);
                maxv[i] = Math.max(maxv[i], l.v.co[i]);
            }
            l = l.next;
          } while (l!=firstl);
          
      }
      else 
        if (item.type==MeshTypes.VERT) {
          minv.load(item.co);
          maxv.load(item.co);
      }
      else {
        console.trace();
        throw "Invalid type for spatialhash";
      }
      var start=_sh_start;
      var end=_sh_end;
      for (var i=0; i<3; i++) {
          start[i] = Math.floor(minv[i]/csize);
          end[i] = Math.floor(maxv[i]/csize);
      }
      for (var x=start[0]; x<=end[0]; x++) {
          for (var y=start[1]; y<=end[1]; y++) {
              for (var z=start[2]; z<=end[2]; z++) {
                  var bset=this.hashlookup(x, y, z, true);
                  if (mode=="a") {
                      bset[item.__hash__()] = item;
                  }
                  else 
                    if (mode=="r") {
                      delete bset[item.__hash__()];
                  }
              }
          }
      }
    }
    this.add = function(item) {
      this._op(item, "a");
      if (this.items[item.__hash__()]==undefined) {
          this.items[item.__hash__()] = item;
          this.length++;
      }
    }
    this.remove = function(item) {
      this._op(item, "r");
      delete this.items[item.__hash__()];
      this.length--;
    }
    
    this.iterator = function() {
      return new obj_value_iter(this.items);
    }
    
    this.query_radius = function(co, radius) {
      var min=new Vector3(co).sub(new Vector3(radius, radius, radius));
      var max=new Vector3(co).add(new Vector3(radius, radius, radius));
      return this.query(min, max);
    }
    this.query = function(start, end) {
      var csize=this.cellsize;
      var minv=_sh_minv.zero();
      var maxv=_sh_maxv.zero();
      for (var i=0; i<3; i++) {
          minv[i] = Math.min(start[i], end[i]);
          maxv[i] = Math.max(start[i], end[i]);
      }
      var start=_sh_start;
      var end=_sh_end;
      for (var i=0; i<3; i++) {
          start[i] = Math.floor(minv[i]/csize);
          end[i] = Math.floor(maxv[i]/csize);
      }
      var ret=new set();
      for (var x=start[0]; x<=end[0]; x++) {
          for (var y=start[1]; y<=end[1]; y++) {
              for (var z=start[2]; z<=end[2]; z++) {
                  var bset=this.hashlookup(x, y, z, false);
                  if (bset!=null) {
                      var __iter_r=__get_iter(new obj_value_iter(bset));
                      var r;
                      while (1) {
                        var __ival_r=__iter_r.next();
                        if (__ival_r.done) {
                            break;
                        }
                        r = __ival_r.value;
                        ret.add(r);
                      }
                  }
              }
          }
      }
      return ret;
    }
    this.union = function(b) {
      var newh=new spatialhash();
      newh.cellsize = Math.min(this.cellsize, b.cellsize);
      var __iter_item=__get_iter(this);
      var item;
      while (1) {
        var __ival_item=__iter_item.next();
        if (__ival_item.done) {
            break;
        }
        item = __ival_item.value;
        newh.add(item);
      }
      var __iter_item=__get_iter(b);
      var item;
      while (1) {
        var __ival_item=__iter_item.next();
        if (__ival_item.done) {
            break;
        }
        item = __ival_item.value;
        newh.add(item);
      }
      return newh;
    }
    this.has = function(b) {
      return this.items[b.__hash__()]!=undefined;
    }
    if (init!=undefined) {
        var __iter_item=__get_iter(init);
        var item;
        while (1) {
          var __ival_item=__iter_item.next();
          if (__ival_item.done) {
              break;
          }
          item = __ival_item.value;
          this.add(item);
        }
    }
  };

  var static_cent_gbw=exports.static_cent_gbw = static_cent_gbw = new Vector3();
  var get_boundary_winding=exports.get_boundary_winding = function get_boundary_winding(points) {
    var cent=static_cent_gbw.zero();
    if (points.length==0)
      return false;
    for (var i=0; i<points.length; i++) {
        cent.add(points[i]);
    }
    cent.divideScalar(points.length);
    var w=0, totw=0;
    for (var i=0; i<points.length; i++) {
        var v1=points[i];
        var v2=points[(i+1)%points.length];
        if (!colinear(v1, v2, cent)) {
            w+=winding(v1, v2, cent);
            totw+=1;
        }
    }
    if (totw>0)
      w/=totw;
    return Math.round(w)==1;
  };

  var PlaneOps=exports.PlaneOps = function(normal) {
    var no=normal;
    this.axis = [0, 0, 0];
    this.reset_axis(normal);
  };

  PlaneOps.prototype = init_prototype(PlaneOps, {
    reset_axis : function(no) {
      var ax, ay, az;
      var nx=Math.abs(no[0]), ny=Math.abs(no[1]), nz=Math.abs(no[2]);
      if (nz>nx&&nz>ny) {
          ax = 0;
          ay = 1;
          az = 2;
      }
      else 
        if (nx>ny&&nx>nz) {
          ax = 2;
          ay = 1;
          az = 0;
      }
      else {
        ax = 0;
        ay = 2;
        az = 1;
      }
      this.axis = [ax, ay, az];
    },

    convex_quad : function(v1, v2, v3, v4) {
      var ax=this.axis;
      v1 = new Vector3([v1[ax[0]], v1[ax[1]], v1[ax[2]]]);
      v2 = new Vector3([v2[ax[0]], v2[ax[1]], v2[ax[2]]]);
      v3 = new Vector3([v3[ax[0]], v3[ax[1]], v3[ax[2]]]);
      v4 = new Vector3([v4[ax[0]], v4[ax[1]], v4[ax[2]]]);
      return convex_quad(v1, v2, v3, v4);
    },

    line_isect : function(v1, v2, v3, v4) {
      var ax=this.axis;
      var orig1=v1, orig2=v2;
      v1 = new Vector3([v1[ax[0]], v1[ax[1]], v1[ax[2]]]);
      v2 = new Vector3([v2[ax[0]], v2[ax[1]], v2[ax[2]]]);
      v3 = new Vector3([v3[ax[0]], v3[ax[1]], v3[ax[2]]]);
      v4 = new Vector3([v4[ax[0]], v4[ax[1]], v4[ax[2]]]);
      var ret=line_isect(v1, v2, v3, v4, true);
      var vi=ret[0];
      if (ret[1]==LINECROSS) {
          ret[0].load(orig2).sub(orig1).mulScalar(ret[2]).add(orig1);
      }
      return ret;
    },

    line_line_cross : function(l1, l2) {
      var ax=this.axis;
      var v1=l1[0], v2=l1[1], v3=l2[0], v4=l2[1];
      v1 = new Vector3([v1[ax[0]], v1[ax[1]], 0.0]);
      v2 = new Vector3([v2[ax[0]], v2[ax[1]], 0.0]);
      v3 = new Vector3([v3[ax[0]], v3[ax[1]], 0.0]);
      v4 = new Vector3([v4[ax[0]], v4[ax[1]], 0.0]);
      return line_line_cross([v1, v2], [v3, v4]);
    },

    winding : function(v1, v2, v3) {
      var ax=this.axis;
      if (v1==undefined)
        console.trace();
      v1 = new Vector3([v1[ax[0]], v1[ax[1]], 0.0]);
      v2 = new Vector3([v2[ax[0]], v2[ax[1]], 0.0]);
      v3 = new Vector3([v3[ax[0]], v3[ax[1]], 0.0]);
      return winding(v1, v2, v3);
    },

    colinear : function(v1, v2, v3) {
      var ax=this.axis;
      v1 = new Vector3([v1[ax[0]], v1[ax[1]], 0.0]);
      v2 = new Vector3([v2[ax[0]], v2[ax[1]], 0.0]);
      v3 = new Vector3([v3[ax[0]], v3[ax[1]], 0.0]);
      return colinear(v1, v2, v3);
    },

    get_boundary_winding : function(points) {
      var ax=this.axis;
      var cent=new Vector3();
      if (points.length==0)
        return false;
      for (var i=0; i<points.length; i++) {
          cent.add(points[i]);
      }
      cent.divideScalar(points.length);
      var w=0, totw=0;
      for (var i=0; i<points.length; i++) {
          var v1=points[i];
          var v2=points[(i+1)%points.length];
          if (!this.colinear(v1, v2, cent)) {
              w+=this.winding(v1, v2, cent);
              totw+=1;
          }
      }
      if (totw>0)
        w/=totw;
      return Math.round(w)==1;
    }

  });

  var _isrp_ret=new Vector3();
  var isect_ray_plane=exports.isect_ray_plane = function isect_ray_plane(planeorigin, planenormal, rayorigin, raynormal) {
    var p=planeorigin, n=planenormal;
    var r=rayorigin, v=raynormal;
    var d=p.vectorLength();
    var t=-(r.dot(n)-p.dot(n))/v.dot(n);
    _isrp_ret.load(v);
    _isrp_ret.mulScalar(t);
    _isrp_ret.add(r);
    return _isrp_ret;
  };

  var mesh_find_tangent=exports.mesh_find_tangent = function mesh_find_tangent(mesh, viewvec, offvec, projmat, verts) {
    if (verts==undefined)
      verts = mesh.verts.selected;
    var vset=new set();
    var eset=new set();
    var __iter_v=__get_iter(verts);
    var v;
    while (1) {
      var __ival_v=__iter_v.next();
      if (__ival_v.done) {
          break;
      }
      v = __ival_v.value;
      vset.add(v);
    }
    var __iter_v=__get_iter(vset);
    var v;
    while (1) {
      var __ival_v=__iter_v.next();
      if (__ival_v.done) {
          break;
      }
      v = __ival_v.value;
      var __iter_e=__get_iter(v.edges);
      var e;
      while (1) {
        var __ival_e=__iter_e.next();
        if (__ival_e.done) {
            break;
        }
        e = __ival_e.value;
        if (vset.has(e.other_vert(v))) {
            eset.add(e);
        }
      }
    }
    if (eset.length==0) {
        return new Vector3(offvec);
    }
    var tanav=new Vector3();
    var evec=new Vector3();
    var tan=new Vector3();
    var co2=new Vector3();
    var __iter_e=__get_iter(eset);
    var e;
    while (1) {
      var __ival_e=__iter_e.next();
      if (__ival_e.done) {
          break;
      }
      e = __ival_e.value;
      evec.load(e.v1.co).multVecMatrix(projmat);
      co2.load(e.v2.co).multVecMatrix(projmat);
      evec.sub(co2);
      evec.normalize();
      tan[0] = evec[1];
      tan[1] = -evec[0];
      tan[2] = 0.0;
      if (tan.dot(offvec)<0.0)
        tan.mulScalar(-1.0);
      tanav.add(tan);
    }
    tanav.normalize();
    return tanav;
  };

  var Mat4Stack=exports.Mat4Stack = function() {
    this.stack = [];
    this.matrix = new Matrix4();
    this.matrix.makeIdentity();
    this.update_func = undefined;
  };

  Mat4Stack.prototype = init_prototype(Mat4Stack, {
    set_internal_matrix : function(mat, update_func) {
      this.update_func = update_func;
      this.matrix = mat;
    },

    reset : function(mat) {
      this.matrix.load(mat);
      this.stack = [];
      if (this.update_func!=undefined)
        this.update_func();
    },

    load : function(mat) {
      this.matrix.load(mat);
      if (this.update_func!=undefined)
        this.update_func();
    },

    multiply : function(mat) {
      this.matrix.multiply(mat);
      if (this.update_func!=undefined)
        this.update_func();
    },

    identity : function() {
      this.matrix.loadIdentity();
      if (this.update_func!=undefined)
        this.update_func();
    },

    push : function(mat2) {
      this.stack.push(new Matrix4(this.matrix));
      if (mat2!=undefined) {
          this.matrix.load(mat2);
          if (this.update_func!=undefined)
            this.update_func();
      }
    },

    pop : function() {
      var mat=this.stack.pop(this.stack.length-1);
      this.matrix.load(mat);
      if (this.update_func!=undefined)
        this.update_func();
      return mat;
    }

  });

  var WrapperVecPool=exports.WrapperVecPool = function(nsize, psize) {
    if (psize==undefined) {
        psize = 512;
    }
    if (nsize==undefined) {
        nsize = 3;
    }
    this.pools = [];
    this.cur = 0;
    this.psize = psize;
    this.bytesize = 4;
    this.nsize = nsize;
    this.new_pool();
  };

  WrapperVecPool.prototype = init_prototype(WrapperVecPool, {
    new_pool : function() {
      var pool=new Float32Array(this.psize*this.nsize);
      this.pools.push(pool);
      this.cur = 0;
    },

    get : function() {
      if (this.cur>=this.psize)
        this.new_pool();
      var pool=this.pools[this.pools.length-1];
      var n=this.nsize;
      var cur=this.cur;
      var bs=this.bytesize;
      var view=new Float32Array(pool.buffer, Math.floor(cur*n*bs), n);
      this.cur++;
      return new WVector3(view);
    }

  });

  var test_vpool=exports.test_vpool = test_vpool = new WrapperVecPool();
  var WVector3=exports.WVector3 = function(view, arg) {
    if (arg==undefined) {
        arg = undefined;
    }
    Object.defineProperty(this, "2", {get: function() {
      return this.view[2];
    }, set: function(n) {
      this.view[2] = n;
    }});
    Object.defineProperty(this, "1", {get: function() {
      return this.view[1];
    }, set: function(n) {
      this.view[1] = n;
    }});
    Object.defineProperty(this, "0", {get: function() {
      return this.view[0];
    }, set: function(n) {
      this.view[0] = n;
    }});
    this.view = view;
    Vector3.call(this, arg);
  };
  WVector3.prototype = inherit(WVector3, Vector3, {
  });
  
  return exports;
});
