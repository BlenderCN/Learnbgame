import bpy
import os
from bpy_extras.io_utils import ImportHelper
import math


bl_info = {
    "name": "Batch Render Tools",
    "author": "Ray Mairlot",
    "version": (0, 6, 0),
    "blender": (2, 77, 0),
    "location": "Properties > Render > Batch Render Tools",
    "description": "A series of tools to help with managing batch renders",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
    }


###############UPDATE FUNCTIONS#################################################################################



def testValidBlend(self, context):
    
    self.valid_path = False
    
    if os.path.isfile(self.filepath):
        
        self.valid_path = True
                
                
                
def calculateFrameStart(self, context):
    
    if self.start > self.end:
        
        self.end = self.start
        


def calculateFrameEnd(self, context):
    
    if self.end < self.start:
        
        self.start = self.end
        


###############PROPERTIES#######################################################################################



class batchJobsPropertiesGroup(bpy.types.PropertyGroup):
    
    start = bpy.props.IntProperty(description="Frame to start rendering from", update=calculateFrameStart)
    
    end = bpy.props.IntProperty(description="Frame to render to", update=calculateFrameEnd)

    expanded = bpy.props.BoolProperty(default=True)
    
    render_options_expanded = bpy.props.BoolProperty(default=False)
    
    filepath = bpy.props.StringProperty(description="Location of the blend file to render", update=testValidBlend)
    
    frame_range_from_file = bpy.props.BoolProperty(default=False, name="Frame range from file", description="Use the frame range set in the file")

    output_path_from_file = bpy.props.BoolProperty(default=True, name="Output path from file", description="Use the output path set in the file")
    
    name = bpy.props.StringProperty(description="Name of the render job")
    
    render = bpy.props.BoolProperty(default=True, description="Include this job when 'Run batch render' is pressed")
    
    valid_path = bpy.props.BoolProperty(default=False)
    
    output_filepath = bpy.props.StringProperty(description="Output filepath where renders will be saved", subtype="FILE_PATH")
        


class batchRenderToolsPropertiesGroup(bpy.types.PropertyGroup):

    copy_blendfile_path = bpy.props.BoolProperty(default=True, description="Copy the current blend file's path to the clipboard")

    background = bpy.props.BoolProperty(default=True, description="Copied path has 'background' (-b) command")

    batch_jobs = bpy.props.CollectionProperty(type=batchJobsPropertiesGroup)

    hibernate = bpy.props.BoolProperty(default=False, name="Hibernate", description="Hibernate the computer after rendering (Windows only)")
    
    summary_expanded = bpy.props.BoolProperty(default=True)
    
    

######################FUNCTIONS#################################################################################



def openCommandPrompt(context):

    binaryPath = os.path.split(bpy.app.binary_path)[0]

    binaryPath = binaryPath.replace('\\', '/' )

    os.system("start cmd /K cd "+binaryPath)
    
    if context.scene.batch_render_tools.copy_blendfile_path:
        
        blenderCommand = ""
        
        if context.scene.batch_render_tools.background:
            
            blenderCommand = "blender -b "
            
        context.window_manager.clipboard = blenderCommand+'"'+bpy.data.filepath+'" '
        
        

def runBatchRender(context):
                
    command = compileCommand()    
    
    hibernate = ""
    if context.scene.batch_render_tools.hibernate and str(bpy.app.build_platform) == "b'Windows'":
        hibernate = " && shutdown -h"
    
    #Running the command directly requires an extra set of quotes around the command, batch does not
    command = 'start cmd /k " "' + command + hibernate + '"'
    command.replace('\\','/')
    print(command)
    os.system(command)
                                                 
        

def compileCommand():
            
    command = bpy.app.binary_path + '" -b '
    
    batchJobs = [batchJob for batchJob in bpy.context.scene.batch_render_tools.batch_jobs if batchJob.render]
    
    for batchJob in batchJobs:
        
        frameRange = ""
        
        if not batchJob.frame_range_from_file:    
            
            frameRange = ' -s ' + str(batchJob.start) + ' -e ' + str(batchJob.end)
            
        outputPath = ""
        
        if not batchJob.output_path_from_file:    
            
            outputPath = ' -o ' + '"' + batchJob.output_filepath + '"'
        
        frameStep = ''
        
        if bpy.context.scene.frame_step != 1:
        
            frameStep = ' -j ' + str(bpy.context.scene.frame_step)
        
        command += '"' + batchJob.filepath + '"' + frameRange + outputPath + frameStep + ' -a ' 

    return command



