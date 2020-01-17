import random

from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation

from agents import Tree, FireFighter
from terrain import Dirt, Water, Road

class ForestFire(Model):
    def __init__(self, height=40, width=40, density=0.65):

        super().__init__()

        self.height = height
        self.width = width
        self.density = density
        
        self.grid = MultiGrid(self.width, self.height, torus=False)

        # Add a schedule for trees and firefighters seperately to prevent race-conditions
        self.schedule_Tree = RandomActivation(self)
        # self.schedule_FireFighter = RandomActivation(self)

        self.datacollector = DataCollector({"Density": lambda m: self.get_avg_density(),
                                            "On Fire": lambda m: self.get_fraction_on_fire()})

        # Create trees and firefighters
        self.init_terrain()
        self.total_trees = 0
        self.init_trees()
        self.init_firefighters()

        # This is required for the datacollector to work
        self.running = True
        self.datacollector.collect(self)

    def init_terrain(self):
        # fill with dirt
        for (_, x, y) in self.grid.coord_iter():
            self.grid.place_agent(Dirt(self.next_id(), self), (x, y))

    def init_trees(self):
        for (agents, x, y) in self.grid.coord_iter():
            if Dirt in (type(agent) for agent in agents):
                self.new_tree((x, y), self.density)
                self.total_trees += 1
        

    def init_firefighters(self):
        pass

    def new_tree(self, pos, density):
        '''
        Method that creates a new agent, and adds it to the correct scheduler.
        '''
        agent = Tree(self.next_id(), self, pos, density)

        self.grid.place_agent(agent, pos)
        self.schedule_Tree.add(agent)

    def step(self):
        '''
        Method that calls the step method for each of the sheep, and then for each of the wolves.
        '''
        self.schedule_Tree.step()

        # Save the statistics
        self.datacollector.collect(self)

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