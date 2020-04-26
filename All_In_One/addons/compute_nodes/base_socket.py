class BaseSocket:
    ir_type = NotImplemented

    def update_at_address(self, address):
        raise NotImplementedError()

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            self.draw_property(layout, text, node)
