from bge_netlogic.ops.abstract_text_buffer import AbstractTextBuffer

class BLTextBuffer(AbstractTextBuffer):
    def __init__(self, blender_text_data):
        AbstractTextBuffer.__init__(self)
        self.blender_text_data = blender_text_data
        self.blender_text_data.clear()
        pass

    def close(self):
        self.blender_text_data.write(self.buffer.getvalue())
        AbstractTextBuffer.close(self)
        pass

    pass
