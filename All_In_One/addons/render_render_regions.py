# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import os,subprocess

bl_info = {
    'name': 'Render Regions',
    'author': 'Marco Crippa <thekrypt77@tiscali.it>',
    'version': (0,1),
    'blender': (2, 5, 7),
    'location': 'Render > Render Regions',
    'warning': 'beta release',
    'description': 'Divide render into blocks, render each block and try to merge them into a single image.',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Render'}

scn = bpy.types.Scene

#all properties for the gui in the panel

scn.RR_reg_columns = bpy.props.IntProperty(
    name = "Columns",
    description = "Set number of columns",
    default = 1,
    min = 1,
    max = 100)

scn.RR_reg_rows = bpy.props.IntProperty(
    name = "Rows",
    description = "Set number of rows",
    default = 1,
    min = 1,
    max = 100)

scn.RR_multiplier = bpy.props.IntProperty(
    name = "Multiplier",
    description = "Set number of tiles",
    default = 1,
    min = 1,
    max = 100)

scn.RR_dim_region = bpy.props.BoolProperty(name = "Use render dimension",
    description = "Use render dimension for each region",
    default = False)

scn.RR_who_region = bpy.props.StringProperty(name = "Select regions",
    description = "Select regions: all= render all regions; x , y , z= render the region number x, y and z; x - z= render the region from number x to z",
    default = "all")

scn.RR_save_region = bpy.props.BoolProperty(name = "Join and save",
    description = "Join and save the regions",
    default = True)

def RENDER_PT_Region(self, context):
        layout = self.layout
        scn = context.scene
        
        label_save="use Compositing Nodes"
        
        box = layout.box()
        row0 = box.row(align=True)
        row1 = box.row(align=True)
        row2 = box.row(align=True)
        row3 = box.row(align=True)
        row4 = box.row(align=True)
        row5 = box.row(align=True)
        row6 = box.row(align=True)

        row0.label(text="Render Regions Setting:")
        row1.prop(scn, "RR_reg_rows")
        row1.prop(scn, "RR_reg_columns")

        row2.prop(scn, "RR_dim_region")
        sub = row2.row()
        sub.active = scn.RR_dim_region
        sub.enabled = scn.RR_dim_region
        sub.prop(scn, "RR_multiplier")

        row3.prop(scn, "RR_who_region")

        if (scn.RR_dim_region==True):
            row1.active=False
            row1.enabled=False
            label_save="use ImageMagick"

        row4.prop(scn, "RR_save_region")
        
        row4.label(text=label_save)
        
        row5.operator("render.regions", text="Regions", icon="RENDER_REGION")
        

class RenderRegions(bpy.types.Operator):
    bl_idname = 'render.regions'
    bl_label = "Render regions"
    bl_description = "Start render regions - Shortcut Ctrl Shift F12"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        rnd = context.scene.render

        file_name=os.path.splitext( os.path.split(bpy.data.filepath)[1])[0]

        if scn.RR_dim_region==False:
            delta_x = 1/scn.RR_reg_columns
            delta_y = 1/scn.RR_reg_rows
        else:
            delta_x = 1/scn.RR_multiplier
            delta_y = 1/scn.RR_multiplier

        min_x = 0
        max_x = delta_x

        min_y = 0
        max_y = delta_y
        
        old_percentage=rnd.resolution_percentage

        rnd.use_border = 1
        
        dir_output=bpy.path.abspath(rnd.filepath)
        
        name_new_scn="JoinRegions"

        images=[]        
#        list of regions to render
        reg=[]
        
        if scn.RR_dim_region==False:
            tot_reg=scn.RR_reg_columns*scn.RR_reg_rows
            num_cols=scn.RR_reg_columns
        else:
            tot_reg=scn.RR_multiplier*scn.RR_multiplier
            num_cols=scn.RR_multiplier

        if "all" in scn.RR_who_region:
            for a in range(0,(tot_reg)):
                reg.append(a)
            print ("Regions to render:")
            print (reg)
        elif "," in scn.RR_who_region:
            control=scn.RR_who_region.replace(',','')
            if (control.isdigit()):
                reg_temp=scn.RR_who_region.split(",")
                for a in range(0,len(reg_temp)):
                    reg.append(int(reg_temp[a]))
                print ("Regions to render:")
                print (reg)
            else:
                reg=""
        elif "-" in scn.RR_who_region:
            control=scn.RR_who_region.replace('-','')
            if (control.isdigit()):
                reg_temp=scn.RR_who_region.split("-")
                for a in range(int(reg_temp[0]),int(reg_temp[1])+1):
                    reg.append(a)
                print ("Regions to render:")
                print (reg)
            else:
                reg=""
        elif scn.RR_who_region.isdigit():
            reg.append(int(scn.RR_who_region))
            print ("Regions to render:")
            print (reg)
        
        else:
            reg=""
        
        if reg!="":

            for x in range (0, len(reg)):
            
                if int(reg[x])<tot_reg:

                    #set row position
                    pos_row=int(reg[x]/num_cols)
                    #set column position
                    pos_col=int( ( reg[x] - ( pos_row*num_cols) ) )
                    
                    rnd.border_min_x=min_x+(delta_x*pos_col)
                    rnd.border_max_x=max_x+(delta_x*pos_col)
                    rnd.border_min_y=min_y+(delta_y*pos_row)
                    rnd.border_max_y=max_y+(delta_y*pos_row)

                    if pos_row<10:
                        n_row="00"+str(pos_row)
                    elif 10<=pos_row<100:
                        n_row="0"+str(pos_row)
                    else:                
                        n_row=str(pos_row)

                    if pos_col<10:
                        n_col="00"+str(pos_col)
                    elif 10<=pos_col<100:
                        n_col="0"+str(pos_col)
                    else:                
                        n_col=str(pos_col)

                    region_name = file_name + "_" + n_row + "_" + n_col + rnd.file_extension

                    rnd.filepath=dir_output+region_name
                    
                    images.append([region_name, rnd.filepath])
                    
                    if (scn.RR_dim_region==True):
                        rnd.resolution_percentage=scn.RR_multiplier*100
                        rnd.use_crop_to_border = 1
                    print("***************************")
                    print("Start render region number "+str(reg[x]))
                    print(region_name)
                    print(reg[x]," - ",pos_row," - ",pos_col)
                    print (rnd.border_min_x," - ",rnd.border_max_x," - ",rnd.border_min_y," - ",rnd.border_max_y)

                    bpy.ops.render.render(write_still=True)

                    print("Finish render region number "+str(reg[x]))
                    print("***************************")
                    
                else:
                    pass

            #create new scene to join regions
            if scn.RR_save_region==True and scn.RR_who_region=="all":
                print("Create new scene to merge regions....")
                if scn.RR_dim_region==False and rnd.use_crop_to_border==0:

                    if name_new_scn in bpy.data.scenes.keys():
                        new_scn = context.scene
                        tree = new_scn.node_tree
                    else:
                        bpy.ops.scene.new(type='NEW')
                        new_scn = context.scene
                        new_scn.name="JoinRegions"
                        new_scn.use_nodes=True
                        tree = new_scn.node_tree

                    for n in tree.nodes:
                        tree.nodes.remove(n)

                    prev_node=""
                    links = tree.links

                    prev_node=tree.nodes.new("IMAGE")
                    prev_node.location = 0,0
                    img=bpy.data.images.load(images[0][1])
                    prev_node.image=img

                    for a in range (1,len(images)):

                        im01 = tree.nodes.new("IMAGE")
                        im01.location = 100*a,-200*a
                        load_img=bpy.data.images.load(images[a][1])
                        im01.image=load_img
                    
                        ao = tree.nodes.new("ALPHAOVER")
                        ao.location = 200*a,-100*a
                        ao.use_premultiply=True

                        link0 = links.new(prev_node.outputs[0],ao.inputs[1])
                        link1 = links.new(im01.outputs[0],ao.inputs[2])

                        prev_node=ao

                    
                    vw = tree.nodes.new("VIEWER")
                    vw.location = 500,0

                    comp = tree.nodes.new("COMPOSITE")
                    comp.location = 700,200

                    of = tree.nodes.new("OUTPUT_FILE")
                    of.location = 900,400
                    if file_name=="":
                        file_name="untitled"
                    of.filepath = dir_output + file_name
                    of.image_type = "PNG"
                    of.quality = 100

                    link2 = links.new(prev_node.outputs[0],vw.inputs[0])
                    link3 = links.new(prev_node.outputs[0],of.inputs[0])
                    link4 = links.new(prev_node.outputs[0],comp.inputs[0])
                
                    #save joined regions 
                    bpy.ops.render.render()
                    print("Saved "+dir_output + file_name+rnd.file_extension)
                
                else:
                    #save with ImageMagick the big render
                    try:
                        num_img=0
                        seq_img=""
                        seq_row=""
                        all_rows=[]

                        if scn.RR_dim_region==True:
                            num_row=scn.RR_multiplier
                            num_col=scn.RR_multiplier
                        else:
                            num_row=scn.RR_reg_rows
                            num_col=scn.RR_reg_columns
                        
#                        for r in range (0, scn.RR_multiplier):
#                            for c in range (0, scn.RR_multiplier):
                        for r in range (0, num_row):
                            for c in range (0, num_col):
                                seq_img=seq_img+images[num_img][1]+" "
                                num_img=num_img+1
                            img_row=dir_output+file_name+"_row"+str(r)+rnd.file_extension
                            all_rows.append(img_row)
                            cmd="convert "+seq_img+"+append "+img_row
                            print("Saved "+img_row)
                            subprocess.call(cmd, shell=True)
                            seq_img=""
                            
                        for x in reversed(range(len(all_rows))):
                            seq_row=seq_row+all_rows[x]+" "
                        final_img=dir_output+file_name+"_final"+rnd.file_extension
                        cmd="convert "+seq_row+"-append "+final_img
                        subprocess.call(cmd, shell=True)
                        print("Saved "+final_img)
                    except:
                        print ("Imagemagik is not installed")

#            reset variables
        rnd.filepath=dir_output
        rnd.resolution_percentage=old_percentage

        return{'FINISHED'}
         
def menu_func(self, context):
    self.layout.menu("RENDER_MT_menuPreset", text=bpy.types.RENDER_MT_menuPreset.bl_label)

# define classes for registration
classes = [
    RenderRegions
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.RENDER_PT_render.append(RENDER_PT_Region)

    kc = bpy.context.window_manager.keyconfigs['Blender']
    km = kc.keymaps.get("Screen")
    kmi = km.keymap_items.new('render.regions', 'F12', 'PRESS', ctrl=True, shift=True)
    
    
def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    bpy.types.RENDER_PT_render.remove(RENDER_PT_Region)

    kms = bpy.context.window_manager.keyconfigs['Blender'].keymaps['Screen']
    for kmi in kms.keymap_items:
        if kmi.idname == 'render.regions':
            kms.keymap_items.remove(kmi)
    
if __name__ == "__main__":
    register()

