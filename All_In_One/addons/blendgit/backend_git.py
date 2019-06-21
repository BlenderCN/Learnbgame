import subprocess
import os
import shutil
import platform

#find/set path to git
#error feedback -> process show stdout
#class structure:
#GitRepo, Git, 
#current file committen, current file updaten

#git command class
class Git():
    def __init__(self, work):
        
        if platform.architecture()[1] == "WindowsPE":
            #assume default git path for windows here, since we dont have winreg access via integrated python
            if platform.architecture()[0] == "64bit":
                self.git = "C://Program Files (x86)//Git//bin//git.exe"
                
            elif platform.architecture()[0] == "32bit":
                self.git = "C://Program Files//Git//bin//git.exe"
        else: #Linux, Mac
            self.git = "/usr/bin/git"
            
        self.work = work
        os.chdir(self.work)
        
    # Getting and Creating Projects 
    def init(self):
        return self.command("init", [self.work])
        
    def clone(self, repo):
        return self.command("clone", [repo])

    # Basic Snapshotting
    
    def add(self, file):
        return self.command("add", [file])
    
    def status(self, file):
        return self.command("status", [file])
    
    #def diff(self):
    #    pass    
    
    def commit(self, file, message):           
        return self.command("commit", ['-m', message, file])
    
    def reset(self, file):
        return self.command("reset", ['--hard', file])
    
    def rm(self, file):
        return self.command("rm", [file])
    
    def mv(self, file, dst):
        return self.command("mv", [file, dst])
        
    def revert(self, file, revision):
        return self.command("revert", [file, revision]) 
        
   
    #Branching and Merging 
    def branch(self, branch, mode):
        if mode == "LIST":
            return self.command("branch", [])
        if mode == "ADD":
            return self.command("branch", [branch])
        if mode == "DELETE":
            return self.command("branch", ['-d', branch])   
    
    def checkout(self, branch):
        return self.command("checkout", [branch])
    
    def log(self, file):
        return self.command("log", [file]) 
    
    def merge(self, branch, strategy, message):
        return self.command("merge", ['-X', strategy, '-m', message, branch])

#    def tag(self):
#        pass

    # Update workdir file with specific version
    
    def update(self, file, path,  commit):
        outRaw = self.command("ls-tree", [commit])
        out = outRaw.decode("utf-8")
        blobnr = self.blobnr(out, file)
        if blobnr != None:
            blob = self.command("cat-file", ["blob", blobnr])
            tmp = open(path + file, "wb+")
            tmp.write(blob)
            tmp.close()
        
    
    def blobnr(self, commitdata, file):
        lines = commitdata.split("\n")
       # print("L", lines)
        for l in lines:
            tab = l.split("\t")
            name = tab[1]
            blob = tab[0].split(" ")[1]
            blobnr = tab[0].split(" ")[2]
            #print("R", records)
            
            if "blob" == blob and file == name:
                return blobnr
        return None
                    
  
    # Sharing and Updating Projects
#    
#    def fetch(self):
#        pass
#    
#    def push(self):
#        pass
#    
#    def pull(self):
#        pass
#   
#    def remote(self):
#        pass
        
    # Miscellaneous
    
    def ignore(self, file, asPattern):
        os.chdir(self.work)
        ig = open(".gitignore", "a+")
        if asPattern:
            ig.write(file + "\n")
        else:
            ig.write("!" + file + "\n")
        ig.close()
#        
#    def show(self)
#        pass
#    
#    def rebase(self)
#        pass
#    
#    def grep(self)
#        pass
#    
#    def bisect(self)
#        pass
    
    #generic Git command with textual feedback  
          
    def command(self, cmd, args): 
        p = subprocess.Popen([self.git, cmd] + args,
            stdout = subprocess.PIPE, 
            stderr = subprocess.STDOUT)
        return p.stdout.read()