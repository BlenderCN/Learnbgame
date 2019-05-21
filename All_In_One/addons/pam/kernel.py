"""Kernel Module"""

import math
import numpy as np

KERNEL_TYPES = [
    ("gauss", "Gauss", "", 0),
    ("gauss_u", "Gauss (u)", "", 1),
    ("gauss_v", "Gauss (v)", "", 2),
    ("stripe_with_end", "Stripe with end", "", 3),
    ("unity", "Unity", "", 4),
    ("yu_kernel", "Yu Kernel", "", 5),
    ("yu_kernel2", "Yu fixed Params", "", 6)
]

def get_kernel(kernel_identifier, args):
    if type(args) is list:
        return KERNEL_DICT[kernel_identifier](*args)
    elif type(args) is dict:
        return KERNEL_DICT[kernel_identifier](**args)

class AbstractKernel():
    def __init__(self):
        self.scale = 1.0

    def apply(self, uv, guv):
        """
        :param uv: uv coordinates
        :type uv: numpy array of floats with shape (x, y, 2)
        :param guv: grid coordinates
        :type guv: numpy array of floats with shape (x, y, 2)"""

        return None

    def get_args(self):
        return {}

    def __eq__(self, other):
        return self.get_args() == other.get_args()

    def __ne__(self, other):
        return self.get_args() != other.get_args()

    def rescale(self, scale):
        self.scale = scale

class GaussKernel(AbstractKernel):
    """Computes distribution value in two dimensional gaussian kernel

    :param float var_u:
    :param float var_v:
    :param float shift_u:
    :param float shift_u:
    :return: gauss value at point uv in 2d space
    :rtype: float"""

    name = "gauss"
    
    def __init__(self, var_u = 1.0, var_v = 1.0, shift_u = 0.0, shift_v = 0.0):
        self.var_u = var_u
        self.var_v = var_v
        self.shift_u = shift_u
        self.shift_v = shift_v

    def apply(self, uv, guv):
        ruv = guv - uv  # compute relative position

        return np.exp(-((ruv[...,0] + self.shift_u / self.scale) ** 2 / (2 * (self.var_u / self.scale) ** 2) +
                        (ruv[...,1] + self.shift_v / self.scale) ** 2 / (2 * (self.var_v / self.scale) ** 2)))

    def get_args(self):
        return {'var_u': self.var_u, 'var_v': self.var_v, 'shift_u': self.shift_u, 'shift_v': self.shift_v}

# copied from:
# http://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python
def unit_vector(vector):
    """Returns the unit vector of the vector

    :param mathutils.Vector vector: a vector
    :return: unit vector
    :rtype: mathutils.Vector

    """
    return vector / np.linalg.norm(vector)


