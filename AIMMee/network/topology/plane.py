import math
import matplotlib.pyplot as plt


class Plane:
    def __init__(self, shape, side_length=None, radius=None):
        self.shape = shape
        self.side_length = side_length
        self.radius = radius

    def is_inside(self, x, y):
        if self.shape == 'circular':
            return math.sqrt(x ** 2 + y ** 2) <= self.radius
        elif self.shape == 'square':
            return abs(x) <= self.side_length / 2 and abs(y) <= self.side_length / 2
        elif self.shape == 'hexagonal':
          if abs(x) <= self.side_length / 2 and abs(y) <= self.side_length * math.sqrt(3) / 2:
              return True
          return False
        else:
            raise ValueError("Invalid shape specified.")

    def show(self):
        if self.shape == 'circular':
            if self.radius is None:
                raise ValueError("Radius not provided for circular shape.")
            circle = plt.Circle((0, 0), self.radius, fill=False, edgecolor='red', linewidth=3)
            plt.gca().add_patch(circle)
        elif self.shape == 'square':
            if self.side_length is None:
                raise ValueError("Side length not provided for square shape.")
            square = plt.Rectangle((-self.side_length / 2, -self.side_length / 2), self.side_length, self.side_length,
                                   fill=False, edgecolor='red', linewidth=3)
            plt.gca().add_patch(square)
        elif self.shape == 'hexagonal':
            if self.side_length is None:
                raise ValueError("Side length not provided for hexagonal shape.")
            angle = 2 * math.pi / 6
            points = [(self.side_length * math.cos(i * angle), self.side_length * math.sin(i * angle))
                      for i in range(6)]
            hexagon = plt.Polygon(points, closed=True, fill=False, edgecolor='red', linewidth=3)
            plt.gca().add_patch(hexagon)
        else:
            raise ValueError("Invalid shape specified.")

        plt.axis('equal')
        if self.side_length is not None:
            plt.xlim(-self.side_length - 1, self.side_length + 1)
            plt.ylim(-self.side_length - 1, self.side_length + 1)
        plt.grid(True)
        plt.show()


# Example usage
plane = Plane(shape='circular', radius=5)
plane.show()

plane = Plane(shape='square', side_length=10)
plane.show()

plane = Plane(shape='hexagonal', side_length=6)
plane.show()
