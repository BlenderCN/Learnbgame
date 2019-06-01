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


    ##########################################################################################
    #    THE VOXEL DATA FORMAT NEEDED FOR THE MITSUBA 
    ##########################################################################################
    #
    #Bytes 1-3     VOL in ASCII
    #Byte 4        File format version number (currently 3)
    #Bytes 5-8     Encoding identifier (32-bit integer).The following choices are available:
    #
    #            1. Dense float32-based representation
    #            2. Dense float16-based representation (currently not supported by this implementation)
    #            3. Dense uint8-based representation (The range 0..255 will be mapped to 0..1)
    #            4. Dense quantized directions. The directions are stored in spherical coordinates
    #                        with a total storage cost of 16 bit per entry.
    #            
    #Bytes 9-12     Number of cells along the X axis (32 bit integer)
    #Bytes 13-16    Number of cells along the Y axis (32 bit integer)
    #Bytes 17-20    Number of cells along the Z axis (32 bit integer)
    #Bytes 21-24    Number of channels (32 bit integer, supported values: 1 or 3)
    #Bytes 25-48    Axis-aligned bounding box of the data stored in single precision (order:
    #               xmin, ymin, zmin, xmax, ymax, zmax)
    #Bytes 49-*     Binary data of the volume stored in the specified encoding. The data
    #               are ordered so that the following C-style indexing operationmakes sense
    #               after the file has been mapped into memory:
    #               data[((zpos*yres + ypos)*xres + xpos)*channels + chan]
    #               where (xpos, ypos, zpos, chan) denotes the lookup location.
    #
    #Example : 
    #    56 4F 4C 33    01 00 00 00    10 00 00 00    10 00 00 00      ||  VOL3 1 3 3
    #    10 00 00 00    01 00 00 00    FF FF FF FF    FF FF FF FF      ||  3 1 -1 -1
    #    FF FF FF FF    01 00 00 00    01 00 00 00    01 00 00 00      ||  -1 1 1 1  
    #    -------------------------------------------------------------
    #     THE REST IS THE CONTENT  3*3*3 =  27 times
    ############################################################################################

from ctypes import cdll, c_uint, c_float, cast, POINTER, byref, sizeof

import os, struct, sys ,bpy

class library_loader():
    
    load_lzo_attempted  = False
    load_lzma_attempted = False        
    has_lzo     = False
    lzodll      = None    
    has_lzma    = False
    lzmadll     = None
    
    platform_search = {
        'lzo': {
            'linux': [
                '/usr/lib/liblzo2.so',
                '/usr/lib/liblzo2.so.2',
                '/usr/lib64/liblzo2.so',
                '/usr/lib64/liblzo2.so.2'
            ],
            'linux2': [
                '/usr/lib/liblzo2.so',
                '/usr/lib/liblzo2.so.2',
                '/usr/lib64/liblzo2.so',
                '/usr/lib64/liblzo2.so.2'
            ]
        },
        'lzma': {
            'linux': [
                '/usr/lib/liblzma.so',
                '/usr/lib/liblzma.so.2',
                '/usr/lib64/liblzma.so'
            ],
            'linux2': [
                '/usr/lib/liblzma.so',
                '/usr/lib/liblzma.so.2',
                '/usr/lib64/liblzma.so'
            ]
        }
    }
    
    @classmethod
    def load_lzo(cls):
        # Only attempt load once per session
        if not cls.load_lzo_attempted:
            
            for sp in cls.platform_search['lzo'][sys.platform]:
                try:
                    cls.lzodll = cdll.LoadLibrary(sp)
                    cls.has_lzo = True
                    break
                except Exception as e:
                    print(e)
            
            if cls.has_lzo:
                print('Volumes: LZO Library found')
            else:
                print('Volumes: LZO Library not found')
            
            cls.load_lzo_attempted = True
        
        return cls.has_lzo, cls.lzodll
    
    @classmethod
    def load_lzma(cls):
        # Only attempt load once per session
        print(sys.platform)
        if not cls.load_lzma_attempted:
            
            for sp in cls.platform_search['lzma'][sys.platform]:
                try:
                    cls.lzmadll = cdll.LoadLibrary(sp)
                    cls.has_lzma = True
                    break
                except Exception as e:
                    print(e)
            
            if cls.has_lzma:
                print('Volumes: LZMA Library found')
            else:
                print('Volumes: LZMA Library not found')
            
            cls.load_lzma_attempted = True
        
        return cls.has_lzma, cls.lzmadll

    
    
