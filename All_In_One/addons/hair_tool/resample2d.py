# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Copyright (C) 2017 JOSECONSCO
# Created by JOSECONSCO

import bisect
import numpy as np
from mathutils import Vector, Quaternion
from math import ceil, floor


def cubic_spline(locs, tknots):
    knots = list(range(len(locs)))

    n = len(knots)
    if n < 2:
        return False
    x = tknots[:]
    result = []
    for j in range(3):  # x, y, z
        a = [loc[j] for loc in locs]
        h = [max(1e-8, x[i+1] - x[i]) for i in range(n-1)]
        q = [False] + [3/h[i]*(a[i+1]-a[i]) - 3/h[i-1]*(a[i]-a[i-1]) for i in range(1, n-1)]
        l = [1.0]
        u = [0.0]
        z = [0.0]
        for i in range(1, n-1):
            l.append(2*(x[i+1]-x[i-1]) - h[i-1]*u[i-1])
            if l[i] == 0:
                l[i] = 1e-8
            u.append(h[i] / l[i])
            z.append((q[i] - h[i-1] * z[i-1]) / l[i])
        l.append(1.0)
        z.append(0.0)
        b = [False for i in range(n-1)]
        c = [False for i in range(n)]
        d = [False for i in range(n-1)]
        c[n-1] = 0.0
        for i in range(n-2, -1, -1):
            c[i] = z[i] - u[i]*c[i+1]
            b[i] = (a[i+1]-a[i])/h[i] - h[i]*(c[i+1]+2*c[i])/3
            d[i] = (c[i+1]-c[i]) / (3*h[i])
        result += [[a[i], b[i], c[i], d[i], x[i]] for i in range(n-1)]
    splines = [[result[i], result[i+n-1], result[i+(n-1)*2]] for i in range(len(knots)-1)]
    return splines


def eval_spline(splines, tknots, t_in):
    out = []
    for t in t_in:
        n = bisect.bisect(tknots, t, lo=0, hi=len(tknots))-1
        n = max(min(n, len(splines)-1), 0)
        # pt = []
        # for i in range(3):
        #     ax, bx, cx, dx, tx = splines[n][i]
        #     x = ax + bx*(t-tx) + cx*(t-tx)**2 + dx*(t-tx)**3
        #     pt.append(x)
        pt = [splines[n][i][0] + splines[n][i][1]*(t-splines[n][i][4]) + splines[n][i][2]*(t-splines[n][i][4]) **
              2 + splines[n][i][3]*(t-splines[n][i][4])**3 for i in range(3)]
        out.append(pt)
    return out

# import math
# p1 = math.floor(t)
# p2 = (p1 + 1)
# p3 = (p2 + 1) if p2 < len(points)-1 else len(points)-1
# p0 = p1 - 1 if p1 >= 1 else 0

# t = t - math.floor(t)
# tt = t * t
# ttt = tt * t

# q1 = -ttt + 2.0*tt - t
# q2 = 3.0*ttt - 5.0*tt + 2.0
# q3 = -3.0*ttt + 4.0*tt + t
# q4 = ttt - tt

# OutVec = 0.5 * (points[p0] * q1 + points[p1] * q2 + points[p2] * q3 + points[p3] * q4)
#resampled_points = [b_spline_point_orig(points, i * (len(points) - 1.00001)/(res-1)) for i in range(res)]

SPLINE_CACHE = {}


def do_cache_coefficients(points_count, res):
    spline_coeff = {}
    t_multiplier = (points_count - 1.001) / (res - 1)  # t is from 0-1, for while curve
    # .001 - cos if we reach res*t_multiplier - ten last point is on end of spline - and p[-1].co = 0,0,0
    for i in range(res):
        spline_coeff[i] = {}
        t_in = i * t_multiplier
        t = t_in - floor(t_in)
        tt = t * t
        ttt = tt * t
        spline_coeff[i]['q1'] = -ttt + 2.0*tt - t
        spline_coeff[i]['q2'] = 3.0*ttt - 5.0*tt + 2.0
        spline_coeff[i]['q3'] = -3.0*ttt + 4.0*tt + t
        spline_coeff[i]['q4'] = ttt - tt
    return spline_coeff


