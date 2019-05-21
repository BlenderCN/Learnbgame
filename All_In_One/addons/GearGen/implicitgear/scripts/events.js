//handle to module.  never access in code; for debug console use only.
var _events = {};

define([
  "util"
], function(util) {
  "use strict";

  var exports = _events = {};
  
  var DomEventTypes = exports.DomEventTypes = {
    on_mousemove   : 'mousemove',
    on_mousedown   : 'mousedown',
    on_mouseup     : 'mouseup',
    on_touchstart  : 'touchstart',
    on_touchcancel : 'touchcanel',
    on_touchmove   : 'touchmove',
    on_touchend    : 'touchend',
    on_mousewheel  : 'mousewheel',
    on_keydown     : 'keydown',
    on_keyup       : 'keyup',
    //on_keypress    : 'keypress'
  };

  function getDom(dom, eventtype) {
    if (eventtype.startsWith("key"))
      return window;
    return dom;
  }
  
  exports.modalStack = [];
  var isModalHead = exports.isModalHead = function isModalHead(owner) {
    return exports.modalStack.length == 0 || 
           exports.modalStack[exports.modalStack.length-1] === owner;
  }
  
  var EventHandler = exports.EventHandler = class EventHandler {
    pushModal(dom, _is_root) {
      if (this.modal_pushed) {
        console.trace("Error: pushModal called twice", this, dom);
        return;
      }
      
      var this2 = this;
      this.modal_pushed = true;
      exports.modalStack.push(this);
      
      function stop_prop(func) {
        return (function(e) {
          if (!_is_root) {
            e.stopPropagation();
            e.preventDefault();
          }
          
          //XXX this isModalHead call really shouldn't be necassary.  argh!
          if (isModalHead(this))
            func.call(this, e);
        }).bind(this2);
      }
      
      for (var k in DomEventTypes) {
        var type = DomEventTypes[k];
        
        if (this[k] === undefined)
          continue;
        
        if (this["__"+k] === undefined) {
          this["__"+k] = stop_prop(this[k]);
        }
        
        getDom(dom, type).addEventListener(type, this["__"+k]);
      }
    }
    
    popModal(dom) {
      var ok = exports.modalStack[exports.modalStack.length-1] === this;
      ok = ok && this.modal_pushed;
      
      if (!ok) {
        console.trace("Error: popModal called but pushModal wasn't", this, dom);
        return;
      }
      
      exports.modalStack.pop();
      
      for (var k in DomEventTypes) {
        if (this[k] === undefined)
          continue;

        var type = DomEventTypes[k];
        
        getDom(dom, type).removeEventListener(type, this["__"+k]);
      }
      
      this.modal_pushed = false;
    }
  }
  
  return exports;
});
