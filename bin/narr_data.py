import numpy
import linecache
import image_processing as img_proc
import utm
import math
import os

def choose_points(coordinate_file, metadata, buoy_coors):
    """ Read in coordinates.txt, choose points within scene corners. """
    # read narr coordinates from file
    coordinates = []

    with open(coordinate_file, 'r') as f:
        for line in f:
            line.replace('\n', '')
            coordinates.append(line.split())

    # pull out i,j,lat, lon and reform to 277x349 grids
    coordinates = numpy.asarray(coordinates)
    i_coor = numpy.empty((len(coordinates)))
    j_coor = numpy.empty((len(coordinates)))
    
    i_coor = [c[0] for c in coordinates]
    i_coor = numpy.reshape(i_coor,(277,349)).astype(float)

    j_coor = [c[1] for c in coordinates]
    j_coor = numpy.reshape(j_coor,(277,349)).astype(float)
     
    narrLat = [c[2] for c in coordinates]
    lat = numpy.reshape(narrLat,(277,349)).astype(float)

    narrLon = [c[3] for c in coordinates]
    east = numpy.where(narrLon > 180.0)
    
    for x in range(len(east[0])):
        narrLon[east[0][x]] = 360.0 - float(narrLon[east[0][x]])
    west = numpy.where(narrLon < 180.0)
    for x in range(len(west[0])):
        narrLon[west[0][x]] = (-1)*float(narrLon[west[0][x]])
    lon = numpy.reshape(narrLon,(277,349)).astype(float)

    if metadata['CORNER_UL_LAT_PRODUCT'] > 0:
        landsatHemi = 6
    else: 
        landsatHemi = 7
    
    UL_X = metadata['CORNER_UL_LAT_PRODUCT'] + 0.5
    UL_Y = metadata['CORNER_UL_LON_PRODUCT'] - 0.5
    LR_X = metadata['CORNER_LR_LAT_PRODUCT'] - 0.5
    LR_Y = metadata['CORNER_LR_LON_PRODUCT'] + 0.5
    
    inLandsat = numpy.asarray([[None,None],[None,None]])
    x_iter = numpy.arange(277)
    
    for k in x_iter:
        try:
        
            for l in xrange(len(lat[1])-1):
                if lon[k,l] > 180:
                    lon[k,l] = 360 - lon[k,l]
                else: 
                    lon[k,l] = (-1)*lon[k,l]
                if lat[k,l] > 84:
                    lat[k,l] = 84
                    
                curr_utm_point = utm.from_latlon(lat[k,l], lon[k,l])
                
                if curr_utm_point[2] <= float(metadata['UTM_ZONE']) + 1 and curr_utm_point[2] >= float(metadata['UTM_ZONE']) - 1:
                    curr_utm_point = img_proc.convert_utm_zones(lat[k,l], lon[k,l], curr_utm_point[2], metadata['UTM_ZONE'])
                
                    if curr_utm_point[0] < UL_X:
                        if curr_utm_point[0] > LR_X:
                           if curr_utm_point[1] > UL_Y:
                               if curr_utm_point[1] < LR_Y:
                                   inLandsat = numpy.append(inLandsat, [[k,l]], axis=0)
                
        except IndexError as i:
            print 'IndexError', i
            
    inLandsat = numpy.delete(inLandsat, 0, 0)
    inLandsat = numpy.delete(inLandsat, 0, 0)
    
    num_points = numpy.shape(inLandsat)[0]
    
    if num_points == 0:
        print 'No NARR points in landsat scene. Fatal.'
        sys.exit(-1)
    
    latvalues = []
    lonvalues = []
    ivalues = []
    jvalues = []
    
    for i in range(num_points):
        latvalues.append(lat[inLandsat[i,0],inLandsat[i,1]])
        lonvalues.append(lon[inLandsat[i,0],inLandsat[i,1]])
        ivalues.append(i_coor[inLandsat[i,0],inLandsat[i,1]])
        jvalues.append(j_coor[inLandsat[i,0],inLandsat[i,1]])
    
    pixelSize = metadata['GRID_CELL_SIZE_THERMAL']

    eastvector = []
    northvector = []
    
    for i in range(num_points): 
        narr_utm_ret = utm.from_latlon(latvalues[i],lonvalues[i])
        eastvector.append(narr_utm_ret[0])
        northvector.append(narr_utm_ret[1])
        
    eastvector = numpy.asarray(eastvector)
    northvector = numpy.asarray(northvector)

    buoy_x = utm.from_latlon(buoy_coors[0], buoy_coors[1])[0]
    buoy_y = utm.from_latlon(buoy_coors[0], buoy_coors[1])[1]

    distances = []
    dist_idx = []

    for g in range(num_points):
        try:
            dist = distance_in_utm(eastvector[g],northvector[g],buoy_x,buoy_y)
            if dist > 0:
                distances.append(dist) 
                dist_idx.append(g)
        except IndexError as e:
            print e

    narr_dict = dict(zip(distances, dist_idx))
    idx = []

    closest = sorted(narr_dict)
    
    for m in range(4):
        idx.append(narr_dict[closest[m]])
    
    NARRindices = []
    for n in idx:
        NARRindices.append(list(inLandsat[n]))
    
    NARRindices = numpy.asarray(NARRindices)
    num_points = 4    # do not remove, important
    
    return NARRindices, num_points, lat, lon
    
    