def get_cubic_spline_points(points, res,  uniform_spacing, noiseStrandSeparation, shrink_ts, use_cache= True):
    """
    Args:
        :verts -2d list of multiple strands (vec1, vec2, vec... n):
        :res  number of points after resampling :
        :uniform_spacing if spacing of points is uniform or not. Is not then can use cache and is faster:
        :noiseStrandSeparation=0 - rendomize tn +/- delta: #TODO:
        :same_point_count=True if false, shorter strands = less points (smaller res): #TODO:
        :shortenStrandLen=0.0 - reduce eval T_max by  *=shrink_t:

    Returns:
        :Vec list - spline points resampled
    """
    points_len = len(points)
    t_map_full_rage = (points_len - 1.01)/(res-1)  # t is from 0-1, for while curve
    resampled_points = []
    if use_cache:
        # print('Using cache')
        global SPLINE_CACHE
        for i in range(res): # i - is time t = i * t_map_full_rage, from <0,1> mapped to <0, point_count/res * res>
            t = i * t_map_full_rage
            p1 = floor(t)
            p2 = (p1 + 1)
            p3 = min(p2 + 1, points_len-1)
            p0 = max(p1 - 1,  0)
            out_pos = points[p0] * SPLINE_CACHE[i]['q1'] + points[p1] * SPLINE_CACHE[i]['q2'] + \
                points[p2] * SPLINE_CACHE[i]['q3'] + points[p3] * SPLINE_CACHE[i]['q4']
            resampled_points.append(0.5 * out_pos)
        return resampled_points
    else:  
        # print('Not using cache')
        #for uniform point distribution t_i has to be modified by strand points legths
        # adjust time spacing based on points distances etc
        t_s_adjusted = get_adjusted_t_s(points, res, uniform_spacing, noiseStrandSeparation, t_map_full_rage ,shrink_ts)
        for t in t_s_adjusted:  # i - is time t = i * t_map_full_rage, from <0,1> mapped to <0, point_count/res * res>
            p1 = floor(t)
            p2 = (p1 + 1)
            p3 = min(p2 + 1, points_len-1)
            p0 = max(p1 - 1,  0)
            t = t - p1
            tt = t * t
            ttt = tt * t
            q1 = -ttt + 2.0*tt - t
            q2 = 3.0*ttt - 5.0*tt + 2.0
            q3 = -3.0*ttt + 4.0*tt + t
            q4 = ttt - tt
            out_pos = points[p0] * q1 + points[p1] * q2 + points[p2] * q3 + points[p3] * q4
            resampled_points.append(0.5 * out_pos)
        return resampled_points



def get_strand_proportions2(strandsList):  # return array <0,1> - where 1 is for longest strand
    lengthPerStrand = []
    for v in strandsList:
        pts = np.array(v).T
        tmp = np.apply_along_axis(np.linalg.norm, 0, pts[:, :-1] - pts[:, 1:])  # do an - an-1 and get length
        t = tmp.sum()  # len of strand
        lengthPerStrand.append(t)  # len*numb of spliness / number of splines
    strand_len_normalized = np.array(lengthPerStrand)/max(lengthPerStrand)
    return strand_len_normalized.tolist()
    #Below wont work is splines have different points counts... but if lens are eq, then works ok
    # pts = np.array(strandsList)
    # tmp = np.apply_along_axis(np.linalg.norm, 1, pts[:, :-1] - pts[:, 1:]) #sum lens of strans 
    # len_sum = tmp.sum(1) #sum x,y,z into strand len lists
    # return list(len_sum/max(len_sum))


