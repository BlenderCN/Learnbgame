//make an optimized vector library

var basic_funcs = {
  zero: [[], "0.0;"],
  negate: [[], "-this[X];"],
  combine: [["b", "u", "v"], "this[X]*u + this[X]*v;"],
  interp: [["b", "t"], "this[X] + (b[X] - this[X])*t;"],
  add: [["b"], "this[X] + b[X];"],
  addFac: [["b", "F"], "this[X] + b[X]*F;"],
  fract: [[], "Math.fract(this[X]);"],
  sub: [["b"], "this[X] - b[X];"],
  mul: [["b"], "this[X] * b[X];"],
  div: [["b"], "this[X] / b[X];"],
  mulScalar: [["b"], "this[X] * b;"],
  divScalar: [["b"], "this[X] / b;"],
  addScalar: [["b"], "this[X] + b;"],
  subScalar: [["b"], "this[X] - b;"],
  ceil: [[], "Math.ceil(this[X])"],
  floor: [[], "Math.floor(this[X])"],
  abs: [[], "Math.abs(this[X])"],
  min: [[], "Math.min(this[X])"],
  max: [[], "Math.max(this[X])"],
  clamp: [["MIN", "MAX"], "min(max(this[X], MAX), MIN)"],
};

function make_norm_safe_dot(cls) {
  var _dot = cls.prototype.dot;

  cls.prototype._dot = _dot;
  cls.prototype.dot = function (b) {
    var ret = _dot.call(this, b);

    if (ret >= 1.0 - DOT_NORM_SNAP_LIMIT && ret <= 1.0 + DOT_NORM_SNAP_LIMIT)
      return 1.0;
    if (ret >= -1.0 - DOT_NORM_SNAP_LIMIT && ret <= -1.0 + DOT_NORM_SNAP_LIMIT)
      return -1.0;

    return ret;
  }
}

