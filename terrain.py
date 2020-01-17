from mesa import Agent

class Terrain(Agent):
    def __init__(self, unique_id, model, color):
        super().__init__(unique_id, model)

        self.color = color

    def get_color(self):
        return self.color

    def get_portrayal(self):
        portrayal = {"Shape": "rect",
                 "Color": self.get_color(),
                 "Filled": "true",
                 "Layer": 0,
                 "w": 1.0,
                 "h": 1.0}
        return portrayal

class Dirt(Terrain):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, "brown")

class Water(Terrain):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, "blue")

class Road(Terrain):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, "grey")