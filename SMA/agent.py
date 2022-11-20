from mesa import Agent
import random

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
        

    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """
        """possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False, # Boolean for whether to use Moore neighborhood (including diagonals) or Von Neumann (only up/down/left/right).
            include_center=False) 
        print(possible_steps)
        
        # Checks which grid cells are empty
        freeSpaces = list(map(self.is_road, possible_steps))
        print(freeSpaces)

        next_moves = [p for p,f in zip(possible_steps, freeSpaces) if f == True]
        print(next_moves)
       
        next_move = self.random.choice(next_moves)
        # Now move:
        if self.random.random() < 0.1:
            self.model.grid.move_agent(self, next_move)
            self.steps_taken+=1

        # If the cell is empty, moves the agent to that cell; otherwise, it stays at the same position
        if freeSpaces[self.direction]:
            self.model.grid.move_agent(self, possible_steps[self.direction])
            print(f"Se mueve de {self.pos} a {possible_steps[self.direction]}; direction {self.direction}")
        else:
            print(f"No se puede mover de {self.pos} en esa direccion.")"""

        # Get the class names of the agents in the cell the car is in
        current_self_content = self.model.grid.get_cell_list_contents([self.pos])
        current_self_content = [type(agent).__name__ for agent in current_self_content] 
        
        if self.turning:
            # If it reached the destination of the turn, it stops turning
            if self.direction == self.get_current_road_direction():
                self.turning = False
                self.direction = None
                return 
            # If it is still turning, it moves in the direction of the turn
            next_step = self.next_step_based_on_direction_self()
            if self.is_position_valid(next_step):
                self.model.grid.move_agent(self, next_step)
                return
            # If its not able to move, stops moving
            else:
                return

        if "Traffic_Light" in current_self_content or self.get_front_agents_traffic_light_on():
            for agent in self.model.grid.get_cell_list_contents([self.pos]):
                if isinstance(agent, Traffic_Light):
                    # If the light is in green, move the car, else stay in the same position
                    if agent.state:
                        next_step = self.next_step_based_on_direction()
                        if self.is_position_valid(next_step):
                            self.model.grid.move_agent(self, next_step)
                            print(f"Se mueve de {self.pos} a {next_step}; direction {self.direction}")
                        else:
                            print(f"No se puede mover de {self.pos} en esa direccion.")
                    else:
                        print(f"No se puede mover de {self.pos} en esa direccion.")
        # If the car is in a road without a traffic light
        else:
            next_step = self.next_step_based_on_direction()
            # Assign the self direction based on the road direction
            if next_step is not None:
                self.direction = self.get_current_road_direction()
            # If it can move, move it, else stand still
            if self.is_position_valid(next_step):
                # If there is a possible turn, 50% chance of turning
                if self.detect_turns() is not None:
                    possible_random = ['Advance', 'Turn']
                    # 50% chance of advancing or turning
                    random_action = self.random.choice(possible_random)
                    # If advance, it moves normally following the direction of the road
                    if random_action == 'Advance':
                        self.model.grid.move_agent(self, next_step)
                        print(f"Se mueve de {self.pos} a {next_step}; direction {self.direction}")
                    # If turn, it starts turning
                    elif random_action == 'Turn':
                        self.turning = True
                        self.direction = self.detect_turns()
                        print(self.direction)
                else:
                    self.model.grid.move_agent(self, next_step)
                    print(f"Se mueve de {self.pos} a {next_step}; direction {self.direction}")

            # If it is not out of bounds but stuck by a car
            elif not self.model.grid.out_of_bounds(next_step) and  self.has_next_step_agent(next_step, 'Car'):
                print(f"No se puede mover de {self.pos} en esa direccion.")
                return
            else:
                # If it cannot move because it is out of bounds, change direction
                next_step = self.next_step_based_on_direction(stuck = True)
                if next_step is not None:
                    self.direction = self.get_road_direction_if_stuck()
                if next_step is not None and self.is_position_valid(next_step):
                    self.model.grid.move_agent(self, next_step)
                    print(f"Se mueve de {self.pos} a {next_step}; direction {self.direction}")
                # If there is literally no position
                else:
                    print(f"No se puede mover de {self.pos} en esa direccion.")

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

    def get_road_direction_if_stuck(self):
        """
        If the car is stuck, get the direction of the road it is in
        """
        for agent in self.model.grid.iter_neighbors(self.pos, moore=False, radius=2):
            if isinstance(agent, Road) and agent.direction != self.direction:
                return agent.direction
        return None

    def has_next_step_agent(self, next_step, agent_type):
        next_self_content = self.model.grid.get_cell_list_contents([next_step])
        next_self_content = [type(agent).__name__ for agent in next_self_content]
        if agent_type in next_self_content:
            return True
        return False 

    def valid_turns(self):
        if self.direction == "Up":
            return ["Left", "Right"]
        elif self.direction == "Down":
            return ["Left", "Right"]
        elif self.direction == "Left":
            return ["Up", "Down"]
        elif self.direction == "Right":
            return ["Up", "Down"]

    def detect_turns(self):
        """
        Detects if there is a turn in the next 2 cells
        """
        for agent in self.model.grid.iter_neighbors(self.pos, moore=False, radius=2):
            
            if isinstance(agent, Road):
                if agent.direction != self.direction and agent.direction in self.valid_turns():
                    if agent.direction == "Up" and self.is_position_valid((self.pos[0], self.pos[1] + 2)) and self.is_position_valid((self.pos[0], self.pos[1] + 1)):
                        return agent.direction
                    elif agent.direction == "Down" and self.is_position_valid((self.pos[0], self.pos[1] - 2)) and self.is_position_valid((self.pos[0], self.pos[1] - 1)):
                        return agent.direction
                    elif agent.direction == "Left" and self.is_position_valid((self.pos[0] - 2, self.pos[1])) and self.is_position_valid((self.pos[0] - 1, self.pos[1])):
                        return agent.direction
                    elif agent.direction == "Right" and self.is_position_valid((self.pos[0] + 2, self.pos[1])) and self.is_position_valid((self.pos[0] + 1, self.pos[1])):
                        return agent.direction
        return None

    def turn(self):
        """
        Turns the car if it is in a turn
        """
        turn = self.detect_turns()
        if turn is not None:
            self.turn = True
            self.direction = turn
            return 

    def get_front_agents(self):
        """
        Returns the agents in front of the car
        """
        
        if self.direction is not None:
            if self.direction == "Up":
                # current_self_content = self.model.grid.get_cell_list_contents([(self.pos[0], self.pos[1] + 1)])
                # return [type(agent).__name__ for agent in current_self_content] 
                if not self.model.grid.out_of_bounds((self.pos[0], self.pos[1] + 1)):
                    return self.model.grid.get_cell_list_contents([(self.pos[0], self.pos[1] + 1)])
                return []
                
            elif self.direction == "Down":
                # current_self_content = self.model.grid.get_cell_list_contents([(self.pos[0], self.pos[1] + 1)])
                # return [type(agent).__name__ for agent in current_self_content]
                if not self.model.grid.out_of_bounds((self.pos[0], self.pos[1] - 1)):
                    return self.model.grid.get_cell_list_contents([(self.pos[0], self.pos[1] - 1)])
                return []
            elif self.direction == "Left":
                # current_self_content = self.model.grid.get_cell_list_contents([(self.pos[0] - 1, self.pos[1])])
                # return [type(agent).__name__ for agent in current_self_content]
                if not self.model.grid.out_of_bounds((self.pos[0] - 1, self.pos[1])):
                    return self.model.grid.get_cell_list_contents([(self.pos[0] - 1, self.pos[1])])
                return []
            elif self.direction == "Right":
                # current_self_content = self.model.grid.get_cell_list_contents([(self.pos[0] + 1, self.pos[1])])
                # return [type(agent).__name__ for agent in current_self_content]
                if not self.model.grid.out_of_bounds((self.pos[0] + 1, self.pos[1])):
                    return self.model.grid.get_cell_list_contents([(self.pos[0] + 1, self.pos[1])])
                return []
        return []

    def get_front_agents_traffic_light_on(self):
        for agent in self.get_front_agents():
            if isinstance(agent, Traffic_Light):
                if not agent.state:
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
