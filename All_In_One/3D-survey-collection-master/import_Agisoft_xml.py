import bpy
from mathutils import Matrix
import os
import xml.etree.ElementTree as ET
from bpy_extras.io_utils import axis_conversion
from bpy_extras.io_utils import ImportHelper

def createcamera(name, transform_matrix, collection_name, root, sensor_id):
    scene = bpy.context.scene
    cam = bpy.data.cameras.new(name)
    cam_ob = bpy.data.objects.new(name, cam)
    cam_ob.matrix_local = transform_matrix
    (sensor_label, sensor_width, sensor_height, focal_length) = find_sensor(root, sensor_id)
    cam.sensor_height = sensor_height
    print(str(sensor_height))
    cam.sensor_width = sensor_width
    cam.lens = focal_length
    scene.collection.children[collection_name].objects.link(cam_ob)

    

def setup_collection(collection_name):
    if bpy.data.collections.get(collection_name) is None:
        newcol = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(newcol)
    

def find_sensor(root, sensor_id):
        for sen in root.iter('sensor'):
                if sen.get('id') == sensor_id:
                        #sensor_id = sen.get('id')
                        sensor_label = sen.get('label')
                        for res in sen.findall('resolution'):
                                img_width = float(res.attrib["width"])
                                print(str(img_width))
                                img_heigth = float(res.attrib["height"])
                        for prop in sen.findall('property'):
                                n = prop.attrib["name"]
                                v = prop.attrib["value"]
                                if(n == "pixel_width"):
                                        sensor_p_width = float(v)
                                elif(n == "pixel_height"):
                                        sensor_p_height = float(v)
                                elif(n == "focal_length"):
                                        focal_length = float(v)
                                        print(str(focal_length))
                                #elif(n == "fixed"):
                                #        self.props[n] = v
                                #elif(n == "layer_index"):
                                #        self.props[n] = v
                                else:
                                        pass
                        
                        sensor_width = img_width*sensor_p_width
                        print(str(sensor_width))
                        sensor_height = img_heigth*sensor_p_height
                                        
                        return sensor_label, sensor_width, sensor_height, focal_length

def load_create_cameras(filepath):

    tree = ET.parse(filepath)
    (dirname, filename) = os.path.split(filepath)
    root = tree.getroot()
    collection_name = os.path.splitext(filename)[0]
    setup_collection(collection_name)
    for cam in root.iter('camera'):
        image_name = cam.get('label')
        cam_name = os.path.splitext(image_name)[0]
        sensor = cam.get('sensor_id')

        for transform in cam.findall('transform'):
            transform_coord = transform.text
            list_coord = transform_coord.split(' ')
            formatted_list_coord = [ (float(list_coord[0]), float(list_coord[1]), float(list_coord[2]), float(list_coord[3])), (float(list_coord[4]), float(list_coord[5]), float(list_coord[6]), float(list_coord[7])), (float(list_coord[8]), float(list_coord[9]), float(list_coord[10]), float(list_coord[11])), (float(list_coord[12]), float(list_coord[13]), float(list_coord[14]), float(list_coord[15])) ]
            matrix = Matrix(formatted_list_coord)
            conversion_matrix = axis_conversion(from_forward='Z', from_up='-Y', to_forward='-Z', to_up='Y').to_4x4()
            matrix = matrix @ conversion_matrix
        #print(image_name+' '+ cam_name)
        #print(matrix)
        createcamera(cam_name, matrix, collection_name, root, sensor)