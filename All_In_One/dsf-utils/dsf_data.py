
node_entry = {
  "id" : "$name",
  "name" : "$name",
  "label" : "$name",
  "type" : "node",
  "rotation_order" : "XYZ",
  "inherits_scale" : True,
  "center_point" : [
    {
      "id" : "x",
      "type" : "float",
      "name" : "xOrigin",
      "label" : "X Origin",
      "visible" : False,
      "value" : 0,
      "min" : -10000,
      "max" : 10000,
      "step_size" : 0.01
    },
    {
      "id" : "y",
      "type" : "float",
      "name" : "yOrigin",
      "label" : "Y Origin",
      "visible" : False,
      "value" : 0,
      "min" : -10000,
      "max" : 10000,
      "step_size" : 0.01
    },
    {
      "id" : "z",
      "type" : "float",
      "name" : "zOrigin",
      "label" : "Z Origin",
      "visible" : False,
      "value" : 0,
      "min" : -10000,
      "max" : 10000,
      "step_size" : 0.01
    }
  ],
  "end_point" : [
    {
      "id" : "x",
      "type" : "float",
      "name" : "xEnd",
      "label" : "X End",
      "visible" : False,
      "value" : 0,
      "min" : -10000,
      "max" : 10000,
      "step_size" : 0.01
    },
    {
      "id" : "y",
      "type" : "float",
      "name" : "yEnd",
      "label" : "Y End",
      "visible" : False,
      "value" : 200,
      "min" : -10000,
      "max" : 10000,
      "step_size" : 0.01
    },
    {
      "id" : "z",
      "type" : "float",
      "name" : "zEnd",
      "label" : "Z End",
      "visible" : False,
      "value" : 0,
      "min" : -10000,
      "max" : 10000,
      "step_size" : 0.01
    }
  ],
  "orientation" : [
    {
      "id" : "x",
      "type" : "float",
      "name" : "xOrientation",
      "label" : "X Orientation",
      "visible" : False,
      "value" : 0,
      "min" : -10000,
      "max" : 10000,
      "step_size" : 0.01
    },
    {
      "id" : "y",
      "type" : "float",
      "name" : "yOrientation",
      "label" : "Y Orientation",
      "visible" : False,
      "value" : 0,
      "min" : -10000,
      "max" : 10000,
      "step_size" : 0.01
    },
    {
      "id" : "z",
      "type" : "float",
      "name" : "zOrientation",
      "label" : "Z Orientation",
      "visible" : False,
      "value" : 0,
      "min" : -10000,
      "max" : 10000,
      "step_size" : 0.01
    }
  ],
  "rotation" : [
    {
      "id" : "x",
      "type" : "float",
      "name" : "XRotate",
      "label" : "X Rotate",
      "value" : 0,
      "min" : -10000,
      "max" : 10000,
      "step_size" : 0.5
    },
    {
      "id" : "y",
      "type" : "float",
      "name" : "YRotate",
      "label" : "Y Rotate",
      "value" : 0,
      "min" : -10000,
      "max" : 10000,
      "step_size" : 0.5
    },
    {
      "id" : "z",
      "type" : "float",
      "name" : "ZRotate",
      "label" : "Z Rotate",
      "value" : 0,
      "min" : -10000,
      "max" : 10000,
      "step_size" : 0.5
    }
  ],
  "translation" : [
    {
      "id" : "x",
      "type" : "float",
      "name" : "XTranslate",
      "label" : "X Translate",
      "value" : 0,
      "min" : -10000,
      "max" : 10000,
      "step_size" : 1
    },
    {
      "id" : "y",
      "type" : "float",
      "name" : "YTranslate",
      "label" : "Y Translate",
      "value" : 0,
      "min" : -10000,
      "max" : 10000,
      "step_size" : 1
    },
    {
      "id" : "z",
      "type" : "float",
      "name" : "ZTranslate",
      "label" : "Z Translate",
      "value" : 0,
      "min" : -10000,
      "max" : 10000,
      "step_size" : 1
    }
  ],
  "scale" : [
    {
      "id" : "x",
      "type" : "float",
      "name" : "XScale",
      "label" : "X Scale",
      "value" : 1,
      "min" : -10000,
      "max" : 10000,
      "display_as_percent" : True,
      "step_size" : 0.005
    },
    {
      "id" : "y",
      "type" : "float",
      "name" : "YScale",
      "label" : "Y Scale",
      "value" : 1,
      "min" : -10000,
      "max" : 10000,
      "display_as_percent" : True,
      "step_size" : 0.005
    },
    {
      "id" : "z",
      "type" : "float",
      "name" : "ZScale",
      "label" : "Z Scale",
      "value" : 1,
      "min" : -10000,
      "max" : 10000,
      "display_as_percent" : True,
      "step_size" : 0.005
    }
  ],
  "general_scale" : {
    "id" : "general_scale",
    "type" : "float",
    "name" : "Scale",
    "label" : "Scale",
    "value" : 1,
    "min" : -10000,
    "max" : 10000,
    "display_as_percent" : True,
    "step_size" : 0.005
  },
  "presentation" : {
    "type" : "Prop",
    "label" : "",
    "description" : "",
    "icon_large" : "",
    "colors" : [ [ 0.4, 0.4, 0.4 ], [ 1, 1, 1 ] ]
  }
}
