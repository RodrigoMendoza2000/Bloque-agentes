from agent_shortest_path import *
from model import RandomModel
from mesa.visualization.modules import CanvasGrid, BarChartModule
from mesa.visualization.ModularVisualization import ModularServer


def agent_portrayal(agent):
    if agent is None:
        return

    portrayal = {"Shape": "rect",
                 "Filled": "true",
                 "Layer": 1,
                 "w": 1,
                 "h": 1
                 }

    if (isinstance(agent, Road)):
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 0
        portrayal["text"] = agent.pos
        portrayal["text_color"] = "black"

    if (isinstance(agent, Destination)):
        portrayal["Color"] = "lightgreen"
        portrayal["Layer"] = 0

    if (isinstance(agent, Traffic_Light)):
        portrayal["Color"] = "red" if not agent.state else "green"
        portrayal["Layer"] = 0
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8
        portrayal["text"] = agent.unique_id
        portrayal["text_color"] = "white"

    if (isinstance(agent, Obstacle)):
        portrayal["Color"] = "cadetblue"
        portrayal["Layer"] = 0
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8

    if (isinstance(agent, Car)):
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 1
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8
        portrayal["text"] = agent.unique_id
        portrayal["text_color"] = "white"

    if (isinstance(agent, Sidewalk)):
        portrayal["Color"] = "lightgrey"
        portrayal["Layer"] = 0
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8

    if (isinstance(agent, Brush)):
        portrayal["Color"] = "lightyellow"
        portrayal["Layer"] = 0
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8

    if (isinstance(agent, Person)):
        portrayal["Color"] = "yellow"
        portrayal["Layer"] = 0
        portrayal["w"] = 0.3
        portrayal["h"] = 0.3

    if (isinstance(agent, Busdestination)):
        portrayal["Color"] = "orange"
        portrayal["Layer"] = 0
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8

    return portrayal


width = 0
height = 0

with open('base.txt') as baseFile:
    lines = baseFile.readlines()
    width = len(lines[0])-1
    height = len(lines)

model_params = {"N": 120}

grid = CanvasGrid(agent_portrayal, width, height, 800, 800)

server = ModularServer(RandomModel, [grid], "Traffic Base", model_params)

server.port = 8521  # The default
server.launch()
