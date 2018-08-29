'''
Created on 26 Aug 2018

@author: si
'''
import glob

from SimplifyRoute.gpx_io import GpxIo
from SimplifyRoute.gis_utils import distance_on_unit_sphere

distance_threshold = 0.2 # km

def simplify_route(input_path, output_path):
    """
    super naive way to simplify number of points.
    prints some stats to STDOUT
    """
    gpx = GpxIo(input_path)
    shortened_route = []
    input_points = 0
    for coord in gpx.points:
        input_points += 1
        if len(shortened_route) == 0:
            shortened_route.append(coord)
            continue
    
        distance_from_last_point = distance_on_unit_sphere(*shortened_route[-1], *coord)
        if distance_from_last_point > distance_threshold:
            shortened_route.append(coord)
    
    print("before: {} after: {} file: {}".format(input_points, len(shortened_route), input_path))
    output = GpxIo(output_path)
    output.add_points(shortened_route)
    output.write_gpx()


source_dir= "/home/si/Documents/Life/Travel/Scandi-Route/"
output_dir = "/home/si/Desktop/"
# 
# "{}2018-07-25_19-12-42.gpx".format(source_dir)
# 
#     output_path = "{}".format()

for input_file in glob.glob(source_dir+'*.gpx'):
    base_file = input_file.split('/')[-1]
    output_file = "{}{}".format(output_dir, base_file)
    simplify_route(input_file, output_file)
