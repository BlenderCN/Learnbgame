import logging
import bpy
import numpy as np
from imp import reload
import csv
import numpy as np

from pam import model
from pam import pam_vis as pv
from pam import colormaps as cm
from pam import pam

m_gray = 'Gray'
m_vc = 'Vertex_Color'

logger = logging.getLogger(__package__)

def delayModel_delayDistribLogNormal(delay, sd):
    """ Simple log-normal distribution of delays. Skips the part with the axon
    diameters for simplicity 
    delay                 : mean delay (for a lognormal distribution)
    sd                    : standard deviation
    returns the delay in ms per mm 
    """
    return np.random.lognormal(np.log(delay), sd, 1)[0]

def getDistancesPerParticle(data):
    distances = []

    for ds in data:
        distances.append(np.mean(ds))
        
    distances = np.array(distances)
    return distances

def getUVs(object, particle_system):
    """ returns a numpy-array of uv - coordinates for a given particle-system 
    on a given object """
    locations = [p.location for p in object.particle_systems[particle_system].particles]
    uvs = [pam.map3dPointToUV(object, object, loc) for loc in locations]
    return np.array(uvs)

def saveUVs(filename, object, particle_system):
    """ saves the uv-coordinates of all particles for a given object and a given
    particle_system id """
    uvs = getUVs(object, particle_system)
    f = open(filename, 'w')
    writer = csv.writer(f, delimiter=";")
    for uv in uvs:
        writer.writerow([uv[0], uv[1]])
        
    f.close()    

def getUVDistance(name, p_index, c_index):
    object = bpy.data.objects[name]
    uvs = getUVs(object, p_index)
    distances = getDistancesPerParticle(model.CONNECTION_RESULTS[c_index]['d'])
    return uvs, distances

def saveUVDistance(filename, name, p_index, c_index):
    uvs, distances = getUVDistance(name, p_index, c_index)
    
    no_particles = len(bpy.data.objects[name].particle_systems[p_index].particles)
    axon_length = [pam.computeDistance_PreToSynapse(c_index, i)[0] for i in range(no_particles)]

    f = open(filename, 'w')
    writer = csv.writer(
        f,
        delimiter=";",
        quoting=csv.QUOTE_NONNUMERIC
    )
    
    for i, uv in enumerate(uvs):
        #for d in distances[i]:
        writer.writerow([uv[0], uv[1], distances[i], axon_length[i]])
        
    f.close()
    
def saveUVDistanceForPost(filename, name, p_index, c_index):
    """ Saves connection length data but for incoming connections of a given
    post-synaptic neuron,
    name and p_index therefore also refer to the post-synaptic layer """
    object = bpy.data.objects[name]
    uvs = getUVs(object, p_index)
    
    distances = []
    axon_lengths = []
    number_particles = len(object.particle_systems[p_index].particles)
    for i, p in enumerate(object.particle_systems[p_index].particles):
        logger.info('%i / %i' % (i, number_particles))
        pre_neurons, synapses = model.getPreIndicesOfPostIndex(c_index, i)
        distance = []
        axon_length = []
        for j in range(len(pre_neurons)):
            distance.append(model.CONNECTION_RESULTS[c_index]['d'][pre_neurons[j]][synapses[j]])
            axon_length.append(pam.computeDistance_PreToSynapse(c_index, pre_neurons[j], [synapses[j]])[0])
            
        distances.append(np.mean(distance))
        axon_lengths.append(np.mean(axon_length))
        
    f = open(filename, 'w')
    writer = csv.writer(
        f,
        delimiter=";",
        quoting=csv.QUOTE_NONNUMERIC
    )
    
    for i, uv in enumerate(uvs):
        #for d in distances[i]:
        writer.writerow([uv[0], uv[1], distances[i], axon_lengths[i]])
        
    f.close()        
            

def saveAllUVDistanceData():
    # requires that hippocampus_rat3.pam is loaded
    saveUVDistance('uvd_EC2_DG.csv', 'EC_2', 0, 0)
    saveUVDistance('uvd_EC2_CA3.csv', 'EC_2', 0, 1)
    saveUVDistance('uvd_EC3_CA1.csv', 'EC_2', 0, 2)
    saveUVDistance('uvd_CA3_CA3.csv', 'CA3_sp', 0, 7)
    saveUVDistance('uvd_DG_CA3.csv', 'DG_sg', 0, 6)
    saveUVDistance('uvd_CA3_CA1.csv', 'CA3_sp', 0, 8)
    saveUVDistance('uvd_CA1_Sub.csv', 'CA1_sp', 0, 9)
    saveUVDistance('uvd_CA1_EC5.csv', 'CA1_sp', 0, 10)
    saveUVDistance('uvd_Sub_EC5.csv', 'Subiculum', 0, 11)
    
