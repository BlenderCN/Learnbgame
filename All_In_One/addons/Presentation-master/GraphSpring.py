# /**
#  * Springy v2.7.1
#  *
#  * Copyright (c) 2010-2013 Dennis Hotson
#  *
#  * Permission is hereby granted, free of charge, to any person
#  * obtaining a copy of this software and associated documentation
#  * files (the "Software"), to deal in the Software without
#  * restriction, including without limitation the rights to use,
#  * copy, modify, merge, publish, distribute, sublicense, and/or sell
#  * copies of the Software, and to permit persons to whom the
#  * Software is furnished to do so, subject to the following
#  * conditions:
#  *
#  * The above copyright notice and this permission notice shall be
#  * included in all copies or substantial portions of the Software.
#  *
#  * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#  * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#  * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#  * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#  * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  * OTHER DEALINGS IN THE SOFTWARE.
#  */
import json
from random import *
import math

class Graph(object):
    nodeSet = {}
    nodes = []
    edges = []
    adjacency = {}
    nextNodeId = 0
    nextEdgeId = 0
    eventListeners = []
    def __init__(self):
        pass
    
    def loadJSON(self, _json):
        res = json.loads(_json)
        if "nodes" in res:
            self.addNodes(res["nodes"])
        if "edges" in res:
            self.addEdges(res["edges"])


        # // add nodes and edges from JSON object
        # Graph.prototype.loadJSON = function(json) {
        # /**
        # Springy's simple JSON format for graphs.

        # historically, Springy uses separate lists
        # of nodes and edges:

        # 	{
        # 		"nodes": [
        # 			"center",
        # 			"left",
        # 			"right",
        # 			"up",
        # 			"satellite"
        # 		],
        # 		"edges": [
        # 			["center", "left"],
        # 			["center", "right"],
        # 			["center", "up"]
        # 		]
        # 	}

        # **/
        # 	// parse if a string is passed (EC5+ browsers)
        # 	if (typeof json == 'string' || json instanceof String) {
        # 		json = JSON.parse( json );
        # 	}

        # 	if ('nodes' in json || 'edges' in json) {
        # 		this.addNodes.apply(this, json['nodes']);
        # 		this.addEdges.apply(this, json['edges']);
        # 	}
        # }

    def addNode(self, node):
        if not node.id in self.nodeSet:
            self.nodes.append(node)
        self.nodeSet[node.id] = node
        self.notify()
        return node
        # Graph.prototype.addNode = function(node) {
        # 	if (!(node.id in this.nodeSet)) {
        # 		this.nodes.push(node);
        # 	}

        # 	this.nodeSet[node.id] = node;

        # 	this.notify();
        # 	return node;
        # };

    def addNodes(self, nodes):
        for i in range(len(nodes)):
            name = nodes[i]
            node = Node(name, {"label": name})
            self.addNode(node)    
        # Graph.prototype.addNodes = function() {
        # 	// accepts variable number of arguments, where each argument
        # 	// is a string that becomes both node identifier and label
        # 	for (var i = 0; i < arguments.length; i++) {
        # 		var name = arguments[i];
        # 		var node = new Node(name, {label:name});
        # 		this.addNode(node);
        # 	}
        # };

    def addEdge(self, edge):
        exists = False
        for i in range(len(self.edges)):
            if self.edges[i].id == edge.id:
                exists = True
        if not exists:
            self.edges.append(edge)
        
        if not edge.source.id in self.adjacency:
            self.adjacency[edge.source.id] = {}
        
        if not edge.target.id in self.adjacency[edge.source.id]:
            self.adjacency[edge.source.id][edge.target.id] = []
        
        exists = False
        temp = self.adjacency[edge.source.id][edge.target.id]
        for i in range(len(temp)):
            if edge.id == temp[i].id:
                exists = True
        
        if not exists:
            self.adjacency[edge.source.id][edge.target.id].append(edge)
        
        self.notify()
        return edge

        # Graph.prototype.addEdge = function(edge) {
        # 	var exists = false;
        # 	this.edges.forEach(function(e) {
        # 		if (edge.id === e.id) { exists = true; }
        # 	});

        # 	if (!exists) {
        # 		this.edges.push(edge);
        # 	}

        # 	if (!(edge.source.id in this.adjacency)) {
        # 		this.adjacency[edge.source.id] = {};
        # 	}
        # 	if (!(edge.target.id in this.adjacency[edge.source.id])) {
        # 		this.adjacency[edge.source.id][edge.target.id] = [];
        # 	}

        # 	exists = false;
        # 	this.adjacency[edge.source.id][edge.target.id].forEach(function(e) {
        # 			if (edge.id === e.id) { exists = true; }
        # 	});

        # 	if (!exists) {
        # 		this.adjacency[edge.source.id][edge.target.id].push(edge);
        # 	}

        # 	this.notify();
        # 	return edge;
        # };

    def addEdges(self, edges):
        for i in range(len(edges)):
            e = edges[i]
            try:
                node1 = self.nodeSet[e[0]]
            except Exception as e:
                raise("invalid node name: node1")
            
            try:
                node2 = self.nodeSet[e[1]]
            except Exception as e:
                raise("invalid node name: node2")
            attr = e[2]
            self.newEdge(node1, node2, attr)
        #     	Graph.prototype.addEdges = function() {
        # 	// accepts variable number of arguments, where each argument
        # 	// is a triple [nodeid1, nodeid2, attributes]
        # 	for (var i = 0; i < arguments.length; i++) {
        # 		var e = arguments[i];
        # 		var node1 = this.nodeSet[e[0]];
        # 		if (node1 == undefined) {
        # 			throw new TypeError("invalid node name: " + e[0]);
        # 		}
        # 		var node2 = this.nodeSet[e[1]];
        # 		if (node2 == undefined) {
        # 			throw new TypeError("invalid node name: " + e[1]);
        # 		}
        # 		var attr = e[2];

        # 		this.newEdge(node1, node2, attr);
        # 	}
        # };


    def newNode(self, data):
        self.nextNodeId = self.nextNodeId + 1
        node = Node(self.nextNodeId, data)
        self.addNode(node)
        return node
        # Graph.prototype.newNode = function(data) {
        # 	var node = new Node(this.nextNodeId++, data);
        # 	this.addNode(node);
        # 	return node;
        # };

    def newEdge(self, source, target ,data):
        self.nextEdgeId = self.nextEdgeId + 1
        edge = Edge(self.nextEdgeId, source, target, data)
        self.addEdge(edge)
        return edge
        # 	Graph.prototype.newEdge = function(source, target, data) {
        # 	var edge = new Edge(this.nextEdgeId++, source, target, data);
        # 	this.addEdge(edge);
        # 	return edge;
        # };

    def getEdges(self, node1, node2):
        if node1.id in self.adjacency and node2.id in self.adjacency[node1.id]:
            return self.adjacency[node1.id][node2.id]
        return []
        # // find the edges from node1 to node2
        # Graph.prototype.getEdges = function(node1, node2) {
        # 	if (node1.id in this.adjacency
        # 		&& node2.id in this.adjacency[node1.id]) {
        # 		return this.adjacency[node1.id][node2.id];
        # 	}

        # 	return [];
        # };

    def removeNode(self, node):
        if node.id in self.nodeSet:
            self.nodeSet.pop(node.id, None)
        updated_nodes = []
        for i in range(len(self.nodes)):
            if self.nodes[i].id != node.id:
                updated_nodes.append(self.nodes[i])
        self.nodes = updated_nodes
        self.detachNode(node)
        # // remove a node and it's associated edges from the graph
        # Graph.prototype.removeNode = function(node) {
        # 	if (node.id in this.nodeSet) {
        # 		delete this.nodeSet[node.id];
        # 	}

        # 	for (var i = this.nodes.length - 1; i >= 0; i--) {
        # 		if (this.nodes[i].id === node.id) {
        # 			this.nodes.splice(i, 1);
        # 		}
        # 	}

        # 	this.detachNode(node);
        # };

    def detachNode(self, node):
        tmpEdges = list(map(lambda x: x, self.edges))
        for e in tmpEdges:
            if e.source.id == node.id or e.target.id == node.id:
                self.removeEdge(e)

        self.notify()
        # // removes edges associated with a given node
        # Graph.prototype.detachNode = function(node) {
        # 	var tmpEdges = this.edges.slice();
        # 	tmpEdges.forEach(function(e) {
        # 		if (e.source.id === node.id || e.target.id === node.id) {
        # 			this.removeEdge(e);
        # 		}
        # 	}, this);

        # 	this.notify();
        # };

    def isEmpty(self, obj):
        for k in obj:
            return True
        return False
        # var isEmpty = function(obj) {
        # 	for (var k in obj) {
        # 		if (obj.hasOwnProperty(k)) {
        # 			return false;
        # 		}
        # 	}
        # 	return true;
        # };
    def merge(self):
        pass
        # /* Merge a list of nodes and edges into the current graph. eg.
        # var o = {
        #     nodes: [
        #         {id: 123, data: {type: 'user', userid: 123, displayname: 'aaa'}},
        #         {id: 234, data: {type: 'user', userid: 234, displayname: 'bbb'}}
        #     ],
        #     edges: [
        #         {from: 0, to: 1, type: 'submitted_design', directed: true, data: {weight: }}
        #     ]
        # }
        # */
        # Graph.prototype.merge = function(data) {
        #     var nodes = [];
        #     data.nodes.forEach(function(n) {
        #         nodes.push(this.addNode(new Node(n.id, n.data)));
        #     }, this);

        #     data.edges.forEach(function(e) {
        #         var from = nodes[e.from];
        #         var to = nodes[e.to];

        #         var id = (e.directed)
        #             ? (id = e.type + "-" + from.id + "-" + to.id)
        #             : (from.id < to.id) // normalise id for non-directed edges
        #                 ? e.type + "-" + from.id + "-" + to.id
        #                 : e.type + "-" + to.id + "-" + from.id;

        #         var edge = this.addEdge(new Edge(id, from, to, e.data));
        #         edge.data.type = e.type;
        #     }, this);
        # };
    
    def filterNodes(self, fn):
        pass
        # Graph.prototype.filterNodes = function(fn) {
        #     var tmpNodes = this.nodes.slice();
        #     tmpNodes.forEach(function(n) {
        #         if (!fn(n)) {
        #             this.removeNode(n);
        #         }
        #     }, this);
        # };

    def filterEdges(self, fn):
        pass
        # Graph.prototype.filterEdges = function(fn) {
        #     var tmpEdges = this.edges.slice();
        #     tmpEdges.forEach(function(e) {
        #         if (!fn(e)) {
        #             this.removeEdge(e);
        #         }
        #     }, this);
        # };
    
    def removeEdge(self, edge):
        updated_edges = []
        for i in range(len(self.edges)):
            if self.edges[i].id != edge.id:
                updated_edges.append(self.edges[i])
        self.edges = updated_edges
        for x in self.adjacency:
            for y in self.adjacency[x]:
                edges = self.adjacency[x][y]
                updated_edges = []
                for j in range(len(edges)):
                    if self.adjacency[x][y][j].id != edge.id:
                        updated_edges.append(self.adjacency[x][y])
                self.adjacency[x][y] = updated_edges
                if len(self.adjacency[x][y]) == 0:
                    self.adjacency[x].pop(y, None)
            if self.isEmpty(self.adjacency[x]):
                self.adjacency.pop(x, None)
        self.notify()   
        # // remove a node and it's associated edges from the graph
        # Graph.prototype.removeEdge = function(edge) {
        #     for (var i = this.edges.length - 1; i >= 0; i--) {
        #         if (this.edges[i].id === edge.id) {
        #             this.edges.splice(i, 1);
        #         }
        #     }

        #     for (var x in this.adjacency) {
        #         for (var y in this.adjacency[x]) {
        #             var edges = this.adjacency[x][y];

        #             for (var j=edges.length - 1; j>=0; j--) {
        #                 if (this.adjacency[x][y][j].id === edge.id) {
        #                     this.adjacency[x][y].splice(j, 1);
        #                 }
        #             }

        #             // Clean up empty edge arrays
        #             if (this.adjacency[x][y].length == 0) {
        #                 delete this.adjacency[x][y];
        #             }
        #         }

        #         // Clean up empty objects
        #         if (isEmpty(this.adjacency[x])) {
        #             delete this.adjacency[x];
        #         }
        #     }

        #     this.notify();
        # };
        
    def addGraphListener(self, obj):
        self.eventListeners.append(obj)
        # Graph.prototype.addGraphListener = function(obj) {
        # 	this.eventListeners.push(obj);
        # };
    def notify(self):
        list(map(lambda obj : obj.graphChanged(), self.eventListeners))
        # Graph.prototype.notify = function() {
        #     this.eventListeners.forEach(function(obj){
        #         obj.graphChanged();
        #     });
        # };

