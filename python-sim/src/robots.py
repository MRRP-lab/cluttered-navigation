
class Robots():
    def __init__(self, N, spawns, collision):
        self.env = None
        self.num = N
        self.coords = spawns
        self.collision = collision

    def set_environment(self, env):
        self.env = env

    # Returns true if there's a robot at this position
    def is_robot(self, x, y):
        for pos in self.coords:
            if (x == pos[0] and y == pos[1]):
                return 1
        return 0

    # Returns a list of entries containing these entries for each robot:
    # [id, x, y]
    def get_coordinate_data(self):
        return [[i, self.coords[i, 0], self.coords[i, 1]] for i in range(self.num)]