# copied from:
# http://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python
def angle_between(v1, v2):
    """Returns the angle in radians between vectors `v1` and `v2`::

        >>> angle_between((1, 0, 0), (0, 1, 0))
        1.5707963267948966
        >>> angle_between((1, 0, 0), (1, 0, 0))
        0.0
        >>> angle_between((1, 0, 0), (-1, 0, 0))
        3.141592653589793

    :param mathutils.Vector v1: a vector
    :param mathutils.Vector v2: another vector
    :return: angle between vectors
    :rtype: float

    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    angle = np.arccos(np.dot(v1_u, v2_u))
    if np.isnan(angle):
        if (v1_u == v2_u).all():
            return 0.0
        else:
            return np.pi
    return angle

class StripeWithEndKernel(AbstractKernel):
    """The kernel is essiantially a stripe along the (vec_u, vec_v) axis
    but everything in the negative direction of the vector is ommitted.

    This function is helpful to model axons which grow only in one direction
    
    :param float vec_u: u-component of the direction vector
    :param float vec_v: v-component of the direction vector
    :param float shift_u: shift along the u-direction relativ in space
    :param float shift_v: shift along the v-direction
    :param float var_v: width of the kernel
    :return:
    :rtype: float
    """

    name = "stripe_with_end"

    def __init__(self, vec_u=1.0, vec_v=0.0, shift_u=0.0, shift_v=0.0, var_v=0.2):
        self.vec_u = vec_u
        self.vec_v = vec_v
        self.shift_u = shift_u
        self.shift_v = shift_v
        self.var_v = var_v

    def apply(self, uv, guv):
        # angle of standard-vector to base
        ruv = guv - uv

        vec = np.array([self.vec_u / self.scale, self.vec_v / self.scale])
        angle = angle_between(vec, np.array([1., 0.]))
        rotMatrix = np.array([
            [np.cos(-angle), -np.sin(-angle)],
            [np.sin(-angle), np.cos(-angle)]
        ])
        rot_vec = np.dot(rotMatrix, ruv[...,np.newaxis])
        rot_vec = np.swapaxes(rot_vec, 0, -1)[0]
        rot_vec[...,0] -= self.shift_u / self.scale
        rot_vec[...,1] -= self.shift_v / self.scale
        
        result = np.exp(-(rot_vec[...,1]**2 / (2 * self.var_v**2)))
        if type(result) is not np.ndarray:
            if rot_vec[0] < 0:
                return 0.0
            else:
                return result
        else:
            np.place(result, rot_vec[...,0] < 0.0, 0.0)
            return result

    def get_args(self):
        return {'vec_u': self.vec_u, 'vec_v': self.vec_v, 'shift_u': self.shift_u, 'shift_v': self.shift_v, 'var_v': self.var_v}

class GaussUKernel(AbstractKernel):
    """Computes distribution value in one dimensional gaussian kernel
    in u direction

    :param float origin_u:
    :param float origin_v:
    :type origin_u:
    :type origin_v:
    :return: gauss value at point uv in 2d space
    :rtype: float
    """

    name = "gauss_u"

    def __init__(self, origin_u = 0.0, var_u = 1.0):
        self.origin_u = origin_u
        self.var_u = var_u

    def apply(self, uv, guv):
        ruv = guv - uv  # compute relative position

        return np.exp(-(1 / 2) * ((ruv[...,0] - self.origin_u / self.scale) / (self.var_u / self.scale)) ** 2)

    def get_args(self):
        return {'origin_u': self.origin_u, 'var_u': self.var_u}

class GaussVKernel(AbstractKernel):
    """Computes distribution value in one dimensional gaussian kernel
    in v direction

    :param float origin_u:
    :param float origin_v:
    :type origin_u:
    :type origin_v:
    :return: gauss value at point uv in 2d space
    :rtype: float

    """

    name = "gauss_v"

    def __init__(self, origin_v = 0.0, var_v = 1.0):
        self.origin_v = origin_v
        self.var_v = var_v

    def apply(self, uv, guv):
        ruv = guv - uv  # compute relative position

        return np.exp(-(1 / 2) * ((ruv[...,1] - self.origin_v / self.scale) / (self.var_v / self.scale)) ** 2)

    def get_args(self):
        return {'origin_v': self.origin_v, 'var_v': self.var_v}

class UnityKernel(AbstractKernel):
    """Returns a unity kernel"""

    name = "unity"

    def __init__(self):
        pass

    def apply(self, uv, guv):
        return np.ones(guv.shape[:2], dtype = np.float)

class YuKernel():
    """Computes distribution value in two dimensional Yu kernel

    :type guv: tuple (float, float)
    :param float alpha_u: compression in u
    :param float alpha_v: compression in v
    :param float omega_u: scaling in u
    :param float omega_v: scaling in v
    :param float ksi_u: shift in u
    :param float ksi_v: shift in v
    :param float tau: rotation angle
    :return: yu_kernel value at point uv in 2d space
    :rtype: float"""

    name = "yu_kernel"

    def __init__(self, alpha_u = 0., alpha_v =  0., omega_u = 1.0, omega_v =1.0, ksi_u = 0., ksi_v = 0., tau = 0.):
        self.alpha_u = alpha_u
        self.alpha_v = alpha_v
        self.omega_u = omega_u
        self.omega_v = omega_v
        self.ksi_u = ksi_u
        self.ksi_v = ksi_v
        self.tau = tau

    @staticmethod
    def _phi(x):
        return np.exp(-(x**2/2))/(np.sqrt(2*np.pi))
    
    @staticmethod
    def _xhi(x):
        return 0.5*(1+ math.erf(x/np.sqrt(2)))

    def yu_kernel(self, duv):
        taur = np.pi/180 * self.tau    # convert angle in radian
        u = duv[0] - self.ksi_u # compute relative u coordinate 
        v = duv[1] - self.ksi_v # compute relative u coordinate 
        ruv = [( u * np.cos(taur) - v * np.sin(taur)), 
               ( u * np.sin(taur) + v * np.cos(taur))] # compute rotation
                  
        return (2/self.omega_v * self._phi(ruv[1]/ self.omega_v) * self._xhi (self.alpha_v * ruv[1]/ self.omega_v)*
                2/self.omega_u * self._phi(ruv[0]/ self.omega_u) * self._xhi (self.alpha_u * ruv[0]/ self.omega_u)) / 20.

    def apply(self, uv, guv):
        ruv = guv - uv
        m = np.empty(shape = ruv.shape[:2])
        for i in range(ruv.shape[0]):
            for j in range(ruv.shape[1]):
                m[i, j] = self.yu_kernel(ruv[i, j])
        return m

    def get_args(self):
        return {'alpha_u': self.alpha_u,
            'alpha_v': self.alpha_v,
            'omega_u': self.omega_u,
            'omega_v': self.omega_v,
            'ksi_u': self.ksi_u,
            'ksi_v': self.ksi_v,
            'tau': self.tau}


# TODO(SK): Rephrase docstring & fill in parameter values
def yu_kernel2(uv, guv):
    """Computes distribution value in two dimensional Yu kernel

    :param uv: uv coordinates
    :type uv: tuple (float, float)
    :param guv:    
    :type guv: tuple (float, float)
    :return: yu_kernel value at point uv in 2d space
    :rtype: float
    
    """

    # omega: Scaling by (omega * bins)
    #         omega = ]0., ∞] (if = 0 => div 0)
         
    # alpha: Compression of function by unknown
    #         alpha = [-∞, ∞]
                
    # ksi:   Shift by (ksi * bins)
    #         ksi = [-∞, ∞]
    
    alpha_u = np.array ([ [ 0.5, 0.5, 0.5], [ 0.15, 0.15, 0.0], [-0.5 , 0.0, 0.0], 
                          [-1.5, 0.0, 0.0], [-0.75, 0.0 , 0.0], [-0.25, 0.0, 0.0], 
                          [0.0, 0.0, 0.0] ])
    alpha_v = np.array ([ [2.0, 2.0, 2.0], [ 1.5,  1.5,  0.8], [ 0.5,  0.5,  0.5],  
                          [0.0, 0.0, 0.0], [-0.5, -0.5, -0.5], [-1.5, -1.0, -1.5], 
                          [-2.0, -1.5, -2.0] ])
    omega_u = np.array ([ [0.3, 0.3, 0.5], [0.3, 0.3, 0.4], [0.4, 0.6, 0.45],  
                          [0.5, 0.8, 0.5], [0.5, 0.7, 0.5], [0.4, 0.6, 0.4], 
                          [0.3, 0.5, 0.3] ])
    omega_v = np.array ([ [1.5, 1.5, 1.0], [1.7, 2.0, 1.7], [2.3, 3.5, 2.5],  
                          [3.0, 5.0, 3.0], [2.2, 4.3, 2.2], [1.2, 2.0, 1.2], 
                          [0.8, 1.5, 0.8] ])
    ksi_u   = np.array ([ [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, -0.5, -0.5],  
                          [0.0, 0.0, 0.0], [0.1, 0.1, 0.0], [0.2,  0.3,  0.0], 
                          [0.3, 0.3, 0.0] ])
    ksi_v   = np.array ([ [-0.5, -0.5, -0.4], [-0.5, -0.5, -0.5], [-0.5, -0.5, -0.5],  
                          [-0.2,  0.0, -0.1], [-0.1, 0.05,  0.0], [ 0.1,  0.2,  0.1], 
                          [0.2, 0.2, 0.1] ])
    tau     = np.array ([ [-2., -2.,  0.], [ 5.,  5.,  5.], [40., 35., 30.],  
                          [80., 60., 55.], [70., 55., 43.], [70., 48., 35.], 
                          [70., 40., 20.] ])
            

    def interpolate (param, coor):            
        u = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0])/3
        v = np.array([0.0, 5.0, 10.0])/10
        
        x2=np.where(u>=coor[0])[0][0]
        x1=x2-1
        y2=np.where(v>=coor[1])[0][0]
        y1=y2-1
        
        a_x1=np.interp(coor[0], [u[x1],u[x2]],[param[x1][y1],param[x2][y1]])
        a_x2=np.interp(coor[0], [u[x1],u[x2]],[param[x1][y2],param[x2][y2]])
        a_y=np.interp(coor[1], [v[y1],v[y2]],[a_x1,a_x2])
        
        return a_y
        

    def phi(x):
        return math.exp(-(x**2/2))/(math.sqrt(2*math.pi))
     

    def xhi(x):
        return 0.5*(1+ math.erf(x/math.sqrt(2)))  
        
    u = guv[0] - uv[0] # compute relative u coordinate 
    v = guv[1] - uv[1] # compute relative u coordinate 

    a_u = interpolate(alpha_u, uv)
    a_v = interpolate(alpha_v, uv)
    o_u = interpolate(omega_u, uv)
    o_v = interpolate(omega_v, uv)
    k_u = interpolate(ksi_u, uv)
    k_v = interpolate(ksi_v, uv)
    t   = interpolate(tau, uv) 
    
    ux = u - k_u
    vy = v - k_v
    taur = math.pi/180 * t    # convert angle in radian
    
    ruv = [( ux * np.cos(taur) - vy * np.sin(taur)), 
           ( ux * np.sin(taur) + vy * np.cos(taur))] # compute rotation
               
    return (2/o_v * phi(ruv[1]/ o_v) * xhi (a_v * ruv[1]/ o_v)*
            2/o_u * phi(ruv[0]/ o_u) * xhi (a_u * ruv[0]/ o_u)) 


KERNEL_DICT = {
    "gauss": GaussKernel,
    "gauss_u": GaussUKernel,
    "gauss_v": GaussVKernel,
    "stripe_with_end": StripeWithEndKernel,
    "unity": UnityKernel,
    "yu_kernel": YuKernel,
    "yu_kernel2": yu_kernel2
}

gauss = GaussKernel
gauss_u = GaussUKernel
gauss_v = GaussVKernel
stripe_with_end = StripeWithEndKernel
unity = UnityKernel
yu_kernel = YuKernel
yu_kernel2 = yu_kernel2