def writeBatchFile(fileName, fileContent):
    
    batFile = open(fileName, 'w')
    
    for command in fileContent:
            
        batFile.write(command)
        batFile.write("\n")
        batFile.write("\n")
        
    batFile.close()    



def batchJobAdd(self, context, filepath="", blenderFile=""):
    
    newBatchJob = context.scene.batch_render_tools.batch_jobs.add()
    newBatchJob.name = "Batch Job " + str(len(context.scene.batch_render_tools.batch_jobs))
    newBatchJob.start = context.scene.frame_start
    newBatchJob.end = context.scene.frame_end
    
    if filepath == "":
    
        newBatchJob.filepath = bpy.data.filepath
        newBatchJob.name = "Batch Job " + str(len(context.scene.batch_render_tools.batch_jobs))
    
    else:
        
        newBatchJob.filepath = os.path.join(filepath, blenderFile)
        newBatchJob.frame_range_from_file = self.frame_range_from_file
        newBatchJob.name = blenderFile
        
        
    
def batchJobRemove(self, context):
    
    context.scene.batch_render_tools.batch_jobs.remove(self.index)
    
    for index, batchJob in enumerate(context.scene.batch_render_tools.batch_jobs):
        
        batchJob.index = index
            
        
        
def batchJobMove(self, context):
    
    if self.direction == "Up":    
        
        context.scene.batch_render_tools.batch_jobs.move(self.index, self.index - 1)

    elif self.direction == "Down":
     
        context.scene.batch_render_tools.batch_jobs.move(self.index, self.index + 1)
        

        
def batchJobCopy(self, context):
    
    newBatchJob = context.scene.batch_render_tools.batch_jobs.add()
    
    for property in context.scene.batch_render_tools.batch_jobs[self.index].items():
        
        newBatchJob[property[0]] = property[1]
        
    newBatchJob.name = "Batch Job " + str(len(context.scene.batch_render_tools.batch_jobs))
            
             
        
def batchJobDeleteAll(self, context):
        
    context.scene.batch_render_tools.batch_jobs.clear()    
    
    
    
def batchJobExpandAll(self, context):
            
    for batchJob in context.scene.batch_render_tools.batch_jobs:
        
        batchJob.expanded = self.expand



def batchJobsFromDirectory(self, context):
    
    filepath = self.filepath
        
    if os.path.isfile(filepath):
        
        filepath = os.path.split(filepath)[0]    
    
    
    blendFiles = [file for file in os.listdir(filepath) if os.path.splitext(file)[1] == ".blend"]
    
    for blenderFile in blendFiles:
        
        batchJobAdd(self, context, filepath, blenderFile)
    
        
        
def selectBlendFile(self, context):
            
    context.scene.batch_render_tools.batch_jobs[self.index].filepath = self.filepath  
        
        
        
def batchJobConvertToBatchFile(self, context):
    
    command = compileCommand()
    command = 'CALL "' + command
    fileName = self.filepath
    
    print(fileName)
    
    commands = []
    commands.append(command)
    
    if context.scene.batch_render_tools.hibernate:
    
        commands.append("shutdown -h")
                
    writeBatchFile(fileName, commands)


                        
###############UI###############################################################################################



class BatchJobsMenu(bpy.types.Menu):
    bl_label = "Batch Jobs Menu"
    bl_idname = "RENDER_MT_batch_jobs"

    def draw(self, context):
        layout = self.layout

        layout.operator("batch_render_tools.expand_all_batch_jobs", text="Expand all batch jobs", icon="TRIA_DOWN_BAR").expand = True
        layout.operator("batch_render_tools.expand_all_batch_jobs", text="Collapse all batch jobs", icon="TRIA_UP_BAR").expand = False
        layout.operator("batch_render_tools.convert_jobs_to_batch_file", text="Generate .bat file", icon="LINENUMBERS_ON")
        layout.operator("batch_render_tools.batch_jobs_from_directory", text="Batch jobs from directory", icon="FILESEL")
        layout.operator("batch_render_tools.delete_all_batch_jobs", icon="X")



