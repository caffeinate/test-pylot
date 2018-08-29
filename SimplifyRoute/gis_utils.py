'''
Created on 26 Aug 2018

@author: si
'''
import math

def distance_on_unit_sphere(lat1, long1, lat2, long2):
    """
    from
    https://gis.stackexchange.com/questions/163785/using-python-to-compute-the-distance-between-coordinates-lat-long-using-havers
    :return: distance in km
    """
    # Converts lat & long to spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
    
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
    
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
    
    # Compute the spherical distance from spherical coordinates.
    # For two locations in spherical coordinates:
    # (1, theta, phi) and (1, theta', phi')cosine( arc length ) =
    # sin phi sin phi' cos(theta-theta') + cos phi cos phi' distance = rho * arc    length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
       math.cos(phi1)*math.cos(phi2))

    if cos > 1.:
        return 0.

    arc = math.acos(cos)*6371 #radius of the earth in km

    return arc