class reading_cache_data():
    
    SZ_FLOAT    = sizeof(c_float)
    SZ_UINT     = sizeof(c_uint)
    
    @classmethod
    def read_data_segment(    
    
    
self, cachefile, cell_count):
        compression     = 0
        binary_file     = None    
        steam_file      = None
        steam_size      = 0  
        props_file      = None
        props_size      = None    
            
        compression = struct.unpack("1B", cachefile.read(1))[0]        
        if not compression:
            binary_file = cachefile.read(self.SZ_FLOAT *cell_count)
            return (compression,binary_file,0,None,0)
        else:
            steam_size = struct.unpack("1I", cachefile.read(self.SZ_UINT))[0]        
            steam_file = cachefile.read(steam_size)
            if compression == 2:
                props_size = struct.unpack("1I", cachefile.read(self.SZ_UINT))[0]
                props_file = cachefile.read(props_size)            
            return (compression,steam_file, steam_size, props_file , props_size)
           
    @classmethod  
    def decompressing_data(self, data, cell_count):
        list    = []
        outlen  = c_uint()
        
        if data[0] == 1:
            has_lzo, lzodll = library_loader.load_lzo()
            if has_lzo:
                print('Volumes: De-compressing LZO stream of length {0:0d} bytes...'.format(data[2]))                            
                uncomp_stream   = (c_float*cell_count*self.SZ_FLOAT)()
                p_dens          = cast(uncomp_stream, POINTER(c_float))                                           
                #call lzo decompressor
                lzodll.lzo1x_decompress(data[1], data[2], p_dens,byref(outlen), None)
                print("Out length: %s" % (str(outlen)))                
                for i in range(int(outlen.value / 4) ):
                    list.append(p_dens[i])
            else:
                print('Volumes: Cannot read compressed LZO stream; no library loaded')                        
        elif data[0] == 2:
            has_lzma, lzmadll = library_loader.load_lzma()
            if has_lzma:
                print('Volumes: De-compressing LZMA stream of length {0:0d} bytes...'.format(data[2]))                            
                uncomp_stream   = (c_float*cell_count*self.SZ_FLOAT)()
                p_dens          = cast(uncomp_stream, POINTER(c_float))
                outlen          = c_uint(cell_count*SZ_FLOAT)                            
                #call lzma decompressor                            
                lzmadll.LzmaUncompress(p_dens, byref(outlen), data[1], byref(c_uint(data[1])), data[3], data[4])
                                
                for i in range(int(outlen.value / 4) ):
                    list.append(p_dens[i])
            else:
                print('Volumes: Cannot read compressed LZMA stream; no library loaded')
        else :                          
           #TODO: extrect so that it will be OK            
           list = struct.unpack(str(int(len(data[1])/4))+"f",data[1])
           """
                        elif heat_data[0] == 0:
                            pass
                            ""
                            print("Length uncompress heat: %i" % (len(heat) / 4))
                            print("Length uncompress heat: %i" % (cell_count))
                            #TODO : I don't think that it needs to be devided a^3 only if its high resolution
                            if is_high_res:                                
                                cells  = int(res_x*res_y*res_z) 
                            else :
                                cells = int(cell_count)                                 
                            heat = struct.unpack(str(cells)+"f",heat_binary)
            """
        return list
    
    @classmethod
    def read_cache(self, smokecache, is_high_res, amplifier, flowtype):
        
        # NOTE - dynamic libraries are not loaded until needed, further down
        # the script...
        
        ###################################################################################################
        # Read cache
        # Pointcache file format v1.04:
        #    name                                   size of uncompressed data
        #--------------------------------------------------------------------------------------------------
        #    header                                   ( 20 Bytes)
        #    data_segment for shadow values           ( cell_count * sizeof(float) Bytes)
        #    data_segment for density values          ( cell_count * sizeof(float) Bytes)
        #    data_segment for heat values             ( cell_count * sizeof(float) Bytes)
        #    data_segment for heat, old values        ( cell_count * sizeof(float) Bytes)
        #    data_segment for vx values               ( cell_count * sizeof(float) Bytes)
        #    data_segment for vy values               ( cell_count * sizeof(float) Bytes)
        #    data_segment for vz values               ( cell_count * sizeof(float) Bytes)
        #    data_segment for obstacles values        ( cell_count * sizeof(char) Bytes)    
        # if simulation is high resolution additionally:
        #    data_segment for density values          ( big_cell_count * sizeof(float) Bytes)
        #    data_segment for tcu values              ( cell_count * sizeof(u_int) Bytes)
        #    data_segment for tcv values              ( cell_count * sizeof(u_int) Bytes)
        #    data_segment for tcw values              ( cell_count * sizeof(u_int) Bytes)
        #
        # header format:
        #    BPHYSICS                (Tag-String, 8 Bytes)
        #    data type               (u_int, 4 Bytes)        => 3 - PTCACHE_TYPE_SMOKE_DOMAIN
        #    cell count              (u_int, 4 Bytes)        Resolution of the smoke simulation
        #    user data type          (u_int int, 4 Bytes)    not used by smoke simulation
        #
        # data segment format:
        #    compressed flag         (u_char, 1 Byte)            => 0 - uncompressed data,
        #                                                           1 - LZO compressed data,
        #                                                           2 - LZMA compressed data
        #    stream size             (u_int, 4 Bytes)            size of data stream (compression 1 and 2)
        #    data stream             (u_char,(stream_size)Bytes) data stream
        #
        # if lzma-compressed additionally:
        #    props size              (u_int, 4 Bytes)            size of props ( has to be 5 Bytes)
        #    props                   (u_char,(props_size)Bytes)  props data for lzma decompressor
        #
        ###################################################################################################
        
        density             = []
        fire                = []    
        heat                = []
        heat_old            = []
        cell_count          = 0
        res_x               = 0
        res_y               = 0
        res_z               = 0
        cachefilepath       = []
        cachefilename       = []
        #if not smokecache.is_baked:
        if False:
            print('Volumes: Smoke data has to be baked for export')
        else:        
            cachefilename = smokecache 
            fullpath = os.path.join( cachefilepath, cachefilename )
            if not os.path.exists(fullpath):
                print('Volumes: Cachefile doesn''t exist: %s' % fullpath)
            else:
                cachefile   = open(fullpath, "rb")
                buffer      = cachefile.read(8)
                temp        = ""
                stream_size = c_uint()
                props_size  = c_uint()
                outlen      = c_uint()
                compressed  = 0
                            
                for i in range(len(buffer)):
                    temp = temp + chr(buffer[i])        
                
                if temp == "BPHYSICS":    #valid cache file
                    data_type = struct.unpack("1I", cachefile.read(self.SZ_UINT))[0]                    
                    if (data_type == 3) or (data_type == 4):
                        cell_count = struct.unpack("1I", cachefile.read(self.SZ_UINT))[0]                        
                        struct.unpack("1I", cachefile.read(self.SZ_UINT))[0]
                        
                        last_pos    = cachefile.tell()
                        buffer      = cachefile.read(4)
                        temp        = ""             
                        new_cache   = False       
                        
                        for i in range(len(buffer)):
                            temp = temp + chr(buffer[i])                    
                        if temp[0] >= '1' and temp[1] == '.':
                            new_cache = True
                        else:
                            cachefile.seek(last_pos)
                        
                        # Try to read new header
                        if new_cache:
                            # number of fluid fields in the cache file
                            fluid_fields     = struct.unpack("1I", cachefile.read(self.SZ_UINT))[0]
                            active_fields    = struct.unpack("1I", cachefile.read(self.SZ_UINT))[0]
                            res_x            = struct.unpack("1I", cachefile.read(self.SZ_UINT))[0]
                            res_y            = struct.unpack("1I", cachefile.read(self.SZ_UINT))[0]
                            res_z            = struct.unpack("1I", cachefile.read(self.SZ_UINT))[0]
                            dx               = struct.unpack("1I", cachefile.read(self.SZ_UINT))[0]
                            cell_count       = res_x*res_y*res_z                        
                        
                        # Shadow values
                        self.read_data_segment(cachefile, cell_count)                    
                        # Density values
                        density_data = self.read_data_segment(cachefile, cell_count)                    
                        # Density, old values
                        if not new_cache:                        
                            density_data = self.read_data_segment(cachefile, cell_count)                       
                        # Heat values
                        heat_data = self.read_data_segment(cachefile, cell_count)                                       
                        # Heat, old values
                        heat_old_data = self.read_data_segment(cachefile, cell_count)                          
                        # Fire values
                        if new_cache and flowtype >= 1:
                            # Fire values
                            fire_data = self.read_data_segment(cachefile, cell_count)                        
                            # Fuel values
                            self.read_data_segment(cachefile, cell_count)                        
                            # React values
                            self.read_data_segment(cachefile, cell_count)
                                    