def read(narr_indices, lat, scene_dir):
    p = numpy.asarray([1000, 975, 950, 925, 900, 875, 850, 825, 800, 775, 750, 725, 700, 650, 600, 550, 500, 450, 400, 350, 300, 275, 250, 225, 200, 175, 150, 125, 100])
    pressures = numpy.reshape([p]*4, (4,29))
    dirs = ['HGT_1', 'HGT_2', 'TMP_1', 'TMP_2', 'SHUM_1', 'SHUM_2']
    
    shape = [277,349]
    indices = [numpy.ravel_multi_index(idx, shape) for idx in narr_indices]
    
    data = [[] for i in range(6)]
    
    for d in dirs:
        for i in indices:
            for press in p:
                filename = os.path.join(scene_dir, 'narr', d, str(press)+'.txt')
                data[dirs.index(d)].append(float(linecache.getline(filename, i+2)))
    
    data = numpy.reshape(data, (6, 4, 29))  # reshape
    hgt_1, hgt_2, tmp_1, tmp_2, shum_1, shum_2 = data   # unpack
    
    rhum_1 = convert_sh_rh(shum_1, tmp_1, pressures)
    rhum_2 = convert_sh_rh(shum_2, tmp_2, pressures)
    
    ght_1 = numpy.divide(hgt_1, 1000.0)   # convert m to km
    ght_2 = numpy.divide(hgt_2, 1000.0)   # convert m to km
    
    return ght_1, ght_2, tmp_1, tmp_2, rhum_1, rhum_2, pressures
        
def convert_sh_rh(specHum, T_k, pressure):
    # Given array of specific humidities, temperature, and pressure, generate array of relative humidities
    # source: http://earthscience.stackexchange.com/questions/2360/how-do-i-convert-specific-humidity-to-relative-humidity
    
    T_k = numpy.asarray(T_k, dtype=numpy.float64)  #numpy.float64
    
    # convert input variables
    T_c = numpy.subtract(T_k, 273.15)   #celcius
    q = specHum   #specific humidity
    p = pressure   #pressures
    
    # compute relative humidity
    a = numpy.divide(numpy.multiply(17.67, T_c), numpy.subtract(T_k, 29.65))
    
    rh = 26.3 * p * q * (1 / numpy.exp(a))
    
    return rh
        