def get_adjusted_t_s(strand, res, uniform_spacing, noiseStrandSeparation, t_map_full_rage , shrink_ts):  # return array <0,1> - where 1 is for longest strand
    vCount = len(strand)
    t_in = np.array([i/(res-1) for i in range(res)])
    corr_t_ins = t_in
    if uniform_spacing:
        domain = [i/(vCount-1) for i in range(vCount)]
        pts = np.array(strand).T
        seg_lens = np.apply_along_axis(np.linalg.norm, 0, pts[:, :-1]-pts[:, 1:])  # do an - an-1 and get length
        t = np.insert(seg_lens, 0, 0).cumsum()  # add zero and sum
        #t will be now proportional to segments distances - bigger point spacing - more time.
        t = t/t[-1] 
        corr_t_ins = np.interp(t_in,  t, domain)
    if type(noiseStrandSeparation) is np.ndarray:
        corr_t_ins = corr_t_ins+noiseStrandSeparation
        np.clip(corr_t_ins, 0, 1, out=corr_t_ins)  # cos t in (0,1)
    return list(corr_t_ins * t_map_full_rage * shrink_ts * (res-1))  # remap from <0,1> to <0, res-1>



def interpol_Catmull_Rom(verts, res, uniform_spacing=False, noiseStrandSeparation=0, same_point_count=True, shortenStrandLen=0, seed=2):
    """ Catmull_Rom - spline interpolation (cubic)
    Args:
        :verts -2d list of multiple strands (vec1, vec2, vec... n):
        :res  number of points after resampling :
        :uniform_spacing if spacing of points is uniform or not. Is not then can use cache and is faster:
        :noiseStrandSeparation=0 - rendomize tn +/- delta: 
        :same_point_count=True if false, shorter strands = less points (smaller res):
        :shortenStrandLen=0.0 - reduce eval T_max by  *=shrink_t:
    """
    strands_count = len(verts)
    use_cache = not(uniform_spacing or noiseStrandSeparation or not same_point_count or shortenStrandLen)  # we need to calc point spacing so can't use chache
    if use_cache:
        len_first = len(verts[0])
        if not all(len(strand) == len_first for strand in verts): #if strands are not equal lengths disable caching
            # print('Not all strands have same point count. Disabling cache')
            use_cache = False
    if use_cache:
        global SPLINE_CACHE
        SPLINE_CACHE.clear()
        SPLINE_CACHE = do_cache_coefficients(len(verts[0]), res)  # assume they are eq. len
    # print('Using cache') if use_cache else print('no cache')

    #shorte stran leg by reducing evel time
    np.random.seed(seed)
    shrink_ts = list(1.0 - np.random.uniform(0, shortenStrandLen/2, strands_count)) if shortenStrandLen else [1]*strands_count
    res_normalized = [res]*strands_count
    if not same_point_count:
        NormalizedStrandsLength = get_strand_proportions2(np.array(verts))
        res_normalized = [max(ceil((res) * strandLen), 2) for strandLen in NormalizedStrandsLength]

    if noiseStrandSeparation:
        rand_delta_t_ins = np.random.rand(res) - 0.5
        deltaMargin = (verts[1][0]-verts[0][0]).length  # AN-A(N-1)
        noiseStrandSeparation = rand_delta_t_ins*deltaMargin*noiseStrandSeparation

    return [get_cubic_spline_points(splinex, res_n,  uniform_spacing, noiseStrandSeparation, t_shrink, use_cache) for splinex, t_shrink, res_n in zip(verts, shrink_ts, res_normalized)]
    