class CommandPromptToolsPanel(bpy.types.Panel):
    """Creates a Panel in the render properties window"""
    bl_label = "Command Prompt Tools"
    bl_idname = "RENDER_PT_command_prompt_tools"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    
    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("batch_render_tools.browse_to_blend", icon="CONSOLE")
        row = layout.row()
        row.enabled = bpy.data.filepath != ""
        row.prop(context.scene.batch_render_tools, "copy_blendfile_path", text="Copy path")
        col = row.column()
        col.enabled = context.scene.batch_render_tools.copy_blendfile_path
        col.prop(context.scene.batch_render_tools, "background", text="Background")
    


class BatchRenderToolsPanel(bpy.types.Panel):
    """Creates a Panel in the render properties window"""
    bl_label = "Batch Render Tools"
    bl_idname = "RENDER_PT_batch_render_tools"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator("batch_render_tools.run_batch_render", icon="RENDER_ANIMATION")
        
        if len([batchJob for batchJob in context.scene.batch_render_tools.batch_jobs if not batchJob.valid_path and batchJob.render]) > 0:
            
            row = layout.row()
            row.label(text="There are batch jobs with invalid filepaths", icon="ERROR")
            
        elif len([batchJob for batchJob in context.scene.batch_render_tools.batch_jobs if batchJob.render]) < 1:
            
            row = layout.row()
            row.label(text="There are no batch jobs set to render", icon="INFO")
        
        row = layout.row()
        row.enabled = str(bpy.app.build_platform) == "b'Windows'"
        row.prop(context.scene.batch_render_tools, "hibernate")
        
        box = layout.box()
        
        row = box.row()
        summaryExpandedIcon = "TRIA_RIGHT"
        if context.scene.batch_render_tools.summary_expanded:
            summaryExpandedIcon = "TRIA_DOWN"
        row.prop(context.scene.batch_render_tools, "summary_expanded", text="", icon=summaryExpandedIcon, emboss=False)
        row.label(text="Batch Jobs summary:")
        
        if context.scene.batch_render_tools.summary_expanded:
        
            row = box.row()
            row.label("Number of batch jobs: "+str(len(context.scene.batch_render_tools.batch_jobs)), icon="LINENUMBERS_ON")
            
            row = box.row()
            row.label("Number of batch jobs to render: "+str(len([batchJob for batchJob in context.scene.batch_render_tools.batch_jobs if batchJob.render])), icon="SCENE")
            
            frames = 0
            for batchJob in context.scene.batch_render_tools.batch_jobs:
                
                if batchJob.render:
                                
                    if batchJob.end == batchJob.start:
                        
                        frames += 1
                        
                    else:           
                        
                        frameRange = batchJob.end - batchJob.start
                    
                        if frameRange == context.scene.frame_step:
                            
                            frames += 2
                            
                        else:
                            
                            frameRange += 1
                            
                            frames += math.ceil(frameRange / context.scene.frame_step)
            
            row = box.row()    
            row.label("Number of frames to render: "+str(frames), icon="IMAGE_DATA")
        
        row = layout.row()
        row.label(text="Manage Batch Jobs:")
        
        row = layout.row(align=True)
        row.operator("batch_render_tools.add_batch_job", icon="ZOOMIN")
        row.menu(BatchJobsMenu.bl_idname, text="", icon="DOWNARROW_HLT")
                
        for index, batchJob in enumerate(context.scene.batch_render_tools.batch_jobs):
            
            column = layout.column(align=True)
            box = column.box()
                        
            expandedIcon = "TRIA_RIGHT"
            if batchJob.expanded:
                expandedIcon = "TRIA_DOWN"
            row = box.row(align=True)
            row.prop(batchJob, "expanded", text="", emboss=False, icon=expandedIcon)
            row.prop(batchJob, "name", text="")
            
            row.separator()
            
            row.prop(batchJob, "render", text="", icon="RESTRICT_RENDER_OFF")
            row.operator("batch_render_tools.copy_batch_job", text="", icon="GHOST").index = index
            
            row.separator()
                            
            operator = row.operator("batch_render_tools.move_batch_job", text="", icon="TRIA_UP")
            operator.direction = "Up"
            operator.index = index             
            operator = row.operator("batch_render_tools.move_batch_job", text="", icon="TRIA_DOWN")
            operator.direction = "Down" 
            operator.index = index
            
            row.separator()
            
            row.operator("batch_render_tools.remove_batch_job", text="", emboss=False, icon="X").index = index
                        
            if batchJob.expanded:

                box = column.box()
                row = box.row(align=True)
                row.prop(batchJob, "filepath", text="")
                row.operator("batch_render_tools.select_blend_file", text="", icon="FILESEL").index = index
                
                if not batchJob.valid_path:
                    row = box.row()
                    row.label(text="Blend file doesn't exist", icon="ERROR")
                
                
                row = box.row()
                row.prop(batchJob, "frame_range_from_file")
                                            
                row = box.row(align=True)
                row.enabled = not batchJob.frame_range_from_file
                                
                row.prop(batchJob, "start")
                row.prop(batchJob, "end")
                
                
                box = box.box()
                row = box.row()
                
                expandedIcon = "TRIA_RIGHT"
                if batchJob.render_options_expanded:
                    expandedIcon = "TRIA_DOWN"
                row.prop(batchJob, "render_options_expanded", text="", emboss=False, icon=expandedIcon)
                row.label("Render Options")
                
                if batchJob.render_options_expanded:
                                    
                    row = box.row()
                    row.prop(batchJob, "output_path_from_file")
                    
                    row = box.row()
                    row.enabled = not batchJob.output_path_from_file
                      
                    row.prop(batchJob, "output_filepath", text="Output")
            
            

