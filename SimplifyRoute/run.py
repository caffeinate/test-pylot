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


input_files = glob.glob(source_dir+'*.gpx')
input_files.sort()

# for input_file in input_files:
#     base_file = input_file.split('/')[-1]
#     output_file = "{}{}".format(output_dir, base_file)
#     simplify_route(input_file, output_file)


def simplify_route_reduced_files(input_paths, output_base_path):
    """
    super naive way to simplify number of points.
    prints some stats to STDOUT

    :param: input_paths is a list of files
    :param: output_base_path is a directory
    """
    max_points_in_output = 1990
    current_output_file = 0
    output = None

    for input_path in input_paths:
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

        #print("before: {} after: {} file: {}".format(input_points, len(shortened_route), input_path))
        output_path = "{}{}.gpx".format(output_base_path, current_output_file)
        if output is None:
            output = GpxIo(output_path)

        for point in shortened_route:
            output.add_point(point)
            if len(output.points_cache)+1 > max_points_in_output:
                # rotate output file
                output.write_gpx()
                current_output_file += 1
                output_path = "{}{}.gpx".format(output_base_path, current_output_file)
                print("creating {}".format(output_path))
                output = GpxIo(output_path)

    output.write_gpx()

simplify_route_reduced_files(input_files, output_dir)