class Node(object):
    id = None
    def __init__(self, id, data = {}):
        self.id = id 
        self.data = data
        #     // Data fields used by layout algorithm in this file:
        #     // this.data.mass
        #     // Data used by default renderer in springyui.js
        #     // this.data.label
        
	# var Node = Springy.Node = function(id, data) {
	# 	this.id = id;
	# 	this.data = (data !== undefined) ? data : {};
	# };
class Edge(object):
    def __init__(self, id, source, target, data = {}):
        self.id = id
        self.source = source
        self.target = target
        self.data = data
        # var Edge = Springy.Edge = function(id, source, target, data) {
        # 	this.id = id;
        # 	this.source = source;
        # 	this.target = target;
        # 	this.data = (data !== undefined) ? data : {};

        # // Edge data field used by layout alorithm
        # // this.data.length
        # // this.data.type
        # };




	

	
class ForceDirected(object):
    def __init__(self, graph, stiffness, repulsion, damping, minEnergyThreshold =  0.01, maxSpeed = 10000000):
        self.graph = graph
        self.stiffness = stiffness # spring stiffness constant
        self.repulsion = repulsion # repulsion constant
        self.damping = damping # velocity damping factor
        self.minEnergyThreshold = minEnergyThreshold # threshold used to determine render stop
        self.maxSpeed = maxSpeed # nodes aren't allowed to exceed this speed

        self.nodePoints = {} # keep track of points associated with nodes
        self.edgeSprings = {} # keep track of springs associated with edges
        # // -----------
        # var Layout = Springy.Layout = {};
        # Layout.ForceDirected = function(graph, stiffness, repulsion, damping, minEnergyThreshold, maxSpeed) {
        #     this.graph = graph;
        #     this.stiffness = stiffness; // spring stiffness constant
        #     this.repulsion = repulsion; // repulsion constant
        #     this.damping = damping; // velocity damping factor
        #     this.minEnergyThreshold = minEnergyThreshold || 0.01; //threshold used to determine render stop
        #     this.maxSpeed = maxSpeed || Infinity; // nodes aren't allowed to exceed this speed

        #     this.nodePoints = {}; // keep track of points associated with nodes
        #     this.edgeSprings = {}; // keep track of springs associated with edges
        # };
    def point(self, node):
        if not node.id in self.nodePoints:
            mass = node.data.mass 
            self.nodePoints[node.id] = Point(Vector.random(), mass)
        return self.nodePoints[node.id]
        # Layout.ForceDirected.prototype.point = function(node) {
        #     if (!(node.id in this.nodePoints)) {
        #         var mass = (node.data.mass !== undefined) ? node.data.mass : 1.0;
        #         this.nodePoints[node.id] = new Layout.ForceDirected.Point(Vector.random(), mass);
        #     }

        #     return this.nodePoints[node.id];
        # };

    def spring(self, edge):
        if not edge.id in self.edgeSprings:
            length = edge.data.length
            existingSpring = False

            _from = self.graph.getEdges(edge.source, edge.target)
            for e in _from:
                if existingSpring == False and e.id in self.edgeSprings:
                    existingSpring = self.edgeSprings[e.id]
                    break
            if existingSpring != False:
                return Spring(existingSpring.point1, existingSpring.point2, 0, 0)
            
            _from = self.graph.getEdges(edge.target, edge.source)
            for e in _from:
                if existingSpring == False and e.id in self.edgeSprings:
                    existingSpring = self.edgeSprings[e.id]
                    break
            
            if existingSpring != False:
                return Spring(existingSpring.point2, existingSpring.point1, 0, 0)
            
            self.edgeSprings[edge.id] = Spring(self.point(edge.source), self.point(edge.target), length, self.stiffness)

        return self.edgeSprings[edge.id]
        # Layout.ForceDirected.prototype.spring = function(edge) {
        # 	if (!(edge.id in this.edgeSprings)) {
        # 		var length = (edge.data.length !== undefined) ? edge.data.length : 1.0;

        # 		var existingSpring = false;

        # 		var from = this.graph.getEdges(edge.source, edge.target);
        # 		from.forEach(function(e) {
        # 			if (existingSpring === false && e.id in this.edgeSprings) {
        # 				existingSpring = this.edgeSprings[e.id];
        # 			}
        # 		}, this);

        # 		if (existingSpring !== false) {
        # 			return new Layout.ForceDirected.Spring(existingSpring.point1, existingSpring.point2, 0.0, 0.0);
        # 		}

        # 		var to = this.graph.getEdges(edge.target, edge.source);
        # 		from.forEach(function(e){
        # 			if (existingSpring === false && e.id in this.edgeSprings) {
        # 				existingSpring = this.edgeSprings[e.id];
        # 			}
        # 		}, this);

        # 		if (existingSpring !== false) {
        # 			return new Layout.ForceDirected.Spring(existingSpring.point2, existingSpring.point1, 0.0, 0.0);
        # 		}

        # 		this.edgeSprings[edge.id] = new Layout.ForceDirected.Spring(
        # 			this.point(edge.source), this.point(edge.target), length, this.stiffness
        # 		);
        # 	}

        # 	return this.edgeSprings[edge.id];
        # };

    def eachNode(self, callback):
        for node in self.graph.nodes:
            callback(node, self.point(node))
        # // callback should accept two arguments: Node, Point
        # Layout.ForceDirected.prototype.eachNode = function(callback) {
        #     var t = this;
        #     this.graph.nodes.forEach(function(n){
        #         callback.call(t, n, t.point(n));
        #     });
        # };

    def eachEdge(self, callback):
        for edge in self.graph.edges:
            callback(edge, self.spring(edge))
        # // callback should accept two arguments: Edge, Spring
        # Layout.ForceDirected.prototype.eachEdge = function(callback) {
        #     var t = this;
        #     this.graph.edges.forEach(function(e){
        #         callback.call(t, e, t.spring(e));
        #     });
        # };

    def eachSpring(self, callback):
        for edge in self.graph.edges:
            callback(self.spring(edge))
        # // callback should accept one argument: Spring
        # Layout.ForceDirected.prototype.eachSpring = function(callback) {
        # 	var t = this;
        # 	this.graph.edges.forEach(function(e){
        # 		callback.call(t, t.spring(e));
        # 	});
        # };


    def applyCoulombsLaw(self):
        for n1 in self.graph.nodes:
            point1 = self.point(n1)
            for n2 in self.graph.nodes:
                point2 = self.point(n2)
                if point1 != point2:
                    d = point1.p.subtract(point2.p)
                    distance = d.magnitude() + .1
                    direction = d.normalise()

                    point1.applyForce(direction.multiply(self.repulsion).divide(distance* distance*.5))
                    point2.applyForce(direction.multiply(self.repulsion).divide(distance* distance*-.5))
                    
        # // Physics stuff
        # Layout.ForceDirected.prototype.applyCoulombsLaw = function() {
        #     this.eachNode(function(n1, point1) {
        #         this.eachNode(function(n2, point2) {
        #             if (point1 !== point2)
        #             {
        #                 var d = point1.p.subtract(point2.p);
        #                 var distance = d.magnitude() + 0.1; // avoid massive forces at small distances (and divide by zero)
        #                 var direction = d.normalise();

        #                 // apply force to each end point
        #                 point1.applyForce(direction.multiply(this.repulsion).divide(distance * distance * 0.5));
        #                 point2.applyForce(direction.multiply(this.repulsion).divide(distance * distance * -0.5));
        #             }
        #         });
        #     });
        # };
    def applyHookesLaw(self):
        for edge in self.graph.edges:
            spring  = (self.spring(edge))
            d = spring.point2.p.subtract(spring.point1.p)
            displacement = spring.length - d.magnitude()
            direction = d.normalise()

            spring.point1.applyForce(direction.multiply(spring.k * displacement * -.5))
            spring.point2.applyForce(direction.multiply(spring.k * displacement * .5))
        # Layout.ForceDirected.prototype.applyHookesLaw = function() {
        # 	this.eachSpring(function(spring){
        # 		var d = spring.point2.p.subtract(spring.point1.p); // the direction of the spring
        # 		var displacement = spring.length - d.magnitude();
        # 		var direction = d.normalise();

        # 		// apply force to each end point
        # 		spring.point1.applyForce(direction.multiply(spring.k * displacement * -0.5));
        # 		spring.point2.applyForce(direction.multiply(spring.k * displacement * 0.5));
        # 	});
        # };
    def attractToCentre(self):
        for node in self.graph.nodes:
            point = self.point(node)
            direction = point.p.multiply(-1)
            point.applyForce(direction.multiply(self.repulsion/50))
        # Layout.ForceDirected.prototype.attractToCentre = function() {
        # 	this.eachNode(function(node, point) {
        # 		var direction = point.p.multiply(-1.0);
        # 		point.applyForce(direction.multiply(this.repulsion / 50.0));
        # 	});
        # };

    def updateVelocity(self, timestep):
        for node in self.graph.nodes:
            point = self.point(node)
            point.v = point.v.add(point.a.multiply(timestep)).multiply(self.damping)
            if point.v.magnitude() > self.maxSpeed:
                point.v = point.v.normalise().multiply(self.maxSpeed)
            point.a = Vector(0,0)
        # Layout.ForceDirected.prototype.updateVelocity = function(timestep) {
        #     this.eachNode(function(node, point) {
        #         // Is this, along with updatePosition below, the only places that your
        #         // integration code exist?
        #         point.v = point.v.add(point.a.multiply(timestep)).multiply(this.damping);
        #         if (point.v.magnitude() > this.maxSpeed) {
        #             point.v = point.v.normalise().multiply(this.maxSpeed);
        #         }
        #         point.a = new Vector(0,0);
        #     });
        # };

    def updatePosition(self, timestep):
        for node in self.graph.nodes:
            point = self.point(node)
            point.p = point.p.add(point.v.multiply(timestep))
        # Layout.ForceDirected.prototype.updatePosition = function(timestep) {
        #     this.eachNode(function(node, point) {
        #         // Same question as above; along with updateVelocity, is this all of
        #         // your integration code?
        #         point.p = point.p.add(point.v.multiply(timestep));
        #     });
        # };

    def totalEnergy(self, timestep):
        energy = 0
        for node in self.graph.nodes:
            point = self.point(node)
            speed = point.v.magnitude()
            energy += .5 * point.m * speed * speed

        return energy    
        # // Calculate the total kinetic energy of the system
        # Layout.ForceDirected.prototype.totalEnergy = function(timestep) {
        # 	var energy = 0.0;
        # 	this.eachNode(function(node, point) {
        # 		var speed = point.v.magnitude();
        # 		energy += 0.5 * point.m * speed * speed;
        # 	});

        # 	return energy;
        # };

	# var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; }; // stolen from coffeescript, thanks jashkenas! ;-)

	# Springy.requestAnimationFrame = __bind(this.requestAnimationFrame ||
	# 	this.webkitRequestAnimationFrame ||
	# 	this.mozRequestAnimationFrame ||
	# 	this.oRequestAnimationFrame ||
	# 	this.msRequestAnimationFrame ||
	# 	(function(callback, element) {
	# 		this.setTimeout(callback, 10);
	# 	}), this);

    def start(self, render, onRenderStop, onRenderStart):
        t = self
        if self._started:
            return
        self._started = True
        self._stop = False
        if onRenderStart:
            onRenderStart()
        self.step(render, onRenderStop)
        # /**
        #  * Start simulation if it's not running already.
        #  * In case it's running then the call is ignored, and none of the callbacks passed is ever executed.
        #  */
        # Layout.ForceDirected.prototype.start = function(render, onRenderStop, onRenderStart) {
        # 	var t = this;

        # 	if (this._started) return;
        # 	this._started = true;
        # 	this._stop = false;

        # 	if (onRenderStart !== undefined) { onRenderStart(); }

        # 	Springy.requestAnimationFrame(function step() {
        # 		t.tick(0.03);

        # 		if (render !== undefined) {
        # 			render();
        # 		}

        # 		// stop simulation when energy of the system goes below a threshold
        # 		if (t._stop || t.totalEnergy() < t.minEnergyThreshold) {
        # 			t._started = false;
        # 			if (onRenderStop !== undefined) { onRenderStop(); }
        # 		} else {
        # 			Springy.requestAnimationFrame(step);
        # 		}
        # 	});
        # };
    def step(self, render, onRenderStop):
        self.tick(.03)
        if render:
            render()
        if self._stop or self.totalEnergy < self.minEnergyThreshold:
            self._started = False
            if onRenderStop:
                onRenderStop()

    def stop(self):
        self._stop = True
        # Layout.ForceDirected.prototype.stop = function() {
        #     this._stop = true;
        # }
    def tick(self, timestep):
        self.applyCoulombsLaw()
        self.applyHookesLaw()
        self.attractToCentre()
        self.updateVelocity(timestep)
        self.updatePosition(timestep)
        # Layout.ForceDirected.prototype.tick = function(timestep) {
        # 	this.applyCoulombsLaw();
        # 	this.applyHookesLaw();
        # 	this.attractToCentre();
        # 	this.updateVelocity(timestep);
        # 	this.updatePosition(timestep);
        # };

    def nearest(self, pos):
        min = { "node": None, "point": None, "distance": None }
        for n in self.graph.nodes:
            point = self.point(n)
            distance = point.p.subtract(pos).magnitude()
            if min["distance"] == None or distance < min["distance"]:
                min = { "node": n, "point": point, "distance": distance }
        return min
        # // Find the nearest point to a particular position
        # Layout.ForceDirected.prototype.nearest = function(pos) {
        #     var min = {node: null, point: null, distance: null};
        #     var t = this;
        #     this.graph.nodes.forEach(function(n){
        #         var point = t.point(n);
        #         var distance = point.p.subtract(pos).magnitude();

        #         if (min.distance === null || distance < min.distance) {
        #             min = {node: n, point: point, distance: distance};
        #         }
        #     });

        #     return min;
        # };
    def getBoundingBox(self):
        bottomleft = Vector(-2,-2)
        topright = Vector(2,2)
        for node in self.graph.nodes:
            point = self.point(node)
            if point.p.x < bottomleft.x:
                bottomleft.x = point.p.x
            if point.p.y < bottomleft.y:
                bottomleft.y = point.p.y
            if point.p.x > topright.x:
                topright.x = point.p.x
            if point.p.y > topright.y:
                topright.y = point.p.y
        padding = topright.subtract(bottomleft).multiply(.07)
        return {"bottomleft": bottomleft.subtract(padding), "topright": topright.add(padding) }
        # // returns [bottomleft, topright]
        # Layout.ForceDirected.prototype.getBoundingBox = function() {
        #     var bottomleft = new Vector(-2,-2);
        #     var topright = new Vector(2,2);

        #     this.eachNode(function(n, point) {
        #         if (point.p.x < bottomleft.x) {
        #             bottomleft.x = point.p.x;
        #         }
        #         if (point.p.y < bottomleft.y) {
        #             bottomleft.y = point.p.y;
        #         }
        #         if (point.p.x > topright.x) {
        #             topright.x = point.p.x;
        #         }
        #         if (point.p.y > topright.y) {
        #             topright.y = point.p.y;
        #         }
        #     });

        #     var padding = topright.subtract(bottomleft).multiply(0.07); // ~5% padding

        #     return {bottomleft: bottomleft.subtract(padding), topright: topright.add(padding)};
        # };

