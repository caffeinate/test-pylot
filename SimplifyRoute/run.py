'''
Created on 26 Aug 2018

@author: si
'''
from SimplifyRoute.gpx_io import GpxIo
from SimplifyRoute.gis_utils import distance_on_unit_sphere

distance_threshold = 0.2 # km

source_dir= "/home/si/Documents/Life/Travel/Scandi-Route/"
gpx = GpxIo("{}2018-07-25_19-12-42.gpx".format(source_dir))


# print(len(list(gpx.points)))

shortened_route = []
for coord in gpx.points:
    if len(shortened_route) == 0:
        shortened_route.append(coord)
        continue

    distance_from_last_point = distance_on_unit_sphere(*shortened_route[-1], *coord)
    if distance_from_last_point > distance_threshold:
        shortened_route.append(coord)

print(len(shortened_route))

output = GpxIo("/home/si/Desktop/output.gpx")
output.add_points(shortened_route)
output.write_gpx()
