//handle to module.  never access in code; for debug console use only.
var _vectormath = undefined;

define([
  "util"
], function(util) {
  "use strict";

  var exports = _vectormath = {};

  var sin=Math.sin, cos=Math.cos, abs=Math.abs, log=Math.log,
      asin=Math.asin, exp=Math.exp, acos=Math.acos, fract=Math.fract,
      sign=Math.sign, tent=Math.tent, atan2=Math.atan2, atan=Math.atan,
      pow=Math.pow, sqrt=Math.sqrt, floor=Math.floor, ceil=Math.ceil,
      min=Math.min, max=Math.max, PI=Math.PI, E=2.718281828459045;

  var Class = util.Class;
  var M_SQRT2=Math.sqrt(2.0);
  var FLT_EPSILON=2.22e-16;
  var DOT_NORM_SNAP_LIMIT = 0.00000000001;

  var basic_funcs = {
    zero    : [[], "0.0;"],
    negate  : [[], "-this[X];"],
    combine : [["b", "u", "v"], "this[X]*u + this[X]*v;"],
    interp  : [["b", "t"], "this[X] + (b[X] - this[X])*t;"],
    add    : [["b"], "this[X] + b[X];"],
    addFac : [["b", "F"], "this[X] + b[X]*F;"],
    fract  : [[], "Math.fract(this[X]);"],
    sub    : [["b"], "this[X] - b[X];"],
    mul    : [["b"], "this[X] * b[X];"],
    div    : [["b"], "this[X] / b[X];"],
    mulScalar : [["b"], "this[X] * b;"],
    divScalar : [["b"], "this[X] / b;"],
    addScalar : [["b"], "this[X] + b;"],
    subScalar : [["b"], "this[X] - b;"],
    ceil      : [[], "Math.ceil(this[X])"],
    floor     : [[], "Math.floor(this[X])"],
    abs       : [[], "Math.abs(this[X])"],
    min       : [[], "Math.min(this[X])"],
    max       : [[], "Math.max(this[X])"],
    clamp     : [["MIN", "MAX"], "min(max(this[X], MAX), MIN)"],
  };

  function bounded_acos(fac) {
    if (fac<=-1.0)
      return Math.pi;
    else 
      if (fac>=1.0)
      return 0.0;
    else 
      return Math.acos(fac);
  }

  function saasin(fac) {
    if (fac<=-1.0)
      return -Math.pi/2.0;
    else 
      if (fac>=1.0)
      return Math.pi/2.0;
    else 
      return Math.asin(fac);
  }

  var HasCSSMatrix=false;
  var HasCSSMatrixCopy=false;
  var M_SQRT2=Math.sqrt(2.0);
  var FLT_EPSILON=2.22e-16;
  function internal_matrix() {
    this.m11 = 0.0;
    this.m12 = 0.0;
    this.m13 = 0.0;
    this.m14 = 0.0;
    this.m21 = 0.0;
    this.m22 = 0.0;
    this.m23 = 0.0;
    this.m24 = 0.0;
    this.m31 = 0.0;
    this.m32 = 0.0;
    this.m33 = 0.0;
    this.m34 = 0.0;
    this.m41 = 0.0;
    this.m42 = 0.0;
    this.m43 = 0.0;
    this.m44 = 0.0;
  }

  var lookat_cache_vs3;
  var lookat_cache_vs4;

  var Matrix4 = exports.Matrix4 = class Matrix4 {
    constructor(m) {
      if (HasCSSMatrix)
        this.$matrix = new WebKitCSSMatrix;
      else 
        this.$matrix = new internal_matrix();
      this.isPersp = false;
      if (typeof m=='object') {
          if ("length" in m&&m.length>=16) {
              this.load(m);
              return ;
          }
          else 
            if (m instanceof Matrix4) {
              this.load(m);
              return ;
          }
      }
      this.makeIdentity();
    }
    clone() {
      return new Matrix4(this);
    }

    load() {
      if (arguments.length==1&&typeof arguments[0]=='object') {
          var matrix;
          if (arguments[0] instanceof Matrix4) {
              matrix = arguments[0].$matrix;
              this.isPersp = arguments[0].isPersp;
              this.$matrix.m11 = matrix.m11;
              this.$matrix.m12 = matrix.m12;
              this.$matrix.m13 = matrix.m13;
              this.$matrix.m14 = matrix.m14;
              this.$matrix.m21 = matrix.m21;
              this.$matrix.m22 = matrix.m22;
              this.$matrix.m23 = matrix.m23;
              this.$matrix.m24 = matrix.m24;
              this.$matrix.m31 = matrix.m31;
              this.$matrix.m32 = matrix.m32;
              this.$matrix.m33 = matrix.m33;
              this.$matrix.m34 = matrix.m34;
              this.$matrix.m41 = matrix.m41;
              this.$matrix.m42 = matrix.m42;
              this.$matrix.m43 = matrix.m43;
              this.$matrix.m44 = matrix.m44;
              return this;
          }
          else 
            matrix = arguments[0];
          if ("length" in matrix&&matrix.length>=16) {
              this.$matrix.m11 = matrix[0];
              this.$matrix.m12 = matrix[1];
              this.$matrix.m13 = matrix[2];
              this.$matrix.m14 = matrix[3];
              this.$matrix.m21 = matrix[4];
              this.$matrix.m22 = matrix[5];
              this.$matrix.m23 = matrix[6];
              this.$matrix.m24 = matrix[7];
              this.$matrix.m31 = matrix[8];
              this.$matrix.m32 = matrix[9];
              this.$matrix.m33 = matrix[10];
              this.$matrix.m34 = matrix[11];
              this.$matrix.m41 = matrix[12];
              this.$matrix.m42 = matrix[13];
              this.$matrix.m43 = matrix[14];
              this.$matrix.m44 = matrix[15];
              return this;
          }
      }
      
      this.makeIdentity();
      
      return this;
    }

    toJSON() {
      return {isPersp: this.isPersp, items: this.getAsArray()}
    }

    static fromJSON() {
      var mat=new Matrix4();
      mat.load(json.items);
      mat.isPersp = json.isPersp;
      return mat;
    }

    getAsArray() {
      return [this.$matrix.m11, this.$matrix.m12, this.$matrix.m13, this.$matrix.m14, this.$matrix.m21, this.$matrix.m22, this.$matrix.m23, this.$matrix.m24, this.$matrix.m31, this.$matrix.m32, this.$matrix.m33, this.$matrix.m34, this.$matrix.m41, this.$matrix.m42, this.$matrix.m43, this.$matrix.m44];
    }

    getAsFloat32Array() {
      if (HasCSSMatrixCopy) {
          var array=new Float32Array(16);
          this.$matrix.copy(array);
          return array;
      }
      return new Float32Array(this.getAsArray());
    }

    setUniform(ctx, loc, transpose) {
      if (Matrix4.setUniformArray==undefined) {
          Matrix4.setUniformWebGLArray = new Float32Array(16);
          Matrix4.setUniformArray = new Array(16);
      }
      if (HasCSSMatrixCopy)
        this.$matrix.copy(Matrix4.setUniformWebGLArray);
      else {
        Matrix4.setUniformArray[0] = this.$matrix.m11;
        Matrix4.setUniformArray[1] = this.$matrix.m12;
        Matrix4.setUniformArray[2] = this.$matrix.m13;
        Matrix4.setUniformArray[3] = this.$matrix.m14;
        Matrix4.setUniformArray[4] = this.$matrix.m21;
        Matrix4.setUniformArray[5] = this.$matrix.m22;
        Matrix4.setUniformArray[6] = this.$matrix.m23;
        Matrix4.setUniformArray[7] = this.$matrix.m24;
        Matrix4.setUniformArray[8] = this.$matrix.m31;
        Matrix4.setUniformArray[9] = this.$matrix.m32;
        Matrix4.setUniformArray[10] = this.$matrix.m33;
        Matrix4.setUniformArray[11] = this.$matrix.m34;
        Matrix4.setUniformArray[12] = this.$matrix.m41;
        Matrix4.setUniformArray[13] = this.$matrix.m42;
        Matrix4.setUniformArray[14] = this.$matrix.m43;
        Matrix4.setUniformArray[15] = this.$matrix.m44;
        Matrix4.setUniformWebGLArray.set(Matrix4.setUniformArray);
      }
      ctx.uniformMatrix4fv(loc, transpose, Matrix4.setUniformWebGLArray);
    }

    makeIdentity() {
      this.$matrix.m11 = 1;
      this.$matrix.m12 = 0;
      this.$matrix.m13 = 0;
      this.$matrix.m14 = 0;
      this.$matrix.m21 = 0;
      this.$matrix.m22 = 1;
      this.$matrix.m23 = 0;
      this.$matrix.m24 = 0;
      this.$matrix.m31 = 0;
      this.$matrix.m32 = 0;
      this.$matrix.m33 = 1;
      this.$matrix.m34 = 0;
      this.$matrix.m41 = 0;
      this.$matrix.m42 = 0;
      this.$matrix.m43 = 0;
      this.$matrix.m44 = 1;
    }

    transpose() {
      var tmp=this.$matrix.m12;
      this.$matrix.m12 = this.$matrix.m21;
      this.$matrix.m21 = tmp;
      tmp = this.$matrix.m13;
      this.$matrix.m13 = this.$matrix.m31;
      this.$matrix.m31 = tmp;
      tmp = this.$matrix.m14;
      this.$matrix.m14 = this.$matrix.m41;
      this.$matrix.m41 = tmp;
      tmp = this.$matrix.m23;
      this.$matrix.m23 = this.$matrix.m32;
      this.$matrix.m32 = tmp;
      tmp = this.$matrix.m24;
      this.$matrix.m24 = this.$matrix.m42;
      this.$matrix.m42 = tmp;
      tmp = this.$matrix.m34;
      this.$matrix.m34 = this.$matrix.m43;
      this.$matrix.m43 = tmp;
    }

    invert() {
      if (HasCSSMatrix) {
          this.$matrix = this.$matrix.inverse();
          return ;
      }
      var det=this._determinant4x4();
      if (Math.abs(det)<1e-08)
        return null;
      this._makeAdjoint();
      this.$matrix.m11/=det;
      this.$matrix.m12/=det;
      this.$matrix.m13/=det;
      this.$matrix.m14/=det;
      this.$matrix.m21/=det;
      this.$matrix.m22/=det;
      this.$matrix.m23/=det;
      this.$matrix.m24/=det;
      this.$matrix.m31/=det;
      this.$matrix.m32/=det;
      this.$matrix.m33/=det;
      this.$matrix.m34/=det;
      this.$matrix.m41/=det;
      this.$matrix.m42/=det;
      this.$matrix.m43/=det;
      this.$matrix.m44/=det;
    }

    translate(x, y, z) {
      if (typeof x=='object'&&"length" in x) {
          var t=x;
          x = t[0];
          y = t[1];
          z = t[2];
      }
      else {
        if (x==undefined)
          x = 0;
        if (y==undefined)
          y = 0;
        if (z==undefined)
          z = 0;
      }
      if (HasCSSMatrix) {
          this.$matrix = this.$matrix.translate(x, y, z);
          return ;
      }
      var matrix=new Matrix4();
      matrix.$matrix.m41 = x;
      matrix.$matrix.m42 = y;
      matrix.$matrix.m43 = z;
      this.multiply(matrix);
    }

    scale(x, y, z) {
      if (typeof x=='object'&&"length" in x) {
          var t=x;
          x = t[0];
          y = t[1];
          z = t[2];
      }
      else {
        if (x==undefined)
          x = 1;
        if (z==undefined) {
            if (y==undefined) {
                y = x;
                z = x;
            }
            else 
              z = 1;
        }
        else 
          if (y==undefined)
          y = x;
      }
      if (HasCSSMatrix) {
          this.$matrix = this.$matrix.scale(x, y, z);
          return ;
      }
      var matrix=new Matrix4();
      matrix.$matrix.m11 = x;
      matrix.$matrix.m22 = y;
      matrix.$matrix.m33 = z;
      this.multiply(matrix);
    }
    
    euler_rotate(x, y, z, order) {
      if (order == undefined) 
        order = "xyz"
      else
        order = order.toLowerCase();
        
      var xmat = new Matrix4();
      var m = xmat.$matrix;
      
      var c = Math.cos(x), s = Math.sin(x);
      
      m.m22 = c; m.m23 = s;
      m.m32 = -s; m.m33 = c;
      
      var ymat = new Matrix4();
      c = Math.cos(y); s = Math.sin(y);
      var m = ymat.$matrix;
      
      m.m11 = c;  m.m13 = s;
      m.m31 = -s; m.m33 = c;
      
      ymat.multiply(xmat);

      var zmat = new Matrix4();
      c = Math.cos(z); s = Math.sin(z);
      var m = zmat.$matrix;
      
      m.m11 = c;  m.m12 = -s;
      m.m21 = s;  m.m22 = c;
      
      zmat.multiply(ymat);
      
      //console.log(""+ymat);
      this.preMultiply(zmat);
    }
    
    toString() {
      var s = ""
      var m = this.$matrix;
      
      function dec(d) {
        var ret = d.toFixed(3);
        
        if (ret[0] != "-") //make room for negative signs
          ret = " " + ret
        return ret 
      }
      
      s  = dec(m.m11) +", " + dec(m.m12) + ", " + dec(m.m13) + ", " + dec(m.m14) + "\n";
      s += dec(m.m21) +", " + dec(m.m22) + ", " + dec(m.m23) + ", " + dec(m.m24) + "\n";
      s += dec(m.m31) +", " + dec(m.m32) + ", " + dec(m.m33) + ", " + dec(m.m34) + "\n";
      s += dec(m.m41) +", " + dec(m.m42) + ", " + dec(m.m43) + ", " + dec(m.m44) + "\n";
      
      return s
    }
    
    rotate(angle, x, y, z) {
      if (typeof x=='object'&&"length" in x) {
          var t=x;
          x = t[0];
          y = t[1];
          z = t[2];
      }
      else {
        if (arguments.length==1) {
            x = 0;
            y = 0;
            z = 1;
        }
        else 
          if (arguments.length==3) {
            this.rotate(angle, 1, 0, 0);
            this.rotate(x, 0, 1, 0);
            this.rotate(y, 0, 0, 1);
            return ;
        }
      }
      if (HasCSSMatrix) {
          this.$matrix = this.$matrix.rotateAxisAngle(x, y, z, angle);
          return ;
      }
      angle/=2;
      var sinA=Math.sin(angle);
      var cosA=Math.cos(angle);
      var sinA2=sinA*sinA;
      var len=Math.sqrt(x*x+y*y+z*z);
      if (len==0) {
          x = 0;
          y = 0;
          z = 1;
      }
      else 
        if (len!=1) {
          x/=len;
          y/=len;
          z/=len;
      }
      var mat=new Matrix4();
      if (x==1&&y==0&&z==0) {
          mat.$matrix.m11 = 1;
          mat.$matrix.m12 = 0;
          mat.$matrix.m13 = 0;
          mat.$matrix.m21 = 0;
          mat.$matrix.m22 = 1-2*sinA2;
          mat.$matrix.m23 = 2*sinA*cosA;
          mat.$matrix.m31 = 0;
          mat.$matrix.m32 = -2*sinA*cosA;
          mat.$matrix.m33 = 1-2*sinA2;
          mat.$matrix.m14 = mat.$matrix.m24 = mat.$matrix.m34 = 0;
          mat.$matrix.m41 = mat.$matrix.m42 = mat.$matrix.m43 = 0;
          mat.$matrix.m44 = 1;
      }
      else 
        if (x==0&&y==1&&z==0) {
          mat.$matrix.m11 = 1-2*sinA2;
          mat.$matrix.m12 = 0;
          mat.$matrix.m13 = -2*sinA*cosA;
          mat.$matrix.m21 = 0;
          mat.$matrix.m22 = 1;
          mat.$matrix.m23 = 0;
          mat.$matrix.m31 = 2*sinA*cosA;
          mat.$matrix.m32 = 0;
          mat.$matrix.m33 = 1-2*sinA2;
          mat.$matrix.m14 = mat.$matrix.m24 = mat.$matrix.m34 = 0;
          mat.$matrix.m41 = mat.$matrix.m42 = mat.$matrix.m43 = 0;
          mat.$matrix.m44 = 1;
      }
      else 
        if (x==0&&y==0&&z==1) {
          mat.$matrix.m11 = 1-2*sinA2;
          mat.$matrix.m12 = 2*sinA*cosA;
          mat.$matrix.m13 = 0;
          mat.$matrix.m21 = -2*sinA*cosA;
          mat.$matrix.m22 = 1-2*sinA2;
          mat.$matrix.m23 = 0;
          mat.$matrix.m31 = 0;
          mat.$matrix.m32 = 0;
          mat.$matrix.m33 = 1;
          mat.$matrix.m14 = mat.$matrix.m24 = mat.$matrix.m34 = 0;
          mat.$matrix.m41 = mat.$matrix.m42 = mat.$matrix.m43 = 0;
          mat.$matrix.m44 = 1;
      }
      else {
        var x2=x*x;
        var y2=y*y;
        var z2=z*z;
        mat.$matrix.m11 = 1-2*(y2+z2)*sinA2;
        mat.$matrix.m12 = 2*(x*y*sinA2+z*sinA*cosA);
        mat.$matrix.m13 = 2*(x*z*sinA2-y*sinA*cosA);
        mat.$matrix.m21 = 2*(y*x*sinA2-z*sinA*cosA);
        mat.$matrix.m22 = 1-2*(z2+x2)*sinA2;
        mat.$matrix.m23 = 2*(y*z*sinA2+x*sinA*cosA);
        mat.$matrix.m31 = 2*(z*x*sinA2+y*sinA*cosA);
        mat.$matrix.m32 = 2*(z*y*sinA2-x*sinA*cosA);
        mat.$matrix.m33 = 1-2*(x2+y2)*sinA2;
        mat.$matrix.m14 = mat.$matrix.m24 = mat.$matrix.m34 = 0;
        mat.$matrix.m41 = mat.$matrix.m42 = mat.$matrix.m43 = 0;
        mat.$matrix.m44 = 1;
      }
      this.multiply(mat);
    }

    preMultiply(mat) {
      var tmp = new Matrix4();
      
      tmp.multiply(this);
      tmp.multiply(mat);
      
      this.load(tmp);
    }
    
    multiply(mat) {
      if (HasCSSMatrix) {
          this.$matrix = this.$matrix.multiply(mat.$matrix);
          return ;
      }
      
      var m11=(mat.$matrix.m11*this.$matrix.m11+mat.$matrix.m12*this.$matrix.m21+mat.$matrix.m13*this.$matrix.m31+mat.$matrix.m14*this.$matrix.m41);
      var m12=(mat.$matrix.m11*this.$matrix.m12+mat.$matrix.m12*this.$matrix.m22+mat.$matrix.m13*this.$matrix.m32+mat.$matrix.m14*this.$matrix.m42);
      var m13=(mat.$matrix.m11*this.$matrix.m13+mat.$matrix.m12*this.$matrix.m23+mat.$matrix.m13*this.$matrix.m33+mat.$matrix.m14*this.$matrix.m43);
      var m14=(mat.$matrix.m11*this.$matrix.m14+mat.$matrix.m12*this.$matrix.m24+mat.$matrix.m13*this.$matrix.m34+mat.$matrix.m14*this.$matrix.m44);
      var m21=(mat.$matrix.m21*this.$matrix.m11+mat.$matrix.m22*this.$matrix.m21+mat.$matrix.m23*this.$matrix.m31+mat.$matrix.m24*this.$matrix.m41);
      var m22=(mat.$matrix.m21*this.$matrix.m12+mat.$matrix.m22*this.$matrix.m22+mat.$matrix.m23*this.$matrix.m32+mat.$matrix.m24*this.$matrix.m42);
      var m23=(mat.$matrix.m21*this.$matrix.m13+mat.$matrix.m22*this.$matrix.m23+mat.$matrix.m23*this.$matrix.m33+mat.$matrix.m24*this.$matrix.m43);
      var m24=(mat.$matrix.m21*this.$matrix.m14+mat.$matrix.m22*this.$matrix.m24+mat.$matrix.m23*this.$matrix.m34+mat.$matrix.m24*this.$matrix.m44);
      var m31=(mat.$matrix.m31*this.$matrix.m11+mat.$matrix.m32*this.$matrix.m21+mat.$matrix.m33*this.$matrix.m31+mat.$matrix.m34*this.$matrix.m41);
      var m32=(mat.$matrix.m31*this.$matrix.m12+mat.$matrix.m32*this.$matrix.m22+mat.$matrix.m33*this.$matrix.m32+mat.$matrix.m34*this.$matrix.m42);
      var m33=(mat.$matrix.m31*this.$matrix.m13+mat.$matrix.m32*this.$matrix.m23+mat.$matrix.m33*this.$matrix.m33+mat.$matrix.m34*this.$matrix.m43);
      var m34=(mat.$matrix.m31*this.$matrix.m14+mat.$matrix.m32*this.$matrix.m24+mat.$matrix.m33*this.$matrix.m34+mat.$matrix.m34*this.$matrix.m44);
      var m41=(mat.$matrix.m41*this.$matrix.m11+mat.$matrix.m42*this.$matrix.m21+mat.$matrix.m43*this.$matrix.m31+mat.$matrix.m44*this.$matrix.m41);
      var m42=(mat.$matrix.m41*this.$matrix.m12+mat.$matrix.m42*this.$matrix.m22+mat.$matrix.m43*this.$matrix.m32+mat.$matrix.m44*this.$matrix.m42);
      var m43=(mat.$matrix.m41*this.$matrix.m13+mat.$matrix.m42*this.$matrix.m23+mat.$matrix.m43*this.$matrix.m33+mat.$matrix.m44*this.$matrix.m43);
      var m44=(mat.$matrix.m41*this.$matrix.m14+mat.$matrix.m42*this.$matrix.m24+mat.$matrix.m43*this.$matrix.m34+mat.$matrix.m44*this.$matrix.m44);
      this.$matrix.m11 = m11;
      this.$matrix.m12 = m12;
      this.$matrix.m13 = m13;
      this.$matrix.m14 = m14;
      this.$matrix.m21 = m21;
      this.$matrix.m22 = m22;
      this.$matrix.m23 = m23;
      this.$matrix.m24 = m24;
      this.$matrix.m31 = m31;
      this.$matrix.m32 = m32;
      this.$matrix.m33 = m33;
      this.$matrix.m34 = m34;
      this.$matrix.m41 = m41;
      this.$matrix.m42 = m42;
      this.$matrix.m43 = m43;
      this.$matrix.m44 = m44;
    }

    divide(divisor) {
      this.$matrix.m11/=divisor;
      this.$matrix.m12/=divisor;
      this.$matrix.m13/=divisor;
      this.$matrix.m14/=divisor;
      this.$matrix.m21/=divisor;
      this.$matrix.m22/=divisor;
      this.$matrix.m23/=divisor;
      this.$matrix.m24/=divisor;
      this.$matrix.m31/=divisor;
      this.$matrix.m32/=divisor;
      this.$matrix.m33/=divisor;
      this.$matrix.m34/=divisor;
      this.$matrix.m41/=divisor;
      this.$matrix.m42/=divisor;
      this.$matrix.m43/=divisor;
      this.$matrix.m44/=divisor;
    }

    ortho(left, right, bottom, top, near, far) {
      var tx=(left+right)/(left-right);
      var ty=(top+bottom)/(top-bottom);
      var tz=(far+near)/(far-near);
      var matrix=new Matrix4();
      matrix.$matrix.m11 = 2/(left-right);
      matrix.$matrix.m12 = 0;
      matrix.$matrix.m13 = 0;
      matrix.$matrix.m14 = 0;
      matrix.$matrix.m21 = 0;
      matrix.$matrix.m22 = 2/(top-bottom);
      matrix.$matrix.m23 = 0;
      matrix.$matrix.m24 = 0;
      matrix.$matrix.m31 = 0;
      matrix.$matrix.m32 = 0;
      matrix.$matrix.m33 = -2/(far-near);
      matrix.$matrix.m34 = 0;
      matrix.$matrix.m41 = tx;
      matrix.$matrix.m42 = ty;
      matrix.$matrix.m43 = tz;
      matrix.$matrix.m44 = 1;
      this.multiply(matrix);
    }

    frustum(left, right, bottom, top, near, far) {
      var matrix=new Matrix4();
      var A=(right+left)/(right-left);
      var B=(top+bottom)/(top-bottom);
      var C=-(far+near)/(far-near);
      var D=-(2*far*near)/(far-near);
      matrix.$matrix.m11 = (2*near)/(right-left);
      matrix.$matrix.m12 = 0;
      matrix.$matrix.m13 = 0;
      matrix.$matrix.m14 = 0;
      matrix.$matrix.m21 = 0;
      matrix.$matrix.m22 = 2*near/(top-bottom);
      matrix.$matrix.m23 = 0;
      matrix.$matrix.m24 = 0;
      matrix.$matrix.m31 = A;
      matrix.$matrix.m32 = B;
      matrix.$matrix.m33 = C;
      matrix.$matrix.m34 = -1;
      matrix.$matrix.m41 = 0;
      matrix.$matrix.m42 = 0;
      matrix.$matrix.m43 = D;
      matrix.$matrix.m44 = 0;
      this.isPersp = true;
      this.multiply(matrix);
    }

    perspective(fovy, aspect, zNear, zFar) {
      var top=Math.tan(fovy*Math.PI/360)*zNear;
      var bottom=-top;
      var left=aspect*bottom;
      var right=aspect*top;
      this.frustum(left, right, bottom, top, zNear, zFar);
    }

    lookat(pos, target, up) {
      var matrix=new Matrix4();
      
      var vec = lookat_cache_vs3.next().load(pos).sub(target);
      var len = vec.vectorLength();
      vec.normalize();
      
      var zvec = vec;
      var yvec = lookat_cache_vs3.next().load(up).normalize();
      var xvec = lookat_cache_vs3.next().load(yvec).cross(zvec).normalize();
      
      //*

      matrix.$matrix.m11 = xvec[0];
      matrix.$matrix.m12 = yvec[0];
      matrix.$matrix.m13 = zvec[0];
      matrix.$matrix.m14 = 0;
      matrix.$matrix.m21 = xvec[1];
      matrix.$matrix.m22 = yvec[1];
      matrix.$matrix.m23 = zvec[1];
      matrix.$matrix.m24 = 0;
      matrix.$matrix.m31 = xvec[2];
      matrix.$matrix.m32 = yvec[2];
      matrix.$matrix.m33 = zvec[2];
      
      //*/
      /*
      matrix.$matrix.m11 = xvec[0];
      matrix.$matrix.m12 = xvec[1];
      matrix.$matrix.m13 = xvec[2];
      matrix.$matrix.m14 = 0;
      matrix.$matrix.m21 = yvec[0];
      matrix.$matrix.m22 = yvec[1];
      matrix.$matrix.m23 = yvec[2];
      matrix.$matrix.m24 = 0;
      matrix.$matrix.m31 = zvec[0];
      matrix.$matrix.m32 = zvec[1];
      matrix.$matrix.m33 = zvec[2];
      matrix.$matrix.m34 = 0;
      matrix.$matrix.m41 = 0;
      matrix.$matrix.m42 = 0;
      matrix.$matrix.m43 = 0;
      matrix.$matrix.m44 = 1;
      */
      
      matrix.translate(-pos[0], -pos[1], -pos[2]);
      this.multiply(matrix);
    }

    makeRotationOnly() {
      var m = this.$matrix;
      
      m.m41 = m.m42 = m.m43 = 0.0;
      m.m44 = 1.0;
      
      return this;
    }
    
    decompose(_translate, _rotate, _scale, _skew, _perspective) {
      if (this.$matrix.m44==0)
        return false;
      
      var translate, rotate, scale, skew, perspective;
      var translate=(_translate==undefined||!("length" in _translate)) ? new Vector3 : _translate;
      var rotate=(_rotate==undefined||!("length" in _rotate)) ? new Vector3 : _rotate;
      var scale=(_scale==undefined||!("length" in _scale)) ? new Vector3 : _scale;
      var skew=(_skew==undefined||!("length" in _skew)) ? new Vector3 : _skew;
      var perspective=(_perspective==undefined||!("length" in _perspective)) ? new Array(4) : _perspective;
      var matrix=new Matrix4(this);
      matrix.divide(matrix.$matrix.m44);
      var perspectiveMatrix=new Matrix4(matrix);
      perspectiveMatrix.$matrix.m14 = 0;
      perspectiveMatrix.$matrix.m24 = 0;
      perspectiveMatrix.$matrix.m34 = 0;
      perspectiveMatrix.$matrix.m44 = 1;
      if (perspectiveMatrix._determinant4x4()==0)
        return false;
        
      if (matrix.$matrix.m14!=0||matrix.$matrix.m24!=0||matrix.$matrix.m34!=0) {
          var rightHandSide=[matrix.$matrix.m14, matrix.$matrix.m24, matrix.$matrix.m34, matrix.$matrix.m44];
          var inversePerspectiveMatrix=new Matrix4(perspectiveMatrix);
          inversePerspectiveMatrix.invert();
          var transposedInversePerspectiveMatrix=new Matrix4(inversePerspectiveMatrix);
          transposedInversePerspectiveMatrix.transpose();
          
          var v4 = new Vector3(rightHandSide);
          v4.multVecMatrix(transposedInversePerspectiveMatrix)
          
          perspective[0] = v4[0];
          perspective[1] = v4[1];
          perspective[2] = v4[2];
          perspective[3] = v4[3];
          
          matrix.$matrix.m14 = matrix.$matrix.m24 = matrix.$matrix.m34 = 0;
          matrix.$matrix.m44 = 1;
      }
      else {
        perspective[0] = perspective[1] = perspective[2] = 0;
        perspective[3] = 1;
      }
      translate[0] = matrix.$matrix.m41;
      matrix.$matrix.m41 = 0;
      translate[1] = matrix.$matrix.m42;
      matrix.$matrix.m42 = 0;
      translate[2] = matrix.$matrix.m43;
      matrix.$matrix.m43 = 0;
      var row0=new Vector3([matrix.$matrix.m11, matrix.$matrix.m12, matrix.$matrix.m13]);
      var row1=new Vector3([matrix.$matrix.m21, matrix.$matrix.m22, matrix.$matrix.m23]);
      var row2=new Vector3([matrix.$matrix.m31, matrix.$matrix.m32, matrix.$matrix.m33]);
      scale[0] = row0.vectorLength();
      row0.divide(scale[0]);
      skew[0] = row0.dot(row1);
      row1.combine(row0, 1.0, -skew[0]);
      scale[1] = row1.vectorLength();
      row1.divide(scale[1]);
      skew[0]/=scale[1];
      skew[1] = row1.dot(row2);
      row2.combine(row0, 1.0, -skew[1]);
      skew[2] = row1.dot(row2);
      row2.combine(row1, 1.0, -skew[2]);
      scale[2] = row2.vectorLength();
      row2.divide(scale[2]);
      skew[1]/=scale[2];
      skew[2]/=scale[2];
      var pdum3=new Vector3(row1);
      pdum3.cross(row2);
      if (row0.dot(pdum3)<0) {
          for (var i=0; i<3; i++) {
              scale[i]*=-1;
              row[0][i]*=-1;
              row[1][i]*=-1;
              row[2][i]*=-1;
          }
      }
      rotate[1] = Math.asin(-row0[2]);
      if (Math.cos(rotate[1])!=0) {
          rotate[0] = Math.atan2(row1[2], row2[2]);
          rotate[2] = Math.atan2(row0[1], row0[0]);
      }
      else {
        rotate[0] = Math.atan2(-row2[0], row1[1]);
        rotate[2] = 0;
      }
      var rad2deg=180/Math.PI;
      rotate[0]*=rad2deg;
      rotate[1]*=rad2deg;
      rotate[2]*=rad2deg;
      return true;
    }

    _determinant2x2(a, b, c, d) {
      return a*d-b*c;
    }

    _determinant3x3(a1, a2, a3, b1, b2, b3, c1, c2, c3) {
      return a1*this._determinant2x2(b2, b3, c2, c3)-b1*this._determinant2x2(a2, a3, c2, c3)+c1*this._determinant2x2(a2, a3, b2, b3);
    }

    _determinant4x4() {
      var a1=this.$matrix.m11;
      var b1=this.$matrix.m12;
      var c1=this.$matrix.m13;
      var d1=this.$matrix.m14;
      var a2=this.$matrix.m21;
      var b2=this.$matrix.m22;
      var c2=this.$matrix.m23;
      var d2=this.$matrix.m24;
      var a3=this.$matrix.m31;
      var b3=this.$matrix.m32;
      var c3=this.$matrix.m33;
      var d3=this.$matrix.m34;
      var a4=this.$matrix.m41;
      var b4=this.$matrix.m42;
      var c4=this.$matrix.m43;
      var d4=this.$matrix.m44;
      return a1*this._determinant3x3(b2, b3, b4, c2, c3, c4, d2, d3, d4)-b1*this._determinant3x3(a2, a3, a4, c2, c3, c4, d2, d3, d4)+c1*this._determinant3x3(a2, a3, a4, b2, b3, b4, d2, d3, d4)-d1*this._determinant3x3(a2, a3, a4, b2, b3, b4, c2, c3, c4);
    }

    _makeAdjoint() {
      var a1=this.$matrix.m11;
      var b1=this.$matrix.m12;
      var c1=this.$matrix.m13;
      var d1=this.$matrix.m14;
      var a2=this.$matrix.m21;
      var b2=this.$matrix.m22;
      var c2=this.$matrix.m23;
      var d2=this.$matrix.m24;
      var a3=this.$matrix.m31;
      var b3=this.$matrix.m32;
      var c3=this.$matrix.m33;
      var d3=this.$matrix.m34;
      var a4=this.$matrix.m41;
      var b4=this.$matrix.m42;
      var c4=this.$matrix.m43;
      var d4=this.$matrix.m44;
      this.$matrix.m11 = this._determinant3x3(b2, b3, b4, c2, c3, c4, d2, d3, d4);
      this.$matrix.m21 = -this._determinant3x3(a2, a3, a4, c2, c3, c4, d2, d3, d4);
      this.$matrix.m31 = this._determinant3x3(a2, a3, a4, b2, b3, b4, d2, d3, d4);
      this.$matrix.m41 = -this._determinant3x3(a2, a3, a4, b2, b3, b4, c2, c3, c4);
      this.$matrix.m12 = -this._determinant3x3(b1, b3, b4, c1, c3, c4, d1, d3, d4);
      this.$matrix.m22 = this._determinant3x3(a1, a3, a4, c1, c3, c4, d1, d3, d4);
      this.$matrix.m32 = -this._determinant3x3(a1, a3, a4, b1, b3, b4, d1, d3, d4);
      this.$matrix.m42 = this._determinant3x3(a1, a3, a4, b1, b3, b4, c1, c3, c4);
      this.$matrix.m13 = this._determinant3x3(b1, b2, b4, c1, c2, c4, d1, d2, d4);
      this.$matrix.m23 = -this._determinant3x3(a1, a2, a4, c1, c2, c4, d1, d2, d4);
      this.$matrix.m33 = this._determinant3x3(a1, a2, a4, b1, b2, b4, d1, d2, d4);
      this.$matrix.m43 = -this._determinant3x3(a1, a2, a4, b1, b2, b4, c1, c2, c4);
      this.$matrix.m14 = -this._determinant3x3(b1, b2, b3, c1, c2, c3, d1, d2, d3);
      this.$matrix.m24 = this._determinant3x3(a1, a2, a3, c1, c2, c3, d1, d2, d3);
      this.$matrix.m34 = -this._determinant3x3(a1, a2, a3, b1, b2, b3, d1, d2, d3);
      this.$matrix.m44 = this._determinant3x3(a1, a2, a3, b1, b2, b3, c1, c2, c3);
    }
  };

  function make_norm_safe_dot(cls) {
    var _dot = cls.prototype.dot;
    
    cls.prototype._dot = _dot;
    cls.prototype.dot = function(b) {
      var ret = _dot.call(this, b);
      
      if (ret >= 1.0-DOT_NORM_SNAP_LIMIT && ret <= 1.0+DOT_NORM_SNAP_LIMIT)
        return 1.0;
      if (ret >= -1.0-DOT_NORM_SNAP_LIMIT && ret <= -1.0+DOT_NORM_SNAP_LIMIT)
        return -1.0;
        
      return ret;
    }
  }

  var BaseVector = exports.BaseVector = class BaseVector extends Array {
    constructor() {
      super();
      
      //this.xyzw = this.init_swizzle(4);
      //this.xyz = this.init_swizzle(3);
      //this.xy = this.init_swizzle(2);
    }
    
    load(data) {
      throw new Error("Implement me!");
    }
    
    init_swizzle(size) {
      var ret = {};
      var cls = size == 4 ? Vector4 : (size == 3 ? Vector3 : Vector2);
      
      for (var k in cls.prototype) {
        var v = cls.prototype[k];
        if (typeof v != "function" && !(v instanceof Function))
          continue;
        
        ret[k] = v.bind(this);
      }
      
      return ret;
    }
    
    vectorLength() {
      return sqrt(this.dot(this));
    }
    
    normalize() {
      var l = this.vectorLength();
      if (l > 0.00000001) {
        this.mulScalar(1.0/l);
      }
      
      return this;
    }
    
    static inherit(cls, vectorsize) {
      make_norm_safe_dot(cls);
     
     var f;
      var vectorDotDistance = "f = function vectorDistance(b) {\n";
      for (var i=0; i<vectorsize; i++) {
        vectorDotDistance += "var d"+i+" = this["+i+"]-b["+i+"];\n";
      }
      
      vectorDotDistance += "return ("
      for (var i=0; i<vectorsize; i++) {
        if (i > 0)
          vectorDotDistance += " + ";
        vectorDotDistance += "d"+i+"*d"+i;
      }
      vectorDotDistance += ");\n"
      vectorDotDistance += "};";
      cls.prototype.vectorDotDistance = eval(vectorDotDistance);
      
      var f;
      var vectorDistance = "f = function vectorDistance(b) {\n";
      for (var i=0; i<vectorsize; i++) {
        vectorDistance += "var d"+i+" = this["+i+"]-b["+i+"];\n";
      }
      
      vectorDistance += "return sqrt("
      for (var i=0; i<vectorsize; i++) {
        if (i > 0)
          vectorDistance += " + ";
        vectorDistance += "d"+i+"*d"+i;
      }
      vectorDistance += ");\n"
      vectorDistance += "};";
      cls.prototype.vectorDistance = eval(vectorDistance);
      
      
      for (var k in basic_funcs) {
        var func = basic_funcs[k];
        var args = func[0];
        var line = func[1];
        var f;
        
        var code = "f = function " + k + "("
        for (var i=0; i<args.length; i++) {
          if (i > 0)
            code += ", ";
          
          line = line.replace(args[i], args[i].toLowerCase());
          code += args[i].toLowerCase();
        }
        code += ") {\n";
        
        for (var i=0; i<vectorsize; i++) {
          var line2 = line.replace(/X/g, ""+i);
          code += "    this["+i+"] = " + line2 + "\n";
        }
        
        code += "return this;"
        code += "}\n";
        
        //console.log(code);
        var f = eval(code);
        
        cls.prototype[k] = f;
        //console.log(k, f);
      }
    }
  }

  var Vector4 = exports.Vector4 = class Vector4 extends BaseVector {
    constructor(data) {
      super();
      
      if (arguments.length > 1) {
        throw new Error("unexpected argument");
      }
      
      this.length = 4;
      this[0] = this[1] = this[2] = this[3] = 0.0;
      
      if (data != undefined) {
        this.load(data);
      }
    }
    
    load(data) {
      if (data == undefined) 
        return this;
      
      this[0] = data[0];
      this[1] = data[1];
      this[2] = data[2];
      this[3] = data[3];
      
      return this;
    }
    
    dot(b) {
      return this[0]*b[0] + this[1]*b[1] + this[2]*b[2] + this[3]*b[3];
    }

    mulVecQuat(q) {
      var t0=-this[1]*this[0]-this[2]*this[1]-this[3]*this[2];
      var t1=this[0]*this[0]+this[2]*this[2]-this[3]*this[1];
      var t2=this[0]*this[1]+this[3]*this[0]-this[1]*this[2];
      this[2] = this[0]*this[2]+this[1]*this[1]-this[2]*this[0];
      this[0] = t1;
      this[1] = t2;
      t1 = t0*-this[1]+this[0]*this[0]-this[1]*this[3]+this[2]*this[2];
      t2 = t0*-this[2]+this[1]*this[0]-this[2]*this[1]+this[0]*this[3];
      this[2] = t0*-this[3]+this[2]*this[0]-this[0]*this[2]+this[1]*this[1];
      this[0] = t1;
      this[1] = t2;
      
      return this;
    }

    multVecMatrix(matrix) {
      var x=this[0];
      var y=this[1];
      var z=this[2];
      var w=this[3];
      this[0] = matrix.$matrix.m41+x*matrix.$matrix.m11+y*matrix.$matrix.m21+z*matrix.$matrix.m31+w*matrix.$matrix.m41;
      this[1] = matrix.$matrix.m42+x*matrix.$matrix.m12+y*matrix.$matrix.m22+z*matrix.$matrix.m32+w*matrix.$matrix.m42;
      this[2] = matrix.$matrix.m43+x*matrix.$matrix.m13+y*matrix.$matrix.m23+z*matrix.$matrix.m33+w*matrix.$matrix.m43;
      this[3] = w*matrix.$matrix.m44+x*matrix.$matrix.m14+y*matrix.$matrix.m24+z*matrix.$matrix.m34;
      return w;
    }
    
    cross(v) {
      var x = this[1]*v[2] - this[2]*v[1];
      var y = this[2]*v[0] - this[0]*v[2];
      var z = this[0]*v[1] - this[1]*v[0];
      
      this[0] = x;
      this[1] = y;
      this[2] = z;
      
      return this;
    }
    
    preNormalizedAngle(v2) {
      if (this.dot(v2)<0.0) {
          var vec=new Vector4();
          vec[0] = -v2[0];
          vec[1] = -v2[1];
          vec[2] = -v2[2];
          vec[3] = -v2[3];
          return Math.pi-2.0*saasin(vec.vectorDistance(this)/2.0);
      }
      else 
        return 2.0*saasin(v2.vectorDistance(this)/2.0);
    }
  }



  var _v3nd_n1_normalizedDot, _v3nd_n2_normalizedDot;
  var _v3nd4_n1_normalizedDot4, _v3nd4_n2_normalizedDot4;

  var Vector3 = exports.Vector3 = class Vector3 extends BaseVector {
    constructor(data) {
      super();
      
      if (arguments.length > 1) {
        throw new Error("unexpected argument");
      }
      
      this.length = 3;
      this[0] = this[1] = this[2] = 0.0;
      
      if (data != undefined) {
        this.load(data);
      }
    }
    
    initVector3() {
      this.length = 3;
      this[0] = this[1] = this[2] = 0;
      return this;
    }
    
    load(data) {
      if (data == undefined) 
        return this;
      
      this[0] = data[0];
      this[1] = data[1];
      this[2] = data[2];
      
      return this;
    }
    
    dot(b) {
      return this[0]*b[0] + this[1]*b[1] + this[2]*b[2];
    }
    
    normalizedDot(v) {
      $_v3nd_n1_normalizedDot.load(this);
      $_v3nd_n2_normalizedDot.load(v);
      $_v3nd_n1_normalizedDot.normalize();
      $_v3nd_n2_normalizedDot.normalize();
      return $_v3nd_n1_normalizedDot.dot($_v3nd_n2_normalizedDot);
    }

    //normalizedDot4
    static normalizedDot4(v1, v2, v3, v4) {
      $_v3nd4_n1_normalizedDot4.load(v2).sub(v1).normalize();
      $_v3nd4_n2_normalizedDot4.load(v4).sub(v3).normalize();
      
      return $_v3nd4_n1_normalizedDot4.dot($_v3nd4_n2_normalizedDot4);
    }

    multVecMatrix(matrix, ignore_w) {
      if (ignore_w==undefined) {
          ignore_w = false;
      }
      var x=this[0];
      var y=this[1];
      var z=this[2];
      this[0] = matrix.$matrix.m41+x*matrix.$matrix.m11+y*matrix.$matrix.m21+z*matrix.$matrix.m31;
      this[1] = matrix.$matrix.m42+x*matrix.$matrix.m12+y*matrix.$matrix.m22+z*matrix.$matrix.m32;
      this[2] = matrix.$matrix.m43+x*matrix.$matrix.m13+y*matrix.$matrix.m23+z*matrix.$matrix.m33;
      var w=matrix.$matrix.m44+x*matrix.$matrix.m14+y*matrix.$matrix.m24+z*matrix.$matrix.m34;
      if (!ignore_w&&w!=1&&w!=0&&matrix.isPersp) {
          this[0]/=w;
          this[1]/=w;
          this[2]/=w;
      }
      return w;
    }
    
    cross(v) {
      var x = this[1]*v[2] - this[2]*v[1];
      var y = this[2]*v[0] - this[0]*v[2];
      var z = this[0]*v[1] - this[1]*v[0];
      
      this[0] = x;
      this[1] = y;
      this[2] = z;
      
      return this;
    }

    //axis is optional, 0
    rot2d(A, axis) {
      var x = this[0];
      var y = this[1];
      
      if (axis == 1) {
        this[0] = x * cos(A) + y*sin(A);
        this[1] = y * cos(A) - x*sin(A);
      } else {
        this[0] = x * cos(A) - y*sin(A);
        this[1] = y * cos(A) + x*sin(A);
      }
      
      return this;
    }
   
    preNormalizedAngle(v2) {
      if (this.dot(v2)<0.0) {
          var vec=new Vector3();
          vec[0] = -v2[0];
          vec[1] = -v2[1];
          vec[2] = -v2[2];
          return Math.pi-2.0*saasin(vec.vectorDistance(this)/2.0);
      }
      else 
        return 2.0*saasin(v2.vectorDistance(this)/2.0);
    }
  }


  var Vector2 = exports.Vector2 = class Vector2 extends BaseVector {
    constructor(data) {
      super();
      
      if (arguments.length > 1) {
        throw new Error("unexpected argument");
      }
      
      this.length = 2;
      this[0] = this[1] = this[2] = 0.0;
      
      if (data != undefined) {
        this.load(data);
      }
    }
    
    load(data) {
      if (data == undefined) 
        return this;
      
      this[0] = data[0];
      this[1] = data[1];
      
      return this;
    }
    
    //axis is optional, 0
    rot2d(A, axis) {
      var x = this[0];
      var y = this[1];
      
      if (axis == 1) {
        this[0] = x * cos(A) + y*sin(A);
        this[1] = y * cos(A) - x*sin(A);
      } else {
        this[0] = x * cos(A) - y*sin(A);
        this[1] = y * cos(A) + x*sin(A);
      }
      
      return this;
    }
    
    dot(b) {
      return this[0]*b[0] + this[1]*b[1] + this[2]*b[2];
    }
    
    mulVecQuat(q) {
      var t0=-this[1]*this[0]-this[2]*this[1]-this[3]*this[2];
      var t1=this[0]*this[0]+this[2]*this[2]-this[3]*this[1];
      var t2=this[0]*this[1]+this[3]*this[0]-this[1]*this[2];
      this[2] = this[0]*this[2]+this[1]*this[1]-this[2]*this[0];
      this[0] = t1;
      this[1] = t2;
      t1 = t0*-this[1]+this[0]*this[0]-this[1]*this[3]+this[2]*this[2];
      t2 = t0*-this[2]+this[1]*this[0]-this[2]*this[1]+this[0]*this[3];
      this[2] = t0*-this[3]+this[2]*this[0]-this[0]*this[2]+this[1]*this[1];
      this[0] = t1;
      this[1] = t2;
      
      return this;
    }
  };

  var Quat = exports.Quat = class Quat extends Vector4 {
    makeUnitQuat() {
      this[0] = 1.0;
      this[1] = this[2] = this[3] = 0.0;
    }

    isZero() {
      return (this[0]==0&&this[1]==0&&this[2]==0&&this[3]==0);
    }

    mulQuat(qt) {
      var a=this[0]*qt[0]-this[1]*qt[1]-this[2]*qt[2]-this[3]*qt[3];
      var b=this[0]*qt[1]+this[1]*qt[0]+this[2]*qt[3]-this[3]*qt[2];
      var c=this[0]*qt[2]+this[2]*qt[0]+this[3]*qt[1]-this[1]*qt[3];
      this[3] = this[0]*qt[3]+this[3]*qt[0]+this[1]*qt[2]-this[2]*qt[1];
      this[0] = a;
      this[1] = b;
      this[2] = c;
    }

    conjugate() {
      this[1] = -this[1];
      this[2] = -this[2];
      this[3] = -this[3];
    }

    dotWithQuat(q2) {
      return this[0]*q2[0]+this[1]*q2[1]+this[2]*q2[2]+this[3]*q2[3];
    }

    invert() {
      var f= this.dot(this);
      
      if (f==0.0)
        return;
        
      conjugate_qt(q);
      this.mulscalar(1.0/f);
    }

    sub(q2) {
      var nq2=new Quat();
      
      nq2[0] = -q2[0];
      nq2[1] = q2[1];
      nq2[2] = q2[2];
      nq2[3] = q2[3];
      
      this.mul(nq2);
    }

    mulScalarWithFactor(fac) {
      var angle=fac*bounded_acos(this[0]);
      var co=Math.cos(angle);
      var si=Math.sin(angle);
      
      this[0] = co;
      
      var last3=Vector3([this[1], this[2], this[3]]);
      last3.normalize();
      last3.mulScalar(si);
      this[1] = last3[0];
      this[2] = last3[1];
      this[3] = last3[2];
      return this;
    }

    toMatrix(m) {
      if (m == undefined) {
        m=new Matrix4();
      }
      
      var q0=M_SQRT2*this[0];
      var q1=M_SQRT2*this[1];
      var q2=M_SQRT2*this[2];
      var q3=M_SQRT2*this[3];
      var qda=q0*q1;
      var qdb=q0*q2;
      var qdc=q0*q3;
      var qaa=q1*q1;
      var qab=q1*q2;
      var qac=q1*q3;
      var qbb=q2*q2;
      var qbc=q2*q3;
      var qcc=q3*q3;
      m.$matrix.m11 = (1.0-qbb-qcc);
      m.$matrix.m12 = (qdc+qab);
      m.$matrix.m13 = (-qdb+qac);
      m.$matrix.m14 = 0.0;
      m.$matrix.m21 = (-qdc+qab);
      m.$matrix.m22 = (1.0-qaa-qcc);
      m.$matrix.m23 = (qda+qbc);
      m.$matrix.m24 = 0.0;
      m.$matrix.m31 = (qdb+qac);
      m.$matrix.m32 = (-qda+qbc);
      m.$matrix.m33 = (1.0-qaa-qbb);
      m.$matrix.m34 = 0.0;
      m.$matrix.m41 = m.$matrix.m42 = m.$matrix.m43 = 0.0;
      m.$matrix.m44 = 1.0;
      
      return m;
    }

    matrixToQuat(wmat) {
      var mat=new Matrix4(wmat);
      
      mat.$matrix.m41 = mat.$matrix.m42 = mat.$matrix.m43 = 0;
      mat.$matrix.m44 = 1.0;
      
      var r1=new Vector3([mat.$matrix.m11, mat.$matrix.m12, mat.$matrix.m13]);
      var r2=new Vector3([mat.$matrix.m21, mat.$matrix.m22, mat.$matrix.m23]);
      var r3=new Vector3([mat.$matrix.m31, mat.$matrix.m32, mat.$matrix.m33]);
      
      r1.normalize();
      r2.normalize();
      r3.normalize();
      
      mat.$matrix.m11 = r1[0];
      mat.$matrix.m12 = r1[1];
      mat.$matrix.m13 = r1[2];
      mat.$matrix.m21 = r2[0];
      mat.$matrix.m22 = r2[1];
      mat.$matrix.m23 = r2[2];
      mat.$matrix.m31 = r3[0];
      mat.$matrix.m32 = r3[1];
      mat.$matrix.m33 = r3[2];
      var tr=0.25*(1.0+mat.$matrix.m11+mat.$matrix.m22+mat.$matrix.m33);
      var s=0;
      if (tr>FLT_EPSILON) {
          s = Math.sqrt(tr);
          this[0] = s;
          s = 1.0/(4.0*s);
          this[1] = ((mat.$matrix.m23-mat.$matrix.m32)*s);
          this[2] = ((mat.$matrix.m31-mat.$matrix.m13)*s);
          this[3] = ((mat.$matrix.m12-mat.$matrix.m21)*s);
      }
      else {
        if (mat.$matrix.m11>mat.$matrix.m22&&mat.$matrix.m11>mat.$matrix.m33) {
            s = 2.0*Math.sqrt(1.0+mat.$matrix.m11-mat.$matrix.m22-mat.$matrix.m33);
            this[1] = (0.25*s);
            s = 1.0/s;
            this[0] = ((mat.$matrix.m32-mat.$matrix.m23)*s);
            this[2] = ((mat.$matrix.m21+mat.$matrix.m12)*s);
            this[3] = ((mat.$matrix.m31+mat.$matrix.m13)*s);
        }
        else 
          if (mat.$matrix.m22>mat.$matrix.m33) {
            s = 2.0*Math.sqrt(1.0+mat.$matrix.m22-mat.$matrix.m11-mat.$matrix.m33);
            this[2] = (0.25*s);
            s = 1.0/s;
            this[0] = ((mat.$matrix.m31-mat.$matrix.m13)*s);
            this[1] = ((mat.$matrix.m21+mat.$matrix.m12)*s);
            this[3] = ((mat.$matrix.m32+mat.$matrix.m23)*s);
        }
        else {
          s = 2.0*Math.sqrt(1.0+mat.$matrix.m33-mat.$matrix.m11-mat.$matrix.m22);
          this[3] = (0.25*s);
          s = 1.0/s;
          this[0] = ((mat.$matrix.m21-mat.$matrix.m12)*s);
          this[1] = ((mat.$matrix.m31+mat.$matrix.m13)*s);
          this[2] = ((mat.$matrix.m32+mat.$matrix.m23)*s);
        }
      }
      this.normalize();
    }

    normalize() {
      var len=Math.sqrt(this.dot(this));
      
      if (len!=0.0) {
          this.mulScalar(1.0/len);
      }
      else {
        this[1] = 1.0;
        this[0] = this[2] = this[3] = 0.0;
      }
      return this;
    }

    axisAngleToQuat(axis, angle) {
      var nor=new Vector3(axis);
      if (nor.normalize()!=0.0) {
          var phi=angle/2.0;
          var si=Math.sin(phi);
          this[0] = Math.cos(phi);
          this[1] = nor[0]*si;
          this[2] = nor[1]*si;
          this[3] = nor[2]*si;
      }
      else {
        this.makeUnitQuat();
      }
    }

    rotationBetweenVecs(v1, v2) {
      v1 = new Vector3(v1);
      v2 = new Vector3(v2);
      v1.normalize();
      v2.normalize();
      var axis=new Vector3(v1);
      axis.cross(v2);
      var angle=v1.preNormalizedAngle(v2);
      this.axisAngleToQuat(axis, angle);
    }

    quatInterp(quat2, t) {
      var quat=new Quat();
      var cosom=this[0]*quat2[0]+this[1]*quat2[1]+this[2]*quat2[2]+this[3]*quat2[3];
      if (cosom<0.0) {
          cosom = -cosom;
          quat[0] = -this[0];
          quat[1] = -this[1];
          quat[2] = -this[2];
          quat[3] = -this[3];
      }
      else {
        quat[0] = this[0];
        quat[1] = this[1];
        quat[2] = this[2];
        quat[3] = this[3];
      }
      var omega, sinom, sc1, sc2;
      if ((1.0-cosom)>0.0001) {
          omega = Math.acos(cosom);
          sinom = Math.sin(omega);
          sc1 = Math.sin((1.0-t)*omega)/sinom;
          sc2 = Math.sin(t*omega)/sinom;
      }
      else {
        sc1 = 1.0-t;
        sc2 = t;
      }
      this[0] = sc1*quat[0]+sc2*quat2[0];
      this[1] = sc1*quat[1]+sc2*quat2[1];
      this[2] = sc1*quat[2]+sc2*quat2[2];
      this[3] = sc1*quat[3]+sc2*quat2[3];
      
      return this;
    }
  }

  _v3nd4_n1_normalizedDot4 = new Vector3();
  _v3nd4_n2_normalizedDot4 = new Vector3();
  _v3nd_n1_normalizedDot = new Vector3();
  _v3nd_n2_normalizedDot = new Vector3();

  BaseVector.inherit(Vector4, 4);
  BaseVector.inherit(Vector3, 3);
  BaseVector.inherit(Vector2, 2);

  lookat_cache_vs3 = util.cachering.fromConstructor(Vector3, 64);
  lookat_cache_vs4 = util.cachering.fromConstructor(Vector4, 64);
  
  return _vectormath;
});
