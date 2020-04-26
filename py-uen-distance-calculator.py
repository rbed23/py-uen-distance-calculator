'''performs LLA2UEN translation for distance calculations'''
# !/usr/bin/env python

from collections import namedtuple
from math import radians, sin, cos, sqrt


def calcLLA2UENdistance(ref, probe):
    '''
    Calculate distance using LLA2UEN transformation

    <type ref> dict
    <desc ref> referential point in LLA format ('lat', 'lon', and 'alt')

    <type probe> dict
    <desc probe> probe point in LLA format

    '''
    # D2R = pi/180.0                  # degrees to radians conversion
    FLATTEN = 1/298.257223563       # WGS84 flattening constant
    R_EARTH = 6378137               # WGS84 equatorial earth radius
    NAV_E2 = (2-FLATTEN)*FLATTEN    # also e^2

    # Determine earth radius at the point latitude:
    slat = sin(radians(probe["lat"]))
    clat = cos(radians(probe["lat"]))
    r_ref = R_EARTH / sqrt(1 - NAV_E2 * slat * slat)

    UEN_point = [0, 0, 0]

    # Up = altitude:
    UEN_point[0] = probe['alt'] - ref['alt']

    # East = longitude:
    # uen(2) = (lla(2)-reflla(2)) * clat * D2R*r;
    delta_east_radians = radians(probe['lon'] - ref['lon'])
    UEN_point[1] = delta_east_radians * clat * r_ref

    # North = latitude:
    # uen(3) = (lla(1)-reflla(1)) * D2R*r;
    delta_north_radians = radians(probe['lat'] - ref['lat'])
    UEN_point[2] = delta_north_radians * r_ref

    # Up Adjusted: Altitude adjusted for Earth curvature:
    # Ri = sqrt(uen(2)^2 + uen(3)^2);
    Ri = sqrt(UEN_point[1]**2 + UEN_point[2]**2)
    h = r_ref * (1 / (cos(Ri / r_ref)) - 1)

    # uen(1) = lla(3) - h
    if UEN_point[0] > h:  # check if altitude adjustment needed
        UEN_point[0] -= h

    UENPoint = namedtuple('uenpoint', 'up east north')
    UENtup = UENPoint._make(UEN_point)

    # calculate the distance
    dist = sqrt(UENtup.north**2+UENtup.east**2)
    distWithAlt = sqrt(dist**2 + UENtup.up**2)

    print(f'UEN distance "over the ground" (in km): {dist*0.001:.3f}')
    print(f'UEN dist adjusted for altitude (in km): {distWithAlt*0.001:.3f}')


def alt_units_conversion(feet):
    '''converts feet to meters
    <type feet> float
    <desc feet> value in imperial units (feet)

    <<type return>> float
    <<type return>> value in metric units (meters)
    '''
    return feet * 0.3048                    # feet-to-meters conversion


def units_validate(value):
    '''
    validates the unit characterization of value
    <type value> float
    <desc value> n/a
    '''
    unit_validate = input(f"Is this value <{value}> in "
                          f"'meters' or 'feet'? : ").lower()
    if unit_validate[0] == 'f':         # if unit is in feet, convert value
        return alt_units_conversion(value)
    elif unit_validate[0] == 'm':       # if unit is in meters, return value
        return value
    else:                               # if unit is neither, ask again
        return units_validate(value)


def main():
    '''start distance calculation script'''

    print("please enter reference location (lat, lon, alt)")
    reference_point = {
        "lat": float(input("latitude (in degrees): ")),
        "lon": float(input("longitude (in degrees): ")),
        "alt": float(input("altitude (in meters): "))
     }
    if reference_point['alt'] != 0:
        reference_point['alt'] = units_validate(reference_point['alt'])

    print("please enter second location (lat, lon, alt)")
    probe_point = {
        "lat": float(input("latitude (in degrees):  ")),
        "lon": float(input("longitude (in degrees): ")),
        "alt": float(input("altitude (in meters): "))
     }
    if probe_point['alt'] != 0:
        probe_point['alt'] = units_validate(probe_point['alt'])

    calcLLA2UENdistance(reference_point, probe_point)


if __name__ == "__main__":
    main()