class Vector(object):
    x = 0
    y = 0
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # // Vector
        # var Vector = Springy.Vector = function(x, y) {
        #     this.x = x;
        #     this.y = y;
        # }
    @staticmethod
    def random():
        return Vector(10.0 * (random() - 0.5), 10.0 * (random() - 0.5))
        # Vector.random = function() {
        #     return new Vector(10.0 * (Math.random() - 0.5), 10.0 * (Math.random() - 0.5));
        # };

    def add(self, v2):
        return Vector(self.x + v2.x, self.y + v2.y)
        # Vector.prototype.add = function(v2) {
        # 	return new Vector(this.x + v2.x, this.y + v2.y);
        # };
    def subtract(self, v2):
        return Vector(self.x - v2.x, self.y - v2.y)
        # Vector.prototype.subtract = function(v2) {
        #     return new Vector(this.x - v2.x, this.y - v2.y);
        # };
    def multiply(self , n):
        return Vector(self.x * n, self.y * n)
        # Vector.prototype.multiply = function(n) {
        # 	return new Vector(this.x * n, this.y * n);
        # };

    def divide(self, n):
        if n == 0:
            return Vector(0,0)
        return Vector(self.x/n, self.y/n)
        # Vector.prototype.divide = function(n) {
        #     return new Vector((this.x / n) || 0, (this.y / n) || 0); // Avoid divide by zero errors..
        # };
    def magnitude(self):
        return math.sqrt(self.x*self.x + self.y*self.y)
        # Vector.prototype.magnitude = function() {
        # 	return Math.sqrt(this.x*this.x + this.y*this.y);
        # };
    def normal(self):
        return Vector(-self.y, self.x)
        # Vector.prototype.normal = function() {
        # 	return new Vector(-this.y, this.x);
        # };
    def normalise(self):
        return self.divide(self.magnitude())
        # Vector.prototype.normalise = function() {
        # 	return this.divide(this.magnitude());
        # };

