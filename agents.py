from mesa import Agent
from utils import rgb_to_hex
import random
from math import sin, cos, pi, e


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

        if self.on_fire:
            for neighbor in self.model.grid.neighbor_iter(self.pos, moore=True):
                if type(neighbor) is Tree and not neighbor.on_fire:
                    if random.random() < neighbor.density * self.model.fire_spread_param:
                        neighbor.on_fire = True
            
            # burn down
            self.density = 0
            self.on_fire = False


    def get_color(self):
        if not self.on_fire:
            return rgb_to_hex((0, min(int(255 * (self.density / 100)), 255), 0))
        else:
           return "red"

    def get_portrayal(self):
        portrayal = {"Shape": "circle",
                 "Color": self.get_color(),
                 "Filled": "true",
                 "Layer": 1,
                 "r": 1}
        return portrayal

class FireFighter(Agent):

    extinguish = "extinguish"
    firelines = "firelines"

    def __init__(self, unique_id, model, pos, strategy):
        super().__init__(unique_id, model)
        self.pos = pos

        self.strategy = strategy

    def step(self):
        # execute strategy
        if self.strategy == FireFighter.extinguish:
            self.extinguish_only()
        elif self.strategy == FireFighter.firelines:
            self.firelines_only()

    # def burn_down_only(self):
    #     # teleport to tree with highest density
    #     max_density = 0
    #     new_location = self.pos
    #     for (agents, x, y) in self.model.grid.coord_iter():
    #         if FireFighter not in [type(agent) for agent in agents]:
    #             for agent in agents:
    #                 if type(agent) is Tree and agent.density > max_density:
    #                     max_density = agent.density
    #                     new_location = (x, y)
    #     self.model.grid.move_agent(self, new_location)

    #     for agent in self.model.grid.get_neighbors(self.pos, moore=True, radius=0, include_center=True):
    #         if type(agent) is Tree and agent.density > 0.25:
    #             self.burn_tree(agent)

    # def cut_down_only(self):
    #     # teleport to tree with highest density
    #     max_density = 0
    #     new_location = self.pos
    #     for (agents, x, y) in self.model.grid.coord_iter():
    #         if FireFighter not in [type(agent) for agent in agents]:
    #             for agent in agents:
    #                 if type(agent) is Tree and agent.density > max_density:
    #                     max_density = agent.density
    #                     new_location = (x, y)
    #     self.model.grid.move_agent(self, new_location)

    #     for agent in self.model.grid.get_neighbors(self.pos, moore=True, radius=0, include_center=True):
    #         if type(agent) is Tree and agent.density > 0.25:
    #             self.cut_down_tree(agent, 0.2)

    def iter_fireline_coords(self):
        (l, r, t, b) = self.model.get_fire_edges()
        margin = self.model.fire_line_margin
        
        left = max(l - margin, 0)
        right = min(r + margin, self.model.width - 1)
        top = max(t - margin, 0)
        bottom = min(b + margin, self.model.height - 1)

        # left
        column = self.model.grid[left]
        for coord in column[top: bottom]:
            yield coord
        
        # right
        column = self.model.grid[right]
        for coord in column[top: bottom + 1]:
            yield coord
        
        # top
        for column in self.model.grid[left: right]:
            yield column[top]

        #bottom
        for column in self.model.grid[left: right]:
            yield column[bottom]
        
    
    def firelines_only(self):
        if self.model.get_number_on_fire() == 0:
            return

        max_density = 0
        max_pos = (0, 0)
        max_tree = None
        for agents in self.iter_fireline_coords():
            for agent in agents:
                if type(agent) is Tree:
                    if agent.density > max_density:
                        max_density = agent.density
                        max_pos = agent.pos
                        max_tree = agent
        
        self.model.grid.move_agent(self, max_pos)

        if max_tree is not None:
            self.cut_down_tree(max_tree, self.model.cut_down_amount)
        else:
            self.model.calculate_fire_edges()

    def extinguish_only(self):
        if self.model.get_number_on_fire() == 0:
            return

        # teleport to tree that is on fire
        new_location = self.pos
        coords = [coord for coord in self.model.grid.coord_iter()]
        random.shuffle(coords)
        for (agents, x, y) in coords:
            if FireFighter not in [type(agent) for agent in agents]:
                for agent in agents:
                    if type(agent) is Tree and agent.on_fire:
                        new_location = (x, y)
            if new_location != self.pos:
                break
        self.model.grid.move_agent(self, new_location)

        self.extinguish_trees(self.pos, radius=0)

    # def burn_plus_cut(self):
    #     # teleport to tree with highest density
    #     max_density = 0
    #     new_location = self.pos
    #     for (agents, x, y) in self.model.grid.coord_iter():
    #         if FireFighter not in [type(agent) for agent in agents]:
    #             for agent in agents:
    #                 if type(agent) is Tree and agent.density > max_density:
    #                     max_density = agent.density
    #                     new_location = (x, y)
    #     self.model.grid.move_agent(self, new_location)

    #     total_density = 0
    #     total_trees = 0
    #     for agent in self.model.grid.get_neighbors(self.pos, moore=True, radius=3, include_center=True):
    #         if type(agent) is Tree:
    #             total_trees += 1
    #             total_density += agent.density

    #     avg_density = total_density / total_trees
    #     if avg_density > 0.3:
    #         # burn middle tree
    #         for agent in self.model.grid.get_neighbors(self.pos, moore=True, radius=0, include_center=True):
    #             if type(agent) is Tree:
    #                 self.burn_tree(agent)
    #     elif avg_density > 0.15:
    #         # cut down middle tree
    #         for agent in self.model.grid.get_neighbors(self.pos, moore=True, radius=0, include_center=True):
    #             if type(agent) is Tree:
    #                 self.cut_down_tree(agent, 0.2)

    # def intelligent(self):
    #     if self.model.get_fraction_on_fire() > 0.02:
    #         self.extinguish_only()
    #     else:
    #         self.burn_plus_cut()

    def cut_down_tree(self, tree, amount):
        tree.density -= min(amount, tree.density)
        self.model.cut_down_cost += 1

    def burn_tree(self, tree):
        tree.on_fire = True
        self.model.burn_cost += 1

    def extinguish_trees(self, pos, radius=1):
        for agent in self.model.grid.get_neighbors(pos, moore=True, radius=radius, include_center=True):
            if type(agent) is Tree and agent.on_fire:
                if random.betavariate(1, self.model.extinguish_difficulty) * self.model.max_density > agent.density:
                    agent.on_fire = False
                    self.model.extinguish_cost += 1

    def get_portrayal(self):
        portrayal = {"Shape": "circle",
                 "Color": "#6666FF",
                 "Filled": "true",
                 "Layer": 2,
                 "r": 0.8}
        return portrayal




