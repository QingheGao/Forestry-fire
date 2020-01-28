from mesa.time import RandomActivation

class RandomActivationForestFire(RandomActivation):
    
    def __init__(self, model):
        super().__init__(model)
        self.tree_schedule = RandomActivation(model)
        self.firefighter_schedule = RandomActivation(model)

        self.steps = 0

    def step(self, activate_firefighters=True):
        self.tree_schedule.step()
        if activate_firefighters:
            self.firefighter_schedule.step()
        
        self.steps += 1

    def add_tree(self, tree):
        self.tree_schedule.add(tree)

    def add_firefighter(self, firefighter):
        self.firefighter_schedule.add(firefighter)