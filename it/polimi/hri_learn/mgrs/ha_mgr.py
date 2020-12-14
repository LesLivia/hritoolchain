from typing import List

from domain.hafeatures import Edge, Location, LOCATIONS
from domain.sigfeatures import ChangePoint, Labels


def identify_edges(chg_pts: List[ChangePoint]):
    edges: List[Edge] = []

    for pt in chg_pts:
        start: Location = LOCATIONS[0] if pt.event == Labels.STARTED else LOCATIONS[1]
        dest: Location = LOCATIONS[1] if pt.event == Labels.STARTED else LOCATIONS[0]
        guard = '{} <= t <= {}'.format(pt.dt.t_min, pt.dt.t_max)
        edges.append(Edge(start, dest, guard))

    return edges
