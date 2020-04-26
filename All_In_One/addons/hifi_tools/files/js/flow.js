//
//  Created by Luis Cuenca on 1/31/18
//  Copyright 2018 High Fidelity, Inc.
//
//
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html
//

/* jslint bitwise: true */

/* global Script, Overlays, Controller, MyAvatar, QUAT, VEC3, AvatarList, Xform
*/

Script.include("/~/system/libraries/Xform.js");
Script.include(Script.resolvePath("VectorMath.js"));

(function(){
    var SHOW_AVATAR = true;
    var SHOW_DEBUG_SHAPES = false;
    var SHOW_SOLID_SHAPES = false;
    var SHOW_DUMMY_JOINTS = false;
    var USE_COLLISIONS = true;
    
    var HAPTIC_TOUCH_STRENGTH = 0.25;
    var HAPTIC_TOUCH_DURATION = 10.0;
    var HAPTIC_SLOPE = 0.18;
    
    var LEFT_HAND = 0;
    var RIGHT_HAND = 1;
    
    var HAPTIC_THRESHOLD = 40;
    
    var FLOW_JOINT_PREFIX = "flow";
    var SIM_JOINT_PREFIX = "sim";
    var JOINT_COLLISION_PREFIX = "joint_";
    var HAND_COLLISION_PREFIX = "hand_";
    var HAND_COLLISION_RADIUS = 0.03;
    var HAND_TOUCHING_DISTANCE = 2.0;
    
    var COLLISION_SHAPES_LIMIT = 16;
    
    var DUMMY_KEYWORD = "Extra";
    var DUMMY_JOINT_COUNT = 8;
    var DUMMY_JOINT_DISTANCE = 0.05;
        
    // Joint groups by keyword
    
    var FLOW_JOINT_KEYWORDS = [];
    var FLOW_JOINT_DATA = {};
    
    var DEFAULT_JOINT_SETTINGS = { "get": function() {
        return {"active": true, "stiffness": 0.0, "gravity": -0.0096 ,"damping": 0.85, "inertia": 0.8, "delta": 0.55, "radius": 0.01};
    }};
    
    var DEFAULT_COLLISION_SETTINGS = {type: "sphere", radius: 0.05, offset: {x: 0, y: 0, z: 0}};
    
    var PRESET_FLOW_DATA = {
        "hair": {"active": true, "stiffness": 0.0, "gravity": -0.0096 ,"damping": 0.85, "inertia": 0.8, "delta": 0.55, "radius": 0.01}, 
        "skirt": {"active": true, "stiffness": 0.0, "gravity": -0.0096 ,"damping": 0.85, "inertia": 0.25, "delta": 0.45, "radius": 0.01}, 
        "breasts": {"active": true, "stiffness": 1, "gravity": -0.0096 ,"damping": 0.65, "inertia": 0.8, "delta": 0.45, "radius": 0.01}
    };
    
    var PRESET_COLLISION_DATA = {
        "Head": {type: "sphere", radius: 0.08, offset: {x: 0, y: 0.06, z: 0.00}},
        "RightArm": {type: "sphere", radius: 0.05, offset: {x: 0.0, y: 0.02, z: 0.00}},
        "LeftArm": {type: "sphere", radius: 0.05, offset: {x: 0.0, y: 0.02, z: 0.00}},
        "Spine2": {type: "sphere", radius: 0.09, offset: {x: 0, y: 0.04, z: 0.00}}
    };
        
    var CUSTOM_FLOW_DATA, CUSTOM_COLLISION_DATA;
    
    // CUSTOM DATA STARTS HERE
    
    //__PYTHONFILL__CUSTOM_SETS__//

    // CUSTOM DATA ENDS HERE
    
    var HAND_COLLISION_JOINTS = ["RightHandMiddle1", "RightHandThumb3", "LeftHandMiddle1", "LeftHandThumb3","RightHandMiddle3", "LeftHandMiddle3"];
    
    if (SHOW_DUMMY_JOINTS) {
        FLOW_JOINT_KEYWORDS.push(DUMMY_KEYWORD);
        FLOW_JOINT_DATA[DUMMY_KEYWORD] = DEFAULT_JOINT_SETTINGS.get();
    }
    
    var FlowDebug = function() {
        var self = this;
        this.debugLines = {};
        this.debugSpheres = {};
        this.debugCubes = {};
        this.showDebugShapes = false;
        this.showSolidShapes = false;
        
        this.setDebugCube = function(cubeName, cubePosition, cubeRotation, cubeDimensions, shapeColor, forceRendering) {
            var doRender = self.showDebugShapes || forceRendering;
            if (!doRender) return;
            var position = cubePosition ? cubePosition : {x: 0, y: 0, z: 0};
            var rotation = cubeRotation ? cubeRotation : {x: 0, y: 0, z: 0, w: 0};
            var dimensions = cubeDimensions ? cubeDimensions : {x: 1, y: 1, z: 1};
            var color = shapeColor !== undefined ? shapeColor : { red: 0, green: 255, blue: 255 };
            if (self.debugCubes[cubeName] !== undefined) {
                Overlays.editOverlay(self.debugCubes[cubeName], {
                    position: position,
                    rotation: rotation,
                    dimensions: dimensions,
                    color: color,
                    solid: self.showSolidShapes,
                    visible: true
                });
            } else {
                self.debugCubes[cubeName] = Overlays.addOverlay("cube", {
                    position: position,
                    rotation: rotation,
                    dimensions: dimensions,
                    color: color,
                    solid: self.showSolidShapes,
                    visible: true
                });
            }
        };
        
        this.setDebugLine = function(lineName, startPosition, endPosition, shapeColor, forceRendering) {
            var doRender = self.showDebugShapes || forceRendering;
            if (!doRender) return;
            var start = startPosition ? startPosition : {x: 0, y: 0, z: 0};
            var end = endPosition ? endPosition : {x: 0, y: 1, z: 0};
            var color = shapeColor ? shapeColor : { red: 0, green: 255, blue: 255 };
            if (self.debugLines[lineName] !== undefined) {
                Overlays.editOverlay(self.debugLines[lineName], {
                    color: color,
                    start: start,
                    end: end,
                    visible: true
                });
            } else {
                self.debugLines[lineName] = Overlays.addOverlay("line3d", {
                    color: color,
                    start: start,
                    end: end,
                    visible: true
                });
            }
        };
        
        this.setDebugSphere = function(sphereName, pos, diameter, shapeColor, forceRendering) {
            var doRender = self.showDebugShapes || forceRendering;
            if (!doRender) return;
            var scale = diameter ? diameter : 0.01;
            var color = shapeColor ? shapeColor : { red: 255, green: 0, blue: 255 };
            if (self.debugSpheres[sphereName] !== undefined) {
                Overlays.editOverlay(self.debugSpheres[sphereName], {
                    color: color,
                    position: pos,
                    scale: {x:scale, y:scale, z:scale},
                    solid: self.showSolidShapes,
                    visible: true
                });
            } else {
                self.debugSpheres[sphereName] = Overlays.addOverlay("sphere", {
                    color: color,
                    position: pos,
                    scale: {x:scale, y:scale, z:scale},
                    solid: self.showSolidShapes,
                    visible: true
                });
            }
        };
        
        this.deleteSphere = function(name) {
            Overlays.deleteOverlay(self.debugSpheres[name]);
            self.debugSpheres[name] = undefined;
        };
        
        this.deleteLine = function(name) {
            Overlays.deleteOverlay(self.debugLines[name]);
            self.debugLines[name] = undefined;
        };
        
        this.deleteCube = function(name) {
            Overlays.deleteOverlay(self.debugCubes[name]);
            self.debugCubes[name] = undefined;
        };
        
        this.cleanup = function() {
            for (var lineName in self.debugLines) {
                if (lineName !== undefined) {
                        self.deleteLine(lineName);
                }
            }
            for (var sphereName in self.debugSpheres) {
                if (sphereName !== undefined) {
                        self.deleteSphere(sphereName);
                }
            }
            for (var cubeName in self.debugCubes) {
                    if (cubeName!== undefined) {
                        self.deleteCube(cubeName);
                }
            }
            self.debugLines = {};
            self.debugSpheres = {};
            self.debugCubes = {};
        };
        
        this.setVisible = function(isVisible) {
            self.showDebugShapes = isVisible;
            for (var lineName in self.debugLines) {
                if (lineName !== undefined) {
                    Overlays.editOverlay(self.debugLines[lineName], {
                        visible: isVisible
                    });
                }
            }
            for (var sphereName in self.debugSpheres) {
                if (sphereName !== undefined) {
                    Overlays.editOverlay(self.debugSpheres[sphereName], {
                        visible: isVisible
                    });
                }
            }
        };
        
        this.setSolid = function(isSolid) {
            self.showSolidShapes = isSolid;
            for (var lineName in self.debugLines) {
                if (lineName !== undefined) {
                    Overlays.editOverlay(self.debugLines[lineName], {
                        solid: isSolid
                    });
                }
            }
            for (var sphereName in self.debugSpheres) {
                if (sphereName !== undefined) {
                    Overlays.editOverlay(self.debugSpheres[sphereName], {
                        solid: isSolid
                    });
                }
            }
        };       

    };


    var FlowHandSystem = function() {
        var self = this;
        this.avatarIds = [];
        this.avatarHands = [];
        this.lastAvatarCount = 0;
        this.leftTriggerValue = 0;
        this.rightTriggerValue = 0;
        this.isLeftHandTouching = false;
        this.leftHandTouchDelta = 0;
        this.leftHandTouchThreshold = 0;
        this.isRightHandTouching = false;
        this.rightHandTouchDelta = 0;
        this.rightHandTouchThreshold = 0;
        
        this.getNearbyAvatars = function(distance) {
            return AvatarList.getAvatarIdentifiers().filter(function(avatarID){
                if (!avatarID) {
                    return false;
                }
                var avatar = AvatarList.getAvatar(avatarID);
                var avatarPosition = avatar && avatar.position;
                if (!avatarPosition) {
                    return false;
                }
                return VEC3.distance(avatarPosition, MyAvatar.position) < distance;
            });
        };
        
        this.setScale = function(scale) {
            for (var j = 0; j < self.avatarHands.length; j++) {
                for (var i = 0; i < HAND_COLLISION_JOINTS.length; i++) {
                    var side = HAND_COLLISION_JOINTS[i];
                    self.avatarHands[j][side].radius = self.avatarHands[j][side].initialRadius * scale;
                }
            }
        };
        
        this.update = function() {
            var nearbyAvatars = self.getNearbyAvatars(HAND_TOUCHING_DISTANCE);
            nearbyAvatars.push(MyAvatar.SELF_ID);
            
            nearbyAvatars.forEach(function(avatarID) {

                var avatar = AvatarList.getAvatar(avatarID);
                var avatarIndex = self.avatarIds.indexOf(avatarID);
                var i, side;
                if (avatarIndex === -1) {
                    var newHands = {};
                    for (i = 0; i < HAND_COLLISION_JOINTS.length; i++) {
                        side = HAND_COLLISION_JOINTS[i];
                        var jointId = avatar.getJointIndex(side);
                        var name =  avatarID + "_" + HAND_COLLISION_PREFIX + side;
                        var handCollisionSettings = {type: "sphere", radius: HAND_COLLISION_RADIUS, offset: {x: 0, y: 0, z: 0}, avatarId: avatarID};
                        newHands[side] = new FlowCollisionSphere(name, jointId, side, handCollisionSettings);
                    }
                    self.avatarHands.push(newHands);
                    avatarIndex = self.avatarIds.length;
                    self.avatarIds.push(avatarID);
                }

                for (i = 0; i < HAND_COLLISION_JOINTS.length; i++) {
                    side = HAND_COLLISION_JOINTS[i];
                    self.avatarHands[avatarIndex][side].update();
                }
            });
            
            if (nearbyAvatars.length < self.lastAvatarCount) {
                var avatarsToUntrack = [];
                for (var i = 0; i < self.avatarIds.length; i++) {
                    var index = nearbyAvatars.indexOf(self.avatarIds[i]);
                    if (index == -1) {
                        avatarsToUntrack.push(i);
                    }
                }
                avatarsToUntrack.sort();
                for (i = 0; i < avatarsToUntrack.length; i++) {
                    self.avatarIds.splice(avatarsToUntrack[i]-i, 1);
                    self.avatarHands.splice(avatarsToUntrack[i]-i, 1);
                }
            }
            self.lastAvatarCount = nearbyAvatars.length;
        };
        
        this.computeCollision = function(collisions) {
            var collisionData = new FlowCollisionData();
            if (collisions.length > 1) {
                for (var i = 0; i < collisions.length; i++) {
                    collisionData.offset += collisions[i].offset;
                    collisionData.normal = VEC3.sum(collisionData.normal, VEC3.multiply(collisions[i].normal, collisions[i].distance));
                    collisionData.position = VEC3.sum(collisionData.position, collisions[i].position);
                    collisionData.radius += collisions[i].radius; 
                    collisionData.distance += collisions[i].distance; 
                }
                collisionData.offset = collisionData.offset/collisions.length;
                collisionData.radius = VEC3.length(collisionData.normal)/2;
                collisionData.normal = VEC3.normalize(collisionData.normal);
                collisionData.position = VEC3.multiply(collisionData.position, 1/collisions.length);
                collisionData.distance = collisionData.distance/collisions.length;
            } else if (collisions.length == 1){
                collisionData = collisions[0];
            }
            collisionData.collisionCount = collisions.length;
            return collisionData;
        };
        
        this.manageHapticPulse = function() {
            if (self.isLeftHandTouching) {
                self.leftHandTouchDelta += HAPTIC_SLOPE;
                self.leftHandTouchThreshold = 0;
                Controller.triggerHapticPulse(HAPTIC_TOUCH_STRENGTH/self.leftHandTouchDelta, HAPTIC_TOUCH_DURATION, LEFT_HAND);
            } else {
                if (self.leftHandTouchThreshold++ > HAPTIC_THRESHOLD) {
                    self.leftHandTouchDelta = 0;
                }               
            }
            if (self.isRightHandTouching) {
                self.rightHandTouchDelta += HAPTIC_SLOPE;
                self.rightHandTouchThreshold = 0;
                Controller.triggerHapticPulse(HAPTIC_TOUCH_STRENGTH/self.rightHandTouchDelta, HAPTIC_TOUCH_DURATION, RIGHT_HAND);
            } else {
                if (self.rightHandTouchThreshold++ > HAPTIC_THRESHOLD) {
                    self.rightHandTouchDelta = 0;
                }
            }
        };
        
        this.checkThreadCollisions = function(thread) {

            var threadCollisionData = Array(thread.joints.length);
            for (var i = 0; i < threadCollisionData.length; i++) {
                threadCollisionData[i] = [];
            }
            self.isRightHandTouching = false;
            self.isLeftHandTouching = false;
            for (i = 0; i < self.avatarHands.length; i++) {
                for (var j = 0; j < HAND_COLLISION_JOINTS.length; j++) {
                    var side = HAND_COLLISION_JOINTS[j];
                    var rootCollision = self.avatarHands[i][side].checkCollision(thread.positions[0], thread.radius);
                    var collisionData = [rootCollision];
                    var tooFar = rootCollision.distance > (thread.length + rootCollision.radius);
                    if (!tooFar) {
                        for (var k = 1; k < thread.joints.length; k++) {
                            var prevCollision = collisionData[k-1];
                            var nextCollision = self.avatarHands[i][side].checkCollision(thread.positions[k], thread.radius);
                            collisionData.push(nextCollision);
                            var isTouching = false;
                            if (prevCollision.offset > 0) {
                                if (k == 1) {
                                    threadCollisionData[k-1].push(prevCollision);
                                    isTouching = true;
                                }
                            } else if (nextCollision.offset > 0) {
                                threadCollisionData[k].push(nextCollision);
                                isTouching = true;
                            } else {
                                var segmentCollision = self.avatarHands[i][side].checkSegmentCollision(thread.positions[k-1], thread.positions[k], prevCollision, nextCollision);
                                if (segmentCollision.offset > 0) {
                                    threadCollisionData[k-1].push(segmentCollision);
                                    threadCollisionData[k].push(segmentCollision);
                                    isTouching = true;
                                }
                            }       
                            
                            if (isTouching) {
                                if (side.indexOf("RightHand") > -1) {
                                    self.isRightHandTouching = true;
                                } else {
                                    self.isLeftHandTouching = true;
                                }
                            } 
                        }
                    }
                }
            }
            
            self.manageHapticPulse();
            
            var collisionResult = [];
            for (i = 0; i < thread.joints.length; i++) {
                collisionResult.push(self.computeCollision(threadCollisionData[i]));
            }
            return collisionResult;
        };

        this.setRightTriggerValue = function(value) {
            self.rightTriggerValue = value;
        };
        
        this.setLeftTriggerValue = function(value) {
            self.leftTriggerValue = value;
        };
    };

    var FlowCollisionSystem = function() {
        var self = this;
        this.collisionSpheres = [];
        this.collisionCubes = [];
        
        this.addCollisionSphere = function(name, jointIndex, jointName, settings) {
            self.collisionSpheres.push(new FlowCollisionSphere(name, jointIndex, jointName, settings));
        };
        
        this.addCollisionCube = function(name, jointIndex, jointName, settings) {
            self.collisionCubes.push(new FlowCollisionCube(name, jointIndex, jointName, settings));
        };
        
        this.addCollisionShape = function(jointIndex, jointName, settings) {
            var name = JOINT_COLLISION_PREFIX + jointIndex;
            switch(settings.type) {
                case "sphere":
                    self.addCollisionSphere(name, jointIndex, jointName, settings);
                    break;
                case "cube":
                    self.addCollisionCube(name, jointIndex, jointName, settings);
                    break;
            }
        };
        
        this.addCollisionToJoint = function(jointName) {
            if (self.collisionSpheres.length >= COLLISION_SHAPES_LIMIT) {
                return false;
            }
            var jointIndex = MyAvatar.getJointIndex(jointName);
            var collisionIndex = self.findCollisionWithJoint(jointIndex);
            if (collisionIndex === -1) {
                self.addCollisionShape(jointIndex, jointName, DEFAULT_COLLISION_SETTINGS);
                return true;
            } else {
                return false;
            }
        };
        
        this.removeCollisionFromJoint = function(jointName) {
            var jointIndex = MyAvatar.getJointIndex(jointName);
            var collisionIndex = self.findCollisionWithJoint(jointIndex);
            if (collisionIndex > -1) {
                self.collisionSpheres[collisionIndex].clean();
                self.collisionSpheres.splice(collisionIndex, 1);
            }
        };
        
        this.update = function() {
            for (var i = 0; i < self.collisionCubes.length; i++) {
                self.collisionCubes[i].update();
            }
            for (i = 0; i < self.collisionSpheres.length; i++) {
                self.collisionSpheres[i].update();
            }
        };
        
        this.computeCollision = function(collisions) {
            var collisionData = new FlowCollisionData();
            if (collisions.length > 1) {
                for (var i = 0; i < collisions.length; i++) {
                    collisionData.offset += collisions[i].offset; 
                    collisionData.normal = VEC3.sum(collisionData.normal, VEC3.multiply(collisions[i].normal, collisions[i].distance));
                    collisionData.position = VEC3.sum(collisionData.position, collisions[i].position);
                    collisionData.radius += collisions[i].radius;
                    collisionData.distance += collisions[i].distance; 
                }
                collisionData.offset = collisionData.offset/collisions.length;
                collisionData.radius = VEC3.length(collisionData.normal)/2;
                collisionData.normal = VEC3.normalize(collisionData.normal);
                collisionData.position = VEC3.multiply(collisionData.position, 1/collisions.length);
                collisionData.distance = collisionData.distance/collisions.length;
            } else if (collisions.length == 1){
                collisionData = collisions[0];
            }
            collisionData.collisionCount = collisions.length;
            return collisionData;
        };
        
        this.setScale = function(scale) {
            for (var j = 0; j < self.collisionSpheres.length; j++) {
                self.collisionSpheres[j].radius = self.collisionSpheres[j].initialRadius * scale;
                self.collisionSpheres[j].offset = VEC3.multiply(self.collisionSpheres[j].initialOffset, scale);
            }
        };

        this.checkThreadCollisions = function(thread, checkSegments) {
            var threadCollisionData = Array(thread.joints.length);
            for (var i = 0; i < threadCollisionData.length; i++) {
                threadCollisionData[i] = [];
            }
            for (var j = 0; j < self.collisionSpheres.length; j++) {
                
                var rootCollision = self.collisionSpheres[j].checkCollision(thread.positions[0], thread.radius);
                var collisionData = [rootCollision];
                var tooFar = rootCollision.distance > (thread.length + rootCollision.radius);
                var nextCollision;
                if (!tooFar) {
                    if (checkSegments) {
                        for (i = 1; i < thread.joints.length; i++) {
                            var prevCollision = collisionData[i-1];
                            nextCollision = self.collisionSpheres[j].checkCollision(thread.positions[i], thread.radius);
                            collisionData.push(nextCollision);
                            if (prevCollision.offset > 0) {
                                if (i == 1) {
                                    threadCollisionData[i-1].push(prevCollision);
                                }
                            } else if (nextCollision.offset > 0) {
                                threadCollisionData[i].push(nextCollision);
                            } else {
                                var segmentCollision = self.collisionSpheres[j].checkSegmentCollision(thread.positions[i-1], thread.positions[i], prevCollision, nextCollision);
                                if (segmentCollision.offset > 0) {
                                    threadCollisionData[i-1].push(segmentCollision);
                                    threadCollisionData[i].push(segmentCollision);
                                }
                            }                       
                        }
                    } else {
                        if (rootCollision.offset > 0) {
                            threadCollisionData[0].push(rootCollision);
                        }
                        for (i = 1; i < thread.joints.length; i++) {
                            nextCollision = self.collisionSpheres[j].checkCollision(thread.positions[i], thread.radius);
                            if (nextCollision.offset > 0) {
                                threadCollisionData[i].push(nextCollision);
                            }
                        }
                    }
                }
            }

            var collisionResult = [];
            for (i = 0; i < thread.joints.length; i++) {
                collisionResult.push(self.computeCollision(threadCollisionData[i]));
            }
            return collisionResult;
        };
        
        this.findCollisionWithJoint = function (jointIndex) {
            for (var i = 0; i < self.collisionSpheres.length; i++) {
                if (self.collisionSpheres[i].jointIndex == jointIndex) {
                    return i;
                }
            }
            return -1;
        };
        
        this.modifyCollision = function(jointName, parameter, value) {
            var jointIndex = MyAvatar.getJointIndex(jointName);
            var collisionIndex = self.findCollisionWithJoint(jointIndex);
            var avatarScale = MyAvatar.scale;
            if (collisionIndex > -1) {
                switch(parameter) {
                    case "radius": {
                        self.collisionSpheres[collisionIndex].initialRadius = value;
                        self.collisionSpheres[collisionIndex].radius = avatarScale*value;
                        break;
                    }
                    case "offset": {
                        var offset = self.collisionSpheres[collisionIndex].offset;
                        self.collisionSpheres[collisionIndex].initialOffset = {x: offset.x, y: value, z: offset.z};
                        self.collisionSpheres[collisionIndex].offset = VEC3.multiply(self.collisionSpheres[collisionIndex].initialOffset, avatarScale);
                        break;
                    }
                }
            }
        };
        
        this.getCollisionData = function() {
            var collisionData = {};
            for (var i = 0; i < self.collisionSpheres.length; i++) {
                var data = {type: "sphere", radius: self.collisionSpheres[i].initialRadius, offset: self.collisionSpheres[i].initialOffset};
                collisionData[self.collisionSpheres[i].jointName] = data;
            }
            return collisionData;
        };

    };
    
    var FlowCollisionData = function(offset, position, radius, normal, distance) {
        this.collisionCount = 0;
        this.offset = offset !== undefined ? offset : 0;
        this.position = position !== undefined ? position : {x: 0, y: 0, z: 0};
        this.radius = radius !== undefined ? radius : 0;
        this.normal = normal !== undefined ? normal : {x: 0, y: 0, z: 0};
        this.distance = distance !== undefined ? distance : 0;
    };
    
    var FlowCollisionSphere = function(name, jointIndex, jointName, settings) {
        var self = this;
        this.name = name;
        this.jointIndex = jointIndex;
        this.jointName = jointName;
        this.radius = this.initialRadius = settings.radius;
        this.offset = settings.offset;
        this.initialOffset = {x: self.offset.x, y: self.offset.y, z: self.offset.z};
        this.attenuation = settings.attenuation;
        this.avatarId = settings.avatarId;
        
        this.position = {x:0, y:0, z:0};
        
        this.update = function() {
            if (self.avatarId !== undefined){
                var avatar = AvatarList.getAvatar(self.avatarId);
                self.position = avatar.getJointPosition(self.jointIndex);
            } else {
                self.position = MyAvatar.jointToWorldPoint(self.offset, self.jointIndex);
            }               
            collisionDebug.setDebugSphere(self.name, self.position, 2*self.radius, {red: 200, green: 10, blue: 50});
            if (self.attenuation && self.attenuation > 0) {
                collisionDebug.setDebugSphere(self.name + "_att", self.position, 2*(self.radius + self.attenuation), {red: 120, green: 200, blue: 50}); 
            }
        };
        
        this.checkCollision = function(point, radius) {
            var centerToJoint = VEC3.subtract(point, self.position);
            var distance = VEC3.length(centerToJoint) - radius;
            var offset =  self.radius - distance;
            var collisionData = new FlowCollisionData(offset, self.position, self.radius, VEC3.normalize(centerToJoint), distance);
            return collisionData;
        };
        
        this.checkSegmentCollision = function(point1, point2, pointCollision1, pointCollision2) {
            var collisionData = new FlowCollisionData();
            var segment = VEC3.subtract(point2, point1);
            var segmentLength = VEC3.length(segment);
            var maxDistance = Math.sqrt(Math.pow(pointCollision1.radius,2) + Math.pow(segmentLength,2));
            if (pointCollision1.distance < maxDistance && pointCollision2.distance < maxDistance) {
                var segmentPercent = pointCollision1.distance/(pointCollision1.distance + pointCollision2.distance);
                var collisionPoint = VEC3.sum(point1, VEC3.multiply(segment, segmentPercent)); 
                var centerToSegment = VEC3.subtract(collisionPoint, self.position);
                var distance = VEC3.length(centerToSegment);
                if (distance < self.radius) {
                    var offset = self.radius - distance;
                    collisionData = new FlowCollisionData(offset, self.position, self.radius, VEC3.normalize(centerToSegment), distance);
                }
            }
            return collisionData;
        };
        
        this.clean = function() {
            collisionDebug.deleteSphere(self.name);
        };
    };
    
    var FlowCollisionCube = function(name, jointIndex, settings) {
        var self = this;
        this.name = name;
        this.jointIndex = jointIndex;
        this.dimensions = settings.dimensions;
        this.offset = settings.offset;
        this.attenuation = settings.attenuation;
        this.avatarId = settings.avatarId;
        
        this.position = {x:0, y:0, z:0};
        this.rotation = {x:0, y:0, z:0, w:0};
        
        this.update = function() {
            if (self.avatarId !== undefined){
                var avatar = AvatarList.getAvatar(self.avatarId);
                self.position = avatar.getJointPosition(self.jointIndex);
                self.rotation = avatar.getJointRotation(self.jointIndex);
            }               
            collisionDebug.setDebugCube(self.name, self.position, self.rotation, self.dimensions, {red: 200, green: 10, blue: 50});
        };
        
        this.checkCollision = function(point, radius) {
            var localPoint = MyAvatar.worldToJointPoint(point, self.jointIndex);
            var localPosition = MyAvatar.worldToJointPoint(self.position, self.jointIndex);
            var centerToJoint = VEC3.subtract(localPoint, localPosition);
            var offsets = { x: (self.dimensions.x/2) - Math.abs(centerToJoint.x), 
                            y: (self.dimensions.y/2) - Math.abs(centerToJoint.y), 
                            z: (self.dimensions.z/2) - Math.abs(centerToJoint.z)};
                            
            radius = 0;
            var normal = {x: 0, y: 0, z: 0};
            var position = {x: 0, y: 0, z: 0};
            var offset = 0;
            if (offsets.x > 0 && offsets.y > 0 && offsets.z > 0) {
                var offsetOrder = [{"coordinate": "x", "value": offsets.x}, {"coordinate": "y", "value": offsets.y}, {"coordinate": "z", "value": offsets.z}]; 
                offsetOrder.sort(function(a, b){
                    return a.value - b.value;
                });
                switch (offsetOrder[0].coordinate) {
                    case "x" :
                        normal = {x: centerToJoint.x > 0 ? 1 : -1, y: 0, z: 0};
                        radius = self.dimensions.x/2;
                        position = VEC3.sum(self.offset, {x: 0, y: centerToJoint.y, z: centerToJoint.z});
                        offset = offsets.x;                     
                    break;
                    case "y" :
                        normal = {x: 0, y: centerToJoint.y > 0 ? 1 : -1, z: 0};
                        radius = self.dimensions.y/2;
                        position = VEC3.sum(self.offset, {x: centerToJoint.x, y: 0, z: centerToJoint.z});
                        offset = offsets.y; 
                    break;
                    case "z" :
                        normal = {x: 0, y: 0, z: centerToJoint.z > 0 ? 1 : -1};
                        radius = self.dimensions.z/2;
                        position = VEC3.sum(self.offset, {x: centerToJoint.x, y: centerToJoint.y, z: 0});
                        offset = offsets.z; 
                    break;
                }
                normal = MyAvatar.jointToWorldDirection(normal, self.jointIndex);
                position = MyAvatar.jointToWorldPoint(position, self.jointIndex);
            }           
            return new FlowCollisionData(offset, position, radius, normal, offset);
        };
    };
    
    var FlowNode = function(initialPosition, settings) {
        var self = this;
        
        this.active = settings.active;
        
        this.radius = this.initialRadius = settings.radius;
        this.gravity = settings.gravity;
        this.damping = settings.damping;
        this.inertia = settings.inertia;
        this.delta = settings.delta;
        
        this.initialPosition = initialPosition;
        
        this.previousPosition = this.initialPosition;
        this.currentPosition = this.initialPosition;
        
        this.previousCollision = new FlowCollisionData();
        
        this.currentVelocity = {x:0, y:0, z:0};
        this.previousVelocity = {x:0, y:0, z:0};
        this.acceleration = {x:0, y:0, z:0};

        this.anchored = false;
        this.colliding = false;
        this.collision = undefined;
        
        this.update = function(accelerationOffset) {
            self.acceleration = {x: 0, y: self.gravity, z: 0};
            self.previousVelocity = self.currentVelocity;
            self.currentVelocity = VEC3.subtract(self.currentPosition, self.previousPosition);
            self.previousPosition = self.currentPosition;
            if (!self.anchored) {   
                // Add inertia
                var centrifugeVector = VEC3.normalize(VEC3.subtract(self.previousVelocity, self.currentVelocity));
                self.acceleration = VEC3.sum(self.acceleration, VEC3.multiply(centrifugeVector, self.inertia * VEC3.length(self.currentVelocity)));
                
                // Add offset
                self.acceleration = VEC3.sum(self.acceleration, accelerationOffset);
                
                // Calculate new position
                self.currentPosition = VEC3.sum(
                    VEC3.sum(self.currentPosition, VEC3.multiply(self.currentVelocity, self.damping)), 
                    VEC3.multiply(self.acceleration, Math.pow(self.delta, 2))
                );                
            } else {
                self.acceleration = {x:0, y:0, z:0};
                self.currentVelocity = {x:0, y:0, z:0};
            }
        };
        
        
        this.solve = function(constrainPoint, maxDistance, collision) {
            self.solveConstraints(constrainPoint, maxDistance);
            self.solveCollisions(collision);      
        };
        
        this.solveConstraints = function(constrainPoint, maxDistance) {
            var constrainVector = VEC3.subtract(self.currentPosition, constrainPoint);
            var difference = maxDistance/VEC3.length(constrainVector);
            self.currentPosition = difference < 1.0 ? VEC3.sum(constrainPoint, VEC3.multiply(constrainVector, difference)) : self.currentPosition;
        };
        
        this.solveCollisions = function(collision) {
            self.colliding = collision && (collision.offset > 0);
            self.collision = collision;
            if (self.colliding) {
                self.currentPosition = VEC3.sum(self.currentPosition, VEC3.multiply(collision.normal, collision.offset));
                self.previousCollision = collision;
            } else {
                self.previousCollision = undefined;
            } 
        };
        
        this.apply = function(name, forceRendering) {
            jointDebug.setDebugSphere(name, self.currentPosition, 2*self.radius, {  red: self.collision && self.collision.collisionCount > 1 ? 0 : 255, 
                                                                                    green:self.colliding ? 0 : 255, 
                                                                                    blue:0 }, forceRendering);
        };
    };
    

    var FlowJoint = function(index, parentIndex, name, group, settings){
        var self = this;
        
        this.index = index;
        this.name = name;
        this.group = group;
        this.parentIndex = parentIndex;
        this.childIndex = -1;
        
        this.isDummy = false;
        
        this.initialPosition = MyAvatar.getJointPosition(index);
        this.initialXform = new Xform(MyAvatar.getJointRotation(index), MyAvatar.getJointTranslation(index));
        
        this.currentRotation = undefined;
        this.recoveryPosition = undefined;
        
        this.node = new FlowNode(self.initialPosition, settings);
        
        this.stiffness = settings.stiffness;

        this.translationDirection = VEC3.normalize(this.initialXform.pos);
        
        this.length = VEC3.length(VEC3.subtract(this.initialPosition, MyAvatar.getJointPosition(self.parentIndex)));
        
        this.update = function () {
            var accelerationOffset = {x: 0, y: 0, z: 0};
            if (!self.isDummy && self.recoveryPosition) {
                var recoveryVector = VEC3.subtract(self.recoveryPosition, self.node.currentPosition);   
                accelerationOffset = VEC3.multiply(recoveryVector, Math.pow(self.stiffness, 3));
            }
            self.node.update(accelerationOffset);
            if (self.node.anchored) {
                if (!self.isDummy) {
                    self.node.currentPosition = MyAvatar.getJointPosition(self.index);
                } else {
                    self.node.currentPosition = MyAvatar.getJointPosition(self.parentIndex);
                }
            }
        };
                
        this.solve = function(collision) {
            var parentPosition = flowJointData[self.parentIndex] ? flowJointData[self.parentIndex].node.currentPosition : MyAvatar.getJointPosition(self.parentIndex);
            self.node.solve(parentPosition, self.length, collision);            
        };
        
        this.apply = function() {
            
            if (self.currentRotation) {
                MyAvatar.setJointRotation(self.index, self.currentRotation);
            }
            self.node.apply(self.name, self.isDummy);
        };
    };
    
    var FlowJointDummy = function(initialPosition, index, parentIndex, childIndex, settings) {
        var group = DUMMY_KEYWORD;
        var name = DUMMY_KEYWORD + "_" + index;
        FlowJoint.call(this, index, parentIndex, name, group, settings);
        this.isDummy = true;
        this.childIndex = childIndex;
        this.initialPosition = initialPosition;
        this.node = new FlowNode(initialPosition, settings);
        this.length = DUMMY_JOINT_DISTANCE;
    };   
    
    var FlowThread = function(root) {
        var self = this;
        this.joints = [];
        this.positions = [];
        this.radius = 0;
        this.length = 0;
        
        this.computeThread = function(rootIndex) {
            var parentIndex = rootIndex;
            var childIndex = flowJointData[parentIndex].childIndex;
            var indexes = [parentIndex];
            for (var i = 0; i < flowSkeleton.length; i++) {
                if (childIndex > -1) {
                    indexes.push(childIndex);
                    childIndex = flowJointData[childIndex].childIndex;
                } else {
                    break;
                }
            }
            for (i = 0; i < indexes.length; i++) {
                var index = indexes[i];
                self.joints.push(index);
                if (i > 0) {
                    self.length += flowJointData[index].length;
                }
            }
        };
        
        this.computeRecovery = function() {
            var parentIndex = self.joints[0];
            var parentJoint = flowJointData[parentIndex];
            parentJoint.recoveryPosition = parentJoint.node.currentPosition;
            var parentRotation = QUAT.multiply(MyAvatar.jointToWorldRotation(QUAT.IDENTITY(), parentJoint.parentIndex), parentJoint.initialXform.rot);
            for (var i = 1; i < self.joints.length; i++) {
                var joint = flowJointData[self.joints[i]];
                var rotation = i === 1 ? parentRotation : QUAT.multiply(rotation, parentJoint.initialXform.rot);
                joint.recoveryPosition = VEC3.sum(parentJoint.recoveryPosition, VEC3.multiplyQbyV(rotation, VEC3.multiply(joint.initialXform.pos, 0.01)));
                parentJoint = joint;
            }
            
        };

        this.update = function() {
            if (!self.getActive()) {
                return;
            }
            self.positions = [];
            self.radius = flowJointData[self.joints[0]].node.radius;
            self.computeRecovery();
            for (var i = 0; i < self.joints.length; i++){
                var joint = flowJointData[self.joints[i]];
                joint.update();
                self.positions.push(joint.node.currentPosition);
            }
        };
        
        this.solve = function(useCollisions) {
            if (!self.getActive()) {
                return;
            }
            var i, index;
            if (useCollisions) {
                var handCollisions = handSystem.checkThreadCollisions(self);
                var bodyCollisions = collisionSystem.checkThreadCollisions(self);
                var handTouchedJoint = -1;
                for (i = 0; i < self.joints.length; i++) {
                    index = self.joints[i];
                    if (bodyCollisions[i].offset > 0) {
                        flowJointData[index].solve(bodyCollisions[i]);
                    } else {
                        handTouchedJoint = (handCollisions[i].offset > 0) ? i : -1;
                        flowJointData[index].solve(handCollisions[i]);
                    }                   
                }
            } else {
                for (i = 0; i < self.joints.length; i++) {
                    index = self.joints[i];
                    flowJointData[index].solve(new FlowCollisionData());
                }
            }
        };
        
        this.computeJointRotations = function() {
            var rootIndex = flowJointData[self.joints[0]].parentIndex;
            var rootFramePositions = [];
            for (var i = 0; i < self.joints.length; i++){
                rootFramePositions.push(MyAvatar.worldToJointPoint(flowJointData[self.joints[i]].node.currentPosition, rootIndex));
            }
            var pos0 = rootFramePositions[0];
            var pos1 = rootFramePositions[1];
            
            var joint0 = flowJointData[self.joints[0]];
            var joint1 = flowJointData[self.joints[1]];
            
            var initial_pos1 = VEC3.sum(pos0, VEC3.multiplyQbyV(joint0.initialXform.rot, VEC3.multiply(joint1.initialXform.pos, 0.01)));
            
            var vec0 = VEC3.subtract(initial_pos1, pos0);
            var vec1 = VEC3.subtract(pos1, pos0);
            
            var delta = QUAT.rotationBetween(vec0, vec1);
            
            joint0.currentRotation = QUAT.multiply(delta, joint0.initialXform.rot);
            
            for (i = 1; i < self.joints.length-1; i++){
                var nextJoint = flowJointData[self.joints[i+1]];
                for (var j = i; j < self.joints.length; j++){
                    rootFramePositions[j] = VEC3.multiplyQbyV(
                        QUAT.inverse(joint0.currentRotation), 
                        VEC3.subtract(rootFramePositions[j], VEC3.multiply(joint0.initialXform.pos, 0.01))
                    );
                }
                pos0 = rootFramePositions[i];
                pos1 = rootFramePositions[i+1];
                initial_pos1 = VEC3.sum(pos0, VEC3.multiplyQbyV(joint1.initialXform.rot, VEC3.multiply(nextJoint.initialXform.pos, 0.01)));
                
                vec0 = VEC3.subtract(initial_pos1, pos0);
                vec1 = VEC3.subtract(pos1, pos0);
            
                delta = QUAT.rotationBetween(vec0, vec1);
            
                joint1.currentRotation = QUAT.multiply(delta, joint1.initialXform.rot);
                joint0 = joint1;
                joint1 = nextJoint;
            }
        };

        this.apply = function() {
            if (!self.getActive()) {
                return;
            }
            self.computeJointRotations();

            for (var i = 0; i < self.joints.length; i++){
                var joint = flowJointData[self.joints[i]];
                var parentJoint = flowJointData[joint.parentIndex];
                jointDebug.setDebugLine(
                    joint.name, 
                    joint.node.currentPosition, 
                    !parentJoint ? MyAvatar.getJointPosition(joint.parentIndex) : parentJoint.node.currentPosition, 
                    {
                        red: 255, 
                        green:(joint.colliding ? 0 : 255), 
                        blue:0
                    }, 
                    joint.isDummy
                );
                joint.apply();
            }
        };
        
        this.getActive = function() {
            return flowJointData[self.joints[0]].node.active;
        };
        
        self.computeThread(root);
    };
    
    var isActive, flowSkeleton, flowJointData, flowThreads, handSystem, collisionSystem, collisionDebug, jointDebug;
    
    function initFlow() {
        stopFlow();
        flowSkeleton = undefined;
        flowJointData = [];
        flowThreads = [];

        handSystem = new FlowHandSystem();
        collisionSystem = new FlowCollisionSystem();
        
        collisionDebug = new FlowDebug();
        jointDebug = new FlowDebug();
        
        collisionDebug.setVisible(SHOW_DEBUG_SHAPES);
        collisionDebug.setSolid(SHOW_SOLID_SHAPES);
        
        MyAvatar.setEnableMeshVisible(SHOW_AVATAR);
        jointDebug.setVisible(SHOW_DEBUG_SHAPES);
        jointDebug.setSolid(SHOW_SOLID_SHAPES);
        
        calculateConstraints();
        isActive = true;
    }
    
    function stopFlow() {
        isActive = false;
        if (!flowSkeleton) {
            return;
        }
        for (var i = 0; i < flowSkeleton.length; i++) {
            var index = flowSkeleton[i].index;
            MyAvatar.setJointRotation(index, flowJointData[index].initialXform.rot);
            MyAvatar.setJointTranslation(index, flowJointData[index].initialXform.pos);
        }
        collisionDebug.cleanup();
        jointDebug.cleanup();
        Script.requestGarbageCollection();
        MyAvatar.clearJointsData();
    }
        
    var setFlowScale = function(scale) {
        collisionSystem.setScale(scale);
        handSystem.setScale(scale);
        for (var i = 0; i < flowThreads.length; i++) {
            for (var j = 0; j < flowThreads[i].joints.length; j++){
                var joint = flowJointData[flowThreads[i].joints[j]];
                joint.node.radius = joint.node.initialRadius * scale;
            }
        }
    };

    var calculateConstraints = function() {
        var collisionKeys = Object.keys(CUSTOM_COLLISION_DATA);
        flowSkeleton = MyAvatar.getSkeleton().filter(
            function(jointInfo){
                var name = jointInfo.name;
                var namesplit = name.split("_");
                var isSimJoint = (name.substring(0, 3).toUpperCase() === SIM_JOINT_PREFIX.toUpperCase() && 
                                    !isNaN(parseFloat(name[name.length-1])) && 
                                    namesplit.length === 1);
                var isFlowJoint = (namesplit.length > 2 && 
                                    namesplit[0].toUpperCase() === FLOW_JOINT_PREFIX.toUpperCase());
                if (isFlowJoint || isSimJoint) {
                    var group;
                    if (isSimJoint) { 
                        for (var k = 1; k < name.length-1; k++) {
                            var subname = parseFloat(name.substring(name.length-k));
                            if (isNaN(subname) && name.length-k > SIM_JOINT_PREFIX.length) {
                                group = name.substring(SIM_JOINT_PREFIX.length, name.length - k + 1);
                                break;
                            }
                        }
                    } else {
                        group = namesplit[1];
                    }
                    if (group !== undefined) {
                        FLOW_JOINT_KEYWORDS.push(group);
                        var jointSettings;
                        if (CUSTOM_FLOW_DATA[group] !== undefined) {
                            jointSettings = CUSTOM_FLOW_DATA[group];
                        } else if (PRESET_FLOW_DATA[group] !== undefined){
                            jointSettings = PRESET_FLOW_DATA[group];
                        } else {
                            jointSettings = DEFAULT_JOINT_SETTINGS.get();
                        }
                        
                        FLOW_JOINT_DATA[group] = jointSettings;
                        if (flowJointData[jointInfo.index] === undefined) {
                            flowJointData[jointInfo.index] = new FlowJoint(jointInfo.index, jointInfo.parentIndex, name, group, jointSettings);
                        } 
                    }
                } 
                else {
                    var collisionSettings = (collisionKeys.length > 0) ? CUSTOM_COLLISION_DATA[name] : PRESET_COLLISION_DATA[name];
                    if (collisionSettings) {
                        collisionSystem.addCollisionShape(jointInfo.index, name, collisionSettings);
                    }
                }
                return (isFlowJoint || isSimJoint);
            }
        );
        
        var roots = [];
        
        for (var i = 0; i < flowSkeleton.length; i++) {
            var index = flowSkeleton[i].index;
            var flowJoint = flowJointData[index];
            var parentFlowJoint = flowJointData[flowJoint.parentIndex];
            if (parentFlowJoint !== undefined) {
                parentFlowJoint.childIndex = index;
            } else {
                flowJoint.node.anchored = true;
                roots.push(index);
            }      
        }
        
        for (i = 0; i < roots.length; i++) {
            var thread = new FlowThread(roots[i]);
            // add threads with at least 2 joints
            if (thread.joints.length > 1) {
                flowThreads.push(thread);
            }
        }
        if (flowThreads.length === 0) {
            MyAvatar.clearJointsData();
        }
        
        if (SHOW_DUMMY_JOINTS) {
            var jointCount = flowJointData.length;
            var extraIndex = flowJointData.length;
            var rightHandIndex = MyAvatar.getJointIndex("RightHand");
            var rightHandPosition = MyAvatar.getJointPosition(rightHandIndex);
            var parentIndex = rightHandIndex;
            for (i = 0; i < DUMMY_JOINT_COUNT; i++) {
                var childIndex = (i == (DUMMY_JOINT_COUNT - 1)) ? -1 : extraIndex + 1;
                flowJointData[extraIndex] = new FlowJointDummy(rightHandPosition, extraIndex, parentIndex, childIndex, FLOW_JOINT_DATA[DUMMY_KEYWORD]);
                parentIndex = extraIndex;
                extraIndex++;
            }
            flowJointData[jointCount].node.anchored = true;
        
            var extraThread = new FlowThread(jointCount);
            flowThreads.push(extraThread);
        }
        setFlowScale(MyAvatar.scale);
    };
    

    Script.update.connect(function(){
        if (!isActive || !flowSkeleton) return;
        
        if (USE_COLLISIONS) {
            Script.beginProfileRange("JS-Update-Collisions");
            collisionSystem.update();
            handSystem.update();
            Script.endProfileRange("JS-Update-Collisions");
        }
        
        Script.beginProfileRange("JS-Update-JointsUpdate");
        
        flowThreads.forEach(function(thread){
            thread.update();
        });

        Script.endProfileRange("JS-Update-JointsUpdate");
        Script.beginProfileRange("JS-Update-JointsSolve");

        flowThreads.forEach(function(thread){
            thread.solve(USE_COLLISIONS);
        });
        
        Script.endProfileRange("JS-Update-JointsSolve");
        Script.beginProfileRange("JS-Update-JointsApply");
        
        flowThreads.forEach(function(thread){
            thread.apply();
        });

        Script.endProfileRange("JS-Update-JointsApply");
    });
    
    Script.scriptEnding.connect(stopFlow);
    
    MyAvatar.skeletonChanged.connect(function(){
        Script.setTimeout(function() {
            stopFlow();
            MyAvatar.clearJointsData();
            initFlow();
        }, 200);
    });
    
    MyAvatar.scaleChanged.connect(function(){
        if (isActive) {
            setFlowScale(MyAvatar.scale);
        }
    });
    
    var varsToDebug = {
        "init": function() {
            initFlow();
        },      
        "stop": function() {
            stopFlow();
        },
        "isActive": function() {
            return isActive;
        },
        "toggleAvatarVisible": function() {
            SHOW_AVATAR = !SHOW_AVATAR;
            MyAvatar.setEnableMeshVisible(SHOW_AVATAR);
        },
        "toggleDebugShapes": function() {
            SHOW_DEBUG_SHAPES = !SHOW_DEBUG_SHAPES;
            if (USE_COLLISIONS) {
                collisionDebug.setVisible(SHOW_DEBUG_SHAPES);
            }
            jointDebug.setVisible(SHOW_DEBUG_SHAPES);
        },
        "toggleSolidShapes": function() {
            SHOW_SOLID_SHAPES = !SHOW_SOLID_SHAPES;
            collisionDebug.setSolid(SHOW_SOLID_SHAPES);
            jointDebug.setSolid(SHOW_SOLID_SHAPES);
        },
        "toggleCollisions": function() {
            USE_COLLISIONS = !USE_COLLISIONS;
            if (USE_COLLISIONS && SHOW_DEBUG_SHAPES) {
                collisionDebug.setVisible(true);
            } else {
                collisionDebug.setVisible(false);
            }
        },
        "toggleDummyJoints": function() {
            SHOW_DUMMY_JOINTS = !SHOW_DUMMY_JOINTS;
            stopFlow();
            initFlow();
        },
        "setJointDataValue": function(group, name, value) {
            var keyword = group.toUpperCase();
            for (var i = 0; i < flowThreads.length; i++) {
                for (var j = 0; j < flowThreads[i].joints.length; j++){
                    var index = flowThreads[i].joints[j];
                    var joint = flowJointData[index];
                    if (joint.name.toUpperCase().indexOf(keyword) > -1) {
                        var floatVal = (typeof value) != "boolean" ? parseFloat(value) : value;
                        FLOW_JOINT_DATA[group][name] = floatVal;
                        if (name === "stiffness") {
                            joint.stiffness = floatVal;
                        } else if (name === "radius") {
                            joint.node.initialRadius = floatVal;
                            joint.node.radius = MyAvatar.scale*floatVal;
                        } 
                        else {
                            joint.node[name] = floatVal;
                        }
                    }
                }
            }
        },
        "setCollisionDataValue": function(group, name, value) {
            var jointName = group;
            var floatVal = parseFloat(value);
            collisionSystem.modifyCollision(jointName, name, floatVal);
        }, 
        "getGroupData": function() {
            var joint_filter_keys = FLOW_JOINT_DATA;
            if (isActive) {
                joint_filter_keys = {};
                for (var i = 0; i < FLOW_JOINT_KEYWORDS.length; i++) {
                    joint_filter_keys[FLOW_JOINT_KEYWORDS[i]] = undefined;
                }
                for (i = 0; i < flowThreads.length; i++) {
                    for (var j = 0; j < flowThreads[i].joints.length; j++){
                        var index = flowThreads[i].joints[j];
                        var joint = flowJointData[index];
                        if (!joint_filter_keys[joint.group]) {
                            joint_filter_keys[joint.group] = {
                                "active": joint.node.active,
                                "stiffness": joint.stiffness, 
                                "radius": joint.node.initialRadius,
                                "gravity": joint.node.gravity,
                                "damping": joint.node.damping, 
                                "inertia": joint.node.inertia, 
                                "delta": joint.node.delta
                            };
                        }
                    }
                }
            }
            return joint_filter_keys;
            
        },
        "getDisplayData": function() {
            return {"avatar": SHOW_AVATAR, "collisions": USE_COLLISIONS, "debug": SHOW_DEBUG_SHAPES, "solid": SHOW_SOLID_SHAPES};
        },
        "getDefaultCollisionData": function() {
            return DEFAULT_COLLISION_SETTINGS;
        },
        "getCollisionData": function() {
            return collisionSystem.getCollisionData();
        },
        "addCollision": function(jointName) {
            return collisionSystem.addCollisionToJoint(jointName);
        },
        "removeCollision": function(jointName) {
            collisionSystem.removeCollisionFromJoint(jointName);
        }
    };
        
    // Register GlobalDebugger for API Debugger
    Script.registerValue("GlobalDebugger", varsToDebug);

    // Capture the controller values
    
    var leftTriggerPress = function (val) {
        var value = (val <= 1) ? val : 0;
        handSystem.setLeftTriggerValue(value);
    };

    var rightTriggerPress = function (val) {
        var value = (val <= 1) ? val : 0;
        handSystem.setRightTriggerValue(value);
    };
    
    var MAPPING_NAME = "com.highfidelity.hairTouch";
    var mapping = Controller.newMapping(MAPPING_NAME);
    mapping.from([Controller.Standard.RT]).peek().to(rightTriggerPress);
    mapping.from([Controller.Standard.LT]).peek().to(leftTriggerPress);

    Controller.enableMapping(MAPPING_NAME);
    if (typeof FLOWAPP === 'undefined') {
        initFlow();
    }
}());