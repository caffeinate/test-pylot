'''
Created on 26 Aug 2018

@author: si
'''
import xml.etree.ElementTree as etree

class GpxIo(object):
    """
    XML parsing and reading a GPX file.
    """
    def __init__(self, filename):
        self.filename = filename
        self.gpx_namespace = '{http://www.topografix.com/GPX/1/1}'
    
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
    
    