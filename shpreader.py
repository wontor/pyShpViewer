#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Author: wangt@njust.edu.cn
Last edited: 2019.7.30
"""


import struct

# ST_POINT = 1
#ST_MULTIPOINT = 8
ST_ARC = 3
ST_POLYGON = 5


def read_polygons(buff, bufflen):
    shapes = []

    p = 0
    while p < bufflen:
        shape = {}

        rnum = struct.unpack("!i",buff[p:p+4])[0]
        if rnum <=0:
            break

        shape['recordnum'] = rnum

        contlen = struct.unpack("!i",buff[p+4:p+8])[0]
        shape['contlen'] = contlen
        
        stype = struct.unpack("i",buff[p+8:p+12])[0]
        shape['type'] = stype

        xmin = struct.unpack("d",buff[p+12:p+20])[0]
        ymin = struct.unpack("d",buff[p+20:p+28])[0]
        xmax = struct.unpack("d",buff[p+28:p+36])[0]
        ymax = struct.unpack("d",buff[p+36:p+44])[0]
        shape['boudingbox'] = {'xmin':xmin,'ymin':ymin,'xmax':xmax,'ymax':ymax}

        numparts = struct.unpack("i",buff[p+44:p+48])[0]
        numpoints = struct.unpack("i",buff[p+48:p+52])[0]
        shape['numparts'] = numparts
        shape['numpoints'] = numpoints

        p += 52
        parts = struct.unpack(str(numparts)+"i",buff[p:p+numparts*4])
        p += numparts*4
        shape['parts'] = parts
        
        points = struct.unpack(str(numpoints*2)+"d",buff[p:p+numpoints*16])
        p += numpoints*16
        shape['points'] = points

        shapes.append(shape)

    return shapes


def read_shp(filename):
    ret = {}

    try:
        with open(filename,"rb") as f:
            buff = f.read()
    except:
        print('open '+filename+' failed')
        return ret

    filelength = len(buff)

    v = struct.unpack("!i",buff[0:4])[0]
    if v != 9994:
        print('not valid shp file')
        return ret

    v = struct.unpack("!i",buff[24:28])[0]
    length = v*2
    if length != filelength:
        print('not valid file length')
        return ret
    
    v = struct.unpack("i",buff[28:32])[0]
    if v != 1000:
        print('not valid file version')
        return ret
    
    stype = struct.unpack("i",buff[32:36])[0]
    if stype not in [ST_POLYGON , ST_ARC] :
        print('not supported type ',stype)
        return ret

    ret['shape_type'] = stype

    xmin = struct.unpack("d",buff[36:44])[0]
    ymin = struct.unpack("d",buff[44:52])[0]
    xmax = struct.unpack("d",buff[52:60])[0]
    ymax = struct.unpack("d",buff[60:68])[0]
    ret['boudingbox']={'xmin':xmin,'ymin':ymin,'xmax':xmax,'ymax':ymax}

    ret['shapes'] = []

    # ST_POLYGON and ST_ART are the same (structure)
    if stype in [ST_POLYGON, ST_ARC]:
        # the file header length is 100
        ret['shapes'] = read_polygons(buff[100:], filelength-100)

    return ret


def draw_shp(painter, rect, shp, orig, ratio=1.0):
    if not shp:
        return
    
    if shp['shape_type'] in [ST_POLYGON, ST_ARC]:
        for shape in shp['shapes']:
            if shape['numparts'] == 0:
                continue

            points = shape['points']

            # draw parts
            pi_start = shape['parts'][0]
            for i in range(shape['numparts']-1):
                pi_end = shape['parts'][i+1]-1
                for pi in range(pi_start,pi_end):
                    painter.drawLine(points[pi*2]*ratio - orig.x(),
                                    rect.bottom() - (points[pi*2+1]*ratio - orig.y()),
                                    points[pi*2+2]*ratio - orig.x(),
                                    rect.bottom() - (points[pi*2+3]*ratio - orig.y()))

                pi_start = shape['parts'][i+1]

            # draw the last part
            pi_end = shape['numpoints']-1
            for pi in range(pi_start,pi_end):
                painter.drawLine(points[pi*2]*ratio - orig.x(),
                                rect.bottom() - (points[pi*2+1]*ratio - orig.y()),
                                points[pi*2+2]*ratio - orig.x(),
                                rect.bottom() - (points[pi*2+3]*ratio - orig.y()))

