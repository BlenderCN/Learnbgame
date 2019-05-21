"""
 ChatModule: Allows to chat with the simulator.
"""

from .base import SyncModule

import bpy

class ChatModule(SyncModule):
    def register(self, parent):
        """
        Register this module with the editor
        """
        parent.registerCommand('msg', self.processMsgCommand)

    def unregister(self, parent):
        """
        Unregister this module from the editor
        """
        parent.unregisterCommand('msg')

    def processMsgCommand(self, username, message):
        """
        A chat message arrived from the simulator.
        """
        props = bpy.context.scene.b2rex_props
        props.chat.add()
        regionss = props.chat[-1]
        regionss.name = username+" "+message
        props.selected_chat = len(props.chat)-1

    def check(self, starttime, budget):
        """
        Check to see if the user wrote a new message for the chat,
        if so, send it.
        """
        props = self._props
        if props.next_chat:
            self.simrt.Msg(props.next_chat)
            props.next_chat = ""

    def draw(self, layout, session, props):
        """
        Draw the chat panel into the given layout.
        """
        if not len(props.chat):
            return
        row = layout.column()
        if props.chat_expand:
            row.prop(props, 'chat_expand', icon="TRIA_DOWN", text="Chat")
        else:
            row.prop(props, 'chat_expand', icon="TRIA_RIGHT", text="Chat")
            return

        row = layout.row() 
        row.label(text="Chat")
        row = layout.row() 
        row.template_list(props, 'chat', props, 'selected_chat',
                          rows=5)
        row = layout.row()
        row.prop(props, 'next_chat')


