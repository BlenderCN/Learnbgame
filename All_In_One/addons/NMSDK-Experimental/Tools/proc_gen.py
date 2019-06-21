"""
A program to generate DESCRIPTOR, SCENE and GEOMETRY files to allow
for procedural generated spawning in NMS.
This works by the user selecting a list of folders directly containing
a SCENE file of a model.
These scenes are packaged together in a way that if the resultant SCENE
is referenced in the leveloneobjects file, one of the models will be
randomly chosen per planet, alleviating the need to add all the models
explicitly into the leveloneobjects file.
"""

__author__ = "monkeyman192"
__version__ = "0.5"

# stdlib imports
import os
import subprocess
from tkinter import (Tk, StringVar, Frame, Label, Entry, LEFT, VERTICAL, RIGHT,
                     BOTH, Y, Button)
from tkinter import filedialog, simpledialog, ttk, messagebox
# Internal imports
from ModelExporter.classes import (List, NMSString0x80, Model, Reference,
                                   TkResourceDescriptorData, TkGeometryData,
                                   TkResourceDescriptorList,
                                   TkModelDescriptorList)
from .wckToolTips import ToolTipManager


tt = ToolTipManager()
root = Tk()


class GUI(Frame):
    def __init__(self, master):
        self.master = master
        Frame.__init__(self, self.master)

        self.proc_name = StringVar()
        self.proc_name.set("PROCMODEL")

        # this will contain the indexes of the selected files
        self.selected_dirs = set()

        self.createWidgets()

    def createWidgets(self):
        # frame with buttons
        name_frame = Frame(self.master)
        name_label = Label(name_frame, text="Name: ")
        name_label.pack(side=LEFT)
        name_entry = Entry(name_frame, textvariable=self.proc_name)
        name_entry.pack(side=LEFT)
        name_frame.pack()
        list_frame = Frame(self.master)
        self.data_view = ttk.Treeview(
            list_frame, columns=['Object Name', 'Path'], displaycolumns='#all',
            selectmode='extended')
        self.data_view.heading("Object Name", text="Object Name")
        self.data_view.heading("Path", text="Path")
        self.data_view.column("Object Name", stretch=True)
        self.data_view.column("Path", stretch=True)
        self.data_view["show"] = 'headings'
        ysb = ttk.Scrollbar(list_frame, orient=VERTICAL,
                            command=self.data_view.yview)
        ysb.pack(side=RIGHT, fill=Y)
        self.data_view.configure(yscroll=ysb.set)
        self.data_view.pack(fill=BOTH, expand=1)
        list_frame.pack(fill=BOTH, expand=1)
        button_frame = Frame(self.master)
        add_button = Button(button_frame, text="ADD", command=self.add)
        add_button.pack(side=LEFT)
        tt.register(add_button, "Opens a dialog to select a folder containing "
                    "all the model folders")
        remove_button = Button(button_frame, text="REMOVE",
                               command=self.remove)
        remove_button.pack(side=LEFT)
        tt.register(remove_button, "Removes selected models from list")
        mult_button = Button(button_frame, text="MULTIPLY",
                             command=self.multiply)
        mult_button.pack(side=LEFT)
        tt.register(mult_button,
                    "Makes copies of all selected entries in the list")
        run_button = Button(button_frame, text="RUN", command=self.run)
        run_button.pack(side=LEFT)
        tt.register(run_button,
                    "Creates the proc-gen spawner for the selected models")
        runall_button = Button(button_frame, text="RUN ALL",
                               command=lambda: self.run(_all=True))
        runall_button.pack(side=LEFT)
        tt.register(runall_button,
                    "Creates the proc-gen spawner for all the models above")
        quit_button = Button(button_frame, text="QUIT", command=self.quit)
        quit_button.pack(side=LEFT)
        tt.register(quit_button, "Exits the program")
        button_frame.pack()

    def create_list(self):
        self.dir_list = os.listdir(self.path_name)
        # now add stuff to it
        # let's do a bit of precessing. We will have two options:
        # 1. The directory chosen contains a list of folders, each of which
        # contains a scene file
        # 2. The directory just contains a scene file
        # either way we want to make sure that the folders contain a scene file
        contains_scene = False
        scene_names = []
        for file in self.dir_list:
            if "SCENE" in file and "EXML" not in file.upper():
                # in this case we have option 2.
                # add the name of the scene file to the list of files
                contains_scene = True
                path = self.get_scene_path(os.path.join(self.path_name, file))
                scene_names.append((file, path))
        if contains_scene is False:
            for folder in self.dir_list:
                # in this case we have option 1
                subfolders = os.listdir(os.path.join(self.path_name, folder))
                # if we make it to this line option 1. is what has happened.
                # Search through
                for file in subfolders:
                    if "SCENE" in file and "EXML" not in file.upper():
                        contains_scene = True
                        path = self.get_scene_path(os.path.join(self.path_name,
                                                                folder, file))
                        scene_names.append((file, path))
        for scene in scene_names:
            self.data_view.insert("", 'end', values=scene)

    def get_scene_path(self, file_path):
        # this will open the scene file and read the path name
        try:
            fd = os.open(file_path, os.O_RDONLY | os.O_BINARY)
            os.lseek(fd, 0x60, os.SEEK_SET)
            bin_data = os.read(fd, 0x80)
            data = bin_data.decode()
            clean_data = data.rstrip(chr(0))
            return clean_data
        finally:
            os.close(fd)

    def remove(self):
        self.data_view.delete(*self.data_view.selection())

    def run(self, _all=False):
        if _all is False:
            # list of iids of selected elements
            self.selected_iids = self.data_view.selection()
        else:
            # in this case we just want everything in the list
            self.selected_iids = self.data_view.get_children()
        self.selected_objects = list(self.data_view.item(iid)['values'][1] for
                                     iid in self.selected_iids)
        if self.check_name(len(self.selected_objects)) is True:
            DataGenerator(self.proc_name.get().upper(), self.selected_objects)

    def check_name(self, length):
        # this will check whether or not the entered name is valid
        number_len = len(str(length))
        # add 1 for the underscore
        if len(self.proc_name.get()) + number_len + 1 > 16:
            short_name = self.proc_name.get().upper()[:16-number_len-1]
            if messagebox.askyesno(
                "Name Error", ("The name you have entered, '{0}', is too long."
                               "\n You can continue with a default shortened "
                               "name ({1}) by pressing 'Yes',\n or press 'No' "
                               "to go back and change the name").format(
                                   self.proc_name.get().upper(), short_name)):
                return True
            else:
                return False
        else:
            return True

    def add(self):
        self.path_name = filedialog.askdirectory(
            title="Specify path containing custom models")
        self.create_list()

    def multiply(self):
        # this creates n copies of all the selected entries in the list and
        # adds them to the list
        number = simpledialog.askinteger(prompt="Enter a number: ",
                                         title="Multiply!", minvalue=1)
        selected = self.data_view.selection()
        for iid in selected:
            for _ in range(number):
                self.data_view.insert(
                    "", 'end', values=self.data_view.item(iid)['values'])

    def quit(self):
        self.master.destroy()