def get2dinterpol_Catmull_Rom(verts, IntervalX, IntervalY, shortenStrandLen, Seed, x_uniform, y_uniform, noiseStrandSeparation):
    wasX_res_minus_one = True if IntervalX == -1 else False
    if wasX_res_minus_one:  # do 3 splines but we will use middle one as output
        IntervalX = 3
    x = interpol_Catmull_Rom(verts, IntervalX, x_uniform, noiseStrandSeparation=noiseStrandSeparation, seed=Seed)
    stramds_firstRow, *strands_afterFirst = x #splits x into x[0] + x[1:]
    strands_afterFirst_Transposed = list(zip(*strands_afterFirst))  # transpose
    x2 = interpol_Catmull_Rom(strands_afterFirst_Transposed, IntervalY, y_uniform, shortenStrandLen=shortenStrandLen, seed=Seed)
    [x2_element.insert(0, first) for x2_element, first in zip(x2,stramds_firstRow)] #add back first row

    #there will be 3 output strands if wasX_res_minus_one - use middle one
    return [x2[1]] if wasX_res_minus_one else x2 


def rotationMatrix(theta, axis):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    quat_rot = Quaternion(axis, theta)
    return np.array(quat_rot.to_matrix())


def parallel_transport_TNB(points):
    '''Get (Tangents,Normals) lists from points (Vector) list (slower than build in hack for alignign :( '''
    # Number of points
    n = len(points)
    points = np.array([point.co.xyz for point in points])
    # Calculate all tangents
    T = np.apply_along_axis(np.gradient, axis=0, arr=points)

    # Normalize all tangents normalized
    def f(m): return m / np.linalg.norm(m)
    T = np.apply_along_axis(f, axis=1, arr=T)

    # Initialize the first parallel-transported normal vector V
    V = np.zeros(np.shape(points))
    V[0] = (T[0][1], -T[0][0], 0)
    V[0] = V[0] / np.linalg.norm(V[0])

    # Compute the values for V for each tangential vector from T
    for i in range(n - 1):
        b = np.cross(T[i], T[i + 1])
        if np.linalg.norm(b) < 0.00001:
            V[i + 1] = V[i]
        else:
            b = b / np.linalg.norm(b)
            phi = np.arccos(np.dot(T[i], T[i + 1]))
            R = rotationMatrix(phi, b)
            V[i + 1] = np.dot(R, V[i])

    # Calculate the second parallel-transported normal vector U
    N = np.array([np.cross(t, v) for (t, v) in zip(T, V)])

    # Normalize all tangents
    return (T,N)

















def get_strand_proportions(strandsList):  # return array <0,1> - where 1 is for longest strand
    lengthPerStrand = []
    # ipdb.set_trace()
    for v in strandsList:
        pts = np.array(v).T
        tmp = np.apply_along_axis(np.linalg.norm, 0, pts[:, :-1] - pts[:, 1:])  # do an - an-1 and get length
        t = tmp.sum()  # add zero and sum
        # t will containt time = dist between neighbor knots normalized
        lengthPerStrand.append(t)  # len*numb of spliness / number of splines
    NormalizedLengthYPerStrand = lengthPerStrand/max(lengthPerStrand)
    return list(NormalizedLengthYPerStrand)


