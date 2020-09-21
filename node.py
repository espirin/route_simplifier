import math

from utm import to_latlon, from_latlon, latlon_to_zone_number, latitude_to_zone_letter

from config import NODES_POSITION_ERROR


class LatLon:
    """LatLon coordinates are a pair of latitude and longitude."""

    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def convert_to_utm(self):
        northeast = from_latlon(self.lat, self.lon)
        north = northeast[1]
        east = northeast[0]
        return UTM(north, east)

    def __hash__(self):
        return hash(f"{self.lat}{self.lon}")


class UTM:
    """UTM coordinates are a pair of north and east. They are used for geometrical operations."""

    def __init__(self, north: float, east: float):
        self.north = north
        self.east = east

    def convert_to_latlon(self, zone: LatLon):
        zone_number = latlon_to_zone_number(zone.lat, zone.lon)
        zone_letter = latitude_to_zone_letter(zone.lat)
        lat, lon = to_latlon(self.east, self.north, zone_number, zone_letter)
        return LatLon(lat, lon)

    def __sub__(self, other):
        return math.sqrt((self.north - other.north) ** 2 + (self.east - other.east) ** 2)


class Node:
    """Node is a point of a route."""

    def __init__(self, latlon: LatLon):
        self.latlon = latlon
        self.utm = latlon.convert_to_utm()

    def __str__(self):
        return f"Node(lat: {self.latlon.lat}, lon: {self.latlon.lon})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, Node) and self.utm - other.utm < NODES_POSITION_ERROR
