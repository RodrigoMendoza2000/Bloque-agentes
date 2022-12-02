# Author: Mohammadhossein Bagheri (@PyBagheri)
# License: MIT
import math

# The graph dictionary represing all nodes and its connections in the base.txt map
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

# Dictionary representing the coordinates in the grid according to the node name in SimCity
nodo_coordenada = {
    'AA': (0,24),
    'AB': (1,24),
    'AC': (13,24),
    'AD': (17,24),
    'AE': (23,24),
    'AF': (1,23),
    'AG': (3,23),
    'AH': (14,23),
    'AI': (16,23),
    'AJ': (22,23),
    'AK': (23,23),
    'AL': (3,22),
    'AM': (21,22),
    'AN': (22,22),
    'AO': (12,20),
    'AP': (13,20),
    'AQ': (17,20),
    'AR': (18,20),
    'AS': (3,19),
    'AT': (0,18),
    'AU': (3,18),
    'AV': (7,18),
    'AW': (13,18),
    'AX': (1,17),
    'AY': (6,17),
    'AZ': (14,17),
    'BA': (1,15),
    'BB': (2,15),
    'BC': (5,15),
    'BD': (6,15),
    'BE': (12,15),
    'BF': (13,15),
    'BG': (17,14),
    'BH': (18,14),
    'BI': (0,12),
    'BJ': (7,12),
    'BK': (13,12),
    'BL': (14,12),
    'BM': (16,12),
    'BN': (17,12),
    'BO': (23,12),
    'BP': (1,11),
    'BQ': (6,11),
    'BR': (13,11),
    'BS': (17,11),
    'BT': (22,11),
    'BU': (1,9),
    'BV': (6,9),
    'BW': (13,9),
    'BX': (17,9),
    'BY': (22,9),
    'BZ': (0,8),
    'CA': (7,8),
    'CB': (10,8),
    'CC': (13,8),
    'CD': (14,8),
    'CE': (16,8),
    'CF': (17,8),
    'CG': (23,8),
    'CH': (10,7),
    'CI': (21,5),
    'CJ': (22,5),
    'CK': (5,4),
    'CL': (6,4),
    'CM': (12,4),
    'CN': (13,4),
    'CO': (19,2),
    'CP': (0,1),
    'CQ': (1,1),
    'CR': (7,1),
    'CS': (14,1),
    'CT': (16,1),
    'CU': (19,1),
    'CV': (22,1),
    'CW': (0,0),
    'CX': (6,0),
    'CY': (13,0),
    'CZ': (17,0),
    'DA': (22,0),
    'DB': (23,0),
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

    def shortest_path_coordinates(self, vertex):
        path = self.build_path(vertex)
        return [nodo_coordenada[vertex] for vertex in path]

class DijkstraCoordinate(Dijkstra):
    """
    To get shortest path between two coordinates, using the parameters as coordinates, not as letters
    """
    def __init__(self, graph, start_coordinate):
        self.graph = graph
        vertex_from_coordinate = [i for i in nodo_coordenada if nodo_coordenada[i] == start_coordinate][0]
        self.start_vertex = vertex_from_coordinate
        self.vertices = list(graph.keys())

        # distance: minimum distance from start vertex
        self.vertex_labels = {
            vertex: {'distance': math.inf, 'prev': '-'} for vertex in self.vertices}

        # Obviously, the start vertex has no distance from itself
        self.vertex_labels[vertex_from_coordinate]['distance'] = 0

    def shortest_path_coordinates(self, coordinate):
        vertex_from_coordinate = [i for i in nodo_coordenada if nodo_coordenada[i] == coordinate][0]
        path = self.build_path(vertex_from_coordinate)
        return [nodo_coordenada[vertex] for vertex in path]


if __name__ == '__main__':
    dijkstraCity = DijkstraCoordinate(graph=simCity, start_coordinate=(3,22))
    dijkstraCity.dijkstra()
    print(dijkstraCity.shortest_path_coordinates((18,14)))
