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
                random_destination = random.choice(
                    self.model.destination_entrance)
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
            self.final_destination = random.choice(
                self.model.destination_positions)
            while self.final_destination == self.from_destination:
                self.final_destination = random.choice(
                    self.model.destination_positions)

            dijkstraCity = DijkstraCoordinate(
                graph=simCity, start_coordinate=self.from_destination)
            dijkstraCity.dijkstra()
            self.path = dijkstraCity.shortest_path_coordinates(
                self.final_destination)

        if self.pos == self.path[0]:
            self.path.pop(0)

        if self.parking and len(self.path) > 0:
            self.parking = False

        if len(self.path) == 0:
            self.model.grid.remove_agent(self)
            # reset all the instance variables
            self.turning = False
            self.direction = None
            self.on_road = False
            self.must_be_assigned_destination = True
            self.final_destination = None
            self.parking = True
            self.from_destination = None
            return
        
        
        self.roundabout_coordinates = [(12,9), (12,8), (13,13), (14,13), (18,12), (18,11), (16,7),(17,7)]

        if self.pos in self.roundabout_coordinates:
            moore_roundabout = self.moore_roundabout()
            if self.is_position_valid_for_parking(moore_roundabout):
                pass
            else:
                return
            
        if self.pos[0] == self.path[0][0] and self.pos[1] - self.path[0][1] > 0:
            # self.set_turn_conditional("Down")
            self.direction = "Down"
            next_step = self.next_step_based_on_direction_self()
            if self.is_position_valid_for_parking(next_step):
                self.model.grid.move_agent(self, next_step)
        elif self.pos[0] == self.path[0][0] and self.pos[1] - self.path[0][1] < 0:
            # self.set_turn_conditional("Up")
            self.direction = "Up"
            next_step = self.next_step_based_on_direction_self()
            if self.is_position_valid_for_parking(next_step):
                self.model.grid.move_agent(self, next_step)
        elif self.pos[0] - self.path[0][0] > 0 and self.pos[1] == self.path[0][1]:
            # self.set_turn_conditional("Left")
            self.direction = "Left"
            next_step = self.next_step_based_on_direction_self()
            if self.is_position_valid_for_parking(next_step):
                self.model.grid.move_agent(self, next_step)
        elif self.pos[0] - self.path[0][0] < 0 and self.pos[1] == self.path[0][1]:
            # self.set_turn_conditional("Right")
            self.direction = "Right"
            next_step = self.next_step_based_on_direction_self()
            if self.is_position_valid_for_parking(next_step):
                self.model.grid.move_agent(self, next_step)

        if len(self.path) > 1:
            if self.pos[0] == self.path[1][0] and self.pos[1] - self.path[1][1] > 0:
                self.set_turn_conditional("Down")
            elif self.pos[0] == self.path[1][0] and self.pos[1] - self.path[1][1] < 0:
                self.set_turn_conditional("Up")
            elif self.pos[0] - self.path[1][0] > 0 and self.pos[1] == self.path[1][1]:
                self.set_turn_conditional("Left")
            elif self.pos[0] - self.path[1][0] < 0 and self.pos[1] == self.path[1][1]:
                self.set_turn_conditional("Right")

        #print(f"Agente: {self.unique_id} is turning {self.turning}, path {self.path}")

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

    def has_next_step_agent(self, next_step, agent_type):
        """
        Checks if the next step has an agent of the type specified
        """
        next_self_content = self.model.grid.get_cell_list_contents([next_step])
        next_self_content = [
            type(agent).__name__ for agent in next_self_content]
        if agent_type in next_self_content:
            return True
        return False

    def standing_on_light(self):
        """
        Checks if the agent is standing on a traffic light
        """
        # state: False = red, True = green
        cell_content = self.model.grid.get_cell_list_contents([self.pos])
        for agent in cell_content:
            if isinstance(agent, Traffic_Light):
                if agent.state:
                    return True
        return False

    def set_turn_conditional(self, next_direction):
        """
        Changes between turning and not turning based on the next direction
        """
        if self.direction != next_direction and self.direction is not None:
            self.turning = True
        else:
            self.turning = False
            
    def moore_roundabout(self):
        if self.direction == "Down":
            return (self.pos[0] + 1, self.pos[1] - 1)
        elif self.direction == "Up":
            return (self.pos[0] - 1, self.pos[1] + 1)
        elif self.direction == "Left":
            return (self.pos[0] - 1, self.pos[1] - 1)
        elif self.direction == "Right":
            return (self.pos[0] + 1, self.pos[1] + 1)
        return (self.pos[0], self.pos[1])


class Traffic_Light(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """

    def __init__(self, unique_id, model, state=False, timeToChange=10):
        super().__init__(unique_id, model)
        self.state = state
        self.timeToChange = timeToChange
        # The current cars that the sole traffic light is looking
        self.current_cars = 0
        # The direction from which the cars are coming
        self.direction = None
        # The traffic light next to it
        self.partner = None
        # The traffic lights that are contrary the traffic light
        self.opposing_traffic_lights = ()
        # All current cars counting the ones of the neighbours
        self.total_cars = 0

    def step(self):
        # if self.model.schedule.steps % self.timeToChange == 0:
        #     self.state = not self.state

        if self.direction is None:
            self.direction = self.get_direction_of_cars()

        if self.partner is None:
            self.partner = self.get_partner()

        if self.opposing_traffic_lights == ():
            self.opposing_traffic_lights = self.get_opposing_traffic_lights()

        self.current_cars = self.get_number_of_cars(3)
        self.total_cars = self.current_cars + self.get_number_cars_from_partner()
        # if self.current_cars != 0:
        #    print(f"Agente: {self.unique_id} cars: {self.current_cars}")
        if self.total_cars > self.get_opposing_traffic_lights_cars():
            self.state = True
            self.partner.state = True
            for agent in self.opposing_traffic_lights:
                agent.state = False

        elif self.total_cars == self.get_opposing_traffic_lights_cars():
            pass

    def get_opposing_traffic_lights(self):
        opposing_traffic_lights = []
        for agent in self.model.grid.iter_neighbors(self.pos, moore=True, radius=3):
            if isinstance(agent, Traffic_Light) and agent != self.partner:
                opposing_traffic_lights.append(agent)
        return opposing_traffic_lights

    def get_opposing_traffic_lights_cars(self):
        opposing_traffic_lights_cars = 0
        for agent in self.opposing_traffic_lights:
            opposing_traffic_lights_cars += agent.current_cars
        return opposing_traffic_lights_cars

    def get_id(self):
        return self.unique_id

    def get_partner(self):
        """
        Gets the partner of the traffic light
        """
        for agent in self.model.grid.iter_neighbors(self.pos, moore=False):
            if isinstance(agent, Traffic_Light):
                return agent

    def get_number_cars_from_partner(self):
        for agent in self.model.grid.iter_neighbors(self.pos, moore=False):
            if isinstance(agent, Traffic_Light):
                return agent.current_cars

    def get_number_of_cars(self, number_positions):
        """
        Gets the number of cars in the traffic light
        """
        number_cars = 0
        for x in range(0, number_positions + 1):
            if self.direction == "Up":
                next_step = (self.pos[0], self.pos[1] - x)
            elif self.direction == "Down":
                next_step = (self.pos[0], self.pos[1] + x)
            elif self.direction == "Left":
                next_step = (self.pos[0] + x, self.pos[1])
            elif self.direction == "Right":
                next_step = (self.pos[0] - x, self.pos[1])

            if self.model.grid.out_of_bounds(next_step):
                number_cars += 0
            else:
                cell_content = self.model.grid.get_cell_list_contents([
                                                                      next_step])
                for agent in cell_content:
                    if isinstance(agent, Car):
                        number_cars += 1
        return number_cars

    def get_direction_of_cars(self):
        partner_direction = self.get_partner_position()
        for agent in self.model.grid.iter_neighbors(self.pos, moore=False):
            if isinstance(agent, Road):
                if (partner_direction in ("Up", "Down")) and (agent.direction in ("Left", "Right")):
                    return agent.direction
                elif (partner_direction in ("Left", "Right")) and (agent.direction in ("Up", "Down")):
                    return agent.direction
        return None

    def get_partner_position(self):
        partner_pos = ()
        for agent in self.model.grid.iter_neighbors(self.pos, moore=False):
            if isinstance(agent, Traffic_Light):
                partner_pos = agent.pos

        if self.pos[0] - partner_pos[0] > 0:
            return "Left"
        elif self.pos[0] - partner_pos[0] < 0:
            return "Right"
        elif self.pos[1] - partner_pos[1] > 0:
            return "Down"
        elif self.pos[1] - partner_pos[1] < 0:
            return "Up"


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

    def __init__(self, unique_id, model, direction="Left"):
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass


class Sidewalk(Agent):
    """
    Sidewalk agent for the people to be in
    """

    def __init__(self, unique_id, model, direction="Left"):
        super().__init__(unique_id, model)
        self.direction = direction

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
    Destination agent for busses destination
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass


class Bus(Car):
    """
    Destination agent for busses
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.path = [(22, 24), (13, 24), (13, 17), (1, 17),
                     (1, 8), (14, 8), (14, 1), (22, 1), (22, 24)]
        self.people_inside = []
        self.stopping = False
        self.waiting_time = 0

    def step(self):
        
        if self.pos == self.path[0]:
            self.path.pop(0)

        if len(self.path) == 0:
            self.path = [(22, 24), (13, 24), (13, 17), (1, 17),
                         (1, 8), (14, 8), (14, 1), (22, 1), (22, 24)]
            
        
            
        if self.stopping:
            self.waiting_time += 1
            if self.waiting_time == 2:
                self.stopping = False
                self.waiting_time = 0
            return

        if self.pos[0] == self.path[0][0] and self.pos[1] - self.path[0][1] > 0:
            self.set_turn_conditional("Down")
            self.direction = "Down"
            next_step = self.next_step_based_on_direction_self()
            if self.is_position_valid_for_parking(next_step):
                self.model.grid.move_agent(self, next_step)
        elif self.pos[0] == self.path[0][0] and self.pos[1] - self.path[0][1] < 0:
            self.set_turn_conditional("Up")
            self.direction = "Up"
            next_step = self.next_step_based_on_direction_self()
            if self.is_position_valid_for_parking(next_step):
                self.model.grid.move_agent(self, next_step)
        elif self.pos[0] - self.path[0][0] > 0 and self.pos[1] == self.path[0][1]:
            self.set_turn_conditional("Left")
            self.direction = "Left"
            next_step = self.next_step_based_on_direction_self()
            if self.is_position_valid_for_parking(next_step):
                self.model.grid.move_agent(self, next_step)
        elif self.pos[0] - self.path[0][0] < 0 and self.pos[1] == self.path[0][1]:
            self.set_turn_conditional("Right")
            self.direction = "Right"
            next_step = self.next_step_based_on_direction_self()
            if self.is_position_valid_for_parking(next_step):
                self.model.grid.move_agent(self, next_step)
                
        for agent in self.model.grid.iter_neighbors(self.pos, moore=False):
            if isinstance(agent, Person):
                if agent.waiting_for_bus:
                    self.people_inside.append(agent)
                    agent.waiting_for_bus = False
                    agent.in_bus = True
                    agent.bus = self
                    agent.original_destination = agent.pos
        
        for agent in self.people_inside:
            agent.model.grid.move_agent(agent, self.pos)
            
        for agent in self.model.grid.iter_neighbors(self.pos, moore=False):
            if isinstance(agent, Busdestination) and self.stopping == False:
                self.stopping = True


class Person(Agent):
    """
    Person agent
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.initial_direction = random.choice(["Left", "Right"])
        self.direction = self.initial_direction
        self.in_bus = False
        self.waiting_for_bus = False
        self.bus = None
        self.original_destination = None

    def step(self):

        if not self.in_bus and "Busdestination" in self.get_cell_class_names(self.pos):
            decision_bus_stop = random.choice([0 for _ in range(9)] + [1])
            if decision_bus_stop == 1:
                self.waiting_for_bus = True

        if self.waiting_for_bus:
            return

        if self.in_bus:
            for agent in self.model.grid.iter_neighbors(self.pos, moore=False):
                if isinstance(agent, Busdestination) and agent.pos != self.original_destination:
                    decision_bus_stop = random.choice(
                        [0 for _ in range(2)] + [1])
                    if decision_bus_stop == 1:
                        self.waiting_for_bus = False
                        self.in_bus = False
                        self.model.grid.move_agent(self, agent.pos)
                        self.bus.people_inside.remove(self)
                        self.bus = None
                        self.direction = self.initial_direction
                        return
            return

        next_position = self.next_step_based_on_direction(self.direction)
        if self.is_valid_position(next_position):
            self.model.grid.move_agent(self, next_position)
        else:
            self.direction = self.next_direction(
                self.direction, self.initial_direction)
            next_position = self.next_step_based_on_direction(self.direction)
            while not self.is_valid_position(next_position):
                self.direction = self.next_direction(
                    self.direction, self.initial_direction)
                next_position = self.next_step_based_on_direction(
                    self.direction)
            self.model.grid.move_agent(self, next_position)

    def is_valid_position(self, position):
        """
        Checks if the position is valid by not being out of bounds, is a road or is a traffic light on green
        """
        if not self.model.grid.out_of_bounds(position):
            cell_content = self.get_cell_class_names(position)
            if "Road" in cell_content or "Traffic_Light" in cell_content or "Obstacle" in cell_content:
                return False
            else:
                return True

        return False

    def get_cell_class_names(self, position):
        """
        Gets the class name of the cell
        """
        cell_content = self.model.grid.get_cell_list_contents([position])
        return [type(agent).__name__ for agent in cell_content]

    def next_step_based_on_direction(self, direction):
        """
        Gets the next step based on the direction
        """
        if direction == "Up":
            return (self.pos[0], self.pos[1] + 1)
        elif direction == "Down":
            return (self.pos[0], self.pos[1] - 1)
        elif direction == "Left":
            return (self.pos[0] - 1, self.pos[1])
        elif direction == "Right":
            return (self.pos[0] + 1, self.pos[1])
        else:
            return None

    def next_direction(self, direction, initial_direction):
        """
        Gets the next direction of the person
        """
        if direction == "Up":
            if initial_direction == "Left":
                return "Left"
            elif initial_direction == "Right":
                return "Right"
        elif direction == "Down":
            if initial_direction == "Left":
                return "Right"
            elif initial_direction == "Right":
                return "Left"
        elif direction == "Left":
            if initial_direction == "Left":
                return "Down"
            elif initial_direction == "Right":
                return "Up"
        elif direction == "Right":
            if initial_direction == "Left":
                return "Up"
            elif initial_direction == "Right":
                return "Down"
        else:
            return None
