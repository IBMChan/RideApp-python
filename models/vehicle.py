class Vehicle:
    def __init__(self, make, model, plate, color, year):
        self.make = make
        self.model = model
        self.plate = plate
        self.color = color
        self.year = year

    def __str__(self):
        return f"{self.year} {self.color} {self.make} {self.model} ({self.plate})"
