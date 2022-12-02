from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent_shortest_path import *
import json
import random


class RandomModel(Model):
    """ 
    Creates a new model with random agents.
    Args:
        N: Number of agents in the simulation
        height, width: The size of the grid to model
    """

    def __init__(self, N):

        dataDictionary = json.load(open("mapDictionary.txt"))

        # Variable to see all the available destination positions
        self.destination_positions = []
        # Where the agents will spawn
        self.destination_entrance = []
        # All the sidewalk positions where the person agent can walk and spawn
        self.sidewalk_positions = []

        # Iterate through the base.txt file to get the positions of 
        # the sidewalks, 
        # traffic lights, bushes, destination and bus destinations
        with open('base.txt') as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0]) - 1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus=False)
            self.schedule = RandomActivation(self)

            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<"]:
                        agent = Road(f"r{r * self.width + c}",
                                     self, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                    elif col in ["S", "s"]:
                        agent = Traffic_Light(
                            f"tl{r * self.width + c}", self,
                            False if col == "S" else True,
                            int(dataDictionary[col]))
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                    elif col == "#":
                        agent = Obstacle(f"ob{r * self.width + c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                    elif col == "D":
                        agent = Destination(f"d{r * self.width + c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.destination_positions.append(
                            (c, self.height - r - 1))
                    elif col == "W":
                        agent = Sidewalk(f"d{r * self.width + c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.sidewalk_positions.append(
                            (c, self.height - r - 1))
                    elif col == "B":
                        agent = Brush(f"d{r * self.width + c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                    elif col == "P":
                        agent = Busdestination(f"d{r * self.width + c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

        self.num_agents = N
        # Add N number of agents to the model
        for i in range(self.num_agents):
            agent = Car(f"c{i}", self)
            self.schedule.add(agent)

        # Add 25 persons to the simulation on a random position
        for i in range(25):
            agent = Person(f"p{i}", self)
            random_sidewalk = random.choice(self.sidewalk_positions)
            self.grid.place_agent(agent, random_sidewalk)
            self.schedule.add(agent)

        # Add one bus to the simulation
        agent = Bus(f"b1", self)
        self.schedule.add(agent)
        self.grid.place_agent(agent, (22, 24))

        # Add the 4 corners of the map where the cars will come from
        self.destination_entrance.append((0, 0))
        self.destination_entrance.append((0, 24))
        self.destination_entrance.append((23, 24))
        self.destination_entrance.append((23, 0))

        self.running = True

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
