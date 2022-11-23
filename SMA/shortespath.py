# Author: Mohammadhossein Bagheri (@PyBagheri)
# License: MIT
import math

simCity = {
    'AA': {'AT': 6},
    'AB': {'AA': 1, 'AF': 1},
    'AC': {'AB': 12, 'AP': 4},
    'AD': {'AC': 4},
    'AE': {'AD': 6},
    'AF': {'AX': 6},
    'AG': {'AF': 2, 'AL': 1},
    'AH': {'AG': 11, 'AZ': 6},
    'AI': {'AH': 2},
    'AJ': {'AI': 6},
    'AK': {'AJ': 1, 'AE': 1},
    'AL': {'AG': 1},
    'AM': {'AN': 1},
    'AN': {'AM': 1, 'AJ': 1},
    'AO': {'AP': 1},
    'AP': {'AO': 1, 'AW': 2},
    'AQ': {'AR': 1, 'AD': 4},
    'AR': {'AQ': 1},
    'AS': {'AU': 1},
    'AT': {'BI': 6},
    'AU': {'AS': 1, 'AT': 3},
    'AV': {'AU': 4},
    'AW': {'AV': 6, 'BF': 3},
    'AX': {'BA': 2},
    'AY': {'AX': 5},
    'AZ': {'AY': 8, 'BL': 5},
    'BA': {'BB': 1, 'BP': 4},
    'BB': {'BA': 1},
    'BC': {'BD': 1},
    'BD': {'BC': 1, 'AY': 2},
    'BE': {'BF': 1},
    'BF': {'BE': 1, 'BK': 3},
    'BG': {'BH': 1, 'AQ': 6},
    'BH': {'BG': 1},
    'BI': {'BZ': 4},
    'BJ': {'BI': 7, 'AV': 6},
    'BK': {'BJ': 6, 'BR': 1},
    'BL': {'BK': 1},
    'BM': {'BL': 2, 'AI': 11},
    'BN': {'BM': 1, 'BG': 2},
    'BO': {'AK': 11, 'BN': 6},
    'BP': {'BU': 2},
    'BQ': {'BP': 5, 'BD': 4},
    'BR': {'BQ': 7, 'BW': 2},
    'BS': {'BR': 4, 'BN': 1},
    'BT': {'BS': 5, 'AN': 11},
    'BU': {'CQ': 8, 'BV': 5},
    'BV': {'BW': 7, 'CL': 5},
    'BW': {'BX': 4, 'CC': 1},
    'BX': {'BS': 2, 'BY': 5},
    'BY': {'BT': 2},
    'BZ': {'CP': 7, 'CA': 7},
    'CA': {'CB': 3, 'CR': 7},
    'CB': {'CC': 3, 'CH': 1},
    'CC': {'CN': 4, 'CD': 1},
    'CD': {'CS': 7, 'CE': 2},
    'CE': {'CF': 1},
    'CF': {'BX': 1, 'CG': 6},
    'CG': {'BO': 4},
    'CH': {'CB': 1},
    'CI': {'CJ': 1},
    'CJ': {'CI': 1, 'BY': 4},
    'CK': {'CL': 1},
    'CL': {'CK': 1, 'CX': 4},
    'CM': {'CN': 1},
    'CN': {'CM': 1, 'CY': 4},
    'CO': {'CU': 1},
    'CP': {'CW': 1, 'CQ': 1},
    'CQ': {'CR': 6},
    'CR': {'CS': 7},
    'CS': {'CT': 2},
    'CT': {'CU': 3, 'CE': 7},
    'CU': {'CO': 1, 'CV': 3},
    'CV': {'CJ': 3},
    'CW': {'CX': 6},
    'CX': {'CY': 7},
    'CY': {'CZ': 4},
    'CZ': {'DA': 5, 'CF': 8},
    'DA': {'DB': 1, 'CV': 1},
    'DB': {'CG': 8},
}


class Dijkstra:
    def __init__(self, graph, start_vertex):
        self.graph = graph
        self.start_vertex = start_vertex
        self.vertices = list(graph.keys())

        # distance: minimum distance from start vertex
        self.vertex_labels = {
            vertex: {'distance': math.inf, 'prev': '-'} for vertex in self.vertices}

        # Obviously, the start vertex has no distance from itself
        self.vertex_labels[start_vertex]['distance'] = 0

    def _get_edge_weight(self, vertex1, vertex2):
        try:
            return self.graph[vertex1][vertex2]
        except KeyError:
            return math.inf

    def _set_label(self, vertex, weight, prev=''):
        self.vertex_labels[vertex]['distance'] = weight

        if prev:
            self.vertex_labels[vertex]['prev'] = prev

    def _get_label(self, vertex):
        return self.vertex_labels[vertex]

    def dijkstra(self):
        interiors = [self.start_vertex]
        max_interior_vertices = len(self.vertices)

        while True:
            exteriors = [
                vertex for vertex in self.vertices if vertex not in interiors]

            # Nearest vertex to start vertex
            nearest_vertex = '-'

            # Distance from start index
            nearest_vertex_distance = math.inf

            for exterior in exteriors:
                exterior_label = self._get_label(exterior)

                # Shortest discovered distance of current outerior from start vertex
                shortest_discovered_distance = exterior_label['distance']

                # Last vertex through which we reached current exterior with shortest distance
                choosen_prev = exterior_label['prev']

                for interior in interiors:
                    # Shortest discovered distance of current interior from start vertex + distance of current interior from current exterior
                    distance_from_exterior = self._get_label(
                        interior)['distance'] + self._get_edge_weight(interior, exterior)

                    if distance_from_exterior < shortest_discovered_distance:
                        shortest_discovered_distance = distance_from_exterior
                        choosen_prev = interior

                self._set_label(
                    exterior, shortest_discovered_distance, choosen_prev)

                # Attempt to find the nearest exterior to start vertex
                if shortest_discovered_distance < nearest_vertex_distance:
                    nearest_vertex_distance = shortest_discovered_distance
                    nearest_vertex = exterior

            interiors.append(nearest_vertex)

            if len(interiors) == max_interior_vertices:
                break

    def build_path(self, vertex):
        if vertex == '-':
            return []

        return self.build_path(self.vertex_labels[vertex]['prev']) + [vertex]


if __name__ == '__main__':
    dijkstraCity = Dijkstra(simCity, start_vertex='AL')
    dijkstraCity.dijkstra()

    for vertex in dijkstraCity.vertices:
        print('C ->', vertex + ':', dijkstraCity.build_path(vertex))
