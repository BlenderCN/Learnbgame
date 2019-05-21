var _fft = undefined;
define([
  "util", "vectormath", "const", "report"
], function(util, vectormath, cconst, report) {
  'use strict';
  
  var exports = _fft = {};
  var Class = util.Class;
  
  var TWOPI = Math.PI*2.0;
  
  var FFX=0, FFY=1, FTOT=2;
  
  var calc_fxfy_ret = new util.cachering(function() {
    return [0, 0];
  }, 64);
  
  var sin_table = (function() {
    var steps = 32768;
    var table = new Float64Array(steps);
    
    var t = 0, dt = (2*Math.PI)/(steps-1);
    
    console.log("building sin table approximation. . .");
    
    for (var i=0; i<steps; i++, t += dt) {
      table[i] = Math.sin(t);
    }
    
    var TWOPI = Math.PI*2.0;
    var ONETWOPI = 1.0 / TWOPI;
    var PIOVER2 = Math.PI / 2.0;
    
    return {
      sin : function(s) {
        i = ~~(s*0.15915494309189535*32768);
        i = i & 32767;
        //i = i < 0 ? i + 32768 : i;
        
        return table[i];
      },
      
      cos : function(s) {
        s += 1.5707963267948966; //PIOVER2;
        i = ~~(s*0.15915494309189535*32768);
        i = i & 32767;
        //i = i < 0 ? i + 32768 : i;
        
        return table[i];
      },
      
      test : function() {
        for (var i=-32; i<32; i++) {
          console.log(Math.sin(i*0.2).toFixed(4), this.sin(i*0.2).toFixed(4));
        }
      }
    }
  })();
  
  
  
  var FFT = exports.FFT = Class([
    function constructor(dimen) {
      this.size = dimen;
      this.radial = undefined;
      this.fft = new Float64Array(dimen*dimen*FTOT);
      
      this.rand = new util.MersenneRandom();
      
      this.fft_pointcachefx = new util.hashtable();
      this.fft_pointcachefy = new util.hashtable();
  //    this.fft_pointcachefmin = new util.hashtable();
//      this.fft_pointcachefmax = new util.hashtable();
      
      this.fmin = 1e17, this.fmax = -1e17;
      
      this.jitter = 0; //jitter added to points;
      this.jittab = [];
      
      this.rand.seed(0);
      for (var i=0; i<128; i++) {
        this.jittab.push(this.rand.random());
      }
      
      this.totpoint = 0;
    },
    
    function remove_points(ps, i1, i2, idxoff) {
      idxoff = idxoff == undefined ? 0 : idxoff;
      var size = this.size, fft = this.fft;
      
      for (var pi=i1; pi<i2; pi++) {
        var key = ""+(pi+idxoff);
        
        var px = this.fft_pointcachefx.get(key);
        var py = this.fft_pointcachefy.get(key);
        
        for (var i=0; i<size*size; i++) {
          var ifx = i % size, ify = ~~(i / size);
          var ret = this.calc_fxfy(px, py, ifx, ify);
          
          var fx = ret[0], fy = ret[1];
          
          if (isNaN(fx) || isNaN(fy)) {
            throw new Error("nan " + fx + ", " + fy + ".");
          }
          fft[i*FTOT] -= fx;
          fft[i*FTOT+1] -= fy;
        }
      }
      
      this.totpoint -= i2 - i1;
    },
    
    //if image is undefined, it will create and return one
    //image MUST match dimensions of fft
    function raster(image) {
      var fft = this.fft, size = this.size, totpoint = this.totpoint;

      if (image == undefined) {
        image = new ImageData(this.size, this.size);
        image.data[0] = image.data[1] = image.data[2] = 0;
        image.data[3] = 255;
        
        var iview = new Int32Array(image.data.buffer);
        iview.fill(iview[0], 0, iview.length);
      }

      var idata = image.data;
      
      if (this.totpoint == 0) {
        report("Warning: no points in FFT");
        return image;
      }
      
      var min = 1e17, max = -1e17;
      var average = 0.0;
      var mi = 0;
      
      for (var i=0; i<fft.length; i += FTOT) {
        var fx = fft[i+FFX], fy = fft[i+FFY];
        
        var p = fx*fx + fy*fy;
        p /= totpoint;
        
        average += p;
        mi++;
        
        min = Math.min(p, min);
        max = Math.max(p, max)
      }
      
      average /= mi;
      
      if (min == 1e17) {
        report("FFT error!");
        return image;
      }
      
      if (isNaN(min) || isNaN(max) || isNaN(average)) {
        console.log("min, max:", min, max);
        report("NaN!");
        throw new Error("nan");
      }
      
      if (min == max) {
        report("Yeek! Perfectly flat FFT! Bad data perhaps?");
        return image;
      }
      
      for (var i=0; i<size*size; i++) {
        var x = i % size, y = ~~(i / size);
        var idx = (y*size + x)*FTOT;
        
        var fx = fft[idx+FFX], fy = fft[idx+FFY];
        
        var periodogram = fx*fx + fy*fy;
        periodogram /= totpoint;
        //periodogram = (periodogram - min) / (max - min);
        
        if (isNaN(fx) || isNaN(fy) || isNaN(periodogram)) {
          report("NaN!");
          throw new Error("nan!");
        }
        
        periodogram *= 0.5;
        
        var f = ~~(periodogram*255);
        
        idx = (y*image.width + x)*4;
        idata[idx] = idata[idx+1] = idata[idx+2] = ~~f;
        idata[idx+3] = 255;
      }
      
      return image;
    },
    
    function eval_radial(t) {
      if (this.radial == undefined) return;
      
      var ri = ~~(t*this.radial.average.length*0.99999999);
      var tot = this.radial.totals[ri];
      
      var avg = this.radial.average, totals = this.radial.totals;
      
      if (tot == 0) {
        var si = ri;
        while (si >= 0 && totals[si] == 0) {
          si--;
        }
        
        if (si < 0) return -1;
        
        
        var ei = ri;
        while (ei < totals.length && totals[ei] == 0) {
          ei++;
        }
        
        if (ei == totals.length) 
          return avg[si] / totals[si];
        
        var t = (ri - si) / (ei - si);
        
        var a = avg[si] / totals[si];
        var b = avg[ei] / totals[ei];
        
        return a + (b - a)*(1.0-t);
      }
        //return -1; //point does not exist in average
      
      return this.radial.average[ri] / tot;
    },
    
    function calc_radial() {
      var totpoint = this.totpoint;
      
      if (totpoint == 0) 
        return;
      
      var average = new Float64Array(~~(this.size/7));
      var totals = new Float64Array(average.length);
      
      average.fill(0, 0, average.length);
      totals.fill(0, 0, totals.length);
      
      var fft = this.fft, size = this.size;
      for (var si=0; si<fft.length; si += FTOT) {
        var x = si % size, y = ~~(si / size);
        
        x -= size*0.5;
        y -= size*0.5;
        
        var r = x*x + y*y;
        r = r != 0.0 ? Math.sqrt(r) : 0.0;
        
        var th = Math.atan2(y, x);
        
        r /= size;
        if (r > 1.0) {
          continue;
        }
        
        var fx = fft[si], fy = fft[si+1];
        var p = (fx*fx + fy*fy) / totpoint;
        
        var ri = ~~(r*average.length*0.99999);
        
        average[ri] += p;
        totals[ri]++;
      }
      
      this.radial = {
        average : average,
        totals  : totals
      };
    },

    function draw(g, fftx, ffty, image) {
      g.putImageData(image, fftx, ffty);
      
      var steps = 32;
      var t = 0, dt = 1.0 / (steps-1);
      
      var h = 40;
      var y = ffty+image.height + h + 2;
      
      g.strokeStyle = "black";
      g.beginPath();
      
      var first = 1;
      
      for (var i=0; i<steps; i++, t += dt) {
        var f = this.eval_radial(t);
        
        //if (f < 0) continue; //fft wants us to skip this t value
        f = 1.0 - f;
        
        var x2 = fftx + i*3;
        var y2 = y + f*h;
        //y2 = y;
        
        if (first) {
          g.moveTo(x2, y2);
          first = 0;
        } else {
          g.lineTo(x2, y2);
        }
      }
      
      g.stroke();
    },
    
    function get(x, y) {
      if (this.totpoint == 0) 
        return 0;
      
      //x, y are in unit 0...<1 range
      
      //x = Math.min(Math.max(x, 0.0), 0.9999999999);
      //y = Math.min(Math.max(y, 0.0), 0.9999999999);
      
      x = ~~(x*this.size);
      y = ~~(y*this.size);
      
      var fft = this.fft;
      var idx = (y*this.size+x)*FTOT;
      var fx = fft[idx], fy = fft[idx+1];
      
      return (fx*fx + fy*fy) / this.totpoint;
    },
    
    function calc_fxfy(x, y, ifx, ify) {
      var ret = calc_fxfy_ret.next();
      var size = this.size, fft = this.fft;
      
      //x += Math.random()/this.size;
      //y += Math.random()/this.size;
      
      var wx=ifx-size*0.5, wy=ify-size*0.5;
      var th = -TWOPI * (wx * x + wy * y);
      
      ret[0] = sin_table.cos(th);
      ret[1] = sin_table.sin(th);
      
      return ret;
    },
    
    function add_points(ps, scale, i1, i2, idxoff) {
      idxoff = idxoff == undefined ? 0 : idxoff;
      
      i1 *= PTOT;
      i2 *= PTOT;
      
      var size = this.size, fft = this.fft;
      
      var fxcache = this.fft_pointcachefx;
      var fycache = this.fft_pointcachefy;
      
      var fmincache = this.fft_pointcachefy;
      var fmaxcache = this.fft_pointcachefy;
      
      var TWOPI = Math.PI*2.0;
      this.totpoint += (i2-i1)/PTOT;
    
      var jit = this.jitter, jt = this.jittab;
      
      for (var i=i1; i<i2; i += PTOT) {
        var x = ps[i]*scale, y = ps[i+1]*scale;
        var pi = ~~(i/PTOT);
        
        //purpose of jitter to so we can handle
        //analyizing grid-aligned data, like void and cluster makes
        var j1 = (i/PTOT) % jt.length;
        var j2 = (j1 + i/PTOT) % jt.length;
        
        x += jit*(jt[j1]-0.5)/scale/size;
        y += jit*(jt[j2]-0.5)/scale/size;
        
        var key = "" + (pi+idxoff);
        fxcache.set(key, x);
        fycache.set(key, y);
        
        for (var si=0; si<size*size; si++) {
          var ifx = si % size, ify = ~~(si / size);
          var fx=0, fy=0, wx=ifx-size*0.5, wy=ify-size*0.5;
        
          //x += Math.random()/this.size;
          //y += Math.random()/this.size;
          
          var th = -TWOPI * (wx * x + wy * y);
          
          var ret = this.calc_fxfy(x, y, ifx, ify);
          fx += ret[0];
          fy += ret[1];
          
          fft[si*FTOT+FFX] += fx;
          fft[si*FTOT+FFY] += fy;
        }
      }
    }
  ]);
  
  return exports;
});
