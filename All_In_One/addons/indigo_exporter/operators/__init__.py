import os, time
import math
import xml.etree.cElementTree as ET
import xml.dom.minidom as MD

import bpy            #@UnresolvedImport

from ..extensions_framework import util as efutil

from .. import export
from .. export import (
    indigo_log, geometry, include, xml_multichild, xml_builder, indigo_visible,
    SceneIterator, ExportCache, exportutil
)
from .. export.igmesh import igmesh_writer
from .. export.geometry import model_object

from .. import eprofiler as ep

class _Impl_operator(object):
    
    def __init__(self, **kwargs):
        """
        Set member vars via keyword arguments
        """
        for k,v in kwargs.items():
            setattr(self,k,v)
    
    def __getattr__(self, a):
        """
        If using the _Impl* object directly and not as operator,
        allow access to member vars via self.properties the same
        as Operator does.
        """
        if a == 'properties' and a not in self.__dict__.keys():
            return self
        return self.__dict__[a]
    
    def set_report(self, report_func):
        export.REPORTER = report_func
        return self
    
class _Impl_OT_igmesh(_Impl_operator):
    '''Export an Indigo format binary mesh file (.igmesh)'''
    
    bl_idname = "export.igmesh"
    bl_label = "Export IGMESH"
    
    objectname = bpy.props.StringProperty(options={'HIDDEN'}, name="Object Name", default='')
    
    filename = bpy.props.StringProperty(name="File Name", description="File name used for exporting the IGMESH file", maxlen= 1024, default= "")
    directory = bpy.props.StringProperty(name="Directory", description="", maxlen= 1024, default= "")
    filepath = bpy.props.StringProperty(name="File Path", description="File path used for exporting the IGMESH file", maxlen= 1024, default= "")
    
    def execute(self, context):
        if not self.properties.filepath:
            indigo_log('Filename not set', message_type='ERROR')
            return {'CANCELLED'}
        
        if self.properties.objectname == '':
            self.properties.objectname = context.active_object.name
        
        try:
            obj = bpy.data.objects[self.properties.objectname]
        except:
            indigo_log('Cannot find mesh data in context', message_type='ERROR')
            return {'CANCELLED'}
        
        mesh = obj.to_mesh(context.scene, True, 'RENDER')
        igmesh_writer.factory(context.scene, obj, self.properties.filepath, mesh, debug=False)
        bpy.data.meshes.remove(mesh)
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        if self.properties.objectname == '':
            self.properties.objectname = context.active_object.name
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class EXPORT_OT_igmesh(_Impl_OT_igmesh, bpy.types.Operator):
    '''Export an Indigo format binary mesh file (.igmesh)'''
    
    def execute(self, context):
        self.set_report(self.report)
        return super().execute(context)
       
# add igmesh operator into file->export menu
menu_func = lambda self, context: self.layout.operator("export.igmesh", text="Export Indigo Mesh...")
bpy.types.INFO_MT_file_export.append(menu_func)
    
