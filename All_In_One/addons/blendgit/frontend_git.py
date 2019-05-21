import bpy
import os
from . import backend_git as b
from bpy.app.handlers import persistent

class GitLog(bpy.types.Operator):
    bl_idname = "git.log"
    bl_label = "Log"
    
    def populateLog(self, context, log):
        records = log.split("\n\n")
        commit = None
        author = None
        date = None
        
        #print("R:", records)
        for i in range(0, len(records)):
               
            if i % 2 == 0:
                lines = records[i].split("\n")
                #print("L:", lines)
                commit = lines[0].split(" ")[1]
                author = lines[1].split(": ")[1]
                date = lines[2].split(": ")[1]
            else:
                message = records[i].split("\n")[0] 
                    
                entry = context.scene.git.history.add()
                entry.message = message
                entry.commit = commit
                entry.author = author
                entry.date = date
                
                #the display name ?
                entry.name = message + " " + date + " " + commit
    
    def isRepo(self, context, g):
        s = g.status(context.scene.git.file)
        stat = s.decode("utf-8")
        if "fatal: Not a git repository" in stat: #very hackish
            return False
        return True    
    
    def execute(self, context):
        g = b.Git(context.scene.git.workdir)
        
        if self.isRepo(context, g):
            logRaw = g.log(context.scene.git.file)
            log = logRaw.decode("utf-8")
            context.scene.git.history.clear()
            
            #print("LOG", log)
            if log != "":
                self.populateLog(context, log)
        
        return {'FINISHED'}
    
class GitReset(bpy.types.Operator):
    bl_idname = "git.reset"
    bl_label = "Reset"
    
    def execute(self, context):
        g = b.Git(context.scene.git.workdir)
        g.reset(context.scene.git.file)
        return {'FINISHED'}

class GitCommit(bpy.types.Operator):
    bl_idname = "git.commit"
    bl_label = "Commit"
    
    def execute(self, context):
        
        g = b.Git(context.scene.git.workdir) 
        s = g.status(context.scene.git.file)
        status = s.decode("utf-8")
        print(status)
        
        if "fatal: Not a git repository" in status: #very hackish
            print("Init and Add")
            print(g.init().decode("utf-8"))
            print(g.add(context.scene.git.file).decode("utf-8"))
            bpy.ops.git.branches_list()
        elif "Untracked" in status:
            print("Add")
            print(g.add(context.scene.git.file).decode("utf-8"))
        
        print(g.commit(context.scene.git.file, context.scene.git.msg).decode("utf-8"))
        bpy.ops.git.log()
#        if len(context.scene.git.history) != 0:
#            context.scene.git.commit = context.scene.git.history[0].commit
#            print("lastcommit", context.scene.git.commit)
#        bpy.ops.wm.save_mainfile(check_existing=False)
        return {'FINISHED'}
    
class GitUpdate(bpy.types.Operator):
    bl_idname = "git.update"
    bl_label = "Update"
    
    def execute(self, context):
        g = b.Git(context.scene.git.workdir) 
        index = context.scene.git.active_entry
        entry = context.scene.git.history[index]
        g.update(context.scene.git.file, context.scene.git.workdir, entry.commit)
        #load file here
        commit = str(entry.commit)
        bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)
        
        #set history pointer
        print("fetched commit", commit)
        for i in range(0, len(bpy.context.scene.git.history)):
            e = bpy.context.scene.git.history[i]
            if e.commit == commit:
                bpy.context.scene.git.active_entry = i
                break
         
        return {'FINISHED'}

class GitListBranches(bpy.types.Operator):
    bl_idname = "git.branches_list"
    bl_label = "List Branches"
    
    def execute(self, context):
        g = b.Git(context.scene.git.workdir)
        br = g.branch("", "LIST").decode("utf-8")
        context.scene.git.branch_items = br
        return {'FINISHED'}

class GitAddBranch(bpy.types.Operator):
    bl_idname = "git.branch_add"
    bl_label = "Add Branch"
    
    def execute(self, context):
        g = b.Git(context.scene.git.workdir)
        g.branch(context.scene.git.add_branch_name, "ADD")
        bpy.ops.git.branches_list()
        bpy.ops.git.log()
        return {'FINISHED'}

class GitDeleteBranch(bpy.types.Operator):
    bl_idname = "git.branch_delete"
    bl_label = "Delete Branch"
    
    def execute(self, context):
        g = b.Git(context.scene.git.workdir)
        print(g.branch(context.scene.git.delete_branch, "DELETE").decode("utf-8"))
        bpy.ops.git.branches_list()
        bpy.ops.git.log()
        return {'FINISHED'}

class GitCheckout(bpy.types.Operator):
    bl_idname = "git.checkout"
    bl_label = "Checkout"
    
    def execute(self, context):
        g = b.Git(context.scene.git.workdir)
        print(g.checkout(context.scene.git.branch).decode("utf-8"))
        bpy.ops.git.log()
        return {'FINISHED'}

class GitMerge(bpy.types.Operator):
    bl_idname = "git.merge"
    bl_label = "Merge"
    
    def execute(self, context):
        g = b.Git(context.scene.git.workdir)
        print("M", context.scene.git.merge_branch)
        o = g.merge(context.scene.git.merge_branch, context.scene.git.merge_strategy, context.scene.git.msg)
        print(o.decode("utf-8"))
        bpy.ops.git.log()
        return {'FINISHED'}
   
    
    
