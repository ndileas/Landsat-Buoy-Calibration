from osgeo import gdal, osr
from PIL import Image, ImageDraw
import numpy
import os
import utm
import ogr
import osr

def find_roi(img_file, lat, lon, zone):
    """ find pixel which corresponds to lat and lon in image. """
    # img_file: full path to georeferenced image file
    # lat, lon: float, location to find
    # zone: utm zone in which the image is projected
    
    ds = gdal.Open(img_file)   # open image
    gt = ds.GetGeoTransform()   # get data transform
    
    # change lat_lon to same projection
    l_x, l_y, l_zone, l_zone_let = utm.from_latlon(lat, lon)
    
    if zone != l_zone:
        l_x, l_y = convert_utm_zones(l_x, l_y, l_zone, zone)

    # calculate pixel locations- source: http://www.gdal.org/gdal_datamodel.html
    x = int((l_x - gt[0]) / gt[1])
    y = int((l_y - gt[3]) / gt[5])
    
    return x, y
    
def convert_utm_zones(x, y, zone_from, zone_to):
    """ convert lat/lon to appropriate utm zone. """

    # Spatial Reference System
    inputEPSG = int(float('326' + str(zone_from)))
    outputEPSG = int(float('326' + str(zone_to)))

    # create a geometry from coordinates
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(x, y)

    # create coordinate transformation
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(inputEPSG)

    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(outputEPSG)

    coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

    # transform point
    point.Transform(coordTransform)

    return point.GetX(), point.GetY()
     
def calc_dc_avg(filename, poi):
    """ calculate the digital count average. """
    #open image
    im = Image.open(filename)
    im_loaded = im.load()
    
    roi = poi[0]-1, poi[1]+1   #ROI gives top left pixel location, 
                               #POI gives center tap location

    dc_sum = 0   #allocate for ROI dc_sum
    #extract ROI DCs
    for i in range(3):
        for j in range(3):
            dc_sum += im_loaded[roi[0]+i, roi[1]+j]
    
    dc_avg = dc_sum / 9.0   #calculate dc_avg

    return dc_avg

def dc_to_rad(band, metadata, DCavg):
    """ Convert digital count average to radiance. """
    
    if band == 10:
        L_add = metadata['RADIANCE_ADD_BAND_10']
        L_mult = metadata['RADIANCE_MULT_BAND_10']
    if band == 11:
        L_add = metadata['RADIANCE_ADD_BAND_11']
        L_mult = metadata['RADIANCE_MULT_BAND_11']

    #calculate LLambda
    LLambdaaddmult = DCavg * L_mult + L_add
        
    return LLambdaaddmult


def write_im(cc):
    img = os.path.join(cc.scene_dir, cc.scene_id+'_B10.TIF')
    zone = cc.metadata['UTM_ZONE']
    narr_pix = []
    
    # get narr point locations
    for lat, lon in cc.narr_coor:
        narr_pix.append(find_roi(img, lat, lon, zone))

    # draw circle on top of image to signify narr points
    image = Image.open(img)
    image = image.point(lambda i:i*(1./256.0)).convert('RGBA')
    draw = ImageDraw.Draw(image)
    rx = 100
    
    for x, y in narr_pix:
        draw.ellipse((x-rx, y-rx, x+rx, y+rx), fill=(255, 0, 0))
        
    # draw buoy onto image
    x = cc.poi[0]
    y = cc.poi[1]
    draw.ellipse((x-rx, y-rx, x+rx, y+rx), fill=(0, 255, 0))

    # downsample
    image = image.resize((500, 486), Image.ANTIALIAS)
    
    data = image.getdata()
    #print data.shape
    #print data.size
    newData = []
    
    for item in data:
        if item[0] == item[1] == item[2] == 0:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    
    image.putdata(newData)
    # save
    save_path = os.path.join(cc.scene_dir, cc.scene_id+'_mod')
    if cc.atmo_src == 'narr':
        save_path += '_narr.png'
    elif cc.atmo_src == 'merra':
        save_path += '_merra.png'
    image.save(save_path)