class _Impl_OT_indigo(_Impl_operator):
    '''Export an Indigo format scene (.igs)'''
    
    bl_idname = 'export.indigo'
    bl_label = 'Export Indigo Scene (.igs)'
    
    filename    = bpy.props.StringProperty(name='IGS filename')
    directory    = bpy.props.StringProperty(name='IGS directory')
    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def check_write(self, directory):
        if not os.access(directory, os.W_OK):
            return False
        return True
   
    def check_medium(self, obj):
        pass
        
    def check_output_path(self, path):
        efutil.export_path = efutil.filesystem_path(path)
        
        if not os.path.isdir(efutil.export_path):
            parent_dir = os.path.realpath( os.path.join(efutil.export_path, os.path.pardir) )
            if not self.check_write(parent_dir):
                indigo_log('Output path "%s" is not writable' % parent_dir)
                raise Exception('Output path is not writable')
            
            try:
                os.makedirs(efutil.export_path)
            except: 
                indigo_log('Could not create output path %s' % efutil.export_path)
                raise Exception('Could not create output path')
        
        if not self.check_write(efutil.export_path):
            indigo_log('Output path "%s" is not writable' % efutil.export_path)
            raise Exception('Output path is not writable')
        
        igs_filename = '/'.join( (efutil.export_path, self.properties.filename) )
        
        # indigo_log('Writing to %s'%igs_filename)
        
        if efutil.export_path[-1] not in ('/', '\\'):
            efutil.export_path += '/'
        
        try:
            out_file = open(igs_filename, 'w')
            out_file.close()
        except:
            indigo_log('Failed to open output file "%s" for writing: check output path setting' % igs_filename)
            raise Exception('Failed to open output file for writing: check output path setting')
        
        return igs_filename
        
    # Exports a default background light if no light sources were found in the scene.
    def export_default_background_light(self, have_illumination):
        #------------------------------------------------------------------------------
        # If there is no illumination in the scene, just add in a uniform environment light
        if not have_illumination:
            background_settings = ET.fromstring("""
                <background_settings>
                    <background_material>
                        <material>
                            <name>background_material</name>

                            <diffuse>
                                <base_emission>
                                    <constant>
                                        <rgb>
                                            <rgb>1 1 1</rgb>
                                            <gamma>1</gamma>
                                        </rgb>
                                    </constant>
                                </base_emission>
                            </diffuse>
                        </material>
                    </background_material>

                    <emission_scale>
                        <material_name>background_material</material_name>
                        <measure>luminance</measure>
                        <value>20000</value>
                    </emission_scale>
                </background_settings>
            """)
            
            self.scene_xml.append(background_settings)
            
    # Exports default null and clay materials.
    def export_tonemapping(self, master_scene):
        if self.verbose: indigo_log('Exporting tonemapping')
        self.scene_xml.append(
            master_scene.camera.data.indigo_tonemapping.build_xml_element(master_scene)
        )
            
    # Exports default null and clay materials.
    def export_default_materials(self, master_scene):
        from .. export.materials.Clay import ClayMaterial, NullMaterialDummy as NullMaterial
        self.scene_xml.append(ClayMaterial().build_xml_element(master_scene))
        self.scene_xml.append(NullMaterial().build_xml_element(master_scene))
    
    scene_xml = None
    verbose = True
    
    def execute(self, master_scene):
        try:
            if master_scene is None:
                #indigo_log('Scene context is invalid')
                raise Exception('Scene context is invalid')
            
            #------------------------------------------------------------------------------
            # Init stats
            if self.verbose: indigo_log('Indigo export started ...')
            export_start_time = time.time()
            
            igs_filename = self.check_output_path(self.properties.directory)
            export_scenes = [master_scene.background_set, master_scene]
            
            if self.verbose: indigo_log('Export render settings')
            
            #------------------------------------------------------------------------------
            # Start with render settings, this also creates the root <scene>
            self.scene_xml = master_scene.indigo_engine.build_xml_element(master_scene)
            
            #------------------------------------------------------------------------------
            # Tonemapping
            self.export_tonemapping(master_scene)
            
            #------------------------------------------------------------------------------
            # Materials - always export the default clay material and a null material
            self.export_default_materials(master_scene)
            
            # Initialise values used for motion blur export.
            fps = master_scene.render.fps / master_scene.render.fps_base
            start_frame = master_scene.frame_current
            exposure = 1 / master_scene.camera.data.indigo_camera.exposure
            camera = (master_scene.camera, [])
            
            # Make a relative igs and mesh dir path like "TheAnimation/00002"
            rel_mesh_dir = efutil.scene_filename()
            rel_frame_dir = '%s/%05i' % (rel_mesh_dir, start_frame) #bpy.path.clean_name(master_scene.name), 
            mesh_dir = '/'.join([efutil.export_path, rel_mesh_dir])
            frame_dir = '/'.join([efutil.export_path, rel_frame_dir])
            
            # Initialise GeometryExporter.
            geometry_exporter = geometry.GeometryExporter()
            geometry_exporter.mesh_dir = mesh_dir
            geometry_exporter.rel_mesh_dir = rel_mesh_dir
            geometry_exporter.skip_existing_meshes = master_scene.indigo_engine.skip_existing_meshes
            geometry_exporter.verbose = self.verbose
            
            # Make frame_dir directory if it does not exist yet.
            if not os.path.exists(frame_dir):
                os.makedirs(frame_dir)
            
            if master_scene.indigo_engine.motionblur:
                # When motion blur is on, calculate the number of frames covered by the exposure time
                start_time = start_frame / fps
                end_time = start_time + exposure
                end_frame = math.ceil(end_time * fps)
                
                # end_frame + 1 because range is max excl
                frame_list = [x for x in range(start_frame, end_frame+1)]
            else:
                frame_list = [start_frame]
                
            #indigo_log('frame_list: %s'%frame_list)
            
            #------------------------------------------------------------------------------
            # Process all objects in all frames in all scenes.
            for cur_frame in frame_list:
                # Calculate normalised time for keyframes.
                normalised_time = (cur_frame - start_frame) / fps / exposure
                if self.verbose: indigo_log('Processing frame: %i time: %f'%(cur_frame, normalised_time))
                
                geometry_exporter.normalised_time = normalised_time
                
                if master_scene.indigo_engine.motionblur:
                    bpy.context.scene.frame_set(cur_frame, 0.0) # waaay too slow for many objects (probably dupli_list gets recreated). Obligatory for motion blur.
                else:
                    bpy.context.scene.frame_current = cur_frame # is it enough?

                # Add Camera matrix.
                camera[1].append((normalised_time, camera[0].matrix_world.copy()))
            
                for ex_scene in export_scenes:
                    if ex_scene is None: continue
                    
                    if self.verbose: indigo_log('Processing objects for scene %s' % ex_scene.name)
                    geometry_exporter.iterateScene(ex_scene)
            
            # Export background light if no light exists.
            self.export_default_background_light(geometry_exporter.isLightingValid())

            #------------------------------------------------------------------------------
            # Export camera
            if self.verbose: indigo_log('Exporting camera')
            self.scene_xml.append(
                camera[0].data.indigo_camera.build_xml_element(master_scene, camera[1])
            )
            #------------------------------------------------------------------------------
            # Export light layers
            from .. export.light_layer import light_layer_xml
            # TODO:
            # light_layer_count was supposed to export correct indices when there
            # is a background_set with emitters on light layers -
            # however, the re-indexing at material export time is non-trivial for
            # now and probably not worth it.
            #light_layer_count = 0
            xml_render_settings = self.scene_xml.find('renderer_settings')
            for ex_scene in export_scenes:
                if ex_scene is None: continue
                
                # Light layer names
                lls = ex_scene.indigo_lightlayers.enumerate()
                
                for layer_name, idx in sorted(lls.items(), key=lambda x: x[1]):
                    if self.verbose: indigo_log('Light layer %i: %s' % (idx, layer_name))
                    xml_render_settings.append(
                        light_layer_xml().build_xml_element(ex_scene, idx, layer_name)
                    )
                
            
            if self.verbose: indigo_log('Exporting lamps')
            
            # use special n==1 case due to bug in indigo <sum> material
            num_lamps = len(geometry_exporter.ExportedLamps)
            
            if num_lamps == 1:
                scene_background_settings = ET.Element('background_settings')
                scene_background_settings_mat = ET.Element('background_material')
                scene_background_settings.append(scene_background_settings_mat)
                
                for ck, ci in geometry_exporter.ExportedLamps.items():
                    for xml in ci:
                        scene_background_settings_mat.append(xml)
                
                self.scene_xml.append(scene_background_settings)
            
            if num_lamps > 1:
                
                scene_background_settings = ET.Element('background_settings')
                scene_background_settings_fmt = {
                    'background_material': {
                        'material': {
                            'name': ['background_material'],
                            'sum': { 'mat': xml_multichild() }
                        }
                    }
                }
                
                for ck, ci in geometry_exporter.ExportedLamps.items():
                    for xml in ci:
                        self.scene_xml.append(xml)
                    
                    scene_background_settings_fmt['background_material']['material']['sum']['mat'].append({
                        'mat_name': [ck],
                        'weight': {'constant': [1]}
                    })
                scene_background_settings_obj = xml_builder()
                scene_background_settings_obj.build_subelements(None, scene_background_settings_fmt, scene_background_settings)
                self.scene_xml.append(scene_background_settings)
            
            #------------------------------------------------------------------------------
            # Export Medium
            from .. export.materials.medium import medium_xml
            # TODO:
            # check if medium is currently used by any material and add 
            # basic medium for SpecularMaterial default

            for ex_scene in export_scenes:
                if ex_scene is None: continue
                
                indigo_material_medium = ex_scene.indigo_material_medium
                medium = indigo_material_medium.medium
                
                if len(indigo_material_medium.medium.items()) == 0 : continue
                
                for medium_name, medium_data in medium.items():
                    
                    medium_index = ex_scene.indigo_material_medium.medium.find(medium_name) # more precise if same name
                    
                    indigo_log('Exporting medium: %s ' % (medium_name))
                    self.scene_xml.append(
                        medium_xml(ex_scene, medium_name, medium_index, medium_data).build_xml_element(ex_scene, medium_name, medium_data)
                    )
                indigo_log('Exporting Medium: %s ' % (medium_name))         
                # TODO: 
                # check for unused medium
                # 4294967292 = 1 mesh + 1 material
                # 10200137
            basic_medium = ET.fromstring("""
                                <medium>
                                   <uid>9999</uid>
                                   <name>basic</name>
                                   <precedence>10</precedence>
                                   <basic>
                                      <ior>1.5</ior>
                                      <cauchy_b_coeff>0</cauchy_b_coeff>
                                      <max_extinction_coeff>1</max_extinction_coeff>
                                      <fast_sss>false</fast_sss>
                                      <absorption_coefficient>
                                         <constant>
                                            <uniform>
                                               <value>0</value>
                                            </uniform>
                                         </constant>
                                      </absorption_coefficient>
                                   </basic>
                                </medium>   
                         """)
            
            self.scene_xml.append(basic_medium)
            
            #------------------------------------------------------------------------------
            # Export used materials.
            if self.verbose: indigo_log('Exporting used materials')
            material_count = 0
            for ck, ci in geometry_exporter.ExportedMaterials.items():
                for xml in ci:
                    self.scene_xml.append(xml)
                material_count += 1
            if self.verbose: indigo_log('Exported %i materials' % material_count)
            
            # Export used meshes.
            if self.verbose: indigo_log('Exporting meshes')
            mesh_count = 0
            for ck, ci in geometry_exporter.MeshesOnDisk.items():
                mesh_name, xml = ci
                self.scene_xml.append(xml)
                mesh_count += 1
            if self.verbose: indigo_log('Exported %i meshes' % mesh_count)
            
            #------------------------------------------------------------------------------
            # We write object instances to a separate file
            oc = 0
            scene_data_xml = ET.Element('scenedata')
            for ck, ci in geometry_exporter.ExportedObjects.items():
                obj_type = ci[0]
                
                if obj_type == 'OBJECT':
                    obj = ci[1]
                    mesh_name = ci[2]
                    obj_matrices = ci[3]
                    scene = ci[4]
                    
                    xml = geometry.model_object(scene).build_xml_element(obj, mesh_name, obj_matrices)
                else:
                    xml = ci[1]
                scene_data_xml.append(xml)
                oc += 1
            
            objects_file_name = '%s/objects.igs' % (
                frame_dir
            )
            objects_file = open(objects_file_name, 'wb')
            ET.ElementTree(element=scene_data_xml).write(objects_file, encoding='utf-8')
            objects_file.close()
            # indigo_log('Exported %i object instances to %s' % (oc,objects_file_name))
            scene_data_include = include.xml_include( efutil.path_relative_to_export(objects_file_name) )
            self.scene_xml.append( scene_data_include.build_xml_element(master_scene) )
            
            #------------------------------------------------------------------------------
            # Write formatted XML for settings, materials and meshes
            out_file = open(igs_filename, 'w')
            xml_str = ET.tostring(self.scene_xml, encoding='utf-8').decode()
            
            # substitute back characters protected from entity encoding in CDATA nodes
            xml_str = xml_str.replace('{_LESSTHAN_}', '<')
            xml_str = xml_str.replace('{_GREATERTHAN_}', '>')
            
            
            xml_dom = MD.parseString(xml_str)
            xml_dom.writexml(out_file, addindent='\t', newl='\n', encoding='utf-8')
            out_file.close()
            
            #------------------------------------------------------------------------------
            # Computing devices
            if len(master_scene.indigo_engine.render_devices):
                from .. core.util import getSettingsPath
                settings_file = getSettingsPath()

                outermark = \
                """<selected_opencl_devices>
                {}
                </selected_opencl_devices>"""
                            
                devicemark = \
                """<device>
                        <device_name><![CDATA[{}]]></device_name>
                        <vendor_name><![CDATA[{}]]></vendor_name>
                        <id>{}</id>
                    </device>"""
                devices = ''
                for d in bpy.context.scene.indigo_engine.render_devices:
                    if d.use:
                        devices += devicemark.format(d.device, d.vendor, d.id)
                selected_devices_xml = outermark.format(devices)
                        
                if os.path.exists(settings_file):
                    # settings file exists
                    with open(settings_file, 'r') as f:
                        xml_string = f.read()
                    
                    import re
                    pattern = r'<settings>.*</settings>'
                    if re.search(pattern, xml_string, re.DOTALL | re.IGNORECASE):
                        # <settings> tag exists (file seems to be correct)
                        pattern = r'<selected_opencl_devices>.*</selected_opencl_devices>'
                        if re.search(pattern, xml_string, re.DOTALL | re.IGNORECASE):
                            # computing devices already exists        
                            xml_string = re.sub(pattern, selected_devices_xml, xml_string, flags=re.DOTALL | re.IGNORECASE)
                        else:
                            # computing devices does not exists yet
                            xml_string = re.sub(r'</settings>', selected_devices_xml+"</settings>", xml_string, flags=re.DOTALL | re.IGNORECASE)
                    else:
                        # settings tag does not exist. create new body
                        xml_string =\
                """<?xml version="1.0" encoding="utf-8"?>
                <settings>
                    {}
                </settings>""".format(selected_devices_xml)

                else:
                    # create new file
                    xml_string =\
                """<?xml version="1.0" encoding="utf-8"?>
                <settings>
                    {}
                </settings>""".format(selected_devices_xml)

                with open(settings_file, 'w') as f:
                    f.write(xml_string)
            
            #------------------------------------------------------------------------------
            # Print stats
            export_end_time = time.time()
            if self.verbose: indigo_log('Total mesh export time: %f seconds' % (geometry_exporter.total_mesh_export_time))
            indigo_log('Export finished; took %f seconds' % (export_end_time-export_start_time))
            
            # Reset to start_frame.
            if len(frame_list) > 1:
                bpy.context.scene.frame_set(start_frame)
            
            return {'FINISHED'}
        
        except Exception as err:
            indigo_log('%s' % err, message_type='ERROR')
            if os.getenv('B25_OBJECT_ANALYSIS', False):
                raise err
            return {'CANCELLED'}
        
