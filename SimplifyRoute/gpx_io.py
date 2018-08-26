'''
Created on 26 Aug 2018

@author: si
'''
import os
import xml.etree.ElementTree as etree

class GpxIo(object):
    """
    XML parsing and reading a GPX file.
    """
    def __init__(self, filename):
        self.filename = filename
        self.gpx_namespace = '{http://www.topografix.com/GPX/1/1}'
        self.points_cache = []
    
    @property
    def points(self):
        """
        Generator that ignores track segments etc. and just iterates through all points
        in file.
        """
        tree = etree.parse(self.filename)
        for track in tree.findall('{}trk'.format(self.gpx_namespace)):
            for track_segment in track.findall('{}trkseg'.format(self.gpx_namespace)):
                for point in track_segment.findall('{}trkpt'.format(self.gpx_namespace)):
                    yield float(point.attrib['lat']), float(point.attrib['lon'])

    def add_points(self, points):
        """
        :param: points list of tuples (lat, lng)
        """
        self.points_cache.extend(points)

    def write_gpx(self):
        """
        file given to constructor mustn't exist.
        """
        if os.access(self.filename, os.F_OK):
            raise IOError("Output file already exists")

        # naive way of making an XML file
        d = """<?xml version="1.0" encoding="UTF-8" ?>
        <gpx xmlns="http://www.topografix.com/GPX/1/1" version="1.1" creator="test-pylot - https://github.com/caffeinate/test-pylot" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd ">
        <trk>
                <name><![CDATA[Created with test-pylot]]></name>
                <trkseg>
                        {}
                </trkseg>
        </trk>
        </gpx>
        """
        points_xml = "\n".join(['<trkpt lat="{}" lon="{}" />'.format(p[0], p[1])\
                                                                for p in self.points_cache])
        with open(self.filename, "w") as f:
            f.write(d.format(points_xml))

