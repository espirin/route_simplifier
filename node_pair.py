import copy
import math
from typing import List, Tuple, Dict

from config import MIN_PAIR_LENGTH
from node import Node


class NodePair:
    """NodePair is a pair of nodes longer than MIN_PAIR_LENGTH with references to neighbor pairs."""

    def __init__(self, node_from: Node, node_to: Node):
        self.node_from = node_from
        self.node_to = node_to

        self.comes_from = set()
        self.leads_to = set()

    def __str__(self):
        return f"NodePair(from: {self.node_from}, to: {self.node_to}, " \
               f"comes_from: {len(self.comes_from)}, leads_to: {len(self.leads_to)})"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(f"{self.node_from}{self.node_to}")

    def __eq__(self, other):
        return isinstance(other, NodePair) and self.node_from == other.node_from \
               and self.node_to == other.node_to


def create_node_pairs(route: List[Node]) -> Tuple[Dict[NodePair, int], List[NodePair]]:
    # Create all pairs and save them in the original order
    pairs_order: List[NodePair] = []

    for i in range(len(route) - 1):
        node_from = route[i]
        node_to = route[i + 1]

        # If a pair is shorter than MIN_PAIR_LENGTH, ignore it.
        if node_from.latlon == node_to.latlon or math.sqrt(
                (node_to.utm.north - node_from.utm.north) ** 2 + (
                        node_to.utm.east - node_from.utm.east) ** 2) < MIN_PAIR_LENGTH:
            continue
        pair = NodePair(node_from, node_to)
        pairs_order.append(pair)

    # Find nodes closer to each other than NODES_POSITION_ERROR and replace them with copies.
    # Replacing with copies is an easier way of replacing positions.
    # This is need to be able to hash pairs (positions of close nodes should be the same).
    for i in range(len(pairs_order) - 1):
        for j in range(i + 1, len(pairs_order)):
            if pairs_order[i] == pairs_order[j]:
                pairs_order[j] = copy.deepcopy(pairs_order[i])

    # Count frequencies of pairs and add references to neighbor links.
    # Keep in mind, that references are added only to the pairs which serve as dictionary keys.
    # Not all pairs in the pairs_order list have them.
    last_pair = None
    pairs_dict: Dict[NodePair, int] = dict()
    for pair in pairs_order:
        if pair in pairs_dict:
            pairs_dict[pair] += 1
        else:
            pairs_dict[pair] = 1

        if last_pair:
            # Added neighbor references to dictionary keys.
            keys = list(pairs_dict.keys())
            last_pair_original = keys[keys.index(last_pair)]
            pair_original = keys[keys.index(pair)]
            last_pair_original.leads_to.add(pair_original)
            pair_original.comes_from.add(last_pair_original)
        last_pair = pair

    return pairs_dict, pairs_order
