from typing import List, Dict

from shapely.geometry import LineString, Point
from shapely.ops import nearest_points

from config import LANE_OFFSET, INTERSECTION_OFFSET, MIN_PAIR_LENGTH, LANE_OFFSET_LENGTH_REDUCTION
from node import Node, UTM, LatLon
from node_pair import NodePair
from route import RoutePart


class Segment(RoutePart):
    """Segments are shortened and offsetted NodePairs."""

    def __init__(self, pair: NodePair, offset_multiplier: int, pairs_dict: Dict[NodePair, int]):
        self.pair = pair
        super().__init__(
            self.create_nodes([self.pair.node_from, self.pair.node_to], offset_multiplier, pairs_dict, LANE_OFFSET))

    def create_nodes(self, nodes: List[Node], offset_multiplier: int, pairs_dict, offset_distance: float) -> List[Node]:
        string = LineString([[node.utm.north, node.utm.east] for node in nodes])

        # Shorten string to avoid overlaps with neighbor strings' offsets
        string = self.shorten_linestring(string, pairs_dict, offset_distance, offset_multiplier)

        # Offset string
        zone_latlon = nodes[0].latlon
        nodes = self.offset_linestring(zone_latlon, string, offset_distance, offset_multiplier)

        return nodes

    @staticmethod
    def offset_linestring(zone_latlon: LatLon, string: LineString, offset_distance: float,
                          offset_multiplier: int) -> List[Node]:
        offsetted_string = string.parallel_offset((offset_multiplier + 1) * offset_distance, side='left', resolution=10)

        nodes = []
        if isinstance(offsetted_string, LineString):
            for north, east in list(offsetted_string.coords):
                utm = UTM(north, east)
                nodes.append(Node(utm.convert_to_latlon(zone_latlon)))
        else:
            raise Exception(f"Error while offsetting linestring. The result geometry is not a LineString.")

        return nodes

    def shorten_linestring(self, string: LineString, pairs_dict: Dict[NodePair, int], offset_distance: float,
                           offset_multiplier: int):
        # Distance to cut from the back of the string.
        if len(self.pair.comes_from) > 0:
            cut_distance_back = max(
                [self.find_cut_distance(string, pair, pairs_dict[pair], offset_distance, 'back') for pair in
                 self.pair.comes_from])
            cut_distance_back = cut_distance_back + INTERSECTION_OFFSET
        else:
            cut_distance_back = 0.0

        # Shorten string in stairs style
        cut_distance_back += LANE_OFFSET_LENGTH_REDUCTION * offset_multiplier
        cut_distance_back = min(cut_distance_back, string.length - MIN_PAIR_LENGTH)

        # Distance to cut from the front of the string.
        if len(self.pair.leads_to) > 0:
            cut_distance_front = max(
                [self.find_cut_distance(string, pair, pairs_dict[pair], offset_distance, 'front') for pair in
                 self.pair.leads_to])
            cut_distance_front = cut_distance_front + INTERSECTION_OFFSET
        else:
            cut_distance_front = 0.0

        # Shorten string in stairs style
        cut_distance_front += LANE_OFFSET_LENGTH_REDUCTION * offset_multiplier
        cut_distance_front = min(cut_distance_front, max(string.length - cut_distance_back - MIN_PAIR_LENGTH, 0))

        shorter_string = self.cut_linestring(string, cut_distance_back, cut_distance_front)

        return shorter_string

    @staticmethod
    def find_cut_distance(current_string: LineString, pair, frequency: int, offset_distance: float, side: str):
        neighbor_string = LineString([[pair.node_from.utm.north, pair.node_from.utm.east],
                                      [pair.node_to.utm.north, pair.node_to.utm.east]])
        offsetted_neighbor_string = neighbor_string.parallel_offset(frequency * offset_distance, side='left',
                                                                    resolution=10)

        # Project neighbor string onto current string.
        if side == 'back':
            projected_point = Point(
                nearest_points(current_string, Point(list(offsetted_neighbor_string.coords)[-1]))[0])
        else:
            projected_point = Point(nearest_points(current_string, Point(list(offsetted_neighbor_string.coords)[0]))[0])

        # Create a line from the side of the current string to the projected points.
        if side == 'back':
            line = LineString([Point(list(current_string.coords)[0]), projected_point])
        else:
            line = LineString([Point(list(current_string.coords)[-1]), projected_point])

        return line.length

    def cut_linestring(self, string: LineString, first_cut_distance: float,
                       second_cut_distance: float) -> LineString:
        before, after = self.cut_linestring_by_distance(string, first_cut_distance)
        before, after = self.cut_linestring_by_distance(after, after.length - second_cut_distance)

        return before

    @staticmethod
    def cut_linestring_by_distance(string: LineString, distance: float):
        if distance <= 0.0:
            return None, string
        elif distance >= string.length:
            return string, None

        coords = list(string.coords)
        for i, p in enumerate(coords):
            pd = string.project(Point(p))
            if pd == distance:
                return LineString(coords[:i + 1]), LineString(coords[i:])
            if pd > distance:
                cp = string.interpolate(distance)
                return LineString(coords[:i] + [(cp.x, cp.y)]), LineString([(cp.x, cp.y)] + coords[i:])


def create_segments(pairs_dict: Dict[NodePair, int]) -> Dict[NodePair, List[Dict]]:
    segments: Dict[NodePair, List[Dict]] = dict()

    for pair, frequency in pairs_dict.items():
        for i in range(frequency):
            if pair in segments:
                segments[pair].append({
                    "used": False,
                    "segment": Segment(pair, i, pairs_dict)
                })
            else:
                segments[pair] = [{
                    "used": False,
                    "segment": Segment(pair, i, pairs_dict)
                }]

    return segments
