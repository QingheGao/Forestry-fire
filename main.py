from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule

# Import the implemented classes
from model import ForestFire

import os
import sys

# Change stdout so we can ignore most prints etc.
orig_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')
sys.stdout = orig_stdout

# You can change this to whatever ou want. Make sure to make the different types
# of agents distinguishable
def agent_portrayal(agent):
    if agent is None:
      return
    return agent.get_portrayal()

# Create a grid of 20 by 20 cells, and display it as 500 by 500 pixels
grid = CanvasGrid(agent_portrayal, ForestFire.width, ForestFire.height, 600, 600)

# Create a dynamic linegraph
chart0 = ChartModule([{"Label": "Total cost",
                      "Color": "yellow"},
                      {"Label": "Extinguish cost",
                       "Color": "blue"},
                      {"Label": "Burn cost",
                       "Color": "orange"},
                      {"Label": "Cut down cost",
                       "Color": "green"}],
                    data_collector_name='datacollector')
chart1 = ChartModule([{"Label": "Total Density",
                      "Color": "green"}],
                    data_collector_name='datacollector')
chart2 = ChartModule([{"Label": "On Fire",
                      "Color": "red"}],
                    data_collector_name='datacollector')
chart3 = ChartModule([{"Label": "Percentage lost",
                       "Color": "black"}],
                    data_collector_name='datacollector')


# Create the server, and pass the grid and the graph
server = ModularServer(ForestFire,
                       [grid, chart3, chart1, chart2],
                       "ForestFire Model",
                       {})

server.port = 8521

server.launch()