def interpol(verts, t_in, uniform_spacing=True, noiseStrandSeparation=0, same_point_count=True,  shortenStrandLen=0.0):
    """ verts, t-ins - output len (by defaut constant unless same_point_count == False
    uniform_spacing - uniform point spacing
    same_point_count - same number of points for each strand. Else less points for shorter strands
    """
    if t_in == -1:
        t_in = 3  # we will use middle one as output single output curve
    verts_out = []
    # DONE: randomize spacing by randomizing   t_ins? +- rand dt (same dt over length
    if noiseStrandSeparation != 0:
        rand_delta_t_ins = 2*np.random.rand(t_in) - 1
    t_ins = []
    if not same_point_count:
        NormalizedStrandsLength = get_strand_proportions(verts)
        for strandLen in NormalizedStrandsLength:
            # segment count (t_in-1) (!=point count) ) + 1 (cos n segment line, has n+1 points)
            t_Normalized = max(ceil((t_in-1) * strandLen), 2)+1  # ceil or round...
            t_ins.append([i / (t_Normalized - 1) for i in range(int(t_Normalized))])
    else:
        t_uniform = [i / (t_in - 1) for i in range(t_in)]
        t_ins = np.repeat([t_uniform], len(verts), axis=0)

    for v, t_in in zip(verts, t_ins):  # TODO: change to take irregural v len (and t_in len)
        vCount = len(v)
        domain = [i / (vCount - 1) for i in range(vCount)]
        pts = np.array(v).T
        tmp = np.apply_along_axis(np.linalg.norm, 0, pts[:, :-1]-pts[:, 1:])  # do an - an-1 and get length
        t = np.insert(tmp, 0, 0).cumsum()  # add zero and sum
        #t will containt time = dist between neighbor knots normalized
        t = t/t[-1]  # normalize; it contains info about <tn, tn+1> for spline n

        corr_t_ins = np.array(t_in)
        if not uniform_spacing:  # do lin interp for spacing instead of even spacing
            corr_t_ins = np.interp(t_in, domain, t)  # don't do  t_ins = np.interp(t_ins,arg , t) ever!!
            #interolate t_ins to t by linear iterpol

        # t_corr = [min(1, max(t_c, 0)) for t_c in t_in] # map to <0,1> range
        if noiseStrandSeparation != 0:
            deltaMargin = corr_t_ins[1:]-corr_t_ins[:-1]  # AN-A(N-1)
            deltaMargin = np.append(deltaMargin, 0) + np.insert(deltaMargin, 0, 0)  # A(N-1) - AN + A(N-2) - A(N-1)
            corr_t_ins = corr_t_ins+rand_delta_t_ins*deltaMargin*noiseStrandSeparation

        if shortenStrandLen > 0:  # randomize strand len by randomizing output domain len <0,1> to <0,x)
            corr_t_ins = (1.0-np.random.uniform(0, shortenStrandLen)) * corr_t_ins
        spl = cubic_spline(v, t)  # retunrs [Ak, Bk, Ck, Dk] spline coeff for segment k.
        out = eval_spline(spl, t, corr_t_ins)
        verts_out.append(out)
    return verts_out


def get2dInterpol(verts, IntervalX, IntervalY, shortenStrandLen, Seed, x_uniform, y_uniform, noiseStrandSeparation):
    np.random.seed(Seed)
    interpol_hair_number = interpol(verts, IntervalX, x_uniform, noiseStrandSeparation=noiseStrandSeparation)  # do spline number interpol
    hairNumber_firstRow = interpol_hair_number[0]
    hairNumber_afterFirst = interpol_hair_number[1:]
    verts_T = np.swapaxes(np.array(hairNumber_afterFirst), 0, 1).tolist()
    np.random.seed(Seed)
    interpol_length = interpol(verts_T, IntervalY, y_uniform, shortenStrandLen=shortenStrandLen)  # do interpol over strand points
    verts_for_addition = np.swapaxes(np.array(interpol_length), 0, 1).tolist()  # revert Transpose for addition
    # verts_for_addition has now curve points beggining curve points [a1,a2,a3...] after interpolation

    addedFirstRow = [hairNumber_firstRow] + verts_for_addition

    strandsPoints = np.swapaxes(np.array(addedFirstRow), 0, 1).tolist()  # it has strands [a1,b1,c1],[a2,b2,c2]...

    # if shortenRandomize and shortenStrandLen!=0:
    #     shortenDist = np.random.randint(0, shortenStrandLen, len(strandsPoints))
    # else:
    #     shortenDist = np.array(len(strandsPoints) * [shortenStrandLen])
    # for i,strand in enumerate(strandsPoints): #reduce strands len by random_int(shortenStrand)
    #     if shortenDist[i] > 0:
    #         strandsPoints[i] = strand[:-shortenDist[i]]
    if IntervalX == -1:
        return [strandsPoints[1]]
    else:
        return strandsPoints
