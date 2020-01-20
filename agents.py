from mesa import Agent
from utils import rgb_to_hex
import random
from math import sin, cos, pi


class Tree(Agent):
    def __init__(self, unique_id, model, pos, density):
        super().__init__(unique_id, model)

        self.on_fire = False
        self.pos = pos

        self.density = density

    def step(self):
        """
        If the tree is on fire, spread it to fine trees nearby.
        """ 

        # check if tree should burn
        if random.random() < (self.density ** 2) * 0.001 * self.model.burn_factor():
            self.on_fire = True

        if self.on_fire:
            # reduce own density
            self.density -= self.density * 0.40

            for neighbor in self.model.grid.neighbor_iter(self.pos, moore=True):
                if type(neighbor) is Tree and not neighbor.on_fire:
                    if random.random() < neighbor.density * 0.4:
                        neighbor.on_fire = True
            
            # check if burn out
            if self.density < 0.1:
                self.on_fire = False
        else:
            # grow a little bit each step if not on fire
            self.density += self.density * (1 - self.density) * 0.02 * self.model.growth_factor()


    def get_color(self):
        if not self.on_fire:
            return rgb_to_hex((0, min(int(255 * self.density * 3), 255), 0))
        else:
           return "red"

    def get_portrayal(self):
        portrayal = {"Shape": "circle",
                 "Color": self.get_color(),
                 "Filled": "true",
                 "Layer": 1,
                 "r": 0.5}
        return portrayal

class FireFighter(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos

        self.strategy = self.extinguish_only

    def step(self):

        # execute strategy
        self.strategy()

        # for neighbor in self.model.grid.neighbor_iter(self.pos):
        #     if type(neighbor) is Tree and neighbor.on_fire:
        #         neighbor.on_fire = False
        #     else:
        #         neighborhoods = self.model.grid.get_neighborhood(self.pos, moore=True)
        #         newpos = random.choice(neighborhoods)
        #         self.model.grid.move_agent(self, newpos)

    def burn_down_only(self):
        # teleport to tree with highest density
        max_density = 0
        new_location = self.pos
        for (agents, x, y) in self.model.grid.coord_iter():
            if FireFighter not in [type(agent) for agent in agents]:
                for agent in agents:
                    if type(agent) is Tree and agent.density > max_density:
                        max_density = agent.density
                        new_location = (x, y)
        self.model.grid.move_agent(self, new_location)

        for agent in self.model.grid.get_neighbors(self.pos, moore=True, radius=0, include_center=True):
            if type(agent) is Tree and agent.density > 0.25:
                agent.on_fire = True

    def cut_down_only(self):
        # teleport to tree with highest density
        max_density = 0
        new_location = self.pos
        for (agents, x, y) in self.model.grid.coord_iter():
            if FireFighter not in [type(agent) for agent in agents]:
                for agent in agents:
                    if type(agent) is Tree and agent.density > max_density:
                        max_density = agent.density
                        new_location = (x, y)
        self.model.grid.move_agent(self, new_location)

        for agent in self.model.grid.get_neighbors(self.pos, moore=True, radius=0, include_center=True):
            if type(agent) is Tree and agent.density > 0.25:
                agent.density -= 0.2

    def extinguish_only(self):
        for agent in self.model.grid.get_neighbors(self.pos, moore=True, radius=1, include_center=True):
            if type(agent) is Tree and agent.on_fire:
                agent.on_fire = False

        # teleport to tree with highest density
        new_location = self.pos
        coords = [coord for coord in self.model.grid.coord_iter()]
        random.shuffle(coords)
        for (agents, x, y) in coords:
            if FireFighter not in [type(agent) for agent in agents]:
                for agent in agents:
                    if type(agent) is Tree and agent.on_fire:
                        new_location = (x, y)
        self.model.grid.move_agent(self, new_location)

    def get_portrayal(self):
        portrayal = {"Shape": "circle",
                 "Color": "yellow",
                 "Filled": "true",
                 "Layer": 1,
                 "r": 0.5}
        return portrayal




