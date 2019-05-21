# octave_gradients
gradients for Cycles color ramps

installation, use Install from File and make sure it's enabled:
![image1](https://cloud.githubusercontent.com/assets/619340/10429386/66712cc4-70f8-11e5-833d-6432f3f51a14.png)

### What is it
____

This adds a panel called Octave Gradient Demo to the Cycles node view. From here you can choose the gradient by name, it will display the colors in the same panel. These are a group of 14 commonly used gradients you might be familiar with from Octave or Matlab. You could easily add extra palettes by augmenting the `hexviz` dict in `__init__.py`, I might extend this feature at a later stage.

![image15](https://cloud.githubusercontent.com/assets/619340/10436220/5d659d54-7125-11e5-8bfa-1032e736df1f.png)

![image2](http://i.stack.imgur.com/9TpRj.png)

### Usage
____

1. enable addon
2. make sure renderer is set to cycles 
3. create a new node based material
4. get a view open to see the nodes for the material
5. in the right side panel (use N to show the shelf) you'll see the _Octave Gradient Demo_ panel.
6. initially this will show all black ramp slots until you change the palette from the dropdown.
7. If you haven't already added a ColorRamp node to the current Material, that's OK the _set gradient_ button adds a ramp for you.
   - If you use _set gradient_  it will place one at (0,0) of the nodeview canvas.
   - If you use the operator called `Octave Cradient Operator` from the spacebar search feature in the nodeview, then it will add a new ColorRamp roughly where you mouse cursor is.

The addon kind of expects that you won't be using more than one ColorRamp node per material. It's the way I use it, but I can imagine that a node-picker would be handier so you can choose freely -- but this is not implemented, and if i'm the only one using it that's the way it will stay until I need more functionality.

### Usage in a script
____

The octave gradients add-on can be scripted without UI interaction. When this code is run in a context that doesn't have a node_tree then the add-on adds a small utility function called 'external_octave' to a globably available namespace called 'driver_namespace'.

external_octave() takes two parameters:  

  1. a colorRamp_reference
  2. a gradient index  (0..13)

options:

    0: 'lines'
    1: 'pink'
    2: 'copper'
    3: 'bone'
    4: 'gray'
    5: 'winter'
    6: 'autumn'
    7: 'summer'
    8: 'spring'
    9: 'cool'
    10: 'hot'
    11: 'hsv'
    12: 'jet'
    13: 'parula'

```python

import bpy
import addon_utils


def do_colorRamp(material_name, mode=12):

    f = addon_utils.enable("octave_gradients")
    if not f:
        print("Blender can't find the addon, this means it isn't installed properly")
        return

    # make it was added already, this checks before running the alternative code
    driver_namespace = bpy.app.driver_namespace
    if 'external_octave' not in driver_namespace:
        bpy.ops.scene.gradient_pusher()

    # the 'external_octave' function is now in drive, this will get a reference to it
    external_octave = bpy.app.driver_namespace['external_octave']

    # add material, or reuse existing one
    mymat = bpy.data.materials.get(material_name)
    if not mymat:
        mymat = bpy.data.materials.new(material_name)
        
    mymat.use_nodes = True
    nodes = mymat.node_tree.nodes

    if 'ColorRamp' not in nodes:
        nodes.new(type="ShaderNodeValToRGB")
    ColorRamp = nodes['ColorRamp']

    external_octave(ColorRamp, mode)  # jet=12

    # hook the ColorRamp up to the DiffuseBSDF node.
    DiffuseBSDF = nodes.get("Diffuse BSDF")
    mymat.node_tree.links.new(ColorRamp.outputs[0], DiffuseBSDF.inputs[0])

do_colorRamp('lazy_material', mode=4)
```