def saveAllUVDistanceDataPost():
    # requires that hippocampus_rat3.pam is loaded
    saveUVDistanceForPost('uvd_EC2_DG_post.csv', 'DG_sg', 0, 0)
    saveUVDistanceForPost('uvd_EC2_CA3_post.csv', 'CA3_sp', 0, 1)
    saveUVDistanceForPost('uvd_EC3_CA1_post.csv', 'CA1_sp', 0, 2)
    saveUVDistanceForPost('uvd_CA3_CA3_post.csv', 'CA3_sp', 0, 7)
    saveUVDistanceForPost('uvd_DG_CA3_post.csv', 'CA3_sp', 0, 6)
    saveUVDistanceForPost('uvd_CA3_CA1_post.csv', 'CA1_sp', 0, 8)
    saveUVDistanceForPost('uvd_CA1_Sub_post.csv', 'Subiculum', 0, 9)    
    saveUVDistanceForPost('uvd_CA1_EC5_post.csv', 'EC_5', 0, 10)
    saveUVDistanceForPost('uvd_Sub_EC5.csv', 'CA1_sp', 0, 11)

def correlate(name, p_index, c_index, d_mean, d_sd):
    object = bpy.data.objects[name]
    uvs = getUVs(object, p_index)
    distances = getDistancesPerParticle(model.CONNECTION_RESULTS[c_index]['d'])

    uvs2 = []
    delays = []
    for index, ds in enumerate(distances):
        samples = []
        for i in range(1):
            delay_mm = max(delayModel_delayDistribLogNormal(d_mean, d_sd), 0.1)
            uvs2.append(list(uvs[index,:]))
            delays.append(max(ds * delay_mm, 0.1))
            #samples.append( max(ds * delay_mm, 0.1) )
        #delays.append(np.mean(samples))
    delays = np.array(delays)
    
    uvs2 = np.array(uvs2)
    print(len(uvs2))
    
    corr_dist_x = np.corrcoef(uvs[:,0], distances)
    corr_dist_y = np.corrcoef(uvs[:,1], distances)    
    corr_dela_x = np.corrcoef(uvs2[:,0], delays)
    corr_dela_y = np.corrcoef(uvs2[:,1], delays)    
    print('Correlation x with distance: %f' % corr_dist_x[0][1])
    print('Correlation x with delay: %f' % corr_dela_x[0][1])
    print('Correlation y with distance: %f' % corr_dist_y[0][1])
    print('Correlation y with delay: %f' % corr_dela_y[0][1])


def getParticleIndicesForVertices(layer, p_layer):
    """ Returns a list of particle-indices corresponding to the order of 
    the vertices of the object. This function only makes sense, if each particle sits
    on top of vertex """
    
    indices = []
    for v in layer.data.vertices:
        indices.append(pam.map3dPointToParticle(layer, p_layer, v.co))
    return indices

def colorizeLayer(pre, distances, interval):
    """ Colorizes a layer according to its distances """
    # exclude all non-existing connections
    #distances[distances == 0] = min(distances[distances>0])
    #mean_d = np.mean(distances)
    #min_percent = np.min(distances)/mean_d
    #max_percent = np.max(distances)/mean_d

    print("Min: %f   max: %f" % (interval[0], interval[1]))

    #distances = distances / mean_d

    pv.colorize_vertices(pre, distances, interval=interval)    
        
