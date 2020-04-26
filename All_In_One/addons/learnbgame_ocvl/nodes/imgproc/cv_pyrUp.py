import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLpyrUpNode(OCVLNodeBase):

    n_doc = "Upsamples an image and then blurs it."

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="Input image.")

    image_0_out: bpy.props.StringProperty(name="image_0_out", default=str(uuid.uuid4()), description="Image 0 output.")
    image_1_out: bpy.props.StringProperty(name="image_1_out", default=str(uuid.uuid4()), description="Image 1 output.")
    image_2_out: bpy.props.StringProperty(name="image_2_out", default=str(uuid.uuid4()), description="Image 2 output.")
    image_3_out: bpy.props.StringProperty(name="image_3_out", default=str(uuid.uuid4()), description="Image 3 output.")
    image_4_out: bpy.props.StringProperty(name="image_4_out", default=str(uuid.uuid4()), description="Image 4 output.")
    image_5_out: bpy.props.StringProperty(name="image_5_out", default=str(uuid.uuid4()), description="Image 5 output.")
    image_6_out: bpy.props.StringProperty(name="image_6_out", default=str(uuid.uuid4()), description="Image 6 output.")
    image_7_out: bpy.props.StringProperty(name="image_7_out", default=str(uuid.uuid4()), description="Image 7 output.")
    image_8_out: bpy.props.StringProperty(name="image_8_out", default=str(uuid.uuid4()), description="Image 8 output.")
    image_9_out: bpy.props.StringProperty(name="image_9_out", default=str(uuid.uuid4()), description="Image 9 output.")
    image_full_out: bpy.props.StringProperty(name="image_full_out", default=str(uuid.uuid4()), description="Image full output.")

    loc_pyramid_size: bpy.props.IntProperty(default=3, min=1, max=10, update=update_node, description="Number levels of pyramids.")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new("StringsSocket", "loc_pyramid_size").prop_name = 'loc_pyramid_size'

        self.outputs.new("StringsSocket", "image_full_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        image_in = self.get_from_props("image_in")
        loc_pyramid_size = self.get_from_props("loc_pyramid_size")

        img = image_in.copy()
        pyramid = [image_in]
        for i in range(loc_pyramid_size):
            img = cv2.pyrUp(img)
            pyramid.append(img)
        self._update_sockets(pyramid)
        self.refresh_output_socket("image_full_out", pyramid, is_uuid_type=True)

    def _update_sockets(self, pyramid):
        for i in range(10):
            prop_name = "image_{}_out".format(i)

            if i < len(pyramid):
                _uuid = str(uuid.uuid4())
                if self.outputs.get(prop_name):
                    pass
                else:
                    self.outputs.new("StringsSocket", prop_name)
                setattr(self, prop_name, _uuid)
                self.socket_data_cache[_uuid] = pyramid[i]
                self.outputs[prop_name].sv_set(_uuid)
            else:
                if self.outputs.get(prop_name):
                    self.outputs.remove(self.outputs[prop_name])

    def draw_buttons(self, context, layout):
        pass
