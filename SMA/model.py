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
        self.destination_entrance = []
        self.sidewalk_positions = []

        with open('base.txt') as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus=False)
            self.schedule = RandomActivation(self)

            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<"]:
                        agent = Road(f"r{r*self.width+c}",
                                     self, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                    elif col in ["S", "s"]:
                        agent = Traffic_Light(
                            f"tl{r*self.width+c}", self, False if col == "S" else True, int(dataDictionary[col]))
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                    elif col == "#":
                        agent = Obstacle(f"ob{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                    elif col == "D":
                        agent = Destination(f"d{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.destination_positions.append(
                            (c, self.height - r - 1))
                    elif col == "W":
                        agent = Sidewalk(f"d{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.sidewalk_positions.append(
                            (c, self.height - r - 1))
                    elif col == "B":
                        agent = Brush(f"d{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                    elif col == "P":
                        agent = Busdestination(f"d{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

        self.num_agents = N
        for i in range(self.num_agents):
            agent = Car(10000 + i, self)
            self.schedule.add(agent)

        for i in range(25):
            agent = Person(f"person{i}", self)
            random_sidewalk = random.choice(self.sidewalk_positions)
            self.grid.place_agent(agent, random_sidewalk)
            self.schedule.add(agent)

        # eliminate two destinations from final destinations and add them to entrance destinations
        self.destination_entrance.append((0,0))
        # self.destination_entrance.append((0,1))
        self.destination_entrance.append((0,24))
        # self.destination_entrance.append((1,24))
        self.destination_entrance.append((23,24))
        # self.destination_entrance.append((23,23))
        self.destination_entrance.append((23,0))
        # self.destination_entrance.append((22,0))
        """self.destination_entrance.append((3,22))
        self.destination_entrance.append((19,2))
        self.destination_positions.remove((3,22))
        self.destination_positions.remove((19,2))"""
        """self.destination_entrance.append((12,15))
        self.destination_entrance.append((12,4))
        self.destination_positions.remove((12,15))
        self.destination_positions.remove((12,4))"""
        """for i in range(2):
            random_destination = random.choice(self.destination_positions)
            self.destination_entrance.append(random_destination)
            self.destination_positions.remove(random_destination)"""

        self.running = True

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
        if self.schedule.steps % 10 == 0:
            for agents, x, y in self.grid.coord_iter():
                for agent in agents:
                    if isinstance(agent, Traffic_Light):
                        agent.state = not agent.state
