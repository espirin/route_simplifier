import argparse
from typing import List, Dict

from io_handler import read_route_json, save_route_osm, save_route_json
from node import Node
from node_pair import create_node_pairs, NodePair
from route import create_route, Route
from segment import create_segments


def simplify_route(path_from: str, path_to: str, json: bool):
    # Read route from file
    print("Reading the input route...")
    original_route: List[Node] = read_route_json(path_from)
    print("Route parsed")

    # Split route into node pairs and count their frequencies. pairs_dict is a graph with pairs as its vertices.
    print("Creating node pairs...")
    pairs_dict, pairs_order = create_node_pairs(original_route)
    print("Created route pairs")

    # Segments are shortened and offsetted pairs. Returns a mapping of pairs to segments.
    print("Creating segments...")
    segments: Dict[NodePair, List[Dict]] = create_segments(pairs_dict)
    print("Segments created")

    # Create route by connecting segments with connections and putting them in the correct order using pairs_order.
    print("Simplifying...")
    simplified_route: Route = create_route(segments, pairs_order)
    print("Simplification completed")

    print("Saving route...")
    if json:
        save_route_json(simplified_route, path_to)
    else:
        save_route_osm(simplified_route, path_to)
    print(f"Route saved as {path_to}")
    print("Done.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simplify route by offsetting overlapping lanes.')
    parser.add_argument('input_path', type=str, help='Path to the input file.')
    parser.add_argument('output_path', type=str, help='Path to the output file.')

    args = parser.parse_args()

    if args.output_path[-4:].lower() == ".osm":
        simplify_route(args.input_path, args.output_path, json=False)
    elif args.output_path[-5:].lower() == ".json":
        simplify_route(args.input_path, args.output_path, json=True)
    else:
        raise Exception("Output file extension should be either .json or .osm")