class EXPORT_OT_indigo(_Impl_OT_indigo, bpy.types.Operator):
    def execute(self, context):
        self.set_report(self.report)
        return super().execute(context.scene)
    
menu_func = lambda self, context: self.layout.operator("export.indigo", text="Export Indigo Scene...")
bpy.types.INFO_MT_file_export.append(menu_func)

class INDIGO_OT_lightlayer_add(bpy.types.Operator):
    '''Add a new light layer definition to the scene'''
    
    bl_idname = "indigo.lightlayer_add"
    bl_label = "Add Indigo Light Layer"
    
    new_lightlayer_name = bpy.props.StringProperty(default='New Light Layer')
    
    def invoke(self, context, event):
        lg = context.scene.indigo_lightlayers.lightlayers
        lg.add()
        new_lg = lg[len(lg)-1]
        new_lg.name = self.properties.new_lightlayer_name
        return {'FINISHED'}
    
class INDIGO_OT_lightlayer_remove(bpy.types.Operator):
    '''Remove the selected lightlayer definition'''
    
    bl_idname = "indigo.lightlayer_remove"
    bl_label = "Remove Indigo Light Layer"
    
    lg_index = bpy.props.IntProperty(default=-1)
    
    def invoke(self, context, event):
        w = context.scene.indigo_lightlayers
        if self.properties.lg_index == -1:
            w.lightlayers.remove(w.lightlayers_index)
        else:
            w.lightlayers.remove( self.properties.lg_index )
        w.lightlayers_index = len(w.lightlayers)-1
        return {'FINISHED'}
    
class INDIGO_OT_medium_add(bpy.types.Operator):
    """Add a new medium definition to the scene"""

    bl_idname = "indigo.medium_add"
    bl_label = "Add Indigo Medium"

    new_medium_name = bpy.props.StringProperty(default='New Medium')

    def invoke(self, context, event):
        me = context.scene.indigo_material_medium.medium
        me.add()
        new_me = me[len(me) - 1]
        new_me.name = self.properties.new_medium_name
        return {'FINISHED'}
    
class INDIGO_OT_medium_remove(bpy.types.Operator):
    '''Remove the selected medium definition'''

    bl_idname = "indigo.medium_remove"
    bl_label = "Remove Indigo Medium"

    me_index = bpy.props.IntProperty(default=-1)

    def invoke(self, context, event):
        w = context.scene.indigo_material_medium
        if self.properties.me_index == -1:
            w.medium.remove(w.medium_index)
        else:
            w.medium.remove( self.properties.me_index )
        w.medium_index = len(w.medium)-1
        return {'FINISHED'}