#                            if new_cache and flowtype >= 1:
#                               #active colors
#                                # r values
#                                self.read_data_segment(cachefile, cell_count)
#                                # g values
#                                self.read_data_segment(cachefile, cell_count)
#                                # b values
#                                self.read_data_segment(cachefile, cell_count)
                                        
                        if is_high_res:
                            # vx values
                            self.read_data_segment(cachefile, cell_count)                        
                            # vy values
                            self.read_data_segment(cachefile, cell_count)                        
                            # vz values
                            self.read_data_segment(cachefile, cell_count)
                                   
                            if not new_cache:
                                # vx, old values
                                self.read_data_segment(cachefile, cell_count)                            
                                #vy,old values
                                self.read_data_segment(cachefile, cell_count)                            
                                # vz,old values
                                self.read_data_segment(cachefile, cell_count)                            
        
                            # Obstacle values
                            self.read_data_segment(cachefile, cell_count)                        
                            # dt value
                            cachefile.read(self.SZ_FLOAT)
                            # dx value
                            cachefile.read(self.SZ_FLOAT)
    
                            if new_cache:
                                #p0
                                cachefile.read(3*self.SZ_FLOAT)
                                #p1
                                cachefile.read(3*self.SZ_FLOAT)
                                #dp0
                                cachefile.read(3*self.SZ_FLOAT)
                                #shift
                                cachefile.read(3*self.SZ_UINT)
                                #obj_shift_f 
                                cachefile.read(3*self.SZ_FLOAT)
                                #obmat
                                cachefile.read(16*self.SZ_FLOAT)
                                #base_res
                                cachefile.read(3*self.SZ_UINT)
                                #res min
                                cachefile.read(3*self.SZ_UINT)
                                #res max
                                cachefile.read(3*self.SZ_UINT)
                                #active color
                                cachefile.read(3*self.SZ_FLOAT)
    
                            # High resolution                    
                            cell_count = cell_count * amplifier * amplifier * amplifier                        
                            # Density values                        
                            density_data = self.read_data_segment(cachefile, cell_count)                            
                            # Fire values
                            if new_cache and flowtype >= 1:
                                fire_data = self.read_data_segment(cachefile, cell_count)                                                               
