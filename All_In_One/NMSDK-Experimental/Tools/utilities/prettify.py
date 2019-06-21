from lxml import etree

from tkinter import Frame, Button, LEFT, Tk
from tkinter import filedialog


root = Tk()


class GUI(Frame):
    def __init__(self, master):
        self.master = master
        Frame.__init__(self, self.master)

        self.createWidgets()

    def createWidgets(self):
        # frame with buttons
        button_frame = Frame(self.master)
        run_button = Button(button_frame, text="RUN", command=self.process)
        run_button.pack(side=LEFT)
        quit_button = Button(button_frame, text="QUIT", command=self.quit)
        quit_button.pack(side=LEFT)
        button_frame.pack()

    def process(self):
        path_name = filedialog.askopenfilename(title="Specify exml file")
        prettyPrintXml(path_name)

    def quit(self):
        self.master.destroy()


def prettyPrintXml(xmlFilePathToPrettyPrint):
    assert xmlFilePathToPrettyPrint is not None
    parser = etree.XMLParser(resolve_entities=False, strip_cdata=False)
    document = etree.parse(xmlFilePathToPrettyPrint, parser)
    document.write(xmlFilePathToPrettyPrint,
                   xml_declaration='<?xml version="1.0" encoding="utf-8"?>',
                   pretty_print=True,
                   encoding='utf-8')

if __name__ == '__main__':
    app = GUI(master=root)
    app.mainloop()
