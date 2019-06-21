from bge_netlogic.ops.abstract_text_buffer import AbstractTextBuffer

class FileTextBuffer(AbstractTextBuffer):
    def __init__(self, file_path):
        AbstractTextBuffer.__init__(self)
        self.file_path = file_path
        pass

    def close(self):
        with open(self.file_path, "w") as f:
            f.truncate(0)
            f.write(self.buffer.getvalue())
        self.buffer.close()
        pass
    pass