#                                # Fuel values                        
#                                read_data_segment(cachefile, cell_count)
                           
                        ### DECOMPRESSING DATA  ###
                        print ("Density compression : %s" %density_data[0])
                        density = self.decompressing_data(density_data, cell_count)
                        cell_count       = res_x*res_y*res_z
                        print ("Heat compression : %s" %heat_data[0])
                        heat    = self.decompressing_data(heat_data, cell_count)
                        print ("Heat old compression : %s" %heat_old_data[0])
                        heat_old= self.decompressing_data(heat_old_data, cell_count)
                        if new_cache and flowtype >= 1:
                            fire = self.decompressing_data(fire_data, cell_count)       
                                                                            
                cachefile.close()                
                return (res_x, res_y, res_z, density, fire, heat ,heat_old)
        return (0,0,0,[],[],[],[])

class volumes(object):
 
 
    def get_color(self, value, c):
        l = len(c)-1
        color = []        
        if value <= c[0][0]:
            color =[c[0][1], c[0][2], c[0][3]]                    
        elif value >= c[l][0]:
            color =[c[l][1], c[l][2], c[l][3]]            
        else :
            for i in range(l):
                if value > c[i][0] and  value <= c[i+1][0] :
                    b = (value - c[i][0])/(c[i+1][0] - c[i][0])                
                    for u in range(3):
                        color.append(c[i][u+1] * (1 - b) + c[i+1][u+1]*b)                            
        return struct.pack("3f",color[0],color[1],color[2])
    
    
    def write_to_file(self,file, data, format):
        packed = struct.pack(format , data)
        file.write(packed)  
    
    def get_scale(self):
        t = 0.0
        for i in bpy.data.objects :
            try :
                if i.modifier['Smoke'].smoke_type == "FLOW" :
                    x = abs(i.modifier['Smoke'].flow_settings.temperature)
                    if x > t :
                        t = x
            except :
                pass 
        if t == 0.0 :
            return 5.0
        else :
            return t
        
    def get_dimention(self,obj):    
        #TODO: Change if for the adaptive domain
        x_max, y_max, z_max = obj.matrix_world * obj.data.vertices[0].co
        x_min, y_min, z_min = x_max, y_max, z_max 
        for i in obj.data.vertices:
            world = i.co * obj.matrix_world
            if world[0] > x_max :
                x_max = world[0]
            elif world[0] < x_min :
                x_min = world[0] 
            if world[1] > y_max :
                y_max = world[1]
            elif world[1] < y_min :
                y_min = world[1]
            if world[2] > z_max :
                z_max = world[2]
            elif world[2] < z_min :
                z_min = world[2]            
        return (x_min, y_min, z_min, x_max, y_max, z_max)
            
    def get_color_ramp(self,obj,scale):
        colors  = []
        ramp    = None
        try : 
            for x in obj.active_material.texture_slots:
                if x != None :
                    t = x.texture
                    if t.type == 'VOXEL_DATA' and t.use_color_ramp and t.voxel_data.smoke_data_type=='SMOKEHEAT' :
                        ramp = t.color_ramp.elements                        
            if ramp != None :        
                for i in ramp :            
                    p       = float((i.position - 0.5 ) * scale)            
                    t   = (p,i.color[0],i.color[1],i.color[2])
                    colors.append(t)
                colors.sort()
        except :
            pass        
        return colors  
        
    def smoke_convertion(self , report, sourceName, destination, frame, obj):
        Amplificator     = 0
        flowtype         = 0        
        if not os.path.exists(sourceName):
            report({'ERROR'}, 'File could not be found :  %s ' %str(sourceName))
            return False
        
        if (obj.modifiers['Smoke'].type != 'SMOKE'):
            report({'ERROR'}, 'Could not find the Smoke modifier (1)')
            return False
        else :
            if(obj.modifiers['Smoke'].domain_settings.use_high_resolution):                    
                Amplificator = obj.modifiers['Smoke'].domain_settings.amplify
        
        cache = reading_cache_data()
        print("Amplify: %i" % Amplificator)
        print("Source Name : %s"%sourceName)
        res_x, res_y, res_z, den, fire, hn, heat = cache.read_cache(sourceName, Amplificator != 0, Amplificator+1, flowtype)
        int32format     ='i'
        float32format   ='f'
        density_loc     = str(destination) + "/voxel_"+ str(obj.name) + "_"+ str(frame) +".vol"
        heat_loc        = str(destination) +  '/heat_'+ str(obj.name) + '_'+ str(frame) +'.vol'
    
        density_file     = open(density_loc,'wb')
        heat_file        = open(heat_loc,'wb')        
        ### WRITEING THE HEADER ###
        density_file.write(bytes('VOL\x03', 'UTF-8'))
        heat_file.write(bytes('VOL\x03', 'UTF-8'))

        data = struct.pack(int32format , 1)
        density_file.write(data)
        heat_file.write(data)
        # dimention
        print("Dim: %ix%ix%i" % (res_x, res_y, res_z))
        self.write_to_file(density_file, res_x*(Amplificator+1), int32format)        
        self.write_to_file(density_file, res_y*(Amplificator+1), int32format)        
        self.write_to_file(density_file, res_z*(Amplificator+1), int32format)
        self.write_to_file(heat_file, res_x, int32format)
        self.write_to_file(heat_file, res_y, int32format)
        self.write_to_file(heat_file, res_z, int32format)       
        #chanels    
        self.write_to_file(density_file, 1, int32format)        #one float / voxel    
        self.write_to_file(heat_file, 3, int32format)           #  3 float / voxel
        # Domain Size  :  Xmin, Ymin, Zmin, Xmax, Ymax, Zmax
        dim = self.get_dimention(obj)
        print("%s %s %s %s %s %s"%dim)        
        for i in range(6):
              self.write_to_file(density_file, dim[i], float32format)
              self.write_to_file(heat_file ,   dim[i], float32format)
              
        ### WRITEING THE VOXEL DATA ###
        print("Length Density: %s"%str(len(den)))
        for i in den:
            self.write_to_file(density_file, i, float32format)   
        density_file.close()
        
        heat_scale  = self.get_scale()                
        colors = self.get_color_ramp(obj,heat_scale)
        if colors == [] :
            colors = [[0.15 ,0.9, 0.0, 0.0],[-0.15, 0.0, 0.0, 0.9]]

        print("Length Heat   : %s"%str(len(heat)))
        for i in heat:
            heat_file.write(self.get_color(i, colors))
        heat_file.close()
        return (density_loc, heat_loc)