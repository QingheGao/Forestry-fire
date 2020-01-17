from mesa import Agent
from utils import rgb_to_hex
import random


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
        if random.random() < self.density * 0.01:
            self.on_fire = True

        if self.on_fire:
            # reduce own density
            self.density -= self.density * 0.90

            # spread to neighbors
            for neighbor in self.model.grid.neighbor_iter(self.pos):
                if type(neighbor) is Tree and not neighbor.on_fire:
                    if random.random() < neighbor.density * 0.2:
                        neighbor.on_fire = True
            
            # check if burn out
            if self.density < 0.1:
                self.on_fire = False
        else:
            # grow a little bit each step if not on fire
            self.density += self.density * (1 - self.density) * 0.2


    def get_color(self):
        if not self.on_fire:
            return rgb_to_hex((0, int(255 * self.density), 0))
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


