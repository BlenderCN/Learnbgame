define([
  "util"
], function(util) {
  "use strict";

  //handle to module.  never access in code; for debug console use only.
  var _linear_algebra = undefined;

  if (window.define == undefined) { //node.js!
    window.define = function(depends, func) {
      for (var i=0; i<depends.length; i++) {
        var mod = require('./'+depends[i]);
        
        depends[i] = mod[i];
      }
      
      func.apply(self, depends);
    }
  }

  define([], function() {
    "use strict";
    
    var exports = self.exports != undefined ? self.exports : {};
    _linear_algebra = exports;
    
    var temp_mats = exports.temp_mats = [];
    var cachering = function(func, size) {
      Array.call(this);
      
      this.cur = 0;
      
      for (var i=0; i<size; i++) {
        this.push(func());
      }
    }
    cachering.prototype = Object.create(Array.prototype);
    cachering.prototype.next = function() {
      var ret = this[this.cur];
      this.cur = (this.cur+1) % this.length;
      
      return ret;
    }

    var _get_temp_matrix = exports._get_temp_matrix = function(m, n) {
      if (n*m > 64) {
        return new Matrix(m, n);
      }
      
      var key = n + m*512;
      
      if (!(key in temp_mats)) {
        temp_mats[key] = new cachering(function() {
          return new Matrix(m, n);
        }, 8);
      }
      
      return temp_mats[key].next();
    }
    
    function merge(a, b) {
      for (var k in a) {
        if (!(k in b)) {
          b[k] = a[k];
        }        
      }
      
      return b;
    }
    
    function Matrix(m, n) {
      //console.log(Symbol.init)
      Array.call(this, n == undefined ? m*m : m*n);
      
      var length = n == undefined ? m*m : m*n;
      
      this.m = m;
      this.n = n;
      
      this.length = length;
      this.makeIdentity();
    }
    
    Matrix.prototype = merge(Object.create(Array.prototype), {
      load : function(data) {
        if (data == undefined) { //this is allowed
          console.log("eck?");
          return this; 
        }
        
        if ((data instanceof Matrix) || typeof data[0] == "number") {
          for (var i=0; i<this.m*this.n; i++) {
            this[i] = data[i];
          }
        } else if (data[0] instanceof Array) {
          var m = this.m, n = this.n;
          
          for (var i=0; i<m; i++) {
            for (var j=0; j<n; j++) {
              this[m*j+i] = data[i][j];
            }
          }
        } else {
          console.trace("Warning, could not load matrix", this, data);
          throw new Error("Invalid data for matrix");
        }
        
        return this;
      },
      
      makeIdentity : function() {
        var m = this.m, n = this.n;
        
        for (var i=0; i<this.length; i++) {
          this[i] = 0.0;
        }
        
        for (var i=0; i<n; i++) {
          this[i*m+i] = 1.0;
        }
        
        return this;
      },
      
      toString : function(dec) {
        var m = this.m, n = this.n;
        
        if (dec == undefined)
          dec = 3.0;
        var col = dec + 1;
        
        if (n == 1.0) {
          var ret = "["
          for (var i=0; i<this.length; i++) {
            if (i > 0) 
              ret += ", ";
            
            if (this[i] == undefined)
              ret += "undefined";
            else
              ret += this[i].toFixed(dec);
          }
          ret += "]";
          
          return ret;
        } else {
          var ret = ""
          
          for (var j=0; j<m; j++) {
            for (var i=0; i<n; i++) {
              //display as rows
              var cell = this[j*m+i];
              
              if (i > 0)
                ret += ",";
              if (cell >= 0)
                ret += " ";
              
              var num = cell.toFixed(dec);
              if (cell == 0.0) {
                num = "   "
              }
              
              ret += num;
            }
            ret += "\n";
          }
          
          ret += "\n";
        }
        
        return ret;
      },
      
      determinant : function() {
        var m = this.m, n = this.n, ret=1;
        if(m != n) { throw new Error('numeric: det() only works on square matrices'); }
        
        var x = this;
        var A = _get_temp_matrix(m, n).load(this);
        var abs = Math.abs;
        
        function swaprow(M, i1, i2) {
          for (var j=0; j<m; j++) {
            var t = M[i1*m + j];
            
            M[i1*m + j] = M[i2*m + j];
            M[i2*m + j] = t;
          }
        }
        
        var i,j,k,Aj,Ai,alpha,temp,k1,k2,k3;
        
        for(j=0;j<n-1;j++) {
            k=j;
            
            for(i=j+1;i<n;i++) { if(abs(A[i*m+j]) > abs(A[k*m+j])) { k = i; } }
            
            if(k !== j) {
                swaprow(A, k, j);
                ret *= -1;
            }
            
            Aj = A[j];
            for(i=j+1;i<n;i++) {
                Ai = A[i];
                
                alpha = A[i*m+j]/(0.00000000000000001+A[j*m+j]);
                for(k=j+1;k<n-1;k+=2) {
                    k1 = k+1;
                    A[i*m+k] -= A[j*m+k]*alpha;
                    A[i*m+k1] -= A[j*m+k1]*alpha;
                }
                if(k!==n) { A[i*m+k] -= A[j*m+k]*alpha; }
            }
            if(A[j*m+j] === 0) { return 0; }
            ret *= A[j*m+j];
        }
        return ret*A[j*m+j];
      },
      
      multiply : function(B) {
        var m = this.m, n = this.n;
        var bm = B.m, bn = B.n;
        
        var A = _get_temp_matrix(m, n).load(this);
        for (var i=0; i<m*n; i++) {
          A[i] = this[i];
        }
        
        for (var i=0; i<m; i++) {      
          for (var j=0; j<n; j++) {
            var sum = 0.0;
            
            for (var k=0; k<m; k++) {
              sum += A[i*m+k]*B[k*m+j];
            }
            
            this[i*m+j] = sum;
          }
        }
        
        return this;
      },
      
      transpose : function() {
        var m = this.m, n = this.n;
        var A = _get_temp_matrix(m, n).load(this);
        
        for (var i=0; i<m; i++) {
          for (var j=0; j<n; j++) {
            this[i*m+j] = A[j*m+i];
          }
        }
        
        return this;
      },
      
      invert : function() {
        //this.transpose();
        
        var m = this.m, n = this.n;
        var abs = Math.abs;
        
        var A = _get_temp_matrix(m, n).load(this);
        var I = _get_temp_matrix(m, n).makeIdentity();
        
        //var A = Ai, Aj;
        //var I = Ii, Ij;
        var i, j, k, x;
        
        function swaprow(M, j1, j2) {
          for (var i=0; i<m; i++) {
            var t = M[j1*m + i];
            
            M[j1*m + i] = M[j2*m + i];
            M[j2*m + i] = t;
          }
        }
        /*
        for (var j=0; j<n; j++) {
          var row=-1, mind=-1;
          
          for (var i=j; i<m; i++) {
            var d = abs(A[i*m+j]);
            
            if (d > mind) {
              mind = d;
              row = i;
            }
          }
          
          if (row == -1) continue;
          
          console.log(row, j);
          
          swaprow(A, row, j);
          swaprow(I, row, j);
          
          var x = 1.0/A[j*m+j];
          if (x == undefined) continue;
          
          for (var i=0; i<m; i++) {
            A[j*m+i]       *= x;
            I[j*m+(m-i-1)] *= x;
          }
          
          var x1 = A[j*m+j];
          
          for (var i=m-1; i >= 0; i--) {
            if (j == i) continue;
            
            var x = A[i*m+j];
            if (x == 0.0) continue;
            
            x = x/x1;
            
            for (var k=0; k<m; k++) {
              A[i*m+k] -= A[j*m+k]*x;
              I[i*m+k] -= I[j*m+k]*x;
            }
          }
        }
        
        this.load(I);
        return this;
        //*/
         for (j=0;j<n;++j) {
             var i0 = -1;
             var v0 = -1;
             
             for (i=j;i!==m;++i) { 
               k = abs(A[i*m+j]); 
               if (k>v0) {
                 i0 = i; v0 = k; 
               } 
            }
            
            swaprow(A, i0, j);
            swaprow(I, i0, j);
           
            var x = A[j*m+j]+0.0000000000000000;
            
            for(k=j;k!==n;++k)    A[j*m+k] /= x; 
            for(k=n-1;k!==-1;--k) I[j*m+k] /= x;
            
            for(i=m-1;i!==-1;--i) {
                if(i!==j) {
                    x = A[i*m+j];
                    
                    for(k=j+1;k!==n;++k)  A[i*m+k] -= A[j*m+k]*x;
                    for(k=n-1;k>0;--k) { I[i*m+k] -= I[j*m+k]*x; --k; I[i*m+k] -= I[j*m+k]*x; }
                    if(k===0) I[i*m] -= I[j*m]*x;
                }
            }
        }
        
        this.load(I);
      }
    });

    function test() {
      var I = new Matrix(5, 5);
      
      function err(row, tm2) {
        var ret = 0.0;
        
        for (var i=row; i<5; i++) {
          //ret += i==row ? Math.abs(tm2[row*tm2.m+i]-1.0) : Math.abs(tm2[row*tm2.m+i]);
          ret += tm2[row*tm2.m+i]*I[i*tm2.m+row];
        }
        
        return ret;
      }
      
      
      var gs = new Array(5);
      var df = 0.00001;
      I.makeIdentity();

      for (var si=0; si<55; si++) {
        for (var i=0; i<25; i++) {
          var r1 = err(i, tm);
          var totgs = 0.0;
          
          for (var j=0; j<5; j++) {
            var orig = tm[i*5+j];
            tm[i*5+j] += df;
            
            var r2 = err(i, tm);
            gs[j] = (r2-r1)/df;
            totgs += gs[j]*gs[j];
          }
          
          if (isNaN(r1)) continue;
          if (totgs == 0) continue;
          r1 /= totgs;
          
          var fsum = 0.0;
          
          var i2 = (i-1+5)%5;
          var div = 0.0;
          
          for (var j=0; j<5; j++) {
            var g = gs[j];
            var fac = -r1*g*0.9;
            /*
            if (isNaN(fac)) continue;
            
            if (tm[i*5+j] == 0.0) 
              continue;

            var div = (tm[i2*5+j]*tm[i*5+j]);
            if (div == 0.0) {
              continue;
            }*/
            
            fsum += (tm[i*5+j]+fac)/div;
            //tm[i*5+j] += fac;
            I[i*5+j]  += fac;
          }
          
          fsum /= 5.0;
          for (var j=0; j<5; j++) {
           // tm[i*5+j] += tm[i2*5+j]*fsum;
         //   I[i*5+j]  += I[i2*5+j]*fsum;
          }
          console.log(fsum);
          //console.log(r1);
        }
      }
      //tm.load(tm2);
      //tm.invert();
      //var I = tm;
      console.log(""+I);
      console.log(""+tm);
      console.log(""+tm2);
      console.log(""+tm2.multiply(I));
    }
    
    return exports;
  });
});
