import math
from abc import ABC
from pprint import pformat
from typing import List, Dict, Tuple

from node import Node
from node_pair import NodePair


class RoutePart(ABC):
    """RoutePart is an abstract class that represent an atom of a route and has a geometry."""

    def __init__(self, nodes: List[Node]):
        self.nodes = nodes

    def __str__(self):
        return f"RoutePart(nodes: {pformat(self.nodes)})"

    def __repr__(self):
        return self.__str__()


class Connection(RoutePart):
    """Connection class represents a connection between two segments."""

    def __init__(self, node_from: Node, node_to: Node):
        super().__init__([node_from, node_to])


class Route:
    """Route class represents a final route consisting of RouteParts."""

    def __init__(self, parts: List[RoutePart]):
        self.parts = parts

    def __str__(self):
        return f"Route(parts: {pformat(self.parts)})"

    def __repr__(self):
        return self.__str__()


def create_route(segments: Dict[NodePair, List[Dict]], pairs_order: List[NodePair]) -> Route:
    route_parts = []
    last_lane = None

    for i in range(len(pairs_order) - 1):
        pair = pairs_order[i]
        next_pair = pairs_order[i + 1]
        segment = segments[pair]
        next_segment = segments[next_pair]

        # Calculate angle between current segment and next segment.
        initial_bearing = calculate_bearing((pair.node_from.latlon.lat,
                                             pair.node_from.latlon.lon),
                                            (pair.node_to.latlon.lat,
                                             pair.node_to.latlon.lon))
        bearing = calculate_bearing((pair.node_to.latlon.lat, pair.node_to.latlon.lon),
                                    (next_pair.node_from.latlon.lat, next_pair.node_from.latlon.lon)) - initial_bearing

        # Greedy connect to a more suitable lane.
        if bearing < 0:
            # Connect to the left most lane possible.
            last_lane = connect_segments(last_lane, segment, next_segment, route_parts, side='left')

        else:
            # Connect to the right most lane possible.
            last_lane = connect_segments(last_lane, segment, next_segment, route_parts, side='right')

    # Corner case. Append the last segment.
    route_parts.append(last_lane['segment'])

    return Route(route_parts)


def connect_segments(last_lane: Dict, segment: List[Dict], next_segment: List[Dict], route_parts: List[RoutePart],
                     side: str) -> Dict:
    node_to = None
    if last_lane is None:
        segment[0]['used'] = True
        node_from = segment[0]['segment'].nodes[-1]
        segment_to_append = segment[0]['segment']
    else:
        node_from = last_lane['segment'].nodes[-1]
        segment_to_append = last_lane['segment']

    if side == 'left':
        for lane in next_segment:
            if not lane['used']:
                lane['used'] = True
                last_lane = lane
                node_to = lane['segment'].nodes[0]
                break
    else:
        for lane in reversed(next_segment):
            if not lane['used']:
                lane['used'] = True
                last_lane = lane
                node_to = lane['segment'].nodes[0]
                break

    route_parts.append(segment_to_append)
    route_parts.append(Connection(node_from, node_to))

    return last_lane


def calculate_bearing(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    # Mathematical magic to calculate a compass bearing of a vector.
    # Returns a number from 0 to 360 representing a compass bearing.
    lat1 = math.radians(a[0])
    lat2 = math.radians(b[0])

    diff_long = math.radians(b[1] - a[1])

    x = math.sin(diff_long) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diff_long))

    initial_bearing = math.atan2(x, y)

    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing
