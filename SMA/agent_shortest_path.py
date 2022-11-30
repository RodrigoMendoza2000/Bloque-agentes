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
        # Indicate if the agent is turning
        self.turning = False
        # The current direction of the agent
        self.direction = None
        # If the car is currently in a road or a destination
        self.on_road = False
        # If the car must be assigned a destionation to start on the road
        self.must_be_assigned_destination = True
        # The final destination where the car will park
        self.final_destination = None
        # If the car is parking (reaching the destination)
        self.parking = False
        # From which destination/position the car came from
        self.from_destination = None

    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """

        # If the car is not present on the road 
        # and must be assigned a destination to start on the road
        if self.must_be_assigned_destination:
            # The 4 destination entrances are the 4 edges of the map
            random_destination = random.choice(self.model.destination_entrance)
            # Safety counter in case there is no available position
            safety_counter = 0
            while self.has_next_step_agent(random_destination, "Car") and safety_counter < 100:
                random_destination = random.choice(
                    self.model.destination_entrance)
                self.from_destination = random_destination
                safety_counter += 1
            if safety_counter < 100:
                self.model.grid.place_agent(self, random_destination)
                self.must_be_assigned_destination = False
                self.from_destination = random_destination
                return
            # If there is no available destination in 100 iterations, wait for the next step
            else:
                return

        # Assign the final destination where the agent needs to go
        if self.final_destination is None:
            # Select a final destination from the list of destination agents
            self.final_destination = random.choice(
                self.model.destination_positions)
            # Final destination and origin destination cannot be the same
            while self.final_destination == self.from_destination:
                self.final_destination = random.choice(
                    self.model.destination_positions)

            # Apply the Dijkstra algorithm to find the shortest path to the final destination
            dijkstraCity = DijkstraCoordinate(
                graph=simCity, start_coordinate=self.from_destination)
            dijkstraCity.dijkstra()
            self.path = dijkstraCity.shortest_path_coordinates(
                self.final_destination)

        # If the car is in the current coordinate of the ideal path, 
        # pop it to go to the next coordinate
        if self.pos == self.path[0]:
            self.path.pop(0)

        # If it is a new agent, set parking to False
        if self.parking and len(self.path) > 0:
            self.parking = False

        # If the car has arrived to the final destination, remove the agent and reset instance variables
        # to allow a new car to spawn
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
        
        # All positions before the roundabout
        self.roundabout_coordinates = [(12,9), (12,8), (13,13), (14,13), (18,12), (18,11), (16,7),(17,7)]

        # If it is on a position before entering the roundabout, check diagonally if there is any car,
        # if there is, wait for the next step
        if self.pos in self.roundabout_coordinates:
            moore_roundabout = self.moore_roundabout()
            if self.is_position_valid_for_parking(moore_roundabout):
                pass
            else:
                return
            
        # Go to position depending on the position of the node and self direction
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

        # To make the turning variable True to allow a smoother transition in Unity
        if len(self.path) > 1:
            if self.pos[0] == self.path[1][0] and self.pos[1] - self.path[1][1] > 0:
                self.set_turn_conditional("Down")
            elif self.pos[0] == self.path[1][0] and self.pos[1] - self.path[1][1] < 0:
                self.set_turn_conditional("Up")
            elif self.pos[0] - self.path[1][0] > 0 and self.pos[1] == self.path[1][1]:
                self.set_turn_conditional("Left")
            elif self.pos[0] - self.path[1][0] < 0 and self.pos[1] == self.path[1][1]:
                self.set_turn_conditional("Right")

    def step(self):
        self.move()

    def next_step_based_on_direction_self(self):
        """
        Get the coordinates of where the agent must move
        based on the direction the agent is facing

        Returns:
            tuple(int, int): The coordinates of the next step
        """
        if self.direction == "Down":
            return (self.pos[0], self.pos[1] - 1)
        elif self.direction == "Up":
            return (self.pos[0], self.pos[1] + 1)
        elif self.direction == "Left":
            return (self.pos[0] - 1, self.pos[1])
        elif self.direction == "Right":
            return (self.pos[0] + 1, self.pos[1])

    def is_position_valid_for_parking(self, position):
        """
        Checks if the position given is valid by not being out of bounds, 
        is a road or is a traffic light on green or it is a parking spot (destination)


        Args:
            position (tuple(int, int)): The coordinates of the position to check

        Returns:
            bool: True if the position is valid, False otherwise
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

        Args:
            next_step (tuple(int, int)): the coordinates of where the agent will go next
            agent_type (string): The name of the agent type to check for

        Returns:
            bool: returns True if the next step has an agent of the type specified, False otherwise
        """
        next_self_content = self.model.grid.get_cell_list_contents([next_step])
        next_self_content = [
            type(agent).__name__ for agent in next_self_content]
        if agent_type in next_self_content:
            return True
        return False

    def set_turn_conditional(self, next_direction):
        """
        Changes between turning and not turning based on the next direction

        Args:
            next_direction (string): the direction that will follow the current self direction
        """
        if self.direction != next_direction and self.direction is not None:
            self.turning = True
        else:
            self.turning = False
            
    def moore_roundabout(self):
        """
        The diagonal position of the agent depending 
        on its direction for the roundabout to be more smooth 
        and follow vehicular traffic rules

        Returns:
            tuple(int, int): the coordinates of the diagonal position
        """
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
    Traffic light agent where the cars/busses will stop if the light is red
    state = True means green/go
    state = False means red/shop
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

        # Initialize the direction of where the cars are coming from
        if self.direction is None:
            self.direction = self.get_direction_of_cars()

        # Get the traffic light which is next to the current one
        if self.partner is None:
            self.partner = self.get_partner()

        # Get both traffic lights that are opposing
        if self.opposing_traffic_lights == ():
            self.opposing_traffic_lights = self.get_opposing_traffic_lights()

        # Will get the number of cars that are in the next 3 positions
        self.current_cars = self.get_number_of_cars(3)
        # Get partner's and add it to self to get the total number of cars in that street
        self.total_cars = self.current_cars + self.get_number_cars_from_partner()

        # If the number of cars is greater than the opposing two traffic lights,
        # turn green and turn red the two opposing traffic lights
        if self.total_cars > self.get_opposing_traffic_lights_cars():
            self.state = True
            self.partner.state = True
            for agent in self.opposing_traffic_lights:
                agent.state = False

        elif self.total_cars == self.get_opposing_traffic_lights_cars():
            pass

    def get_opposing_traffic_lights(self):
        """
        Gets the two traffic lights opposing self

        Returns:
            list: list with the two opposing traffic lights
        """
        opposing_traffic_lights = []
        for agent in self.model.grid.iter_neighbors(self.pos, moore=True, radius=3):
            if isinstance(agent, Traffic_Light) and agent != self.partner:
                opposing_traffic_lights.append(agent)
        return opposing_traffic_lights

    def get_opposing_traffic_lights_cars(self):
        """
        Gets the number of cars following both traffic lights

        Returns:
            int: Sum of both traffic light cars
        """
        opposing_traffic_lights_cars = 0
        for agent in self.opposing_traffic_lights:
            opposing_traffic_lights_cars += agent.current_cars
        return opposing_traffic_lights_cars

    def get_partner(self):
        """
        Gets the traffic light next to self

        Returns:
            Traffic_Light: agent instance of partner
        """
        for agent in self.model.grid.iter_neighbors(self.pos, moore=False):
            if isinstance(agent, Traffic_Light):
                return agent

    def get_number_cars_from_partner(self):
        """
        Gets the number of cars of the traffic light next to self
        
        Returns:
            int: number of cars following partner traffic light
        """
        for agent in self.model.grid.iter_neighbors(self.pos, moore=False):
            if isinstance(agent, Traffic_Light):
                return agent.current_cars

    def get_number_of_cars(self, number_positions):
        """
        Gets the number of cars following x positions of the traffic light

        Args:
            number_positions (int): The amount of cells to check

        Returns:
            int: number of cars
        """
        number_cars = 0
        far_away_cars = number_positions
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
                        number_cars += (1 * far_away_cars)
            far_away_cars -= 1
        return number_cars

    def get_direction_of_cars(self):
        """
        Returns where the cars are coming from according to the direction of the road

        Returns:
            string: direction of the road where the cars are coming from (Up, Down, Left, Right)
        """
        partner_direction = self.get_partner_position()
        for agent in self.model.grid.iter_neighbors(self.pos, moore=False):
            if isinstance(agent, Road):
                if (partner_direction in ("Up", "Down")) and (agent.direction in ("Left", "Right")):
                    return agent.direction
                elif (partner_direction in ("Left", "Right")) and (agent.direction in ("Up", "Down")):
                    return agent.direction
        return None

    def get_partner_position(self):
        """
        Get if the partner is above, below, left or right of self

        Returns:
            string: direction of the partner (Up, Down, Left, Right)
        """
        
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
    The final destination of every car, where the car will arrive
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
    Road agent. For the cars and busses to move on
    """

    def __init__(self, unique_id, model, direction="Left"):
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass


class Sidewalk(Agent):
    """
    Sidewalk agent for the people walk in
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
    Destination agent for all bus stops
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass


class Bus(Car):
    """
    Bus agent that will follow a predetermined route and will go through 
    every bus destination picking up people and dropping them off
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        # The predetermined path that the bus will follow
        self.path = [(22, 24), (13, 24), (13, 17), (1, 17),
                     (1, 8), (14, 8), (14, 1), (22, 1), (22, 24)]
        # A list of all the person agents that the bus is carrying
        self.people_inside = []
        # If the bus is currently waiting in a bus destination
        self.stopping = False
        # How much time the bus has left to wait in the bus destination
        self.waiting_time = 0

    def step(self):
        
        # If the bus is in the first element of its path, 
        # pop that element to follow the next road
        if self.pos == self.path[0]:
            self.path.pop(0)

        # If the bus has made a full loop of its path, 
        # reset the path it will follow so it can start again
        if len(self.path) == 0:
            self.path = [(22, 24), (13, 24), (13, 17), (1, 17),
                         (1, 8), (14, 8), (14, 1), (22, 1), (22, 24)]
            
        # If the bus is in a bus destination and waiting, wait 3 steps then move.
        if self.stopping:
            self.waiting_time += 1
            if self.waiting_time == 2:
                self.stopping = False
                self.waiting_time = 0
            return

        # Follow the path of the bus until it reaches the next element in the list 
        # setting if the bus is turning and its current direction
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
                
        # If the bus is in a bus destination, 
        # and there is someone waiting for the bus, picks them up
        for agent in self.model.grid.iter_neighbors(self.pos, moore=False):
            if isinstance(agent, Person):
                if agent.waiting_for_bus:
                    self.people_inside.append(agent)
                    agent.waiting_for_bus = False
                    agent.in_bus = True
                    agent.bus = self
                    agent.original_destination = agent.pos
        
        # Everytime the bus moves, move the people inside the bus with it
        for agent in self.people_inside:
            agent.model.grid.move_agent(agent, self.pos)
            
        # If the bus is in a bus destination, stop for 3 steps in the bus destination
        for agent in self.model.grid.iter_neighbors(self.pos, moore=False):
            if isinstance(agent, Busdestination) and self.stopping == False:
                self.stopping = True


class Person(Agent):
    """
    Person agent that will move around the sidewalk, and will be able to get into a bus
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        # A random direction that will determine where the agent will move, 
        # clockwise or counter clockwise
        self.initial_direction = random.choice(["Left", "Right"])
        # The direction where the agent will move
        self.direction = self.initial_direction
        # If the person is in a bus or not
        self.in_bus = False
        # If the person is staying in the BusDestination
        self.waiting_for_bus = False
        # The bus agent of where the person is current in
        self.bus = None
        # The original bus destination where the person will be picked off
        self.original_destination = None

    def step(self):

        # If the person passes through the BusDestination, it will have a 10% chance of waiting for a bus
        if not self.in_bus and "Busdestination" in self.get_cell_class_names(self.pos):
            decision_bus_stop = random.choice([0 for _ in range(9)] + [1])
            if decision_bus_stop == 1:
                self.waiting_for_bus = True

        # Stay in the bus destination until the bus picks them up
        if self.waiting_for_bus:
            return

        # If the person is in a bus, it will have a 33% chance of getting 
        # off the bus when the bus is in a bus destination
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

        # The person will wander either clockwise or counter 
        # clockwise until it is waiting for a bus
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
        Checks if the position is valid by not being out of bounds, 
        is a road or is a traffic light on green

        Args:
            position (tuple(int, int)): The position in the grid to check

        Returns:
            bool: True if the position is valid, False otherwise
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
        Get all the class names of the agents in the cell

        Args:
            position (tuple(int, int)): The position in the grid to check

        Returns:
            list: A list of the class name of every agent in the cell
        """
        cell_content = self.model.grid.get_cell_list_contents([position])
        return [type(agent).__name__ for agent in cell_content]

    def next_step_based_on_direction(self, direction):
        """
        Get the next position based on the direction

        Args:
            direction (string): The direction to move into (Up, Down, Left, Right)

        Returns:
            tuple(int, int): The coordinates of the cell to move into
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
        Know where to move next depending on the direction and the initial direction

        Args:
            direction (string): The current direction of the agent
            initial_direction (string): The direction assigned at the initialization of the agent

        Returns:
            string: The next direction to move into and be assigned to the agent
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