###############OPERATORS########################################################################################

                        

class BatchJobsFromDirectoryOperator(bpy.types.Operator, ImportHelper):
    """Generate batch jobs from a folder of blends you want to render"""    
    bl_idname = "batch_render_tools.batch_jobs_from_directory"
    bl_label = "Select directory"


    filter_glob = bpy.props.StringProperty(default="*.blend",options={'HIDDEN'})
    
    filename = bpy.props.StringProperty(default="")
    
    frame_range_from_file = bpy.props.BoolProperty(default=False, name="Frame ranges from files") 
                
            
    def execute(self, context):
        
        batchJobsFromDirectory(self, context)
        
        return {'FINISHED'}
    
    
    def invoke(self, context, event):
        
        self.filename = ""
        
        context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}
    
    
    
class SelectBlendFileOperator(bpy.types.Operator, ImportHelper):
    """Select the blend file for this batch job"""
    bl_idname = "batch_render_tools.select_blend_file"
    bl_label = "Select blend file"

    index = bpy.props.IntProperty(options={'HIDDEN'})

    filter_glob = bpy.props.StringProperty(default="*.blend",options={'HIDDEN'})
                       
    def execute(self, context):
        
        selectBlendFile(self, context)
        
        return {'FINISHED'}
    
    
    def invoke(self, context, event):
                
        context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}    
    

    
class BatchJobsConvertToBatchFileOperator(bpy.types.Operator, ImportHelper):
    """Convert the batch jobs to a Windows Batch (.bat) file"""
    bl_idname = "batch_render_tools.convert_jobs_to_batch_file"
    bl_label = "Generate .bat file from batch jobs"


    filename = bpy.props.StringProperty(default="")

    filter_glob = bpy.props.StringProperty(default="*.bat",options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        return len(context.scene.batch_render_tools.batch_jobs) > 0
        
        
    def execute(self, context):
                        
        batchJobConvertToBatchFile(self, context)
        
        return {'FINISHED'}
    
    
    def invoke(self, context, event):
        
        self.filename = "batchRender.bat"
        
        context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}
    
   

