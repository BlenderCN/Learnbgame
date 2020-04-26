import bpy

class Socket:
    input_link_limit = 0
    output_link_limit = 0

    def draw_color(self, context, node):
        return self.color

    def draw(self, context, layout, node, text):
        raise NotImplementedError()

    def get_index(self, node):
        if self.is_output:
            return list(node.outputs).index(self)
        else:
            return list(node.inputs).index(self)

    def get_property(self):
        return None

    def set_property(self, value):
        pass

    def link_with(self, other):
        if self.is_output:
            self.id_data.links.new(other, self)
        else:
            self.id_data.links.new(self, other)

class DataFlowSocket(Socket):
    input_link_limit = 1
    output_link_limit = 0

    data_type = NotImplemented

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text=text)
        else:
            self.draw_property(layout, text, node)

    def draw_property(self, layout, text, node):
        layout.label(text=text)

    def get_value(self):
        raise NotImplementedError()

    def internal_data_changed(self, context = None):
        self.id_data.internal_data_socket_changed()

    def external_data_changed(self, context = None):
        self.id_data.external_data_socket_changed()

    def get_dependencies(self):
        return
        yield

class InternalDataFlowSocket(DataFlowSocket):
    pass

class ExternalDataFlowSocket(DataFlowSocket):
    pass

class ControlFlowBaseSocket(Socket):
    input_link_limit = 0
    output_link_limit = 1

    def draw(self, context, layout, node, text):
        layout.label(text=text)

class RelationalSocket(Socket):
    def draw(self, context, layout, node, text):
        layout.label(text=text)