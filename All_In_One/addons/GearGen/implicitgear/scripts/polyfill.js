if (window.Symbol == undefined) { //eek!
  window.Symbol = {
    iterator : "$__iterator__$",
    keystr   : "$__keystr__$"
  }
} else {
  Symbol.keystr = Symbol("keystr");
}

window.list = function list(iter) {
  var ret = [];
  
  if (typeof iter == "string") {
    iter = new String();
  }
  
  if (Symbol.iterator in iter) {
    for (var item of iter) {
      ret.push(item);
    }
  } else {
    iter.forEach(function(item) {
      ret.push(item);
    }, this);
  }
  
  return ret;
}

function ArrayIter(array) {
  this.array = array;
  this.i = 0;
  this.ret = {done : false, value : undefined};
}

ArrayIter.prototype[Symbol.iterator] = function() {
  return this;
}

ArrayIter.prototype.next = function() {
  var ret = this.ret;
  
  if (this.i >= this.array.length) {
    ret.done = true;
    ret.value = undefined;
    return ret;
  }
  
  ret.value = this.array[this.i++];
  return ret;
}

/*Override array iterator to not allocate too much*/
Array.prototype[Symbol.iterator] = function() {
  return new ArrayIter(this);
}

if (Math.fract == undefined) {
  Math.fract = function fract(f) {
    var sn = (f>=0)*2.0-1.0;
    f = f*sn - Math.floor(f*sn);
    
    sn = sn<0.0;
    
    return f*(1-sn) + (1.0-f)*sn;
  };
}

if (Math.tent == undefined) {
  Math.tent = function tent(f) {
    return 1.0 - Math.abs(Math.fract(f)-0.5)*2.0;
  };
}

if (Math.sign == undefined) {
  Math.sign = function sign(f) {
    return (f>0.0)*2.0-1.0;
  };
}

if (Array.prototype.pop_i == undefined) {
  Array.prototype.pop_i = function(idx) {
    if (idx < 0 || idx >= this.length) {
      throw new Error("Index out of range");
    }
    
    while (idx < this.length) {
      this[idx] = this[idx+1];
      idx++;
    }
    
    this.length -= 1;
  }
}

if (Array.prototype.remove == undefined) {
  Array.prototype.remove = function(item, suppress_error) {
    var i = this.indexOf(item);
    
    if (i < 0) {
      if (suppress_error)
        console.trace("Warning: item not in array", item);
      else
        throw new Error("Error: item not in array " + item);
      
      return;
    }
    
    this.pop_i(i);
  }
}

if (String.prototype.contains == undefined) {
  String.prototype.contains = function(substr) {
    return String.search(substr) != null;
  }
}

String.prototype[Symbol.keystr] = function() {
  return this;
}

Number.prototype[Symbol.keystr] = Boolean.prototype[Symbol.keystr] = function() {
  return ""+this;
}

