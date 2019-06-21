//
//  Created by Luis Cuenca on 1/31/18
//  Copyright 2018 High Fidelity, Inc.
//
//
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html
//

/* jslint bitwise: true */

/* global Script
*/

(function(){
    var Vector3 = new (function() {
        var self = this;
        this.EPSILON = 0.000001;
        this.EPSILON_SQUARED = self.EPSILON * self.EPSILON;
        this.PI = 3.14159265358979;
        this.ALMOST_ONE= 1.0 - self.EPSILON;
        this.PI_OVER_TWO = 1.57079632679490;
        
        this.cross = function(A, B) {
            return {x: (A.y * B.z - A.z * B.y), y: (A.z * B.x - A.x * B.z), z: (A.x * B.y - A.y * B.x)};
        };
        this.distance = function(A, B) {
            return Math.sqrt((A.x - B.x) * (A.x - B.x) + (A.y - B.y) * (A.y - B.y) + (A.z - B.z) * (A.z - B.z));
        };
        this.dot = function(A, B) {
            return A.x * B.x + A.y * B.y + A.z * B.z;
        };
        this.length = function(V) {
            return Math.sqrt(V.x * V.x + V.y * V.y + V.z * V.z);
        };
        this.subtract = function(A, B) {
            return {x: (A.x - B.x), y: (A.y - B.y), z: (A.z - B.z)};
        };
        this.sum = function(A, B) {
            return {x: (A.x + B.x), y: (A.y + B.y), z: (A.z + B.z)};
        };
        this.multiply = function(V, scale) {
            return {x: scale * V.x, y: scale * V.y, z: scale * V.z};
        };
        this.normalize = function(V) {
            var L2 = V.x*V.x + V.y*V.y + V.z*V.z;
            if (L2 < self.EPSILON_SQUARED) {
                return {x: V.x, y: V.y, z: V.z};
            }
            var invL = 1.0/Math.sqrt(L2);
            return {x: invL * V.x, y: invL * V.y, z: invL * V.z}; 
        };
        this.multiplyQbyV = function(Q,V) {
            var num = Q.x * 2.0;
            var num2 = Q.y * 2.0;
            var num3 = Q.z * 2.0;
            var num4 = Q.x * num;
            var num5 = Q.y * num2;
            var num6 = Q.z * num3;
            var num7 = Q.x * num2;
            var num8 = Q.x * num3;
            var num9 = Q.y * num3;
            var num10 = Q.w * num;
            var num11 = Q.w * num2;
            var num12 = Q.w * num3;
            var result = {x: 0, y: 0, z: 0};
            result.x = (1.0 - (num5 + num6)) * V.x + (num7 - num12) * V.y + (num8 + num11) * V.z;
            result.y = (num7 + num12) * V.x + (1.0 - (num4 + num6)) * V.y + (num9 - num10) * V.z;
            result.z = (num8 - num11) * V.x + (num9 + num10) * V.y + (1.0 - (num4 + num5)) * V.z;
            return result;
        };  
    })();

    var Quaternion = new (function() {
        var self = this;
        
        this.IDENTITY = function() {
            return {x:0, y:0, z:0, w:1};
        };
        
        this.multiply = function(Q, R) {
            // from this page:
            // http://mathworld.wolfram.com/Quaternion.html
            return {
                w: Q.w * R.w - Q.x * R.x - Q.y * R.y - Q.z * R.z,
                x: Q.w * R.x + Q.x * R.w + Q.y * R.z - Q.z * R.y,
                y: Q.w * R.y - Q.x * R.z + Q.y * R.w + Q.z * R.x,
                z: Q.w * R.z + Q.x * R.y - Q.y * R.x + Q.z * R.w};
        };

        this.angleAxis = function(angle, axis) {
            var s = Math.sin(0.5 * angle);
            return {w: Math.cos(0.5 * angle),x: s * axis.x, y: s * axis.y, z: s * axis.z};
        };
        
        this.inverse = function(Q) {
            return {w: -Q.w, x: Q.x, y: Q.y, z: Q.z};
        };
        
        this.rotationBetween = function(orig, dest) {
            var v1 = Vector3.normalize(orig);
            var v2 = Vector3.normalize(dest);
            var cosTheta = Vector3.dot(v1, v2);
            var rotationAxis;
            if(cosTheta >= 1 - Vector3.EPSILON){
                return self.IDENTITY();
            }

            if(cosTheta < -1 + Vector3.EPSILON)
            {
                // special case when vectors in opposite directions :
                // there is no "ideal" rotation axis
                // So guess one; any will do as long as it's perpendicular to start
                // This implementation favors a rotation around the Up axis (Y),
                // since it's often what you want to do.
                rotationAxis = Vector3.cross({x: 0, y: 0, z: 1}, v1);
                if(Vector3.length(rotationAxis) < Vector3.EPSILON) { // bad luck, they were parallel, try again!
                    rotationAxis = Vector3.cross({x:1, y:0, z:0}, v1);
                }
                rotationAxis = Vector3.normalize(rotationAxis);
                return self.angleAxis(Vector3.PI, rotationAxis);
            }
            // Implementation from Stan Melax's Game Programming Gems 1 article
            rotationAxis = Vector3.cross(v1, v2);

            var s = Math.sqrt((1 + cosTheta) * 2);
            var invs = 1 / s;

            return {
                w: s * 0.5,
                x: rotationAxis.x * invs, 
                y: rotationAxis.y * invs,
                z: rotationAxis.z * invs,
            }
        }
    })();
    Script.registerValue("VEC3", Vector3);
    Script.registerValue("QUAT", Quaternion);
})();