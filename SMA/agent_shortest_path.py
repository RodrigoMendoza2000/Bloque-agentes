from mesa import Agent
import random
from shortespath import DijkstraCoordinate, simCity, nodo_coordenada

class Car(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of eight directions
    """
    def __init__(self, unique_id, model):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        self.turning = False
        self.direction = None
        self.on_road = False
        # If the car must be assigned a destionation to start on the road
        self.must_be_assigned_destination = True
        # The final destination where the car will park
        self.final_destination = None
        # If the car is parking
        self.parking = False
        # From which destination the car came from
        self.from_destination = None
        

    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """
        # print(f"Agente: {self.unique_id} movimiento {self.direction}, final destination {self.final_destination}, is parking {self.parking}")
        #print(f"Agente: {self.unique_id} direction {self.direction}")
        

        # If the car is not present on the road and must be assigned a destination
        if self.must_be_assigned_destination:
            random_destination = random.choice(self.model.destination_entrance)
            # Safety counter in case there is no available position
            safety_counter = 0
            while self.has_next_step_agent(random_destination, "Car") and safety_counter < 100:
                random_destination = random.choice(self.model.destination_entrance)
                self.from_destination = random_destination
                safety_counter += 1
                # print(self.has_next_step_agent(random_destination, "Car"))
            if safety_counter < 100:
                self.model.grid.place_agent(self, random_destination)
                self.must_be_assigned_destination = False
                self.from_destination = random_destination
                
                return 
            # If there is no available destination in 100 iterations, wait
            else:
                return

        if self.final_destination is None:
            self.final_destination = random.choice(self.model.destination_positions)
            while self.final_destination == self.from_destination:
                self.final_destination = random.choice(self.model.destination_positions)

            dijkstraCity = DijkstraCoordinate(graph=simCity, start_coordinate=self.from_destination)
            dijkstraCity.dijkstra()
            self.path = dijkstraCity.shortest_path_coordinates(self.final_destination)
        

        if self.pos == self.path[0]:
            self.path.pop(0)

        if len(self.path) == 0:
            self.model.grid.remove_agent(self)
            # reset all the instance variables
            self.turning = False
            self.direction = None
            self.on_road = False
            self.must_be_assigned_destination = True
            self.final_destination = None
            self.parking = False
            self.from_destination = None
            return
        
        if self.pos[0] == self.path[0][0] and self.pos[1] - self.path[0][1] > 0:
            self.direction = "Down"
            next_step = self.next_step_based_on_direction_self()
            if self.is_position_valid_for_parking(next_step):
                self.model.grid.move_agent(self, next_step)
        elif self.pos[0] == self.path[0][0] and self.pos[1] - self.path[0][1] < 0:
            self.direction = "Up"
            next_step = self.next_step_based_on_direction_self()
            if self.is_position_valid_for_parking(next_step):
                self.model.grid.move_agent(self, next_step)
        elif self.pos[0] - self.path[0][0] > 0 and self.pos[1] == self.path[0][1]:
            self.direction = "Left"
            next_step = self.next_step_based_on_direction_self()
            if self.is_position_valid_for_parking(next_step):
                self.model.grid.move_agent(self, next_step)
        elif self.pos[0] - self.path[0][0] < 0 and self.pos[1] == self.path[0][1]:
            self.direction = "Right"
            next_step = self.next_step_based_on_direction_self()
            if self.is_position_valid_for_parking(next_step):
                self.model.grid.move_agent(self, next_step)

        print(f"Agente: {self.unique_id} path {self.path}")
            

        

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        # print(f"Agente: {self.unique_id} movimiento {self.direction}")
        self.move()

    def is_road(self, cell):
        """
        If the cell is a road, returns True; otherwise, returns False
        """
        for agent in self.model.grid.get_cell_list_contents([cell]):
            if isinstance(agent, Road):
                return True
        return False

    def get_current_road_direction(self):
        """
        Get the current direction of the cell the agent is in
        """
        for agent in self.model.grid.get_cell_list_contents([self.pos]):
            if isinstance(agent, Road):
                return agent.direction
        return None

    def next_step_based_on_direction(self, stuck=False):
        """
        Returns the next step based on the direction the agent is facing if not standing on road,
        else get the next step based on the direction of the road
        """
        direction = self.get_current_road_direction()
        # print(f"\nAgente: {self.unique_id} direction {direction}")
        # For when the car is on a road that has a traffic light
        if direction is None and self.direction is not None:
            if self.direction == "Down":
                return (self.pos[0], self.pos[1] - 1)
            # Up
            elif self.direction == "Up":
                return (self.pos[0], self.pos[1] + 1)
            # Left
            elif self.direction == "Left":
                return (self.pos[0] - 1, self.pos[1])
            # Right
            elif self.direction == "Right":
                return (self.pos[0] + 1, self.pos[1])
        else:
            if stuck:
                direction = self.get_road_direction_if_stuck()
                
            # Down
            if direction == "Down":
                return (self.pos[0], self.pos[1] - 1)
            # Up
            elif direction == "Up":
                return (self.pos[0], self.pos[1] + 1)
            # Left
            elif direction == "Left":
                return (self.pos[0] - 1, self.pos[1])
            # Right
            elif direction == "Right":
                return (self.pos[0] + 1, self.pos[1])


    def next_step_based_on_direction_self(self):
        """
        Get the next step based on the direction the agent is facing
        """
        if self.direction == "Down":
                return (self.pos[0], self.pos[1] - 1)
        # Up
        elif self.direction == "Up":
            return (self.pos[0], self.pos[1] + 1)
        # Left
        elif self.direction == "Left":
            return (self.pos[0] - 1, self.pos[1])
        # Right
        elif self.direction == "Right":
            return (self.pos[0] + 1, self.pos[1])

    def is_position_valid(self, position):
        """
        Checks if the position is valid by not being out of bounds, is a road or is a traffic light on green
        """ 
        if not self.model.grid.out_of_bounds(position):
            cell_content = self.model.grid.get_cell_list_contents([position])
            if len(cell_content) == 1 and (isinstance(cell_content[0], Road) or isinstance(cell_content[0], Traffic_Light)):
                if isinstance(cell_content[0], Traffic_Light):
                    if cell_content[0].state:
                        return True
                    else:
                        return False
                return True
        return False

    def is_position_valid_for_parking(self, position):
        """
        Checks if the position is valid by not being out of bounds, is a road or is a traffic light on green
        """ 
        if not self.model.grid.out_of_bounds(position):
            cell_content = self.model.grid.get_cell_list_contents([position])
            if len(cell_content) == 1 and (isinstance(cell_content[0], Road) or isinstance(cell_content[0], Traffic_Light)) or isinstance(cell_content[0], Destination):
                if isinstance(cell_content[0], Traffic_Light):
                    if cell_content[0].state:
                        return True
                    else:
                        return False
                return True
        return False
    


class Traffic_Light(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model, state = False, timeToChange = 10):
        super().__init__(unique_id, model)
        self.state = state
        self.timeToChange = timeToChange

    def step(self):
        # if self.model.schedule.steps % self.timeToChange == 0:
        #     self.state = not self.state
        pass

class Destination(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Road(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model, direction= "Left"):
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass

class Sidewalk(Agent):
    """
    Sidewalk agent for the people to be in
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass
    
class Brush(Agent):
    """
    Brush agent for obstacles
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass
    
class Busdestination(Agent):
    """
    Destination agent for busses
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass
    
class Person(Agent):
    """
    Person agent
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