function genClass(name, size) {
  var code = "var " + name + " = exports." + name + " = class " + name + " extends Array {\n"
  code += "  constructor(b) {\n    super(" + size + ");\n"
  code += "    this.length = " + size + ";\n\n";
  code += "    if (b !== undefined) this.load(b);\n";
  code += "    else this.zero();\n";
  code += "  }\n\n";
  code += "  load(b) {\n";
  code += "    if (b === undefined) return this;\n\n";

  for (var i = 0; i < size; i++) {
    code += "    this[" + i + "] = b[" + i + "];\n";
  }

  code += "\n    return this;\n"
  code += "  }\n\n";

  var f;
  var vectorDotDistance = "  vectorDotDistance(b) {\n";
  for (var i = 0; i < size; i++) {
    vectorDotDistance += "    var d" + i + " = this[" + i + "]-b[" + i + "];\n";
  }

  vectorDotDistance += "    return ("
  for (var i = 0; i < size; i++) {
    if (i > 0)
      vectorDotDistance += " + ";
    vectorDotDistance += "d" + i + "*d" + i;
  }
  vectorDotDistance += ");\n"
  vectorDotDistance += "  };\n\n";

  code += vectorDotDistance;

  var f;
  var vectorDistance = "  vectorDistance(b) {\n";
  for (var i = 0; i < size; i++) {
    vectorDistance += "    var d" + i + " = this[" + i + "]-b[" + i + "];\n";
  }

  vectorDistance += "    return sqrt("
  for (var i = 0; i < size; i++) {
    if (i > 0)
      vectorDistance += " + ";
    vectorDistance += "d" + i + "*d" + i;
  }
  vectorDistance += ");\n"
  vectorDistance += "  };\n\n";

  code += vectorDistance;

  var vectorLength = "  vectorLength() {\n";
  vectorLength += "    var dot = ";

  for (var i = 0; i < size; i++) {
    if (i > 0) {
      vectorLength += " + ";
    }
    vectorLength += "this[" + i + "]*this[" + i + "]";
  }

  vectorLength += ";\n\n";
  vectorLength += "    return dot != 0.0 ? Math.sqrt(dot) : 0.0;\n";
  vectorLength += "  }\n\n"

  code += vectorLength;

  var normalize = "  normalize() {\n";
  normalize += "    var dot = ";

  for (var i = 0; i < size; i++) {
    if (i > 0) {
      normalize += " + ";
    }
    normalize += "this[" + i + "]*this[" + i + "]";
  }

  normalize += ";\n\n";
  normalize += "    if (dot <= 0.000001) return this;\n";
  normalize += "    this.mulScalar(1.0/Math.sqrt(dot));\n\n";
  normalize += "    return this;\n";
  normalize += "  }\n\n"

  code += normalize;

  var dot_tmpl = "";
  for (var i=0; i<size; i++) {
    if (i > 0) {
      dot_tmpl += " + ";
    }

    dot_tmpl += "VAR1[" + i + "]*VAR2[" + i + "]";
  }

  code += [
"  normalizedDot(b) {",
"    var l1 = " + dot_tmpl.replace(/VAR1/g, "this").replace(/VAR2/g, "this"),
"    var l2 = " + dot_tmpl.replace(/VAR1/g, "b").replace(/VAR2/g, "b"),
"    ",
"    l1 = l1 != 0.0 ? Math.sqrt(l1) : 0.0;",
"    l2 = l2 != 0.0 ? Math.sqrt(l2) : 0.0;",
"    l1 = l1 == 0.0 ? 1.0 : 1.0 / l1;",
"    l2 = l2 == 0.0 ? 1.0 : 1.0 / l2;",
"    ",
"    return (" + dot_tmpl.replace(/VAR1/g, "this").replace(/VAR2/g, "b") + ")*l1*l2;",
"  }\n\n"
  ].join("\n");

  var dot = "  dot(b) {\n"
  dot += "    return ";
  for (var i = 0; i < size; i++) {
    if (i > 0) {
      dot += " + ";
    }
    dot += "this[" + i + "]*b[" + i + "]";
  }
  dot += ";\n  }\n\n";
  code += dot;

  for (var k in basic_funcs) {
    var func = basic_funcs[k];
    var args = func[0];
    var line = func[1];
    var f;

    var fcode = "  " + k + "("
    for (var i = 0; i < args.length; i++) {
      if (i > 0)
        fcode += ", ";

      line = line.replace(args[i], args[i].toLowerCase());
      fcode += args[i].toLowerCase();
    }
    fcode += ") {\n";

    for (var i = 0; i < size; i++) {
      var line2 = line.replace(/X/g, "" + i);
      fcode += "    this[" + i + "] = " + line2 + "\n";
    }

    fcode += "    return this;\n"
    fcode += "  }\n\n";

    code += fcode;
  }

  code += "  rot2d(th) {\n";
  code += [
"    var x = this[0];",
"    var y = this[1];",
"",
"    if (axis == 1) {",
"      this[0] = x * cos(A) + y*sin(A);",
"      this[1] = y * cos(A) - x*sin(A);",
"    } else {",
"      this[0] = x * cos(A) - y*sin(A);",
"      this[1] = y * cos(A) + x*sin(A);",
"    }",
"  ",
"    return this;",
"  }"
  ].join("\n") + "\n";

  var lines = code.split("\n");
  var code2 = ""
  for (var line of lines) {
    code2 += "  " + line + "\n";
  }


  return code2;
}

var out = "//WARNING: AUTO-GENERATED FILE! DO NOT EDIT!\n"
out += "var _vectormath = undefined; //for debugging purposes only\n\n";
out += "define(['util', 'matrixmath'], function(util, matrixmath) {\n"
out += "  'use strict';\n";

out += "\n  var exports = _vectormath = {};\n\n";
out += "  //forward matrix exports\n";
out += "  for (var k in matrixmath) exports[k] = matrixmath[k];\n\n";

out += "  var sqrt=Math.sqrt, PI=Math.PI, sin=Math.sin, cos=Math.cos, asin=Math.asin, acos=Math.acos, atan = Math.atan,  atan2=Math.atan2;\n";
out += "  var floor=Math.floor, ceil=Math.ceil, min=Math.min, max=Math.max, fract = function(f) { return f - Math.floor(f);};\n\n";

out += genClass("Vector2", 2) + "  }\n";
out += genClass("Vector3", 3) + "  }\n\n";
out += genClass("Vector4", 4) + "  }\n\n";

out += "  //add matrix methods to vectors\n";
out += "  matrixmath.initVector(Vector2, 2);\n"
out += "  matrixmath.initVector(Vector3, 3);\n"
out += "  matrixmath.initVector(Vector4, 4);\n\n"

out += "  return exports;\n});\n";
console.log(out);

var fs = require('fs');
fs.writeFileSync("scripts/vectormath.js", out);
