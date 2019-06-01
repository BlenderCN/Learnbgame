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
from math import ceil
# import sys
# dir = 'C:\\Users\\JoseConseco\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages'
# if not dir in sys.path:
#     sys.path.append(dir )
# import ipdb
# calculates natural cubic splines through all given knots
def cubic_spline(locs, tknots):
    knots = list(range(len(locs)))

    n = len(knots)
    if n < 2:
        return False
    x = tknots[:]
    result = []
    for j in range(3): #x, y, z
        a = [loc[j] for loc in locs]
        h = [max(1e-8,x[i+1] - x[i]) for i in range(n-1) ]
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
        n = max(min(n,len(splines)-1),0)
        # pt = []
        # for i in range(3):
        #     ax, bx, cx, dx, tx = splines[n][i]
        #     x = ax + bx*(t-tx) + cx*(t-tx)**2 + dx*(t-tx)**3
        #     pt.append(x)
        pt = [splines[n][i][0] + splines[n][i][1]*(t-splines[n][i][4]) + splines[n][i][2]*(t-splines[n][i][4])**2 + splines[n][i][3]*(t-splines[n][i][4])**3 for i in range(3)]
        out.append(pt)
    return out


def get_strand_proportions(strandsList):  #return array <0,1> - where 1 is for longest strand
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

def interpol(verts, t_in, uniform = True, noiseStrandSeparation = 0, constantLen = True,  shortenStrandLen=0.0):
    """ verts, t-ins - output len (by defaut constant unless constantLen == False
    uniform - uniform point spacing
    constantLen - same number of points for each strand. Else less points for shorter strands
    """
    if t_in == -1:
        t_in = 3 # we will use middle one as output single output curve
    verts_out = []
    # DONE: randomize spacing by randomizing   t_ins? +- rand dt (same dt over length
    if noiseStrandSeparation != 0:
        rand_delta_t_ins = 2*np.random.rand(t_in) - 1
    t_ins = []
    if not constantLen:
        NormalizedStrandsLength = get_strand_proportions(verts)
        for strandLen in NormalizedStrandsLength:
            # segment count (t_in-1) (!=point count) ) + 1 (cos n segment line, has n+1 points)
            t_Normalized = max(ceil((t_in-1) * strandLen), 2)+1  #ceil or round...
            t_ins.append([i / (t_Normalized - 1) for i in range(int(t_Normalized))])
    else:
        t_uniform = [i / (t_in - 1) for i in range(t_in)]
        t_ins=np.repeat([t_uniform], len(verts), axis=0)

    for v, t_in in zip(verts, t_ins):  #TODO: change to take irregural v len (and t_in len)
        vCount = len(v)
        domain = [i / (vCount - 1) for i in range(vCount)]
        pts = np.array(v).T
        tmp = np.apply_along_axis(np.linalg.norm, 0, pts[:, :-1]-pts[:, 1:]) #do an - an-1 and get length
        t = np.insert(tmp, 0, 0).cumsum() #add zero and sum
        #t will containt time = dist between neighbor knots normalized
        t = t/t[-1]  #normalize; it contains info about <tn, tn+1> for spline n

        corr_t_ins = np.array(t_in)
        if not uniform: #do lin interp for spacing instead of even spacing
            corr_t_ins = np.interp(t_in, domain , t)  #don't do  t_ins = np.interp(t_ins,arg , t) ever!!
            #interolate t_ins to t by linear iterpol

        # t_corr = [min(1, max(t_c, 0)) for t_c in t_in] # map to <0,1> range
        if noiseStrandSeparation!=0:
            deltaMargin = corr_t_ins[1:]-corr_t_ins[:-1]  #AN-A(N-1)
            deltaMargin = np.append(deltaMargin,0) + np.insert(deltaMargin, 0, 0) # A(N-1) - AN + A(N-2) - A(N-1)
            corr_t_ins = corr_t_ins+rand_delta_t_ins*deltaMargin*noiseStrandSeparation

        if shortenStrandLen>0: #randomize strand len by randomizing output domain len <0,1> to <0,x)
            corr_t_ins = (1.0-np.random.uniform(0,shortenStrandLen)) * corr_t_ins
        spl = cubic_spline(v, t)  #retunrs [Ak, Bk, Ck, Dk] spline coeff for segment k.
        out = eval_spline(spl, t, corr_t_ins)
        verts_out.append(out)
    return verts_out


def get2dInterpol(verts, IntervalX, IntervalY, shortenStrandLen, Seed, x_uniform, y_uniform, noiseStrandSeparation):
    np.random.seed(Seed)
    interpol_hair_number = interpol(verts, IntervalX, x_uniform, noiseStrandSeparation=noiseStrandSeparation)  #do spline number interpol
    hairNumber_firstRow = interpol_hair_number[0]
    hairNumber_afterFirst = interpol_hair_number[1:]
    verts_T = np.swapaxes(np.array(hairNumber_afterFirst),0,1).tolist()
    np.random.seed(Seed)
    interpol_length = interpol(verts_T, IntervalY, y_uniform, shortenStrandLen=shortenStrandLen) #do interpol over strand points
    verts_for_addition = np.swapaxes(np.array(interpol_length), 0, 1).tolist() #revert Transpose for addition
    # verts_for_addition has now curve points beggining curve points [a1,a2,a3...] after interpolation

    addedFirstRow = [hairNumber_firstRow] + verts_for_addition

    strandsPoints = np.swapaxes(np.array(addedFirstRow), 0, 1).tolist()  #it has strands [a1,b1,c1],[a2,b2,c2]...

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






