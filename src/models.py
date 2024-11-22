class Upgrade:
    def __init__(self, name, cost, productivity_boost, description):
        self.name = name
        self.cost = cost
        self.productivity_boost = productivity_boost
        self.description = description
        self.count = 0
        
    def total_boost(self):
        return self.productivity_boost * self.count
