"""BlenderFDS, result types"""

class BFResult():
    """Result returned by all exporting methods.
    
    sender -- message sender. Type: string or None.
    msg -- descriptive message, define at init only. Type: string or None. Eg. "msg"
    msgs -- list of descriptive messages. Type: list or None. Eg: ["msg1", "msg2", "msg3"]
    operators -- list of Blender operators that can help solving messages. Type: list or None.
    value -- value. Type: any.
    labels -- (readonly) formatted sender and msgs. Type: list of str. Eg: ("sender: msg1", "sender: msg2", ...))
    """
    icon = "INFO" # icon displayed by self.draw()
    
    def __init__(self, sender=None, msg=None, msgs=None, operators=None, value=None):
        self.sender = sender
        # msgs
        if msg: self.msgs = list((msg,))
        elif msgs: self.msgs = msgs
        else: self.msgs = list()
        # operators
        if operators: self.operators = operators
        else: self.operators = list()
        self.value = value
    
    # Thanks to idname, BFResult can be a well behaved item of a BFList (not unique!)
    def _get_idname(self) -> "str":
        return getattr(self.sender, "idname", str())
    
    idname = property(_get_idname)

    def __str__(self):
        return "<{0}: {1}>".format(
            self.__class__.__name__,
            getattr(self, "value", None) or self.labels
        )

    def __repr__(self):
        return self.__str__()

    def _get_labels(self) -> "list of str":
        """Format sender and msgs. Eg: ("XB: message", ...)."""
        sender = getattr(self.sender, "fds_label", None) or \
                 getattr(self.sender, "label", None) or \
                 getattr(self.sender, "idname", None)
        if sender: return list(": ".join((sender, msg)) for msg in self.msgs or tuple())
        else: return self.msgs or list()
    
    labels = property(_get_labels)

    def draw(self, layout):
        """Draw self user interface"""
        if not self.msgs: return
        layout = layout.column()
        for index, msg in enumerate(self.msgs):
            try: operator = self.operators[index]
            except IndexError: operator = None
            if operator:
                row = layout.split(.7)
                row.label(icon=self.icon, text=msg)
                row.operator(operator)
            else:
                layout.label(icon=self.icon, text=msg)

class BFException(BFResult, Exception):
    """Exception raised by all methods in case of an error."""
    icon = "ERROR" # icon displayed by self.draw()