class Point(object):
    def __init__(self, position, mass):
        self.p = position
        self.m = mass
        self.v = Vector(0,0)
        self.a = Vector(0,0)
        # // Point
        # Layout.ForceDirected.Point = function(position, mass) {
        #     this.p = position; // position
        #     this.m = mass; // mass
        #     this.v = new Vector(0, 0); // velocity
        #     this.a = new Vector(0, 0); // acceleration
        # };
    def applyForce(self, force):
        self.a = self.a.add(force.divide(self.m))
        # Layout.ForceDirected.Point.prototype.applyForce = function(force) {
        # 	this.a = this.a.add(force.divide(this.m));
        # };

class Spring(object):
    def __init__(self, point1, point2, length , k):
        self.point1 = point1
        self.point2 = point2
        self.length = length
        self.k = k
        # // Spring
        # Layout.ForceDirected.Spring = function(point1, point2, length, k) {
        # 	this.point1 = point1;
        # 	this.point2 = point2;
        # 	this.length = length; // spring length at rest
        # 	this.k = k; // spring constant (See Hooke's law) .. how stiff the spring is
        # };

	# // Layout.ForceDirected.Spring.prototype.distanceToPoint = function(point)
	# // {
	# // 	// hardcore vector arithmetic.. ohh yeah!
	# // 	// .. see http://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment/865080#865080
	# // 	var n = this.point2.p.subtract(this.point1.p).normalise().normal();
	# // 	var ac = point.p.subtract(this.point1.p);
	# // 	return Math.abs(ac.x * n.x + ac.y * n.y);
	# // };

	# /**
	#  * Renderer handles the layout rendering loop
	#  * @param onRenderStop optional callback function that gets executed whenever rendering stops.
	#  * @param onRenderStart optional callback function that gets executed whenever rendering starts.
	#  * @param onRenderFrame optional callback function that gets executed after each frame is rendered.
	#  */
	# var Renderer = Springy.Renderer = function(layout, clear, drawEdge, drawNode, onRenderStop, onRenderStart, onRenderFrame) {
	# 	this.layout = layout;
	# 	this.clear = clear;
	# 	this.drawEdge = drawEdge;
	# 	this.drawNode = drawNode;
	# 	this.onRenderStop = onRenderStop;
	# 	this.onRenderStart = onRenderStart;
	# 	this.onRenderFrame = onRenderFrame;

	# 	this.layout.graph.addGraphListener(this);
	# }

	# Renderer.prototype.graphChanged = function(e) {
	# 	this.start();
	# };

	# /**
	#  * Starts the simulation of the layout in use.
	#  *
	#  * Note that in case the algorithm is still or already running then the layout that's in use
	#  * might silently ignore the call, and your optional <code>done</code> callback is never executed.
	#  * At least the built-in ForceDirected layout behaves in this way.
	#  *
	#  * @param done An optional callback function that gets executed when the springy algorithm stops,
	#  * either because it ended or because stop() was called.
	#  */
	# Renderer.prototype.start = function(done) {
	# 	var t = this;
	# 	this.layout.start(function render() {
	# 		t.clear();

	# 		t.layout.eachEdge(function(edge, spring) {
	# 			t.drawEdge(edge, spring.point1.p, spring.point2.p);
	# 		});

	# 		t.layout.eachNode(function(node, point) {
	# 			t.drawNode(node, point.p);
	# 		});
			
	# 		if (t.onRenderFrame !== undefined) { t.onRenderFrame(); }
	# 	}, this.onRenderStop, this.onRenderStart);
	# };

	# Renderer.prototype.stop = function() {
	# 	this.layout.stop();
	# };


    