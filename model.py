from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from mesa.time import RandomActivation
import random
from math import pi, sin, cos

from agents import Tree, FireFighter
from terrain import Dirt


class ForestFire(Model):
    def __init__(self, height=40, width=40, density_lower=0.1, density_upper=0.2, number_firefighters=10):

        super().__init__()

        self.height = height
        self.width = width
        self.density_lower = density_lower
        self.density_upper = density_upper
        self.number_firefighters = number_firefighters

        self.extinguish_cost = 0
        self.burn_cost = 0
        self.cut_down_cost = 0
        
        self.grid = MultiGrid(self.width, self.height, torus=False)

        # Add a schedule for trees and firefighters seperately to prevent race-conditions
        self.schedule_Tree = RandomActivation(self)
        self.schedule_FireFighter = RandomActivation(self)

        self.datacollector = DataCollector({"Density": lambda m: self.get_avg_density(),
                                            "On Fire": lambda m: self.get_fraction_on_fire(),
                                            "Burn factor": lambda m: self.burn_factor(),
                                            "Growth factor": lambda m: self.growth_factor(),
                                            "Total cost": lambda m: self.extinguish_cost + self.burn_cost + self.cut_down_cost,
                                            "Extinguish cost": lambda m: self.extinguish_cost,
                                            "Burn cost": lambda m: self.burn_cost,
                                            "Cut down cost": lambda m: self.cut_down_cost
                                            })

        # Create trees and firefighters
        self.init_terrain()
        self.total_trees = 0
        self.init_trees()
        self.init_firefighters()

        self.step_counter = 0

        # This is required for the datacollector to work
        self.running = True
        self.datacollector.collect(self)

    def burn_factor(self):
        return (sin((self.step_counter / 365) * 2 * pi) + 1) / 2

    def growth_factor(self):
        return (sin((self.step_counter / 365) * 2 * pi) + 1) / 2

    def init_terrain(self):
        # fill with dirt
        for (_, x, y) in self.grid.coord_iter():
            self.grid.place_agent(Dirt(self.next_id(), self), (x, y))

    def init_trees(self):
        for (agents, x, y) in self.grid.coord_iter():
            if Dirt in (type(agent) for agent in agents):
                self.new_tree((x, y), random.uniform(self.density_lower, self.density_upper))
                self.total_trees += 1

    def init_firefighters(self):
        for _ in range(self.number_firefighters):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.new_firefighter((x, y))

    def new_tree(self, pos, density):
        '''
        Method that creates a new agent, and adds it to the correct scheduler.
        '''
        agent = Tree(self.next_id(), self, pos, density)

        self.grid.place_agent(agent, pos)
        self.schedule_Tree.add(agent)

    def new_firefighter(self, pos):
        agent = FireFighter(self.next_id(), self, pos)

        self.grid.place_agent(agent, pos)
        self.schedule_FireFighter.add(agent)

    def step(self):
        '''
        Method that calls the step method for each of the sheep, and then for each of the wolves.
        '''
        self.schedule_Tree.step()
        self.schedule_FireFighter.step()

        # Save the statistics
        self.datacollector.collect(self)

        self.step_counter += 1

    def get_avg_density(self):
        total_density = 0
        for (agents, _, _) in self.grid.coord_iter():
            for agent in agents:
                if type(agent) is Tree:
                    total_density += agent.density
        return total_density / self.total_trees

    def get_fraction_on_fire(self):
        total_burning = 0
        for (agents, _, _) in self.grid.coord_iter():
            for agent in agents:
                if type(agent) is Tree and agent.on_fire:
                    total_burning += 1
        return total_burning / self.total_trees
