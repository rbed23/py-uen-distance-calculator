'''performs basic metrics analysis on GFM donations'''
#!/usr/bin/env python

import  sys
from collections import namedtuple
from math import *

def calcLLA2UENdistance(ref,probe):
    '''
    Calculate distance using LLA2UEN transformation

    <type ref> named tuple
    <desc ref> referential point in LLA format ('lat', 'lon', and 'alt')

    <type probe> named tuple
    <desc probe> probe point in LLA format

    '''    
    D2R = pi/180.0              # degrees to radians conversion
    FLATTEN = 1/298.257223563   # WGS84 flattening constant
    R_EARTH = 6378137           # WGS84 equatorial earth radius
    
    # Determine earth radius at the reference point latitude:
    slat = sin(radians(ref.lat))
    clat = cos(radians(ref.lat))
    NAV_E2 = (2-FLATTEN)*FLATTEN # also e^2
    r_ref = R_EARTH / sqrt(1 - NAV_E2 * slat * slat)     
    
    radPoint = namedtuple('radpoint', 'lat lon alt')

    #lat1, lon1, alt1 = radians(probe.lat), probe.lon, probe.alt*0.3048) # convert feet to meters
    p_rad = radPoint(radians(probe.lat), radians(probe.lon), radians(probe.alt))
    
    #lat2, lon2, alt2 = ref.lat, ref.lon, ref.alt*0.3048 # convert feet to meters
    r_rad = radPoint(radians(ref.lat), radians(ref.lon), radians(ref.alt))
    
    #rlat, rlon, ralt = lat2, lon2, alt2


    UENPoint = namedtuple('uenpoint', 'up east north')
    prbUEN = [0,0,0]
    refUEN = [0,0,0]

    #Up = altitude:    
    prbUEN[0] = p_rad.alt - r_ref
    refUEN[0] = r_rad.alt - r_ref
    
    #East = longitude:
    #uen(2) = (lla(2)-reflla(2)) * clat * D2R*r;
    #east_rads = lon1 - rlon
    probe_east_rads = p_rad.lon - r_rad.lon
    prbUEN[1] = probe_east_rads * clat * r_ref
    
    #east_rads = lon2 - rlon
    ref_east_rads = r_rad.lon - r_rad.lon
    refUEN[1] = ref_east_rads * clat * r_ref
    
    #North = latitude:
    #uen(3) = (lla(1)-reflla(1))*D2R*r;
    #north_rads = lat1 - rlat
    probe_north_rads = p_rad.lat - r_rad.lat
    prbUEN[2] = probe_north_rads * r_ref
    
    #north_rads = lat2 - rlat
    ref_north_rads = r_rad.lat - r_rad.lat
    refUEN[2] = ref_north_rads * r_ref

    #Up: Altitude adjusted for Earth curvature:
    #Ri = sqrt(uen(2)^2 + uen(3)^2);
    Ri = sqrt(prbUEN[1]**2 + prbUEN[2]**2)
    h = r_ref * (1 / (cos(Ri / r_ref)) - 1)
    #uen(1) = lla(3) - h
    prbUEN[0] = p_rad.alt - h

    prbUENtup = UENPoint._make(prbUEN)
    refUENtup = UENPoint._make(refUEN)
    #calculate the distance
    #dist = sqrt((float(prbUEN['north']-srcUEN['north'])**2) + (float(prbUEN['east']-srcUEN['east'])**2))
    dist = sqrt((prbUENtup.north-refUENtup.north)**2+(prbUENtup.east-refUENtup.east)**2)
    distWithAlt = sqrt(dist**2 + (prbUENtup.up-refUENtup.up)**2)
    
    #print (prbUEN)
    #print (srcUEN)

    print (f'UEN distance (in km): {dist*0.001:.3f}')
    print (f'UEN dist with altitude adjustment (in km): {distWithAlt*0.001:.3f}')

def main():
    LLAPoint = namedtuple('llapoint', 'lat lon alt')

    print("please enter referent location (lat, lon, alt)")
    y = float(input("lat: "))
    x = float(input("lon: "))
    z = float(input("alt: "))
    ref_pt = LLAPoint(y, x, z)
    print("please enter second location (lat, lon, alt)")
    y = float(input("lat: "))
    x = float(input("lon: "))
    z = float(input("alt: "))
    probe_pt = LLAPoint(y, x, z)

    calcLLA2UENdistance(ref_pt, probe_pt)    

if __name__ == "__main__":
    main()
