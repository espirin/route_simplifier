import json
from typing import List, Dict
from lxml import etree

from node import LatLon, Node
from route import Route


def read_route_json(path: str) -> List[Node]:
    with open(path) as f:
        route = json.load(f)

    route = [Node(LatLon(node["lat"], node["lon"])) for node in route]
    return route


def save_route_osm(route: Route, path: str):
    root = etree.Element("osm", version="0.6", generator="JOSM")  # Header of the main route file

    # Create nodes.
    node_counter = -1
    for route_part in route.parts:
        for node in route_part.nodes:
            osm_node = etree.Element("node", id=str(node_counter),
                                     lon=str(node.latlon.lon),
                                     lat=str(node.latlon.lat))
            # Add restaurant tag to show it on the map.
            osm_node.append(etree.Element("tag", k="amenity", v="restaurant"))
            root.append(osm_node)
            node_counter -= 1

    # Create a single way connecting all nodes.
    way = etree.Element("way", id=str(node_counter))
    for i in range(-1, node_counter, -1):
        way.append(etree.Element("nd", ref=str(i)))
    root.append(way)

    # Add OSM header and save route.
    source = "<?xml version='1.0' encoding='UTF-8'?>\n" + etree.tostring(root, pretty_print=True).decode('utf-8')
    with open(path, "w") as f:
        f.write(source)


def save_route_json(route: Route, path: str):
    route_json: List[Dict[str, float]] = []

    for route_part in route.parts:
        for node in route_part.nodes:
            route_json.append({
                "lat": node.latlon.lat,
                "lon": node.latlon.lon
            })

    with open(path, "w") as f:
        json.dump(route_json, f)