class DataGenerator():
    def __init__(self, name, objects):
        self.name = name
        self.objects = objects

        self.path = os.path.join('CUSTOMMODELS', self.name.upper())

        # run the jobs
        self.generate_descriptor()
        self.generate_scene()
        self.generate_geometry()

        self.write()
        self.convert_to_mbin()

    def generate_descriptor(self):
        data_list = List()
        for i in range(len(self.objects)):
            data = dict()
            data['Id'] = "_{0}_{1}".format(self.name.upper(), i)
            data['Name'] = "_{0}_{1}".format(self.name.upper(), i)
            data['ReferencePaths'] = List(
                NMSString0x80(Value='{}.SCENE.MBIN'.format(self.objects[i])))
            data['Chance'] = 0
            data_list.append(TkResourceDescriptorData(**data))
        main_data = TkResourceDescriptorList(
            TypeId="_{}_".format(self.name.upper()),
            Descriptors=data_list)
        self.TkModelDescriptorList = TkModelDescriptorList(
            List=List(main_data))
        self.TkModelDescriptorList.make_elements(main=True)

    def generate_scene(self):
        # first generate the data
        self.SceneData = Model(os.path.join(self.path, self.name.upper()))
        self.SceneData.create_attributes(
            {'GEOMETRY': os.path.join(
                self.path, '{}.GEOMETRY.MBIN'.format(self.name.upper())),
             'NUMLODS': 1})
        for i in range(len(self.objects)):
            ref = Reference("_{0}_{1}".format(self.name.upper(), i),
                            Scenegraph='{}.SCENE.MBIN'.format(self.objects[i]))
            # just pass None because it doesn't matter with how Reference is
            # set up currently !!! THIS MIGHT CHANGE !!!
            ref.create_attributes(None)
            self.SceneData.add_child(ref)

        self.SceneData.construct_data()

        self.TkSceneNodeData = self.SceneData.get_data()
        self.TkSceneNodeData.make_elements(main=True)

    def generate_geometry(self):
        # this is super easy as the default template is all we need. Yay!
        self.TkGeometryData = TkGeometryData()
        self.TkGeometryData.make_elements(main=True)

    def write(self):
        # make sure the directory exists:
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.TkModelDescriptorList.tree.write(
            "{}.DESCRIPTOR.exml".format(
                os.path.join(self.path, self.name.upper())))
        self.TkGeometryData.tree.write(
            "{}.GEOMETRY.exml".format(
                os.path.join(self.path, self.name.upper())))
        self.TkSceneNodeData.tree.write(
            "{}.SCENE.exml".format(
                os.path.join(self.path, self.name.upper())))

    def convert_to_mbin(self):
        # passes all the files produced by
        print('Converting all .exml files to .mbin. Please wait while this '
              'finishes.')
        for directory, _, files in os.walk(self.path):
            for file in files:
                location = os.path.join(directory, file)
                if os.path.splitext(location)[1] == '.exml':
                    subprocess.call(["MBINCompiler.exe", location])
                    os.remove(location)


app = GUI(master=root)
app.mainloop()
