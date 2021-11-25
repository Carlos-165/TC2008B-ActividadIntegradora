from main2 import modeloAlmacen
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "red",
                 "r": 0.5}
    return portrayal

grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
server = ModularServer(modeloAlmacen,
                       [grid],
                       "Money Model",
                       {"width":9, "height":10, "agentsCaja": 20, "agentsRobot": 5})
server.port = 8521 # The default
server.launch()