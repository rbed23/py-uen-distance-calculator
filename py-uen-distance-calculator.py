'''performs basic metrics analysis on GFM donations'''
#!/usr/bin/env python

import  sys
from collections import namedtuple
from math import *

def calcLLA2UENdistance(ref,probe):
    '''
    Calculate distance using LLA2UEN transformation

    <type ref> dict
    <desc ref> referential point in LLA format ('lat', 'lon', and 'alt')

    <type probe> dict
    <desc probe> probe point in LLA format

    '''    
    #D2R = pi/180.0              # degrees to radians conversion
    FLATTEN = 1/298.257223563   # WGS84 flattening constant
    R_EARTH = 6378137           # WGS84 equatorial earth radius
    
    # Determine earth radius at the reference point latitude:
    slat = sin(radians(probe["lat"]))
    clat = cos(radians(probe["lat"]))
    NAV_E2 = (2-FLATTEN)*FLATTEN # also e^2
    r_ref = R_EARTH / sqrt(1 - NAV_E2 * slat * slat)     
    
    UEN_point = [0,0,0]

    #Up = altitude:
    UEN_point[0] = probe['alt'] - ref['alt']
    
    #East = longitude:
    #uen(2) = (lla(2)-reflla(2)) * clat * D2R*r;
    probe_east_rads = radians(probe['lon'] - ref['lon'])
    UEN_point[1] = probe_east_rads * clat * r_ref
 
    #North = latitude:
    #uen(3) = (lla(1)-reflla(1)) * D2R*r;
    probe_north_rads = radians(probe['lat'] - ref['lat'])
    UEN_point[2] = probe_north_rads * r_ref
    
    #Up Adjusted: Altitude adjusted for Earth curvature:
    #Ri = sqrt(uen(2)^2 + uen(3)^2);
    Ri = sqrt(UEN_point[1]**2 + UEN_point[2]**2)
    h = r_ref * (1 / (cos(Ri / r_ref)) - 1)
    #uen(1) = lla(3) - h
    UEN_point[0] -= h

    UENPoint = namedtuple('uenpoint', 'up east north')
    UENtup = UENPoint._make(UEN_point)

    #calculate the distance
    dist = sqrt(UENtup.north**2+UENtup.east**2)
    distWithAlt = sqrt(dist**2 + UENtup.up**2)

    print (f'UEN distance "over the ground" (in km): {dist*0.001:.3f}')
    print (f'UEN dist adjusted for altitude (in km): {distWithAlt*0.001:.3f}')

def alt_units_conversion(feet):
    return feet * 0.3048

def units_validate(value):
    unit_validate = input(f"Is this value <{value}> in\
     'meters' or 'feet'? : ").lower()
    if unit_validate[0] == 'f':
        return alt_units_conversion(value)
    elif unit_validate[0] == 'm':
        return value
    else:
        return units_validate(value)

def main():

    print("please enter reference location (lat, lon, alt)")
    reference_point = {
        "lat" : float(input("latitude:  ")),
        "lon" : float(input("longitude: ")),
        "alt" : float(input("altitude (in meters): "))
     }
    if reference_point['alt'] != 0:
        reference_point['alt'] = units_validate(reference_point['alt'])

    print("please enter second location (lat, lon, alt)")
    probe_point = {
        "lat" : float(input("latitude:  ")),
        "lon" : float(input("longitude: ")),
        "alt" : float(input("altitude (in meters): "))
     }
    if probe_point['alt'] != 0:
        probe_point['alt'] = units_validate(probe_point['alt'])
    
    calcLLA2UENdistance(reference_point, probe_point)    

if __name__ == "__main__":
    main()
