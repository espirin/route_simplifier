# Values in meters

LANE_OFFSET = 2  # Distance to which each lane is going to be moved
LANE_OFFSET_LENGTH_REDUCTION = 0.5  # Distance reduction of each offsetted segment.
# The further the lane is - the shorter it is

INTERSECTION_OFFSET = 3  # Shorten segment which neighbors an intersection by this length
NODES_POSITION_ERROR = 1  # If nodes are closer to each other than NODES_POSITION_ERROR, then they are the same node
MIN_PAIR_LENGTH = 2  # Filter out pairs shorter than MIN_PAIR_LENGTH
