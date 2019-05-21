var requirejs = require('requirejs');
var fs = require('fs');

var meta = JSON.parse(fs.readFileSync('package.json'));
global.CACHE_VERSION = meta.gearcache_version;

requirejs.config({
    //Pass the top-level main.js/index.js require
    //function to requirejs so that node modules
    //are loaded relative to the top-level JS file.
    nodeRequire: require,
    baseUrl    : './scripts'
});

global.window = global;
global._appstate = {};
global.ImageData = class ImageData {
    constructor(data, w, h) {
        this.data = data;
        this.width = w;
        this.height = h;
    }
};

global.redraw_all = function() {
    //stub function;
}

global.GRAPHICAL_TEST_MODE = false;

var argv = process.argv;
var args = [];

for (var i=2; i<argv.length; i++) {
    argv[i] = argv[i].trim();
    
    if (i > 2 && i < argv.length - 1 && argv[i] == '=') {
        //merge with adjacent
        args[args.length-1] += "=" + argv[i+1];
        i++;
    } else {
        args.push(argv[i]);
    }
}

var argmap = {}

for (var arg of args) {
    var param = arg.split("=");
    
    if (param.length != 2) {
        console.log("WARNING: malformed parameter ", param);
        continue;
    }
    
    var key = param[0], val = param[1].toLowerCase();
    
    if (val == 'true') 
        val = true;
    else if (val == 'false')
        val = false;
    else
        val = parseFloat(val);
    
    argmap[key] = val;
}
args = argmap;


class Cache {
    constructor(path) {
        this.path = path;
        this.keys = {};
    }
    
    load() {
        if (!fs.existsSync(this.path)) {
            return;
        }
        
        var buf = fs.readFileSync(this.path, "ascii");
        var ob = JSON.parse(buf);
        
        if (ob['VERSION'] != CACHE_VERSION) {
          console.warn("#Outdated gear cache detected; will regenerate. . .");
          this.keys = {VERSION : CACHE_VERSION};
          
          return;
        }
        
        this.keys = ob;
    }
    
    has(key) {
        return key in this.keys;
    }
    
    get(key) {
        return this.keys[key];
    }
    
    set(key, val) {
        this.keys[key] = val;
    }
    
    write() {
        this.keys['VERSION'] = CACHE_VERSION;
        fs.writeFileSync(this.path, JSON.stringify(this.keys));
    }
};

requirejs(['implicitgear'], function(implicitgear) {
    var cache = new Cache("gearcache.json");
    cache.load();
    
    var profile = new implicitgear.Profile(12);
    
    console.log("#\n#Using parameters:");
    for (var k in args) {
        if (k in profile) {
            console.log("#  ", k, "=", args[k]);
            profile[k] = args[k];
        }
    }
    console.log("#\n");
    
    if (cache.has(profile.hash())) {
        var rec = cache.get(profile.hash());
        
        console.log("pitch:", rec.pitch_radius);
        for (var v of rec.verts) {
            console.log(v[0], v[1]);
        }
        
        console.log("#loaded from cache");
        return;
    }
    
    var gear = new implicitgear.ImplicitGear(undefined, profile);
    gear.run();

    var cacherec = {pitch_radius: profile.pitch_radius, verts: []};
    
    var v = gear.mesh.verts[0], startv = v;
    var e = v.edges[0];
    
    var sortlist = [], _i=0;
    do {
        sortlist.push(v);
        
        v = e.otherVertex(v);
        if (v.edges.length == 2) {
            e = v.otherEdge(e);
        } else {
            sortlist.push(v);
            break;
        }
        
        if (_i++ > 5000000) {
            console.log("Infinite loop detected!");
            break;
        }
    } while (v != startv);
    
    console.log("pitch:", profile.pitch_radius);
    
    for (var v of sortlist) {
        console.log(v[0], v[1])
        cacherec.verts.push([v[0], v[1]]);
    }
    
    cache.set(profile.hash(), cacherec);
    cache.write();
});