class OpenCommandPromptOperator(bpy.types.Operator):
    """Open an empty Command Prompt Window"""
    bl_idname = "batch_render_tools.browse_to_blend"
    bl_label = "Open Command Prompt"


    def execute(self, context):
        openCommandPrompt(context)
        return {'FINISHED'}
    
    

class BatchRenderOperator(bpy.types.Operator):
    """Run the batch render"""
    bl_idname = "batch_render_tools.run_batch_render"
    bl_label = "Run batch render"


    @classmethod
    def poll(cls, context):
        #There are batch jobs to render
        #There are no batch jobs to render that have invalid paths
        return len([batchJob for batchJob in context.scene.batch_render_tools.batch_jobs if batchJob.render]) > 0 \
           and len([batchJob for batchJob in context.scene.batch_render_tools.batch_jobs if not batchJob.valid_path and batchJob.render]) == 0


    def execute(self, context):
        runBatchRender(context)
        return {'FINISHED'}
    
    
    
class BatchJobRemoveOperator(bpy.types.Operator):
    """Add a new batch render job"""
    bl_idname = "batch_render_tools.add_batch_job"
    bl_label = "Add batch render job"


    def execute(self, context):
        batchJobAdd(self, context)
        return {'FINISHED'}  

    
    
class BatchJobRemoveOperator(bpy.types.Operator):
    """Remove the selected batch render job"""
    bl_idname = "batch_render_tools.remove_batch_job"
    bl_label = "Remove batch render job"

    index = bpy.props.IntProperty()

    def execute(self, context):
        batchJobRemove(self, context)
        return {'FINISHED'}  
     
     
         
class BatchJobMoveOperator(bpy.types.Operator):
    """Move the selected batch render job up or down"""
    bl_idname = "batch_render_tools.move_batch_job"
    bl_label = "Move batch render job"

    index = bpy.props.IntProperty()
    direction = bpy.props.StringProperty(default="Up")

    def execute(self, context):
        batchJobMove(self, context)
        return {'FINISHED'}    
    
    
    
class BatchJobCopyOperator(bpy.types.Operator):
    """Copy the selected batch render"""
    bl_idname = "batch_render_tools.copy_batch_job"
    bl_label = "Copy the batch render job"
    
    index = bpy.props.IntProperty()
    
    def execute(self, context):
        batchJobCopy(self, context)
        return {'FINISHED'}  
    
    
    
class BatchJobDeleteAllOperator(bpy.types.Operator):
    """Delete all the batch render jobs"""
    bl_idname = "batch_render_tools.delete_all_batch_jobs"
    bl_label = "Delete all batch jobs"
    
    @classmethod
    def poll(cls, context):
        return len(context.scene.batch_render_tools.batch_jobs) > 0
               
        
    def execute(self, context):
        batchJobDeleteAll(self, context)
        return {'FINISHED'}   
    
    
    
class BatchJobExpandAllOperator(bpy.types.Operator):
    """Expand/collapse all the batch render jobs"""
    bl_idname = "batch_render_tools.expand_all_batch_jobs"
    bl_label = "Delete all batch jobs"
    
    expand = bpy.props.BoolProperty()
    
    @classmethod
    def poll(cls, context):
        return len(context.scene.batch_render_tools.batch_jobs) > 0

        
    def execute(self, context):
        batchJobExpandAll(self, context)
        return {'FINISHED'}   
    
    
                                        
def register():

    bpy.utils.register_class(batchJobsPropertiesGroup)
    bpy.utils.register_class(batchRenderToolsPropertiesGroup)
    
    bpy.types.Scene.batch_render_tools = bpy.props.PointerProperty(type=batchRenderToolsPropertiesGroup)

    bpy.utils.register_module(__name__)



def unregister():
        
    bpy.utils.unregister_class(batchRenderToolsPropertiesGroup)
    bpy.utils.unregister_class(batchJobsPropertiesGroup)
    
    del bpy.types.Scene.batch_render_tools
    
    bpy.utils.unregister_module(__name__)



if __name__ == "__main__":
    register() 
