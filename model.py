from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from mesa.time import RandomActivation
import random
from math import pi, sin, cos

from agents import Tree, FireFighter
from terrain import Dirt


class ForestFire(Model):
    
    width = 50
    height = 50
    
    def __init__(self, height=height, width=width,
        initial_density_dist_alpha=1.5, initial_density_dist_beta=10, max_density=555,
        fire_spread_param=0.0045,
        number_firefighters=10, extinguish_difficulty=5, fire_line_margin=5, cut_down_amount=555, firefighter_response_delay=1):

        super().__init__()

        # don't use for simulation
        random.seed(0)

        self.height = height
        self.width = width
        self.initial_density_dist_alpha = initial_density_dist_alpha
        self.initial_density_dist_beta = initial_density_dist_beta
        self.max_density = max_density
        
        self.fire_spread_param = fire_spread_param
        
        self.number_firefighters = number_firefighters
        self.extinguish_difficulty = extinguish_difficulty
        self.fire_line_margin = fire_line_margin
        self.cut_down_amount = cut_down_amount
        self.firefighter_response_delay = firefighter_response_delay

        self.fire_edges = None

        self.extinguish_cost = 0
        self.burn_cost = 0
        self.cut_down_cost = 0
        
        self.grid = MultiGrid(self.width, self.height, torus=False)

        # Add a schedule for trees and firefighters seperately to prevent race-conditions
        self.schedule_Tree = RandomActivation(self)
        self.schedule_FireFighter = RandomActivation(self)

        self.datacollector = DataCollector({"Density": lambda m: self.get_avg_density(),
                                            "On Fire": lambda m: self.get_fraction_on_fire(),
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

    def init_terrain(self):
        # fill with dirt
        for (_, x, y) in self.grid.coord_iter():
            self.grid.place_agent(Dirt(self.next_id(), self), (x, y))

    def init_trees(self):
        for (agents, x, y) in self.grid.coord_iter():
            if Dirt in (type(agent) for agent in agents):
                self.new_tree((x, y), random.betavariate(self.initial_density_dist_alpha, self.initial_density_dist_beta) * self.max_density)
                self.total_trees += 1

        fire_x = random.randint(0, self.width - 1)
        fire_y = random.randint(0, self.height - 1)
        for agent in self.grid[fire_x][fire_y]:
            if type(agent) is Tree:
                agent.on_fire = True

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

        if self.step_counter > self.firefighter_response_delay:
            self.schedule_FireFighter.step()

        # Save the statistics
        self.datacollector.collect(self)

        self.step_counter += 1

    def calculate_fire_edges(self):
        max_x = 0
        min_x = self.width
        max_y = 0
        min_y = self.height

        for (agents, x, y) in self.grid.coord_iter():
            for agent in agents:
                if type(agent) is Tree and agent.on_fire:
                    if x > max_x:
                        max_x = x
                    if x < min_x:
                        min_x = x
                    if y > max_y:
                        max_y = y
                    if y < min_y:
                        min_y = y
        
        self.fire_edges = (min_x, max_x, min_y, max_y)
    
    def get_fire_edges(self):
        if self.fire_edges is None:
            self.calculate_fire_edges()
        return self.fire_edges

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