def colorizeMapping(mapping_id):
    """ Colorizes pre layer for a given mapping """
    
    pre = model.CONNECTIONS[mapping_id][0][0]
    post = model.CONNECTIONS[mapping_id][0][-1]
    #neuron = bpy.data.objects['Neuron_Sphere']

    distances_pre = getDistancesPerParticle(model.CONNECTION_RESULTS[mapping_id]['d'])
    pre_indices = getParticleIndicesForVertices(pre, 0)

    for i, p_ind in enumerate(pre_indices):
        if distances_pre[p_ind] == 0:
            pv.visualizePoint(pre.particle_systems[0].particles[p_ind].location)

    
    
    distances_post = []
    post_indices = getParticleIndicesForVertices(post, 0)
    
    for i, p in enumerate(post.particle_systems[0].particles):
        pre_neurons, synapses = model.getPreIndicesOfPostIndex(mapping_id, i)
        distance = []
        for j in range(len(pre_neurons)):
            distance.append(model.CONNECTION_RESULTS[mapping_id]['d'][pre_neurons[j]][synapses[j]])
            
        mean = np.mean(distance)
        if np.isnan(mean):
            distances_post.append(0)
        else:
            distances_post.append(mean)
    
    for i, p_ind in enumerate(post_indices):
        if distances_post[p_ind] == 0:
            pv.visualizePoint(post.particle_systems[0].particles[p_ind].location)

    print(distances_post)
    print(type(distances_pre))
    print(type(distances_post))
    mean_d = np.mean(list(distances_pre) + distances_post)
    min_percent = np.min(list(distances_pre) + distances_post) / mean_d
    max_percent = np.max(list(distances_pre) + distances_post) / mean_d
    distances_pre = distances_pre / mean_d
    distances_post = np.array(distances_post) / mean_d    
    
    colorizeLayer(pre, np.take(distances_pre, pre_indices), [min_percent, max_percent])
    colorizeLayer(post, np.take(distances_post, post_indices), [min_percent, max_percent])


def setMaterial(list, material_name):
    """ Turns each object in list gray. List contains names of objects """
    for name in list:
        O[name].data.materials[0] = bpy.data.materials[material_name]
        
    
def colorizeEC2_DG():
    setMaterial(['EC_3', 'EC_5', 'CA1_sp', 'Subiculum', 'CA3_sp'], m_gray)
    setMaterial(['EC_2', 'DG_sg'], m_vc)    
    colorizeMapping(0)
    
def colorizeEC2_CA3():
    setMaterial(['EC_3', 'EC_5', 'CA1_sp', 'Subiculum', 'DG_sg'], m_gray)
    setMaterial(['EC_2', 'CA3_sp'], m_vc)
    colorizeMapping(1)
    
def colorizeEC3_CA1():
    setMaterial(['EC_2', 'CA3_sp', 'EC_3', 'EC_5', 'CA1_sp', 'Subiculum', 'DG_sg'], m_gray)
    setMaterial(['EC_3', 'CA1_sp'], m_vc)
    colorizeMapping(2)

def colorizeDG_CA3():
    setMaterial(['EC_2', 'CA3_sp', 'EC_3', 'EC_5', 'CA1_sp', 'Subiculum', 'DG_sg'], m_gray)
    setMaterial(['DG_sg', 'CA3_sp'], m_vc)
    colorizeMapping(6)

def colorizeCA3_CA1():
    setMaterial(['EC_2', 'CA3_sp', 'EC_3', 'EC_5', 'CA1_sp', 'Subiculum', 'DG_sg'], m_gray)
    setMaterial(['CA1_sp', 'CA3_sp'], m_vc)
    colorizeMapping(8)    
    
def colorizeSub_EC5():
    setMaterial(['EC_2', 'CA3_sp', 'EC_3', 'EC_5', 'CA1_sp', 'Subiculum', 'DG_sg'], m_gray)
    setMaterial(['Subiculum', 'EC_5'], m_vc)
    colorizeMapping(11)        
    
#    delays = []
#    for ds in distances:
#        samples = []
#        for i in range(1):
#            delay_mm = max(delayModel_delayDistribLogNormal(1.5, .1), 0.1)
#            samples.append( max(ds * delay_mm, 0.1) )
#        delays.append(np.mean(samples))
#        
#    min_d = np.min(delays) / np.mean(delays)
#    max_d = np.max(delays) / np.mean(delays)
#
#    #print("Delays min: %f   max: %f" % (min_d, max_d))
#
#    delays = delays / np.mean(delays)
#
#    v_dist = getDistancesPerParticle(model.CONNECTION_RESULTS[mapping_id]['d'])
#    v_dist[v_dist == 0] = min(v_dist[v_dist>0])
#    mean_v = np.mean(v_dist)
#    v_dist = v_dist / mean_v

#colors = pv.getColors(cm.standard, v_dist, interval=[min_percent, max_percent])
#pv.generateLayerNeurons(o, 0, neuron, colors)