def convert_geopotential_geometric(geopotential, lat):
    """Convert array of geopotential heightsto geometric heights.
    """
    # source: http://www.ofcm.gov/fmh3/pdf/12-app-d.pdf
    # http://gis.stackexchange.com/questions/20200/how-do-you-compute-the-earths-radius-at-a-given-geodetic-latitude
    
    # convert latitiude to radians
    radlat = (lat * math.pi) / 180.0
    
    # gravity at latitude
    grav_lat = 9.80616 * (1 - 0.002637 * numpy.cos(2 * radlat) + 0.0000059 * numpy.power(numpy.cos(2 * radlat), 2))

    # radius of earth at latitude: R(f)^2 = ( (a^2 cos(f))^2 + (b^2 sin(f))^2 ) / ( (a cos(f))^2 + (b sin(f))^2 )
    R_max = 6378.137    # km
    R_min = 6356.752    # km
    
    part1 = numpy.power((R_max ** 2) * numpy.cos(radlat), 2)
    part2 = numpy.power((R_min ** 2) * numpy.sin(radlat), 2) 
    part3 = numpy.power(R_max * numpy.cos(radlat), 2)
    part4 = numpy.power(R_min * numpy.sin(radlat), 2)
    R_lat = numpy.sqrt((part1 + part2) / (part3 + part4))
    
    # ratio of average gravity to estimated gravity
    grav_ratio = grav_lat * R_lat / 9.80665   #average gravity
    
    # calculate geometric height
    geometric_height = [[0]]*4
    for i in range(4):
        geometric_height[i] = ((R_lat[i] * geopotential[i]) / numpy.absolute(grav_ratio[i] - geopotential[i]))
    
    return numpy.asarray(geometric_height)
        
        
def distance_in_utm(e1, n1, e2, n2):
    """Calculate distances between UTM coordinates.
    """
    
    s = 0.9996    # scale factor 
    r = 6378137.0    # Earth radius
    
    SR1 = s / (math.cos(e1 / r))
    SR2 = s / (math.cos(((e2 - e1) / 6) / r))
    SR3 = s / (math.cos(e2 / r))
    
    Edist = ((e2 - e1) / 6) * (SR1 + 4 * SR2 + SR3)
    
    d = math.sqrt(Edist**2 + (n2 - n1)**2)
    
    return d

def interpolate_time(metadata, h1, h2, t1, t2, r1, r2, p):
    # determine three hour-increment before and after scene center scan time
    time = metadata['SCENE_CENTER_TIME'].replace('"', '')
    hour = int(time[0:2])
    minute = int(time[3:5])
    second = int(time[6:8])
    
    date = metadata['DATE_ACQUIRED']
    year = int(date[0:4])
    month = int(date[5:7])
    day = int(date[8:10])

    rem1 = hour % 3
    rem2 = 3 - rem1
    hour1 = hour - rem1
    hour2 = hour + rem2

    # round to nearest minute
    if second > 30: minute = minute + 100

    # convert hour-min acquisition time to decimal time
    time = hour + minute / 60.0

    # interpolate in time
    height = h1 + (time-hour1) * ((h2 - h1)/(hour2 - hour1))
    rhum= r1 + (time-hour1) * ((r2 - r1)/(hour2 - hour1))
    temp = t1 + (time-hour1) * ((t2 - t1)/(hour2 - hour1))

    return height, rhum, temp
    
def read_stan_atmo(filename='./data/shared/modtran/stanAtm.txt'):
    # read in file containing standard mid lat summer atmosphere information 
    # to be used for upper layers of atmo profile
    stan_atmo = []
    chars = ['\n']

    with open(filename, 'r') as f:
        for line in f:
            data = line.translate(None, ''.join(chars))
            data = data.split()
            data = filter(None, data)
            data = [float(j) for j in data]
            stan_atmo.append(data)

    stan_atmo = numpy.asarray(stan_atmo)
    
    # separate variables in standard atmosphere
    # self.stanGeoHeight = stan_atmo[:,0]
    # self.stanPress = stan_atmo[:,1]
    # self.stanTemp = stan_atmo[:,2]
    # self.stanRelHum = stan_atmo[:,3]
    
    return stan_atmo[:,0], stan_atmo[:,1], stan_atmo[:,2], stan_atmo[:,3]