from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from mesa.time import RandomActivation
import random
from math import pi, sin, cos

from agents import Tree, FireFighter
from terrain import Dirt
from schedule import RandomActivationForestFire


class ForestFire(Model):
    
    width = 50
    height = 50
    
    def __init__(self, height=height, width=width,
        initial_density_dist_alpha=1.5, initial_density_dist_beta=10, max_density=555,
        fire_spread_param=0.0045,
        firefighter_strategy=FireFighter.extinguish,
        number_firefighters=10, extinguish_difficulty=3, fire_line_margin=5, cut_down_amount=250, firefighter_response_delay=1):

        super().__init__()

        # don't use for simulation
        # random.seed(0)

        self.height = height
        self.width = width
        self.initial_density_dist_alpha = initial_density_dist_alpha
        self.initial_density_dist_beta = initial_density_dist_beta
        self.max_density = max_density
        
        self.fire_spread_param = fire_spread_param

        self.firefighter_strategy = firefighter_strategy
        self.number_firefighters = number_firefighters
        self.extinguish_difficulty = extinguish_difficulty
        self.fire_line_margin = fire_line_margin
        self.cut_down_amount = cut_down_amount
        self.firefighter_response_delay = firefighter_response_delay

        self.fire_edges = None

        self.extinguish_cost = 0
        self.burn_cost = 0
        self.cut_down_cost = 0
        self.burnout_time = 0
        
        self.grid = MultiGrid(self.width, self.height, torus=False)

        self.schedule = RandomActivationForestFire(self)

        self.datacollector = DataCollector({"Average Density": lambda m: self.get_total_density() / self.total_trees,
                                            "Total Density": lambda m: self.get_total_density(),
                                            "Percentage lost": lambda m: self.percentage_lost(),
                                            "On Fire": lambda m: self.get_number_on_fire() / self.total_trees,
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

        self.steps = 0

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

        self.initial_total_density = self.get_total_density()

    def init_firefighters(self):
        for _ in range(self.number_firefighters):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.new_firefighter((x, y))

    def new_tree(self, pos, density):
        '''
        Method that creates a new agent, and adds it to the correct scheduler.
        '''
        tree = Tree(self.next_id(), self, pos, density)

        self.grid.place_agent(tree, pos)
        self.schedule.add_tree(tree)

    def new_firefighter(self, pos):
        firefighter = FireFighter(self.next_id(), self, pos, self.firefighter_strategy)

        self.grid.place_agent(firefighter, pos)
        self.schedule.add_firefighter(firefighter)

    def step(self):
        '''
        Method that calls the step method for each of the sheep, and then for each of the wolves.
        '''
        if self.schedule.steps > self.firefighter_response_delay:
            self.schedule.step()
        else:
            self.schedule.step(activate_firefighters=False)

        # Save the statistics
        self.datacollector.collect(self)

        if self.get_number_on_fire() > 0:
            self.burnout_time += 1

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

    def get_total_density(self):
        total_density = 0
        for (agents, _, _) in self.grid.coord_iter():
            for agent in agents:
                if type(agent) is Tree:
                    total_density += agent.density
        return total_density

    def get_number_on_fire(self):
        total_burning = 0
        for (agents, _, _) in self.grid.coord_iter():
            for agent in agents:
                if type(agent) is Tree and agent.on_fire:
                    total_burning += 1
        return total_burning

    def percentage_lost(self):
        return (1 - self.get_total_density() / self.initial_total_density) * 100