class LogEntry(bpy.types.PropertyGroup):
    
    message = bpy.props.StringProperty(name = "message")
    author = bpy.props.StringProperty(name = "author")
    date = bpy.props.StringProperty(name = "date")
    commit = bpy.props.StringProperty(name = "commit")
    

class GitContext(bpy.types.PropertyGroup):
   
    merge_strategies = [("ours", "Ours", "In case of conflict prefer merged-in branch changes", 0),
                        ("theirs", "Theirs", "In case of conflict prefer target branch changes", 1)]
    
    def branches(self, br):
        lines = br.split("\n")
        #print(br, lines)
        items = []
        for i in range(0, len(lines)-1):
            st = lines[i][2:]
            t = (st, st, st, i)
            items.append(t)
        return items
    
    def branch_items(self, context):
        return self.branches(context.scene.git.branch_items)
    
    def checkout(self, context):
        bpy.ops.git.checkout()
        return None
    
    workdir = bpy.props.StringProperty(name = "workdir")
    file = bpy.props.StringProperty(name = "file")
    msg = bpy.props.StringProperty(name = "msg")
    merge_msg = bpy.props.StringProperty(name = "merge_msg")
    active_entry = bpy.props.IntProperty(name = "active_entry")
    history = bpy.props.CollectionProperty(type = LogEntry, name = "history")
    
    branch = bpy.props.EnumProperty(items = branch_items, name = "branch", update = checkout)
    delete_branch = bpy.props.EnumProperty(items = branch_items, name = "delete_branch")
    add_branch_name = bpy.props.StringProperty(name = "add_branch_name")
    merge_strategy = bpy.props.EnumProperty(items = merge_strategies, name = "merge_strategy")
    merge_branch = bpy.props.EnumProperty(items = branch_items, name = "merge_branch")
    branch_items = bpy.props.StringProperty(name = "branch_items")
       

class GitPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_git"
    bl_label = "Git"
    bl_context = "object"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    
    def register():
        
        if hasattr(bpy.types.Scene, "git") == 0:
            print("creating GitContext")
            bpy.types.Scene.git = bpy.props.PointerProperty(type = GitContext, name = "GitContext")
    #    bpy.types.Scene.commit = bpy.props.StringProperty(name = "commit")
        bpy.app.handlers.load_post.append(GitPanel.file_handler)
        bpy.app.handlers.save_post.append(GitPanel.file_handler)
    
    def unregister():
        #del bpy.types.Scene.git
        pass
     
    def draw(self, context):
        
        layout = self.layout
        
#        row = layout.row(align=True)
#        row.prop(context.scene, "workdir", text = "Working Directory")
#        props = row.operator("buttons.directory_browse", text = "", icon = 'FILE_FOLDER')
#        props["filepath"] = context.scene.workdir
#        layout.operator("git.status")
#        
#        row = layout.row(align=True)
#        row.prop(context.scene, "repo", text = "Repository Path")
#        props = row.operator("buttons.directory_browse", text = "", icon = 'FILE_FOLDER')
#        props["filepath"] = context.scene.repo
#        layout.operator("git.init")
#        
#        row = layout.row(align=True)
#        row.prop(context.scene, "file", text = "File to add")
#        props = row.operator("buttons.file_browse", text = "", icon = 'FILESEL')
#        props["filepath"] = context.scene.file
#        layout.operator("git.add")
        
#        row = layout.row(align=True)
#        row.prop(context.scene, "file", text = "File to commit")
#        props = row.operator("buttons.file_browse", text = "", icon = 'FILESEL')
#        props["filepath"] = context.scene.file
        
        if context.scene.git.file == "":
            layout.label("Save file to enable Git versioning")
            return 
        
        if len(context.scene.git.history) != 0:    
            layout.label("Branches")
        
            layout.prop(context.scene.git, "branch", text = "Branch")
            layout.prop(context.scene.git, "add_branch_name", text = "New Branch")
            layout.operator("git.branch_add")
        
            layout.prop(context.scene.git, "delete_branch", text = "Branch To Delete")
            layout.operator("git.branch_delete")
        
            layout.prop(context.scene.git, "merge_branch", text = "Incoming Branch")
            layout.prop(context.scene.git, "merge_strategy", text = "Merge Strategy")
            layout.prop(context.scene.git, "merge_msg", text = "Message")
            layout.operator("git.merge")
        
            layout.separator()
        
        layout.label("History")
        layout.template_list("UI_UL_list", "history", context.scene.git, "history", context.scene.git, "active_entry" , rows = 5)
        
        if len(context.scene.git.history) != 0:
            layout.operator("git.update")
        
        layout.prop(context.scene.git, "msg", text = "Message")        
        layout.operator("git.commit")
            
            #layout.operator("git.reset") need to unload file first ?
        
    @persistent
    def file_handler(dummy):
        print("File Handler:", bpy.data.filepath)
        currentfile = bpy.path.basename(bpy.data.filepath)
        currentdir = bpy.path.abspath("//")
        
        bpy.context.scene.git.workdir = currentdir        
        bpy.context.scene.git.file = currentfile
        
        bpy.ops.git.branches_list()
        
        if currentdir != "" and currentfile != "":
            bpy.ops.git.log()